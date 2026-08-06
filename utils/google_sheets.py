"""
Google Sheets authentication helper.
"""

import os
import gspread


def get_worksheet(sheet_name: str = "Rolling total"):
    """Authenticate and fetch a fresh worksheet object per execution by tab name."""
    spreadsheet_url = os.getenv("SPREADSHEET_URL")
    if not spreadsheet_url:
        raise ValueError("SPREADSHEET_URL is missing from environment variables (.env).")

    base_dir = os.path.dirname(os.path.dirname(__file__))
    credentials_path = os.path.join(base_dir, "credentials.json")
    client = gspread.service_account(filename=credentials_path)
    sheet = client.open_by_url(spreadsheet_url)
    return sheet.worksheet(sheet_name)