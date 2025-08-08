#!/bin/bash

# Development startup script for UI Service
echo "🚀 Starting XERPIUM UI Service in development mode..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Running in Docker container, using Docker Vite config..."
    # Use the Docker-specific vite config by running with --config flag
    echo "🔥 Starting Vite development server with Docker configuration..."
    npm run dev -- --config vite.config.docker.ts
else
    echo "💻 Running locally, using standard Vite config..."
    echo "🔥 Starting Vite development server..."
    npm run dev
fi