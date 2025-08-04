"""
Base service class for inventory module operations.

Provides common business logic patterns, error handling,
and integration with the Business Object Framework.
"""

from typing import List, Optional, Dict, Any, Type, TypeVar
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from inventory_module.framework.base import CompanyBusinessObject

T = TypeVar('T', bound=CompanyBusinessObject)


class ServiceError(Exception):
    """Base exception for service layer errors."""
    pass


class ValidationError(ServiceError):
    """Exception for validation errors."""
    pass


class NotFoundError(ServiceError):
    """Exception for resource not found errors."""
    pass


class PermissionError(ServiceError):
    """Exception for permission denied errors."""
    pass


class BaseService:
    """
    Base service class providing common business logic patterns.
    
    This mimics the Business Object Framework service patterns
    with CRUD operations, validation, and event publishing.
    """
    
    def __init__(self, db_session: Session, user_id: int = None, company_id: int = None):
        """
        Initialize service with database session and context.
        
        Args:
            db_session: SQLAlchemy database session
            user_id: Current user ID for audit trails
            company_id: Company ID for multi-company data isolation
        """
        self.db = db_session
        self.user_id = user_id
        self.company_id = company_id
    
    def _validate_company_access(self, model: CompanyBusinessObject) -> None:
        """Validate user has access to company data."""
        if self.company_id and model.company_id != self.company_id:
            raise PermissionError(f"Access denied to {model.__class__.__name__} from different company")
    
    def _apply_company_filter(self, query, model_class: Type[T]):
        """Apply company filter to query if company_id is set."""
        if self.company_id:
            query = query.filter(model_class.company_id == self.company_id)
        return query
    
    def get_by_id(self, model_class: Type[T], id: int) -> Optional[T]:
        """Get model by ID with company filtering."""
        query = self.db.query(model_class).filter(model_class.id == id)
        query = self._apply_company_filter(query, model_class)
        model = query.first()
        
        if model:
            self._validate_company_access(model)
        
        return model
    
    def get_by_id_or_raise(self, model_class: Type[T], id: int) -> T:
        """Get model by ID or raise NotFoundError."""
        model = self.get_by_id(model_class, id)
        if not model:
            raise NotFoundError(f"{model_class.__name__} with ID {id} not found")
        return model
    
    def list_all(self, model_class: Type[T], active_only: bool = True, 
                 limit: int = None, offset: int = 0, 
                 order_by: str = None, order_desc: bool = False) -> List[T]:
        """List all models with filtering and pagination."""
        query = self.db.query(model_class)
        query = self._apply_company_filter(query, model_class)
        
        # Filter active only if model has is_active field
        if active_only and hasattr(model_class, 'is_active'):
            query = query.filter(model_class.is_active == True)
        
        # Apply ordering
        if order_by and hasattr(model_class, order_by):
            order_field = getattr(model_class, order_by)
            if order_desc:
                query = query.order_by(desc(order_field))
            else:
                query = query.order_by(asc(order_field))
        
        # Apply pagination
        if offset > 0:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def count_all(self, model_class: Type[T], active_only: bool = True) -> int:
        """Count all models with filtering."""
        query = self.db.query(model_class)
        query = self._apply_company_filter(query, model_class)
        
        if active_only and hasattr(model_class, 'is_active'):
            query = query.filter(model_class.is_active == True)
        
        return query.count()
    
    def create(self, model_class: Type[T], data: Dict[str, Any]) -> T:
        """Create new model with validation and audit."""
        # Set company ID if not provided
        if self.company_id and 'company_id' not in data:
            data['company_id'] = self.company_id
        
        # Create model instance
        model = model_class(**data)
        
        # Validate model
        self._validate_model(model)
        
        # Save to database
        self.db.add(model)
        self.db.flush()  # Get ID without committing
        
        # Log audit trail and publish events
        model.log_audit_trail("created", self.user_id)
        model.publish_event(f"{model_class.__name__.lower()}.created", {
            "model_id": model.id,
            "company_id": model.company_id
        })
        
        return model
    
    def update(self, model: T, data: Dict[str, Any]) -> T:
        """Update model with validation and audit."""
        self._validate_company_access(model)
        
        # Store original values for audit
        original_data = model.to_dict()
        
        # Update model
        for key, value in data.items():
            if hasattr(model, key) and key != 'id':  # Don't allow ID updates
                setattr(model, key, value)
        
        # Update timestamp
        model.updated_at = datetime.utcnow()
        
        # Validate model
        self._validate_model(model)
        
        # Log audit trail with changes
        changes = {k: {"old": original_data.get(k), "new": v} 
                  for k, v in data.items() if original_data.get(k) != v}
        
        model.log_audit_trail("updated", self.user_id, {"changes": changes})
        model.publish_event(f"{model.__class__.__name__.lower()}.updated", {
            "model_id": model.id,
            "company_id": model.company_id,
            "changes": list(changes.keys())
        })
        
        return model
    
    def delete(self, model: T, soft_delete: bool = True) -> bool:
        """Delete model (soft or hard delete)."""
        self._validate_company_access(model)
        
        if soft_delete and hasattr(model, 'is_active'):
            # Soft delete by setting is_active = False
            model.is_active = False
            model.updated_at = datetime.utcnow()
            
            model.log_audit_trail("soft_deleted", self.user_id)
            model.publish_event(f"{model.__class__.__name__.lower()}.soft_deleted", {
                "model_id": model.id,
                "company_id": model.company_id
            })
        else:
            # Hard delete
            model.log_audit_trail("deleted", self.user_id)
            model.publish_event(f"{model.__class__.__name__.lower()}.deleted", {
                "model_id": model.id,
                "company_id": model.company_id
            })
            
            self.db.delete(model)
        
        return True
    
    def activate(self, model: T) -> T:
        """Activate a deactivated model."""
        self._validate_company_access(model)
        
        if hasattr(model, 'is_active'):
            model.is_active = True
            model.updated_at = datetime.utcnow()
            
            model.log_audit_trail("activated", self.user_id)
            model.publish_event(f"{model.__class__.__name__.lower()}.activated", {
                "model_id": model.id,
                "company_id": model.company_id
            })
        
        return model
    
    def deactivate(self, model: T) -> T:
        """Deactivate a model."""
        self._validate_company_access(model)
        
        if hasattr(model, 'is_active'):
            model.is_active = False
            model.updated_at = datetime.utcnow()
            
            model.log_audit_trail("deactivated", self.user_id)
            model.publish_event(f"{model.__class__.__name__.lower()}.deactivated", {
                "model_id": model.id,
                "company_id": model.company_id
            })
        
        return model
    
    def search(self, model_class: Type[T], search_term: str, 
               search_fields: List[str], limit: int = 50) -> List[T]:
        """Search models by text across specified fields."""
        query = self.db.query(model_class)
        query = self._apply_company_filter(query, model_class)
        
        # Build search conditions
        search_conditions = []
        for field in search_fields:
            if hasattr(model_class, field):
                field_attr = getattr(model_class, field)
                search_conditions.append(field_attr.ilike(f"%{search_term}%"))
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        # Filter active only
        if hasattr(model_class, 'is_active'):
            query = query.filter(model_class.is_active == True)
        
        return query.limit(limit).all()
    
    def _validate_model(self, model: T) -> None:
        """Validate model before save. Override in subclasses."""
        # Basic validation
        if hasattr(model, 'company_id') and not model.company_id:
            raise ValidationError("Company ID is required")
        
        # Subclasses can override for specific validation
        pass
    
    def commit(self) -> None:
        """Commit database transaction."""
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise ServiceError(f"Failed to commit transaction: {str(e)}")
    
    def rollback(self) -> None:
        """Rollback database transaction."""
        self.db.rollback()