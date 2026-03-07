"""
Resume Screening — JD Service

AI-powered Job Description generation and analysis.
"""

import logging
import json

from ....core.llm import get_llm_service

logger = logging.getLogger("botivate.agents.resume_screening.jd")


class JDService:
    """Job Description generation and analysis using LLM."""

    async def generate_jd(
        self,
        title: str,
        company_name: str = "",
        department: str = "",
        experience_level: str = "mid",
        skills: list[str] | None = None,
        additional_context: str = "",
    ) -> dict:
        """Generate a structured job description using AI."""
        llm = get_llm_service()

        prompt = (
            f"Generate a professional job description for the following role:\n\n"
            f"Title: {title}\n"
            f"Company: {company_name or 'Not specified'}\n"
            f"Department: {department or 'Not specified'}\n"
            f"Experience Level: {experience_level}\n"
            f"Key Skills: {', '.join(skills) if skills else 'Not specified'}\n"
            f"Additional Context: {additional_context or 'None'}\n\n"
            "Generate the JD in JSON format with these fields:\n"
            '{"title": "", "summary": "", "responsibilities": ["..."], '
            '"requirements": ["..."], "nice_to_have": ["..."], '
            '"experience": "", "skills": ["..."], "benefits": ["..."]}'
        )

        response = await llm.chat(
            [{"role": "user", "content": prompt}],
            provider="groq",
        )

        # Try to parse JSON from response
        try:
            # Find JSON block in response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                jd_data = json.loads(response[json_start:json_end])
                return jd_data
        except json.JSONDecodeError:
            pass

        # Fallback: return raw text
        return {
            "title": title,
            "raw_text": response,
            "skills": skills or [],
        }

    async def analyze_jd(self, jd_text: str) -> dict:
        """Analyze a JD to extract structured information."""
        llm = get_llm_service()

        prompt = (
            "Analyze this job description and extract structured information.\n\n"
            f"JD:\n{jd_text[:3000]}\n\n"
            "Return a JSON object with:\n"
            '{"title": "", "key_skills": ["..."], "experience_years": 0, '
            '"education_level": "", "role_type": "full-time|part-time|contract", '
            '"seniority": "junior|mid|senior|lead", "key_responsibilities": ["..."]}'
        )

        response = await llm.chat(
            [{"role": "user", "content": prompt}],
            provider="groq",
        )

        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except json.JSONDecodeError:
            pass

        return {"raw_analysis": response}


# Singleton
_service = None


def get_jd_service() -> JDService:
    global _service
    if _service is None:
        _service = JDService()
    return _service
