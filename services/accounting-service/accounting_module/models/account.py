"""
Account models for accounting management including chart of accounts,
account types, and account hierarchies.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from accounting_module.framework.base import CompanyBusinessObject

class AccountType(str, enum.Enum):
    """Account type enumeration"""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

class AccountSubType(str, enum.Enum):
    """Account subtype enumeration"""
    # Asset subtypes
    CURRENT_ASSET = "current_asset"
    FIXED_ASSET = "fixed_asset"
    INTANGIBLE_ASSET = "intangible_asset"
    OTHER_ASSET = "other_asset"
    
    # Liability subtypes
    CURRENT_LIABILITY = "current_liability"
    LONG_TERM_LIABILITY = "long_term_liability"
    OTHER_LIABILITY = "other_liability"
    
    # Equity subtypes
    OWNER_EQUITY = "owner_equity"
    RETAINED_EARNINGS = "retained_earnings"
    OTHER_EQUITY = "other_equity"
    
    # Revenue subtypes
    OPERATING_REVENUE = "operating_revenue"
    NON_OPERATING_REVENUE = "non_operating_revenue"
    OTHER_REVENUE = "other_revenue"
    
    # Expense subtypes
    OPERATING_EXPENSE = "operating_expense"
    COST_OF_SALES = "cost_of_sales"
    TAX_EXPENSE = "tax_expense"
    OTHER_EXPENSE = "other_expense"

class AccountStatus(str, enum.Enum):
    """Account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"

class Account(CompanyBusinessObject):
    """
    Account model representing items in the chart of accounts.
    
    Comprehensive account information including identification,
    categorization, and accounting settings.
    """
    
    __tablename__ = "accounts"
    
    # Basic account information
    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    account_type = Column(Enum(AccountType), nullable=False, index=True)
    account_subtype = Column(Enum(AccountSubType), nullable=False, index=True)
    
    # Account hierarchy
    parent_account_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Account settings
    is_contra = Column(Boolean, nullable=False, default=False)
    allow_manual_journal_entries = Column(Boolean, nullable=False, default=True)
    is_reconciled = Column(Boolean, nullable=False, default=False)
    
    # Currency and balance settings
    currency_code = Column(String(3), nullable=False, default="USD")
    opening_balance = Column(Numeric(15, 2), nullable=False, default=0)
    current_balance = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Status and control
    status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE, index=True)
    is_system_account = Column(Boolean, nullable=False, default=False)
    
    # Tax and reporting settings
    tax_code = Column(String(50), nullable=True)
    is_tax_account = Column(Boolean, nullable=False, default=False)
    
    # Bank account information (if applicable)
    is_bank_account = Column(Boolean, nullable=False, default=False)
    bank_name = Column(String(255), nullable=True)
    bank_account_number = Column(String(100), nullable=True)
    bank_routing_number = Column(String(50), nullable=True)
    
    # Relationships
    # parent_account = relationship("Account", remote_side=[id], back_populates="child_accounts")
    # child_accounts = relationship("Account", back_populates="parent_account")
    # journal_entries = relationship("JournalEntryLine", back_populates="account")
    
    def __str__(self):
        """String representation of account."""
        return f"{self.code} - {self.name}"
    
    def __repr__(self):
        """Detailed representation of account."""
        return (
            f"Account(id={self.id}, code='{self.code}', name='{self.name}', "
            f"type='{self.account_type.value}', subtype='{self.account_subtype.value}')"
        )
    
    @property
    def display_name(self) -> str:
        """Get display name with code."""
        return f"{self.code} - {self.name}"
    
    @property
    def is_debit_increased(self) -> bool:
        """Check if account balance increases with debit entries."""
        return self.account_type in [AccountType.ASSET, AccountType.EXPENSE]
    
    @property
    def is_credit_increased(self) -> bool:
        """Check if account balance increases with credit entries."""
        return self.account_type in [AccountType.LIABILITY, AccountType.EQUITY, AccountType.REVENUE]
    
    @property
    def is_balance_sheet_account(self) -> bool:
        """Check if this is a balance sheet account (asset, liability, equity)."""
        return self.account_type in [AccountType.ASSET, AccountType.LIABILITY, AccountType.EQUITY]
    
    @property
    def is_income_statement_account(self) -> bool:
        """Check if this is an income statement account (revenue, expense)."""
        return self.account_type in [AccountType.REVENUE, AccountType.EXPENSE]
    
    def validate_account_type_subtype_match(self) -> bool:
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
        
        return self.account_subtype in type_subtype_mapping.get(self.account_type, [])
    
    def calculate_balance_change(self, debit_amount: Decimal, credit_amount: Decimal) -> Decimal:
        """Calculate the change in account balance from a journal entry."""
        if self.is_debit_increased:
            return debit_amount - credit_amount
        else:
            return credit_amount - debit_amount
    
    def update_balance(self, debit_amount: Decimal, credit_amount: Decimal) -> None:
        """Update account balance based on journal entry amounts."""
        balance_change = self.calculate_balance_change(debit_amount, credit_amount)
        self.current_balance = Decimal(str(self.current_balance)) + balance_change

class AccountHierarchy(CompanyBusinessObject):
    """
    Account Hierarchy model for organizing accounts in reporting structures.
    
    Provides hierarchical structure for financial reporting beyond the
    simple parent-child relationships in Account model.
    """
    
    __tablename__ = "account_hierarchies"
    
    # Hierarchy information
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    
    # Hierarchy structure
    parent_hierarchy_id = Column(
        Integer,
        ForeignKey("account_hierarchies.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Display and organization
    display_order = Column(Integer, nullable=False, default=0)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    # parent_hierarchy = relationship("AccountHierarchy", remote_side=[id], back_populates="child_hierarchies")
    # child_hierarchies = relationship("AccountHierarchy", back_populates="parent_hierarchy")
    # hierarchy_accounts = relationship("AccountHierarchyMapping", back_populates="hierarchy")
    
    def __str__(self):
        """String representation of account hierarchy."""
        return f"{self.name} ({self.code})"
    
    def __repr__(self):
        """Detailed representation of account hierarchy."""
        return (
            f"AccountHierarchy(id={self.id}, name='{self.name}', code='{self.code}', "
            f"parent_id={self.parent_hierarchy_id}, active={self.is_active})"
        )

class AccountHierarchyMapping(CompanyBusinessObject):
    """
    Mapping between accounts and reporting hierarchies.
    
    Allows accounts to be mapped to multiple reporting hierarchies
    for different financial reporting purposes.
    """
    
    __tablename__ = "account_hierarchy_mappings"
    
    # References
    account_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    hierarchy_id = Column(
        Integer,
        ForeignKey("account_hierarchies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Mapping properties
    display_order = Column(Integer, nullable=False, default=0)
    is_primary = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    # account = relationship("Account", back_populates="hierarchy_mappings")
    # hierarchy = relationship("AccountHierarchy", back_populates="hierarchy_accounts")
    
    def __str__(self):
        """String representation of account hierarchy mapping."""
        return f"Mapping Account {self.account_id} to Hierarchy {self.hierarchy_id}"
    
    def __repr__(self):
        """Detailed representation of account hierarchy mapping."""
        return (
            f"AccountHierarchyMapping(id={self.id}, account_id={self.account_id}, "
            f"hierarchy_id={self.hierarchy_id}, primary={self.is_primary})"
        )