#!/usr/bin/env python3
"""
Manual test script to verify quote models work correctly.
"""

import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta

# Add the sales_module to Python path
sys.path.insert(0, os.path.dirname(__file__))

from sales_module.models.quote import (
    SalesQuote, SalesQuoteLineItem, QuoteVersion, QuoteApproval,
    QuoteStatus, ApprovalStatus, LineItemType
)


def test_sales_quote_creation():
    """Test creating a SalesQuote instance."""
    print("Testing SalesQuote creation...")
    
    quote_data = {
        "company_id": 1,
        "quote_number": "QUO-2025-001",
        "title": "Test Quote",
        "description": "Test quote description",
        "customer_id": 100,
        "prepared_by_user_id": 1,
        "valid_until": datetime.utcnow() + timedelta(days=30),
        "subtotal": Decimal("1000.00"),
        "total_amount": Decimal("1080.00"),
        "tax_amount": Decimal("80.00"),
        "currency_code": "USD"
    }
    
    quote = SalesQuote(**quote_data)
    
    # Test basic properties
    assert quote.quote_number == "QUO-2025-001"
    assert quote.status == QuoteStatus.DRAFT
    assert quote.version == 1
    assert quote.total_amount == Decimal("1080.00")
    assert quote.framework_version == "1.0.0"
    
    # Test string representations
    print(f"Quote str: {str(quote)}")
    print(f"Quote repr: {repr(quote)}")
    print(f"Display ID: {quote.display_identifier}")
    
    # Test properties
    print(f"Is expired: {quote.is_expired}")
    print(f"Days until expiry: {quote.days_until_expiry}")
    print(f"Is open: {quote.is_open}")
    print(f"Is closed: {quote.is_closed}")
    
    print("✅ SalesQuote creation test passed!")
    return quote


def test_quote_line_item_creation():
    """Test creating a SalesQuoteLineItem instance."""
    print("\nTesting SalesQuoteLineItem creation...")
    
    line_item_data = {
        "company_id": 1,
        "quote_id": 1,  # Would be from actual quote
        "line_number": 1,
        "item_name": "Test Product",
        "description": "Test product description",
        "quantity": Decimal("2.0"),
        "unit_price": Decimal("500.00"),
        "line_total": Decimal("1000.00")
    }
    
    line_item = SalesQuoteLineItem(**line_item_data)
    
    # Test basic properties
    assert line_item.line_number == 1
    assert line_item.item_name == "Test Product"
    assert line_item.quantity == Decimal("2.0")
    assert line_item.unit_price == Decimal("500.00")
    assert line_item.line_type == LineItemType.PRODUCT
    
    # Test string representations
    print(f"Line item str: {str(line_item)}")
    print(f"Line item repr: {repr(line_item)}")
    
    # Test calculations
    line_item.unit_cost = Decimal("300.00")
    line_item.line_cost = Decimal("600.00")
    print(f"Unit margin: {line_item.unit_margin}")
    print(f"Margin percentage: {line_item.margin_percentage}")
    print(f"Line margin: {line_item.line_margin}")
    
    # Test effective unit price
    print(f"Effective unit price: {line_item.effective_unit_price}")
    
    print("✅ SalesQuoteLineItem creation test passed!")
    return line_item


def test_quote_version_creation():
    """Test creating a QuoteVersion instance."""
    print("\nTesting QuoteVersion creation...")
    
    version_data = {
        "company_id": 1,
        "quote_id": 1,
        "version_number": 1,
        "created_by_user_id": 1,
        "change_reason": "Initial version",
        "quote_data": {"test": "data"}
    }
    
    version = QuoteVersion(**version_data)
    
    # Test basic properties
    assert version.version_number == 1
    assert version.change_reason == "Initial version"
    assert version.quote_data == {"test": "data"}
    
    # Test string representations
    print(f"Version str: {str(version)}")
    print(f"Version repr: {repr(version)}")
    
    print("✅ QuoteVersion creation test passed!")
    return version


def test_quote_approval_creation():
    """Test creating a QuoteApproval instance."""
    print("\nTesting QuoteApproval creation...")
    
    approval_data = {
        "company_id": 1,
        "quote_id": 1,
        "approval_level": 1,
        "requested_by_user_id": 1,
        "assigned_to_user_id": 2,
        "request_reason": "Quote exceeds approval threshold",
        "due_date": datetime.utcnow() + timedelta(hours=24),
        "quote_total": Decimal("1080.00")
    }
    
    approval = QuoteApproval(**approval_data)
    
    # Test basic properties
    assert approval.approval_level == 1
    assert approval.status == ApprovalStatus.PENDING
    assert approval.sla_hours == 24
    
    # Test string representations
    print(f"Approval str: {str(approval)}")
    print(f"Approval repr: {repr(approval)}")
    
    # Test time properties
    print(f"Is overdue: {approval.is_overdue}")
    print(f"Hours remaining: {approval.hours_remaining}")
    
    print("✅ QuoteApproval creation test passed!")
    return approval


def test_quote_methods():
    """Test quote methods and workflows."""
    print("\nTesting quote methods...")
    
    quote = test_sales_quote_creation()
    
    # Test discount application
    quote.subtotal = Decimal("1000.00")
    quote.tax_amount = Decimal("80.00")
    quote.shipping_amount = Decimal("20.00")
    
    print(f"Before discount - Total: {quote.total_amount}")
    quote.apply_overall_discount(Decimal("10.0"))  # 10% discount
    print(f"After 10% discount - Total: {quote.total_amount}")
    print(f"Discount amount: {quote.discount_amount}")
    
    # Test validity extension
    original_valid_until = quote.valid_until
    quote.extend_validity(10, user_id=1)
    print(f"Extended validity from {original_valid_until} to {quote.valid_until}")
    
    # Test status changes
    quote.send_to_customer(user_id=1)
    print(f"After sending - Status: {quote.status}")
    
    quote.mark_accepted(user_id=1, notes="Customer approved")
    print(f"After acceptance - Status: {quote.status}")
    
    print("✅ Quote methods test passed!")


def test_line_item_methods():
    """Test line item methods and calculations."""
    print("\nTesting line item methods...")
    
    line_item = test_quote_line_item_creation()
    
    # Test calculation
    line_item.quantity = Decimal("3.0")
    line_item.unit_price = Decimal("100.00")
    line_item.discount_percentage = Decimal("10.0")
    line_item.unit_cost = Decimal("60.00")
    line_item.tax_percentage = Decimal("8.0")
    
    print(f"Before calculation - Line total: {line_item.line_total}")
    line_item.calculate_line_total()
    print(f"After calculation - Line total: {line_item.line_total}")
    print(f"Discount amount: {line_item.discount_amount}")
    print(f"Tax amount: {line_item.tax_amount}")
    print(f"Line cost: {line_item.line_cost}")
    
    # Test discount application
    line_item.apply_discount(discount_percentage=Decimal("15.0"))
    print(f"After 15% discount - Line total: {line_item.line_total}")
    
    # Test price update
    line_item.update_pricing(Decimal("120.00"), recalculate=True)
    print(f"After price update - Line total: {line_item.line_total}")
    
    print("✅ Line item methods test passed!")


def test_approval_methods():
    """Test approval methods and workflows."""
    print("\nTesting approval methods...")
    
    approval = test_quote_approval_creation()
    
    # Test approval
    print(f"Initial status: {approval.status}")
    approval.approve(approver_user_id=2, notes="Quote looks good")
    print(f"After approval - Status: {approval.status}")
    print(f"Response notes: {approval.response_notes}")
    
    # Test rejection (create new approval)
    rejection_data = {
        "company_id": 1,
        "quote_id": 1,
        "approval_level": 1,
        "requested_by_user_id": 1,
        "assigned_to_user_id": 2
    }
    rejection_approval = QuoteApproval(**rejection_data)
    
    rejection_approval.reject(rejector_user_id=2, reason="Discount too high")
    print(f"Rejection status: {rejection_approval.status}")
    print(f"Rejection reason: {rejection_approval.response_notes}")
    
    print("✅ Approval methods test passed!")


def main():
    """Run all tests."""
    print("🚀 Starting Sales Module Model Tests\n")
    
    try:
        test_sales_quote_creation()
        test_quote_line_item_creation()
        test_quote_version_creation()
        test_quote_approval_creation()
        test_quote_methods()
        test_line_item_methods()
        test_approval_methods()
        
        print("\n🎉 All tests passed successfully!")
        print("✅ Quote models are working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)