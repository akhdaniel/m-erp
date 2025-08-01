# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-08-01-business-object-framework/spec.md

> Created: 2025-08-01
> Version: 1.0.0

## Test Coverage

### Unit Tests

**BusinessObjectBase Model**
- Test automatic timestamp creation and updates
- Test company_id field presence and validation
- Test framework_version field default value
- Test created_by field assignment
- Test soft delete functionality
- Test multi-company data isolation

**AuditableMixin**
- Test automatic audit log creation on create operations
- Test automatic audit log creation on update operations
- Test automatic audit log creation on delete operations
- Test before/after data capture
- Test user context propagation to audit logs
- Test audit log creation failure handling

**EventPublisherMixin**
- Test automatic event publishing on create operations
- Test automatic event publishing on update operations
- Test automatic event publishing on delete operations
- Test event payload structure and content
- Test event publishing failure handling (non-blocking)
- Test correlation ID propagation

**ExtensibleMixin**
- Test custom field addition and retrieval
- Test custom field validation
- Test custom field type conversion
- Test bulk custom field operations
- Test custom field deletion
- Test company isolation for custom fields

**BusinessObjectService**
- Test create operation with all framework features
- Test update operation with change detection
- Test delete operation (soft and hard delete)
- Test pagination functionality
- Test search and filtering operations
- Test company isolation enforcement
- Test permission validation
- Test error handling and rollback scenarios

**Schema Framework**
- Test automatic validation rule application
- Test create schema validation
- Test update schema validation
- Test response schema serialization
- Test custom validator integration
- Test error message formatting

### Integration Tests

**Database Integration**
- Test framework models with actual PostgreSQL database
- Test migration scripts execution and rollback
- Test foreign key constraints and referential integrity
- Test database connection pooling with framework operations
- Test transaction handling across framework components
- Test concurrent access and locking scenarios

**Messaging System Integration**
- Test event publishing to Redis Streams
- Test event consumption by audit service
- Test event payload serialization/deserialization
- Test message ordering and delivery guarantees
- Test error handling when Redis is unavailable
- Test event replay and processing idempotency

**Audit Service Integration**
- Test audit log creation via API calls
- Test audit log data structure and completeness
- Test audit log querying and filtering
- Test audit service failure handling (graceful degradation)
- Test audit log retention and cleanup
- Test cross-service audit correlation

**Authentication Integration**
- Test JWT token validation in framework operations
- Test user context extraction and propagation
- Test company_id enforcement from user context
- Test permission checking integration
- Test multi-company access control
- Test admin override functionality

**Service Discovery Integration**
- Test framework service registration
- Test health check reporting
- Test service dependency validation
- Test graceful service startup and shutdown
- Test inter-service communication patterns

### Feature Tests (End-to-End)

**Complete Business Object Lifecycle**
- Create business object with all framework features enabled
- Update business object with audit and event tracking
- Query business object with extensions and filters
- Delete business object with proper cleanup
- Verify audit trail completeness
- Verify event publishing throughout lifecycle

**Multi-Company Data Isolation**
- Create objects in different companies
- Verify cross-company access is blocked
- Test company switching scenarios
- Verify audit logs respect company boundaries
- Test bulk operations across companies (should fail)

**Extension System Workflow**
- Add custom fields to business object
- Update custom field values
- Query objects by custom field values
- Remove custom fields
- Verify custom field audit trail
- Test custom field validation

**Error Handling and Recovery**
- Test framework behavior during database outages
- Test framework behavior during Redis outages
- Test framework behavior during audit service outages
- Test partial failure scenarios (some operations succeed)
- Test data consistency after failure recovery
- Test transaction rollback scenarios

**Performance and Scalability**
- Test framework overhead on basic CRUD operations
- Test bulk operation performance
- Test concurrent user access patterns
- Test large dataset handling
- Test memory usage under load
- Test database connection usage efficiency

## Mocking Requirements

### External Services

**Redis Messaging System**
- Mock Redis client for unit tests
- Mock event publishing success/failure scenarios
- Mock Redis Streams functionality
- Mock pub/sub channel operations
- Simulate Redis connection failures
- Mock message acknowledgment scenarios

**Audit Service API**
- Mock audit service HTTP client
- Mock successful audit log creation
- Mock audit service failure scenarios
- Mock audit service timeout scenarios
- Mock audit service response parsing
- Mock audit service authentication

**User Authentication Service**
- Mock JWT token validation
- Mock user context objects
- Mock company_id extraction
- Mock permission checking results
- Mock admin user scenarios
- Mock authentication failure scenarios

**Database Layer**
- Mock SQLAlchemy session objects
- Mock database query results
- Mock database constraint violations
- Mock database connection failures
- Mock transaction commit/rollback
- Mock concurrent access scenarios

### Test Data Management

**Business Object Test Data**
- Factory classes for creating test business objects
- Realistic test data generators
- Multi-company test data scenarios
- Test data cleanup utilities
- Test data versioning for migrations
- Performance test data sets

**User and Authentication Test Data**
- Test user accounts with different permissions
- Test company structures and relationships
- Test JWT tokens with various expiration times
- Test user context objects
- Test admin and regular user scenarios

**Event and Audit Test Data**
- Sample event payloads for each event type
- Sample audit log entries with various change types
- Test correlation IDs and request chains
- Sample error scenarios and recovery patterns

## Test Environment Setup

### Database Configuration
- Separate test database instances for each test suite
- Database transaction isolation for test cases
- Automatic database cleanup between tests
- Migration testing with fresh database instances
- Performance testing with realistic data volumes

### Redis Configuration
- Separate Redis instance for testing
- Redis stream cleanup between tests
- Mock Redis for unit tests, real Redis for integration tests
- Redis cluster testing for scalability scenarios

### Service Dependencies
- Mock external services for unit/integration tests
- Containerized services for end-to-end tests
- Service health check validation
- Dependency injection for test scenarios

### Continuous Integration
- Automated test execution on all code changes
- Test coverage reporting and enforcement (90%+ target)
- Performance regression testing
- Cross-platform testing (Linux, macOS)
- Database migration testing with multiple PostgreSQL versions