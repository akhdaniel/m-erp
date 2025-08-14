"""
Quote service for managing sales quotes and proposals.

Provides business logic for quote management including
quote creation, pricing, approval workflows, and conversion to orders.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

from .base_service import BaseService
from sales_module.models import (
    SalesQuote, SalesQuoteLineItem, QuoteVersion, QuoteApproval,
    QuoteStatus, ApprovalStatus
)
from sales_module.integrations.inventory_client import inventory_client
from sales_module.messaging.event_publisher import sales_event_publisher


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
        
        # Publish quote created event
        self._publish_quote_event("created", quote, user_id, company_id)
        
        return quote
    
    def add_line_item(self, quote_id: int, line_item_data: Dict[str, Any],
                     user_id: int = None, company_id: int = None) -> Optional[SalesQuoteLineItem]:
        """
        Add line item to quote with inventory integration.
        
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
        
        # Enhanced inventory integration
        if 'product_id' in line_item_data and line_item_data['product_id']:
            product_info = self._get_product_information(
                line_item_data['product_id'], 
                company_id,
                quote.customer_id if hasattr(quote, 'customer_id') else None
            )
            
            if product_info:
                # Auto-populate product information
                line_item_data.setdefault('item_name', product_info.get('name', ''))
                line_item_data.setdefault('item_code', product_info.get('code', ''))
                line_item_data.setdefault('description', product_info.get('description', ''))
                line_item_data.setdefault('unit_of_measure', product_info.get('unit_of_measure', 'each'))
                
                # Set pricing from inventory if not provided
                if 'unit_price' not in line_item_data and 'list_price' in product_info:
                    line_item_data['unit_price'] = Decimal(str(product_info['list_price']))
                if 'unit_cost' not in line_item_data and 'cost_price' in product_info:
                    line_item_data['unit_cost'] = Decimal(str(product_info['cost_price']))
        
        # Set quote relationship
        line_item_data['quote_id'] = quote_id
        line_item_data['company_id'] = company_id
        
        # Set line number if not provided
        if 'line_number' not in line_item_data:
            # In production, would get next line number from database
            line_item_data['line_number'] = self._get_next_line_number(quote_id, company_id)
        
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
        # In production, would fetch line item from database:
        # line_item = self.db_session.query(SalesQuoteLineItem).filter(
        #     SalesQuoteLineItem.id == line_item_id,
        #     SalesQuoteLineItem.company_id == company_id,
        #     SalesQuoteLineItem.is_active == True
        # ).first()
        
        # For now, create a mock line item for demonstration
        line_item = SalesQuoteLineItem(
            id=line_item_id,
            company_id=company_id,
            quote_id=1,  # Would be actual quote ID
            line_number=1,
            item_name="Mock Product",
            quantity=Decimal("1.0"),
            unit_price=new_unit_price,
            line_total=new_unit_price
        )
        
        # Update pricing
        line_item.update_pricing(new_unit_price, recalculate=True)
        
        # Apply discount if provided
        if discount_percentage:
            line_item.apply_discount(discount_percentage=discount_percentage)
        
        # Save changes
        line_item.save(self.db_session, user_id)
        
        # Recalculate quote totals
        if hasattr(line_item, 'quote_id'):
            self.calculate_quote_totals(line_item.quote_id, company_id)
        
        return line_item
    
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
        
        # Publish quote sent event
        self._publish_quote_event("sent", quote, user_id, company_id)
        
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
        # In production, would fetch approval from database:
        # approval = self.db_session.query(QuoteApproval).filter(
        #     QuoteApproval.id == approval_id,
        #     QuoteApproval.company_id == company_id,
        #     QuoteApproval.status == ApprovalStatus.PENDING
        # ).first()
        
        # For demonstration, create mock approval
        approval = QuoteApproval(
            id=approval_id,
            company_id=company_id,
            quote_id=1,  # Would be actual quote ID
            approval_level=1,
            requested_by_user_id=1,
            assigned_to_user_id=user_id,
            status=ApprovalStatus.PENDING
        )
        
        if not approval:
            return None
        
        # Validate user has permission to approve
        if approval.assigned_to_user_id != user_id and not self._user_can_escalate_approval(user_id, approval.approval_level):
            raise ValueError("User not authorized to approve this request")
        
        # Approve the request
        approval.approve(user_id, approver_notes)
        
        # Publish approval event
        self._publish_approval_event("approved", approval, user_id, company_id)
        
        # Update quote status if this was the final approval
        if self._is_final_approval(approval):
            quote = self.get_by_id(approval.quote_id, company_id)
            if quote:
                quote.status = QuoteStatus.APPROVED
                quote.approved_by_user_id = user_id
                quote.save(self.db_session, user_id)
                
                # Publish quote approved event
                self._publish_quote_event("approved", quote, user_id, company_id)
        
        return approval
    
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
        # For demonstration, create mock approval
        approval = QuoteApproval(
            id=approval_id,
            company_id=company_id,
            quote_id=1,  # Would be actual quote ID
            approval_level=1,
            requested_by_user_id=1,
            assigned_to_user_id=user_id,
            status=ApprovalStatus.PENDING
        )
        
        if not approval:
            return None
        
        # Validate user has permission to reject
        if approval.assigned_to_user_id != user_id and not self._user_can_escalate_approval(user_id, approval.approval_level):
            raise ValueError("User not authorized to reject this request")
        
        # Reject the request
        approval.reject(user_id, rejection_reason)
        
        # Update quote status back to draft for revision
        quote = self.get_by_id(approval.quote_id, company_id)
        if quote:
            quote.status = QuoteStatus.DRAFT
            quote.save(self.db_session, user_id)
        
        return approval
    
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
    
    # Inventory Integration Methods
    
    def _get_product_information(self, product_id: int, company_id: int, 
                               customer_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Get product information from inventory service.
        
        Args:
            product_id: Product ID
            company_id: Company ID for isolation
            customer_id: Optional customer ID for customer-specific pricing
            
        Returns:
            Product information dictionary or None if not found
        """
        try:
            # Get basic product information
            product_info = inventory_client.get_product_by_id(product_id, company_id)
            if not product_info:
                return None
            
            # Get pricing information
            pricing_info = inventory_client.get_product_pricing(
                product_id, company_id, customer_id
            )
            if pricing_info:
                product_info.update(pricing_info)
            
            return product_info
            
        except Exception as e:
            print(f"Error fetching product information: {e}")
            return None
    
    def check_product_availability(self, product_id: int, quantity: Decimal, 
                                 company_id: int, warehouse_id: int = None) -> Dict[str, Any]:
        """
        Check product availability for quote line item.
        
        Args:
            product_id: Product ID
            quantity: Required quantity
            company_id: Company ID for isolation
            warehouse_id: Optional warehouse ID
            
        Returns:
            Availability information dictionary
        """
        try:
            return inventory_client.check_product_availability(
                product_id, quantity, company_id, warehouse_id
            )
        except Exception as e:
            print(f"Error checking product availability: {e}")
            return {
                "available": False,
                "available_quantity": 0,
                "error": str(e)
            }
    
    def validate_quote_inventory(self, quote_id: int, company_id: int = None) -> Dict[str, Any]:
        """
        Validate inventory availability for all quote line items.
        
        Args:
            quote_id: Quote ID
            company_id: Company ID for isolation
            
        Returns:
            Validation result dictionary
        """
        quote = self.get_by_id(quote_id, company_id)
        if not quote:
            return {"valid": False, "error": "Quote not found"}
        
        validation_results = {
            "valid": True,
            "line_items": [],
            "issues": []
        }
        
        # In production, would iterate through actual line items from database
        # For now, simulate the validation process
        
        # Mock line items for demonstration
        mock_line_items = [
            {"id": 1, "product_id": 100, "quantity": Decimal("2.0"), "item_name": "Product A"},
            {"id": 2, "product_id": 101, "quantity": Decimal("1.0"), "item_name": "Product B"}
        ]
        
        for line_item in mock_line_items:
            if line_item.get('product_id'):
                availability = self.check_product_availability(
                    line_item['product_id'], 
                    line_item['quantity'], 
                    company_id
                )
                
                item_result = {
                    "line_item_id": line_item['id'],
                    "product_id": line_item['product_id'],
                    "item_name": line_item['item_name'],
                    "requested_quantity": line_item['quantity'],
                    "available": availability.get('available', False),
                    "available_quantity": availability.get('available_quantity', 0)
                }
                
                validation_results["line_items"].append(item_result)
                
                if not availability.get('available', False):
                    validation_results["valid"] = False
                    validation_results["issues"].append(
                        f"Insufficient stock for {line_item['item_name']}: "
                        f"requested {line_item['quantity']}, "
                        f"available {availability.get('available_quantity', 0)}"
                    )
        
        return validation_results
    
    def reserve_quote_inventory(self, quote_id: int, company_id: int = None, 
                              expiry_hours: int = 24) -> Dict[str, Any]:
        """
        Reserve inventory for quote line items.
        
        Args:
            quote_id: Quote ID
            company_id: Company ID for isolation
            expiry_hours: Hours until reservations expire
            
        Returns:
            Reservation result dictionary
        """
        quote = self.get_by_id(quote_id, company_id)
        if not quote:
            return {"success": False, "error": "Quote not found"}
        
        reservations = []
        failed_reservations = []
        
        # Mock line items for demonstration
        mock_line_items = [
            {"id": 1, "product_id": 100, "quantity": Decimal("2.0")},
            {"id": 2, "product_id": 101, "quantity": Decimal("1.0")}
        ]
        
        for line_item in mock_line_items:
            if line_item.get('product_id'):
                try:
                    reservation_result = inventory_client.reserve_stock(
                        line_item['product_id'],
                        line_item['quantity'],
                        "quote",
                        quote_id,
                        company_id,
                        expiry_hours=expiry_hours
                    )
                    
                    if reservation_result.get('success', False):
                        reservations.append({
                            "line_item_id": line_item['id'],
                            "product_id": line_item['product_id'],
                            "reservation_id": reservation_result.get('reservation_id'),
                            "quantity": line_item['quantity']
                        })
                    else:
                        failed_reservations.append({
                            "line_item_id": line_item['id'],
                            "product_id": line_item['product_id'],
                            "error": reservation_result.get('error', 'Unknown error')
                        })
                        
                except Exception as e:
                    failed_reservations.append({
                        "line_item_id": line_item['id'],
                        "product_id": line_item['product_id'],
                        "error": str(e)
                    })
        
        return {
            "success": len(failed_reservations) == 0,
            "reservations": reservations,
            "failed_reservations": failed_reservations,
            "quote_id": quote_id
        }
    
    def _get_next_line_number(self, quote_id: int, company_id: int) -> int:
        """
        Get next line number for quote line item.
        
        Args:
            quote_id: Quote ID
            company_id: Company ID for isolation
            
        Returns:
            Next line number
        """
        # In production, would query database:
        # max_line_number = self.db_session.query(func.max(SalesQuoteLineItem.line_number)).filter(
        #     SalesQuoteLineItem.quote_id == quote_id,
        #     SalesQuoteLineItem.company_id == company_id,
        #     SalesQuoteLineItem.is_active == True
        # ).scalar() or 0
        # return max_line_number + 1
        
        # For now, return 1 as placeholder
        return 1
    
    def _user_can_escalate_approval(self, user_id: int, approval_level: int) -> bool:
        """
        Check if user can escalate approval beyond assigned level.
        
        Args:
            user_id: User ID
            approval_level: Current approval level
            
        Returns:
            True if user can escalate, False otherwise
        """
        # In production, would check user roles and permissions
        # For now, simulate escalation rules
        return user_id in [1, 2, 3]  # Mock admin users
    
    def _is_final_approval(self, approval: QuoteApproval) -> bool:
        """
        Check if this is the final approval needed for the quote.
        
        Args:
            approval: Approval instance
            
        Returns:
            True if this is the final approval, False otherwise
        """
        # In production, would check if all required approval levels are complete
        # For now, assume level 1 approvals are final for most quotes
        return approval.approval_level >= 1
    
    def escalate_approval(self, approval_id: int, escalation_reason: str,
                         escalate_to_user_id: int, user_id: int = None,
                         company_id: int = None) -> Optional[QuoteApproval]:
        """
        Escalate approval to higher authority.
        
        Args:
            approval_id: Approval request ID
            escalation_reason: Reason for escalation
            escalate_to_user_id: User ID to escalate to
            user_id: ID of user escalating
            company_id: Company ID for isolation
            
        Returns:
            Updated approval instance or None if not found
        """
        # For demonstration, create mock approval
        approval = QuoteApproval(
            id=approval_id,
            company_id=company_id,
            quote_id=1,
            approval_level=1,
            requested_by_user_id=1,
            assigned_to_user_id=2,
            status=ApprovalStatus.PENDING
        )
        
        if not approval:
            return None
        
        # Escalate the approval
        approval.escalate(escalate_to_user_id, escalation_reason, user_id)
        
        return approval
    
    def get_pending_approvals(self, user_id: int, company_id: int = None) -> List[Dict[str, Any]]:
        """
        Get pending approvals assigned to user.
        
        Args:
            user_id: User ID
            company_id: Company ID for isolation
            
        Returns:
            List of pending approval dictionaries
        """
        # In production, would query database for pending approvals
        # For now, return mock data
        return [
            {
                "approval_id": 1,
                "quote_id": 1,
                "quote_number": "QUO-2025-001",
                "approval_level": 1,
                "requested_by": "John Doe",
                "request_date": datetime.utcnow().isoformat(),
                "due_date": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                "quote_total": "5000.00",
                "discount_percentage": "15.0",
                "urgency_level": "normal",
                "request_reason": "High discount requires approval"
            }
        ]
    
    # Event Publishing Methods
    
    def _publish_quote_event(self, event_type: str, quote: SalesQuote, 
                           user_id: int = None, company_id: int = None) -> None:
        """
        Publish quote-related event.
        
        Args:
            event_type: Type of event
            quote: Quote instance
            user_id: User ID
            company_id: Company ID
        """
        try:
            quote_data = {
                "quote_id": quote.id if hasattr(quote, 'id') else None,
                "quote_number": quote.quote_number if hasattr(quote, 'quote_number') else None,
                "customer_id": quote.customer_id if hasattr(quote, 'customer_id') else None,
                "total_amount": str(quote.total_amount) if hasattr(quote, 'total_amount') else None,
                "status": quote.status.value if hasattr(quote, 'status') else None,
                "currency_code": quote.currency_code if hasattr(quote, 'currency_code') else None
            }
            
            sales_event_publisher.publish_quote_event(
                event_type, quote_data, user_id, company_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish quote event {event_type}: {e}")
    
    def _publish_approval_event(self, event_type: str, approval: QuoteApproval,
                              user_id: int = None, company_id: int = None) -> None:
        """
        Publish approval-related event.
        
        Args:
            event_type: Type of event
            approval: Approval instance
            user_id: User ID
            company_id: Company ID
        """
        try:
            approval_data = {
                "approval_id": approval.id if hasattr(approval, 'id') else None,
                "quote_id": approval.quote_id if hasattr(approval, 'quote_id') else None,
                "approval_level": approval.approval_level if hasattr(approval, 'approval_level') else None,
                "assigned_to_user_id": approval.assigned_to_user_id if hasattr(approval, 'assigned_to_user_id') else None,
                "status": approval.status.value if hasattr(approval, 'status') else None
            }
            
            sales_event_publisher.publish_approval_event(
                event_type, approval_data, user_id, company_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish approval event {event_type}: {e}")
    
    def _publish_inventory_event(self, event_type: str, inventory_data: Dict[str, Any],
                               user_id: int = None, company_id: int = None) -> None:
        """
        Publish inventory-related event.
        
        Args:
            event_type: Type of event
            inventory_data: Inventory data
            user_id: User ID
            company_id: Company ID
        """
        try:
            sales_event_publisher.publish_inventory_event(
                event_type, inventory_data, user_id, company_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish inventory event {event_type}: {e}")