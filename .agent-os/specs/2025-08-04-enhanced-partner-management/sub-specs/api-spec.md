# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-08-04-enhanced-partner-management/spec.md

> Created: 2025-08-04
> Version: 1.0.0

## Base URL Structure

All enhanced partner management endpoints will be added to the existing company-partner-service:
- Base URL: `http://localhost:8002/api/`
- Framework endpoints: `http://localhost:8002/api/framework/`

## Partner Contacts Endpoints

### GET /api/framework/partner-contacts/

**Purpose:** Retrieve all partner contacts with filtering and pagination
**Parameters:** 
- `company_id`: Filter by company (optional, defaults to user's company)
- `partner_id`: Filter by specific partner
- `role`: Filter by contact role
- `active`: Filter by active status (default: true)
- `limit`: Pagination limit (default: 50)
- `offset`: Pagination offset (default: 0)
**Response:** Paginated list of partner contact objects
**Errors:** 401 Unauthorized, 403 Forbidden, 500 Internal Server Error

### POST /api/framework/partner-contacts/

**Purpose:** Create new partner contact
**Parameters:** JSON body with contact details including partner_id, name, role, email, phone
**Response:** Created contact object with generated ID
**Errors:** 400 Bad Request, 401 Unauthorized, 403 Forbidden, 422 Validation Error

### GET /api/framework/partner-contacts/{contact_id}

**Purpose:** Retrieve specific partner contact by ID
**Parameters:** contact_id in URL path
**Response:** Complete contact object with all details
**Errors:** 401 Unauthorized, 403 Forbidden, 404 Not Found

### PUT /api/framework/partner-contacts/{contact_id}

**Purpose:** Update existing partner contact
**Parameters:** contact_id in URL path, JSON body with updated contact details
**Response:** Updated contact object
**Errors:** 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Validation Error

### DELETE /api/framework/partner-contacts/{contact_id}

**Purpose:** Soft delete partner contact (set active=false)
**Parameters:** contact_id in URL path
**Response:** Success confirmation message
**Errors:** 401 Unauthorized, 403 Forbidden, 404 Not Found

## Partner Addresses Endpoints

### GET /api/framework/partner-addresses/

**Purpose:** Retrieve all partner addresses with filtering and pagination
**Parameters:**
- `company_id`: Filter by company (optional)
- `partner_id`: Filter by specific partner
- `type`: Filter by address type (billing, shipping, etc.)
- `country`: Filter by country code
- `active`: Filter by active status
**Response:** Paginated list of partner address objects
**Errors:** 401 Unauthorized, 403 Forbidden, 500 Internal Server Error

### POST /api/framework/partner-addresses/

**Purpose:** Create new partner address
**Parameters:** JSON body with address details including partner_id, type, street1, city, country
**Response:** Created address object with generated ID
**Errors:** 400 Bad Request, 401 Unauthorized, 403 Forbidden, 422 Validation Error

### GET /api/framework/partner-addresses/{address_id}

**Purpose:** Retrieve specific partner address by ID
**Parameters:** address_id in URL path
**Response:** Complete address object with all details
**Errors:** 401 Unauthorized, 403 Forbidden, 404 Not Found

### PUT /api/framework/partner-addresses/{address_id}

**Purpose:** Update existing partner address
**Parameters:** address_id in URL path, JSON body with updated address details
**Response:** Updated address object
**Errors:** 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Validation Error

### DELETE /api/framework/partner-addresses/{address_id}

**Purpose:** Soft delete partner address (set active=false)
**Parameters:** address_id in URL path
**Response:** Success confirmation message
**Errors:** 401 Unauthorized, 403 Forbidden, 404 Not Found

## Partner Categories Endpoints

### GET /api/framework/partner-categories/

**Purpose:** Retrieve all partner categories with hierarchical structure
**Parameters:**
- `company_id`: Filter by company (optional)
- `parent_id`: Filter by parent category (null for root categories)
- `active`: Filter by active status
**Response:** List of partner category objects with parent-child relationships
**Errors:** 401 Unauthorized, 403 Forbidden, 500 Internal Server Error

### POST /api/framework/partner-categories/

**Purpose:** Create new partner category
**Parameters:** JSON body with category details including name, description, parent_id (optional)
**Response:** Created category object with generated ID
**Errors:** 400 Bad Request, 401 Unauthorized, 403 Forbidden, 422 Validation Error

### GET /api/framework/partner-categories/{category_id}

**Purpose:** Retrieve specific partner category by ID
**Parameters:** category_id in URL path
**Response:** Complete category object with hierarchy information
**Errors:** 401 Unauthorized, 403 Forbidden, 404 Not Found

### PUT /api/framework/partner-categories/{category_id}

**Purpose:** Update existing partner category
**Parameters:** category_id in URL path, JSON body with updated category details
**Response:** Updated category object
**Errors:** 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Validation Error

### DELETE /api/framework/partner-categories/{category_id}

**Purpose:** Soft delete partner category (set active=false)
**Parameters:** category_id in URL path
**Response:** Success confirmation message
**Errors:** 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict (if category has children or assigned partners)

## Partner Relationships Endpoints

### GET /api/framework/partner-relationships/

**Purpose:** Retrieve partner relationships with hierarchy support
**Parameters:**
- `company_id`: Filter by company (optional)
- `parent_partner_id`: Filter by parent partner
- `child_partner_id`: Filter by child partner
- `relationship_type`: Filter by relationship type
- `active`: Filter by active status
**Response:** List of partner relationship objects
**Errors:** 401 Unauthorized, 403 Forbidden, 500 Internal Server Error

### POST /api/framework/partner-relationships/

**Purpose:** Create new partner relationship
**Parameters:** JSON body with relationship details including parent_partner_id, child_partner_id, relationship_type
**Response:** Created relationship object with generated ID
**Errors:** 400 Bad Request, 401 Unauthorized, 403 Forbidden, 422 Validation Error

### GET /api/framework/partner-relationships/{relationship_id}

**Purpose:** Retrieve specific partner relationship by ID
**Parameters:** relationship_id in URL path
**Response:** Complete relationship object with partner details
**Errors:** 401 Unauthorized, 403 Forbidden, 404 Not Found

### PUT /api/framework/partner-relationships/{relationship_id}

**Purpose:** Update existing partner relationship
**Parameters:** relationship_id in URL path, JSON body with updated relationship details
**Response:** Updated relationship object
**Errors:** 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Validation Error

### DELETE /api/framework/partner-relationships/{relationship_id}

**Purpose:** Soft delete partner relationship (set active=false)
**Parameters:** relationship_id in URL path
**Response:** Success confirmation message
**Errors:** 401 Unauthorized, 403 Forbidden, 404 Not Found

## Partner Communications Endpoints

### GET /api/framework/partner-communications/

**Purpose:** Retrieve partner communications with filtering and pagination
**Parameters:**
- `company_id`: Filter by company (optional)
- `partner_id`: Filter by specific partner
- `contact_id`: Filter by specific contact
- `communication_type`: Filter by communication type
- `date_from`: Filter by date range (start)
- `date_to`: Filter by date range (end)
- `limit`: Pagination limit (default: 50)
- `offset`: Pagination offset (default: 0)
**Response:** Paginated list of communication objects ordered by date (newest first)
**Errors:** 401 Unauthorized, 403 Forbidden, 500 Internal Server Error

### POST /api/framework/partner-communications/

**Purpose:** Create new partner communication record
**Parameters:** JSON body with communication details including partner_id, communication_type, subject, content, communication_date
**Response:** Created communication object with generated ID
**Errors:** 400 Bad Request, 401 Unauthorized, 403 Forbidden, 422 Validation Error

### GET /api/framework/partner-communications/{communication_id}

**Purpose:** Retrieve specific partner communication by ID
**Parameters:** communication_id in URL path
**Response:** Complete communication object with all details
**Errors:** 401 Unauthorized, 403 Forbidden, 404 Not Found

### PUT /api/framework/partner-communications/{communication_id}

**Purpose:** Update existing partner communication
**Parameters:** communication_id in URL path, JSON body with updated communication details
**Response:** Updated communication object
**Errors:** 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Validation Error

### DELETE /api/framework/partner-communications/{communication_id}

**Purpose:** Hard delete partner communication record
**Parameters:** communication_id in URL path
**Response:** Success confirmation message
**Errors:** 401 Unauthorized, 403 Forbidden, 404 Not Found

## Special Endpoints

### GET /api/partners/{partner_id}/summary

**Purpose:** Get comprehensive partner summary including contacts, addresses, categories, and recent communications
**Parameters:** partner_id in URL path
**Response:** Complete partner object with all related data
**Errors:** 401 Unauthorized, 403 Forbidden, 404 Not Found

### POST /api/partners/{partner_id}/assign-categories

**Purpose:** Bulk assign categories to a partner
**Parameters:** partner_id in URL path, JSON body with array of category_ids
**Response:** Success confirmation with updated category assignments
**Errors:** 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found

### GET /api/partner-categories/{category_id}/partners

**Purpose:** Get all partners assigned to a specific category
**Parameters:** category_id in URL path, pagination parameters
**Response:** Paginated list of partners in the category
**Errors:** 401 Unauthorized, 403 Forbidden, 404 Not Found