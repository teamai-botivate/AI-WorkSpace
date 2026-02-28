"""
Botivate HR Support - Chat API Router
Connects the frontend chatbot to the LangGraph agent.

OPTIMIZED v2:
- Employee data cache (2-min TTL) — avoids hitting Google Sheets every message
- Parallel data fetch (employee data + approval requests run simultaneously)  
- SSE streaming endpoint — user sees response tokens instantly
- Single cached adapter connection (no duplicate OAuth)
"""

import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.schemas import ChatMessage, ChatResponse, TokenPayload, ApprovalRequestCreate
from app.models.models import DatabaseConnection, RequestPriority, UserRole
from app.utils.auth import get_current_user
from app.agents.hr_agent import chat_with_agent, chat_with_agent_stream
from app.adapters.adapter_factory import (
    get_cached_adapter,
    get_cached_employee_data,
    set_cached_employee_data,
)
from app.services.company_service import get_company
from app.services.approval_service import create_approval_request

router = APIRouter(prefix="/api/chat", tags=["Chat"])


async def _fetch_employee_data(adapter, primary_key_col, employee_id, master_table, company_id):
    """Fetch employee data with cache layer."""
    # Check cache first
    cached = get_cached_employee_data(company_id, employee_id)
    if cached:
        return cached

    # Cache miss — fetch from Google Sheets
    employee_data = {}
    try:
        raw_record = await adapter.get_record_by_key(primary_key_col, employee_id, table_name=master_table)
        if raw_record:
            employee_data = raw_record
        else:
            # Case-insensitive fallback
            all_records = await adapter.get_all_records(table_name=master_table)
            for rec in all_records:
                if str(rec.get(primary_key_col, "")).strip().lower() == employee_id.strip().lower():
                    employee_data = rec
                    break
        if employee_data:
            set_cached_employee_data(company_id, employee_id, employee_data)
    except Exception as e:
        print(f"[{company_id}][CHAT LOG] ⚠️ Employee data fetch error: {e}")
    return employee_data


async def _fetch_recent_requests(db, company_id, employee_id):
    """Fetch recent approval requests from local SQLite."""
    from app.services.approval_service import get_employee_requests
    recent_requests_orm = await get_employee_requests(db, company_id, employee_id)
    return [
        {
            "id": r.id,
            "request_type": r.request_type,
            "status": r.status.value,
            "context": r.context,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in recent_requests_orm
    ]


async def _prepare_chat_context(data, user, db):
    """Prepare all context needed for the agent. Runs data fetches in PARALLEL."""
    employee_id = user.employee_id
    company_id = user.company_id

    # 1. Fetch company + DB connection (fast — local SQLite, sequential)
    company = await get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    result = await db.execute(
        select(DatabaseConnection).where(
            DatabaseConnection.company_id == company_id,
            DatabaseConnection.is_active == True,
        )
    )
    db_conn = result.scalars().first()
    if not db_conn or not db_conn.schema_map:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Company database not configured properly.",
        )

    schema_map = db_conn.schema_map
    primary_key_col = schema_map.get("primary_key", "")
    master_table = schema_map.get("master_table", None)

    # 2. Get CACHED adapter connection
    adapter = await get_cached_adapter(db_conn.db_type, db_conn.connection_config)

    # 3. PARALLEL: fetch employee data + approval requests simultaneously
    employee_data_task = _fetch_employee_data(adapter, primary_key_col, employee_id, master_table, company_id)
    recent_requests_task = _fetch_recent_requests(db, company_id, employee_id)
    employee_data, recent_requests = await asyncio.gather(employee_data_task, recent_requests_task)

    print(f"[{company_id}][CHAT LOG] ✅ Parallel data fetch complete for '{employee_id}'")

    return {
        "company_id": company_id,
        "employee_id": employee_id,
        "employee_name": user.employee_name,
        "role": user.role.value if isinstance(user.role, UserRole) else user.role,
        "schema_map": schema_map,
        "db_config": db_conn.connection_config,
        "db_type": db_conn.db_type.value if db_conn else "google_sheets",
        "employee_data": employee_data,
        "recent_requests": recent_requests,
        "db_conn": db_conn,
    }


@router.post("/send", response_model=ChatResponse)
async def send_message(
    data: ChatMessage,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the AI chatbot (non-streaming).
    For streaming, use POST /api/chat/stream instead.
    """
    print(f"\n[{user.company_id}][CHAT LOG] 🗨️ New Chat Request from Employee: '{user.employee_id}'")

    ctx = await _prepare_chat_context(data, user, db)

    # Send to LangGraph agent
    print(f"[{ctx['company_id']}][CHAT LOG] Passing to HR Agent: '{data.message}'")
    try:
        agent_result = await chat_with_agent(
            company_id=ctx["company_id"],
            employee_id=ctx["employee_id"],
            employee_name=ctx["employee_name"],
            role=ctx["role"],
            schema_map=ctx["schema_map"],
            db_config=ctx["db_config"],
            db_type=ctx["db_type"],
            user_message=data.message,
            employee_data=ctx["employee_data"],
            chat_history=[],
            employee_requests=ctx["recent_requests"],
        )
        print(f"[{ctx['company_id']}][CHAT LOG] ✅ Agent completed.")
    except Exception as e:
        print(f"[{ctx['company_id']}][CHAT ERROR] ❌ Agent crashed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent runtime error: {str(e)}")

    # Create approval request if flagged
    await _handle_approval_if_needed(agent_result, ctx, data, user, db)

    return ChatResponse(
        reply=agent_result.get("reply", "I'm sorry, something went wrong."),
        actions=agent_result.get("actions"),
    )


@router.post("/stream")
async def stream_message(
    data: ChatMessage,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    SSE streaming endpoint — sends response tokens as they arrive.
    Frontend receives partial text in real-time for perceived instant response.
    Sends heartbeat events to keep the connection alive during agent processing.
    """
    print(f"\n[{user.company_id}][CHAT STREAM] 🗨️ Streaming Chat from: '{user.employee_id}'")

    # Prepare all context BEFORE entering the generator (ensures DB session is alive)
    try:
        ctx = await _prepare_chat_context(data, user, db)
    except Exception as e:
        print(f"[CHAT STREAM ERROR] Context preparation failed: {e}")
        # Return error as a non-streaming JSON response
        raise HTTPException(status_code=500, detail=f"Context preparation failed: {str(e)}")

    # Pre-extract all values needed by the generator (avoid using db inside generator)
    stream_params = {
        "company_id": ctx["company_id"],
        "employee_id": ctx["employee_id"],
        "employee_name": ctx["employee_name"],
        "role": ctx["role"],
        "schema_map": ctx["schema_map"],
        "db_config": ctx["db_config"],
        "db_type": ctx["db_type"],
        "employee_data": ctx["employee_data"],
        "recent_requests": ctx["recent_requests"],
        "user_message": data.message,
    }

    async def event_generator():
        try:
            full_response = ""
            async for chunk in chat_with_agent_stream(
                company_id=stream_params["company_id"],
                employee_id=stream_params["employee_id"],
                employee_name=stream_params["employee_name"],
                role=stream_params["role"],
                schema_map=stream_params["schema_map"],
                db_config=stream_params["db_config"],
                db_type=stream_params["db_type"],
                user_message=stream_params["user_message"],
                employee_data=stream_params["employee_data"],
                chat_history=[],
                employee_requests=stream_params["recent_requests"],
            ):
                if chunk == "__HEARTBEAT__":
                    # Keep-alive event — browser ignores events without "data:" prefix
                    yield ": heartbeat\n\n"
                    continue
                full_response += chunk
                yield f"data: {json.dumps({'token': chunk})}\n\n"

            # Send final event with complete response
            yield f"data: {json.dumps({'done': True, 'reply': full_response})}\n\n"

            print(f"[{stream_params['company_id']}][CHAT STREAM] ✅ Stream complete. Length: {len(full_response)}")

        except Exception as e:
            import traceback
            print(f"[CHAT STREAM ERROR] {e}\n{traceback.format_exc()}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _handle_approval_if_needed(agent_result, ctx, data, user, db):
    """Create approval request if the agent flagged one."""
    if agent_result.get("approval_needed"):
        intent = agent_result.get("approval_request_type") or agent_result.get("intent", "general")
        request_details = agent_result.get("request_details") or {}
        try:
            await create_approval_request(
                db=db,
                company_id=ctx["company_id"],
                data=ApprovalRequestCreate(
                    employee_id=ctx["employee_id"],
                    employee_name=ctx["employee_name"],
                    request_type=intent,
                    request_details=request_details,
                    context=data.message,
                    priority=RequestPriority.NORMAL,
                    assigned_to_role=UserRole.MANAGER,
                ),
            )
        except Exception as e:
            print(f"[CHAT] Error creating approval request: {e}")
