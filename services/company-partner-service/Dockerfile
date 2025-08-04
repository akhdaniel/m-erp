FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY services/company-partner-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/company-partner-service/app/ ./app/
COPY services/company-partner-service/tests/ ./tests/
COPY services/company-partner-service/migrations/ ./migrations/
COPY services/company-partner-service/alembic.ini .
COPY services/company-partner-service/start.sh .
COPY services/company-partner-service/messaging/ ./messaging/

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