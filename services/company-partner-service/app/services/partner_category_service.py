"""
Partner Category service using Business Object Framework.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.framework.services import BusinessObjectService
from app.models.partner_category import PartnerCategory
from app.schemas.partner_category import (
    PartnerCategoryCreate, 
    PartnerCategoryUpdate, 
    PartnerCategoryResponse,
    PartnerCategoryTreeResponse,
    PartnerCategoryStatsResponse
)


class PartnerCategoryService(BusinessObjectService[PartnerCategory, PartnerCategoryCreate, PartnerCategoryUpdate]):
    """
    Service for managing partner categories using the Business Object Framework.
    
    Provides CRUD operations plus category-specific functionality like
    hierarchical organization, statistics, and validation.
    """
    
    def __init__(self):
        super().__init__(PartnerCategory)
    
    def get_category_tree(self, db: Session, company_id: int) -> List[PartnerCategoryTreeResponse]:
        """
        Get hierarchical tree of categories for a company.
        
        Returns categories organized in parent-child relationships
        for tree display in UI components.
        """
        # Get all root categories (no parent)
        root_categories = db.query(PartnerCategory).filter(
            PartnerCategory.company_id == company_id,
            PartnerCategory.parent_category_id == None,
            PartnerCategory.is_active == True
        ).order_by(PartnerCategory.name).all()
        
        tree = []
        for root in root_categories:
            tree_node = self._build_category_tree_node(root)
            tree.append(tree_node)
        
        return tree
    
    def _build_category_tree_node(self, category: PartnerCategory) -> PartnerCategoryTreeResponse:
        """Build a tree node with children recursively."""
        children = []
        for child in category.child_categories:
            if child.is_active:
                children.append(self._build_category_tree_node(child))
        
        return PartnerCategoryTreeResponse(
            id=category.id,
            name=category.name,
            code=category.code,
            description=category.description,
            color=category.color,
            is_active=category.is_active,
            is_default=category.is_default,
            partner_count=category.get_partner_count(),
            children=children
        )
    
    def get_statistics(self, db: Session, company_id: int) -> PartnerCategoryStatsResponse:
        """Get category statistics for dashboard and reporting."""
        # Basic counts
        total_query = db.query(func.count(PartnerCategory.id)).filter(
            PartnerCategory.company_id == company_id
        )
        active_query = total_query.filter(PartnerCategory.is_active == True)
        
        total_categories = total_query.scalar()
        active_categories = active_query.scalar()
        
        # Categories with partners
        categories_with_partners = db.query(func.count(PartnerCategory.id.distinct())).join(
            PartnerCategory.partners
        ).filter(
            PartnerCategory.company_id == company_id,
            PartnerCategory.is_active == True
        ).scalar()
        
        # Top categories by partner count
        from app.models.partner import Partner
        top_categories_query = db.query(
            PartnerCategory.id,
            PartnerCategory.name,
            PartnerCategory.code,
            func.count(Partner.id).label('partner_count')
        ).outerjoin(Partner).filter(
            PartnerCategory.company_id == company_id,
            PartnerCategory.is_active == True
        ).group_by(
            PartnerCategory.id, PartnerCategory.name, PartnerCategory.code
        ).order_by(desc('partner_count')).limit(10)
        
        top_categories = [
            {
                'id': result.id,
                'name': result.name,
                'code': result.code,
                'partner_count': result.partner_count
            }
            for result in top_categories_query.all()
        ]
        
        return PartnerCategoryStatsResponse(
            total_categories=total_categories,
            active_categories=active_categories,
            categories_with_partners=categories_with_partners,
            top_categories=top_categories
        )
    
    def create_default_categories(self, db: Session, company_id: int) -> List[PartnerCategory]:
        """
        Create default partner categories for a new company.
        
        Creates standard categories that most businesses need.
        """
        default_categories = [
            {
                'name': 'Customers',
                'code': 'CUSTOMERS',
                'description': 'All customer partners',
                'color': '#4CAF50',
                'is_default': True
            },
            {
                'name': 'Suppliers',
                'code': 'SUPPLIERS', 
                'description': 'All supplier partners',
                'color': '#2196F3',
                'is_default': True
            },
            {
                'name': 'Vendors',
                'code': 'VENDORS',
                'description': 'All vendor partners',
                'color': '#FF9800',
                'is_default': True
            },
            {
                'name': 'Strategic Partners',
                'code': 'STRATEGIC',
                'description': 'Strategic business partners',
                'color': '#9C27B0',
                'is_default': False
            }
        ]
        
        created_categories = []
        for category_data in default_categories:
            # Check if category already exists
            existing = db.query(PartnerCategory).filter(
                PartnerCategory.company_id == company_id,
                PartnerCategory.code == category_data['code']
            ).first()
            
            if not existing:
                category = PartnerCategory(
                    company_id=company_id,
                    **category_data
                )
                db.add(category)
                created_categories.append(category)
        
        db.commit()
        return created_categories
    
    def validate_hierarchy(self, db: Session, category_id: int, parent_category_id: int) -> bool:
        """
        Validate that setting parent_category_id won't create circular reference.
        
        Returns True if the hierarchy is valid, False if it would create a cycle.
        """
        if category_id == parent_category_id:
            return False
        
        # Get the proposed parent category
        parent = db.query(PartnerCategory).filter(PartnerCategory.id == parent_category_id).first()
        if not parent:
            return False
        
        # Check if the category would become an ancestor of itself
        current = parent
        while current and current.parent_category_id:
            if current.parent_category_id == category_id:
                return False
            current = current.parent_category if current.parent_category else None
        
        return True
    
    def move_partners_to_category(
        self, 
        db: Session, 
        from_category_id: int, 
        to_category_id: int,
        company_id: int
    ) -> int:
        """
        Move all partners from one category to another.
        
        Returns the number of partners moved.
        """
        from app.models.partner import Partner
        
        # Validate both categories exist and belong to the company
        from_category = db.query(PartnerCategory).filter(
            PartnerCategory.id == from_category_id,
            PartnerCategory.company_id == company_id
        ).first()
        
        to_category = db.query(PartnerCategory).filter(
            PartnerCategory.id == to_category_id,
            PartnerCategory.company_id == company_id
        ).first()
        
        if not from_category or not to_category:
            raise ValueError("Invalid category IDs")
        
        # Update all partners
        updated_count = db.query(Partner).filter(
            Partner.category_id == from_category_id,
            Partner.company_id == company_id
        ).update({'category_id': to_category_id})
        
        db.commit()
        return updated_count
    
    def get_category_usage_report(self, db: Session, company_id: int) -> Dict[str, Any]:
        """Generate detailed category usage report."""
        from app.models.partner import Partner
        
        report = db.query(
            PartnerCategory.id,
            PartnerCategory.name,
            PartnerCategory.code,
            PartnerCategory.full_path,
            func.count(Partner.id).label('total_partners'),
            func.count(func.nullif(Partner.is_active, False)).label('active_partners')
        ).outerjoin(Partner).filter(
            PartnerCategory.company_id == company_id
        ).group_by(
            PartnerCategory.id, PartnerCategory.name, PartnerCategory.code
        ).order_by(PartnerCategory.name).all()
        
        return {
            'categories': [
                {
                    'id': r.id,
                    'name': r.name,
                    'code': r.code,
                    'full_path': r.full_path,
                    'total_partners': r.total_partners,
                    'active_partners': r.active_partners
                }
                for r in report
            ],
            'summary': {
                'total_categories': len(report),
                'total_partners': sum(r.total_partners for r in report),
                'active_partners': sum(r.active_partners for r in report)
            }
        }