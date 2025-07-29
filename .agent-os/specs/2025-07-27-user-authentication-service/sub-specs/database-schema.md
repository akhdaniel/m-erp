# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-07-27-user-authentication-service/spec.md

> Created: 2025-07-27
> Version: 1.0.0

## Schema Changes

### New Tables

**users**
- Primary table for user account information
- Stores authentication credentials and basic profile data
- Includes soft delete capability and audit timestamps

**user_sessions** 
- Tracks active user sessions and refresh tokens
- Enables session management and token revocation
- Stores device/browser information for security

**roles**
- Defines system roles (admin, user, manager, etc.)
- Supports hierarchical role inheritance
- Enables role-based access control

**user_roles**
- Many-to-many relationship between users and roles
- Allows users to have multiple roles
- Includes assignment timestamps and assigned_by tracking

## Database Specifications

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_created_at ON users(created_at);
```

### User Sessions Table
```sql
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    is_revoked BOOLEAN DEFAULT false
);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(refresh_token);
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);
```

### Roles Table
```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_roles_name ON roles(name);
CREATE INDEX idx_roles_permissions ON roles USING GIN (permissions);
```

### User Roles Table
```sql
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER REFERENCES users(id),
    UNIQUE(user_id, role_id)
);

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
```

## Rationale

**Email as Username**: Using email as the primary identifier simplifies user experience and eliminates the need for separate username management.

**Soft Delete**: The `deleted_at` field enables soft deletion to maintain referential integrity while allowing user account recovery.

**JSONB Permissions**: Storing permissions as JSONB provides flexibility for different permission structures while maintaining query performance.

**Session Tracking**: Separate session table enables proper token management, device tracking, and security auditing.

**Performance Considerations**: Strategic indexes on commonly queried fields (email, active status, tokens) ensure fast authentication operations.

**Security Features**: Password hash storage, session expiration, and revocation capabilities provide comprehensive security controls.