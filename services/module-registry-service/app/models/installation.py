"""
Module installation model
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum, JSON, DateTime
from sqlalchemy.orm import relationship
import enum
from app.models.base import CompanyBaseModel


class InstallationStatus(str, enum.Enum):
    """Installation status enumeration"""
    PENDING = "pending"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"
    UNINSTALLING = "uninstalling"
    UNINSTALLED = "uninstalled"


class ModuleInstallation(CompanyBaseModel):
    """Module installation model"""
    __tablename__ = "module_installations"
    
    # Foreign keys
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Installation information
    status = Column(Enum(InstallationStatus), nullable=False, default=InstallationStatus.PENDING)
    installed_version = Column(String(50), nullable=False)
    
    # Installation metadata
    installed_by = Column(String(255), nullable=False)  # User who installed the module
    installed_at = Column(DateTime, nullable=True)  # When installation completed
    uninstalled_at = Column(DateTime, nullable=True)  # When uninstallation completed
    
    # Configuration
    configuration = Column(JSON, nullable=True)  # Module-specific configuration
    
    # Installation details
    installation_log = Column(JSON, nullable=True)  # Installation process log
    error_message = Column(String(1000), nullable=True)  # Error message if installation failed
    
    # Module state
    is_active = Column(Boolean, default=True, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)  # Can be disabled without uninstalling
    
    # Health monitoring
    last_health_check = Column(DateTime, nullable=True)
    health_status = Column(String(50), nullable=True)  # healthy, unhealthy, unknown
    health_details = Column(JSON, nullable=True)  # Health check details
    
    # Relationships
    module = relationship("Module", back_populates="installations")
    
    def __repr__(self):
        return f"<ModuleInstallation(id={self.id}, module_id={self.module_id}, company_id={self.company_id}, status='{self.status}')>"
    
    @property
    def is_healthy(self) -> bool:
        """Check if installation is healthy"""
        return (
            self.status == InstallationStatus.INSTALLED and
            self.is_active and
            self.is_enabled and
            self.health_status in ["healthy", None]
        )
    
    def to_dict(self) -> dict:
        """Convert installation to dictionary for API responses"""
        return {
            "id": self.id,
            "module_id": self.module_id,
            "company_id": self.company_id,
            "status": self.status,
            "installed_version": self.installed_version,
            "installed_by": self.installed_by,
            "installed_at": self.installed_at.isoformat() if self.installed_at else None,
            "uninstalled_at": self.uninstalled_at.isoformat() if self.uninstalled_at else None,
            "configuration": self.configuration,
            "installation_log": self.installation_log,
            "error_message": self.error_message,
            "is_active": self.is_active,
            "is_enabled": self.is_enabled,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "health_status": self.health_status,
            "health_details": self.health_details,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }