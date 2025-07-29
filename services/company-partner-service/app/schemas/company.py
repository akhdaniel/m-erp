"""
Company schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class CompanyBase(BaseModel):
    """Base schema for company data."""
    name: str = Field(..., min_length=1, max_length=255)
    legal_name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=2, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    tax_id: Optional[str] = Field(None, max_length=100)
    street: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    currency: str = Field(default="USD", max_length=3)
    timezone: str = Field(default="UTC", max_length=50)
    logo_url: Optional[str] = None
    is_active: bool = True

    @validator('code')
    def validate_code(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Company code must be at least 2 characters')
        return v.strip().upper()

    @validator('currency')
    def validate_currency(cls, v):
        if v and len(v) != 3:
            raise ValueError('Currency must be 3 characters')
        return v.upper()


class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    tax_id: Optional[str] = Field(None, max_length=100)
    street: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    currency: Optional[str] = Field(None, max_length=3)
    timezone: Optional[str] = Field(None, max_length=50)
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('code')
    def validate_code(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Company code must be at least 2 characters')
        return v.strip().upper() if v else v

    @validator('currency')
    def validate_currency(cls, v):
        if v and len(v) != 3:
            raise ValueError('Currency must be 3 characters')
        return v.upper() if v else v


class CompanyResponse(CompanyBase):
    """Schema for company response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Schema for company list response."""
    companies: list[CompanyResponse]
    total: int
    page: int
    per_page: int
    pages: int