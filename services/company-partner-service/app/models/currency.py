"""
Currency models for multi-currency support.
"""

from decimal import Decimal
from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, Text, CheckConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Currency(BaseModel):
    """
    Currency model for multi-currency operations.
    
    This model stores currency definitions used throughout the system.
    All monetary amounts reference currencies for proper localization and conversion.
    """
    
    __tablename__ = "currencies"
    
    # Currency identification
    code = Column(String(3), unique=True, nullable=False, index=True)  # ISO 4217 code (USD, EUR, etc.)
    name = Column(String(100), nullable=False)  # US Dollar, Euro, etc.
    symbol = Column(String(10), nullable=False)  # $, €, £, etc.
    
    # Configuration
    decimal_places = Column(Integer, default=2, nullable=False)  # Number of decimal places
    rounding = Column(Numeric(10, 6), default=Decimal('0.01'), nullable=False)  # Rounding precision
    
    # Display formatting
    position = Column(String(10), default='before', nullable=False)  # 'before' ($100) or 'after' (100$)
    thousands_sep = Column(String(1), default=',')  # Thousands separator
    decimal_sep = Column(String(1), default='.')  # Decimal separator
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_base = Column(Boolean, default=False, nullable=False, index=True)  # Base currency for calculations
    
    # Multi-company support
    company_id = Column(Integer, nullable=False, index=True)
    
    # Relationships
    # exchange_rates = relationship("CurrencyRate", back_populates="currency")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("LENGTH(code) = 3", name="currencies_code_length_check"),
        CheckConstraint("LENGTH(name) >= 1", name="currencies_name_check"),
        CheckConstraint("LENGTH(symbol) >= 1", name="currencies_symbol_check"),
        CheckConstraint("decimal_places >= 0", name="currencies_decimal_places_check"),
        CheckConstraint("decimal_places <= 6", name="currencies_decimal_places_max_check"),
        CheckConstraint("position IN ('before', 'after')", name="currencies_position_check"),
        Index('idx_currencies_active_base', 'is_active', 'is_base'),
        {'extend_existing': True}
    )
    
    def __str__(self):
        """String representation of the currency."""
        return f"Currency(code='{self.code}', name='{self.name}', active={self.is_active})"
    
    def __repr__(self):
        """Detailed representation of the currency."""
        return (
            f"Currency(id={self.id}, code='{self.code}', name='{self.name}', "
            f"symbol='{self.symbol}', active={self.is_active})"
        )
    
    def format_amount(self, amount: Decimal) -> str:
        """Format an amount according to this currency's settings."""
        # Round the amount according to currency settings
        rounded_amount = amount.quantize(self.rounding)
        
        # Format with decimal places
        formatted = f"{rounded_amount:.{self.decimal_places}f}"
        
        # Add thousands separator
        if self.thousands_sep and len(formatted.split('.')[0]) > 3:
            parts = formatted.split('.')
            integer_part = parts[0]
            decimal_part = parts[1] if len(parts) > 1 else ''
            
            # Add thousands separators
            reversed_int = integer_part[::-1]
            separated = self.thousands_sep.join([reversed_int[i:i+3] for i in range(0, len(reversed_int), 3)])
            integer_part = separated[::-1]
            
            formatted = integer_part
            if decimal_part:
                formatted += self.decimal_sep + decimal_part
        
        # Add currency symbol
        if self.position == 'before':
            return f"{self.symbol}{formatted}"
        else:
            return f"{formatted}{self.symbol}"


class CurrencyRate(BaseModel):
    """
    Currency exchange rate model for currency conversions.
    
    This model stores historical and current exchange rates between currencies.
    Rates are stored as conversion factors from the base currency.
    """
    
    __tablename__ = "currency_rates"
    
    # Rate identification
    currency_id = Column(Integer, nullable=False, index=True)  # Target currency
    base_currency_id = Column(Integer, nullable=False, index=True)  # Base currency (usually company currency)
    
    # Rate data
    rate = Column(Numeric(20, 10), nullable=False)  # Exchange rate (base_currency_amount = target_currency_amount * rate)
    inverse_rate = Column(Numeric(20, 10), nullable=False)  # Inverse rate for optimization
    
    # Temporal data
    date_start = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    date_end = Column(DateTime(timezone=True), index=True)  # NULL means current rate
    
    # Rate source and metadata
    source = Column(String(50), default='manual')  # 'manual', 'api', 'system'
    provider = Column(String(100))  # Rate provider (e.g., 'fixer.io', 'manual_entry')
    
    # Multi-company support
    company_id = Column(Integer, nullable=False, index=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("rate > 0", name="currency_rates_rate_positive_check"),
        CheckConstraint("inverse_rate > 0", name="currency_rates_inverse_rate_positive_check"),
        CheckConstraint("date_end IS NULL OR date_end > date_start", name="currency_rates_date_check"),
        Index('idx_currency_rates_lookup', 'currency_id', 'base_currency_id', 'company_id', 'date_start'),
        Index('idx_currency_rates_current', 'currency_id', 'base_currency_id', 'company_id', 'date_end'),
        {'extend_existing': True}
    )
    
    def __str__(self):
        """String representation of the currency rate."""
        return f"CurrencyRate(currency_id={self.currency_id}, rate={self.rate}, date={self.date_start})"
    
    def __repr__(self):
        """Detailed representation of the currency rate."""
        return (
            f"CurrencyRate(id={self.id}, currency_id={self.currency_id}, "
            f"base_currency_id={self.base_currency_id}, rate={self.rate}, "
            f"date_start={self.date_start}, company_id={self.company_id})"
        )
    
    def is_current(self) -> bool:
        """Check if this rate is currently active."""
        return self.date_end is None
    
    def convert_amount(self, amount: Decimal, to_base: bool = False) -> Decimal:
        """Convert amount using this rate."""
        if to_base:
            # Convert from target currency to base currency
            return amount * self.rate
        else:
            # Convert from base currency to target currency
            return amount * self.inverse_rate