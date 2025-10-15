"""
Test scenarios for sales order creation.

Comprehensive test coverage for creating sales orders through various scenarios:
- Basic order creation
- Order creation from quotes
- Order validation
- Error handling during creation
- Date handling scenarios including the time component fix
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from sales_module.models.order import SalesOrder, OrderStatus, PaymentStatus
from sales_module.services.order_service import OrderService


class TestSalesOrderCreationScenarios:
    """Test scenarios for sales order creation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.order_service = OrderService(db_session=self.mock_db_session)
        self.test_time = datetime(2025, 1, 6, 15, 30, 0)
        
    def create_basic_order_data(self):
        """Create basic order data for testing."""
        return {
            "order_number": "SO202500001",
            "title": "Test Order",
            "description": "Test order description",
            "customer_id": 100,
            "sales_rep_user_id": 1,
            "total_amount": Decimal("1000.00"),
            "currency_code": "USD"
        }
        
    def test_basic_order_creation(self):
        """Test basic order creation with minimal required fields."""
        order_data = self.create_basic_order_data()
        
        with patch('sales_module.services.order_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = self.test_time
            
            # Execute
            result = self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
            
            # Verify results
            assert result.order_number == "SO202500001"
            assert result.title == "Test Order"
            assert result.customer_id == 100
            assert result.status == OrderStatus.DRAFT  # Default status
            assert result.payment_status == PaymentStatus.PENDING  # Default status
            assert result.order_date == self.test_time  # Set by service
            assert result.sales_rep_user_id == 1  # Set from user_id if not provided in data
            
    def test_order_creation_with_line_items(self):
        """Test order creation with line items."""
        order_data = self.create_basic_order_data()
        line_items = [
            {
                "line_number": 1,
                "item_name": "Test Product 1",
                "quantity": Decimal("2"),
                "unit_price": Decimal("500.00"),
                "line_total": Decimal("1000.00")
            }
        ]
        
        # Mock the methods called by create_order
        self.order_service.create = Mock(return_value=Mock(id=1, order_number="SO202500001"))
        self.order_service.add_line_item = Mock(return_value=Mock(id=1))
        self.order_service.calculate_order_totals = Mock()
        
        with patch('sales_module.services.order_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = self.test_time
            
            # Execute
            result = self.order_service.create_order(
                order_data=order_data,
                line_items=line_items,
                user_id=1,
                company_id=1
            )
            
            # Verify methods were called
            assert result is not None
            self.order_service.add_line_item.assert_called_once()
            self.order_service.calculate_order_totals.assert_called_once()
            
    def test_order_creation_auto_generates_number(self):
        """Test that order number is auto-generated if not provided."""
        order_data = self.create_basic_order_data()
        order_data.pop("order_number")  # Remove order number to trigger auto-generation
        
        # Mock the generate_order_number method
        with patch.object(self.order_service, 'generate_order_number', return_value="SO-AUTO-001"):
            with patch('sales_module.services.order_service.datetime') as mock_datetime:
                mock_datetime.utcnow.return_value = self.test_time
                
                # Execute
                result = self.order_service.create_order(
                    order_data=order_data,
                    user_id=1,
                    company_id=1
                )
                
                # Verify auto-generation
                assert result.order_number == "SO-AUTO-001"
                
    def test_order_creation_sets_current_user_as_sales_rep(self):
        """Test that sales_rep_user_id is set to the current user if not provided."""
        order_data = self.create_basic_order_data()
        order_data.pop("sales_rep_user_id")  # Remove to trigger auto-setting
        
        with patch('sales_module.services.order_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = self.test_time
            
            # Execute
            result = self.order_service.create_order(
                order_data=order_data,
                user_id=5,
                company_id=1
            )
            
            # Verify sales rep was set to user
            assert result.sales_rep_user_id == 5
            
    def test_order_creation_with_existing_sales_rep(self):
        """Test that provided sales_rep_user_id is preserved."""
        order_data = self.create_basic_order_data()
        order_data["sales_rep_user_id"] = 99  # Override with different user
        
        with patch('sales_module.services.order_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = self.test_time
            
            # Execute
            result = self.order_service.create_order(
                order_data=order_data,
                user_id=5,  # Different user creating the order
                company_id=1
            )
            
            # Verify provided sales rep is preserved
            assert result.sales_rep_user_id == 99
            
    def test_order_creation_with_order_date_as_datetime(self):
        """Test order creation with explicit datetime value."""
        order_data = self.create_basic_order_data()
        explicit_date = datetime(2025, 1, 10, 9, 0, 0)
        order_data["order_date"] = explicit_date
        
        # Execute
        result = self.order_service.create_order(
            order_data=order_data,
            user_id=1,
            company_id=1
        )
        
        # Verify explicit date is preserved
        assert result.order_date == explicit_date
        
    def test_order_creation_with_order_date_as_date(self):
        """Test order creation with date-only value (should be converted to datetime with 00:00:00 time)."""
        order_data = self.create_basic_order_data()
        from datetime import date
        date_only = date(2025, 1, 10)
        order_data["order_date"] = date_only
        
        # Execute
        result = self.order_service.create_order(
            order_data=order_data,
            user_id=1,
            company_id=1
        )
        
        # Verify date is converted to datetime with 00:00:00 time
        expected_datetime = datetime(2025, 1, 10, 0, 0, 0)
        assert result.order_date == expected_datetime
        
    def test_order_creation_with_order_date_as_string(self):
        """Test order creation with date string (should be converted to datetime with 00:00:00 time)."""
        order_data = self.create_basic_order_data()
        order_data["order_date"] = "2025-01-10"  # Date string without time
        
        # Execute
        result = self.order_service.create_order(
            order_data=order_data,
            user_id=1,
            company_id=1
        )
        
        # Verify date string is converted to datetime with 00:00:00 time
        expected_datetime = datetime(2025, 1, 10, 0, 0, 0)
        assert result.order_date == expected_datetime
        
    def test_order_creation_with_datetime_string(self):
        """Test order creation with datetime string (should preserve time components)."""
        order_data = self.create_basic_order_data()
        order_data["order_date"] = "2025-01-10T15:30:00"  # Datetime string with time
        
        # Execute
        result = self.order_service.create_order(
            order_data=order_data,
            user_id=1,
            company_id=1
        )
        
        # Verify datetime string is parsed and time is preserved
        expected_datetime = datetime(2025, 1, 10, 15, 30, 0)
        assert result.order_date == expected_datetime
        
    def test_order_creation_validation_required_fields(self):
        """Test that required fields validation works during creation."""
        # Test without customer_id (should fail validation)
        order_data = self.create_basic_order_data()
        order_data.pop("customer_id")
        
        with pytest.raises(ValueError, match="Field 'customer_id' is required for order creation"):
            self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
            
    def test_order_creation_validation_date_comparison(self):
        """Test that date validation works during creation."""
        order_data = self.create_basic_order_data()
        # Set required date before order date (should fail validation)
        order_data["order_date"] = datetime(2025, 1, 10)
        order_data["required_date"] = datetime(2025, 1, 5)  # Before order date
        
        with pytest.raises(ValueError, match="Required date cannot be before order date"):
            self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
            
    def test_order_creation_with_valid_dates(self):
        """Test order creation with valid date relationships."""
        order_data = self.create_basic_order_data()
        # Set required date after order date (should be valid)
        order_data["order_date"] = datetime(2025, 1, 10)
        order_data["required_date"] = datetime(2025, 1, 15)  # After order date
        
        with patch('sales_module.services.order_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2025, 1, 10, 12, 0, 0)
            
            # Execute - this should not raise an error
            result = self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
            
            # Verify the order was created successfully
            assert result is not None
            assert result.order_date == datetime(2025, 1, 10)
            assert result.required_date == datetime(2025, 1, 15)
            
    def test_order_creation_with_none_dates(self):
        """Test order creation when required_date is None (should not fail validation)."""
        order_data = self.create_basic_order_data()
        order_data["order_date"] = datetime(2025, 1, 10)
        order_data["required_date"] = None  # None value should not cause validation to fail
        
        with patch('sales_module.services.order_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2025, 1, 10, 12, 0, 0)
            
            # Execute - this should not raise an error
            result = self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
            
            # Verify the order was created successfully
            assert result is not None
            assert result.order_date == datetime(2025, 1, 10)
            assert result.required_date is None
            
    def test_order_creation_with_missing_order_date(self):
        """Test order creation when order_date is not provided (should be set to current time)."""
        order_data = self.create_basic_order_data()
        order_data.pop("order_date")  # Remove order_date to trigger auto-setting
        
        with patch('sales_module.services.order_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = self.test_time
            
            result = self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
            
            # Verify order date was set to current time
            assert result.order_date == self.test_time
            
    def test_order_creation_error_handling(self):
        """Test error handling during order creation."""
        # This test would need more sophisticated mocking to test actual error scenarios
        # For now, test the validation error path
        order_data = self.create_basic_order_data()
        order_data.pop("customer_id")  # Missing required field
        
        with pytest.raises(ValueError):
            self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )


class TestSalesOrderFromQuoteCreation:
    """Test scenarios for creating sales orders from quotes."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.order_service = OrderService(db_session=self.mock_db_session)
        self.test_time = datetime(2025, 1, 6, 15, 30, 0)
        
    def create_mock_quote(self):
        """Create a mock quote for testing."""
        quote = Mock()
        quote.id = 1
        quote.company_id = 1
        quote.quote_number = "QT202500001"
        quote.title = "Test Quotation"
        quote.customer_id = 100
        quote.status = "accepted"  # String status to match actual model
        quote.total_amount = Decimal("1500.00")
        quote.currency_code = "USD"
        quote.payment_terms_days = 30
        quote.line_items = []
        return quote
        
    def test_create_order_from_accepted_quote(self):
        """Test creating order from accepted quote."""
        quote = self.create_mock_quote()
        
        # Mock the database query to return the quote
        mock_query = Mock()
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = quote
        
        # Mock the from_quote method on SalesOrder
        with patch('sales_module.models.order.SalesOrder') as mock_sales_order_class:
            mock_order = Mock()
            mock_sales_order_class.from_quote.return_value = mock_order
            mock_order.order_number = "SO-NEW-001"
            mock_order.id = 1
            
            # Execute
            result = self.order_service.create_order_from_quote(
                quote_id=1,
                user_id=1,
                company_id=1
            )
            
            # Verify
            assert result == mock_order
            mock_sales_order_class.from_quote.assert_called_once_with(quote, 1)
            
    def test_create_order_from_quote_not_found(self):
        """Test error when quote is not found."""
        # Mock the database query to return None
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Quotation 1 not found"):
            self.order_service.create_order_from_quote(
                quote_id=1,
                user_id=1,
                company_id=1
            )
            
    def test_create_order_from_quote_not_accepted(self):
        """Test error when quote is not accepted."""
        quote = self.create_mock_quote()
        quote.status = "draft"  # Not accepted
        
        # Mock the database query to return the quote
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = quote
        
        with pytest.raises(ValueError, match="must be accepted before creating order"):
            self.order_service.create_order_from_quote(
                quote_id=1,
                user_id=1,
                company_id=1
            )


def run_order_creation_tests():
    """Run all order creation tests and display results."""
    print("🧪 Running Sales Order Creation Test Scenarios")
    print("=" * 70)
    
    # Create test instances
    order_creation_tests = TestSalesOrderCreationScenarios()
    quote_creation_tests = TestSalesOrderFromQuoteCreation()
    
    # Run tests
    passed = 0
    failed = 0
    total = 0
    
    # Test basic order creation scenarios
    test_methods = [
        method for method in dir(order_creation_tests) 
        if method.startswith("test_")
    ]
    
    for test_method_name in test_methods:
        total += 1
        try:
            test_method = getattr(order_creation_tests, test_method_name)
            order_creation_tests.setup_method()  # Reset before each test
            test_method()
            print(f"✅ {test_method_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_method_name}: {str(e)}")
            failed += 1
    
    # Test quote creation scenarios
    quote_test_methods = [
        method for method in dir(quote_creation_tests) 
        if method.startswith("test_")
    ]
    
    for test_method_name in quote_test_methods:
        total += 1
        try:
            test_method = getattr(quote_creation_tests, test_method_name)
            quote_creation_tests.setup_method()  # Reset before each test
            test_method()
            print(f"✅ {test_method_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_method_name}: {str(e)}")
            failed += 1
    
    # Print summary
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📝 Total:  {total}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All Sales Order Creation Tests Passed!")
    elif success_rate >= 80:
        print("⚠️  Most tests passed. Minor issues detected.")
    else:
        print("❌ Multiple test failures. Order creation needs attention.")
    
    return success_rate == 100


if __name__ == "__main__":
    success = run_order_creation_tests()
    exit(0 if success else 1)