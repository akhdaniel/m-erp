-- Create Sales Menus and Permissions
-- This script creates the sales module menu structure and associated permissions

-- First, create the sales permissions if they don't exist
INSERT INTO permissions (code, name, description, category)
VALUES 
    ('access_sales', 'Access Sales', 'Permission to access sales module', 'sales'),
    ('manage_quotes', 'Manage Quotes', 'Permission to create and manage quotes', 'sales'),
    ('manage_orders', 'Manage Orders', 'Permission to create and manage sales orders', 'sales'),
    ('view_pricing', 'View Pricing', 'Permission to view pricing rules', 'sales'),
    ('manage_pricing', 'Manage Pricing', 'Permission to manage pricing rules', 'sales'),
    ('sales_analytics', 'Sales Analytics', 'Permission to view sales analytics', 'sales'),
    ('approve_discounts', 'Approve Discounts', 'Permission to approve special discounts', 'sales')
ON CONFLICT (code) DO NOTHING;

-- Create the main Sales dropdown menu
INSERT INTO menu_items (
    code, title, description, parent_id, order_index, level, 
    url, icon, item_type, is_active, is_visible, required_permission
)
VALUES (
    'sales_management', 
    'Sales', 
    'Sales Management',
    NULL,  -- Top-level menu
    2,     -- After Inventory menu
    0,     -- Top level
    '#',   -- Dropdown URL
    'shopping-cart',
    'dropdown',
    true,
    true,
    'access_sales'
)
ON CONFLICT (code) DO NOTHING;

-- Get the sales menu ID for setting as parent
DO $$
DECLARE
    sales_menu_id INTEGER;
BEGIN
    SELECT id INTO sales_menu_id FROM menu_items WHERE code = 'sales_management';
    
    -- Create Sales submenu items
    INSERT INTO menu_items (
        code, title, description, parent_id, order_index, level, 
        url, icon, item_type, is_active, is_visible, required_permission
    )
    VALUES 
        ('sales_quotes', 'Quotes', 'Quote Management', sales_menu_id, 1, 1, 
         '/sales/quotes', 'file-text', 'link', true, true, 'manage_quotes'),
        
        ('sales_orders', 'Orders', 'Sales Order Management', sales_menu_id, 2, 1,
         '/sales/orders', 'shopping-bag', 'link', true, true, 'manage_orders'),
        
        ('sales_pricing', 'Pricing Rules', 'Pricing Management', sales_menu_id, 3, 1,
         '/sales/pricing', 'dollar-sign', 'link', true, true, 'view_pricing'),
        
        ('sales_customers', 'Customers', 'Customer Management', sales_menu_id, 4, 1,
         '/sales/customers', 'users', 'link', true, true, 'access_sales'),
         
        ('sales_analytics', 'Analytics', 'Sales Analytics & Reports', sales_menu_id, 5, 1,
         '/sales/analytics', 'bar-chart', 'link', true, true, 'sales_analytics')
    ON CONFLICT (code) DO NOTHING;
END $$;

-- Now link permissions to sales roles
-- First, let's check what roles exist
SELECT 'Current roles:' as info;
SELECT id, name FROM roles WHERE name LIKE '%sales%';

-- Get role IDs and assign permissions
DO $$
DECLARE
    sales_user_role_id INTEGER;
    sales_manager_role_id INTEGER;
    perm RECORD;
BEGIN
    -- Get sales role IDs
    SELECT id INTO sales_user_role_id FROM roles WHERE name = 'sales_user';
    SELECT id INTO sales_manager_role_id FROM roles WHERE name = 'sales_manager';
    
    -- Assign basic sales permissions to sales_user role
    IF sales_user_role_id IS NOT NULL THEN
        FOR perm IN 
            SELECT id FROM permissions 
            WHERE code IN ('access_sales', 'manage_quotes', 'manage_orders', 'view_pricing')
        LOOP
            INSERT INTO role_permissions (role_id, permission_id)
            VALUES (sales_user_role_id, perm.id)
            ON CONFLICT DO NOTHING;
        END LOOP;
        RAISE NOTICE 'Added permissions to sales_user role';
    END IF;
    
    -- Assign all sales permissions to sales_manager role
    IF sales_manager_role_id IS NOT NULL THEN
        FOR perm IN 
            SELECT id FROM permissions 
            WHERE code IN ('access_sales', 'manage_quotes', 'manage_orders', 
                          'view_pricing', 'manage_pricing', 'sales_analytics', 
                          'approve_discounts')
        LOOP
            INSERT INTO role_permissions (role_id, permission_id)
            VALUES (sales_manager_role_id, perm.id)
            ON CONFLICT DO NOTHING;
        END LOOP;
        RAISE NOTICE 'Added permissions to sales_manager role';
    END IF;
END $$;

-- Display the created menu structure
SELECT 'Created Sales Menu Structure:' as info;
SELECT id, code, title, parent_id, required_permission 
FROM menu_items 
WHERE code LIKE '%sales%' 
ORDER BY order_index;

-- Display role permissions
SELECT 'Sales Role Permissions:' as info;
SELECT r.name as role_name, p.code as permission_code, p.name as permission_name
FROM roles r
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
WHERE r.name LIKE '%sales%'
ORDER BY r.name, p.code;