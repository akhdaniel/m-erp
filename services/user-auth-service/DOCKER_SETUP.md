# Docker Setup and Troubleshooting Guide

## Quick Start

1. **Stop any existing containers:**
   ```bash
   docker-compose down
   ```

2. **Build and start the services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - API: http://localhost:8000
   - Health check: http://localhost:8000/health
   - API docs: http://localhost:8000/docs

## Troubleshooting Common Issues

### Issue: "Nothing loads in browser"

**Solution:**
- Make sure you're accessing `http://localhost:8000` (not `http://0.0.0.0:8000`)
- Check if the container is running: `docker ps`
- Check logs: `docker-compose logs auth-service`

### Issue: "Database connection failed"

**Solution:**
1. Check if PostgreSQL is running: `docker-compose logs postgres`
2. Wait for database to be fully ready (may take 30-60 seconds on first run)
3. Restart the services: `docker-compose restart`

### Issue: "Port already in use"

**Solution:**
1. Check what's using port 8000: `lsof -i :8000`
2. Either stop the conflicting service or change the port in `docker-compose.yml`:
   ```yaml
   ports:
     - "8001:8000"  # Use port 8001 on host instead
   ```

### Issue: "Build fails"

**Solution:**
1. Clean up Docker cache:
   ```bash
   docker system prune -f
   docker-compose build --no-cache
   ```

## Testing the Service

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "User Authentication Service",
  "version": "1.0.0",
  "environment": "development"
}
```

### 2. API Documentation
Visit: http://localhost:8000/docs

This will show you all available endpoints with interactive testing capabilities.

### 3. User Registration
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

## Container Management

### View running containers:
```bash
docker ps
```

### View logs:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs auth-service
docker-compose logs postgres
```

### Restart services:
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart auth-service
```

### Stop services:
```bash
docker-compose down
```

### Clean up (removes volumes):
```bash
docker-compose down -v
```

## Development Mode

For development with auto-reload:

1. **Install dependencies locally:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start only the database:**
   ```bash
   docker-compose up postgres
   ```

3. **Run the application locally:**
   ```bash
   export DATABASE_URL="postgresql+asyncpg://authuser:authpass123@localhost:5432/userauth"
   export SECRET_KEY="your-secret-key"
   export DEBUG=true
   
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Environment Variables

Key environment variables in `docker-compose.yml`:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (change in production!)
- `DEBUG`: Enable debug mode
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `ALLOWED_ORIGINS`: CORS allowed origins

## Database Access

To access the PostgreSQL database directly:

```bash
docker exec -it user-auth-postgres psql -U authuser -d userauth
```

Common SQL commands:
```sql
-- List tables
\dt

-- List users
SELECT * FROM users;

-- List roles
SELECT * FROM roles;
```

## Common URLs

- **Health Check:** http://localhost:8000/health
- **API Documentation:** http://localhost:8000/docs
- **OpenAPI JSON:** http://localhost:8000/openapi.json
- **ReDoc:** http://localhost:8000/redoc

## Next Steps

Once the service is running:

1. Visit http://localhost:8000/docs to explore the API
2. Register a test user via the API
3. Test authentication endpoints
4. Explore admin functionality (requires admin user)

For production deployment, make sure to:
- Change the `SECRET_KEY` to a secure random value
- Use strong database passwords
- Set up proper networking and security groups
- Configure proper logging and monitoring