"""
Google Sheets authentication helper.
"""

import os

import gspread

from config import SPREADSHEET_ACTIVITY_URL, SPREADSHEET_REPORT_URL
from models.log_level import LogLevel
from utils.logger import log_event


def get_report_worksheet(sheet_name: str = "Rolling total"):
    """Authenticate and fetch a fresh worksheet object per execution by tab name."""
    if not SPREADSHEET_REPORT_URL:
        log_event(
            None,
            LogLevel.CRITICAL,
            "SPREADSHEET_REPORT_URL is missing from environment variables (.env).",
        )
        raise ValueError(
            "SPREADSHEET_REPORT_URL is missing from environment variables (.env)."
        )

    base_dir = os.path.dirname(os.path.dirname(__file__))
    credentials_path = os.path.join(base_dir, "credentials.json")

    if not os.path.exists(credentials_path):
        log_event(
            None,
            LogLevel.CRITICAL,
            f"Google Service Account file not found at: {credentials_path}",
        )
        raise FileNotFoundError(
            f"Missing Google Sheets credentials file at {credentials_path}"
        )

    try:
        client = gspread.service_account(filename=credentials_path)
        sheet = client.open_by_url(SPREADSHEET_REPORT_URL)
        return sheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        log_event(
            None,
            LogLevel.ERROR,
            f"Worksheet '{sheet_name}' not found in target Google Sheet.",
        )
        raise
    except Exception as exc:
        log_event(
            None,
            LogLevel.ERROR,
            f"Failed to authenticate or fetch Google Sheet: {exc}",
            exc=exc,
        )
        raise


def get_activity_worksheet(sheet_name: str = "Activity_Pull"):
    """Authenticate and fetch a fresh worksheet object per execution by tab name."""
    if not SPREADSHEET_ACTIVITY_URL:
        log_event(
            None,
            LogLevel.CRITICAL,
            "SPREADSHEET_ACTIVITY_URL is missing from environment variables (.env).",
        )
        raise ValueError(
            "SPREADSHEET_ACTIVITY_URL is missing from environment variables (.env)."
        )

    base_dir = os.path.dirname(os.path.dirname(__file__))
    credentials_path = os.path.join(base_dir, "credentials.json")

    if not os.path.exists(credentials_path):
        log_event(
            None,
            LogLevel.CRITICAL,
            f"Google Service Account file not found at: {credentials_path}",
        )
        raise FileNotFoundError(
            f"Missing Google Sheets credentials file at {credentials_path}"
        )

    try:
        client = gspread.service_account(filename=credentials_path)
        sheet = client.open_by_url(SPREADSHEET_ACTIVITY_URL)
        return sheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        log_event(
            None,
            LogLevel.ERROR,
            f"Worksheet '{sheet_name}' not found in target Google Sheet.",
        )
        raise
    except Exception as exc:
        log_event(
            None,
            LogLevel.ERROR,
            f"Failed to authenticate or fetch Google Sheet: {exc}",
            exc=exc,
        )
        raise
