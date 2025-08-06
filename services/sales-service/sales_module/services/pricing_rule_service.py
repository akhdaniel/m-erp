"""
Pricing Rule service for dynamic pricing and discount management.

Provides business logic for pricing rule management, price calculations,
discount application, and integration with inventory and customer data.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

from .base_service import BaseService
from sales_module.models.pricing_rules import PricingRule, PricingRuleType, DiscountType
from sales_module.integrations.inventory_client import inventory_client
from sales_module.messaging.event_publisher import sales_event_publisher


class PricingRuleService(BaseService):
    """
    Pricing Rule service for comprehensive pricing and discount management.
    
    Handles dynamic pricing calculations, discount application,
    rule management, and integration with product and customer data.
    """
    
    def __init__(self, db_session=None):
        """Initialize pricing rule service."""
        super().__init__(db_session)
        self.model_class = PricingRule
    
    def calculate_product_price(self, product_id: int, customer_id: int = None,
                              quantity: Decimal = Decimal('1.0'), base_price: Decimal = None,
                              product_category_id: int = None, company_id: int = None) -> Dict[str, Any]:
        """
        Calculate final product price for customer with all applicable pricing rules.
        
        Args:
            product_id: Product ID
            customer_id: Customer ID (optional)
            quantity: Quantity being purchased
            base_price: Base price if known (otherwise will lookup from inventory)
            product_category_id: Product category ID (optional)
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with pricing details and applied rules
        """
        logger.info(f"Calculating price for product {product_id}, customer {customer_id}, quantity {quantity}")
        
        # Get base price if not provided
        if not base_price:
            # In production, would call inventory service to get product price
            base_price = Decimal('100.00')  # Mock base price for demo
            logger.info(f"Using mock base price: {base_price}")
        
        # Get applicable pricing rules
        applicable_rules = self.get_applicable_rules(
            customer_id=customer_id,
            product_id=product_id,
            product_category_id=product_category_id,
            quantity=quantity,
            amount=base_price * quantity,
            company_id=company_id
        )
        
        # Calculate best price from all applicable rules
        best_price = base_price
        best_rule = None
        applied_rules = []
        total_discount = Decimal('0.00')
        
        for rule in applicable_rules:
            calculated_price = rule.calculate_price(base_price, quantity)
            if calculated_price and calculated_price < best_price:
                best_price = calculated_price
                best_rule = rule
            
            # Track all applicable rules for transparency
            rule_discount = rule.calculate_discount_amount(base_price, quantity)
            applied_rules.append({
                "rule_id": rule.id,
                "rule_name": rule.name,
                "rule_type": rule.rule_type.value,
                "discount_type": rule.discount_type.value,
                "discount_value": float(rule.discount_value),
                "calculated_price": float(calculated_price) if calculated_price else None,
                "discount_amount": float(rule_discount),
                "priority": rule.priority,
                "is_best": rule == best_rule
            })
        
        # Calculate total discount
        total_discount = (base_price * quantity) - (best_price * quantity)
        discount_percentage = (total_discount / (base_price * quantity)) * 100 if base_price > 0 else 0
        
        pricing_result = {
            "base_price": float(base_price),
            "final_price": float(best_price),
            "quantity": float(quantity),
            "line_total": float(best_price * quantity),
            "discount_amount": float(total_discount),
            "discount_percentage": float(discount_percentage),
            "rules_applied": len(applied_rules),
            "best_rule": {
                "rule_id": best_rule.id if best_rule else None,
                "rule_name": best_rule.name if best_rule else None,
                "rule_type": best_rule.rule_type.value if best_rule else None
            },
            "applicable_rules": applied_rules,
            "calculation_timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish pricing calculation event
        try:
            if sales_event_publisher and hasattr(sales_event_publisher, 'publish_event'):
                sales_event_publisher.publish_event("pricing.calculated", {
                    "product_id": product_id,
                    "customer_id": customer_id,
                    "company_id": company_id,
                    "base_price": float(base_price),
                    "final_price": float(best_price),
                    "discount_amount": float(total_discount),
                    "rules_count": len(applied_rules)
                })
        except Exception as e:
            logger.warning(f"Failed to publish pricing event: {e}")
        
        logger.info(f"Price calculation result: base={base_price}, final={best_price}, discount={total_discount}")
        return pricing_result
    
    def get_applicable_rules(self, customer_id: int = None, product_id: int = None,
                           product_category_id: int = None, quantity: Decimal = None,
                           amount: Decimal = None, company_id: int = None) -> List[PricingRule]:
        """
        Get applicable pricing rules for given criteria.
        
        Args:
            customer_id: Customer ID (optional)
            product_id: Product ID (optional)
            product_category_id: Product category ID (optional)
            quantity: Quantity (optional)
            amount: Total amount (optional)
            company_id: Company ID for isolation
            
        Returns:
            List of applicable pricing rules sorted by priority
        """
        # In production, would use actual database session
        # For now, return mock rules for demonstration
        logger.info(f"Getting applicable rules for customer={customer_id}, product={product_id}, quantity={quantity}")
        
        mock_rules = []
        
        # Mock volume discount rule
        if quantity and quantity >= 10:
            mock_rule = type('MockRule', (), {
                'id': 1,
                'name': 'Volume Discount 10%',
                'rule_type': PricingRuleType.VOLUME_DISCOUNT,
                'discount_type': DiscountType.PERCENTAGE,
                'discount_value': Decimal('10.00'),
                'priority': 1,
                'is_active': True,
                'calculate_price': lambda self, base_price, qty: base_price * Decimal('0.9'),
                'calculate_discount_amount': lambda self, base_price, qty: (base_price * qty) * Decimal('0.1'),
                'is_applicable_to_quantity': lambda self, qty: qty >= 10,
                'is_applicable_to_amount': lambda self, amt: True
            })()
            mock_rules.append(mock_rule)
        
        # Mock customer-specific rule
        if customer_id == 100:
            mock_rule = type('MockRule', (), {
                'id': 2,
                'name': 'VIP Customer 15% Discount',
                'rule_type': PricingRuleType.CUSTOMER_SPECIFIC,
                'discount_type': DiscountType.PERCENTAGE,
                'discount_value': Decimal('15.00'),
                'priority': 2,
                'is_active': True,
                'calculate_price': lambda self, base_price, qty: base_price * Decimal('0.85'),
                'calculate_discount_amount': lambda self, base_price, qty: (base_price * qty) * Decimal('0.15'),
                'is_applicable_to_quantity': lambda self, qty: True,
                'is_applicable_to_amount': lambda self, amt: True
            })()
            mock_rules.append(mock_rule)
        
        logger.info(f"Found {len(mock_rules)} applicable mock rules")
        return mock_rules
    
    def create_pricing_rule(self, rule_data: Dict[str, Any], user_id: int = None,
                          company_id: int = None) -> PricingRule:
        """
        Create new pricing rule with validation.
        
        Args:
            rule_data: Rule information
            user_id: ID of user creating the rule
            company_id: Company ID for multi-company isolation
            
        Returns:
            Created pricing rule instance
        """
        logger.info(f"Creating pricing rule: {rule_data.get('name')}")
        
        # Validate rule data
        self.validate_rule_data(rule_data)
        
        # Set default values
        rule_data.setdefault('priority', 100)
        rule_data.setdefault('is_active', True)
        rule_data.setdefault('framework_version', 1)
        
        if user_id:
            rule_data['created_by'] = user_id
        if company_id:
            rule_data['company_id'] = company_id
        
        # Create the rule using base service
        pricing_rule = self.create(rule_data, user_id, company_id)
        
        logger.info(f"Created pricing rule {pricing_rule.id}: {pricing_rule.name}")
        
        # Publish event
        try:
            if sales_event_publisher and hasattr(sales_event_publisher, 'publish_event'):
                sales_event_publisher.publish_event("pricing_rule.created", {
                    "rule_id": pricing_rule.id,
                    "rule_name": pricing_rule.name,
                    "rule_type": pricing_rule.rule_type.value,
                    "company_id": company_id,
                    "created_by": user_id
                })
        except Exception as e:
            logger.warning(f"Failed to publish pricing rule created event: {e}")
        
        return pricing_rule
    
    def update_pricing_rule(self, rule_id: int, rule_data: Dict[str, Any],
                          user_id: int = None, company_id: int = None) -> PricingRule:
        """
        Update existing pricing rule.
        
        Args:
            rule_id: Rule ID to update
            rule_data: Updated rule information
            user_id: ID of user updating the rule
            company_id: Company ID for isolation
            
        Returns:
            Updated pricing rule instance
        """
        logger.info(f"Updating pricing rule {rule_id}")
        
        # Validate rule data
        self.validate_rule_data(rule_data)
        
        # Update the rule using base service
        pricing_rule = self.update(rule_id, rule_data, user_id, company_id)
        
        logger.info(f"Updated pricing rule {pricing_rule.id}: {pricing_rule.name}")
        
        # Publish event
        try:
            if sales_event_publisher and hasattr(sales_event_publisher, 'publish_event'):
                sales_event_publisher.publish_event("pricing_rule.updated", {
                    "rule_id": pricing_rule.id,
                    "rule_name": pricing_rule.name,
                    "rule_type": pricing_rule.rule_type.value,
                    "company_id": company_id,
                    "updated_by": user_id
                })
        except Exception as e:
            logger.warning(f"Failed to publish pricing rule updated event: {e}")
        
        return pricing_rule
    
    def activate_rule(self, rule_id: int, user_id: int = None, company_id: int = None) -> PricingRule:
        """Activate pricing rule."""
        pricing_rule = self.get_by_id(rule_id, company_id)
        if not pricing_rule:
            raise ValueError(f"Pricing rule {rule_id} not found")
        
        pricing_rule.activate(user_id)
        return pricing_rule
    
    def deactivate_rule(self, rule_id: int, user_id: int = None, company_id: int = None) -> PricingRule:
        """Deactivate pricing rule."""
        pricing_rule = self.get_by_id(rule_id, company_id)
        if not pricing_rule:
            raise ValueError(f"Pricing rule {rule_id} not found")
        
        pricing_rule.deactivate(user_id)
        return pricing_rule
    
    def get_rules_by_type(self, rule_type: PricingRuleType, company_id: int = None) -> List[PricingRule]:
        """Get all pricing rules of specific type."""
        filters = {
            'rule_type': rule_type.value,
            'is_active': True
        }
        if company_id:
            filters['company_id'] = company_id
        
        result = self.list(filters=filters)
        return result.get('items', [])
    
    def get_customer_rules(self, customer_id: int, company_id: int = None) -> List[PricingRule]:
        """Get all pricing rules applicable to specific customer."""
        filters = {
            'customer_id': customer_id,
            'is_active': True
        }
        if company_id:
            filters['company_id'] = company_id
        
        result = self.list(filters=filters)
        return result.get('items', [])
    
    def validate_rule_data(self, rule_data: Dict[str, Any]) -> None:
        """
        Validate pricing rule data.
        
        Args:
            rule_data: Rule data to validate
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['name', 'rule_type', 'discount_type', 'discount_value']
        for field in required_fields:
            if not rule_data.get(field):
                raise ValueError(f"Missing required field: {field}")
        
        # Validate rule type
        try:
            PricingRuleType(rule_data['rule_type'])
        except ValueError:
            raise ValueError(f"Invalid rule type: {rule_data['rule_type']}")
        
        # Validate discount type
        try:
            DiscountType(rule_data['discount_type'])
        except ValueError:
            raise ValueError(f"Invalid discount type: {rule_data['discount_type']}")
        
        # Validate discount value
        discount_value = rule_data.get('discount_value')
        if isinstance(discount_value, (int, float)):
            discount_value = Decimal(str(discount_value))
        
        if not isinstance(discount_value, Decimal) or discount_value < 0:
            raise ValueError("Discount value must be a non-negative number")
        
        # Validate percentage discount is not over 100%
        if (rule_data['discount_type'] == DiscountType.PERCENTAGE and 
            discount_value > 100):
            raise ValueError("Percentage discount cannot exceed 100%")
        
        # Validate quantity ranges
        min_qty = rule_data.get('min_quantity')
        max_qty = rule_data.get('max_quantity')
        if min_qty and max_qty and min_qty > max_qty:
            raise ValueError("Minimum quantity cannot be greater than maximum quantity")
        
        # Validate amount ranges
        min_amt = rule_data.get('min_amount')
        max_amt = rule_data.get('max_amount')
        if min_amt and max_amt and min_amt > max_amt:
            raise ValueError("Minimum amount cannot be greater than maximum amount")
        
        # Validate date ranges
        start_date = rule_data.get('start_date')
        end_date = rule_data.get('end_date')
        if start_date and end_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start_date > end_date:
                raise ValueError("Start date cannot be after end date")
    
    def calculate_bulk_pricing(self, items: List[Dict[str, Any]], customer_id: int = None,
                             company_id: int = None) -> Dict[str, Any]:
        """
        Calculate pricing for multiple items at once.
        
        Args:
            items: List of items with product_id, quantity, base_price (optional)
            customer_id: Customer ID (optional)
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with bulk pricing results
        """
        logger.info(f"Calculating bulk pricing for {len(items)} items")
        
        item_results = []
        total_base = Decimal('0.00')
        total_final = Decimal('0.00')
        total_discount = Decimal('0.00')
        
        for item in items:
            item_result = self.calculate_product_price(
                product_id=item['product_id'],
                customer_id=customer_id,
                quantity=Decimal(str(item['quantity'])),
                base_price=Decimal(str(item['base_price'])) if item.get('base_price') else None,
                product_category_id=item.get('product_category_id'),
                company_id=company_id
            )
            
            item_results.append({
                "product_id": item['product_id'],
                "quantity": item['quantity'],
                **item_result
            })
            
            total_base += Decimal(str(item_result['base_price'])) * Decimal(str(item['quantity']))
            total_final += Decimal(str(item_result['line_total']))
            total_discount += Decimal(str(item_result['discount_amount']))
        
        bulk_result = {
            "items": item_results,
            "summary": {
                "total_base_amount": float(total_base),
                "total_final_amount": float(total_final),
                "total_discount_amount": float(total_discount),
                "overall_discount_percentage": float((total_discount / total_base) * 100) if total_base > 0 else 0,
                "items_count": len(items),
                "rules_applied_count": sum(1 for item in item_results if item['rules_applied'] > 0)
            },
            "calculation_timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Bulk pricing completed: {len(items)} items, total discount: {total_discount}")
        return bulk_result