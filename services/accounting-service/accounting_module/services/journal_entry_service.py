"""
Journal Entry management services for accounting operations.

Provides business logic for journal entries, posting controls,
and journal entry lifecycle management.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from accounting_module.models.journal_entry import (
    JournalEntry, JournalEntryLine, JournalEntryType, 
    JournalEntryStatus, ReversingEntry
)
from accounting_module.models.account import Account
from accounting_module.services.base_service import BaseService, ServiceError, ValidationError, NotFoundError

import logging
logger = logging.getLogger(__name__)

class JournalEntryService(BaseService):
    """
    Journal Entry Service for managing journal entries.
    
    Handles journal entry creation, validation, posting, and reversal operations.
    """
    
    def create_journal_entry(self, description: str, entry_date: datetime,
                           entry_type: JournalEntryType = JournalEntryType.STANDARD,
                           **kwargs) -> JournalEntry:
        """Create a new journal entry."""
        # Generate entry number
        entry_number = self._generate_entry_number()
        
        # Validate entry date
        if entry_date > datetime.utcnow():
            raise ValidationError("Entry date cannot be in the future")
        
        journal_entry_data = {
            'entry_number': entry_number,
            'description': description,
            'entry_date': entry_date,
            'entry_type': entry_type,
            **kwargs
        }
        
        journal_entry = self.create(JournalEntry, journal_entry_data)
        return journal_entry
    
    def add_journal_entry_line(self, journal_entry_id: int, account_id: int,
                              debit_amount: Decimal = Decimal('0'),
                              credit_amount: Decimal = Decimal('0'),
                              description: str = None, **kwargs) -> JournalEntryLine:
        """Add a line to a journal entry."""
        # Validate journal entry
        journal_entry = self.get_by_id_or_raise(JournalEntry, journal_entry_id)
        if journal_entry.status != JournalEntryStatus.DRAFT:
            raise ValidationError("Cannot add lines to a posted or cancelled journal entry")
        
        # Validate account
        account = self.get_by_id_or_raise(Account, account_id)
        if not account.is_active:
            raise ValidationError("Account must be active")
        
        # Validate amounts
        debit_decimal = Decimal(str(debit_amount))
        credit_decimal = Decimal(str(credit_amount))
        
        if debit_decimal != 0 and credit_decimal != 0:
            raise ValidationError("Line cannot have both debit and credit amounts")
        
        if debit_decimal == 0 and credit_decimal == 0:
            raise ValidationError("Line must have either debit or credit amount")
        
        # Get next line number
        max_line_number = self.db.query(func.max(JournalEntryLine.line_number)).filter(
            JournalEntryLine.journal_entry_id == journal_entry_id
        ).scalar() or 0
        
        line_data = {
            'journal_entry_id': journal_entry_id,
            'account_id': account_id,
            'debit_amount': debit_decimal,
            'credit_amount': credit_decimal,
            'description': description,
            'line_number': max_line_number + 1,
            **kwargs
        }
        
        journal_entry_line = self.create(JournalEntryLine, line_data)
        
        # Update journal entry totals
        self._update_journal_entry_totals(journal_entry)
        
        return journal_entry_line
    
    def update_journal_entry_line(self, line_id: int, **kwargs) -> JournalEntryLine:
        """Update a journal entry line."""
        line = self.get_by_id_or_raise(JournalEntryLine, line_id)
        
        # Validate journal entry status
        journal_entry = self.get_by_id_or_raise(JournalEntry, line.journal_entry_id)
        if journal_entry.status != JournalEntryStatus.DRAFT:
            raise ValidationError("Cannot update lines in a posted or cancelled journal entry")
        
        # Validate amounts if provided
        if 'debit_amount' in kwargs or 'credit_amount' in kwargs:
            debit_amount = kwargs.get('debit_amount', line.debit_amount)
            credit_amount = kwargs.get('credit_amount', line.credit_amount)
            
            debit_decimal = Decimal(str(debit_amount))
            credit_decimal = Decimal(str(credit_amount))
            
            if debit_decimal != 0 and credit_decimal != 0:
                raise ValidationError("Line cannot have both debit and credit amounts")
            
            if debit_decimal == 0 and credit_decimal == 0:
                raise ValidationError("Line must have either debit or credit amount")
            
            kwargs['debit_amount'] = debit_decimal
            kwargs['credit_amount'] = credit_decimal
        
        # Validate account if provided
        if 'account_id' in kwargs and kwargs['account_id']:
            account = self.get_by_id_or_raise(Account, kwargs['account_id'])
            if not account.is_active:
                raise ValidationError("Account must be active")
        
        updated_line = self.update(line, kwargs)
        
        # Update journal entry totals
        self._update_journal_entry_totals(journal_entry)
        
        return updated_line
    
    def delete_journal_entry_line(self, line_id: int) -> bool:
        """Delete a journal entry line."""
        line = self.get_by_id_or_raise(JournalEntryLine, line_id)
        
        # Validate journal entry status
        journal_entry = self.get_by_id_or_raise(JournalEntry, line.journal_entry_id)
        if journal_entry.status != JournalEntryStatus.DRAFT:
            raise ValidationError("Cannot delete lines from a posted or cancelled journal entry")
        
        # Delete the line
        self.db.delete(line)
        self.db.flush()
        
        # Update journal entry totals
        self._update_journal_entry_totals(journal_entry)
        
        return True
    
    def post_journal_entry(self, journal_entry_id: int, 
                          posting_date: datetime = None) -> JournalEntry:
        """Post a journal entry to the ledger."""
        journal_entry = self.get_by_id_or_raise(JournalEntry, journal_entry_id)
        
        # Validate journal entry
        if journal_entry.status != JournalEntryStatus.DRAFT:
            raise ValidationError("Journal entry must be in draft status to post")
        
        # Validate that entry is balanced
        if not journal_entry.is_balanced:
            raise ValidationError("Journal entry is not balanced (debits must equal credits)")
        
        # Validate that entry has lines
        line_count = self.db.query(func.count(JournalEntryLine.id)).filter(
            JournalEntryLine.journal_entry_id == journal_entry_id
        ).scalar()
        
        if line_count == 0:
            raise ValidationError("Journal entry must have at least one line")
        
        # Set posting date if not provided
        if not posting_date:
            posting_date = datetime.utcnow()
        
        # Update account balances
        lines = self.db.query(JournalEntryLine).filter(
            JournalEntryLine.journal_entry_id == journal_entry_id
        ).all()
        
        for line in lines:
            account = self.get_by_id_or_raise(Account, line.account_id)
            account.update_balance(line.debit_amount, line.credit_amount)
            line.is_posted = True
        
        # Update journal entry status
        update_data = {
            'status': JournalEntryStatus.POSTED,
            'posting_date': posting_date,
            'posted_by_user_id': self.user_id
        }
        
        updated_entry = self.update(journal_entry, update_data)
        self.commit()
        
        # Create reversing entry if needed
        if journal_entry.entry_type == JournalEntryType.REVERSING:
            self._create_reversing_entry(journal_entry)
        
        return updated_entry
    
    def cancel_journal_entry(self, journal_entry_id: int) -> JournalEntry:
        """Cancel a journal entry."""
        journal_entry = self.get_by_id_or_raise(JournalEntry, journal_entry_id)
        
        # Validate journal entry status
        if journal_entry.status == JournalEntryStatus.CANCELLED:
            raise ValidationError("Journal entry is already cancelled")
        
        # If entry is posted, reverse the account balances
        if journal_entry.status == JournalEntryStatus.POSTED:
            lines = self.db.query(JournalEntryLine).filter(
                JournalEntryLine.journal_entry_id == journal_entry_id
            ).all()
            
            for line in lines:
                account = self.get_by_id_or_raise(Account, line.account_id)
                # Reverse the balance update
                account.update_balance(line.credit_amount, line.debit_amount)
        
        # Update journal entry status
        update_data = {
            'status': JournalEntryStatus.CANCELLED
        }
        
        return self.update(journal_entry, update_data)
    
    def search_journal_entries(self, search_term: str = None,
                              entry_type: JournalEntryType = None,
                              status: JournalEntryStatus = None,
                              date_from: datetime = None,
                              date_to: datetime = None,
                              limit: int = 50) -> List[JournalEntry]:
        """Search journal entries by various criteria."""
        query = self.db.query(JournalEntry)
        query = self._apply_company_filter(query, JournalEntry)
        
        # Apply text search
        if search_term:
            search_conditions = [
                JournalEntry.entry_number.ilike(f"%{search_term}%"),
                JournalEntry.description.ilike(f"%{search_term}%"),
                JournalEntry.reference.ilike(f"%{search_term}%")
            ]
            query = query.filter(or_(*search_conditions))
        
        # Apply filters
        if entry_type:
            query = query.filter(JournalEntry.entry_type == entry_type)
        if status:
            query = query.filter(JournalEntry.status == status)
        if date_from:
            query = query.filter(JournalEntry.entry_date >= date_from)
        if date_to:
            query = query.filter(JournalEntry.entry_date <= date_to)
        
        query = query.order_by(desc(JournalEntry.entry_date), desc(JournalEntry.id))
        return query.limit(limit).all()
    
    def get_journal_entry_statistics(self) -> Dict[str, Any]:
        """Get journal entry statistics for dashboard."""
        # Get total journal entry count
        total_entries = self.count_all(JournalEntry, active_only=False)
        
        # Get posted journal entry count
        posted_entries = self.db.query(func.count(JournalEntry.id)).filter(
            and_(
                JournalEntry.company_id == self.company_id,
                JournalEntry.status == JournalEntryStatus.POSTED
            )
        ).scalar()
        
        # Get journal entry counts by type
        entry_type_counts = {}
        for entry_type in JournalEntryType:
            count = self.db.query(func.count(JournalEntry.id)).filter(
                and_(
                    JournalEntry.entry_type == entry_type,
                    JournalEntry.company_id == self.company_id
                )
            ).scalar()
            entry_type_counts[entry_type.value] = count
        
        # Get journal entry counts by status
        entry_status_counts = {}
        for status in JournalEntryStatus:
            count = self.db.query(func.count(JournalEntry.id)).filter(
                and_(
                    JournalEntry.status == status,
                    JournalEntry.company_id == self.company_id
                )
            ).scalar()
            entry_status_counts[status.value] = count
        
        return {
            "total": total_entries,
            "posted": posted_entries,
            "by_type": entry_type_counts,
            "by_status": entry_status_counts
        }
    
    def _generate_entry_number(self) -> str:
        """Generate unique journal entry number."""
        # In production, would use company settings and sequence numbers
        timestamp = int(time.time())
        return f"JE{timestamp:08d}"
    
    def _update_journal_entry_totals(self, journal_entry: JournalEntry) -> None:
        """Update journal entry total debit and credit amounts."""
        # Calculate totals from lines
        totals = self.db.query(
            func.sum(JournalEntryLine.debit_amount).label('total_debit'),
            func.sum(JournalEntryLine.credit_amount).label('total_credit')
        ).filter(JournalEntryLine.journal_entry_id == journal_entry.id).first()
        
        total_debit = totals.total_debit or Decimal('0')
        total_credit = totals.total_credit or Decimal('0')
        
        # Update journal entry
        journal_entry.total_debit = total_debit
        journal_entry.total_credit = total_credit
    
    def _create_reversing_entry(self, original_entry: JournalEntry) -> ReversingEntry:
        """Create a reversing entry for an adjusting entry."""
        # Calculate reversal date (first day of next month)
        reversal_date = datetime(
            year=original_entry.entry_date.year + (1 if original_entry.entry_date.month == 12 else 0),
            month=1 if original_entry.entry_date.month == 12 else original_entry.entry_date.month + 1,
            day=1
        )
        
        reversing_data = {
            'original_entry_id': original_entry.id,
            'reversal_date': reversal_date
        }
        
        reversing_entry = self.create(ReversingEntry, reversing_data)
        return reversing_entry

class ReversingEntryService(BaseService):
    """
    Reversing Entry Service for managing automatic reversing entries.
    
    Handles creation and processing of reversing entries for adjusting entries.
    """
    
    def process_reversing_entries(self, process_date: datetime = None) -> int:
        """Process reversing entries that are due to be reversed."""
        if not process_date:
            process_date = datetime.utcnow()
        
        # Find reversing entries that need to be processed
        reversing_entries = self.db.query(ReversingEntry).filter(
            and_(
                ReversingEntry.reversal_date <= process_date,
                ReversingEntry.is_processed == False,
                ReversingEntry.company_id == self.company_id
            )
        ).all()
        
        processed_count = 0
        
        for reversing_entry in reversing_entries:
            try:
                # Create the actual reversing journal entry
                original_entry = self.get_by_id_or_raise(JournalEntry, reversing_entry.original_entry_id)
                
                # Create new journal entry with reversed amounts
                reversed_entry = self._create_reversed_entry(original_entry, reversing_entry.reversal_date)
                
                # Update reversing entry with reference to the new entry
                reversing_entry.reversing_entry_id = reversed_entry.id
                reversing_entry.is_processed = True
                reversing_entry.processed_date = datetime.utcnow()
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process reversing entry {reversing_entry.id}: {e}")
                continue
        
        self.commit()
        return processed_count
    
    def _create_reversed_entry(self, original_entry: JournalEntry, 
                              reversal_date: datetime) -> JournalEntry:
        """Create a reversed journal entry."""
        from accounting_module.services.journal_entry_service import JournalEntryService
        
        # Create journal entry service with same context
        je_service = JournalEntryService(self.db, self.user_id, self.company_id)
        
        # Create new journal entry
        reversed_entry = je_service.create_journal_entry(
            description=f"Reversal of {original_entry.entry_number}: {original_entry.description}",
            entry_date=reversal_date,
            entry_type=JournalEntryType.REVERSING,
            reference=f"REVERSE-{original_entry.entry_number}"
        )
        
        # Copy and reverse lines from original entry
        original_lines = self.db.query(JournalEntryLine).filter(
            JournalEntryLine.journal_entry_id == original_entry.id
        ).order_by(JournalEntryLine.line_number).all()
        
        for line in original_lines:
            je_service.add_journal_entry_line(
                journal_entry_id=reversed_entry.id,
                account_id=line.account_id,
                debit_amount=line.credit_amount,  # Reverse debit/credit
                credit_amount=line.debit_amount,  # Reverse debit/credit
                description=f"Reversal: {line.description}" if line.description else None,
                reference=line.reference
            )
        
        # Post the reversed entry
        je_service.post_journal_entry(reversed_entry.id)
        
        return reversed_entry