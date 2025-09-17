"""
Bank Transaction models for accounting management including bank accounts,
bank statements, and bank reconciliations.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from accounting_module.framework.base import CompanyBusinessObject
from accounting_module.models.account import Account

class BankAccountType(str, enum.Enum):
    """Bank account type enumeration"""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    LOAN = "loan"

class BankTransactionType(str, enum.Enum):
    """Bank transaction type enumeration"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    FEE = "fee"
    INTEREST = "interest"

class BankTransactionStatus(str, enum.Enum):
    """Bank transaction status enumeration"""
    PENDING = "pending"
    CLEARED = "cleared"
    RECONCILED = "reconciled"
    VOID = "void"

class BankStatementStatus(str, enum.Enum):
    """Bank statement status enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    RECONCILED = "reconciled"

class BankAccount(CompanyBusinessObject):
    """
    Bank Account model representing company bank accounts.
    
    Comprehensive bank account information including banking details,
    balances, and integration with chart of accounts.
    """
    
    __tablename__ = "bank_accounts"
    
    # Basic bank account information
    account_name = Column(String(255), nullable=False, index=True)
    bank_name = Column(String(255), nullable=False)
    account_number = Column(String(100), nullable=False, index=True)
    routing_number = Column(String(50), nullable=True)
    
    # Account type and identification
    account_type = Column(Enum(BankAccountType), nullable=False, default=BankAccountType.CHECKING)
    currency_code = Column(String(3), nullable=False, default="USD")
    
    # Integration with chart of accounts
    gl_account_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Balance information
    current_balance = Column(Numeric(15, 2), nullable=False, default=0)
    available_balance = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Status and control
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_default = Column(Boolean, nullable=False, default=False)
    
    # Bank contact information
    bank_contact = Column(String(255), nullable=True)
    bank_phone = Column(String(50), nullable=True)
    bank_address = Column(Text, nullable=True)
    
    # Online banking information
    online_banking_url = Column(String(500), nullable=True)
    online_banking_username = Column(String(100), nullable=True)
    
    # Relationships
    # gl_account = relationship("Account", back_populates="bank_accounts")
    # bank_transactions = relationship("BankTransaction", back_populates="bank_account")
    # bank_statements = relationship("BankStatement", back_populates="bank_account")
    
    def __str__(self):
        """String representation of bank account."""
        return f"{self.bank_name} - {self.account_name} ({self.account_number})"
    
    def __repr__(self):
        """Detailed representation of bank account."""
        return (
            f"BankAccount(id={self.id}, bank='{self.bank_name}', "
            f"account='{self.account_name}', number='{self.account_number}')"
        )
    
    @property
    def display_name(self) -> str:
        """Get display name for bank account."""
        return f"{self.bank_name} - {self.account_name}"
    
    @property
    def masked_account_number(self) -> str:
        """Get masked account number for display."""
        if len(self.account_number) > 4:
            return "*" * (len(self.account_number) - 4) + self.account_number[-4:]
        return self.account_number
    
    def update_balance(self, amount: Decimal, transaction_type: BankTransactionType) -> None:
        """Update account balance based on transaction type."""
        if transaction_type in [BankTransactionType.DEPOSIT, BankTransactionType.INTEREST]:
            self.current_balance = Decimal(str(self.current_balance)) + amount
        else:
            self.current_balance = Decimal(str(self.current_balance)) - amount

class BankTransaction(CompanyBusinessObject):
    """
    Bank Transaction model representing individual bank transactions.
    
    Individual bank transactions that can be imported from bank feeds,
    manually entered, or automatically created from journal entries.
    """
    
    __tablename__ = "bank_transactions"
    
    # References
    bank_account_id = Column(
        Integer,
        ForeignKey("bank_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Basic transaction information
    transaction_date = Column(Date, nullable=False, index=True)
    description = Column(String(500), nullable=False)
    reference_number = Column(String(100), nullable=True, index=True)
    
    # Amount information
    amount = Column(Numeric(15, 2), nullable=False)
    running_balance = Column(Numeric(15, 2), nullable=True)
    
    # Transaction type and status
    transaction_type = Column(Enum(BankTransactionType), nullable=False, index=True)
    status = Column(Enum(BankTransactionStatus), nullable=False, default=BankTransactionStatus.PENDING, index=True)
    
    # Reconciliation information
    statement_id = Column(
        Integer,
        ForeignKey("bank_statements.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    is_reconciled = Column(Boolean, nullable=False, default=False)
    reconciliation_date = Column(DateTime, nullable=True)
    
    # Integration with journal entries
    journal_entry_id = Column(
        Integer,
        ForeignKey("journal_entries.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Categorization
    category = Column(String(100), nullable=True)
    payee = Column(String(255), nullable=True)
    
    # User information
    created_by_user_id = Column(Integer, nullable=True)
    reconciled_by_user_id = Column(Integer, nullable=True)
    
    # Relationships
    # bank_account = relationship("BankAccount", back_populates="bank_transactions")
    # bank_statement = relationship("BankStatement", back_populates="bank_transactions")
    # journal_entry = relationship("JournalEntry", back_populates="bank_transaction")
    
    def __str__(self):
        """String representation of bank transaction."""
        return f"{self.transaction_date}: {self.description} ({self.amount})"
    
    def __repr__(self):
        """Detailed representation of bank transaction."""
        return (
            f"BankTransaction(id={self.id}, date={self.transaction_date}, "
            f"amount={self.amount}, type='{self.transaction_type.value}', status='{self.status.value}')"
        )
    
    @property
    def display_amount(self) -> str:
        """Get display amount with appropriate sign."""
        if self.transaction_type in [BankTransactionType.DEPOSIT, BankTransactionType.INTEREST]:
            return f"+{self.amount}"
        return f"-{self.amount}"
    
    def is_matching_journal_entry(self, journal_entry_line) -> bool:
        """Check if this transaction matches a journal entry line."""
        # In production, would implement matching logic based on date, amount, and description
        return False

class BankStatement(CompanyBusinessObject):
    """
    Bank Statement model representing bank statement periods.
    
    Bank statements that group bank transactions for reconciliation
    and reporting purposes.
    """
    
    __tablename__ = "bank_statements"
    
    # References
    bank_account_id = Column(
        Integer,
        ForeignKey("bank_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Statement information
    statement_number = Column(String(100), nullable=False, index=True)
    statement_date = Column(Date, nullable=False)
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)
    
    # Balance information
    opening_balance = Column(Numeric(15, 2), nullable=False)
    closing_balance = Column(Numeric(15, 2), nullable=False)
    calculated_closing_balance = Column(Numeric(15, 2), nullable=True)
    
    # Status
    status = Column(Enum(BankStatementStatus), nullable=False, default=BankStatementStatus.OPEN, index=True)
    
    # User information
    prepared_by_user_id = Column(Integer, nullable=True)
    reviewed_by_user_id = Column(Integer, nullable=True)
    review_date = Column(DateTime, nullable=True)
    
    # Relationships
    # bank_account = relationship("BankAccount", back_populates="bank_statements")
    # bank_transactions = relationship("BankTransaction", back_populates="bank_statement")
    
    def __str__(self):
        """String representation of bank statement."""
        return f"Statement {self.statement_number} ({self.period_start_date} to {self.period_end_date})"
    
    def __repr__(self):
        """Detailed representation of bank statement."""
        return (
            f"BankStatement(id={self.id}, number='{self.statement_number}', "
            f"period={self.period_start_date} to {self.period_end_date}, status='{self.status.value}')"
        )
    
    @property
    def display_name(self) -> str:
        """Get display name for bank statement."""
        return f"Statement {self.statement_number}"
    
    def calculate_closing_balance(self) -> Decimal:
        """Calculate the expected closing balance based on transactions."""
        # In production, would sum transactions within the statement period
        return self.opening_balance
    
    def validate_statement_balance(self) -> bool:
        """Validate that calculated balance matches bank statement balance."""
        calculated = self.calculate_closing_balance()
        return Decimal(str(calculated)) == Decimal(str(self.closing_balance))

class BankReconciliation(CompanyBusinessObject):
    """
    Bank Reconciliation model for reconciling bank statements.
    
    Records of bank reconciliations that match bank transactions
    with journal entries and identify discrepancies.
    """
    
    __tablename__ = "bank_reconciliations"
    
    # References
    bank_statement_id = Column(
        Integer,
        ForeignKey("bank_statements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True
    )
    
    # Reconciliation information
    reconciliation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    reconciled_by_user_id = Column(Integer, nullable=True)
    
    # Discrepancy tracking
    book_balance = Column(Numeric(15, 2), nullable=False)
    bank_balance = Column(Numeric(15, 2), nullable=False)
    adjusted_book_balance = Column(Numeric(15, 2), nullable=False)
    adjusted_bank_balance = Column(Numeric(15, 2), nullable=False)
    
    # Status
    is_complete = Column(Boolean, nullable=False, default=False)
    completion_date = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    # bank_statement = relationship("BankStatement", back_populates="bank_reconciliation")
    # reconciliation_items = relationship("BankReconciliationItem", back_populates="bank_reconciliation")
    
    def __str__(self):
        """String representation of bank reconciliation."""
        return f"Reconciliation for {self.bank_statement_id} on {self.reconciliation_date}"
    
    def __repr__(self):
        """Detailed representation of bank reconciliation."""
        return (
            f"BankReconciliation(id={self.id}, statement_id={self.bank_statement_id}, "
            f"date={self.reconciliation_date}, complete={self.is_complete})"
        )
    
    @property
    def is_balanced(self) -> bool:
        """Check if reconciliation is balanced."""
        return Decimal(str(self.adjusted_book_balance)) == Decimal(str(self.adjusted_bank_balance))
    
    def calculate_adjusted_balances(self) -> tuple[Decimal, Decimal]:
        """Calculate adjusted book and bank balances."""
        # In production, would calculate based on reconciliation items
        return self.book_balance, self.bank_balance

class BankReconciliationItem(CompanyBusinessObject):
    """
    Bank Reconciliation Item model for individual reconciliation items.
    
    Individual items that explain differences between book and bank balances
    during the reconciliation process.
    """
    
    __tablename__ = "bank_reconciliation_items"
    
    # References
    bank_reconciliation_id = Column(
        Integer,
        ForeignKey("bank_reconciliations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Item information
    description = Column(String(500), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Item type
    is_book_item = Column(Boolean, nullable=False, default=False)  # True if affects book balance
    is_bank_item = Column(Boolean, nullable=False, default=False)  # True if affects bank balance
    
    # References to related records
    bank_transaction_id = Column(
        Integer,
        ForeignKey("bank_transactions.id", ondelete="SET NULL"),
        nullable=True
    )
    journal_entry_id = Column(
        Integer,
        ForeignKey("journal_entries.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Status
    is_cleared = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    # bank_reconciliation = relationship("BankReconciliation", back_populates="reconciliation_items")
    # bank_transaction = relationship("BankTransaction", back_populates="reconciliation_items")
    # journal_entry = relationship("JournalEntry", back_populates="reconciliation_items")
    
    def __str__(self):
        """String representation of bank reconciliation item."""
        return f"{self.description}: {self.amount}"
    
    def __repr__(self):
        """Detailed representation of bank reconciliation item."""
        return (
            f"BankReconciliationItem(id={self.id}, reconciliation_id={self.bank_reconciliation_id}, "
            f"amount={self.amount}, book_item={self.is_book_item}, bank_item={self.is_bank_item})"
        )