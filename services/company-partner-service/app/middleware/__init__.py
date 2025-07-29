"""
Middleware package for authentication and other middleware.
"""

from .auth import auth_client, get_current_user, get_current_active_user, verify_company_access

__all__ = [
    "auth_client",
    "get_current_user", 
    "get_current_active_user",
    "verify_company_access",
]