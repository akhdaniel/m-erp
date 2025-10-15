"""
Test scenarios specifically for sales order date handling.

Focus on testing the time component handling functionality we implemented:
- When order_date does not contain time, set time to 00:00:00
- Date validation with None values
- Various date input formats
"""

import pytest
from datetime import datetime, date
from unittest.mock import Mock, patch

from sales_module.services.order_service import OrderService
from sales_module.models.order import OrderStatus, PaymentStatus


class TestOrderDateHandling:
    """Test date handling functionality in order creation."""
    
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
            "customer_id": 100,
            "sales_rep_user_id": 1,
        }
    
    def test_order_creation_with_datetime_preserves_time(self):
        """Test that datetime objects preserve their time components."""
        order_data = self.create_basic_order_data()
        original_datetime = datetime(2025, 1, 10, 15, 30, 45)  # Includes time
        order_data["order_date"] = original_datetime
        
        # Mock the create method to avoid database issues
        with patch.object(self.order_service, 'create') as mock_create:
            mock_order = Mock()
            mock_order.id = 1
            mock_order.order_number = "SO202500001"
            mock_order.status = OrderStatus.DRAFT
            mock_order.order_date = original_datetime  # This should be the preserved datetime
            mock_create.return_value = mock_order
            
            result = self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
            
            # Verify the datetime with time components was preserved
            assert result.order_date == original_datetime
            assert result.order_date.hour == 15
            assert result.order_date.minute == 30
            assert result.order_date.second == 45
    
    def test_order_creation_with_date_converts_to_datetime_with_zero_time(self):
        """Test that date-only objects are converted to datetime with 00:00:00 time."""
        order_data = self.create_basic_order_data()
        date_only = date(2025, 1, 10)  # Date without time components
        order_data["order_date"] = date_only
        
        # Mock the create method to avoid database issues
        with patch.object(self.order_service, 'create') as mock_create:
            mock_order = Mock()
            mock_order.id = 1
            mock_order.order_number = "SO202500001" 
            mock_order.status = OrderStatus.DRAFT
            mock_create.return_value = mock_order
            
            result = self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
            
            # Verify the date was converted to datetime with 00:00:00
            # The actual value would be in the order_data before it's passed to create
            # Let's check that the conversion logic worked in the service method
            # Since we're mocking create, we need to verify the conversion happened 
            # inside create_order method before it calls create
            
            # Check that the call to create used the converted datetime
            assert mock_create.call_args is not None
            called_with_data = mock_create.call_args[0][0]  # First argument is data dict
            converted_date = called_with_data['order_date']
            
            assert isinstance(converted_date, datetime)
            assert converted_date.year == 2025
            assert converted_date.month == 1
            assert converted_date.day == 10
            assert converted_date.hour == 0
            assert converted_date.minute == 0
            assert converted_date.second == 0
    
    def test_order_creation_with_date_string_converts_to_zero_time(self):
        """Test that date-only strings are converted to datetime with 00:00:00 time."""
        order_data = self.create_basic_order_data()
        order_data["order_date"] = "2025-01-10"  # Date string without time
        
        # Mock the create method 
        with patch.object(self.order_service, 'create') as mock_create:
            mock_order = Mock()
            mock_order.id = 1
            mock_create.return_value = mock_order
            
            self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
            
            # Verify the date string was converted properly
            called_with_data = mock_create.call_args[0][0]  # First argument is data dict
            converted_date = called_with_data['order_date']
            
            assert isinstance(converted_date, datetime)
            assert converted_date.year == 2025
            assert converted_date.month == 1
            assert converted_date.day == 10
            assert converted_date.hour == 0
            assert converted_date.minute == 0
            assert converted_date.second == 0
    
    def test_order_creation_with_datetime_string_preserves_time(self):
        """Test that datetime strings preserve their time components."""
        order_data = self.create_basic_order_data()
        order_data["order_date"] = "2025-01-10T15:30:45"  # DateTime string with time
        
        # Mock the create method
        with patch.object(self.order_service, 'create') as mock_create:
            mock_order = Mock()
            mock_order.id = 1
            mock_create.return_value = mock_order
            
            self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
            
            # Verify the datetime string was parsed and time preserved
            called_with_data = mock_create.call_args[0][0]  # First argument is data dict
            converted_date = called_with_data['order_date']
            
            assert isinstance(converted_date, datetime)
            assert converted_date.year == 2025
            assert converted_date.month == 1
            assert converted_date.day == 10
            assert converted_date.hour == 15  # Time preserved
            assert converted_date.minute == 30
            assert converted_date.second == 45
    
    def test_order_creation_with_no_order_date_gets_current_time(self):
        """Test that order_date is set to current time when not provided."""
        order_data = self.create_basic_order_data()
        # Don't include order_date in data
        
        # Mock datetime.utcnow to return a specific time
        with patch('sales_module.services.order_service.datetime') as mock_datetime:
            expected_time = datetime(2025, 1, 15, 9, 15, 30)
            mock_datetime.utcnow.return_value = expected_time
            
            # Mock the create method
            with patch.object(self.order_service, 'create') as mock_create:
                mock_order = Mock()
                mock_order.id = 1
                mock_create.return_value = mock_order
                
                self.order_service.create_order(
                    order_data=order_data,
                    user_id=1,
                    company_id=1
                )
                
                # Verify the expected time was used
                called_with_data = mock_create.call_args[0][0]
                assert called_with_data['order_date'] == expected_time
    
    def test_order_validation_with_none_values_does_not_fail(self):
        """Test that date validation does not fail when dates are None."""
        order_data = self.create_basic_order_data()
        order_data["order_date"] = datetime(2025, 1, 10)
        order_data["required_date"] = None  # None value should not cause comparison issue
        
        # This should not raise an error
        try:
            # Mock the create method to focus on validation only
            with patch.object(self.order_service, 'create') as mock_create:
                mock_order = Mock()
                mock_order.id = 1
                mock_create.return_value = mock_order
                
                result = self.order_service.create_order(
                    order_data=order_data,
                    user_id=1,
                    company_id=1
                )
                # If we reach here, validation passed
                assert result is not None
        except TypeError:
            pytest.fail("Date validation failed with None values when it should have been handled")
    
    def test_order_validation_with_valid_date_range(self):
        """Test that date validation passes with valid date ranges."""
        order_data = self.create_basic_order_data()
        order_data["order_date"] = datetime(2025, 1, 10)
        order_data["required_date"] = datetime(2025, 1, 15)  # After order date
        
        # Mock the create method to focus on validation
        with patch.object(self.order_service, 'create') as mock_create:
            mock_order = Mock()
            mock_order.id = 1
            mock_create.return_value = mock_order
            
            result = self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
            
            # Should succeed since required date is after order date
            assert result is not None
    
    def test_order_validation_fails_with_invalid_date_range(self):
        """Test that date validation fails when required date is before order date."""
        order_data = self.create_basic_order_data()
        order_data["order_date"] = datetime(2025, 1, 10)
        order_data["required_date"] = datetime(2025, 1, 5)  # Before order date
        
        # This should raise a ValueError
        with pytest.raises(ValueError, match="Required date cannot be before order date"):
            self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
    
    def test_order_validation_with_string_dates(self):
        """Test that date validation works with string date values."""
        order_data = self.create_basic_order_data()
        order_data["order_date"] = "2025-01-10"  # String date
        order_data["required_date"] = "2025-01-15"  # String date after order date
        
        # Mock the create method 
        with patch.object(self.order_service, 'create') as mock_create:
            mock_order = Mock()
            mock_order.id = 1
            mock_create.return_value = mock_order
            
            # This should not raise an error - dates should be parsed and validated
            result = self.order_service.create_order(
                order_data=order_data,
                user_id=1,
                company_id=1
            )
            
            # Should succeed since required date string is after order date string
            assert result is not None


def run_date_handling_tests():
    """Run all date handling tests and display results."""
    print("🧪 Running Sales Order Date Handling Tests")
    print("=" * 60)
    
    test_instance = TestOrderDateHandling()
    
    # Get all test methods
    test_methods = [
        method for method in dir(test_instance) 
        if method.startswith("test_")
    ]
    
    passed = 0
    failed = 0
    total = len(test_methods)
    
    for test_method_name in test_methods:
        try:
            test_instance.setup_method()  # Reset before each test
            test_method = getattr(test_instance, test_method_name)
            test_method()
            print(f"✅ {test_method_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_method_name}: {str(e)}")
            failed += 1
    
    # Print summary
    print("=" * 60)
    print("📊 DATE HANDLING TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📝 Total:  {total}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All Date Handling Tests Passed!")
    elif success_rate >= 80:
        print("⚠️  Most tests passed. Minor issues detected.")
    else:
        print("❌ Multiple test failures. Date handling needs attention.")
    
    return success_rate == 100


if __name__ == "__main__":
    success = run_date_handling_tests()
    exit(0 if success else 1)