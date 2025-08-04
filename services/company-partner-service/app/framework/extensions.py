"""
Extension system for Business Object Framework.

Provides ExtensibleMixin and supporting classes for adding dynamic custom fields,
validation rules, and querying capabilities to business objects.
"""

import json
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from app.models.extensions import (
    BusinessObjectExtension, 
    BusinessObjectValidator, 
    BusinessObjectFieldDefinition
)


class ExtensibleMixin:
    """
    Mixin that adds custom field support to business objects.
    
    This mixin provides methods to get, set, and manage custom fields
    on business objects dynamically. It integrates with the extension
    system database tables to store and retrieve custom field values.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._extensions_cache = {}
        self._extensions_loaded = False
    
    async def load_extensions(self, db: AsyncSession):
        """
        Load all custom field extensions for this object from the database.
        
        Args:
            db: Database session
        """
        if not hasattr(self, 'id') or not self.id:
            return
        
        entity_type = self.__class__.__name__.lower()
        company_id = getattr(self, 'company_id', None)
        
        # Build query
        query = select(BusinessObjectExtension).where(
            and_(
                BusinessObjectExtension.entity_type == entity_type,
                BusinessObjectExtension.entity_id == self.id,
                BusinessObjectExtension.is_active == True
            )
        )
        
        # Add company filter if this is a company-scoped object
        if company_id is not None:
            query = query.where(BusinessObjectExtension.company_id == company_id)
        
        # Execute query
        result = await db.execute(query)
        extensions = result.scalars().all()
        
        # Cache the extensions
        self._extensions_cache = {}
        for ext in extensions:
            self._extensions_cache[ext.field_name] = ext
        
        self._extensions_loaded = True
    
    async def get_extension(self, field_name: str, db: AsyncSession = None) -> Any:
        """
        Get the value of a custom field.
        
        Args:
            field_name: Name of the custom field
            db: Database session (required if extensions not loaded)
            
        Returns:
            The typed value of the custom field, or None if not found
        """
        # Load extensions if not already loaded
        if not self._extensions_loaded and db:
            await self.load_extensions(db)
        
        # Get from cache
        if field_name in self._extensions_cache:
            return self._extensions_cache[field_name].get_typed_value()
        
        return None
    
    async def set_extension(
        self, 
        field_name: str, 
        field_value: Any, 
        field_type: str, 
        db: AsyncSession
    ) -> BusinessObjectExtension:
        """
        Set the value of a custom field.
        
        Args:
            field_name: Name of the custom field
            field_value: Value to set
            field_type: Type of the field ('string', 'integer', 'decimal', etc.)
            db: Database session
            
        Returns:
            The BusinessObjectExtension object that was created or updated
        """
        if not hasattr(self, 'id') or not self.id:
            raise ValueError("Cannot set extension on object without ID")
        
        entity_type = self.__class__.__name__.lower()
        company_id = getattr(self, 'company_id', None)
        
        if company_id is None:
            raise ValueError("Cannot set extension on object without company_id")
        
        # Check if extension already exists
        query = select(BusinessObjectExtension).where(
            and_(
                BusinessObjectExtension.entity_type == entity_type,
                BusinessObjectExtension.entity_id == self.id,
                BusinessObjectExtension.field_name == field_name,
                BusinessObjectExtension.company_id == company_id
            )
        )
        
        result = await db.execute(query)
        extension = result.scalar_one_or_none()
        
        if extension:
            # Update existing extension
            extension.field_type = field_type
            extension.set_typed_value(field_value)
            extension.updated_at = datetime.utcnow()
            extension.is_active = True
        else:
            # Create new extension
            extension = BusinessObjectExtension(
                entity_type=entity_type,
                entity_id=self.id,
                field_name=field_name,
                field_type=field_type,
                company_id=company_id,
                is_active=True,
                framework_version='1.0.0'
            )
            extension.set_typed_value(field_value)
            db.add(extension)
        
        await db.commit()
        await db.refresh(extension)
        
        # Update cache
        self._extensions_cache[field_name] = extension
        
        return extension
    
    async def remove_extension(self, field_name: str, db: AsyncSession) -> bool:
        """
        Remove a custom field (soft delete).
        
        Args:
            field_name: Name of the custom field to remove
            db: Database session
            
        Returns:
            True if the field was removed, False if not found
        """
        if not hasattr(self, 'id') or not self.id:
            return False
        
        entity_type = self.__class__.__name__.lower()
        company_id = getattr(self, 'company_id', None)
        
        if company_id is None:
            return False
        
        # Find the extension
        query = select(BusinessObjectExtension).where(
            and_(
                BusinessObjectExtension.entity_type == entity_type,
                BusinessObjectExtension.entity_id == self.id,
                BusinessObjectExtension.field_name == field_name,
                BusinessObjectExtension.company_id == company_id
            )
        )
        
        result = await db.execute(query)
        extension = result.scalar_one_or_none()
        
        if extension:
            # Soft delete
            extension.is_active = False
            extension.updated_at = datetime.utcnow()
            await db.commit()
            
            # Remove from cache
            if field_name in self._extensions_cache:
                del self._extensions_cache[field_name]
            
            return True
        
        return False
    
    async def get_all_extensions(self, db: AsyncSession = None) -> Dict[str, Any]:
        """
        Get all custom fields for this object.
        
        Args:
            db: Database session (required if extensions not loaded)
            
        Returns:
            Dictionary mapping field names to their typed values
        """
        # Load extensions if not already loaded
        if not self._extensions_loaded and db:
            await self.load_extensions(db)
        
        # Convert to dictionary
        result = {}
        for field_name, extension in self._extensions_cache.items():
            result[field_name] = extension.get_typed_value()
        
        return result
    
    async def has_extension(self, field_name: str, db: AsyncSession = None) -> bool:
        """
        Check if a custom field exists for this object.
        
        Args:
            field_name: Name of the custom field
            db: Database session (required if extensions not loaded)
            
        Returns:
            True if the field exists, False otherwise
        """
        # Load extensions if not already loaded
        if not self._extensions_loaded and db:
            await self.load_extensions(db)
        
        return field_name in self._extensions_cache
    
    def get_extension_metadata(self, field_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a custom field (type, creation date, etc.).
        
        Args:
            field_name: Name of the custom field
            
        Returns:
            Dictionary with field metadata, or None if not found
        """
        if field_name not in self._extensions_cache:
            return None
        
        extension = self._extensions_cache[field_name]
        return {
            'field_name': extension.field_name,
            'field_type': extension.field_type,
            'field_value': extension.field_value,
            'typed_value': extension.get_typed_value(),
            'created_at': extension.created_at,
            'updated_at': extension.updated_at,
            'is_active': extension.is_active
        }


class ExtensionValidator:
    """
    Validator for custom field values.
    
    Provides validation logic for different field types and validation rules
    that can be applied to custom fields.
    """
    
    @staticmethod
    def validate_field_value(
        field_value: Any, 
        field_type: str, 
        validators: List[BusinessObjectValidator]
    ) -> tuple[bool, List[str]]:
        """
        Validate a field value against a list of validation rules.
        
        Args:
            field_value: The value to validate
            field_type: The type of the field
            validators: List of validator rules to apply
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        # Sort validators by validation_order
        sorted_validators = sorted(validators, key=lambda v: v.validation_order)
        
        for validator in sorted_validators:
            if not validator.is_active:
                continue
            
            config = validator.get_config()
            is_valid, error_msg = ExtensionValidator._apply_validator(
                field_value, field_type, validator.validator_type, config
            )
            
            if not is_valid:
                errors.append(error_msg)
                # Stop on first error if configured to do so
                if config.get('stop_on_error', False):
                    break
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _apply_validator(
        field_value: Any, 
        field_type: str, 
        validator_type: str, 
        config: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Apply a single validation rule.
        
        Args:
            field_value: The value to validate
            field_type: The type of the field
            validator_type: The type of validator to apply
            config: Configuration for the validator
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if validator_type == 'required':
                return ExtensionValidator._validate_required(field_value, config)
            elif validator_type == 'email':
                return ExtensionValidator._validate_email(field_value, config)
            elif validator_type == 'length':
                return ExtensionValidator._validate_length(field_value, config)
            elif validator_type == 'range':
                return ExtensionValidator._validate_range(field_value, field_type, config)
            elif validator_type == 'pattern':
                return ExtensionValidator._validate_pattern(field_value, config)
            elif validator_type == 'options':
                return ExtensionValidator._validate_options(field_value, config)
            elif validator_type == 'custom':
                return ExtensionValidator._validate_custom(field_value, field_type, config)
            else:
                return True, None
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def _validate_required(field_value: Any, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate that a field has a value."""
        if field_value is None or (isinstance(field_value, str) and not field_value.strip()):
            return False, config.get('message', 'This field is required')
        return True, None
    
    @staticmethod
    def _validate_email(field_value: Any, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate email format."""
        if not field_value:
            return True, None  # Optional field
        
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, str(field_value)):
            return False, config.get('message', 'Invalid email format')
        return True, None
    
    @staticmethod
    def _validate_length(field_value: Any, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate string length."""
        if not field_value:
            return True, None
        
        value_str = str(field_value)
        min_length = config.get('min', 0)
        max_length = config.get('max', float('inf'))
        
        if len(value_str) < min_length:
            return False, config.get('message', f'Minimum length is {min_length}')
        if len(value_str) > max_length:
            return False, config.get('message', f'Maximum length is {max_length}')
        
        return True, None
    
    @staticmethod
    def _validate_range(field_value: Any, field_type: str, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate numeric range."""
        if not field_value:
            return True, None
        
        try:
            if field_type == 'integer':
                num_value = int(field_value)
            elif field_type == 'decimal':
                num_value = float(field_value)
            else:
                num_value = float(field_value)
            
            min_val = config.get('min', float('-inf'))
            max_val = config.get('max', float('inf'))
            
            if num_value < min_val:
                return False, config.get('message', f'Minimum value is {min_val}')
            if num_value > max_val:
                return False, config.get('message', f'Maximum value is {max_val}')
            
            return True, None
        except (ValueError, TypeError):
            return False, config.get('message', 'Invalid numeric value')
    
    @staticmethod
    def _validate_pattern(field_value: Any, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate against a regex pattern."""
        if not field_value:
            return True, None
        
        import re
        pattern = config.get('pattern')
        if not pattern:
            return True, None
        
        if not re.match(pattern, str(field_value)):
            return False, config.get('message', 'Invalid format')
        
        return True, None
    
    @staticmethod
    def _validate_options(field_value: Any, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate that value is in allowed options."""
        if not field_value:
            return True, None
        
        allowed_options = config.get('options', [])
        if not allowed_options:
            return True, None
        
        if str(field_value) not in [str(opt) for opt in allowed_options]:
            return False, config.get('message', f'Value must be one of: {", ".join(map(str, allowed_options))}')
        
        return True, None
    
    @staticmethod
    def _validate_custom(field_value: Any, field_type: str, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Apply custom validation logic."""
        # This would be implemented to call custom validation functions
        # For now, just return True
        return True, None


class ExtensionQueryBuilder:
    """
    Query builder for filtering objects based on extension field values.
    
    Provides utilities for building SQLAlchemy queries that filter
    business objects based on their custom field values.
    """
    
    @staticmethod
    def build_extension_filter(
        base_query,
        entity_type: str,
        field_filters: Dict[str, Any],
        company_id: Optional[int] = None
    ):
        """
        Add extension field filters to a query.
        
        Args:
            base_query: Base SQLAlchemy query
            entity_type: Type of entity being queried
            field_filters: Dictionary of field_name -> value filters
            company_id: Company ID for multi-tenant filtering
            
        Returns:
            Modified query with extension filters applied
        """
        if not field_filters:
            return base_query
        
        # For each extension filter, join with the extensions table
        for field_name, field_value in field_filters.items():
            # Create an alias for this join
            ext_alias = BusinessObjectExtension.__table__.alias(f'ext_{field_name}')
            
            # Build join conditions
            join_conditions = [
                ext_alias.c.entity_type == entity_type,
                ext_alias.c.field_name == field_name,
                ext_alias.c.is_active == True
            ]
            
            # Add company filter if provided
            if company_id is not None:
                join_conditions.append(ext_alias.c.company_id == company_id)
            
            # Add value filter
            if isinstance(field_value, (list, tuple)):
                # Multiple values (IN clause)
                join_conditions.append(ext_alias.c.field_value.in_([str(v) for v in field_value]))
            else:
                # Single value
                join_conditions.append(ext_alias.c.field_value == str(field_value))
            
            # Join to the base query
            # Note: This assumes the base model has an 'id' column
            base_query = base_query.join(
                ext_alias,
                and_(
                    ext_alias.c.entity_id == base_query.column_descriptions[0]['entity'].id,
                    *join_conditions
                )
            )
        
        return base_query
    
    @staticmethod
    def build_extension_sort(
        base_query,
        entity_type: str,
        sort_field: str,
        sort_direction: str = 'asc',
        company_id: Optional[int] = None
    ):
        """
        Add extension field sorting to a query.
        
        Args:
            base_query: Base SQLAlchemy query
            entity_type: Type of entity being queried
            sort_field: Name of the extension field to sort by
            sort_direction: 'asc' or 'desc'
            company_id: Company ID for multi-tenant filtering
            
        Returns:
            Modified query with extension sorting applied
        """
        # Create an alias for the sort join
        sort_alias = BusinessObjectExtension.__table__.alias(f'sort_{sort_field}')
        
        # Build join conditions
        join_conditions = [
            sort_alias.c.entity_type == entity_type,
            sort_alias.c.field_name == sort_field,
            sort_alias.c.is_active == True
        ]
        
        # Add company filter if provided
        if company_id is not None:
            join_conditions.append(sort_alias.c.company_id == company_id)
        
        # Join to the base query
        base_query = base_query.outerjoin(
            sort_alias,
            and_(
                sort_alias.c.entity_id == base_query.column_descriptions[0]['entity'].id,
                *join_conditions
            )
        )
        
        # Add ordering
        if sort_direction.lower() == 'desc':
            base_query = base_query.order_by(sort_alias.c.field_value.desc())
        else:
            base_query = base_query.order_by(sort_alias.c.field_value.asc())
        
        return base_query


# Utility functions for type conversion
def convert_to_extension_type(value: Any, field_type: str) -> str:
    """
    Convert a Python value to string format for extension storage.
    
    Args:
        value: The value to convert
        field_type: The target field type
        
    Returns:
        String representation suitable for storage
    """
    if value is None:
        return None
    
    if field_type == 'json':
        return json.dumps(value)
    elif field_type in ['date', 'datetime']:
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        else:
            return str(value)
    else:
        return str(value)


def convert_from_extension_type(value: str, field_type: str) -> Any:
    """
    Convert a stored string value to the appropriate Python type.
    
    Args:
        value: The stored string value
        field_type: The field type
        
    Returns:
        The value converted to the appropriate Python type
    """
    if value is None:
        return None
    
    try:
        if field_type == 'string':
            return str(value)
        elif field_type == 'integer':
            return int(value)
        elif field_type == 'decimal':
            return Decimal(value)
        elif field_type == 'boolean':
            return value.lower() in ('true', '1', 'yes', 'on')
        elif field_type == 'date':
            return datetime.fromisoformat(value).date()
        elif field_type == 'datetime':
            return datetime.fromisoformat(value)
        elif field_type == 'json':
            return json.loads(value)
        else:
            return value
    except (ValueError, TypeError, json.JSONDecodeError):
        return value