"""
Currency schemas for API request/response validation.
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, validator, Field


class CurrencyBase(BaseModel):
    """Base currency schema with common fields."""
    code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    name: str = Field(..., min_length=1, max_length=100, description="Currency name")
    symbol: str = Field(..., min_length=1, max_length=10, description="Currency symbol")
    decimal_places: int = Field(default=2, ge=0, le=6, description="Number of decimal places")
    rounding: Decimal = Field(default=Decimal('0.01'), description="Rounding precision")
    position: str = Field(default='before', description="Symbol position")
    thousands_sep: Optional[str] = Field(default=',', max_length=1, description="Thousands separator")
    decimal_sep: Optional[str] = Field(default='.', max_length=1, description="Decimal separator")
    is_active: bool = Field(default=True, description="Whether currency is active")
    is_base: bool = Field(default=False, description="Whether this is the base currency")
    
    @validator('code')
    def code_must_be_uppercase(cls, v):
        """Ensure currency code is uppercase."""
        return v.upper()
    
    @validator('position')
    def position_must_be_valid(cls, v):
        """Ensure position is valid."""
        if v not in ['before', 'after']:
            raise ValueError("Position must be 'before' or 'after'")
        return v
    
    @validator('rounding')
    def rounding_must_be_positive(cls, v):
        """Ensure rounding is positive."""
        if v <= 0:
            raise ValueError("Rounding must be positive")
        return v


class CurrencyCreate(CurrencyBase):
    """Schema for creating a new currency."""
    pass


class CurrencyUpdate(BaseModel):
    """Schema for updating a currency."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    decimal_places: Optional[int] = Field(None, ge=0, le=6)
    rounding: Optional[Decimal] = None
    position: Optional[str] = None
    thousands_sep: Optional[str] = Field(None, max_length=1)
    decimal_sep: Optional[str] = Field(None, max_length=1)
    is_active: Optional[bool] = None
    is_base: Optional[bool] = None
    
    @validator('position')
    def position_must_be_valid(cls, v):
        """Ensure position is valid."""
        if v is not None and v not in ['before', 'after']:
            raise ValueError("Position must be 'before' or 'after'")
        return v
    
    @validator('rounding')
    def rounding_must_be_positive(cls, v):
        """Ensure rounding is positive."""
        if v is not None and v <= 0:
            raise ValueError("Rounding must be positive")
        return v


class Currency(CurrencyBase):
    """Schema for currency response."""
    id: int
    created_at: datetime
    updated_at: datetime
    company_id: int
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class CurrencyList(BaseModel):
    """Schema for currency list response."""
    currencies: List[Currency]
    total: int
    page: int
    size: int
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


# Currency Rate Schemas

class CurrencyRateBase(BaseModel):
    """Base currency rate schema with common fields."""
    currency_id: int = Field(..., description="Target currency ID")
    base_currency_id: int = Field(..., description="Base currency ID")
    rate: Decimal = Field(..., gt=0, description="Exchange rate")
    date_start: datetime = Field(..., description="Rate start date")
    date_end: Optional[datetime] = Field(None, description="Rate end date")
    source: str = Field(default='manual', max_length=50, description="Rate source")
    provider: Optional[str] = Field(None, max_length=100, description="Rate provider")
    
    @validator('rate')
    def rate_must_be_positive(cls, v):
        """Ensure rate is positive."""
        if v <= 0:
            raise ValueError("Rate must be positive")
        return v
    
    @validator('date_end')
    def date_end_must_be_after_start(cls, v, values):
        """Ensure end date is after start date."""
        if v is not None and 'date_start' in values and v <= values['date_start']:
            raise ValueError("End date must be after start date")
        return v


class CurrencyRateCreate(CurrencyRateBase):
    """Schema for creating a new currency rate."""
    pass


class CurrencyRateUpdate(BaseModel):
    """Schema for updating a currency rate."""
    rate: Optional[Decimal] = Field(None, gt=0)
    date_end: Optional[datetime] = None
    source: Optional[str] = Field(None, max_length=50)
    provider: Optional[str] = Field(None, max_length=100)


class CurrencyRate(CurrencyRateBase):
    """Schema for currency rate response."""
    id: int
    inverse_rate: Decimal
    created_at: datetime
    updated_at: datetime
    company_id: int
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class CurrencyRateList(BaseModel):
    """Schema for currency rate list response."""
    rates: List[CurrencyRate]
    total: int
    page: int
    size: int
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


# Conversion Schemas

class CurrencyConversionRequest(BaseModel):
    """Schema for currency conversion request."""
    amount: Decimal = Field(..., description="Amount to convert")
    from_currency: str = Field(..., min_length=3, max_length=3, description="Source currency code")
    to_currency: str = Field(..., min_length=3, max_length=3, description="Target currency code")
    date: Optional[datetime] = Field(None, description="Conversion date (defaults to current)")
    
    @validator('from_currency', 'to_currency')
    def currency_must_be_uppercase(cls, v):
        """Ensure currency codes are uppercase."""
        return v.upper()


class CurrencyConversionResponse(BaseModel):
    """Schema for currency conversion response."""
    original_amount: Decimal
    converted_amount: Decimal
    from_currency: str
    to_currency: str
    rate: Decimal
    conversion_date: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class CurrencyFormattingRequest(BaseModel):
    """Schema for currency formatting request."""
    amount: Decimal = Field(..., description="Amount to format")
    currency_code: str = Field(..., min_length=3, max_length=3, description="Currency code")
    
    @validator('currency_code')
    def currency_must_be_uppercase(cls, v):
        """Ensure currency code is uppercase."""
        return v.upper()


class CurrencyFormattingResponse(BaseModel):
    """Schema for currency formatting response."""
    formatted_amount: str
    currency_code: str
    raw_amount: Decimal
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True