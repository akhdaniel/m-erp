"""
Database models for the Menu & Access Rights Service.
"""

from .base import BaseModel
from .permission import Permission
from .role import Role, role_permissions
from .menu import MenuItem

__all__ = [
    "BaseModel",
    "Permission",
    "Role",
    "role_permissions",
    "MenuItem",
]