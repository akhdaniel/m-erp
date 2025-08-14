"""
Tests for sales order models and workflow validation.

Comprehensive test coverage for order processing, fulfillment workflows,
payment tracking, and business rule validation.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from sales_module.models.order import (
    SalesOrder, SalesOrderLineItem, OrderShipment, OrderInvoice,
    OrderStatus, PaymentStatus, ShipmentStatus, InvoiceStatus
)
from sales_module.models.quote import SalesQuote, SalesQuoteLineItem


class TestOrderStatus:
    """Test order status enumeration values."""
    
    def test_order_status_values(self):
        """Test all order status values are defined correctly."""
        expected_statuses = [
            "draft", "pending", "confirmed", "in_production", "ready_to_ship",
            "partially_shipped", "shipped", "delivered", "completed", 
            "cancelled", "on_hold"
        ]
        
        actual_statuses = [status.value for status in OrderStatus]
        assert set(actual_statuses) == set(expected_statuses)
    
    def test_payment_status_values(self):
        """Test all payment status values are defined correctly."""
        expected_statuses = [
            "pending", "authorized", "partially_paid", "paid", 
            "overdue", "refunded", "cancelled"
        ]
        
        actual_statuses = [status.value for status in PaymentStatus]
        assert set(actual_statuses) == set(expected_statuses)
    
    def test_shipment_status_values(self):
        """Test all shipment status values are defined correctly."""
        expected_statuses = [
            "preparing", "ready", "shipped", "in_transit", 
            "out_for_delivery", "delivered", "failed_delivery", "returned"
        ]
        
        actual_statuses = [status.value for status in ShipmentStatus]
        assert set(actual_statuses) == set(expected_statuses)
    
    def test_invoice_status_values(self):
        """Test all invoice status values are defined correctly."""
        expected_statuses = [
            "draft", "sent", "viewed", "paid", "overdue", "cancelled", "refunded"
        ]
        
        actual_statuses = [status.value for status in InvoiceStatus]
        assert set(actual_statuses) == set(expected_statuses)


class TestSalesOrder:
    """Test SalesOrder model functionality."""
    
    def setup_method(self):
        """Set up test data."""
        self.order_data = {
            "company_id": 1,
            "order_number": "SO202500001",
            "title": "Test Order",
            "description": "Test order description",
            "customer_id": 100,
            "sales_rep_user_id": 1,
            "total_amount": Decimal("1000.00"),
            "currency_code": "USD"
        }
    
    def test_order_creation(self):
        """Test basic order creation."""
        order = SalesOrder(**self.order_data)
        
        assert order.order_number == "SO202500001"
        assert order.title == "Test Order"
        assert order.customer_id == 100
        assert order.total_amount == Decimal("1000.00")
        assert order.status == OrderStatus.DRAFT
        assert order.payment_status == PaymentStatus.PENDING
        assert order.is_active is True
    
    def test_order_defaults(self):
        """Test order default values."""
        order = SalesOrder(**self.order_data)
        
        assert order.status == OrderStatus.DRAFT
        assert order.payment_status == PaymentStatus.PENDING
        assert order.subtotal == 0.0
        assert order.discount_amount == 0.0
        assert order.tax_amount == 0.0
        assert order.shipping_amount == 0.0
        assert order.paid_amount == 0.0
        assert order.payment_terms_days == 30
        assert order.currency_code == "USD"
        assert order.is_priority is False
        assert order.requires_approval is False
        assert order.is_dropship is False
        assert order.is_backorder_allowed is True
        assert order.items_shipped == 0
        assert order.items_remaining == 0
        assert order.shipment_count == 0
        assert order.is_active is True
    
    def test_string_representation(self):
        """Test order string representations."""
        order = SalesOrder(**self.order_data)
        
        assert str(order) == "Order SO202500001"
        assert "SO202500001" in repr(order)
        assert "draft" in repr(order)
        assert "1000" in repr(order)
    
    def test_display_identifier(self):
        """Test display identifier property."""
        order = SalesOrder(**self.order_data)
        
        expected = "SO202500001 - Test Order"
        assert order.display_identifier == expected
    
    def test_order_number_generation(self):
        """Test order number generation."""
        order = SalesOrder(**self.order_data)
        
        # Test with default prefix
        generated_number = order.generate_order_number()
        assert generated_number.startswith("SO")
        assert len(generated_number) == 10  # SO + 8 digits
        
        # Test with custom prefix
        generated_number = order.generate_order_number("SALES")
        assert generated_number.startswith("SALES")
    
    def test_is_overdue_property(self):
        """Test is_overdue property logic."""
        order = SalesOrder(**self.order_data)
        
        # No required date - not overdue
        assert order.is_overdue is False
        
        # Future required date - not overdue
        order.required_date = datetime.utcnow() + timedelta(days=5)
        assert order.is_overdue is False
        
        # Past required date - overdue
        order.required_date = datetime.utcnow() - timedelta(days=1)
        assert order.is_overdue is True
        
        # Completed order with past date - not overdue
        order.status = OrderStatus.COMPLETED
        assert order.is_overdue is False
        
        # Cancelled order with past date - not overdue
        order.status = OrderStatus.CANCELLED
        assert order.is_overdue is False
    
    def test_days_until_required_property(self):
        """Test days_until_required property calculation."""
        order = SalesOrder(**self.order_data)
        
        # No required date
        assert order.days_until_required is None
        
        # Future date
        future_date = datetime.utcnow() + timedelta(days=5)
        order.required_date = future_date
        assert order.days_until_required == 5
        
        # Past date (negative days)
        past_date = datetime.utcnow() - timedelta(days=3)
        order.required_date = past_date
        assert order.days_until_required == -3
        
        # Completed order
        order.status = OrderStatus.COMPLETED
        assert order.days_until_required is None
    
    def test_payment_properties(self):
        """Test payment-related properties."""
        order = SalesOrder(**self.order_data)
        
        # Not paid initially
        assert order.is_paid is False
        assert order.payment_percentage == 0.0
        
        # Partially paid
        order.paid_amount = Decimal("500.00")
        order.payment_status = PaymentStatus.PARTIALLY_PAID
        assert order.is_paid is False
        assert order.payment_percentage == 50.0
        
        # Fully paid
        order.paid_amount = Decimal("1000.00")
        order.payment_status = PaymentStatus.PAID
        assert order.is_paid is True
        assert order.payment_percentage == 100.0
    
    def test_shipping_properties(self):
        """Test shipping-related properties."""
        order = SalesOrder(**self.order_data)
        
        # Not shipped initially
        assert order.is_shipped is False
        assert order.is_completed is False
        
        # Partially shipped
        order.status = OrderStatus.PARTIALLY_SHIPPED
        assert order.is_shipped is False
        
        # Fully shipped
        order.status = OrderStatus.SHIPPED
        assert order.is_shipped is True
        
        # Delivered
        order.status = OrderStatus.DELIVERED
        assert order.is_shipped is True
        
        # Completed
        order.status = OrderStatus.COMPLETED
        assert order.is_shipped is True
        assert order.is_completed is True
    
    def test_fulfillment_percentage(self):
        """Test fulfillment percentage calculation."""
        order = SalesOrder(**self.order_data)
        
        # No items
        assert order.fulfillment_percentage == 0.0
        
        # Partial fulfillment
        order.items_shipped = 7
        order.items_remaining = 3
        assert order.fulfillment_percentage == 70.0
        
        # Full fulfillment
        order.items_shipped = 10
        order.items_remaining = 0
        assert order.fulfillment_percentage == 100.0
    
    def test_calculate_totals(self):
        """Test calculate_totals method."""
        order = SalesOrder(**self.order_data)
        order.total_amount = Decimal("1000.00")
        order.paid_amount = Decimal("300.00")
        order.payment_terms_days = 15
        order.order_date = datetime.utcnow()
        
        order.calculate_totals()
        
        # Check outstanding amount calculation
        assert order.outstanding_amount == Decimal("700.00")
        
        # Check due date calculation
        expected_due_date = order.order_date + timedelta(days=15)
        assert order.due_date.date() == expected_due_date.date()
    
    @patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail')
    @patch('sales_module.framework.base.CompanyBusinessObject.publish_event')
    def test_confirm_order(self, mock_publish, mock_audit):
        """Test order confirmation workflow."""
        order = SalesOrder(**self.order_data)
        order.confirm_order(user_id=1)
        
        # Check status change
        assert order.status == OrderStatus.CONFIRMED
        
        # Check audit and event publishing
        mock_audit.assert_called_once_with("order_confirmed", 1)
        mock_publish.assert_called_once()
        
        # Check event data
        event_call = mock_publish.call_args[0]
        assert event_call[0] == "order.confirmed"
        assert "order_id" in event_call[1]
        assert "order_number" in event_call[1]
        assert "customer_id" in event_call[1]
        assert "total_amount" in event_call[1]
    
    @patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail')
    @patch('sales_module.framework.base.CompanyBusinessObject.publish_event')
    def test_cancel_order(self, mock_publish, mock_audit):
        """Test order cancellation workflow."""
        order = SalesOrder(**self.order_data)
        order.status = OrderStatus.CONFIRMED
        
        reason = "Customer requested cancellation"
        order.cancel_order(reason, user_id=1)
        
        # Check status change
        assert order.status == OrderStatus.CANCELLED
        
        # Check audit and event publishing
        mock_audit.assert_called_once_with("order_cancelled", 1, {
            "previous_status": "confirmed",
            "cancellation_reason": reason
        })
        mock_publish.assert_called_once()
        
        # Check event data
        event_call = mock_publish.call_args[0]
        assert event_call[0] == "order.cancelled"
        assert event_call[1]["cancellation_reason"] == reason
    
    @patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail')
    @patch('sales_module.framework.base.CompanyBusinessObject.publish_event')
    def test_put_on_hold(self, mock_publish, mock_audit):
        """Test putting order on hold."""
        order = SalesOrder(**self.order_data)
        order.status = OrderStatus.CONFIRMED
        
        reason = "Credit check required"
        order.put_on_hold(reason, user_id=1)
        
        # Check status change
        assert order.status == OrderStatus.ON_HOLD
        
        # Check audit and event publishing
        mock_audit.assert_called_once_with("order_on_hold", 1, {
            "previous_status": "confirmed",
            "hold_reason": reason
        })
        mock_publish.assert_called_once()
    
    @patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail')
    @patch('sales_module.framework.base.CompanyBusinessObject.publish_event')
    def test_release_hold(self, mock_publish, mock_audit):
        """Test releasing order from hold."""
        order = SalesOrder(**self.order_data)
        order.status = OrderStatus.ON_HOLD
        
        order.release_hold(user_id=1)
        
        # Check status change
        assert order.status == OrderStatus.CONFIRMED
        
        # Check audit and event publishing
        mock_audit.assert_called_once_with("order_hold_released", 1)
        mock_publish.assert_called_once()
    
    @patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail')
    @patch('sales_module.framework.base.CompanyBusinessObject.publish_event')
    def test_record_payment(self, mock_publish, mock_audit):
        """Test recording payment against order."""
        order = SalesOrder(**self.order_data)
        order.total_amount = Decimal("1000.00")
        order.outstanding_amount = Decimal("1000.00")
        
        # Record partial payment
        payment_amount = Decimal("300.00")
        order.record_payment(payment_amount, "credit_card", user_id=1)
        
        # Check payment calculation
        assert order.paid_amount == Decimal("300.00")
        assert order.outstanding_amount == Decimal("700.00")
        assert order.payment_status == PaymentStatus.PARTIALLY_PAID
        
        # Record remaining payment
        remaining_payment = Decimal("700.00")
        order.record_payment(remaining_payment, "credit_card", user_id=1)
        
        # Check full payment
        assert order.paid_amount == Decimal("1000.00")
        assert order.outstanding_amount == Decimal("0.00")
        assert order.payment_status == PaymentStatus.PAID
        
        # Check audit and event publishing
        assert mock_audit.call_count == 2
        assert mock_publish.call_count == 2


class TestSalesOrderLineItem:
    """Test SalesOrderLineItem model functionality."""
    
    def setup_method(self):
        """Set up test data."""
        self.line_item_data = {
            "company_id": 1,
            "order_id": 1,
            "line_number": 1,
            "item_name": "Test Product",
            "description": "Test product description",
            "quantity_ordered": Decimal("10.0"),
            "unit_price": Decimal("100.00"),
            "line_total": Decimal("1000.00")
        }
    
    def test_line_item_creation(self):
        """Test basic line item creation."""
        line_item = SalesOrderLineItem(**self.line_item_data)
        
        assert line_item.order_id == 1
        assert line_item.line_number == 1
        assert line_item.item_name == "Test Product"
        assert line_item.quantity_ordered == Decimal("10.0")
        assert line_item.unit_price == Decimal("100.00")
        assert line_item.line_total == Decimal("1000.00")
    
    def test_line_item_defaults(self):
        """Test line item default values."""
        line_item = SalesOrderLineItem(**self.line_item_data)
        
        assert line_item.quantity_shipped == 0.0
        assert line_item.quantity_cancelled == 0.0
        assert line_item.quantity_backordered == 0.0
        assert line_item.unit_of_measure == "each"
        assert line_item.discount_percentage == 0.0
        assert line_item.discount_amount == 0.0
        assert line_item.tax_percentage == 0.0
        assert line_item.tax_amount == 0.0
        assert line_item.reserved_quantity == 0.0
        assert line_item.allocated_quantity == 0.0
        assert line_item.is_backordered is False
        assert line_item.is_dropship is False
        assert line_item.requires_special_handling is False
        assert line_item.is_active is True
    
    def test_string_representation(self):
        """Test line item string representations."""
        line_item = SalesOrderLineItem(**self.line_item_data)
        
        expected_str = "Line 1: Test Product (Qty: 10.0)"
        assert str(line_item) == expected_str
        
        assert "line_number=1" in repr(line_item)
        assert "Test Product" in repr(line_item)
        assert "quantity=10.0" in repr(line_item)
    
    def test_quantity_remaining_property(self):
        """Test quantity_remaining property calculation."""
        line_item = SalesOrderLineItem(**self.line_item_data)
        
        # Initially all quantity remaining
        assert line_item.quantity_remaining == Decimal("10.0")
        
        # After partial shipment
        line_item.quantity_shipped = Decimal("6.0")
        assert line_item.quantity_remaining == Decimal("4.0")
        
        # After cancellation
        line_item.quantity_cancelled = Decimal("2.0")
        assert line_item.quantity_remaining == Decimal("2.0")
        
        # Fully processed
        line_item.quantity_shipped = Decimal("8.0")
        assert line_item.quantity_remaining == Decimal("0.0")
    
    def test_is_fully_shipped_property(self):
        """Test is_fully_shipped property."""
        line_item = SalesOrderLineItem(**self.line_item_data)
        
        # Not shipped initially
        assert line_item.is_fully_shipped is False
        
        # Partially shipped
        line_item.quantity_shipped = Decimal("6.0")
        assert line_item.is_fully_shipped is False
        
        # Fully shipped
        line_item.quantity_shipped = Decimal("10.0")
        assert line_item.is_fully_shipped is True
        
        # Over-shipped
        line_item.quantity_shipped = Decimal("12.0")
        assert line_item.is_fully_shipped is True
    
    def test_fulfillment_percentage(self):
        """Test fulfillment percentage calculation."""
        line_item = SalesOrderLineItem(**self.line_item_data)
        
        # No shipment
        assert line_item.fulfillment_percentage == 0.0
        
        # Partial shipment
        line_item.quantity_shipped = Decimal("3.0")
        assert line_item.fulfillment_percentage == 30.0
        
        # Full shipment
        line_item.quantity_shipped = Decimal("10.0")
        assert line_item.fulfillment_percentage == 100.0
        
        # Over-shipment
        line_item.quantity_shipped = Decimal("12.0")
        assert line_item.fulfillment_percentage == 120.0
        
        # Zero quantity ordered (edge case)
        line_item.quantity_ordered = Decimal("0.0")
        assert line_item.fulfillment_percentage == 0.0
    
    def test_margin_calculations(self):
        """Test margin calculation properties."""
        line_item = SalesOrderLineItem(**self.line_item_data)
        
        # No cost data - no margin
        assert line_item.line_margin is None
        assert line_item.margin_percentage is None
        
        # With cost data
        line_item.unit_cost = Decimal("60.00")  # $60 unit cost
        line_item.line_cost = Decimal("600.00")  # $600 line cost for 10 units
        
        # Line margin: $1000 - $600 = $400
        assert line_item.line_margin == Decimal("400.00")
        
        # Margin percentage: ($400 / $1000) * 100 = 40%
        assert line_item.margin_percentage == 40.0
    
    def test_calculate_line_total(self):
        """Test line total calculation."""
        line_item = SalesOrderLineItem(**self.line_item_data)
        line_item.quantity_ordered = Decimal("5.0")
        line_item.unit_price = Decimal("100.00")
        line_item.discount_amount = Decimal("50.00")
        line_item.unit_cost = Decimal("60.00")
        line_item.tax_percentage = Decimal("8.5")  # 8.5% tax
        
        line_item.calculate_line_total()
        
        # Line total: (5 * $100) - $50 = $450
        assert line_item.line_total == Decimal("450.00")
        
        # Line cost: 5 * $60 = $300
        assert line_item.line_cost == Decimal("300.00")
        
        # Tax amount: $450 * 8.5% = $38.25
        assert line_item.tax_amount == Decimal("38.25")
    
    @patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail')
    @patch('sales_module.framework.base.CompanyBusinessObject.publish_event')
    def test_ship_quantity(self, mock_publish, mock_audit):
        """Test shipping quantity workflow."""
        line_item = SalesOrderLineItem(**self.line_item_data)
        
        # Ship partial quantity
        quantity_to_ship = Decimal("6.0")
        line_item.ship_quantity(quantity_to_ship, user_id=1)
        
        # Check quantity update
        assert line_item.quantity_shipped == Decimal("6.0")
        assert line_item.quantity_remaining == Decimal("4.0")
        assert line_item.shipped_date is not None
        
        # Check audit and event publishing
        mock_audit.assert_called_once()
        mock_publish.assert_called_once()
        
        # Check event data
        event_call = mock_publish.call_args[0]
        assert event_call[0] == "order_line.shipped"
        assert event_call[1]["quantity_shipped"] == 6.0
        assert event_call[1]["fully_shipped"] is False
    
    def test_ship_quantity_validation(self):
        """Test ship quantity validation."""
        line_item = SalesOrderLineItem(**self.line_item_data)
        line_item.quantity_shipped = Decimal("8.0")  # Already shipped 8 out of 10
        
        # Try to ship more than remaining (should fail)
        with pytest.raises(ValueError, match="Cannot ship more than remaining quantity"):
            line_item.ship_quantity(Decimal("5.0"))  # Only 2 remaining, trying to ship 5
    
    def test_ship_quantity_sets_date_only_once(self):
        """Test that shipped_date is set only on first shipment."""
        line_item = SalesOrderLineItem(**self.line_item_data)
        
        # First shipment
        with patch('sales_module.models.order.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2025, 1, 15, 10, 30)
            line_item.ship_quantity(Decimal("3.0"))
            first_ship_date = line_item.shipped_date
        
        # Second shipment
        with patch('sales_module.models.order.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2025, 1, 16, 14, 45)
            line_item.ship_quantity(Decimal("2.0"))
            
        # Date should remain the same from first shipment
        assert line_item.shipped_date == first_ship_date


class TestOrderShipment:
    """Test OrderShipment model functionality."""
    
    def setup_method(self):
        """Set up test data."""
        self.shipment_data = {
            "company_id": 1,
            "order_id": 1,
            "shipment_number": "SHIP202500001",
            "carrier_name": "UPS",
            "shipping_address": {"street": "123 Main St", "city": "Anytown", "state": "CA"},
            "return_address": {"street": "456 Oak Ave", "city": "Business City", "state": "NY"}
        }
    
    def test_shipment_creation(self):
        """Test basic shipment creation."""
        shipment = OrderShipment(**self.shipment_data)
        
        assert shipment.order_id == 1
        assert shipment.shipment_number == "SHIP202500001"
        assert shipment.carrier_name == "UPS"
        assert shipment.status == ShipmentStatus.PREPARING
    
    def test_shipment_defaults(self):
        """Test shipment default values."""
        shipment = OrderShipment(**self.shipment_data)
        
        assert shipment.status == ShipmentStatus.PREPARING
        assert shipment.weight_unit == "lbs"
        assert shipment.package_count == 1
        assert shipment.signature_required is False
        assert shipment.is_active is True
    
    def test_string_representation(self):
        """Test shipment string representations."""
        shipment = OrderShipment(**self.shipment_data)
        
        assert str(shipment) == "Shipment SHIP202500001"
        assert "SHIP202500001" in repr(shipment)
        assert "preparing" in repr(shipment)
        assert "UPS" in repr(shipment)
    
    def test_shipment_number_generation(self):
        """Test shipment number generation."""
        shipment = OrderShipment(**self.shipment_data)
        
        # Test with default prefix
        generated_number = shipment.generate_shipment_number()
        assert generated_number.startswith("SHIP")
        assert len(generated_number) == 12  # SHIP + 8 digits
        
        # Test with custom prefix
        generated_number = shipment.generate_shipment_number("TRACK")
        assert generated_number.startswith("TRACK")
    
    def test_shipment_status_properties(self):
        """Test shipment status properties."""
        shipment = OrderShipment(**self.shipment_data)
        
        # Initially not shipped
        assert shipment.is_shipped is False
        assert shipment.is_delivered is False
        
        # Ready status - still not shipped
        shipment.status = ShipmentStatus.READY
        assert shipment.is_shipped is False
        
        # Shipped status
        shipment.status = ShipmentStatus.SHIPPED
        assert shipment.is_shipped is True
        assert shipment.is_delivered is False
        
        # Delivered status
        shipment.status = ShipmentStatus.DELIVERED
        assert shipment.is_shipped is True
        assert shipment.is_delivered is True
    
    def test_days_in_transit_property(self):
        """Test days_in_transit property calculation."""
        shipment = OrderShipment(**self.shipment_data)
        
        # No ship date
        assert shipment.days_in_transit is None
        
        # With ship date, no delivery
        ship_date = datetime.utcnow() - timedelta(days=3)
        shipment.ship_date = ship_date
        assert shipment.days_in_transit == 3
        
        # With ship date and delivery
        delivery_date = ship_date + timedelta(days=2)
        shipment.actual_delivery_date = delivery_date
        assert shipment.days_in_transit == 2
    
    def test_is_overdue_property(self):
        """Test is_overdue property."""
        shipment = OrderShipment(**self.shipment_data)
        
        # No estimated delivery date - not overdue
        assert shipment.is_overdue is False
        
        # Future estimated date - not overdue
        future_date = datetime.utcnow() + timedelta(days=2)
        shipment.estimated_delivery_date = future_date
        assert shipment.is_overdue is False
        
        # Past estimated date - overdue
        past_date = datetime.utcnow() - timedelta(days=1)
        shipment.estimated_delivery_date = past_date
        assert shipment.is_overdue is True
        
        # Already delivered with past date - not overdue
        shipment.status = ShipmentStatus.DELIVERED
        assert shipment.is_overdue is False
    
    @patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail')
    @patch('sales_module.framework.base.CompanyBusinessObject.publish_event')
    def test_ship_method(self, mock_publish, mock_audit):
        """Test shipping workflow."""
        shipment = OrderShipment(**self.shipment_data)
        tracking_number = "1Z999AA1234567890"
        
        shipment.ship(tracking_number, user_id=1)
        
        # Check status and data updates
        assert shipment.status == ShipmentStatus.SHIPPED
        assert shipment.tracking_number == tracking_number
        assert shipment.ship_date is not None
        
        # Check audit and event publishing
        mock_audit.assert_called_once_with("shipment_shipped", 1, {
            "tracking_number": tracking_number
        })
        mock_publish.assert_called_once()
        
        # Check event data
        event_call = mock_publish.call_args[0]
        assert event_call[0] == "shipment.shipped"
        assert event_call[1]["tracking_number"] == tracking_number
    
    @patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail')
    @patch('sales_module.framework.base.CompanyBusinessObject.publish_event')
    def test_mark_delivered(self, mock_publish, mock_audit):
        """Test delivery marking workflow."""
        shipment = OrderShipment(**self.shipment_data)
        delivered_to = "John Doe"
        
        shipment.mark_delivered(delivered_to, user_id=1)
        
        # Check status and data updates
        assert shipment.status == ShipmentStatus.DELIVERED
        assert shipment.delivered_to == delivered_to
        assert shipment.actual_delivery_date is not None
        
        # Check audit and event publishing
        mock_audit.assert_called_once_with("shipment_delivered", 1, {
            "delivered_to": delivered_to
        })
        mock_publish.assert_called_once()


class TestOrderInvoice:
    """Test OrderInvoice model functionality."""
    
    def setup_method(self):
        """Set up test data."""
        self.invoice_data = {
            "company_id": 1,
            "order_id": 1,
            "invoice_number": "INV202500001",
            "subtotal": Decimal("1000.00"),
            "tax_amount": Decimal("85.00"),
            "total_amount": Decimal("1085.00"),
            "outstanding_amount": Decimal("1085.00"),
            "line_items_data": [{"item": "Test Product", "quantity": 10, "price": 100}],
            "billing_address": {"street": "123 Billing St", "city": "Invoice City"}
        }
    
    def test_invoice_creation(self):
        """Test basic invoice creation."""
        invoice = OrderInvoice(**self.invoice_data)
        
        assert invoice.order_id == 1
        assert invoice.invoice_number == "INV202500001"
        assert invoice.total_amount == Decimal("1085.00")
        assert invoice.status == InvoiceStatus.DRAFT
    
    def test_invoice_defaults(self):
        """Test invoice default values."""
        invoice = OrderInvoice(**self.invoice_data)
        
        assert invoice.status == InvoiceStatus.DRAFT
        assert invoice.invoice_type == "standard"
        assert invoice.discount_amount == 0.0
        assert invoice.paid_amount == 0.0
        assert invoice.currency_code == "USD"
        assert invoice.payment_terms_days == 30
        assert invoice.pdf_generated is False
        assert invoice.email_sent_count == 0
        assert invoice.viewed_by_customer is False
        assert invoice.is_active is True
    
    def test_string_representation(self):
        """Test invoice string representations."""
        invoice = OrderInvoice(**self.invoice_data)
        
        assert str(invoice) == "Invoice INV202500001"
        assert "INV202500001" in repr(invoice)
        assert "draft" in repr(invoice)
        assert "1085" in repr(invoice)
    
    def test_invoice_number_generation(self):
        """Test invoice number generation."""
        invoice = OrderInvoice(**self.invoice_data)
        
        # Test with default prefix
        generated_number = invoice.generate_invoice_number()
        assert generated_number.startswith("INV")
        assert len(generated_number) == 11  # INV + 8 digits
        
        # Test with custom prefix
        generated_number = invoice.generate_invoice_number("BILL")
        assert generated_number.startswith("BILL")
    
    def test_overdue_properties(self):
        """Test overdue-related properties."""
        invoice = OrderInvoice(**self.invoice_data)
        
        # Future due date - not overdue
        invoice.due_date = datetime.utcnow() + timedelta(days=5)
        assert invoice.is_overdue is False
        assert invoice.days_overdue == 0
        
        # Past due date - overdue
        invoice.due_date = datetime.utcnow() - timedelta(days=3)
        assert invoice.is_overdue is True
        assert invoice.days_overdue == 3
        
        # Paid invoice with past due date - not overdue
        invoice.status = InvoiceStatus.PAID
        assert invoice.is_overdue is False
        assert invoice.days_overdue == 0
    
    def test_payment_properties(self):
        """Test payment-related properties."""
        invoice = OrderInvoice(**self.invoice_data)
        
        # Not paid initially
        assert invoice.is_paid is False
        assert invoice.payment_percentage == 0.0
        
        # Partially paid
        invoice.paid_amount = Decimal("500.00")
        assert invoice.is_paid is False
        assert invoice.payment_percentage == 500.0 / 1085.0 * 100  # ~46.08%
        
        # Fully paid
        invoice.paid_amount = Decimal("1085.00")
        invoice.status = InvoiceStatus.PAID
        assert invoice.is_paid is True
        assert invoice.payment_percentage == 100.0
    
    @patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail')
    @patch('sales_module.framework.base.CompanyBusinessObject.publish_event')
    def test_send_to_customer(self, mock_publish, mock_audit):
        """Test sending invoice to customer."""
        invoice = OrderInvoice(**self.invoice_data)
        email_template = "standard_invoice_template"
        
        invoice.send_to_customer(user_id=1, email_template=email_template)
        
        # Check status and data updates
        assert invoice.status == InvoiceStatus.SENT
        assert invoice.sent_date is not None
        assert invoice.email_sent_count == 1
        assert invoice.last_email_sent is not None
        
        # Check audit and event publishing
        mock_audit.assert_called_once_with("invoice_sent", 1, {
            "email_template": email_template
        })
        mock_publish.assert_called_once()
        
        # Check event data
        event_call = mock_publish.call_args[0]
        assert event_call[0] == "invoice.sent"
        assert event_call[1]["total_amount"] == 1085.0
    
    @patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail')
    @patch('sales_module.framework.base.CompanyBusinessObject.publish_event')
    def test_record_payment(self, mock_publish, mock_audit):
        """Test recording payment against invoice."""
        invoice = OrderInvoice(**self.invoice_data)
        payment_amount = Decimal("500.00")
        
        invoice.record_payment(payment_amount, "credit_card", user_id=1)
        
        # Check payment calculation
        assert invoice.paid_amount == Decimal("500.00")
        assert invoice.outstanding_amount == Decimal("585.00")
        assert invoice.status == InvoiceStatus.DRAFT  # Not fully paid yet
        
        # Record full payment
        remaining_payment = Decimal("585.00")
        invoice.record_payment(remaining_payment, "credit_card", user_id=1)
        
        # Check full payment
        assert invoice.paid_amount == Decimal("1085.00")
        assert invoice.outstanding_amount == Decimal("0.00")
        assert invoice.status == InvoiceStatus.PAID
        
        # Check audit and event publishing
        assert mock_audit.call_count == 2
        assert mock_publish.call_count == 2
    
    @patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail')
    @patch('sales_module.framework.base.CompanyBusinessObject.publish_event')
    def test_mark_overdue(self, mock_publish, mock_audit):
        """Test marking invoice as overdue."""
        invoice = OrderInvoice(**self.invoice_data)
        invoice.status = InvoiceStatus.SENT
        invoice.due_date = datetime.utcnow() - timedelta(days=5)
        
        invoice.mark_overdue(user_id=1)
        
        # Check status update
        assert invoice.status == InvoiceStatus.OVERDUE
        
        # Check audit and event publishing
        mock_audit.assert_called_once_with("invoice_overdue", 1, {
            "days_overdue": 5
        })
        mock_publish.assert_called_once()
        
        # Check event data
        event_call = mock_publish.call_args[0]
        assert event_call[0] == "invoice.overdue"
        assert event_call[1]["days_overdue"] == 5
    
    def test_mark_overdue_skips_paid_invoices(self):
        """Test that paid invoices are not marked overdue."""
        invoice = OrderInvoice(**self.invoice_data)
        invoice.status = InvoiceStatus.PAID
        invoice.due_date = datetime.utcnow() - timedelta(days=5)
        
        with patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail') as mock_audit:
            invoice.mark_overdue(user_id=1)
            
            # Status should remain paid
            assert invoice.status == InvoiceStatus.PAID
            
            # No audit should be logged
            mock_audit.assert_not_called()


class TestQuoteToOrderIntegration:
    """Test quote-to-order conversion functionality."""
    
    def setup_method(self):
        """Set up test data for quote-to-order conversion."""
        self.quote_data = {
            "company_id": 1,
            "quote_number": "QT202500001",
            "title": "Test Quote",
            "description": "Test quote description",
            "customer_id": 100,
            "prepared_by_user_id": 1,
            "subtotal": Decimal("1000.00"),
            "discount_amount": Decimal("100.00"),
            "tax_amount": Decimal("72.00"),
            "total_amount": Decimal("972.00"),
            "currency_code": "USD",
            "payment_terms_days": 30,
            "valid_until": datetime.utcnow() + timedelta(days=30),
            "notes": "Special handling required"
        }
        
        self.quote_line_data = {
            "company_id": 1,
            "quote_id": 1,
            "line_number": 1,
            "item_code": "PROD001",
            "item_name": "Test Product",
            "description": "Test product description",
            "quantity": Decimal("10.0"),
            "unit_price": Decimal("100.00"),
            "discount_amount": Decimal("50.00"),
            "line_total": Decimal("950.00"),
            "tax_percentage": Decimal("8.0"),
            "tax_amount": Decimal("76.00"),
            "unit_of_measure": "each",
            "delivery_date": datetime.utcnow() + timedelta(days=14)
        }
    
    def test_order_from_quote_creation(self):
        """Test creating an order from a quote."""
        quote = SalesQuote(**self.quote_data)
        user_id = 5
        
        order = SalesOrder.from_quote(quote, user_id=user_id)
        
        # Check basic order information
        assert order.company_id == quote.company_id
        assert order.title == quote.title
        assert order.customer_id == quote.customer_id
        assert order.quote_id == quote.id
        assert order.sales_rep_user_id == user_id
        
        # Check financial information transfer
        assert order.subtotal == quote.subtotal
        assert order.discount_amount == quote.discount_amount
        assert order.tax_amount == quote.tax_amount
        assert order.total_amount == quote.total_amount
        assert order.currency_code == quote.currency_code
        assert order.payment_terms_days == quote.payment_terms_days
        
        # Check order-specific settings
        assert order.status == OrderStatus.CONFIRMED
        assert order.payment_status == PaymentStatus.PENDING
        assert order.outstanding_amount == quote.total_amount
        assert order.source_channel == "quote_conversion"
        assert order.special_instructions == quote.notes
        
        # Check order number generation
        assert order.order_number.startswith("SO")
        assert len(order.order_number) == 10
    
    def test_order_from_quote_with_custom_data(self):
        """Test creating an order from quote with additional custom data."""
        quote = SalesQuote(**self.quote_data)
        
        custom_data = {
            "order_number": "SO-CUSTOM-001",
            "customer_po_number": "PO123456",
            "required_date": datetime.utcnow() + timedelta(days=7),
            "shipping_method": "Express"
        }
        
        order = SalesOrder.from_quote(quote, user_id=3, **custom_data)
        
        # Check custom data was applied
        assert order.order_number == "SO-CUSTOM-001"
        assert order.customer_po_number == "PO123456"
        assert order.required_date == custom_data["required_date"]
        assert order.shipping_method == "Express"
        assert order.sales_rep_user_id == 3
    
    def test_order_from_quote_uses_quote_user_when_no_user_provided(self):
        """Test that order uses quote's user when no user_id provided."""
        quote = SalesQuote(**self.quote_data)
        
        order = SalesOrder.from_quote(quote)
        
        # Should use quote's prepared_by_user_id
        assert order.sales_rep_user_id == quote.prepared_by_user_id
    
    def test_order_from_quote_generates_description_when_none(self):
        """Test description generation when quote has no description."""
        quote_data = self.quote_data.copy()
        quote_data["description"] = None
        quote = SalesQuote(**quote_data)
        
        order = SalesOrder.from_quote(quote)
        
        expected_description = f"Order converted from quote {quote.quote_number}"
        assert order.description == expected_description
    
    def test_order_line_item_from_quote_line_item(self):
        """Test creating order line item from quote line item."""
        quote_line = SalesQuoteLineItem(**self.quote_line_data)
        order_id = 10
        
        order_line = SalesOrderLineItem.from_quote_line_item(quote_line, order_id)
        
        # Check basic information transfer
        assert order_line.company_id == quote_line.company_id
        assert order_line.order_id == order_id
        assert order_line.line_number == quote_line.line_number
        
        # Check product information
        assert order_line.item_code == quote_line.item_code
        assert order_line.item_name == quote_line.item_name
        assert order_line.description == quote_line.description
        
        # Check quantities
        assert order_line.quantity_ordered == quote_line.quantity
        assert order_line.quantity_shipped == 0.0
        assert order_line.quantity_cancelled == 0.0
        assert order_line.unit_of_measure == quote_line.unit_of_measure
        
        # Check pricing
        assert order_line.unit_price == quote_line.unit_price
        assert order_line.discount_amount == quote_line.discount_amount
        assert order_line.line_total == quote_line.line_total
        
        # Check tax information
        assert order_line.tax_percentage == quote_line.tax_percentage
        assert order_line.tax_amount == quote_line.tax_amount
        
        # Check delivery date conversion
        assert order_line.required_date == quote_line.delivery_date
    
    def test_order_line_item_from_quote_with_custom_data(self):
        """Test creating order line item with additional custom data."""
        quote_line = SalesQuoteLineItem(**self.quote_line_data)
        order_id = 15
        
        custom_data = {
            "warehouse_id": 5,
            "required_date": datetime.utcnow() + timedelta(days=21),
            "unit_cost": Decimal("60.00"),
            "is_dropship": True,
            "notes": "Custom handling instructions"
        }
        
        order_line = SalesOrderLineItem.from_quote_line_item(
            quote_line, order_id, **custom_data
        )
        
        # Check custom data was applied
        assert order_line.warehouse_id == 5
        assert order_line.required_date == custom_data["required_date"]
        assert order_line.unit_cost == Decimal("60.00")
        assert order_line.is_dropship is True
        assert order_line.notes == "Custom handling instructions"
    
    def test_order_line_item_calculates_totals_after_creation(self):
        """Test that order line item recalculates totals after creation."""
        quote_line_data = self.quote_line_data.copy()
        quote_line_data["discount_amount"] = Decimal("0.00")  # No discount
        quote_line_data["tax_percentage"] = Decimal("10.0")  # 10% tax
        
        quote_line = SalesQuoteLineItem(**quote_line_data)
        order_id = 20
        
        order_line = SalesOrderLineItem.from_quote_line_item(quote_line, order_id)
        
        # Check that totals were recalculated
        expected_line_total = quote_line_data["quantity"] * quote_line_data["unit_price"]
        expected_tax = expected_line_total * (Decimal("10.0") / 100)
        
        assert order_line.line_total == expected_line_total
        assert order_line.tax_amount == expected_tax
    
    def test_complete_quote_to_order_workflow(self):
        """Test complete quote-to-order conversion workflow."""
        # Create quote with line items
        quote = SalesQuote(**self.quote_data)
        quote.id = 1  # Mock ID
        
        quote_line_1 = SalesQuoteLineItem(**self.quote_line_data)
        quote_line_2 = SalesQuoteLineItem(**{
            **self.quote_line_data,
            "line_number": 2,
            "item_name": "Second Product",
            "quantity": Decimal("5.0"),
            "unit_price": Decimal("200.00"),
            "line_total": Decimal("1000.00")
        })
        
        # Create order from quote
        order = SalesOrder.from_quote(quote, user_id=7)
        order.id = 1  # Mock ID
        
        # Create order line items from quote line items
        order_lines = [
            SalesOrderLineItem.from_quote_line_item(quote_line_1, order.id),
            SalesOrderLineItem.from_quote_line_item(quote_line_2, order.id)
        ]
        
        # Verify complete conversion
        assert order.quote_id == quote.id
        assert len(order_lines) == 2
        
        # Verify line items
        assert order_lines[0].line_number == 1
        assert order_lines[0].item_name == "Test Product"
        assert order_lines[1].line_number == 2
        assert order_lines[1].item_name == "Second Product"
        
        # Verify all line items belong to the order
        for line in order_lines:
            assert line.order_id == order.id
            assert line.company_id == order.company_id
    
    def test_quote_to_order_preserves_product_specifications(self):
        """Test that product specifications are preserved in conversion."""
        quote_line_data = self.quote_line_data.copy()
        quote_line_data["specifications"] = {
            "color": "blue",
            "size": "large",
            "material": "cotton"
        }
        quote_line_data["custom_options"] = {
            "engraving": "Custom Text",
            "gift_wrap": True
        }
        
        quote_line = SalesQuoteLineItem(**quote_line_data)
        order_line = SalesOrderLineItem.from_quote_line_item(quote_line, order_id=25)
        
        # Check specifications preservation
        assert order_line.specifications == quote_line_data["specifications"]
        assert order_line.custom_options == quote_line_data["custom_options"]
    
    def test_order_due_date_calculation_from_quote(self):
        """Test that order due date is calculated properly from quote data."""
        quote = SalesQuote(**self.quote_data)
        quote.payment_terms_days = 15
        
        with patch('sales_module.models.order.datetime') as mock_datetime:
            base_time = datetime(2025, 6, 15, 10, 0, 0)
            mock_datetime.utcnow.return_value = base_time
            
            order = SalesOrder.from_quote(quote, user_id=8)
            
            # Due date should be order_date + payment_terms_days
            expected_due_date = base_time + timedelta(days=15)
            assert order.due_date.date() == expected_due_date.date()
    
    @patch('sales_module.framework.base.CompanyBusinessObject.log_audit_trail')
    @patch('sales_module.framework.base.CompanyBusinessObject.publish_event')
    def test_quote_conversion_maintains_audit_capability(self, mock_publish, mock_audit):
        """Test that orders created from quotes maintain audit and event capabilities."""
        quote = SalesQuote(**self.quote_data)
        order = SalesOrder.from_quote(quote, user_id=9)
        
        # Test that the order can still perform audit operations
        order.confirm_order(user_id=9)
        
        # Should be able to log audit trail and publish events
        mock_audit.assert_called_once_with("order_confirmed", 9)
        mock_publish.assert_called_once()
        
        # Verify the order maintains all audit capabilities
        assert hasattr(order, 'log_audit_trail')
        assert hasattr(order, 'publish_event')
        assert order.status == OrderStatus.CONFIRMED