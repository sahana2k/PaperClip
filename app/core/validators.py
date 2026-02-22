"""
Input validation utilities for PaperClip.
Provides functions and Pydantic validators for ensuring data integrity.
"""
import re
from typing import Optional
from pydantic import validator, field_validator, BaseModel


class QueryValidator(BaseModel):
    """Validates research query parameters."""

    query: str
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query string."""
        if not v:
            raise ValueError("Query cannot be empty")
        
        if len(v) < 3:
            raise ValueError("Query must be at least 3 characters long")
        
        if len(v) > 500:
            raise ValueError("Query cannot exceed 500 characters")
        
        # Remove leading/trailing whitespace
        v = v.strip()
        
        # Check for SQL injection patterns (basic check)
        dangerous_patterns = [
            r"(?i)(union|select|insert|update|delete|drop|create|alter)",
            r"(?i)(script|javascript|onerror|onload)",
            r"[;\"'\\]",  # Common injection characters
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v):
                raise ValueError("Query contains invalid characters or patterns")
        
        return v


class TopicValidator(BaseModel):
    """Validates research topic parameters."""

    topic: str
    
    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate topic string."""
        if not v:
            raise ValueError("Topic cannot be empty")
        
        if len(v) < 3:
            raise ValueError("Topic must be at least 3 characters long")
        
        if len(v) > 300:
            raise ValueError("Topic cannot exceed 300 characters")
        
        v = v.strip()
        return v


class UniversityValidator(BaseModel):
    """Validates university name parameters."""

    university: str
    
    @field_validator("university")
    @classmethod
    def validate_university(cls, v: str) -> str:
        """Validate university name."""
        if not v:
            raise ValueError("University name cannot be empty")
        
        if len(v) < 2:
            raise ValueError("University name must be at least 2 characters long")
        
        if len(v) > 200:
            raise ValueError("University name cannot exceed 200 characters")
        
        v = v.strip()
        
        # Check for obviously invalid patterns
        if re.search(r"[<>\"'%;()&+]", v):
            raise ValueError("University name contains invalid characters")
        
        return v


class UserIdValidator(BaseModel):
    """Validates user ID parameters."""

    user_id: str
    
    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user ID."""
        if not v:
            raise ValueError("User ID cannot be empty")
        
        if len(v) < 3:
            raise ValueError("User ID must be at least 3 characters long")
        
        if len(v) > 100:
            raise ValueError("User ID cannot exceed 100 characters")
        
        v = v.strip()
        
        # Allow alphanumeric, underscore, hyphen, and dot
        if not re.match(r"^[a-zA-Z0-9_.-]+$", v):
            raise ValueError(
                "User ID can only contain letters, numbers, underscore, hyphen, and dot"
            )
        
        return v


class CommandValidator(BaseModel):
    """Validates command parameters."""

    command: Optional[str] = None
    
    @field_validator("command")
    @classmethod
    def validate_command(cls, v: Optional[str]) -> Optional[str]:
        """Validate command string."""
        if v is None:
            return None
        
        valid_commands = [
            "domain_discovery",
            "paper_summarizer",
            "professor_finder",
            "dataset_hub",
            "pretrained_models",
            "generate_code",
        ]
        
        if v not in valid_commands:
            raise ValueError(
                f"Invalid command. Must be one of: {', '.join(valid_commands)}"
            )
        
        return v


class ModelNameValidator(BaseModel):
    """Validates model name parameters."""

    model_name: Optional[str] = None
    
    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate model name."""
        if v is None:
            return None
        
        if len(v) < 2:
            raise ValueError("Model name must be at least 2 characters long")
        
        if len(v) > 200:
            raise ValueError("Model name cannot exceed 200 characters")
        
        v = v.strip()
        return v


class EmailValidator(BaseModel):
    """Validates email address parameters."""

    email: str
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email address."""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email address format")
        
        if len(v) > 255:
            raise ValueError("Email address cannot exceed 255 characters")
        
        return v.lower().strip()


class PaginationValidator(BaseModel):
    """Validates pagination parameters."""

    skip: int = 0
    limit: int = 10
    
    @field_validator("skip")
    @classmethod
    def validate_skip(cls, v: int) -> int:
        """Validate skip parameter."""
        if v < 0:
            raise ValueError("skip must be a non-negative integer")
        
        if v > 10000:
            raise ValueError("skip cannot exceed 10000")
        
        return v
    
    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """Validate limit parameter."""
        if v < 1:
            raise ValueError("limit must be at least 1")
        
        if v > 100:
            raise ValueError("limit cannot exceed 100")
        
        return v


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input by removing potentially dangerous characters.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Truncate if too long
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace("\x00", "")
    
    # Remove control characters except newlines and tabs
    text = "".join(
        char for char in text 
        if ord(char) >= 32 or char in "\n\t"
    )
    
    return text.strip()


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid URL format
    """
    url_pattern = (
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$"
    )
    
    return bool(re.match(url_pattern, url, re.IGNORECASE))
