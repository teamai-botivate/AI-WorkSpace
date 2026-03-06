"""
Botivate HR Support — Database Operations Agent (Multi-Agent Architecture)
A dedicated LangGraph agent that handles ALL CRUD operations on the company's 
external database (Google Sheets, etc.)

FULLY DYNAMIC: Reads ALL tables, understands schema, and AI decides which 
table(s) to update/insert into. Zero hardcoded column names or table names.

This agent is called as a SUB-AGENT by the HR Conversational Agent.
It has its own LangGraph pipeline:
  1. connect_and_discover → Connects to DB, reads ALL tables & their headers
  2. read_employee_data → Fetches the employee's data from relevant tables
  3. plan_operations → AI generates multi-table operation plan (update + insert)
  4. execute_operations → Writes to the correct table(s)
  5. verify_operations → Re-reads to confirm changes
"""

import json
import re
from typing import Any, Dict, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.config import settings
from app.adapters.adapter_factory import get_adapter
from app.models.models import DatabaseType


# ── Agent State ──────────────────────────────────────────

class DBAgentState(TypedDict):
    # Input
    db_type: str
    connection_config: Dict[str, Any]
    schema_map: Dict[str, Any]
    employee_id: str
    action: str              # "leave_request_applied", "leave_request_approved", etc.
    context: Dict[str, Any]  # Rich context: dates, reason, decided_by, etc.
    
    # Working state — MULTI-TABLE
    all_tables: List[str]                         # All available table names
    all_tables_headers: Dict[str, List[str]]      # {table_name: [headers]}
    employee_data_by_table: Dict[str, Any]        # {table_name: [records] or record}
    primary_key: str
    operation_plan: Dict[str, Any]                # AI-generated multi-table plan
    
    # Output
    success: bool
    updates_applied: Dict[str, Any]
    new_columns_created: List[str]
    rows_inserted: Dict[str, Any]
    error: Optional[str]
    verification: Optional[Dict[str, Any]]
    retry_count: int


# ── LLM ──────────────────────────────────────────────────

def get_db_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )


# ── Node 1: Connect & Discover ALL Tables ──────────────

async def connect_and_discover(state: DBAgentState) -> DBAgentState:
    """Connect to the database and read ALL tables and their headers."""
    try:
        adapter = await get_adapter(
            DatabaseType(state["db_type"]), 
            state["connection_config"]
        )
        
        primary_key = state["schema_map"].get("primary_key", "")
        if not primary_key:
            state["error"] = "No primary_key in schema_map. Cannot identify employee row."
            state["success"] = False
            return state
        
        # Discover ALL tables
        all_tables = await adapter.get_available_tables()
        all_tables_headers = {}
        
        for table_name in all_tables:
            try:
                headers = await adapter.get_headers(table_name=table_name)
                if headers:  # Skip empty tables
                    all_tables_headers[table_name] = headers
            except Exception as e:
                print(f"[DB AGENT] ⚠️ Could not read headers for '{table_name}': {e}")
        
        state["all_tables"] = all_tables
        state["all_tables_headers"] = all_tables_headers
        state["primary_key"] = primary_key
        print(f"[DB AGENT] ✅ Discovered {len(all_tables_headers)} tables: {list(all_tables_headers.keys())}")
        
    except Exception as e:
        state["error"] = f"Connection failed: {str(e)}"
        state["success"] = False
        print(f"[DB AGENT] ❌ Connection error: {e}")
    
    return state


# ── Node 2: Read Employee's Data From ALL Relevant Tables ─

async def read_employee_data(state: DBAgentState) -> DBAgentState:
    """Fetch the employee's data from ALL tables where their ID appears."""
    if state.get("error"):
        return state
    
    try:
        adapter = await get_adapter(
            DatabaseType(state["db_type"]),
            state["connection_config"]
        )
        
        employee_data_by_table = {}
        pk = state["primary_key"]
        employee_id = state["employee_id"]
        
        # Determine master table
        master_table = state["schema_map"].get("master_table")
        
        for table_name, headers in state["all_tables_headers"].items():
            try:
                all_records = await adapter.get_all_records(table_name=table_name)
                
                if table_name == master_table:
                    # Master table: find the single employee record by PK
                    record = None
                    for rec in all_records:
                        if str(rec.get(pk, "")).strip().lower() == str(employee_id).strip().lower():
                            record = rec
                            break
                    if record:
                        employee_data_by_table[table_name] = {"type": "master", "record": record}
                        print(f"[DB AGENT] ✅ Master '{table_name}': found employee record")
                else:
                    # Child tables: find ALL rows matching employee_id in ANY column
                    matching_rows = []
                    for rec in all_records:
                        for col_val in rec.values():
                            if str(col_val).strip().lower() == str(employee_id).strip().lower():
                                matching_rows.append(rec)
                                break
                    
                    if matching_rows:
                        employee_data_by_table[table_name] = {"type": "child", "records": matching_rows}
                        print(f"[DB AGENT] ✅ Child '{table_name}': found {len(matching_rows)} matching rows")
                    else:
                        # Still include the table structure (with sample) for AI context
                        employee_data_by_table[table_name] = {
                            "type": "child", 
                            "records": [],
                            "sample_rows": all_records[:2] if len(all_records) <= 50 else all_records[:2],
                            "total_rows": len(all_records)
                        }
                        print(f"[DB AGENT] ℹ️ Child '{table_name}': no matching rows (included schema for AI)")
                        
            except Exception as e:
                print(f"[DB AGENT] ⚠️ Error reading '{table_name}': {e}")
        
        if master_table and master_table not in employee_data_by_table:
            state["error"] = f"Employee '{employee_id}' not found in master table '{master_table}'."
            state["success"] = False
            return state
        
        state["employee_data_by_table"] = employee_data_by_table
        print(f"[DB AGENT] ✅ Employee data collected from {len(employee_data_by_table)} tables")
        
    except Exception as e:
        state["error"] = f"Read failed: {str(e)}"
        state["success"] = False
        print(f"[DB AGENT] ❌ Read error: {e}")
    
    return state


# ── Node 3: Plan Operations (AI generates multi-table CRUD) ─

async def plan_operations(state: DBAgentState) -> DBAgentState:
    """AI analyzes ALL tables, current data, and action context to generate a multi-table operation plan."""
    if state.get("error"):
        return state
    
    try:
        if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here":
            state["operation_plan"] = _fallback_plan(state)
            return state
        
        llm = get_db_llm()
        
        # Build comprehensive context for AI
        tables_context = {}
        for table_name, data in state["employee_data_by_table"].items():
            entry = {"headers": state["all_tables_headers"].get(table_name, [])}
            if data["type"] == "master":
                entry["employee_row"] = data["record"]
            else:
                entry["employee_matching_rows"] = data["records"]
                if data.get("sample_rows"):
                    entry["sample_rows_for_structure"] = data["sample_rows"]
                entry["total_rows_in_table"] = data.get("total_rows", len(data["records"]))
            tables_context[table_name] = entry
        
        # Also include tables with no employee data but that might need new rows
        for table_name in state["all_tables_headers"]:
            if table_name not in tables_context:
                tables_context[table_name] = {
                    "headers": state["all_tables_headers"][table_name],
                    "note": "No employee data found in this table yet"
                }
        
        prompt = f"""You are an expert HR database administrator managing a multi-table employee database.

=== ALL AVAILABLE TABLES AND THEIR DATA ===
{json.dumps(tables_context, default=str, indent=2)}

=== PRIMARY KEY COLUMN === "{state['primary_key']}"
=== EMPLOYEE ID === "{state['employee_id']}"
=== ACTION THAT OCCURRED === "{state['action']}"

=== ACTION DETAILS ===
{json.dumps(state['context'], default=str, indent=2)}

YOUR TASK:
Analyze ALL tables and determine EXACTLY which table(s) need to be modified and how.
You can perform TWO types of operations:
1. **UPDATE**: Modify existing values in a row (e.g., update leave balance in master table)
2. **INSERT**: Add a new row to a table (e.g., add a leave record entry in Leave_Record table)

CRITICAL RULES:
1. USE EXACT TABLE NAMES and COLUMN NAMES as they appear above — bit-for-bit match.
2. For UPDATES: Match column names EXACTLY from the table's headers.
3. For INSERTS: Use the column names from that table's headers. Fill in values logically.
4. NEVER update the primary key column ("{state['primary_key']}").
5. For numeric calculations (like deducting leave balance): Read the current value, calculate, return the final NUMBER.

HOW TO DECIDE WHAT TO DO:
- If action contains "applied" or "submitted": 
  * Look for a tracking/record table (like "Leave_Record", "Attendance", etc.) and INSERT a new row with status "Pending"
  * Update any status columns in the master table if they exist
  * Do NOT change numeric balances yet (leave balance, etc.)

- If action contains "approved":
  * UPDATE the tracking/record table row's status to "Approved" (find the matching row)
  * UPDATE the master table's numeric columns (e.g., deduct leave balance, increment leaves taken)
  * If there's a "Leaves Taken" column: add the duration
  * If there's a "Leaves Remaining" or "Balance" column: subtract the duration

- If action contains "rejected":
  * UPDATE only the status in any relevant table to "Rejected"
  * Do NOT change any numeric balances

- For "data_update": 
  * UPDATE the specified values in the correct table

=== RESPONSE FORMAT ===
Return ONLY valid JSON:
{{
  "operations": [
    {{
      "table": "Exact Table Name",
      "type": "update",
      "filters": {{
        "Column1": "value to match row",
        "Column2": "another value to narrow down"
      }},
      "updates": {{
        "Column Name": "new value"
      }}
    }},
    {{
      "table": "Exact Table Name", 
      "type": "insert",
      "new_row": {{
        "Column1": "value1",
        "Column2": "value2"
      }}
    }}
  ],
  "new_columns": []
}}

IMPORTANT FOR UPDATES:
- Use "filters" with MULTIPLE columns to identify the EXACT row to update.
- For child tables (like Leave_Record): ALWAYS include BOTH the employee ID column AND a status/date column in filters to find the specific row.
  Example: {{"Employee_ID": "EMP002", "Approval Status": "Pending"}} to find the pending leave row.
- For master table: Just include the primary key in filters: {{"{state['primary_key']}": "{state['employee_id']}"}}

If no changes are needed, return {{"operations": [], "new_columns": []}}.
No explanations. Only JSON."""

        resp = await llm.ainvoke([HumanMessage(content=prompt)])
        raw = resp.content.strip()
        clean = re.sub(r"```json\s*|```\s*", "", raw).strip()
        
        plan = json.loads(clean)
        
        # Safety validations
        if not isinstance(plan, dict):
            raise ValueError(f"Plan is not a dict: {type(plan)}")
        
        plan.setdefault("operations", [])
        plan.setdefault("new_columns", [])
        
        # Safety: never update the primary key in any operation
        for op in plan["operations"]:
            if op.get("type") == "update" and op.get("updates"):
                op["updates"].pop(state["primary_key"], None)
        
        state["operation_plan"] = plan
        print(f"[DB AGENT] ✅ Operation plan: {len(plan['operations'])} operations across tables")
        for op in plan["operations"]:
            print(f"[DB AGENT]   → {op['type'].upper()} on '{op['table']}': {json.dumps(op.get('updates') or op.get('new_row', {}), default=str)}")
        
    except json.JSONDecodeError as je:
        print(f"[DB AGENT] ⚠️ AI JSON parse error: {je}, using fallback")
        state["operation_plan"] = _fallback_plan(state)
    except Exception as e:
        print(f"[DB AGENT] ⚠️ Plan error: {e}, using fallback")
        state["operation_plan"] = _fallback_plan(state)
    
    return state


# ── Node 4: Execute Operations (Multi-Table) ────────────

async def execute_operations(state: DBAgentState) -> DBAgentState:
    """Execute the AI-generated multi-table operation plan."""
    if state.get("error"):
        return state
    
    plan = state.get("operation_plan", {})
    operations = plan.get("operations", [])
    new_columns = plan.get("new_columns", [])
    
    if not operations and not new_columns:
        state["success"] = True
        state["updates_applied"] = {}
        state["new_columns_created"] = []
        state["rows_inserted"] = {}
        print("[DB AGENT] ℹ️ No operations needed")
        return state
    
    try:
        adapter = await get_adapter(
            DatabaseType(state["db_type"]),
            state["connection_config"]
        )
        
        all_updates = {}
        all_inserts = {}
        created_cols = []
        
        # Step 1: Create new columns first (if any)
        for col_spec in new_columns:
            if isinstance(col_spec, dict):
                col_name = col_spec.get("column")
                table_name = col_spec.get("table")
            else:
                col_name = col_spec
                table_name = None
            
            if col_name:
                try:
                    existing_headers = await adapter.get_headers(table_name=table_name)
                    if col_name not in existing_headers:
                        await adapter.add_column(col_name, table_name=table_name)
                        created_cols.append(f"{table_name or 'default'}:{col_name}")
                        print(f"[DB AGENT] ✅ Created column '{col_name}' in '{table_name or 'default'}'")
                except Exception as ce:
                    print(f"[DB AGENT] ⚠️ Failed to create column '{col_name}': {ce}")
        
        # Step 2: Execute each operation
        for op in operations:
            table_name = op.get("table")
            op_type = op.get("type", "update")
            
            try:
                if op_type == "update":
                    updates = op.get("updates", {})
                    filters = op.get("filters", {})
                    
                    if not updates:
                        continue
                    
                    success = False
                    if filters and len(filters) > 1:
                        # Multi-filter matching (for child tables with duplicate keys)
                        print(f"[DB AGENT] Using multi-filter update on '{table_name}': filters={filters}")
                        success = await adapter.update_record_by_filters(
                            filters, updates, table_name=table_name
                        )
                    elif filters:
                        # Single filter — use standard update_record
                        match_col = list(filters.keys())[0]
                        match_val = list(filters.values())[0]
                        success = await adapter.update_record(
                            match_col, match_val, updates, table_name=table_name
                        )
                    else:
                        # Legacy fallback — use PK
                        match_col = op.get("match_column", state["primary_key"])
                        match_val = op.get("match_value", state["employee_id"])
                        success = await adapter.update_record(
                            match_col, match_val, updates, table_name=table_name
                        )
                    
                    if success:
                        key = f"update:{table_name}"
                        all_updates[key] = updates
                        print(f"[DB AGENT] ✅ UPDATED '{table_name}': {updates}")
                    else:
                        print(f"[DB AGENT] ⚠️ update returned False for '{table_name}'")
                elif op_type == "insert":
                    new_row = op.get("new_row", {})
                    if new_row:
                        success = await adapter.create_record(new_row, table_name=table_name)
                        if success:
                            key = f"insert:{table_name}"
                            all_inserts[key] = new_row
                            print(f"[DB AGENT] ✅ INSERTED into '{table_name}': {new_row}")
                        else:
                            print(f"[DB AGENT] ⚠️ create_record returned False for '{table_name}'")
                            
            except Exception as op_err:
                print(f"[DB AGENT] ❌ Operation failed on '{table_name}': {op_err}")
        
        state["success"] = bool(all_updates or all_inserts)
        state["updates_applied"] = {**all_updates, **all_inserts}
        state["rows_inserted"] = all_inserts
        state["new_columns_created"] = created_cols
        
        if state["success"]:
            print(f"[DB AGENT] ✅ All operations completed: {len(all_updates)} updates, {len(all_inserts)} inserts")
        else:
            state["error"] = "No operations succeeded"
            
    except Exception as e:
        state["error"] = f"Execute failed: {str(e)}"
        state["success"] = False
        print(f"[DB AGENT] ❌ Execute error: {e}")
    
    return state


# ── Node 5: Verify Operations ──────────────────────────

async def verify_operations(state: DBAgentState) -> DBAgentState:
    """Re-read data to verify the operations were applied."""
    if not state.get("success"):
        # If execution failed, try retry
        retry = state.get("retry_count", 0)
        if retry < 2 and state.get("operation_plan"):
            state["retry_count"] = retry + 1
            state["error"] = None  # Clear error for retry
            print(f"[DB AGENT] 🔄 Retrying... attempt {retry + 1}")
            return state
        return state
    
    try:
        adapter = await get_adapter(
            DatabaseType(state["db_type"]),
            state["connection_config"]
        )
        
        # Verify master table updates
        master_table = state["schema_map"].get("master_table")
        if master_table:
            updated_record = await adapter.get_record_by_key(
                state["primary_key"], 
                state["employee_id"],
                table_name=master_table
            )
            
            if updated_record:
                update_key = f"update:{master_table}"
                expected_updates = state.get("updates_applied", {}).get(update_key, {})
                verified = {}
                failed = {}
                for col, expected_val in expected_updates.items():
                    actual_val = updated_record.get(col)
                    if str(actual_val).strip() == str(expected_val).strip():
                        verified[col] = actual_val
                    else:
                        failed[col] = {"expected": expected_val, "actual": actual_val}
                
                state["verification"] = {
                    "verified_count": len(verified),
                    "failed_count": len(failed),
                    "verified_fields": verified,
                    "failed_fields": failed,
                }
                
                if failed:
                    print(f"[DB AGENT] ⚠️ Verification: {len(verified)} OK, {len(failed)} MISMATCH: {failed}")
                else:
                    print(f"[DB AGENT] ✅ Verification: ALL {len(verified)} fields confirmed!")
            else:
                state["verification"] = {"note": "Could not re-read master record for verification"}
        else:
            state["verification"] = {"note": "No master table configured for verification"}
            
    except Exception as e:
        print(f"[DB AGENT] ⚠️ Verification error (non-critical): {e}")
        state["verification"] = {"error": str(e)}
    
    return state


# ── Routing Logic ────────────────────────────────────────

def should_retry(state: DBAgentState) -> str:
    """After verify, decide if we need to retry or finish."""
    if not state.get("success") and state.get("retry_count", 0) < 2:
        return "retry"
    return "done"


# ── Non-AI Fallback Plan ────────────────────────────────

def _fallback_plan(state: DBAgentState) -> dict:
    """Generate basic operation plan without AI — uses master table only."""
    operations = []
    
    # Parse action type
    action = state.get("action", "")
    context = state.get("context", {})
    master_table = state["schema_map"].get("master_table")
    
    parts = action.split("_")
    action_status = parts[-1] if len(parts) > 1 else "applied"
    
    status_value = {
        "applied": "Pending",
        "approved": "Approved", 
        "rejected": "Rejected",
    }.get(action_status, "Pending")
    
    # Try to update status columns in master table
    if master_table and master_table in state.get("all_tables_headers", {}):
        headers = state["all_tables_headers"][master_table]
        updates = {}
        
        for h in headers:
            h_lower = h.lower()
            if "status" in h_lower and any(kw in h_lower for kw in ["leave", "request", "approval"]):
                updates[h] = status_value
        
        if updates:
            operations.append({
                "table": master_table,
                "type": "update",
                "match_column": state["primary_key"],
                "match_value": state["employee_id"],
                "updates": updates
            })
    
    return {"operations": operations, "new_columns": []}


# ── Build the DB Agent Graph ─────────────────────────────

def build_db_agent_graph() -> StateGraph:
    """Construct the Database Operations Agent LangGraph."""
    graph = StateGraph(DBAgentState)
    
    # Add nodes
    graph.add_node("connect_and_discover", connect_and_discover)
    graph.add_node("read_employee_data", read_employee_data)
    graph.add_node("plan_operations", plan_operations)
    graph.add_node("execute_operations", execute_operations)
    graph.add_node("verify_operations", verify_operations)
    
    # Set entry point
    graph.set_entry_point("connect_and_discover")
    
    # Linear flow: connect → read → plan → execute → verify
    graph.add_edge("connect_and_discover", "read_employee_data")
    graph.add_edge("read_employee_data", "plan_operations")
    graph.add_edge("plan_operations", "execute_operations")
    graph.add_edge("execute_operations", "verify_operations")
    
    # After verify: retry or finish
    graph.add_conditional_edges(
        "verify_operations",
        should_retry,
        {
            "retry": "execute_operations",  # Retry from execute
            "done": END,
        },
    )
    
    return graph


# Compile the DB agent graph once
db_agent_graph = build_db_agent_graph().compile()


# ── Public API ───────────────────────────────────────────

async def run_db_agent(
    db_type: str,
    connection_config: dict,
    schema_map: dict,
    employee_id: str,
    action: str,
    context: dict,
) -> dict:
    """
    Public entry point: run the Database Agent to perform multi-table CRUD operations.
    
    Args:
        db_type: "google_sheets", "postgresql", etc.
        connection_config: Adapter connection config
        schema_map: Schema map with primary_key, master_table, child_tables, etc.
        employee_id: Which employee's data to operate on
        action: "leave_request_applied", "leave_request_approved", etc.
        context: Rich context dict with details
    
    Returns:
        {success, updates_applied, new_columns_created, rows_inserted, error, verification}
    """
    initial_state: DBAgentState = {
        "db_type": db_type,
        "connection_config": connection_config,
        "schema_map": schema_map,
        "employee_id": employee_id,
        "action": action,
        "context": context,
        "all_tables": [],
        "all_tables_headers": {},
        "employee_data_by_table": {},
        "primary_key": "",
        "operation_plan": {},
        "success": False,
        "updates_applied": {},
        "new_columns_created": [],
        "rows_inserted": {},
        "error": None,
        "verification": None,
        "retry_count": 0,
    }
    
    print(f"\n[DB AGENT] 🚀 Starting Multi-Table DB Agent for {employee_id} | Action: {action}")
    print(f"[DB AGENT] Context: {json.dumps(context, default=str)}")
    
    result = await db_agent_graph.ainvoke(initial_state)
    
    output = {
        "success": result.get("success", False),
        "updates_applied": result.get("updates_applied", {}),
        "new_columns_created": result.get("new_columns_created", []),
        "rows_inserted": result.get("rows_inserted", {}),
        "error": result.get("error"),
        "verification": result.get("verification"),
    }
    
    if output["success"]:
        print(f"[DB AGENT] ✅ COMPLETED: {output['updates_applied']}")
    else:
        print(f"[DB AGENT] ❌ FAILED: {output['error']}")
    
    return output
