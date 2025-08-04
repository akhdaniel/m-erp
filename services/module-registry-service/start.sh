#!/bin/bash

# Module Registry Service Startup Script

echo "🚀 Starting Module Registry Service..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
python -c "
import time
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def wait_for_db():
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            engine = create_async_engine(settings.database_url)
            async with engine.begin() as conn:
                await conn.execute('SELECT 1')
            await engine.dispose()
            print('✅ Database is ready!')
            break
        except Exception as e:
            retry_count += 1
            print(f'⏳ Database not ready (attempt {retry_count}/{max_retries}): {e}')
            time.sleep(2)
    
    if retry_count >= max_retries:
        print('❌ Database connection failed after maximum retries')
        sys.exit(1)

asyncio.run(wait_for_db())
"

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Start the service
echo "🎯 Starting Module Registry Service on port 8005..."
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload