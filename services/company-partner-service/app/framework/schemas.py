"""
Schema framework for Business Object Framework.

Provides standardized Pydantic schema classes with common validation
patterns, field handling, and templates for Create/Update/Response operations.
"""

from datetime import datetime
from typing import Optional, Dict, Any, Type, TypeVar, Generic
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.config import ConfigDict


# Type variable for generic schema classes
T = TypeVar('T')


class BaseBusinessObjectSchema(BaseModel):
    """
    Base schema class for all business objects.
    
    Provides common fields and validation rules that should be
    applied to all business objects in the system:
    - Standard field validation
    - User-friendly error messages
    - Automatic field transformation
    """
    
    model_config = ConfigDict(
        # Enable validation on assignment
        validate_assignment=True,
        # Use enum values instead of names
        use_enum_values=True,
        # Allow population by field name or alias
        populate_by_name=True,
        # Validate default values
        validate_default=True,
        # Include extra fields validation
        extra='forbid',
        # JSON encoders for serialization
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        # JSON schema examples
        json_schema_extra={
            "example": {
                "id": 1,
                "created_at": "2025-08-01T10:00:00Z",
                "updated_at": "2025-08-01T10:00:00Z",
                "framework_version": "1.0.0"
            }
        }
    )
    
    # Framework fields (read-only in most schemas)
    id: Optional[int] = Field(None, description="Unique identifier", ge=1)
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    framework_version: Optional[str] = Field(None, description="Framework version", max_length=20)
    
    @field_validator('framework_version')
    @classmethod
    def validate_framework_version(cls, v):
        """Validate framework version format."""
        if v is not None and not isinstance(v, str):
            raise ValueError("Framework version must be a string")
        return v
    
    @field_validator('created_at', 'updated_at')
    @classmethod
    def validate_timestamps(cls, v):
        """Validate timestamp fields."""
        if v is not None and not isinstance(v, datetime):
            raise ValueError("Timestamp must be a datetime object")
        return v


class CompanyBusinessObjectSchema(BaseBusinessObjectSchema):
    """
    Schema class for company-scoped business objects.
    
    Extends BaseBusinessObjectSchema with company_id field
    and multi-company validation rules.
    """
    
    company_id: Optional[int] = Field(None, description="Company ID for multi-tenant isolation", ge=1)
    
    @field_validator('company_id')
    @classmethod
    def validate_company_id(cls, v):
        """Validate company_id field."""
        if v is not None and (not isinstance(v, int) or v < 1):
            raise ValueError("Company ID must be a positive integer")
        return v


class CreateSchemaBase(BaseModel):
    """
    Base template for Create operation schemas.
    
    Excludes read-only fields like id, timestamps, and framework_version
    that are automatically managed by the system.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
        validate_default=True,
        extra='forbid'
    )
    
    # Create schemas should not include auto-managed fields
    # Subclasses will define their specific business fields


class UpdateSchemaBase(BaseModel):
    """
    Base template for Update operation schemas.
    
    Makes most fields optional to support partial updates.
    Excludes read-only fields that cannot be modified.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
        validate_default=True,
        extra='forbid'
    )
    
    # Update schemas make fields optional for partial updates
    # Subclasses will define their specific business fields as Optional


class ResponseSchemaBase(BaseBusinessObjectSchema):
    """
    Base template for Response schemas.
    
    Includes all fields that should be returned in API responses,
    including read-only framework fields.
    """
    
    # Response schemas include all fields from BaseBusinessObjectSchema
    # Subclasses will add their specific business fields


# Schema validation framework
class ValidationFramework:
    """
    Framework for custom validation rules and validators.
    
    Provides utilities for registering and applying custom
    validation logic to business object schemas.
    """
    
    _custom_validators: Dict[str, Any] = {}
    
    @classmethod
    def register_validator(cls, name: str, validator_func):
        """
        Register a custom validator function.
        
        Args:
            name: Validator name
            validator_func: Validation function
        """
        cls._custom_validators[name] = validator_func
    
    @classmethod
    def get_validator(cls, name: str):
        """
        Get a registered validator by name.
        
        Args:
            name: Validator name
            
        Returns:
            Validator function or None
        """
        return cls._custom_validators.get(name)
    
    @classmethod
    def apply_validators(cls, schema_class: Type[BaseModel], validators: list):
        """
        Apply custom validators to a schema class.
        
        Args:
            schema_class: Schema class to modify
            validators: List of validator names to apply
        """
        for validator_name in validators:
            validator_func = cls.get_validator(validator_name)
            if validator_func:
                # Apply validator to schema class
                setattr(schema_class, f'validate_{validator_name}', validator_func)


# Common validation rules
def validate_non_empty_string(v: str) -> str:
    """Validate that string is not empty or whitespace only."""
    if not v or not v.strip():
        raise ValueError("Field cannot be empty")
    return v.strip()


def validate_positive_integer(v: int) -> int:
    """Validate that integer is positive."""
    if v <= 0:
        raise ValueError("Value must be positive")
    return v


def validate_email_format(v: str) -> str:
    """Validate email format."""
    import re
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
        raise ValueError("Invalid email format")
    return v.lower()


# Register common validators
ValidationFramework.register_validator('non_empty_string', validate_non_empty_string)
ValidationFramework.register_validator('positive_integer', validate_positive_integer)
ValidationFramework.register_validator('email_format', validate_email_format)


# Schema factory functions
def create_schema_factory(
    model_class: Type,
    base_schema: Type[BaseModel] = CompanyBusinessObjectSchema,
    custom_fields: Optional[Dict[str, Any]] = None,
    custom_validators: Optional[Dict[str, Any]] = None
) -> Dict[str, Type[BaseModel]]:
    """
    Factory function to create Create, Update, and Response schemas for a model.
    
    Args:
        model_class: SQLAlchemy model class
        base_schema: Base schema class to inherit from
        custom_fields: Additional fields to add to schemas
        custom_validators: Custom validation rules to apply
        
    Returns:
        Dictionary with 'Create', 'Update', and 'Response' schema classes
    """
    model_name = model_class.__name__
    custom_fields = custom_fields or {}
    custom_validators = custom_validators or {}
    
    # Convert custom_fields to proper Field annotations
    field_annotations = {}
    for field_name, field_type in custom_fields.items():
        if isinstance(field_type, type):
            field_annotations[field_name] = field_type
        else:
            field_annotations[field_name] = field_type
    
    # Create Response schema (includes all fields)
    response_attrs = {
        '__module__': model_class.__module__,
        '__annotations__': field_annotations.copy()
    }
    ResponseSchema = type(
        f"{model_name}ResponseSchema",
        (ResponseSchemaBase,),
        response_attrs
    )
    
    # Create Create schema (excludes auto-managed fields)
    create_field_annotations = {
        k: v for k, v in field_annotations.items() 
        if k not in ['id', 'created_at', 'updated_at', 'framework_version']
    }
    create_attrs = {
        '__module__': model_class.__module__,
        '__annotations__': create_field_annotations
    }
    CreateSchema = type(
        f"{model_name}CreateSchema",
        (CreateSchemaBase,),
        create_attrs
    )
    
    # Create Update schema (makes fields optional)
    update_field_annotations = {
        k: Optional[v] for k, v in field_annotations.items() 
        if k not in ['id', 'created_at', 'updated_at', 'framework_version']
    }
    update_attrs = {
        '__module__': model_class.__module__,
        '__annotations__': update_field_annotations
    }
    UpdateSchema = type(
        f"{model_name}UpdateSchema", 
        (UpdateSchemaBase,),
        update_attrs
    )
    
    # Apply custom validators if provided
    for schema in [CreateSchema, UpdateSchema, ResponseSchema]:
        if custom_validators:
            ValidationFramework.apply_validators(schema, list(custom_validators.keys()))
    
    return {
        'Create': CreateSchema,
        'Update': UpdateSchema,
        'Response': ResponseSchema
    }


def create_company_schema_factory(
    model_class: Type,
    custom_fields: Optional[Dict[str, Any]] = None,
    custom_validators: Optional[Dict[str, Any]] = None
) -> Dict[str, Type[BaseModel]]:
    """
    Convenience factory for company-scoped business objects.
    
    Args:
        model_class: SQLAlchemy model class
        custom_fields: Additional fields to add to schemas
        custom_validators: Custom validation rules to apply
        
    Returns:
        Dictionary with 'Create', 'Update', and 'Response' schema classes
    """
    return create_schema_factory(
        model_class=model_class,
        base_schema=CompanyBusinessObjectSchema,
        custom_fields=custom_fields,
        custom_validators=custom_validators
    )