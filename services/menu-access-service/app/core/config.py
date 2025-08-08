import os
from typing import Optional

from pydantic import BaseModel


class Settings(BaseModel):
    project_name: str = "Menu & Access Rights Service"
    version: str = "1.0.0"
    description: str = "XERPIUM Menu & Access Rights Management Microservice"
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:password@localhost:5432/menu_access_db"
    )
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Auth Service Integration
    auth_service_url: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    auth_service_token: Optional[str] = os.getenv("AUTH_SERVICE_TOKEN")
    service_key: str = os.getenv("SERVICE_KEY", "menu-access-service-key")
    service_secret: str = os.getenv("SERVICE_SECRET", "menu-access-service-secret-key-that-is-long-enough")
    
    # Redis (for caching and future rate limiting)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/2")
    
    # Security settings
    rate_limiting_enabled: bool = os.getenv("RATE_LIMITING_ENABLED", "false").lower() == "true"
    
    # Service-specific settings
    default_menu_cache_ttl: int = int(os.getenv("MENU_CACHE_TTL", "3600"))  # 1 hour
    max_menu_depth: int = int(os.getenv("MAX_MENU_DEPTH", "5"))  # Maximum menu nesting


settings = Settings()