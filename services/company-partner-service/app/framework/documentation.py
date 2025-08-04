"""
API Documentation Templates for Business Object Framework.

Provides standardized documentation templates, examples, and utilities
for generating consistent API documentation across all business object endpoints.
"""

from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel

from app.framework.schemas import BaseBusinessObjectSchema, CreateSchemaBase, UpdateSchemaBase


class APIDocumentationTemplate:
    """
    Template generator for API documentation.
    
    Creates consistent OpenAPI documentation with examples, descriptions,
    and response schemas for all business object endpoints.
    """
    
    @staticmethod
    def generate_endpoint_docs(
        entity_name: str,
        entity_description: str,
        create_schema: Type[CreateSchemaBase],
        update_schema: Type[UpdateSchemaBase],
        response_schema: Type[BaseBusinessObjectSchema]
    ) -> Dict[str, Any]:
        """
        Generate complete endpoint documentation for a business object.
        
        Args:
            entity_name: Name of the entity (e.g., "partner", "company")
            entity_description: Human-readable description
            create_schema: Pydantic schema for creation
            update_schema: Pydantic schema for updates
            response_schema: Pydantic schema for responses
            
        Returns:
            Dictionary with documentation for all endpoints
        """
        docs = {
            "create": APIDocumentationTemplate._create_endpoint_docs(
                entity_name, entity_description, create_schema, response_schema
            ),
            "read": APIDocumentationTemplate._read_endpoint_docs(
                entity_name, entity_description, response_schema
            ),
            "list": APIDocumentationTemplate._list_endpoint_docs(
                entity_name, entity_description, response_schema
            ),
            "update": APIDocumentationTemplate._update_endpoint_docs(
                entity_name, entity_description, update_schema, response_schema
            ),
            "delete": APIDocumentationTemplate._delete_endpoint_docs(
                entity_name, entity_description
            ),
            "extensions": APIDocumentationTemplate._extension_endpoint_docs(
                entity_name, entity_description
            ),
            "audit": APIDocumentationTemplate._audit_endpoint_docs(
                entity_name, entity_description
            )
        }
        return docs
    
    @staticmethod
    def _create_endpoint_docs(
        entity_name: str,
        entity_description: str,
        create_schema: Type[CreateSchemaBase],
        response_schema: Type[BaseBusinessObjectSchema]
    ) -> Dict[str, Any]:
        """Generate CREATE endpoint documentation."""
        return {
            "summary": f"Create {entity_name}",
            "description": f"Create a new {entity_name} instance with the provided data.",
            "operation_id": f"create_{entity_name}",
            "tags": [f"{entity_name}s"],
            "request_body": {
                "description": f"Data for creating a new {entity_name}",
                "required": True,
                "content": {
                    "application/json": {
                        "schema": create_schema.model_json_schema(),
                        "example": APIDocumentationTemplate._generate_create_example(entity_name)
                    }
                }
            },
            "responses": {
                "201": {
                    "description": f"{entity_name.title()} created successfully",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": response_schema.model_json_schema(),
                                    "meta": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string", "example": "created"},
                                            "status_code": {"type": "integer", "example": 201},
                                            "timestamp": {"type": "string", "format": "date-time"},
                                            "entity_type": {"type": "string", "example": entity_name}
                                        }
                                    }
                                }
                            },
                            "example": APIDocumentationTemplate._generate_create_response_example(entity_name)
                        }
                    }
                },
                "422": APIDocumentationTemplate._validation_error_response(),
                "403": APIDocumentationTemplate._permission_error_response(),
                "500": APIDocumentationTemplate._server_error_response()
            }
        }
    
    @staticmethod
    def _read_endpoint_docs(
        entity_name: str,
        entity_description: str,
        response_schema: Type[BaseBusinessObjectSchema]
    ) -> Dict[str, Any]:
        """Generate READ endpoint documentation."""
        return {
            "summary": f"Get {entity_name}",
            "description": f"Retrieve a specific {entity_name} by its ID.",
            "operation_id": f"get_{entity_name}",
            "tags": [f"{entity_name}s"],
            "parameters": [
                {
                    "name": "object_id",
                    "in": "path",
                    "description": f"The ID of the {entity_name} to retrieve",
                    "required": True,
                    "schema": {"type": "integer", "minimum": 1},
                    "example": 1
                }
            ],
            "responses": {
                "200": {
                    "description": f"{entity_name.title()} retrieved successfully",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": response_schema.model_json_schema(),
                                    "meta": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string", "example": "single"},
                                            "timestamp": {"type": "string", "format": "date-time"},
                                            "entity_type": {"type": "string", "example": entity_name}
                                        }
                                    }
                                }
                            },
                            "example": APIDocumentationTemplate._generate_read_response_example(entity_name)
                        }
                    }
                },
                "404": APIDocumentationTemplate._not_found_error_response(entity_name),
                "403": APIDocumentationTemplate._permission_error_response(),
                "500": APIDocumentationTemplate._server_error_response()
            }
        }
    
    @staticmethod
    def _list_endpoint_docs(
        entity_name: str,
        entity_description: str,
        response_schema: Type[BaseBusinessObjectSchema]
    ) -> Dict[str, Any]:
        """Generate LIST endpoint documentation."""
        return {
            "summary": f"List {entity_name}s",
            "description": f"Retrieve a paginated list of {entity_name}s with optional filtering.",
            "operation_id": f"list_{entity_name}s",
            "tags": [f"{entity_name}s"],
            "parameters": [
                {
                    "name": "page",
                    "in": "query",
                    "description": "Page number for pagination",
                    "schema": {"type": "integer", "minimum": 1, "default": 1},
                    "example": 1
                },
                {
                    "name": "per_page",
                    "in": "query",
                    "description": "Number of items per page",
                    "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 50},
                    "example": 50
                }
            ],
            "responses": {
                "200": {
                    "description": f"{entity_name.title()}s retrieved successfully",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "array",
                                        "items": response_schema.model_json_schema()
                                    },
                                    "meta": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string", "example": "list"},
                                            "total": {"type": "integer", "example": 150},
                                            "page": {"type": "integer", "example": 1},
                                            "per_page": {"type": "integer", "example": 50},
                                            "total_pages": {"type": "integer", "example": 3},
                                            "has_next": {"type": "boolean", "example": True},
                                            "has_previous": {"type": "boolean", "example": False},
                                            "timestamp": {"type": "string", "format": "date-time"},
                                            "entity_type": {"type": "string", "example": entity_name}
                                        }
                                    }
                                }
                            },
                            "example": APIDocumentationTemplate._generate_list_response_example(entity_name)
                        }
                    }
                },
                "403": APIDocumentationTemplate._permission_error_response(),
                "500": APIDocumentationTemplate._server_error_response()
            }
        }
    
    @staticmethod
    def _update_endpoint_docs(
        entity_name: str,
        entity_description: str,
        update_schema: Type[UpdateSchemaBase],
        response_schema: Type[BaseBusinessObjectSchema]
    ) -> Dict[str, Any]:
        """Generate UPDATE endpoint documentation."""
        return {
            "summary": f"Update {entity_name}",
            "description": f"Update an existing {entity_name} with the provided data. Only provided fields will be updated.",
            "operation_id": f"update_{entity_name}",
            "tags": [f"{entity_name}s"],
            "parameters": [
                {
                    "name": "object_id",
                    "in": "path",
                    "description": f"The ID of the {entity_name} to update",
                    "required": True,
                    "schema": {"type": "integer", "minimum": 1},
                    "example": 1
                }
            ],
            "request_body": {
                "description": f"Updated data for the {entity_name}",
                "required": True,
                "content": {
                    "application/json": {
                        "schema": update_schema.model_json_schema(),
                        "example": APIDocumentationTemplate._generate_update_example(entity_name)
                    }
                }
            },
            "responses": {
                "200": {
                    "description": f"{entity_name.title()} updated successfully",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": response_schema.model_json_schema(),
                                    "meta": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string", "example": "updated"},
                                            "status_code": {"type": "integer", "example": 200},
                                            "timestamp": {"type": "string", "format": "date-time"},
                                            "entity_type": {"type": "string", "example": entity_name}
                                        }
                                    }
                                }
                            },
                            "example": APIDocumentationTemplate._generate_update_response_example(entity_name)
                        }
                    }
                },
                "404": APIDocumentationTemplate._not_found_error_response(entity_name),
                "422": APIDocumentationTemplate._validation_error_response(),
                "403": APIDocumentationTemplate._permission_error_response(),
                "500": APIDocumentationTemplate._server_error_response()
            }
        }
    
    @staticmethod
    def _delete_endpoint_docs(entity_name: str, entity_description: str) -> Dict[str, Any]:
        """Generate DELETE endpoint documentation."""
        return {
            "summary": f"Delete {entity_name}",
            "description": f"Delete a {entity_name} by its ID. This operation cannot be undone.",
            "operation_id": f"delete_{entity_name}",
            "tags": [f"{entity_name}s"],
            "parameters": [
                {
                    "name": "object_id",
                    "in": "path",
                    "description": f"The ID of the {entity_name} to delete",
                    "required": True,
                    "schema": {"type": "integer", "minimum": 1},
                    "example": 1
                }
            ],
            "responses": {
                "204": {
                    "description": f"{entity_name.title()} deleted successfully",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "meta": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string", "example": "deleted"},
                                            "status_code": {"type": "integer", "example": 204},
                                            "timestamp": {"type": "string", "format": "date-time"},
                                            "entity_type": {"type": "string", "example": entity_name},
                                            "deleted_id": {"type": "integer", "example": 1}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "404": APIDocumentationTemplate._not_found_error_response(entity_name),
                "403": APIDocumentationTemplate._permission_error_response(),
                "500": APIDocumentationTemplate._server_error_response()
            }
        }
    
    @staticmethod
    def _extension_endpoint_docs(entity_name: str, entity_description: str) -> Dict[str, Any]:
        """Generate extension endpoint documentation."""
        return {
            "get_extensions": {
                "summary": f"Get {entity_name} extensions",
                "description": f"Retrieve all custom field extensions for a {entity_name}.",
                "operation_id": f"get_{entity_name}_extensions",
                "tags": [f"{entity_name}-extensions"],
                "parameters": [
                    {
                        "name": "object_id",
                        "in": "path",
                        "description": f"The ID of the {entity_name}",
                        "required": True,
                        "schema": {"type": "integer", "minimum": 1},
                        "example": 1
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Extensions retrieved successfully",
                        "content": {
                            "application/json": {
                                "example": {
                                    "data": [
                                        {
                                            "id": 1,
                                            "field_name": "custom_rating",
                                            "field_type": "integer",
                                            "field_value": "5",
                                            "typed_value": 5,
                                            "created_at": "2025-08-01T10:00:00Z",
                                            "updated_at": "2025-08-01T10:00:00Z"
                                        }
                                    ],
                                    "meta": {
                                        "type": "list",
                                        "entity_type": entity_name,
                                        "entity_id": 1
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "set_extension": {
                "summary": f"Set {entity_name} extension",
                "description": f"Create or update a custom field extension for a {entity_name}.",
                "operation_id": f"set_{entity_name}_extension",
                "tags": [f"{entity_name}-extensions"],
                "request_body": {
                    "content": {
                        "application/json": {
                            "example": {
                                "field_name": "custom_rating",
                                "field_type": "integer",
                                "field_value": "5"
                            }
                        }
                    }
                }
            }
        }
    
    @staticmethod
    def _audit_endpoint_docs(entity_name: str, entity_description: str) -> Dict[str, Any]:
        """Generate audit endpoint documentation."""
        return {
            "get_audit_trail": {
                "summary": f"Get {entity_name} audit trail",
                "description": f"Retrieve the audit trail for a {entity_name}.",
                "operation_id": f"get_{entity_name}_audit_trail",
                "tags": [f"{entity_name}-audit"],
                "responses": {
                    "200": {
                        "description": "Audit trail retrieved successfully",
                        "content": {
                            "application/json": {
                                "example": {
                                    "data": [
                                        {
                                            "id": "audit_1_1",
                                            "action": "created",
                                            "timestamp": "2025-08-01T10:00:00Z",
                                            "user_id": 1,
                                            "changes": {"created": True}
                                        }
                                    ],
                                    "meta": {
                                        "type": "list",
                                        "total": 1,
                                        "page": 1,
                                        "per_page": 50,
                                        "entity_type": entity_name,
                                        "entity_id": 1
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    # Example generators
    @staticmethod
    def _generate_create_example(entity_name: str) -> Dict[str, Any]:
        """Generate example for CREATE requests."""
        examples = {
            "partner": {
                "name": "Acme Corp",
                "partner_type": "company",
                "email": "contact@acme.com",
                "phone": "+1-555-0123",
                "company_id": 1
            },
            "company": {
                "name": "My Company",
                "code": "MYCO",
                "currency": "USD"
            }
        }
        return examples.get(entity_name, {"name": f"New {entity_name.title()}"})
    
    @staticmethod
    def _generate_create_response_example(entity_name: str) -> Dict[str, Any]:
        """Generate example for CREATE responses."""
        return {
            "data": {
                "id": 1,
                **APIDocumentationTemplate._generate_create_example(entity_name),
                "created_at": "2025-08-01T10:00:00Z",
                "updated_at": "2025-08-01T10:00:00Z",
                "framework_version": "1.0.0"
            },
            "meta": {
                "type": "created",
                "status_code": 201,
                "timestamp": "2025-08-01T10:00:00Z",
                "entity_type": entity_name
            }
        }
    
    @staticmethod
    def _generate_read_response_example(entity_name: str) -> Dict[str, Any]:
        """Generate example for READ responses."""
        return {
            "data": {
                "id": 1,
                **APIDocumentationTemplate._generate_create_example(entity_name),
                "created_at": "2025-08-01T10:00:00Z",
                "updated_at": "2025-08-01T10:00:00Z",
                "framework_version": "1.0.0"
            },
            "meta": {
                "type": "single",
                "timestamp": "2025-08-01T10:00:00Z",
                "entity_type": entity_name
            }
        }
    
    @staticmethod
    def _generate_list_response_example(entity_name: str) -> Dict[str, Any]:
        """Generate example for LIST responses."""
        return {
            "data": [
                {
                    "id": 1,
                    **APIDocumentationTemplate._generate_create_example(entity_name),
                    "created_at": "2025-08-01T10:00:00Z",
                    "updated_at": "2025-08-01T10:00:00Z",
                    "framework_version": "1.0.0"
                },
                {
                    "id": 2,
                    **APIDocumentationTemplate._generate_create_example(entity_name),
                    "created_at": "2025-08-01T10:00:00Z",
                    "updated_at": "2025-08-01T10:00:00Z",
                    "framework_version": "1.0.0"
                }
            ],
            "meta": {
                "type": "list",
                "total": 150,
                "page": 1,
                "per_page": 50,
                "total_pages": 3,
                "has_next": True,
                "has_previous": False,
                "timestamp": "2025-08-01T10:00:00Z",
                "entity_type": entity_name
            }
        }
    
    @staticmethod
    def _generate_update_example(entity_name: str) -> Dict[str, Any]:
        """Generate example for UPDATE requests."""
        examples = {
            "partner": {
                "name": "Updated Acme Corp",
                "email": "newemail@acme.com"
            },
            "company": {
                "name": "Updated Company Name"
            }
        }
        return examples.get(entity_name, {"name": f"Updated {entity_name.title()}"})
    
    @staticmethod
    def _generate_update_response_example(entity_name: str) -> Dict[str, Any]:
        """Generate example for UPDATE responses."""
        return {
            "data": {
                "id": 1,
                **APIDocumentationTemplate._generate_create_example(entity_name),
                **APIDocumentationTemplate._generate_update_example(entity_name),
                "created_at": "2025-08-01T10:00:00Z",
                "updated_at": "2025-08-01T10:05:00Z",
                "framework_version": "1.0.0"
            },
            "meta": {
                "type": "updated",
                "status_code": 200,
                "timestamp": "2025-08-01T10:05:00Z",
                "entity_type": entity_name
            }
        }
    
    # Error response templates
    @staticmethod
    def _validation_error_response() -> Dict[str, Any]:
        """Standard validation error response."""
        return {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error_code": {"type": "string", "example": "VALIDATION_ERROR"},
                            "message": {"type": "string", "example": "Validation failed"},
                            "details": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "field": {"type": "string"},
                                        "message": {"type": "string"}
                                    }
                                }
                            },
                            "timestamp": {"type": "string", "format": "date-time"}
                        }
                    },
                    "example": {
                        "error_code": "VALIDATION_ERROR",
                        "message": "Validation failed",
                        "details": [
                            {"field": "name", "message": "Name is required"},
                            {"field": "email", "message": "Invalid email format"}
                        ],
                        "timestamp": "2025-08-01T10:00:00Z"
                    }
                }
            }
        }
    
    @staticmethod
    def _not_found_error_response(entity_name: str) -> Dict[str, Any]:
        """Standard not found error response."""
        return {
            "description": f"{entity_name.title()} not found",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error_code": {"type": "string", "example": "NOT_FOUND"},
                            "message": {"type": "string", "example": f"{entity_name.title()} with ID 1 not found"},
                            "timestamp": {"type": "string", "format": "date-time"}
                        }
                    },
                    "example": {
                        "error_code": "NOT_FOUND",
                        "message": f"{entity_name.title()} with ID 1 not found",
                        "timestamp": "2025-08-01T10:00:00Z"
                    }
                }
            }
        }
    
    @staticmethod
    def _permission_error_response() -> Dict[str, Any]:
        """Standard permission error response."""
        return {
            "description": "Permission denied",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error_code": {"type": "string", "example": "PERMISSION_DENIED"},
                            "message": {"type": "string", "example": "Permission denied for read on resource"},
                            "timestamp": {"type": "string", "format": "date-time"}
                        }
                    },
                    "example": {
                        "error_code": "PERMISSION_DENIED",
                        "message": "Permission denied for read on resource",
                        "timestamp": "2025-08-01T10:00:00Z"
                    }
                }
            }
        }
    
    @staticmethod
    def _server_error_response() -> Dict[str, Any]:
        """Standard server error response."""
        return {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error_code": {"type": "string", "example": "DATABASE_ERROR"},
                            "message": {"type": "string", "example": "A database error occurred"},
                            "timestamp": {"type": "string", "format": "date-time"}
                        }
                    },
                    "example": {
                        "error_code": "DATABASE_ERROR",
                        "message": "A database error occurred",
                        "timestamp": "2025-08-01T10:00:00Z"
                    }
                }
            }
        }


class QuickStartGuideGenerator:
    """
    Generator for Business Object Framework quick-start guide.
    
    Creates step-by-step examples for implementing new business objects
    using the framework templates and patterns.
    """
    
    @staticmethod
    def generate_implementation_example(entity_name: str) -> Dict[str, str]:
        """
        Generate a complete implementation example for a business object.
        
        Args:
            entity_name: Name of the entity to implement
            
        Returns:
            Dictionary with code examples for each step
        """
        examples = {
            "model": QuickStartGuideGenerator._generate_model_example(entity_name),
            "schemas": QuickStartGuideGenerator._generate_schemas_example(entity_name),
            "service": QuickStartGuideGenerator._generate_service_example(entity_name),
            "router": QuickStartGuideGenerator._generate_router_example(entity_name),
            "registration": QuickStartGuideGenerator._generate_registration_example(entity_name)
        }
        return examples
    
    @staticmethod
    def _generate_model_example(entity_name: str) -> str:
        """Generate SQLAlchemy model example."""
        return f'''"""
{entity_name.title()} model implementation.
"""

from sqlalchemy import Column, String, Text, Boolean
from app.models.base import CompanyBaseModel


class {entity_name.title()}(CompanyBaseModel):
    """
    {entity_name.title()} business object.
    
    Represents a {entity_name} entity with company isolation and framework features.
    """
    
    __tablename__ = "{entity_name}s"
    
    # Business fields
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Add custom fields as needed for your business logic
    
    def __repr__(self):
        return f"<{entity_name.title()}(id={{self.id}}, name='{{self.name}}', company_id={{self.company_id}})>"
'''
    
    @staticmethod
    def _generate_schemas_example(entity_name: str) -> str:
        """Generate Pydantic schemas example."""
        return f'''"""
{entity_name.title()} Pydantic schemas.
"""

from typing import Optional
from pydantic import Field, field_validator

from app.framework.schemas import (
    CompanyBusinessObjectSchema,
    CreateSchemaBase,
    UpdateSchemaBase,
    ResponseSchemaBase
)


class {entity_name.title()}CreateSchema(CreateSchemaBase):
    """Schema for creating {entity_name}s."""
    
    name: str = Field(..., description="{entity_name.title()} name", max_length=200)
    description: Optional[str] = Field(None, description="{entity_name.title()} description")
    is_active: bool = Field(True, description="Whether the {entity_name} is active")
    company_id: int = Field(..., description="Company ID", ge=1)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class {entity_name.title()}UpdateSchema(UpdateSchemaBase):
    """Schema for updating {entity_name}s."""
    
    name: Optional[str] = Field(None, description="{entity_name.title()} name", max_length=200)
    description: Optional[str] = Field(None, description="{entity_name.title()} description")
    is_active: Optional[bool] = Field(None, description="Whether the {entity_name} is active")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v


class {entity_name.title()}ResponseSchema(CompanyBusinessObjectSchema):
    """Schema for {entity_name} responses."""
    
    name: str
    description: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True
'''
    
    @staticmethod
    def _generate_service_example(entity_name: str) -> str:
        """Generate service class example."""
        return f'''"""
{entity_name.title()} service implementation.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.framework.services import CompanyBusinessObjectService
from app.models.{entity_name} import {entity_name.title()}


class {entity_name.title()}Service(CompanyBusinessObjectService[{entity_name.title()}]):
    """
    Service for {entity_name} business logic.
    
    Inherits all standard CRUD operations from CompanyBusinessObjectService
    and adds {entity_name}-specific business logic.
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, {entity_name.title()})
    
    # Add custom business methods here
    async def find_by_name(self, name: str, company_id: int):
        """Find {entity_name} by name within a company."""
        return await self.get_by_filters({{"name": name, "company_id": company_id}})
    
    async def activate(self, {entity_name}_id: int) -> {entity_name.title()}:
        """Activate a {entity_name}."""
        return await self.update({entity_name}_id, {{"is_active": True}})
    
    async def deactivate(self, {entity_name}_id: int) -> {entity_name.title()}:
        """Deactivate a {entity_name}."""
        return await self.update({entity_name}_id, {{"is_active": False}})
'''
    
    @staticmethod
    def _generate_router_example(entity_name: str) -> str:
        """Generate router implementation example."""
        return f'''"""
{entity_name.title()} API router.
"""

from app.framework.controllers import create_business_object_router
from app.models.{entity_name} import {entity_name.title()}
from app.services.{entity_name}_service import {entity_name.title()}Service
from app.schemas.{entity_name} import (
    {entity_name.title()}CreateSchema,
    {entity_name.title()}UpdateSchema,
    {entity_name.title()}ResponseSchema
)

# Create the standardized router
{entity_name}_router = create_business_object_router(
    model_class={entity_name.title()},
    service_class={entity_name.title()}Service,
    create_schema={entity_name.title()}CreateSchema,
    update_schema={entity_name.title()}UpdateSchema,
    response_schema={entity_name.title()}ResponseSchema,
    prefix="/api/v1/{entity_name}s",
    tags=["{entity_name}s"],
    enable_extensions=True,
    enable_audit_trail=True,
    require_authentication=True,
    enforce_company_isolation=True
)

# Access the FastAPI router
router = {entity_name}_router.router

# Add custom endpoints if needed
@router.post("/{{{entity_name}_id}}/activate")
async def activate_{entity_name}({entity_name}_id: int):
    """Custom endpoint to activate a {entity_name}."""
    # Implementation here
    pass
'''
    
    @staticmethod
    def _generate_registration_example(entity_name: str) -> str:
        """Generate main app registration example."""
        return f'''"""
Register {entity_name} router in main.py
"""

# In your FastAPI main.py file:

from app.routers.{entity_name} import router as {entity_name}_router

# Add to your FastAPI app
app.include_router({entity_name}_router)

# That's it! Your {entity_name} API is now available with:
# - POST /api/v1/{entity_name}s (create)
# - GET /api/v1/{entity_name}s/{{id}} (read)
# - GET /api/v1/{entity_name}s (list with pagination)
# - PUT /api/v1/{entity_name}s/{{id}} (update)
# - DELETE /api/v1/{entity_name}s/{{id}} (delete)
# - GET /api/v1/{entity_name}s/{{id}}/extensions (get custom fields)
# - POST /api/v1/{entity_name}s/{{id}}/extensions (set custom field)
# - DELETE /api/v1/{entity_name}s/{{id}}/extensions/{{field_name}} (delete custom field)
# - GET /api/v1/{entity_name}s/{{id}}/audit (get audit trail)
# - GET /api/v1/{entity_name}s/{{id}}/changes (get recent changes)
'''
    
    @staticmethod
    def generate_quick_start_guide() -> str:
        """Generate complete quick-start guide."""
        return '''# Business Object Framework Quick Start Guide

This guide shows you how to create a new business object API in just 5 minutes using the Business Object Framework.

## Step 1: Create the SQLAlchemy Model

Create a new file `app/models/product.py`:

```python
"""
Product model implementation.
"""

from sqlalchemy import Column, String, Text, Boolean, Decimal
from app.models.base import CompanyBaseModel


class Product(CompanyBaseModel):
    """
    Product business object.
    
    Represents a product entity with company isolation and framework features.
    """
    
    __tablename__ = "products"
    
    # Business fields
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Decimal(10, 2), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', company_id={self.company_id})>"
```

## Step 2: Create Pydantic Schemas

Create a new file `app/schemas/product.py`:

```python
"""
Product Pydantic schemas.
"""

from typing import Optional
from decimal import Decimal
from pydantic import Field, field_validator

from app.framework.schemas import (
    CompanyBusinessObjectSchema,
    CreateSchemaBase,
    UpdateSchemaBase
)


class ProductCreateSchema(CreateSchemaBase):
    """Schema for creating products."""
    
    name: str = Field(..., description="Product name", max_length=200)
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., description="Product price", ge=0)
    is_active: bool = Field(True, description="Whether the product is active")
    company_id: int = Field(..., description="Company ID", ge=1)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class ProductUpdateSchema(UpdateSchemaBase):
    """Schema for updating products."""
    
    name: Optional[str] = Field(None, description="Product name", max_length=200)
    description: Optional[str] = Field(None, description="Product description")
    price: Optional[Decimal] = Field(None, description="Product price", ge=0)
    is_active: Optional[bool] = Field(None, description="Whether the product is active")


class ProductResponseSchema(CompanyBusinessObjectSchema):
    """Schema for product responses."""
    
    name: str
    description: Optional[str]
    price: Decimal
    is_active: bool
    
    class Config:
        from_attributes = True
```

## Step 3: Create Service Class

Create a new file `app/services/product_service.py`:

```python
"""
Product service implementation.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.framework.services import CompanyBusinessObjectService
from app.models.product import Product


class ProductService(CompanyBusinessObjectService[Product]):
    """
    Service for product business logic.
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Product)
    
    # Add custom business methods
    async def find_by_name(self, name: str, company_id: int):
        """Find product by name within a company."""
        return await self.get_by_filters({"name": name, "company_id": company_id})
```

## Step 4: Create API Router

Create a new file `app/routers/products.py`:

```python
"""
Product API router.
"""

from app.framework.controllers import create_business_object_router
from app.models.product import Product
from app.services.product_service import ProductService
from app.schemas.product import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductResponseSchema
)

# Create the standardized router
product_router = create_business_object_router(
    model_class=Product,
    service_class=ProductService,
    create_schema=ProductCreateSchema,
    update_schema=ProductUpdateSchema,
    response_schema=ProductResponseSchema,
    prefix="/api/v1/products",
    tags=["products"],
    enable_extensions=True,
    enable_audit_trail=True,
    require_authentication=True,
    enforce_company_isolation=True
)

# Access the FastAPI router
router = product_router.router
```

## Step 5: Register Router

In your `app/main.py`, add:

```python
from app.routers.products import router as products_router

app.include_router(products_router)
```

## That's It! 🎉

Your Product API is now available with all these endpoints:

- `POST /api/v1/products` - Create product
- `GET /api/v1/products/{id}` - Get product by ID
- `GET /api/v1/products` - List products (paginated)
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `GET /api/v1/products/{id}/extensions` - Get custom fields
- `POST /api/v1/products/{id}/extensions` - Set custom field
- `DELETE /api/v1/products/{id}/extensions/{field_name}` - Delete custom field
- `GET /api/v1/products/{id}/audit` - Get audit trail
- `GET /api/v1/products/{id}/changes` - Get recent changes

## Features Included Automatically

✅ **Multi-company data isolation** - Users only see data from their companies
✅ **Authentication & authorization** - JWT token validation on all endpoints
✅ **Standardized error handling** - Consistent error responses with proper HTTP codes
✅ **Request/response validation** - Automatic Pydantic validation
✅ **Custom fields support** - Add custom fields dynamically via API
✅ **Audit trail** - Automatic logging of all changes
✅ **Pagination** - Built-in pagination for list endpoints
✅ **OpenAPI documentation** - Auto-generated API docs
✅ **Extension endpoints** - Custom field management out of the box
✅ **Event publishing** - Automatic event publishing for integrations

## Next Steps

1. **Add custom endpoints**: Extend the router with business-specific endpoints
2. **Custom validation**: Add field-specific validation rules  
3. **Business logic**: Implement custom methods in your service class
4. **Database migration**: Create Alembic migration for your new table
5. **Tests**: Write tests using the framework test utilities

The Business Object Framework handles all the boilerplate, so you can focus on your business logic!
'''


# Usage example
def create_product_documentation():
    """Example of generating documentation for a Product entity."""
    from app.schemas.product import ProductCreateSchema, ProductUpdateSchema, ProductResponseSchema
    
    docs = APIDocumentationTemplate.generate_endpoint_docs(
        entity_name="product",
        entity_description="Product management",
        create_schema=ProductCreateSchema,
        update_schema=ProductUpdateSchema,
        response_schema=ProductResponseSchema
    )
    
    return docs