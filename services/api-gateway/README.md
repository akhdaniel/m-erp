# API Gateway Service

Kong-based API Gateway for M-ERP microservices system.

## Overview

This service provides centralized routing, authentication, rate limiting, and monitoring for all M-ERP microservices. It acts as the single entry point for all client requests.

## Configuration

The gateway is configured via `kong.yml` using Kong's declarative configuration format.

### Services Routing

- **User Auth Service**: `/api/v1/auth`, `/api/auth`, `/api/admin`, `/api/services`, `/api/token`, `/api/audit`, `/api/password`
- **Company Partner Service**: `/api/v1/companies`, `/api/v1/partners`
- **Menu Access Service**: `/api/v1/permissions`, `/api/v1/roles`, `/api/v1/menus`

## Features

- **CORS Support**: Configured for browser compatibility
- **Rate Limiting**: 100 requests/second, 1000/minute, 10000/hour
- **Request Size Limiting**: Maximum 10MB payload
- **Prometheus Metrics**: Performance monitoring and analytics
- **Consumer Management**: Development and service-to-service access

## Usage

### Development Access

Access the API gateway at `http://localhost:8080`

Example requests:
```bash
# User authentication
curl http://localhost:8080/api/auth/health

# Company management
curl http://localhost:8080/api/v1/companies

# Menu access
curl http://localhost:8080/api/v1/permissions
```

### Admin Interface

Kong's admin API is available at `http://localhost:8444` for configuration management.

## Monitoring

Prometheus metrics are exposed and can be scraped for monitoring:
- Request rates per service
- Response times
- Error rates
- Consumer-specific metrics

## Consumers

- `m-erp-development`: For development and testing
- `m-erp-services`: For service-to-service communication