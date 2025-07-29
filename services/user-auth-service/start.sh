#!/bin/bash
set -e

echo "🚀 Starting User Authentication Service..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until pg_isready -h postgres -p 5432 -U authuser -d userauth; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "✅ Database is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Seed initial data if needed
echo "🌱 Seeding initial data..."
python -c "
import asyncio
from app.core.seed_data import seed_initial_data

async def main():
    await seed_initial_data()
    print('✅ Initial data seeded successfully')

if __name__ == '__main__':
    asyncio.run(main())
" || echo "⚠️  Seeding skipped (data may already exist)"

echo "🎉 Starting application server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload