"""
Configuration management for PaperClip application.
Uses Pydantic Settings for environment variable validation and type safety.
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ===== Application Settings =====
    app_name: str = Field(default="Paperclip", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # ===== Server Settings =====
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    workers: int = Field(default=1, env="WORKERS")

    # ===== LLM & AI Services =====
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    cohere_api_key: Optional[str] = Field(default=None, env="COHERE_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    langchain_api_key: Optional[str] = Field(default=None, env="LANGCHAIN_API_KEY")
    langchain_tracing_v2: bool = Field(default=False, env="LANGCHAIN_TRACING_V2")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")

    # ===== External API Tokens =====
    github_token: str = Field(default="", env="GITHUB_TOKEN")
    semantic_scholar_api_key: Optional[str] = Field(default=None, env="SEMANTIC_SCHOLAR_API_KEY")

    # ===== Database Settings =====
    database_url: str = Field(
        default="sqlite:///./paperclip.db", 
        env="DATABASE_URL"
    )
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    database_pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    database_pool_pre_ping: bool = Field(default=True, env="DATABASE_POOL_PRE_PING")

    # ===== Security Settings =====
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # ===== CORS Settings =====
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    # ===== Rate Limiting =====
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_strategy: str = Field(default="moving-window", env="RATE_LIMIT_STRATEGY")

    # ===== Caching (Redis) =====
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    cache_enabled: bool = Field(default=False, env="CACHE_ENABLED")

    # ===== Monitoring & Observability =====
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_enabled: bool = Field(default=False, env="PROMETHEUS_ENABLED")
    jaeger_enabled: bool = Field(default=False, env="JAEGER_ENABLED")
    jaeger_agent_host: str = Field(default="localhost", env="JAEGER_AGENT_HOST")
    jaeger_agent_port: int = Field(default=6831, env="JAEGER_AGENT_PORT")

    # ===== Feature Flags =====
    feature_async_processing: bool = Field(default=True, env="FEATURE_ASYNC_PROCESSING")
    feature_caching: bool = Field(default=False, env="FEATURE_CACHING")
    feature_websocket_chat: bool = Field(default=False, env="FEATURE_WEBSOCKET_CHAT")

    # ===== External Services URLs =====
    arxiv_api_url: str = Field(
        default="http://export.arxiv.org/api/query",
        env="ARXIV_API_URL"
    )
    huggingface_api_url: str = Field(
        default="https://api-inference.huggingface.co/models",
        env="HUGGINGFACE_API_URL"
    )

    # ===== File Upload =====
    max_upload_size_mb: int = Field(default=10, env="MAX_UPLOAD_SIZE_MB")
    upload_directory: str = Field(default="./uploads", env="UPLOAD_DIRECTORY")

    # ===== Email Configuration =====
    smtp_server: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    sender_email: str = Field(default="noreply@paperclip.com", env="SENDER_EMAIL")

    # ===== Frontend Configuration =====
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    frontend_host: str = Field(default="localhost", env="FRONTEND_HOST")
    frontend_port: int = Field(default=3000, env="FRONTEND_PORT")

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    # ===== Validators =====
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is a valid Python logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()

    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the expected values."""
        valid_envs = ["development", "staging", "production", "testing"]
        if v.lower() not in valid_envs:
            raise ValueError(f"environment must be one of {valid_envs}")
        return v.lower()

    @validator("port")
    def validate_port(cls, v: int) -> int:
        """Validate port is within valid range."""
        if not (1 <= v <= 65535):
            raise ValueError("port must be between 1 and 65535")
        return v

    @validator("openai_api_key")
    def validate_openai_key(cls, v: str) -> str:
        """Ensure OpenAI API key is provided in production."""
        if not v or v == "your-openai-key-here":
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("⚠️ OPENAI_API_KEY not set - some features will not work")
        return v

    @validator("cohere_api_key")
    def validate_cohere_key(cls, v: str) -> str:
        """Ensure Cohere API key is provided in production."""
        if not v or v == "your-cohere-api-key-here":
            # Warn but allow in development
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("⚠️ COHERE_API_KEY not set - some features will not work")
        return v

    @validator("github_token")
    def validate_github_token(cls, v: str) -> str:
        """Ensure GitHub token is provided in production."""
        if not v or v == "your-github-personal-access-token-here":
            # Warn but allow in development
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("⚠️ GITHUB_TOKEN not set - some features will not work")
        return v

    @validator("secret_key")
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is changed in production."""
        if v == "change-me-in-production":
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                "SECRET_KEY is still the default value. "
                "Change it in your .env file for production."
            )
        return v

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Global settings instance
settings = Settings()


def validate_settings() -> None:
    """
    Validate all critical settings are properly configured.
    Call this at application startup.
    """
    import logging
    logger = logging.getLogger(__name__)

    errors = []

    # Check at least one LLM provider is set
    if not settings.openai_api_key and not settings.cohere_api_key:
        errors.append("At least one LLM API key must be set (OPENAI_API_KEY or COHERE_API_KEY)")
    
    if not settings.github_token:
        logger.warning("⚠️ GITHUB_TOKEN not set - GitHub features will not work")

    # Check production settings
    if settings.is_production():
        if settings.debug:
            errors.append("DEBUG cannot be True in production")
        if settings.secret_key == "change-me-in-production":
            errors.append("SECRET_KEY must be changed for production")
        if "sqlite" in settings.database_url:
            errors.append("SQLite cannot be used in production. Use PostgreSQL.")

    if errors:
        error_msg = "\n".join(f"  ❌ {e}" for e in errors)
        logger.error(f"Configuration validation failed:\n{error_msg}")
        raise ValueError(f"Configuration errors:\n{error_msg}")
    
    logger.info("✅ Configuration validation passed")
