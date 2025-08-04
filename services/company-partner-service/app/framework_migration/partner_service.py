"""
Framework-based Partner service using Business Object Framework.

This service demonstrates how to migrate existing Partner service logic to use
the Business Object Framework while maintaining all existing functionality.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_

from app.models.partner import Partner
from app.framework.services import CompanyBusinessObjectService
from app.framework_migration.partner_schemas import PartnerFrameworkCreate, PartnerFrameworkUpdate


class PartnerFrameworkService(CompanyBusinessObjectService[Partner]):
    """Framework-based Partner service with enhanced capabilities."""
    
    def __init__(self, db: AsyncSession):
        """Initialize Partner service with framework support."""
        super().__init__(db, Partner)
    
    # === Enhanced Framework Operations ===
    
    async def create_partner(self, partner_data: PartnerFrameworkCreate) -> Partner:
        """Create a new partner using framework create method."""
        return await self.create(partner_data.dict())
    
    async def get_partner(self, partner_id: int, company_id: Optional[int] = None) -> Optional[Partner]:
        """Get partner by ID with optional company validation."""
        if company_id:
            return await self.get_by_id(partner_id, {"company_id": company_id})
        return await self.get_by_id(partner_id)
    
    async def update_partner(self, partner_id: int, partner_data: PartnerFrameworkUpdate, company_id: Optional[int] = None) -> Optional[Partner]:
        """Update partner using framework update method."""
        filters = {"company_id": company_id} if company_id else {}
        return await self.update(partner_id, partner_data.dict(exclude_unset=True), filters)
    
    async def delete_partner(self, partner_id: int, company_id: Optional[int] = None) -> bool:
        """Soft delete partner using framework delete method."""
        filters = {"company_id": company_id} if company_id else {}
        return await self.soft_delete(partner_id, filters)
    
    async def activate_partner(self, partner_id: int, company_id: Optional[int] = None) -> Optional[Partner]:
        """Activate partner using framework update method."""
        filters = {"company_id": company_id} if company_id else {}
        return await self.update(partner_id, {"is_active": True}, filters)
    
    async def deactivate_partner(self, partner_id: int, company_id: Optional[int] = None) -> Optional[Partner]:
        """Deactivate partner using framework update method."""
        filters = {"company_id": company_id} if company_id else {}
        return await self.update(partner_id, {"is_active": False}, filters)
    
    # === Business-Specific Methods ===
    
    async def get_partner_by_code(self, company_id: int, code: str) -> Optional[Partner]:
        """Get partner by code within a company."""
        return await self.get_by_filters({"company_id": company_id, "code": code.upper()})
    
    async def get_partners_by_company(
        self,
        company_id: int,
        partner_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Partner]:
        """Get all partners for a specific company with filtering."""
        filters = {"company_id": company_id}
        
        if active_only:
            filters["is_active"] = True
        
        if partner_type:
            # Handle partner type filtering
            if partner_type == "customer":
                filters["is_customer"] = True
            elif partner_type == "supplier":
                filters["is_supplier"] = True
            elif partner_type == "vendor":
                filters["is_vendor"] = True
        
        return await self.get_list(filters=filters)
    
    async def get_partners(
        self,
        company_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        partner_type: Optional[str] = None,
        active_only: bool = True
    ) -> tuple[List[Partner], int]:
        """Get partners with pagination and search using framework methods."""
        
        # Build base filters
        filters = {}
        if company_id:
            filters["company_id"] = company_id
        if active_only:
            filters["is_active"] = True
        
        # Handle partner type filtering
        if partner_type:
            if partner_type == "customer":
                filters["is_customer"] = True
            elif partner_type == "supplier":
                filters["is_supplier"] = True
            elif partner_type == "vendor":
                filters["is_vendor"] = True
        
        # Use framework list method with search
        partners = await self.get_list(
            filters=filters,
            search_fields=["name", "code", "email"] if search else None,
            search_term=search,
            skip=skip,
            limit=limit
        )
        
        # Get total count
        total = await self.count(filters)
        
        return partners, total
    
    async def find_customers(self, company_id: int, active_only: bool = True) -> List[Partner]:
        """Find all customer partners for a company."""
        filters = {"company_id": company_id, "is_customer": True}
        if active_only:
            filters["is_active"] = True
        return await self.get_list(filters=filters)
    
    async def find_suppliers(self, company_id: int, active_only: bool = True) -> List[Partner]:
        """Find all supplier partners for a company."""
        filters = {"company_id": company_id, "is_supplier": True}
        if active_only:
            filters["is_active"] = True
        return await self.get_list(filters=filters)
    
    async def find_vendors(self, company_id: int, active_only: bool = True) -> List[Partner]:
        """Find all vendor partners for a company."""
        filters = {"company_id": company_id, "is_vendor": True}
        if active_only:
            filters["is_active"] = True
        return await self.get_list(filters=filters)
    
    async def bulk_create_partners(self, partners_data: List[PartnerFrameworkCreate]) -> List[Partner]:
        """Bulk create partners using framework bulk operations."""
        return await self.bulk_create([p.dict() for p in partners_data])
    
    async def get_partner_statistics(self, company_id: int) -> Dict[str, Any]:
        """Get partner statistics for a company."""
        
        # Use framework count method for different partner types
        total_partners = await self.count({"company_id": company_id})
        active_partners = await self.count({"company_id": company_id, "is_active": True})
        customers = await self.count({"company_id": company_id, "is_customer": True, "is_active": True})
        suppliers = await self.count({"company_id": company_id, "is_supplier": True, "is_active": True})
        vendors = await self.count({"company_id": company_id, "is_vendor": True, "is_active": True})
        
        return {
            "total_partners": total_partners,
            "active_partners": active_partners,
            "customers": customers,
            "suppliers": suppliers,
            "vendors": vendors,
            "inactive_partners": total_partners - active_partners
        }


# Factory function for creating Partner service instances
def create_partner_service(db: AsyncSession) -> PartnerFrameworkService:
    """Factory function to create Partner service instance."""
    return PartnerFrameworkService(db)