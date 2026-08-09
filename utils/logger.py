"""
Structured JSONL Python Logger with Dynamic Guild-Based Paths and Auto-Cleanup.
"""

import sys
import json
import logging
from pathlib import Path
from config import DATA_ROOT
from logging.handlers import TimedRotatingFileHandler
from models.log_level import LogLevel

LOG_RETENTION_DAYS = 7


class JsonLineFormatter(logging.Formatter):
    """Formats log records as JSON strings for easy parsing in dashboard UIs."""

    def format(self, record: logging.LogRecord) -> str:
        log_object = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "guild_id": getattr(record, "guild_id", "system"),
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_object, ensure_ascii=False)


def _get_server_logger(guild_id: int | str | None) -> logging.Logger:
    """
    Dynamically gets or creates a standard Python logger that writes to
    {DATA_ROOT}/{guild_id}/logs/bot_log.jsonl
    """
    target_server = str(guild_id) if guild_id else "system"
    logger_name = f"bot_logger_{target_server}"
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        log_dir = Path(DATA_ROOT) / target_server / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        file_path = log_dir / "bot_log.jsonl"

        file_handler = TimedRotatingFileHandler(
            filename=file_path,
            when="midnight",
            utc=True,
            backupCount=LOG_RETENTION_DAYS,
            encoding="utf-8"
        )
        file_handler.suffix = "%Y-%m-%d.jsonl"
        file_handler.setFormatter(JsonLineFormatter())

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(fmt="%(levelname)s - %(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        )

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def log_event(
        guild_id: int | str | None,
        level: LogLevel,
        message: str,
        exc: Exception | None = None
) -> None:
    """Logs a structured message to target server logs and Docker console."""
    logger = _get_server_logger(guild_id)
    numeric_level = getattr(logging, level.value, logging.INFO)
    extra = {"guild_id": str(guild_id) if guild_id else "system"}
    logger.log(numeric_level, message, exc_info=exc, extra=extra)