"""
Resume Screening Agent — Plugin Entry Point

Exports a single `router` that the plugin_loader mounts at /api/resume_screening/

Sub-routers:
  /screening  — Resume analysis pipeline (analyze, status, open_report)
  /jd         — JD Generator (generate-jd)
  /email      — Aptitude tests & candidate emailing
"""

from fastapi import APIRouter

from .routers.screening_router import router as screening_router
from .routers.jd_router import router as jd_router
from .routers.email_router import router as email_router

router = APIRouter()

router.include_router(screening_router, prefix="/screening", tags=["Resume Screening"])
router.include_router(jd_router, prefix="/jd", tags=["JD Generator"])
router.include_router(email_router, prefix="/email", tags=["Aptitude & Email"])


@router.get("/health")
async def agent_health():
    """Agent-level health check."""
    return {"status": "healthy", "agent": "resume_screening", "version": "1.0.0"}
