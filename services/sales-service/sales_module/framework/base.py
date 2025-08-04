"""
Local Business Object Framework base classes for the Sales Module.

In production, these would be imported from the company-partner-service
Business Object Framework. For the sales module implementation,
we provide local interfaces that match the framework patterns.
"""

from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Any

# Create base for models
Base = declarative_base()


class TimestampMixin:
    """Mixin to add timestamp fields to models."""
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class BaseModel(Base, TimestampMixin):
    """
    Base model class providing common functionality.
    
    This mimics the Business Object Framework BaseModel with:
    - Primary key
    - Timestamps (created_at, updated_at)
    - Basic audit capabilities
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: dict) -> None:
        """Update model from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()


class CompanyBusinessObject(BaseModel):
    """
    Base class for business objects that belong to a company.
    
    This mimics the Business Object Framework CompanyBusinessObject with:
    - Company-scoped data isolation
    - Multi-company support
    - Automatic audit logging (simulated)
    - Event publishing (simulated)
    """
    __abstract__ = True
    
    # Company relationship for multi-company data isolation
    company_id = Column(Integer, nullable=False, index=True)
    
    # Framework version for migration tracking
    framework_version = Column(String(50), nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set framework version
        self.framework_version = "1.0.0"
    
    @property
    def company(self):
        """
        Company relationship property.
        In production, this would be a proper SQLAlchemy relationship
        to the Company model from company-partner-service.
        """
        # This would be implemented as:
        # return relationship("Company", back_populates="business_objects")
        return None
    
    def publish_event(self, event_type: str, event_data: dict = None) -> None:
        """
        Publish business event for audit and integration.
        
        In production, this would integrate with the Redis Streams
        event system from the Business Object Framework.
        """
        # Simulated event publishing
        print(f"Sales Event Published: {event_type} for {self.__class__.__name__}({self.id})")
        if event_data:
            print(f"Event Data: {event_data}")
    
    def log_audit_trail(self, action: str, user_id: int = None, details: dict = None) -> None:
        """
        Log audit trail for compliance.
        
        In production, this would integrate with the audit service
        from the Business Object Framework.
        """
        # Simulated audit logging
        print(f"Sales Audit Log: {action} on {self.__class__.__name__}({self.id}) by user {user_id}")
        if details:
            print(f"Audit Details: {details}")
    
    def validate_company_access(self, user_company_id: int) -> bool:
        """
        Validate that user has access to this company's data.
        
        In production, this would integrate with the auth service
        and company access controls.
        """
        return self.company_id == user_company_id
    
    def save(self, db_session: Any = None, user_id: int = None) -> None:
        """
        Save the model with automatic audit logging and event publishing.
        
        In production, this would be handled by the Business Object Framework
        service layer with proper database session management.
        """
        # Update timestamp
        self.updated_at = datetime.utcnow()
        
        # Log audit trail
        action = "created" if not hasattr(self, 'id') or self.id is None else "updated"
        self.log_audit_trail(action, user_id)
        
        # Publish event
        event_type = f"{self.__class__.__name__.lower()}.{action}"
        self.publish_event(event_type, {"model_id": self.id, "company_id": self.company_id})
        
        # In production, would call db_session.add(self) and db_session.commit()
        print(f"Sales Model {self.__class__.__name__}({self.id}) saved successfully")