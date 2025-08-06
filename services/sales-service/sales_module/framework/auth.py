"""
Authentication and authorization for Sales Service.

Provides user and company identification for API endpoints
with multi-company data isolation.
"""

from typing import Optional
from fastapi import HTTPException, Header, Depends
import jwt
import os

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def get_current_user_id(
    authorization: Optional[str] = Header(None)
) -> int:
    """
    Extract user ID from JWT token.
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        int: Current user ID
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        # For development/testing, return default user ID
        return int(os.getenv("DEFAULT_USER_ID", "1"))
    
    try:
        # Extract token from "Bearer <token>" format
        token = authorization.replace("Bearer ", "")
        
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")
        
        return int(user_id)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user_id in token")


def get_current_company_id(
    authorization: Optional[str] = Header(None),
    x_company_id: Optional[str] = Header(None)
) -> int:
    """
    Extract company ID from headers for multi-company isolation.
    
    Args:
        authorization: Authorization header with Bearer token
        x_company_id: Company ID header override
        
    Returns:
        int: Current company ID
        
    Raises:
        HTTPException: If company ID cannot be determined
    """
    # Check for explicit company ID header first
    if x_company_id:
        try:
            return int(x_company_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid company ID format")
    
    # Try to extract from JWT token
    if authorization:
        try:
            token = authorization.replace("Bearer ", "")
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            company_id = payload.get("company_id")
            
            if company_id:
                return int(company_id)
                
        except (jwt.InvalidTokenError, ValueError):
            pass
    
    # For development/testing, return default company ID
    default_company_id = os.getenv("DEFAULT_COMPANY_ID", "1")
    return int(default_company_id)


def get_user_permissions(user_id: int = Depends(get_current_user_id)) -> dict:
    """
    Get user permissions for authorization checks.
    
    Args:
        user_id: Current user ID
        
    Returns:
        dict: User permissions dictionary
    """
    # In production, would fetch from user service or cache
    # For now, return full permissions for development
    return {
        "can_create_orders": True,
        "can_edit_orders": True,
        "can_cancel_orders": True,
        "can_confirm_orders": True,
        "can_ship_orders": True,
        "can_create_invoices": True,
        "can_record_payments": True,
        "can_view_all_orders": True,
        "can_manage_inventory": True
    }