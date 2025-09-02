"""Simple JWT authentication middleware."""

import jwt
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode a JWT token with verification."""
    try:
        # Verify the token signature using the service secret key
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check if token is expired
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            if datetime.utcnow().timestamp() > exp_timestamp:
                logger.warning("Token is expired")
                return None
        
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token signature has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        return None
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
        "email": payload.get("email", f"user_{payload.get('user_id', 'unknown')}@m-erp.com"),
        "permissions": payload.get("permissions", []),
        "is_active": True
    }
    
    logger.debug(f"Extracted user data: {user_data}")
    return user_data