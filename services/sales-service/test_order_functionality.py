#!/usr/bin/env python3
"""
Order Service Functionality Test

Simple test without external dependencies to verify order service
functionality including quote conversion, inventory integration,
and fulfillment workflows.
"""

import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add the sales_module to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from sales_module.models import (
        SalesQuote, SalesOrder, SalesOrderLineItem, OrderShipment, OrderInvoice,
        OrderStatus, PaymentStatus, ShipmentStatus, InvoiceStatus, QuoteStatus
    )
    from sales_module.services import OrderService
    print("✅ Successfully imported sales module components")
except ImportError as e:
    print(f"❌ Failed to import sales module: {e}")
    sys.exit(1)


class SimpleOrderServiceTest:
    """Simple test class for order service functionality"""
    
    def __init__(self):
        self.test_results = []
        self.mock_db_session = Mock()
        self.order_service = OrderService(db_session=self.mock_db_session)
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"    {details}")
        self.test_results.append((test_name, success, details))
    
    def create_mock_quote(self) -> Mock:
        """Create a mock quote for testing"""
        quote = Mock()
        quote.id = 1
        quote.company_id = 1
        quote.quote_number = "Q-TEST-001"
        quote.title = "Test Quote"
        quote.customer_id = 100
        quote.status = QuoteStatus.ACCEPTED
        quote.total_amount = Decimal('1650.00')
        quote.currency_code = "USD"
        
        # Mock line items
        line_item1 = Mock()
        line_item1.id = 1
        line_item1.product_id = 101
        line_item1.item_name = "Product A"
        line_item1.quantity = Decimal('5')
        line_item1.unit_price = Decimal('200.00')
        
        line_item2 = Mock()
        line_item2.id = 2
        line_item2.product_id = 102
        line_item2.product_variant_id = 201
        line_item2.item_name = "Product B"
        line_item2.quantity = Decimal('2')
        line_item2.unit_price = Decimal('250.00')
        
        quote.line_items = [line_item1, line_item2]
        return quote
    
    def create_mock_order(self) -> Mock:
        """Create a mock order for testing"""
        order = Mock()
        order.id = 1
        order.company_id = 1
        order.order_number = "SO-TEST-001"
        order.title = "Test Order"
        order.customer_id = 100
        order.status = OrderStatus.CONFIRMED
        order.total_amount = Decimal('1650.00')
        order.currency_code = "USD"
        
        # Mock line items
        line_item1 = Mock()
        line_item1.id = 1
        line_item1.product_id = 101
        line_item1.item_name = "Product A"
        line_item1.quantity = Decimal('5')
        
        line_item2 = Mock()
        line_item2.id = 2
        line_item2.product_id = 102
        line_item2.product_variant_id = 201
        line_item2.item_name = "Product B"
        line_item2.quantity = Decimal('2')
        
        order.line_items = [line_item1, line_item2]
        return order
    
    def test_order_service_initialization(self):
        """Test order service can be initialized"""
        try:
            service = OrderService(db_session=self.mock_db_session)
            assert service.model_class == SalesOrder
            assert hasattr(service, 'inventory_service_url')
            assert hasattr(service, 'inventory_timeout')
            self.log_test("Order Service Initialization", True, "Service initialized with correct attributes")
        except Exception as e:
            self.log_test("Order Service Initialization", False, str(e))
    
    @patch('sales_module.services.order_service.SalesOrder')
    @patch('sales_module.services.order_service.SalesOrderLineItem')
    def test_create_order_from_quote(self, mock_line_item_class, mock_order_class):
        """Test order creation from quote"""
        try:
            # Setup mocks
            quote = self.create_mock_quote()
            self.mock_db_session.query.return_value.filter.return_value.first.return_value = quote
            
            mock_order = Mock()
            mock_order.id = 1
            mock_order_class.from_quote.return_value = mock_order
            
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
            self.log_test("Create Order From Quote", True, f"Order created from quote {quote.quote_number}")
            
        except Exception as e:
            self.log_test("Create Order From Quote", False, str(e))
    
    def test_quote_not_found_handling(self):
        """Test handling of quote not found scenario"""
        try:
            # Setup: No quote found
            self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
            
            # Execute and verify exception
            try:
                self.order_service.create_order_from_quote(
                    quote_id=999,
                    user_id=1,
                    company_id=1
                )
                self.log_test("Quote Not Found Handling", False, "Expected ValueError not raised")
            except ValueError as ve:
                if "Quote 999 not found" in str(ve):
                    self.log_test("Quote Not Found Handling", True, "Correct error message for missing quote")
                else:
                    self.log_test("Quote Not Found Handling", False, f"Unexpected error message: {ve}")
            except Exception as e:
                self.log_test("Quote Not Found Handling", False, f"Unexpected exception type: {e}")
                
        except Exception as e:
            self.log_test("Quote Not Found Handling", False, str(e))
    
    @patch('sales_module.services.order_service.requests.get')
    def test_check_product_availability(self, mock_get):
        """Test inventory availability checking"""
        try:
            # Setup mock response
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
                company_id=1
            )
            
            # Verify
            assert result["can_fulfill"] is True
            assert result["available_quantity"] == 10
            self.log_test("Check Product Availability", True, "Availability check returned expected data")
            
        except Exception as e:
            self.log_test("Check Product Availability", False, str(e))
    
    @patch('sales_module.services.order_service.requests.get')
    def test_inventory_service_connection_error(self, mock_get):
        """Test handling of inventory service connection errors"""
        try:
            # Setup: Connection error
            mock_get.side_effect = Exception("Connection refused")
            
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
            self.log_test("Inventory Service Connection Error", True, "Graceful fallback when inventory service unavailable")
            
        except Exception as e:
            self.log_test("Inventory Service Connection Error", False, str(e))
    
    def test_check_inventory_availability_for_order(self):
        """Test checking availability for entire order"""
        try:
            # Setup
            order = self.create_mock_order()
            self.order_service.get_by_id = Mock(return_value=order)
            self.order_service._check_product_availability = Mock(side_effect=[
                {"can_fulfill": True, "available_quantity": 10, "locations": []},
                {"can_fulfill": False, "available_quantity": 1, "locations": []}
            ])
            
            # Execute
            result = self.order_service.check_inventory_availability(order_id=1, company_id=1)
            
            # Verify
            assert result["order_id"] == 1
            assert result["can_fulfill"] is False  # One item can't be fulfilled
            assert len(result["line_items"]) == 2
            assert len(result["errors"]) == 1
            self.log_test("Check Order Inventory Availability", True, "Order-level availability check working correctly")
            
        except Exception as e:
            self.log_test("Check Order Inventory Availability", False, str(e))
    
    @patch('sales_module.services.order_service.requests.post')
    def test_consume_order_inventory(self, mock_post):
        """Test inventory consumption during shipment"""
        try:
            # Setup
            order = self.create_mock_order()
            self.order_service.get_by_id = Mock(return_value=order)
            
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "mov-123"}
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
            assert result["consumed_items"][0]["quantity_consumed"] == "3"
            assert result["consumed_items"][1]["quantity_consumed"] == "2"
            self.log_test("Consume Order Inventory", True, "Inventory consumption processed correctly")
            
        except Exception as e:
            self.log_test("Consume Order Inventory", False, str(e))
    
    def test_get_order_fulfillment_status(self):
        """Test getting order fulfillment status"""
        try:
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
            result = self.order_service.get_order_fulfillment_status(order_id=1, company_id=1)
            
            # Verify
            assert result["order_id"] == 1
            assert result["status"] == "PARTIALLY_SHIPPED"
            assert result["fulfillment_percentage"] == 60.0
            assert result["payment_percentage"] == 50.0
            assert result["paid_amount"] == 825.00
            self.log_test("Get Order Fulfillment Status", True, "Fulfillment status returned correctly")
            
        except Exception as e:
            self.log_test("Get Order Fulfillment Status", False, str(e))
    
    def test_get_order_analytics(self):
        """Test order analytics functionality"""
        try:
            # Execute
            result = self.order_service.get_order_analytics(
                company_id=1,
                date_range={"from": datetime.now(), "to": datetime.now() + timedelta(days=30)}
            )
            
            # Verify structure
            required_sections = ["summary", "financial_metrics", "fulfillment_metrics", "by_status"]
            for section in required_sections:
                assert section in result
            
            # Verify summary fields
            summary_fields = ["total_orders", "orders_confirmed", "orders_shipped", "orders_completed"]
            for field in summary_fields:
                assert field in result["summary"]
            
            self.log_test("Get Order Analytics", True, "Analytics structure is correct")
            
        except Exception as e:
            self.log_test("Get Order Analytics", False, str(e))
    
    def test_order_models_can_be_instantiated(self):
        """Test that order models can be instantiated"""
        try:
            # Test SalesOrder
            order = SalesOrder(
                company_id=1,
                order_number="TEST-001",
                title="Test Order",
                customer_id=100,
                status=OrderStatus.DRAFT,
                total_amount=Decimal('1000.00')
            )
            assert order.company_id == 1
            assert order.status == OrderStatus.DRAFT
            
            # Test SalesOrderLineItem
            line_item = SalesOrderLineItem(
                company_id=1,
                order_id=1,
                line_number=1,
                item_name="Test Item",
                quantity=Decimal('5'),
                unit_price=Decimal('100.00'),
                line_total=Decimal('500.00')
            )
            assert line_item.quantity == Decimal('5')
            
            self.log_test("Order Models Instantiation", True, "All order models can be created")
            
        except Exception as e:
            self.log_test("Order Models Instantiation", False, str(e))
    
    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🧪 Running Order Service Functionality Tests")
        print("=" * 60)
        
        # Run individual tests
        self.test_order_service_initialization()
        self.test_create_order_from_quote()
        self.test_quote_not_found_handling()
        self.test_check_product_availability()
        self.test_inventory_service_connection_error()
        self.test_check_inventory_availability_for_order()
        self.test_consume_order_inventory()
        self.test_get_order_fulfillment_status()
        self.test_get_order_analytics()
        self.test_order_models_can_be_instantiated()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        failed = sum(1 for _, success, _ in self.test_results if not success)
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📝 Total:  {total}")
        
        if failed > 0:
            print("\nFailed Tests:")
            for name, success, details in self.test_results:
                if not success:
                    print(f"   • {name}: {details}")
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 All tests passed! Order service functionality is working correctly.")
        elif success_rate >= 80:
            print("⚠️  Most tests passed. Minor issues detected.")
        else:
            print("❌ Multiple test failures. Order service needs attention.")
        
        return success_rate == 100


def main():
    """Main test runner"""
    tester = SimpleOrderServiceTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()