#!/bin/bash

# Sales Service startup script
echo "Starting Sales Service..."

# Wait for database to be ready
echo "Waiting for database connection..."
python -c "
import time
import psycopg2
import os
import sys

def wait_for_db():
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@postgres:5432/sales_db')
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Extract connection parameters from URL
            import re
            match = re.match(r'postgresql\+?.*://(.+):(.+)@(.+):(\d+)/(.+)', db_url)
            if match:
                user, password, host, port, database = match.groups()
                conn = psycopg2.connect(
                    host=host,
                    port=int(port),
                    user=user,
                    password=password,
                    database=database
                )
                conn.close()
                print('Database connection successful')
                return True
        except Exception as e:
            print(f'Database connection failed (attempt {retry_count + 1}/{max_retries}): {e}')
            time.sleep(2)
            retry_count += 1
    
    print('Failed to connect to database after maximum retries')
    return False

if not wait_for_db():
    sys.exit(1)
"

# Run database migrations if they exist
if [ -d "migrations" ]; then
    echo "Running database migrations..."
    alembic upgrade head || echo "Migration failed or no migrations to run"
fi

# Start the application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8006 --reload