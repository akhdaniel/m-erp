"""
Account management services for accounting operations.

Provides business logic for chart of accounts, account hierarchies,
and account-related operations with validation and integration.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from accounting_module.models.account import Account, AccountType, AccountSubType, AccountStatus
from accounting_module.services.base_service import BaseService, ServiceError, ValidationError, NotFoundError

import logging
logger = logging.getLogger(__name__)

class AccountService(BaseService):
    """
    Account Service for managing chart of accounts.
    
    Handles account creation, updates, validation, and account lifecycle management.
    """
    
    def create_account(self, code: str, name: str, account_type: AccountType,
                      account_subtype: AccountSubType, **kwargs) -> Account:
        """Create a new account."""
        # Validate account type and subtype compatibility
        if not self._validate_account_type_subtype(account_type, account_subtype):
            raise ValidationError(f"Account subtype '{account_subtype}' is not valid for account type '{account_type}'")
        
        # Validate account code uniqueness
        existing = self.db.query(Account).filter(
            and_(
                Account.code == code,
                Account.company_id == self.company_id
            )
        ).first()
        
        if existing:
            raise ValidationError(f"Account code '{code}' already exists")
        
        # Validate parent account if specified
        parent_account_id = kwargs.get('parent_account_id')
        if parent_account_id:
            parent = self.get_by_id_or_raise(Account, parent_account_id)
            if not parent.is_active:
                raise ValidationError("Parent account must be active")
        
        account_data = {
            'code': code,
            'name': name,
            'account_type': account_type,
            'account_subtype': account_subtype,
            **kwargs
        }
        
        account = self.create(Account, account_data)
        return account
    
    def update_account(self, account_id: int, **kwargs) -> Account:
        """Update account information."""
        account = self.get_by_id_or_raise(Account, account_id)
        
        # Validate account type and subtype if both are being updated
        if 'account_type' in kwargs and 'account_subtype' in kwargs:
            account_type = kwargs['account_type']
            account_subtype = kwargs['account_subtype']
            if not self._validate_account_type_subtype(account_type, account_subtype):
                raise ValidationError(f"Account subtype '{account_subtype}' is not valid for account type '{account_type}'")
        # Validate account subtype if only subtype is being updated
        elif 'account_subtype' in kwargs:
            account_type = account.account_type
            account_subtype = kwargs['account_subtype']
            if not self._validate_account_type_subtype(account_type, account_subtype):
                raise ValidationError(f"Account subtype '{account_subtype}' is not valid for account type '{account_type}'")
        # Validate account type if only type is being updated
        elif 'account_type' in kwargs:
            account_type = kwargs['account_type']
            account_subtype = account.account_subtype
            if not self._validate_account_type_subtype(account_type, account_subtype):
                raise ValidationError(f"Account subtype '{account_subtype}' is not valid for account type '{account_type}'")
        
        # Validate parent account if specified
        if 'parent_account_id' in kwargs and kwargs['parent_account_id']:
            parent = self.get_by_id_or_raise(Account, kwargs['parent_account_id'])
            if not parent.is_active:
                raise ValidationError("Parent account must be active")
        
        return self.update(account, kwargs)
    
    def get_accounts_by_type(self, account_type: AccountType, 
                           active_only: bool = True) -> List[Account]:
        """Get accounts by account type."""
        query = self.db.query(Account).filter(Account.account_type == account_type)
        query = self._apply_company_filter(query, Account)
        
        if active_only:
            query = query.filter(Account.status == AccountStatus.ACTIVE)
        
        query = query.order_by(Account.code)
        return query.all()
    
    def search_accounts(self, search_term: str, 
                       account_type: AccountType = None,
                       status: AccountStatus = None,
                       limit: int = 50) -> List[Account]:
        """Search accounts by various criteria."""
        search_fields = ['code', 'name', 'description']
        query = self.db.query(Account)
        
        # Apply text search
        search_conditions = []
        for field in search_fields:
            if hasattr(Account, field):
                field_attr = getattr(Account, field)
                search_conditions.append(field_attr.ilike(f"%{search_term}%"))
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        # Apply filters
        if account_type:
            query = query.filter(Account.account_type == account_type)
        if status:
            query = query.filter(Account.status == status)
        
        query = self._apply_company_filter(query, Account)
        query = query.order_by(Account.code)
        
        return query.limit(limit).all()
    
    def get_account_hierarchy(self, root_account_id: int = None) -> List[Dict[str, Any]]:
        """Get hierarchical account structure."""
        if root_account_id:
            accounts = self._get_child_accounts(root_account_id)
        else:
            # Get root-level accounts (no parent)
            query = self.db.query(Account).filter(Account.parent_account_id.is_(None))
            query = self._apply_company_filter(query, Account)
            query = query.filter(Account.status == AccountStatus.ACTIVE)
            query = query.order_by(Account.code)
            accounts = query.all()
        
        hierarchy = []
        for account in accounts:
            account_dict = account.to_dict()
            account_dict['children'] = self.get_account_hierarchy(account.id)
            hierarchy.append(account_dict)
        
        return hierarchy
    
    def _get_child_accounts(self, parent_id: int) -> List[Account]:
        """Get child accounts of a parent account."""
        query = self.db.query(Account).filter(Account.parent_account_id == parent_id)
        query = self._apply_company_filter(query, Account)
        query = query.filter(Account.status == AccountStatus.ACTIVE)
        query = query.order_by(Account.code)
        return query.all()
    
    def close_account(self, account_id: int) -> Account:
        """Close an account (set status to closed)."""
        account = self.get_by_id_or_raise(Account, account_id)
        
        # Check if account has a zero balance
        if Decimal(str(account.current_balance)) != 0:
            raise ValidationError("Cannot close account with non-zero balance")
        
        update_data = {
            'status': AccountStatus.CLOSED,
            'is_active': False
        }
        
        return self.update(account, update_data)
    
    def get_account_statistics(self) -> Dict[str, Any]:
        """Get account statistics for dashboard."""
        # Get total account count
        total_accounts = self.count_all(Account, active_only=False)
        
        # Get active account count
        active_accounts = self.count_all(Account, active_only=True)
        
        # Get account counts by type
        account_type_counts = {}
        for account_type in AccountType:
            count = self.db.query(func.count(Account.id)).filter(
                and_(
                    Account.account_type == account_type,
                    Account.company_id == self.company_id,
                    Account.is_active == True
                )
            ).scalar()
            account_type_counts[account_type.value] = count
        
        return {
            "total": total_accounts,
            "active": active_accounts,
            "by_type": account_type_counts
        }
    
    def _validate_account_type_subtype(self, account_type: AccountType, 
                                     account_subtype: AccountSubType) -> bool:
        """Validate that account type and subtype are compatible."""
        type_subtype_mapping = {
            AccountType.ASSET: [AccountSubType.CURRENT_ASSET, AccountSubType.FIXED_ASSET, 
                               AccountSubType.INTANGIBLE_ASSET, AccountSubType.OTHER_ASSET],
            AccountType.LIABILITY: [AccountSubType.CURRENT_LIABILITY, AccountSubType.LONG_TERM_LIABILITY, 
                                   AccountSubType.OTHER_LIABILITY],
            AccountType.EQUITY: [AccountSubType.OWNER_EQUITY, AccountSubType.RETAINED_EARNINGS, 
                                AccountSubType.OTHER_EQUITY],
            AccountType.REVENUE: [AccountSubType.OPERATING_REVENUE, AccountSubType.NON_OPERATING_REVENUE, 
                                 AccountSubType.OTHER_REVENUE],
            AccountType.EXPENSE: [AccountSubType.OPERATING_EXPENSE, AccountSubType.COST_OF_SALES, 
                                 AccountSubType.TAX_EXPENSE, AccountSubType.OTHER_EXPENSE]
        }
        
        return account_subtype in type_subtype_mapping.get(account_type, [])

class AccountHierarchyService(BaseService):
    """
    Account Hierarchy Service for managing reporting hierarchies.
    
    Handles creation and management of account reporting hierarchies
    for different financial reporting purposes.
    """
    
    def create_hierarchy(self, code: str, name: str, 
                        parent_hierarchy_id: int = None, **kwargs) -> 'AccountHierarchy':
        """Create a new account hierarchy."""
        from accounting_module.models.account import AccountHierarchy
        
        # Validate parent hierarchy if specified
        if parent_hierarchy_id:
            parent = self.get_by_id_or_raise(AccountHierarchy, parent_hierarchy_id)
            if not parent.is_active:
                raise ValidationError("Parent hierarchy must be active")
        
        # Check for duplicate code within company
        existing = self.db.query(AccountHierarchy).filter(
            and_(
                AccountHierarchy.code == code,
                AccountHierarchy.company_id == self.company_id
            )
        ).first()
        
        if existing:
            raise ValidationError(f"Hierarchy code '{code}' already exists")
        
        hierarchy_data = {
            'code': code,
            'name': name,
            'parent_hierarchy_id': parent_hierarchy_id,
            **kwargs
        }
        
        hierarchy = self.create(AccountHierarchy, hierarchy_data)
        return hierarchy
    
    def get_hierarchy_tree(self, root_id: int = None) -> List[Dict[str, Any]]:
        """Get hierarchical structure of account hierarchies."""
        from accounting_module.models.account import AccountHierarchy
        
        if root_id:
            hierarchies = self._get_child_hierarchies(root_id)
        else:
            # Get root-level hierarchies (no parent)
            query = self.db.query(AccountHierarchy).filter(AccountHierarchy.parent_hierarchy_id.is_(None))
            query = self._apply_company_filter(query, AccountHierarchy)
            query = query.filter(AccountHierarchy.is_active == True)
            query = query.order_by(AccountHierarchy.display_order, AccountHierarchy.name)
            hierarchies = query.all()
        
        tree = []
        for hierarchy in hierarchies:
            hierarchy_dict = hierarchy.to_dict()
            hierarchy_dict['children'] = self.get_hierarchy_tree(hierarchy.id)
            tree.append(hierarchy_dict)
        
        return tree
    
    def _get_child_hierarchies(self, parent_id: int) -> List['AccountHierarchy']:
        """Get child hierarchies of a parent hierarchy."""
        from accounting_module.models.account import AccountHierarchy
        
        query = self.db.query(AccountHierarchy).filter(AccountHierarchy.parent_hierarchy_id == parent_id)
        query = self._apply_company_filter(query, AccountHierarchy)
        query = query.filter(AccountHierarchy.is_active == True)
        query = query.order_by(AccountHierarchy.display_order, AccountHierarchy.name)
        return query.all()