# Company & Partner Management Service

This microservice handles company and business partner management for the M-ERP (Microservices-based ERP) system. It provides multi-company operations with complete data isolation and comprehensive partner relationship management.

## Features

- **Multi-Company Operations** - Complete data isolation with company-scoped access
- **Business Partner Management** - Customers, suppliers, vendors with hierarchical relationships
- **Contact & Address Management** - Multiple contacts and addresses per partner
- **Auth Service Integration** - JWT authentication via existing User Authentication Service
- **Company-Scoped APIs** - All endpoints automatically filter by user's company context
- **RESTful API Design** - Consistent patterns following auth service architecture

## Architecture

### Service Structure
```
company-partner-service/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py        # Service configuration
│   │   └── database.py      # Database connection and session management
│   ├── models/
│   │   ├── base.py          # Base models with company_id mixin
│   │   ├── company.py       # Company data model
│   │   └── partner.py       # Partner data model
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

### Multi-Company Data Isolation

The service implements company-scoped data isolation using:

1. **CompanyMixin** - All business objects inherit company_id field
2. **Automatic Filtering** - Company context middleware ensures proper scoping
3. **Database Constraints** - Foreign key constraints maintain referential integrity
4. **API Security** - User's company access validated via Auth Service

## Quick Start

### Prerequisites

- Docker and Docker Compose
- User Authentication Service running on port 8000

### Development Setup

1. **Clone and navigate to service directory:**
   ```bash
   cd services/company-partner-service
   ```

2. **Start the development environment:**
   ```bash
   docker-compose up -d
   ```

3. **Verify service is running:**
   ```bash
   curl http://localhost:8002/health
   ```

### Service Endpoints

The service will be available at `http://localhost:8002` with the following endpoints:

- `GET /health` - Service health check with dependency status
- `GET /` - Service information and status

*Additional API endpoints will be added as development progresses.*

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://cpuser:cppass123@localhost:5433/company_partner_db` | PostgreSQL connection string |
| `AUTH_SERVICE_URL` | `http://localhost:8001` | User Authentication Service URL |
| `DEBUG` | `true` | Enable debug mode |
| `ENVIRONMENT` | `development` | Environment setting |
| `REDIS_URL` | `redis://localhost:6379/1` | Redis connection for caching |
| `ALLOW_MULTI_COMPANY` | `true` | Enable multi-company features |
| `DEFAULT_COMPANY_NAME` | `Default Company` | Default company name for setup |

### Development Ports

- **Service:** 8002 (HTTP API)
- **Database:** 5433 (PostgreSQL)
- **Redis:** 6380 (Cache)

*Different ports are used to avoid conflicts with the User Authentication Service.*

## Integration with Auth Service

This service integrates with the User Authentication Service for:

- **JWT Token Validation** - All API calls require valid user tokens
- **User Company Access** - Determines which companies a user can access
- **Service-to-Service Auth** - Authenticated communication between microservices

### Auth Service Communication

The service connects to the Auth Service via HTTP calls to:
- Validate user JWT tokens
- Retrieve user company permissions
- Perform service-to-service authentication

## Database Schema

### Core Tables

- **companies** - Company master data with settings
- **partners** - Business partners (customers, suppliers, vendors)
- **company_users** - User-company access associations
- **partner_contacts** - Contact information for partners
- **partner_addresses** - Address information for partners

### Multi-Company Isolation

All business tables include `company_id` foreign key to ensure proper data isolation:

```sql
-- Example: Partners table structure
CREATE TABLE partners (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'customer', 'supplier', 'vendor'
    parent_id INTEGER REFERENCES partners(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_partners_company_id ON partners(company_id);
```

## Testing

### Running Tests

```bash
# Inside the container
docker exec -it company-partner-service pytest tests/ -v

# Or with coverage
docker exec -it company-partner-service pytest tests/ --cov=app --cov-report=html
```

### Test Categories

- **Unit Tests** - Model validation, business logic
- **Integration Tests** - Database operations, Auth Service communication
- **API Tests** - Endpoint functionality and validation
- **Security Tests** - Multi-company data isolation

## Development

### Adding New Features

1. Follow TDD approach - write tests first
2. Use the CompanyMixin for all business models
3. Ensure proper company scoping in all queries
4. Test multi-company data isolation

### Code Standards

- Follow existing FastAPI patterns from Auth Service
- Use async/await for all database operations
- Implement proper error handling and logging
- Follow PEP 8 style guidelines

## Infrastructure Verification

Run the verification script to test all components:

```bash
python3 verify_setup.py
```

This tests:
- Module imports
- Configuration loading  
- FastAPI app creation
- Database model definitions
- Health endpoint functionality

## Production Deployment

Production deployment will follow the same patterns as the User Authentication Service with:

- **Multi-container Docker setup** with PostgreSQL, Redis, and Nginx
- **Environment-based configuration** with secure secrets management
- **Health monitoring** and logging integration
- **SSL termination** and security headers

*Production deployment configuration will be added in later development phases.*

## Support

For development support:
- Check service logs: `docker logs company-partner-service`
- Monitor health: `curl http://localhost:8002/health`
- Review database: Connect to PostgreSQL on port 5433

## Roadmap

- **Phase 1** ✅ - Infrastructure setup and basic service framework
- **Phase 2** - Database models and company management
- **Phase 3** - Partner management and relationships
- **Phase 4** - Auth service integration and middleware
- **Phase 5** - API implementation and testing
- **Phase 6** - Production deployment and monitoring