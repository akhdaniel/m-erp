"""
Pydantic schemas for authentication API requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# Request Schemas

class UserRegistrationRequest(BaseModel):
    """Schema for user registration request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="User's password")
    first_name: str = Field(..., min_length=1, max_length=50, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="User's last name")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!",
                "first_name": "John",
                "last_name": "Doe"
            }
        }
    }


class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }
    }


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., description="Valid refresh token")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


class LogoutRequest(BaseModel):
    """Schema for logout request."""
    refresh_token: str = Field(..., description="Refresh token to revoke")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


# Response Schemas

class UserResponse(BaseModel):
    """Schema for user data in API responses."""
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }
    }


class TokenResponse(BaseModel):
    """Schema for token-only responses."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class AuthResponse(BaseModel):
    """Schema for authentication responses that include user data and tokens."""
    user: UserResponse
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:00:00Z"
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    message: str = Field(..., description="Response message")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "User successfully logged out"
            }
        }
    }


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str = Field(..., description="Error detail message")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Invalid credentials"
            }
        }
    }


# Profile Management Schemas

class UpdateProfileRequest(BaseModel):
    """Schema for updating user profile."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="User's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="User's last name")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "John",
                "last_name": "Doe"
            }
        }
    }


class ChangePasswordRequest(BaseModel):
    """Schema for changing user password."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewSecurePassword123!"
            }
        }
    }


class ChangeEmailRequest(BaseModel):
    """Schema for changing user email."""
    new_email: EmailStr = Field(..., description="New email address")
    password: str = Field(..., description="Current password for verification")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "new_email": "newemail@example.com",
                "password": "CurrentPassword123!"
            }
        }
    }


class UserPermissionsResponse(BaseModel):
    """Schema for user permissions response."""
    user_id: int
    permissions: List[str] = Field(..., description="List of user permissions")
    roles: List[str] = Field(..., description="List of user role names")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "permissions": ["read", "write", "manage_users"],
                "roles": ["user", "admin"]
            }
        }
    }


# Admin Management Schemas

class AdminCreateUserRequest(BaseModel):
    """Schema for admin creating a new user."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="Initial password")
    first_name: str = Field(..., min_length=1, max_length=50, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="User's last name")
    is_active: bool = Field(default=True, description="Whether user account is active")
    role_names: Optional[List[str]] = Field(default=None, description="List of role names to assign")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
                "first_name": "New",
                "last_name": "User",
                "is_active": True,
                "role_names": ["user"]
            }
        }
    }


class AdminUserResponse(BaseModel):
    """Schema for admin user response with additional fields."""
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    roles: List[str] = Field(..., description="List of role names")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "roles": ["user", "admin"],
                "last_login": "2024-01-01T12:00:00Z"
            }
        }
    }


class AdminUserListResponse(BaseModel):
    """Schema for paginated user list response."""
    users: List[AdminUserResponse]
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of users per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "users": [],
                "total": 100,
                "page": 1,
                "per_page": 20,
                "total_pages": 5
            }
        }
    }


class AdminAssignRoleRequest(BaseModel):
    """Schema for admin role assignment."""
    user_id: int = Field(..., description="User ID to assign role to")
    role_name: str = Field(..., min_length=1, description="Role name to assign")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "role_name": "admin"
            }
        }
    }


class AdminRemoveRoleRequest(BaseModel):
    """Schema for admin role removal."""
    user_id: int = Field(..., description="User ID to remove role from")
    role_name: str = Field(..., min_length=1, description="Role name to remove")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "role_name": "admin"
            }
        }
    }


class AdminUserStatusRequest(BaseModel):
    """Schema for admin user status change."""
    user_id: int = Field(..., description="User ID to change status")
    is_active: bool = Field(..., description="New active status")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "is_active": False
            }
        }
    }


# Current user context (for dependency injection)

class CurrentUser(BaseModel):
    """Schema for current authenticated user context."""
    user_id: int
    email: str
    permissions: List[str]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "email": "user@example.com",
                "permissions": ["read", "write", "manage_users"]
            }
        }
    }