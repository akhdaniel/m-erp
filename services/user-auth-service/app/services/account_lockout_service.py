"""
Account lockout service for preventing brute force attacks.
Manages account locking, unlocking, and failed attempt tracking.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.models.user import User
from app.models.audit_log import AuditAction
from app.services.audit_service import AuditService
from app.core.config import settings


class AccountLockoutConfig:
    """Configuration for account lockout behavior."""
    
    # Maximum failed attempts before lockout
    MAX_FAILED_ATTEMPTS = 5
    
    # Lockout duration in minutes
    LOCKOUT_DURATION_MINUTES = 15
    
    # Progressive lockout durations (minutes) based on lockout count
    PROGRESSIVE_LOCKOUT_DURATIONS = [15, 30, 60, 120, 240]  # 15min, 30min, 1hr, 2hr, 4hr
    
    # Time window for failed attempts (minutes)
    FAILED_ATTEMPTS_WINDOW_MINUTES = 60
    
    # Enable progressive lockout (longer lockouts for repeat offenders)
    ENABLE_PROGRESSIVE_LOCKOUT = True
    
    # Enable IP-based tracking
    ENABLE_IP_TRACKING = True
    
    # Maximum failed attempts per IP before additional restrictions
    MAX_IP_FAILED_ATTEMPTS = 20


class AccountLockoutService:
    """Service for managing account lockouts and brute force protection."""
    
    @staticmethod
    async def check_account_lockout(
        db: AsyncSession,
        user: User,
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """
        Check if account is locked and return lockout status.
        
        Args:
            db: Database session
            user: User to check
            request: Optional request for IP tracking
            
        Returns:
            Dictionary with lockout status and details
        """
        # Check if account is currently locked
        if user.is_locked:
            remaining_time = user.lockout_remaining_time
            
            # Log continued attempt on locked account
            if request:
                await AuditService.log_action(
                    db=db,
                    action=AuditAction.UNAUTHORIZED_ACCESS,
                    description=f"Login attempt on locked account: {user.email}",
                    user_id=user.id,
                    request=request,
                    success=False,
                    error_message="Account is locked",
                    metadata={
                        "remaining_lockout_seconds": int(remaining_time.total_seconds()) if remaining_time else 0,
                        "failed_attempts": user.failed_login_attempts
                    }
                )
            
            return {
                "is_locked": True,
                "locked_until": user.locked_until,
                "remaining_time": remaining_time,
                "failed_attempts": user.failed_login_attempts,
                "reason": "Account locked due to multiple failed login attempts"
            }
        
        return {
            "is_locked": False,
            "failed_attempts": user.failed_login_attempts,
            "max_attempts": AccountLockoutConfig.MAX_FAILED_ATTEMPTS
        }
    
    @staticmethod
    async def handle_failed_login(
        db: AsyncSession,
        user: User,
        reason: str,
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """
        Handle failed login attempt and potentially lock account.
        
        Args:
            db: Database session
            user: User who failed login
            reason: Reason for login failure
            request: Optional request for IP tracking
            
        Returns:
            Dictionary with lockout result and details
        """
        # Determine lockout parameters
        max_attempts = AccountLockoutConfig.MAX_FAILED_ATTEMPTS
        lockout_duration = AccountLockoutConfig.LOCKOUT_DURATION_MINUTES
        
        # Apply progressive lockout if enabled
        if AccountLockoutConfig.ENABLE_PROGRESSIVE_LOCKOUT:
            lockout_count = await AccountLockoutService._get_user_lockout_count(db, user)
            if lockout_count > 0 and lockout_count <= len(AccountLockoutConfig.PROGRESSIVE_LOCKOUT_DURATIONS):
                lockout_duration = AccountLockoutConfig.PROGRESSIVE_LOCKOUT_DURATIONS[lockout_count - 1]
        
        # Increment failed attempts
        was_locked = user.increment_failed_attempts(max_attempts, lockout_duration)
        
        # Save user changes
        await db.commit()
        await db.refresh(user)
        
        # Log the failed attempt
        await AuditService.log_authentication_failure(
            db=db,
            email=user.email,
            reason=reason,
            request=request,
            attempt_count=user.failed_login_attempts
        )
        
        # If account was just locked, log lockout event
        if was_locked:
            await AuditService.log_action(
                db=db,
                action=AuditAction.ACCOUNT_LOCKED,
                description=f"Account locked after {user.failed_login_attempts} failed attempts",
                user_id=user.id,
                request=request,
                success=False,
                metadata={
                    "failed_attempts": user.failed_login_attempts,
                    "lockout_duration_minutes": lockout_duration,
                    "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                    "reason": reason
                }
            )
        
        # Check IP-based restrictions if enabled
        ip_status = {}
        if request and AccountLockoutConfig.ENABLE_IP_TRACKING:
            ip_status = await AccountLockoutService._check_ip_restrictions(db, request)
        
        return {
            "account_locked": was_locked,
            "failed_attempts": user.failed_login_attempts,
            "max_attempts": max_attempts,
            "locked_until": user.locked_until,
            "lockout_duration_minutes": lockout_duration if was_locked else None,
            "progressive_lockout_applied": AccountLockoutConfig.ENABLE_PROGRESSIVE_LOCKOUT and was_locked,
            "ip_status": ip_status
        }
    
    @staticmethod
    async def handle_successful_login(
        db: AsyncSession,
        user: User,
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """
        Handle successful login and reset failed attempts.
        
        Args:
            db: Database session
            user: User who successfully logged in
            request: Optional request for logging
            
        Returns:
            Dictionary with reset status
        """
        had_failed_attempts = user.failed_login_attempts > 0
        was_locked = user.is_locked
        
        # Reset failed attempts
        user.reset_failed_attempts()
        user.last_login = datetime.utcnow()
        
        # Save changes
        await db.commit()
        await db.refresh(user)
        
        # Log successful login
        await AuditService.log_authentication_success(
            db=db,
            user_id=user.id,
            request=request
        )
        
        # If account was previously locked or had failed attempts, log the reset
        if was_locked or had_failed_attempts:
            await AuditService.log_action(
                db=db,
                action=AuditAction.ACCOUNT_UNLOCKED,
                description="Account unlocked after successful login",
                user_id=user.id,
                request=request,
                success=True,
                metadata={
                    "was_locked": was_locked,
                    "previous_failed_attempts": user.failed_login_attempts if had_failed_attempts else 0
                }
            )
        
        return {
            "login_successful": True,
            "account_was_locked": was_locked,
            "had_failed_attempts": had_failed_attempts,
            "failed_attempts_reset": True
        }
    
    @staticmethod
    async def unlock_user_account(
        db: AsyncSession,
        user: User,
        admin_user_id: int,
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """
        Manually unlock a user account (admin action).
        
        Args:
            db: Database session
            user: User to unlock
            admin_user_id: ID of admin performing unlock
            request: Optional request for logging
            
        Returns:
            Dictionary with unlock result
        """
        was_locked = user.is_locked
        failed_attempts = user.failed_login_attempts
        
        # Unlock account
        user.unlock_account()
        
        # Save changes
        await db.commit()
        await db.refresh(user)
        
        # Log admin unlock action
        await AuditService.log_admin_action(
            db=db,
            admin_user_id=admin_user_id,
            action_type="account_unlock",
            description=f"Manually unlocked account for user: {user.email}",
            target_user_id=user.id,
            request=request,
            metadata={
                "was_locked": was_locked,
                "previous_failed_attempts": failed_attempts,
                "locked_until": user.locked_until.isoformat() if user.locked_until else None
            }
        )
        
        return {
            "account_unlocked": True,
            "was_locked": was_locked,
            "previous_failed_attempts": failed_attempts,
            "unlocked_by_admin": admin_user_id
        }
    
    @staticmethod
    async def get_lockout_statistics(
        db: AsyncSession,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get account lockout statistics for monitoring.
        
        Args:
            db: Database session
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with lockout statistics
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Currently locked accounts
        locked_accounts_query = select(func.count(User.id)).where(
            and_(
                User.locked_until.isnot(None),
                User.locked_until > datetime.utcnow()
            )
        )
        locked_accounts_result = await db.execute(locked_accounts_query)
        currently_locked = locked_accounts_result.scalar() or 0
        
        # Accounts with recent failed attempts
        failed_attempts_query = select(func.count(User.id)).where(
            and_(
                User.failed_login_attempts > 0,
                User.last_failed_login >= since
            )
        )
        failed_attempts_result = await db.execute(failed_attempts_query)
        accounts_with_failed_attempts = failed_attempts_result.scalar() or 0
        
        # Top accounts by failed attempts
        top_failed_query = select(
            User.email,
            User.failed_login_attempts,
            User.last_failed_login,
            User.locked_until
        ).where(
            User.failed_login_attempts > 0
        ).order_by(User.failed_login_attempts.desc()).limit(10)
        
        top_failed_result = await db.execute(top_failed_query)
        top_failed_accounts = [
            {
                "email": row.email,
                "failed_attempts": row.failed_login_attempts,
                "last_failed_login": row.last_failed_login.isoformat() if row.last_failed_login else None,
                "locked_until": row.locked_until.isoformat() if row.locked_until else None,
                "is_locked": row.locked_until and row.locked_until > datetime.utcnow()
            }
            for row in top_failed_result
        ]
        
        return {
            "period_hours": hours,
            "currently_locked_accounts": currently_locked,
            "accounts_with_failed_attempts": accounts_with_failed_attempts,
            "top_failed_accounts": top_failed_accounts,
            "lockout_config": {
                "max_failed_attempts": AccountLockoutConfig.MAX_FAILED_ATTEMPTS,
                "lockout_duration_minutes": AccountLockoutConfig.LOCKOUT_DURATION_MINUTES,
                "progressive_lockout_enabled": AccountLockoutConfig.ENABLE_PROGRESSIVE_LOCKOUT,
                "ip_tracking_enabled": AccountLockoutConfig.ENABLE_IP_TRACKING
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def _get_user_lockout_count(db: AsyncSession, user: User) -> int:
        """Get number of times user has been locked out in the past."""
        # This could be implemented by tracking lockout history in audit logs
        # For now, return 0 for simplicity
        return 0
    
    @staticmethod
    async def _check_ip_restrictions(
        db: AsyncSession,
        request: Request
    ) -> Dict[str, Any]:
        """
        Check IP-based restrictions for additional security.
        
        Args:
            db: Database session
            request: Request object for IP extraction
            
        Returns:
            Dictionary with IP restriction status
        """
        ip_address = request.client.host if request.client else "unknown"
        
        # This could be enhanced with IP-based rate limiting
        # For now, return basic status
        return {
            "ip_address": ip_address,
            "additional_restrictions": False,
            "ip_based_lockout": False
        }


# Convenience functions
async def check_account_lockout(
    db: AsyncSession,
    user: User,
    request: Optional[Request] = None
) -> Dict[str, Any]:
    """Convenience function for checking account lockout."""
    return await AccountLockoutService.check_account_lockout(db, user, request)


async def handle_failed_login(
    db: AsyncSession,
    user: User,
    reason: str,
    request: Optional[Request] = None
) -> Dict[str, Any]:
    """Convenience function for handling failed login."""
    return await AccountLockoutService.handle_failed_login(db, user, reason, request)


async def handle_successful_login(
    db: AsyncSession,
    user: User,
    request: Optional[Request] = None
) -> Dict[str, Any]:
    """Convenience function for handling successful login."""
    return await AccountLockoutService.handle_successful_login(db, user, request)