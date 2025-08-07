#!/bin/bash

# Login as admin
echo "🔐 Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to login"
    exit 1
fi

echo "✅ Login successful"

# Get current roles
echo "📋 Getting current roles..."
ROLES=$(curl -s -X GET http://localhost:8001/roles/ \
  -H "Authorization: Bearer $TOKEN")

# Extract admin role ID
ADMIN_ROLE_ID=$(echo $ROLES | python3 -c "
import sys, json
roles = json.load(sys.stdin)
for role in roles:
    if role['name'] in ['admin', 'Admin', 'superuser']:
        print(role['id'])
        break
")

if [ -z "$ADMIN_ROLE_ID" ]; then
    echo "❌ Admin role not found"
    exit 1
fi

echo "✅ Found admin role ID: $ADMIN_ROLE_ID"

# Update admin role with all permissions
echo "🔧 Updating admin role permissions..."
UPDATE_RESPONSE=$(curl -s -X PUT http://localhost:8001/roles/$ADMIN_ROLE_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "admin",
    "description": "System Administrator with full access",
    "permissions": [
      "manage_system",
      "manage_partners",
      "manage_companies",
      "manage_currencies",
      "access_admin_dashboard",
      "manage_users",
      "view_audit_logs",
      "manage_roles",
      "companies.view",
      "companies.create",
      "companies.update",
      "companies.delete",
      "partners.view",
      "partners.create",
      "partners.update",
      "partners.delete",
      "users.view",
      "users.create",
      "users.update",
      "users.delete",
      "inventory.access",
      "inventory.manage",
      "sales.access",
      "sales.manage",
      "menu.view",
      "menu.admin"
    ]
  }')

# Check if update was successful
if echo $UPDATE_RESPONSE | grep -q '"id"'; then
    echo "✅ Successfully updated admin role permissions!"
    echo ""
    echo "📘 Next steps:"
    echo "1. Log out and log back in to get updated permissions"
    echo "2. The menu should now be visible in the UI"
else
    echo "❌ Failed to update role: $UPDATE_RESPONSE"
    exit 1
fi