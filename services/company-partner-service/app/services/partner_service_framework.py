"""
Framework-based Partner service using Business Object Framework.

This service leverages the Business Object Framework to provide standardized
CRUD operations with automatic audit logging, event publishing, and
multi-company data isolation.
"""

from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func

from app.models.partner import Partner
from app.schemas.partner import PartnerCreate, PartnerUpdate
from app.framework.services import CompanyBusinessObjectService
from app.services.messaging_service import get_messaging_service


class PartnerFrameworkService(CompanyBusinessObjectService[Partner, PartnerCreate, PartnerUpdate]):
    """
    Framework-based Partner service with standardized CRUD operations.
    
    Provides:
    - Automatic audit logging for all operations
    - Event publishing for partner lifecycle events
    - Multi-company data isolation
    - Standardized error handling
    - Built-in search and filtering capabilities
    """
    
    def __init__(self):
        """Initialize the Partner service with framework capabilities."""
        messaging_service = None
        try:
            # Get messaging service asynchronously when needed
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we'll get it later
                pass
            else:
                messaging_service = loop.run_until_complete(get_messaging_service())
        except Exception:
            # Messaging service is optional for framework operations
            pass
        
        super().__init__(Partner, messaging_service)
    
    # Custom business logic methods
    
    async def get_partner_by_code(
        self,
        db: AsyncSession,
        company_id: int,
        code: str
    ) -> Optional[Partner]:
        """
        Get a partner by code within a company.
        
        Args:
            db: Database session
            company_id: Company ID for data isolation
            code: Partner code
            
        Returns:
            Partner object or None if not found
        """
        filters = {'code': code}
        partners, _ = await self.get_list(
            db=db,
            company_id=company_id,
            limit=1,
            filters=filters
        )
        return partners[0] if partners else None
    
    async def search_partners(
        self,
        db: AsyncSession,
        company_id: int,
        search_term: str,
        partner_type: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Partner], int]:
        """
        Advanced search for partners with multiple criteria.
        
        Args:
            db: Database session
            company_id: Company ID for data isolation
            search_term: Search term for name, code, or email
            partner_type: Filter by partner type (customer, supplier, vendor)
            active_only: Return only active partners
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (partners list, total count)
        """
        filters = {}
        
        if partner_type:
            filters['partner_type'] = partner_type
        
        if active_only:
            filters['is_active'] = True
        
        return await self.get_list(
            db=db,
            company_id=company_id,
            skip=skip,
            limit=limit,
            search=search_term,
            filters=filters
        )
    
    async def get_partners_by_type(
        self,
        db: AsyncSession,
        company_id: int,
        is_customer: Optional[bool] = None,
        is_supplier: Optional[bool] = None,
        is_vendor: Optional[bool] = None,
        active_only: bool = True
    ) -> List[Partner]:
        """
        Get partners filtered by their types (customer, supplier, vendor).
        
        Args:
            db: Database session
            company_id: Company ID for data isolation
            is_customer: Filter by customer status
            is_supplier: Filter by supplier status
            is_vendor: Filter by vendor status
            active_only: Return only active partners
            
        Returns:
            List of matching partners
        """
        filters = {}
        
        if is_customer is not None:
            filters['is_customer'] = is_customer
        
        if is_supplier is not None:
            filters['is_supplier'] = is_supplier
        
        if is_vendor is not None:
            filters['is_vendor'] = is_vendor
        
        if active_only:
            filters['is_active'] = True
        
        partners, _ = await self.get_list(
            db=db,
            company_id=company_id,
            filters=filters,
            limit=1000  # Get all matching partners
        )
        
        return partners
    
    async def activate_partner(
        self,
        db: AsyncSession,
        partner_id: int,
        company_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Partner]:
        """
        Activate a partner (set is_active to True).
        
        Args:
            db: Database session
            partner_id: Partner ID
            company_id: Company ID for data isolation
            user_id: ID of user performing the action
            
        Returns:
            Updated partner or None if not found
        """
        return await self.activate(
            db=db,
            obj_id=partner_id,
            company_id=company_id,
            user_id=user_id
        )
    
    async def deactivate_partner(
        self,
        db: AsyncSession,
        partner_id: int,
        company_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Partner]:
        """
        Deactivate a partner (set is_active to False).
        
        Args:
            db: Database session
            partner_id: Partner ID
            company_id: Company ID for data isolation
            user_id: ID of user performing the action
            
        Returns:
            Updated partner or None if not found
        """
        return await self.deactivate(
            db=db,
            obj_id=partner_id,
            company_id=company_id,
            user_id=user_id
        )
    
    async def get_partner_statistics(
        self,
        db: AsyncSession,
        company_id: int
    ) -> Dict[str, Any]:
        """
        Get partner statistics for a company.
        
        Args:
            db: Database session
            company_id: Company ID for data isolation
            
        Returns:
            Dictionary with partner statistics
        """
        # Use framework's get_list method with different filters
        all_partners, total = await self.get_list(
            db=db,
            company_id=company_id,
            limit=10000  # Get all partners for statistics
        )
        
        active_partners, active_total = await self.get_list(
            db=db,
            company_id=company_id,
            filters={'is_active': True},
            limit=10000
        )
        
        customers, customer_total = await self.get_list(
            db=db,
            company_id=company_id,
            filters={'is_customer': True, 'is_active': True},
            limit=10000
        )
        
        suppliers, supplier_total = await self.get_list(
            db=db,
            company_id=company_id,
            filters={'is_supplier': True, 'is_active': True},
            limit=10000
        )
        
        vendors, vendor_total = await self.get_list(
            db=db,
            company_id=company_id,
            filters={'is_vendor': True, 'is_active': True},
            limit=10000
        )
        
        return {
            'total_partners': total,
            'active_partners': active_total,
            'inactive_partners': total - active_total,
            'customers': customer_total,
            'suppliers': supplier_total,
            'vendors': vendor_total,
            'last_updated': None  # Could be enhanced to track last update
        }


# Create a singleton instance for use in API endpoints
partner_framework_service = PartnerFrameworkService()