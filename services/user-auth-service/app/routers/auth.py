"""
Authentication API endpoints for user registration, login, token refresh, and logout.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import Annotated, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.role import Role, UserRole, UserSession
from app.services.password_service import PasswordService
from app.services.jwt_service import JWTService
from app.services.session_service import SessionService
from app.services.account_lockout_service import AccountLockoutService
from app.services.messaging_service import get_messaging_service
from app.schemas.auth import (
    UserRegistrationRequest, 
    UserLoginRequest, 
    TokenRefreshRequest, 
    LogoutRequest,
    AuthResponse, 
    TokenResponse, 
    MessageResponse, 
    UserResponse,
    CurrentUser,
    UpdateProfileRequest,
    ChangePasswordRequest,
    ChangeEmailRequest,
    UserPermissionsResponse,
    AdminCreateUserRequest,
    AdminUserResponse,
    AdminUserListResponse,
    AdminAssignRoleRequest,
    AdminRemoveRoleRequest,
    AdminUserStatusRequest
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()


# Dependency for getting current user from access token
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> CurrentUser:
    """
    Dependency to extract and validate current user from access token.
    """
    token = credentials.credentials
    
    # Verify access token
    payload = JWTService.verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    permissions = payload.get("permissions", [])
    
    # Get user from database to verify existence and active status
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return CurrentUser(
        user_id=user.id,
        email=user.email,
        permissions=permissions
    )


# Dependency for admin permission check
async def get_admin_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> CurrentUser:
    """
    Dependency to ensure current user has admin permissions.
    """
    if "manage_users" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required"
        )
    return current_user

# Alias for consistency
require_admin = get_admin_user


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password"
)
async def register_user(
    user_data: UserRegistrationRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **password**: Strong password (min 8 characters)
    - **first_name**: User's first name
    - **last_name**: User's last name
    
    Returns the user data along with access and refresh tokens.
    """
    
    # Check if email already exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered"
        )
    
    # Validate password with comprehensive policy enforcement
    user_context = {
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "name": f"{user_data.first_name} {user_data.last_name}"
    }
    
    validation_result = PasswordService.validate_password_policy(
        user_data.password, user_context
    )
    
    if not validation_result["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password does not meet policy requirements: {'; '.join(validation_result['feedback'])}"
        )
    
    # Hash password
    password_hash = PasswordService.hash_password(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Assign default "user" role
    stmt = select(Role).where(Role.name == "user")
    result = await db.execute(stmt)
    user_role = result.scalar_one_or_none()
    
    if user_role:
        user_role_assignment = UserRole(
            user_id=new_user.id,
            role_id=user_role.id
        )
        db.add(user_role_assignment)
        await db.commit()
    
    # Get user permissions
    permissions = await new_user.get_permissions(db)
    
    # Generate tokens
    access_token = JWTService.create_access_token(new_user.id, permissions)
    refresh_token = JWTService.create_refresh_token(new_user.id)
    
    # Create session
    await SessionService.create_session(
        db,
        new_user.id,
        refresh_token
    )
    
    # Add initial password to history
    await PasswordService.add_to_password_history(db, new_user.id, password_hash)
    
    # Publish user created event
    messaging_service = await get_messaging_service()
    if messaging_service:
        user_data = {
            "id": new_user.id,
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at.isoformat() if new_user.created_at else None
        }
        await messaging_service.publish_user_created(
            user_id=new_user.id,
            user_data=user_data
        )
    
    return AuthResponse(
        user=UserResponse.model_validate(new_user),
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login user",
    description="Authenticate user with email and password"
)
async def login_user(
    login_data: UserLoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Authenticate user and return tokens.
    
    - **email**: User's registered email address
    - **password**: User's password
    
    Returns the user data along with access and refresh tokens.
    Implements account lockout protection against brute force attacks.
    """
    
    # Find user by email
    stmt = select(User).where(User.email == login_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # If user doesn't exist, still check for account lockout attempts on email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check account lockout status first
    lockout_status = await AccountLockoutService.check_account_lockout(db, user, request)
    if lockout_status["is_locked"]:
        remaining_minutes = int(lockout_status["remaining_time"].total_seconds() / 60) if lockout_status["remaining_time"] else 0
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked due to multiple failed login attempts. Try again in {remaining_minutes} minutes.",
            headers={
                "X-Account-Locked": "true",
                "X-Lockout-Remaining-Minutes": str(remaining_minutes),
                "Retry-After": str(remaining_minutes * 60)
            }
        )
    
    # Verify password
    if not PasswordService.verify_password(login_data.password, user.password_hash):
        # Handle failed login attempt
        lockout_result = await AccountLockoutService.handle_failed_login(
            db, user, "Invalid password", request
        )
        
        if lockout_result["account_locked"]:
            lockout_minutes = lockout_result["lockout_duration_minutes"]
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked after {lockout_result['failed_attempts']} failed attempts. Try again in {lockout_minutes} minutes.",
                headers={
                    "X-Account-Locked": "true",
                    "X-Failed-Attempts": str(lockout_result["failed_attempts"]),
                    "X-Lockout-Duration-Minutes": str(lockout_minutes),
                    "Retry-After": str(lockout_minutes * 60)
                }
            )
        else:
            remaining_attempts = lockout_result["max_attempts"] - lockout_result["failed_attempts"]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid email or password. {remaining_attempts} attempts remaining before account lockout.",
                headers={
                    "X-Failed-Attempts": str(lockout_result["failed_attempts"]),
                    "X-Remaining-Attempts": str(remaining_attempts)
                }
            )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Handle successful login (resets failed attempts)
    await AccountLockoutService.handle_successful_login(db, user, request)
    
    # Get user permissions
    permissions = await user.get_permissions(db)
    
    # Generate tokens
    access_token = JWTService.create_access_token(user.id, permissions)
    refresh_token = JWTService.create_refresh_token(user.id)
    
    # Create session
    await SessionService.create_session(
        db,
        user.id,
        refresh_token
    )
    
    # Publish user logged in event
    messaging_service = await get_messaging_service()
    if messaging_service:
        login_data = {
            "user_id": user.id,
            "email": user.email,
            "login_time": datetime.utcnow().isoformat(),
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        }
        await messaging_service.publish_user_logged_in(
            user_id=user.id,
            login_data=login_data
        )
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get new access token using valid refresh token"
)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Refresh access token using a valid refresh token.
    
    - **refresh_token**: Valid refresh token from login or previous refresh
    
    Returns new access and refresh tokens.
    """
    
    # Verify refresh token
    payload = JWTService.verify_refresh_token(refresh_data.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Verify session is still valid
    is_valid = await SessionService.is_session_valid(db, refresh_data.refresh_token)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked or expired"
        )
    
    user_id = payload["user_id"]
    
    # Get user and permissions
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    permissions = await user.get_permissions(db)
    
    # Generate new tokens
    new_access_token = JWTService.create_access_token(user.id, permissions)
    new_refresh_token = JWTService.create_refresh_token(user.id)
    
    # Revoke old session and create new one
    await SessionService.revoke_session(db, refresh_data.refresh_token)
    await SessionService.create_session(db, user.id, new_refresh_token)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout user",
    description="Revoke refresh token and end user session"
)
async def logout_user(
    logout_data: LogoutRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Logout user by revoking their refresh token.
    
    - **refresh_token**: Refresh token to revoke
    
    Returns success message.
    """
    
    # Verify refresh token format (but allow revocation even if expired)
    payload = JWTService.verify_refresh_token(logout_data.refresh_token)
    if payload is None:
        # Try to extract user_id without verification for logging purposes
        user_id = JWTService.extract_user_id(logout_data.refresh_token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token format"
            )
    
    # Attempt to revoke session
    revoked = await SessionService.revoke_session(db, logout_data.refresh_token)
    
    if not revoked:
        # Token might already be revoked or not exist, but we'll return success
        # to prevent information leakage about token existence
        pass
    
    return MessageResponse(message="User successfully logged out")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information"
)
async def get_current_user_info(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get current authenticated user's information.
    
    Requires valid access token in Authorization header.
    
    Returns user profile data.
    """
    
    # Get full user data from database
    stmt = select(User).where(User.id == current_user.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create response with permissions
    user_dict = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "permissions": current_user.permissions
    }
    
    return UserResponse(**user_dict)


@router.post(
    "/logout-all",
    response_model=MessageResponse,
    summary="Logout from all devices",
    description="Revoke all refresh tokens for current user"
)
async def logout_all_devices(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Logout user from all devices by revoking all sessions.
    
    Requires valid access token in Authorization header.
    
    Returns success message with count of revoked sessions.
    """
    
    # Revoke all user sessions
    revoked_count = await SessionService.revoke_all_user_sessions(db, current_user.user_id)
    
    return MessageResponse(
        message=f"Successfully logged out from {revoked_count} device(s)"
    )


@router.post(
    "/validate-token",
    summary="Validate JWT token",
    description="Validate a JWT token and return user information"
)
async def validate_token(
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
):
    """
    Validate JWT token and return user information.
    
    This endpoint is used by other services to validate tokens
    and get user information for authorization.
    
    Returns the user data if token is valid.
    """
    return {
        "id": current_user.user_id,
        "email": current_user.email,
        "is_active": True,  # get_current_user already verified this
        "permissions": current_user.permissions
    }


@router.get(
    "/debug-token",
    summary="Debug token parsing",
    description="Debug endpoint to test token parsing"
)
async def debug_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """Debug endpoint to test raw token parsing."""
    try:
        token = credentials.credentials
        payload = JWTService.verify_access_token(token)
        return {
            "token_valid": payload is not None,
            "payload": payload,
            "token_length": len(token) if token else 0
        }
    except Exception as e:
        return {
            "error": str(e),
            "token_present": bool(credentials),
            "credentials_str": str(credentials) if credentials else None
        }


@router.get(
    "/debug-user",
    summary="Debug user lookup",
    description="Debug endpoint to test user database lookup"
)
async def debug_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Debug endpoint to test user database lookup."""
    try:
        token = credentials.credentials
        payload = JWTService.verify_access_token(token)
        
        if payload is None:
            return {"error": "Token verification failed"}
        
        user_id = payload.get("user_id")
        
        # Get user from database
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        return {
            "user_id_from_token": user_id,
            "user_found": user is not None,
            "user_is_active": user.is_active if user else None,
            "user_email": user.email if user else None,
            "user_verified": user.is_verified if user else None
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }


@router.get(
    "/debug-dependency",
    summary="Debug get_current_user dependency",
    description="Debug endpoint using get_current_user dependency"
)
async def debug_dependency(
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
):
    """Debug endpoint using the actual get_current_user dependency."""
    return {
        "success": True,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "permissions": current_user.permissions
    }


# Profile Management Endpoints

@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update current user's profile information"
)
async def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update current user's profile information.
    
    - **first_name**: New first name (optional)
    - **last_name**: New last name (optional)
    
    Only provided fields will be updated.
    """
    
    # Get user from database
    stmt = select(User).where(User.id == current_user.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update only provided fields
    if profile_data.first_name is not None:
        user.first_name = profile_data.first_name
    
    if profile_data.last_name is not None:
        user.last_name = profile_data.last_name
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.get(
    "/permissions",
    response_model=UserPermissionsResponse,
    summary="Get user permissions",
    description="Get current user's permissions and roles"
)
async def get_user_permissions(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get current user's permissions and roles.
    
    Returns the complete list of permissions and role names for the authenticated user.
    """
    
    # Get user with roles
    stmt = select(User).where(User.id == current_user.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user permissions and roles
    permissions = await user.get_permissions(db)
    
    # Get role names
    stmt = select(Role.name).join(UserRole).where(UserRole.user_id == user.id)
    result = await db.execute(stmt)
    role_names = [row[0] for row in result.fetchall()]
    
    return UserPermissionsResponse(
        user_id=user.id,
        permissions=permissions,
        roles=role_names
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change current user's password"
)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Change current user's password.
    
    - **current_password**: Current password for verification
    - **new_password**: New password (must meet strength requirements)
    
    Requires current password verification for security.
    """
    
    # Get user from database
    stmt = select(User).where(User.id == current_user.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not PasswordService.verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password with comprehensive policy enforcement
    user_context = {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "name": user.full_name
    }
    
    validation_result = PasswordService.validate_password_policy(
        password_data.new_password, user_context
    )
    
    if not validation_result["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password does not meet policy requirements: {'; '.join(validation_result['feedback'])}"
        )
    
    # Check password history
    history_ok = await PasswordService.check_password_history(
        db, user.id, password_data.new_password
    )
    
    if not history_ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password has been used recently. Please choose a different password."
        )
    
    # Hash new password
    new_password_hash = PasswordService.hash_password(password_data.new_password)
    
    # Add current password to history before updating
    await PasswordService.add_to_password_history(db, user.id, user.password_hash)
    
    # Update password
    user.password_hash = new_password_hash
    await db.commit()
    
    # Optionally revoke all user sessions to force re-login
    await SessionService.revoke_all_user_sessions(db, user.id)
    
    return MessageResponse(
        message="Password changed successfully. Please log in again."
    )


@router.post(
    "/change-email",
    response_model=UserResponse,
    summary="Change email address",
    description="Change current user's email address"
)
async def change_email(
    email_data: ChangeEmailRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Change current user's email address.
    
    - **new_email**: New email address (must be unique)
    - **password**: Current password for verification
    
    Requires password verification for security.
    """
    
    # Get user from database
    stmt = select(User).where(User.id == current_user.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify password
    if not PasswordService.verify_password(email_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect"
        )
    
    # Check if new email already exists
    stmt = select(User).where(User.email == email_data.new_email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user and existing_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already exists"
        )
    
    # Update email
    user.email = email_data.new_email
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


# Admin User Management Endpoints

admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])


@admin_router.get(
    "/users",
    response_model=AdminUserListResponse,
    summary="List all users",
    description="Get paginated list of all users with search functionality"
)
async def list_users(
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None
):
    """
    List all users with pagination and optional search.
    
    - **page**: Page number (starts from 1)
    - **per_page**: Number of users per page (max 100)
    - **search**: Optional search term for email or name
    
    Requires admin permissions (manage_users).
    """
    # Limit per_page to reasonable bounds
    per_page = min(max(per_page, 1), 100)
    offset = (page - 1) * per_page
    
    # Build base query
    query = select(User)
    count_query = select(func.count(User.id))
    
    # Add search filter if provided
    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            User.first_name.ilike(f"%{search}%"),
            User.last_name.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated users
    query = query.offset(offset).limit(per_page).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Convert to admin response format with roles
    admin_users = []
    for user in users:
        # Get user roles
        role_stmt = select(Role.name).join(UserRole).where(UserRole.user_id == user.id)
        role_result = await db.execute(role_stmt)
        role_names = [row[0] for row in role_result.fetchall()]
        
        admin_user_data = AdminUserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=role_names,
            last_login=None  # TODO: Add last_login tracking
        )
        admin_users.append(admin_user_data)
    
    total_pages = (total + per_page - 1) // per_page
    
    return AdminUserListResponse(
        users=admin_users,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@admin_router.get(
    "/users/{user_id}",
    response_model=AdminUserResponse,
    summary="Get user by ID",
    description="Get detailed information about a specific user"
)
async def get_user_by_id(
    user_id: int,
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get detailed information about a specific user.
    
    - **user_id**: User ID to retrieve
    
    Requires admin permissions (manage_users).
    """
    # Get user
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user roles
    role_stmt = select(Role.name).join(UserRole).where(UserRole.user_id == user.id)
    role_result = await db.execute(role_stmt)
    role_names = [row[0] for row in role_result.fetchall()]
    
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=role_names,
        last_login=None  # TODO: Add last_login tracking
    )


@admin_router.post(
    "/assign-role",
    response_model=MessageResponse,
    summary="Assign role to user",
    description="Assign a role to a user"
)
async def assign_role_to_user(
    role_data: AdminAssignRoleRequest,
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Assign a role to a user.
    
    - **user_id**: User ID to assign role to
    - **role_name**: Name of role to assign
    
    Requires admin permissions (manage_users and manage_roles).
    """
    if "manage_roles" not in admin_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role management permissions required"
        )
    
    # Get user
    user_stmt = select(User).where(User.id == role_data.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get role
    role_stmt = select(Role).where(Role.name == role_data.role_name)
    role_result = await db.execute(role_stmt)
    role = role_result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Check if user already has this role
    existing_stmt = select(UserRole).where(
        and_(UserRole.user_id == role_data.user_id, UserRole.role_id == role.id)
    )
    existing_result = await db.execute(existing_stmt)
    existing_assignment = existing_result.scalar_one_or_none()
    
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this role"
        )
    
    # Create role assignment
    user_role = UserRole(user_id=role_data.user_id, role_id=role.id)
    db.add(user_role)
    await db.commit()
    
    return MessageResponse(
        message=f"Successfully assigned role '{role_data.role_name}' to user"
    )


@admin_router.post(
    "/remove-role",
    response_model=MessageResponse,
    summary="Remove role from user",
    description="Remove a role from a user"
)
async def remove_role_from_user(
    role_data: AdminRemoveRoleRequest,
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Remove a role from a user.
    
    - **user_id**: User ID to remove role from
    - **role_name**: Name of role to remove
    
    Requires admin permissions (manage_users and manage_roles).
    """
    if "manage_roles" not in admin_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role management permissions required"
        )
    
    # Get role
    role_stmt = select(Role).where(Role.name == role_data.role_name)
    role_result = await db.execute(role_stmt)
    role = role_result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Find and remove role assignment
    assignment_stmt = select(UserRole).where(
        and_(UserRole.user_id == role_data.user_id, UserRole.role_id == role.id)
    )
    assignment_result = await db.execute(assignment_stmt)
    assignment = assignment_result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have this role"
        )
    
    # Remove assignment
    await db.delete(assignment)
    await db.commit()
    
    return MessageResponse(
        message=f"Successfully removed role '{role_data.role_name}' from user"
    )


@admin_router.post(
    "/user-status",
    response_model=AdminUserResponse,
    summary="Update user status",
    description="Activate or deactivate a user account"
)
async def update_user_status(
    status_data: AdminUserStatusRequest,
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update user active status.
    
    - **user_id**: User ID to update
    - **is_active**: New active status
    
    Requires admin permissions (manage_users).
    """
    # Get user
    stmt = select(User).where(User.id == status_data.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update status
    user.is_active = status_data.is_active
    await db.commit()
    await db.refresh(user)
    
    # If deactivating, revoke all user sessions
    if not status_data.is_active:
        await SessionService.revoke_all_user_sessions(db, user.id)
    
    # Get user roles for response
    role_stmt = select(Role.name).join(UserRole).where(UserRole.user_id == user.id)
    role_result = await db.execute(role_stmt)
    role_names = [row[0] for row in role_result.fetchall()]
    
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=role_names,
        last_login=None
    )


@admin_router.post(
    "/create-user",
    response_model=AdminUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user account with specified roles"
)
async def create_user(
    user_data: AdminCreateUserRequest,
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Create a new user account.
    
    - **email**: User's email address (must be unique)
    - **password**: Initial password
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **is_active**: Whether account is active
    - **role_names**: List of role names to assign (optional)
    
    Requires admin permissions (manage_users).
    """
    # Check if email already exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already exists"
        )
    
    # Validate password strength
    if not PasswordService.is_password_strong(user_data.password):
        feedback = PasswordService.generate_password_strength_feedback(user_data.password)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password is too weak: {'; '.join(feedback)}"
        )
    
    # Hash password
    password_hash = PasswordService.hash_password(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_active=user_data.is_active
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Assign roles if provided
    assigned_roles = []
    if user_data.role_names:
        for role_name in user_data.role_names:
            role_stmt = select(Role).where(Role.name == role_name)
            role_result = await db.execute(role_stmt)
            role = role_result.scalar_one_or_none()
            
            if role:
                user_role = UserRole(user_id=new_user.id, role_id=role.id)
                db.add(user_role)
                assigned_roles.append(role_name)
        
        await db.commit()
    
    return AdminUserResponse(
        id=new_user.id,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        roles=assigned_roles,
        last_login=None
    )


@admin_router.delete(
    "/users/{user_id}",
    response_model=MessageResponse,
    summary="Delete user",
    description="Permanently delete a user account"
)
async def delete_user(
    user_id: int,
    admin_user: Annotated[CurrentUser, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Permanently delete a user account.
    
    - **user_id**: User ID to delete
    
    Warning: This action cannot be undone.
    Requires admin permissions (manage_users).
    """
    # Prevent admin from deleting themselves
    if user_id == admin_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Get user
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_email = user.email
    
    # Delete user (this will cascade delete user_roles and other related records)
    await db.delete(user)
    await db.commit()
    
    return MessageResponse(
        message=f"Successfully deleted user: {user_email}"
    )


# Account Lockout Management Endpoints
@admin_router.post(
    "/unlock-account/{user_id}",
    response_model=MessageResponse,
    summary="Unlock user account",
    description="Manually unlock a locked user account and reset failed attempts"
)
async def unlock_user_account(
    user_id: int,
    request: Request,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Manually unlock a user account and reset failed login attempts.
    Requires admin permissions.
    """
    # Get user
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if account is actually locked
    if not user.is_locked:
        return MessageResponse(
            message=f"User account {user.email} is not currently locked"
        )
    
    # Unlock account
    unlock_result = await AccountLockoutService.unlock_user_account(
        db, user, current_user.user_id, request
    )
    
    return MessageResponse(
        message=f"Successfully unlocked account for user: {user.email}"
    )


@admin_router.get(
    "/lockout-statistics",
    summary="Get account lockout statistics",
    description="Get statistics about account lockouts for security monitoring"
)
async def get_lockout_statistics(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    hours: Optional[int] = 24
):
    """
    Get account lockout statistics for security monitoring.
    Requires admin permissions.
    """
    if hours < 1 or hours > 168:  # Max 7 days
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hours must be between 1 and 168 (7 days)"
        )
    
    statistics = await AccountLockoutService.get_lockout_statistics(db, hours)
    return statistics


@admin_router.get(
    "/locked-accounts",
    summary="Get currently locked accounts",
    description="Get list of all currently locked user accounts"
)
async def get_locked_accounts(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get list of all currently locked user accounts.
    Requires admin permissions.
    """
    # Query for locked accounts
    stmt = select(User).where(
        and_(
            User.locked_until.isnot(None),
            User.locked_until > func.now()
        )
    ).order_by(User.locked_until.desc())
    
    result = await db.execute(stmt)
    locked_users = result.scalars().all()
    
    locked_accounts = []
    for user in locked_users:
        remaining_time = user.lockout_remaining_time
        locked_accounts.append({
            "user_id": user.id,
            "email": user.email,
            "failed_attempts": user.failed_login_attempts,
            "locked_until": user.locked_until.isoformat(),
            "remaining_minutes": int(remaining_time.total_seconds() / 60) if remaining_time else 0,
            "last_failed_login": user.last_failed_login.isoformat() if user.last_failed_login else None
        })
    
    return {
        "locked_accounts": locked_accounts,
        "total_locked": len(locked_accounts)
    }