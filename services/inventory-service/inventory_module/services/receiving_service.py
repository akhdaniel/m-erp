"""
Receiving services for inbound inventory operations.

Provides business logic for receiving records, line item management,
quality control, and integration with stock management.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from inventory_module.models import (
    ReceivingRecord, ReceivingLineItem, ReceivingStatus, ReceivingLineStatus,
    StockMovementType
)
from inventory_module.services.base_service import BaseService, ServiceError, ValidationError, NotFoundError
from inventory_module.services.stock_service import StockService


class ReceivingService(BaseService):
    """
    Receiving Service for managing inbound inventory operations.
    
    Handles receiving record creation, line item processing,
    quality control, and integration with stock management.
    """
    
    def create_receiving_record(self, source_document_type: str,
                               source_document_id: int,
                               supplier_id: int,
                               warehouse_id: int,
                               line_items: List[Dict[str, Any]],
                               **kwargs) -> ReceivingRecord:
        """Create a new receiving record with line items."""
        # Generate receipt number if not provided
        receipt_number = kwargs.get('receipt_number')
        if not receipt_number:
            receipt_number = self._generate_receipt_number()
        
        # Validate receipt number uniqueness
        existing = self.db.query(ReceivingRecord).filter(
            and_(
                ReceivingRecord.receipt_number == receipt_number,
                ReceivingRecord.company_id == self.company_id
            )
        ).first()
        
        if existing:
            raise ValidationError(f"Receipt number '{receipt_number}' already exists")
        
        # Create receiving record
        record_data = {
            'receipt_number': receipt_number,
            'source_document_type': source_document_type,
            'source_document_id': source_document_id,
            'supplier_id': supplier_id,
            'warehouse_id': warehouse_id,
            'status': ReceivingStatus.PENDING,
            **kwargs
        }
        
        receiving_record = self.create(ReceivingRecord, record_data)
        
        # Create line items
        total_expected = Decimal('0.00')
        total_value = Decimal('0.00')
        
        for line_num, line_data in enumerate(line_items, 1):
            line_item = self._create_line_item(
                receiving_record.id,
                line_num,
                line_data
            )
            total_expected += line_item.quantity_expected
            if line_item.total_cost:
                total_value += line_item.total_cost
        
        # Update totals
        receiving_record.total_quantity_expected = total_expected
        receiving_record.total_value_expected = total_value
        
        return receiving_record
    
    def _create_line_item(self, receiving_record_id: int, line_number: int,
                         line_data: Dict[str, Any]) -> ReceivingLineItem:
        """Create a receiving line item."""
        line_item_data = {
            'receiving_record_id': receiving_record_id,
            'line_number': line_number,
            'status': ReceivingLineStatus.PENDING,
            **line_data
        }
        
        # Calculate total cost if unit cost provided
        if line_data.get('unit_cost') and line_data.get('quantity_expected'):
            line_item_data['total_cost'] = (
                line_data['unit_cost'] * line_data['quantity_expected']
            )
        
        return self.create(ReceivingLineItem, line_item_data)
    
    def start_receiving(self, receiving_record_id: int) -> ReceivingRecord:
        """Start the receiving process."""
        record = self.get_by_id_or_raise(ReceivingRecord, receiving_record_id)
        
        if not record.can_be_received():
            raise ValidationError("Receipt cannot be started in current status")
        
        record.start_receiving(self.user_id)
        
        return record
    
    def receive_line_item(self, line_item_id: int, quantity: Decimal,
                         location_id: int = None,
                         batch_number: str = None,
                         serial_numbers: List[str] = None,
                         expiration_date: datetime = None,
                         quality_notes: str = None) -> ReceivingLineItem:
        """Receive quantity for a line item."""
        line_item = self.get_by_id_or_raise(ReceivingLineItem, line_item_id)
        
        # Receive the quantity
        line_item.receive_quantity(quantity, self.user_id, location_id)
        
        # Update additional tracking information
        if batch_number:
            line_item.batch_number = batch_number
        if serial_numbers:
            line_item.serial_numbers = serial_numbers
        if expiration_date:
            line_item.expiration_date = expiration_date
        if quality_notes:
            line_item.quality_notes = quality_notes
        
        # Create stock movement and update stock levels
        self._create_stock_movement(line_item, quantity, location_id)
        
        # Update receiving record totals
        self._update_receiving_record_totals(line_item.receiving_record_id)
        
        return line_item
    
    def _create_stock_movement(self, line_item: ReceivingLineItem, 
                              quantity: Decimal, location_id: int) -> None:
        """Create stock movement and update stock levels."""
        if not location_id:
            # Use putaway location if specified, otherwise use default receiving location
            location_id = line_item.put_away_location_id
            if not location_id:
                # Get warehouse default receiving location
                record = self.get_by_id(ReceivingRecord, line_item.receiving_record_id)
                # Would get warehouse default location in production
                return
        
        # Create stock service and adjust stock
        stock_service = StockService(self.db, self.user_id, self.company_id)
        
        stock_service.adjust_stock(
            product_id=line_item.product_id,
            quantity_change=quantity,
            location_id=location_id,
            movement_type=StockMovementType.RECEIPT,
            product_variant_id=line_item.product_variant_id,
            unit_cost=line_item.unit_cost,
            reason=f"Receipt from {line_item.receiving_record.receipt_number}"
        )
    
    def _update_receiving_record_totals(self, receiving_record_id: int) -> None:
        """Update receiving record totals based on line items."""
        record = self.get_by_id(ReceivingRecord, receiving_record_id)
        if not record:
            return
        
        # Calculate totals from line items
        line_items = self.get_receiving_line_items(receiving_record_id)
        
        total_received = sum(item.quantity_received for item in line_items)
        total_value_received = sum(
            item.total_value_received for item in line_items
        )
        
        record.total_quantity_received = total_received
        record.total_value_received = total_value_received
        
        # Check if receiving is complete
        if total_received >= record.total_quantity_expected:
            record.status = ReceivingStatus.COMPLETE
        elif total_received > 0:
            record.status = ReceivingStatus.PARTIAL
    
    def reject_line_item_quantity(self, line_item_id: int, quantity: Decimal,
                                 reason: str) -> ReceivingLineItem:
        """Reject quantity for a line item."""
        line_item = self.get_by_id_or_raise(ReceivingLineItem, line_item_id)
        
        line_item.reject_quantity(quantity, reason, self.user_id)
        
        # Update receiving record totals
        self._update_receiving_record_totals(line_item.receiving_record_id)
        
        return line_item
    
    def mark_line_item_damaged(self, line_item_id: int, quantity: Decimal,
                              description: str) -> ReceivingLineItem:
        """Mark quantity as damaged for a line item."""
        line_item = self.get_by_id_or_raise(ReceivingLineItem, line_item_id)
        
        line_item.mark_damaged(quantity, description, self.user_id)
        
        # Update receiving record totals
        self._update_receiving_record_totals(line_item.receiving_record_id)
        
        return line_item
    
    def perform_quality_inspection(self, line_item_id: int, passed: bool,
                                  notes: str = None) -> ReceivingLineItem:
        """Perform quality inspection on a line item."""
        line_item = self.get_by_id_or_raise(ReceivingLineItem, line_item_id)
        
        if passed:
            line_item.pass_quality_inspection(self.user_id, notes)
        else:
            line_item.fail_quality_inspection(self.user_id, notes or "Quality inspection failed")
            
            # Update receiving record totals after potential rejection
            self._update_receiving_record_totals(line_item.receiving_record_id)
        
        return line_item
    
    def complete_receiving(self, receiving_record_id: int) -> ReceivingRecord:
        """Complete the receiving process."""
        record = self.get_by_id_or_raise(ReceivingRecord, receiving_record_id)
        
        # Validate all line items are processed
        pending_items = self.get_pending_line_items(receiving_record_id)
        if pending_items:
            raise ValidationError(f"{len(pending_items)} line items are still pending")
        
        record.complete_receiving(self.user_id)
        
        return record
    
    def cancel_receiving(self, receiving_record_id: int, reason: str) -> ReceivingRecord:
        """Cancel the receiving process."""
        record = self.get_by_id_or_raise(ReceivingRecord, receiving_record_id)
        
        record.cancel_receiving(self.user_id, reason)
        
        return record
    
    def get_receiving_record_by_number(self, receipt_number: str) -> Optional[ReceivingRecord]:
        """Get receiving record by receipt number."""
        query = self.db.query(ReceivingRecord).filter(
            ReceivingRecord.receipt_number == receipt_number
        )
        query = self._apply_company_filter(query, ReceivingRecord)
        return query.first()
    
    def get_receiving_line_items(self, receiving_record_id: int) -> List[ReceivingLineItem]:
        """Get all line items for a receiving record."""
        query = self.db.query(ReceivingLineItem).filter(
            ReceivingLineItem.receiving_record_id == receiving_record_id
        )
        query = self._apply_company_filter(query, ReceivingLineItem)
        query = query.order_by(ReceivingLineItem.line_number)
        
        return query.all()
    
    def get_pending_line_items(self, receiving_record_id: int) -> List[ReceivingLineItem]:
        """Get pending line items for a receiving record."""
        query = self.db.query(ReceivingLineItem).filter(
            and_(
                ReceivingLineItem.receiving_record_id == receiving_record_id,
                ReceivingLineItem.status == ReceivingLineStatus.PENDING
            )
        )
        query = self._apply_company_filter(query, ReceivingLineItem)
        
        return query.all()
    
    def get_overdue_receipts(self, days_overdue: int = 1) -> List[ReceivingRecord]:
        """Get overdue receiving records."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_overdue)
        
        query = self.db.query(ReceivingRecord).filter(
            and_(
                ReceivingRecord.expected_date < cutoff_date,
                ReceivingRecord.status.in_([ReceivingStatus.PENDING, ReceivingStatus.PARTIAL])
            )
        )
        query = self._apply_company_filter(query, ReceivingRecord)
        query = query.order_by(ReceivingRecord.expected_date)
        
        return query.all()
    
    def get_receipts_by_supplier(self, supplier_id: int, 
                                days_back: int = 30,
                                limit: int = 50) -> List[ReceivingRecord]:
        """Get receiving records for a specific supplier."""
        since_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = self.db.query(ReceivingRecord).filter(
            and_(
                ReceivingRecord.supplier_id == supplier_id,
                ReceivingRecord.created_at >= since_date
            )
        )
        query = self._apply_company_filter(query, ReceivingRecord)
        query = query.order_by(desc(ReceivingRecord.created_at))
        
        return query.limit(limit).all()
    
    def get_receipts_by_status(self, status: ReceivingStatus,
                              limit: int = 100) -> List[ReceivingRecord]:
        """Get receiving records by status."""
        query = self.db.query(ReceivingRecord).filter(
            ReceivingRecord.status == status
        )
        query = self._apply_company_filter(query, ReceivingRecord)
        query = query.order_by(desc(ReceivingRecord.created_at))
        
        return query.limit(limit).all()
    
    def search_receipts(self, search_term: str, limit: int = 50) -> List[ReceivingRecord]:
        """Search receiving records by various criteria."""
        search_fields = ['receipt_number', 'source_document_number', 'supplier_invoice_number']
        
        query = self.db.query(ReceivingRecord)
        
        # Apply text search
        search_conditions = []
        for field in search_fields:
            if hasattr(ReceivingRecord, field):
                field_attr = getattr(ReceivingRecord, field)
                search_conditions.append(field_attr.ilike(f"%{search_term}%"))
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        query = self._apply_company_filter(query, ReceivingRecord)
        query = query.order_by(desc(ReceivingRecord.created_at))
        
        return query.limit(limit).all()
    
    def calculate_receiving_statistics(self, days_back: int = 30) -> Dict[str, Any]:
        """Calculate receiving statistics for reporting."""
        since_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Overall statistics
        query = self.db.query(
            func.count(ReceivingRecord.id).label('total_receipts'),
            func.sum(ReceivingRecord.total_quantity_expected).label('total_expected'),
            func.sum(ReceivingRecord.total_quantity_received).label('total_received'),
            func.sum(ReceivingRecord.total_value_received).label('total_value')
        ).filter(ReceivingRecord.created_at >= since_date)
        
        query = self._apply_company_filter(query, ReceivingRecord)
        overall = query.first()
        
        # Status breakdown
        status_query = self.db.query(
            ReceivingRecord.status,
            func.count(ReceivingRecord.id).label('count')
        ).filter(ReceivingRecord.created_at >= since_date)
        
        status_query = self._apply_company_filter(status_query, ReceivingRecord)
        status_query = status_query.group_by(ReceivingRecord.status)
        status_results = status_query.all()
        
        status_breakdown = {
            result.status.value: result.count for result in status_results
        }
        
        return {
            'period_days': days_back,
            'total_receipts': overall.total_receipts or 0,
            'total_quantity_expected': float(overall.total_expected or 0),
            'total_quantity_received': float(overall.total_received or 0),
            'total_value_received': float(overall.total_value or 0),
            'status_breakdown': status_breakdown,
            'completion_rate': (
                float(overall.total_received / overall.total_expected * 100)
                if overall.total_expected else 0
            )
        }
    
    def _generate_receipt_number(self, prefix: str = "REC") -> str:
        """Generate unique receipt number."""
        # In production, would use company settings and sequence numbers
        import time
        timestamp = int(time.time())
        return f"{prefix}{timestamp:08d}"