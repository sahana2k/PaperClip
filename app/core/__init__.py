"""Core module for PaperClip application."""

from app.core.config import Settings, settings, validate_settings
from app.core.exceptions import (
    PaperClipException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    ResearchToolError,
    LLMError,
    DatabaseError,
    RateLimitError,
    ExternalAPIError,
    ConfigurationError,
    TimeoutError,
    InvalidStateError,
)
from app.core.logger import setup_logging, get_logger, LoggerMixin

__all__ = [
    "Settings",
    "settings",
    "validate_settings",
    "PaperClipException",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "ResearchToolError",
    "LLMError",
    "DatabaseError",
    "RateLimitError",
    "ExternalAPIError",
    "ConfigurationError",
    "TimeoutError",
    "InvalidStateError",
    "setup_logging",
    "get_logger",
    "LoggerMixin",
]
