"""
Journal Entry models for accounting management including journal entries,
journal entry lines, and posting controls.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from accounting_module.framework.base import CompanyBusinessObject
from accounting_module.models.account import Account

class JournalEntryType(str, enum.Enum):
    """Journal entry type enumeration"""
    STANDARD = "standard"
    ADJUSTING = "adjusting"
    CLOSING = "closing"
    REVERSING = "reversing"

class JournalEntryStatus(str, enum.Enum):
    """Journal entry status enumeration"""
    DRAFT = "draft"
    POSTED = "posted"
    CANCELLED = "cancelled"

class JournalEntry(CompanyBusinessObject):
    """
    Journal Entry model representing accounting entries.
    
    Comprehensive journal entry information including header information
    and references to journal entry lines.
    """
    
    __tablename__ = "journal_entries"
    
    # Basic journal entry information
    entry_number = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text)
    reference = Column(String(100), nullable=True, index=True)
    
    # Entry type and status
    entry_type = Column(Enum(JournalEntryType), nullable=False, default=JournalEntryType.STANDARD, index=True)
    status = Column(Enum(JournalEntryStatus), nullable=False, default=JournalEntryStatus.DRAFT, index=True)
    
    # Date information
    entry_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    posting_date = Column(DateTime, nullable=True)
    
    # Amount totals
    total_debit = Column(Numeric(15, 2), nullable=False, default=0)
    total_credit = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Source information
    source_module = Column(String(100), nullable=True)  # e.g., "sales", "purchasing", "inventory"
    source_document_id = Column(String(100), nullable=True)  # e.g., invoice number, PO number
    
    # User and approval information
    created_by_user_id = Column(Integer, nullable=True)
    posted_by_user_id = Column(Integer, nullable=True)
    approved_by_user_id = Column(Integer, nullable=True)
    approval_date = Column(DateTime, nullable=True)
    
    # Relationships
    # journal_entry_lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    
    def __str__(self):
        """String representation of journal entry."""
        return f"JE-{self.entry_number}: {self.description}"
    
    def __repr__(self):
        """Detailed representation of journal entry."""
        return (
            f"JournalEntry(id={self.id}, entry_number='{self.entry_number}', "
            f"date={self.entry_date}, status='{self.status.value}')"
        )
    
    @property
    def is_balanced(self) -> bool:
        """Check if journal entry is balanced (debits equal credits)."""
        return Decimal(str(self.total_debit)) == Decimal(str(self.total_credit))
    
    @property
    def display_name(self) -> str:
        """Get display name with entry number."""
        return f"JE-{self.entry_number}"
    
    def calculate_totals(self) -> tuple[Decimal, Decimal]:
        """Calculate total debit and credit amounts from lines."""
        # In production, would sum from journal_entry_lines
        return Decimal(str(self.total_debit)), Decimal(str(self.total_credit))
    
    def validate_entry(self) -> List[str]:
        """Validate journal entry before posting."""
        errors = []
        
        # Check if entry is balanced
        if not self.is_balanced:
            errors.append("Journal entry is not balanced (debits must equal credits)")
        
        # Check if entry has lines
        # In production, would check journal_entry_lines
        if Decimal(str(self.total_debit)) == 0 and Decimal(str(self.total_credit)) == 0:
            errors.append("Journal entry must have at least one line")
        
        # Check if entry date is valid
        if self.entry_date > datetime.utcnow():
            errors.append("Entry date cannot be in the future")
        
        return errors

class JournalEntryLine(CompanyBusinessObject):
    """
    Journal Entry Line model representing individual account entries.
    
    Individual line items that make up a journal entry, with account
    references, amounts, and descriptions.
    """
    
    __tablename__ = "journal_entry_lines"
    
    # References
    journal_entry_id = Column(
        Integer,
        ForeignKey("journal_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    account_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Amount information
    debit_amount = Column(Numeric(15, 2), nullable=False, default=0)
    credit_amount = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Description and reference
    description = Column(Text)
    reference = Column(String(100), nullable=True)
    
    # Line properties
    line_number = Column(Integer, nullable=False)
    is_posted = Column(Boolean, nullable=False, default=False)
    
    # Tax information
    tax_code = Column(String(50), nullable=True)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Dimension information (for reporting)
    department_id = Column(Integer, nullable=True)
    project_id = Column(Integer, nullable=True)
    cost_center_id = Column(Integer, nullable=True)
    
    # Relationships
    # journal_entry = relationship("JournalEntry", back_populates="journal_entry_lines")
    # account = relationship("Account", back_populates="journal_entries")
    
    def __str__(self):
        """String representation of journal entry line."""
        return f"Line {self.line_number}: {self.account_id} Dr:{self.debit_amount} Cr:{self.credit_amount}"
    
    def __repr__(self):
        """Detailed representation of journal entry line."""
        return (
            f"JournalEntryLine(id={self.id}, entry_id={self.journal_entry_id}, "
            f"account_id={self.account_id}, debit={self.debit_amount}, credit={self.credit_amount})"
        )
    
    @property
    def net_amount(self) -> Decimal:
        """Get net amount (debit - credit)."""
        return Decimal(str(self.debit_amount)) - Decimal(str(self.credit_amount))
    
    def validate_line(self) -> List[str]:
        """Validate journal entry line."""
        errors = []
        
        # Check if both debit and credit are non-zero
        if Decimal(str(self.debit_amount)) != 0 and Decimal(str(self.credit_amount)) != 0:
            errors.append("Line cannot have both debit and credit amounts")
        
        # Check if both debit and credit are zero
        if Decimal(str(self.debit_amount)) == 0 and Decimal(str(self.credit_amount)) == 0:
            errors.append("Line must have either debit or credit amount")
        
        return errors

class ReversingEntry(CompanyBusinessObject):
    """
    Reversing Entry model for automatic reversal of adjusting entries.
    
    Tracks reversing entries that are automatically created to reverse
    adjusting entries at the beginning of the next accounting period.
    """
    
    __tablename__ = "reversing_entries"
    
    # References
    original_entry_id = Column(
        Integer,
        ForeignKey("journal_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True
    )
    reversing_entry_id = Column(
        Integer,
        ForeignKey("journal_entries.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Reversal information
    reversal_date = Column(DateTime, nullable=False)
    is_processed = Column(Boolean, nullable=False, default=False)
    processed_date = Column(DateTime, nullable=True)
    
    # Relationships
    # original_entry = relationship("JournalEntry", foreign_keys=[original_entry_id])
    # reversing_entry = relationship("JournalEntry", foreign_keys=[reversing_entry_id])
    
    def __str__(self):
        """String representation of reversing entry."""
        return f"Reverse JE-{self.original_entry_id} on {self.reversal_date}"
    
    def __repr__(self):
        """Detailed representation of reversing entry."""
        return (
            f"ReversingEntry(id={self.id}, original_id={self.original_entry_id}, "
            f"reversing_id={self.reversing_entry_id}, date={self.reversal_date})"
        )