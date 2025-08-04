"""
Service framework for Business Object Framework.

Provides standardized service classes with CRUD operations, audit logging,
event publishing, and multi-company data isolation.
"""

import math
from typing import Optional, List, Tuple, Type, TypeVar, Generic, Dict, Any
from datetime import datetime
from sqlalchemy import and_, func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import BaseModel

from app.framework.base import BusinessObjectBase, CompanyBusinessObject
from app.framework.schemas import CreateSchemaBase, UpdateSchemaBase
from app.services.messaging_service import CompanyPartnerMessagingService


# Type variables for generic service classes
ModelType = TypeVar('ModelType', bound=BusinessObjectBase)
CreateSchemaType = TypeVar('CreateSchemaType', bound=CreateSchemaBase)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=UpdateSchemaBase)


class BusinessObjectService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic service class for business objects.
    
    Provides standardized CRUD operations with automatic audit logging,
    event publishing, and proper error handling for all business objects.
    """
    
    def __init__(
        self,
        model: Type[ModelType],
        messaging_service: Optional[CompanyPartnerMessagingService] = None
    ):
        """
        Initialize the service with a model class and optional messaging service.
        
        Args:
            model: SQLAlchemy model class
            messaging_service: Optional messaging service for events and audit
        """
        self.model = model
        self.messaging_service = messaging_service
        self.model_name = model.__name__.lower()
    
    async def create(
        self,
        db: AsyncSession,
        create_data: CreateSchemaType,
        **kwargs
    ) -> ModelType:
        """
        Create a new business object.
        
        Args:
            db: Database session
            create_data: Pydantic schema with creation data
            **kwargs: Additional parameters (e.g., company_id, user_id)
            
        Returns:
            Created business object
            
        Raises:
            ValueError: If data validation fails or integrity constraints are violated
            SQLAlchemyError: If database operation fails
        """
        try:
            # Convert Pydantic model to dict
            create_dict = create_data.model_dump(exclude_unset=True)
            
            # Add framework fields
            create_dict['created_at'] = datetime.utcnow()
            create_dict['updated_at'] = datetime.utcnow()
            create_dict['framework_version'] = '1.0.0'
            
            # Add any additional kwargs (like company_id from context)
            for key, value in kwargs.items():
                if key not in create_dict and value is not None:
                    create_dict[key] = value
            
            # Create the object
            db_obj = self.model(**create_dict)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            
            # Publish audit event
            await self._publish_audit_event(
                'created',
                db_obj,
                changes=create_dict,
                user_id=kwargs.get('user_id')
            )
            
            # Publish business event
            await self._publish_business_event(
                f'{self.model_name}_created',
                db_obj,
                user_id=kwargs.get('user_id')
            )
            
            return db_obj
            
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Failed to create {self.model_name}: {self._parse_integrity_error(e)}")
        except SQLAlchemyError as e:
            await db.rollback()
            raise ValueError(f"Database error creating {self.model_name}: {str(e)}")
    
    async def get_by_id(
        self,
        db: AsyncSession,
        obj_id: int,
        **kwargs
    ) -> Optional[ModelType]:
        """
        Get a business object by ID.
        
        Args:
            db: Database session
            obj_id: Object ID
            **kwargs: Additional filters (e.g., company_id)
            
        Returns:
            Business object or None if not found
        """
        try:
            query = select(self.model).where(self.model.id == obj_id)
            
            # Apply additional filters
            query = self._apply_filters(query, **kwargs)
            
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            raise ValueError(f"Database error retrieving {self.model_name}: {str(e)}")
    
    async def get_list(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        **kwargs
    ) -> Tuple[List[ModelType], int]:
        """
        Get a list of business objects with pagination and filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search term for text fields
            filters: Additional filters as dict
            order_by: Field name to order by
            **kwargs: Additional filters (e.g., company_id)
            
        Returns:
            Tuple of (objects list, total count)
        """
        try:
            # Build base queries
            query = select(self.model)
            count_query = select(func.count(self.model.id))
            
            # Apply standard filters
            query = self._apply_filters(query, **kwargs)
            count_query = self._apply_filters(count_query, **kwargs)
            
            # Apply additional filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        query = query.where(getattr(self.model, key) == value)
                        count_query = count_query.where(getattr(self.model, key) == value)
            
            # Apply search
            if search:
                search_conditions = self._build_search_conditions(search)
                if search_conditions is not None:
                    query = query.where(search_conditions)
                    count_query = count_query.where(search_conditions)
            
            # Get total count
            total_result = await db.execute(count_query)
            total = total_result.scalar()
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                query = query.order_by(getattr(self.model, order_by))
            elif hasattr(self.model, 'created_at'):
                query = query.order_by(self.model.created_at.desc())
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            # Execute query
            result = await db.execute(query)
            objects = result.scalars().all()
            
            return list(objects), total
            
        except SQLAlchemyError as e:
            raise ValueError(f"Database error listing {self.model_name}: {str(e)}")
    
    async def update(
        self,
        db: AsyncSession,
        obj_id: int,
        update_data: UpdateSchemaType,
        **kwargs
    ) -> Optional[ModelType]:
        """
        Update a business object.
        
        Args:
            db: Database session
            obj_id: Object ID
            update_data: Pydantic schema with update data
            **kwargs: Additional parameters (e.g., company_id, user_id)
            
        Returns:
            Updated business object or None if not found
        """
        try:
            # Get existing object
            db_obj = await self.get_by_id(db, obj_id, **kwargs)
            if not db_obj:
                return None
            
            # Convert update data to dict and exclude unset fields
            update_dict = update_data.model_dump(exclude_unset=True)
            
            # Track changes for audit
            changes = {}
            for field, new_value in update_dict.items():
                if hasattr(db_obj, field):
                    old_value = getattr(db_obj, field)
                    if old_value != new_value:
                        changes[field] = {'old': old_value, 'new': new_value}
                        setattr(db_obj, field, new_value)
            
            # Update framework fields
            if changes:  # Only update if there are actual changes
                db_obj.updated_at = datetime.utcnow()
                changes['updated_at'] = {'old': None, 'new': db_obj.updated_at}
            
            # Commit changes
            await db.commit()
            await db.refresh(db_obj)
            
            # Publish audit event
            if changes:
                await self._publish_audit_event(
                    'updated',
                    db_obj,
                    changes=changes,
                    user_id=kwargs.get('user_id')
                )
                
                # Publish business event
                await self._publish_business_event(
                    f'{self.model_name}_updated',
                    db_obj,
                    changes=changes,
                    user_id=kwargs.get('user_id')
                )
            
            return db_obj
            
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Failed to update {self.model_name}: {self._parse_integrity_error(e)}")
        except SQLAlchemyError as e:
            await db.rollback()
            raise ValueError(f"Database error updating {self.model_name}: {str(e)}")
    
    async def delete(
        self,
        db: AsyncSession,
        obj_id: int,
        **kwargs
    ) -> bool:
        """
        Delete a business object (hard delete).
        
        Args:
            db: Database session
            obj_id: Object ID
            **kwargs: Additional filters (e.g., company_id, user_id)
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Get existing object for audit logging
            db_obj = await self.get_by_id(db, obj_id, **kwargs)
            if not db_obj:
                return False
            
            # Store object data for audit
            obj_data = self._obj_to_dict(db_obj)
            
            # Delete the object
            await db.delete(db_obj)
            await db.commit()
            
            # Publish audit event
            await self._publish_audit_event(
                'deleted',
                None,  # Object no longer exists
                changes={'deleted_object': obj_data},
                entity_id=obj_id,
                user_id=kwargs.get('user_id')
            )
            
            # Publish business event
            await self._publish_business_event(
                f'{self.model_name}_deleted',
                None,
                entity_id=obj_id,
                user_id=kwargs.get('user_id')
            )
            
            return True
            
        except SQLAlchemyError as e:
            await db.rollback()
            raise ValueError(f"Database error deleting {self.model_name}: {str(e)}")
    
    async def soft_delete(
        self,
        db: AsyncSession,
        obj_id: int,
        **kwargs
    ) -> Optional[ModelType]:
        """
        Soft delete a business object (set is_active to False).
        
        Args:
            db: Database session
            obj_id: Object ID
            **kwargs: Additional filters (e.g., company_id, user_id)
            
        Returns:
            Updated business object or None if not found
        """
        if not hasattr(self.model, 'is_active'):
            raise ValueError(f"Model {self.model_name} does not support soft delete (no is_active field)")
        
        try:
            # Get existing object
            db_obj = await self.get_by_id(db, obj_id, **kwargs)
            if not db_obj:
                return None
            
            # Set is_active to False
            old_active = db_obj.is_active
            db_obj.is_active = False
            db_obj.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(db_obj)
            
            # Publish audit event
            await self._publish_audit_event(
                'soft_deleted',
                db_obj,
                changes={'is_active': {'old': old_active, 'new': False}},
                user_id=kwargs.get('user_id')
            )
            
            # Publish business event
            await self._publish_business_event(
                f'{self.model_name}_soft_deleted',
                db_obj,
                user_id=kwargs.get('user_id')
            )
            
            return db_obj
            
        except SQLAlchemyError as e:
            await db.rollback()
            raise ValueError(f"Database error soft deleting {self.model_name}: {str(e)}")
    
    async def activate(
        self,
        db: AsyncSession,
        obj_id: int,
        **kwargs
    ) -> Optional[ModelType]:
        """
        Activate a business object (set is_active to True).
        
        Args:
            db: Database session
            obj_id: Object ID
            **kwargs: Additional filters (e.g., company_id, user_id)
            
        Returns:
            Updated business object or None if not found
        """
        if not hasattr(self.model, 'is_active'):
            raise ValueError(f"Model {self.model_name} does not support activation (no is_active field)")
        
        try:
            # Get existing object (including inactive ones)
            query = select(self.model).where(self.model.id == obj_id)
            query = self._apply_filters(query, **kwargs)
            
            result = await db.execute(query)
            db_obj = result.scalar_one_or_none()
            
            if not db_obj:
                return None
            
            # Set is_active to True
            old_active = db_obj.is_active
            db_obj.is_active = True
            db_obj.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(db_obj)
            
            # Publish audit event
            await self._publish_audit_event(
                'activated',
                db_obj,
                changes={'is_active': {'old': old_active, 'new': True}},
                user_id=kwargs.get('user_id')
            )
            
            # Publish business event
            await self._publish_business_event(
                f'{self.model_name}_activated',
                db_obj,
                user_id=kwargs.get('user_id')
            )
            
            return db_obj
            
        except SQLAlchemyError as e:
            await db.rollback()
            raise ValueError(f"Database error activating {self.model_name}: {str(e)}")
    
    async def deactivate(
        self,
        db: AsyncSession,
        obj_id: int,
        **kwargs
    ) -> Optional[ModelType]:
        """
        Deactivate a business object (set is_active to False).
        
        This is an alias for soft_delete for consistency.
        """
        return await self.soft_delete(db, obj_id, **kwargs)
    
    async def bulk_create(
        self,
        db: AsyncSession,
        create_data_list: List[CreateSchemaType],
        **kwargs
    ) -> List[ModelType]:
        """
        Create multiple business objects in a single transaction.
        
        Args:
            db: Database session
            create_data_list: List of Pydantic schemas with creation data
            **kwargs: Additional parameters (e.g., company_id, user_id)
            
        Returns:
            List of created business objects
        """
        try:
            created_objects = []
            
            for create_data in create_data_list:
                # Convert to dict
                create_dict = create_data.model_dump(exclude_unset=True)
                
                # Add framework fields
                create_dict['created_at'] = datetime.utcnow()
                create_dict['updated_at'] = datetime.utcnow()
                create_dict['framework_version'] = '1.0.0'
                
                # Add additional kwargs
                for key, value in kwargs.items():
                    if key not in create_dict and value is not None:
                        create_dict[key] = value
                
                # Create object
                db_obj = self.model(**create_dict)
                db.add(db_obj)
                created_objects.append(db_obj)
            
            # Commit all objects
            await db.commit()
            
            # Refresh all objects
            for obj in created_objects:
                await db.refresh(obj)
            
            # Publish bulk audit event
            await self._publish_audit_event(
                'bulk_created',
                None,
                changes={'count': len(created_objects)},
                user_id=kwargs.get('user_id')
            )
            
            # Publish bulk business event
            await self._publish_business_event(
                f'{self.model_name}_bulk_created',
                None,
                count=len(created_objects),
                user_id=kwargs.get('user_id')
            )
            
            return created_objects
            
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Failed to bulk create {self.model_name}: {self._parse_integrity_error(e)}")
        except SQLAlchemyError as e:
            await db.rollback()
            raise ValueError(f"Database error bulk creating {self.model_name}: {str(e)}")
    
    # Helper methods
    
    def _apply_filters(self, query, **kwargs):
        """Apply common filters to a query."""
        # Apply company_id filter if model supports it and filter is provided
        if hasattr(self.model, 'company_id'):
            company_id = kwargs.get('company_id')
            if company_id is not None:
                query = query.where(self.model.company_id == company_id)
        
        return query
    
    def _build_search_conditions(self, search: str):
        """Build search conditions for text fields."""
        if not search:
            return None
        
        search_filter = f"%{search}%"
        conditions = []
        
        # Common searchable fields
        searchable_fields = ['name', 'code', 'description', 'email']
        
        for field_name in searchable_fields:
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                if hasattr(field.type, 'python_type') and field.type.python_type == str:
                    conditions.append(field.ilike(search_filter))
        
        if conditions:
            from sqlalchemy import or_
            return or_(*conditions)
        
        return None
    
    def _parse_integrity_error(self, error: IntegrityError) -> str:
        """Parse SQLAlchemy integrity error into user-friendly message."""
        error_msg = str(error.orig)
        
        if "duplicate key" in error_msg or "UNIQUE constraint" in error_msg:
            return "A record with this data already exists"
        elif "foreign key" in error_msg or "FOREIGN KEY constraint" in error_msg:
            return "Referenced record does not exist"
        elif "not null" in error_msg or "NOT NULL constraint" in error_msg:
            return "Required field is missing"
        else:
            return "Data integrity error"
    
    def _obj_to_dict(self, obj) -> Dict[str, Any]:
        """Convert SQLAlchemy object to dictionary."""
        if obj is None:
            return {}
        
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        
        return result
    
    async def _publish_audit_event(
        self,
        action: str,
        obj: Optional[ModelType],
        changes: Optional[Dict[str, Any]] = None,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None
    ):
        """Publish audit event for the operation."""
        try:
            if self.messaging_service:
                await self.messaging_service.publish_audit_event(
                    entity_type=self.model_name,
                    entity_id=entity_id or (obj.id if obj else None),
                    action=action,
                    changes=changes or {},
                    user_id=user_id,
                    timestamp=datetime.utcnow()
                )
        except Exception as e:
            # Log error but don't fail the main operation
            print(f"Failed to publish audit event: {e}")
    
    async def _publish_business_event(
        self,
        event_type: str,
        obj: Optional[ModelType],
        changes: Optional[Dict[str, Any]] = None,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        **kwargs
    ):
        """Publish business event for the operation."""
        try:
            if self.messaging_service:
                event_data = {
                    'entity_type': self.model_name,
                    'entity_id': entity_id or (obj.id if obj else None),
                    'changes': changes or {},
                    'user_id': user_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    **kwargs
                }
                
                await self.messaging_service.publish_business_event(
                    event_type=event_type,
                    data=event_data
                )
        except Exception as e:
            # Log error but don't fail the main operation
            print(f"Failed to publish business event: {e}")


class CompanyBusinessObjectService(BusinessObjectService[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Service class for company-scoped business objects.
    
    Extends BusinessObjectService with automatic company_id enforcement
    and multi-company data isolation.
    """
    
    def __init__(
        self,
        model: Type[ModelType],
        messaging_service: Optional[CompanyPartnerMessagingService] = None
    ):
        """
        Initialize the company service with a model class.
        
        Args:
            model: SQLAlchemy model class (must inherit from CompanyBusinessObject)
            messaging_service: Optional messaging service for events and audit
        """
        if not issubclass(model, CompanyBusinessObject):
            raise ValueError(f"Model {model.__name__} must inherit from CompanyBusinessObject")
        
        super().__init__(model, messaging_service)
    
    def _apply_filters(self, query, **kwargs):
        """Apply company-specific filters to a query."""
        # Always apply company_id filter for company business objects
        company_id = kwargs.get('company_id')
        if company_id is None:
            raise ValueError("company_id is required for company business objects")
        
        query = query.where(self.model.company_id == company_id)
        return super()._apply_filters(query, **kwargs)
    
    async def create(
        self,
        db: AsyncSession,
        create_data: CreateSchemaType,
        company_id: int,
        **kwargs
    ) -> ModelType:
        """
        Create a new company business object.
        
        Args:
            db: Database session
            create_data: Pydantic schema with creation data
            company_id: Company ID for data isolation
            **kwargs: Additional parameters (e.g., user_id)
            
        Returns:
            Created business object
        """
        # Ensure company_id is set
        kwargs['company_id'] = company_id
        return await super().create(db, create_data, **kwargs)
    
    async def get_by_id(
        self,
        db: AsyncSession,
        obj_id: int,
        company_id: int,
        **kwargs
    ) -> Optional[ModelType]:
        """
        Get a company business object by ID.
        
        Args:
            db: Database session
            obj_id: Object ID
            company_id: Company ID for data isolation
            **kwargs: Additional filters
            
        Returns:
            Business object or None if not found
        """
        kwargs['company_id'] = company_id
        return await super().get_by_id(db, obj_id, **kwargs)
    
    async def get_list(
        self,
        db: AsyncSession,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        **kwargs
    ) -> Tuple[List[ModelType], int]:
        """
        Get a list of company business objects.
        
        Args:
            db: Database session
            company_id: Company ID for data isolation
            skip: Number of records to skip
            limit: Maximum number of records to return
            **kwargs: Additional filters
            
        Returns:
            Tuple of (objects list, total count)
        """
        kwargs['company_id'] = company_id
        return await super().get_list(db, skip=skip, limit=limit, **kwargs)
    
    async def update(
        self,
        db: AsyncSession,
        obj_id: int,
        update_data: UpdateSchemaType,
        company_id: int,
        **kwargs
    ) -> Optional[ModelType]:
        """
        Update a company business object.
        
        Args:
            db: Database session
            obj_id: Object ID
            update_data: Pydantic schema with update data
            company_id: Company ID for data isolation
            **kwargs: Additional parameters
            
        Returns:
            Updated business object or None if not found
        """
        kwargs['company_id'] = company_id
        return await super().update(db, obj_id, update_data, **kwargs)
    
    async def delete(
        self,
        db: AsyncSession,
        obj_id: int,
        company_id: int,
        **kwargs
    ) -> bool:
        """
        Delete a company business object.
        
        Args:
            db: Database session
            obj_id: Object ID
            company_id: Company ID for data isolation
            **kwargs: Additional parameters
            
        Returns:
            True if deleted, False if not found
        """
        kwargs['company_id'] = company_id
        return await super().delete(db, obj_id, **kwargs)


# Service factory functions
def create_business_object_service(
    model: Type[ModelType],
    messaging_service: Optional[CompanyPartnerMessagingService] = None
) -> BusinessObjectService[ModelType, CreateSchemaBase, UpdateSchemaBase]:
    """
    Factory function to create a BusinessObjectService for a model.
    
    Args:
        model: SQLAlchemy model class
        messaging_service: Optional messaging service for events and audit
        
    Returns:
        Configured BusinessObjectService instance
    """
    return BusinessObjectService(model, messaging_service)


def create_company_business_object_service(
    model: Type[ModelType],
    messaging_service: Optional[CompanyPartnerMessagingService] = None
) -> CompanyBusinessObjectService[ModelType, CreateSchemaBase, UpdateSchemaBase]:
    """
    Factory function to create a CompanyBusinessObjectService for a model.
    
    Args:
        model: SQLAlchemy model class (must inherit from CompanyBusinessObject)
        messaging_service: Optional messaging service for events and audit
        
    Returns:
        Configured CompanyBusinessObjectService instance
    """
    return CompanyBusinessObjectService(model, messaging_service)


# Service template classes for rapid development
class ServiceTemplate:
    """
    Template class for generating service methods dynamically.
    
    Provides utilities for creating service classes with custom business logic
    while maintaining framework standards.
    """
    
    @staticmethod
    def create_service_class(
        model: Type[ModelType],
        base_service: Type = BusinessObjectService,
        custom_methods: Optional[Dict[str, Any]] = None,
        messaging_service: Optional[CompanyPartnerMessagingService] = None
    ) -> Type[BusinessObjectService]:
        """
        Create a custom service class with additional methods.
        
        Args:
            model: SQLAlchemy model class
            base_service: Base service class to inherit from
            custom_methods: Dictionary of custom methods to add
            messaging_service: Optional messaging service
            
        Returns:
            Custom service class
        """
        class_name = f"{model.__name__}Service"
        custom_methods = custom_methods or {}
        
        # Create class attributes
        class_attrs = {
            '__module__': model.__module__,
            '_model': model,
            '_messaging_service': messaging_service
        }
        
        # Add custom methods
        for method_name, method_func in custom_methods.items():
            class_attrs[method_name] = method_func
        
        # Create the service class
        service_class = type(
            class_name,
            (base_service,),
            class_attrs
        )
        
        return service_class
    
    @staticmethod
    def add_search_method(
        service_class: Type[BusinessObjectService],
        search_fields: List[str]
    ):
        """
        Add custom search method to service class.
        
        Args:
            service_class: Service class to modify
            search_fields: List of field names to search in
        """
        async def advanced_search(
            self,
            db: AsyncSession,
            search_term: str,
            **kwargs
        ) -> Tuple[List[ModelType], int]:
            """Advanced search across specified fields."""
            from sqlalchemy import or_
            
            conditions = []
            search_filter = f"%{search_term}%"
            
            for field_name in search_fields:
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    conditions.append(field.ilike(search_filter))
            
            if conditions:
                kwargs['filters'] = kwargs.get('filters', {})
                # This would need to be integrated with the main get_list method
                pass
            
            return await self.get_list(db, search=search_term, **kwargs)
        
        # Add method to class
        setattr(service_class, 'advanced_search', advanced_search)