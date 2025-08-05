"""
Tests for QuoteService business logic and workflow management.

Comprehensive test suite for quote service operations including
CRUD operations, workflow management, approval processes, and integrations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta

from sales_module.services.quote_service import QuoteService
from sales_module.models.quote import (
    SalesQuote, SalesQuoteLineItem, QuoteVersion, QuoteApproval,
    QuoteStatus, ApprovalStatus, LineItemType
)


class TestQuoteServiceInit:
    """Test QuoteService initialization and configuration."""
    
    def test_service_initialization(self):
        """Test service initializes correctly."""
        service = QuoteService()
        
        assert service.model_class == SalesQuote
        assert service.db_session is None
        
        # Test with database session
        mock_session = Mock()
        service_with_session = QuoteService(mock_session)
        assert service_with_session.db_session == mock_session


class TestQuoteCreation:
    """Test quote creation functionality."""
    
    @pytest.fixture
    def quote_service(self):
        """Create quote service with mocked session."""
        mock_session = Mock()
        return QuoteService(mock_session)
    
    @pytest.fixture
    def sample_quote_data(self):
        """Sample quote data for testing."""
        return {
            "title": "Test Quote",
            "description": "Test quote description",
            "customer_id": 100,
            "subtotal": Decimal("1000.00"),
            "total_amount": Decimal("1080.00"),
            "tax_amount": Decimal("80.00"),
            "currency_code": "USD"
        }
    
    @pytest.fixture
    def sample_line_items(self):
        """Sample line items for testing."""
        return [
            {
                "line_number": 1,
                "item_name": "Product A",
                "quantity": Decimal("2.0"),
                "unit_price": Decimal("500.00"),
                "line_total": Decimal("1000.00")
            },
            {
                "line_number": 2,
                "item_name": "Product B",
                "quantity": Decimal("1.0"),
                "unit_price": Decimal("200.00"),
                "line_total": Decimal("200.00")
            }
        ]
    
    def test_create_quote_basic(self, quote_service, sample_quote_data):
        """Test basic quote creation without line items."""
        with patch.object(quote_service, 'create') as mock_create:
            mock_quote = Mock(spec=SalesQuote)
            mock_quote.id = 1
            mock_create.return_value = mock_quote
            
            result = quote_service.create_quote(
                sample_quote_data, 
                user_id=1, 
                company_id=1
            )
            
            assert result == mock_quote
            mock_create.assert_called_once()
            
            # Verify quote number generation
            call_args = mock_create.call_args[0][0]  # First positional argument
            assert 'quote_number' in call_args
            assert call_args['quote_number'].startswith('QUO')
            assert call_args['prepared_by_user_id'] == 1
            assert 'valid_until' in call_args
    
    def test_create_quote_with_custom_quote_number(self, quote_service, sample_quote_data):
        """Test quote creation with custom quote number."""
        sample_quote_data['quote_number'] = 'CUSTOM-2025-001'
        
        with patch.object(quote_service, 'create') as mock_create:
            mock_quote = Mock(spec=SalesQuote)
            mock_create.return_value = mock_quote
            
            quote_service.create_quote(sample_quote_data, user_id=1, company_id=1)
            
            call_args = mock_create.call_args[0][0]
            assert call_args['quote_number'] == 'CUSTOM-2025-001'
    
    def test_create_quote_with_line_items(self, quote_service, sample_quote_data, sample_line_items):
        """Test quote creation with line items."""
        with patch.object(quote_service, 'create') as mock_create, \
             patch.object(quote_service, 'add_line_item') as mock_add_line, \
             patch.object(quote_service, 'calculate_quote_totals') as mock_calc_totals:
            
            mock_quote = Mock(spec=SalesQuote)
            mock_quote.id = 1
            mock_create.return_value = mock_quote
            
            result = quote_service.create_quote(
                sample_quote_data,
                line_items=sample_line_items,
                user_id=1,
                company_id=1
            )
            
            assert result == mock_quote
            assert mock_add_line.call_count == 2  # Two line items
            mock_calc_totals.assert_called_once_with(1, 1)
    
    def test_create_quote_validation_error(self, quote_service):
        """Test quote creation with validation error."""
        invalid_data = {"description": "Missing required fields"}
        
        with patch.object(quote_service, 'validate_create_data') as mock_validate:
            mock_validate.side_effect = ValueError("Field 'title' is required")
            
            with pytest.raises(ValueError, match="Field 'title' is required"):
                quote_service.create_quote(invalid_data, user_id=1, company_id=1)


class TestLineItemManagement:
    """Test line item management functionality."""
    
    @pytest.fixture
    def quote_service(self):
        """Create quote service with mocked session."""
        return QuoteService(Mock())
    
    @pytest.fixture
    def mock_quote(self):
        """Mock quote for testing."""
        quote = Mock(spec=SalesQuote)
        quote.id = 1
        quote.company_id = 1
        return quote
    
    def test_add_line_item_success(self, quote_service, mock_quote):
        """Test successful line item addition."""
        line_item_data = {
            "item_name": "Test Product",
            "quantity": Decimal("2.0"),
            "unit_price": Decimal("100.00")
        }
        
        with patch.object(quote_service, 'get_by_id') as mock_get, \
             patch.object(quote_service, 'calculate_quote_totals') as mock_calc, \
             patch('sales_module.services.quote_service.SalesQuoteLineItem') as mock_line_item_class:
            
            mock_get.return_value = mock_quote
            mock_line_item = Mock(spec=SalesQuoteLineItem)
            mock_line_item_class.return_value = mock_line_item
            
            result = quote_service.add_line_item(1, line_item_data, user_id=1, company_id=1)
            
            assert result == mock_line_item
            mock_line_item.calculate_line_total.assert_called_once()
            mock_line_item.save.assert_called_once()
            mock_calc.assert_called_once_with(1, 1)
    
    def test_add_line_item_quote_not_found(self, quote_service):
        """Test line item addition when quote not found."""
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            result = quote_service.add_line_item(999, {}, user_id=1, company_id=1)
            
            assert result is None
    
    def test_update_line_item_pricing(self, quote_service):
        """Test line item pricing update."""
        result = quote_service.update_line_item_pricing(
            1, 
            Decimal("150.00"), 
            discount_percentage=Decimal("10.0"),
            user_id=1,
            company_id=1
        )
        
        # Currently returns None as it's a placeholder implementation
        assert result is None


class TestQuoteCalculations:
    """Test quote calculation functionality."""
    
    @pytest.fixture
    def quote_service(self):
        """Create quote service with mocked session."""
        return QuoteService(Mock())
    
    @pytest.fixture
    def mock_quote(self):
        """Mock quote for testing."""
        quote = Mock(spec=SalesQuote)
        quote.id = 1
        quote.subtotal = Decimal("1000.00")
        quote.tax_amount = Decimal("80.00")
        quote.shipping_amount = Decimal("20.00")
        return quote
    
    def test_calculate_quote_totals(self, quote_service, mock_quote):
        """Test quote totals calculation."""
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = mock_quote
            
            result = quote_service.calculate_quote_totals(1, company_id=1)
            
            assert result == mock_quote
            mock_quote.calculate_totals.assert_called_once()
            mock_quote.save.assert_called_once()
    
    def test_calculate_quote_totals_not_found(self, quote_service):
        """Test quote totals calculation when quote not found."""
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            result = quote_service.calculate_quote_totals(999, company_id=1)
            
            assert result is None
    
    def test_apply_overall_discount(self, quote_service, mock_quote):
        """Test applying overall discount to quote."""
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = mock_quote
            
            result = quote_service.apply_overall_discount(
                1, 
                Decimal("15.0"), 
                user_id=1, 
                company_id=1
            )
            
            assert result == mock_quote
            mock_quote.apply_overall_discount.assert_called_once_with(Decimal("15.0"))
            mock_quote.save.assert_called_once()


class TestQuoteWorkflow:
    """Test quote workflow and status transitions."""
    
    @pytest.fixture
    def quote_service(self):
        """Create quote service with mocked session."""
        return QuoteService(Mock())
    
    @pytest.fixture
    def mock_quote(self):
        """Mock quote for testing."""
        quote = Mock(spec=SalesQuote)
        quote.id = 1
        quote.status = QuoteStatus.APPROVED
        quote.requires_approval = False
        quote.quote_number = "QUO-2025-001"
        return quote
    
    def test_send_quote_to_customer_success(self, quote_service, mock_quote):
        """Test successful quote sending to customer."""
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = mock_quote
            
            result = quote_service.send_quote_to_customer(
                1, 
                email_template="standard",
                user_id=1,
                company_id=1
            )
            
            assert result == mock_quote
            mock_quote.send_to_customer.assert_called_once_with(1, "standard")
    
    def test_send_quote_requires_approval(self, quote_service, mock_quote):
        """Test sending quote that requires approval."""
        mock_quote.status = QuoteStatus.DRAFT
        mock_quote.requires_approval = True
        
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = mock_quote
            
            with pytest.raises(ValueError, match="Quote must be approved before sending"):
                quote_service.send_quote_to_customer(1, user_id=1, company_id=1)
    
    def test_extend_quote_validity(self, quote_service, mock_quote):
        """Test extending quote validity period."""
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = mock_quote
            
            result = quote_service.extend_quote_validity(
                1, 
                additional_days=15,
                user_id=1,
                company_id=1
            )
            
            assert result == mock_quote
            mock_quote.extend_validity.assert_called_once_with(15, 1)


class TestQuoteVersioning:
    """Test quote versioning functionality."""
    
    @pytest.fixture
    def quote_service(self):
        """Create quote service with mocked session."""
        return QuoteService(Mock())
    
    @pytest.fixture
    def mock_quote(self):
        """Mock quote for testing."""
        quote = Mock(spec=SalesQuote)
        quote.id = 1
        return quote
    
    def test_create_quote_version(self, quote_service, mock_quote):
        """Test creating new quote version."""
        mock_version = Mock(spec=QuoteVersion)
        
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = mock_quote
            mock_quote.create_new_version.return_value = mock_version
            
            result = quote_service.create_quote_version(
                1,
                reason="Customer requested changes",
                user_id=1,
                company_id=1
            )
            
            assert result == mock_version
            mock_quote.create_new_version.assert_called_once_with(1, "Customer requested changes")
    
    def test_create_quote_version_not_found(self, quote_service):
        """Test creating version for non-existent quote."""
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            result = quote_service.create_quote_version(999, user_id=1, company_id=1)
            
            assert result is None


class TestApprovalWorkflow:
    """Test quote approval workflow functionality."""
    
    @pytest.fixture
    def quote_service(self):
        """Create quote service with mocked session."""
        return QuoteService(Mock())
    
    @pytest.fixture
    def mock_quote(self):
        """Mock quote for testing."""
        quote = Mock(spec=SalesQuote)
        quote.id = 1
        quote.overall_discount_percentage = Decimal("10.0")
        quote.total_amount = Decimal("5000.00")
        quote.margin_percentage = Decimal("25.0")
        quote.status = QuoteStatus.DRAFT
        return quote
    
    def test_request_quote_approval(self, quote_service, mock_quote):
        """Test requesting quote approval."""
        with patch.object(quote_service, 'get_by_id') as mock_get, \
             patch.object(quote_service, 'get_approver_for_level') as mock_get_approver, \
             patch('sales_module.services.quote_service.QuoteApproval') as mock_approval_class:
            
            mock_get.return_value = mock_quote
            mock_get_approver.return_value = 2  # Approver user ID
            mock_approval = Mock(spec=QuoteApproval)
            mock_approval_class.return_value = mock_approval
            
            result = quote_service.request_quote_approval(
                1,
                approval_level=1,
                request_reason="High discount requires approval",
                urgency="high",
                user_id=1,
                company_id=1
            )
            
            assert result == mock_approval
            mock_approval.save.assert_called_once()
            
            # Verify quote status updated
            assert mock_quote.status == QuoteStatus.PENDING_APPROVAL
            mock_quote.save.assert_called_once()
    
    def test_request_approval_quote_not_found(self, quote_service):
        """Test approval request for non-existent quote."""
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            result = quote_service.request_quote_approval(999, user_id=1, company_id=1)
            
            assert result is None
    
    def test_approve_quote(self, quote_service):
        """Test approving quote."""
        result = quote_service.approve_quote(
            1,
            approver_notes="Quote looks good to go",
            user_id=2,
            company_id=1
        )
        
        # Currently returns None as it's a placeholder implementation
        assert result is None
    
    def test_reject_quote_approval(self, quote_service):
        """Test rejecting quote approval."""
        result = quote_service.reject_quote_approval(
            1,
            rejection_reason="Discount too high",
            user_id=2,
            company_id=1
        )
        
        # Currently returns None as it's a placeholder implementation
        assert result is None


class TestQuoteConversion:
    """Test quote to order conversion functionality."""
    
    @pytest.fixture
    def quote_service(self):
        """Create quote service with mocked session."""
        return QuoteService(Mock())
    
    @pytest.fixture
    def mock_accepted_quote(self):
        """Mock accepted quote for testing."""
        quote = Mock(spec=SalesQuote)
        quote.id = 1
        quote.status = QuoteStatus.ACCEPTED
        quote.quote_number = "QUO-2025-001"
        return quote
    
    def test_convert_quote_to_order_success(self, quote_service, mock_accepted_quote):
        """Test successful quote to order conversion."""
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = mock_accepted_quote
            
            result = quote_service.convert_quote_to_order(
                1,
                order_data={"delivery_date": "2025-09-01"},
                user_id=1,
                company_id=1
            )
            
            assert result["success"] is True
            assert "order_id" in result
            assert result["quote_id"] == 1
            assert "QUO-2025-001" in result["message"]
            mock_accepted_quote.convert_to_order.assert_called_once()
    
    def test_convert_quote_not_found(self, quote_service):
        """Test conversion of non-existent quote."""
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            result = quote_service.convert_quote_to_order(999, user_id=1, company_id=1)
            
            assert result["success"] is False
            assert "Quote not found" in result["error"]
    
    def test_convert_quote_wrong_status(self, quote_service):
        """Test conversion of quote with wrong status."""
        mock_quote = Mock(spec=SalesQuote)
        mock_quote.status = QuoteStatus.DRAFT
        
        with patch.object(quote_service, 'get_by_id') as mock_get:
            mock_get.return_value = mock_quote
            
            result = quote_service.convert_quote_to_order(1, user_id=1, company_id=1)
            
            assert result["success"] is False
            assert "must be accepted" in result["error"]


class TestAnalyticsAndReporting:
    """Test quote analytics and reporting functionality."""
    
    @pytest.fixture
    def quote_service(self):
        """Create quote service with mocked session."""
        return QuoteService(Mock())
    
    def test_get_quote_analytics(self, quote_service):
        """Test getting quote analytics."""
        date_range = {
            "start_date": datetime(2025, 1, 1),
            "end_date": datetime(2025, 12, 31)
        }
        
        result = quote_service.get_quote_analytics(
            company_id=1,
            date_range=date_range
        )
        
        # Verify analytics structure
        assert "summary" in result
        assert "conversion_metrics" in result
        assert "by_status" in result
        assert "approval_metrics" in result
        assert "top_quotes" in result
        assert "quote_trends" in result
        
        # Verify summary fields
        summary = result["summary"]
        expected_fields = [
            "total_quotes", "quotes_sent", "quotes_accepted", 
            "quotes_rejected", "quotes_expired", "quotes_converted"
        ]
        for field in expected_fields:
            assert field in summary
        
        # Verify conversion metrics
        conversion = result["conversion_metrics"]
        expected_conversion_fields = [
            "quote_to_order_rate", "average_quote_value", 
            "average_time_to_close", "win_rate"
        ]
        for field in expected_conversion_fields:
            assert field in conversion


class TestUtilityMethods:
    """Test utility and helper methods."""
    
    @pytest.fixture
    def quote_service(self):
        """Create quote service with mocked session."""
        return QuoteService(Mock())
    
    def test_get_approver_for_level(self, quote_service):
        """Test getting approver for approval level."""
        result = quote_service.get_approver_for_level(1, company_id=1)
        
        # Currently returns 1 as placeholder
        assert result == 1
    
    def test_generate_quote_number(self, quote_service):
        """Test quote number generation."""
        result = quote_service.generate_quote_number("TEST")
        
        assert result.startswith("TEST")
        assert len(result) > 4  # Prefix + timestamp


class TestValidation:
    """Test service validation methods."""
    
    @pytest.fixture
    def quote_service(self):
        """Create quote service with mocked session."""
        return QuoteService(Mock())
    
    def test_validate_create_data_success(self, quote_service):
        """Test successful validation of create data."""
        valid_data = {
            "title": "Test Quote",
            "customer_id": 100,
            "valid_from": datetime.utcnow(),
            "valid_until": datetime.utcnow() + timedelta(days=30)
        }
        
        # Should not raise any exception
        quote_service.validate_create_data(valid_data)
    
    def test_validate_create_data_missing_required(self, quote_service):
        """Test validation failure for missing required fields."""
        invalid_data = {"description": "Missing title and customer_id"}
        
        with pytest.raises(ValueError, match="Field 'title' is required"):
            quote_service.validate_create_data(invalid_data)
    
    def test_validate_create_data_invalid_dates(self, quote_service):
        """Test validation failure for invalid date range."""
        base_date = datetime.utcnow()
        invalid_data = {
            "title": "Test Quote",
            "customer_id": 100,
            "valid_from": base_date,
            "valid_until": base_date - timedelta(days=1)  # Invalid: until before from
        }
        
        with pytest.raises(ValueError, match="Valid until date must be after valid from date"):
            quote_service.validate_create_data(invalid_data)
    
    def test_validate_update_data_success(self, quote_service):
        """Test successful validation of update data."""
        mock_quote = Mock(spec=SalesQuote)
        mock_quote.quote_number = "QUO-2025-001"
        mock_quote.status = QuoteStatus.DRAFT
        
        valid_data = {"title": "Updated Title"}
        
        # Should not raise any exception
        quote_service.validate_update_data(valid_data, mock_quote)
    
    def test_validate_update_data_quote_number_change(self, quote_service):
        """Test validation failure when trying to change quote number."""
        mock_quote = Mock(spec=SalesQuote)
        mock_quote.quote_number = "QUO-2025-001"
        
        invalid_data = {"quote_number": "QUO-2025-002"}
        
        with pytest.raises(ValueError, match="Quote number cannot be changed"):
            quote_service.validate_update_data(invalid_data, mock_quote)
    
    def test_validate_update_data_converted_quote(self, quote_service):
        """Test validation failure when trying to edit converted quote."""
        mock_quote = Mock(spec=SalesQuote)
        mock_quote.status = QuoteStatus.CONVERTED
        
        invalid_data = {"title": "Cannot update converted quote"}
        
        with pytest.raises(ValueError, match="Cannot edit quotes that have been converted"):
            quote_service.validate_update_data(invalid_data, mock_quote)