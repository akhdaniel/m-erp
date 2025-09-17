"""
Bank Transaction management services for accounting operations.

Provides business logic for bank accounts, transactions,
reconciliations, and bank-related operations.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date
import time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from accounting_module.models.bank import (
    BankAccount, BankTransaction, BankStatement, 
    BankAccountType, BankTransactionType, BankTransactionStatus,
    BankStatementStatus
)
from accounting_module.models.journal_entry import JournalEntry, JournalEntryLine
from accounting_module.models.account import Account
from accounting_module.services.base_service import BaseService, ServiceError, ValidationError, NotFoundError

import logging
logger = logging.getLogger(__name__)

class BankAccountService(BaseService):
    """
    Bank Account Service for managing company bank accounts.
    
    Handles bank account creation, updates, and integration with chart of accounts.
    """
    
    def create_bank_account(self, account_name: str, bank_name: str,
                          account_number: str, account_type: BankAccountType,
                          gl_account_id: int = None, **kwargs) -> BankAccount:
        """Create a new bank account."""
        # Validate account number uniqueness
        existing = self.db.query(BankAccount).filter(
            and_(
                BankAccount.account_number == account_number,
                BankAccount.company_id == self.company_id
            )
        ).first()
        
        if existing:
            raise ValidationError(f"Bank account number '{account_number}' already exists")
        
        # Validate GL account if specified
        if gl_account_id:
            gl_account = self.get_by_id_or_raise(Account, gl_account_id)
            if not gl_account.is_active:
                raise ValidationError("GL account must be active")
            if not gl_account.is_bank_account:
                raise ValidationError("GL account must be configured as a bank account")
        
        # Validate there's only one default account per type
        if kwargs.get('is_default', False):
            existing_default = self.db.query(BankAccount).filter(
                and_(
                    BankAccount.account_type == account_type,
                    BankAccount.is_default == True,
                    BankAccount.company_id == self.company_id
                )
            ).first()
            
            if existing_default:
                raise ValidationError(f"Another {account_type.value} account is already set as default")
        
        bank_account_data = {
            'account_name': account_name,
            'bank_name': bank_name,
            'account_number': account_number,
            'account_type': account_type,
            'gl_account_id': gl_account_id,
            **kwargs
        }
        
        bank_account = self.create(BankAccount, bank_account_data)
        return bank_account
    
    def update_bank_account(self, bank_account_id: int, **kwargs) -> BankAccount:
        """Update bank account information."""
        bank_account = self.get_by_id_or_raise(BankAccount, bank_account_id)
        
        # Validate GL account if specified
        if 'gl_account_id' in kwargs and kwargs['gl_account_id']:
            gl_account = self.get_by_id_or_raise(Account, kwargs['gl_account_id'])
            if not gl_account.is_active:
                raise ValidationError("GL account must be active")
            if not gl_account.is_bank_account:
                raise ValidationError("GL account must be configured as a bank account")
        
        # Validate there's only one default account per type
        if kwargs.get('is_default', False) and 'account_type' in kwargs:
            account_type = kwargs['account_type']
            existing_default = self.db.query(BankAccount).filter(
                and_(
                    BankAccount.account_type == account_type,
                    BankAccount.is_default == True,
                    BankAccount.id != bank_account_id,
                    BankAccount.company_id == self.company_id
                )
            ).first()
            
            if existing_default:
                raise ValidationError(f"Another {account_type.value} account is already set as default")
        elif kwargs.get('is_default', False):
            account_type = bank_account.account_type
            existing_default = self.db.query(BankAccount).filter(
                and_(
                    BankAccount.account_type == account_type,
                    BankAccount.is_default == True,
                    BankAccount.id != bank_account_id,
                    BankAccount.company_id == self.company_id
                )
            ).first()
            
            if existing_default:
                raise ValidationError(f"Another {account_type.value} account is already set as default")
        
        return self.update(bank_account, kwargs)
    
    def get_bank_accounts_by_type(self, account_type: BankAccountType,
                                active_only: bool = True) -> List[BankAccount]:
        """Get bank accounts by account type."""
        query = self.db.query(BankAccount).filter(BankAccount.account_type == account_type)
        query = self._apply_company_filter(query, BankAccount)
        
        if active_only:
            query = query.filter(BankAccount.is_active == True)
        
        query = query.order_by(BankAccount.account_name)
        return query.all()
    
    def search_bank_accounts(self, search_term: str,
                           account_type: BankAccountType = None,
                           active_only: bool = True,
                           limit: int = 50) -> List[BankAccount]:
        """Search bank accounts by various criteria."""
        search_fields = ['account_name', 'bank_name', 'account_number']
        query = self.db.query(BankAccount)
        
        # Apply text search
        search_conditions = []
        for field in search_fields:
            if hasattr(BankAccount, field):
                field_attr = getattr(BankAccount, field)
                search_conditions.append(field_attr.ilike(f"%{search_term}%"))
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        # Apply filters
        if account_type:
            query = query.filter(BankAccount.account_type == account_type)
        if active_only:
            query = query.filter(BankAccount.is_active == True)
        
        query = self._apply_company_filter(query, BankAccount)
        query = query.order_by(BankAccount.account_name)
        
        return query.limit(limit).all()
    
    def get_bank_account_statistics(self) -> Dict[str, Any]:
        """Get bank account statistics for dashboard."""
        # Get total bank account count
        total_accounts = self.count_all(BankAccount, active_only=False)
        
        # Get active bank account count
        active_accounts = self.count_all(BankAccount, active_only=True)
        
        # Get bank account counts by type
        account_type_counts = {}
        for account_type in BankAccountType:
            count = self.db.query(func.count(BankAccount.id)).filter(
                and_(
                    BankAccount.account_type == account_type,
                    BankAccount.company_id == self.company_id,
                    BankAccount.is_active == True
                )
            ).scalar()
            account_type_counts[account_type.value] = count
        
        return {
            "total": total_accounts,
            "active": active_accounts,
            "by_type": account_type_counts
        }

class BankTransactionService(BaseService):
    """
    Bank Transaction Service for managing bank transactions.
    
    Handles bank transaction creation, categorization, and integration with journal entries.
    """
    
    def create_bank_transaction(self, bank_account_id: int, transaction_date: date,
                              description: str, amount: Decimal,
                              transaction_type: BankTransactionType,
                              **kwargs) -> BankTransaction:
        """Create a new bank transaction."""
        # Validate bank account
        bank_account = self.get_by_id_or_raise(BankAccount, bank_account_id)
        if not bank_account.is_active:
            raise ValidationError("Bank account must be active")
        
        # Validate amount
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValidationError("Amount must be positive")
        
        # Validate transaction date
        if transaction_date > date.today():
            raise ValidationError("Transaction date cannot be in the future")
        
        bank_transaction_data = {
            'bank_account_id': bank_account_id,
            'transaction_date': transaction_date,
            'description': description,
            'amount': amount_decimal,
            'transaction_type': transaction_type,
            **kwargs
        }
        
        bank_transaction = self.create(BankTransaction, bank_transaction_data)
        
        # Update bank account balance
        bank_account.update_balance(amount_decimal, transaction_type)
        
        return bank_transaction
    
    def update_bank_transaction(self, transaction_id: int, **kwargs) -> BankTransaction:
        """Update bank transaction information."""
        transaction = self.get_by_id_or_raise(BankTransaction, transaction_id)
        
        # Validate status - cannot update reconciled transactions
        if transaction.is_reconciled:
            raise ValidationError("Cannot update reconciled transactions")
        
        # Validate amount if provided
        if 'amount' in kwargs:
            amount_decimal = Decimal(str(kwargs['amount']))
            if amount_decimal <= 0:
                raise ValidationError("Amount must be positive")
            kwargs['amount'] = amount_decimal
        
        # Validate transaction date if provided
        if 'transaction_date' in kwargs and kwargs['transaction_date'] > date.today():
            raise ValidationError("Transaction date cannot be in the future")
        
        # Validate bank account if provided
        if 'bank_account_id' in kwargs:
            bank_account = self.get_by_id_or_raise(BankAccount, kwargs['bank_account_id'])
            if not bank_account.is_active:
                raise ValidationError("Bank account must be active")
        
        updated_transaction = self.update(transaction, kwargs)
        return updated_transaction
    
    def reconcile_bank_transaction(self, transaction_id: int,
                                 journal_entry_id: int = None) -> BankTransaction:
        """Mark a bank transaction as reconciled."""
        transaction = self.get_by_id_or_raise(BankTransaction, transaction_id)
        
        # Update transaction status
        update_data = {
            'status': BankTransactionStatus.RECONCILED,
            'is_reconciled': True,
            'reconciliation_date': datetime.utcnow(),
            'reconciled_by_user_id': self.user_id
        }
        
        if journal_entry_id:
            update_data['journal_entry_id'] = journal_entry_id
        
        return self.update(transaction, update_data)
    
    def search_bank_transactions(self, search_term: str = None,
                               bank_account_id: int = None,
                               transaction_type: BankTransactionType = None,
                               status: BankTransactionStatus = None,
                               date_from: date = None,
                               date_to: date = None,
                               limit: int = 50) -> List[BankTransaction]:
        """Search bank transactions by various criteria."""
        query = self.db.query(BankTransaction)
        query = self._apply_company_filter(query, BankTransaction)
        
        # Apply text search
        if search_term:
            search_conditions = [
                BankTransaction.description.ilike(f"%{search_term}%"),
                BankTransaction.reference_number.ilike(f"%{search_term}%"),
                BankTransaction.payee.ilike(f"%{search_term}%")
            ]
            query = query.filter(or_(*search_conditions))
        
        # Apply filters
        if bank_account_id:
            query = query.filter(BankTransaction.bank_account_id == bank_account_id)
        if transaction_type:
            query = query.filter(BankTransaction.transaction_type == transaction_type)
        if status:
            query = query.filter(BankTransaction.status == status)
        if date_from:
            query = query.filter(BankTransaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(BankTransaction.transaction_date <= date_to)
        
        query = query.order_by(desc(BankTransaction.transaction_date), desc(BankTransaction.id))
        return query.limit(limit).all()
    
    def get_uncleared_transactions(self, bank_account_id: int,
                                 statement_id: int = None) -> List[BankTransaction]:
        """Get uncleared transactions for bank reconciliation."""
        query = self.db.query(BankTransaction).filter(
            and_(
                BankTransaction.bank_account_id == bank_account_id,
                BankTransaction.status.in_([BankTransactionStatus.PENDING, BankTransactionStatus.CLEARED]),
                BankTransaction.is_reconciled == False
            )
        )
        
        if statement_id:
            query = query.filter(BankTransaction.statement_id == statement_id)
        
        query = self._apply_company_filter(query, BankTransaction)
        query = query.order_by(BankTransaction.transaction_date)
        return query.all()
    
    def get_bank_transaction_statistics(self) -> Dict[str, Any]:
        """Get bank transaction statistics for dashboard."""
        # Get total transaction count
        total_transactions = self.count_all(BankTransaction, active_only=False)
        
        # Get reconciled transaction count
        reconciled_transactions = self.db.query(func.count(BankTransaction.id)).filter(
            and_(
                BankTransaction.company_id == self.company_id,
                BankTransaction.is_reconciled == True
            )
        ).scalar()
        
        # Get transaction counts by type
        transaction_type_counts = {}
        for transaction_type in BankTransactionType:
            count = self.db.query(func.count(BankTransaction.id)).filter(
                and_(
                    BankTransaction.transaction_type == transaction_type,
                    BankTransaction.company_id == self.company_id
                )
            ).scalar()
            transaction_type_counts[transaction_type.value] = count
        
        # Get transaction counts by status
        transaction_status_counts = {}
        for status in BankTransactionStatus:
            count = self.db.query(func.count(BankTransaction.id)).filter(
                and_(
                    BankTransaction.status == status,
                    BankTransaction.company_id == self.company_id
                )
            ).scalar()
            transaction_status_counts[status.value] = count
        
        return {
            "total": total_transactions,
            "reconciled": reconciled_transactions,
            "by_type": transaction_type_counts,
            "by_status": transaction_status_counts
        }

class BankStatementService(BaseService):
    """
    Bank Statement Service for managing bank statements.
    
    Handles bank statement creation, closing, and reconciliation processes.
    """
    
    def create_bank_statement(self, bank_account_id: int,
                            statement_number: str, statement_date: date,
                            period_start_date: date, period_end_date: date,
                            opening_balance: Decimal, closing_balance: Decimal,
                            **kwargs) -> BankStatement:
        """Create a new bank statement."""
        # Validate bank account
        bank_account = self.get_by_id_or_raise(BankAccount, bank_account_id)
        if not bank_account.is_active:
            raise ValidationError("Bank account must be active")
        
        # Validate statement number uniqueness
        existing = self.db.query(BankStatement).filter(
            and_(
                BankStatement.statement_number == statement_number,
                BankStatement.company_id == self.company_id
            )
        ).first()
        
        if existing:
            raise ValidationError(f"Bank statement number '{statement_number}' already exists")
        
        # Validate dates
        if period_start_date > period_end_date:
            raise ValidationError("Period start date cannot be after period end date")
        
        if statement_date < period_end_date:
            raise ValidationError("Statement date cannot be before period end date")
        
        # Validate balances
        opening_balance_decimal = Decimal(str(opening_balance))
        closing_balance_decimal = Decimal(str(closing_balance))
        
        bank_statement_data = {
            'bank_account_id': bank_account_id,
            'statement_number': statement_number,
            'statement_date': statement_date,
            'period_start_date': period_start_date,
            'period_end_date': period_end_date,
            'opening_balance': opening_balance_decimal,
            'closing_balance': closing_balance_decimal,
            **kwargs
        }
        
        bank_statement = self.create(BankStatement, bank_statement_data)
        return bank_statement
    
    def close_bank_statement(self, statement_id: int) -> BankStatement:
        """Close a bank statement."""
        statement = self.get_by_id_or_raise(BankStatement, statement_id)
        
        # Validate that statement is not already closed
        if statement.status == BankStatementStatus.CLOSED:
            raise ValidationError("Bank statement is already closed")
        
        # Validate that calculated closing balance matches provided closing balance
        if not statement.validate_statement_balance():
            raise ValidationError("Calculated closing balance does not match provided closing balance")
        
        # Update statement status
        update_data = {
            'status': BankStatementStatus.CLOSED
        }
        
        return self.update(statement, update_data)
    
    def search_bank_statements(self, search_term: str = None,
                             bank_account_id: int = None,
                             status: BankStatementStatus = None,
                             date_from: date = None,
                             date_to: date = None,
                             limit: int = 50) -> List[BankStatement]:
        """Search bank statements by various criteria."""
        query = self.db.query(BankStatement)
        query = self._apply_company_filter(query, BankStatement)
        
        # Apply text search
        if search_term:
            search_conditions = [
                BankStatement.statement_number.ilike(f"%{search_term}%")
            ]
            query = query.filter(or_(*search_conditions))
        
        # Apply filters
        if bank_account_id:
            query = query.filter(BankStatement.bank_account_id == bank_account_id)
        if status:
            query = query.filter(BankStatement.status == status)
        if date_from:
            query = query.filter(BankStatement.period_end_date >= date_from)
        if date_to:
            query = query.filter(BankStatement.period_end_date <= date_to)
        
        query = query.order_by(desc(BankStatement.period_end_date), desc(BankStatement.id))
        return query.limit(limit).all()