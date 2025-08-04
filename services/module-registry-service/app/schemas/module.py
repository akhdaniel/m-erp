"""
Module schemas for API serialization
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.models.module import ModuleStatus, ModuleType


class ModuleBase(BaseModel):
    """Base module schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Module name")
    display_name: str = Field(..., min_length=1, max_length=255, description="Display name")
    description: Optional[str] = Field(None, max_length=1000, description="Module description")
    version: str = Field(..., min_length=1, max_length=50, description="Module version")
    author: str = Field(..., min_length=1, max_length=255, description="Module author")
    author_email: Optional[str] = Field(None, max_length=255, description="Author email")
    license: Optional[str] = Field(None, max_length=100, description="Module license")
    homepage_url: Optional[str] = Field(None, max_length=500, description="Homepage URL")
    documentation_url: Optional[str] = Field(None, max_length=500, description="Documentation URL")
    repository_url: Optional[str] = Field(None, max_length=500, description="Repository URL")
    module_type: ModuleType = Field(default=ModuleType.FULL_MODULE, description="Module type")
    minimum_framework_version: str = Field(default="1.0.0", max_length=50, description="Minimum framework version")
    python_version: str = Field(default=">=3.12", max_length=50, description="Python version requirement")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Module name must be alphanumeric (hyphens and underscores allowed)')
        return v.lower()
    
    @validator('version')
    def validate_version(cls, v):
        # Basic semantic version validation
        import re
        if not re.match(r'^\d+\.\d+\.\d+(-\w+)?$', v):
            raise ValueError('Version must follow semantic versioning (e.g., 1.0.0 or 1.0.0-beta)')
        return v


class ModuleCreate(ModuleBase):
    """Schema for creating modules"""
    manifest: Dict[str, Any] = Field(..., description="Module manifest (YAML as dict)")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="Configuration schema")
    default_config: Optional[Dict[str, Any]] = Field(None, description="Default configuration")
    is_public: bool = Field(default=False, description="Public in marketplace")
    requires_approval: bool = Field(default=True, description="Requires admin approval")


class ModuleUpdate(BaseModel):
    """Schema for updating modules"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    author_email: Optional[str] = Field(None, max_length=255)
    license: Optional[str] = Field(None, max_length=100)
    homepage_url: Optional[str] = Field(None, max_length=500)
    documentation_url: Optional[str] = Field(None, max_length=500)
    repository_url: Optional[str] = Field(None, max_length=500)
    config_schema: Optional[Dict[str, Any]] = None
    default_config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    requires_approval: Optional[bool] = None
    is_active: Optional[bool] = None


class ModuleResponse(ModuleBase):
    """Schema for module responses"""
    id: int
    status: ModuleStatus
    manifest: Dict[str, Any]
    config_schema: Optional[Dict[str, Any]]
    default_config: Optional[Dict[str, Any]]
    is_active: bool
    is_public: bool
    requires_approval: bool
    security_scan_status: Optional[str]
    security_scan_date: Optional[datetime]
    validation_errors: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    package_size: Optional[int]
    package_hash: Optional[str]
    
    class Config:
        from_attributes = True


class ModuleListResponse(BaseModel):
    """Schema for module list responses"""
    modules: List[ModuleResponse]
    total: int
    page: int
    page_size: int


class ModuleStatusUpdate(BaseModel):
    """Schema for updating module status"""
    status: ModuleStatus = Field(..., description="New module status")
    validation_errors: Optional[Dict[str, Any]] = Field(None, description="Validation errors if rejecting")


class ModuleManifest(BaseModel):
    """Schema for module manifest validation"""
    name: str = Field(..., description="Module name")
    version: str = Field(..., description="Module version")
    description: str = Field(..., description="Module description")
    author: str = Field(..., description="Module author")
    
    # Dependencies
    dependencies: Optional[List[Dict[str, str]]] = Field(default=[], description="Module dependencies")
    
    # Entry points
    entry_points: Optional[Dict[str, str]] = Field(default={}, description="Module entry points")
    
    # API endpoints
    endpoints: Optional[List[Dict[str, Any]]] = Field(default=[], description="Module API endpoints")
    
    # Event handlers
    event_handlers: Optional[Dict[str, str]] = Field(default={}, description="Event handler mappings")
    
    # Configuration schema
    config_schema: Optional[Dict[str, Any]] = Field(None, description="Configuration schema")
    
    # Module metadata
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")