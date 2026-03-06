"""
Botivate Gateway — Central API Gateway
Serves workspace config, agent registry, and health checks.
All agent backends remain independent; this gateway orchestrates discovery.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

from app.config import load_config, get_agent_by_id, get_active_agents

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | GATEWAY | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("gateway")


# ── Lifespan ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config()
    workspace = config["workspace"]
    logger.info(f"🚀 {workspace['name']} Gateway v{workspace['version']} starting...")
    logger.info(f"📦 Registered agents: {len(config.get('agents', []))}")
    yield
    logger.info("Gateway shutting down.")


# ── App ───────────────────────────────────────────────────

config = load_config()
workspace_meta = config["workspace"]

app = FastAPI(
    title=f"{workspace_meta['name']} Gateway",
    description="Central API Gateway for the AI Workforce Portal",
    version=workspace_meta["version"],
    lifespan=lifespan,
)

# CORS
cors_origins = config.get("gateway", {}).get("corsOrigins", ["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes: Workspace Config ─────────────────────────────

@app.get("/api/config")
async def get_workspace_config():
    """Return the full workspace configuration (consumed by frontend)."""
    return load_config()


@app.get("/api/health")
async def gateway_health():
    """Gateway health check."""
    return {"status": "healthy", "service": "gateway"}


# ── Routes: Agent Registry ────────────────────────────────

@app.get("/api/agents")
async def list_agents():
    """List all registered agents with metadata."""
    return get_active_agents()


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get a specific agent's config."""
    agent = get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return agent


@app.get("/api/agents/{agent_id}/health")
async def check_agent_health(agent_id: str):
    """Check if an agent's backend is reachable."""
    agent = get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    backend = agent.get("backend", {})
    port = backend.get("port")
    health_endpoint = backend.get("healthCheck", "/docs")

    # Support deployed (remote) backends
    if backend.get("deployed") and backend.get("deployedUrl"):
        url = f"{backend['deployedUrl'].rstrip('/')}{health_endpoint}"
    else:
        url = f"http://localhost:{port}{health_endpoint}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            healthy = resp.status_code < 400
            return {
                "agent_id": agent_id,
                "healthy": healthy,
                "status": "running" if healthy else "error",
                "port": port,
                "url": url,
                "deployed": backend.get("deployed", False),
            }
    except httpx.ConnectError:
        return {
            "agent_id": agent_id,
            "healthy": False,
            "status": "offline",
            "port": port,
            "url": url,
            "deployed": backend.get("deployed", False),
        }
    except Exception as e:
        return {
            "agent_id": agent_id,
            "healthy": False,
            "status": "error",
            "port": port,
            "error": str(e),
            "deployed": backend.get("deployed", False),
        }


@app.get("/api/agents/health/all")
async def check_all_agents_health():
    """Check health of all active agents in parallel."""
    agents = get_active_agents()
    results = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        for agent in agents:
            backend = agent.get("backend", {})
            port = backend.get("port")
            health_endpoint = backend.get("healthCheck", "/docs")

            if backend.get("deployed") and backend.get("deployedUrl"):
                url = f"{backend['deployedUrl'].rstrip('/')}{health_endpoint}"
            else:
                url = f"http://localhost:{port}{health_endpoint}"

            try:
                resp = await client.get(url)
                results.append({
                    "agent_id": agent["id"],
                    "name": agent["name"],
                    "healthy": resp.status_code < 400,
                    "status": "running",
                    "port": port,
                    "deployed": backend.get("deployed", False),
                })
            except Exception:
                results.append({
                    "agent_id": agent["id"],
                    "name": agent["name"],
                    "healthy": False,
                    "status": "offline",
                    "port": port,
                    "deployed": backend.get("deployed", False),
                })

    return {
        "total": len(results),
        "healthy": sum(1 for r in results if r["healthy"]),
        "agents": results,
    }
