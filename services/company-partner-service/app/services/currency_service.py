"""
Currency service for managing currencies and exchange rates.
"""

from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, desc, asc, select, update, delete
from fastapi import HTTPException, status

from app.models.currency import Currency, CurrencyRate
from app.schemas.currency import (
    CurrencyCreate, CurrencyUpdate, CurrencyRateCreate, CurrencyRateUpdate,
    CurrencyConversionRequest, CurrencyConversionResponse
)


class CurrencyService:
    """Service for currency operations."""
    
    def __init__(self, db: AsyncSession, company_id: int):
        """Initialize currency service."""
        self.db = db
        self.company_id = company_id
    
    # Currency CRUD Operations
    
    async def create_currency(self, currency_data: CurrencyCreate) -> Currency:
        """Create a new currency."""
        # Check if currency code already exists for this company
        stmt = select(Currency).where(
            and_(
                Currency.code == currency_data.code.upper(),
                Currency.company_id == self.company_id
            )
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Currency with code '{currency_data.code}' already exists"
            )
        
        # Ensure only one base currency per company
        if currency_data.is_base:
            await self._ensure_single_base_currency()
        
        # Create currency
        currency = Currency(
            **currency_data.dict(),
            company_id=self.company_id
        )
        
        self.db.add(currency)
        await self.db.commit()
        await self.db.refresh(currency)
        
        return currency
    
    async def get_currency(self, currency_id: int) -> Currency:
        """Get currency by ID."""
        stmt = select(Currency).where(
            and_(
                Currency.id == currency_id,
                Currency.company_id == self.company_id
            )
        )
        result = await self.db.execute(stmt)
        currency = result.scalar_one_or_none()
        
        if not currency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Currency not found"
            )
        
        return currency
    
    async def get_currency_by_code(self, code: str) -> Currency:
        """Get currency by code."""
        stmt = select(Currency).where(
            and_(
                Currency.code == code.upper(),
                Currency.company_id == self.company_id
            )
        )
        result = await self.db.execute(stmt)
        currency = result.scalar_one_or_none()
        
        if not currency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Currency with code '{code}' not found"
            )
        
        return currency
    
    async def list_currencies(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Currency], int]:
        """List currencies with optional filtering."""
        # Build base query
        conditions = [Currency.company_id == self.company_id]
        
        # Apply filters
        if is_active is not None:
            conditions.append(Currency.is_active == is_active)
        
        if search:
            search_term = f"%{search}%"
            conditions.append(
                or_(
                    Currency.code.ilike(search_term),
                    Currency.name.ilike(search_term),
                    Currency.symbol.ilike(search_term)
                )
            )
        
        # Get total count
        count_stmt = select(func.count(Currency.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        stmt = select(Currency).where(and_(*conditions)).order_by(
            desc(Currency.is_base),  # Base currency first
            asc(Currency.code)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        currencies = result.scalars().all()
        
        return list(currencies), total
    
    async def update_currency(self, currency_id: int, currency_data: CurrencyUpdate) -> Currency:
        """Update a currency."""
        currency = await self.get_currency(currency_id)
        
        # Ensure only one base currency per company
        if currency_data.is_base and not currency.is_base:
            await self._ensure_single_base_currency()
        
        # Update fields
        for field, value in currency_data.dict(exclude_unset=True).items():
            setattr(currency, field, value)
        
        await self.db.commit()
        await self.db.refresh(currency)
        
        return currency
    
    async def delete_currency(self, currency_id: int) -> bool:
        """Delete a currency (soft delete by deactivating)."""
        currency = await self.get_currency(currency_id)
        
        # Don't allow deleting base currency
        if currency.is_base:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete base currency"
            )
        
        # Check if currency is used in any active rates
        count_stmt = select(func.count(CurrencyRate.id)).where(
            and_(
                or_(
                    CurrencyRate.currency_id == currency_id,
                    CurrencyRate.base_currency_id == currency_id
                ),
                CurrencyRate.date_end.is_(None),
                CurrencyRate.company_id == self.company_id
            )
        )
        count_result = await self.db.execute(count_stmt)
        active_rates = count_result.scalar()
        
        if active_rates > 0:
            # Soft delete by deactivating
            currency.is_active = False
            await self.db.commit()
        else:
            # Hard delete if no active rates
            await self.db.delete(currency)
            await self.db.commit()
        
        return True
    
    # Exchange Rate Operations
    
    async def create_rate(self, rate_data: CurrencyRateCreate) -> CurrencyRate:
        """Create a new exchange rate."""
        # Validate currencies exist
        await self.get_currency(rate_data.base_currency_id)
        await self.get_currency(rate_data.currency_id)
        
        # End any existing current rate for this pair
        await self._end_current_rate(rate_data.currency_id, rate_data.base_currency_id)
        
        # Calculate inverse rate
        inverse_rate = Decimal('1') / rate_data.rate
        
        rate = CurrencyRate(
            **rate_data.dict(),
            inverse_rate=inverse_rate,
            company_id=self.company_id
        )
        
        self.db.add(rate)
        await self.db.commit()
        await self.db.refresh(rate)
        
        return rate
    
    async def get_current_rate(self, from_currency_id: int, to_currency_id: int) -> Optional[CurrencyRate]:
        """Get current exchange rate between two currencies."""
        stmt = select(CurrencyRate).where(
            and_(
                CurrencyRate.currency_id == to_currency_id,
                CurrencyRate.base_currency_id == from_currency_id,
                CurrencyRate.date_end.is_(None),
                CurrencyRate.company_id == self.company_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_rate_at_date(
        self,
        from_currency_id: int,
        to_currency_id: int,
        date: datetime
    ) -> Optional[CurrencyRate]:
        """Get exchange rate at a specific date."""
        stmt = select(CurrencyRate).where(
            and_(
                CurrencyRate.currency_id == to_currency_id,
                CurrencyRate.base_currency_id == from_currency_id,
                CurrencyRate.date_start <= date,
                or_(
                    CurrencyRate.date_end.is_(None),
                    CurrencyRate.date_end > date
                ),
                CurrencyRate.company_id == self.company_id
            )
        ).order_by(desc(CurrencyRate.date_start))
        
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def list_rates(
        self,
        currency_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[CurrencyRate], int]:
        """List exchange rates."""
        conditions = [CurrencyRate.company_id == self.company_id]
        
        if currency_id:
            conditions.append(
                or_(
                    CurrencyRate.currency_id == currency_id,
                    CurrencyRate.base_currency_id == currency_id
                )
            )
        
        # Get total count
        count_stmt = select(func.count(CurrencyRate.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # Get rates
        stmt = select(CurrencyRate).where(and_(*conditions)).order_by(
            desc(CurrencyRate.date_start)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        rates = result.scalars().all()
        
        return list(rates), total
    
    async def update_rate(self, rate_id: int, rate_data: CurrencyRateUpdate) -> CurrencyRate:
        """Update an exchange rate."""
        stmt = select(CurrencyRate).where(
            and_(
                CurrencyRate.id == rate_id,
                CurrencyRate.company_id == self.company_id
            )
        )
        result = await self.db.execute(stmt)
        rate = result.scalar_one_or_none()
        
        if not rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange rate not found"
            )
        
        # Update fields
        for field, value in rate_data.dict(exclude_unset=True).items():
            setattr(rate, field, value)
        
        # Recalculate inverse rate if rate changed
        if hasattr(rate_data, 'rate') and rate_data.rate:
            rate.inverse_rate = Decimal('1') / rate.rate
        
        await self.db.commit()
        await self.db.refresh(rate)
        
        return rate
    
    # Currency Conversion Operations
    
    async def convert_amount(self, conversion: CurrencyConversionRequest) -> CurrencyConversionResponse:
        """Convert amount between currencies."""
        # Get currencies
        from_currency = await self.get_currency_by_code(conversion.from_currency)
        to_currency = await self.get_currency_by_code(conversion.to_currency)
        
        # If same currency, return as-is
        if from_currency.id == to_currency.id:
            return CurrencyConversionResponse(
                original_amount=conversion.amount,
                converted_amount=conversion.amount,
                from_currency=conversion.from_currency,
                to_currency=conversion.to_currency,
                rate=Decimal('1'),
                conversion_date=conversion.date or datetime.now(timezone.utc)
            )
        
        # Get exchange rate
        conversion_date = conversion.date or datetime.now(timezone.utc)
        
        if conversion.date:
            rate = await self.get_rate_at_date(from_currency.id, to_currency.id, conversion_date)
        else:
            rate = await self.get_current_rate(from_currency.id, to_currency.id)
        
        if not rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No exchange rate found for {conversion.from_currency} to {conversion.to_currency}"
            )
        
        # Convert amount
        converted_amount = conversion.amount * rate.inverse_rate
        
        return CurrencyConversionResponse(
            original_amount=conversion.amount,
            converted_amount=converted_amount,
            from_currency=conversion.from_currency,
            to_currency=conversion.to_currency,
            rate=rate.inverse_rate,
            conversion_date=conversion_date
        )
    
    async def format_amount(self, amount: Decimal, currency_code: str) -> str:
        """Format amount according to currency settings."""
        currency = await self.get_currency_by_code(currency_code)
        return currency.format_amount(amount)
    
    # Utility Methods
    
    async def _ensure_single_base_currency(self):
        """Ensure only one base currency exists per company."""
        stmt = update(Currency).where(
            and_(
                Currency.company_id == self.company_id,
                Currency.is_base == True
            )
        ).values(is_base=False)
        await self.db.execute(stmt)
    
    async def _end_current_rate(self, currency_id: int, base_currency_id: int):
        """End current exchange rate for currency pair."""
        stmt = update(CurrencyRate).where(
            and_(
                CurrencyRate.currency_id == currency_id,
                CurrencyRate.base_currency_id == base_currency_id,
                CurrencyRate.date_end.is_(None),
                CurrencyRate.company_id == self.company_id
            )
        ).values(date_end=datetime.now(timezone.utc))
        await self.db.execute(stmt)
    
    async def get_base_currency(self) -> Currency:
        """Get the base currency for the company."""
        stmt = select(Currency).where(
            and_(
                Currency.company_id == self.company_id,
                Currency.is_base == True,
                Currency.is_active == True
            )
        )
        result = await self.db.execute(stmt)
        base_currency = result.scalar_one_or_none()
        
        if not base_currency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No base currency configured for company"
            )
        
        return base_currency