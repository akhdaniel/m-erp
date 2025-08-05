-- SQL Script to insert Inventory and Sales Management menu items and permissions
-- This script should be run against the menu_access_db

-- Insert permissions for Inventory Management
INSERT INTO permissions (code, name, description, is_enabled) VALUES
    ('inventory.access', 'Inventory Management', 'Access to inventory management system', true),
    ('products.view', 'View Products', 'View product catalog and details', true),
    ('products.manage', 'Manage Products', 'Create, update, and delete products', true),
    ('stock.view', 'View Stock', 'View stock levels and movements', true),
    ('warehouses.view', 'View Warehouses', 'View warehouse and location information', true),
    ('receiving.view', 'View Receiving', 'View inbound receiving operations', true)
ON CONFLICT (code) DO NOTHING;

-- Insert permissions for Sales Management
INSERT INTO permissions (code, name, description, is_enabled) VALUES
    ('sales.access', 'Sales Management', 'Access to sales management system', true),
    ('quotes.view', 'View Quotes', 'View sales quotes and proposals', true),
    ('orders.view', 'View Orders', 'View sales orders and processing', true),
    ('customers.view', 'View Customers', 'View customer accounts and details', true),
    ('invoices.view', 'View Invoices', 'View customer invoices', true)
ON CONFLICT (code) DO NOTHING;

-- Insert root menu items
INSERT INTO menu_items (code, title, description, url, icon, order_index, level, item_type, is_active, is_visible) VALUES
    ('inventory_management', 'Inventory Management', 'Complete inventory and warehouse management system', '/inventory', 'fas fa-boxes-stacked', 30, 0, 'dropdown', true, true),
    ('sales_management', 'Sales Management', 'Complete sales and revenue management system', '/sales', 'fas fa-shopping-cart', 20, 0, 'dropdown', true, true)
ON CONFLICT (code) DO NOTHING;

-- Insert Inventory Management sub-menu items
WITH root_inventory AS (SELECT id FROM menu_items WHERE code = 'inventory_management' LIMIT 1)
INSERT INTO menu_items (code, title, description, url, icon, parent_id, order_index, level, item_type, is_active, is_visible, required_permission)
SELECT 
    'products_catalog',
    'Products',
    'Product catalog and management',
    '/inventory/products',
    'fas fa-box',
    m.id,
    10,
    1,
    'link',
    true,
    true,
    'products.view'
FROM root_inventory m
UNION ALL
SELECT 
    'product_categories',
    'Product Categories',
    'Manage product categories and classification',
    '/inventory/categories',
    'fas fa-sitemap',
    m.id,
    20,
    1,
    'link',
    true,
    true,
    'products.view'
FROM root_inventory m
UNION ALL
SELECT 
    'stock_movements',
    'Stock Movements',
    'View stock movements and adjustments',
    '/inventory/stock-movements',
    'fas fa-arrows-alt-h',
    m.id,
    30,
    1,
    'link',
    true,
    true,
    'stock.view'
FROM root_inventory m
UNION ALL
SELECT 
    'stock_levels',
    'Stock Levels',
    'Current stock levels and alerts',
    '/inventory/stock-levels',
    'fas fa-chart-line',
    m.id,
    40,
    1,
    'link',
    true,
    true,
    'stock.view'
FROM root_inventory m
UNION ALL
SELECT 
    'warehouses_management',
    'Warehouses',
    'Warehouse and location management',
    '/inventory/warehouses',
    'fas fa-warehouse',
    m.id,
    50,
    1,
    'link',
    true,
    true,
    'warehouses.view'
FROM root_inventory m
UNION ALL
SELECT 
    'inventory_receiving',
    'Receiving',
    'Inbound inventory receiving operations',
    '/inventory/receiving',
    'fas fa-truck-loading',
    m.id,
    60,
    1,
    'link',
    true,
    true,
    'receiving.view'
FROM root_inventory m
ON CONFLICT (code) DO NOTHING;

-- Insert Sales Management sub-menu items
WITH root_sales AS (SELECT id FROM menu_items WHERE code = 'sales_management' LIMIT 1)
INSERT INTO menu_items (code, title, description, url, icon, parent_id, order_index, level, item_type, is_active, is_visible, required_permission)
SELECT 
    'quotes_management',
    'Sales Quotes',
    'Create and manage sales quotes and proposals',
    '/sales/quotes',
    'fas fa-file-invoice-dollar',
    m.id,
    10,
    1,
    'link',
    true,
    true,
    'quotes.view'
FROM root_sales m
UNION ALL
SELECT 
    'sales_orders',
    'Sales Orders',
    'Process and manage sales orders',
    '/sales/orders',
    'fas fa-receipt',
    m.id,
    20,
    1,
    'link',
    true,
    true,
    'orders.view'
FROM root_sales m
UNION ALL
SELECT 
    'customers_management',
    'Customers',
    'Manage customer accounts and relationships',
    '/sales/customers',
    'fas fa-users',
    m.id,
    30,
    1,
    'link',
    true,
    true,
    'customers.view'
FROM root_sales m
UNION ALL
SELECT 
    'sales_products',
    'Products',
    'Product catalog and inventory for sales',
    '/sales/products',
    'fas fa-tags',
    m.id,
    40,
    1,
    'link',
    true,
    true,
    'products.view'
FROM root_sales m
UNION ALL
SELECT 
    'sales_invoices',
    'Invoices',
    'Sales invoices and billing management',
    '/sales/invoices',
    'fas fa-file-invoice',
    m.id,
    50,
    1,
    'link',
    true,
    true,
    'invoices.view'
FROM root_sales m
UNION ALL
SELECT 
    'sales_analytics',
    'Sales Analytics',
    'Sales reports and performance analytics',
    '/sales/analytics',
    'fas fa-chart-bar',
    m.id,
    60,
    1,
    'link',
    true,
    true,
    NULL
FROM root_sales m
ON CONFLICT (code) DO NOTHING;

-- Optional: Add a simple permission-to-role mapping for admin role
INSERT INTO role_permissions (role_id, permission_id, granted_at)
SELECT 1, p.id, NOW()
FROM permissions p
WHERE p.code IN ('inventory.access', 'products.view', 'stock.view', 'warehouses.view', 'receiving.view',
                 'sales.access', 'quotes.view', 'orders.view', 'customers.view', 'invoices.view')
ON CONFLICT DO NOTHING;