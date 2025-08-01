"""
Company service for business logic operations.
"""

import math
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    """Service class for company operations."""

    @staticmethod
    async def create_company(
        db: AsyncSession,
        company_data: CompanyCreate
    ) -> Company:
        """Create a new company."""
        try:
            company = Company(**company_data.dict())
            db.add(company)
            await db.commit()
            await db.refresh(company)
            return company
        except IntegrityError as e:
            await db.rollback()
            if "companies_code_key" in str(e.orig):
                raise ValueError(f"Company code '{company_data.code}' already exists")
            raise ValueError("Failed to create company due to data integrity error")

    @staticmethod
    async def get_company(
        db: AsyncSession,
        company_id: int
    ) -> Optional[Company]:
        """Get a company by ID."""
        result = await db.execute(
            select(Company).where(Company.id == company_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_company_by_code(
        db: AsyncSession,
        code: str
    ) -> Optional[Company]:
        """Get a company by code."""
        result = await db.execute(
            select(Company).where(Company.code == code.upper())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_companies(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        active_only: bool = False
    ) -> Tuple[List[Company], int]:
        """Get companies with pagination and optional filtering."""
        query = select(Company)
        count_query = select(func.count(Company.id))

        conditions = []
        if search:
            search_filter = f"%{search}%"
            conditions.append(
                Company.name.ilike(search_filter) |
                Company.legal_name.ilike(search_filter) |
                Company.code.ilike(search_filter)
            )
        
        if active_only:
            conditions.append(Company.is_active == True)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get companies with pagination
        query = query.order_by(Company.name).offset(skip).limit(limit)
        result = await db.execute(query)
        companies = result.scalars().all()

        return companies, total

    @staticmethod
    async def update_company(
        db: AsyncSession,
        company_id: int,
        company_data: CompanyUpdate
    ) -> Optional[Company]:
        """Update a company."""
        company = await CompanyService.get_company(db, company_id)
        if not company:
            return None

        try:
            update_data = company_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(company, field, value)
            
            await db.commit()
            await db.refresh(company)
            return company
        except IntegrityError as e:
            await db.rollback()
            if "companies_code_key" in str(e.orig):
                raise ValueError(f"Company code '{company_data.code}' already exists")
            raise ValueError("Failed to update company due to data integrity error")

    @staticmethod
    async def update_company_with_changes(
        db: AsyncSession,
        company_id: int,
        company_data: CompanyUpdate
    ) -> Optional[Tuple[Company, Dict[str, Any], Dict[str, Any], Dict[str, Any]]]:
        """Update a company and return before/after data and changes."""
        company = await CompanyService.get_company(db, company_id)
        if not company:
            return None
        
        # Capture before data
        before_data = {
            "id": company.id,
            "name": company.name,
            "legal_name": company.legal_name,
            "code": company.code,
            "is_active": company.is_active,
            "updated_at": company.updated_at.isoformat() if company.updated_at else None
        }
        
        try:
            update_data = company_data.dict(exclude_unset=True)
            changes = {}
            
            for field, value in update_data.items():
                old_value = getattr(company, field)
                if old_value != value:
                    changes[field] = {"from": old_value, "to": value}
                    setattr(company, field, value)
            
            await db.commit()
            await db.refresh(company)
            
            # Capture after data
            after_data = {
                "id": company.id,
                "name": company.name,
                "legal_name": company.legal_name,
                "code": company.code,
                "is_active": company.is_active,
                "updated_at": company.updated_at.isoformat() if company.updated_at else None
            }
            
            return company, before_data, after_data, changes
            
        except IntegrityError as e:
            await db.rollback()
            if "companies_code_key" in str(e.orig):
                raise ValueError(f"Company code '{company_data.code}' already exists")
            raise ValueError("Failed to update company due to data integrity error")

    @staticmethod
    async def delete_company(
        db: AsyncSession,
        company_id: int
    ) -> bool:
        """Delete a company (soft delete by setting is_active to False)."""
        company = await CompanyService.get_company(db, company_id)
        if not company:
            return False

        company.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def activate_company(
        db: AsyncSession,
        company_id: int
    ) -> Optional[Company]:
        """Activate a company (set is_active to True)."""
        company = await CompanyService.get_company(db, company_id)
        if not company:
            return None

        company.is_active = True
        await db.commit()
        await db.refresh(company)
        return company

    @staticmethod
    async def deactivate_company(
        db: AsyncSession,
        company_id: int
    ) -> Optional[Company]:
        """Deactivate a company (set is_active to False)."""
        company = await CompanyService.get_company(db, company_id)
        if not company:
            return None

        company.is_active = False
        await db.commit()
        await db.refresh(company)
        return company