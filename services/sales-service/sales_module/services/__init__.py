"""
Sales Module Services Package.

This package contains all service layer classes that implement
business logic for the sales management module.
"""

# from .customer_service import CustomerService
# from .opportunity_service import OpportunityService
from .quote_service import QuoteService
# from .order_service import OrderService
from .pricing_rule_service import PricingRuleService
# from .pricing_service import PricingService

__all__ = [
    # "CustomerService",
    # "OpportunityService", 
    "QuoteService",
    # "OrderService",
    "PricingRuleService",
    # "PricingService"
]