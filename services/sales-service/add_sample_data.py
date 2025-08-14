#!/usr/bin/env python3
"""
Add sample sales data to demonstrate the service-driven UI architecture.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Import models
from sales_module.models import (
    SalesQuote, SalesQuoteLineItem, QuoteVersion, QuoteApproval,
    SalesOrder, SalesOrderLineItem, OrderShipment, OrderInvoice,
    QuoteStatus, OrderStatus, PaymentStatus, ShipmentStatus, InvoiceStatus
)
from sales_module.models.pricing import PriceRule
from sales_module.framework.database import Base

# Database URL
DATABASE_URL = "postgresql://postgres:password@postgres:5432/sales_db"

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_sample_data():
    """Create sample sales data"""
    session = SessionLocal()
    
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Check if data already exists
        existing_quotes = session.query(SalesQuote).count()
        if existing_quotes > 0:
            print(f"ℹ️  Database already has {existing_quotes} quotes. Skipping sample data creation.")
            return
        
        print("💰 Creating sample sales data...")
        
        # Sample customer IDs (from partner service)
        customer_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Sample product IDs (from inventory service)
        product_ids = list(range(1, 21))  # Assuming 20 products from inventory
        
        # Create pricing rules
        pricing_rules = [
            PriceRule(
                rule_name="VIP Customer Discount",
                rule_type="customer_specific",
                priority=100,
                discount_percentage=Decimal("15.00"),
                customer_ids=[1, 2],  # VIP customers
                is_active=True,
                company_id=1
            ),
            PriceRule(
                rule_name="Volume Discount - Large Orders",
                rule_type="volume_discount",
                priority=80,
                discount_percentage=Decimal("10.00"),
                min_quantity=Decimal("50"),
                is_active=True,
                company_id=1
            ),
            PriceRule(
                rule_name="Summer Sale 2025",
                rule_type="promotional",
                priority=60,
                discount_percentage=Decimal("20.00"),
                valid_from=datetime(2025, 6, 1),
                valid_to=datetime(2025, 8, 31),
                is_active=True,
                company_id=1
            ),
            PriceRule(
                rule_name="Electronics Category Discount",
                rule_type="product_category",
                priority=50,
                discount_percentage=Decimal("5.00"),
                product_category_ids=[1],  # Electronics category
                is_active=True,
                company_id=1
            )
        ]
        session.add_all(pricing_rules)
        session.commit()
        print(f"✅ Created {len(pricing_rules)} pricing rules")
        
        # Create quotes
        quotes = []
        quote_statuses = [QuoteStatus.DRAFT, QuoteStatus.SENT, QuoteStatus.VIEWED, 
                         QuoteStatus.ACCEPTED, QuoteStatus.REJECTED, QuoteStatus.EXPIRED]
        
        for i in range(1, 31):  # Create 30 quotes
            customer_id = random.choice(customer_ids)
            status = random.choice(quote_statuses)
            
            quote = SalesQuote(
                quote_number=f"Q-2025-{i:04d}",
                title=f"Quote for Customer {customer_id} - Project {i}",
                description=f"Sales quote for various products and services",
                customer_id=customer_id,
                status=status,
                valid_until=datetime.now() + timedelta(days=random.randint(7, 30)),
                sent_date=datetime.now() - timedelta(days=random.randint(1, 10)) if status != QuoteStatus.DRAFT else None,
                viewed_date=datetime.now() - timedelta(days=random.randint(0, 5)) if status in [QuoteStatus.VIEWED, QuoteStatus.ACCEPTED] else None,
                accepted_date=datetime.now() - timedelta(days=random.randint(0, 3)) if status == QuoteStatus.ACCEPTED else None,
                payment_terms_days=random.choice([15, 30, 45, 60]),
                currency_code="USD",
                sales_rep_user_id=random.choice([1, 2, 3]),
                priority=random.choice(['low', 'normal', 'high']),
                is_active=True,
                company_id=1
            )
            
            # Add line items
            num_items = random.randint(1, 5)
            subtotal = Decimal("0")
            for j in range(num_items):
                product_id = random.choice(product_ids)
                quantity = Decimal(random.randint(1, 20))
                unit_price = Decimal(random.uniform(50, 500)).quantize(Decimal("0.01"))
                discount_pct = Decimal(random.choice([0, 5, 10, 15])).quantize(Decimal("0.01"))
                
                line_item = SalesQuoteLineItem(
                    line_number=j + 1,
                    product_id=product_id,
                    item_name=f"Product {product_id}",
                    quantity=quantity,
                    unit_price=unit_price,
                    discount_percentage=discount_pct,
                    discount_amount=(unit_price * quantity * discount_pct / 100).quantize(Decimal("0.01")),
                    line_total=(unit_price * quantity * (100 - discount_pct) / 100).quantize(Decimal("0.01")),
                    is_active=True,
                    company_id=1
                )
                quote.line_items.append(line_item)
                subtotal += line_item.line_total
            
            # Calculate totals
            quote.subtotal = subtotal
            quote.discount_amount = (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))  # 5% overall discount
            quote.tax_amount = ((subtotal - quote.discount_amount) * Decimal("0.08")).quantize(Decimal("0.01"))  # 8% tax
            quote.total_amount = subtotal - quote.discount_amount + quote.tax_amount
            
            quotes.append(quote)
        
        session.add_all(quotes)
        session.commit()
        print(f"✅ Created {len(quotes)} quotes with line items")
        
        # Create orders from accepted quotes
        orders = []
        accepted_quotes = [q for q in quotes if q.status == QuoteStatus.ACCEPTED]
        
        for i, quote in enumerate(accepted_quotes, 1):
            order_status = random.choice([OrderStatus.PENDING, OrderStatus.CONFIRMED, 
                                        OrderStatus.PROCESSING, OrderStatus.SHIPPED, 
                                        OrderStatus.DELIVERED, OrderStatus.COMPLETED])
            
            order = SalesOrder(
                order_number=f"SO-2025-{i:04d}",
                title=f"Order from {quote.title}",
                description=quote.description,
                customer_id=quote.customer_id,
                quote_id=quote.id,
                status=order_status,
                payment_status=random.choice([PaymentStatus.UNPAID, PaymentStatus.PARTIAL, PaymentStatus.PAID]),
                order_date=quote.accepted_date,
                required_date=datetime.now() + timedelta(days=random.randint(7, 21)),
                confirmed_date=datetime.now() - timedelta(days=random.randint(0, 5)) if order_status != OrderStatus.PENDING else None,
                shipped_date=datetime.now() - timedelta(days=random.randint(0, 3)) if order_status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.COMPLETED] else None,
                delivered_date=datetime.now() - timedelta(days=random.randint(0, 1)) if order_status in [OrderStatus.DELIVERED, OrderStatus.COMPLETED] else None,
                completed_date=datetime.now() if order_status == OrderStatus.COMPLETED else None,
                subtotal=quote.subtotal,
                discount_amount=quote.discount_amount,
                tax_amount=quote.tax_amount,
                shipping_amount=Decimal(random.uniform(10, 50)).quantize(Decimal("0.01")),
                total_amount=quote.total_amount + Decimal(random.uniform(10, 50)).quantize(Decimal("0.01")),
                currency_code=quote.currency_code,
                payment_terms_days=quote.payment_terms_days,
                paid_amount=Decimal("0") if order_status == OrderStatus.PENDING else quote.total_amount * Decimal(random.uniform(0.3, 1.0)),
                sales_rep_user_id=quote.sales_rep_user_id,
                priority=quote.priority,
                shipping_method=random.choice(['standard', 'express', 'overnight']),
                is_active=True,
                company_id=1
            )
            
            # Copy line items from quote
            for quote_item in quote.line_items:
                order_item = SalesOrderLineItem(
                    line_number=quote_item.line_number,
                    product_id=quote_item.product_id,
                    item_name=quote_item.item_name,
                    quantity=quote_item.quantity,
                    unit_price=quote_item.unit_price,
                    discount_percentage=quote_item.discount_percentage,
                    discount_amount=quote_item.discount_amount,
                    line_total=quote_item.line_total,
                    quantity_shipped=quote_item.quantity if order_status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.COMPLETED] else Decimal("0"),
                    quantity_invoiced=quote_item.quantity if order_status in [OrderStatus.DELIVERED, OrderStatus.COMPLETED] else Decimal("0"),
                    is_active=True,
                    company_id=1
                )
                order.line_items.append(order_item)
            
            # Calculate outstanding amount
            order.outstanding_amount = order.total_amount - order.paid_amount
            
            # Update order item counts
            order.items_shipped = sum(1 for item in order.line_items if item.quantity_shipped > 0)
            order.items_remaining = len(order.line_items) - order.items_shipped
            
            orders.append(order)
        
        session.add_all(orders)
        session.commit()
        print(f"✅ Created {len(orders)} orders from accepted quotes")
        
        # Create shipments for shipped orders
        shipments = []
        shipped_orders = [o for o in orders if o.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.COMPLETED]]
        
        for order in shipped_orders:
            shipment = OrderShipment(
                order_id=order.id,
                shipment_number=f"SH-{order.order_number}",
                status=ShipmentStatus.DELIVERED if order.status in [OrderStatus.DELIVERED, OrderStatus.COMPLETED] else ShipmentStatus.IN_TRANSIT,
                tracking_number=f"TRK{random.randint(100000, 999999)}",
                carrier=random.choice(["FedEx", "UPS", "DHL", "USPS"]),
                shipping_method=order.shipping_method,
                shipped_date=order.shipped_date,
                estimated_delivery_date=order.shipped_date + timedelta(days=random.randint(2, 5)) if order.shipped_date else None,
                actual_delivery_date=order.delivered_date,
                shipping_cost=order.shipping_amount,
                company_id=1
            )
            shipments.append(shipment)
            order.shipment_count = 1
        
        session.add_all(shipments)
        session.commit()
        print(f"✅ Created {len(shipments)} shipments")
        
        # Create invoices for completed orders
        invoices = []
        completed_orders = [o for o in orders if o.status in [OrderStatus.DELIVERED, OrderStatus.COMPLETED]]
        
        for order in completed_orders:
            invoice = OrderInvoice(
                order_id=order.id,
                invoice_number=f"INV-{order.order_number}",
                status=InvoiceStatus.PAID if order.payment_status == PaymentStatus.PAID else InvoiceStatus.SENT,
                invoice_date=order.delivered_date or order.shipped_date,
                due_date=(order.delivered_date or order.shipped_date) + timedelta(days=order.payment_terms_days) if order.delivered_date or order.shipped_date else None,
                sent_date=order.delivered_date or order.shipped_date,
                payment_terms_days=order.payment_terms_days,
                subtotal=order.subtotal,
                discount_amount=order.discount_amount,
                tax_amount=order.tax_amount,
                total_amount=order.total_amount,
                paid_amount=order.paid_amount,
                outstanding_amount=order.outstanding_amount,
                currency_code=order.currency_code,
                is_active=True,
                company_id=1
            )
            invoices.append(invoice)
            order.invoice_count = 1
        
        session.add_all(invoices)
        session.commit()
        print(f"✅ Created {len(invoices)} invoices")
        
        # Summary statistics
        print("\n📊 Sample Data Summary:")
        print(f"   • Pricing Rules: {len(pricing_rules)}")
        print(f"   • Quotes: {len(quotes)}")
        print(f"   • - Draft: {sum(1 for q in quotes if q.status == QuoteStatus.DRAFT)}")
        print(f"   • - Sent: {sum(1 for q in quotes if q.status == QuoteStatus.SENT)}")
        print(f"   • - Accepted: {sum(1 for q in quotes if q.status == QuoteStatus.ACCEPTED)}")
        print(f"   • Orders: {len(orders)}")
        print(f"   • - Pending: {sum(1 for o in orders if o.status == OrderStatus.PENDING)}")
        print(f"   • - Shipped: {sum(1 for o in orders if o.status == OrderStatus.SHIPPED)}")
        print(f"   • - Completed: {sum(1 for o in orders if o.status == OrderStatus.COMPLETED)}")
        print(f"   • Shipments: {len(shipments)}")
        print(f"   • Invoices: {len(invoices)}")
        
        # Calculate revenue metrics
        total_revenue = sum(o.paid_amount for o in orders)
        pending_revenue = sum(o.outstanding_amount for o in orders)
        
        print(f"\n💰 Revenue Metrics:")
        print(f"   • Total Revenue: ${total_revenue:,.2f}")
        print(f"   • Pending Revenue: ${pending_revenue:,.2f}")
        print(f"   • Average Order Value: ${total_revenue/len(orders) if orders else 0:,.2f}")
        
        print("\n✨ Sample data created successfully!")
        print("   The sales dashboard should now display real data.")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_sample_data()