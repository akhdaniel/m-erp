# Module Registry Service

The Module Registry Service is a core component of the XERPIUM Extension System that manages module registration, installation, and lifecycle for the Phase 3 Plugin/Extension Framework.

## 🚀 Features

### Module Management
- **Module Registration** - Register new modules with validation and approval workflow
- **Module Approval** - Admin approval system for security and quality control
- **Version Management** - Semantic versioning support with dependency resolution
- **Module Marketplace** - Public/private module visibility and discovery

### Installation Management
- **Module Installation** - Install modules per company with configuration
- **Health Monitoring** - Real-time health checks and status tracking
- **Configuration Management** - Dynamic configuration with hot-reloading
- **Uninstallation** - Clean uninstallation with rollback capabilities

### Extension Framework Integration
- **Service Discovery** - Automatic registration with XERPIUM service registry
- **Business Object Framework** - Integration with existing framework patterns
- **Multi-Company Support** - Company-scoped module installations and configurations
- **Event Publishing** - Integration with Redis Streams for module lifecycle events

## 🏗️ Architecture

### Service Structure
```
module-registry-service/
├── app/
│   ├── core/
│   │   ├── config.py              # Service configuration
│   │   ├── database.py            # Async database session management
│   │   └── service_registry.py    # Service discovery integration
│   ├── models/
│   │   ├── base.py               # Base model classes
│   │   ├── module.py             # Module data model
│   │   ├── installation.py      # Installation data model
│   │   └── dependency.py        # Dependency data model
│   ├── schemas/
│   │   ├── module.py             # Module API schemas
│   │   └── installation.py      # Installation API schemas
│   ├── services/
│   │   ├── module_service.py     # Module CRUD operations
│   │   └── installation_service.py # Installation management
│   ├── routers/
│   │   ├── modules.py           # Module API endpoints
│   │   └── installations.py    # Installation API endpoints
│   └── main.py                  # FastAPI application
├── migrations/                  # Database migrations
├── tests/                      # Comprehensive test suite
└── docker-compose.yml         # Development environment
```

### Database Schema

#### Core Tables
- **modules** - Module registry with metadata, manifests, and packages
- **module_dependencies** - Module dependency tracking and resolution
- **module_installations** - Company-specific module installations with configuration

#### Multi-Company Isolation
All installation data includes `company_id` for proper data isolation following XERPIUM patterns.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Service Registry running on port 8003
- Basic knowledge of FastAPI and the XERPIUM Extension System

### Development Setup

1. **Navigate to service directory:**
   ```bash
   cd services/module-registry-service
   ```

2. **Start the development environment:**
   ```bash
   docker-compose up -d
   ```

3. **Verify service is running:**
   ```bash
   curl http://localhost:8005/health
   ```

### Available Endpoints

#### Module Management
- `POST /api/v1/modules/` - Register new module
- `GET /api/v1/modules/` - List modules with filtering
- `GET /api/v1/modules/{id}` - Get module by ID
- `PUT /api/v1/modules/{id}` - Update module
- `PATCH /api/v1/modules/{id}/status` - Approve/reject module
- `DELETE /api/v1/modules/{id}` - Delete module (soft delete)
- `GET /api/v1/modules/{id}/package` - Download module package
- `POST /api/v1/modules/validate-manifest` - Validate module manifest

#### Installation Management
- `POST /api/v1/installations/` - Install module
- `GET /api/v1/installations/` - List installations
- `GET /api/v1/installations/{id}` - Get installation details
- `PUT /api/v1/installations/{id}` - Update installation configuration
- `DELETE /api/v1/installations/{id}` - Uninstall module
- `POST /api/v1/installations/{id}/health-check` - Perform health check

#### Service Endpoints
- `GET /health` - Service health check
- `GET /info` - Service information
- `GET /docs` - Auto-generated API documentation (development only)

## 📊 API Documentation

- **Auto-generated Docs**: http://localhost:8005/docs
- **Redoc**: http://localhost:8005/redoc

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://mruser:mrpass123@localhost:5434/module_registry_db` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6381/2` | Redis connection for caching |
| `SERVICE_REGISTRY_URL` | `http://localhost:8003` | Service registry URL |
| `AUTH_SERVICE_URL` | `http://localhost:8001` | User authentication service URL |
| `DEBUG` | `true` | Enable debug mode |
| `ENVIRONMENT` | `development` | Environment setting |
| `MAX_MODULE_SIZE_MB` | `50` | Maximum module package size |
| `MODULE_STORAGE_PATH` | `/tmp/modules` | Module storage directory |

### Development Ports
- **Service:** 8005 (HTTP API)
- **Database:** 5434 (PostgreSQL)
- **Redis:** 6381 (Cache/Messaging)

## 🧪 Testing

### Running Tests

```bash
# Inside the container
docker exec -it module-registry-service pytest tests/ -v

# Or with coverage
docker exec -it module-registry-service pytest tests/ --cov=app --cov-report=html
```

### Test Categories
- **Unit Tests** - Service layer, model validation, business logic
- **Integration Tests** - Database operations, service discovery integration
- **API Tests** - Endpoint functionality and validation
- **Security Tests** - Module validation and company isolation

## 🔧 Module Development

### Module Manifest Format

```yaml
name: my-module
version: 1.0.0
description: My custom business module
author: Developer Name

dependencies:
  - name: business-object-framework
    version: ">=1.0.0"
    type: module

entry_points:
  main: my_module.main:main

endpoints:
  - path: /my-endpoint
    method: GET
    handler: my_module.handlers:get_data

config_schema:
  type: object
  properties:
    api_key:
      type: string
      description: API key for external service
  required:
    - api_key
```

### Module Registration Process

1. **Register Module** - Submit module with manifest and optional package
2. **Validation** - Automatic manifest validation and security scanning
3. **Admin Approval** - Manual approval for security and quality
4. **Installation** - Company-specific installation with configuration
5. **Health Monitoring** - Continuous health checks and status tracking

## 📈 Integration with XERPIUM

### Service Discovery
- Automatic registration with XERPIUM service registry
- Health check integration for monitoring
- Service-to-service communication patterns

### Business Object Framework
- Modules can leverage existing Business Object Framework
- Automatic audit logging and event publishing
- Multi-company data isolation patterns

### Event System
- Module lifecycle events published to Redis Streams
- Integration with existing audit and notification services
- Cross-module communication via events

## 🔒 Security

### Module Security
- Module manifest validation
- Package integrity checking (SHA256 hashes)
- Admin approval workflow for new modules
- Company-scoped installations for data isolation

### API Security
- JWT token validation (integration with auth service)
- Company-level access control
- Input validation and sanitization

## 📋 Development

### Adding New Features
1. Follow TDD approach - write tests first
2. Use existing service patterns and database models
3. Ensure proper error handling and logging
4. Test integration with service discovery

### Code Standards
- Follow existing FastAPI patterns from other XERPIUM services
- Use async/await for all database operations
- Implement proper error handling and logging
- Follow PEP 8 style guidelines

## 🚀 Production Deployment

Production deployment follows the same patterns as other XERPIUM services:

- **Multi-container Docker setup** with PostgreSQL, Redis, and service
- **Environment-based configuration** with secure secrets management
- **Health monitoring** and logging integration
- **Service discovery** integration with XERPIUM infrastructure

## 📊 Phase 3 Integration

This service is **Task 1** of Phase 3: Extension System & First Business Module. It provides the foundation for:

- **Plugin/Extension Framework** (Task 2)
- **Module Management API** (Task 3)
- **CLI Tools for Module Development** (Task 4)
- **Purchasing Module Implementation** (Tasks 5-8)
- **Auto-Documentation System** (Task 9)
- **UI Integration** (Task 10)

## 🎯 Next Phase Features

### Phase 3 Continuation
- Plugin loader and validation system
- Module template generator CLI
- Purchasing module implementation
- Advanced module features (backup, rollback, monitoring)

### Future Phases
- Module marketplace with ratings and reviews
- Advanced security scanning and sandboxing
- Module analytics and usage tracking
- Enterprise deployment and scaling features

## 📞 Support

For development support:
- Check service logs: `docker logs module-registry-service`
- Monitor health: `curl http://localhost:8005/health`
- Review database: Connect to PostgreSQL on port 5434
- API documentation: http://localhost:8005/docs

---

**Service Status**: ✅ **Production Ready**  
**Phase 3 Task 1**: ✅ **Complete**  
**Integration**: ✅ **Service Discovery, Business Object Framework, Multi-Company Support**