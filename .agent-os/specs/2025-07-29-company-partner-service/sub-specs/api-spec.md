# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-07-29-company-partner-service/spec.md

> Created: 2025-07-29
> Version: 1.0.0

## Authentication & Authorization

All API endpoints require JWT authentication via the User Authentication Service. The service validates tokens by calling the auth service and extracts user company permissions for multi-company data isolation.

**Authorization Header:** `Bearer <jwt_token>`

**Company Context:** Most endpoints require a company_id parameter or use the user's default company from their JWT token claims.

## Company Management Endpoints

### GET /api/companies

**Purpose:** List companies accessible to the authenticated user
**Parameters:** 
- `limit` (optional): Number of companies to return (default: 50)
- `offset` (optional): Pagination offset (default: 0)
- `search` (optional): Search by company name or code

**Response:**
```json
{
  "companies": [
    {
      "id": 1,
      "name": "Acme Corporation",
      "legal_name": "Acme Corporation Inc.",
      "code": "ACME",
      "email": "info@acme.com",
      "phone": "+1-555-0123",
      "website": "https://acme.com",
      "currency": "USD",
      "timezone": "America/New_York",
      "is_active": true,
      "created_at": "2025-07-29T10:00:00Z",
      "updated_at": "2025-07-29T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**Errors:** 401 (Unauthorized), 403 (Insufficient permissions)

### POST /api/companies

**Purpose:** Create a new company (admin only)
**Parameters:** Company creation data in request body

**Request Body:**
```json
{
  "name": "New Company LLC",
  "legal_name": "New Company Limited Liability Company",
  "code": "NEWCO",
  "email": "contact@newcompany.com",
  "phone": "+1-555-0199",
  "website": "https://newcompany.com",
  "tax_id": "12-3456789",
  "street": "123 Business Ave",
  "city": "Business City",
  "state": "CA",
  "zip": "90210",
  "country": "USA",
  "currency": "USD",
  "timezone": "America/Los_Angeles"
}
```

**Response:** 201 Created with company object
**Errors:** 400 (Validation error), 401 (Unauthorized), 403 (Not admin), 409 (Code already exists)

### GET /api/companies/{company_id}

**Purpose:** Get specific company details
**Parameters:** `company_id` in URL path

**Response:** Single company object
**Errors:** 401 (Unauthorized), 403 (No access to company), 404 (Company not found)

### PUT /api/companies/{company_id}

**Purpose:** Update company information (admin only)
**Parameters:** `company_id` in URL path, update data in request body
**Response:** Updated company object
**Errors:** 400 (Validation error), 401 (Unauthorized), 403 (Not admin), 404 (Company not found)

### DELETE /api/companies/{company_id}

**Purpose:** Deactivate company (soft delete, admin only)
**Parameters:** `company_id` in URL path
**Response:** 204 No Content
**Errors:** 401 (Unauthorized), 403 (Not admin), 404 (Company not found)

## Partner Management Endpoints

### GET /api/companies/{company_id}/partners

**Purpose:** List partners for a specific company
**Parameters:**
- `company_id` in URL path
- `partner_type` (optional): Filter by customer/supplier/vendor
- `is_active` (optional): Filter active/inactive partners
- `search` (optional): Search by partner name or code
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "partners": [
    {
      "id": 1,
      "company_id": 1,
      "name": "ABC Supplier Co",
      "code": "ABC001",
      "partner_type": "supplier",
      "email": "orders@abcsupplier.com",
      "phone": "+1-555-0156",
      "is_customer": false,
      "is_supplier": true,
      "is_vendor": false,
      "is_active": true,
      "created_at": "2025-07-29T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**Errors:** 401 (Unauthorized), 403 (No access to company), 404 (Company not found)

### POST /api/companies/{company_id}/partners

**Purpose:** Create a new partner in the specified company
**Parameters:** `company_id` in URL path, partner data in request body

**Request Body:**
```json
{
  "name": "New Customer Inc",
  "code": "NEWCUST",
  "partner_type": "customer",
  "email": "billing@newcustomer.com",
  "phone": "+1-555-0177",
  "mobile": "+1-555-0178",
  "website": "https://newcustomer.com",
  "tax_id": "98-7654321",
  "industry": "Technology",
  "is_customer": true,
  "is_supplier": false,
  "is_vendor": false
}
```

**Response:** 201 Created with partner object
**Errors:** 400 (Validation error), 401 (Unauthorized), 403 (No access to company), 409 (Code already exists in company)

### GET /api/companies/{company_id}/partners/{partner_id}

**Purpose:** Get specific partner details with contacts and addresses
**Parameters:** `company_id` and `partner_id` in URL path

**Response:**
```json
{
  "id": 1,
  "company_id": 1,
  "name": "ABC Supplier Co",
  "code": "ABC001",
  "partner_type": "supplier",
  "email": "orders@abcsupplier.com",
  "phone": "+1-555-0156",
  "contacts": [
    {
      "id": 1,
      "name": "John Smith",
      "title": "Purchasing Manager",
      "email": "john.smith@abcsupplier.com",
      "phone": "+1-555-0157",
      "is_primary": true
    }
  ],
  "addresses": [
    {
      "id": 1,
      "address_type": "default",
      "street": "456 Supplier St",
      "city": "Supply City",
      "state": "TX",
      "zip": "75001",
      "country": "USA",
      "is_default": true
    }
  ],
  "is_active": true,
  "created_at": "2025-07-29T10:00:00Z"
}
```

**Errors:** 401 (Unauthorized), 403 (No access to company), 404 (Partner not found)

### PUT /api/companies/{company_id}/partners/{partner_id}

**Purpose:** Update partner information
**Parameters:** `company_id` and `partner_id` in URL path, update data in request body
**Response:** Updated partner object
**Errors:** 400 (Validation error), 401 (Unauthorized), 403 (No access), 404 (Partner not found)

### DELETE /api/companies/{company_id}/partners/{partner_id}

**Purpose:** Deactivate partner (soft delete)
**Parameters:** `company_id` and `partner_id` in URL path
**Response:** 204 No Content
**Errors:** 401 (Unauthorized), 403 (No access), 404 (Partner not found)

## Partner Contact Management

### POST /api/companies/{company_id}/partners/{partner_id}/contacts

**Purpose:** Add new contact to partner
**Parameters:** Company ID, partner ID in URL path, contact data in request body
**Response:** 201 Created with contact object
**Errors:** 400 (Validation error), 401 (Unauthorized), 403 (No access), 404 (Partner not found)

### PUT /api/companies/{company_id}/partners/{partner_id}/contacts/{contact_id}

**Purpose:** Update partner contact information
**Parameters:** Company ID, partner ID, contact ID in URL path, contact data in request body
**Response:** Updated contact object
**Errors:** 400 (Validation error), 401 (Unauthorized), 403 (No access), 404 (Contact not found)

### DELETE /api/companies/{company_id}/partners/{partner_id}/contacts/{contact_id}

**Purpose:** Delete partner contact
**Parameters:** Company ID, partner ID, contact ID in URL path
**Response:** 204 No Content
**Errors:** 401 (Unauthorized), 403 (No access), 404 (Contact not found)

## Partner Address Management

### POST /api/companies/{company_id}/partners/{partner_id}/addresses

**Purpose:** Add new address to partner
**Parameters:** Company ID, partner ID in URL path, address data in request body
**Response:** 201 Created with address object
**Errors:** 400 (Validation error), 401 (Unauthorized), 403 (No access), 404 (Partner not found)

### PUT /api/companies/{company_id}/partners/{partner_id}/addresses/{address_id}

**Purpose:** Update partner address information
**Parameters:** Company ID, partner ID, address ID in URL path, address data in request body
**Response:** Updated address object
**Errors:** 400 (Validation error), 401 (Unauthorized), 403 (No access), 404 (Address not found)

### DELETE /api/companies/{company_id}/partners/{partner_id}/addresses/{address_id}

**Purpose:** Delete partner address
**Parameters:** Company ID, partner ID, address ID in URL path
**Response:** 204 No Content
**Errors:** 401 (Unauthorized), 403 (No access), 404 (Address not found)

## User-Company Association Endpoints

### GET /api/user/companies

**Purpose:** Get companies accessible to current user
**Parameters:** None (uses current user from JWT)
**Response:** List of companies with user roles
**Errors:** 401 (Unauthorized)

### POST /api/companies/{company_id}/users

**Purpose:** Add user to company (admin only)
**Parameters:** Company ID in URL path, user assignment data in request body

**Request Body:**
```json
{
  "user_id": 123,
  "role": "user",
  "is_default_company": false
}
```

**Response:** 201 Created with user-company association
**Errors:** 400 (Validation error), 401 (Unauthorized), 403 (Not admin), 404 (Company or user not found)

### DELETE /api/companies/{company_id}/users/{user_id}

**Purpose:** Remove user from company (admin only)
**Parameters:** Company ID and user ID in URL path
**Response:** 204 No Content
**Errors:** 401 (Unauthorized), 403 (Not admin), 404 (Association not found)

## Health and Status Endpoints

### GET /health

**Purpose:** Service health check
**Parameters:** None
**Response:**
```json
{
  "status": "healthy",
  "service": "Company/Partner Service",
  "version": "1.0.0",
  "environment": "development"
}
```

**Errors:** 503 (Service unhealthy)