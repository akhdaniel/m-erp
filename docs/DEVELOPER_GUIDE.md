# XERPIUM Developer Guide

> **XERPIUM** - Extensible Enterprise Resource Planning for Modern Businesses
> 
> Version: 1.0.0  
> Last Updated: August 8, 2025

## Welcome to XERPIUM Development

XERPIUM is a microservices-based ERP platform built with modern architecture principles. This guide will help you understand the system and start building new services effectively.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Quick Start](#quick-start)
3. [Development Environment Setup](#development-environment-setup)
4. [Service Development Workflow](#service-development-workflow)
5. [Core Concepts](#core-concepts)
6. [Documentation Index](#documentation-index)
7. [Getting Help](#getting-help)

## Architecture Overview

XERPIUM follows a **plugin-within-service** microservices architecture where:

- **Core Services** provide platform functionality (auth, partners, menus)
- **Business Modules** extend services with domain-specific features (inventory, sales, purchasing)
- **Event-Driven Communication** enables loose coupling via Redis Streams
- **Multi-Company Data Isolation** ensures secure tenant separation
- **Business Object Framework** accelerates development with standardized patterns

### Current Service Architecture

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  API Gateway    │  │ Service Registry│  │ Module Registry │
│  (Kong)         │  │  (Redis-based)  │  │  (FastAPI)      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────┐
    │                            │                            │
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ User Auth       │  │ Company Partner │  │ Menu Access     │
│ Service         │  │ Service         │  │ Service         │
│ (FastAPI)       │  │ (FastAPI)       │  │ (FastAPI)       │
└─────────────────┘  └─────────────────┘  └─────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Inventory       │  │ Sales           │  │ UI Service      │
│ Service         │  │ Service         │  │ (Vue.js)        │
│ (FastAPI)       │  │ (FastAPI)       │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘

         ┌─────────────────────────────┐
         │ Redis Message Bus           │
         │ - Event Streaming           │
         │ - Pub/Sub Notifications     │
         │ - Service Discovery         │
         └─────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for development)
- Node.js 22 LTS (for frontend development)
- Git

### 1. Clone and Start

```bash
git clone <repository-url>
cd m-erp

# Start all services
docker-compose up -d

# Verify services are running
./test_docker_services.sh
```

### 2. Access the Platform

- **Admin Interface**: http://localhost:8001/admin/admin.html
- **API Gateway**: http://localhost:8000
- **Service Discovery**: http://localhost:8003/services/
- **API Documentation**: Each service provides `/api/docs` endpoint

### 3. Test Basic Functionality

```bash
# Test user authentication
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Test company API
curl -X GET http://localhost:8002/api/v1/companies/ \
  -H "Authorization: Bearer <your-token>"
```

## Development Environment Setup

### Local Development Without Docker

1. **Set up Python environment:**
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Set up databases:**
```bash
# PostgreSQL databases for each service
createdb xerpium_auth
createdb xerpium_company
createdb xerpium_inventory
createdb xerpium_sales
```

3. **Set up Redis:**
```bash
# Install and start Redis
brew install redis  # macOS
redis-server
```

4. **Start services individually:**
```bash
# Terminal 1 - Auth Service
cd services/user-auth-service
python -m app.main

# Terminal 2 - Company Service  
cd services/company-partner-service
python -m app.main

# Continue for other services...
```

### Development Tools

- **API Testing**: Postman collections available in `docs/api/`
- **Database Management**: pgAdmin or TablePlus
- **Redis Management**: RedisInsight
- **Log Aggregation**: All services log to stdout (captured by Docker)

## Service Development Workflow

### 1. Planning Phase
```bash
# Use Agent OS for structured development
@~/.agent-os/instructions/create-spec.md
```

### 2. Create New Service

```bash
# Copy service template
cp -r services/template-service services/my-new-service
cd services/my-new-service

# Update configuration
# Edit app/core/config.py
# Edit requirements.txt
# Edit Dockerfile
```

### 3. Implement Using Framework

```python
# models/my_model.py
from company_partner_service.app.framework.base import CompanyBusinessObject

class MyBusinessObject(CompanyBusinessObject):
    __tablename__ = "my_objects"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
```

### 4. Generate CRUD Operations

The Business Object Framework automatically provides:
- RESTful API endpoints
- Database operations
- Multi-company data isolation
- Event publishing
- Audit logging

### 5. Integration and Testing

```bash
# Run service tests
pytest tests/

# Test API endpoints
curl -X GET http://localhost:8XXX/api/v1/my-objects/
```

## Core Concepts

### Multi-Company Data Isolation

Every business object automatically includes `company_id` for tenant separation:

```python
# All queries automatically filtered by company
objects = service.get_all()  # Only returns current company's data
```

### Event-Driven Architecture

Services communicate through Redis Streams:

```python
# Publish events automatically
partner = partner_service.create(partner_data)  
# Publishes PARTNER_CREATED event

# Subscribe to events
@event_handler(EventType.PARTNER_CREATED)
def handle_partner_created(event_data):
    # React to partner creation
    pass
```

### Business Object Framework

Rapid development through base classes:

```python
from app.framework.base import CompanyBusinessObject

class Product(CompanyBusinessObject):
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False)
    price = Column(Decimal(10, 2))
    
    # Automatic features:
    # - CRUD operations
    # - API endpoints
    # - Event publishing
    # - Audit logging
    # - Multi-company isolation
```

### Service-Driven UI Framework

**New in v1.1.0**: Services now control their own UI presentation through JSON schemas, eliminating the need for custom frontend code.

#### How It Works

1. **Services Define UI Schemas**: Backend services provide JSON schemas that describe how their data should be displayed
2. **Generic Components Render**: The UI service uses generic components that render based on these schemas
3. **Dynamic Loading**: When users navigate to a route, the UI fetches the schema and renders accordingly

#### Example: Product List Schema

```python
# In your service (e.g., inventory_module/api/ui_schemas.py)
@router.get("/ui-schemas/products/list")
async def get_products_list_schema():
    return {
        "title": "Products",
        "viewType": "table",
        "endpoint": "/api/v1/products/",
        "searchable": True,
        "columns": [
            {"field": "name", "label": "Product Name"},
            {"field": "price", "label": "Price", "formatter": "currency"},
            {"field": "stock", "label": "Stock", "cellClassFunction": "..."}
        ],
        "filters": [
            {"field": "category", "type": "select", "optionsEndpoint": "/api/v1/categories"}
        ],
        "createRoute": "/products/new",
        "editRoute": "/products/{id}/edit"
    }
```

#### Example: Product Form Schema

```python
@router.get("/ui-schemas/products/form")
async def get_products_form_schema():
    return {
        "title": "Product Details",
        "endpoint": "/api/v1/products",
        "sections": [{
            "title": "Basic Information",
            "fields": [
                {"name": "name", "type": "text", "label": "Product Name", "required": True},
                {"name": "price", "type": "number", "label": "Price", "prefix": "$"},
                {"name": "category_id", "type": "select", "optionsEndpoint": "/api/v1/categories"}
            ]
        }]
    }
```

#### Benefits

- **No Frontend Changes**: Update your service schema, UI updates automatically
- **Consistent UI**: All services use the same components for uniformity
- **Rapid Development**: New services get full UI with just schema definitions
- **Service Autonomy**: Each service controls its own presentation
- **Type Safety**: Schemas can be validated with Pydantic models

#### Generic Components Available

- **GenericListView**: Tables, cards, or list views with sorting, filtering, pagination
- **GenericFormView**: Dynamic forms with validation, sections, and field types
- **GenericTreeView**: Hierarchical data display (coming soon)
- **GenericDashboard**: Widget-based dashboards with charts and metrics

## Documentation Index

### Core Documentation
- **[Service Development Tutorial](docs/SERVICE_DEVELOPMENT_TUTORIAL.md)** - Step-by-step service creation
- **[Business Object Framework](docs/BUSINESS_OBJECT_FRAMEWORK.md)** - Using the development framework
- **[Service-Driven UI Framework](docs/SERVICE_DRIVEN_UI_FRAMEWORK.md)** - Dynamic UI generation system
- **[API Standards](docs/API_STANDARDS.md)** - REST API conventions and patterns
- **[Integration Patterns](docs/INTEGRATION_PATTERNS.md)** - Service communication patterns
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Testing strategies and tools

### Technical References
- **[Event System](REDIS_MESSAGE_QUEUE_IMPLEMENTATION.md)** - Event-driven architecture
- **[Menu System](docs/dynamic-menu-system.md)** - Dynamic navigation
- **[Service Registration](services/MENU_REGISTRATION_GUIDE.md)** - Service integration

### Examples and Templates
- **Inventory Service**: Comprehensive business module example
- **Sales Service**: Quote-to-cash workflow implementation
- **Purchasing Service**: Complete procurement workflow

## Development Best Practices

### 1. Follow Framework Patterns
- Use `CompanyBusinessObject` for all business entities
- Implement service layer for business logic
- Use Pydantic schemas for API validation
- Follow established naming conventions

### 2. Multi-Company Awareness
- Always design with multi-tenancy in mind
- Test with multiple companies
- Never hardcode company references

### 3. Event-Driven Design
- Publish events for significant business actions
- Design for eventual consistency
- Handle event failures gracefully

### 4. API Design
- Follow REST conventions
- Use proper HTTP status codes
- Implement pagination for list endpoints
- Provide comprehensive error messages

### 5. Testing Strategy
- Unit tests for business logic
- Integration tests for API endpoints
- Event-driven communication tests
- Multi-company isolation tests

## Getting Help

### Resources
- **Architecture Documentation**: `@.agent-os/product/`
- **Service Examples**: `services/inventory-service/`, `services/sales-service/`
- **API Documentation**: Each service provides OpenAPI docs at `/api/docs`
- **Framework Documentation**: `services/company-partner-service/app/framework/`

### Support Channels
- **Technical Issues**: Review service logs via `docker-compose logs <service>`
- **API Testing**: Use provided Postman collections
- **Database Issues**: Connect directly to PostgreSQL for debugging
- **Event System**: Monitor Redis Streams with RedisInsight

### Common Development Tasks

#### Adding a New Business Entity
```bash
# 1. Create model using framework
# 2. Run database migration
# 3. Test CRUD operations
# 4. Verify event publishing
# 5. Update API documentation
```

#### Integrating with Existing Services
```bash
# 1. Subscribe to relevant events
# 2. Implement service client
# 3. Add proper error handling
# 4. Test integration scenarios
```

#### Extending the UI (Service-Driven Approach)
```bash
# 1. Define UI schemas in your service
# 2. Register menu items via menu service
# 3. No frontend code needed - generic components render your schemas
# 4. Test by navigating to your routes

# Example: Add a new list view
# In your service's ui_schemas.py:
@router.get("/ui-schemas/my-entity/list")
async def get_my_entity_list_schema():
    return {
        "title": "My Entities",
        "endpoint": "/api/v1/my-entities/",
        "columns": [...],
        "filters": [...]
    }
```

---

## Next Steps

1. **Read the [Service Development Tutorial](docs/SERVICE_DEVELOPMENT_TUTORIAL.md)** for hands-on guidance
2. **Explore the [Business Object Framework](docs/BUSINESS_OBJECT_FRAMEWORK.md)** for rapid development
3. **Review existing services** in `services/` for implementation examples
4. **Start building** your first service using the established patterns

Welcome to XERPIUM development! 🚀