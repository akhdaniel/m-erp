"""
Production configuration settings and security hardening.
"""

import os
from typing import List, Optional
from pydantic import BaseModel, validator


class ProductionSettings(BaseModel):
    """Production-specific configuration settings."""
    
    # Application Settings
    project_name: str = "User Authentication Service"
    version: str = "1.0.0"
    description: str = "XERPIUM User Authentication Microservice"
    environment: str = "production"
    debug: bool = False
    
    # Security Settings
    secret_key: str = os.getenv("SECRET_KEY", "")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Database Settings
    database_url: str = os.getenv("DATABASE_URL", "")
    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    database_max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "30"))
    database_pool_timeout: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
    
    # Redis Settings
    redis_url: str = os.getenv("REDIS_URL", "")
    redis_pool_size: int = int(os.getenv("REDIS_POOL_SIZE", "10"))
    redis_timeout: int = int(os.getenv("REDIS_TIMEOUT", "5"))
    
    # Security & Rate Limiting
    rate_limiting_enabled: bool = os.getenv("RATE_LIMITING_ENABLED", "true").lower() == "true"
    rate_limit_auth_requests: str = os.getenv("RATE_LIMIT_AUTH", "5/minute")
    rate_limit_general_requests: str = os.getenv("RATE_LIMIT_GENERAL", "100/minute")
    rate_limit_admin_requests: str = os.getenv("RATE_LIMIT_ADMIN", "20/minute")
    
    # Account Security
    max_failed_login_attempts: int = int(os.getenv("MAX_FAILED_ATTEMPTS", "5"))
    account_lockout_duration_minutes: int = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))
    progressive_lockout_enabled: bool = os.getenv("PROGRESSIVE_LOCKOUT", "true").lower() == "true"
    
    # Password Policy
    password_min_length: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    password_max_length: int = int(os.getenv("PASSWORD_MAX_LENGTH", "128"))
    password_history_count: int = int(os.getenv("PASSWORD_HISTORY_COUNT", "5"))
    password_complexity_score: int = int(os.getenv("PASSWORD_MIN_COMPLEXITY", "60"))
    
    # Audit & Logging
    audit_logging_enabled: bool = os.getenv("AUDIT_LOGGING_ENABLED", "true").lower() == "true"
    audit_retention_days: int = int(os.getenv("AUDIT_RETENTION_DAYS", "90"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "json"  # json or text
    
    # CORS Settings
    allowed_origins: List[str] = []
    allowed_credentials: bool = True
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    allowed_headers: List[str] = ["*"]
    
    # SSL/TLS Settings
    force_https: bool = os.getenv("FORCE_HTTPS", "true").lower() == "true"
    hsts_max_age: int = int(os.getenv("HSTS_MAX_AGE", "31536000"))  # 1 year
    secure_cookies: bool = os.getenv("SECURE_COOKIES", "true").lower() == "true"
    
    # API Settings
    api_prefix: str = "/api"
    docs_enabled: bool = os.getenv("DOCS_ENABLED", "false").lower() == "true"
    openapi_url: Optional[str] = None if not os.getenv("DOCS_ENABLED", "false").lower() == "true" else "/openapi.json"
    
    # Monitoring & Health
    health_check_enabled: bool = True
    metrics_enabled: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN")
    
    # Service Discovery
    service_name: str = "user-auth-service"
    service_port: int = int(os.getenv("PORT", "8000"))
    service_host: str = os.getenv("HOST", "0.0.0.0")
    
    # External Services
    email_service_url: Optional[str] = os.getenv("EMAIL_SERVICE_URL")
    notification_service_url: Optional[str] = os.getenv("NOTIFICATION_SERVICE_URL")
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        """Validate secret key meets security requirements."""
        if not v:
            raise ValueError("SECRET_KEY environment variable is required in production")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL is provided."""
        if not v:
            raise ValueError("DATABASE_URL environment variable is required in production")
        if "sqlite" in v.lower():
            raise ValueError("SQLite is not recommended for production. Use PostgreSQL.")
        return v
    
    @validator("redis_url")
    def validate_redis_url(cls, v):
        """Validate Redis URL is provided."""
        if not v:
            raise ValueError("REDIS_URL environment variable is required in production")
        return v
    
    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse CORS allowed origins from environment."""
        if isinstance(v, str):
            origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
            return [origin.strip() for origin in origins if origin.strip()]
        return v or []
    
    @validator("allowed_origins")
    def validate_allowed_origins(cls, v):
        """Validate CORS origins are properly configured."""
        if not v:
            raise ValueError("ALLOWED_ORIGINS must be configured in production")
        for origin in v:
            if origin == "*":
                raise ValueError("Wildcard CORS origins (*) are not allowed in production")
        return v
    
    class Config:
        env_file = ".env.production"
        case_sensitive = False


def get_production_settings() -> ProductionSettings:
    """Get production settings with validation."""
    return ProductionSettings()


# Production security headers
PRODUCTION_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "X-Permitted-Cross-Domain-Policies": "none",
    "Clear-Site-Data": '"cache", "cookies", "storage", "executionContexts"',  # On logout
}

# Production rate limiting configuration
PRODUCTION_RATE_LIMITS = {
    "/api/auth/login": "5/minute",
    "/api/auth/register": "3/minute", 
    "/api/auth/refresh": "10/minute",
    "/api/auth/logout": "10/minute",
    "/api/auth/change-password": "3/minute",
    "/api/password-policy/validate": "20/minute",
    "/api/admin/*": "20/minute",
    "/api/services/*": "50/minute",
    "default": "100/minute"
}

# Production logging configuration
PRODUCTION_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
        },
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "json",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        },
        "error": {
            "level": "ERROR", 
            "formatter": "json",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr"
        }
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
        "app": {
            "handlers": ["default", "error"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
        "sqlalchemy": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False
        }
    }
}