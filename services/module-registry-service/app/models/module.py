"""
Module model for the registry
"""
from sqlalchemy import Column, String, Text, Boolean, Enum, JSON, LargeBinary, Integer, DateTime
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class ModuleStatus(str, enum.Enum):
    """Module status enumeration"""
    REGISTERED = "registered"
    APPROVED = "approved" 
    REJECTED = "rejected"
    DEPRECATED = "deprecated"


class ModuleType(str, enum.Enum):
    """Module type enumeration"""
    BUSINESS_OBJECT = "business_object"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    REPORT = "report"
    UI_COMPONENT = "ui_component"
    FULL_MODULE = "full_module"


class Module(BaseModel):
    """Module registry model"""
    __tablename__ = "modules"
    
    # Basic module information
    name = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=False)
    
    # Module metadata
    author = Column(String(255), nullable=False)
    author_email = Column(String(255), nullable=True)
    license = Column(String(100), nullable=True)
    homepage_url = Column(String(500), nullable=True)
    documentation_url = Column(String(500), nullable=True)
    repository_url = Column(String(500), nullable=True)
    
    # Module classification
    module_type = Column(Enum(ModuleType), nullable=False, default=ModuleType.FULL_MODULE)
    status = Column(Enum(ModuleStatus), nullable=False, default=ModuleStatus.REGISTERED)
    
    # Technical details
    minimum_framework_version = Column(String(50), nullable=False, default="1.0.0")
    python_version = Column(String(50), nullable=False, default=">=3.12")
    
    # Module manifest and package
    manifest = Column(JSON, nullable=False)  # YAML manifest as JSON
    package_data = Column(LargeBinary, nullable=True)  # Module package file
    package_size = Column(Integer, nullable=True)  # Package size in bytes
    package_hash = Column(String(64), nullable=True)  # SHA256 hash
    
    # Configuration schema
    config_schema = Column(JSON, nullable=True)  # JSON schema for module configuration
    default_config = Column(JSON, nullable=True)  # Default configuration values
    
    # Module flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)  # Public in module marketplace
    requires_approval = Column(Boolean, default=True, nullable=False)  # Requires admin approval
    
    # Security and validation
    security_scan_status = Column(String(50), nullable=True)  # Security scan results
    security_scan_date = Column(DateTime, nullable=True)
    validation_errors = Column(JSON, nullable=True)  # Validation error details
    
    # Relationships
    dependencies = relationship("ModuleDependency", back_populates="module", foreign_keys="ModuleDependency.module_id")
    dependent_modules = relationship("ModuleDependency", back_populates="dependency", foreign_keys="ModuleDependency.dependency_id")
    installations = relationship("ModuleInstallation", back_populates="module")
    
    def __repr__(self):
        return f"<Module(id={self.id}, name='{self.name}', version='{self.version}', status='{self.status}')>"
    
    @property
    def full_name(self) -> str:
        """Get full module name with version"""
        return f"{self.name}@{self.version}"
    
    @property
    def is_installed(self) -> bool:
        """Check if module has any active installations"""
        return any(install.is_active for install in self.installations)
    
    def to_dict(self) -> dict:
        """Convert module to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "author_email": self.author_email,
            "license": self.license,
            "homepage_url": self.homepage_url,
            "documentation_url": self.documentation_url,
            "repository_url": self.repository_url,
            "module_type": self.module_type,
            "status": self.status,
            "minimum_framework_version": self.minimum_framework_version,
            "python_version": self.python_version,
            "manifest": self.manifest,
            "config_schema": self.config_schema,
            "default_config": self.default_config,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "requires_approval": self.requires_approval,
            "security_scan_status": self.security_scan_status,
            "security_scan_date": self.security_scan_date.isoformat() if self.security_scan_date else None,
            "validation_errors": self.validation_errors,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "package_size": self.package_size,
            "package_hash": self.package_hash,
        }