"""Menu API router."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.services.menu import MenuService
from app.schemas.menu import (
    MenuItemCreate, MenuItemUpdate, MenuItemResponse,
    MenuItemWithChildren, MenuTreeResponse, UserMenuRequest,
    MenuBulkOperation, MenuReorderRequest
)
from app.core.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/menus", tags=["menus"])


@router.get("/tree", response_model=MenuTreeResponse)
async def get_menu_tree(
    request: Request,
    db: AsyncSession = Depends(get_db),
    include_permissions: bool = Query(False, description="Include user permissions in response"),
    active_only: bool = Query(True, description="Only show active menu items")
):
    """Get the complete menu tree for the current user."""
    # Get current user from request
    current_user = request.state.user
    
    service = MenuService(db)
    
    # Get user permissions
    user_permissions = []
    user_role_level = None
    
    if current_user:
        # Get user's permissions from the user data (already resolved by auth service)
        user_permissions = current_user.get('permissions', [])
        user_role_level = current_user.get('role_level', None)
        logger.info(f"User {current_user.get('email', 'unknown')} has permissions: {user_permissions}")
    else:
        logger.info("No authenticated user")
    
    # Get all menus or user-specific menus
    if current_user:
        menus = await service.get_user_menus(user_permissions, user_role_level)
        # Build hierarchical tree with permission filtering
        menu_tree = await service.build_menu_tree(menus, user_permissions, user_role_level)
    else:
        # For unauthenticated requests, return public menus only
        menus = await service.get_all_menus(active_only=active_only)
        # Filter to only show menus without required permissions
        public_menus = [m for m in menus if not m.required_permission]
        # Build tree without permission filtering
        menu_tree = await service.build_menu_tree(public_menus)
    
    response = MenuTreeResponse(
        menus=menu_tree,
        total_items=len(menus)
    )
    
    if include_permissions:
        response.user_permissions = user_permissions
    
    return response


@router.get("/", response_model=List[MenuItemResponse])
async def get_all_menus(
    db: AsyncSession = Depends(get_db),
    active_only: bool = Query(True, description="Only show active menu items"),
    level: Optional[int] = Query(None, description="Filter by menu level"),
    parent_id: Optional[int] = Query(None, description="Filter by parent ID")
):
    """Get all menu items (flat list)."""
    service = MenuService(db)
    menus = await service.get_all_menus(active_only=active_only)
    
    # Apply filters
    if level is not None:
        menus = [m for m in menus if m.level == level]
    
    if parent_id is not None:
        menus = [m for m in menus if m.parent_id == parent_id]
    
    return menus


@router.get("/{menu_id}", response_model=MenuItemResponse)
async def get_menu_item(
    menu_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific menu item by ID."""
    service = MenuService(db)
    menu = await service.get_menu_item(menu_id)
    
    if not menu:
        raise HTTPException(status_code=404, detail=f"Menu item {menu_id} not found")
    
    return menu


@router.get("/code/{code}", response_model=MenuItemResponse)
async def get_menu_by_code(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific menu item by code."""
    service = MenuService(db)
    menu = await service.get_menu_item_by_code(code)
    
    if not menu:
        raise HTTPException(status_code=404, detail=f"Menu item with code '{code}' not found")
    
    return menu


@router.post("/", response_model=MenuItemResponse)
async def create_menu_item(
    menu_data: MenuItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new menu item."""
    service = MenuService(db)
    
    try:
        menu = await service.create_menu_item(menu_data)
        return menu
    except BadRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{menu_id}", response_model=MenuItemResponse)
async def update_menu_item(
    menu_id: int,
    menu_data: MenuItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing menu item."""
    service = MenuService(db)
    
    try:
        menu = await service.update_menu_item(menu_id, menu_data)
        return menu
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{menu_id}")
async def delete_menu_item(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a menu item and its children."""
    service = MenuService(db)
    
    try:
        await service.delete_menu_item(menu_id)
        return {"message": f"Menu item {menu_id} deleted successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/reorder", response_model=MenuItemResponse)
async def reorder_menu_item(
    reorder_data: MenuReorderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reorder a menu item or move it to a different parent."""
    service = MenuService(db)
    
    try:
        menu = await service.reorder_menu_item(
            reorder_data.menu_id,
            reorder_data.new_order,
            reorder_data.new_parent_id
        )
        return menu
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/bulk/status")
async def bulk_update_status(
    bulk_data: MenuBulkOperation,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Bulk update menu items status."""
    service = MenuService(db)
    
    if bulk_data.operation not in ["activate", "deactivate"]:
        raise HTTPException(
            status_code=400, 
            detail="Operation must be 'activate' or 'deactivate'"
        )
    
    is_active = bulk_data.operation == "activate"
    updated_menus = await service.bulk_update_status(bulk_data.menu_ids, is_active)
    
    return {
        "message": f"Successfully {bulk_data.operation}d {len(updated_menus)} menu items",
        "updated_ids": [m.id for m in updated_menus]
    }


@router.get("/statistics/summary")
async def get_menu_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get menu statistics summary."""
    service = MenuService(db)
    stats = await service.get_menu_statistics()
    return stats


@router.post("/user/menus", response_model=MenuTreeResponse)
async def get_user_specific_menus(
    request_data: UserMenuRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get menu tree for a specific user (admin only)."""
    # This endpoint could be used by admins to preview what menus a user would see
    # For now, we'll implement it similarly to the main tree endpoint
    service = MenuService(db)
    
    # If user_id is provided, we would fetch that user's permissions
    # For now, use current user's permissions
    user_permissions = []
    user_role_level = None
    
    if current_user:
        user_permissions = current_user.get('permissions', [])
        user_role_level = current_user.get('role_level', None)
    
    menus = await service.get_user_menus(user_permissions, user_role_level)
    menu_tree = await service.build_menu_tree(menus, user_permissions, user_role_level)
    
    response = MenuTreeResponse(
        menus=menu_tree,
        total_items=len(menus)
    )
    
    if request_data.include_permissions:
        response.user_permissions = user_permissions
    
    return response