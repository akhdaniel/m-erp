"""
Module dependency model
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class DependencyType(str, enum.Enum):
    """Dependency type enumeration"""
    MODULE = "module"  # Dependency on another module
    SERVICE = "service"  # Dependency on a microservice
    PYTHON_PACKAGE = "python_package"  # Dependency on a Python package
    SYSTEM = "system"  # System-level dependency


class ModuleDependency(BaseModel):
    """Module dependency model"""
    __tablename__ = "module_dependencies"
    
    # Foreign keys
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    dependency_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=True, index=True)  # Null for non-module dependencies
    
    # Dependency information
    dependency_type = Column(Enum(DependencyType), nullable=False, default=DependencyType.MODULE)
    dependency_name = Column(String(255), nullable=False, index=True)  # Name of the dependency
    version_constraint = Column(String(100), nullable=True)  # Version constraint (e.g., ">=1.0.0,<2.0.0")
    
    # Dependency metadata
    is_optional = Column(Boolean, default=False, nullable=False)
    is_dev_dependency = Column(Boolean, default=False, nullable=False)  # Development-only dependency
    description = Column(String(500), nullable=True)  # Purpose of this dependency
    
    # Relationships
    module = relationship("Module", back_populates="dependencies", foreign_keys=[module_id])
    dependency = relationship("Module", back_populates="dependent_modules", foreign_keys=[dependency_id])
    
    def __repr__(self):
        return f"<ModuleDependency(module_id={self.module_id}, dependency='{self.dependency_name}', version='{self.version_constraint}')>"
    
    def to_dict(self) -> dict:
        """Convert dependency to dictionary for API responses"""
        return {
            "id": self.id,
            "module_id": self.module_id,
            "dependency_id": self.dependency_id,
            "dependency_type": self.dependency_type,
            "dependency_name": self.dependency_name,
            "version_constraint": self.version_constraint,
            "is_optional": self.is_optional,
            "is_dev_dependency": self.is_dev_dependency,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }