"""
Comprehensive test suite for Quote API endpoints.

Tests all quote management API endpoints including CRUD operations,
workflow management, approvals, and inventory integration.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta
import json

from sales_module.api.quote_api import router as quote_router
from sales_module.models import QuoteStatus, ApprovalStatus
from sales_module.services.quote_service import QuoteService


# Test fixture setup
@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    app = FastAPI()
    app.include_router(quote_router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_quote_service():
    """Create mock quote service."""
    return Mock(spec=QuoteService)


@pytest.fixture
def mock_quote():
    """Create mock quote object."""
    quote = Mock()
    quote.id = 1
    quote.quote_number = "QUO-2025-001"
    quote.title = "Test Quote"
    quote.description = "Test quote description"
    quote.status = QuoteStatus.DRAFT
    quote.customer_id = 100
    quote.contact_person = "John Doe"
    quote.contact_email = "john@example.com"
    quote.contact_phone = "+1-555-0123"
    
    # Dates
    quote.valid_from = datetime.utcnow()
    quote.valid_until = datetime.utcnow() + timedelta(days=30)
    quote.quote_date = datetime.utcnow()
    
    # Financial data
    quote.subtotal = Decimal("1000.00")
    quote.tax_amount = Decimal("80.00")
    quote.shipping_amount = Decimal("0.00")
    quote.overall_discount_percentage = Decimal("0.00")
    quote.overall_discount_amount = Decimal("0.00")
    quote.total_amount = Decimal("1080.00")
    
    quote.total_cost = Decimal("600.00")
    quote.margin_amount = Decimal("480.00")
    quote.margin_percentage = Decimal("44.44")
    
    quote.currency_code = "USD"
    
    # Terms
    quote.payment_terms = "Net 30"
    quote.delivery_terms = "FOB Origin"
    quote.special_instructions = None
    
    # Workflow fields
    quote.requires_approval = False
    quote.is_template = False
    quote.sent_to_customer = False
    quote.sent_at = None
    
    # System fields
    quote.prepared_by_user_id = 1
    quote.approved_by_user_id = None
    quote.company_id = 1
    quote.created_at = datetime.utcnow()
    quote.updated_at = None
    
    return quote


@pytest.fixture
def mock_line_item():
    """Create mock line item object."""
    line_item = Mock()
    line_item.id = 1
    line_item.line_number = 1
    line_item.product_id = 100
    line_item.item_name = "Test Product"
    line_item.item_code = "TEST-001"
    line_item.description = "Test product description"
    
    line_item.quantity = Decimal("2.0")
    line_item.unit_of_measure = "each"
    line_item.unit_price = Decimal("500.00")
    line_item.unit_cost = Decimal("300.00")
    
    line_item.discount_percentage = Decimal("0.00")
    line_item.discount_amount = Decimal("0.00")
    line_item.tax_percentage = Decimal("8.00")
    line_item.tax_amount = Decimal("80.00")
    line_item.line_total = Decimal("1000.00")
    
    line_item.created_at = datetime.utcnow()
    line_item.updated_at = None
    
    return line_item


@pytest.fixture
def mock_approval():
    """Create mock approval object."""
    approval = Mock()
    approval.id = 1
    approval.approval_level = 1
    approval.status = ApprovalStatus.PENDING
    approval.requested_by_user_id = 1
    approval.assigned_to_user_id = 2
    
    approval.request_reason = "High discount requires approval"
    approval.urgency_level = "normal"
    
    approval.discount_percentage = Decimal("15.0")
    approval.quote_total = Decimal("5000.00")
    approval.margin_percentage = Decimal("25.0")
    
    approval.due_date = datetime.utcnow() + timedelta(hours=24)
    approval.approved_at = None
    approval.approved_by_user_id = None
    approval.approver_notes = None
    
    approval.escalated_to_user_id = None
    approval.escalation_reason = None
    
    approval.created_at = datetime.utcnow()
    
    return approval


class TestQuoteCRUD:
    """Test quote CRUD operations."""
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_user_id')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_create_quote_success(self, mock_company_id, mock_user_id, mock_get_service, 
                                 client, mock_quote_service, mock_quote):
        """Test successful quote creation."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_user_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.create_quote.return_value = mock_quote
        
        # Test data
        quote_data = {
            "title": "Test Quote",
            "description": "Test quote description",
            "customer_id": 100,
            "currency_code": "USD",
            "contact_person": "John Doe",
            "contact_email": "john@example.com",
            "payment_terms": "Net 30",
            "requires_approval": False
        }
        
        # Make request
        response = client.post("/api/v1/quotes/", json=quote_data)
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["quote_number"] == "QUO-2025-001"
        assert data["title"] == "Test Quote"
        assert data["customer_id"] == 100
        
        # Service was called correctly
        mock_quote_service.create_quote.assert_called_once()
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_list_quotes_success(self, mock_company_id, mock_get_service, 
                                client, mock_quote_service, mock_quote):
        """Test successful quote listing."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.get_all.return_value = [mock_quote]
        mock_quote_service.count.return_value = 1
        
        # Make request
        response = client.get("/api/v1/quotes/?page=1&page_size=20")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data["quotes"]) == 1
        assert data["total_count"] == 1
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total_pages"] == 1
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_get_quote_success(self, mock_company_id, mock_get_service, 
                              client, mock_quote_service, mock_quote):
        """Test successful quote retrieval."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.get_by_id.return_value = mock_quote
        
        # Make request
        response = client.get("/api/v1/quotes/1")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["quote_number"] == "QUO-2025-001"
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_get_quote_not_found(self, mock_company_id, mock_get_service, 
                                 client, mock_quote_service):
        """Test quote not found."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.get_by_id.return_value = None
        
        # Make request
        response = client.get("/api/v1/quotes/999")
        
        # Assertions
        assert response.status_code == 404
        assert "Quote not found" in response.json()["detail"]
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_user_id')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_update_quote_success(self, mock_company_id, mock_user_id, mock_get_service, 
                                 client, mock_quote_service, mock_quote):
        """Test successful quote update."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_user_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.get_by_id.return_value = mock_quote
        mock_quote_service.update.return_value = mock_quote
        
        # Test data
        update_data = {
            "title": "Updated Quote Title",
            "description": "Updated description"
        }
        
        # Make request
        response = client.put("/api/v1/quotes/1", json=update_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_user_id')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_delete_quote_success(self, mock_company_id, mock_user_id, mock_get_service, 
                                 client, mock_quote_service, mock_quote):
        """Test successful quote deletion."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_user_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.get_by_id.return_value = mock_quote
        mock_quote_service.delete.return_value = True
        
        # Make request
        response = client.delete("/api/v1/quotes/1")
        
        # Assertions
        assert response.status_code == 204


class TestLineItemOperations:
    """Test line item operations."""
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_user_id')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_add_line_item_success(self, mock_company_id, mock_user_id, mock_get_service, 
                                  client, mock_quote_service, mock_line_item):
        """Test successful line item addition."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_user_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.add_line_item.return_value = mock_line_item
        
        # Test data
        line_item_data = {
            "product_id": 100,
            "item_name": "Test Product",
            "item_code": "TEST-001",
            "description": "Test product description",
            "quantity": "2.0",
            "unit_of_measure": "each",
            "unit_price": "500.00",
            "unit_cost": "300.00"
        }
        
        # Make request
        response = client.post("/api/v1/quotes/1/line-items", json=line_item_data)
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["item_name"] == "Test Product"
        assert data["quantity"] == "2.0"
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_user_id')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_update_line_item_success(self, mock_company_id, mock_user_id, mock_get_service, 
                                     client, mock_quote_service, mock_line_item):
        """Test successful line item update."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_user_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.update_line_item_pricing.return_value = mock_line_item
        
        # Test data
        update_data = {
            "unit_price": "450.00",
            "discount_percentage": "10.0"
        }
        
        # Make request
        response = client.put("/api/v1/quotes/1/line-items/1", json=update_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1


class TestQuoteOperations:
    """Test quote operations."""
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_user_id')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_apply_discount_success(self, mock_company_id, mock_user_id, mock_get_service, 
                                   client, mock_quote_service, mock_quote):
        """Test successful discount application."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_user_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.apply_overall_discount.return_value = mock_quote
        
        # Test data
        discount_data = {
            "discount_percentage": "15.0",
            "reason": "Volume discount"
        }
        
        # Make request
        response = client.post("/api/v1/quotes/1/discount", json=discount_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_user_id')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_send_quote_success(self, mock_company_id, mock_user_id, mock_get_service, 
                               client, mock_quote_service, mock_quote):
        """Test successful quote sending."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_user_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.send_quote_to_customer.return_value = mock_quote
        
        # Test data
        send_data = {
            "email_template": "standard",
            "custom_message": "Please review the attached quote"
        }
        
        # Make request
        response = client.post("/api/v1/quotes/1/send", json=send_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_user_id')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_convert_to_order_success(self, mock_company_id, mock_user_id, mock_get_service, 
                                     client, mock_quote_service):
        """Test successful quote conversion."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_user_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.convert_quote_to_order.return_value = {
            "success": True,
            "order_id": 12345,
            "quote_id": 1,
            "message": "Quote QUO-2025-001 successfully converted to order"
        }
        
        # Test data
        conversion_data = {
            "order_data": {"delivery_date": "2025-02-01"},
            "delivery_date": "2025-02-01T10:00:00Z",
            "special_instructions": "Rush order"
        }
        
        # Make request
        response = client.post("/api/v1/quotes/1/convert", json=conversion_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["order_id"] == 12345
        assert data["quote_id"] == 1


class TestApprovalWorkflow:
    """Test approval workflow operations."""
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_user_id')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_request_approval_success(self, mock_company_id, mock_user_id, mock_get_service, 
                                     client, mock_quote_service, mock_approval):
        """Test successful approval request."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_user_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.request_quote_approval.return_value = mock_approval
        
        # Test data
        approval_data = {
            "approval_level": 1,
            "request_reason": "High discount requires approval",
            "urgency": "normal"
        }
        
        # Make request
        response = client.post("/api/v1/quotes/1/approvals", json=approval_data)
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["approval_level"] == 1
        assert data["status"] == "pending"
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_user_id')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_approve_quote_success(self, mock_company_id, mock_user_id, mock_get_service, 
                                  client, mock_quote_service, mock_approval):
        """Test successful quote approval."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_user_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_approval.status = ApprovalStatus.APPROVED
        mock_quote_service.approve_quote.return_value = mock_approval
        
        # Test data
        action_data = {
            "action": "approve",
            "notes": "Approved with conditions"
        }
        
        # Make request
        response = client.post("/api/v1/quotes/approvals/1/action", json=action_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_user_id')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_reject_approval_success(self, mock_company_id, mock_user_id, mock_get_service, 
                                    client, mock_quote_service, mock_approval):
        """Test successful approval rejection."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_user_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_approval.status = ApprovalStatus.REJECTED
        mock_quote_service.reject_quote_approval.return_value = mock_approval
        
        # Test data
        action_data = {
            "action": "reject",
            "notes": "Discount too high"
        }
        
        # Make request
        response = client.post("/api/v1/quotes/approvals/1/action", json=action_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_user_id')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_get_pending_approvals_success(self, mock_company_id, mock_user_id, mock_get_service, 
                                          client, mock_quote_service):
        """Test getting pending approvals."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_user_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.get_pending_approvals.return_value = [
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
        
        # Make request
        response = client.get("/api/v1/quotes/approvals/pending")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data["approvals"]) == 1
        assert data["total_count"] == 1


class TestInventoryIntegration:
    """Test inventory integration endpoints."""
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_validate_inventory_success(self, mock_company_id, mock_get_service, 
                                       client, mock_quote_service):
        """Test successful inventory validation."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.validate_quote_inventory.return_value = {
            "valid": True,
            "line_items": [
                {
                    "line_item_id": 1,
                    "product_id": 100,
                    "item_name": "Product A",
                    "requested_quantity": "2.0",
                    "available": True,
                    "available_quantity": "10.0"
                }
            ],
            "issues": []
        }
        
        # Make request
        response = client.get("/api/v1/quotes/1/inventory/validate")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert len(data["line_items"]) == 1
        assert len(data["issues"]) == 0
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_reserve_inventory_success(self, mock_company_id, mock_get_service, 
                                      client, mock_quote_service):
        """Test successful inventory reservation."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.reserve_quote_inventory.return_value = {
            "success": True,
            "reservations": [
                {
                    "line_item_id": 1,
                    "product_id": 100,
                    "reservation_id": "RES-12345",
                    "quantity": "2.0"
                }
            ],
            "failed_reservations": [],
            "quote_id": 1
        }
        
        # Make request
        response = client.post("/api/v1/quotes/1/inventory/reserve?expiry_hours=24")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["reservations"]) == 1
        assert len(data["failed_reservations"]) == 0


class TestAnalytics:
    """Test analytics endpoints."""
    
    @patch('sales_module.api.quote_api.get_quote_service')
    @patch('sales_module.api.quote_api.get_current_company_id')
    def test_get_analytics_success(self, mock_company_id, mock_get_service, 
                                  client, mock_quote_service):
        """Test successful analytics retrieval."""
        # Setup mocks
        mock_company_id.return_value = 1
        mock_get_service.return_value = mock_quote_service
        mock_quote_service.get_quote_analytics.return_value = {
            "summary": {
                "total_quotes": 150,
                "quotes_sent": 120,
                "quotes_accepted": 45,
                "quotes_rejected": 30,
                "quotes_expired": 15,
                "quotes_converted": 40
            },
            "conversion_metrics": {
                "quote_to_order_rate": 26.67,
                "average_quote_value": 5500.00,
                "average_time_to_close": 12,
                "win_rate": 37.50
            },
            "by_status": {
                "draft": 20,
                "pending_approval": 5,
                "approved": 10,
                "sent": 75,
                "accepted": 45,
                "rejected": 30,
                "expired": 15,
                "converted": 40
            },
            "approval_metrics": {
                "quotes_requiring_approval": 25,
                "average_approval_time": 4.5,
                "approval_rate": 80.0
            },
            "top_quotes": [],
            "quote_trends": []
        }
        
        # Make request
        response = client.get("/api/v1/quotes/analytics")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["total_quotes"] == 150
        assert data["conversion_metrics"]["quote_to_order_rate"] == 26.67


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_invalid_quote_id(self, client):
        """Test invalid quote ID handling."""
        response = client.get("/api/v1/quotes/invalid")
        assert response.status_code == 422  # Validation error
    
    def test_negative_quote_id(self, client):
        """Test negative quote ID handling."""
        response = client.get("/api/v1/quotes/-1")
        assert response.status_code == 422  # Validation error
    
    @patch('sales_module.api.quote_api.get_quote_service')
    def test_service_exception_handling(self, mock_get_service, client):
        """Test service exception handling."""
        # Setup mock to raise exception
        mock_service = Mock()
        mock_service.get_by_id.side_effect = Exception("Database error")
        mock_get_service.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/quotes/1")
        
        # Assertions
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


class TestValidation:
    """Test request validation."""
    
    def test_create_quote_validation(self, client):
        """Test quote creation validation."""
        # Missing required fields
        invalid_data = {
            "description": "Test quote without title"
        }
        
        response = client.post("/api/v1/quotes/", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_line_item_validation(self, client):
        """Test line item validation."""
        # Negative quantity
        invalid_data = {
            "item_name": "Test Product",
            "quantity": "-1.0",
            "unit_price": "100.00"
        }
        
        response = client.post("/api/v1/quotes/1/line-items", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_discount_validation(self, client):
        """Test discount validation."""
        # Invalid discount percentage
        invalid_data = {
            "discount_percentage": "150.0"  # Over 100%
        }
        
        response = client.post("/api/v1/quotes/1/discount", json=invalid_data)
        assert response.status_code == 422  # Validation error


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check_success(self, client):
        """Test successful health check."""
        response = client.get("/api/v1/quotes/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "quote-api"