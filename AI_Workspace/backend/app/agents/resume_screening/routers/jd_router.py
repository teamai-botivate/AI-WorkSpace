"""
Resume Screening — JD Generator Router

Ported from original Resume-Screening-Agent/JD_Generator/backend/main.py + agent.py.
Uses OpenAI GPT-4o to generate professional, ATS-friendly Job Descriptions.
"""

import os
import json
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from ..core.config import get_settings

logger = logging.getLogger("JDGenerator")

router = APIRouter()

settings = get_settings()


class JDRequest(BaseModel):
    companyName: str
    companyType: str
    industry: str
    location: str
    roleTitle: str
    experience: str
    employmentType: str
    workMode: str
    salary: str


async def generate_jd_ai(data: dict) -> str:
    """AI Agent to generate a professional, ATS-friendly JD."""
    client = OpenAI(api_key=settings.openai_api_key)

    prompt = f"""
    You are an expert HR Specialist and Technical Recruiter. 
    Generate a professional and ATS-friendly Job Description based on the following structured input:

    ----------------------------
    COMPANY DETAILS
    ----------------------------
    Company Name: {data['companyName']}
    Company Type: {data['companyType']}
    Industry: {data['industry']}
    Location: {data['location']}

    ----------------------------
    ROLE IDENTIFICATION
    ----------------------------
    Role Title: {data['roleTitle']}
    Experience Level: {data['experience']}
    Employment Type: {data['employmentType']}
    Work Mode: {data['workMode']}
    Offered Salary: {data['salary']} Lakhs per Annum (LPA)

    ----------------------------
    INTELLIGENT ANALYSIS REQUIREMENTS
    ----------------------------
    - Analyze the role and industry carefully.
    - Automatically determine all the required Key Skills and modern Tech Stack based on market standards.
    - Do NOT rely on pre-provided skills (infer them from the role title and industry).
    - Adjust responsibilities and tools based on experience level ({data['experience']}).
    - Mention the salary of {data['salary']} LPA clearly as the first point in the compensation section.
    - Ensure the JD is ATS-friendly.

    ----------------------------
    OUTPUT FORMAT (MUST FOLLOW THIS EXACTLY)
    ----------------------------
    1. COMPANY NAME: [Name]
    2. JOB TITLE: [Title] ([Experience])
    3. ROLE SUMMARY: (2-3 lines context)
    4. KEY RESPONSIBILITIES: (5-7 bullet points)
    5. REQUIRED SKILLS: (Bulleted list)
    6. TECH STACK: (Separately mentioned list)
    7. PREFERRED SKILLS: (Bulleted list)
    8. COMPENSATION & BENEFITS (MANDATORY: Include "{data['salary']} LPA"): (Include Salary and other perks)
    9. CLOSING LINE: (Professional call to action)

    CONSTRAINTS:
    - YOU MUST INCLUDE THE SALARY OF {data['salary']} LPA IN SECTION 8.
    - Keep it concise (under 250 words total).
    - Use professional, punchy language.
    - MIMITIC KEYWORD DENSITY: Ensure the 'Required Skills' and 'Tech Stack' sections are keyword-rich to help with ATS parsing.
    - Maintain the numbered structure (1-9).
    - Response should only contain the JD text.
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional JD writer robot."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error generating JD: {str(e)}"


@router.post("/generate-jd")
async def generate_jd_endpoint(request: JDRequest):
    logger.info(f"Received JD Generation Request for Role: {request.roleTitle} at {request.companyName}")
    try:
        jd_text = await generate_jd_ai(request.model_dump())
        return {"status": "success", "jd": jd_text}
    except Exception as e:
        logger.error(f"Error during JD Generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
