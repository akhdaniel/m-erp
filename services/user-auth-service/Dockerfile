FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY services/user-auth-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/user-auth-service/app/ ./app/
COPY services/user-auth-service/migrations/ ./migrations/
COPY services/user-auth-service/alembic.ini .
COPY services/user-auth-service/start.sh .
COPY services/user-auth-service/messaging/ ./messaging/

# Create non-root user and make start script executable
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app \
    && chmod +x start.sh
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["./start.sh"]