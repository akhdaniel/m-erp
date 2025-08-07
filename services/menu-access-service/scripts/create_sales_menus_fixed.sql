-- Create Sales Menus and Permissions
-- This script creates the sales module menu structure and associated permissions

-- First, create the sales permissions if they don't exist
INSERT INTO permissions (code, name, description, category, action, is_active, is_system)
VALUES 
    ('access_sales', 'Access Sales', 'Permission to access sales module', 'sales', 'access', true, false),
    ('manage_quotes', 'Manage Quotes', 'Permission to create and manage quotes', 'sales', 'manage', true, false),
    ('manage_orders', 'Manage Orders', 'Permission to create and manage sales orders', 'sales', 'manage', true, false),
    ('view_pricing', 'View Pricing', 'Permission to view pricing rules', 'sales', 'view', true, false),
    ('manage_pricing', 'Manage Pricing', 'Permission to manage pricing rules', 'sales', 'manage', true, false),
    ('sales_analytics', 'Sales Analytics', 'Permission to view sales analytics', 'sales', 'view', true, false),
    ('approve_discounts', 'Approve Discounts', 'Permission to approve special discounts', 'sales', 'approve', true, false)
ON CONFLICT (code) DO NOTHING;

-- Create the main Sales dropdown menu
INSERT INTO menu_items (
    code, title, description, parent_id, order_index, level, 
    url, icon, target, item_type, is_external, is_active, is_visible, required_permission
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
    NULL,  -- target
    'dropdown',
    false, -- is_external
    true,  -- is_active
    true,  -- is_visible
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
        url, icon, target, item_type, is_external, is_active, is_visible, required_permission
    )
    VALUES 
        ('sales_quotes', 'Quotes', 'Quote Management', sales_menu_id, 1, 1, 
         '/sales/quotes', 'file-text', NULL, 'link', false, true, true, 'manage_quotes'),
        
        ('sales_orders', 'Orders', 'Sales Order Management', sales_menu_id, 2, 1,
         '/sales/orders', 'shopping-bag', NULL, 'link', false, true, true, 'manage_orders'),
        
        ('sales_pricing', 'Pricing Rules', 'Pricing Management', sales_menu_id, 3, 1,
         '/sales/pricing', 'dollar-sign', NULL, 'link', false, true, true, 'view_pricing'),
        
        ('sales_customers', 'Customers', 'Customer Management', sales_menu_id, 4, 1,
         '/sales/customers', 'users', NULL, 'link', false, true, true, 'access_sales'),
         
        ('sales_analytics', 'Analytics', 'Sales Analytics & Reports', sales_menu_id, 5, 1,
         '/sales/analytics', 'bar-chart', NULL, 'link', false, true, true, 'sales_analytics')
    ON CONFLICT (code) DO NOTHING;
    
    RAISE NOTICE 'Created sales submenus under parent ID: %', sales_menu_id;
END $$;

-- Check if sales roles exist in user_auth database
-- Note: Roles are in the user_auth database, not menu_access_db
-- We need to ensure the admin user has the sales permissions

-- For now, let's display what we created
SELECT 'Created Sales Menu Structure:' as info;
SELECT id, code, title, parent_id, required_permission 
FROM menu_items 
WHERE code LIKE '%sales%' 
ORDER BY parent_id NULLS FIRST, order_index;

SELECT 'Created Sales Permissions:' as info;
SELECT id, code, name, category, action
FROM permissions
WHERE category = 'sales'
ORDER BY code;