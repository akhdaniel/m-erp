# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-07-29-company-partner-service/spec.md

> Created: 2025-07-29
> Version: 1.0.0

## Technical Requirements

- **Framework:** FastAPI with async/await support following the exact patterns from User Authentication Service
- **Database:** PostgreSQL with AsyncSession and SQLAlchemy ORM using identical patterns as auth service
- **Authentication:** JWT-based authentication with service-to-service communication via existing Auth Service
- **Multi-Company Isolation:** Database-level data isolation using company_id filters on all business objects
- **API Design:** RESTful APIs with consistent response formats matching auth service patterns
- **Testing:** Comprehensive test coverage including unit tests, integration tests, and multi-company isolation tests
- **Docker:** Containerized deployment with docker-compose integration matching existing auth service setup
- **Inter-Service Communication:** HTTP-based service calls to Auth Service for user authentication and company permissions

## Approach Options

**Option A:** Separate Database per Company
- Pros: Complete data isolation, easier compliance, simple queries
- Cons: Complex service logic, scaling challenges, backup complexity

**Option B:** Single Database with Company ID Column (Selected)
- Pros: Simpler service logic, easier cross-company reporting, better scalability
- Cons: Requires careful query filtering, potential data leakage if misconfigured

**Option C:** Schema-per-Company in Single Database
- Pros: Good isolation with single database, moderate complexity
- Cons: Schema management overhead, PostgreSQL connection limits

**Rationale:** Option B provides the best balance of simplicity, scalability, and isolation control. The company_id column approach is industry standard for multi-tenant SaaS applications and can be properly secured with careful ORM configuration and query filters.

## External Dependencies

- **asyncpg** - PostgreSQL async driver (already used in auth service)
- **SQLAlchemy** - ORM with async support (already used in auth service)
- **FastAPI** - Web framework (already used in auth service)
- **httpx** - HTTP client for service-to-service communication
- **alembic** - Database migrations (already used in auth service)
- **pytest-asyncio** - Async testing support (already used in auth service)

**Justification:** All dependencies except httpx are already in use by the auth service, ensuring consistency and reducing the overall system complexity. httpx is needed for HTTP calls to the auth service for user validation and company permission checks.

## Service Architecture

### Service Structure
Following the exact structure of the User Authentication Service:
```
company-partner-service/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py        # Service configuration
│   │   └── database.py      # Database connection and session management
│   ├── models/
│   │   ├── company.py       # Company data model
│   │   ├── partner.py       # Partner data model
│   │   └── base.py          # Base model with company_id mixin
│   ├── schemas/
│   │   ├── company.py       # Company API schemas
│   │   └── partner.py       # Partner API schemas
│   ├── routers/
│   │   ├── companies.py     # Company CRUD endpoints
│   │   └── partners.py      # Partner CRUD endpoints
│   ├── services/
│   │   ├── auth_client.py   # Auth service integration
│   │   ├── company_service.py
│   │   └── partner_service.py
│   └── middleware/
│       └── company_context.py # Company isolation middleware
├── tests/                   # Comprehensive test suite
├── migrations/              # Database migration files
├── docker-compose.yml       # Development environment
└── requirements.txt         # Python dependencies
```

### Multi-Company Data Isolation Strategy

1. **Base Model Pattern:** All business objects inherit from CompanyMixin with company_id field
2. **Query Filtering:** Automatic company_id filtering in all database queries via SQLAlchemy events
3. **Middleware Protection:** Company context middleware validates user access to requested company
4. **API Security:** All endpoints require company scope validation via Auth Service integration
5. **Database Constraints:** Foreign key constraints ensure referential integrity within company boundaries