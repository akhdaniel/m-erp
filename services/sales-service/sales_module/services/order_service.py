"""
Order service for managing sales orders and fulfillment.

Provides business logic for order processing including
order lifecycle, fulfillment, shipping, invoicing, and payments.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from .base_service import BaseService
from sales_module.models import (
    SalesOrder, SalesOrderLineItem, OrderShipment, OrderInvoice,
    OrderStatus, PaymentStatus, ShipmentStatus, InvoiceStatus
)


class OrderService(BaseService):
    """
    Order service for comprehensive sales order management.
    
    Handles order lifecycle from creation through fulfillment,
    shipping, invoicing, and payment collection.
    """
    
    def __init__(self, db_session=None):
        """Initialize order service."""
        super().__init__(db_session)
        self.model_class = SalesOrder
    
    def create_order(self, order_data: Dict[str, Any], line_items: List[Dict[str, Any]] = None,
                    user_id: int = None, company_id: int = None) -> SalesOrder:
        """
        Create new sales order with line items.
        
        Args:
            order_data: Order information
            line_items: List of line item data
            user_id: ID of user creating the order
            company_id: Company ID for multi-company isolation
            
        Returns:
            Created order instance
        """
        # Generate order number if not provided
        if 'order_number' not in order_data or not order_data['order_number']:
            order_data['order_number'] = self.generate_order_number()
        
        # Set order date if not provided
        if 'order_date' not in order_data:
            order_data['order_date'] = datetime.utcnow()
        
        # Set sales rep if not provided
        if 'sales_rep_user_id' not in order_data:
            order_data['sales_rep_user_id'] = user_id
        
        # Create order
        order = self.create(order_data, user_id, company_id)
        
        # Add line items if provided
        if line_items:
            for item_data in line_items:
                self.add_line_item(order.id, item_data, user_id, company_id)
        
        # Calculate totals
        self.calculate_order_totals(order.id, company_id)
        
        return order
    
    def create_order_from_quote(self, quote_id: int, order_data: Dict[str, Any] = None,
                               user_id: int = None, company_id: int = None) -> SalesOrder:
        """
        Create order from accepted quote.
        
        Args:
            quote_id: Quote ID to convert
            order_data: Additional order data
            user_id: ID of user creating order
            company_id: Company ID for isolation
            
        Returns:
            Created order instance
        """
        # In production, would fetch quote and validate
        print(f"Order Service: Creating order from quote {quote_id}")
        
        # Would copy quote data to order
        base_order_data = {
            'quote_id': quote_id,
            'title': f"Order from Quote {quote_id}",
            'customer_id': 1,  # Would get from quote
            # Copy other relevant fields from quote
        }
        
        # Merge with provided order data
        if order_data:
            base_order_data.update(order_data)
        
        return self.create_order(base_order_data, None, user_id, company_id)
    
    def add_line_item(self, order_id: int, line_item_data: Dict[str, Any],
                     user_id: int = None, company_id: int = None) -> Optional[SalesOrderLineItem]:
        """
        Add line item to order.
        
        Args:
            order_id: Order ID
            line_item_data: Line item information
            user_id: ID of user adding the line item
            company_id: Company ID for isolation
            
        Returns:
            Created line item instance or None if order not found
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            return None
        
        # Validate order can be modified
        if order.status not in [OrderStatus.DRAFT, OrderStatus.PENDING]:
            raise ValueError("Cannot add line items to confirmed orders")
        
        # Set order relationship
        line_item_data['order_id'] = order_id
        line_item_data['company_id'] = company_id
        
        # Set line number if not provided
        if 'line_number' not in line_item_data:
            # In production, would get next line number from database
            line_item_data['line_number'] = 1
        
        # Create line item
        line_item = SalesOrderLineItem(**line_item_data)
        
        # Calculate line totals
        line_item.calculate_line_total()
        
        line_item.save(self.db_session, user_id)
        
        # Recalculate order totals
        self.calculate_order_totals(order_id, company_id)
        
        return line_item
    
    def calculate_order_totals(self, order_id: int, company_id: int = None) -> Optional[SalesOrder]:
        """
        Calculate and update order totals from line items.
        
        Args:
            order_id: Order ID
            company_id: Company ID for isolation
            
        Returns:
            Updated order instance or None if not found
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            return None
        
        order.calculate_totals()
        order.save(self.db_session)
        
        # Update item counts for fulfillment tracking
        # In production, would sum from actual line items
        order.items_remaining = 10  # Would calculate from line items
        
        return order
    
    def confirm_order(self, order_id: int, user_id: int = None, 
                     company_id: int = None) -> Optional[SalesOrder]:
        """
        Confirm order and start fulfillment process.
        
        Args:
            order_id: Order ID
            user_id: ID of user confirming order
            company_id: Company ID for isolation
            
        Returns:
            Updated order instance or None if not found
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            return None
        
        # Validate order can be confirmed
        if order.status != OrderStatus.DRAFT:
            raise ValueError("Only draft orders can be confirmed")
        
        order.confirm_order(user_id)
        
        # In production, would trigger fulfillment workflows:
        # - Reserve inventory
        # - Create production orders if needed
        # - Schedule shipments
        # - Generate pick lists
        
        return order
    
    def ship_order_items(self, order_id: int, shipment_data: Dict[str, Any],
                        line_item_shipments: List[Dict[str, Any]],
                        user_id: int = None, company_id: int = None) -> Optional[OrderShipment]:
        """
        Ship order items and create shipment record.
        
        Args:
            order_id: Order ID
            shipment_data: Shipment information
            line_item_shipments: List of line items and quantities being shipped
            user_id: ID of user creating shipment
            company_id: Company ID for isolation
            
        Returns:
            Created shipment instance or None if order not found
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            return None
        
        # Validate order can be shipped
        if order.status not in [OrderStatus.CONFIRMED, OrderStatus.IN_PRODUCTION, 
                               OrderStatus.READY_TO_SHIP, OrderStatus.PARTIALLY_SHIPPED]:
            raise ValueError("Order must be confirmed before shipping")
        
        # Create shipment
        shipment_data.update({
            'order_id': order_id,
            'company_id': company_id,
            'shipment_number': self.generate_shipment_number()
        })
        
        shipment = OrderShipment(**shipment_data)
        shipment.save(self.db_session, user_id)
        
        # Update line item quantities
        total_items_shipped = 0
        for item_shipment in line_item_shipments:
            line_item_id = item_shipment['line_item_id']
            quantity_shipped = item_shipment['quantity_shipped']
            
            # In production, would update actual line item
            print(f"Shipping {quantity_shipped} of line item {line_item_id}")
            total_items_shipped += quantity_shipped
        
        # Update order status and counts
        order.items_shipped += total_items_shipped
        order.items_remaining -= total_items_shipped
        order.shipment_count += 1
        
        # Update order status based on fulfillment
        if order.items_remaining <= 0:
            order.status = OrderStatus.SHIPPED
            order.shipped_date = datetime.utcnow()
        else:
            order.status = OrderStatus.PARTIALLY_SHIPPED
        
        order.save(self.db_session, user_id)
        
        return shipment
    
    def update_shipment_tracking(self, shipment_id: int, tracking_number: str,
                               carrier: str = None, user_id: int = None,
                               company_id: int = None) -> Optional[OrderShipment]:
        """
        Update shipment with tracking information.
        
        Args:
            shipment_id: Shipment ID
            tracking_number: Carrier tracking number
            carrier: Carrier name
            user_id: ID of user updating tracking
            company_id: Company ID for isolation
            
        Returns:
            Updated shipment instance or None if not found
        """
        # In production, would fetch shipment from database
        print(f"Order Service: Updating shipment {shipment_id} tracking")
        print(f"Tracking number: {tracking_number}")
        
        # Would update shipment and possibly order status
        return None  # Would return actual shipment
    
    def mark_shipment_delivered(self, shipment_id: int, delivered_to: str = None,
                              user_id: int = None, company_id: int = None) -> Optional[OrderShipment]:
        """
        Mark shipment as delivered.
        
        Args:
            shipment_id: Shipment ID
            delivered_to: Person/entity who received delivery
            user_id: ID of user marking as delivered
            company_id: Company ID for isolation
            
        Returns:
            Updated shipment instance or None if not found
        """
        # In production, would fetch shipment and related order
        print(f"Order Service: Marking shipment {shipment_id} as delivered")
        
        # Would:
        # 1. Update shipment status to delivered
        # 2. Update order status if all shipments delivered
        # 3. Trigger post-delivery workflows
        
        return None  # Would return actual shipment
    
    def create_invoice(self, order_id: int, invoice_data: Dict[str, Any] = None,
                      user_id: int = None, company_id: int = None) -> Optional[OrderInvoice]:
        """
        Create invoice for order or partial order.
        
        Args:
            order_id: Order ID
            invoice_data: Additional invoice data
            user_id: ID of user creating invoice
            company_id: Company ID for isolation
            
        Returns:
            Created invoice instance or None if order not found
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            return None
        
        # Prepare invoice data
        base_invoice_data = {
            'order_id': order_id,
            'company_id': company_id,
            'invoice_number': self.generate_invoice_number(),
            'subtotal': order.subtotal,
            'tax_amount': order.tax_amount,
            'discount_amount': order.discount_amount,
            'total_amount': order.total_amount,
            'outstanding_amount': order.total_amount,
            'currency_code': order.currency_code,
            'payment_terms_days': order.payment_terms_days,
            'due_date': datetime.utcnow() + timedelta(days=order.payment_terms_days),
            'line_items_data': [],  # Would snapshot line items
            'billing_address': order.billing_address
        }
        
        # Merge with provided data
        if invoice_data:
            base_invoice_data.update(invoice_data)
        
        # Create invoice
        invoice = OrderInvoice(**base_invoice_data)
        invoice.save(self.db_session, user_id)
        
        return invoice
    
    def send_invoice(self, invoice_id: int, email_template: str = None,
                    user_id: int = None, company_id: int = None) -> Optional[OrderInvoice]:
        """
        Send invoice to customer.
        
        Args:
            invoice_id: Invoice ID
            email_template: Email template to use
            user_id: ID of user sending invoice
            company_id: Company ID for isolation
            
        Returns:
            Updated invoice instance or None if not found
        """
        # In production, would fetch invoice
        print(f"Order Service: Sending invoice {invoice_id}")
        
        # Would send via email service and update status
        return None  # Would return actual invoice
    
    def record_payment(self, order_id: int, payment_amount: Decimal, 
                      payment_method: str = None, invoice_id: int = None,
                      user_id: int = None, company_id: int = None) -> Optional[SalesOrder]:
        """
        Record payment against order.
        
        Args:
            order_id: Order ID
            payment_amount: Payment amount
            payment_method: Payment method used
            invoice_id: Specific invoice ID if paying specific invoice
            user_id: ID of user recording payment
            company_id: Company ID for isolation
            
        Returns:
            Updated order instance or None if not found
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            return None
        
        order.record_payment(payment_amount, payment_method, user_id)
        
        # Update related invoice if specified
        if invoice_id:
            # In production, would update specific invoice
            print(f"Recording payment against invoice {invoice_id}")
        
        return order
    
    def cancel_order(self, order_id: int, reason: str, user_id: int = None,
                    company_id: int = None) -> Optional[SalesOrder]:
        """
        Cancel order and handle cleanup.
        
        Args:
            order_id: Order ID
            reason: Cancellation reason
            user_id: ID of user cancelling order
            company_id: Company ID for isolation
            
        Returns:
            Updated order instance or None if not found
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            return None
        
        # Validate order can be cancelled
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.COMPLETED]:
            raise ValueError("Cannot cancel orders that have been shipped or completed")
        
        order.cancel_order(reason, user_id)
        
        # In production, would handle:
        # - Release reserved inventory
        # - Cancel production orders
        # - Cancel shipments
        # - Process refunds if needed
        
        return order
    
    def put_order_on_hold(self, order_id: int, reason: str, user_id: int = None,
                         company_id: int = None) -> Optional[SalesOrder]:
        """
        Put order on hold.
        
        Args:
            order_id: Order ID
            reason: Hold reason
            user_id: ID of user putting order on hold
            company_id: Company ID for isolation
            
        Returns:
            Updated order instance or None if not found
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            return None
        
        order.put_on_hold(reason, user_id)
        return order
    
    def release_order_hold(self, order_id: int, user_id: int = None,
                          company_id: int = None) -> Optional[SalesOrder]:
        """
        Release order from hold.
        
        Args:
            order_id: Order ID
            user_id: ID of user releasing hold
            company_id: Company ID for isolation
            
        Returns:
            Updated order instance or None if not found
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            return None
        
        order.release_hold(user_id)
        return order
    
    def get_order_fulfillment_status(self, order_id: int, 
                                   company_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive order fulfillment status.
        
        Args:
            order_id: Order ID
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with fulfillment status or None if not found
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            return None
        
        return {
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status.value,
            "fulfillment_percentage": order.fulfillment_percentage,
            "payment_percentage": order.payment_percentage,
            "items_shipped": order.items_shipped,
            "items_remaining": order.items_remaining,
            "shipment_count": order.shipment_count,
            "is_overdue": order.is_overdue,
            "days_until_required": order.days_until_required,
            "payment_status": order.payment_status.value,
            "paid_amount": float(order.paid_amount),
            "outstanding_amount": float(order.outstanding_amount),
            "shipments": [],  # Would include actual shipment data
            "invoices": []    # Would include actual invoice data
        }
    
    def get_order_analytics(self, company_id: int = None,
                          date_range: Dict[str, datetime] = None) -> Dict[str, Any]:
        """
        Get order analytics and metrics.
        
        Args:
            company_id: Company ID for isolation
            date_range: Date range for analytics
            
        Returns:
            Dictionary with analytics data
        """
        # In production, would query aggregated data from database
        return {
            "summary": {
                "total_orders": 0,
                "orders_confirmed": 0,
                "orders_shipped": 0,
                "orders_delivered": 0,
                "orders_completed": 0,
                "orders_cancelled": 0
            },
            "financial_metrics": {
                "total_order_value": 0.0,
                "average_order_value": 0.0,
                "total_paid": 0.0,
                "total_outstanding": 0.0
            },
            "fulfillment_metrics": {
                "average_fulfillment_time": 0,  # days
                "on_time_delivery_rate": 0.0,
                "average_shipping_time": 0,  # days
                "orders_on_hold": 0
            },
            "by_status": {
                "draft": 0,
                "pending": 0,
                "confirmed": 0,
                "in_production": 0,
                "ready_to_ship": 0,
                "partially_shipped": 0,
                "shipped": 0,
                "delivered": 0,
                "completed": 0,
                "cancelled": 0,
                "on_hold": 0
            },
            "top_orders": [],     # Top orders by value
            "order_trends": []    # Order volume over time
        }
    
    # Utility methods
    
    def generate_order_number(self, prefix: str = "SO") -> str:
        """Generate unique order number."""
        return self.generate_number(prefix, "order_sequence")
    
    def generate_shipment_number(self, prefix: str = "SHIP") -> str:
        """Generate unique shipment number."""
        return self.generate_number(prefix, "shipment_sequence")
    
    def generate_invoice_number(self, prefix: str = "INV") -> str:
        """Generate unique invoice number."""
        return self.generate_number(prefix, "invoice_sequence")
    
    # Validation overrides
    
    def validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validate order creation data."""
        required_fields = ['title', 'customer_id']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Field '{field}' is required for order creation")
        
        # Validate dates
        if 'required_date' in data and 'order_date' in data:
            if data['required_date'] < data['order_date']:
                raise ValueError("Required date cannot be before order date")
    
    def validate_update_data(self, data: Dict[str, Any], order: SalesOrder) -> None:
        """Validate order update data."""
        # Don't allow changing order number
        if 'order_number' in data and data['order_number'] != order.order_number:
            raise ValueError("Order number cannot be changed after creation")
        
        # Don't allow editing completed/cancelled orders
        if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            raise ValueError("Cannot edit completed or cancelled orders")