"""
Sales Module Models Package.

This package contains all database models for the sales management module,
including customers, opportunities, quotes, orders, and pricing models.
"""

# from .customer import Customer, CustomerContact, CustomerAddress, CustomerCategory
# from .opportunity import SalesOpportunity, OpportunityStage, OpportunityActivity
from .quote import SalesQuote, SalesQuoteLineItem, QuoteVersion, QuoteApproval, QuoteStatus, ApprovalStatus, LineItemType
# from .order import SalesOrder, SalesOrderLineItem, OrderShipment, OrderInvoice
# from .pricing import PriceList, PriceRule, Discount, Promotion

__all__ = [
    # Customer models
    # "Customer",
    # "CustomerContact",
    # "CustomerAddress", 
    # "CustomerCategory",
    
    # Opportunity models
    # "SalesOpportunity",
    # "OpportunityStage",
    # "OpportunityActivity",
    
    # Quote models
    "SalesQuote",
    "SalesQuoteLineItem",
    "QuoteVersion",
    "QuoteApproval",
    "QuoteStatus",
    "ApprovalStatus",
    "LineItemType",
    
    # Order models
    # "SalesOrder",
    # "SalesOrderLineItem",
    # "OrderShipment",
    # "OrderInvoice",
    
    # Pricing models
    # "PriceList",
    # "PriceRule",
    # "Discount",
    # "Promotion"
]