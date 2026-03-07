"""
Botivate AI Workspace — Configuration

Loads settings from .env file and workspace.config.json.
Provides a single Settings object and workspace config for the entire app.
"""

import json
import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings

# Project root = AI_Workspace/ (parent of backend/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE_CONFIG_PATH = PROJECT_ROOT / "workspace.config.json"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "Botivate AI Workspace"
    app_url: str = "http://localhost:8000"
    app_secret_key: str = "change-me"

    # Database
    database_url: str = f"sqlite+aiosqlite:///{PROJECT_ROOT / 'data' / 'workspace.db'}"

    # JWT
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    # LLM Providers
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    groq_api_key: str = ""
    huggingface_api_token: str = ""

    # Google
    google_service_account_json: str = str(PROJECT_ROOT / "credentials" / "google" / "service-account.json")
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"

    # SMTP
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # ChromaDB
    chroma_persist_dir: str = str(PROJECT_ROOT / "data" / "chroma")

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_workers: int = 2

    class Config:
        env_file = str(PROJECT_ROOT / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


def load_workspace_config() -> dict:
    """Load workspace.config.json from project root."""
    if WORKSPACE_CONFIG_PATH.exists():
        with open(WORKSPACE_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "company": {"name": "", "primaryColor": "#2563eb"},
        "agents": {},
        "features": {},
        "setup_completed": False,
    }


def save_workspace_config(config: dict) -> None:
    """Save workspace.config.json to project root."""
    with open(WORKSPACE_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def is_setup_completed() -> bool:
    """Check if the initial company setup has been done."""
    config = load_workspace_config()
    if config.get("setup_completed") is True:
        return True
    # Also consider setup done if company name was changed from default
    company_name = config.get("company", {}).get("name", "")
    return bool(company_name and company_name != "Botivate" and company_name.strip())


def get_agent_data_dir(agent_name: str) -> Path:
    """Get the isolated data directory for an agent."""
    agent_dir = PROJECT_ROOT / "data" / "agents" / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)
    return agent_dir
