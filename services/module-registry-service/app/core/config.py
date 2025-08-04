"""
Configuration settings for Module Registry Service
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    app_name: str = "Module Registry Service"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    
    # Database settings
    database_url: str = "postgresql+asyncpg://mruser:mrpass123@localhost:5434/module_registry_db"
    
    # Redis settings  
    redis_url: str = "redis://localhost:6381/2"
    
    # Service registry settings
    service_registry_url: str = "http://localhost:8003"
    service_name: str = "module-registry-service"
    service_host: str = "localhost"
    service_port: int = 8005
    
    # Auth service settings
    auth_service_url: str = "http://localhost:8001"
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    
    # Module settings
    max_module_size_mb: int = 50
    module_storage_path: str = "/tmp/modules"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()