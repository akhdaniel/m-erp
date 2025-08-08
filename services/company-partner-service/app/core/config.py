import os
from typing import Optional

from pydantic import BaseModel


class Settings(BaseModel):
  project_name: str = "Company & Partner Management Service"
  version: str = "1.0.0"
  description: str = "XERPIUM Company & Partner Management Microservice"
  
  # Database
  database_url: str = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:password@localhost:5432/company_partner_db"
  )
  
  # Environment
  environment: str = os.getenv("ENVIRONMENT", "development")
  debug: bool = os.getenv("DEBUG", "true").lower() == "true"
  
  # CORS
  allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]
  
  # Auth Service Integration
  auth_service_url: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
  auth_service_token: Optional[str] = os.getenv("AUTH_SERVICE_TOKEN")
  service_key: str = os.getenv("SERVICE_KEY", "company-partner-service-key")
  
  # Redis (for caching and future rate limiting)
  redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/1")
  
  # Security settings
  rate_limiting_enabled: bool = os.getenv("RATE_LIMITING_ENABLED", "false").lower() == "true"
  
  # Company-specific settings
  default_company_name: str = os.getenv("DEFAULT_COMPANY_NAME", "Default Company")
  allow_multi_company: bool = os.getenv("ALLOW_MULTI_COMPANY", "true").lower() == "true"


settings = Settings()