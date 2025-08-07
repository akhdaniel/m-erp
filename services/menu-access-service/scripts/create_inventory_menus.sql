-- Create inventory menu items

-- Main inventory menu
INSERT INTO menu_items (
    code, 
    title, 
    description, 
    parent_id, 
    order_index, 
    level, 
    url, 
    icon, 
    item_type, 
    is_external, 
    is_active, 
    is_visible, 
    required_permission
) VALUES 
-- Root level menu
('inventory_management', 'Inventory', 'Inventory Management', NULL, 3, 0, '#', 'warehouse', 'menu', false, true, true, 'access_inventory'),

-- Sub menus
('inventory_products', 'Products', 'Product Management', 1, 1, 1, '/inventory/products', 'box', 'link', false, true, true, 'view_products'),
('inventory_stock', 'Stock', 'Stock Management', 1, 2, 1, '/inventory/stock', 'layers', 'link', false, true, true, 'view_stock'),
('inventory_warehouses', 'Warehouses', 'Warehouse Management', 1, 3, 1, '/inventory/warehouses', 'building', 'link', false, true, true, 'view_warehouses'),
('inventory_receiving', 'Receiving', 'Receiving Management', 1, 4, 1, '/inventory/receiving', 'truck', 'link', false, true, true, 'manage_stock'),
('inventory_reports', 'Reports', 'Inventory Reports', 1, 5, 1, '/inventory/reports', 'file-text', 'link', false, true, true, 'view_inventory_reports');

-- Update parent_id references to actual IDs
UPDATE menu_items 
SET parent_id = (SELECT id FROM menu_items WHERE code = 'inventory_management')
WHERE code IN ('inventory_products', 'inventory_stock', 'inventory_warehouses', 'inventory_receiving', 'inventory_reports');