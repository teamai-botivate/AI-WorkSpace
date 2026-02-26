"""
Botivate Gateway — Configuration Loader
Reads the master workspace.config.json dynamically.
"""

import json
import os
from functools import lru_cache
from typing import Any, Dict

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config",
    "workspace.config.json",
)


def load_config() -> Dict[str, Any]:
    """Load workspace config from disk (always fresh read)."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Workspace config not found at: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_agent_by_id(agent_id: str) -> Dict[str, Any] | None:
    """Find an agent config by its ID."""
    config = load_config()
    for agent in config.get("agents", []):
        if agent["id"] == agent_id:
            return agent
    return None


def get_active_agents() -> list[Dict[str, Any]]:
    """Return only agents with status 'active'."""
    config = load_config()
    return [a for a in config.get("agents", []) if a.get("status") == "active"]
