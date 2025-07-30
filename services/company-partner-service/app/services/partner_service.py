"""
Partner service for business logic operations.
"""

import math
from typing import Optional, List, Tuple
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.models.partner import Partner
from app.schemas.partner import PartnerCreate, PartnerUpdate


class PartnerService:
    """Service class for partner operations."""

    @staticmethod
    async def create_partner(
        db: AsyncSession,
        partner_data: PartnerCreate
    ) -> Partner:
        """Create a new partner."""
        try:
            partner = Partner(**partner_data.dict())
            db.add(partner)
            await db.commit()
            await db.refresh(partner)
            return partner
        except IntegrityError as e:
            await db.rollback()
            if "partners_company_code_unique" in str(e.orig):
                raise ValueError(f"Partner code '{partner_data.code}' already exists for this company")
            raise ValueError("Failed to create partner due to data integrity error")

    @staticmethod
    async def get_partner(
        db: AsyncSession,
        partner_id: int,
        company_id: Optional[int] = None
    ) -> Optional[Partner]:
        """Get a partner by ID, optionally filtered by company."""
        query = select(Partner).where(Partner.id == partner_id)
        if company_id:
            query = query.where(Partner.company_id == company_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_partner_by_code(
        db: AsyncSession,
        company_id: int,
        code: str
    ) -> Optional[Partner]:
        """Get a partner by code within a company."""
        result = await db.execute(
            select(Partner).where(
                and_(
                    Partner.company_id == company_id,
                    Partner.code == code.upper()
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_partners(
        db: AsyncSession,
        company_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        partner_type: Optional[str] = None,
        active_only: bool = True
    ) -> Tuple[List[Partner], int]:
        """Get partners with pagination and optional filtering."""
        query = select(Partner)
        count_query = select(func.count(Partner.id))

        conditions = []
        
        if company_id:
            conditions.append(Partner.company_id == company_id)

        if search:
            search_filter = f"%{search}%"
            conditions.append(
                Partner.name.ilike(search_filter) |
                Partner.code.ilike(search_filter) |
                Partner.email.ilike(search_filter)
            )
        
        if partner_type:
            if partner_type == "customer":
                conditions.append(Partner.is_customer == True)
            elif partner_type == "supplier":
                conditions.append(Partner.is_supplier == True)
            elif partner_type == "vendor":
                conditions.append(Partner.is_vendor == True)
            else:
                conditions.append(Partner.partner_type == partner_type)
        
        if active_only:
            conditions.append(Partner.is_active == True)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get partners with pagination
        query = query.order_by(Partner.name).offset(skip).limit(limit)
        result = await db.execute(query)
        partners = result.scalars().all()

        return partners, total

    @staticmethod
    async def update_partner(
        db: AsyncSession,
        partner_id: int,
        partner_data: PartnerUpdate,
        company_id: Optional[int] = None
    ) -> Optional[Partner]:
        """Update a partner."""
        partner = await PartnerService.get_partner(db, partner_id, company_id)
        if not partner:
            return None

        try:
            update_data = partner_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(partner, field, value)
            
            await db.commit()
            await db.refresh(partner)
            return partner
        except IntegrityError as e:
            await db.rollback()
            if "partners_company_code_unique" in str(e.orig):
                raise ValueError(f"Partner code '{partner_data.code}' already exists for this company")
            raise ValueError("Failed to update partner due to data integrity error")

    @staticmethod
    async def delete_partner(
        db: AsyncSession,
        partner_id: int,
        company_id: Optional[int] = None
    ) -> bool:
        """Delete a partner (soft delete by setting is_active to False)."""
        partner = await PartnerService.get_partner(db, partner_id, company_id)
        if not partner:
            return False

        partner.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def activate_partner(
        db: AsyncSession,
        partner_id: int,
        company_id: Optional[int] = None
    ) -> Optional[Partner]:
        """Activate a partner (set is_active to True)."""
        partner = await PartnerService.get_partner(db, partner_id, company_id)
        if not partner:
            return None

        partner.is_active = True
        await db.commit()
        await db.refresh(partner)
        return partner

    @staticmethod
    async def deactivate_partner(
        db: AsyncSession,
        partner_id: int,
        company_id: Optional[int] = None
    ) -> Optional[Partner]:
        """Deactivate a partner (set is_active to False)."""
        partner = await PartnerService.get_partner(db, partner_id, company_id)
        if not partner:
            return None

        partner.is_active = False
        await db.commit()
        await db.refresh(partner)
        return partner

    @staticmethod
    async def get_partners_by_company(
        db: AsyncSession,
        company_id: int,
        partner_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Partner]:
        """Get all partners for a specific company."""
        conditions = [Partner.company_id == company_id]
        
        if partner_type:
            if partner_type == "customer":
                conditions.append(Partner.is_customer == True)
            elif partner_type == "supplier":
                conditions.append(Partner.is_supplier == True)
            elif partner_type == "vendor":
                conditions.append(Partner.is_vendor == True)
        
        if active_only:
            conditions.append(Partner.is_active == True)

        query = select(Partner).where(and_(*conditions)).order_by(Partner.name)
        result = await db.execute(query)
        return result.scalars().all()