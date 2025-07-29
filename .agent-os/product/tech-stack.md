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