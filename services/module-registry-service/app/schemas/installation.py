"""
Installation schemas for API serialization
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.installation import InstallationStatus


class InstallationBase(BaseModel):
    """Base installation schema"""
    module_id: int = Field(..., description="Module ID to install")
    company_id: Optional[int] = Field(None, description="Company ID (null for global installation)")
    configuration: Optional[Dict[str, Any]] = Field(default={}, description="Module configuration")


class InstallationCreate(InstallationBase):
    """Schema for creating installations"""
    pass


class InstallationUpdate(BaseModel):
    """Schema for updating installations"""
    configuration: Optional[Dict[str, Any]] = Field(None, description="Updated configuration")
    is_enabled: Optional[bool] = Field(None, description="Enable/disable module")


class InstallationResponse(InstallationBase):
    """Schema for installation responses"""
    id: int
    status: InstallationStatus
    installed_version: str
    installed_by: str
    installed_at: Optional[datetime]
    uninstalled_at: Optional[datetime]
    installation_log: Optional[Dict[str, Any]]
    error_message: Optional[str]
    is_active: bool
    is_enabled: bool
    last_health_check: Optional[datetime]
    health_status: Optional[str]
    health_details: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InstallationListResponse(BaseModel):
    """Schema for installation list responses"""
    installations: List[InstallationResponse]
    total: int
    page: int
    page_size: int


class InstallationStatusUpdate(BaseModel):
    """Schema for updating installation status"""
    status: InstallationStatus = Field(..., description="New installation status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    installation_log: Optional[Dict[str, Any]] = Field(None, description="Installation log")


class HealthCheckResult(BaseModel):
    """Schema for comprehensive health check results"""
    installation_id: int = Field(..., description="Installation ID")
    status: str = Field(..., description="Overall health status (healthy, degraded, unhealthy, error)")
    checks: Dict[str, bool] = Field(..., description="Individual health check results")
    last_check: datetime = Field(..., description="When health check was performed")
    response_time_ms: int = Field(..., description="Health check response time in milliseconds")
    errors: List[str] = Field(default=[], description="List of error messages if any")