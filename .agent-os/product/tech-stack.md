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
- **UI Servce**: 
	- port: 9000
	- use external network chat_odoo_network so that reachable from external nginx proxy  contianer
- **Kong Servce**: 
	- port: 8000
- **Redit Service**: 
	- port: 6379
- **PostgreSQL**: 
	- port: 5432
- **user-auth-service**: 
	- port: 8001
- **company-partner-service**: 
	- port: 8002
- **menu-access-service**: 
	- port 8003
- **service-registry**: 
	- port: 8004
- **inventory-service**: 
	- port: 8005
- **sales-service**: 
	- port: 8006
- **purchasing-service**: 
	- port: 8007
- **notification-registry**: 
	- port: 8009
- **ui-registry**: 
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
