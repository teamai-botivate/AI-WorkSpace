"""
Botivate AI Workspace — Main Application

Single FastAPI entry point that:
  1. Loads configuration
  2. Discovers and mounts agent plugins
  3. Serves the agent registry API
  4. Provides health check endpoints
  5. Serves static files for agents that have them
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings, load_workspace_config, save_workspace_config, is_setup_completed, PROJECT_ROOT
from .plugin_loader import load_agents, AGENTS_DIR
from .core.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-30s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("botivate.main")

# Agent registry — populated at startup
agent_registry: list[dict] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global agent_registry

    logger.info("=" * 60)
    logger.info("  BOTIVATE AI WORKSPACE — Starting Up")
    logger.info("=" * 60)

    settings = get_settings()
    logger.info(f"App: {settings.app_name}")
    logger.info(f"URL: {settings.app_url}")

    # Ensure data directories exist
    (PROJECT_ROOT / "data" / "chroma").mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "data" / "uploads").mkdir(parents=True, exist_ok=True)

    # Initialize shared database tables
    await init_db()

    # Load agent plugins
    agent_registry = load_agents(app)

    # Mount static files for agents that have a static/ folder
    for agent_dir in AGENTS_DIR.iterdir():
        if not agent_dir.is_dir():
            continue
        static_dir = agent_dir / "static"
        if static_dir.exists() and static_dir.is_dir():
            mount_path = f"/static/agents/{agent_dir.name}"
            app.mount(mount_path, StaticFiles(directory=str(static_dir), html=True), name=f"static_{agent_dir.name}")
            logger.info(f"Mounted static files: {mount_path}/")

    logger.info("=" * 60)
    logger.info("  BOTIVATE AI WORKSPACE — Ready")
    logger.info("=" * 60)

    yield

    logger.info("Botivate AI Workspace shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Botivate AI Workspace",
    description="Unified AI Agent Platform — White-Label, Plugin-Based",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────
# Core API Routes
# ─────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """System health check."""
    return {"status": "healthy", "service": "botivate-workspace"}


@app.get("/api/config")
async def get_workspace_config():
    """Return workspace configuration (branding, features, setup status)."""
    config = load_workspace_config()
    return {
        "company": config.get("company", {}),
        "features": config.get("features", {}),
        "setup_completed": is_setup_completed(),
    }


@app.post("/api/setup")
async def run_setup(request: Request):
    """First-time company setup — saves branding to workspace.config.json."""
    body = await request.json()
    company_data = body.get("company", {})

    # Validate required fields
    name = company_data.get("name", "").strip()
    if not name:
        return JSONResponse(status_code=400, content={"error": "Company name is required"})

    # Load current config and merge
    config = load_workspace_config()
    config["company"] = {
        "name": name,
        "tagline": company_data.get("tagline", "").strip(),
        "logo": company_data.get("logo", "/assets/logo.png"),
        "favicon": company_data.get("favicon", "/assets/favicon.ico"),
        "primaryColor": company_data.get("primaryColor", "#2563eb"),
        "accentColor": company_data.get("accentColor", "#06b6d4"),
        "mode": company_data.get("mode", "light"),
    }
    config["setup_completed"] = True

    save_workspace_config(config)
    logger.info(f"Setup completed for company: {name}")

    return {
        "message": "Setup completed successfully",
        "company": config["company"],
    }


@app.get("/api/agents")
async def get_agents():
    """Return the registry of all discovered agents and their status."""
    return {
        "agents": agent_registry,
        "total": len(agent_registry),
        "active": sum(1 for a in agent_registry if a["status"] == "active"),
    }


@app.get("/api/agents/{agent_name}/health")
async def agent_health(agent_name: str):
    """Check health of a specific agent."""
    for agent in agent_registry:
        if agent["name"] == agent_name:
            return {
                "agent": agent_name,
                "status": agent["status"],
                "version": agent.get("version", "unknown"),
            }
    return JSONResponse(
        status_code=404,
        content={"error": f"Agent '{agent_name}' not found"},
    )


# ─────────────────────────────────────────────────
# Global Exception Handler
# ─────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions — never crash the whole server."""
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )
