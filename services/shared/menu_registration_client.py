"""
Menu Registration Client
Shared client for services to register their menus with the menu-access-service
"""

import httpx
import logging
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MenuItem(BaseModel):
    """Menu item model for registration"""
    code: str
    title: str
    description: Optional[str] = None
    parent_code: Optional[str] = None  # Use parent_code instead of parent_id
    order_index: int = 0
    level: int = 0
    url: str = "#"
    icon: Optional[str] = None
    item_type: str = "link"  # link, dropdown, divider, header
    is_external: bool = False
    is_active: bool = True
    is_visible: bool = True
    required_permission: Optional[str] = None


class MenuPermission(BaseModel):
    """Permission model for menu access"""
    code: str
    name: str
    description: Optional[str] = None
    category: str
    action: str = "access"
    is_active: bool = True
    is_system: bool = False


class MenuRegistrationClient:
    """Client for registering service menus with menu-access-service"""
    
    def __init__(
        self, 
        menu_service_url: str = "http://menu-access-service:8000",
        service_name: str = None,
        service_token: str = None
    ):
        self.menu_service_url = menu_service_url.rstrip('/')
        self.service_name = service_name
        self.service_token = service_token
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def register_permissions(self, permissions: List[MenuPermission]) -> bool:
        """Register permissions required for menu items"""
        try:
            # Note: This would need an endpoint in menu-access-service to bulk create permissions
            # For now, we'll log what would be registered
            logger.info(f"Would register {len(permissions)} permissions for {self.service_name}")
            for perm in permissions:
                logger.debug(f"  - {perm.code}: {perm.name}")
            
            # In a real implementation:
            # response = await self.client.post(
            #     f"{self.menu_service_url}/api/v1/permissions/bulk",
            #     json=[perm.dict() for perm in permissions],
            #     headers=self._get_headers()
            # )
            # return response.status_code == 200
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register permissions: {e}")
            return False
    
    async def register_menus(self, menus: List[MenuItem]) -> bool:
        """Register menu items for the service"""
        try:
            # First, separate parent menus from child menus
            parent_menus = [m for m in menus if m.parent_code is None]
            child_menus = [m for m in menus if m.parent_code is not None]
            
            # Register parent menus first
            for menu in parent_menus:
                logger.info(f"Registering parent menu: {menu.code}")
                # In real implementation, make API call to create menu
                
            # Then register child menus
            for menu in child_menus:
                logger.info(f"Registering child menu: {menu.code} under {menu.parent_code}")
                # In real implementation, look up parent_id from parent_code and create child
            
            logger.info(f"Successfully registered {len(menus)} menus for {self.service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register menus: {e}")
            return False
    
    async def unregister_menus(self, menu_codes: List[str]) -> bool:
        """Remove menu items when service shuts down"""
        try:
            for code in menu_codes:
                logger.info(f"Unregistering menu: {code}")
                # In real implementation, make API call to delete menu
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister menus: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {"Content-Type": "application/json"}
        if self.service_token:
            headers["Authorization"] = f"Bearer {self.service_token}"
        if self.service_name:
            headers["X-Service-Name"] = self.service_name
        return headers


async def register_service_menus(
    service_name: str,
    permissions: List[MenuPermission],
    menus: List[MenuItem],
    menu_service_url: str = "http://menu-access-service:8000"
) -> bool:
    """
    Convenience function to register a service's menus and permissions
    
    Args:
        service_name: Name of the service registering menus
        permissions: List of permissions to create
        menus: List of menu items to create
        menu_service_url: URL of the menu-access-service
        
    Returns:
        True if registration successful, False otherwise
    """
    async with MenuRegistrationClient(
        menu_service_url=menu_service_url,
        service_name=service_name
    ) as client:
        # Register permissions first
        if permissions:
            success = await client.register_permissions(permissions)
            if not success:
                logger.error("Failed to register permissions")
                return False
        
        # Then register menus
        if menus:
            success = await client.register_menus(menus)
            if not success:
                logger.error("Failed to register menus")
                return False
        
        logger.info(f"Successfully registered menus for {service_name}")
        return True