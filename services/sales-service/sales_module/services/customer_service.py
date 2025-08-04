"""
Customer service for managing customer relationships and data.

Provides business logic for customer management including
customer creation, updates, contact management, and analytics.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from .base_service import BaseService
from sales_module.models import Customer, CustomerContact, CustomerAddress, CustomerCategory


class CustomerService(BaseService):
    """
    Customer service for comprehensive customer relationship management.
    
    Handles customer lifecycle, contact management, address management,
    and customer analytics and reporting.
    """
    
    def __init__(self, db_session=None):
        """Initialize customer service."""
        super().__init__(db_session)
        self.model_class = Customer
    
    def create_customer(self, customer_data: Dict[str, Any], user_id: int = None,
                       company_id: int = None) -> Customer:
        """
        Create new customer with validation and number generation.
        
        Args:
            customer_data: Customer information
            user_id: ID of user creating the customer
            company_id: Company ID for multi-company isolation
            
        Returns:
            Created customer instance
        """
        # Generate customer number if not provided
        if 'customer_number' not in customer_data or not customer_data['customer_number']:
            customer_data['customer_number'] = self.generate_customer_number()
        
        # Set acquisition date if not provided
        if 'acquisition_date' not in customer_data:
            customer_data['acquisition_date'] = datetime.utcnow()
        
        # Create customer
        customer = self.create(customer_data, user_id, company_id)
        
        return customer
    
    def update_financial_metrics(self, customer_id: int, order_count_change: int = 0,
                                order_value_change: Decimal = None, user_id: int = None,
                                company_id: int = None) -> Optional[Customer]:
        """
        Update customer financial metrics after order changes.
        
        Args:
            customer_id: Customer ID
            order_count_change: Change in order count (+/-)
            order_value_change: Change in order value
            user_id: ID of user making the change
            company_id: Company ID for isolation
            
        Returns:
            Updated customer instance or None if not found
        """
        customer = self.get_by_id(customer_id, company_id)
        if not customer:
            return None
        
        # Update financial metrics
        customer.update_financial_metrics(order_count_change, order_value_change)
        
        # Update last order date if new order
        if order_count_change > 0:
            customer.last_order_date = datetime.utcnow()
            if not customer.first_order_date:
                customer.first_order_date = datetime.utcnow()
        
        # Save changes
        customer.save(self.db_session, user_id)
        
        return customer
    
    def block_customer(self, customer_id: int, reason: str, user_id: int = None,
                      company_id: int = None) -> Optional[Customer]:
        """
        Block customer from placing orders.
        
        Args:
            customer_id: Customer ID
            reason: Reason for blocking
            user_id: ID of user blocking the customer
            company_id: Company ID for isolation
            
        Returns:
            Updated customer instance or None if not found
        """
        customer = self.get_by_id(customer_id, company_id)
        if not customer:
            return None
        
        customer.block_customer(reason, user_id)
        return customer
    
    def unblock_customer(self, customer_id: int, user_id: int = None,
                        company_id: int = None) -> Optional[Customer]:
        """
        Unblock customer to allow orders.
        
        Args:
            customer_id: Customer ID
            user_id: ID of user unblocking the customer
            company_id: Company ID for isolation
            
        Returns:
            Updated customer instance or None if not found
        """
        customer = self.get_by_id(customer_id, company_id)
        if not customer:
            return None
        
        customer.unblock_customer(user_id)
        return customer
    
    def get_customer_credit_info(self, customer_id: int, company_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Get customer credit information and score.
        
        Args:
            customer_id: Customer ID
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with credit information or None if not found
        """
        customer = self.get_by_id(customer_id, company_id)
        if not customer:
            return None
        
        return {
            "customer_id": customer.id,
            "customer_number": customer.customer_number,
            "credit_limit": float(customer.credit_limit) if customer.credit_limit else None,
            "outstanding_balance": float(customer.outstanding_balance),
            "available_credit": float(customer.available_credit) if customer.available_credit else None,
            "is_over_limit": customer.is_over_credit_limit,
            "credit_score": customer.calculate_credit_score(),
            "payment_terms_days": customer.payment_terms_days,
            "status": customer.status.value,
            "is_blocked": customer.is_blocked
        }
    
    def add_customer_contact(self, customer_id: int, contact_data: Dict[str, Any],
                           user_id: int = None, company_id: int = None) -> Optional[CustomerContact]:
        """
        Add contact to customer.
        
        Args:
            customer_id: Customer ID
            contact_data: Contact information
            user_id: ID of user adding the contact
            company_id: Company ID for isolation
            
        Returns:
            Created contact instance or None if customer not found
        """
        customer = self.get_by_id(customer_id, company_id)
        if not customer:
            return None
        
        # Set customer relationship
        contact_data['customer_id'] = customer_id
        contact_data['company_id'] = company_id
        
        # Create contact
        contact = CustomerContact(**contact_data)
        contact.save(self.db_session, user_id)
        
        return contact
    
    def add_customer_address(self, customer_id: int, address_data: Dict[str, Any],
                           user_id: int = None, company_id: int = None) -> Optional[CustomerAddress]:
        """
        Add address to customer.
        
        Args:
            customer_id: Customer ID
            address_data: Address information
            user_id: ID of user adding the address
            company_id: Company ID for isolation
            
        Returns:
            Created address instance or None if customer not found
        """
        customer = self.get_by_id(customer_id, company_id)
        if not customer:
            return None
        
        # Set customer relationship
        address_data['customer_id'] = customer_id
        address_data['company_id'] = company_id
        
        # Create address
        address = CustomerAddress(**address_data)
        
        # Validate and geocode address
        address.validate_address()
        address.geocode_address()
        
        address.save(self.db_session, user_id)
        
        return address
    
    def get_customer_dashboard_data(self, customer_id: int, 
                                  company_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive customer dashboard data.
        
        Args:
            customer_id: Customer ID
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with dashboard data or None if not found
        """
        customer = self.get_by_id(customer_id, company_id)
        if not customer:
            return None
        
        # In production, would query related data from database
        return {
            "customer_info": {
                "id": customer.id,
                "name": customer.name,
                "customer_number": customer.customer_number,
                "display_name": customer.display_name or customer.name,
                "status": customer.status.value,
                "customer_type": customer.customer_type.value,
                "is_vip": customer.is_vip,
                "is_blocked": customer.is_blocked
            },
            "financial_summary": {
                "total_orders": customer.total_orders_count,
                "total_value": float(customer.total_orders_value),
                "average_order_value": float(customer.average_order_value),
                "outstanding_balance": float(customer.outstanding_balance),
                "credit_limit": float(customer.credit_limit) if customer.credit_limit else None,
                "available_credit": float(customer.available_credit) if customer.available_credit else None,
                "credit_score": customer.calculate_credit_score()
            },
            "activity_summary": {
                "customer_age_days": customer.customer_age_days,
                "days_since_last_order": customer.days_since_last_order,
                "first_order_date": customer.first_order_date.isoformat() if customer.first_order_date else None,
                "last_order_date": customer.last_order_date.isoformat() if customer.last_order_date else None,
                "acquisition_date": customer.acquisition_date.isoformat() if customer.acquisition_date else None
            },
            "contact_info": {
                "sales_rep_id": customer.sales_rep_user_id,
                "preferred_communication": customer.preferred_communication,
                "language": customer.language_code,
                "timezone": customer.timezone,
                "marketing_allowed": customer.allow_marketing
            },
            # Would include actual data in production:
            "recent_orders": [],
            "open_quotes": [],
            "active_opportunities": [],
            "contacts": [],
            "addresses": []
        }
    
    def search_customers(self, search_term: str, filters: Dict[str, Any] = None,
                        company_id: int = None, page: int = 1, 
                        page_size: int = 50) -> Dict[str, Any]:
        """
        Search customers with advanced filtering.
        
        Args:
            search_term: Search term for name, number, email, etc.
            filters: Additional filter criteria
            company_id: Company ID for isolation
            page: Page number
            page_size: Items per page
            
        Returns:
            Search results with pagination
        """
        # In production, would implement full-text search across:
        # - Customer name, display_name, customer_number
        # - Contact email addresses and names
        # - Address information
        # - Tags and custom attributes
        
        print(f"Customer Service: Searching customers for '{search_term}' with filters {filters}")
        
        return {
            "items": [],  # Would contain actual search results
            "total": 0,
            "page": page,
            "page_size": page_size,
            "search_term": search_term,
            "filters": filters
        }
    
    def get_customer_analytics(self, company_id: int = None, 
                             date_range: Dict[str, datetime] = None) -> Dict[str, Any]:
        """
        Get customer analytics and metrics.
        
        Args:
            company_id: Company ID for isolation
            date_range: Date range for analytics
            
        Returns:
            Dictionary with analytics data
        """
        # In production, would query aggregated data from database
        return {
            "summary": {
                "total_customers": 0,
                "active_customers": 0,
                "new_customers_this_month": 0,
                "vip_customers": 0,
                "blocked_customers": 0
            },
            "by_status": {
                "prospect": 0,
                "active": 0,
                "inactive": 0,
                "blocked": 0,
                "vip": 0
            },
            "by_type": {
                "individual": 0,
                "business": 0,
                "government": 0,
                "non_profit": 0
            },
            "financial_metrics": {
                "total_order_value": 0.0,
                "average_order_value": 0.0,
                "total_outstanding": 0.0,
                "customers_over_credit_limit": 0
            },
            "top_customers": [],  # Top customers by order value
            "acquisition_trends": []  # Customer acquisition over time
        }
    
    # Validation overrides
    
    def validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validate customer creation data."""
        required_fields = ['name']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Field '{field}' is required for customer creation")
        
        # Validate email format if provided
        if 'email' in data and data['email']:
            # Would implement email validation
            pass
        
        # Validate credit limit
        if 'credit_limit' in data and data['credit_limit'] is not None:
            if data['credit_limit'] < 0:
                raise ValueError("Credit limit cannot be negative")
    
    def validate_update_data(self, data: Dict[str, Any], customer: Customer) -> None:
        """Validate customer update data."""
        # Don't allow changing customer number
        if 'customer_number' in data and data['customer_number'] != customer.customer_number:
            raise ValueError("Customer number cannot be changed after creation")
        
        # Validate credit limit changes
        if 'credit_limit' in data and data['credit_limit'] is not None:
            if data['credit_limit'] < 0:
                raise ValueError("Credit limit cannot be negative")
    
    # Lifecycle hooks
    
    def after_create(self, customer: Customer, user_id: int = None) -> None:
        """Post-creation customer setup."""
        # In production, might:
        # - Send welcome email
        # - Create default contacts/addresses
        # - Set up customer portal access
        # - Trigger CRM workflows
        pass
    
    def generate_customer_number(self, prefix: str = "CUST") -> str:
        """Generate unique customer number."""
        return self.generate_number(prefix, "customer_sequence")