# Technical Stack

> Last Updated: 2025-07-27
> Version: 1.0.0

## Core Technologies

### Application Framework
- **Framework:** Python (for core services)
- **Version:** 3.12+
- **Web Framework:** FastAPI or Django (service-specific choice)
- **Architecture:** Microservices with service-specific technology choices

### Database System
- **Primary:** PostgreSQL
- **Version:** 17+
- **ORM:** SQLAlchemy (Python services), service-specific ORMs for other languages
- **Multi-Database:** Yes, each service can have its own database

### Microservices Architecture
- **Service Communication:** REST APIs with JSON
- **Service Discovery:** Docker for development, Kubernetes service discovery for production
- **API Gateway:** Kong or Nginx
- **Message Queue:** Redis (optimal for ERP workloads - fast, simple, persistent)
- **Event System:** Redis Streams for event sourcing and inter-service communication


## Default admin user for testing
- user: admin@m-erp.com
- password: admin123

## Containerization
- **Docker compose**: use docker compose command, not docker-compose
- **Server**: on VM cloud with domain demo.xerpium.com, IP address 8.215.67.59

## Service driven US
- all menus and dashboard items in the UI are triggered by the service it self
- services has modulename-service/modulename_module/menu_init.py for requesting menu to display
- services has modulename-service/register_ui.py for requesting dashboard items to display

## Standard Services

### Accessing Services 

To get availabel APIs on the service use: /api/openapi.json
To access the services directly, do not use /api/v1 endpoint prefix.
To access the service from kong, prefix with /api/v1/<servicename>.

Example;
curl http://localhost:8006/api/openapi.json
curl https://demo.xerpium.com/api/v1/sales/customers
curl http://localhost:8006/customers

### **UI Servce**: 
	- port: 9000
	- use external network chat_odoo_network so that reachable from external nginx proxy  contianer
    - API end points: 
        - localhost:9000
###  **Kong Servce**: 
	- port: 8000
    - end point mappings:
        - /api/v1/base => company-partner-service
        - /api/v1/inventory => inventory-service
        - /api/v1/sales => sales-service
        - /api/v1/purchasing => purchasing-service
###  **Redit Service**: 
	- port: 6379
###  **PostgreSQL**: 
	- port: 5432
###  **user-auth-service**: 
	- port: 8001
###  **company-partner-service**: 
	- port: 8002
    - API end points: 
        - localhost:8002/dashboard    
        - localhost:8002/partners    
        - localhost:8002/companies    
###  **menu-access-service**: 
	- port 8003
###  **service-registry**: 
	- port: 8004
###  **inventory-service**: 
	- port: 8005
    - API end points: 
        - localhost:8005/dashboard 
        - localhost:8005/products        
        - localhost:8005/stock_moves        
###  **sales-service**: 
	- port: 8006
    - API end points: 
        - localhost:8006/dashboard
        - localhost:8006/orders
        - localhost:8006/transactions
###  **purchasing-service**: 
	- port: 8007
###  **notification-registry**: 
	- port: 8009
###  **ui-registry**: 
	- port: 8010
 
## Frontend Stack

### JavaScript Framework
- **Framework:** React
- **Version:** Latest stable
- **Build Tool:** Vite

### Import Strategy
- **Strategy:** Node.js modules
- **Package Manager:** npm
- **Node Version:** 22 LTS

### CSS Framework
- **Framework:** TailwindCSS
- **Version:** 4.0+
- **PostCSS:** Yes

### UI Component Library
- **Library:** Material-UI or Ant Design
- **Version:** Latest
- **Installation:** Via npm

## Assets & Media

### Fonts Provider
- **Provider:** Google Fonts
- **Loading Strategy:** Self-hosted for performance

### Icon Library
- **Library:** Lucide
- **Implementation:** React components

## Infrastructure

### Application Hosting
- **Platform:** Digital Ocean
- **Development:** Docker Compose for local development
- **Production:** Kubernetes on Digital Ocean
- **Container:** Docker containers for each microservice
- **Region:** Primary region based on user base

### Database Hosting
- **Provider:** Digital Ocean
- **Service:** Managed PostgreSQL clusters per service
- **Backups:** Daily automated with point-in-time recovery

### Asset Storage
- **Provider:** Amazon S3
- **CDN:** CloudFront
- **Access:** Private with signed URLs

## Deployment

### CI/CD Pipeline
- **Platform:** GitHub Actions
- **Containerization:** Docker for service packaging
- **Orchestration:** Kubernetes for service deployment
- **Testing:** Service-level and integration tests

### Service Management
- **Monitoring:** Prometheus + Grafana
- **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing:** Jaeger for distributed tracing

### Environments
- **Development:** Docker Compose with Redis for messaging
- **Staging:** staging branch with simplified Kubernetes setup
- **Production:** main branch with Kubernetes deployment and managed Redis cluster

### Code Repository
- **Repository:** GitHub monorepo with service-specific folders
- **Branching:** GitFlow with service-specific feature branches

# XERPIUM Development Cheat Sheet

> Quick reference guide for developing new services and features in XERPIUM

## 🚀 Quick Start

### 1. Create New Service
```bash
# Copy template
cp -r services/template-service services/my-new-service
cd services/my-new-service

# Update configuration files
# - app/core/config.py (service name, ports)
# - requirements.txt (dependencies)
# - Dockerfile (if needed)
# - docker-compose.yml (port mapping)
```

### 2. Define Business Objects
```python
# models/my_model.py
from company_partner_service.app.framework.base import CompanyBusinessObject

class MyBusinessObject(CompanyBusinessObject):
    __tablename__ = "my_objects"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    # company_id automatically included
    # created_at, updated_at automatically included
```

### 3. Generate CRUD Operations
The Business Object Framework automatically provides:
- RESTful API endpoints at `/api/v1/my-objects/`
- Database operations (create, read, update, delete)
- Multi-company data isolation
- Event publishing (MY_OBJECT_CREATED, MY_OBJECT_UPDATED, etc.)
- Audit logging

## 🏗️ Service Development Workflow

### 1. Planning
- Review @.agent-os/product/roadmap.md for current priorities
- Follow @.agent-os/instructions/create-spec.md for new features
- Check existing services for implementation patterns

### 2. Implementation
1. **Models**: Define business objects using CompanyBusinessObject
2. **Services**: Implement business logic layer
3. **API**: Create REST endpoints (often auto-generated)
4. **UI Schemas**: Define dynamic UI presentation
5. **Events**: Publish/subscribe to relevant business events
6. **Tests**: Write unit and integration tests

### 3. Integration
- Register with service registry
- Register menu items with menu service
- Test event-driven communication
- Verify multi-company data isolation

## 🛠️ Core Patterns & Frameworks

### Business Object Framework
```python
# Base classes
CompanyBusinessObject  # For company-scoped entities
BusinessObjectBase     # For system-wide entities

# Automatic features
# - CRUD operations
# - API endpoints
# - Event publishing
# - Audit logging
# - Multi-company isolation
```

### Service-Driven UI Framework
```python
# Define UI schemas in your service
@app.get("/ui-schemas/my-objects/list")
async def get_list_schema():
    return {
        "title": "My Objects",
        "viewType": "table",
        "endpoint": "/api/v1/my-objects/",
        "columns": [
            {"field": "name", "label": "Name"},
            {"field": "created_at", "label": "Created"}
        ]
    }
```

## 📡 API Development

### REST Conventions
- Use plural nouns: `/products/` not `/product/`
- Use hyphens: `/product-categories/` not `/product_categories/`
- Version endpoints: `/api/v1/products/`
- Proper HTTP methods: GET, POST, PUT, PATCH, DELETE

### Standard Endpoints
```
GET    /api/v1/resource/          # List with pagination
POST   /api/v1/resource/          # Create new
GET    /api/v1/resource/{id}      # Get by ID
PUT    /api/v1/resource/{id}      # Update entire resource
DELETE /api/v1/resource/{id}      # Delete (soft delete preferred)
GET    /api/v1/resource/{id}/...  # Related resources
POST   /api/v1/resource/action    # Custom actions
```

### Response Formats
```python
# Single resource
{
  "id": 123,
  "name": "Resource Name",
  "created_at": "2025-08-08T10:30:00Z",
  "company_id": 1
}

# Collection
{
  "items": [...],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 150
  }
}

# Error
{
  "error": "ValidationError",
  "message": "Invalid input data",
  "details": [
    {"field": "name", "message": "Field required"}
  ]
}
```

## 🔄 Event-Driven Architecture

### Publishing Events
```python
# Automatic for CRUD operations
product = product_service.create(product_data)
# Automatically publishes PRODUCT_CREATED event

# Custom events
from messaging import MessagePublisher
publisher = MessagePublisher()
publisher.publish_event("CUSTOM_EVENT", {
    "data": "event_data",
    "timestamp": datetime.utcnow().isoformat()
})
```

### Consuming Events
```python
# In consumer service
@event_handler("PRODUCT_CREATED")
def handle_product_created(event_data):
    # Process new product
    pass
```

## 🧪 Testing

### Service Tests
```python
# tests/test_my_service.py
def test_create_object():
    service = MyService(db_session)
    data = {"name": "Test Object"}
    obj = service.create(data, company_id=1)
    assert obj.name == "Test Object"
    assert obj.company_id == 1
```

### API Tests
```python
# tests/test_api.py
def test_create_endpoint():
    response = client.post("/api/v1/my-objects/", 
                          json={"name": "Test"},
                          headers={"Authorization": "Bearer token"})
    assert response.status_code == 201
```

## 🐳 Docker & Deployment

### Docker Commands
```bash
# Build service
docker-compose build my-service

# Start service
docker-compose up -d my-service

# View logs
docker-compose logs my-service

# Stop service
docker-compose stop my-service
```

### Health Checks
```python
# Add to main.py
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}
```

## 🔧 Common Tasks

### Add Database Migration
```bash
# Create migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head
```

### Register Menu Items
```python
# In menu_init.py
menu_items = [
    {
        "name": "My Module",
        "path": "/my-module",
        "icon": "package"
    }
]
```

### Add Custom Business Logic
```python
# In service class
class MyService(GenericBusinessObjectService):
    def custom_business_operation(self, obj_id: int, company_id: int):
        obj = self.get_by_id(obj_id, company_id)
        # Custom logic here
        return result
```

## 📚 Key Documentation

- **Service Development**: docs/SERVICE_DEVELOPMENT_TUTORIAL.md
- **Business Framework**: docs/BUSINESS_OBJECT_FRAMEWORK.md
- **Service-Driven UI**: docs/SERVICE_DRIVEN_UI_FRAMEWORK.md
- **API Standards**: docs/API_STANDARDS.md
- **Testing Guide**: docs/TESTING_GUIDE.md

## 🆘 Getting Help

### Common Issues
1. **Service not registering**: Check Redis connection and service registry URL
2. **Events not firing**: Verify Redis Streams configuration
3. **Multi-company data leak**: Ensure company_id filtering in queries
4. **UI not showing**: Check UI schema endpoints and menu registration

### Debugging
```bash
# Check service logs
docker-compose logs my-service

# Test API endpoint
curl -X GET http://localhost:8XXX/api/v1/my-objects/

# Check database
psql -d my_service_db -c "SELECT * FROM my_objects LIMIT 5;"

# Monitor events
redis-cli -h localhost -p 6379
```

---
*Last Updated: 2025-09-03*
