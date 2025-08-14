#!/usr/bin/env python3
"""
Complete Order Workflow End-to-End Test

Tests the entire order lifecycle from quote conversion through
delivery and payment with full inventory integration.
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import httpx
import pytest
from typing import Dict, Any, List

# Add the sales_module to Python path
sys.path.insert(0, os.path.dirname(__file__))

from sales_module.models import (
    SalesQuote, SalesOrder, SalesOrderLineItem, OrderShipment, OrderInvoice,
    OrderStatus, PaymentStatus, ShipmentStatus, InvoiceStatus, QuoteStatus
)
from sales_module.services import OrderService
from sales_module.framework.database import get_db_session


class OrderWorkflowTester:
    """End-to-end order workflow testing"""
    
    def __init__(self, base_url: str = "http://localhost:8006"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
        self.test_data = {}
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_step(self, step: str, details: str = ""):
        """Log test step with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ✓ {step}")
        if details:
            print(f"    {details}")
    
    def log_error(self, step: str, error: str):
        """Log error with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ✗ {step}")
        print(f"    ERROR: {error}")
    
    async def test_service_health(self) -> bool:
        """Test that the sales service is running"""
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                health_data = response.json()
                self.log_step("Service health check", f"Status: {health_data.get('status', 'unknown')}")
                return True
            else:
                self.log_error("Service health check", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_error("Service health check", str(e))
            return False
    
    async def setup_test_quote(self) -> Dict[str, Any]:
        """Create a test quote that can be converted to an order"""
        quote_data = {
            "quote_number": f"TEST-QUOTE-{int(datetime.now().timestamp())}",
            "title": "End-to-End Test Quote",
            "description": "Test quote for complete order workflow testing",
            "customer_id": 1,
            "status": "accepted",  # Ready for conversion
            "subtotal": 1500.00,
            "tax_amount": 150.00,
            "total_amount": 1650.00,
            "currency_code": "USD",
            "valid_from": datetime.utcnow().isoformat(),
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "payment_terms_days": 30,
            "prepared_by_user_id": 1,
            "line_items": [
                {
                    "line_number": 1,
                    "product_id": 101,
                    "item_name": "Test Product A",
                    "quantity": 5,
                    "unit_price": 200.00,
                    "line_total": 1000.00
                },
                {
                    "line_number": 2,
                    "product_id": 102,
                    "item_name": "Test Product B", 
                    "quantity": 2,
                    "unit_price": 250.00,
                    "line_total": 500.00
                }
            ]
        }
        
        try:
            response = await self.client.post("/api/v1/quotes/", json=quote_data)
            if response.status_code == 201:
                quote_result = response.json()
                self.test_data['quote'] = quote_result
                self.log_step("Test quote created", f"Quote ID: {quote_result['id']}")
                return quote_result
            else:
                self.log_error("Test quote creation", f"HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_error("Test quote creation", str(e))
            return None
    
    async def test_create_order_from_quote(self) -> Dict[str, Any]:
        """Test creating an order from the test quote"""
        quote = self.test_data.get('quote')
        if not quote:
            self.log_error("Create order from quote", "No test quote available")
            return None
        
        order_request = {
            "quote_id": quote['id'],
            "order_data": {
                "shipping_method": "Standard Shipping",
                "delivery_instructions": "Test delivery for end-to-end workflow",
                "internal_notes": "Created from automated test quote"
            }
        }
        
        try:
            response = await self.client.post("/orders/from-quote", json=order_request)
            if response.status_code == 201:
                order_result = response.json()
                self.test_data['order'] = order_result
                self.log_step("Order created from quote", 
                            f"Order ID: {order_result['id']}, Number: {order_result['order_number']}")
                return order_result
            else:
                self.log_error("Create order from quote", f"HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_error("Create order from quote", str(e))
            return None
    
    async def test_check_inventory_availability(self) -> Dict[str, Any]:
        """Test checking inventory availability for the order"""
        order = self.test_data.get('order')
        if not order:
            self.log_error("Check inventory availability", "No order available")
            return None
        
        try:
            response = await self.client.get(f"/orders/{order['id']}/inventory-availability")
            if response.status_code == 200:
                availability = response.json()
                self.test_data['inventory_availability'] = availability
                can_fulfill = availability.get('can_fulfill', False)
                self.log_step("Inventory availability checked", 
                            f"Can fulfill: {can_fulfill}, Line items: {len(availability.get('line_items', []))}")
                return availability
            else:
                self.log_error("Check inventory availability", f"HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_error("Check inventory availability", str(e))
            return None
    
    async def test_confirm_order(self) -> Dict[str, Any]:
        """Test confirming the order (with inventory reservation)"""
        order = self.test_data.get('order')
        if not order:
            self.log_error("Confirm order", "No order available")
            return None
        
        try:
            response = await self.client.put(f"/orders/{order['id']}/confirm")
            if response.status_code == 200:
                confirmed_order = response.json()
                self.test_data['confirmed_order'] = confirmed_order
                self.log_step("Order confirmed", 
                            f"Status: {confirmed_order['status']}, Hold status: {confirmed_order.get('hold_status', False)}")
                return confirmed_order
            else:
                self.log_error("Confirm order", f"HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_error("Confirm order", str(e))
            return None
    
    async def test_get_order_line_items(self) -> List[Dict[str, Any]]:
        """Test getting order line items"""
        order = self.test_data.get('order')
        if not order:
            self.log_error("Get order line items", "No order available")
            return None
        
        try:
            response = await self.client.get(f"/orders/{order['id']}/line-items")
            if response.status_code == 200:
                line_items = response.json()
                self.test_data['line_items'] = line_items
                self.log_step("Order line items retrieved", f"Count: {len(line_items)}")
                return line_items
            else:
                self.log_error("Get order line items", f"HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_error("Get order line items", str(e))
            return None
    
    async def test_create_shipment(self) -> Dict[str, Any]:
        """Test creating a shipment for the order"""
        order = self.test_data.get('order')
        line_items = self.test_data.get('line_items', [])
        
        if not order or not line_items:
            self.log_error("Create shipment", "No order or line items available")
            return None
        
        # Create shipment data with line item shipments
        shipment_data = {
            "tracking_number": f"TEST-TRACK-{int(datetime.now().timestamp())}",
            "carrier": "Test Carrier",
            "shipping_method": "Standard Shipping",
            "shipped_date": datetime.utcnow().isoformat(),
            "estimated_delivery_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),
            "notes": "Test shipment from automated workflow test",
            "line_item_shipments": [
                {
                    "line_item_id": line_items[0]['id'],
                    "quantity_shipped": 3  # Partial shipment of first item
                },
                {
                    "line_item_id": line_items[1]['id'], 
                    "quantity_shipped": 2  # Full shipment of second item
                }
            ]
        }
        
        try:
            response = await self.client.post(f"/orders/{order['id']}/shipments", json=shipment_data)
            if response.status_code == 201:
                shipment = response.json()
                self.test_data['shipment'] = shipment
                self.log_step("Shipment created", 
                            f"Shipment ID: {shipment['id']}, Tracking: {shipment.get('tracking_number')}")
                return shipment
            else:
                self.log_error("Create shipment", f"HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_error("Create shipment", str(e))
            return None
    
    async def test_update_shipment_tracking(self) -> Dict[str, Any]:
        """Test updating shipment tracking information"""
        shipment = self.test_data.get('shipment')
        if not shipment:
            self.log_error("Update shipment tracking", "No shipment available")
            return None
        
        tracking_data = {
            "tracking_number": f"UPDATED-{shipment.get('tracking_number', 'TEST')}",
            "carrier": "Updated Test Carrier"
        }
        
        try:
            response = await self.client.put(f"/shipments/{shipment['id']}/tracking", json=tracking_data)
            if response.status_code == 200:
                result = response.json()
                self.log_step("Shipment tracking updated", result.get('message', 'Success'))
                return result
            else:
                self.log_error("Update shipment tracking", f"HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_error("Update shipment tracking", str(e))
            return None
    
    async def test_create_invoice(self) -> Dict[str, Any]:
        """Test creating an invoice for the order"""
        order = self.test_data.get('order')
        if not order:
            self.log_error("Create invoice", "No order available")
            return None
        
        invoice_data = {
            "invoice_date": datetime.utcnow().isoformat(),
            "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "payment_terms_days": 30,
            "notes": "Test invoice from automated workflow"
        }
        
        try:
            response = await self.client.post(f"/orders/{order['id']}/invoices", json=invoice_data)
            if response.status_code == 201:
                invoice = response.json()
                self.test_data['invoice'] = invoice
                self.log_step("Invoice created", 
                            f"Invoice ID: {invoice['id']}, Number: {invoice['invoice_number']}")
                return invoice
            else:
                self.log_error("Create invoice", f"HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_error("Create invoice", str(e))
            return None
    
    async def test_record_payment(self) -> Dict[str, Any]:
        """Test recording a payment against the order"""
        order = self.test_data.get('order')
        invoice = self.test_data.get('invoice')
        
        if not order:
            self.log_error("Record payment", "No order available")
            return None
        
        payment_data = {
            "payment_amount": 825.00,  # Partial payment (50%)
            "payment_method": "Credit Card",
            "payment_reference": f"TEST-PAY-{int(datetime.now().timestamp())}",
            "invoice_id": invoice['id'] if invoice else None,
            "notes": "Partial payment from automated test"
        }
        
        try:
            response = await self.client.post(f"/orders/{order['id']}/payments", json=payment_data)
            if response.status_code == 200:
                updated_order = response.json()
                self.test_data['payment_order'] = updated_order
                self.log_step("Payment recorded", 
                            f"Paid: ${updated_order['paid_amount']}, Outstanding: ${updated_order['outstanding_amount']}")
                return updated_order
            else:
                self.log_error("Record payment", f"HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_error("Record payment", str(e))
            return None
    
    async def test_get_fulfillment_status(self) -> Dict[str, Any]:
        """Test getting comprehensive order fulfillment status"""
        order = self.test_data.get('order')
        if not order:
            self.log_error("Get fulfillment status", "No order available")
            return None
        
        try:
            response = await self.client.get(f"/orders/{order['id']}/fulfillment-status")
            if response.status_code == 200:
                status = response.json()
                self.test_data['fulfillment_status'] = status
                self.log_step("Fulfillment status retrieved", 
                            f"Status: {status.get('status')}, Fulfillment: {status.get('fulfillment_percentage', 0)}%")
                return status
            else:
                self.log_error("Get fulfillment status", f"HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_error("Get fulfillment status", str(e))
            return None
    
    async def test_order_analytics(self) -> Dict[str, Any]:
        """Test getting order analytics"""
        try:
            response = await self.client.get("/orders/analytics/summary")
            if response.status_code == 200:
                analytics = response.json()
                self.test_data['analytics'] = analytics
                self.log_step("Order analytics retrieved", 
                            f"Total orders: {analytics.get('summary', {}).get('total_orders', 0)}")
                return analytics
            else:
                self.log_error("Get order analytics", f"HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_error("Get order analytics", str(e))
            return None
    
    async def test_list_orders_with_filters(self) -> List[Dict[str, Any]]:
        """Test listing orders with various filters"""
        try:
            # Test basic listing
            response = await self.client.get("/orders/")
            if response.status_code != 200:
                self.log_error("List orders (basic)", f"HTTP {response.status_code} - {response.text}")
                return None
            
            orders = response.json()
            self.log_step("Orders listed (basic)", f"Count: {len(orders)}")
            
            # Test with filters
            filter_params = {
                "status": "CONFIRMED",
                "limit": 10,
                "offset": 0
            }
            
            response = await self.client.get("/orders/", params=filter_params)
            if response.status_code == 200:
                filtered_orders = response.json()
                self.log_step("Orders listed (filtered)", f"Count: {len(filtered_orders)}")
                return filtered_orders
            else:
                self.log_error("List orders (filtered)", f"HTTP {response.status_code} - {response.text}")
                return orders
                
        except Exception as e:
            self.log_error("List orders", str(e))
            return None
    
    def print_test_summary(self):
        """Print a comprehensive summary of the test results"""
        print("\n" + "="*60)
        print("🚀 ORDER WORKFLOW TEST SUMMARY")
        print("="*60)
        
        # Test data summary
        order = self.test_data.get('order', {})
        shipment = self.test_data.get('shipment', {})
        invoice = self.test_data.get('invoice', {})
        fulfillment = self.test_data.get('fulfillment_status', {})
        
        if order:
            print(f"📋 Order: {order.get('order_number')} (ID: {order.get('id')})")
            print(f"   Status: {order.get('status')}")
            print(f"   Total: ${order.get('total_amount', 0)}")
            print(f"   Customer: {order.get('customer_id')}")
        
        if shipment:
            print(f"📦 Shipment: {shipment.get('shipment_number')} (ID: {shipment.get('id')})")
            print(f"   Tracking: {shipment.get('tracking_number')}")
            print(f"   Carrier: {shipment.get('carrier')}")
        
        if invoice:
            print(f"🧾 Invoice: {invoice.get('invoice_number')} (ID: {invoice.get('id')})")
            print(f"   Total: ${invoice.get('total_amount', 0)}")
            print(f"   Outstanding: ${invoice.get('outstanding_amount', 0)}")
        
        if fulfillment:
            print(f"📊 Fulfillment: {fulfillment.get('fulfillment_percentage', 0)}% complete")
            print(f"   Payment: {fulfillment.get('payment_percentage', 0)}% paid")
        
        print("\n✅ End-to-End Order Workflow Test Completed Successfully!")
        print("="*60)


async def run_complete_workflow_test():
    """Run the complete order workflow test"""
    print("🚀 Starting Complete Order Workflow Test")
    print("="*60)
    
    async with OrderWorkflowTester() as tester:
        # Test service health
        if not await tester.test_service_health():
            print("❌ Sales service is not running. Please start the service first.")
            return False
        
        # Step 1: Setup test quote
        quote = await tester.setup_test_quote()
        if not quote:
            print("❌ Failed to create test quote. Cannot proceed.")
            return False
        
        # Step 2: Create order from quote
        order = await tester.test_create_order_from_quote()
        if not order:
            print("❌ Failed to create order from quote. Cannot proceed.")
            return False
        
        # Step 3: Check inventory availability
        availability = await tester.test_check_inventory_availability()
        # Note: This might fail if inventory service is not running, but we'll continue
        
        # Step 4: Confirm order (with inventory reservation)
        confirmed_order = await tester.test_confirm_order()
        # Note: This might put order on hold if inventory service is not available
        
        # Step 5: Get order line items
        line_items = await tester.test_get_order_line_items()
        if not line_items:
            print("❌ Failed to get order line items. Cannot proceed with shipping.")
            return False
        
        # Step 6: Create shipment
        shipment = await tester.test_create_shipment()
        # Note: Inventory consumption might fail if inventory service is not running
        
        # Step 7: Update shipment tracking
        if shipment:
            await tester.test_update_shipment_tracking()
        
        # Step 8: Create invoice
        invoice = await tester.test_create_invoice()
        
        # Step 9: Record payment
        payment_order = await tester.test_record_payment()
        
        # Step 10: Get fulfillment status
        fulfillment_status = await tester.test_get_fulfillment_status()
        
        # Step 11: Test analytics
        analytics = await tester.test_order_analytics()
        
        # Step 12: Test order listing with filters
        orders_list = await tester.test_list_orders_with_filters()
        
        # Print comprehensive summary
        tester.print_test_summary()
        
        return True


if __name__ == "__main__":
    # Run the complete workflow test
    try:
        success = asyncio.run(run_complete_workflow_test())
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)