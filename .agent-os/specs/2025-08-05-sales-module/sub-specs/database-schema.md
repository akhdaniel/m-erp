# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-08-05-sales-module/spec.md

> Created: 2025-08-05
> Version: 1.0.0

## Database Schema Changes

### New Tables

#### quotes
```sql
CREATE TABLE quotes (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    quote_number VARCHAR(50) NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES partners(id),
    quote_date DATE NOT NULL,
    expiration_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'draft', -- draft, sent, approved, rejected, expired, converted
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    tax_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    currency_code VARCHAR(3) NOT NULL DEFAULT 'USD',
    terms TEXT,
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    framework_version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    
    CONSTRAINT quotes_company_quote_number_unique UNIQUE(company_id, quote_number),
    CONSTRAINT quotes_status_check CHECK (status IN ('draft', 'sent', 'approved', 'rejected', 'expired', 'converted')),
    CONSTRAINT quotes_expiration_after_quote_date CHECK (expiration_date IS NULL OR expiration_date >= quote_date),
    CONSTRAINT quotes_amounts_non_negative CHECK (
        subtotal >= 0 AND tax_amount >= 0 AND 
        discount_amount >= 0 AND total_amount >= 0
    )
);

CREATE INDEX idx_quotes_company_id ON quotes(company_id);
CREATE INDEX idx_quotes_customer_id ON quotes(customer_id);
CREATE INDEX idx_quotes_status ON quotes(status);
CREATE INDEX idx_quotes_quote_date ON quotes(quote_date);
CREATE INDEX idx_quotes_expiration_date ON quotes(expiration_date);
```

#### quote_lines  
```sql
CREATE TABLE quote_lines (
    id SERIAL PRIMARY KEY,
    quote_id INTEGER NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL, -- References inventory module product
    product_name VARCHAR(255) NOT NULL, -- Snapshot of product name
    product_code VARCHAR(100), -- Snapshot of product code
    description TEXT,
    quantity DECIMAL(12,3) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0.00,
    discount_amount DECIMAL(12,2) DEFAULT 0.00,
    line_total DECIMAL(12,2) NOT NULL,
    currency_code VARCHAR(3) NOT NULL DEFAULT 'USD',
    delivery_estimate_days INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT quote_lines_quantity_positive CHECK (quantity > 0),
    CONSTRAINT quote_lines_unit_price_non_negative CHECK (unit_price >= 0),
    CONSTRAINT quote_lines_discount_percent_valid CHECK (discount_percent >= 0 AND discount_percent <= 100),
    CONSTRAINT quote_lines_discount_amount_non_negative CHECK (discount_amount >= 0),
    CONSTRAINT quote_lines_line_total_non_negative CHECK (line_total >= 0)
);

CREATE INDEX idx_quote_lines_quote_id ON quote_lines(quote_id);
CREATE INDEX idx_quote_lines_product_id ON quote_lines(product_id);
```

#### sales_orders
```sql
CREATE TABLE sales_orders (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    order_number VARCHAR(50) NOT NULL,
    quote_id INTEGER REFERENCES quotes(id),
    customer_id INTEGER NOT NULL REFERENCES partners(id),
    order_date DATE NOT NULL,
    requested_delivery_date DATE,
    promised_delivery_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'confirmed', -- confirmed, processing, shipped, delivered, cancelled
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    tax_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    currency_code VARCHAR(3) NOT NULL DEFAULT 'USD',
    payment_terms VARCHAR(50),
    shipping_address TEXT,
    billing_address TEXT,
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    framework_version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    
    CONSTRAINT sales_orders_company_order_number_unique UNIQUE(company_id, order_number),
    CONSTRAINT sales_orders_status_check CHECK (status IN ('confirmed', 'processing', 'shipped', 'delivered', 'cancelled')),
    CONSTRAINT sales_orders_delivery_dates_check CHECK (
        requested_delivery_date IS NULL OR requested_delivery_date >= order_date
    ),
    CONSTRAINT sales_orders_amounts_non_negative CHECK (
        subtotal >= 0 AND tax_amount >= 0 AND 
        discount_amount >= 0 AND total_amount >= 0
    )
);

CREATE INDEX idx_sales_orders_company_id ON sales_orders(company_id);
CREATE INDEX idx_sales_orders_customer_id ON sales_orders(customer_id);
CREATE INDEX idx_sales_orders_quote_id ON sales_orders(quote_id);
CREATE INDEX idx_sales_orders_status ON sales_orders(status);
CREATE INDEX idx_sales_orders_order_date ON sales_orders(order_date);
CREATE INDEX idx_sales_orders_requested_delivery_date ON sales_orders(requested_delivery_date);
```

#### sales_order_lines
```sql
CREATE TABLE sales_order_lines (
    id SERIAL PRIMARY KEY,
    sales_order_id INTEGER NOT NULL REFERENCES sales_orders(id) ON DELETE CASCADE,
    quote_line_id INTEGER REFERENCES quote_lines(id),
    product_id INTEGER NOT NULL, -- References inventory module product
    product_name VARCHAR(255) NOT NULL, -- Snapshot of product name
    product_code VARCHAR(100), -- Snapshot of product code
    description TEXT,
    quantity_ordered DECIMAL(12,3) NOT NULL,
    quantity_shipped DECIMAL(12,3) DEFAULT 0.00,
    quantity_remaining DECIMAL(12,3) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0.00,
    discount_amount DECIMAL(12,2) DEFAULT 0.00,
    line_total DECIMAL(12,2) NOT NULL,
    currency_code VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'pending', -- pending, reserved, shipped, delivered, cancelled
    reservation_id VARCHAR(100), -- References inventory reservation
    scheduled_ship_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT sales_order_lines_quantity_ordered_positive CHECK (quantity_ordered > 0),
    CONSTRAINT sales_order_lines_quantity_shipped_non_negative CHECK (quantity_shipped >= 0),
    CONSTRAINT sales_order_lines_quantity_remaining_non_negative CHECK (quantity_remaining >= 0),
    CONSTRAINT sales_order_lines_unit_price_non_negative CHECK (unit_price >= 0),
    CONSTRAINT sales_order_lines_discount_percent_valid CHECK (discount_percent >= 0 AND discount_percent <= 100),
    CONSTRAINT sales_order_lines_discount_amount_non_negative CHECK (discount_amount >= 0),
    CONSTRAINT sales_order_lines_line_total_non_negative CHECK (line_total >= 0),
    CONSTRAINT sales_order_lines_status_check CHECK (status IN ('pending', 'reserved', 'shipped', 'delivered', 'cancelled'))
);

CREATE INDEX idx_sales_order_lines_sales_order_id ON sales_order_lines(sales_order_id);
CREATE INDEX idx_sales_order_lines_product_id ON sales_order_lines(product_id);
CREATE INDEX idx_sales_order_lines_quote_line_id ON sales_order_lines(quote_line_id);
CREATE INDEX idx_sales_order_lines_status ON sales_order_lines(status);
CREATE INDEX idx_sales_order_lines_reservation_id ON sales_order_lines(reservation_id);
```

#### pricing_rules
```sql
CREATE TABLE pricing_rules (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    rule_type VARCHAR(30) NOT NULL, -- customer_specific, volume_discount, promotional, product_category
    priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    
    -- Customer specific rules
    customer_id INTEGER REFERENCES partners(id),
    
    -- Product specific rules  
    product_id INTEGER, -- References inventory module product
    product_category_id INTEGER, -- References inventory module category
    
    -- Volume discount rules
    min_quantity DECIMAL(12,3),
    max_quantity DECIMAL(12,3),
    min_amount DECIMAL(12,2),
    max_amount DECIMAL(12,2),
    
    -- Discount configuration
    discount_type VARCHAR(20) NOT NULL DEFAULT 'percentage', -- percentage, fixed_amount, fixed_price
    discount_value DECIMAL(12,2) NOT NULL,
    
    -- Date range for promotional rules
    start_date DATE,
    end_date DATE,
    
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    framework_version INTEGER DEFAULT 1,
    
    CONSTRAINT pricing_rules_rule_type_check CHECK (rule_type IN ('customer_specific', 'volume_discount', 'promotional', 'product_category')),
    CONSTRAINT pricing_rules_discount_type_check CHECK (discount_type IN ('percentage', 'fixed_amount', 'fixed_price')),
    CONSTRAINT pricing_rules_discount_value_non_negative CHECK (discount_value >= 0),
    CONSTRAINT pricing_rules_quantities_valid CHECK (
        min_quantity IS NULL OR max_quantity IS NULL OR min_quantity <= max_quantity
    ),
    CONSTRAINT pricing_rules_amounts_valid CHECK (
        min_amount IS NULL OR max_amount IS NULL OR min_amount <= max_amount
    ),
    CONSTRAINT pricing_rules_date_range_valid CHECK (
        start_date IS NULL OR end_date IS NULL OR start_date <= end_date
    )
);

CREATE INDEX idx_pricing_rules_company_id ON pricing_rules(company_id);
CREATE INDEX idx_pricing_rules_customer_id ON pricing_rules(customer_id);
CREATE INDEX idx_pricing_rules_product_id ON pricing_rules(product_id);
CREATE INDEX idx_pricing_rules_rule_type ON pricing_rules(rule_type);
CREATE INDEX idx_pricing_rules_is_active ON pricing_rules(is_active);
CREATE INDEX idx_pricing_rules_priority ON pricing_rules(priority);
```

### Table Modifications

No modifications to existing tables required. The sales module integrates with existing tables through foreign key references:
- `partners` table for customer relationships
- `companies` table for multi-company data isolation  
- `users` table for audit and approval tracking
- Inventory module tables through API integration (no direct foreign keys)

### Migration Strategy

1. **Create sales module database** following established patterns
2. **Run table creation scripts** in dependency order (quotes, quote_lines, sales_orders, sales_order_lines, pricing_rules)
3. **Verify foreign key constraints** to existing partner and company tables
4. **Create initial data** including default pricing rules and system configurations
5. **Test integration points** with inventory module for product references

### Data Integrity Rules

- **Multi-company isolation** enforced through company_id in all main tables
- **Cascade deletes** for line items when parent records are deleted
- **Audit trail** maintained through framework_version and timestamp columns
- **Data validation** enforced through database constraints and application logic
- **Referential integrity** maintained for partner and user relationships
- **Cross-service integrity** managed through API calls and event publishing