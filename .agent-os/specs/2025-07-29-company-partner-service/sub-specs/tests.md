# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-07-29-company-partner-service/spec.md

> Created: 2025-07-29
> Version: 1.0.0

## Test Coverage

### Unit Tests

**CompanyModel**
- Test company creation with valid data
- Test company validation (name, code, email format)
- Test company code uniqueness constraint
- Test company soft delete functionality
- Test company timezone and currency defaults

**PartnerModel**
- Test partner creation with company association
- Test partner type validation (customer/supplier/vendor)
- Test partner code uniqueness within company scope
- Test partner hierarchy (parent-child relationships)
- Test partner soft delete and cascade effects

**CompanyUserModel**
- Test user-company association creation
- Test role validation (admin, manager, user, viewer)
- Test unique constraint (company_id, user_id)
- Test default company flag functionality

**PartnerContactModel**
- Test contact creation with partner association
- Test primary contact designation
- Test contact information validation

**PartnerAddressModel**
- Test address creation with partner association
- Test address type validation
- Test default address designation

### Integration Tests

**Company Management API**
- Test company creation with authentication
- Test company listing with user permissions
- Test company update with proper authorization
- Test company deletion (soft delete)
- Test company access control across multiple companies

**Partner Management API**
- Test partner CRUD operations within company scope
- Test partner listing with filtering and pagination
- Test partner type-specific operations
- Test partner hierarchy management
- Test partner search functionality

**Multi-Company Data Isolation**
- Test user can only access assigned companies
- Test partner data isolation between companies
- Test cross-company data leakage prevention
- Test company-scoped queries return correct data
- Test unauthorized company access returns 403

**Auth Service Integration**
- Test JWT token validation via auth service
- Test user company permissions retrieval
- Test service-to-service authentication
- Test token refresh and expiration handling
- Test user role validation for admin operations

**Partner Contact & Address Management**
- Test contact CRUD operations on partners
- Test address CRUD operations on partners
- Test contact and address data isolation
- Test primary contact/address designation
- Test cascade deletion of contacts/addresses

### Feature Tests

**Multi-Company Operations Workflow**
- User logs in and sees available companies
- User switches between companies and sees appropriate data
- Admin creates new company and assigns users
- Users can only access data from their assigned companies
- Company data remains isolated across different user sessions

**Partner Lifecycle Management**
- Create customer partner with contact and billing address
- Create supplier partner with multiple contacts
- Update partner information and verify changes
- Deactivate partner and verify soft delete
- Search and filter partners by various criteria

**Business Partner Relationships**
- Create parent company and subsidiary partners
- Test hierarchical partner relationships
- Manage corporate group structures
- Test partner relationship integrity

### Mocking Requirements

**Auth Service Calls:** Mock HTTP calls to user authentication service for:
- JWT token validation endpoints
- User company permissions retrieval
- User information lookup by user_id
- Service-to-service authentication tokens

**Database Transactions:** Mock database operations for:
- Connection failures and retry logic
- Transaction rollback scenarios
- Concurrent access and locking tests
- Database constraint violation handling

**External Service Dependencies:** Mock external calls for:
- Currency conversion API calls (if implemented)
- Address validation services (if implemented)
- Email notification services (if implemented)

### Performance Tests

**Database Query Performance**
- Test company-scoped queries with large datasets
- Test partner search with complex filters
- Test pagination performance with large result sets
- Test indexing effectiveness on company_id columns

**Concurrent Access Testing**
- Test multiple users accessing same company data
- Test concurrent partner creation and updates
- Test company switching performance
- Test database connection pooling under load

### Security Tests

**Authentication Security**
- Test invalid JWT token handling
- Test expired token scenarios
- Test missing authentication headers
- Test service-to-service authentication failures

**Authorization Security**
- Test unauthorized company access attempts
- Test privilege escalation prevention
- Test cross-company data access prevention
- Test admin-only operation security

**Data Isolation Security**
- Test SQL injection prevention in company-scoped queries
- Test parameter tampering in company_id fields
- Test direct database access bypass attempts
- Test company context manipulation prevention

### Test Data Management

**Test Database Setup**
- Use separate test database instance
- Implement test data factories for companies and partners
- Create test users via auth service integration
- Establish known test company structures

**Test Data Cleanup**
- Implement proper test teardown
- Reset database state between tests
- Clean up test users in auth service
- Manage test data isolation between test runs

### Continuous Integration Requirements

**Automated Test Execution**
- Run full test suite on every commit
- Execute integration tests against real auth service
- Perform database migration tests
- Run security and performance test subsets

**Test Coverage Metrics**
- Maintain minimum 90% code coverage
- Track API endpoint coverage
- Monitor database model coverage
- Measure business logic test coverage