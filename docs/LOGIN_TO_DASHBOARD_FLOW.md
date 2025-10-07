# XERPIUM ERP System - Login to Dashboard Flow

## Overview
This document describes the complete user authentication, session management, menu loading, and dashboard display flow in the XERPIUM microservices ERP system.

## 1. User Authentication Flow

### 1.1 Login Process
1. **User Initiates Login**:
   - User accesses `/login` route in the UI Service
   - Login form displays with email/password fields

2. **Credentials Submission**:
   - User enters email and password
   - UI Service makes POST request to `/api/auth/login` endpoint in User Authentication Service

3. **User Authentication Service Processing**:
   - Verifies user exists by email
   - Checks account lockout status using AccountLockoutService
   - Verifies password using PasswordService
   - Ensures user account is active
   - Handles failed login attempts and account lockout
   - On success, generates JWT tokens (access and refresh)

4. **Token Creation**:
   - Creates access token with user permissions valid for 15 minutes
   - Creates refresh token valid for 7 days
   - Stores refresh token in database as UserSession

5. **Response to UI Service**:
   - Returns AuthResponse with user data and tokens
   - Publishes user_logged_in event to messaging system

### 1.2 Session Management
1. **Token Storage in UI**:
   - UI Service stores tokens in browser storage
   - Creates authStore with user data and tokens

2. **Session Persistence**:
   - Access token stored in memory for API requests
   - Refresh token stored securely for automatic token refresh

3. **Token Validation**:
   - Each API request includes access token in Authorization header
   - Services validate tokens with User Authentication Service

## 2. Menu Loading Process

### 2.1 Menu Initialization
1. **Router Navigation Guard**:
   - Vue Router checks authentication status in `beforeEach` guard
   - If authenticated, calls menuStore.fetchMenus()

2. **API Request to Menu Access Service**:
   - UI Service makes GET request to `/api/v1/menus/tree`
   - Includes Authorization header with access token

3. **Menu Access Service Authentication**:
   - AuthenticationMiddleware validates token using auth_client
   - Validates against User Authentication Service (`/api/validate/user-token`)

### 2.2 Menu Processing in Menu Access Service
1. **User Permissions Retrieval**:
   - Extracts user permissions from validated token
   - Filters menus based on user permissions

2. **Menu Hierarchy Building**:
   - Retrieves all active menus from database
   - Builds hierarchical tree structure
   - Filters menus based on required permissions
   - Returns MenuTreeResponse with hierarchical menu structure

3. **Response to UI Service**:
   - Returns complete menu tree with user permissions

### 2.3 Menu Storage in UI
1. **Menu Store Population**:
   - UI Service stores retrieved menus in menuStore
   - Organizes menus by service and hierarchy
   - Updates reactive state for dynamic route generation

## 3. Dynamic Route Generation

### 3.1 Route Creation Logic
1. **Router Guard Processing**:
   - Navigation guard calls `addDynamicRoutes()` when user authenticates
   - Generates dynamic Vue routes from menu structure
   - For dashboard routes: uses DynamicDashboard.vue component
   - For other routes: uses DynamicView.vue component

2. **Route Patterns Generated**:
   - List routes: `/sales/transactions`
   - Detail routes: `/sales/transactions/:id`
   - Edit routes: `/sales/transactions/:id/edit`
   - Create routes: `/sales/transactions/new`

3. **Router Integration**:
   - Adds dynamic routes to Vue Router using `router.addRoute()`
   - Maintains route protection with authentication requirements

## 4. Dashboard Display Process

### 4.1 Default Route Handling
1. **Route Redirect**:
   - Root path `/` redirects to `/dashboard` by router configuration
   - `{ path: '/', redirect: '/dashboard' }`

2. **Dashboard View Loading**:
   - DashboardView.vue component loads
   - Displays default dashboard interface

### 4.2 Dynamic Dashboard Loading
1. **UI Schema Retrieval**:
   - For service-specific dashboards, DynamicDashboard.vue calls UI schema endpoints
   - Retrieves dashboard configuration from appropriate service (e.g., `/ui-schemas/dashboard`)

2. **Component Rendering**:
   - Generic UI components render dashboard based on JSON schema
   - Loads widgets, metrics, and charts from service-provided configurations

3. **Dashboard Data Fetching**:
   - Dashboard components make API calls to data endpoints
   - Real-time updates through messaging system

## 5. Security and Authentication Validation

### 5.1 Continuous Authentication
1. **Token Expiration Handling**:
   - UI Service monitors token expiration
   - Automatically refreshes access token using refresh token
   - Makes POST request to `/api/auth/refresh` with refresh token

2. **Permission Validation**:
   - Each route validates required permissions
   - Navigation guard checks `authStore.hasPermission()`
   - Redirects to dashboard if insufficient permissions

### 5.2 Service Communication Security
1. **Inter-service Authentication**:
   - Menu Access Service validates tokens with User Authentication Service
   - Services use service-to-service authentication tokens
   - All inter-service communication secured with JWT tokens

## 6. Data Flow Summary

```
User Login
    ↓
UI Service → User Auth Service (credentials)
    ↓
User Auth Service (validates, creates tokens)
    ↓
Response with tokens → UI Service
    ↓
UI Service stores tokens in authStore
    ↓
UI Service requests menus → Menu Access Service (with token)
    ↓
Menu Access Service validates token, retrieves user permissions
    ↓
Menu Access Service returns filtered menu tree
    ↓
UI Service stores menus in menuStore
    ↓
Vue Router generates dynamic routes from menus
    ↓
User navigates to /dashboard (default redirect)
    ↓
DashboardView.vue loads and renders dashboard interface
```

## 7. Key Components Involved

### 7.1 Frontend Components
- **AuthStore**: Manages user authentication state and tokens
- **MenuStore**: Stores and manages menu data
- **AppLayout.vue**: Main application layout with menu navigation
- **Vue Router**: Handles route management and navigation guards
- **DynamicView/Dashboard**: Renders service-provided UI schemas

### 7.2 Backend Services
- **User Authentication Service**: Handles login, token creation/validation
- **Menu Access Service**: Manages menu permissions and retrieval
- **UI Registry Service**: Stores and provides UI component schemas
- **Individual Business Services**: Provide service-specific UI schemas

### 7.3 Middleware/Infrastructure
- **AuthenticationMiddleware**: Validates tokens and extracts user data
- **Kong API Gateway**: Routes requests and handles security
- **Redis**: Stores JWT tokens and session information
- **Database**: Stores users, permissions, and menu configurations