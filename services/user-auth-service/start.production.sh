#!/bin/bash

# Production startup script for User Authentication Service
set -e

echo "🚀 Starting User Authentication Service (Production)..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
while ! pg_isready -h "${DATABASE_HOST:-postgres}" -p "${DATABASE_PORT:-5432}" -U "${DATABASE_USER:-postgres}"; do
    echo "Database not ready, waiting..."
    sleep 2
done
echo "✅ Database is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
while ! redis-cli -h "${REDIS_HOST:-redis}" -p "${REDIS_PORT:-6379}" ping > /dev/null 2>&1; do
    echo "Redis not ready, waiting..."
    sleep 2
done
echo "✅ Redis is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head
echo "✅ Database migrations completed!"

# Seed initial data (if needed)
echo "🌱 Seeding initial data..."
python -c "
import asyncio
from app.core.database import get_db
from app.scripts.seed_data import seed_initial_data

async def main():
    async for db in get_db():
        await seed_initial_data(db)
        break

if __name__ == '__main__':
    asyncio.run(main())
"
echo "✅ Initial data seeded successfully!"

# Validate production configuration
echo "🔧 Validating production configuration..."
python -c "
from app.core.production_config import get_production_settings
try:
    settings = get_production_settings()
    print('✅ Production configuration is valid')
except Exception as e:
    print(f'❌ Production configuration error: {e}')
    exit(1)
"

# Set production security settings
export ENVIRONMENT=production
export DEBUG=false

# Start the application with production settings
echo "🎉 Starting application server (Production Mode)..."

# Use Gunicorn for production with multiple workers
exec gunicorn app.main:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 120 \
    --keep-alive 5 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance