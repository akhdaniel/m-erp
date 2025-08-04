"""
Framework-based Partner schemas using Business Object Framework.

This file demonstrates how to migrate existing Partner schemas to use the
Business Object Framework base classes while maintaining compatibility.
"""

from typing import Optional
from pydantic import Field, validator

from app.framework.schemas import (
    CompanyBusinessObjectSchema,
    CreateSchemaBase,
    UpdateSchemaBase
)


class PartnerFrameworkBase(CompanyBusinessObjectSchema):
    """Framework-based base schema for partner data."""
    
    # Core partner fields
    name: str = Field(..., min_length=1, max_length=255, description="Partner name")
    code: Optional[str] = Field(None, max_length=50, description="Partner code")
    partner_type: str = Field(default="customer", max_length=20, description="Partner type")
    
    # Contact information
    email: Optional[str] = Field(None, max_length=255, description="Email address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    mobile: Optional[str] = Field(None, max_length=50, description="Mobile number")
    website: Optional[str] = Field(None, max_length=255, description="Website URL")
    
    # Business information
    tax_id: Optional[str] = Field(None, max_length=100, description="Tax ID")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    
    # Relationship management
    parent_partner_id: Optional[int] = Field(None, description="Parent partner ID")
    
    # Partner type flags
    is_company: bool = Field(False, description="Is a company")
    is_customer: bool = Field(True, description="Is a customer")
    is_supplier: bool = Field(False, description="Is a supplier")
    is_vendor: bool = Field(False, description="Is a vendor")
    is_active: bool = Field(True, description="Is active")

    @validator('partner_type')
    def validate_partner_type(cls, v):
        """Validate partner type."""
        valid_types = ['customer', 'supplier', 'vendor', 'both']
        if v not in valid_types:
            raise ValueError(f'Partner type must be one of: {", ".join(valid_types)}')
        return v

    @validator('code')
    def validate_code(cls, v):
        """Validate and normalize partner code."""
        if v and len(v.strip()) < 1:
            raise ValueError('Partner code cannot be empty')
        return v.strip().upper() if v else v


class PartnerFrameworkCreate(CreateSchemaBase, PartnerFrameworkBase):
    """Framework-based schema for creating a new partner."""
    
    # Override company_id to make it required for creation
    company_id: int = Field(..., gt=0, description="Company ID")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "ACME Corp",
                "code": "ACME001",
                "partner_type": "customer",
                "email": "contact@acme.com",
                "phone": "+1-555-0123",
                "is_customer": True,
                "is_company": True,
                "company_id": 1
            }
        }


class PartnerFrameworkUpdate(UpdateSchemaBase):
    """Framework-based schema for updating a partner."""
    
    # All fields optional for updates
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    partner_type: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    mobile: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    tax_id: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    parent_partner_id: Optional[int] = None
    is_company: Optional[bool] = None
    is_customer: Optional[bool] = None
    is_supplier: Optional[bool] = None
    is_vendor: Optional[bool] = None
    is_active: Optional[bool] = None

    @validator('partner_type')
    def validate_partner_type(cls, v):
        """Validate partner type if provided."""
        if v:
            valid_types = ['customer', 'supplier', 'vendor', 'both']
            if v not in valid_types:
                raise ValueError(f'Partner type must be one of: {", ".join(valid_types)}')
        return v

    @validator('code')
    def validate_code(cls, v):
        """Validate and normalize partner code if provided."""
        if v and len(v.strip()) < 1:
            raise ValueError('Partner code cannot be empty')
        return v.strip().upper() if v else v

    class Config:
        schema_extra = {
            "example": {
                "name": "Updated Partner Name",
                "email": "newemail@example.com",
                "phone": "+1-555-9999",
                "is_active": True
            }
        }


class PartnerFrameworkResponse(PartnerFrameworkBase):
    """Framework-based schema for partner response."""
    
    # Add ID field from framework
    id: int = Field(..., description="Partner ID")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "company_id": 1,
                "name": "ACME Corp",
                "code": "ACME001",
                "partner_type": "customer",
                "email": "contact@acme.com",
                "phone": "+1-555-0123",
                "is_customer": True,
                "is_company": True,
                "is_active": True,
                "created_at": "2025-08-01T10:00:00Z",
                "updated_at": "2025-08-01T10:00:00Z"
            }
        }


class PartnerFrameworkListResponse(CompanyBusinessObjectSchema):
    """Framework-based schema for partner list response."""
    
    partners: list[PartnerFrameworkResponse] = Field(..., description="List of partners")
    total: int = Field(..., description="Total number of partners")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of partners per page")
    pages: int = Field(..., description="Total number of pages")
    
    class Config:
        schema_extra = {
            "example": {
                "partners": [
                    {
                        "id": 1,
                        "company_id": 1,
                        "name": "ACME Corp",
                        "code": "ACME001",
                        "partner_type": "customer",
                        "is_customer": True,
                        "is_active": True,
                        "created_at": "2025-08-01T10:00:00Z",
                        "updated_at": "2025-08-01T10:00:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "per_page": 50,
                "pages": 1
            }
        }