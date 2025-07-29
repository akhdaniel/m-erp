#!/bin/bash
set -e

echo "🚀 Starting Company & Partner Management Service..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until pg_isready -h postgres -p 5432 -U cpuser -d company_partner_db; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "✅ Database is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

echo "🎉 Starting application server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload