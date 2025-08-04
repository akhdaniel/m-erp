# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-08-03-enhanced-partner-management/spec.md

> Created: 2025-08-03
> Version: 1.0.0

## Endpoints

### Partner Contact Management

#### POST /partners/{partner_id}/contacts

**Purpose:** Create a new contact for a partner
**Parameters:** 
- `partner_id` (path): Partner ID
- `company_id` (query, optional): Company ID for access verification
**Request Body:** ContactCreate schema
**Response:** ContactResponse schema
**Errors:** 400 (validation error), 403 (access denied), 404 (partner not found)

#### GET /partners/{partner_id}/contacts

**Purpose:** List all contacts for a partner
**Parameters:** 
- `partner_id` (path): Partner ID
- `company_id` (query, optional): Company ID for access verification
- `active_only` (query, default: true): Return only active contacts
**Response:** List[ContactResponse]
**Errors:** 403 (access denied), 404 (partner not found)

#### GET /partners/{partner_id}/contacts/{contact_id}

**Purpose:** Get specific contact details
**Parameters:** 
- `partner_id` (path): Partner ID
- `contact_id` (path): Contact ID
- `company_id` (query, optional): Company ID for access verification
**Response:** ContactResponse schema
**Errors:** 403 (access denied), 404 (partner/contact not found)

#### PUT /partners/{partner_id}/contacts/{contact_id}

**Purpose:** Update contact information
**Parameters:** 
- `partner_id` (path): Partner ID
- `contact_id` (path): Contact ID
- `company_id` (query, optional): Company ID for access verification
**Request Body:** ContactUpdate schema
**Response:** ContactResponse schema
**Errors:** 400 (validation error), 403 (access denied), 404 (partner/contact not found)

#### DELETE /partners/{partner_id}/contacts/{contact_id}

**Purpose:** Delete a contact (soft delete)
**Parameters:** 
- `partner_id` (path): Partner ID
- `contact_id` (path): Contact ID
- `company_id` (query, optional): Company ID for access verification
**Response:** 204 No Content
**Errors:** 403 (access denied), 404 (partner/contact not found)

#### POST /partners/{partner_id}/contacts/{contact_id}/set-primary

**Purpose:** Set contact as primary contact for partner
**Parameters:** 
- `partner_id` (path): Partner ID
- `contact_id` (path): Contact ID
- `company_id` (query, optional): Company ID for access verification
**Response:** ContactResponse schema
**Errors:** 403 (access denied), 404 (partner/contact not found)

### Partner Address Management

#### POST /partners/{partner_id}/addresses

**Purpose:** Create a new address for a partner
**Parameters:** 
- `partner_id` (path): Partner ID
- `company_id` (query, optional): Company ID for access verification
**Request Body:** AddressCreate schema
**Response:** AddressResponse schema
**Errors:** 400 (validation error), 403 (access denied), 404 (partner not found)

#### GET /partners/{partner_id}/addresses

**Purpose:** List all addresses for a partner
**Parameters:** 
- `partner_id` (path): Partner ID
- `company_id` (query, optional): Company ID for access verification
- `address_type` (query, optional): Filter by address type
**Response:** List[AddressResponse]
**Errors:** 403 (access denied), 404 (partner not found)

#### GET /partners/{partner_id}/addresses/{address_id}

**Purpose:** Get specific address details
**Parameters:** 
- `partner_id` (path): Partner ID
- `address_id` (path): Address ID
- `company_id` (query, optional): Company ID for access verification
**Response:** AddressResponse schema
**Errors:** 403 (access denied), 404 (partner/address not found)

#### PUT /partners/{partner_id}/addresses/{address_id}

**Purpose:** Update address information
**Parameters:** 
- `partner_id` (path): Partner ID
- `address_id` (path): Address ID
- `company_id` (query, optional): Company ID for access verification
**Request Body:** AddressUpdate schema
**Response:** AddressResponse schema
**Errors:** 400 (validation error), 403 (access denied), 404 (partner/address not found)

#### DELETE /partners/{partner_id}/addresses/{address_id}

**Purpose:** Delete an address
**Parameters:** 
- `partner_id` (path): Partner ID
- `address_id` (path): Address ID
- `company_id` (query, optional): Company ID for access verification
**Response:** 204 No Content
**Errors:** 403 (access denied), 404 (partner/address not found)

#### POST /partners/{partner_id}/addresses/{address_id}/set-default

**Purpose:** Set address as default for its type
**Parameters:** 
- `partner_id` (path): Partner ID
- `address_id` (path): Address ID
- `company_id` (query, optional): Company ID for access verification
**Response:** AddressResponse schema
**Errors:** 403 (access denied), 404 (partner/address not found)

### Enhanced Partner Endpoints

#### GET /partners/{partner_id}/details

**Purpose:** Get complete partner details including contacts and addresses
**Parameters:** 
- `partner_id` (path): Partner ID
- `company_id` (query, optional): Company ID for access verification
- `include_contacts` (query, default: true): Include contact information
- `include_addresses` (query, default: true): Include address information
**Response:** PartnerDetailResponse schema
**Errors:** 403 (access denied), 404 (partner not found)

## Schema Definitions

### ContactCreate
```json
{
  "name": "string (required, max 255)",
  "title": "string (optional, max 100)",
  "email": "string (optional, max 255, email format)",
  "phone": "string (optional, max 50)",
  "mobile": "string (optional, max 50)",
  "department": "string (optional, max 100)",
  "notes": "string (optional, text)",
  "is_primary": "boolean (default: false)"
}
```

### ContactUpdate
```json
{
  "name": "string (optional, max 255)",
  "title": "string (optional, max 100)",
  "email": "string (optional, max 255, email format)",
  "phone": "string (optional, max 50)",
  "mobile": "string (optional, max 50)",
  "department": "string (optional, max 100)",
  "notes": "string (optional, text)",
  "is_primary": "boolean (optional)",
  "is_active": "boolean (optional)"
}
```

### ContactResponse
```json
{
  "id": "integer",
  "partner_id": "integer",
  "name": "string",
  "title": "string (nullable)",
  "email": "string (nullable)",
  "phone": "string (nullable)",
  "mobile": "string (nullable)",
  "department": "string (nullable)",
  "notes": "string (nullable)",
  "is_primary": "boolean",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### AddressCreate
```json
{
  "address_type": "string (required, enum: default/billing/shipping/other)",
  "street": "string (required, text)",
  "street2": "string (optional, text)",
  "city": "string (required, max 100)",
  "state": "string (optional, max 100)",
  "zip": "string (optional, max 20)",
  "country": "string (required, max 100)",
  "is_default": "boolean (default: false)"
}
```

### AddressUpdate
```json
{
  "address_type": "string (optional, enum: default/billing/shipping/other)",
  "street": "string (optional, text)",
  "street2": "string (optional, text)",
  "city": "string (optional, max 100)",
  "state": "string (optional, max 100)",
  "zip": "string (optional, max 20)",
  "country": "string (optional, max 100)",
  "is_default": "boolean (optional)"
}
```

### AddressResponse
```json
{
  "id": "integer",
  "partner_id": "integer",
  "address_type": "string",
  "street": "string",
  "street2": "string (nullable)",
  "city": "string",
  "state": "string (nullable)",
  "zip": "string (nullable)",
  "country": "string",
  "is_default": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "formatted_address": "string",
  "single_line_address": "string"
}
```

### PartnerDetailResponse
```json
{
  "partner": "PartnerResponse (existing schema)",
  "contacts": "List[ContactResponse] (optional)",
  "addresses": "List[AddressResponse] (optional)",
  "primary_contact": "ContactResponse (nullable)",
  "default_addresses": {
    "billing": "AddressResponse (nullable)",
    "shipping": "AddressResponse (nullable)",
    "default": "AddressResponse (nullable)"
  }
}
```

## Authentication & Authorization

All endpoints require:
- Valid JWT token authentication
- Company access verification for the partner's company
- Proper error handling for unauthorized access attempts

## Event Publishing

Contact and address operations will publish the following events:
- `partner_contact_created`
- `partner_contact_updated`
- `partner_contact_deleted`
- `partner_contact_primary_changed`
- `partner_address_created`
- `partner_address_updated`
- `partner_address_deleted`
- `partner_address_default_changed`