"""
Pydantic schemas for extension system API endpoints.

Provides request/response schemas for managing custom fields,
field definitions, and validation rules through the API.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum

from app.framework.schemas import CompanyBusinessObjectSchema, CreateSchemaBase, UpdateSchemaBase


class FieldType(str, Enum):
    """Supported custom field types."""
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    JSON = "json"


class ValidatorType(str, Enum):
    """Supported validation rule types."""
    REQUIRED = "required"
    EMAIL = "email"
    LENGTH = "length"
    RANGE = "range"
    PATTERN = "pattern"
    OPTIONS = "options"
    CUSTOM = "custom"


# Business Object Extension Schemas
class BusinessObjectExtensionBase(BaseModel):
    """Base schema for business object extensions."""
    entity_type: str = Field(..., description="Type of entity (e.g., 'partner', 'company')", max_length=100)
    entity_id: int = Field(..., description="ID of the entity instance", ge=1)
    field_name: str = Field(..., description="Name of the custom field", max_length=100)
    field_type: FieldType = Field(..., description="Data type of the field")
    field_value: Optional[str] = Field(None, description="String representation of the field value")
    
    @field_validator('field_name')
    @classmethod
    def validate_field_name(cls, v):
        """Validate field name format."""
        if not v or not v.strip():
            raise ValueError("Field name cannot be empty")
        
        # Field name should be a valid identifier
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v.strip()):
            raise ValueError("Field name must be a valid identifier (letters, numbers, underscore)")
        
        return v.strip().lower()
    
    @field_validator('entity_type')
    @classmethod
    def validate_entity_type(cls, v):
        """Validate entity type format."""
        if not v or not v.strip():
            raise ValueError("Entity type cannot be empty")
        return v.strip().lower()


class BusinessObjectExtensionCreate(BusinessObjectExtensionBase):
    """Schema for creating business object extensions."""
    company_id: int = Field(..., description="Company ID for multi-tenant isolation", ge=1)


class BusinessObjectExtensionUpdate(BaseModel):
    """Schema for updating business object extensions."""
    field_type: Optional[FieldType] = Field(None, description="Data type of the field")
    field_value: Optional[str] = Field(None, description="String representation of the field value")
    is_active: Optional[bool] = Field(None, description="Whether the field is active")


class BusinessObjectExtensionResponse(CompanyBusinessObjectSchema):
    """Schema for business object extension responses."""
    entity_type: str
    entity_id: int
    field_name: str
    field_type: FieldType
    field_value: Optional[str]
    typed_value: Optional[Any] = Field(None, description="Value converted to appropriate Python type")
    is_active: bool
    
    class Config:
        from_attributes = True


# Business Object Field Definition Schemas
class BusinessObjectFieldDefinitionBase(BaseModel):
    """Base schema for field definitions."""
    entity_type: str = Field(..., description="Type of entity", max_length=100)
    field_name: str = Field(..., description="Name of the field", max_length=100)
    field_type: FieldType = Field(..., description="Data type of the field")
    field_label: Optional[str] = Field(None, description="Human-readable label", max_length=200)
    field_description: Optional[str] = Field(None, description="Help text or description")
    is_required: bool = Field(False, description="Whether the field is required")
    default_value: Optional[str] = Field(None, description="Default value as string")
    field_options: Optional[Dict[str, Any]] = Field(None, description="Options for select fields, etc.")
    display_order: int = Field(0, description="Order for displaying fields", ge=0)
    
    @field_validator('field_name')
    @classmethod
    def validate_field_name(cls, v):
        """Validate field name format."""
        if not v or not v.strip():
            raise ValueError("Field name cannot be empty")
        
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v.strip()):
            raise ValueError("Field name must be a valid identifier")
        
        return v.strip().lower()
    
    @field_validator('entity_type')
    @classmethod
    def validate_entity_type(cls, v):
        """Validate entity type format."""
        if not v or not v.strip():
            raise ValueError("Entity type cannot be empty")
        return v.strip().lower()


class BusinessObjectFieldDefinitionCreate(BusinessObjectFieldDefinitionBase):
    """Schema for creating field definitions."""
    company_id: int = Field(..., description="Company ID for multi-tenant isolation", ge=1)


class BusinessObjectFieldDefinitionUpdate(BaseModel):
    """Schema for updating field definitions."""
    field_type: Optional[FieldType] = None
    field_label: Optional[str] = Field(None, max_length=200)
    field_description: Optional[str] = None
    is_required: Optional[bool] = None
    default_value: Optional[str] = None
    field_options: Optional[Dict[str, Any]] = None
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class BusinessObjectFieldDefinitionResponse(CompanyBusinessObjectSchema):
    """Schema for field definition responses."""
    entity_type: str
    field_name: str
    field_type: FieldType
    field_label: Optional[str]
    field_description: Optional[str]
    is_required: bool
    default_value: Optional[str]
    field_options: Optional[Dict[str, Any]]
    display_order: int
    is_active: bool
    typed_default_value: Optional[Any] = Field(None, description="Default value converted to appropriate type")
    
    class Config:
        from_attributes = True


# Business Object Validator Schemas
class BusinessObjectValidatorBase(BaseModel):
    """Base schema for business object validators."""
    entity_type: str = Field(..., description="Type of entity", max_length=100)
    field_name: str = Field(..., description="Name of the field to validate", max_length=100)
    validator_type: ValidatorType = Field(..., description="Type of validator")
    validator_config: Dict[str, Any] = Field(default_factory=dict, description="Configuration for the validator")
    validation_order: int = Field(0, description="Order in which to apply validators", ge=0)
    
    @field_validator('field_name')
    @classmethod
    def validate_field_name(cls, v):
        """Validate field name format."""
        if not v or not v.strip():
            raise ValueError("Field name cannot be empty")
        
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v.strip()):
            raise ValueError("Field name must be a valid identifier")
        
        return v.strip().lower()
    
    @field_validator('entity_type')
    @classmethod
    def validate_entity_type(cls, v):
        """Validate entity type format."""
        if not v or not v.strip():
            raise ValueError("Entity type cannot be empty")
        return v.strip().lower()
    
    @field_validator('validator_config')
    @classmethod
    def validate_validator_config(cls, v, info):
        """Validate validator configuration based on validator type."""
        validator_type = info.data.get('validator_type')
        
        if validator_type == ValidatorType.REQUIRED:
            # Required validator can have a custom message
            allowed_keys = {'message'}
        elif validator_type == ValidatorType.EMAIL:
            # Email validator can have a custom message
            allowed_keys = {'message'}
        elif validator_type == ValidatorType.LENGTH:
            # Length validator needs min/max values
            allowed_keys = {'min', 'max', 'message'}
            if 'min' not in v and 'max' not in v:
                raise ValueError("Length validator must specify 'min' or 'max'")
        elif validator_type == ValidatorType.RANGE:
            # Range validator needs min/max values
            allowed_keys = {'min', 'max', 'message'}
            if 'min' not in v and 'max' not in v:
                raise ValueError("Range validator must specify 'min' or 'max'")
        elif validator_type == ValidatorType.PATTERN:
            # Pattern validator needs a regex pattern
            allowed_keys = {'pattern', 'message'}
            if 'pattern' not in v:
                raise ValueError("Pattern validator must specify 'pattern'")
        elif validator_type == ValidatorType.OPTIONS:
            # Options validator needs a list of allowed values
            allowed_keys = {'options', 'message'}
            if 'options' not in v:
                raise ValueError("Options validator must specify 'options'")
        elif validator_type == ValidatorType.CUSTOM:
            # Custom validator can have any configuration
            allowed_keys = set(v.keys())
        else:
            allowed_keys = {'message'}
        
        # Check for unexpected keys
        unexpected_keys = set(v.keys()) - allowed_keys
        if unexpected_keys:
            raise ValueError(f"Unexpected configuration keys for {validator_type}: {unexpected_keys}")
        
        return v


class BusinessObjectValidatorCreate(BusinessObjectValidatorBase):
    """Schema for creating business object validators."""
    company_id: int = Field(..., description="Company ID for multi-tenant isolation", ge=1)


class BusinessObjectValidatorUpdate(BaseModel):
    """Schema for updating business object validators."""
    validator_type: Optional[ValidatorType] = None
    validator_config: Optional[Dict[str, Any]] = None
    validation_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class BusinessObjectValidatorResponse(CompanyBusinessObjectSchema):
    """Schema for business object validator responses."""
    entity_type: str
    field_name: str
    validator_type: ValidatorType
    validator_config: Dict[str, Any]
    validation_order: int
    is_active: bool
    
    class Config:
        from_attributes = True


# Bulk operation schemas
class BulkExtensionCreate(BaseModel):
    """Schema for creating multiple extensions at once."""
    extensions: List[BusinessObjectExtensionCreate] = Field(..., description="List of extensions to create")
    
    @field_validator('extensions')
    @classmethod
    def validate_extensions_not_empty(cls, v):
        if not v:
            raise ValueError("Extensions list cannot be empty")
        return v


class BulkExtensionResponse(BaseModel):
    """Schema for bulk extension creation response."""
    created: List[BusinessObjectExtensionResponse] = Field(..., description="Successfully created extensions")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Errors encountered during creation")


# Extension value schemas with type conversion
class ExtensionValueRequest(BaseModel):
    """Schema for setting extension values with proper type handling."""
    field_name: str = Field(..., description="Name of the field")
    field_type: FieldType = Field(..., description="Type of the field")
    value: Union[str, int, float, bool, datetime, Dict[str, Any], List[Any]] = Field(..., description="Value to set")
    
    @field_validator('field_name')
    @classmethod
    def validate_field_name(cls, v):
        """Validate field name format."""
        if not v or not v.strip():
            raise ValueError("Field name cannot be empty")
        
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v.strip()):
            raise ValueError("Field name must be a valid identifier")
        
        return v.strip().lower()


class ExtensionValueResponse(BaseModel):
    """Schema for extension value responses."""
    field_name: str
    field_type: FieldType
    raw_value: str = Field(..., description="Raw string value as stored")
    typed_value: Union[str, int, float, bool, datetime, Dict[str, Any], List[Any]] = Field(..., description="Value converted to proper type")
    is_valid: bool = Field(..., description="Whether the value passed validation")
    validation_errors: List[str] = Field(default_factory=list, description="Validation error messages")


# Query and filtering schemas
class ExtensionFilterRequest(BaseModel):
    """Schema for filtering objects by extension field values."""
    field_filters: Dict[str, Union[str, int, float, bool, List[Union[str, int, float, bool]]]] = Field(
        default_factory=dict, 
        description="Dictionary of field_name -> value filters"
    )
    sort_field: Optional[str] = Field(None, description="Extension field to sort by")
    sort_direction: Optional[str] = Field("asc", description="Sort direction: 'asc' or 'desc'")
    
    @field_validator('sort_direction')
    @classmethod
    def validate_sort_direction(cls, v):
        if v and v.lower() not in ['asc', 'desc']:
            raise ValueError("Sort direction must be 'asc' or 'desc'")
        return v.lower() if v else 'asc'


# Validation schemas
class ValidationRequest(BaseModel):
    """Schema for validating extension field values."""
    entity_type: str = Field(..., description="Type of entity")
    field_name: str = Field(..., description="Name of the field")
    field_type: FieldType = Field(..., description="Type of the field")
    field_value: Union[str, int, float, bool, datetime, Dict[str, Any], List[Any]] = Field(..., description="Value to validate")
    company_id: int = Field(..., description="Company ID for validator lookup", ge=1)


class ValidationResponse(BaseModel):
    """Schema for validation responses."""
    is_valid: bool = Field(..., description="Whether the value is valid")
    errors: List[str] = Field(default_factory=list, description="List of validation error messages")
    field_name: str = Field(..., description="Name of the validated field")
    field_type: FieldType = Field(..., description="Type of the validated field")


# Summary and statistics schemas
class ExtensionSummaryResponse(BaseModel):
    """Schema for extension usage summary."""
    entity_type: str
    total_entities: int = Field(..., description="Total number of entities of this type")
    entities_with_extensions: int = Field(..., description="Number of entities with custom fields")
    total_extensions: int = Field(..., description="Total number of extension field instances")
    unique_fields: int = Field(..., description="Number of unique custom field names")
    field_usage: Dict[str, int] = Field(default_factory=dict, description="Usage count per field name")


class FieldDefinitionSummaryResponse(BaseModel):
    """Schema for field definition summary."""
    entity_type: str
    total_definitions: int = Field(..., description="Total number of field definitions")
    active_definitions: int = Field(..., description="Number of active field definitions")
    required_fields: int = Field(..., description="Number of required fields")
    field_types: Dict[str, int] = Field(default_factory=dict, description="Count by field type")


class ValidatorSummaryResponse(BaseModel):
    """Schema for validator summary."""
    entity_type: str
    total_validators: int = Field(..., description="Total number of validators")
    active_validators: int = Field(..., description="Number of active validators")
    validator_types: Dict[str, int] = Field(default_factory=dict, description="Count by validator type")
    fields_with_validation: int = Field(..., description="Number of fields with validation rules")