"""
Tests for password policy enforcement and validation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.services.password_service import PasswordService, PasswordPolicyConfig
from app.models.password_history import PasswordHistory
from tests.conftest import create_test_user, get_test_token


class TestPasswordPolicyService:
    """Test password policy enforcement in PasswordService."""
    
    def test_password_policy_config(self):
        """Test password policy configuration values."""
        assert PasswordPolicyConfig.MIN_LENGTH == 8
        assert PasswordPolicyConfig.MAX_LENGTH == 128
        assert PasswordPolicyConfig.RECOMMENDED_LENGTH == 12
        assert PasswordPolicyConfig.REQUIRE_UPPERCASE is True
        assert PasswordPolicyConfig.REQUIRE_LOWERCASE is True
        assert PasswordPolicyConfig.REQUIRE_DIGITS is True
        assert PasswordPolicyConfig.REQUIRE_SPECIAL_CHARS is True
        assert PasswordPolicyConfig.MIN_SPECIAL_CHARS == 1
        assert PasswordPolicyConfig.MIN_UNIQUE_CHARS == 6
        assert PasswordPolicyConfig.MAX_REPEATED_CHARS == 2
        assert PasswordPolicyConfig.PASSWORD_HISTORY_COUNT == 5
        assert PasswordPolicyConfig.MIN_COMPLEXITY_SCORE == 60
    
    def test_password_validation_empty_password(self):
        """Test validation with empty password."""
        result = PasswordService.validate_password_policy("")
        
        assert result["is_valid"] is False
        assert result["score"] == 0
        assert result["strength"] == "Very Weak"
        assert "Password is required" in result["feedback"]
        assert "empty_password" in result["violations"]
    
    def test_password_validation_too_short(self):
        """Test validation with too short password."""
        result = PasswordService.validate_password_policy("Ab1!")
        
        assert result["is_valid"] is False
        assert f"Password must be at least {PasswordPolicyConfig.MIN_LENGTH} characters long" in result["feedback"]
        assert "min_length" in result["violations"]
    
    def test_password_validation_too_long(self):
        """Test validation with too long password."""
        long_password = "A" * (PasswordPolicyConfig.MAX_LENGTH + 1)
        result = PasswordService.validate_password_policy(long_password)
        
        assert result["is_valid"] is False
        assert f"Password must not exceed {PasswordPolicyConfig.MAX_LENGTH} characters" in result["feedback"]
        assert "max_length" in result["violations"]
    
    def test_password_validation_missing_character_types(self):
        """Test validation with missing character types."""
        # Missing uppercase
        result = PasswordService.validate_password_policy("password123!")
        assert "missing_uppercase" in result["violations"]
        
        # Missing lowercase
        result = PasswordService.validate_password_policy("PASSWORD123!")
        assert "missing_lowercase" in result["violations"]
        
        # Missing digits
        result = PasswordService.validate_password_policy("Password!")
        assert "missing_digit" in result["violations"]
        
        # Missing special characters
        result = PasswordService.validate_password_policy("Password123")
        assert "missing_special" in result["violations"]
    
    def test_password_validation_repeated_characters(self):
        """Test validation with repeated characters."""
        result = PasswordService.validate_password_policy("Password1111!")
        
        assert "repeated_chars" in result["violations"]
        assert any("repeated" in feedback for feedback in result["feedback"])
    
    def test_password_validation_sequential_patterns(self):
        """Test validation with sequential patterns."""
        # Sequential numbers
        result = PasswordService.validate_password_policy("Password123!")
        assert "sequential_patterns" in result["violations"]
        
        # Sequential letters
        result = PasswordService.validate_password_policy("Passwordabc!")
        assert "sequential_patterns" in result["violations"]
    
    def test_password_validation_forbidden_patterns(self):
        """Test validation with forbidden patterns."""
        result = PasswordService.validate_password_policy("Passwordqwer!")
        
        assert "forbidden_patterns" in result["violations"]
        assert any("forbidden patterns" in feedback for feedback in result["feedback"])
    
    def test_password_validation_common_passwords(self):
        """Test validation with common passwords."""
        for common_password in ["password", "123456", "qwerty", "admin"]:
            result = PasswordService.validate_password_policy(common_password)
            assert "common_password" in result["violations"]
            assert "too common and easily guessable" in ' '.join(result["feedback"])
    
    def test_password_validation_personal_info(self):
        """Test validation with personal information."""
        user_context = {
            "email": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "name": "John Doe"
        }
        
        # Password contains email part
        result = PasswordService.validate_password_policy("johndoe123!", user_context)
        assert "personal_info" in result["violations"]
        
        # Password contains name
        result = PasswordService.validate_password_policy("John123!", user_context)
        assert "personal_info" in result["violations"]
    
    def test_password_validation_strong_password(self):
        """Test validation with strong password."""
        result = PasswordService.validate_password_policy("MyStr0ng!P@ssw0rd")
        
        assert result["is_valid"] is True
        assert result["score"] >= PasswordPolicyConfig.MIN_COMPLEXITY_SCORE
        assert result["strength"] in ["Strong", "Very Strong"]
        assert len(result["violations"]) == 0
        assert len(result["feedback"]) == 0
    
    def test_password_entropy_calculation(self):
        """Test password entropy calculation."""
        # Simple password
        entropy1 = PasswordService._estimate_entropy("password")
        
        # Complex password
        entropy2 = PasswordService._estimate_entropy("MyC0mpl3x!P@ssw0rd")
        
        assert entropy2 > entropy1
        assert entropy2 > 50  # Should have good entropy
    
    def test_password_complexity_scoring(self):
        """Test password complexity scoring system."""
        # Weak password
        result1 = PasswordService.validate_password_policy("password123")
        
        # Strong password
        result2 = PasswordService.validate_password_policy("MyStr0ng!P@ssw0rd2024")
        
        assert result2["score"] > result1["score"]
        assert result2["strength"] != "Very Weak"
    
    def test_generate_secure_password(self):
        """Test secure password generation."""
        password = PasswordService.generate_secure_password()
        
        # Test generated password meets policy
        result = PasswordService.validate_password_policy(password)
        assert result["is_valid"] is True
        assert result["score"] >= PasswordPolicyConfig.MIN_COMPLEXITY_SCORE
        
        # Test custom length
        password_16 = PasswordService.generate_secure_password(16)
        assert len(password_16) == 16
        
        result_16 = PasswordService.validate_password_policy(password_16)
        assert result_16["is_valid"] is True
    
    def test_password_policy_info(self):
        """Test password policy information retrieval."""
        policy_info = PasswordService.get_password_policy_info()
        
        assert "requirements" in policy_info
        assert "guidelines" in policy_info
        assert "forbidden" in policy_info
        
        requirements = policy_info["requirements"]
        assert requirements["min_length"] == PasswordPolicyConfig.MIN_LENGTH
        assert requirements["require_uppercase"] == PasswordPolicyConfig.REQUIRE_UPPERCASE
        
        assert len(policy_info["guidelines"]) > 0
        assert len(policy_info["forbidden"]) > 0
    
    @pytest.mark.asyncio
    async def test_password_history_checking(self, db_session: AsyncSession):
        """Test password history functionality."""
        # Create test user
        user = await create_test_user(db_session, email="history@example.com")
        
        # Test new password (should be allowed)
        is_allowed = await PasswordService.check_password_history(
            db_session, user.id, "NewPassword123!"
        )
        assert is_allowed is True
        
        # Add password to history
        password_hash = PasswordService.hash_password("OldPassword123!")
        await PasswordService.add_to_password_history(db_session, user.id, password_hash)
        
        # Test same password (should be rejected)
        is_allowed = await PasswordService.check_password_history(
            db_session, user.id, "OldPassword123!"
        )
        assert is_allowed is False
        
        # Test different password (should be allowed)
        is_allowed = await PasswordService.check_password_history(
            db_session, user.id, "DifferentPassword123!"
        )
        assert is_allowed is True


class TestPasswordPolicyEndpoints:
    """Test password policy API endpoints."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_get_password_policy(self, client: TestClient):
        """Test password policy information endpoint."""
        response = client.get("/api/password-policy/policy")
        assert response.status_code == 200
        
        data = response.json()
        assert "requirements" in data
        assert "guidelines" in data
        assert "forbidden" in data
        
        requirements = data["requirements"]
        assert requirements["min_length"] == 8
        assert requirements["require_uppercase"] is True
    
    def test_validate_password_endpoint(self, client: TestClient):
        """Test password validation endpoint."""
        # Valid password
        response = client.post("/api/password-policy/validate", json={
            "password": "MyStr0ng!P@ssw0rd"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is True
        assert data["score"] >= 60
        assert data["strength"] in ["Strong", "Very Strong"]
        
        # Invalid password
        response = client.post("/api/password-policy/validate", json={
            "password": "weak"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is False
        assert len(data["feedback"]) > 0
        assert len(data["violations"]) > 0
    
    def test_validate_password_with_context(self, client: TestClient):
        """Test password validation with user context."""
        response = client.post("/api/password-policy/validate", json={
            "password": "john123!",
            "user_context": {
                "first_name": "John",
                "email": "john@example.com"
            }
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is False
        assert "personal_info" in data["violations"]
    
    @pytest.mark.asyncio
    async def test_validate_password_for_user(self, client: TestClient, db_session: AsyncSession):
        """Test password validation for authenticated user."""
        # Create user and get token
        user = await create_test_user(db_session, email="user@example.com", password="CurrentPass123!")
        token = await get_test_token(db_session, user.email, "CurrentPass123!")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Valid password
        response = client.post("/api/password-policy/validate-for-user", 
            json={"password": "NewStr0ng!P@ssw0rd"},
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is True
        
        # Password with user's name (should fail)
        response = client.post("/api/password-policy/validate-for-user",
            json={"password": f"{user.first_name}123!"},
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is False
        assert "personal_info" in data["violations"]
    
    def test_generate_password_endpoint(self, client: TestClient):
        """Test password generation endpoint."""
        response = client.post("/api/password-policy/generate", json={
            "length": 16
        })
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["password"]) == 16
        assert data["validation"]["is_valid"] is True
        assert data["validation"]["score"] >= 60
        
        # Test default length
        response = client.post("/api/password-policy/generate", json={})
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["password"]) == 12  # Default length
    
    def test_password_strength_check(self, client: TestClient):
        """Test quick password strength check endpoint."""
        response = client.get("/api/password-policy/strength/MyStr0ng!P@ssw0rd")
        assert response.status_code == 200
        
        data = response.json()
        assert "strength" in data
        assert "score" in data
        assert "is_valid" in data
        assert data["is_valid"] is True
        
        # Test with weak password
        response = client.get("/api/password-policy/strength/weak")
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is False
    
    def test_password_too_long_for_url(self, client: TestClient):
        """Test password too long for URL parameter."""
        long_password = "A" * 200
        response = client.get(f"/api/password-policy/strength/{long_password}")
        assert response.status_code == 400
        assert "too long for URL parameter" in response.json()["detail"]


class TestPasswordPolicyIntegration:
    """Test password policy integration with authentication."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_registration_with_weak_password(self, client: TestClient):
        """Test user registration with weak password."""
        response = client.post("/api/auth/register", json={
            "email": "weak@example.com",
            "password": "weak",
            "first_name": "Test",
            "last_name": "User"
        })
        assert response.status_code == 400
        assert "does not meet policy requirements" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_registration_with_personal_info_password(self, client: TestClient):
        """Test user registration with password containing personal info."""
        response = client.post("/api/auth/register", json={
            "email": "john.doe@example.com",
            "password": "johndoe123!",
            "first_name": "John",
            "last_name": "Doe"
        })
        assert response.status_code == 400
        assert "personal information" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_registration_with_strong_password(self, client: TestClient):
        """Test user registration with strong password."""
        response = client.post("/api/auth/register", json={
            "email": "strong@example.com",
            "password": "MyStr0ng!P@ssw0rd2024",
            "first_name": "Test",
            "last_name": "User"
        })
        assert response.status_code == 201
        assert "access_token" in response.json()
    
    @pytest.mark.asyncio
    async def test_password_change_with_policy_enforcement(self, client: TestClient, db_session: AsyncSession):
        """Test password change with policy enforcement."""
        # Create user
        user = await create_test_user(db_session, email="change@example.com", password="OldPass123!")
        token = await get_test_token(db_session, user.email, "OldPass123!")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try weak password
        response = client.post("/api/auth/change-password", json={
            "current_password": "OldPass123!",
            "new_password": "weak"
        }, headers=headers)
        assert response.status_code == 400
        assert "does not meet policy requirements" in response.json()["detail"]
        
        # Try strong password
        response = client.post("/api/auth/change-password", json={
            "current_password": "OldPass123!",
            "new_password": "NewStr0ng!P@ssw0rd2024"
        }, headers=headers)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_password_history_prevention(self, client: TestClient, db_session: AsyncSession):
        """Test password history prevents reuse."""
        # Create user
        user = await create_test_user(db_session, email="reuse@example.com", password="FirstPass123!")
        token = await get_test_token(db_session, user.email, "FirstPass123!")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Change to second password
        response = client.post("/api/auth/change-password", json={
            "current_password": "FirstPass123!",
            "new_password": "SecondPass123!"
        }, headers=headers)
        assert response.status_code == 200
        
        # Get new token after password change
        login_response = client.post("/api/auth/login", json={
            "email": "reuse@example.com",
            "password": "SecondPass123!"
        })
        assert login_response.status_code == 200
        new_token = login_response.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        
        # Try to change back to first password
        response = client.post("/api/auth/change-password", json={
            "current_password": "SecondPass123!",
            "new_password": "FirstPass123!"
        }, headers=new_headers)
        assert response.status_code == 400
        assert "used recently" in response.json()["detail"]