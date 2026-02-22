"""
Custom exception classes for PaperClip application.
Provides structured error handling throughout the application.
"""
from typing import Any, Dict, Optional


class PaperClipException(Exception):
    """
    Base exception class for all PaperClip exceptions.
    All custom exceptions should inherit from this.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "PAPERCLIP_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(PaperClipException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        status_code: int = 422,
    ):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status_code,
            details=details,
        )


class AuthenticationError(PaperClipException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
        )


class AuthorizationError(PaperClipException):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
        )


class NotFoundError(PaperClipException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str = "Resource"):
        super().__init__(
            message=f"{resource} not found",
            error_code="NOT_FOUND",
            status_code=404,
            details={"resource": resource},
        )


class ConflictError(PaperClipException):
    """Raised when a resource already exists."""

    def __init__(self, message: str, resource: Optional[str] = None):
        details = {"resource": resource} if resource else {}
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=details,
        )


class ResearchToolError(PaperClipException):
    """Raised when a research tool fails."""

    def __init__(
        self,
        message: str,
        tool_name: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        merged_details = {"tool": tool_name}
        if details:
            merged_details.update(details)
        
        super().__init__(
            message=message,
            error_code="RESEARCH_TOOL_ERROR",
            status_code=status_code,
            details=merged_details,
        )


class LLMError(PaperClipException):
    """Raised when LLM service fails."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        status_code: int = 500,
    ):
        details = {"provider": provider} if provider else {}
        super().__init__(
            message=message,
            error_code="LLM_ERROR",
            status_code=status_code,
            details=details,
        )


class DatabaseError(PaperClipException):
    """Raised when database operations fail."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        status_code: int = 500,
    ):
        details = {"operation": operation} if operation else {}
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status_code,
            details=details,
        )


class RateLimitError(PaperClipException):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after": retry_after},
        )


class ExternalAPIError(PaperClipException):
    """Raised when external API call fails."""

    def __init__(
        self,
        message: str,
        api_name: str,
        status_code: int = 503,
        details: Optional[Dict[str, Any]] = None,
    ):
        merged_details = {"api": api_name}
        if details:
            merged_details.update(details)
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_API_ERROR",
            status_code=status_code,
            details=merged_details,
        )


class ConfigurationError(PaperClipException):
    """Raised when application configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=500,
        )


class TimeoutError(PaperClipException):
    """Raised when an operation times out."""

    def __init__(
        self,
        message: str,
        timeout_seconds: int,
        operation: Optional[str] = None,
    ):
        details = {
            "timeout_seconds": timeout_seconds,
        }
        if operation:
            details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="TIMEOUT",
            status_code=504,
            details=details,
        )


class InvalidStateError(PaperClipException):
    """Raised when application is in an invalid state."""

    def __init__(self, message: str, current_state: Optional[str] = None):
        details = {"current_state": current_state} if current_state else {}
        super().__init__(
            message=message,
            error_code="INVALID_STATE",
            status_code=500,
            details=details,
        )
