"""
Business Object Framework API Controllers.

Provides standardized API controller templates and patterns for building
consistent REST APIs with automatic CRUD operations, error handling,
authentication, and extension support.
"""

import logging
from typing import Type, Optional, Dict, Any, List, Union, Callable
from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, func
from pydantic import BaseModel

from app.core.database import get_db
from app.middleware.auth import get_current_user, require_company_access
from app.framework.services import BusinessObjectService, CompanyBusinessObjectService
from app.framework.schemas import BaseBusinessObjectSchema, CreateSchemaBase, UpdateSchemaBase
from app.models.base import BaseModel, CompanyBaseModel
from app.models.extensions import BusinessObjectExtension, BusinessObjectValidator

logger = logging.getLogger(__name__)


class StandardizedErrorHandler:
    """
    Standardized error handling for Business Object Framework APIs.
    
    Provides consistent error response formatting across all generated
    API endpoints with proper HTTP status codes and structured error messages.
    """
    
    @staticmethod
    def handle_validation_error(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle Pydantic validation errors."""
        return {
            "error_code": "VALIDATION_ERROR",
            "message": "Validation failed",
            "details": errors,
            "status_code": HTTPStatus.UNPROCESSABLE_ENTITY,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def handle_not_found_error(entity_type: str, entity_id: Union[int, str]) -> Dict[str, Any]:
        """Handle entity not found errors."""
        return {
            "error_code": "NOT_FOUND",
            "message": f"{entity_type.title()} with ID {entity_id} not found",
            "status_code": HTTPStatus.NOT_FOUND,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod  
    def handle_permission_error(action: str, resource: str) -> Dict[str, Any]:
        """Handle permission denied errors."""
        return {
            "error_code": "PERMISSION_DENIED",
            "message": f"Permission denied for {action} on {resource}",
            "status_code": HTTPStatus.FORBIDDEN,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def handle_business_logic_error(error_code: str, message: str) -> Dict[str, Any]:
        """Handle business logic validation errors."""
        return {
            "error_code": error_code,
            "message": message,
            "status_code": HTTPStatus.UNPROCESSABLE_ENTITY,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def handle_database_error(error: Exception) -> Dict[str, Any]:
        """Handle database-related errors."""
        logger.error(f"Database error: {str(error)}")
        return {
            "error_code": "DATABASE_ERROR",
            "message": "A database error occurred",
            "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def format_error_response(error_dict: Dict[str, Any]) -> JSONResponse:
        """Format error dictionary as JSONResponse."""
        status_code = error_dict.pop("status_code", HTTPStatus.INTERNAL_SERVER_ERROR)
        return JSONResponse(
            status_code=status_code,
            content=error_dict
        )


class ResponseFormatter:
    """
    Standardized response formatting for Business Object Framework APIs.
    
    Provides consistent response structure with metadata for all API responses
    including single objects, lists, and operation confirmations.
    """
    
    @staticmethod
    def format_single_response(obj: Dict[str, Any], meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format single object response."""
        response = {
            "data": obj,
            "meta": {
                "type": "single",
                "timestamp": datetime.utcnow().isoformat(),
                **(meta or {})
            }
        }
        return response
    
    @staticmethod
    def format_list_response(
        items: List[Dict[str, Any]], 
        total: int, 
        page: int = 1, 
        per_page: int = 50,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format list response with pagination metadata."""
        total_pages = (total + per_page - 1) // per_page
        
        response = {
            "data": items,
            "meta": {
                "type": "list",
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
                "timestamp": datetime.utcnow().isoformat(),
                **(meta or {})
            }
        }
        return response
    
    @staticmethod
    def format_created_response(obj: Dict[str, Any], meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format created object response."""
        response = {
            "data": obj,
            "meta": {
                "type": "created",
                "status_code": HTTPStatus.CREATED,
                "timestamp": datetime.utcnow().isoformat(),
                **(meta or {})
            }
        }
        return response
    
    @staticmethod
    def format_updated_response(obj: Dict[str, Any], meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format updated object response."""
        response = {
            "data": obj,
            "meta": {
                "type": "updated", 
                "status_code": HTTPStatus.OK,
                "timestamp": datetime.utcnow().isoformat(),
                **(meta or {})
            }
        }
        return response
    
    @staticmethod
    def format_deleted_response(meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format deleted confirmation response."""
        response = {
            "meta": {
                "type": "deleted",
                "status_code": HTTPStatus.NO_CONTENT,
                "timestamp": datetime.utcnow().isoformat(),
                **(meta or {})
            }
        }
        return response


class ExtensionEndpointMixin:
    """
    Mixin for adding extension field endpoints to business object routers.
    
    Provides standardized endpoints for managing custom fields on business objects
    with proper validation and company isolation.
    """
    
    def add_extension_endpoints(self, router: APIRouter, entity_type: str):
        """Add extension-related endpoints to the router."""
        
        @router.get("/{object_id}/extensions", tags=[f"{entity_type}-extensions"])
        async def get_object_extensions(
            object_id: int = Path(..., description=f"{entity_type.title()} ID"),
            db: AsyncSession = Depends(get_db),
            current_user: dict = Depends(get_current_user)
        ):
            """Get all custom field extensions for an object."""
            try:
                # Get the object first to verify access and company
                obj = await self.service_class(db).get_by_id(object_id)
                if not obj:
                    error_response = StandardizedErrorHandler.handle_not_found_error(entity_type, object_id)
                    return StandardizedErrorHandler.format_error_response(error_response)
                
                # Check company access if applicable
                if hasattr(obj, 'company_id'):
                    await require_company_access(current_user, obj.company_id)
                
                # Get extensions
                query = select(BusinessObjectExtension).where(
                    and_(
                        BusinessObjectExtension.entity_type == entity_type,
                        BusinessObjectExtension.entity_id == object_id,
                        BusinessObjectExtension.is_active == True
                    )
                )
                
                if hasattr(obj, 'company_id'):
                    query = query.where(BusinessObjectExtension.company_id == obj.company_id)
                
                result = await db.execute(query)
                extensions = result.scalars().all()
                
                # Format extensions with typed values
                extension_data = []
                for ext in extensions:
                    ext_dict = {
                        "id": ext.id,
                        "field_name": ext.field_name,
                        "field_type": ext.field_type,
                        "field_value": ext.field_value,
                        "typed_value": ext.get_typed_value(),
                        "created_at": ext.created_at,
                        "updated_at": ext.updated_at
                    }
                    extension_data.append(ext_dict)
                
                return ResponseFormatter.format_list_response(
                    extension_data, 
                    len(extension_data),
                    meta={"entity_type": entity_type, "entity_id": object_id}
                )
                
            except Exception as e:
                logger.error(f"Error getting extensions for {entity_type} {object_id}: {str(e)}")
                error_response = StandardizedErrorHandler.handle_database_error(e)
                return StandardizedErrorHandler.format_error_response(error_response)
        
        @router.post("/{object_id}/extensions", tags=[f"{entity_type}-extensions"])
        async def set_object_extension(
            object_id: int = Path(..., description=f"{entity_type.title()} ID"),
            extension_data: dict = Body(...),
            db: AsyncSession = Depends(get_db),
            current_user: dict = Depends(get_current_user)
        ):
            """Set a custom field extension for an object."""
            try:
                # Get the object first to verify access and company
                obj = await self.service_class(db).get_by_id(object_id)
                if not obj:
                    error_response = StandardizedErrorHandler.handle_not_found_error(entity_type, object_id)
                    return StandardizedErrorHandler.format_error_response(error_response)
                
                # Check company access if applicable
                company_id = None
                if hasattr(obj, 'company_id'):
                    company_id = obj.company_id
                    await require_company_access(current_user, company_id)
                
                # Validate required fields
                required_fields = ['field_name', 'field_type', 'field_value']
                for field in required_fields:
                    if field not in extension_data:
                        error_response = StandardizedErrorHandler.handle_validation_error([
                            {"field": field, "message": f"{field} is required"}
                        ])
                        return StandardizedErrorHandler.format_error_response(error_response)
                
                # Check if extension already exists
                existing_query = select(BusinessObjectExtension).where(
                    and_(
                        BusinessObjectExtension.entity_type == entity_type,
                        BusinessObjectExtension.entity_id == object_id,
                        BusinessObjectExtension.field_name == extension_data['field_name']
                    )
                )
                
                if company_id:
                    existing_query = existing_query.where(BusinessObjectExtension.company_id == company_id)
                
                result = await db.execute(existing_query)
                existing_extension = result.scalar_one_or_none()
                
                if existing_extension:
                    # Update existing extension
                    existing_extension.field_type = extension_data['field_type']
                    existing_extension.set_typed_value(extension_data['field_value'])
                    existing_extension.updated_at = datetime.utcnow()
                    extension = existing_extension
                else:
                    # Create new extension
                    extension = BusinessObjectExtension(
                        entity_type=entity_type,
                        entity_id=object_id,
                        field_name=extension_data['field_name'],
                        field_type=extension_data['field_type'],
                        company_id=company_id,
                        is_active=True,
                        framework_version='1.0.0'
                    )
                    extension.set_typed_value(extension_data['field_value'])
                    db.add(extension)
                
                await db.commit()
                await db.refresh(extension)
                
                # Format response
                response_data = {
                    "id": extension.id,
                    "field_name": extension.field_name,
                    "field_type": extension.field_type,
                    "field_value": extension.field_value,
                    "typed_value": extension.get_typed_value(),
                    "created_at": extension.created_at,
                    "updated_at": extension.updated_at
                }
                
                return ResponseFormatter.format_created_response(
                    response_data,
                    meta={"entity_type": entity_type, "entity_id": object_id}
                )
                
            except Exception as e:
                logger.error(f"Error setting extension for {entity_type} {object_id}: {str(e)}")
                error_response = StandardizedErrorHandler.handle_database_error(e)
                return StandardizedErrorHandler.format_error_response(error_response)
        
        @router.delete("/{object_id}/extensions/{field_name}", tags=[f"{entity_type}-extensions"])
        async def delete_object_extension(
            object_id: int = Path(..., description=f"{entity_type.title()} ID"),
            field_name: str = Path(..., description="Extension field name"),
            db: AsyncSession = Depends(get_db),
            current_user: dict = Depends(get_current_user)
        ):
            """Delete a custom field extension from an object."""
            try:
                # Get the object first to verify access and company
                obj = await self.service_class(db).get_by_id(object_id)
                if not obj:
                    error_response = StandardizedErrorHandler.handle_not_found_error(entity_type, object_id)
                    return StandardizedErrorHandler.format_error_response(error_response)
                
                # Check company access if applicable
                company_id = None
                if hasattr(obj, 'company_id'):
                    company_id = obj.company_id
                    await require_company_access(current_user, company_id)
                
                # Find the extension
                query = select(BusinessObjectExtension).where(
                    and_(
                        BusinessObjectExtension.entity_type == entity_type,
                        BusinessObjectExtension.entity_id == object_id,
                        BusinessObjectExtension.field_name == field_name
                    )
                )
                
                if company_id:
                    query = query.where(BusinessObjectExtension.company_id == company_id)
                
                result = await db.execute(query)
                extension = result.scalar_one_or_none()
                
                if not extension:
                    error_response = StandardizedErrorHandler.handle_not_found_error(
                        f"{entity_type} extension field", field_name
                    )
                    return StandardizedErrorHandler.format_error_response(error_response)
                
                # Soft delete the extension
                extension.is_active = False
                extension.updated_at = datetime.utcnow()
                
                await db.commit()
                
                return ResponseFormatter.format_deleted_response(
                    meta={"entity_type": entity_type, "entity_id": object_id, "field_name": field_name}
                )
                
            except Exception as e:
                logger.error(f"Error deleting extension {field_name} for {entity_type} {object_id}: {str(e)}")
                error_response = StandardizedErrorHandler.handle_database_error(e)
                return StandardizedErrorHandler.format_error_response(error_response)


class AuditTrailEndpointMixin:
    """
    Mixin for adding audit trail endpoints to business object routers.
    
    Provides standardized endpoints for accessing audit logs and change history
    for business objects with proper company isolation.
    """
    
    def add_audit_endpoints(self, router: APIRouter, entity_type: str):
        """Add audit trail endpoints to the router."""
        
        @router.get("/{object_id}/audit", tags=[f"{entity_type}-audit"])
        async def get_object_audit_trail(
            object_id: int = Path(..., description=f"{entity_type.title()} ID"),
            page: int = Query(1, ge=1, description="Page number"),
            per_page: int = Query(50, ge=1, le=100, description="Items per page"),
            db: AsyncSession = Depends(get_db),
            current_user: dict = Depends(get_current_user)
        ):
            """Get audit trail for an object."""
            try:
                # Get the object first to verify access and company
                obj = await self.service_class(db).get_by_id(object_id)
                if not obj:
                    error_response = StandardizedErrorHandler.handle_not_found_error(entity_type, object_id)
                    return StandardizedErrorHandler.format_error_response(error_response)
                
                # Check company access if applicable
                if hasattr(obj, 'company_id'):
                    await require_company_access(current_user, obj.company_id)
                
                # Query audit logs (this would integrate with your audit service)
                # For now, return placeholder response
                audit_data = [
                    {
                        "id": f"audit_{object_id}_1",
                        "action": "created",
                        "timestamp": datetime.utcnow().isoformat(),
                        "user_id": current_user.get("user_id"),
                        "changes": {"created": True}
                    }
                ]
                
                return ResponseFormatter.format_list_response(
                    audit_data,
                    len(audit_data),
                    page=page,
                    per_page=per_page,
                    meta={"entity_type": entity_type, "entity_id": object_id}
                )
                
            except Exception as e:
                logger.error(f"Error getting audit trail for {entity_type} {object_id}: {str(e)}")
                error_response = StandardizedErrorHandler.handle_database_error(e)
                return StandardizedErrorHandler.format_error_response(error_response)
        
        @router.get("/{object_id}/changes", tags=[f"{entity_type}-audit"])
        async def get_object_changes(
            object_id: int = Path(..., description=f"{entity_type.title()} ID"),
            since: Optional[datetime] = Query(None, description="Get changes since timestamp"),
            db: AsyncSession = Depends(get_db),
            current_user: dict = Depends(get_current_user)
        ):
            """Get recent changes for an object."""
            try:
                # Get the object first to verify access and company
                obj = await self.service_class(db).get_by_id(object_id)
                if not obj:
                    error_response = StandardizedErrorHandler.handle_not_found_error(entity_type, object_id)
                    return StandardizedErrorHandler.format_error_response(error_response)
                
                # Check company access if applicable
                if hasattr(obj, 'company_id'):
                    await require_company_access(current_user, obj.company_id)
                
                # Query recent changes (placeholder implementation)
                changes_data = [
                    {
                        "field": "updated_at",
                        "old_value": None,
                        "new_value": obj.updated_at.isoformat() if hasattr(obj, 'updated_at') else None,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ]
                
                return ResponseFormatter.format_list_response(
                    changes_data,
                    len(changes_data),
                    meta={"entity_type": entity_type, "entity_id": object_id, "since": since}
                )
                
            except Exception as e:
                logger.error(f"Error getting changes for {entity_type} {object_id}: {str(e)}")
                error_response = StandardizedErrorHandler.handle_database_error(e)
                return StandardizedErrorHandler.format_error_response(error_response)


class BusinessObjectRouter(ExtensionEndpointMixin, AuditTrailEndpointMixin):
    """
    Standardized Business Object API Router.
    
    Generates consistent CRUD endpoints for business objects with automatic
    error handling, authentication, extension support, and audit trails.
    """
    
    def __init__(
        self,
        model_class: Type[BaseModel],
        service_class: Type[BusinessObjectService],
        create_schema: Type[CreateSchemaBase],
        update_schema: Type[UpdateSchemaBase], 
        response_schema: Type[BaseBusinessObjectSchema],
        prefix: str = "",
        tags: Optional[List[str]] = None,
        enable_extensions: bool = True,
        enable_audit_trail: bool = True,
        require_authentication: bool = True,
        enforce_company_isolation: bool = None
    ):
        """Initialize the Business Object Router."""
        self.model_class = model_class
        self.service_class = service_class
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.response_schema = response_schema
        self.prefix = prefix
        self.tags = tags or []
        self.enable_extensions = enable_extensions
        self.enable_audit_trail = enable_audit_trail
        self.require_authentication = require_authentication
        
        # Auto-detect company isolation based on model type
        if enforce_company_isolation is None:
            self.enforce_company_isolation = issubclass(model_class, CompanyBaseModel)
        else:
            self.enforce_company_isolation = enforce_company_isolation
        
        # Create the FastAPI router
        self.router = APIRouter(prefix=prefix, tags=tags)
        
        # Generate all endpoints
        self.create_endpoints()
    
    def create_endpoints(self):
        """Create all CRUD endpoints for the business object."""
        entity_type = self.model_class.__name__.lower()
        
        # Standard CRUD endpoints
        self.router.add_api_route(
            "/",
            self.get_create_endpoint(),
            methods=["POST"],
            response_model=None,
            status_code=201,
            summary=f"Create {entity_type}",
            description=f"Create a new {entity_type} instance"
        )
        
        self.router.add_api_route(
            "/{object_id}",
            self.get_read_endpoint(),
            methods=["GET"],
            response_model=None,
            summary=f"Get {entity_type}",
            description=f"Get a {entity_type} by ID"
        )
        
        self.router.add_api_route(
            "/",
            self.get_list_endpoint(),
            methods=["GET"],
            response_model=None,
            summary=f"List {entity_type}s",
            description=f"Get a paginated list of {entity_type}s"
        )
        
        self.router.add_api_route(
            "/{object_id}",
            self.get_update_endpoint(),
            methods=["PUT"],
            response_model=None,
            summary=f"Update {entity_type}",
            description=f"Update a {entity_type} by ID"
        )
        
        self.router.add_api_route(
            "/{object_id}",
            self.get_delete_endpoint(),
            methods=["DELETE"],
            response_model=None,
            status_code=204,
            summary=f"Delete {entity_type}",
            description=f"Delete a {entity_type} by ID"
        )
        
        # Extension endpoints
        if self.enable_extensions:
            self.add_extension_endpoints(self.router, entity_type)
        
        # Audit trail endpoints
        if self.enable_audit_trail:
            self.add_audit_endpoints(self.router, entity_type)
    
    def get_create_endpoint(self) -> Callable:
        """Generate the CREATE endpoint function."""
        
        async def create_endpoint(
            create_data: self.create_schema,
            db: AsyncSession = Depends(get_db),
            current_user: dict = Depends(get_current_user) if self.require_authentication else None
        ):
            """Create a new object."""
            try:
                # Company access validation for company-scoped objects
                if self.enforce_company_isolation and hasattr(create_data, 'company_id'):
                    await require_company_access(current_user, create_data.company_id)
                
                # Create the object using the service
                service = self.service_class(db)
                
                # Convert Pydantic model to dict for service
                create_dict = create_data.model_dump()
                
                # Add audit context if available
                if current_user:
                    create_dict['_audit_user_id'] = current_user.get('user_id')
                
                # Create the object
                created_obj = await service.create(create_dict)
                
                # Convert to response format
                if hasattr(created_obj, '__dict__'):
                    response_data = {k: v for k, v in created_obj.__dict__.items() if not k.startswith('_')}
                else:
                    response_data = created_obj
                
                return ResponseFormatter.format_created_response(
                    response_data,
                    meta={"entity_type": self.model_class.__name__.lower()}
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
                error_response = StandardizedErrorHandler.handle_database_error(e)
                return StandardizedErrorHandler.format_error_response(error_response)
        
        return create_endpoint
    
    def get_read_endpoint(self) -> Callable:
        """Generate the READ endpoint function."""
        
        async def read_endpoint(
            object_id: int = Path(..., description="Object ID"),
            db: AsyncSession = Depends(get_db),
            current_user: dict = Depends(get_current_user) if self.require_authentication else None
        ):
            """Get an object by ID."""
            try:
                service = self.service_class(db)
                obj = await service.get_by_id(object_id)
                
                if not obj:
                    entity_type = self.model_class.__name__.lower()
                    error_response = StandardizedErrorHandler.handle_not_found_error(entity_type, object_id)
                    return StandardizedErrorHandler.format_error_response(error_response)
                
                # Company access validation
                if self.enforce_company_isolation and hasattr(obj, 'company_id'):
                    await require_company_access(current_user, obj.company_id)
                
                # Convert to response format
                if hasattr(obj, '__dict__'):
                    response_data = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
                else:
                    response_data = obj
                
                return ResponseFormatter.format_single_response(
                    response_data,
                    meta={"entity_type": self.model_class.__name__.lower()}
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting {self.model_class.__name__} {object_id}: {str(e)}")
                error_response = StandardizedErrorHandler.handle_database_error(e)
                return StandardizedErrorHandler.format_error_response(error_response)
        
        return read_endpoint
    
    def get_list_endpoint(self) -> Callable:
        """Generate the LIST endpoint function."""
        
        async def list_endpoint(
            page: int = Query(1, ge=1, description="Page number"),
            per_page: int = Query(50, ge=1, le=100, description="Items per page"),
            db: AsyncSession = Depends(get_db),
            current_user: dict = Depends(get_current_user) if self.require_authentication else None
        ):
            """Get a paginated list of objects."""
            try:
                service = self.service_class(db)
                
                # Build filters for company isolation
                filters = {}
                if self.enforce_company_isolation and current_user:
                    user_companies = current_user.get('company_ids', [])
                    if user_companies:
                        filters['company_id__in'] = user_companies
                
                # Get paginated list
                objects, total = await service.get_list(
                    filters=filters,
                    offset=(page - 1) * per_page,
                    limit=per_page
                )
                
                # Convert to response format
                response_data = []
                for obj in objects:
                    if hasattr(obj, '__dict__'):
                        obj_data = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
                    else:
                        obj_data = obj
                    response_data.append(obj_data)
                
                return ResponseFormatter.format_list_response(
                    response_data,
                    total,
                    page=page,
                    per_page=per_page,
                    meta={"entity_type": self.model_class.__name__.lower()}
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error listing {self.model_class.__name__}: {str(e)}")
                error_response = StandardizedErrorHandler.handle_database_error(e)
                return StandardizedErrorHandler.format_error_response(error_response)
        
        return list_endpoint
    
    def get_update_endpoint(self) -> Callable:
        """Generate the UPDATE endpoint function."""
        
        async def update_endpoint(
            object_id: int = Path(..., description="Object ID"),
            update_data: self.update_schema = Body(...),
            db: AsyncSession = Depends(get_db),
            current_user: dict = Depends(get_current_user) if self.require_authentication else None
        ):
            """Update an object by ID."""
            try:
                service = self.service_class(db)
                
                # Get existing object for validation
                existing_obj = await service.get_by_id(object_id)
                if not existing_obj:
                    entity_type = self.model_class.__name__.lower()
                    error_response = StandardizedErrorHandler.handle_not_found_error(entity_type, object_id)
                    return StandardizedErrorHandler.format_error_response(error_response)
                
                # Company access validation
                if self.enforce_company_isolation and hasattr(existing_obj, 'company_id'):
                    await require_company_access(current_user, existing_obj.company_id)
                
                # Convert Pydantic model to dict for service
                update_dict = update_data.model_dump(exclude_unset=True)
                
                # Add audit context if available
                if current_user:
                    update_dict['_audit_user_id'] = current_user.get('user_id')
                
                # Update the object
                updated_obj = await service.update(object_id, update_dict)
                
                # Convert to response format
                if hasattr(updated_obj, '__dict__'):
                    response_data = {k: v for k, v in updated_obj.__dict__.items() if not k.startswith('_')}
                else:
                    response_data = updated_obj
                
                return ResponseFormatter.format_updated_response(
                    response_data,
                    meta={"entity_type": self.model_class.__name__.lower()}
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error updating {self.model_class.__name__} {object_id}: {str(e)}")
                error_response = StandardizedErrorHandler.handle_database_error(e)
                return StandardizedErrorHandler.format_error_response(error_response)
        
        return update_endpoint
    
    def get_delete_endpoint(self) -> Callable:
        """Generate the DELETE endpoint function."""
        
        async def delete_endpoint(
            object_id: int = Path(..., description="Object ID"),
            db: AsyncSession = Depends(get_db),
            current_user: dict = Depends(get_current_user) if self.require_authentication else None
        ):
            """Delete an object by ID."""
            try:
                service = self.service_class(db)
                
                # Get existing object for validation
                existing_obj = await service.get_by_id(object_id)
                if not existing_obj:
                    entity_type = self.model_class.__name__.lower()
                    error_response = StandardizedErrorHandler.handle_not_found_error(entity_type, object_id)
                    return StandardizedErrorHandler.format_error_response(error_response)
                
                # Company access validation
                if self.enforce_company_isolation and hasattr(existing_obj, 'company_id'):
                    await require_company_access(current_user, existing_obj.company_id)
                
                # Add audit context if available
                audit_context = {}
                if current_user:
                    audit_context['_audit_user_id'] = current_user.get('user_id')
                
                # Delete the object
                success = await service.delete(object_id, **audit_context)
                
                if not success:
                    entity_type = self.model_class.__name__.lower()
                    error_response = StandardizedErrorHandler.handle_not_found_error(entity_type, object_id)
                    return StandardizedErrorHandler.format_error_response(error_response)
                
                return ResponseFormatter.format_deleted_response(
                    meta={"entity_type": self.model_class.__name__.lower(), "deleted_id": object_id}
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error deleting {self.model_class.__name__} {object_id}: {str(e)}")
                error_response = StandardizedErrorHandler.handle_database_error(e)
                return StandardizedErrorHandler.format_error_response(error_response)
        
        return delete_endpoint


def create_business_object_router(
    model_class: Type[BaseModel],
    service_class: Type[BusinessObjectService],
    create_schema: Type[CreateSchemaBase],
    update_schema: Type[UpdateSchemaBase],
    response_schema: Type[BaseBusinessObjectSchema],
    prefix: str = "",
    tags: Optional[List[str]] = None,
    enable_extensions: bool = True,
    enable_audit_trail: bool = True,
    require_authentication: bool = True,
    enforce_company_isolation: bool = None
) -> BusinessObjectRouter:
    """
    Factory function for creating standardized Business Object routers.
    
    Creates a complete REST API router for a business object with all standard
    CRUD operations, error handling, authentication, and optional extension support.
    
    Args:
        model_class: SQLAlchemy model class
        service_class: Service class for business logic
        create_schema: Pydantic schema for creation requests
        update_schema: Pydantic schema for update requests  
        response_schema: Pydantic schema for responses
        prefix: URL prefix for all endpoints
        tags: OpenAPI tags for documentation
        enable_extensions: Whether to add extension endpoints
        enable_audit_trail: Whether to add audit trail endpoints
        require_authentication: Whether to require authentication
        enforce_company_isolation: Whether to enforce company-based access control
        
    Returns:
        Configured BusinessObjectRouter instance
    """
    return BusinessObjectRouter(
        model_class=model_class,
        service_class=service_class,
        create_schema=create_schema,
        update_schema=update_schema,
        response_schema=response_schema,
        prefix=prefix,
        tags=tags,
        enable_extensions=enable_extensions,
        enable_audit_trail=enable_audit_trail,
        require_authentication=require_authentication,
        enforce_company_isolation=enforce_company_isolation
    )