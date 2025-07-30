#!/bin/bash

echo "🚀 Starting Menu & Access Rights Service..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
while ! pg_isready -h postgres -p 5432 > /dev/null 2>&1; do
  sleep 1
done
echo "✅ Database is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Start the application
echo "🎉 Starting application server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload