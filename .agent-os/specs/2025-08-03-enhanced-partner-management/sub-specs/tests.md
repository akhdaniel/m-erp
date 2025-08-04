# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-08-03-enhanced-partner-management/spec.md

> Created: 2025-08-03
> Version: 1.0.0

## Test Coverage

### Unit Tests

**PartnerContact Model Tests**
- Test contact creation with valid data
- Test contact validation rules (name required, email format)
- Test primary contact designation logic
- Test contact display name formatting
- Test contact phone number priority (mobile over phone)
- Test contact activation/deactivation

**PartnerAddress Model Tests**
- Test address creation with valid data
- Test address type validation (default, billing, shipping, other)
- Test address completeness validation (street, city, country required)
- Test address formatting methods (single line, multi-line)
- Test default address designation logic
- Test address type checking methods

**Enhanced Partner Model Tests**
- Test partner industry field addition
- Test partner relationship activation (contacts and addresses)
- Test partner categorization methods
- Test hierarchical partner relationships (parent-child)
- Test partner type combination logic

**Contact Service Tests**
- Test contact creation with partner association
- Test contact retrieval by partner ID
- Test primary contact setting (only one per partner)
- Test contact update operations
- Test contact soft deletion
- Test contact search and filtering

**Address Service Tests**
- Test address creation with partner association
- Test address retrieval by partner ID and type
- Test default address setting (one per type per partner)
- Test address update operations
- Test address deletion
- Test address type filtering

### Integration Tests

**Partner Contact API Integration**
- Test POST /partners/{id}/contacts endpoint with authentication
- Test GET /partners/{id}/contacts endpoint with pagination
- Test PUT /partners/{id}/contacts/{contact_id} endpoint
- Test DELETE /partners/{id}/contacts/{contact_id} endpoint
- Test POST /partners/{id}/contacts/{contact_id}/set-primary endpoint
- Test company access verification for all contact endpoints

**Partner Address API Integration**
- Test POST /partners/{id}/addresses endpoint with authentication
- Test GET /partners/{id}/addresses endpoint with type filtering
- Test PUT /partners/{id}/addresses/{address_id} endpoint
- Test DELETE /partners/{id}/addresses/{address_id} endpoint
- Test POST /partners/{id}/addresses/{address_id}/set-default endpoint
- Test company access verification for all address endpoints

**Enhanced Partner Details Integration**
- Test GET /partners/{id}/details endpoint with contacts and addresses
- Test partner details with include/exclude parameters
- Test company access verification for partner details
- Test partner details response structure and formatting

**Database Migration Integration**
- Test industry field addition migration
- Test existing partner data preservation during migration
- Test migration rollback functionality
- Test database constraints and indexes after migration

**Event Publishing Integration**
- Test contact creation event publishing
- Test contact update event publishing
- Test contact deletion event publishing
- Test primary contact change event publishing
- Test address creation event publishing
- Test address update event publishing
- Test address deletion event publishing
- Test default address change event publishing

### Feature Tests

**Complete Contact Management Workflow**
- Create partner with basic information
- Add multiple contacts to partner
- Set one contact as primary
- Update contact information
- Deactivate and reactivate contact
- Verify contact relationships and constraints

**Complete Address Management Workflow**
- Create partner with basic information
- Add multiple addresses of different types
- Set default addresses for each type
- Update address information
- Delete address and verify cascading
- Verify address type constraints and formatting

**Enhanced Partner Management Workflow**
- Create partner with industry classification
- Add contacts and addresses in single workflow
- Retrieve complete partner details
- Update partner with enhanced information
- Verify multi-company data isolation
- Test hierarchical partner relationships

**Cross-Service Integration Workflow**
- Create partner with contacts and addresses
- Verify event publishing to Redis
- Test audit logging integration
- Verify notification service integration
- Test service discovery and health checks

### Mocking Requirements

**External Services**
- **User Authentication Service:** Mock JWT token validation and user data retrieval
- **Service Registry:** Mock service registration and health check responses
- **Redis Messaging:** Mock event publishing and consumption for integration tests

**Database Operations**
- **Multi-Company Isolation:** Mock company access verification
- **Relationship Loading:** Mock SQLAlchemy relationship loading for performance tests
- **Transaction Handling:** Mock database transaction rollback scenarios

**Time-Based Tests**
- **Creation Timestamps:** Mock datetime.now() for consistent test data
- **Event Publishing:** Mock timezone handling for event timestamps
- **Audit Logging:** Mock audit event timestamp generation

## Test Data Fixtures

### Partner Test Data
```python
PARTNER_BASE_DATA = {
    "name": "Test Partner Corp",
    "email": "contact@testpartner.com",
    "phone": "+1-555-0123",
    "is_customer": True,
    "is_supplier": False,
    "company_id": 1,
    "industry": "Technology"
}
```

### Contact Test Data
```python
CONTACT_TEST_DATA = [
    {
        "name": "John Doe",
        "title": "Sales Manager",
        "email": "john.doe@testpartner.com",
        "phone": "+1-555-0124",
        "mobile": "+1-555-0125",
        "department": "Sales",
        "is_primary": True
    },
    {
        "name": "Jane Smith",
        "title": "Accounting Manager",
        "email": "jane.smith@testpartner.com",
        "phone": "+1-555-0126",
        "department": "Accounting",
        "is_primary": False
    }
]
```

### Address Test Data
```python
ADDRESS_TEST_DATA = [
    {
        "address_type": "billing",
        "street": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "country": "United States",
        "is_default": True
    },
    {
        "address_type": "shipping",
        "street": "456 Warehouse Ave",
        "city": "New York",
        "state": "NY", 
        "zip": "10002",
        "country": "United States",
        "is_default": True
    }
]
```

## Performance Testing

### Load Testing Requirements
- Test contact creation performance with 1000+ contacts per partner
- Test address retrieval performance with multiple address types
- Test partner details endpoint with large contact/address datasets
- Test database query performance with proper indexing

### Stress Testing Requirements
- Test concurrent contact/address modifications
- Test primary/default designation race conditions
- Test database constraint enforcement under load
- Test event publishing performance under high load