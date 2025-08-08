# Audit Logger Service

A microservice that demonstrates event-driven patterns by consuming business events from other services and creating audit logs.

## Features

- Consumes all business events from the message queue
- Creates detailed audit logs for compliance and monitoring
- Demonstrates inter-service communication patterns
- Shows how services can be decoupled through messaging

## Events Processed

- User events (created, updated, logged in/out, etc.)
- Company events (created, updated, etc.)
- Partner events (created, updated, etc.)
- Security events (violations, lockouts, etc.)

## Architecture

This service demonstrates:
1. **Event Consumer** - Subscribes to business events
2. **Event Processing** - Transforms events into audit logs
3. **Database Storage** - Stores audit trails
4. **Health Monitoring** - Reports service health

## Usage

The service automatically starts consuming events when deployed with the rest of the XERPIUM system.

Audit logs include:
- Event type and timestamp
- Entity affected (user, company, partner, etc.)
- Changes made (before/after data)
- User who made the change
- Source service and correlation IDs
- Additional metadata

This provides a complete audit trail for compliance and security monitoring.