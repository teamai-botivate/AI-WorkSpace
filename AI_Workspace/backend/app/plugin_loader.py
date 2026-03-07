"""
Botivate AI Workspace — Plugin Loader

Discovers, validates, and mounts agent plugins at startup.
Each agent lives in backend/app/agents/{agent_name}/ and must have:
  - agent.json  (metadata, required env keys, version)
  - __init__.py (exports `router` — a FastAPI APIRouter)

The loader:
  1. Scans the agents/ directory for valid plugin folders
  2. Reads agent.json and checks required_env_keys against settings
  3. Imports the agent's router from __init__.py
  4. Mounts it under /api/{agent_name}/
  5. Builds a registry accessible via GET /api/agents
"""

import json
import importlib
import logging
import traceback
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from .config import get_settings, load_workspace_config

logger = logging.getLogger("botivate.plugin_loader")

AGENTS_DIR = Path(__file__).resolve().parent / "agents"


def _validate_env_keys(required_keys: list[str], settings) -> tuple[bool, list[str]]:
    """Check that all required environment keys have non-empty values."""
    missing = []
    for key in required_keys:
        attr_name = key.lower()
        value = getattr(settings, attr_name, None)
        if not value:
            missing.append(key)
    return len(missing) == 0, missing


def discover_agents() -> list[dict[str, Any]]:
    """Scan agents/ directory and return metadata for all valid agents."""
    agents = []
    if not AGENTS_DIR.exists():
        logger.warning(f"Agents directory not found: {AGENTS_DIR}")
        return agents

    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue
        if agent_dir.name.startswith("_"):
            continue

        agent_json_path = agent_dir / "agent.json"
        init_path = agent_dir / "__init__.py"

        if not agent_json_path.exists():
            logger.warning(f"Skipping {agent_dir.name}: no agent.json found")
            continue
        if not init_path.exists():
            logger.warning(f"Skipping {agent_dir.name}: no __init__.py found")
            continue

        try:
            with open(agent_json_path, "r", encoding="utf-8") as f:
                agent_meta = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Skipping {agent_dir.name}: invalid agent.json — {e}")
            continue

        agent_meta["_dir_name"] = agent_dir.name
        agent_meta["_dir_path"] = str(agent_dir)
        agents.append(agent_meta)

    return agents


def load_agents(app: FastAPI) -> list[dict[str, Any]]:
    """
    Discover, validate, and mount all agent plugins.
    Returns the agent registry (list of loaded agent info).
    """
    settings = get_settings()
    workspace_config = load_workspace_config()
    config_agents = workspace_config.get("agents", {})

    discovered = discover_agents()
    registry: list[dict[str, Any]] = []

    for agent_meta in discovered:
        agent_name = agent_meta["_dir_name"]
        display_name = agent_meta.get("name", agent_name)

        # Check workspace.config.json for enabled/disabled
        agent_config = config_agents.get(agent_name, {})
        if agent_config.get("enabled") is False:
            logger.info(f"Agent '{display_name}' is disabled in workspace.config.json — skipping")
            registry.append({
                "name": agent_name,
                "display_name": agent_config.get("displayName", display_name),
                "status": "disabled",
                "description": agent_meta.get("description", ""),
                "version": agent_meta.get("version", "0.1.0"),
            })
            continue

        # Check if agent.json itself has enabled: false
        if agent_meta.get("enabled") is False:
            logger.info(f"Agent '{display_name}' is disabled in agent.json — skipping")
            registry.append({
                "name": agent_name,
                "display_name": display_name,
                "status": "disabled",
                "description": agent_meta.get("description", ""),
                "version": agent_meta.get("version", "0.1.0"),
            })
            continue

        # Validate required environment keys
        required_keys = agent_meta.get("required_env_keys", [])
        keys_ok, missing_keys = _validate_env_keys(required_keys, settings)
        if not keys_ok:
            logger.warning(
                f"Agent '{display_name}' skipped — missing env keys: {', '.join(missing_keys)}"
            )
            registry.append({
                "name": agent_name,
                "display_name": display_name,
                "status": "missing_credentials",
                "missing_keys": missing_keys,
                "description": agent_meta.get("description", ""),
                "version": agent_meta.get("version", "0.1.0"),
            })
            continue

        # Import and mount the agent's router
        try:
            module_path = f"backend.app.agents.{agent_name}"
            module = importlib.import_module(module_path)
            router = getattr(module, "router", None)

            if router is None:
                logger.error(f"Agent '{display_name}' has no 'router' in __init__.py — skipping")
                registry.append({
                    "name": agent_name,
                    "display_name": display_name,
                    "status": "error",
                    "error": "No router exported from __init__.py",
                    "description": agent_meta.get("description", ""),
                    "version": agent_meta.get("version", "0.1.0"),
                })
                continue

            # Mount under /api/{agent_name}/
            prefix = f"/api/{agent_name}"
            app.include_router(router, prefix=prefix, tags=[display_name])
            logger.info(f"Loaded agent '{display_name}' v{agent_meta.get('version', '?')} at {prefix}/")

            # Use display name from workspace config if available
            final_display_name = agent_config.get("displayName", display_name)
            final_description = agent_config.get("description", agent_meta.get("description", ""))
            final_icon = agent_config.get("icon", agent_meta.get("icon", "Bot"))
            final_gradient = agent_config.get("gradient", agent_meta.get("gradient", ["#6366f1", "#4f46e5"]))
            final_category = agent_config.get("category", agent_meta.get("category", "General"))
            final_features = agent_config.get("features", agent_meta.get("features", []))

            registry.append({
                "name": agent_name,
                "display_name": final_display_name,
                "status": "active",
                "version": agent_meta.get("version", "0.1.0"),
                "description": final_description,
                "icon": final_icon,
                "gradient": final_gradient,
                "category": final_category,
                "features": final_features,
                "api_prefix": prefix,
            })

        except Exception as e:
            logger.error(f"Failed to load agent '{display_name}': {e}")
            logger.debug(traceback.format_exc())
            registry.append({
                "name": agent_name,
                "display_name": display_name,
                "status": "error",
                "error": str(e),
                "description": agent_meta.get("description", ""),
                "version": agent_meta.get("version", "0.1.0"),
            })

    # Summary log
    active = sum(1 for a in registry if a["status"] == "active")
    total = len(registry)
    logger.info(f"Plugin loader: {active}/{total} agents loaded successfully")

    return registry
