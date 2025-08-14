#!/usr/bin/env python3
"""
Order Service Integration Test

Tests the order service layer including quote-to-order conversion,
inventory integration methods, and fulfillment workflows without 
requiring external services.
"""

import sys
import os
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

# Add the sales_module to Python path
sys.path.insert(0, os.path.dirname(__file__))

from sales_module.models import (
    SalesQuote, SalesOrder, SalesOrderLineItem, OrderShipment, OrderInvoice,
    OrderStatus, PaymentStatus, ShipmentStatus, InvoiceStatus, QuoteStatus
)
from sales_module.services import OrderService


class TestOrderServiceIntegration:
    """Integration tests for OrderService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db_session = Mock(spec=Session)
        self.order_service = OrderService(db_session=self.mock_db_session)
        
        # Mock current time for consistent testing
        self.test_time = datetime(2025, 1, 6, 15, 30, 0)
        
    def create_test_quote(self) -> SalesQuote:
        """Create a test quote for conversion testing"""
        quote = SalesQuote(
            id=1,
            company_id=1,
            quote_number="Q-TEST-001",
            title="Test Quote for Order Conversion",
            description="Comprehensive test quote",
            customer_id=100,
            status=QuoteStatus.ACCEPTED,
            subtotal=Decimal('1500.00'),
            tax_amount=Decimal('150.00'),
            total_amount=Decimal('1650.00'),
            currency_code="USD",
            valid_from=self.test_time,
            valid_until=self.test_time + timedelta(days=30),
            payment_terms_days=30,
            prepared_by_user_id=1
        )
        
        # Add line items
        quote.line_items = [
            Mock(
                id=1,
                line_number=1,
                product_id=101,
                item_name="Test Product A",
                quantity=Decimal('5'),
                unit_price=Decimal('200.00'),
                line_total=Decimal('1000.00'),
                specifications={"size": "large"},
                custom_options={"color": "blue"}
            ),
            Mock(
                id=2,
                line_number=2,
                product_id=102,
                product_variant_id=201,
                item_name="Test Product B",
                quantity=Decimal('2'),
                unit_price=Decimal('250.00'),
                line_total=Decimal('500.00'),
                specifications={"material": "steel"},
                custom_options={"finish": "matte"}
            )
        ]
        
        return quote
    
    def create_test_order(self) -> SalesOrder:
        """Create a test order for testing"""
        order = SalesOrder(
            id=1,
            company_id=1,
            order_number="SO-TEST-001",
            title="Test Order",
            customer_id=100,
            status=OrderStatus.CONFIRMED,
            total_amount=Decimal('1650.00'),
            currency_code="USD"
        )
        
        # Add line items
        order.line_items = [
            Mock(
                id=1,
                product_id=101,
                item_name="Test Product A",
                quantity=Decimal('5'),
                unit_price=Decimal('200.00'),
                line_total=Decimal('1000.00')
            ),
            Mock(
                id=2,
                product_id=102,
                product_variant_id=201,
                item_name="Test Product B",
                quantity=Decimal('2'),
                unit_price=Decimal('250.00'),
                line_total=Decimal('500.00')
            )
        ]
        
        return order
    
    @patch('sales_module.services.order_service.SalesOrder')
    @patch('sales_module.services.order_service.SalesOrderLineItem')
    def test_create_order_from_quote_success(self, mock_line_item_class, mock_order_class):
        """Test successful order creation from quote"""
        # Setup
        quote = self.create_test_quote()
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = quote
        
        mock_order = Mock()
        mock_order_class.from_quote.return_value = mock_order
        mock_order.id = 1
        
        mock_line_item = Mock()
        mock_line_item_class.from_quote_line_item.return_value = mock_line_item
        
        # Execute
        result = self.order_service.create_order_from_quote(
            quote_id=1,
            order_data={"priority": "high"},
            user_id=1,
            company_id=1
        )
        
        # Verify
        assert result == mock_order
        mock_order_class.from_quote.assert_called_once_with(quote, 1, priority="high")
        mock_order.save.assert_called()
        quote.convert_to_order.assert_called_once_with(1, 1)
    
    def test_create_order_from_quote_not_found(self):
        """Test order creation fails when quote not found"""
        # Setup
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Quote 1 not found"):
            self.order_service.create_order_from_quote(
                quote_id=1,
                user_id=1,
                company_id=1
            )
    
    def test_create_order_from_quote_not_accepted(self):
        """Test order creation fails when quote not accepted"""
        # Setup
        quote = self.create_test_quote()
        quote.status = QuoteStatus.DRAFT
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = quote
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Quote 1 must be accepted"):
            self.order_service.create_order_from_quote(
                quote_id=1,
                user_id=1,
                company_id=1
            )
    
    @patch('sales_module.services.order_service.requests.get')
    def test_check_product_availability_success(self, mock_get):
        """Test successful inventory availability check"""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "can_fulfill": True,
            "available_quantity": 10,
            "locations": [{"location_id": 1, "quantity": 10}]
        }
        mock_get.return_value = mock_response
        
        # Execute
        result = self.order_service._check_product_availability(
            product_id=101,
            quantity=Decimal('5'),
            product_variant_id=None,
            company_id=1
        )
        
        # Verify
        assert result["can_fulfill"] is True
        assert result["available_quantity"] == 10
        mock_get.assert_called_once()
        
        # Verify request parameters
        call_args = mock_get.call_args
        assert call_args[1]["params"]["product_id"] == 101
        assert call_args[1]["params"]["quantity"] == "5"
        assert call_args[1]["params"]["company_id"] == 1
    
    @patch('sales_module.services.order_service.requests.get')
    def test_check_product_availability_service_error(self, mock_get):
        """Test inventory availability check with service error"""
        # Setup
        mock_get.side_effect = Exception("Connection error")
        
        # Execute
        result = self.order_service._check_product_availability(
            product_id=101,
            quantity=Decimal('5'),
            company_id=1
        )
        
        # Verify fallback response
        assert result["can_fulfill"] is False
        assert result["available_quantity"] == 0
        assert result["locations"] == []
    
    @patch('sales_module.services.order_service.requests.post')
    @patch('sales_module.services.order_service.requests.delete')
    def test_reserve_order_inventory_success(self, mock_delete, mock_post):
        """Test successful inventory reservation"""
        # Setup
        order = self.create_test_order()
        self.order_service.get_by_id = Mock(return_value=order)
        
        # Mock successful reservation responses
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "res-123", "quantity": "5"}
        mock_post.return_value = mock_response
        
        # Execute
        result = self.order_service._reserve_order_inventory(
            order_id=1,
            user_id=1,
            company_id=1
        )
        
        # Verify
        assert result is True
        assert mock_post.call_count == 2  # Two line items
        order.save.assert_called()
        
        # Verify reservation data was stored
        assert hasattr(order, 'inventory_reservations')
    
    @patch('sales_module.services.order_service.requests.post')
    @patch('sales_module.services.order_service.requests.delete')
    def test_reserve_order_inventory_partial_failure(self, mock_delete, mock_post):
        """Test inventory reservation with partial failure and rollback"""
        # Setup
        order = self.create_test_order()
        self.order_service.get_by_id = Mock(return_value=order)
        self.order_service._release_order_reservations = Mock()
        
        # Mock first reservation success, second failure
        success_response = Mock()
        success_response.status_code = 201
        success_response.json.return_value = {"id": "res-123", "quantity": "5"}
        
        failure_response = Mock()
        failure_response.status_code = 400
        failure_response.text = "Insufficient stock"
        
        mock_post.side_effect = [success_response, failure_response]
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Inventory reservation failed"):
            self.order_service._reserve_order_inventory(
                order_id=1,
                user_id=1,
                company_id=1
            )
        
        # Verify rollback was called
        self.order_service._release_order_reservations.assert_called_once()
    
    @patch('sales_module.services.order_service.requests.post')
    def test_consume_order_inventory_success(self, mock_post):
        """Test successful inventory consumption"""
        # Setup
        order = self.create_test_order()
        self.order_service.get_by_id = Mock(return_value=order)
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "mov-456"}
        mock_post.return_value = mock_response
        
        shipment_items = [
            {"line_item_id": 1, "quantity_shipped": 3},
            {"line_item_id": 2, "quantity_shipped": 2}
        ]
        
        # Execute
        result = self.order_service.consume_order_inventory(
            order_id=1,
            shipment_items=shipment_items,
            user_id=1,
            company_id=1
        )
        
        # Verify
        assert len(result["consumed_items"]) == 2
        assert len(result["errors"]) == 0
        assert mock_post.call_count == 2
        
        # Verify consumption data
        consumed_items = result["consumed_items"]
        assert consumed_items[0]["line_item_id"] == 1
        assert consumed_items[0]["quantity_consumed"] == "3"
        assert consumed_items[1]["line_item_id"] == 2
        assert consumed_items[1]["quantity_consumed"] == "2"
    
    def test_check_inventory_availability_for_order(self):
        """Test checking inventory availability for entire order"""
        # Setup
        order = self.create_test_order()
        self.order_service.get_by_id = Mock(return_value=order)
        self.order_service._check_product_availability = Mock(side_effect=[
            {"can_fulfill": True, "available_quantity": 10, "locations": []},
            {"can_fulfill": False, "available_quantity": 1, "locations": []}
        ])
        
        # Execute
        result = self.order_service.check_inventory_availability(
            order_id=1,
            company_id=1
        )
        
        # Verify
        assert result["order_id"] == 1
        assert result["can_fulfill"] is False  # One item can't be fulfilled
        assert len(result["line_items"]) == 2
        assert len(result["errors"]) == 1
        
        # Check specific line item results
        line_items = result["line_items"]
        assert line_items[0]["can_fulfill"] is True
        assert line_items[1]["can_fulfill"] is False
    
    @patch('sales_module.services.order_service.datetime')
    def test_confirm_order_with_inventory_reservation(self, mock_datetime):
        """Test order confirmation with inventory reservation"""
        # Setup
        mock_datetime.utcnow.return_value = self.test_time
        
        order = Mock()
        order.status = OrderStatus.DRAFT
        order.order_number = "SO-TEST-001"
        
        self.order_service.get_by_id = Mock(return_value=order)
        self.order_service._reserve_order_inventory = Mock(return_value=True)
        
        # Execute
        result = self.order_service.confirm_order(
            order_id=1,
            user_id=1,
            company_id=1
        )
        
        # Verify
        assert result == order
        order.confirm_order.assert_called_once_with(1)
        self.order_service._reserve_order_inventory.assert_called_once_with(1, 1, 1)
        assert order.status == OrderStatus.CONFIRMED
    
    def test_confirm_order_inventory_reservation_failure(self):
        """Test order confirmation with inventory reservation failure"""
        # Setup
        order = Mock()
        order.status = OrderStatus.DRAFT
        order.order_number = "SO-TEST-001"
        
        self.order_service.get_by_id = Mock(return_value=order)
        self.order_service._reserve_order_inventory = Mock(side_effect=Exception("No stock"))
        
        # Execute & Verify
        with pytest.raises(ValueError, match="inventory reservation failed"):
            self.order_service.confirm_order(
                order_id=1,
                user_id=1,
                company_id=1
            )
        
        # Verify order was put on hold
        order.put_on_hold.assert_called_once()
    
    def test_cancel_order_with_inventory_release(self):
        """Test order cancellation with inventory release"""
        # Setup
        order = Mock()
        order.status = OrderStatus.CONFIRMED
        order.order_number = "SO-TEST-001"
        
        self.order_service.get_by_id = Mock(return_value=order)
        self.order_service.release_order_inventory = Mock(return_value=True)
        
        # Execute
        result = self.order_service.cancel_order(
            order_id=1,
            reason="Customer requested cancellation",
            user_id=1,
            company_id=1
        )
        
        # Verify
        assert result == order
        order.cancel_order.assert_called_once_with("Customer requested cancellation", 1)
        self.order_service.release_order_inventory.assert_called_once_with(1, 1, 1)
    
    @patch('sales_module.services.order_service.requests.delete')
    def test_release_order_inventory(self, mock_delete):
        """Test releasing order inventory reservations"""
        # Setup
        order = Mock()
        order.inventory_reservations = [
            {"reservation_id": "res-123", "line_item_id": 1},
            {"reservation_id": "res-456", "line_item_id": 2}
        ]
        
        self.order_service.get_by_id = Mock(return_value=order)
        
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        # Execute
        result = self.order_service.release_order_inventory(
            order_id=1,
            user_id=1,
            company_id=1
        )
        
        # Verify
        assert result is True
        assert mock_delete.call_count == 2
        assert order.inventory_reservations == []
        order.save.assert_called()
    
    def test_get_order_fulfillment_status(self):
        """Test getting comprehensive fulfillment status"""
        # Setup
        order = Mock()
        order.id = 1
        order.order_number = "SO-TEST-001"
        order.status = OrderStatus.PARTIALLY_SHIPPED
        order.fulfillment_percentage = 60.0
        order.payment_percentage = 50.0
        order.items_shipped = 3
        order.items_remaining = 2
        order.shipment_count = 1
        order.is_overdue = False
        order.days_until_required = 5
        order.payment_status = PaymentStatus.PARTIALLY_PAID
        order.paid_amount = Decimal('825.00')
        order.outstanding_amount = Decimal('825.00')
        
        self.order_service.get_by_id = Mock(return_value=order)
        
        # Execute
        result = self.order_service.get_order_fulfillment_status(
            order_id=1,
            company_id=1
        )
        
        # Verify
        assert result["order_id"] == 1
        assert result["order_number"] == "SO-TEST-001"
        assert result["status"] == "PARTIALLY_SHIPPED"
        assert result["fulfillment_percentage"] == 60.0
        assert result["payment_percentage"] == 50.0
        assert result["items_shipped"] == 3
        assert result["items_remaining"] == 2
        assert result["is_overdue"] is False
        assert result["paid_amount"] == 825.00
        assert result["outstanding_amount"] == 825.00
    
    def test_get_order_analytics(self):
        """Test getting order analytics"""
        # Execute
        result = self.order_service.get_order_analytics(
            company_id=1,
            date_range={"from": self.test_time, "to": self.test_time + timedelta(days=30)}
        )
        
        # Verify structure
        assert "summary" in result
        assert "financial_metrics" in result
        assert "fulfillment_metrics" in result
        assert "by_status" in result
        
        # Verify summary structure
        summary = result["summary"]
        expected_fields = [
            "total_orders", "orders_confirmed", "orders_shipped",
            "orders_delivered", "orders_completed", "orders_cancelled"
        ]
        for field in expected_fields:
            assert field in summary
        
        # Verify financial metrics
        financial = result["financial_metrics"]
        expected_financial = [
            "total_order_value", "average_order_value",
            "total_paid", "total_outstanding"
        ]
        for field in expected_financial:
            assert field in financial


def run_tests():
    """Run all order service integration tests"""
    print("🧪 Running Order Service Integration Tests")
    print("=" * 60)
    
    # Configure pytest to run tests
    test_args = [
        __file__,
        "-v",  # Verbose output
        "-s",  # Don't capture output
        "--tb=short"  # Short traceback format
    ]
    
    # Run tests
    result = pytest.main(test_args)
    
    if result == 0:
        print("\n✅ All Order Service Integration Tests Passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return result == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)