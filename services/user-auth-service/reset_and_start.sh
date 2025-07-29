#!/bin/bash

echo "🧹 Cleaning up Docker environment..."

# Stop and remove containers and volumes
docker-compose down -v

# Remove any orphaned containers
docker container prune -f

# Remove dangling images
docker image prune -f

echo "🚀 Starting fresh environment..."

# Build and start services
docker-compose up --build

echo "✅ Environment reset complete!"