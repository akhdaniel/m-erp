"""Menu schemas for API request/response validation."""
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field

# Define MenuItemType here since it's not in the model
MenuItemType = Literal["link", "divider", "header", "dropdown"]


class MenuItemBase(BaseModel):
    """Base menu item schema with common fields."""
    code: str = Field(..., description="Unique menu item code")
    title: str = Field(..., description="Display title for the menu item")
    description: Optional[str] = Field(None, description="Menu item description")
    url: Optional[str] = Field(None, description="Target URL for the menu item")
    external_url: Optional[bool] = Field(False, description="Whether URL is external")
    icon: Optional[str] = Field(None, description="Icon class for the menu item")
    order_index: int = Field(0, description="Display order within parent")
    level: int = Field(0, description="Hierarchy level (0 for root)")
    is_active: bool = Field(True, description="Whether menu item is active")
    is_visible: bool = Field(True, description="Whether menu item is visible")
    required_permission: Optional[str] = Field(None, description="Permission code required to access")
    required_role_level: Optional[int] = Field(None, description="Minimum role level required")
    css_class: Optional[str] = Field(None, description="CSS class for styling")
    badge_text: Optional[str] = Field(None, description="Badge text to display")
    badge_class: Optional[str] = Field(None, description="CSS class for badge")
    target: Optional[str] = Field(None, description="Link target (_blank, _self, etc)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata", alias="metadata_info")
    item_type: MenuItemType = Field("link", description="Type of menu item")


class MenuItemCreate(MenuItemBase):
    """Schema for creating a new menu item."""
    parent_id: Optional[int] = Field(None, description="Parent menu item ID")


class MenuItemUpdate(BaseModel):
    """Schema for updating an existing menu item."""
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    external_url: Optional[bool] = None
    icon: Optional[str] = None
    order_index: Optional[int] = None
    level: Optional[int] = None
    is_active: Optional[bool] = None
    is_visible: Optional[bool] = None
    required_permission: Optional[str] = None
    required_role_level: Optional[int] = None
    css_class: Optional[str] = None
    badge_text: Optional[str] = None
    badge_class: Optional[str] = None
    target: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    item_type: Optional[MenuItemType] = None
    parent_id: Optional[int] = None


class MenuItemResponse(MenuItemBase):
    """Schema for menu item response."""
    id: int
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True


class MenuItemWithChildren(MenuItemResponse):
    """Schema for menu item with nested children."""
    children: List['MenuItemWithChildren'] = []
    
    class Config:
        from_attributes = True


class MenuTreeResponse(BaseModel):
    """Schema for the complete menu tree response."""
    menus: List[MenuItemWithChildren]
    total_items: int
    user_permissions: Optional[List[str]] = Field(None, description="User's permission codes")


class UserMenuRequest(BaseModel):
    """Schema for requesting user-specific menus."""
    user_id: Optional[int] = Field(None, description="User ID to get menus for")
    include_permissions: bool = Field(False, description="Include user permissions in response")


class MenuBulkOperation(BaseModel):
    """Schema for bulk menu operations."""
    menu_ids: List[int] = Field(..., description="List of menu item IDs")
    operation: str = Field(..., description="Operation to perform (activate, deactivate, delete)")


class MenuReorderRequest(BaseModel):
    """Schema for reordering menu items."""
    menu_id: int = Field(..., description="Menu item ID to move")
    new_order: int = Field(..., description="New order index")
    new_parent_id: Optional[int] = Field(None, description="New parent ID if changing parent")


# Update forward references for recursive models
MenuItemWithChildren.model_rebuild()