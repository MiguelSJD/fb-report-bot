from enum import Enum

class LogLevel(str, Enum):
    """Enumeration of supported application log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return self.value