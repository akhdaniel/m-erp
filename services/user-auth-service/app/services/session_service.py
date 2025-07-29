"""
Session management service for handling user sessions and refresh tokens.
Provides session creation, validation, and cleanup functionality.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update

from app.models.role import UserSession
from app.core.config import settings


class SessionService:
  """Service for managing user sessions and refresh tokens."""
  
  @classmethod
  async def create_session(
    cls,
    db: AsyncSession,
    user_id: int,
    refresh_token: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
  ) -> UserSession:
    """
    Create a new user session with refresh token.
    
    Args:
      db: Database session
      user_id: User ID for the session
      refresh_token: Refresh token string
      ip_address: Client IP address (optional)
      user_agent: Client user agent (optional)
      expires_delta: Custom expiration time (defaults to config setting)
      
    Returns:
      UserSession: Created session object
    """
    if expires_delta is None:
      expires_delta = timedelta(days=settings.refresh_token_expire_days)
    
    expires_at = datetime.now(timezone.utc) + expires_delta
    
    session = UserSession(
      user_id=user_id,
      refresh_token=refresh_token,
      expires_at=expires_at,
      ip_address=ip_address,
      user_agent=user_agent[:500] if user_agent else None  # Truncate to fit DB field
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session
  
  @classmethod
  async def get_session_by_token(
    cls,
    db: AsyncSession,
    refresh_token: str
  ) -> Optional[UserSession]:
    """
    Retrieve session by refresh token.
    
    Args:
      db: Database session
      refresh_token: Refresh token to search for
      
    Returns:
      UserSession: Session object if found, None otherwise
    """
    stmt = select(UserSession).where(
      UserSession.refresh_token == refresh_token
    )
    
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
  
  @classmethod
  async def is_session_valid(
    cls,
    db: AsyncSession,
    refresh_token: str
  ) -> bool:
    """
    Check if session is valid (exists, not expired, not revoked).
    
    Args:
      db: Database session
      refresh_token: Refresh token to validate
      
    Returns:
      bool: True if session is valid, False otherwise
    """
    session = await cls.get_session_by_token(db, refresh_token)
    
    if session is None:
      return False
    
    # Check if session is valid (not expired and not revoked)
    return session.is_valid
  
  @classmethod
  async def revoke_session(
    cls,
    db: AsyncSession,
    refresh_token: str
  ) -> bool:
    """
    Revoke a session by marking it as revoked.
    
    Args:
      db: Database session
      refresh_token: Refresh token to revoke
      
    Returns:
      bool: True if session was found and revoked, False otherwise
    """
    stmt = (
      update(UserSession)
      .where(UserSession.refresh_token == refresh_token)
      .values(is_revoked=True)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount > 0
  
  @classmethod
  async def revoke_all_user_sessions(
    cls,
    db: AsyncSession,
    user_id: int
  ) -> int:
    """
    Revoke all sessions for a specific user.
    Useful for logout from all devices or security incidents.
    
    Args:
      db: Database session
      user_id: User ID whose sessions to revoke
      
    Returns:
      int: Number of sessions revoked
    """
    stmt = (
      update(UserSession)
      .where(
        UserSession.user_id == user_id,
        UserSession.is_revoked == False
      )
      .values(is_revoked=True)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount
  
  @classmethod
  async def cleanup_expired_sessions(
    cls,
    db: AsyncSession,
    batch_size: int = 1000
  ) -> int:
    """
    Clean up expired sessions from the database.
    Should be run periodically to prevent database bloat.
    
    Args:
      db: Database session
      batch_size: Number of sessions to delete in one operation
      
    Returns:
      int: Number of sessions cleaned up
    """
    now = datetime.now(timezone.utc)
    
    stmt = (
      delete(UserSession)
      .where(UserSession.expires_at < now)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount
  
  @classmethod
  async def cleanup_revoked_sessions(
    cls,
    db: AsyncSession,
    days_old: int = 30,
    batch_size: int = 1000
  ) -> int:
    """
    Clean up old revoked sessions from the database.
    
    Args:
      db: Database session
      days_old: Remove revoked sessions older than this many days
      batch_size: Number of sessions to delete in one operation
      
    Returns:
      int: Number of sessions cleaned up
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
    
    stmt = (
      delete(UserSession)
      .where(
        UserSession.is_revoked == True,
        UserSession.created_at < cutoff_date
      )
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount
  
  @classmethod
  async def get_user_active_sessions(
    cls,
    db: AsyncSession,
    user_id: int
  ) -> list[UserSession]:
    """
    Get all active (valid) sessions for a user.
    
    Args:
      db: Database session
      user_id: User ID to get sessions for
      
    Returns:
      list[UserSession]: List of active sessions
    """
    now = datetime.now(timezone.utc)
    
    stmt = select(UserSession).where(
      UserSession.user_id == user_id,
      UserSession.is_revoked == False,
      UserSession.expires_at > now
    ).order_by(UserSession.created_at.desc())
    
    result = await db.execute(stmt)
    return list(result.scalars().all())
  
  @classmethod
  async def update_session_activity(
    cls,
    db: AsyncSession,
    refresh_token: str,
    ip_address: Optional[str] = None
  ) -> bool:
    """
    Update session last activity (useful for tracking usage).
    Note: This could be extended to track last_used timestamp.
    
    Args:
      db: Database session
      refresh_token: Refresh token to update
      ip_address: Updated IP address (optional)
      
    Returns:
      bool: True if session was found and updated, False otherwise
    """
    update_values = {}
    
    if ip_address:
      update_values["ip_address"] = ip_address
    
    if not update_values:
      return False
    
    stmt = (
      update(UserSession)
      .where(UserSession.refresh_token == refresh_token)
      .values(**update_values)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount > 0
  
  @classmethod
  async def count_user_sessions(
    cls,
    db: AsyncSession,
    user_id: int,
    active_only: bool = True
  ) -> int:
    """
    Count sessions for a user.
    
    Args:
      db: Database session
      user_id: User ID to count sessions for
      active_only: Only count active (non-revoked, non-expired) sessions
      
    Returns:
      int: Number of sessions
    """
    stmt = select(UserSession).where(UserSession.user_id == user_id)
    
    if active_only:
      now = datetime.now(timezone.utc)
      stmt = stmt.where(
        UserSession.is_revoked == False,
        UserSession.expires_at > now
      )
    
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    return len(list(sessions))