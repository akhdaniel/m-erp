"""
Tests for Quote models.

Comprehensive test suite for SalesQuote, SalesQuoteLineItem, 
QuoteVersion, and QuoteApproval models.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from sales_module.models.quote import (
    SalesQuote, SalesQuoteLineItem, QuoteVersion, QuoteApproval,
    QuoteStatus, ApprovalStatus, LineItemType
)


class TestSalesQuote:
    """Test SalesQuote model functionality."""
    
    def test_create_quote(self, db_session, sample_quote_data):
        """Test creating a new sales quote."""
        quote = SalesQuote(**sample_quote_data)
        db_session.add(quote)
        db_session.commit()
        
        assert quote.id is not None
        assert quote.quote_number == "QUO-2025-001"
        assert quote.status == QuoteStatus.DRAFT
        assert quote.version == 1
        assert quote.total_amount == Decimal("1080.00")
        assert quote.company_id == sample_quote_data["company_id"]
        assert quote.framework_version == "1.0.0"
    
    def test_quote_string_representation(self, sample_quote):
        """Test quote string representation."""
        assert str(sample_quote) == f"Quote {sample_quote.quote_number} v{sample_quote.version}"
        assert "SalesQuote" in repr(sample_quote)
        assert sample_quote.quote_number in repr(sample_quote)
    
    def test_quote_display_identifier(self, sample_quote):
        """Test quote display identifier property."""
        expected = f"{sample_quote.quote_number} v{sample_quote.version} - {sample_quote.title}"
        assert sample_quote.display_identifier == expected
    
    def test_quote_expiry_properties(self, db_session, sample_quote_data):
        """Test quote expiry-related properties."""
        # Create expired quote
        expired_data = sample_quote_data.copy()
        expired_data["quote_number"] = "QUO-EXPIRED"
        expired_data["valid_until"] = datetime.utcnow() - timedelta(days=1)
        expired_quote = SalesQuote(**expired_data)
        
        assert expired_quote.is_expired is True
        assert expired_quote.days_until_expiry == 0
        
        # Create valid quote
        valid_data = sample_quote_data.copy()
        valid_data["quote_number"] = "QUO-VALID"
        valid_data["valid_until"] = datetime.utcnow() + timedelta(days=5)
        valid_quote = SalesQuote(**valid_data)
        
        assert valid_quote.is_expired is False
        assert valid_quote.days_until_expiry >= 4  # Allow for test execution time
    
    def test_quote_status_properties(self, sample_quote):
        """Test quote status properties."""
        # Test open status
        sample_quote.status = QuoteStatus.DRAFT
        assert sample_quote.is_open is True
        assert sample_quote.is_closed is False
        
        sample_quote.status = QuoteStatus.SENT
        assert sample_quote.is_open is True
        assert sample_quote.is_closed is False
        
        # Test closed status
        sample_quote.status = QuoteStatus.ACCEPTED
        assert sample_quote.is_open is False
        assert sample_quote.is_closed is True
        
        sample_quote.status = QuoteStatus.REJECTED
        assert sample_quote.is_open is False
        assert sample_quote.is_closed is True
    
    def test_quote_margin_calculations(self, sample_quote):
        """Test quote margin calculation properties."""
        # Without cost - should return None
        assert sample_quote.gross_margin is None
        assert sample_quote.gross_margin_percentage is None
        
        # With cost
        sample_quote.total_cost = Decimal("800.00")
        sample_quote.total_amount = Decimal("1000.00")
        
        assert sample_quote.gross_margin == Decimal("200.00")
        assert sample_quote.gross_margin_percentage == 20.0
    
    def test_generate_quote_number(self, sample_quote):
        """Test quote number generation."""
        quote_number = sample_quote.generate_quote_number("TEST")
        assert quote_number.startswith("TEST")
        assert len(quote_number) > 4  # Prefix + timestamp
    
    def test_apply_overall_discount(self, sample_quote):
        """Test applying overall discount to quote."""
        sample_quote.subtotal = Decimal("1000.00")
        sample_quote.tax_amount = Decimal("80.00")
        sample_quote.shipping_amount = Decimal("20.00")
        
        sample_quote.apply_overall_discount(Decimal("10.0"))  # 10% discount
        
        assert sample_quote.overall_discount_percentage == Decimal("10.0")
        assert sample_quote.discount_amount == Decimal("100.00")
        assert sample_quote.total_amount == Decimal("1000.00")  # 1000 - 100 + 80 + 20
    
    def test_extend_validity(self, db_session, sample_quote):
        """Test extending quote validity."""
        original_valid_until = sample_quote.valid_until
        
        sample_quote.extend_validity(10, user_id=1)
        
        expected_valid_until = original_valid_until + timedelta(days=10)
        assert sample_quote.valid_until == expected_valid_until
    
    def test_send_to_customer(self, db_session, sample_quote):
        """Test sending quote to customer."""
        sample_quote.send_to_customer(user_id=1, email_template="standard")
        
        assert sample_quote.status == QuoteStatus.SENT
        assert sample_quote.sent_date is not None
        assert sample_quote.sent_by_user_id == 1
        assert sample_quote.email_sent_count == 1
        assert sample_quote.last_email_sent is not None
    
    def test_mark_accepted(self, db_session, sample_quote):
        """Test marking quote as accepted."""
        sample_quote.mark_accepted(user_id=1, notes="Customer accepted via email")
        
        assert sample_quote.status == QuoteStatus.ACCEPTED
        assert sample_quote.customer_response_date is not None
        assert sample_quote.customer_response_notes == "Customer accepted via email"
    
    def test_mark_rejected(self, db_session, sample_quote):
        """Test marking quote as rejected."""
        sample_quote.mark_rejected("Price too high", user_id=1, notes="Customer wants discount")
        
        assert sample_quote.status == QuoteStatus.REJECTED
        assert sample_quote.customer_response_date is not None
        assert sample_quote.rejection_reason == "Price too high"
        assert sample_quote.customer_response_notes == "Customer wants discount"
    
    def test_convert_to_order(self, db_session, sample_quote):
        """Test converting quote to order."""
        sample_quote.convert_to_order(user_id=1, order_id=123)
        
        assert sample_quote.status == QuoteStatus.CONVERTED
        assert sample_quote.converted_date is not None
        assert sample_quote.converted_by_user_id == 1
        assert sample_quote.converted_to_order_id == 123
    
    def test_create_new_version(self, db_session, sample_quote):
        """Test creating new quote version."""
        original_version = sample_quote.version
        
        version_record = sample_quote.create_new_version(user_id=1, reason="Customer requested changes")
        
        assert sample_quote.version == original_version + 1
        assert sample_quote.status == QuoteStatus.DRAFT
        assert version_record.version_number == original_version
        assert version_record.change_reason == "Customer requested changes"
    
    def test_quote_validation(self, db_session, sample_company_id):
        """Test quote validation constraints."""
        # Test missing required fields
        with pytest.raises(IntegrityError):
            incomplete_quote = SalesQuote(
                company_id=sample_company_id,
                # Missing quote_number, title, customer_id, prepared_by_user_id, valid_until
            )
            db_session.add(incomplete_quote)
            db_session.commit()


class TestSalesQuoteLineItem:
    """Test SalesQuoteLineItem model functionality."""
    
    def test_create_line_item(self, db_session, sample_quote, sample_line_item_data):
        """Test creating a new quote line item."""
        line_item_data = sample_line_item_data.copy()
        line_item_data["quote_id"] = sample_quote.id
        
        line_item = SalesQuoteLineItem(**line_item_data)
        db_session.add(line_item)
        db_session.commit()
        
        assert line_item.id is not None
        assert line_item.quote_id == sample_quote.id
        assert line_item.line_number == 1
        assert line_item.item_name == "Test Product"
        assert line_item.quantity == Decimal("2.0")
        assert line_item.unit_price == Decimal("500.00")
        assert line_item.line_total == Decimal("1000.00")
        assert line_item.line_type == LineItemType.PRODUCT
    
    def test_line_item_string_representation(self, sample_line_item):
        """Test line item string representation."""
        expected_str = f"Line {sample_line_item.line_number}: {sample_line_item.item_name} (Qty: {sample_line_item.quantity})"
        assert str(sample_line_item) == expected_str
        assert "SalesQuoteLineItem" in repr(sample_line_item)
    
    def test_line_item_margin_calculations(self, sample_line_item):
        """Test line item margin calculations."""
        # Without cost - should return None
        assert sample_line_item.unit_margin is None
        assert sample_line_item.margin_percentage is None
        assert sample_line_item.line_margin is None
        
        # With cost
        sample_line_item.unit_cost = Decimal("300.00")
        sample_line_item.line_cost = Decimal("600.00")  # 2 * 300
        
        assert sample_line_item.unit_margin == Decimal("200.00")  # 500 - 300
        assert sample_line_item.margin_percentage == 40.0  # (500-300)/500 * 100
        assert sample_line_item.line_margin == Decimal("400.00")  # 1000 - 600
    
    def test_effective_unit_price(self, sample_line_item):
        """Test effective unit price calculation."""
        # Without discount
        assert sample_line_item.effective_unit_price == sample_line_item.unit_price
        
        # With percentage discount
        sample_line_item.discount_percentage = Decimal("10.0")
        expected_price = sample_line_item.unit_price * Decimal("0.9")  # 90% of original
        assert sample_line_item.effective_unit_price == expected_price
        
        # Reset and test amount discount
        sample_line_item.discount_percentage = Decimal("0.0")
        sample_line_item.discount_amount = Decimal("100.00")  # $50 per unit for qty 2
        expected_price = sample_line_item.unit_price - (Decimal("100.00") / sample_line_item.quantity)
        assert sample_line_item.effective_unit_price == expected_price
    
    def test_calculate_line_total(self, sample_line_item):
        """Test line total calculation."""
        sample_line_item.quantity = Decimal("3.0")
        sample_line_item.unit_price = Decimal("100.00")
        sample_line_item.discount_percentage = Decimal("10.0")
        sample_line_item.unit_cost = Decimal("60.00")
        sample_line_item.tax_percentage = Decimal("8.0")
        
        sample_line_item.calculate_line_total()
        
        # Gross: 3 * 100 = 300
        # Discount: 300 * 0.1 = 30
        # Line total: 300 - 30 = 270
        # Line cost: 3 * 60 = 180
        # Tax: 270 * 0.08 = 21.60
        
        assert sample_line_item.line_total == Decimal("270.00")
        assert sample_line_item.discount_amount == Decimal("30.00")
        assert sample_line_item.line_cost == Decimal("180.00")
        assert sample_line_item.tax_amount == Decimal("21.60")
    
    def test_apply_discount(self, sample_line_item):
        """Test applying discount to line item."""
        sample_line_item.quantity = Decimal("2.0")
        sample_line_item.unit_price = Decimal("100.00")
        
        # Apply percentage discount
        sample_line_item.apply_discount(discount_percentage=Decimal("15.0"))
        
        assert sample_line_item.discount_percentage == Decimal("15.0")
        assert sample_line_item.discount_amount == Decimal("30.00")  # 200 * 0.15
        assert sample_line_item.line_total == Decimal("170.00")  # 200 - 30
        
        # Reset and apply amount discount
        sample_line_item.discount_percentage = Decimal("0.0")
        sample_line_item.apply_discount(discount_amount=Decimal("40.00"))
        
        assert sample_line_item.discount_amount == Decimal("40.00")
        assert sample_line_item.discount_percentage == Decimal("20.0")  # 40/200 * 100
    
    def test_update_pricing(self, sample_line_item):
        """Test updating line item pricing."""
        new_price = Decimal("750.00")
        sample_line_item.update_pricing(new_price, recalculate=True)
        
        assert sample_line_item.unit_price == new_price
        # Line total should be recalculated: 2 * 750 = 1500
        assert sample_line_item.line_total == Decimal("1500.00")


class TestQuoteVersion:
    """Test QuoteVersion model functionality."""
    
    def test_create_quote_version(self, db_session, sample_quote):
        """Test creating a quote version record."""
        version_data = {
            "company_id": sample_quote.company_id,
            "quote_id": sample_quote.id,
            "version_number": 1,
            "created_by_user_id": 1,
            "change_reason": "Initial version",
            "quote_data": sample_quote.to_dict()
        }
        
        version = QuoteVersion(**version_data)
        db_session.add(version)
        db_session.commit()
        
        assert version.id is not None
        assert version.quote_id == sample_quote.id
        assert version.version_number == 1
        assert version.change_reason == "Initial version"
        assert version.quote_data is not None
    
    def test_version_string_representation(self, db_session, sample_quote):
        """Test version string representation."""
        version = QuoteVersion(
            company_id=sample_quote.company_id,
            quote_id=sample_quote.id,
            version_number=1,
            created_by_user_id=1,
            change_reason="Test version"
        )
        
        assert str(version) == "Version 1 - Test version"
        assert "QuoteVersion" in repr(version)


class TestQuoteApproval:
    """Test QuoteApproval model functionality."""
    
    def test_create_quote_approval(self, db_session, sample_quote):
        """Test creating a quote approval record."""
        approval_data = {
            "company_id": sample_quote.company_id,
            "quote_id": sample_quote.id,
            "approval_level": 1,
            "requested_by_user_id": 1,
            "assigned_to_user_id": 2,
            "request_reason": "Quote exceeds approval threshold",
            "due_date": datetime.utcnow() + timedelta(hours=24),
            "quote_total": sample_quote.total_amount
        }
        
        approval = QuoteApproval(**approval_data)
        db_session.add(approval)
        db_session.commit()
        
        assert approval.id is not None
        assert approval.quote_id == sample_quote.id
        assert approval.approval_level == 1
        assert approval.status == ApprovalStatus.PENDING
        assert approval.sla_hours == 24
    
    def test_approval_string_representation(self, db_session, sample_quote):
        """Test approval string representation."""
        approval = QuoteApproval(
            company_id=sample_quote.company_id,
            quote_id=sample_quote.id,
            approval_level=2,
            requested_by_user_id=1,
            assigned_to_user_id=2
        )
        
        expected_str = f"Approval Level 2 - {approval.status.value}"
        assert str(approval) == expected_str
        assert "QuoteApproval" in repr(approval)
    
    def test_approval_time_properties(self, db_session, sample_quote):
        """Test approval time-related properties."""
        # Create overdue approval
        overdue_approval = QuoteApproval(
            company_id=sample_quote.company_id,
            quote_id=sample_quote.id,
            approval_level=1,
            requested_by_user_id=1,
            assigned_to_user_id=2,
            due_date=datetime.utcnow() - timedelta(hours=1)
        )
        
        assert overdue_approval.is_overdue is True
        assert overdue_approval.hours_remaining is None or overdue_approval.hours_remaining < 0
        
        # Create pending approval
        pending_approval = QuoteApproval(
            company_id=sample_quote.company_id,
            quote_id=sample_quote.id,
            approval_level=1,
            requested_by_user_id=1,
            assigned_to_user_id=2,
            due_date=datetime.utcnow() + timedelta(hours=2)
        )
        
        assert pending_approval.is_overdue is False
        assert pending_approval.hours_remaining is not None
        assert pending_approval.hours_remaining > 0
    
    def test_approval_response_time(self, db_session, sample_quote):
        """Test approval response time calculation."""
        request_time = datetime.utcnow()
        response_time = request_time + timedelta(hours=3)
        
        approval = QuoteApproval(
            company_id=sample_quote.company_id,
            quote_id=sample_quote.id,
            approval_level=1,
            requested_by_user_id=1,
            assigned_to_user_id=2,
            request_date=request_time,
            response_date=response_time
        )
        
        assert approval.response_time_hours == 3.0
    
    def test_approve_quote(self, db_session, sample_quote):
        """Test approving a quote."""
        approval = QuoteApproval(
            company_id=sample_quote.company_id,
            quote_id=sample_quote.id,
            approval_level=1,
            requested_by_user_id=1,
            assigned_to_user_id=2
        )
        db_session.add(approval)
        db_session.commit()
        
        approval.approve(approver_user_id=2, notes="Quote looks good")
        
        assert approval.status == ApprovalStatus.APPROVED
        assert approval.response_date is not None
        assert approval.response_by_user_id == 2
        assert approval.response_notes == "Quote looks good"
    
    def test_reject_quote(self, db_session, sample_quote):
        """Test rejecting a quote."""
        approval = QuoteApproval(
            company_id=sample_quote.company_id,
            quote_id=sample_quote.id,
            approval_level=1,
            requested_by_user_id=1,
            assigned_to_user_id=2
        )
        db_session.add(approval)
        db_session.commit()
        
        approval.reject(rejector_user_id=2, reason="Discount too high")
        
        assert approval.status == ApprovalStatus.REJECTED
        assert approval.response_date is not None
        assert approval.response_by_user_id == 2
        assert approval.response_notes == "Discount too high"
    
    def test_escalate_approval(self, db_session, sample_quote):
        """Test escalating approval."""
        approval = QuoteApproval(
            company_id=sample_quote.company_id,
            quote_id=sample_quote.id,
            approval_level=1,
            requested_by_user_id=1,
            assigned_to_user_id=2,
            due_date=datetime.utcnow() + timedelta(hours=1)
        )
        db_session.add(approval)
        db_session.commit()
        
        original_due_date = approval.due_date
        approval.escalate(escalated_to_user_id=3, reason="Manager unavailable", escalated_by_user_id=1)
        
        assert approval.status == ApprovalStatus.ESCALATED
        assert approval.escalated_date is not None
        assert approval.escalated_to_user_id == 3
        assert approval.escalation_reason == "Manager unavailable"
        assert approval.due_date > original_due_date  # Due date extended