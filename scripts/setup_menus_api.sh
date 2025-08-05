#!/bin/bash
# Setup script for inventory and sales menus using API calls

echo "🔧 Setting up Inventory Management and Sales Module menus..."

# Base URL for menu-access-service
BASE_URL="http://localhost:8003"

# Function to create a menu item
create_menu() {
    local endpoint="$1"
    local data="$2"
    
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$data" \
        "$BASE_URL$endpoint")
    
    if echo "$response" | grep -q "success\|created"; then
        echo "✅ Created: $(echo "$data" | grep -o '"title":"[^"]*"' | cut -d'"' -f4)"
    else
        echo "❌ Failed: $(echo "$response" | grep -o '"detail":"[^"]*"' | cut -d'"' -f4 2>/dev/null || echo "$response")"
    fi
}

echo "🏗️  Creating Inventory Management menus..."

# Inventory Management Root
create_menu "/api/v1/menus/" '{
    "code": "inventory_management",
    "title": "Inventory Management",
    "description": "Complete inventory and warehouse management system",
    "url": "/inventory",
    "icon": "fas fa-boxes-stacked",
    "order_index": 30,
    "level": 0,
    "item_type": "dropdown",
    "required_permission": "inventory.access"
}'

sleep 1

echo "🏗️  Creating Sales Management menus..."

# Sales Management Root
create_menu "/api/v1/menus/" '{
    "code": "sales_management",
    "title": "Sales Management",
    "description": "Complete sales and revenue management system",
    "url": "/sales",
    "icon": "fas fa-shopping-cart",
    "order_index": 20,
    "level": 0,
    "item_type": "dropdown",
    "required_permission": "sales.access"
}'

echo ""
echo "✅ Menu setup complete!"
echo ""
echo "📘 To see the new menus:"
echo "1. Refresh your M-ERP interface"
echo "2. The new menus should appear in the navigation"
echo "3. You may need to reload the page after menus are registered"
echo ""
echo "📱 UI will be available at: http://localhost:3000"