#!/usr/bin/env python3
"""
Generate sample data for Sales Dashboard demonstration.

This script creates sample quotes and orders with realistic data patterns
to showcase the dashboard widgets and analytics capabilities.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from random import randint, choice, uniform

# Add sales module to path
sys.path.insert(0, os.path.dirname(__file__))

from sales_module.framework.database import get_db_session
from sales_module.services.quote_service import QuoteService
from sales_module.services.order_service import OrderService
from sales_module.models import QuoteStatus, OrderStatus, PaymentStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SampleDataGenerator:
    """Generate sample sales data for dashboard demonstration."""
    
    def __init__(self):
        self.company_id = 1
        self.user_id = 1
        
        # Sample customer data
        self.customers = [
            {"name": "TechCorp Solutions", "id": 1},
            {"name": "Global Manufacturing Ltd", "id": 2},
            {"name": "Innovation Systems Inc", "id": 3},
            {"name": "Metro Retail Group", "id": 4},
            {"name": "Digital Ventures Co", "id": 5},
            {"name": "Enterprise Solutions LLC", "id": 6},
            {"name": "Advanced Technologies", "id": 7},
            {"name": "Industrial Partners", "id": 8},
            {"name": "Smart Systems Corp", "id": 9},
            {"name": "Future Dynamics Inc", "id": 10}
        ]
        
        # Sample product data
        self.products = [
            {"name": "Professional Software License", "price": 2500.00, "code": "PSL-001"},
            {"name": "Enterprise Hardware Solution", "price": 4800.00, "code": "EHS-002"},
            {"name": "Cloud Integration Service", "price": 3200.00, "code": "CIS-003"},
            {"name": "Security Audit Package", "price": 1800.00, "code": "SAP-004"},
            {"name": "Training & Support Bundle", "price": 1200.00, "code": "TSB-005"},
            {"name": "Custom Development Hours", "price": 150.00, "code": "CDH-006"},
            {"name": "Data Migration Service", "price": 2200.00, "code": "DMS-007"},
            {"name": "Performance Optimization", "price": 1600.00, "code": "PO-008"},
            {"name": "Backup & Recovery Setup", "price": 950.00, "code": "BRS-009"},
            {"name": "Monitoring & Maintenance", "price": 1400.00, "code": "MM-010"}
        ]

    async def generate_sample_quotes(self, db_session, count=25):
        """Generate sample quotes with varied statuses and dates."""
        quote_service = QuoteService(db_session=db_session)
        
        logger.info(f"Generating {count} sample quotes...")
        
        # Define quote status distribution
        status_distribution = [
            (QuoteStatus.DRAFT, 6),
            (QuoteStatus.SENT, 8), 
            (QuoteStatus.VIEWED, 6),
            (QuoteStatus.ACCEPTED, 3),
            (QuoteStatus.REJECTED, 2)
        ]
        
        quote_count = 0
        for status, num_quotes in status_distribution:
            for i in range(num_quotes):
                try:
                    # Generate quote date in the last 60 days
                    days_ago = randint(1, 60)
                    quote_date = date.today() - timedelta(days=days_ago)
                    
                    # Valid until date (30-90 days from quote date)
                    valid_until = quote_date + timedelta(days=randint(30, 90))
                    
                    customer = choice(self.customers)
                    
                    # Generate line items (1-4 per quote)
                    line_items = []
                    num_items = randint(1, 4)
                    total_amount = 0
                    
                    for j in range(num_items):
                        product = choice(self.products)
                        quantity = randint(1, 5)
                        unit_price = Decimal(str(product["price"]))
                        discount = randint(0, 15) if randint(1, 100) <= 30 else 0  # 30% chance of discount
                        
                        line_total = unit_price * quantity * (1 - Decimal(discount) / 100)
                        total_amount += line_total
                        
                        line_items.append({
                            "product_id": None,
                            "item_code": product["code"],
                            "item_name": product["name"],
                            "description": f"Professional {product['name']} for enterprise deployment",
                            "quantity": quantity,
                            "unit_price": float(unit_price),
                            "discount_percentage": discount,
                            "line_total": float(line_total)
                        })
                    
                    # Create quote data
                    quote_data = {
                        "title": f"{customer['name']} - {choice(['Q1', 'Q2', 'Q3', 'Q4'])} {choice(['Enterprise', 'Professional', 'Premium'])} Package",
                        "description": f"Customized solution package for {customer['name']} including software, services, and support",
                        "customer_id": customer["id"],
                        "customer_name": customer["name"],
                        "quote_date": quote_date,
                        "valid_until": valid_until,
                        "payment_terms_days": choice([15, 30, 45, 60]),
                        "currency_code": "USD",
                        "subtotal_amount": float(total_amount),
                        "tax_amount": float(total_amount * Decimal("0.08")),  # 8% tax
                        "total_amount": float(total_amount * Decimal("1.08")),
                        "status": status,
                        "terms_and_conditions": "Standard terms and conditions apply. Payment due within specified terms."
                    }
                    
                    # Create quote
                    quote = quote_service.create_quote(
                        quote_data=quote_data,
                        line_items=line_items,
                        user_id=self.user_id,
                        company_id=self.company_id
                    )
                    
                    if quote:
                        quote_count += 1
                        logger.info(f"Created quote #{quote.quote_number} for {customer['name']} - Status: {status.value}")
                    
                except Exception as e:
                    logger.error(f"Error creating quote: {e}")
                    continue
        
        logger.info(f"Successfully created {quote_count} sample quotes")
        return quote_count

    async def generate_sample_orders(self, db_session, count=15):
        """Generate sample orders with varied statuses and realistic data."""
        order_service = OrderService(db_session=db_session)
        
        logger.info(f"Generating {count} sample orders...")
        
        # Define order status distribution
        status_distribution = [
            (OrderStatus.PENDING, 3),
            (OrderStatus.CONFIRMED, 4),
            (OrderStatus.PROCESSING, 3),
            (OrderStatus.SHIPPED, 2),
            (OrderStatus.DELIVERED, 2),
            (OrderStatus.COMPLETED, 1)
        ]
        
        order_count = 0
        for status, num_orders in status_distribution:
            for i in range(num_orders):
                try:
                    # Generate order date in the last 45 days
                    days_ago = randint(1, 45)
                    order_date = date.today() - timedelta(days=days_ago)
                    
                    # Required date (7-21 days from order date)
                    required_date = order_date + timedelta(days=randint(7, 21))
                    
                    customer = choice(self.customers)
                    
                    # Generate line items (1-3 per order)
                    line_items = []
                    num_items = randint(1, 3)
                    total_amount = 0
                    
                    for j in range(num_items):
                        product = choice(self.products)
                        quantity = randint(1, 3)
                        unit_price = Decimal(str(product["price"]))
                        
                        line_total = unit_price * quantity
                        total_amount += line_total
                        
                        line_items.append({
                            "product_id": None,
                            "item_code": product["code"],
                            "item_name": product["name"],
                            "description": f"Ordered: {product['name']}",
                            "quantity": quantity,
                            "unit_price": float(unit_price),
                            "line_total": float(line_total)
                        })
                    
                    # Payment status based on order status
                    if status in [OrderStatus.COMPLETED, OrderStatus.DELIVERED]:
                        payment_status = PaymentStatus.PAID
                    elif status in [OrderStatus.SHIPPED, OrderStatus.PROCESSING]:
                        payment_status = choice([PaymentStatus.PARTIAL, PaymentStatus.PAID])
                    else:
                        payment_status = PaymentStatus.UNPAID
                    
                    # Create order data
                    order_data = {
                        "title": f"{customer['name']} - Order #{1000 + order_count}",
                        "customer_id": customer["id"], 
                        "customer_name": customer["name"],
                        "order_date": order_date,
                        "required_date": required_date,
                        "priority": choice(["low", "normal", "high"]),
                        "payment_terms_days": choice([15, 30, 45]),
                        "shipping_method": choice(["standard", "express", "overnight"]),
                        "subtotal_amount": float(total_amount),
                        "tax_amount": float(total_amount * Decimal("0.08")),
                        "shipping_amount": float(randint(50, 200)),
                        "total_amount": float(total_amount * Decimal("1.08") + randint(50, 200)),
                        "status": status,
                        "payment_status": payment_status,
                        "billing_address": f"123 Business Ave, Suite {randint(100, 999)}, Enterprise City, ST 12345",
                        "shipping_address": f"456 Corporate Blvd, Floor {randint(1, 20)}, Business Town, ST 54321"
                    }
                    
                    # Create order
                    order = order_service.create_order(
                        order_data=order_data,
                        line_items=line_items,
                        user_id=self.user_id,
                        company_id=self.company_id
                    )
                    
                    if order:
                        order_count += 1
                        logger.info(f"Created order #{order.order_number} for {customer['name']} - Status: {status.value}")
                    
                except Exception as e:
                    logger.error(f"Error creating order: {e}")
                    continue
        
        logger.info(f"Successfully created {order_count} sample orders")
        return order_count

    async def generate_all_sample_data(self):
        """Generate all sample data for dashboard demonstration."""
        logger.info("Starting sample data generation for Sales Dashboard...")
        
        # Get database session
        db_session = next(get_db_session())
        
        try:
            # Generate quotes
            quotes_created = await self.generate_sample_quotes(db_session, count=25)
            
            # Generate orders
            orders_created = await self.generate_sample_orders(db_session, count=15)
            
            logger.info(f"✅ Sample data generation completed!")
            logger.info(f"   - Created {quotes_created} quotes")
            logger.info(f"   - Created {orders_created} orders")
            logger.info("Sales Dashboard is now ready with sample data.")
            
            return {
                "quotes_created": quotes_created,
                "orders_created": orders_created,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error during sample data generation: {e}")
            return {"success": False, "error": str(e)}
        
        finally:
            db_session.close()


async def main():
    """Main function to generate sample data."""
    generator = SampleDataGenerator()
    result = await generator.generate_all_sample_data()
    
    if result["success"]:
        print("\n🎉 Sales Dashboard Sample Data Generated Successfully! 🎉")
        print(f"   📋 Quotes Created: {result['quotes_created']}")
        print(f"   🛒 Orders Created: {result['orders_created']}")
        print("\nThe dashboard should now display realistic data across all widgets.")
        return 0
    else:
        print(f"\n❌ Sample data generation failed: {result['error']}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)