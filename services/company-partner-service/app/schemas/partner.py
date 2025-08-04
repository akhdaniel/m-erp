"""
Partner schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class PartnerBase(BaseModel):
    """Base schema for partner data."""
    name: str = Field(..., min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    partner_type: str = Field(default="customer", max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    mobile: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    tax_id: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    parent_partner_id: Optional[int] = None
    category_id: Optional[int] = None
    is_company: bool = False
    is_customer: bool = True
    is_supplier: bool = False
    is_vendor: bool = False
    is_active: bool = True

    @validator('partner_type')
    def validate_partner_type(cls, v):
        valid_types = ['customer', 'supplier', 'vendor', 'both']
        if v not in valid_types:
            raise ValueError(f'Partner type must be one of: {", ".join(valid_types)}')
        return v

    @validator('code')
    def validate_code(cls, v):
        if v and len(v.strip()) < 1:
            raise ValueError('Partner code cannot be empty')
        return v.strip().upper() if v else v


class PartnerCreate(PartnerBase):
    """Schema for creating a new partner."""
    company_id: int = Field(..., gt=0)


class PartnerUpdate(BaseModel):
    """Schema for updating a partner."""
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
    category_id: Optional[int] = None
    is_company: Optional[bool] = None
    is_customer: Optional[bool] = None
    is_supplier: Optional[bool] = None
    is_vendor: Optional[bool] = None
    is_active: Optional[bool] = None

    @validator('partner_type')
    def validate_partner_type(cls, v):
        if v:
            valid_types = ['customer', 'supplier', 'vendor', 'both']
            if v not in valid_types:
                raise ValueError(f'Partner type must be one of: {", ".join(valid_types)}')
        return v

    @validator('code')
    def validate_code(cls, v):
        if v and len(v.strip()) < 1:
            raise ValueError('Partner code cannot be empty')
        return v.strip().upper() if v else v


class PartnerResponse(PartnerBase):
    """Schema for partner response."""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PartnerListResponse(BaseModel):
    """Schema for partner list response."""
    partners: list[PartnerResponse]
    total: int
    page: int
    per_page: int
    pages: int