import os
from typing import Optional

from pydantic import BaseModel


class Settings(BaseModel):
  project_name: str = "User Authentication Service"
  version: str = "1.0.0"
  description: str = "XERPIUM User Authentication Microservice"
  
  # Database
  database_url: str = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./user_auth.db"
  )
  
  # JWT Settings
  secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
  algorithm: str = "HS256"
  access_token_expire_minutes: int = 15
  refresh_token_expire_days: int = 7
  
  # Environment
  environment: str = os.getenv("ENVIRONMENT", "development")
  debug: bool = os.getenv("DEBUG", "true").lower() == "true"
  
  # CORS
  allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]
  
  # Redis (for rate limiting and caching)
  redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
  
  # Security settings
  rate_limiting_enabled: bool = os.getenv("RATE_LIMITING_ENABLED", "true").lower() == "true"
  audit_logging_enabled: bool = os.getenv("AUDIT_LOGGING_ENABLED", "true").lower() == "true"
  


settings = Settings()