# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY services/inventory-service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY services/shared /app/shared

# Copy application code from services/inventory-service (excluding shared directory)
COPY services/inventory-service/requirements.txt /app/
COPY services/inventory-service/main.py /app/
COPY services/inventory-service/inventory_module /app/inventory_module
COPY services/inventory-service/register_ui.py /app/
COPY services/inventory-service/ui_package.json /app/
COPY services/inventory-service/restart /app/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set Python path to include app directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose port
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]