"""
Menu Registration Client
Shared client for services to register their menus with the menu-access-service
"""

import httpx
import logging
import os
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
        menu_service_url: str = "http://menu-access-service:8003",
        service_name: str = None,
        service_token: str = None
    ):
        self.menu_service_url = menu_service_url.rstrip('/')
        self.service_name = service_name or os.getenv("SERVICE_NAME")
        self.service_key = os.getenv("SERVICE_KEY")
        self.service_secret = os.getenv("SERVICE_SECRET")
        self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://user-auth-service:8000")
        self.service_token = service_token
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def _get_service_token(self) -> Optional[str]:
        """Get service token from auth service for authentication"""
        if self.service_token:
            logger.debug(f"Using provided service token for {self.service_name}")
            return self.service_token
            
        if not self.service_name or not self.service_key or not self.service_secret:
            logger.warning(f"Missing service credentials for {self.service_name}: name={self.service_name}, key={bool(self.service_key)}, secret={bool(self.service_secret)}")
            return None
            
        try:
            logger.debug(f"Getting service token for {self.service_name} from {self.auth_service_url}")
            auth_data = {
                "service_name": self.service_name,
                "service_key": self.service_key,
                "service_secret": self.service_secret
            }
            
            response = await self.client.post(
                f"{self.auth_service_url}/api/services/token",
                json=auth_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.service_token = data.get("access_token")
                logger.info(f"Service token obtained for {self.service_name}")
                logger.debug(f"Token scopes: {data.get('scopes', [])}")
                return self.service_token
            else:
                logger.error(f"Failed to get service token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting service token: {str(e)}")
            return None
    
    async def register_permissions(self, permissions: List[MenuPermission]) -> bool:
        """Register permissions required for menu items"""
        try:
            if not permissions:
                logger.info(f"No permissions to register for {self.service_name}")
                return True
            
            logger.info(f"Registering {len(permissions)} permissions for {self.service_name}")
            for perm in permissions:
                logger.debug(f"  - {perm.code}: {perm.name}")
            
            # Make API call to register permissions
            # Note: For now, we'll just log them as the menu-access-service doesn't have a specific
            # permissions registration endpoint. Permissions are typically associated with menu items.
            logger.info(f"Permissions would be registered with menu items for {self.service_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register permissions: {e}")
            return False
    
    async def register_menus(self, menus: List[MenuItem]) -> bool:
        """Register menu items for the service"""
        try:
            if not menus:
                logger.info(f"No menus to register for {self.service_name}")
                return True
            
            logger.info(f"Registering {len(menus)} menus for {self.service_name}")
            
            # Get service token for authentication
            service_token = await self._get_service_token()
            if not service_token:
                logger.error(f"Unable to obtain service token for {self.service_name}")
                return False
            
            logger.debug(f"Using service token for {self.service_name}: {service_token[:20]}...")
            
            # Register all menus - the menu service will handle parent-child relationships
            registered_menus = []
            failed_menus = []
            
            # First, register all menus to ensure they exist (this handles creation/update)
            menu_responses = {}
            for menu in menus:
                try:
                    # Convert MenuItem to dict for API call
                    menu_dict = menu.model_dump()
                    
                    # Remove parent_code as it's not in the API schema (we'll handle it later)
                    menu_dict.pop('parent_code', None)
                    
                    # Add service token to headers for authentication
                    headers = self._get_headers()
                    headers["Authorization"] = f"Bearer {service_token}"
                    logger.debug(f"Making POST request to {self.menu_service_url}/ with headers: {list(headers.keys())}")
                    
                    # Make API call to create/update menu
                    response = await self.client.post(
                        f"{self.menu_service_url}/",
                        json=menu_dict,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201]:
                        menu_data = response.json()
                        menu_responses[menu.code] = menu_data
                        logger.info(f"Successfully registered menu: {menu.code}")
                    else:
                        failed_menus.append((menu.code, response.status_code, response.text))
                        logger.error(f"Failed to register menu {menu.code}: {response.status_code} - {response.text}")
                        
                except Exception as e:
                    failed_menus.append((menu.code, str(e)))
                    logger.error(f"Exception while registering menu {menu.code}: {e}")
            
            # Now handle parent-child relationships
            for menu in menus:
                if menu.code not in menu_responses:
                    continue  # Skip if menu registration failed
                    
                try:
                    menu_data = menu_responses[menu.code]
                    menu_id = menu_data['id']
                    
                    # Handle parent_code to parent_id conversion
                    if menu.parent_code:
                        # First, try to find the parent menu by code
                        parent_response = await self.client.get(
                            f"{self.menu_service_url}/code/{menu.parent_code}",
                            headers=self._get_headers()
                        )
                        
                        if parent_response.status_code == 200:
                            parent_data = parent_response.json()
                            parent_id = parent_data['id']
                            
                            # Update the menu item with the parent_id if it's different
                            # Use the reorder endpoint which properly handles parent changes
                            if menu_data.get('parent_id') != parent_id:
                                reorder_data = {
                                    "menu_id": menu_id,
                                    "new_order": menu.order_index,
                                    "new_parent_id": parent_id
                                }
                                update_response = await self.client.post(
                                    f"{self.menu_service_url}/reorder",
                                    json=reorder_data,
                                    headers=headers
                                )
                                
                                if update_response.status_code not in [200, 201]:
                                    logger.warning(f"Failed to update parent for menu {menu.code}: {update_response.status_code} - {update_response.text}")
                        else:
                            logger.warning(f"Parent menu {menu.parent_code} not found for {menu.code}")
                    
                    registered_menus.append(menu.code)
                        
                except Exception as e:
                    logger.error(f"Exception while updating parent for menu {menu.code}: {e}")
            
            logger.info(f"Successfully registered {len(registered_menus)} menus for {self.service_name}")
            
            if failed_menus:
                logger.warning(f"Failed to register {len(failed_menus)} menus: {failed_menus}")
                # If all menus failed, return False
                if len(failed_menus) == len(menus):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register menus: {e}")
            return False
    
    async def unregister_menus(self, menu_codes: List[str]) -> bool:
        """Remove menu items when service shuts down"""
        try:
            if not menu_codes:
                logger.info(f"No menus to unregister for {self.service_name}")
                return True
            
            logger.info(f"Unregistering {len(menu_codes)} menus for {self.service_name}")
            
            # Get service token for authentication
            service_token = await self._get_service_token()
            if not service_token:
                logger.error(f"Unable to obtain service token for {self.service_name}")
                return False
            
            # Add service token to headers for authentication
            auth_headers = self._get_headers()
            auth_headers["Authorization"] = f"Bearer {service_token}"
            
            unregistered_menus = []
            failed_menus = []
            
            for code in menu_codes:
                try:
                    # First, find the menu by code to get its ID
                    response = await self.client.get(
                        f"{self.menu_service_url}/menus/code/{code}",
                        headers=auth_headers
                    )
                    
                    if response.status_code == 200:
                        menu_data = response.json()
                        menu_id = menu_data['id']
                        
                        # Now delete the menu by ID
                        delete_response = await self.client.delete(
                            f"{self.menu_service_url}/menus/{menu_id}",
                            headers=auth_headers
                        )
                        
                        if delete_response.status_code in [200, 204]:
                            unregistered_menus.append(code)
                            logger.info(f"Successfully unregistered menu: {code}")
                        else:
                            failed_menus.append((code, delete_response.status_code, delete_response.text))
                            logger.error(f"Failed to unregister menu {code}: {delete_response.status_code} - {delete_response.text}")
                    else:
                        logger.warning(f"Menu {code} not found for unregistration")
                        
                except Exception as e:
                    failed_menus.append((code, str(e)))
                    logger.error(f"Exception while unregistering menu {code}: {e}")
            
            logger.info(f"Successfully unregistered {len(unregistered_menus)} menus for {self.service_name}")
            
            if failed_menus:
                logger.warning(f"Failed to unregister {len(failed_menus)} menus: {failed_menus}")
                
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
    menu_service_url: str = "http://menu-access-service:8003"
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