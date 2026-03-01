"""
Botivate HR Support - Chat API Router
Connects the frontend chatbot to the LangGraph agent.

OPTIMIZED:
- Single adapter connection per request (no duplicates)
- No auto schema re-analysis during chat (demand only)
- Single employee data fetch (reused across the pipeline)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.schemas import ChatMessage, ChatResponse, TokenPayload, ApprovalRequestCreate
from app.models.models import DatabaseConnection, RequestPriority, UserRole
from app.utils.auth import get_current_user
from app.agents.hr_agent import chat_with_agent
from app.adapters.adapter_factory import get_cached_adapter
from app.services.company_service import get_company
from app.services.approval_service import create_approval_request

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/send", response_model=ChatResponse)
async def send_message(
    data: ChatMessage,
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the AI chatbot.
    The agent handles intent detection, RAG, DB queries, and approval routing.
    """
    employee_id = user.employee_id
    company_id = user.company_id
    print(f"\n[{company_id}][CHAT LOG] 🗨️ New Chat Request from Employee: '{employee_id}'")

    # 1. Fetch company (fast — local SQLite)
    company = await get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # 2. Fetch active database connection (fast — local SQLite)
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

    # 3. Get CACHED adapter connection (reuse OAuth, no duplicate connect)
    adapter = await get_cached_adapter(db_conn.db_type, db_conn.connection_config)

    # 4. Fetch employee data ONCE (single Google Sheets API call)
    employee_data = {}
    try:
        raw_record = await adapter.get_record_by_key(primary_key_col, employee_id, table_name=master_table)
        if raw_record:
            employee_data = raw_record
            print(f"[{company_id}][CHAT LOG] ✅ Employee data fetched for '{employee_id}'")
        else:
            # Case-insensitive fallback
            all_records = await adapter.get_all_records(table_name=master_table)
            for rec in all_records:
                if str(rec.get(primary_key_col, "")).strip().lower() == employee_id.strip().lower():
                    employee_data = rec
                    print(f"[{company_id}][CHAT LOG] ✅ Fallback match found for '{employee_id}'")
                    break
    except Exception as e:
        print(f"[{company_id}][CHAT LOG] ⚠️ Employee data fetch error: {e}")

    # 5. Fetch recent approval requests (fast — local SQLite)
    from app.services.approval_service import get_employee_requests
    recent_requests_orm = await get_employee_requests(db, company_id, employee_id)
    recent_requests = [
        {
            "id": r.id,
            "request_type": r.request_type,
            "status": r.status.value,
            "context": r.context,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in recent_requests_orm
    ]

    # 6. Send to LangGraph agent (single pipeline)
    print(f"[{company_id}][CHAT LOG] Passing to HR Agent: '{data.message}'")
    try:
        agent_result = await chat_with_agent(
            company_id=company_id,
            employee_id=employee_id,
            employee_name=user.employee_name,
            role=user.role.value if isinstance(user.role, UserRole) else user.role,
            schema_map=schema_map,
            db_config=db_conn.connection_config,
            db_type=db_conn.db_type.value if db_conn else "google_sheets",
            user_message=data.message,
            employee_data=employee_data,
            chat_history=[],
            employee_requests=recent_requests,
        )
        print(f"[{company_id}][CHAT LOG] ✅ Agent completed.")
    except Exception as e:
        print(f"[{company_id}][CHAT ERROR] ❌ Agent crashed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent runtime error: {str(e)}")

    # 7. Create approval request if flagged
    if agent_result.get("approval_needed"):
        intent = agent_result.get("approval_request_type") or agent_result.get("intent", "general")
        request_details = agent_result.get("request_details") or {}
        try:
            await create_approval_request(
                db=db,
                company_id=company_id,
                data=ApprovalRequestCreate(
                    employee_id=employee_id,
                    employee_name=user.employee_name,
                    request_type=intent,
                    request_details=request_details,
                    context=data.message,
                    priority=RequestPriority.NORMAL,
                    assigned_to_role=UserRole.MANAGER,
                ),
            )
        except Exception as e:
            print(f"[CHAT] Error creating approval request: {e}")

    return ChatResponse(
        reply=agent_result.get("reply", "I'm sorry, something went wrong."),
        actions=agent_result.get("actions"),
    )
