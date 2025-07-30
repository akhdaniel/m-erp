#!/bin/bash

# Development startup script for UI Service
echo "🚀 Starting M-ERP UI Service in development mode..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🔥 Starting Vite development server..."
npm run dev