#!/bin/bash

echo "🐳 Testing M-ERP Docker Services"
echo "================================="

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo "🔍 Checking $service_name at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is healthy"
            return 0
        else
            echo "   Attempt $attempt/$max_attempts - waiting for $service_name..."
            sleep 2
            ((attempt++))
        fi
    done
    
    echo "❌ $service_name failed to start or respond"
    return 1
}

# Check if Docker Compose is running
echo "📋 Checking Docker Compose status..."
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Starting Docker Compose services..."
    docker-compose up -d
    echo "⏳ Waiting for services to initialize..."
    sleep 30
fi

echo ""
echo "🏥 Health Check Results:"
echo "------------------------"

# Check all services
check_service "User Auth Service" "http://localhost:8001/health"
check_service "Company Partner Service" "http://localhost:8002/health" 
check_service "Menu Access Service" "http://localhost:8003/health"
check_service "Service Registry" "http://localhost:8004/health"
check_service "Notification Service" "http://localhost:8005/health"
check_service "Inventory Service" "http://localhost:8005/health"
check_service "Sales Service" "http://localhost:8006/health"
check_service "Audit Service" "http://localhost:8007/health"

# Check infrastructure
check_service "Kong API Gateway" "http://localhost:9080"
check_service "UI Service" "http://localhost:3000"

echo ""
echo "📊 Service URLs:"
echo "----------------"
echo "• User Auth:     http://localhost:8001"
echo "• Partners:      http://localhost:8002" 
echo "• Menu Access:   http://localhost:8003"
echo "• Registry:      http://localhost:8004"
echo "• Inventory:     http://localhost:8005"
echo "• Sales:         http://localhost:8006"
echo "• Audit:         http://localhost:8007"
echo "• API Gateway:   http://localhost:9080"
echo "• UI Frontend:   http://localhost:3000"

echo ""
echo "🚀 API Documentation:"
echo "---------------------"
echo "• Sales API:     http://localhost:8006/api/docs"
echo "• Inventory API: http://localhost:8005/api/docs"
echo "• Partners API:  http://localhost:8002/docs"

echo ""
echo "🐳 Docker Status:"
docker-compose ps