"""
Framework-based Company service using Business Object Framework.

This service leverages the Business Object Framework to provide standardized
CRUD operations with automatic audit logging, event publishing, and
standardized error handling.
"""

from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.framework.services import BusinessObjectService
from app.services.messaging_service import get_messaging_service


class CompanyFrameworkService(BusinessObjectService[Company, CompanyCreate, CompanyUpdate]):
    """
    Framework-based Company service with standardized CRUD operations.
    
    Provides:
    - Automatic audit logging for all operations
    - Event publishing for company lifecycle events
    - Standardized error handling
    - Built-in search and filtering capabilities
    """
    
    def __init__(self):
        """Initialize the Company service with framework capabilities."""
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
        
        super().__init__(Company, messaging_service)
    
    # Custom business logic methods
    
    async def get_company_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> Optional[Company]:
        """
        Get a company by code.
        
        Args:
            db: Database session
            code: Company code
            
        Returns:
            Company object or None if not found
        """
        filters = {'code': code}
        companies, _ = await self.get_list(
            db=db,
            limit=1,
            filters=filters
        )
        return companies[0] if companies else None
    
    async def search_companies(
        self,
        db: AsyncSession,
        search_term: str,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Company], int]:
        """
        Advanced search for companies with multiple criteria.
        
        Args:
            db: Database session
            search_term: Search term for name, legal name, or code
            active_only: Return only active companies
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (companies list, total count)
        """
        filters = {}
        
        if active_only:
            filters['is_active'] = True
        
        return await self.get_list(
            db=db,
            skip=skip,
            limit=limit,
            search=search_term,
            filters=filters
        )
    
    async def get_active_companies(
        self,
        db: AsyncSession
    ) -> List[Company]:
        """
        Get all active companies.
        
        Args:
            db: Database session
            
        Returns:
            List of active companies
        """
        companies, _ = await self.get_list(
            db=db,
            filters={'is_active': True},
            limit=1000  # Get all active companies
        )
        
        return companies
    
    async def activate_company(
        self,
        db: AsyncSession,
        company_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Company]:
        """
        Activate a company (set is_active to True).
        
        Args:
            db: Database session
            company_id: Company ID
            user_id: ID of user performing the action
            
        Returns:
            Updated company or None if not found
        """
        return await self.activate(
            db=db,
            obj_id=company_id,
            user_id=user_id
        )
    
    async def deactivate_company(
        self,
        db: AsyncSession,
        company_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Company]:
        """
        Deactivate a company (set is_active to False).
        
        Args:
            db: Database session
            company_id: Company ID
            user_id: ID of user performing the action
            
        Returns:
            Updated company or None if not found
        """
        return await self.deactivate(
            db=db,
            obj_id=company_id,
            user_id=user_id
        )
    
    async def get_company_statistics(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get company statistics.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with company statistics
        """
        # Use framework's get_list method with different filters
        all_companies, total = await self.get_list(
            db=db,
            limit=10000  # Get all companies for statistics
        )
        
        active_companies, active_total = await self.get_list(
            db=db,
            filters={'is_active': True},
            limit=10000
        )
        
        # Count companies by currency
        currency_stats = {}
        for company in all_companies:
            currency = company.currency or 'USD'
            currency_stats[currency] = currency_stats.get(currency, 0) + 1
        
        return {
            'total_companies': total,
            'active_companies': active_total,
            'inactive_companies': total - active_total,
            'currencies': currency_stats,
            'last_updated': None  # Could be enhanced to track last update
        }
    
    async def validate_company_code(
        self,
        db: AsyncSession,
        code: str,
        exclude_company_id: Optional[int] = None
    ) -> bool:
        """
        Validate that a company code is unique.
        
        Args:
            db: Database session
            code: Company code to validate
            exclude_company_id: Company ID to exclude from check (for updates)
            
        Returns:
            True if code is available, False if already exists
        """
        existing_company = await self.get_company_by_code(db, code)
        
        if not existing_company:
            return True
        
        # If we're excluding a specific company (for updates), check if it's the same company
        if exclude_company_id and existing_company.id == exclude_company_id:
            return True
        
        return False


# Create a singleton instance for use in API endpoints
company_framework_service = CompanyFrameworkService()