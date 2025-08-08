"""
Configuration settings for the Service Registry.
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "XERPIUM Service Registry"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # Service Registry Configuration
    REGISTRY_KEY_PREFIX: str = "m-erp:services"
    HEARTBEAT_INTERVAL: int = 30  # seconds
    HEALTH_CHECK_INTERVAL: int = 60  # seconds
    SERVICE_TTL: int = 180  # seconds (3 minutes)
    
    # Kong Configuration
    KONG_ADMIN_URL: str = "http://kong:8001"
    KONG_GATEWAY_URL: str = "http://kong:8000"
    
    # Authentication Service
    AUTH_SERVICE_URL: str = "http://user-auth-service:8000"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080"
    ]
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()