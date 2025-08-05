"""
Partner Category schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class PartnerCategoryBase(BaseModel):
    """Base schema for partner category data."""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7, pattern=r'^#[0-9A-Fa-f]{6}$')
    parent_category_id: Optional[int] = None
    is_active: bool = True
    is_default: bool = False

    @validator('code')
    def validate_code(cls, v):
        if v and len(v.strip()) < 1:
            raise ValueError('Category code cannot be empty')
        return v.strip().upper() if v else v

    @validator('name')
    def validate_name(cls, v):
        if v and len(v.strip()) < 1:
            raise ValueError('Category name cannot be empty')
        return v.strip() if v else v

    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            v = f"#{v}"
        return v


class PartnerCategoryCreate(PartnerCategoryBase):
    """Schema for creating a new partner category."""
    company_id: int = Field(..., gt=0)


class PartnerCategoryUpdate(BaseModel):
    """Schema for updating a partner category."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7, pattern=r'^#[0-9A-Fa-f]{6}$')
    parent_category_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

    @validator('code')
    def validate_code(cls, v):
        if v and len(v.strip()) < 1:
            raise ValueError('Category code cannot be empty')
        return v.strip().upper() if v else v

    @validator('name')
    def validate_name(cls, v):
        if v and len(v.strip()) < 1:
            raise ValueError('Category name cannot be empty')
        return v.strip() if v else v

    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            v = f"#{v}"
        return v


class PartnerCategoryResponse(PartnerCategoryBase):
    """Schema for partner category response."""
    id: int
    company_id: int
    full_path: str
    is_parent: bool
    has_parent: bool
    partner_count: int
    can_be_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PartnerCategoryTreeResponse(BaseModel):
    """Schema for hierarchical partner category tree response."""
    id: int
    name: str
    code: str
    description: Optional[str]
    color: Optional[str]
    is_active: bool
    is_default: bool
    partner_count: int
    children: Optional[List['PartnerCategoryTreeResponse']] = []

    class Config:
        from_attributes = True


class PartnerCategoryListResponse(BaseModel):
    """Schema for partner category list response."""
    categories: List[PartnerCategoryResponse]
    total: int
    page: int
    per_page: int
    pages: int


class PartnerCategoryStatsResponse(BaseModel):
    """Schema for partner category statistics response."""
    total_categories: int
    active_categories: int
    categories_with_partners: int
    top_categories: List[dict]  # Top categories by partner count