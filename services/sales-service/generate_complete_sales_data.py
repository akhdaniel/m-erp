#!/usr/bin/env python3
"""
Generate comprehensive sample data for sales dashboard demonstration.
Creates quotes, orders, and pricing rules with realistic data.
"""

import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Add the sales module to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sales_module.framework.database import SessionLocal, engine
from sales_module.framework.base import Base
from sales_module.models.quote import SalesQuotation, SalesQuotationLineItem, QuotationStatus
from sales_module.models.order import SalesOrder, SalesOrderLineItem, OrderStatus, PaymentStatus, ShipmentStatus
from sales_module.models.pricing_rules import PricingRule, PricingRuleType, DiscountType

# Note: Tables should already exist in the database from migrations
# If not, we'll just use the existing tables

def generate_sample_data():
    """Generate comprehensive sample data for sales dashboard."""
    
    db = SessionLocal()
    
    try:
        print("🧹 Cleaning existing data...")
        # Clean existing data (skip if tables don't exist)
        try:
            db.query(SalesQuotationLineItem).delete()
            db.query(SalesQuotation).delete()
        except Exception as e:
            print(f"  Skipping quote table cleanup: {e}")
            db.rollback()
        
        try:
            db.query(SalesOrderLineItem).delete()
            db.query(SalesOrder).delete()
        except Exception as e:
            print(f"  Skipping order table cleanup: {e}")
            db.rollback()
            
        try:
            db.query(PricingRule).delete()
            db.commit()
        except Exception as e:
            print(f"  Skipping pricing rule cleanup: {e}")
            db.rollback()
        
        # Sample customer data (these would normally come from Partners service)
        customers = [
            {"id": 1, "name": "TechCorp Solutions", "is_vip": True},
            {"id": 2, "name": "Global Manufacturing Inc", "is_vip": False},
            {"id": 3, "name": "Innovation Systems", "is_vip": True},
            {"id": 4, "name": "Metro Retail Group", "is_vip": False},
            {"id": 5, "name": "Digital Ventures LLC", "is_vip": False},
            {"id": 6, "name": "Enterprise Holdings", "is_vip": True},
            {"id": 7, "name": "NextGen Industries", "is_vip": False},
            {"id": 8, "name": "Cloud Solutions Pro", "is_vip": True},
            {"id": 9, "name": "Data Analytics Corp", "is_vip": False},
            {"id": 10, "name": "Smart Tech Solutions", "is_vip": False}
        ]
        
        # Sample product data (these would normally come from Inventory service)
        products = [
            {"id": 1, "name": "Enterprise Software License", "price": 5000.00},
            {"id": 2, "name": "Cloud Storage 1TB", "price": 99.99},
            {"id": 3, "name": "Professional Services Hour", "price": 150.00},
            {"id": 4, "name": "Hardware Server Unit", "price": 8500.00},
            {"id": 5, "name": "Network Switch 48-port", "price": 2500.00},
            {"id": 6, "name": "Security Suite Annual", "price": 1200.00},
            {"id": 7, "name": "Database License", "price": 3500.00},
            {"id": 8, "name": "Backup Solution", "price": 800.00},
            {"id": 9, "name": "Monitoring Tool", "price": 600.00},
            {"id": 10, "name": "Development IDE License", "price": 299.99}
        ]
        
        print("💰 Creating pricing rules...")
        # Create pricing rules
        pricing_rules = [
            PricingRule(
                name="VIP Customer Discount",
                description="15% discount for VIP customers",
                rule_type=PricingRuleType.CUSTOMER_SPECIFIC,
                discount_type=DiscountType.PERCENTAGE,
                discount_value=Decimal("15.0"),
                priority=10,
                is_active=True,
                company_id=1
            ),
            PricingRule(
                name="Volume Discount - Large Orders",
                description="10% off orders over $10,000",
                rule_type=PricingRuleType.VOLUME_DISCOUNT,
                discount_type=DiscountType.PERCENTAGE,
                discount_value=Decimal("10.0"),
                min_amount=Decimal("10000.00"),
                priority=5,
                is_active=True,
                company_id=1
            ),
            PricingRule(
                name="Q1 Promotion",
                description="5% discount on all products",
                rule_type=PricingRuleType.PROMOTIONAL,
                discount_type=DiscountType.PERCENTAGE,
                discount_value=Decimal("5.0"),
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now() + timedelta(days=60),
                priority=1,
                is_active=True,
                company_id=1
            )
        ]
        
        for rule in pricing_rules:
            db.add(rule)
        
        print("📝 Creating quotes...")
        # Create quotes with various statuses
        quote_statuses = [QuotationStatus.DRAFT, QuotationStatus.SENT, QuotationStatus.ACCEPTED, QuotationStatus.REJECTED, QuotationStatus.EXPIRED]
        quotes_created = 0
        
        for i in range(30):  # Create 30 quotes
            customer = random.choice(customers)
            days_ago = random.randint(0, 60)
            quote_date = datetime.now() - timedelta(days=days_ago)
            valid_days = random.choice([7, 14, 30])
            
            status = random.choice(quote_statuses)
            if days_ago > 30:
                status = random.choice([QuotationStatus.ACCEPTED, QuotationStatus.REJECTED, QuotationStatus.EXPIRED])
            
            quote = SalesQuotation(
                quote_number=f"QT-2025-{1000 + i:04d}",
                customer_id=customer["id"],
                title=f"Quotation for {customer['name']}",
                valid_from=quote_date,
                valid_until=quote_date + timedelta(days=valid_days),
                status=status,
                subtotal=Decimal("0"),
                tax_amount=Decimal("0"),
                total_amount=Decimal("0"),
                currency_code="USD",
                payment_terms_days=30,
                prepared_by_user_id=1,
                company_id=1
            )
            
            db.add(quote)
            db.flush()
            
            # Add line items
            num_items = random.randint(1, 5)
            subtotal = Decimal("0")
            
            for j in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 10)
                unit_price = Decimal(str(product["price"]))
                discount = Decimal(str(random.choice([0, 5, 10, 15])))
                
                line_subtotal = unit_price * quantity
                discount_amount = line_subtotal * (discount / 100)
                line_total = line_subtotal - discount_amount
                
                item = SalesQuotationLineItem(
                    quote_id=quote.id,
                    product_id=product["id"],
                    description=product["name"],
                    quantity=quantity,
                    unit_price=unit_price,
                    discount_percentage=discount,
                    discount_amount=discount_amount,
                    total_price=line_total
                )
                
                db.add(item)
                subtotal += line_total
            
            # Update quote totals
            quote.subtotal = subtotal
            quote.tax_amount = subtotal * Decimal("0.08")  # 8% tax
            quote.total_amount = subtotal + quote.tax_amount
            quotes_created += 1
        
        print(f"✅ Created {quotes_created} quotes")
        
        print("📦 Creating orders...")
        # Create orders (some from accepted quotes)
        order_statuses = [OrderStatus.DRAFT, OrderStatus.CONFIRMED, OrderStatus.PROCESSING, 
                         OrderStatus.COMPLETED, OrderStatus.CANCELLED]
        payment_statuses = [PaymentStatus.PENDING, PaymentStatus.PARTIAL, PaymentStatus.PAID, PaymentStatus.OVERDUE]
        
        orders_created = 0
        
        for i in range(50):  # Create 50 orders
            customer = random.choice(customers)
            days_ago = random.randint(0, 90)
            order_date = datetime.now() - timedelta(days=days_ago)
            delivery_date = order_date + timedelta(days=random.randint(3, 14))
            
            # Determine statuses based on age
            if days_ago > 60:
                order_status = random.choice([OrderStatus.COMPLETED, OrderStatus.CANCELLED])
                payment_status = PaymentStatus.PAID if order_status == OrderStatus.COMPLETED else PaymentStatus.PENDING
            elif days_ago > 30:
                order_status = random.choice([OrderStatus.PROCESSING, OrderStatus.CONFIRMED])
                payment_status = random.choice([PaymentStatus.PAID, PaymentStatus.PARTIAL])
            else:
                order_status = random.choice([OrderStatus.DRAFT, OrderStatus.CONFIRMED])
                payment_status = random.choice([PaymentStatus.PENDING, PaymentStatus.PARTIAL])
            
            order = SalesOrder(
                order_number=f"ORD-2025-{2000 + i:04d}",
                customer_id=customer["id"],
                description=f"Order for {customer['name']}",
                order_date=order_date,
                delivery_date=delivery_date,
                status=order_status,
                payment_status=payment_status,
                subtotal=Decimal("0"),
                tax_amount=Decimal("0"),
                shipping_amount=Decimal("50.00"),
                total_amount=Decimal("0"),
                currency_code="USD",
                payment_terms_days=30,
                sales_rep_id=1,
                shipping_address=f"{random.randint(100, 999)} Main St, City, State 12345",
                company_id=1
            )
            
            db.add(order)
            db.flush()
            
            # Add line items
            num_items = random.randint(1, 6)
            subtotal = Decimal("0")
            
            for j in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 15)
                unit_price = Decimal(str(product["price"]))
                
                # Apply VIP discount if applicable
                discount = Decimal("0")
                if customer["is_vip"]:
                    discount = Decimal("15")
                elif subtotal > 10000:
                    discount = Decimal("10")
                elif random.random() > 0.7:
                    discount = Decimal("5")
                
                line_subtotal = unit_price * quantity
                discount_amount = line_subtotal * (discount / 100)
                line_total = line_subtotal - discount_amount
                
                item = SalesOrderLineItem(
                    order_id=order.id,
                    product_id=product["id"],
                    description=product["name"],
                    quantity=quantity,
                    unit_price=unit_price,
                    discount_percentage=discount,
                    discount_amount=discount_amount,
                    total_price=line_total
                )
                
                db.add(item)
                subtotal += line_total
            
            # Update order totals
            order.subtotal = subtotal
            order.tax_amount = subtotal * Decimal("0.08")  # 8% tax
            order.total_amount = subtotal + order.tax_amount + order.shipping_amount
            
            # Set payment information
            if payment_status == PaymentStatus.PAID:
                order.paid_amount = order.total_amount
            elif payment_status == PaymentStatus.PARTIAL:
                order.paid_amount = order.total_amount * Decimal("0.5")
            else:
                order.paid_amount = Decimal("0")
            
            orders_created += 1
        
        print(f"✅ Created {orders_created} orders")
        
        # Commit all changes
        db.commit()
        
        # Display summary statistics
        print("\n📊 Dashboard Data Summary:")
        print("=" * 50)
        
        # Active quotes
        active_quotes = db.query(SalesQuotation).filter(
            SalesQuotation.status.in_([QuotationStatus.DRAFT, QuotationStatus.SENT])
        ).count()
        print(f"Active Quotations: {active_quotes}")
        
        # Pending orders
        pending_orders = db.query(SalesOrder).filter(
            SalesOrder.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PROCESSING])
        ).count()
        print(f"Pending Orders: {pending_orders}")
        
        # Monthly revenue (current month)
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = db.query(SalesOrder).filter(
            SalesOrder.order_date >= start_of_month,
            SalesOrder.payment_status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL])
        ).with_entities(
            db.func.sum(SalesOrder.paid_amount)
        ).scalar() or 0
        print(f"Monthly Revenue: ${monthly_revenue:,.2f}")
        
        # Conversion rate
        total_quotes = db.query(SalesQuotation).count()
        accepted_quotes = db.query(SalesQuotation).filter(
            SalesQuotation.status == QuotationStatus.ACCEPTED
        ).count()
        conversion_rate = (accepted_quotes / total_quotes * 100) if total_quotes > 0 else 0
        print(f"Quotation Conversion Rate: {conversion_rate:.1f}%")
        
        # Top customers
        print("\nTop 5 Customers by Revenue:")
        top_customers_query = db.query(
            SalesOrder.customer_name,
            db.func.count(SalesOrder.id).label('order_count'),
            db.func.sum(SalesOrder.total_amount).label('total_revenue')
        ).group_by(
            SalesOrder.customer_name
        ).order_by(
            db.func.sum(SalesOrder.total_amount).desc()
        ).limit(5)
        
        for customer in top_customers_query:
            print(f"  - {customer.customer_name}: ${customer.total_revenue:,.2f} ({customer.order_count} orders)")
        
        print("\n✨ Sample data generation complete!")
        print("🚀 Sales dashboard is now ready with realistic data")
        
    except Exception as e:
        print(f"❌ Error generating data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    generate_sample_data()