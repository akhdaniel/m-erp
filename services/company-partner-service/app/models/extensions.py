"""
Extension system models for Business Object Framework.

These models support dynamic custom fields, validation rules, and field definitions
for business objects with multi-company data isolation.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from app.models.base import CompanyBaseModel


class BusinessObjectExtension(CompanyBaseModel):
    """
    Model for storing custom field values for business objects.
    
    This table stores the actual values of custom fields that have been
    added to business objects dynamically. Each row represents one
    custom field value for a specific entity instance.
    """
    
    __tablename__ = "business_object_extensions"
    
    # Entity identification
    entity_type = Column(String(100), nullable=False, index=True)  # e.g., 'partner', 'company'
    entity_id = Column(Integer, nullable=False, index=True)  # ID of the actual entity record
    
    # Field definition
    field_name = Column(String(100), nullable=False, index=True)  # Name of the custom field
    field_type = Column(String(50), nullable=False)  # Type: 'string', 'integer', 'decimal', 'boolean', 'date', 'json'
    field_value = Column(Text, nullable=True)  # Stored as text, converted based on field_type
    
    # Framework fields
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    framework_version = Column(String(20), nullable=True, default='1.0.0')
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('entity_type', 'entity_id', 'field_name', 'company_id', 
                        name='uq_extensions_entity_field_company'),
        Index('idx_extensions_entity_company', 'entity_type', 'entity_id', 'company_id'),
        Index('idx_extensions_field_type', 'field_type'),
        Index('idx_extensions_active', 'is_active'),
        {'extend_existing': True}
    )
    
    def get_typed_value(self):
        """
        Convert the stored string value to the appropriate Python type.
        
        Returns:
            The field value converted to the appropriate type based on field_type
        """
        if self.field_value is None:
            return None
        
        try:
            if self.field_type == 'string':
                return str(self.field_value)
            elif self.field_type == 'integer':
                return int(self.field_value)
            elif self.field_type == 'decimal':
                from decimal import Decimal
                return Decimal(self.field_value)
            elif self.field_type == 'boolean':
                return self.field_value.lower() in ('true', '1', 'yes', 'on')
            elif self.field_type == 'date':
                from datetime import datetime
                return datetime.fromisoformat(self.field_value).date()
            elif self.field_type == 'datetime':
                from datetime import datetime
                return datetime.fromisoformat(self.field_value)
            elif self.field_type == 'json':
                import json
                return json.loads(self.field_value)
            else:
                return self.field_value
        except (ValueError, TypeError, json.JSONDecodeError):
            # Return original value if conversion fails
            return self.field_value
    
    def set_typed_value(self, value):
        """
        Set the field value from a Python type, converting to string for storage.
        
        Args:
            value: The value to store
        """
        if value is None:
            self.field_value = None
            return
        
        if self.field_type == 'json':
            import json
            self.field_value = json.dumps(value)
        elif self.field_type == 'date':
            if hasattr(value, 'isoformat'):
                self.field_value = value.isoformat()
            else:
                self.field_value = str(value)
        elif self.field_type == 'datetime':
            if hasattr(value, 'isoformat'):
                self.field_value = value.isoformat()
            else:
                self.field_value = str(value)
        else:
            self.field_value = str(value)
    
    def __repr__(self):
        return f"<BusinessObjectExtension(entity_type='{self.entity_type}', entity_id={self.entity_id}, field_name='{self.field_name}', field_value='{self.field_value}')>"


class BusinessObjectValidator(CompanyBaseModel):
    """
    Model for storing validation rules for custom fields.
    
    This table defines validation rules that should be applied to
    custom fields. Multiple validators can be applied to the same field.
    """
    
    __tablename__ = "business_object_validators"
    
    # Field identification
    entity_type = Column(String(100), nullable=False, index=True)  # e.g., 'partner', 'company'
    field_name = Column(String(100), nullable=False, index=True)  # Name of the field to validate
    
    # Validator definition
    validator_type = Column(String(50), nullable=False, index=True)  # e.g., 'required', 'email', 'range', 'pattern'
    validator_config = Column(Text, nullable=False, default='{}')  # JSON configuration for the validator
    validation_order = Column(Integer, nullable=False, default=0)  # Order in which to apply validators
    
    # Framework fields
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    framework_version = Column(String(20), nullable=True, default='1.0.0')
    
    # Indexes
    __table_args__ = (
        Index('idx_validators_entity_field', 'entity_type', 'field_name'),
        Index('idx_validators_company', 'company_id'),
        Index('idx_validators_type_active', 'validator_type', 'is_active'),
        Index('idx_validators_order', 'validation_order'),
        {'extend_existing': True}
    )
    
    def get_config(self):
        """
        Parse the validator configuration from JSON.
        
        Returns:
            Dictionary containing the validator configuration
        """
        try:
            import json
            return json.loads(self.validator_config or '{}')
        except json.JSONDecodeError:
            return {}
    
    def set_config(self, config_dict):
        """
        Set the validator configuration from a dictionary.
        
        Args:
            config_dict: Dictionary containing the validator configuration
        """
        import json
        self.validator_config = json.dumps(config_dict)
    
    def __repr__(self):
        return f"<BusinessObjectValidator(entity_type='{self.entity_type}', field_name='{self.field_name}', validator_type='{self.validator_type}')>"


class BusinessObjectFieldDefinition(CompanyBaseModel):
    """
    Model for storing field definitions and metadata.
    
    This table defines the structure and metadata for custom fields,
    including labels, descriptions, options, and display properties.
    """
    
    __tablename__ = "business_object_field_definitions"
    
    # Field identification
    entity_type = Column(String(100), nullable=False, index=True)  # e.g., 'partner', 'company'
    field_name = Column(String(100), nullable=False, index=True)  # Unique name for the field
    
    # Field properties
    field_type = Column(String(50), nullable=False)  # Data type: 'string', 'integer', 'decimal', etc.
    field_label = Column(String(200), nullable=True)  # Human-readable label
    field_description = Column(Text, nullable=True)  # Help text or description
    is_required = Column(Boolean, nullable=False, default=False)  # Whether the field is required
    default_value = Column(Text, nullable=True)  # Default value as string
    field_options = Column(Text, nullable=True)  # JSON for dropdown options, etc.
    
    # Display properties
    display_order = Column(Integer, nullable=False, default=0)  # Order for displaying fields
    
    # Framework fields
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    framework_version = Column(String(20), nullable=True, default='1.0.0')
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('entity_type', 'field_name', 'company_id', 
                        name='uq_field_definitions_entity_field_company'),
        Index('idx_field_definitions_entity_company', 'entity_type', 'company_id'),
        Index('idx_field_definitions_active', 'is_active'),
        Index('idx_field_definitions_order', 'display_order'),
        {'extend_existing': True}
    )
    
    def get_options(self):
        """
        Parse the field options from JSON.
        
        Returns:
            Dictionary or list containing field options (e.g., for select fields)
        """
        try:
            import json
            return json.loads(self.field_options or '{}')
        except json.JSONDecodeError:
            return {}
    
    def set_options(self, options):
        """
        Set the field options from a dictionary or list.
        
        Args:
            options: Dictionary or list containing field options
        """
        import json
        self.field_options = json.dumps(options)
    
    def get_default_typed_value(self):
        """
        Get the default value converted to the appropriate type.
        
        Returns:
            The default value converted based on field_type
        """
        if self.default_value is None:
            return None
        
        try:
            if self.field_type == 'string':
                return str(self.default_value)
            elif self.field_type == 'integer':
                return int(self.default_value)
            elif self.field_type == 'decimal':
                from decimal import Decimal
                return Decimal(self.default_value)
            elif self.field_type == 'boolean':
                return self.default_value.lower() in ('true', '1', 'yes', 'on')
            elif self.field_type == 'date':
                from datetime import datetime
                return datetime.fromisoformat(self.default_value).date()
            elif self.field_type == 'datetime':
                from datetime import datetime
                return datetime.fromisoformat(self.default_value)
            elif self.field_type == 'json':
                import json
                return json.loads(self.default_value)
            else:
                return self.default_value
        except (ValueError, TypeError, json.JSONDecodeError):
            return self.default_value
    
    def __repr__(self):
        return f"<BusinessObjectFieldDefinition(entity_type='{self.entity_type}', field_name='{self.field_name}', field_type='{self.field_type}')>"