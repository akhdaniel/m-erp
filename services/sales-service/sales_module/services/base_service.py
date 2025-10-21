"""
Base service class for sales module services.

Provides common functionality and patterns for all sales services
including database operations, validation, and event handling.
"""

from typing import Optional, List, Dict, Any, Type, TypeVar
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from sales_module.framework.base import CompanyBusinessObject

T = TypeVar('T', bound=CompanyBusinessObject)
import logging
logger = logging.getLogger('uvicorn')

class ServiceError(Exception):
    """Base exception for service layer errors."""
    pass



class NotFoundError(ServiceError):
    """Exception for resource not found errors."""
    pass


class BaseService:
    """
    Base service class providing common functionality for sales services.
    
    In production, this would integrate with the Business Object Framework
    services and provide standardized CRUD operations, validation,
    and event handling patterns.
    """
    
    def __init__(self, db_session: Session = None, company_id:int = None):
        """Initialize base service with database session."""
        self.db_session = db_session
        self.db = db_session
        self.model_class: Optional[Type[CompanyBusinessObject]] = None
        self.company_id = company_id

    def commit(self):
        self.db_session.commit()

    def rollback(self):
        self.db_session.rollback()


    def create(self, data: Dict[str, Any], user_id: int = None, 
               company_id: int = None) -> CompanyBusinessObject:
        """
        Create new entity with validation and audit logging.
        
        Args:
            data: Dictionary of field values
            user_id: ID of user performing the action
            company_id: Company ID for multi-company isolation
            
        Returns:
            Created entity instance
        """
        if not self.model_class:
            raise NotImplementedError("model_class must be set in service")
        
        # Validate required fields
        self.validate_create_data(data)
        
        # Set company ID for multi-company isolation
        if company_id:
            data['company_id'] = company_id
        
        # Create entity instance
        logger.info(f'order service data={data}')
        entity = self.model_class(**data)
        
        # Perform pre-create operations
        self.before_create(entity, user_id)
        
        # Save entity (in production, would use database session)
        entity.save(self.db_session, user_id)
        
        # Perform post-create operations
        self.after_create(entity, user_id)


        logger.info(f"create: base_service; entity={entity.id}")
        
        return entity
 
    def _apply_company_filter(self, query, model_class: Type[T]):
        """Apply company filter to query if company_id is set."""
        if self.company_id:
            query = query.filter(model_class.company_id == self.company_id)
        return query
        
    def _validate_company_access(self, model: CompanyBusinessObject) -> None:
        """Validate user has access to company data."""
        if self.company_id and model.company_id != self.company_id:
            raise PermissionError(f"Access denied to {model.__class__.__name__} from different company")
        
    def get_by_id(self, id: int, company_id: int) -> Optional[T]:
        model_class = self.model_class
        """Get model by ID with company filtering."""
        self.company_id = company_id

        # logger.info(f"get_by_id: model_class={model_class}, id={id}, company_id={company_id}")
        query = self.db.query(model_class).filter(model_class.id == id)
        # logger.info(f'query1={query}')

        query = self._apply_company_filter(query, model_class)
        # logger.info(f'query2={query}')
        model = query.first()
        # logger.info(f"mode1={model}")
        
        if model:
            self._validate_company_access(model)
        
        # logger.info(f"mode2={model}")
        return model
        
    def get_by_id_or_raise(self, id: int, company_id: int = None) -> T:
        """Get model by ID or raise NotFoundError."""
        model_class = self.model_class
        # logger.info(f'get_by_id_or_raise: model_class={model_class}, id={id}, company_id={company_id}')
        model = self.get_by_id(id, company_id)
        # logger.info(f"mode3={model}")
        if not model:
            raise NotFoundError(f"{model_class.__name__} with ID {id} not found")
        # logger.info(f"mode4={model}")
        return model
    
    def update(self, model_class: Type[T], entity_id: int, data: Dict[str, Any], user_id: int = None,
               company_id: int = None) -> Optional[CompanyBusinessObject]:
        """
        Update entity with validation and audit logging.
        
        Args:
            entity_id: Entity ID to update
            data: Dictionary of field values to update
            user_id: ID of user performing the action
            company_id: Company ID for isolation
            
        Returns:
            Updated entity instance or None if not found
        """
        # Get existing entity
        # logger.info(f"update model_class={model_class}")            
        entity = self.get_by_id(model_class, entity_id, company_id)
        # logger.info(f"entity00={entity}")            
        if not entity:
            # logger.info(f"entity0={entity}")            
            return None
        
        # Validate update data
        # logger.info(f"entity1={entity}")
        self.validate_update_data(data, entity)
        
        # Perform pre-update operations
        # logger.info(f"entity2={entity}")
        self.before_update(entity, data, user_id)
        
        # Update entity fields
        logger.info(f"data={data}")
        entity.update_from_dict(data)
        
        # Save entity
        logger.info(f"entity3={entity}")
        entity.save(self.db_session, user_id)
        
        # Perform post-update operations
        self.after_update(entity, user_id)
        logger.info(f"entity4={entity}")
        
        return entity
    
    def delete(self, entity_id: int, user_id: int = None, 
               company_id: int = None) -> bool:
        """
        Delete entity with audit logging.
        
        Args:
            entity_id: Entity ID to delete
            user_id: ID of user performing the action
            company_id: Company ID for isolation
            
        Returns:
            True if deleted successfully, False if not found
        """
        # Get existing entity
        entity = self.get_by_id(entity_id, company_id)
        if not entity:
            return False
        
        # Perform pre-delete operations
        self.before_delete(entity, user_id)
        
        # Soft delete by setting is_active = False
        entity.is_active = False
        entity.save(self.db_session, user_id)
        
        # Perform post-delete operations
        self.after_delete(entity, user_id)
        
        return True
    
    def list(self, filters: Dict[str, Any] = None, company_id: int = None,
             page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """
        List entities with filtering, pagination, and company isolation.
        
        Args:
            filters: Dictionary of filter criteria
            company_id: Company ID for isolation
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Dictionary with items, total count, and pagination info
        """
        if not self.model_class:
            raise NotImplementedError("model_class must be set in service")
        
        # In production, would build database query with filters
        # query = self.db_session.query(self.model_class)
        # 
        # if company_id:
        #     query = query.filter(self.model_class.company_id == company_id)
        # 
        # query = query.filter(self.model_class.is_active == True)
        # 
        # # Apply filters
        # if filters:
        #     query = self.apply_filters(query, filters)
        # 
        # # Apply pagination
        # total = query.count()
        # items = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # Simulated for demo
        print(f"Sales Service: Listing {self.model_class.__name__} with filters {filters}")
        
        return {
            "items": [],  # Would contain actual entities
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0
        }
    
    def search(self, search_term: str, company_id: int = None,
               page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """
        Full-text search across entity fields.
        
        Args:
            search_term: Search term
            company_id: Company ID for isolation
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Dictionary with search results and pagination info
        """
        # In production, would implement full-text search
        print(f"Sales Service: Searching {self.model_class.__name__} for '{search_term}'")
        
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "search_term": search_term
        }
    
    # Validation hooks (override in subclasses)
    
    def validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validate data for create operation."""
        pass
    
    def validate_update_data(self, data: Dict[str, Any], entity: CompanyBusinessObject) -> None:
        """Validate data for update operation."""
        pass
    
    # Lifecycle hooks (override in subclasses)
    
    def before_create(self, entity: CompanyBusinessObject, user_id: int = None) -> None:
        """Called before entity creation."""
        pass
    
    def after_create(self, entity: CompanyBusinessObject, user_id: int = None) -> None:
        """Called after entity creation."""
        pass
    
    def before_update(self, entity: CompanyBusinessObject, data: Dict[str, Any], 
                     user_id: int = None) -> None:
        """Called before entity update."""
        pass
    
    def after_update(self, entity: CompanyBusinessObject, user_id: int = None) -> None:
        """Called after entity update."""
        pass
    
    def before_delete(self, entity: CompanyBusinessObject, user_id: int = None) -> None:
        """Called before entity deletion."""
        pass
    
    def after_delete(self, entity: CompanyBusinessObject, user_id: int = None) -> None:
        """Called after entity deletion."""
        pass
    
    # Utility methods
    
    def apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to query (to be implemented in production)."""
        # Would implement complex filtering logic
        return query
    
    def validate_company_access(self, entity: CompanyBusinessObject, 
                               user_company_id: int) -> bool:
        """Validate user has access to entity's company data."""
        return entity.validate_company_access(user_company_id)
    
    def generate_number(self, prefix: str, sequence_name: str = None) -> str:
        """Generate sequential number for entity."""
        # In production, would use database sequences or counters
        import time
        timestamp = int(time.time())
        return f"{prefix}{timestamp:08d}"
    
