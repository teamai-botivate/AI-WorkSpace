"""
Resume Screening — Email & Aptitude Router

Ported from original Resume-Screening-Agent/Aptitude_Generator/backend/main.py + agent.py.
Aptitude test generation, assessment management, candidate email outreach.
"""

import os
import json
import time
import uuid
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import APIRouter, HTTPException, BackgroundTasks, Form
from pydantic import BaseModel
from openai import OpenAI
from ..core.config import get_settings

logger = logging.getLogger("AptitudeGenerator")

router = APIRouter()

settings = get_settings()

# Simple JSON file DB for assessments (same as original)
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "assessments_db.json")


def _init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"assessments": [], "submissions": []}, f)


def _get_db():
    _init_db()
    with open(DB_FILE, "r") as f:
        return json.load(f)


def _save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


# --- AI Agent Functions ---

def generate_aptitude_questions(jd_text: str):
    """Analyzes JD and generates 25 MCQ + 4 Coding questions."""
    client = OpenAI(api_key=settings.openai_api_key)

    prompt = f"""
    Create a recruitment assessment JSON for the following Job Description.
    
    REQUIRED JSON STRUCTURE:
    {{
      "mcqs": [
        {{
          "id": "Q1",
          "question": "text",
          "options": ["A", "B", "C", "D"],
          "answer": "correct option text"
        }}
      ],
      "coding_questions": [
        {{
          "title": "Title of DSA Problem",
          "description": "Clear problem statement and requirements",
          "constraints": "Complexity and input limits",
          "example_input": "sample input string",
          "example_output": "sample output string",
          "test_cases": [
            {{"input": "in1", "output": "out1"}},
            {{"input": "in2", "output": "out2"}}
          ]
        }}
      ]
    }}

    RULES:
    1. Generate 25 MCQs.
    2. If the JD is technical (CS/IT), generate 4 Coding Questions. Otherwise, "coding_questions" must be [].
    3. Coding questions must be role-agnostic DSA (MNC style).
    4. OUTPUT ONLY THE JSON. NO EXPLANATION.

    JOB DESCRIPTION:
    {jd_text}
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a JSON-only generator. You honestly follow the requested schema and never omit fields."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )
        response_content = completion.choices[0].message.content
        data = json.loads(response_content)
        mcqs = data.get("mcqs", [])
        coding = data.get("coding_questions", [])
        logger.info(f"✅ Generated {len(mcqs)} MCQs and {len(coding)} Coding questions.")
        return {"mcqs": mcqs, "coding_questions": coding}
    except Exception as e:
        logger.error(f"❌ AGENT ERROR: {e}")
        raise e


def evaluate_code(problem_text: str, user_code: str, language: str, test_cases: list):
    """Evaluates candidate code against test cases using AI."""
    client = OpenAI(api_key=settings.openai_api_key)

    prompt = f"""
    Evaluate the following coding assessment submission.
    
    PROBLEM DESCRIPTION:
    {problem_text}
    
    TEST CASES:
    {json.dumps(test_cases, indent=2)}
    
    CANDIDATE CODE ({language}):
    {user_code}
    
    INSTRUCTIONS:
    1. Analyze the code for logic, correctness, and adherence to constraints.
    2. Check if the code would pass the provided test cases.
    3. Return a JSON object with:
       - "success": boolean (true if logic is correct and passes test cases)
       - "output": string (compiler-style output or explanation of errors)
       - "passed_count": number of test cases passed
       - "total_count": total number of test cases provided
    
    OUTPUT ONLY THE JSON.
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a code execution and evaluation agent. Be strict and accurate."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"success": False, "output": f"Evaluation Error: {str(e)}", "passed_count": 0, "total_count": len(test_cases)}


# --- Pydantic Models ---


class JDRequest(BaseModel):
    jd_text: str


class RunCodeRequest(BaseModel):
    code: str
    language: str
    problem_text: str
    test_cases: list


class EmailRequest(BaseModel):
    emails: list[str]
    job_title: str
    mcq_count: int
    coding_count: int
    assessment_link: str
    mcqs: list[dict]
    coding_questions: list[dict]


class RejectionRequest(BaseModel):
    emails: list[str]
    job_title: str


# --- Endpoints ---


@router.post("/generate-aptitude")
async def generate_aptitude(request: JDRequest):
    if not request.jd_text.strip():
        raise HTTPException(status_code=400, detail="Job Description text is empty")
    try:
        result = generate_aptitude_questions(request.jd_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-code")
async def run_code(request: RunCodeRequest):
    try:
        result = evaluate_code(request.problem_text, request.code, request.language, request.test_cases)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-assessment")
async def send_assessment(request: EmailRequest, background_tasks: BackgroundTasks):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_user, smtp_password]):
        raise HTTPException(status_code=500, detail="SMTP credentials not configured.")

    def update_db_task():
        try:
            token = request.assessment_link.split("token=")[-1]
            db = _get_db()
            db["assessments"].append(
                {
                    "id": str(uuid.uuid4()),
                    "token": token,
                    "job_title": request.job_title,
                    "emails": request.emails,
                    "mcqs": request.mcqs,
                    "coding_questions": request.coding_questions,
                    "timestamp": time.time(),
                    "status": "Sent",
                }
            )
            _save_db(db)
        except Exception as e:
            logger.warning(f"DB Warning: {e}")

    background_tasks.add_task(update_db_task)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        format_info = ""
        if request.mcq_count > 0:
            format_info += f"<li><strong>Aptitude:</strong> {request.mcq_count} MCQs</li>"
        if request.coding_count > 0:
            format_info += f"<li><strong>Coding:</strong> {request.coding_count} DSA Questions</li>"

        for recipient_email in request.emails:
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = recipient_email
            msg["Subject"] = f"Career Opportunity | {request.job_title} Technical Evaluation"

            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #6366f1;">Congratulations!</h2>
                <p>Dear Candidate,</p>
                <p>Your profile for the <strong>{request.job_title}</strong> role has been shortlisted. Please complete the following technical assessment.</p>
                
                <div style="background: #f4f4f9; padding: 20px; border-radius: 10px; border-left: 5px solid #6366f1; margin: 20px 0;">
                    <p><strong>Assessment Details:</strong></p>
                    <ul>
                        {format_info}
                        <li><strong>Environment:</strong> Online IDE (Multiple Languages Supported)</li>
                        <li><strong>Estimated Time:</strong> 1 Hour</li>
                    </ul>

                    <div style="background: #fff5f5; border: 1px solid #feb2b2; padding: 15px; border-radius: 8px; margin-top: 15px;">
                        <p style="color: #c53030; margin-top: 0;"><strong>⚠️ PROCTORING RULES:</strong></p>
                        <p style="font-size: 0.9rem; margin-bottom: 0;">Camera must stay ON. Tab switching and head movement are strictly monitored by AI.</p>
                    </div>

                    <p style="text-align: center; margin-top: 25px;">
                        <a href="{request.assessment_link}" style="background: #6366f1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Enter Test Environment</a>
                    </p>
                </div>
                <p>Best Regards,<br><strong>Talent Acquisition Team</strong><br>RecruitAI</p>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, "html"))
            server.send_message(msg)

        server.quit()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"SMTP Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-rejection")
async def send_rejection(request: RejectionRequest):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_user, smtp_password]):
        raise HTTPException(status_code=500, detail="SMTP credentials not configured.")

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        for recipient_email in request.emails:
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = recipient_email
            msg["Subject"] = f"Update on your application for {request.job_title}"

            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <p>Dear Candidate,</p>
                <p>Thank you for giving us the opportunity to consider your application for the <strong>{request.job_title}</strong> position.</p>
                <p>We have reviewed your profile, and while we were impressed with your qualifications, we have decided to proceed with other candidates who more closely align with our current requirements.</p>
                <p>We will keep your resume in our database and may contact you if a suitable opening arises in the future.</p>
                <p>We wish you the best in your job search.</p>
                <br>
                <p>Best Regards,<br><strong>Talent Acquisition Team</strong><br>RecruitAI</p>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, "html"))
            server.send_message(msg)

        server.quit()
        return {"status": "success", "message": f"Sent rejection to {len(request.emails)} candidates"}
    except Exception as e:
        logger.error(f"SMTP Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-assessment/{token}")
async def get_assessment(token: str):
    db = _get_db()
    assessment = next((a for a in db["assessments"] if a["token"] == token), None)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return {
        "mcqs": assessment.get("mcqs", []),
        "coding": assessment.get("coding_questions", []),
        "job_title": assessment["job_title"],
    }


@router.post("/submit-assessment")
async def submit_assessment(data: dict):
    try:
        db = _get_db()
        db["submissions"].append(
            {
                "token": data["token"],
                "email": data["email"],
                "mcq_score": data.get("mcq_score", 0),
                "mcq_total": data.get("mcq_total", 0),
                "coding_score": data.get("coding_score", 0),
                "coding_total": data.get("coding_total", 0),
                "timestamp": time.time(),
                "suspicious": data.get("suspicious", "Normal"),
            }
        )
        _save_db(db)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-analytics")
async def get_analytics():
    return _get_db()


@router.delete("/delete-assessment/{token}")
async def delete_assessment(token: str):
    db = _get_db()
    db["assessments"] = [a for a in db["assessments"] if a["token"] != token]
    db["submissions"] = [s for s in db["submissions"] if s["token"] != token]
    _save_db(db)
    return {"status": "success"}
