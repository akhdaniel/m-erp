"""
Tests for account lockout functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User
from app.services.account_lockout_service import (
    AccountLockoutService, 
    AccountLockoutConfig,
    check_account_lockout,
    handle_failed_login,
    handle_successful_login
)
from tests.conftest import create_test_user, create_test_role, get_test_token


class TestUserModel:
    """Test User model lockout functionality."""
    
    def test_is_locked_property(self):
        """Test is_locked property."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User"
        )
        
        # Not locked initially
        assert user.is_locked is False
        
        # Set lockout in future
        user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        assert user.is_locked is True
        
        # Set lockout in past
        user.locked_until = datetime.utcnow() - timedelta(minutes=5)
        assert user.is_locked is False
    
    def test_lockout_remaining_time(self):
        """Test lockout_remaining_time property."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User"
        )
        
        # No lockout
        assert user.lockout_remaining_time is None
        
        # Lockout in future
        future_time = datetime.utcnow() + timedelta(minutes=10)
        user.locked_until = future_time
        remaining = user.lockout_remaining_time
        assert remaining is not None
        assert remaining.total_seconds() > 0
        
        # Lockout in past
        user.locked_until = datetime.utcnow() - timedelta(minutes=5)
        assert user.lockout_remaining_time is None
    
    def test_increment_failed_attempts(self):
        """Test increment_failed_attempts method."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User"
        )
        
        # First attempt
        locked = user.increment_failed_attempts(max_attempts=3, lockout_duration_minutes=15)
        assert user.failed_login_attempts == 1
        assert locked is False
        assert user.locked_until is None
        assert user.last_failed_login is not None
        
        # Second attempt
        locked = user.increment_failed_attempts(max_attempts=3, lockout_duration_minutes=15)
        assert user.failed_login_attempts == 2
        assert locked is False
        
        # Third attempt - should lock
        locked = user.increment_failed_attempts(max_attempts=3, lockout_duration_minutes=15)
        assert user.failed_login_attempts == 3
        assert locked is True
        assert user.locked_until is not None
        assert user.is_locked is True
    
    def test_reset_failed_attempts(self):
        """Test reset_failed_attempts method."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User"
        )
        
        # Set some failed attempts and lockout
        user.failed_login_attempts = 5
        user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        user.last_failed_login = datetime.utcnow()
        
        # Reset
        user.reset_failed_attempts()
        
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
        assert user.last_failed_login is None
        assert user.is_locked is False
    
    def test_unlock_account(self):
        """Test unlock_account method."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User"
        )
        
        # Set lockout state
        user.failed_login_attempts = 5
        user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        user.last_failed_login = datetime.utcnow()
        
        # Unlock
        user.unlock_account()
        
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
        assert user.last_failed_login is None
        assert user.is_locked is False


class TestAccountLockoutService:
    """Test AccountLockoutService functionality."""
    
    @pytest.mark.asyncio
    async def test_check_account_lockout_not_locked(self, db_session: AsyncSession):
        """Test checking lockout status for unlocked account."""
        user = await create_test_user(db_session, email="test@example.com")
        
        status = await AccountLockoutService.check_account_lockout(db_session, user)
        
        assert status["is_locked"] is False
        assert status["failed_attempts"] == 0
        assert status["max_attempts"] == AccountLockoutConfig.MAX_FAILED_ATTEMPTS
    
    @pytest.mark.asyncio
    async def test_check_account_lockout_locked(self, db_session: AsyncSession):
        """Test checking lockout status for locked account."""
        user = await create_test_user(db_session, email="test@example.com")
        
        # Lock the account
        user.failed_login_attempts = 5
        user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        await db_session.commit()
        
        status = await AccountLockoutService.check_account_lockout(db_session, user)
        
        assert status["is_locked"] is True
        assert status["locked_until"] == user.locked_until
        assert status["remaining_time"] is not None
        assert status["failed_attempts"] == 5
        assert "Account locked" in status["reason"]
    
    @pytest.mark.asyncio
    async def test_handle_failed_login_not_locked(self, db_session: AsyncSession):
        """Test handling failed login that doesn't cause lockout."""
        user = await create_test_user(db_session, email="test@example.com")
        
        result = await AccountLockoutService.handle_failed_login(
            db_session, user, "Invalid password"
        )
        
        assert result["account_locked"] is False
        assert result["failed_attempts"] == 1
        assert result["max_attempts"] == AccountLockoutConfig.MAX_FAILED_ATTEMPTS
        assert user.failed_login_attempts == 1
        assert user.locked_until is None
    
    @pytest.mark.asyncio
    async def test_handle_failed_login_causes_lockout(self, db_session: AsyncSession):
        """Test handling failed login that causes account lockout."""
        user = await create_test_user(db_session, email="test@example.com")
        
        # Set to just before lockout threshold
        user.failed_login_attempts = AccountLockoutConfig.MAX_FAILED_ATTEMPTS - 1
        await db_session.commit()
        
        result = await AccountLockoutService.handle_failed_login(
            db_session, user, "Invalid password"
        )
        
        assert result["account_locked"] is True
        assert result["failed_attempts"] == AccountLockoutConfig.MAX_FAILED_ATTEMPTS
        assert result["lockout_duration_minutes"] == AccountLockoutConfig.LOCKOUT_DURATION_MINUTES
        assert user.failed_login_attempts == AccountLockoutConfig.MAX_FAILED_ATTEMPTS
        assert user.locked_until is not None
        assert user.is_locked is True
    
    @pytest.mark.asyncio
    async def test_handle_successful_login(self, db_session: AsyncSession):
        """Test handling successful login."""
        user = await create_test_user(db_session, email="test@example.com")
        
        # Set some failed attempts
        user.failed_login_attempts = 3
        user.last_failed_login = datetime.utcnow()
        await db_session.commit()
        
        result = await AccountLockoutService.handle_successful_login(db_session, user)
        
        assert result["login_successful"] is True
        assert result["had_failed_attempts"] is True
        assert result["failed_attempts_reset"] is True
        assert user.failed_login_attempts == 0
        assert user.last_failed_login is None
        assert user.last_login is not None
    
    @pytest.mark.asyncio
    async def test_handle_successful_login_locked_account(self, db_session: AsyncSession):
        """Test handling successful login for previously locked account."""
        user = await create_test_user(db_session, email="test@example.com")
        
        # Set locked state
        user.failed_login_attempts = 5
        user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        user.last_failed_login = datetime.utcnow()
        await db_session.commit()
        
        result = await AccountLockoutService.handle_successful_login(db_session, user)
        
        assert result["login_successful"] is True
        assert result["account_was_locked"] is True
        assert result["had_failed_attempts"] is True
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
        assert user.is_locked is False
    
    @pytest.mark.asyncio
    async def test_unlock_user_account(self, db_session: AsyncSession):
        """Test manually unlocking user account."""
        user = await create_test_user(db_session, email="test@example.com")
        admin_user = await create_test_user(db_session, email="admin@example.com")
        
        # Lock the account
        user.failed_login_attempts = 5
        user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        await db_session.commit()
        
        result = await AccountLockoutService.unlock_user_account(
            db_session, user, admin_user.id
        )
        
        assert result["account_unlocked"] is True
        assert result["was_locked"] is True
        assert result["previous_failed_attempts"] == 5
        assert result["unlocked_by_admin"] == admin_user.id
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
        assert user.is_locked is False
    
    @pytest.mark.asyncio
    async def test_get_lockout_statistics(self, db_session: AsyncSession):
        """Test getting lockout statistics."""
        # Create users with different lockout states
        user1 = await create_test_user(db_session, email="locked@example.com")
        user2 = await create_test_user(db_session, email="failed@example.com")
        user3 = await create_test_user(db_session, email="normal@example.com")
        
        # Lock user1
        user1.failed_login_attempts = 5
        user1.locked_until = datetime.utcnow() + timedelta(minutes=15)
        user1.last_failed_login = datetime.utcnow()
        
        # Set failed attempts for user2
        user2.failed_login_attempts = 3
        user2.last_failed_login = datetime.utcnow()
        
        await db_session.commit()
        
        stats = await AccountLockoutService.get_lockout_statistics(db_session, 24)
        
        assert stats["period_hours"] == 24
        assert stats["currently_locked_accounts"] >= 1
        assert stats["accounts_with_failed_attempts"] >= 2
        assert "lockout_config" in stats
        assert "generated_at" in stats
        assert len(stats["top_failed_accounts"]) >= 2


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_check_account_lockout_convenience(self, db_session: AsyncSession):
        """Test check_account_lockout convenience function."""
        user = await create_test_user(db_session, email="test@example.com")
        
        status = await check_account_lockout(db_session, user)
        
        assert status["is_locked"] is False
        assert "failed_attempts" in status
    
    @pytest.mark.asyncio
    async def test_handle_failed_login_convenience(self, db_session: AsyncSession):
        """Test handle_failed_login convenience function."""
        user = await create_test_user(db_session, email="test@example.com")
        
        result = await handle_failed_login(db_session, user, "Test failure")
        
        assert "account_locked" in result
        assert "failed_attempts" in result
    
    @pytest.mark.asyncio
    async def test_handle_successful_login_convenience(self, db_session: AsyncSession):
        """Test handle_successful_login convenience function."""
        user = await create_test_user(db_session, email="test@example.com")
        
        result = await handle_successful_login(db_session, user)
        
        assert result["login_successful"] is True


class TestLoginEndpointIntegration:
    """Test login endpoint with account lockout integration."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_login_success_resets_failed_attempts(self, client: TestClient, db_session: AsyncSession):
        """Test that successful login resets failed attempts."""
        # Create user with failed attempts
        user = await create_test_user(db_session, email="test@example.com", password="correct_password")
        user.failed_login_attempts = 3
        user.last_failed_login = datetime.utcnow()
        await db_session.commit()
        
        # Successful login
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "correct_password"
        })
        
        assert response.status_code == 200
        
        # Check that failed attempts were reset
        await db_session.refresh(user)
        assert user.failed_login_attempts == 0
        assert user.last_failed_login is None
        assert user.last_login is not None
    
    @pytest.mark.asyncio
    async def test_login_failure_increments_attempts(self, client: TestClient, db_session: AsyncSession):
        """Test that failed login increments failed attempts."""
        user = await create_test_user(db_session, email="test@example.com", password="correct_password")
        
        # Failed login
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrong_password"
        })
        
        assert response.status_code == 401
        assert "attempts remaining" in response.json()["detail"]
        assert "X-Failed-Attempts" in response.headers
        assert "X-Remaining-Attempts" in response.headers
        
        # Check that failed attempts were incremented
        await db_session.refresh(user)
        assert user.failed_login_attempts == 1
        assert user.last_failed_login is not None
    
    @pytest.mark.asyncio
    async def test_login_lockout_after_max_attempts(self, client: TestClient, db_session: AsyncSession):
        """Test that account gets locked after max failed attempts."""
        user = await create_test_user(db_session, email="test@example.com", password="correct_password")
        
        # Make failed attempts up to the limit
        for attempt in range(AccountLockoutConfig.MAX_FAILED_ATTEMPTS):
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "wrong_password"
            })
            
            if attempt < AccountLockoutConfig.MAX_FAILED_ATTEMPTS - 1:
                assert response.status_code == 401
                assert "attempts remaining" in response.json()["detail"]
            else:
                # Last attempt should lock the account
                assert response.status_code == 423
                assert "Account locked" in response.json()["detail"]
                assert "X-Account-Locked" in response.headers
                assert "X-Lockout-Duration-Minutes" in response.headers
                assert "Retry-After" in response.headers
        
        # Check that account is locked
        await db_session.refresh(user)
        assert user.failed_login_attempts == AccountLockoutConfig.MAX_FAILED_ATTEMPTS
        assert user.is_locked is True
    
    @pytest.mark.asyncio
    async def test_login_blocked_when_locked(self, client: TestClient, db_session: AsyncSession):
        """Test that login is blocked when account is locked."""
        user = await create_test_user(db_session, email="test@example.com", password="correct_password")
        
        # Lock the account
        user.failed_login_attempts = 5
        user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        await db_session.commit()
        
        # Try to login with correct password
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "correct_password"
        })
        
        assert response.status_code == 423
        assert "Account locked" in response.json()["detail"]
        assert "X-Account-Locked" in response.headers
        assert "X-Lockout-Remaining-Minutes" in response.headers
        assert "Retry-After" in response.headers


class TestAdminEndpoints:
    """Test admin lockout management endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_unlock_account_success(self, client: TestClient, db_session: AsyncSession):
        """Test admin unlocking account successfully."""
        # Create admin user
        admin_role = await create_test_role(db_session, name="admin", permissions=["manage_users"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        admin_token = get_test_token(admin_user.id)
        
        # Create locked user
        locked_user = await create_test_user(db_session, email="locked@example.com")
        locked_user.failed_login_attempts = 5
        locked_user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        await db_session.commit()
        
        # Unlock account
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(f"/api/admin/unlock-account/{locked_user.id}", headers=headers)
        
        assert response.status_code == 200
        assert "Successfully unlocked" in response.json()["message"]
        
        # Verify account is unlocked
        await db_session.refresh(locked_user)
        assert locked_user.is_locked is False
        assert locked_user.failed_login_attempts == 0
    
    @pytest.mark.asyncio
    async def test_unlock_account_not_locked(self, client: TestClient, db_session: AsyncSession):
        """Test admin unlocking account that isn't locked."""
        # Create admin user
        admin_role = await create_test_role(db_session, name="admin", permissions=["manage_users"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        admin_token = get_test_token(admin_user.id)
        
        # Create unlocked user
        user = await create_test_user(db_session, email="user@example.com")
        
        # Try to unlock
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(f"/api/admin/unlock-account/{user.id}", headers=headers)
        
        assert response.status_code == 200
        assert "not currently locked" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_get_lockout_statistics(self, client: TestClient, db_session: AsyncSession):
        """Test getting lockout statistics."""
        # Create admin user
        admin_role = await create_test_role(db_session, name="admin", permissions=["manage_users"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        admin_token = get_test_token(admin_user.id)
        
        # Get statistics
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/admin/lockout-statistics", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "period_hours" in data
        assert "currently_locked_accounts" in data
        assert "accounts_with_failed_attempts" in data
        assert "lockout_config" in data
    
    @pytest.mark.asyncio
    async def test_get_locked_accounts(self, client: TestClient, db_session: AsyncSession):
        """Test getting list of locked accounts."""
        # Create admin user
        admin_role = await create_test_role(db_session, name="admin", permissions=["manage_users"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        admin_token = get_test_token(admin_user.id)
        
        # Create locked user
        locked_user = await create_test_user(db_session, email="locked@example.com")
        locked_user.failed_login_attempts = 5
        locked_user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        await db_session.commit()
        
        # Get locked accounts
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/admin/locked-accounts", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "locked_accounts" in data
        assert "total_locked" in data
        assert data["total_locked"] >= 1
        
        # Check locked account details
        locked_account = next(
            (acc for acc in data["locked_accounts"] if acc["email"] == "locked@example.com"), 
            None
        )
        assert locked_account is not None
        assert locked_account["failed_attempts"] == 5
        assert locked_account["remaining_minutes"] > 0
    
    @pytest.mark.asyncio
    async def test_admin_endpoints_require_permission(self, client: TestClient, db_session: AsyncSession):
        """Test that admin endpoints require proper permissions."""
        # Create regular user without admin permissions
        user = await create_test_user(db_session, email="user@example.com")
        token = get_test_token(user.id)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # All admin endpoints should return 403
        endpoints = [
            ("POST", "/api/admin/unlock-account/1"),
            ("GET", "/api/admin/lockout-statistics"),
            ("GET", "/api/admin/locked-accounts")
        ]
        
        for method, endpoint in endpoints:
            if method == "POST":
                response = client.post(endpoint, headers=headers)
            else:
                response = client.get(endpoint, headers=headers)
            
            assert response.status_code == 403