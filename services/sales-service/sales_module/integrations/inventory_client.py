"""
Inventory service integration client for sales module.

Provides integration with the inventory service for product information,
availability checks, and stock reservations.
"""

import requests
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class InventoryServiceClient:
    """
    Client for integrating with the inventory service.
    
    Handles product lookups, availability checks, stock reservations,
    and pricing information retrieval.
    """
    
    def __init__(self, base_url: str = "http://localhost:8005", timeout: int = 30):
        """
        Initialize inventory service client.
        
        Args:
            base_url: Base URL of inventory service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_product_by_id(self, product_id: int, company_id: int) -> Optional[Dict[str, Any]]:
        """
        Get product information by ID.
        
        Args:
            product_id: Product ID
            company_id: Company ID for isolation
            
        Returns:
            Product information dictionary or None if not found
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/products/{product_id}",
                params={"company_id": company_id},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error fetching product {product_id}: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Network error fetching product {product_id}: {e}")
            return None
    
    def check_product_availability(self, product_id: int, quantity: Decimal, 
                                 company_id: int, warehouse_id: int = None) -> Dict[str, Any]:
        """
        Check product availability for given quantity.
        
        Args:
            product_id: Product ID
            quantity: Required quantity
            company_id: Company ID for isolation
            warehouse_id: Optional warehouse ID for location-specific check
            
        Returns:
            Availability information dictionary
        """
        try:
            params = {
                "company_id": company_id,
                "quantity": str(quantity)
            }
            if warehouse_id:
                params["warehouse_id"] = warehouse_id
            
            response = self.session.get(
                f"{self.base_url}/api/v1/stock/availability/{product_id}",
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error checking availability for product {product_id}: {response.status_code}")
                return {
                    "available": False,
                    "available_quantity": 0,
                    "error": f"Service error: {response.status_code}"
                }
                
        except requests.RequestException as e:
            logger.error(f"Network error checking availability for product {product_id}: {e}")
            return {
                "available": False,
                "available_quantity": 0,
                "error": f"Network error: {str(e)}"
            }
    
    def get_product_pricing(self, product_id: int, company_id: int, 
                           customer_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Get product pricing information.
        
        Args:
            product_id: Product ID
            company_id: Company ID for isolation
            customer_id: Optional customer ID for customer-specific pricing
            
        Returns:
            Pricing information dictionary or None if not found
        """
        try:
            params = {"company_id": company_id}
            if customer_id:
                params["customer_id"] = customer_id
            
            response = self.session.get(
                f"{self.base_url}/api/v1/products/{product_id}/pricing",
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error fetching pricing for product {product_id}: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Network error fetching pricing for product {product_id}: {e}")
            return None
    
    def reserve_stock(self, product_id: int, quantity: Decimal, 
                     reference_type: str, reference_id: int, company_id: int,
                     warehouse_id: int = None, expiry_hours: int = 24) -> Dict[str, Any]:
        """
        Reserve stock for a quote or order.
        
        Args:
            product_id: Product ID
            quantity: Quantity to reserve
            reference_type: Type of reference (quote, order, etc.)
            reference_id: Reference entity ID
            company_id: Company ID for isolation
            warehouse_id: Optional warehouse ID
            expiry_hours: Hours until reservation expires
            
        Returns:
            Reservation result dictionary
        """
        try:
            data = {
                "product_id": product_id,
                "quantity": str(quantity),
                "reference_type": reference_type,
                "reference_id": reference_id,
                "company_id": company_id,
                "expiry_hours": expiry_hours
            }
            if warehouse_id:
                data["warehouse_id"] = warehouse_id
            
            response = self.session.post(
                f"{self.base_url}/api/v1/stock/reservations",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error reserving stock for product {product_id}: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Service error: {response.status_code}"
                }
                
        except requests.RequestException as e:
            logger.error(f"Network error reserving stock for product {product_id}: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
    
    def release_stock_reservation(self, reservation_id: int, company_id: int) -> Dict[str, Any]:
        """
        Release a stock reservation.
        
        Args:
            reservation_id: Reservation ID
            company_id: Company ID for isolation
            
        Returns:
            Release result dictionary
        """
        try:
            response = self.session.delete(
                f"{self.base_url}/api/v1/stock/reservations/{reservation_id}",
                params={"company_id": company_id},
                timeout=self.timeout
            )
            
            if response.status_code in [200, 204]:
                return {"success": True}
            else:
                logger.error(f"Error releasing reservation {reservation_id}: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Service error: {response.status_code}"
                }
                
        except requests.RequestException as e:
            logger.error(f"Network error releasing reservation {reservation_id}: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
    
    def get_stock_levels(self, product_ids: List[int], company_id: int) -> Dict[int, Dict[str, Any]]:
        """
        Get stock levels for multiple products.
        
        Args:
            product_ids: List of product IDs
            company_id: Company ID for isolation
            
        Returns:
            Dictionary mapping product IDs to stock level information
        """
        try:
            data = {
                "product_ids": product_ids,
                "company_id": company_id
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/stock/levels/bulk",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching stock levels: {response.status_code}")
                return {}
                
        except requests.RequestException as e:
            logger.error(f"Network error fetching stock levels: {e}")
            return {}
    
    def health_check(self) -> bool:
        """
        Check if inventory service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5  # Short timeout for health check
            )
            return response.status_code == 200
        except requests.RequestException:
            return False


# Singleton instance for dependency injection
inventory_client = InventoryServiceClient()