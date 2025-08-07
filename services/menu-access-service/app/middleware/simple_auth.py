"""Simple JWT authentication middleware."""

import jwt
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# This should match the secret in user-auth-service
JWT_SECRET = "your-secret-key-here"  # In production, use environment variable
JWT_ALGORITHM = "HS256"


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode a JWT token without verification (for development)."""
    try:
        # For development, we'll decode without verification
        # In production, you should verify the signature
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Check if token is expired
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            if datetime.utcnow().timestamp() > exp_timestamp:
                logger.warning("Token is expired")
                return None
        
        return payload
    except Exception as e:
        logger.error(f"Error decoding JWT token: {str(e)}")
        return None


async def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """Extract user information from JWT token."""
    payload = decode_jwt_token(token)
    if not payload:
        return None
    
    # Extract user information from token payload
    user_data = {
        "user_id": payload.get("user_id"),
        "email": payload.get("email", "unknown"),
        "permissions": payload.get("permissions", []),
        "is_active": True
    }
    
    return user_data