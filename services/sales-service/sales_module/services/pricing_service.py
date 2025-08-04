"""
Pricing service for dynamic pricing and discount management.

Provides business logic for pricing calculations, discount application,
promotional campaigns, and price list management.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

from .base_service import BaseService
from sales_module.models import (
    PriceList, PriceRule, Discount, Promotion,
    PriceListType, RuleType, DiscountType, PromotionType
)


class PricingService(BaseService):
    """
    Pricing service for comprehensive pricing and discount management.
    
    Handles dynamic pricing calculations, discount application,
    promotional campaigns, and price optimization.
    """
    
    def __init__(self, db_session=None):
        """Initialize pricing service."""
        super().__init__(db_session)
        self.model_class = PriceList
    
    def calculate_product_price(self, product_id: int, customer_id: int,
                              quantity: Decimal = 1, base_price: Decimal = None,
                              company_id: int = None) -> Dict[str, Any]:
        """
        Calculate final product price for customer with all applicable discounts.
        
        Args:
            product_id: Product ID
            customer_id: Customer ID
            quantity: Quantity being purchased
            base_price: Base price if known (otherwise will lookup)
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with pricing details
        """
        # In production, would:
        # 1. Get base price from product catalog
        # 2. Find applicable price lists for customer
        # 3. Apply price rules in priority order
        # 4. Apply applicable discounts
        # 5. Apply promotions
        # 6. Calculate final price
        
        if base_price is None:
            base_price = self.get_base_price(product_id, company_id)
        
        # Find applicable price lists
        applicable_price_lists = self.get_applicable_price_lists(
            customer_id, product_id, company_id
        )
        
        # Apply price list calculations
        calculated_price = base_price
        applied_price_list = None
        
        for price_list in applicable_price_lists:
            list_price = price_list.calculate_price(base_price, quantity)
            if list_price < calculated_price:
                calculated_price = list_price
                applied_price_list = price_list
        
        # Apply price rules
        applied_rules = []
        rule_discount = Decimal('0.00')
        
        # Apply discounts
        applied_discounts = []
        discount_amount = Decimal('0.00')
        
        # Apply promotions
        applied_promotions = []
        promotion_savings = Decimal('0.00')
        
        # Calculate final price
        final_price = calculated_price - discount_amount - promotion_savings
        final_price = max(final_price, Decimal('0.01'))  # Minimum price
        
        total_savings = base_price - final_price
        savings_percentage = (total_savings / base_price * 100) if base_price > 0 else 0
        
        return {
            "product_id": product_id,
            "customer_id": customer_id,
            "quantity": float(quantity),
            "base_price": float(base_price),
            "calculated_price": float(calculated_price),
            "final_price": float(final_price),
            "total_savings": float(total_savings),
            "savings_percentage": float(savings_percentage),
            "applied_price_list": {
                "id": applied_price_list.id,
                "name": applied_price_list.name,
                "code": applied_price_list.code
            } if applied_price_list else None,
            "applied_rules": [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "type": rule.rule_type.value,
                    "savings": float(rule.calculate_discount(base_price, quantity) or 0)
                } for rule in applied_rules
            ],
            "applied_discounts": [
                {
                    "id": discount.id,
                    "name": discount.name,
                    "code": discount.code,
                    "type": discount.discount_type.value,
                    "savings": float(discount.calculate_discount(calculated_price, quantity) or 0)
                } for discount in applied_discounts
            ],
            "applied_promotions": [
                {
                    "id": promotion.id,
                    "name": promotion.name,
                    "code": promotion.code,
                    "savings": float(promotion_savings)
                } for promotion in applied_promotions
            ]
        }
    
    def calculate_order_pricing(self, order_items: List[Dict[str, Any]],
                              customer_id: int, company_id: int = None) -> Dict[str, Any]:
        """
        Calculate pricing for entire order with line-item and order-level discounts.
        
        Args:
            order_items: List of order items with product_id, quantity, base_price
            customer_id: Customer ID
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with complete order pricing
        """
        line_item_pricing = []
        order_subtotal = Decimal('0.00')
        total_savings = Decimal('0.00')
        
        # Calculate pricing for each line item
        for item in order_items:
            item_pricing = self.calculate_product_price(
                product_id=item['product_id'],
                customer_id=customer_id,
                quantity=Decimal(str(item['quantity'])),
                base_price=Decimal(str(item.get('base_price', 0))),
                company_id=company_id
            )
            
            line_total = Decimal(str(item_pricing['final_price'])) * Decimal(str(item['quantity']))
            item_pricing['line_total'] = float(line_total)
            
            line_item_pricing.append(item_pricing)
            order_subtotal += line_total
            total_savings += Decimal(str(item_pricing['total_savings'])) * Decimal(str(item['quantity']))
        
        # Apply order-level discounts and promotions
        order_level_discounts = self.get_order_level_discounts(customer_id, order_subtotal, company_id)
        order_discount_amount = Decimal('0.00')
        
        for discount in order_level_discounts:
            discount_amount = discount.calculate_discount(order_subtotal, 1, order_subtotal)
            order_discount_amount += discount_amount
        
        # Apply order-level promotions
        order_promotions = self.get_order_level_promotions(customer_id, order_items, company_id)
        order_promotion_savings = Decimal('0.00')
        
        for promotion in order_promotions:
            promotion_result = promotion.apply_promotion({
                'customer_id': customer_id,
                'total_amount': float(order_subtotal),
                'item_count': len(order_items)
            })
            if promotion_result['applied']:
                order_promotion_savings += Decimal(str(promotion_result['reward_amount']))
        
        # Calculate final order totals
        final_subtotal = order_subtotal - order_discount_amount - order_promotion_savings
        total_order_savings = total_savings + order_discount_amount + order_promotion_savings
        
        return {
            "customer_id": customer_id,
            "line_items": line_item_pricing,
            "order_subtotal": float(order_subtotal),
            "order_discount_amount": float(order_discount_amount),
            "order_promotion_savings": float(order_promotion_savings),
            "final_subtotal": float(final_subtotal),
            "total_savings": float(total_order_savings),
            "savings_percentage": float((total_order_savings / order_subtotal * 100) if order_subtotal > 0 else 0),
            "order_level_discounts": [
                {
                    "id": discount.id,
                    "name": discount.name,
                    "code": discount.code,
                    "savings": float(discount.calculate_discount(order_subtotal, 1, order_subtotal))
                } for discount in order_level_discounts
            ],
            "order_level_promotions": [
                {
                    "id": promotion.id,
                    "name": promotion.name,
                    "code": promotion.code,
                    "savings": float(order_promotion_savings)
                } for promotion in order_promotions
            ]
        }
    
    def apply_coupon_code(self, coupon_code: str, customer_id: int,
                         order_data: Dict[str, Any], company_id: int = None) -> Dict[str, Any]:
        """
        Apply coupon code to order and calculate savings.
        
        Args:
            coupon_code: Coupon/discount code
            customer_id: Customer ID
            order_data: Order information for validation
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with coupon application results
        """
        # Find discount or promotion by code
        discount = self.get_discount_by_code(coupon_code, company_id)
        promotion = self.get_promotion_by_code(coupon_code, company_id)
        
        if not discount and not promotion:
            return {
                "success": False,
                "error": "Invalid coupon code",
                "code": coupon_code
            }
        
        # Apply discount if found
        if discount:
            if not discount.is_applicable_to_customer(customer_id):
                return {
                    "success": False,
                    "error": "Coupon not valid for this customer",
                    "code": coupon_code
                }
            
            order_total = Decimal(str(order_data.get('total_amount', 0)))
            savings = discount.calculate_discount(order_total, 1, order_total)
            
            return {
                "success": True,
                "type": "discount",
                "discount_id": discount.id,
                "name": discount.name,
                "code": discount.code,
                "savings": float(savings),
                "description": f"Save {discount.percentage_value}% on your order" if discount.discount_type == DiscountType.PERCENTAGE else f"Save ${savings} on your order"
            }
        
        # Apply promotion if found
        if promotion:
            if not promotion.is_applicable_to_customer(customer_id):
                return {
                    "success": False,
                    "error": "Promotion not valid for this customer",
                    "code": coupon_code
                }
            
            result = promotion.apply_promotion(order_data)
            
            return {
                "success": result['applied'],
                "type": "promotion",
                "promotion_id": promotion.id,
                "name": promotion.name,
                "code": promotion.code,
                "savings": result.get('reward_amount', 0),
                "description": result.get('promotion_name', promotion.name),
                "error": result.get('reason') if not result['applied'] else None
            }
    
    def create_customer_price_list(self, customer_id: int, price_list_data: Dict[str, Any],
                                 user_id: int = None, company_id: int = None) -> PriceList:
        """
        Create customer-specific price list.
        
        Args:
            customer_id: Customer ID
            price_list_data: Price list information
            user_id: ID of user creating price list
            company_id: Company ID for isolation
            
        Returns:
            Created price list instance
        """
        # Set customer-specific settings
        price_list_data.update({
            'price_list_type': PriceListType.CUSTOMER_SPECIFIC,
            'specific_customers': [customer_id],
            'name': f"Customer {customer_id} Pricing"
        })
        
        return self.create(price_list_data, user_id, company_id)
    
    def create_volume_discount(self, discount_data: Dict[str, Any], 
                             tier_rules: List[Dict[str, Any]],
                             user_id: int = None, company_id: int = None) -> Discount:
        """
        Create volume-based discount with tier rules.
        
        Args:
            discount_data: Discount information
            tier_rules: List of volume tier rules
            user_id: ID of user creating discount
            company_id: Company ID for isolation
            
        Returns:
            Created discount instance
        """
        discount_data.update({
            'discount_type': DiscountType.VOLUME_TIER,
            'tier_rules': tier_rules
        })
        
        # Generate discount code if not provided
        if 'code' not in discount_data or not discount_data['code']:
            discount_data['code'] = self.generate_discount_code()
        
        discount = Discount(**discount_data)
        discount.save(self.db_session, user_id)
        
        return discount
    
    def create_promotion_campaign(self, promotion_data: Dict[str, Any],
                                user_id: int = None, company_id: int = None) -> Promotion:
        """
        Create promotional campaign.
        
        Args:
            promotion_data: Promotion information
            user_id: ID of user creating promotion
            company_id: Company ID for isolation
            
        Returns:
            Created promotion instance
        """
        # Generate promotion code if not provided
        if 'code' not in promotion_data or not promotion_data['code']:
            promotion_data['code'] = self.generate_promotion_code()
        
        promotion = Promotion(**promotion_data)
        promotion.save(self.db_session, user_id)
        
        return promotion
    
    def get_pricing_analytics(self, company_id: int = None,
                            date_range: Dict[str, datetime] = None) -> Dict[str, Any]:
        """
        Get pricing analytics and performance metrics.
        
        Args:
            company_id: Company ID for isolation
            date_range: Date range for analytics
            
        Returns:
            Dictionary with pricing analytics
        """
        return {
            "price_list_performance": {
                "total_price_lists": 0,
                "active_price_lists": 0,
                "most_used_price_list": None,
                "average_discount_percentage": 0.0
            },
            "discount_performance": {
                "total_discounts": 0,
                "active_discounts": 0,
                "total_usage": 0,
                "total_savings_provided": 0.0,
                "most_popular_discount": None,
                "average_discount_amount": 0.0
            },
            "promotion_performance": {
                "total_promotions": 0,
                "active_promotions": 0,
                "total_conversions": 0,
                "total_revenue_generated": 0.0,
                "conversion_rate": 0.0,
                "roi": 0.0
            },
            "pricing_trends": {
                "average_selling_price": 0.0,
                "price_variance": 0.0,
                "margin_impact": 0.0,
                "customer_price_sensitivity": 0.0
            },
            "customer_segments": {
                "high_discount_customers": 0,
                "price_sensitive_customers": 0,
                "premium_customers": 0
            }
        }
    
    def optimize_pricing(self, product_id: int, analysis_period_days: int = 90,
                        company_id: int = None) -> Dict[str, Any]:
        """
        Analyze pricing performance and provide optimization recommendations.
        
        Args:
            product_id: Product ID to analyze
            analysis_period_days: Period for analysis
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with pricing optimization recommendations
        """
        # In production, would analyze:
        # - Sales volume at different price points
        # - Competitor pricing
        # - Customer price sensitivity
        # - Profit margins
        # - Market demand patterns
        
        return {
            "product_id": product_id,
            "current_metrics": {
                "average_selling_price": 0.0,
                "sales_volume": 0,
                "revenue": 0.0,
                "margin": 0.0,
                "discount_frequency": 0.0
            },
            "market_analysis": {
                "competitor_average": 0.0,
                "market_position": "competitive",  # below, competitive, premium
                "price_elasticity": 0.0
            },
            "recommendations": [
                {
                    "type": "price_adjustment",
                    "current_price": 0.0,
                    "recommended_price": 0.0,
                    "expected_impact": {
                        "volume_change": 0.0,
                        "revenue_change": 0.0,
                        "margin_change": 0.0
                    },
                    "confidence": 0.85,
                    "reasoning": "Market analysis suggests room for price increase"
                }
            ],
            "risk_assessment": {
                "volume_risk": "low",  # low, medium, high
                "competitive_risk": "medium",
                "customer_retention_risk": "low"
            }
        }
    
    # Utility methods
    
    def get_base_price(self, product_id: int, company_id: int = None) -> Decimal:
        """Get base price for product."""
        # In production, would query product catalog
        return Decimal('100.00')  # Placeholder
    
    def get_applicable_price_lists(self, customer_id: int, product_id: int,
                                 company_id: int = None) -> List[PriceList]:
        """Get price lists applicable to customer and product."""
        # In production, would query database with filters
        return []  # Placeholder
    
    def get_order_level_discounts(self, customer_id: int, order_total: Decimal,
                                company_id: int = None) -> List[Discount]:
        """Get order-level discounts for customer."""
        # In production, would query applicable discounts
        return []  # Placeholder
    
    def get_order_level_promotions(self, customer_id: int, order_items: List[Dict[str, Any]],
                                 company_id: int = None) -> List[Promotion]:
        """Get order-level promotions for customer."""
        # In production, would query applicable promotions
        return []  # Placeholder
    
    def get_discount_by_code(self, code: str, company_id: int = None) -> Optional[Discount]:
        """Get discount by code."""
        # In production, would query database
        return None  # Placeholder
    
    def get_promotion_by_code(self, code: str, company_id: int = None) -> Optional[Promotion]:
        """Get promotion by code."""
        # In production, would query database
        return None  # Placeholder
    
    def generate_discount_code(self, prefix: str = "DISC") -> str:
        """Generate unique discount code."""
        return self.generate_number(prefix, "discount_sequence")
    
    def generate_promotion_code(self, prefix: str = "PROMO") -> str:
        """Generate unique promotion code."""
        return self.generate_number(prefix, "promotion_sequence")
    
    # Validation overrides
    
    def validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validate pricing entity creation data."""
        if self.model_class == PriceList:
            required_fields = ['name', 'code', 'price_list_type']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValueError(f"Field '{field}' is required for price list creation")
        
        elif self.model_class == Discount:
            required_fields = ['name', 'code', 'discount_type']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValueError(f"Field '{field}' is required for discount creation")
        
        elif self.model_class == Promotion:
            required_fields = ['name', 'code', 'promotion_type']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValueError(f"Field '{field}' is required for promotion creation")