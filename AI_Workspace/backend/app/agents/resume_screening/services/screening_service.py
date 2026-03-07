"""
Resume Screening — Screening Service

Multi-stage resume evaluation pipeline:
  1. Text extraction (PDF/DOCX)
  2. Keyword matching
  3. Experience scoring
  4. Semantic similarity (embeddings)
  5. AI deep read (LLM analysis)
"""

import logging
import re
from pathlib import Path

from ....config import get_agent_data_dir

logger = logging.getLogger("botivate.agents.resume_screening.screening")


class ScreeningService:
    """Multi-stage resume screening pipeline."""

    # Scoring weights
    WEIGHTS = {
        "keyword": 0.25,
        "experience": 0.20,
        "education": 0.10,
        "semantic": 0.15,
        "ai_analysis": 0.30,
    }

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from a PDF file."""
        import pdfplumber
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text content from a DOCX file."""
        from docx import Document
        doc = Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX."""
        path = Path(file_path)
        if path.suffix.lower() == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif path.suffix.lower() in (".docx", ".doc"):
            return self.extract_text_from_docx(file_path)
        else:
            return path.read_text(encoding="utf-8", errors="ignore")

    def score_keywords(self, resume_text: str, required_skills: list[str]) -> float:
        """Score based on keyword/skill matches."""
        if not required_skills:
            return 0.5  # neutral if no skills specified
        resume_lower = resume_text.lower()
        matches = sum(1 for skill in required_skills if skill.lower() in resume_lower)
        return min(matches / len(required_skills), 1.0)

    def score_experience(self, resume_text: str, required_years: int = 0) -> float:
        """Score based on years of experience mentioned."""
        # Find year patterns like "5 years", "5+ years", etc.
        patterns = re.findall(r"(\d+)\+?\s*(?:years?|yrs?)", resume_text.lower())
        if not patterns:
            return 0.3  # Some experience assumed

        max_years = max(int(y) for y in patterns)
        if required_years <= 0:
            return min(max_years / 10, 1.0)
        return min(max_years / required_years, 1.0)

    def score_education(self, resume_text: str) -> float:
        """Score based on education level detected."""
        text_lower = resume_text.lower()
        if any(term in text_lower for term in ["phd", "doctorate", "ph.d"]):
            return 1.0
        if any(term in text_lower for term in ["master", "m.s.", "m.sc", "mba", "m.tech"]):
            return 0.85
        if any(term in text_lower for term in ["bachelor", "b.s.", "b.sc", "b.tech", "b.e."]):
            return 0.7
        if any(term in text_lower for term in ["diploma", "associate"]):
            return 0.5
        return 0.3

    async def ai_analysis(self, resume_text: str, jd_text: str) -> tuple[float, str]:
        """Use LLM for deep resume analysis against JD."""
        from ....core.llm import get_llm_service

        llm = get_llm_service()
        prompt = (
            "You are an expert HR recruiter. Analyze this resume against the job description.\n\n"
            f"JOB DESCRIPTION:\n{jd_text[:2000]}\n\n"
            f"RESUME:\n{resume_text[:3000]}\n\n"
            "Provide:\n"
            "1. A match score from 0.0 to 1.0\n"
            "2. Key strengths (2-3 bullet points)\n"
            "3. Key gaps (2-3 bullet points)\n"
            "4. Overall recommendation (Strongly Recommend / Recommend / Maybe / Pass)\n\n"
            "Format your response as:\n"
            "SCORE: <number>\n"
            "STRENGTHS:\n- ...\nGAPS:\n- ...\nRECOMMENDATION: <text>"
        )

        response = await llm.chat(
            [{"role": "user", "content": prompt}],
            provider="groq",
        )

        # Parse score from response
        score_match = re.search(r"SCORE:\s*([\d.]+)", response)
        score = float(score_match.group(1)) if score_match else 0.5
        score = max(0.0, min(1.0, score))

        return score, response

    async def screen_resume(
        self,
        resume_path: str,
        jd_text: str,
        required_skills: list[str] | None = None,
        required_years: int = 0,
    ) -> dict:
        """Run the full multi-stage screening pipeline."""
        resume_text = self.extract_text(resume_path)

        keyword_score = self.score_keywords(resume_text, required_skills or [])
        experience_score = self.score_experience(resume_text, required_years)
        education_score = self.score_education(resume_text)
        ai_score, ai_text = await self.ai_analysis(resume_text, jd_text)

        overall = (
            keyword_score * self.WEIGHTS["keyword"]
            + experience_score * self.WEIGHTS["experience"]
            + education_score * self.WEIGHTS["education"]
            + ai_score * (self.WEIGHTS["semantic"] + self.WEIGHTS["ai_analysis"])
        )

        return {
            "resume_text": resume_text,
            "scores": {
                "overall": round(overall, 3),
                "keyword": round(keyword_score, 3),
                "experience": round(experience_score, 3),
                "education": round(education_score, 3),
                "ai_analysis": round(ai_score, 3),
            },
            "ai_analysis_text": ai_text,
            "recommendation": (
                "Strongly Recommend" if overall >= 0.8
                else "Recommend" if overall >= 0.6
                else "Maybe" if overall >= 0.4
                else "Pass"
            ),
        }


# Singleton
_service = None


def get_screening_service() -> ScreeningService:
    global _service
    if _service is None:
        _service = ScreeningService()
    return _service
