"""Menu service for business logic."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update, delete
from sqlalchemy.orm import selectinload

from app.models.menu import MenuItem
from app.models.permission import Permission
from app.models.role import Role
from app.schemas.menu import (
    MenuItemCreate, MenuItemUpdate, MenuItemResponse, 
    MenuItemWithChildren, MenuTreeResponse
)
from app.core.exceptions import NotFoundException, BadRequestException


class MenuService:
    """Service for menu operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_menu_item(self, menu_data: MenuItemCreate) -> MenuItem:
        """Create a new menu item."""
        # Check if code already exists
        existing = await self.db.execute(
            select(MenuItem).where(MenuItem.code == menu_data.code)
        )
        if existing.scalar_one_or_none():
            raise BadRequestException(f"Menu item with code '{menu_data.code}' already exists")
        
        # Validate parent if provided
        if menu_data.parent_id:
            parent = await self.get_menu_item(menu_data.parent_id)
            if not parent:
                raise NotFoundException(f"Parent menu item with ID {menu_data.parent_id} not found")
        
        # Create menu item
        menu_item = MenuItem(**menu_data.model_dump())
        self.db.add(menu_item)
        await self.db.commit()
        await self.db.refresh(menu_item)
        return menu_item
    
    async def get_menu_item(self, menu_id: int) -> Optional[MenuItem]:
        """Get a single menu item by ID."""
        result = await self.db.execute(
            select(MenuItem)
            .where(MenuItem.id == menu_id)
        )
        return result.scalar_one_or_none()
    
    async def get_menu_item_by_code(self, code: str) -> Optional[MenuItem]:
        """Get a single menu item by code."""
        result = await self.db.execute(
            select(MenuItem)
            .where(MenuItem.code == code)
        )
        return result.scalar_one_or_none()
    
    async def update_menu_item(self, menu_id: int, menu_data: MenuItemUpdate) -> MenuItem:
        """Update an existing menu item."""
        menu_item = await self.get_menu_item(menu_id)
        if not menu_item:
            raise NotFoundException(f"Menu item with ID {menu_id} not found")
        
        # Check code uniqueness if being updated
        update_data = menu_data.model_dump(exclude_unset=True)
        if 'code' in update_data and update_data['code'] != menu_item.code:
            existing = await self.db.execute(
                select(MenuItem).where(
                    and_(
                        MenuItem.code == update_data['code'],
                        MenuItem.id != menu_id
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise BadRequestException(f"Menu item with code '{update_data['code']}' already exists")
        
        # Update fields
        for field, value in update_data.items():
            setattr(menu_item, field, value)
        
        await self.db.commit()
        await self.db.refresh(menu_item)
        return menu_item
    
    async def delete_menu_item(self, menu_id: int) -> bool:
        """Delete a menu item and its children."""
        menu_item = await self.get_menu_item(menu_id)
        if not menu_item:
            raise NotFoundException(f"Menu item with ID {menu_id} not found")
        
        # Delete will cascade to children due to model configuration
        await self.db.delete(menu_item)
        await self.db.commit()
        return True
    
    async def get_all_menus(self, active_only: bool = True) -> List[MenuItem]:
        """Get all menu items."""
        query = select(MenuItem)
        if active_only:
            query = query.where(MenuItem.is_active == True)
        
        result = await self.db.execute(query.order_by(MenuItem.level, MenuItem.order_index))
        return result.scalars().all()
    
    async def get_user_menus(
        self, 
        user_permissions: List[str], 
        user_role_level: Optional[int] = None
    ) -> List[MenuItem]:
        """Get menu items accessible by a user based on permissions."""
        # Get all active menus
        all_menus = await self.get_all_menus(active_only=True)
        
        # Filter menus based on user permissions
        accessible_menus = []
        for menu in all_menus:
            if await self._can_access_menu(menu, user_permissions, user_role_level):
                accessible_menus.append(menu)
        
        return accessible_menus
    
    async def _can_access_menu(
        self, 
        menu: MenuItem, 
        user_permissions: List[str], 
        user_role_level: Optional[int]
    ) -> bool:
        """Check if a user can access a menu item."""
        # Check visibility
        if not menu.is_visible or not menu.is_active:
            return False
        
        # Check permission requirement
        if menu.required_permission and menu.required_permission not in user_permissions:
            return False
        
        # Check role level requirement
        if menu.required_role_level is not None and user_role_level is not None:
            if user_role_level > menu.required_role_level:
                return False
        
        return True
    
    async def build_menu_tree(
        self, 
        menus: List[MenuItem], 
        user_permissions: Optional[List[str]] = None,
        user_role_level: Optional[int] = None
    ) -> List[MenuItemWithChildren]:
        """Build a hierarchical menu tree from flat menu list."""
        # Create a dictionary for quick lookup
        menu_dict = {menu.id: menu for menu in menus}
        
        # Build a dictionary of children for each parent
        children_by_parent = {}
        for menu in menus:
            if menu.parent_id:
                if menu.parent_id not in children_by_parent:
                    children_by_parent[menu.parent_id] = []
                children_by_parent[menu.parent_id].append(menu)
        
        # Build the tree
        root_menus = []
        for menu in menus:
            # Skip if user doesn't have access
            if user_permissions is not None:
                if not await self._can_access_menu(menu, user_permissions, user_role_level):
                    continue
            
            if menu.parent_id is None:
                # Root menu item
                menu_with_children = await self._build_menu_with_children(
                    menu, children_by_parent, user_permissions, user_role_level
                )
                if menu_with_children:  # Only add if has accessible items
                    root_menus.append(menu_with_children)
        
        # Sort by order_index
        root_menus.sort(key=lambda x: x.order_index)
        return root_menus
    
    async def _build_menu_with_children(
        self,
        menu: MenuItem,
        children_by_parent: Dict[int, List[MenuItem]],
        user_permissions: Optional[List[str]] = None,
        user_role_level: Optional[int] = None
    ) -> Optional[MenuItemWithChildren]:
        """Build a menu item with its children."""
        # Skip if user doesn't have access
        if user_permissions is not None:
            if not await self._can_access_menu(menu, user_permissions, user_role_level):
                return None
        
        # Create menu response
        menu_data = MenuItemResponse.model_validate(menu)
        menu_with_children = MenuItemWithChildren(**menu_data.model_dump())
        
        # Add children if any
        children = []
        if menu.id in children_by_parent:
            for child in children_by_parent[menu.id]:
                child_with_children = await self._build_menu_with_children(
                    child, children_by_parent, user_permissions, user_role_level
                )
                if child_with_children:
                    children.append(child_with_children)
        
        # Sort children by order_index
        children.sort(key=lambda x: x.order_index)
        menu_with_children.children = children
        
        # For dropdown menus without accessible children, don't include them
        if menu.item_type == 'dropdown' and not children:
            return None
        
        return menu_with_children
    
    
    async def reorder_menu_item(
        self, 
        menu_id: int, 
        new_order: int, 
        new_parent_id: Optional[int] = None
    ) -> MenuItem:
        """Reorder a menu item within its parent or move to a new parent."""
        menu_item = await self.get_menu_item(menu_id)
        if not menu_item:
            raise NotFoundException(f"Menu item with ID {menu_id} not found")
        
        # If changing parent, validate new parent
        if new_parent_id is not None and new_parent_id != menu_item.parent_id:
            if new_parent_id > 0:  # Not moving to root
                new_parent = await self.get_menu_item(new_parent_id)
                if not new_parent:
                    raise NotFoundException(f"Parent menu item with ID {new_parent_id} not found")
                menu_item.parent_id = new_parent_id
                menu_item.level = new_parent.level + 1
            else:
                menu_item.parent_id = None
                menu_item.level = 0
        
        # Update order
        menu_item.order_index = new_order
        
        # Reorder siblings if needed
        siblings_query = select(MenuItem).where(
            MenuItem.parent_id == menu_item.parent_id,
            MenuItem.id != menu_id
        ).order_by(MenuItem.order_index)
        
        result = await self.db.execute(siblings_query)
        siblings = result.scalars().all()
        
        # Adjust sibling orders
        current_order = 0
        for sibling in siblings:
            if current_order == new_order:
                current_order += 1
            if sibling.order_index != current_order:
                sibling.order_index = current_order
            current_order += 1
        
        await self.db.commit()
        await self.db.refresh(menu_item)
        return menu_item
    
    async def bulk_update_status(
        self, 
        menu_ids: List[int], 
        is_active: bool
    ) -> List[MenuItem]:
        """Bulk update menu items active status."""
        result = await self.db.execute(
            update(MenuItem)
            .where(MenuItem.id.in_(menu_ids))
            .values(is_active=is_active)
            .returning(MenuItem)
        )
        updated_menus = result.scalars().all()
        await self.db.commit()
        return updated_menus
    
    async def get_menu_statistics(self) -> Dict[str, Any]:
        """Get menu statistics."""
        # Total menus
        total_result = await self.db.execute(
            select(MenuItem.id).count()
        )
        total_menus = total_result.scalar()
        
        # Active menus
        active_result = await self.db.execute(
            select(MenuItem.id).where(MenuItem.is_active == True).count()
        )
        active_menus = active_result.scalar()
        
        # Menus by type
        type_stats = {}
        for menu_type in ['link', 'dropdown', 'divider', 'header']:
            type_result = await self.db.execute(
                select(MenuItem.id).where(MenuItem.item_type == menu_type).count()
            )
            type_stats[menu_type] = type_result.scalar()
        
        # Menus by level
        level_stats = {}
        for level in range(5):  # Assuming max 5 levels
            level_result = await self.db.execute(
                select(MenuItem.id).where(MenuItem.level == level).count()
            )
            count = level_result.scalar()
            if count > 0:
                level_stats[f"level_{level}"] = count
        
        return {
            "total_menus": total_menus,
            "active_menus": active_menus,
            "inactive_menus": total_menus - active_menus,
            "by_type": type_stats,
            "by_level": level_stats
        }