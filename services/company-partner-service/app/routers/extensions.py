"""
API router for extension system endpoints.

Provides REST API endpoints for managing custom fields, field definitions,
and validation rules for business objects.
"""

from typing import List, Optional, Dict, Any
from http import HTTPStatus
from fastapi import APIRouter, Depends, Query, Path, Body
from fastapi.responses import JSONResponse
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middleware.auth import get_current_user, require_company_access
from app.models.extensions import (
    BusinessObjectExtension,
    BusinessObjectValidator,
    BusinessObjectFieldDefinition
)
from app.schemas.extensions import (
    BusinessObjectExtensionCreate,
    BusinessObjectExtensionUpdate,
    BusinessObjectExtensionResponse,
    BusinessObjectFieldDefinitionCreate,
    BusinessObjectFieldDefinitionUpdate,
    BusinessObjectFieldDefinitionResponse,
    BusinessObjectValidatorCreate,
    BusinessObjectValidatorUpdate,
    BusinessObjectValidatorResponse,
    BulkExtensionCreate,
    BulkExtensionResponse,
    ExtensionValueRequest,
    ExtensionValueResponse,
    ExtensionFilterRequest,
    ValidationRequest,
    ValidationResponse,
    ExtensionSummaryResponse,
    FieldDefinitionSummaryResponse,
    ValidatorSummaryResponse
)
from app.framework.extensions import ExtensionValidator
from app.services.messaging_service import CompanyPartnerMessagingService

router = APIRouter(prefix="/extensions", tags=["extensions"])


# Business Object Extension Endpoints
@router.post("/", response_model=BusinessObjectExtensionResponse, status_code=201)
async def create_extension(
    extension_data: BusinessObjectExtensionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new custom field extension for a business object."""
    # Verify company access
    await require_company_access(current_user, extension_data.company_id)
    
    # Check if extension already exists
    existing_query = select(BusinessObjectExtension).where(
        and_(
            BusinessObjectExtension.entity_type == extension_data.entity_type,
            BusinessObjectExtension.entity_id == extension_data.entity_id,
            BusinessObjectExtension.field_name == extension_data.field_name,
            BusinessObjectExtension.company_id == extension_data.company_id
        )
    )
    
    result = await db.execute(existing_query)
    existing_extension = result.scalar_one_or_none()
    
    if existing_extension:
        return JSONResponse(
            status_code=HTTPStatus.CONFLICT,
            content={"detail": f"Extension field '{extension_data.field_name}' already exists for this entity"}
        )
    
    # Create new extension
    extension = BusinessObjectExtension(
        entity_type=extension_data.entity_type,
        entity_id=extension_data.entity_id,
        field_name=extension_data.field_name,
        field_type=extension_data.field_type.value,
        field_value=extension_data.field_value,
        company_id=extension_data.company_id,
        is_active=True,
        framework_version='1.0.0'
    )
    
    db.add(extension)
    await db.commit()
    await db.refresh(extension)
    
    # Prepare response
    response_data = BusinessObjectExtensionResponse.from_orm(extension)
    response_data.typed_value = extension.get_typed_value()
    
    return response_data


@router.get("/{extension_id}", response_model=BusinessObjectExtensionResponse)
async def get_extension(
    extension_id: int = Path(..., description="Extension ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific extension by ID."""
    query = select(BusinessObjectExtension).where(BusinessObjectExtension.id == extension_id)
    result = await db.execute(query)
    extension = result.scalar_one_or_none()
    
    if not extension:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"detail": "Extension not found"}
        )
    
    # Verify company access
    await require_company_access(current_user, extension.company_id)
    
    # Prepare response
    response_data = BusinessObjectExtensionResponse.from_orm(extension)
    response_data.typed_value = extension.get_typed_value()
    
    return response_data


@router.get("/", response_model=List[BusinessObjectExtensionResponse])
async def list_extensions(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    field_name: Optional[str] = Query(None, description="Filter by field name"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List extensions with optional filtering."""
    query = select(BusinessObjectExtension)
    
    # Build filters
    conditions = []
    
    if entity_type:
        conditions.append(BusinessObjectExtension.entity_type == entity_type.lower())
    
    if entity_id:
        conditions.append(BusinessObjectExtension.entity_id == entity_id)
    
    if field_name:
        conditions.append(BusinessObjectExtension.field_name == field_name.lower())
    
    if company_id:
        await require_company_access(current_user, company_id)
        conditions.append(BusinessObjectExtension.company_id == company_id)
    else:
        # Filter to user's accessible companies
        user_companies = current_user.get('company_ids', [])
        if user_companies:
            conditions.append(BusinessObjectExtension.company_id.in_(user_companies))
    
    if is_active is not None:
        conditions.append(BusinessObjectExtension.is_active == is_active)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(BusinessObjectExtension.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    extensions = result.scalars().all()
    
    # Prepare response
    response_data = []
    for extension in extensions:
        ext_response = BusinessObjectExtensionResponse.from_orm(extension)
        ext_response.typed_value = extension.get_typed_value()
        response_data.append(ext_response)
    
    return response_data


@router.put("/{extension_id}", response_model=BusinessObjectExtensionResponse)
async def update_extension(
    extension_id: int = Path(..., description="Extension ID"),
    update_data: BusinessObjectExtensionUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing extension."""
    query = select(BusinessObjectExtension).where(BusinessObjectExtension.id == extension_id)
    result = await db.execute(query)
    extension = result.scalar_one_or_none()
    
    if not extension:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"detail": "Extension not found"}
        )
    
    # Verify company access
    await require_company_access(current_user, extension.company_id)
    
    # Update fields
    if update_data.field_type is not None:
        extension.field_type = update_data.field_type.value
    
    if update_data.field_value is not None:
        extension.field_value = update_data.field_value
    
    if update_data.is_active is not None:
        extension.is_active = update_data.is_active
    
    extension.updated_at = func.now()
    
    await db.commit()
    await db.refresh(extension)
    
    # Prepare response
    response_data = BusinessObjectExtensionResponse.from_orm(extension)
    response_data.typed_value = extension.get_typed_value()
    
    return response_data


@router.delete("/{extension_id}", status_code=204)
async def delete_extension(
    extension_id: int = Path(..., description="Extension ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete an extension (soft delete)."""
    query = select(BusinessObjectExtension).where(BusinessObjectExtension.id == extension_id)
    result = await db.execute(query)
    extension = result.scalar_one_or_none()
    
    if not extension:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"detail": "Extension not found"}
        )
    
    # Verify company access
    await require_company_access(current_user, extension.company_id)
    
    # Soft delete
    extension.is_active = False
    extension.updated_at = func.now()
    
    await db.commit()
    
    return None


# Field Definition Endpoints
@router.post("/field-definitions", response_model=BusinessObjectFieldDefinitionResponse, status_code=201)
async def create_field_definition(
    definition_data: BusinessObjectFieldDefinitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new field definition."""
    # Verify company access
    await require_company_access(current_user, definition_data.company_id)
    
    # Check if definition already exists
    existing_query = select(BusinessObjectFieldDefinition).where(
        and_(
            BusinessObjectFieldDefinition.entity_type == definition_data.entity_type,
            BusinessObjectFieldDefinition.field_name == definition_data.field_name,
            BusinessObjectFieldDefinition.company_id == definition_data.company_id
        )
    )
    
    result = await db.execute(existing_query)
    existing_definition = result.scalar_one_or_none()
    
    if existing_definition:
        return JSONResponse(
            status_code=HTTPStatus.CONFLICT,
            content={"detail": f"Field definition '{definition_data.field_name}' already exists for {definition_data.entity_type}"}
        )
    
    # Create field definition
    field_definition = BusinessObjectFieldDefinition(
        entity_type=definition_data.entity_type,
        field_name=definition_data.field_name,
        field_type=definition_data.field_type.value,
        field_label=definition_data.field_label,
        field_description=definition_data.field_description,
        is_required=definition_data.is_required,
        default_value=definition_data.default_value,
        display_order=definition_data.display_order,
        company_id=definition_data.company_id,
        is_active=True,
        framework_version='1.0.0'
    )
    
    if definition_data.field_options:
        field_definition.set_options(definition_data.field_options)
    
    db.add(field_definition)
    await db.commit()
    await db.refresh(field_definition)
    
    # Prepare response
    response_data = BusinessObjectFieldDefinitionResponse.from_orm(field_definition)
    response_data.field_options = field_definition.get_options()
    response_data.typed_default_value = field_definition.get_default_typed_value()
    
    return response_data


@router.get("/field-definitions", response_model=List[BusinessObjectFieldDefinitionResponse])
async def list_field_definitions(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List field definitions with optional filtering."""
    query = select(BusinessObjectFieldDefinition)
    
    # Build filters
    conditions = []
    
    if entity_type:
        conditions.append(BusinessObjectFieldDefinition.entity_type == entity_type.lower())
    
    if company_id:
        await require_company_access(current_user, company_id)
        conditions.append(BusinessObjectFieldDefinition.company_id == company_id)
    else:
        # Filter to user's accessible companies
        user_companies = current_user.get('company_ids', [])
        if user_companies:
            conditions.append(BusinessObjectFieldDefinition.company_id.in_(user_companies))
    
    if is_active is not None:
        conditions.append(BusinessObjectFieldDefinition.is_active == is_active)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Apply pagination and ordering
    query = query.offset(skip).limit(limit).order_by(
        BusinessObjectFieldDefinition.entity_type,
        BusinessObjectFieldDefinition.display_order,
        BusinessObjectFieldDefinition.field_name
    )
    
    # Execute query
    result = await db.execute(query)
    definitions = result.scalars().all()
    
    # Prepare response
    response_data = []
    for definition in definitions:
        def_response = BusinessObjectFieldDefinitionResponse.from_orm(definition)
        def_response.field_options = definition.get_options()
        def_response.typed_default_value = definition.get_default_typed_value()
        response_data.append(def_response)
    
    return response_data


# Validator Endpoints
@router.post("/validators", response_model=BusinessObjectValidatorResponse, status_code=201)
async def create_validator(
    validator_data: BusinessObjectValidatorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new field validator."""
    # Verify company access
    await require_company_access(current_user, validator_data.company_id)
    
    # Create validator
    validator = BusinessObjectValidator(
        entity_type=validator_data.entity_type,
        field_name=validator_data.field_name,
        validator_type=validator_data.validator_type.value,
        validation_order=validator_data.validation_order,
        company_id=validator_data.company_id,
        is_active=True,
        framework_version='1.0.0'
    )
    
    validator.set_config(validator_data.validator_config)
    
    db.add(validator)
    await db.commit()
    await db.refresh(validator)
    
    # Prepare response
    response_data = BusinessObjectValidatorResponse.from_orm(validator)
    response_data.validator_config = validator.get_config()
    
    return response_data


@router.get("/validators", response_model=List[BusinessObjectValidatorResponse])
async def list_validators(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    field_name: Optional[str] = Query(None, description="Filter by field name"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List validators with optional filtering."""
    query = select(BusinessObjectValidator)
    
    # Build filters
    conditions = []
    
    if entity_type:
        conditions.append(BusinessObjectValidator.entity_type == entity_type.lower())
    
    if field_name:
        conditions.append(BusinessObjectValidator.field_name == field_name.lower())
    
    if company_id:
        await require_company_access(current_user, company_id)
        conditions.append(BusinessObjectValidator.company_id == company_id)
    else:
        # Filter to user's accessible companies
        user_companies = current_user.get('company_ids', [])
        if user_companies:
            conditions.append(BusinessObjectValidator.company_id.in_(user_companies))
    
    if is_active is not None:
        conditions.append(BusinessObjectValidator.is_active == is_active)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Apply pagination and ordering
    query = query.offset(skip).limit(limit).order_by(
        BusinessObjectValidator.entity_type,
        BusinessObjectValidator.field_name,
        BusinessObjectValidator.validation_order
    )
    
    # Execute query
    result = await db.execute(query)
    validators = result.scalars().all()
    
    # Prepare response
    response_data = []
    for validator in validators:
        val_response = BusinessObjectValidatorResponse.from_orm(validator)
        val_response.validator_config = validator.get_config()
        response_data.append(val_response)
    
    return response_data


# Bulk Operations
@router.post("/bulk", response_model=BulkExtensionResponse, status_code=201)
async def bulk_create_extensions(
    bulk_data: BulkExtensionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create multiple extensions in a single operation."""
    created_extensions = []
    errors = []
    
    for i, extension_data in enumerate(bulk_data.extensions):
        try:
            # Verify company access
            await require_company_access(current_user, extension_data.company_id)
            
            # Check if extension already exists
            existing_query = select(BusinessObjectExtension).where(
                and_(
                    BusinessObjectExtension.entity_type == extension_data.entity_type,
                    BusinessObjectExtension.entity_id == extension_data.entity_id,
                    BusinessObjectExtension.field_name == extension_data.field_name,
                    BusinessObjectExtension.company_id == extension_data.company_id
                )
            )
            
            result = await db.execute(existing_query)
            existing_extension = result.scalar_one_or_none()
            
            if existing_extension:
                errors.append({
                    "index": i,
                    "field_name": extension_data.field_name,
                    "error": "Extension already exists"
                })
                continue
            
            # Create new extension
            extension = BusinessObjectExtension(
                entity_type=extension_data.entity_type,
                entity_id=extension_data.entity_id,
                field_name=extension_data.field_name,
                field_type=extension_data.field_type.value,
                field_value=extension_data.field_value,
                company_id=extension_data.company_id,
                is_active=True,
                framework_version='1.0.0'
            )
            
            db.add(extension)
            await db.commit()
            await db.refresh(extension)
            
            # Prepare response
            response_data = BusinessObjectExtensionResponse.from_orm(extension)
            response_data.typed_value = extension.get_typed_value()
            created_extensions.append(response_data)
            
        except Exception as e:
            errors.append({
                "index": i,
                "field_name": extension_data.field_name,
                "error": str(e)
            })
    
    return BulkExtensionResponse(created=created_extensions, errors=errors)


# Validation Endpoint
@router.post("/validate", response_model=ValidationResponse)
async def validate_field_value(
    validation_request: ValidationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Validate a field value against all applicable validation rules."""
    # Verify company access
    await require_company_access(current_user, validation_request.company_id)
    
    # Get validators for this field
    validators_query = select(BusinessObjectValidator).where(
        and_(
            BusinessObjectValidator.entity_type == validation_request.entity_type,
            BusinessObjectValidator.field_name == validation_request.field_name,
            BusinessObjectValidator.company_id == validation_request.company_id,
            BusinessObjectValidator.is_active == True
        )
    )
    
    result = await db.execute(validators_query)
    validators = result.scalars().all()
    
    # Validate the field value
    is_valid, errors = ExtensionValidator.validate_field_value(
        validation_request.field_value,
        validation_request.field_type.value,
        validators
    )
    
    return ValidationResponse(
        is_valid=is_valid,
        errors=errors,
        field_name=validation_request.field_name,
        field_type=validation_request.field_type
    )


# Summary and Statistics Endpoints
@router.get("/summary/{entity_type}", response_model=ExtensionSummaryResponse)
async def get_extension_summary(
    entity_type: str = Path(..., description="Entity type to summarize"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get usage summary for extensions of a specific entity type."""
    if company_id:
        await require_company_access(current_user, company_id)
        company_filter = BusinessObjectExtension.company_id == company_id
    else:
        # Filter to user's accessible companies
        user_companies = current_user.get('company_ids', [])
        company_filter = BusinessObjectExtension.company_id.in_(user_companies) if user_companies else True
    
    # Get total extensions count
    total_query = select(func.count(BusinessObjectExtension.id)).where(
        and_(
            BusinessObjectExtension.entity_type == entity_type.lower(),
            BusinessObjectExtension.is_active == True,
            company_filter
        )
    )
    total_result = await db.execute(total_query)
    total_extensions = total_result.scalar()
    
    # Get unique entities count
    entities_query = select(func.count(func.distinct(BusinessObjectExtension.entity_id))).where(
        and_(
            BusinessObjectExtension.entity_type == entity_type.lower(),
            BusinessObjectExtension.is_active == True,
            company_filter
        )
    )
    entities_result = await db.execute(entities_query)
    entities_with_extensions = entities_result.scalar()
    
    # Get unique fields count
    fields_query = select(func.count(func.distinct(BusinessObjectExtension.field_name))).where(
        and_(
            BusinessObjectExtension.entity_type == entity_type.lower(),
            BusinessObjectExtension.is_active == True,
            company_filter
        )
    )
    fields_result = await db.execute(fields_query)
    unique_fields = fields_result.scalar()
    
    # Get field usage statistics
    usage_query = select(
        BusinessObjectExtension.field_name,
        func.count(BusinessObjectExtension.id)
    ).where(
        and_(
            BusinessObjectExtension.entity_type == entity_type.lower(),
            BusinessObjectExtension.is_active == True,
            company_filter
        )
    ).group_by(BusinessObjectExtension.field_name)
    
    usage_result = await db.execute(usage_query)
    field_usage = {field_name: count for field_name, count in usage_result.all()}
    
    return ExtensionSummaryResponse(
        entity_type=entity_type.lower(),
        total_entities=0,  # Would need to query the actual entity table
        entities_with_extensions=entities_with_extensions or 0,
        total_extensions=total_extensions or 0,
        unique_fields=unique_fields or 0,
        field_usage=field_usage
    )