"""
Order service for managing sales orders and fulfillment.

Provides business logic for order processing including
order lifecycle, fulfillment, shipping, invoicing, and payments.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import requests
import logging

from .base_service import BaseService
from sales_module.models import (
    SalesOrder, SalesOrderLineItem, OrderShipment, OrderInvoice,
    OrderStatus, PaymentStatus, ShipmentStatus, InvoiceStatus
)
from sales_module.models.quote import SalesQuote

# Set up logging
logger = logging.getLogger(__name__)


class OrderService(BaseService):
    """
    Order service for comprehensive sales order management.
    
    Handles order lifecycle from creation through fulfillment,
    shipping, invoicing, and payment collection with full
    inventory integration for stock reservation and management.
    """
    
    def __init__(self, db_session=None):
        """Initialize order service."""
        super().__init__(db_session)
        self.model_class = SalesOrder
        
        # Inventory service integration
        self.inventory_service_url = "http://inventory-service:8005"
        self.inventory_timeout = 30
    
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
        Create order from accepted quote with complete data transfer.
        
        Args:
            quote_id: Quote ID to convert
            order_data: Additional order data
            user_id: ID of user creating order
            company_id: Company ID for isolation
            
        Returns:
            Created order instance
        """
        # Fetch the actual quote
        quote = self.db_session.query(SalesQuote).filter(
            SalesQuote.id == quote_id,
            SalesQuote.company_id == company_id
        ).first()
        
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")
        
        if quote.status != "accepted":
            raise ValueError(f"Quote {quote_id} must be accepted before creating order")
        
        # Use the quote model's from_quote method
        order = SalesOrder.from_quote(quote, user_id, **(order_data or {}))
        order.save(self.db_session, user_id)
        
        # Create line items from quote line items
        for quote_line in quote.line_items:
            order_line = SalesOrderLineItem.from_quote_line_item(quote_line, order.id)
            order_line.save(self.db_session, user_id)
        
        # Recalculate totals after adding line items
        order.calculate_totals()
        order.save(self.db_session, user_id)
        
        # Mark quote as converted
        quote.convert_to_order(user_id, order.id)
        quote.save(self.db_session, user_id)
        
        logger.info(f"Created order {order.order_number} from quote {quote.quote_number}")
        
        return order
    
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
        
        # Trigger fulfillment workflows
        try:
            # Reserve inventory for all line items
            self._reserve_order_inventory(order.id, user_id, company_id)
            
            # Update order status to confirmed with inventory reserved
            order.status = OrderStatus.CONFIRMED
            order.save(self.db_session, user_id)
            
            logger.info(f"Order {order.order_number} confirmed with inventory reserved")
            
        except Exception as e:
            # If inventory reservation fails, put order on hold
            order.put_on_hold(f"Inventory reservation failed: {str(e)}", user_id)
            logger.error(f"Failed to reserve inventory for order {order.order_number}: {e}")
            raise ValueError(f"Order confirmed but inventory reservation failed: {e}")
        
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
        
        # Consume inventory for shipped items
        consumption_results = self.consume_order_inventory(
            order_id, line_item_shipments, user_id, company_id
        )
        
        if consumption_results["errors"]:
            logger.warning(f"Inventory consumption errors for order {order.order_number}: {consumption_results['errors']}")
        
        # Update line item quantities
        total_items_shipped = 0
        for item_shipment in line_item_shipments:
            line_item_id = item_shipment['line_item_id']
            quantity_shipped = item_shipment['quantity_shipped']
            
            # Update actual line item shipped quantities
            line_item = next(
                (item for item in order.line_items if item.id == line_item_id),
                None
            )
            if line_item:
                line_item.quantity_shipped = (line_item.quantity_shipped or 0) + quantity_shipped
                line_item.save(self.db_session, user_id)
            
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
        
        # Handle order cancellation workflows
        try:
            # Release reserved inventory
            self.release_order_inventory(order_id, user_id, company_id)
            
            # Cancel any pending shipments (would integrate with shipping service)
            # Process refunds if payments were made (would integrate with payment service)
            # Update related quotes, opportunities, etc.
            
            logger.info(f"Order {order.order_number} cancelled: {reason}")
            
        except Exception as e:
            logger.error(f"Error during order cancellation cleanup: {e}")
            # Order is still cancelled, but cleanup may have failed
        
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
    
    # Inventory Integration Methods
    
    def check_inventory_availability(self, order_id: int, company_id: int = None) -> Dict[str, Any]:
        """
        Check inventory availability for all items in order.
        
        Args:
            order_id: Order ID
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with availability information
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        availability_results = {
            "order_id": order_id,
            "order_number": order.order_number,
            "can_fulfill": True,
            "line_items": [],
            "warnings": [],
            "errors": []
        }
        
        # Check each line item
        for line_item in order.line_items:
            if line_item.product_id:
                availability = self._check_product_availability(
                    line_item.product_id,
                    line_item.quantity,
                    line_item.product_variant_id,
                    company_id
                )
                
                line_result = {
                    "line_item_id": line_item.id,
                    "product_id": line_item.product_id,
                    "product_variant_id": line_item.product_variant_id,
                    "item_name": line_item.item_name,
                    "quantity_requested": float(line_item.quantity),
                    "quantity_available": availability.get("available_quantity", 0),
                    "can_fulfill": availability.get("can_fulfill", False),
                    "locations": availability.get("locations", [])
                }
                
                if not availability.get("can_fulfill", False):
                    availability_results["can_fulfill"] = False
                    shortage = float(line_item.quantity) - availability.get("available_quantity", 0)
                    availability_results["errors"].append(
                        f"Insufficient stock for {line_item.item_name}. "
                        f"Need {line_item.quantity}, available {availability.get('available_quantity', 0)}, "
                        f"shortage {shortage}"
                    )
                
                availability_results["line_items"].append(line_result)
        
        return availability_results
    
    def _check_product_availability(self, product_id: int, quantity: Decimal,
                                  product_variant_id: int = None, company_id: int = None) -> Dict[str, Any]:
        """
        Check availability for a specific product.
        
        Args:
            product_id: Product ID
            quantity: Required quantity
            product_variant_id: Product variant ID (optional)
            company_id: Company ID
            
        Returns:
            Dictionary with availability information
        """
        try:
            # Make API call to inventory service
            params = {
                "product_id": product_id,
                "quantity": str(quantity),
                "company_id": company_id
            }
            
            if product_variant_id:
                params["product_variant_id"] = product_variant_id
            
            response = requests.get(
                f"{self.inventory_service_url}/api/v1/stock/availability",
                params=params,
                timeout=self.inventory_timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Inventory service error: {response.status_code} - {response.text}")
                return {"can_fulfill": False, "available_quantity": 0, "locations": []}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to check inventory availability: {e}")
            return {"can_fulfill": False, "available_quantity": 0, "locations": []}
    
    def _reserve_order_inventory(self, order_id: int, user_id: int = None, company_id: int = None) -> bool:
        """
        Reserve inventory for all items in order.
        
        Args:
            order_id: Order ID
            user_id: User ID performing reservation
            company_id: Company ID
            
        Returns:
            True if successful, raises exception if failed
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        reservations = []
        failed_reservations = []
        
        try:
            # Reserve each line item
            for line_item in order.line_items:
                if line_item.product_id:
                    reservation_data = {
                        "product_id": line_item.product_id,
                        "quantity": str(line_item.quantity),
                        "reservation_reference": f"ORDER-{order.order_number}-LINE-{line_item.line_number}",
                        "reservation_type": "sales_order",
                        "reserved_for_user_id": user_id,
                        "reserved_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                        "notes": f"Reserved for sales order {order.order_number}"
                    }
                    
                    if line_item.product_variant_id:
                        reservation_data["product_variant_id"] = line_item.product_variant_id
                    
                    # Make API call to reserve inventory
                    response = requests.post(
                        f"{self.inventory_service_url}/api/v1/stock/reserve",
                        json=reservation_data,
                        headers={"Content-Type": "application/json"},
                        timeout=self.inventory_timeout
                    )
                    
                    if response.status_code == 201:
                        reservation_result = response.json()
                        reservations.append({
                            "line_item_id": line_item.id,
                            "reservation_id": reservation_result.get("id"),
                            "quantity_reserved": reservation_result.get("quantity")
                        })
                        logger.info(f"Reserved {line_item.quantity} units of product {line_item.product_id} for order {order.order_number}")
                    else:
                        error_msg = f"Failed to reserve {line_item.item_name}: {response.text}"
                        failed_reservations.append(error_msg)
                        logger.error(error_msg)
            
            # If any reservations failed, rollback all
            if failed_reservations:
                self._release_order_reservations(reservations)
                raise ValueError(f"Inventory reservation failed: {'; '.join(failed_reservations)}")
            
            # Store reservation IDs on order for later reference
            order.inventory_reservations = reservations
            order.save(self.db_session, user_id)
            
            return True
            
        except Exception as e:
            # Rollback any successful reservations
            if reservations:
                self._release_order_reservations(reservations)
            raise e
    
    def _release_order_reservations(self, reservations: List[Dict[str, Any]]) -> None:
        """
        Release inventory reservations.
        
        Args:
            reservations: List of reservation dictionaries
        """
        for reservation in reservations:
            if "reservation_id" in reservation:
                try:
                    response = requests.delete(
                        f"{self.inventory_service_url}/api/v1/stock/reservations/{reservation['reservation_id']}",
                        timeout=self.inventory_timeout
                    )
                    if response.status_code == 204:
                        logger.info(f"Released reservation {reservation['reservation_id']}")
                    else:
                        logger.error(f"Failed to release reservation {reservation['reservation_id']}: {response.text}")
                except Exception as e:
                    logger.error(f"Error releasing reservation {reservation['reservation_id']}: {e}")
    
    def release_order_inventory(self, order_id: int, user_id: int = None, company_id: int = None) -> bool:
        """
        Release all inventory reservations for an order.
        
        Args:
            order_id: Order ID
            user_id: User ID performing release
            company_id: Company ID
            
        Returns:
            True if successful
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        if hasattr(order, 'inventory_reservations') and order.inventory_reservations:
            self._release_order_reservations(order.inventory_reservations)
            order.inventory_reservations = []
            order.save(self.db_session, user_id)
            
            logger.info(f"Released all inventory reservations for order {order.order_number}")
        
        return True
    
    def consume_order_inventory(self, order_id: int, shipment_items: List[Dict[str, Any]],
                              user_id: int = None, company_id: int = None) -> Dict[str, Any]:
        """
        Consume inventory for shipped order items.
        
        Args:
            order_id: Order ID
            shipment_items: List of items being shipped with quantities
            user_id: User ID performing consumption
            company_id: Company ID
            
        Returns:
            Dictionary with consumption results
        """
        order = self.get_by_id(order_id, company_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        consumption_results = {
            "order_id": order_id,
            "order_number": order.order_number,
            "consumed_items": [],
            "errors": []
        }
        
        for shipment_item in shipment_items:
            line_item_id = shipment_item.get("line_item_id")
            quantity_shipped = shipment_item.get("quantity_shipped")
            
            # Find the order line item
            line_item = next(
                (item for item in order.line_items if item.id == line_item_id),
                None
            )
            
            if not line_item:
                consumption_results["errors"].append(f"Line item {line_item_id} not found")
                continue
            
            if line_item.product_id:
                try:
                    # Make API call to consume inventory
                    consumption_data = {
                        "product_id": line_item.product_id,
                        "quantity": str(quantity_shipped),
                        "movement_type": "sales_shipment",
                        "reference_number": f"ORDER-{order.order_number}-SHIPMENT",
                        "notes": f"Shipped for sales order {order.order_number}"
                    }
                    
                    if line_item.product_variant_id:
                        consumption_data["product_variant_id"] = line_item.product_variant_id
                    
                    response = requests.post(
                        f"{self.inventory_service_url}/api/v1/stock/consume",
                        json=consumption_data,
                        headers={"Content-Type": "application/json"},
                        timeout=self.inventory_timeout
                    )
                    
                    if response.status_code == 201:
                        consumption_result = response.json()
                        consumption_results["consumed_items"].append({
                            "line_item_id": line_item_id,
                            "product_id": line_item.product_id,
                            "item_name": line_item.item_name,
                            "quantity_consumed": str(quantity_shipped),
                            "movement_id": consumption_result.get("id")
                        })
                        logger.info(f"Consumed {quantity_shipped} units of {line_item.item_name} for order {order.order_number}")
                    else:
                        error_msg = f"Failed to consume inventory for {line_item.item_name}: {response.text}"
                        consumption_results["errors"].append(error_msg)
                        logger.error(error_msg)
                        
                except Exception as e:
                    error_msg = f"Error consuming inventory for {line_item.item_name}: {str(e)}"
                    consumption_results["errors"].append(error_msg)
                    logger.error(error_msg)
        
        return consumption_results
    
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