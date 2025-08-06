"""
Role Management API endpoints for managing system roles and permissions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Annotated, List, Optional

from app.core.database import get_db
from app.models.role import Role, UserRole
from app.models.user import User
from app.routers.auth import get_admin_user, CurrentUser
from app.schemas.auth import MessageResponse


# Role-specific schemas
from pydantic import BaseModel, Field


class RoleResponse(BaseModel):
    """Schema for role response."""
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[str]
    user_count: int = Field(..., description="Number of users with this role")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "sales_manager",
                "description": "Sales Manager with full sales access",
                "permissions": ["access_sales", "manage_sales", "manage_quotes"],
                "user_count": 5
            }
        }
    }


class RoleListResponse(BaseModel):
    """Schema for role list response."""
    roles: List[RoleResponse]
    total: int


class CreateRoleRequest(BaseModel):
    """Schema for creating a new role."""
    name: str = Field(..., min_length=1, max_length=50, description="Role name (unique)")
    description: Optional[str] = Field(None, max_length=255, description="Role description")
    permissions: List[str] = Field(..., description="List of permissions")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "custom_role",
                "description": "Custom role for specific needs",
                "permissions": ["view_profile", "edit_profile"]
            }
        }
    }


class UpdateRoleRequest(BaseModel):
    """Schema for updating an existing role."""
    description: Optional[str] = Field(None, max_length=255, description="Role description")
    permissions: Optional[List[str]] = Field(None, description="List of permissions")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "description": "Updated role description",
                "permissions": ["view_profile", "edit_profile", "access_reports"]
            }
        }
    }


class PermissionsListResponse(BaseModel):
    """Schema for available permissions list."""
    permissions: List[str]
    categories: dict = Field(..., description="Permissions organized by category")


# Available permissions organized by category
AVAILABLE_PERMISSIONS = {
    "User Management": [
        "manage_users",
        "view_users"
    ],
    "Role Management": [
        "manage_roles"
    ],
    "System Management": [
        "manage_system",
        "access_admin_dashboard"
    ],
    "Audit and Logs": [
        "view_audit_logs"
    ],
    "Company Management": [
        "manage_companies",
        "view_companies"
    ],
    "Partner Management": [
        "manage_partners",
        "view_partners"
    ],
    "Currency Management": [
        "manage_currencies"
    ],
    "Profile Management": [
        "view_profile",
        "edit_profile"
    ],
    "Inventory Management": [
        "access_inventory",
        "manage_inventory",
        "manage_products",
        "manage_stock",
        "manage_warehouses",
        "view_inventory_reports",
        "view_products",
        "view_stock",
        "view_warehouses"
    ],
    "Sales Management": [
        "access_sales",
        "manage_sales",
        "manage_quotes",
        "manage_orders",
        "view_sales_reports",
        "view_quotes",
        "view_orders"
    ],
    "Purchase Management": [
        "access_purchase",
        "manage_purchase",
        "manage_purchase_orders",
        "manage_suppliers",
        "view_purchase_reports",
        "view_purchase_orders",
        "view_suppliers"
    ],
    "Accounting": [
        "access_accounting",
        "manage_accounting",
        "manage_accounts",
        "manage_journals",
        "view_financial_reports"
    ],
    "Reporting": [
        "view_reports"
    ]
}


router = APIRouter(prefix="/api/roles", tags=["Role Management"])


@router.get(
    "/",
    response_model=RoleListResponse,
    summary="List all roles",
    description="Get list of all system roles with user counts"
)
async def list_roles(
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    List all system roles with user counts.
    
    Requires admin permissions (manage_users).
    """
    if "manage_roles" not in admin_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role management permissions required"
        )
    
    # Get all roles
    stmt = select(Role).order_by(Role.name)
    result = await db.execute(stmt)
    roles = result.scalars().all()
    
    # Get user count for each role
    role_responses = []
    for role in roles:
        # Count users with this role
        count_stmt = select(func.count(UserRole.user_id)).where(UserRole.role_id == role.id)
        count_result = await db.execute(count_stmt)
        user_count = count_result.scalar() or 0
        
        role_response = RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=role.permissions,
            user_count=user_count
        )
        role_responses.append(role_response)
    
    return RoleListResponse(
        roles=role_responses,
        total=len(role_responses)
    )


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Get role by ID",
    description="Get detailed information about a specific role"
)
async def get_role_by_id(
    role_id: int,
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get detailed information about a specific role.
    
    - **role_id**: Role ID to retrieve
    
    Requires admin permissions (manage_users).
    """
    if "manage_roles" not in admin_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role management permissions required"
        )
    
    # Get role
    stmt = select(Role).where(Role.id == role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Count users with this role
    count_stmt = select(func.count(UserRole.user_id)).where(UserRole.role_id == role.id)
    count_result = await db.execute(count_stmt)
    user_count = count_result.scalar() or 0
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=role.permissions,
        user_count=user_count
    )


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new role",
    description="Create a new system role with permissions"
)
async def create_role(
    role_data: CreateRoleRequest,
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Create a new system role.
    
    - **name**: Unique role name (required)
    - **description**: Role description (optional)
    - **permissions**: List of permissions for this role
    
    Requires admin permissions (manage_roles).
    """
    if "manage_roles" not in admin_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role management permissions required"
        )
    
    # Check if role name already exists
    existing_stmt = select(Role).where(Role.name == role_data.name)
    existing_result = await db.execute(existing_stmt)
    existing_role = existing_result.scalar_one_or_none()
    
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )
    
    # Validate permissions against available ones
    all_permissions = [perm for category in AVAILABLE_PERMISSIONS.values() for perm in category]
    invalid_permissions = [perm for perm in role_data.permissions if perm not in all_permissions]
    
    if invalid_permissions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permissions: {', '.join(invalid_permissions)}"
        )
    
    # Create new role
    new_role = Role(
        name=role_data.name,
        description=role_data.description,
        permissions=role_data.permissions
    )
    
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    
    return RoleResponse(
        id=new_role.id,
        name=new_role.name,
        description=new_role.description,
        permissions=new_role.permissions,
        user_count=0
    )


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Update role",
    description="Update an existing role's description and permissions"
)
async def update_role(
    role_id: int,
    role_data: UpdateRoleRequest,
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update an existing role.
    
    - **role_id**: Role ID to update
    - **description**: New role description (optional)
    - **permissions**: New list of permissions (optional)
    
    Requires admin permissions (manage_roles).
    Note: Role name cannot be changed to prevent breaking references.
    """
    if "manage_roles" not in admin_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role management permissions required"
        )
    
    # Get role
    stmt = select(Role).where(Role.id == role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Check if this is a system role that shouldn't be modified
    system_roles = ["superuser", "admin"]
    if role.name in system_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot modify system role '{role.name}'"
        )
    
    # Update fields if provided
    if role_data.description is not None:
        role.description = role_data.description
    
    if role_data.permissions is not None:
        # Validate permissions against available ones
        all_permissions = [perm for category in AVAILABLE_PERMISSIONS.values() for perm in category]
        invalid_permissions = [perm for perm in role_data.permissions if perm not in all_permissions]
        
        if invalid_permissions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid permissions: {', '.join(invalid_permissions)}"
            )
        
        role.permissions = role_data.permissions
    
    await db.commit()
    await db.refresh(role)
    
    # Count users with this role
    count_stmt = select(func.count(UserRole.user_id)).where(UserRole.role_id == role.id)
    count_result = await db.execute(count_stmt)
    user_count = count_result.scalar() or 0
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=role.permissions,
        user_count=user_count
    )


@router.delete(
    "/{role_id}",
    response_model=MessageResponse,
    summary="Delete role",
    description="Delete a role (only if no users are assigned to it)"
)
async def delete_role(
    role_id: int,
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete a role.
    
    - **role_id**: Role ID to delete
    
    Can only delete roles that have no users assigned.
    System roles (superuser, admin) cannot be deleted.
    
    Requires admin permissions (manage_roles).
    """
    if "manage_roles" not in admin_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role management permissions required"
        )
    
    # Get role
    stmt = select(Role).where(Role.id == role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Check if this is a system role that shouldn't be deleted
    system_roles = ["superuser", "admin", "user", "readonly"]
    if role.name in system_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete system role '{role.name}'"
        )
    
    # Check if any users have this role
    count_stmt = select(func.count(UserRole.user_id)).where(UserRole.role_id == role.id)
    count_result = await db.execute(count_stmt)
    user_count = count_result.scalar() or 0
    
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role. {user_count} user(s) are assigned to this role. Remove role assignments first."
        )
    
    # Delete role
    await db.delete(role)
    await db.commit()
    
    return MessageResponse(
        message=f"Successfully deleted role '{role.name}'"
    )


@router.get(
    "/{role_id}/users",
    summary="Get users with specific role",
    description="Get list of users assigned to a specific role"
)
async def get_role_users(
    role_id: int,
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    per_page: int = 20
):
    """
    Get list of users assigned to a specific role.
    
    - **role_id**: Role ID to get users for
    - **page**: Page number (starts from 1)
    - **per_page**: Number of users per page (max 100)
    
    Requires admin permissions (manage_users).
    """
    if "manage_roles" not in admin_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role management permissions required"
        )
    
    # Verify role exists
    role_stmt = select(Role).where(Role.id == role_id)
    role_result = await db.execute(role_stmt)
    role = role_result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Limit per_page to reasonable bounds
    per_page = min(max(per_page, 1), 100)
    offset = (page - 1) * per_page
    
    # Get users with this role
    users_stmt = (
        select(User)
        .join(UserRole)
        .where(UserRole.role_id == role_id)
        .offset(offset)
        .limit(per_page)
        .order_by(User.email)
    )
    users_result = await db.execute(users_stmt)
    users = users_result.scalars().all()
    
    # Get total count
    count_stmt = select(func.count(User.id)).join(UserRole).where(UserRole.role_id == role_id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0
    
    # Format users
    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "created_at": user.created_at
        })
    
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "role_id": role_id,
        "role_name": role.name,
        "users": user_list,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


@router.get(
    "/permissions/available",
    response_model=PermissionsListResponse,
    summary="Get available permissions",
    description="Get list of all available permissions organized by category"
)
async def get_available_permissions(
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)]
):
    """
    Get list of all available permissions organized by category.
    
    Requires admin permissions (manage_roles).
    """
    if "manage_roles" not in admin_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role management permissions required"
        )
    
    # Flatten permissions list
    all_permissions = []
    for category_permissions in AVAILABLE_PERMISSIONS.values():
        all_permissions.extend(category_permissions)
    
    return PermissionsListResponse(
        permissions=sorted(all_permissions),
        categories=AVAILABLE_PERMISSIONS
    )