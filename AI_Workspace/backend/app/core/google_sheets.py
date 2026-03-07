"""
Shared Google Sheets Service

Provides read/write access to Google Sheets using a service account.
Used by agents for data syncing (e.g., employee data, candidate tracking).
"""

import logging
from pathlib import Path
from functools import lru_cache

from ..config import get_settings

logger = logging.getLogger("botivate.core.google_sheets")


class GoogleSheetsService:
    """Google Sheets client using service account credentials."""

    def __init__(self):
        self.settings = get_settings()
        self._client = None

    @property
    def client(self):
        """Lazy-loaded gspread client."""
        if self._client is None:
            creds_path = Path(self.settings.google_service_account_json)
            if not creds_path.exists():
                raise FileNotFoundError(
                    f"Service account JSON not found at {creds_path}. "
                    "See credentials/README.md for setup."
                )
            import gspread
            from google.oauth2.service_account import Credentials

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.readonly",
            ]
            credentials = Credentials.from_service_account_file(str(creds_path), scopes=scopes)
            self._client = gspread.authorize(credentials)
        return self._client

    def open_spreadsheet(self, spreadsheet_id: str):
        """Open a spreadsheet by its ID."""
        return self.client.open_by_key(spreadsheet_id)

    def read_sheet(self, spreadsheet_id: str, sheet_name: str = "Sheet1") -> list[dict]:
        """Read all rows from a sheet as a list of dicts (header row = keys)."""
        spreadsheet = self.open_spreadsheet(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        return worksheet.get_all_records()

    def write_row(self, spreadsheet_id: str, row_data: list, sheet_name: str = "Sheet1"):
        """Append a row to the end of a sheet."""
        spreadsheet = self.open_spreadsheet(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        worksheet.append_row(row_data)

    def update_cell(
        self, spreadsheet_id: str, row: int, col: int, value, sheet_name: str = "Sheet1"
    ):
        """Update a single cell."""
        spreadsheet = self.open_spreadsheet(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        worksheet.update_cell(row, col, value)


@lru_cache()
def get_sheets_service() -> GoogleSheetsService:
    """Cached Google Sheets service instance."""
    return GoogleSheetsService()
