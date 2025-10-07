# XERPIUM ERP System - Login to Dashboard Flow

## Overview
This document describes the complete user authentication, session management, menu loading, and dashboard display flow in the XERPIUM microservices ERP system.

## 1. User Authentication Flow

### 1.1 Login Process
1. **User Initiates Login**:
   - File: `services/ui-service/src/views/auth/LoginView.vue`
   - User accesses `/login` route in the UI Service
   - Login form displays with email/password fields

2. **Credentials Submission**:
   - File: `services/ui-service/src/views/auth/LoginView.vue`
   - User enters email and password
   - UI Service makes POST request to `/api/auth/login` endpoint in User Authentication Service

3. **User Authentication Service Processing**:
   - File: `services/user-auth-service/app/routers/auth.py`
   - Verifies user exists by email
   - Checks account lockout status using AccountLockoutService
   - Verifies password using PasswordService
   - Ensures user account is active
   - Handles failed login attempts and account lockout
   - On success, generates JWT tokens (access and refresh)

4. **Token Creation**:
   - File: `services/user-auth-service/app/services/jwt_service.py`
   - Creates access token with user permissions valid for 15 minutes
   - Creates refresh token valid for 7 days
   - Stores refresh token in database as UserSession

5. **Response to UI Service**:
   - File: `services/user-auth-service/app/routers/auth.py`
   - Returns AuthResponse with user data and tokens
   - Publishes user_logged_in event to messaging system

### 1.2 Session Management
1. **Token Storage in UI**:
   - File: `services/ui-service/src/stores/auth.ts`
   - UI Service stores tokens in browser storage
   - Creates authStore with user data and tokens

2. **Session Persistence**:
   - File: `services/ui-service/src/stores/auth.ts`
   - Access token stored in memory for API requests
   - Refresh token stored securely for automatic token refresh

3. **Token Validation**:
   - File: `services/ui-service/src/services/api.ts`
   - Each API request includes access token in Authorization header
   - Services validate tokens with User Authentication Service

## 2. Menu Loading Process

### 2.1 Menu Initialization
1. **Router Navigation Guard**:
   - File: `services/ui-service/src/router/index.ts`
   - Vue Router checks authentication status in `beforeEach` guard
   - If authenticated, calls menuStore.fetchMenus()

2. **API Request to Menu Access Service**:
   - File: `services/ui-service/src/stores/menu.ts`
   - UI Service makes GET request to `/api/v1/menus/tree`
   - Includes Authorization header with access token

3. **Menu Access Service Authentication**:
   - File: `services/menu-access-service/app/middleware/request_auth.py`
   - AuthenticationMiddleware validates token using auth_client
   - Validates against User Authentication Service (`/api/validate/user-token`)

### 2.2 Menu Processing in Menu Access Service
1. **User Permissions Retrieval**:
   - File: `services/menu-access-service/app/routers/menu.py`
   - Extracts user permissions from validated token
   - Filters menus based on user permissions

2. **Menu Hierarchy Building**:
   - File: `services/menu-access-service/app/services/menu.py`
   - Retrieves all active menus from database
   - Builds hierarchical tree structure
   - Filters menus based on required permissions
   - Returns MenuTreeResponse with hierarchical menu structure

3. **Response to UI Service**:
   - File: `services/menu-access-service/app/routers/menu.py`
   - Returns complete menu tree with user permissions

### 2.3 Menu Storage in UI
1. **Menu Store Population**:
   - File: `services/ui-service/src/stores/menu.ts`
   - UI Service stores retrieved menus in menuStore
   - Organizes menus by service and hierarchy
   - Updates reactive state for dynamic route generation

## 3. Dynamic Route Generation

### 3.1 Route Creation Logic
1. **Router Guard Processing**:
   - File: `services/ui-service/src/router/index.ts`
   - Navigation guard calls `addDynamicRoutes()` when user authenticates
   - Generates dynamic Vue routes from menu structure
   - For dashboard routes: uses DynamicDashboard.vue component
   - For other routes: uses DynamicView.vue component

2. **Route Patterns Generated**:
   - File: `services/ui-service/src/router/index.ts`
   - List routes: `/sales/transactions`
   - Detail routes: `/sales/transactions/:id`
   - Edit routes: `/sales/transactions/:id/edit`
   - Create routes: `/sales/transactions/new`

3. **Router Integration**:
   - File: `services/ui-service/src/router/index.ts`
   - Adds dynamic routes to Vue Router using `router.addRoute()`
   - Maintains route protection with authentication requirements

## 4. Dashboard Display Process

### 4.1 Default Route Handling
1. **Route Redirect**:
   - File: `services/ui-service/src/router/index.ts`
   - Root path `/` redirects to `/dashboard` by router configuration
   - `{ path: '/', redirect: '/dashboard' }`

2. **Dashboard View Loading**:
   - File: `services/ui-service/src/views/DashboardView.vue`
   - DashboardView.vue component loads
   - Displays default dashboard interface

### 4.2 Dynamic Dashboard Loading
1. **UI Schema Retrieval**:
   - File: `services/ui-service/src/views/DynamicDashboard.vue`
   - For service-specific dashboards, DynamicDashboard.vue calls UI schema endpoints
   - Retrieves dashboard configuration from appropriate service (e.g., `/ui-schemas/dashboard`)

2. **Component Rendering**:
   - File: `services/ui-service/src/components/generic/DynamicDashboard.vue`
   - Generic UI components render dashboard based on JSON schema
   - Loads widgets, metrics, and charts from service-provided configurations

3. **Dashboard Data Fetching**:
   - File: `services/ui-service/src/services/api.ts`
   - Dashboard components make API calls to data endpoints
   - Real-time updates through messaging system

## 5. Security and Authentication Validation

### 5.1 Continuous Authentication
1. **Token Expiration Handling**:
   - File: `services/ui-service/src/stores/auth.ts`
   - UI Service monitors token expiration
   - Automatically refreshes access token using refresh token
   - Makes POST request to `/api/auth/refresh` with refresh token

2. **Permission Validation**:
   - File: `services/ui-service/src/router/index.ts`
   - Each route validates required permissions
   - Navigation guard checks `authStore.hasPermission()`
   - Redirects to dashboard if insufficient permissions

### 5.2 Service Communication Security
1. **Inter-service Authentication**:
   - File: `services/menu-access-service/app/middleware/auth.py`
   - Menu Access Service validates tokens with User Authentication Service
   - Services use service-to-service authentication tokens
   - All inter-service communication secured with JWT tokens

## 6. Data Flow Summary

```
User Login
    ↓ (File: src/views/auth/LoginView.vue)
UI Service → User Auth Service (credentials)
    ↓ (File: app/routers/auth.py)
User Auth Service (validates, creates tokens)
    ↓ (File: app/services/jwt_service.py)
Response with tokens → UI Service
    ↓ (File: src/stores/auth.ts)
UI Service stores tokens in authStore
    ↓ (File: src/stores/menu.ts)
UI Service requests menus → Menu Access Service (with token)
    ↓ (File: app/middleware/request_auth.py)
Menu Access Service validates token, retrieves user permissions
    ↓ (File: app/services/menu.py)
Menu Access Service returns filtered menu tree
    ↓ (File: src/stores/menu.ts)
UI Service stores menus in menuStore
    ↓ (File: src/router/index.ts)
Vue Router generates dynamic routes from menus
    ↓ (File: src/views/DashboardView.vue)
User navigates to /dashboard (default redirect)
    ↓ (File: src/views/DynamicDashboard.vue)
DashboardView.vue loads and renders dashboard interface
```

## 7. Key Components Involved

### 7.1 Frontend Components
- **AuthStore**: Manages user authentication state and tokens (File: `services/ui-service/src/stores/auth.ts`)
- **MenuStore**: Stores and manages menu data (File: `services/ui-service/src/stores/menu.ts`)
- **AppLayout.vue**: Main application layout with menu navigation (File: `services/ui-service/src/components/AppLayout.vue`)
- **Vue Router**: Handles route management and navigation guards (File: `services/ui-service/src/router/index.ts`)
- **DynamicView/Dashboard**: Renders service-provided UI schemas (Files: `services/ui-service/src/views/DynamicView.vue`, `services/ui-service/src/views/DynamicDashboard.vue`)

### 7.2 Backend Services
- **User Authentication Service**: Handles login, token creation/validation (File: `services/user-auth-service/app/routers/auth.py`)
- **Menu Access Service**: Manages menu permissions and retrieval (File: `services/menu-access-service/app/routers/menu.py`)
- **UI Registry Service**: Stores and provides UI component schemas (Files: `services/ui-registry-service/app/routers/ui_schemas.py`)
- **Individual Business Services**: Provide service-specific UI schemas (Files: `services/*/api/ui_schemas.py`)

### 7.3 Middleware/Infrastructure
- **AuthenticationMiddleware**: Validates tokens and extracts user data (File: `services/menu-access-service/app/middleware/request_auth.py`)
- **Kong API Gateway**: Routes requests and handles security (Configuration in `docker-compose.yml`)
- **Redis**: Stores JWT tokens and session information (Used in `services/user-auth-service/app/services/session_service.py`)
- **Database**: Stores users, permissions, and menu configurations (Files: `services/*/app/models/*.py`)