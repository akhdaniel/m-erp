import pytest
from datetime import datetime, timedelta, timezone

from app.services.password_service import PasswordService
from app.services.jwt_service import JWTService
from app.services.session_service import SessionService
from app.models.user import User
from app.models.role import UserSession


# Password Service Tests

@pytest.mark.unit
def test_password_hash_generation():
  """Test password hashing generates different hashes for same password."""
  password = "test_password_123"
  
  hash1 = PasswordService.hash_password(password)
  hash2 = PasswordService.hash_password(password)
  
  assert hash1 != hash2  # Different salts should produce different hashes
  assert len(hash1) > 0
  assert len(hash2) > 0


@pytest.mark.unit
def test_password_verification_success():
  """Test password verification with correct password."""
  password = "secure_password_456"
  password_hash = PasswordService.hash_password(password)
  
  assert PasswordService.verify_password(password, password_hash) is True


@pytest.mark.unit
def test_password_verification_failure():
  """Test password verification with incorrect password."""
  password = "correct_password"
  wrong_password = "wrong_password"
  password_hash = PasswordService.hash_password(password)
  
  assert PasswordService.verify_password(wrong_password, password_hash) is False


@pytest.mark.unit
def test_password_hash_not_empty():
  """Test that password hashing doesn't return empty string."""
  password = "test"
  password_hash = PasswordService.hash_password(password)
  
  assert password_hash is not None
  assert len(password_hash) > 0
  assert password_hash != password  # Hash should be different from original


@pytest.mark.unit
def test_password_verification_empty_inputs():
  """Test password verification with empty inputs."""
  password_hash = PasswordService.hash_password("test")
  
  # Empty password should fail
  assert PasswordService.verify_password("", password_hash) is False
  
  # Empty hash should fail
  assert PasswordService.verify_password("test", "") is False
  
  # Both empty should fail
  assert PasswordService.verify_password("", "") is False


@pytest.mark.unit
def test_password_hash_consistency():
  """Test that same password can be verified multiple times."""
  password = "consistent_password"
  password_hash = PasswordService.hash_password(password)
  
  # Verify multiple times
  for _ in range(5):
    assert PasswordService.verify_password(password, password_hash) is True


@pytest.mark.unit
def test_password_special_characters():
  """Test password hashing and verification with special characters."""
  password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:,.<>?"
  password_hash = PasswordService.hash_password(password)
  
  assert PasswordService.verify_password(password, password_hash) is True


@pytest.mark.unit
def test_password_unicode_characters():
  """Test password hashing with unicode characters."""
  password = "пароль密码パスワード🔒"
  password_hash = PasswordService.hash_password(password)
  
  assert PasswordService.verify_password(password, password_hash) is True


# JWT Service Tests

@pytest.mark.unit
def test_jwt_access_token_generation():
  """Test JWT access token generation."""
  user_id = 123
  permissions = ["read", "write"]
  
  token = JWTService.create_access_token(user_id, permissions)
  
  assert token is not None
  assert len(token) > 0
  assert isinstance(token, str)


@pytest.mark.unit
def test_jwt_refresh_token_generation():
  """Test JWT refresh token generation."""
  user_id = 456
  
  token = JWTService.create_refresh_token(user_id)
  
  assert token is not None
  assert len(token) > 0
  assert isinstance(token, str)


@pytest.mark.unit
def test_jwt_access_token_validation():
  """Test JWT access token validation."""
  user_id = 789
  permissions = ["manage_users", "view_reports"]
  
  token = JWTService.create_access_token(user_id, permissions)
  payload = JWTService.verify_access_token(token)
  
  assert payload is not None
  assert payload["user_id"] == user_id
  assert payload["permissions"] == permissions
  assert payload["type"] == "access"


@pytest.mark.unit
def test_jwt_refresh_token_validation():
  """Test JWT refresh token validation."""
  user_id = 101112
  
  token = JWTService.create_refresh_token(user_id)
  payload = JWTService.verify_refresh_token(token)
  
  assert payload is not None
  assert payload["user_id"] == user_id
  assert payload["type"] == "refresh"


@pytest.mark.unit
def test_jwt_invalid_token_handling():
  """Test handling of invalid JWT tokens."""
  invalid_token = "invalid.jwt.token"
  
  assert JWTService.verify_access_token(invalid_token) is None
  assert JWTService.verify_refresh_token(invalid_token) is None


@pytest.mark.unit
def test_jwt_expired_token_handling():
  """Test handling of expired JWT tokens."""
  user_id = 131415
  
  # Create token with negative expiration (already expired)
  expired_token = JWTService.create_access_token(
    user_id, 
    ["test"], 
    expires_delta=timedelta(seconds=-1)
  )
  
  # Verification should return None for expired token
  assert JWTService.verify_access_token(expired_token) is None


@pytest.mark.unit
def test_jwt_token_expiration_times():
  """Test JWT token expiration times are set correctly."""
  user_id = 161718
  
  access_token = JWTService.create_access_token(user_id, ["test"])
  refresh_token = JWTService.create_refresh_token(user_id)
  
  access_payload = JWTService.verify_access_token(access_token)
  refresh_payload = JWTService.verify_refresh_token(refresh_token)
  
  # Check that expiration times exist and are in the future
  assert "exp" in access_payload
  assert "exp" in refresh_payload
  
  access_exp = datetime.fromtimestamp(access_payload["exp"], tz=timezone.utc)
  refresh_exp = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)
  
  now = datetime.now(timezone.utc)
  assert access_exp > now
  assert refresh_exp > now
  assert refresh_exp > access_exp  # Refresh should expire later


@pytest.mark.unit
def test_jwt_wrong_token_type_validation():
  """Test that access/refresh tokens are validated correctly."""
  user_id = 192021
  
  access_token = JWTService.create_access_token(user_id, ["test"])
  refresh_token = JWTService.create_refresh_token(user_id)
  
  # Access token should not validate as refresh token
  assert JWTService.verify_refresh_token(access_token) is None
  
  # Refresh token should not validate as access token
  assert JWTService.verify_access_token(refresh_token) is None


# Session Service Tests

@pytest.mark.asyncio
@pytest.mark.unit
async def test_session_creation(test_db_session):
  """Test session creation with refresh token."""
  user = User(
    email="session@example.com",
    password_hash="hashed_password",
    first_name="Session",
    last_name="User"
  )
  
  test_db_session.add(user)
  await test_db_session.commit()
  await test_db_session.refresh(user)
  
  refresh_token = "test_refresh_token_123"
  ip_address = "192.168.1.1"
  user_agent = "Test Browser"
  
  session = await SessionService.create_session(
    test_db_session,
    user.id,
    refresh_token,
    ip_address,
    user_agent
  )
  
  assert session is not None
  assert session.user_id == user.id
  assert session.refresh_token == refresh_token
  assert session.ip_address == ip_address
  assert session.user_agent == user_agent
  assert session.is_revoked is False
  now = datetime.now(timezone.utc)
  # Convert session.expires_at to timezone-aware if it's naive
  expires_at = session.expires_at
  if expires_at.tzinfo is None:
    expires_at = expires_at.replace(tzinfo=timezone.utc)
  assert expires_at > now


@pytest.mark.asyncio
@pytest.mark.unit
async def test_session_retrieval(test_db_session):
  """Test session retrieval by refresh token."""
  user = User(
    email="retrieve@example.com",
    password_hash="hashed_password",
    first_name="Retrieve",
    last_name="User"
  )
  
  test_db_session.add(user)
  await test_db_session.commit()
  await test_db_session.refresh(user)
  
  refresh_token = "retrieve_token_456"
  
  # Create session
  session = await SessionService.create_session(
    test_db_session,
    user.id,
    refresh_token
  )
  
  # Retrieve session
  retrieved_session = await SessionService.get_session_by_token(
    test_db_session,
    refresh_token
  )
  
  assert retrieved_session is not None
  assert retrieved_session.id == session.id
  assert retrieved_session.refresh_token == refresh_token


@pytest.mark.asyncio
@pytest.mark.unit
async def test_session_revocation(test_db_session):
  """Test session revocation."""
  user = User(
    email="revoke@example.com",
    password_hash="hashed_password",
    first_name="Revoke",
    last_name="User"
  )
  
  test_db_session.add(user)
  await test_db_session.commit()
  await test_db_session.refresh(user)
  
  refresh_token = "revoke_token_789"
  
  # Create session
  session = await SessionService.create_session(
    test_db_session,
    user.id,
    refresh_token
  )
  
  # Revoke session
  revoked = await SessionService.revoke_session(
    test_db_session,
    refresh_token
  )
  
  assert revoked is True
  
  # Verify session is revoked
  retrieved_session = await SessionService.get_session_by_token(
    test_db_session,
    refresh_token
  )
  
  assert retrieved_session.is_revoked is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_session_cleanup_expired(test_db_session):
  """Test cleanup of expired sessions."""
  user = User(
    email="cleanup@example.com",
    password_hash="hashed_password",
    first_name="Cleanup",
    last_name="User"
  )
  
  test_db_session.add(user)
  await test_db_session.commit()
  await test_db_session.refresh(user)
  
  # Create expired session
  expired_session = UserSession(
    user_id=user.id,
    refresh_token="expired_token",
    expires_at=datetime.now(timezone.utc) - timedelta(days=1)
  )
  
  test_db_session.add(expired_session)
  await test_db_session.commit()
  
  # Clean up expired sessions
  cleaned_count = await SessionService.cleanup_expired_sessions(test_db_session)
  
  assert cleaned_count > 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_session_validation(test_db_session):
  """Test session validation (not expired and not revoked)."""
  user = User(
    email="validate@example.com",
    password_hash="hashed_password",
    first_name="Validate",
    last_name="User"
  )
  
  test_db_session.add(user)
  await test_db_session.commit()
  await test_db_session.refresh(user)
  
  refresh_token = "validate_token_101112"
  
  # Create valid session
  session = await SessionService.create_session(
    test_db_session,
    user.id,
    refresh_token
  )
  
  # Validate session
  is_valid = await SessionService.is_session_valid(
    test_db_session,
    refresh_token
  )
  
  assert is_valid is True
  
  # Revoke and test again
  await SessionService.revoke_session(test_db_session, refresh_token)
  
  is_valid_after_revoke = await SessionService.is_session_valid(
    test_db_session,
    refresh_token
  )
  
  assert is_valid_after_revoke is False