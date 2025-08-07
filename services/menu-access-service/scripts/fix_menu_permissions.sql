-- Fix menu permissions to allow public access to dashboard
-- and ensure admin role has all required permissions

-- Make dashboard menu public (no permission required)
UPDATE menus 
SET required_permission = NULL 
WHERE code IN ('dashboard', 'home');

-- Create missing permissions for menu access
INSERT INTO permissions (code, name, description, category)
VALUES 
    ('access_inventory', 'Access Inventory', 'Permission to access inventory module', 'inventory'),
    ('view_products', 'View Products', 'Permission to view products', 'inventory'),
    ('manage_stock', 'Manage Stock', 'Permission to manage stock', 'inventory'),
    ('view_warehouses', 'View Warehouses', 'Permission to view warehouses', 'inventory'),
    ('process_receiving', 'Process Receiving', 'Permission to process receiving', 'inventory'),
    ('access_sales', 'Access Sales', 'Permission to access sales module', 'sales'),
    ('manage_quotes', 'Manage Quotes', 'Permission to manage quotes', 'sales'),
    ('manage_orders', 'Manage Orders', 'Permission to manage orders', 'sales'),
    ('view_pricing', 'View Pricing', 'Permission to view pricing', 'sales'),
    ('sales_analytics', 'Sales Analytics', 'Permission to view sales analytics', 'sales')
ON CONFLICT (code) DO NOTHING;

-- Get admin role ID and ensure it has all permissions
DO $$
DECLARE
    admin_role_id INTEGER;
    perm RECORD;
BEGIN
    -- Get admin role ID
    SELECT id INTO admin_role_id FROM roles WHERE name = 'admin' OR name = 'Admin' LIMIT 1;
    
    IF admin_role_id IS NOT NULL THEN
        -- Add all menu-related permissions to admin role
        FOR perm IN 
            SELECT p.id 
            FROM permissions p
            WHERE p.code IN (
                'access_inventory', 'view_products', 'manage_stock', 
                'view_warehouses', 'process_receiving', 'access_sales',
                'manage_quotes', 'manage_orders', 'view_pricing', 'sales_analytics'
            )
        LOOP
            INSERT INTO role_permissions (role_id, permission_id)
            VALUES (admin_role_id, perm.id)
            ON CONFLICT DO NOTHING;
        END LOOP;
        
        RAISE NOTICE 'Admin role permissions updated successfully';
    ELSE
        RAISE NOTICE 'Admin role not found';
    END IF;
END $$;

-- Show current menu status
SELECT 
    name, 
    code, 
    CASE 
        WHEN required_permission IS NULL THEN 'PUBLIC'
        ELSE 'Requires: ' || required_permission
    END as permission_status,
    is_visible
FROM menus 
ORDER BY sequence, name;