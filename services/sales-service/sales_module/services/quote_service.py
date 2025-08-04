"""
Quote service for managing sales quotes and proposals.

Provides business logic for quote management including
quote creation, pricing, approval workflows, and conversion to orders.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from .base_service import BaseService
from sales_module.models import (
    SalesQuote, SalesQuoteLineItem, QuoteVersion, QuoteApproval,
    QuoteStatus, ApprovalStatus
)


class QuoteService(BaseService):
    """
    Quote service for comprehensive sales quote management.
    
    Handles quote lifecycle, pricing calculations, approval workflows,
    versioning, and conversion to orders.
    """
    
    def __init__(self, db_session=None):
        """Initialize quote service."""
        super().__init__(db_session)
        self.model_class = SalesQuote
    
    def create_quote(self, quote_data: Dict[str, Any], line_items: List[Dict[str, Any]] = None,
                    user_id: int = None, company_id: int = None) -> SalesQuote:
        """
        Create new quote with line items and pricing calculations.
        
        Args:
            quote_data: Quote information
            line_items: List of line item data
            user_id: ID of user creating the quote
            company_id: Company ID for multi-company isolation
            
        Returns:
            Created quote instance
        """
        # Generate quote number if not provided
        if 'quote_number' not in quote_data or not quote_data['quote_number']:
            quote_data['quote_number'] = self.generate_quote_number()
        
        # Set default validity period if not provided
        if 'valid_until' not in quote_data:
            quote_data['valid_until'] = datetime.utcnow() + timedelta(days=30)
        
        # Set prepared by user
        quote_data['prepared_by_user_id'] = user_id
        
        # Create quote
        quote = self.create(quote_data, user_id, company_id)
        
        # Add line items if provided
        if line_items:
            for item_data in line_items:
                self.add_line_item(quote.id, item_data, user_id, company_id)
        
        # Calculate totals
        self.calculate_quote_totals(quote.id, company_id)
        
        return quote
    
    def add_line_item(self, quote_id: int, line_item_data: Dict[str, Any],
                     user_id: int = None, company_id: int = None) -> Optional[SalesQuoteLineItem]:
        """
        Add line item to quote.
        
        Args:
            quote_id: Quote ID
            line_item_data: Line item information
            user_id: ID of user adding the line item
            company_id: Company ID for isolation
            
        Returns:
            Created line item instance or None if quote not found
        """
        quote = self.get_by_id(quote_id, company_id)
        if not quote:
            return None
        
        # Set quote relationship
        line_item_data['quote_id'] = quote_id
        line_item_data['company_id'] = company_id
        
        # Set line number if not provided
        if 'line_number' not in line_item_data:
            # In production, would get next line number from database
            line_item_data['line_number'] = 1
        
        # Create line item
        line_item = SalesQuoteLineItem(**line_item_data)
        
        # Calculate line totals
        line_item.calculate_line_total()
        
        line_item.save(self.db_session, user_id)
        
        # Recalculate quote totals
        self.calculate_quote_totals(quote_id, company_id)
        
        return line_item
    
    def update_line_item_pricing(self, line_item_id: int, new_unit_price: Decimal,
                               discount_percentage: Decimal = None, user_id: int = None,
                               company_id: int = None) -> Optional[SalesQuoteLineItem]:
        """
        Update line item pricing and recalculate totals.
        
        Args:
            line_item_id: Line item ID
            new_unit_price: New unit price
            discount_percentage: New discount percentage
            user_id: ID of user making the change
            company_id: Company ID for isolation
            
        Returns:
            Updated line item instance or None if not found
        """
        # In production, would fetch line item from database
        # For now, simulate the update process
        
        print(f"Quote Service: Updating line item {line_item_id} pricing")
        print(f"New unit price: {new_unit_price}")
        if discount_percentage:
            print(f"New discount: {discount_percentage}%")
        
        # Would update pricing and recalculate totals
        return None  # Would return actual updated line item
    
    def calculate_quote_totals(self, quote_id: int, company_id: int = None) -> Optional[SalesQuote]:
        """
        Calculate and update quote totals from line items.
        
        Args:
            quote_id: Quote ID
            company_id: Company ID for isolation
            
        Returns:
            Updated quote instance or None if not found
        """
        quote = self.get_by_id(quote_id, company_id)
        if not quote:
            return None
        
        # In production, would:
        # 1. Sum all line item totals for subtotal
        # 2. Apply overall discount
        # 3. Calculate tax based on customer location and products
        # 4. Add shipping charges
        # 5. Calculate final total
        # 6. Update margin calculations if costs available
        
        quote.calculate_totals()
        quote.save(self.db_session)
        
        return quote
    
    def apply_overall_discount(self, quote_id: int, discount_percentage: Decimal,
                             user_id: int = None, company_id: int = None) -> Optional[SalesQuote]:
        """
        Apply overall discount to quote.
        
        Args:
            quote_id: Quote ID
            discount_percentage: Discount percentage to apply
            user_id: ID of user applying discount
            company_id: Company ID for isolation
            
        Returns:
            Updated quote instance or None if not found
        """
        quote = self.get_by_id(quote_id, company_id)
        if not quote:
            return None
        
        quote.apply_overall_discount(discount_percentage)
        quote.save(self.db_session, user_id)
        
        return quote
    
    def send_quote_to_customer(self, quote_id: int, email_template: str = None,
                              user_id: int = None, company_id: int = None) -> Optional[SalesQuote]:
        """
        Send quote to customer via email.
        
        Args:
            quote_id: Quote ID
            email_template: Email template to use
            user_id: ID of user sending the quote
            company_id: Company ID for isolation
            
        Returns:
            Updated quote instance or None if not found
        """
        quote = self.get_by_id(quote_id, company_id)
        if not quote:
            return None
        
        # Validate quote is ready to send
        if quote.status != QuoteStatus.APPROVED and quote.requires_approval:
            raise ValueError("Quote must be approved before sending to customer")
        
        quote.send_to_customer(user_id, email_template)
        
        return quote
    
    def create_quote_version(self, quote_id: int, reason: str = None,
                           user_id: int = None, company_id: int = None) -> Optional[QuoteVersion]:
        """
        Create new version of quote for revision tracking.
        
        Args:
            quote_id: Quote ID
            reason: Reason for creating new version
            user_id: ID of user creating version
            company_id: Company ID for isolation
            
        Returns:
            Created quote version instance or None if quote not found
        """
        quote = self.get_by_id(quote_id, company_id)
        if not quote:
            return None
        
        version = quote.create_new_version(user_id, reason)
        return version
    
    def request_quote_approval(self, quote_id: int, approval_level: int = 1,
                             request_reason: str = None, urgency: str = "normal",
                             user_id: int = None, company_id: int = None) -> Optional[QuoteApproval]:
        """
        Request approval for quote.
        
        Args:
            quote_id: Quote ID
            approval_level: Level of approval required
            request_reason: Reason for approval request
            urgency: Urgency level (low, normal, high, urgent)
            user_id: ID of user requesting approval
            company_id: Company ID for isolation
            
        Returns:
            Created approval request instance or None if quote not found
        """
        quote = self.get_by_id(quote_id, company_id)
        if not quote:
            return None
        
        # Create approval request
        approval_data = {
            'quote_id': quote_id,
            'company_id': company_id,
            'approval_level': approval_level,
            'requested_by_user_id': user_id,
            'assigned_to_user_id': self.get_approver_for_level(approval_level, company_id),
            'request_reason': request_reason,
            'urgency_level': urgency,
            'discount_percentage': quote.overall_discount_percentage,
            'quote_total': quote.total_amount,
            'margin_percentage': quote.margin_percentage,
            'due_date': datetime.utcnow() + timedelta(hours=24)  # Default 24-hour SLA
        }
        
        approval = QuoteApproval(**approval_data)
        approval.save(self.db_session, user_id)
        
        # Update quote status
        quote.status = QuoteStatus.PENDING_APPROVAL
        quote.save(self.db_session, user_id)
        
        return approval
    
    def approve_quote(self, approval_id: int, approver_notes: str = None,
                     user_id: int = None, company_id: int = None) -> Optional[QuoteApproval]:
        """
        Approve quote approval request.
        
        Args:
            approval_id: Approval request ID
            approver_notes: Approval notes
            user_id: ID of user approving
            company_id: Company ID for isolation
            
        Returns:
            Updated approval instance or None if not found
        """
        # In production, would fetch approval from database
        print(f"Quote Service: Approving quote approval {approval_id}")
        
        # Would:
        # 1. Update approval status to approved
        # 2. Update quote status to approved
        # 3. Log audit trail
        # 4. Send notifications
        
        return None  # Would return actual approval instance
    
    def reject_quote_approval(self, approval_id: int, rejection_reason: str,
                            user_id: int = None, company_id: int = None) -> Optional[QuoteApproval]:
        """
        Reject quote approval request.
        
        Args:
            approval_id: Approval request ID
            rejection_reason: Reason for rejection
            user_id: ID of user rejecting
            company_id: Company ID for isolation
            
        Returns:
            Updated approval instance or None if not found
        """
        # In production, would fetch approval from database
        print(f"Quote Service: Rejecting quote approval {approval_id}")
        print(f"Rejection reason: {rejection_reason}")
        
        return None  # Would return actual approval instance
    
    def convert_quote_to_order(self, quote_id: int, order_data: Dict[str, Any] = None,
                              user_id: int = None, company_id: int = None) -> Dict[str, Any]:
        """
        Convert accepted quote to sales order.
        
        Args:
            quote_id: Quote ID to convert
            order_data: Additional order information
            user_id: ID of user converting quote
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with conversion results
        """
        quote = self.get_by_id(quote_id, company_id)
        if not quote:
            return {"success": False, "error": "Quote not found"}
        
        # Validate quote can be converted
        if quote.status != QuoteStatus.ACCEPTED:
            return {"success": False, "error": "Quote must be accepted to convert to order"}
        
        # In production, would:
        # 1. Create sales order from quote data
        # 2. Copy all line items to order
        # 3. Set up order workflow
        # 4. Update quote status to converted
        # 5. Link quote to order
        
        print(f"Quote Service: Converting quote {quote.quote_number} to order")
        
        # Simulate order creation
        order_id = 12345  # Would be actual order ID
        
        quote.convert_to_order(user_id, order_id)
        
        return {
            "success": True,
            "order_id": order_id,
            "quote_id": quote_id,
            "message": f"Quote {quote.quote_number} successfully converted to order"
        }
    
    def extend_quote_validity(self, quote_id: int, additional_days: int,
                            user_id: int = None, company_id: int = None) -> Optional[SalesQuote]:
        """
        Extend quote validity period.
        
        Args:
            quote_id: Quote ID
            additional_days: Number of days to extend
            user_id: ID of user extending validity
            company_id: Company ID for isolation
            
        Returns:
            Updated quote instance or None if not found
        """
        quote = self.get_by_id(quote_id, company_id)
        if not quote:
            return None
        
        quote.extend_validity(additional_days, user_id)
        return quote
    
    def get_quote_analytics(self, company_id: int = None, 
                          date_range: Dict[str, datetime] = None) -> Dict[str, Any]:
        """
        Get quote analytics and metrics.
        
        Args:
            company_id: Company ID for isolation
            date_range: Date range for analytics
            
        Returns:
            Dictionary with analytics data
        """
        # In production, would query aggregated data from database
        return {
            "summary": {
                "total_quotes": 0,
                "quotes_sent": 0,
                "quotes_accepted": 0,
                "quotes_rejected": 0,
                "quotes_expired": 0,
                "quotes_converted": 0
            },
            "conversion_metrics": {
                "quote_to_order_rate": 0.0,
                "average_quote_value": 0.0,
                "average_time_to_close": 0,  # days
                "win_rate": 0.0
            },
            "by_status": {
                "draft": 0,
                "pending_approval": 0,
                "approved": 0,
                "sent": 0,
                "accepted": 0,
                "rejected": 0,
                "expired": 0,
                "converted": 0
            },
            "approval_metrics": {
                "quotes_requiring_approval": 0,
                "average_approval_time": 0,  # hours
                "approval_rate": 0.0
            },
            "top_quotes": [],  # Top quotes by value
            "quote_trends": []  # Quote volume over time
        }
    
    # Utility methods
    
    def get_approver_for_level(self, approval_level: int, company_id: int) -> int:
        """Get appropriate approver user ID for approval level."""
        # In production, would query approval hierarchy
        return 1  # Would return actual approver user ID
    
    def generate_quote_number(self, prefix: str = "QUO") -> str:
        """Generate unique quote number."""
        return self.generate_number(prefix, "quote_sequence")
    
    # Validation overrides
    
    def validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validate quote creation data."""
        required_fields = ['title', 'customer_id']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Field '{field}' is required for quote creation")
        
        # Validate validity dates
        if 'valid_until' in data and 'valid_from' in data:
            if data['valid_until'] <= data['valid_from']:
                raise ValueError("Valid until date must be after valid from date")
    
    def validate_update_data(self, data: Dict[str, Any], quote: SalesQuote) -> None:
        """Validate quote update data."""
        # Don't allow changing quote number
        if 'quote_number' in data and data['quote_number'] != quote.quote_number:
            raise ValueError("Quote number cannot be changed after creation")
        
        # Don't allow editing converted quotes
        if quote.status == QuoteStatus.CONVERTED:
            raise ValueError("Cannot edit quotes that have been converted to orders")