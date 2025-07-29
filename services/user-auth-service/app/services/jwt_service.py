"""
JWT token service for access and refresh token management.
Handles token generation, validation, and expiration.
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List

from app.core.config import settings


class JWTService:
  """Service for handling JWT token operations."""
  
  @classmethod
  def create_access_token(
    cls, 
    user_id: int, 
    permissions: List[str],
    expires_delta: Optional[timedelta] = None
  ) -> str:
    """
    Create a JWT access token for a user.
    
    Args:
      user_id: User ID to include in token
      permissions: List of user permissions
      expires_delta: Custom expiration time (defaults to config setting)
      
    Returns:
      str: Encoded JWT token
    """
    if expires_delta is None:
      expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    
    # Use timestamp with microseconds for uniqueness
    iat_timestamp = now.timestamp()
    exp_timestamp = expire.timestamp()
    nbf_timestamp = now.timestamp()
    
    payload = {
      "user_id": user_id,
      "permissions": permissions,
      "type": "access",
      "iat": iat_timestamp,
      "exp": exp_timestamp,
      "nbf": nbf_timestamp  # Not valid before now
    }
    
    return jwt.encode(
      payload, 
      settings.secret_key, 
      algorithm=settings.algorithm
    )
  
  @classmethod
  def create_refresh_token(
    cls, 
    user_id: int,
    expires_delta: Optional[timedelta] = None
  ) -> str:
    """
    Create a JWT refresh token for a user.
    
    Args:
      user_id: User ID to include in token
      expires_delta: Custom expiration time (defaults to config setting)
      
    Returns:
      str: Encoded JWT token
    """
    if expires_delta is None:
      expires_delta = timedelta(days=settings.refresh_token_expire_days)
    
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    
    # Use timestamp with microseconds for uniqueness
    iat_timestamp = now.timestamp()
    exp_timestamp = expire.timestamp()
    nbf_timestamp = now.timestamp()
    
    payload = {
      "user_id": user_id,
      "type": "refresh",
      "iat": iat_timestamp,
      "exp": exp_timestamp,
      "nbf": nbf_timestamp
    }
    
    return jwt.encode(
      payload, 
      settings.secret_key, 
      algorithm=settings.algorithm
    )
  
  @classmethod
  def verify_access_token(cls, token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode an access token.
    
    Args:
      token: JWT token string to verify
      
    Returns:
      Dict containing token payload if valid, None if invalid
    """
    try:
      payload = jwt.decode(
        token, 
        settings.secret_key, 
        algorithms=[settings.algorithm]
      )
      
      # Verify token type
      if payload.get("type") != "access":
        return None
      
      # Verify required fields
      required_fields = ["user_id", "permissions", "type", "exp"]
      if not all(field in payload for field in required_fields):
        return None
      
      return payload
    
    except jwt.ExpiredSignatureError:
      # Token has expired
      return None
    except jwt.InvalidTokenError:
      # Token is invalid (malformed, wrong signature, etc.)
      return None
    except Exception:
      # Any other error
      return None
  
  @classmethod
  def verify_refresh_token(cls, token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a refresh token.
    
    Args:
      token: JWT token string to verify
      
    Returns:
      Dict containing token payload if valid, None if invalid
    """
    try:
      payload = jwt.decode(
        token, 
        settings.secret_key, 
        algorithms=[settings.algorithm]
      )
      
      # Verify token type
      if payload.get("type") != "refresh":
        return None
      
      # Verify required fields
      required_fields = ["user_id", "type", "exp"]
      if not all(field in payload for field in required_fields):
        return None
      
      return payload
    
    except jwt.ExpiredSignatureError:
      # Token has expired
      return None
    except jwt.InvalidTokenError:
      # Token is invalid
      return None
    except Exception:
      # Any other error
      return None
  
  @classmethod
  def get_token_expiration(cls, token: str) -> Optional[datetime]:
    """
    Get expiration time from token without verifying signature.
    Useful for checking expiration before attempting verification.
    
    Args:
      token: JWT token string
      
    Returns:
      datetime: Expiration time if readable, None if not
    """
    try:
      # Decode without verification to get expiration
      payload = jwt.decode(
        token, 
        options={"verify_signature": False}
      )
      
      exp_timestamp = payload.get("exp")
      if exp_timestamp:
        return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
      
      return None
    
    except Exception:
      return None
  
  @classmethod
  def is_token_expired(cls, token: str) -> bool:
    """
    Check if token is expired without full verification.
    
    Args:
      token: JWT token string
      
    Returns:
      bool: True if expired, False if not or cannot determine
    """
    expiration = cls.get_token_expiration(token)
    if expiration is None:
      return True  # Assume expired if can't read expiration
    
    return datetime.now(timezone.utc) >= expiration
  
  @classmethod
  def extract_user_id(cls, token: str) -> Optional[int]:
    """
    Extract user ID from token without full verification.
    Useful for logging or identification before verification.
    
    Args:
      token: JWT token string
      
    Returns:
      int: User ID if readable, None if not
    """
    try:
      payload = jwt.decode(
        token, 
        options={"verify_signature": False}
      )
      
      user_id = payload.get("user_id")
      return int(user_id) if user_id is not None else None
    
    except Exception:
      return None
  
  @classmethod
  def refresh_access_token(
    cls, 
    refresh_token: str, 
    permissions: List[str]
  ) -> Optional[str]:
    """
    Create new access token using valid refresh token.
    
    Args:
      refresh_token: Valid refresh token
      permissions: Current user permissions
      
    Returns:
      str: New access token if refresh token is valid, None otherwise
    """
    refresh_payload = cls.verify_refresh_token(refresh_token)
    if refresh_payload is None:
      return None
    
    user_id = refresh_payload["user_id"]
    return cls.create_access_token(user_id, permissions)

  @classmethod
  def create_service_token(
    cls,
    payload: Dict[str, Any],
    expires_at: datetime
  ) -> str:
    """
    Create a JWT service token for inter-service communication.
    
    Args:
      payload: Token payload containing service info
      expires_at: Token expiration time
      
    Returns:
      str: Encoded JWT service token
    """
    now = datetime.now(timezone.utc)
    
    # Use timestamp with microseconds for uniqueness
    iat_timestamp = now.timestamp()
    exp_timestamp = expires_at.timestamp()
    nbf_timestamp = now.timestamp()
    
    token_payload = {
      **payload,
      "iat": iat_timestamp,
      "exp": exp_timestamp,
      "nbf": nbf_timestamp
    }
    
    return jwt.encode(
      token_payload,
      settings.secret_key,
      algorithm=settings.algorithm
    )

  @classmethod
  def verify_service_token(cls, token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a service token.
    
    Args:
      token: JWT service token string to verify
      
    Returns:
      Dict containing token payload if valid, None if invalid
    """
    try:
      payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
      )
      
      # Verify token type
      if payload.get("type") != "service_token":
        return None
      
      # Verify required fields
      required_fields = ["service_id", "service_name", "scopes", "type", "exp"]
      if not all(field in payload for field in required_fields):
        return None
      
      return payload
    
    except jwt.ExpiredSignatureError:
      # Token has expired
      return None
    except jwt.InvalidTokenError:
      # Token is invalid
      return None
    except Exception:
      # Any other error
      return None

  @classmethod
  def extract_service_id(cls, token: str) -> Optional[int]:
    """
    Extract service ID from service token without full verification.
    
    Args:
      token: JWT service token string
      
    Returns:
      int: Service ID if readable, None if not
    """
    try:
      payload = jwt.decode(
        token,
        options={"verify_signature": False}
      )
      
      service_id = payload.get("service_id")
      return int(service_id) if service_id is not None else None
    
    except Exception:
      return None