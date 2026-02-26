"""
Botivate HR Support - AI Schema Analyzer Service
Uses LLM (Langchain) to automatically analyze database schemas.
Identifies primary keys, communication columns, employee name, and logical groupings.
Zero manual mapping required.
"""

import json
import re
from typing import List, Dict, Union

from app.config import settings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.models.schemas import SchemaAnalysisResult

async def analyze_schema(headers_input: Union[List[str], Dict[str, List[str]]]) -> SchemaAnalysisResult:
    """
    Analyze column headers using AI and return a structured schema map.
    This replaces all manual column mapping. Supports Multi-Table schemas.
    """
    # Normalize input
    if isinstance(headers_input, list):
        tables_headers = {"default": headers_input}
    else:
        tables_headers = headers_input

    # Prepare offline fallback
    if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here":
        print("⚠️ [MOCK SCHEMA] Skipping AI schema analysis because OpenAI key is missing. Using naive matcher.")
        pk, name, email, phone, whatsapp, role = None, None, None, None, None, None
        
        # Pick the first table as master
        master_table = list(tables_headers.keys())[0] if tables_headers else None
        headers = tables_headers.get(master_table, []) if master_table else []
        
        for h in headers:
            hl = h.lower().strip()
            if not pk and any(kw in hl for kw in ["employee id", "emp id", "emp_id", "staff id", "emp code", "employee_id", "id", "code"]):
                pk = h
            if not name and "name" in hl and "id" not in hl and "user" not in hl:
                name = h
            if not email and "email" in hl and "password" not in hl:
                email = h
            if not phone and any(kw in hl for kw in ["phone", "mobile", "contact"]) and "email" not in hl:
                phone = h
            if not whatsapp and "whatsapp" in hl:
                whatsapp = h
            if not role and any(kw in hl for kw in ["role", "designation", "position", "job title"]):
                role = h
        
        if not pk:
            for h in headers:
                if "id" in h.lower():
                    pk = h
                    break
                    
        child_tables = {k: {"columns": v} for k, v in tables_headers.items() if k != master_table}
        
        return SchemaAnalysisResult(
            primary_key=pk or (headers[0] if headers else "ID"),
            employee_name=name or (headers[1] if len(headers) > 1 else "Name"),
            email=email,
            phone=phone,
            whatsapp=whatsapp,
            role_column=role,
            categories={"other": [h for h in headers if h not in [pk, name, email, phone, whatsapp, role]]},
            master_table=master_table,
            child_tables=child_tables
        )

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )

    prompt = f"""You are an advanced database schema analyzer for an HR system.

Below is a dictionary of available data tables (Worksheets/SQL tables) and their respective column headers:

{json.dumps(tables_headers, indent=2)}

Your task:
1. Identify the MASTER TABLE which contains the primary employee records.
2. Inside that master table, identify:
   - PRIMARY EMPLOYEE IDENTIFIER column (Employee ID, Emp Code, etc.)
   - EMPLOYEE NAME column (Full Name, Name, etc.)
   - EMAIL column (if present)
   - PHONE NUMBER column (if present)
   - WHATSAPP column (if present)
   - ROLE OR DESIGNATION column (if present)
3. Group ALL remaining columns in the Master Table logically into categories: personal, job, leave, payroll, status, other.
4. Any other table provided should be placed into "child_tables", preserving its table name and indicating its columns. Try to guess what the foreign key might be if there's a column like "Emp ID" in the child table.

Return ONLY valid JSON in this exact format:
{{
  "master_table": "exact_master_table_name",
  "primary_key": "exact_column_name_in_master",
  "employee_name": "exact_column_name_in_master",
  "email": "exact_column_name_or_null",
  "phone": "exact_column_name_or_null",
  "whatsapp": "exact_column_name_or_null",
  "role_column": "exact_column_name_or_null",
  "categories": {{
    "personal": ["col1"],
    "job": ["col2"],
    "leave": ["col3"],
    "payroll": [],
    "status": [],
    "other": []
  }},
  "child_tables": {{
    "Some Other Tab": {{ "columns": ["col1", "col2"], "foreign_key_candidate": "col1" }}
  }}
}}

Rules:
- Use EXACT table and column names as they appear in the input.
- Return ONLY the JSON, no Markdown.
"""

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    raw = response.content.strip()

    clean = re.sub(r"```json|```", "", raw).strip()
    parsed = json.loads(clean)

    return SchemaAnalysisResult(**parsed)
