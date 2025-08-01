"""
Currency management API endpoints.
"""

from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middleware.auth import get_current_user_company
from app.services.currency_service import CurrencyService
from app.schemas.currency import (
    Currency, CurrencyCreate, CurrencyUpdate, CurrencyList,
    CurrencyRate, CurrencyRateCreate, CurrencyRateUpdate, CurrencyRateList,
    CurrencyConversionRequest, CurrencyConversionResponse,
    CurrencyFormattingRequest, CurrencyFormattingResponse
)

router = APIRouter(prefix="/api/v1/currencies", tags=["currencies"])


def get_currency_service(
    db: AsyncSession = Depends(get_db),
    company_id: int = Depends(get_current_user_company)
) -> CurrencyService:
    """Get currency service instance."""
    return CurrencyService(db, company_id)


# Currency Management Endpoints

@router.post("/", response_model=Currency, status_code=status.HTTP_201_CREATED)
async def create_currency(
    currency_data: CurrencyCreate,
    service: CurrencyService = Depends(get_currency_service)
):
    """Create a new currency."""
    return await service.create_currency(currency_data)


@router.get("/", response_model=CurrencyList)
async def list_currencies(
    skip: int = Query(0, ge=0, description="Number of currencies to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of currencies to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in code, name, or symbol"),
    service: CurrencyService = Depends(get_currency_service)
):
    """List currencies with optional filtering."""
    currencies, total = await service.list_currencies(
        skip=skip,
        limit=limit,
        is_active=is_active,
        search=search
    )
    
    return CurrencyList(
        currencies=currencies,
        total=total,
        page=skip // limit + 1,
        size=len(currencies)
    )


@router.get("/{currency_id}", response_model=Currency)
async def get_currency(
    currency_id: int,
    service: CurrencyService = Depends(get_currency_service)
):
    """Get currency by ID."""
    return await service.get_currency(currency_id)


@router.get("/by-code/{currency_code}", response_model=Currency)
async def get_currency_by_code(
    currency_code: str,
    service: CurrencyService = Depends(get_currency_service)
):
    """Get currency by code."""
    return await service.get_currency_by_code(currency_code)


@router.put("/{currency_id}", response_model=Currency)
async def update_currency(
    currency_id: int,
    currency_data: CurrencyUpdate,
    service: CurrencyService = Depends(get_currency_service)
):
    """Update a currency."""
    return await service.update_currency(currency_id, currency_data)


@router.delete("/{currency_id}")
async def delete_currency(
    currency_id: int,
    service: CurrencyService = Depends(get_currency_service)
):
    """Delete a currency (deactivate if in use)."""
    success = await service.delete_currency(currency_id)
    return {"message": "Currency deleted successfully" if success else "Failed to delete currency"}


# Exchange Rate Endpoints

@router.post("/rates", response_model=CurrencyRate, status_code=status.HTTP_201_CREATED)
async def create_exchange_rate(
    rate_data: CurrencyRateCreate,
    service: CurrencyService = Depends(get_currency_service)
):
    """Create a new exchange rate."""
    return await service.create_rate(rate_data)


@router.get("/rates", response_model=CurrencyRateList)
async def list_exchange_rates(
    currency_id: Optional[int] = Query(None, description="Filter by currency ID"),
    skip: int = Query(0, ge=0, description="Number of rates to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of rates to return"),
    service: CurrencyService = Depends(get_currency_service)
):
    """List exchange rates with optional filtering."""
    rates, total = await service.list_rates(
        currency_id=currency_id,
        skip=skip,
        limit=limit
    )
    
    return CurrencyRateList(
        rates=rates,
        total=total,
        page=skip // limit + 1,
        size=len(rates)
    )


@router.get("/rates/{from_currency_id}/{to_currency_id}", response_model=CurrencyRate)
async def get_current_exchange_rate(
    from_currency_id: int,
    to_currency_id: int,
    service: CurrencyService = Depends(get_currency_service)
):
    """Get current exchange rate between two currencies."""
    rate = await service.get_current_rate(from_currency_id, to_currency_id)
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No exchange rate found between currencies {from_currency_id} and {to_currency_id}"
        )
    return rate


@router.put("/rates/{rate_id}", response_model=CurrencyRate)
async def update_exchange_rate(
    rate_id: int,
    rate_data: CurrencyRateUpdate,
    service: CurrencyService = Depends(get_currency_service)
):
    """Update an exchange rate."""
    return await service.update_rate(rate_id, rate_data)


# Currency Conversion Endpoints

@router.post("/convert", response_model=CurrencyConversionResponse)
async def convert_currency(
    conversion: CurrencyConversionRequest,
    service: CurrencyService = Depends(get_currency_service)
):
    """Convert amount between currencies."""
    return await service.convert_amount(conversion)


@router.post("/format", response_model=CurrencyFormattingResponse)
async def format_currency(
    formatting: CurrencyFormattingRequest,
    service: CurrencyService = Depends(get_currency_service)
):
    """Format amount according to currency settings."""
    formatted = await service.format_amount(formatting.amount, formatting.currency_code)
    
    return CurrencyFormattingResponse(
        formatted_amount=formatted,
        currency_code=formatting.currency_code.upper(),
        raw_amount=formatting.amount
    )


# Utility Endpoints

@router.get("/base/current", response_model=Currency)
async def get_base_currency(
    service: CurrencyService = Depends(get_currency_service)
):
    """Get the current base currency for the company."""
    return await service.get_base_currency()


@router.get("/active/summary")
async def get_currencies_summary(
    service: CurrencyService = Depends(get_currency_service)
):
    """Get summary of active currencies."""
    currencies, total = await service.list_currencies(is_active=True, limit=1000)
    
    base_currency = None
    try:
        base_currency = await service.get_base_currency()
    except HTTPException:
        pass
    
    return {
        "total_active": total,
        "currencies": [
            {
                "id": curr.id,
                "code": curr.code,
                "name": curr.name,
                "symbol": curr.symbol,
                "is_base": curr.is_base
            }
            for curr in currencies
        ],
        "base_currency": {
            "id": base_currency.id,
            "code": base_currency.code,
            "name": base_currency.name,
            "symbol": base_currency.symbol
        } if base_currency else None
    }