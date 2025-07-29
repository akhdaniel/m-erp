# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-07-27-user-authentication-service/spec.md

> Created: 2025-07-27
> Version: 1.0.0

## Endpoints

### POST /auth/register

**Purpose:** Register a new user account
**Parameters:** 
- email (string, required): User's email address
- password (string, required): User's password (min 8 characters)
- first_name (string, required): User's first name
- last_name (string, required): User's last name

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-07-27T15:00:00Z"
  },
  "message": "User registered successfully"
}
```

**Errors:** 400 (validation), 409 (email exists)

### POST /auth/login

**Purpose:** Authenticate user and return JWT tokens
**Parameters:**
- email (string, required): User's email
- password (string, required): User's password

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "roles": ["user"]
  }
}
```

**Errors:** 401 (invalid credentials), 403 (account disabled)

### POST /auth/refresh

**Purpose:** Refresh access token using refresh token
**Parameters:**
- refresh_token (string, required): Valid refresh token

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

**Errors:** 401 (invalid/expired token)

### POST /auth/logout

**Purpose:** Invalidate user session and tokens
**Parameters:** None (requires Authorization header)
**Response:**
```json
{
  "message": "Logged out successfully"
}
```

**Errors:** 401 (invalid token)

### GET /auth/me

**Purpose:** Get current user profile information
**Parameters:** None (requires Authorization header)
**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "roles": ["user", "manager"],
  "permissions": ["read_users", "manage_partners"],
  "last_login": "2025-07-27T14:00:00Z"
}
```

**Errors:** 401 (invalid token)

### PUT /auth/me

**Purpose:** Update current user profile
**Parameters:**
- first_name (string, optional): Updated first name
- last_name (string, optional): Updated last name

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "updated_at": "2025-07-27T15:30:00Z"
  },
  "message": "Profile updated successfully"
}
```

**Errors:** 401 (invalid token), 400 (validation)

### POST /auth/change-password

**Purpose:** Change user password
**Parameters:**
- current_password (string, required): Current password
- new_password (string, required): New password (min 8 characters)

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

**Errors:** 401 (invalid token/password), 400 (validation)

## Admin Endpoints

### GET /admin/users

**Purpose:** List all users (admin only)
**Parameters:**
- page (int, optional): Page number (default: 1)
- per_page (int, optional): Items per page (default: 20)
- search (string, optional): Search by email/name

**Response:**
```json
{
  "users": [...],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "total_pages": 8
}
```

**Errors:** 401 (unauthorized), 403 (not admin)

### POST /admin/users

**Purpose:** Create new user (admin only)
**Parameters:**
- email, password, first_name, last_name (required)
- roles (array, optional): Role IDs to assign

**Response:**
```json
{
  "user": {...},
  "message": "User created successfully"
}
```

**Errors:** 401 (unauthorized), 403 (not admin), 400 (validation)

### PUT /admin/users/{user_id}

**Purpose:** Update user account (admin only)
**Parameters:**
- first_name, last_name (optional)
- is_active (boolean, optional): Enable/disable account
- roles (array, optional): Update user roles

**Response:**
```json
{
  "user": {...},
  "message": "User updated successfully"
}
```

**Errors:** 401 (unauthorized), 403 (not admin), 404 (not found)

### DELETE /admin/users/{user_id}

**Purpose:** Soft delete user account (admin only)
**Parameters:** None
**Response:**
```json
{
  "message": "User deleted successfully"
}
```

**Errors:** 401 (unauthorized), 403 (not admin), 404 (not found)

## Token Validation Endpoint

### POST /auth/verify

**Purpose:** Verify JWT token validity (for other microservices)
**Parameters:**
- token (string, required): JWT access token to verify

**Response:**
```json
{
  "valid": true,
  "user_id": 1,
  "permissions": ["read_users", "manage_partners"],
  "expires_at": "2025-07-27T15:15:00Z"
}
```

**Errors:** 400 (invalid token format), 401 (expired/invalid token)