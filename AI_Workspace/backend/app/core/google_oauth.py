"""
Shared Google OAuth Service

Handles OAuth 2.0 flows for Gmail and other Google API access.
Manages token storage in credentials/tokens/.
"""

import json
import logging
from pathlib import Path
from functools import lru_cache

from ..config import get_settings, PROJECT_ROOT

logger = logging.getLogger("botivate.core.google_oauth")

TOKENS_DIR = PROJECT_ROOT / "credentials" / "tokens"


class GoogleOAuthService:
    """Google OAuth 2.0 helper for consent flows and token management."""

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    def __init__(self):
        self.settings = get_settings()
        TOKENS_DIR.mkdir(parents=True, exist_ok=True)

    def _get_client_config(self) -> dict:
        """Load OAuth client configuration."""
        return {
            "web": {
                "client_id": self.settings.google_oauth_client_id,
                "client_secret": self.settings.google_oauth_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.settings.google_oauth_redirect_uri],
            }
        }

    def get_authorization_url(self, state: str | None = None) -> str:
        """Generate the Google OAuth consent URL."""
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_config(
            self._get_client_config(),
            scopes=self.SCOPES,
            redirect_uri=self.settings.google_oauth_redirect_uri,
        )
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=state,
        )
        return auth_url

    def exchange_code(self, code: str, token_name: str = "default") -> dict:
        """Exchange authorization code for tokens and save them."""
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_config(
            self._get_client_config(),
            scopes=self.SCOPES,
            redirect_uri=self.settings.google_oauth_redirect_uri,
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials

        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": list(credentials.scopes) if credentials.scopes else self.SCOPES,
        }

        token_path = TOKENS_DIR / f"{token_name}.json"
        with open(token_path, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)

        logger.info(f"OAuth tokens saved: {token_path}")
        return token_data

    def get_credentials(self, token_name: str = "default"):
        """Load saved credentials from tokens directory."""
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        token_path = TOKENS_DIR / f"{token_name}.json"
        if not token_path.exists():
            return None

        with open(token_path, "r", encoding="utf-8") as f:
            token_data = json.load(f)

        credentials = Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get("token_uri"),
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=token_data.get("scopes"),
        )

        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            # Save refreshed token
            token_data["token"] = credentials.token
            with open(token_path, "w", encoding="utf-8") as f:
                json.dump(token_data, f, indent=2)

        return credentials

    def get_gmail_service(self, token_name: str = "default"):
        """Get an authenticated Gmail API service."""
        from googleapiclient.discovery import build

        credentials = self.get_credentials(token_name)
        if credentials is None:
            raise ValueError(f"No OAuth tokens found for '{token_name}'. Complete OAuth flow first.")
        return build("gmail", "v1", credentials=credentials)


@lru_cache()
def get_oauth_service() -> GoogleOAuthService:
    """Cached Google OAuth service instance."""
    return GoogleOAuthService()
