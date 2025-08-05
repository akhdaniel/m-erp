#!/bin/bash

# Sales Service Development Server Runner
# This script starts the FastAPI development server

echo "🚀 Starting Sales Service Development Server"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Set environment variables
export SERVICE_NAME="sales-service"
export SERVICE_PORT=8006
export DEBUG=true

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Service Information:"
echo "   • Service URL: http://localhost:8006"
echo "   • API Documentation: http://localhost:8006/api/docs"
echo "   • Health Check: http://localhost:8006/health"
echo "   • Quote API: http://localhost:8006/api/v1/quotes/"
echo ""
echo "🌐 Starting server..."
echo "   Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python main.py