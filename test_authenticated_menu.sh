#!/bin/bash

# Test authenticated menu access
# First, login to get a token
echo "Logging in as admin@example.com..."

LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

if [ -z "$TOKEN" ]; then
    echo "Failed to login. Response:"
    echo $LOGIN_RESPONSE
    exit 1
fi

echo "Got token: ${TOKEN:0:20}..."

# Now get menus with authentication
echo -e "\nFetching menus with authentication..."
curl -s http://localhost:8003/api/v1/menus/tree \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | grep -E "(title|code)" | head -20

echo -e "\nChecking user permissions from auth service..."
curl -s http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data = json.load(sys.stdin); print('User:', data.get('email')); print('Permissions:', data.get('permissions', [])[:5], '...')"