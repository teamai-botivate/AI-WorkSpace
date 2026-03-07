"""
HR Support Agent — Plugin Entry Point

Exports a single `router` that the plugin_loader mounts at /api/hr_support/
"""

from fastapi import APIRouter

from .routers.company_router import router as company_router
from .routers.auth_router import router as auth_router
from .routers.chat_router import router as chat_router
from .routers.approval_router import router as approval_router, notifications_router

router = APIRouter()

# Mount sub-routers (prefixes are already set inside each router file)
router.include_router(company_router)
router.include_router(auth_router)
router.include_router(chat_router)
router.include_router(approval_router)
router.include_router(notifications_router)


@router.get("/health")
async def agent_health():
    """Agent-level health check."""
    return {"status": "healthy", "agent": "hr_support", "version": "1.0.0"}
