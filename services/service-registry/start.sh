#!/bin/bash

echo "Starting Service Registry..."

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info