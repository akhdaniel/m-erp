# Production Deployment Guide

## Overview

This guide covers deploying the User Authentication Service to production with enterprise-grade security, monitoring, and scalability.

## Prerequisites

- Docker and Docker Compose installed
- SSL certificates for HTTPS
- PostgreSQL database
- Redis instance
- Domain name configured

## Quick Start

1. **Copy production environment file:**
   ```bash
   cp .env.production.example .env.production
   ```

2. **Update environment variables:**
   Edit `.env.production` with your production values:
   - `SECRET_KEY` - Generate a strong 32+ character secret
   - `DATABASE_URL` - Production PostgreSQL connection
   - `REDIS_URL` - Production Redis connection
   - `ALLOWED_ORIGINS` - Your frontend domains

3. **Deploy with Docker Compose:**
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

## Environment Configuration

### Critical Security Settings

```bash
# Generate a secure secret key (32+ characters)
SECRET_KEY=your-super-secure-secret-key-at-least-32-characters-long

# Database connection
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/user_auth_prod

# Redis connection  
REDIS_URL=redis://:password@localhost:6379/0

# CORS origins (no wildcards in production)
ALLOWED_ORIGINS=https://your-frontend.com,https://admin.your-domain.com
```

### Security Settings

```bash
# Account security
MAX_FAILED_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
PROGRESSIVE_LOCKOUT=true

# Rate limiting
RATE_LIMITING_ENABLED=true
RATE_LIMIT_AUTH=5/minute
RATE_LIMIT_GENERAL=100/minute

# SSL/TLS
FORCE_HTTPS=true
HSTS_MAX_AGE=31536000
SECURE_COOKIES=true

# API documentation (disable in production)
DOCS_ENABLED=false
```

## Database Setup

### PostgreSQL Configuration

1. **Create production database:**
   ```sql
   CREATE DATABASE user_auth_prod;
   CREATE USER auth_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE user_auth_prod TO auth_user;
   ```

2. **Run migrations:**
   ```bash
   docker exec user-auth-service-prod alembic upgrade head
   ```

3. **Database optimization:**
   ```sql
   -- Recommended PostgreSQL settings for production
   ALTER SYSTEM SET shared_buffers = '256MB';
   ALTER SYSTEM SET effective_cache_size = '1GB';
   ALTER SYSTEM SET maintenance_work_mem = '64MB';
   ALTER SYSTEM SET checkpoint_completion_target = 0.9;
   ALTER SYSTEM SET wal_buffers = '16MB';
   ALTER SYSTEM SET default_statistics_target = 100;
   ```

## Redis Configuration

### Production Redis Setup

```bash
# Redis configuration for production
redis-server --requirepass your_redis_password \
             --maxmemory 256mb \
             --maxmemory-policy allkeys-lru \
             --save 900 1 \
             --save 300 10 \
             --save 60 10000
```

## SSL/TLS Setup

### Certificate Installation

1. **Obtain SSL certificates:**
   ```bash
   # Using Let's Encrypt (recommended)
   certbot certonly --standalone -d your-domain.com
   ```

2. **Copy certificates:**
   ```bash
   mkdir -p ssl/
   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
   cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
   ```

3. **Update nginx configuration:**
   Edit `nginx.prod.conf` and update `server_name` with your domain.

## Monitoring & Logging

### Health Checks

The service includes comprehensive health checks:
- Application health: `GET /health`
- Database connectivity
- Redis connectivity
- Service dependencies

### Logging Configuration

Production logging uses JSON format for structured logging:

```json
{
  "timestamp": "2025-07-28T10:00:00Z",
  "level": "INFO",
  "service": "user-auth-service",
  "message": "User login successful",
  "user_id": 123,
  "ip_address": "192.168.1.100"
}
```

### Monitoring Endpoints

- **Health Check:** `GET /health`
- **Metrics:** `GET /metrics` (if enabled)
- **Audit Logs:** `GET /api/admin/audit-logs`

## Security Configuration

### Security Headers

Production deployment includes comprehensive security headers:

```http
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
```

### Rate Limiting

Production rate limits by endpoint:

```yaml
/api/auth/login: 5/minute
/api/auth/register: 3/minute
/api/auth/refresh: 10/minute
/api/admin/*: 20/minute
default: 100/minute
```

### Account Security

- **Account Lockout:** 5 failed attempts = 15-minute lockout
- **Progressive Lockout:** Increasing lockout durations
- **Password Policy:** 8+ chars, complexity requirements
- **Password History:** Prevents last 5 passwords reuse

## Performance Optimization

### Application Scaling

```yaml
# Gunicorn configuration in production
workers: 4
worker_class: uvicorn.workers.UvicornWorker
worker_connections: 1000
max_requests: 1000
timeout: 120
```

### Database Connection Pooling

```python
# Database pool settings
pool_size: 20
max_overflow: 30
pool_timeout: 30
```

### Redis Connection Pooling

```python
# Redis pool settings
pool_size: 10
timeout: 5
```

## Backup Strategy

### Database Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U auth_user user_auth_prod > /backups/auth_backup_$DATE.sql
```

### Automated Backup

```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * /path/to/backup_script.sh
```

## Disaster Recovery

### Recovery Procedures

1. **Database Recovery:**
   ```bash
   psql -h localhost -U auth_user user_auth_prod < /backups/auth_backup_latest.sql
   ```

2. **Service Recovery:**
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

3. **Health Verification:**
   ```bash
   curl -f https://your-domain.com/health
   ```

## Maintenance

### Regular Maintenance Tasks

1. **Weekly:**
   - Review security logs
   - Check system resources
   - Verify backups

2. **Monthly:**
   - Update dependencies
   - Review performance metrics
   - Clean up old audit logs

3. **Quarterly:**
   - Security audit
   - Performance optimization
   - Disaster recovery testing

### Updates and Patches

```bash
# Update application
git pull origin main
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# Database migrations
docker exec user-auth-service-prod alembic upgrade head
```

## Troubleshooting

### Common Issues

1. **Service won't start:**
   ```bash
   # Check logs
   docker logs user-auth-service-prod
   
   # Check configuration
   docker exec user-auth-service-prod python -c "from app.core.production_config import get_production_settings; get_production_settings()"
   ```

2. **Database connection issues:**
   ```bash
   # Test database connectivity
   docker exec user-auth-service-prod pg_isready -h postgres -p 5432
   ```

3. **Redis connection issues:**
   ```bash
   # Test Redis connectivity
   docker exec user-auth-service-prod redis-cli -h redis ping
   ```

### Performance Issues

1. **High CPU usage:**
   - Check worker configuration
   - Review rate limiting settings
   - Monitor database query performance

2. **Memory issues:**
   - Check Redis memory usage
   - Review database connection pools
   - Monitor application memory leaks

3. **Slow response times:**
   - Check database query performance
   - Review Redis cache hit rates
   - Monitor network latency

## Security Checklist

### Pre-deployment Security Checklist

- [ ] Strong SECRET_KEY configured (32+ characters)
- [ ] Database credentials secured
- [ ] Redis password configured
- [ ] CORS origins properly configured (no wildcards)
- [ ] SSL certificates installed and valid
- [ ] API documentation disabled (`DOCS_ENABLED=false`)
- [ ] Debug mode disabled (`DEBUG=false`)
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Account lockout configured
- [ ] Audit logging enabled
- [ ] Log retention configured
- [ ] Monitoring and alerting setup

### Post-deployment Security Verification

- [ ] HTTPS working correctly
- [ ] Security headers present
- [ ] Rate limiting functional
- [ ] Authentication working
- [ ] Authorization working
- [ ] Audit logs being created
- [ ] Health checks responding
- [ ] Monitoring alerts configured

## Support

For production deployment support:
- Review application logs: `docker logs user-auth-service-prod`
- Check health endpoint: `curl https://your-domain.com/health`
- Monitor system resources: `docker stats`
- Review audit logs via admin endpoints

## Additional Resources

- [Security Documentation](./SECURITY.md)
- [API Documentation](./API.md)
- [Monitoring Guide](./MONITORING.md)
- [Backup Procedures](./BACKUP.md)