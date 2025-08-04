# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-08-02-extension-system-purchasing-module/spec.md

> Created: 2025-08-02
> Version: 1.0.0

## Schema Changes

### Module Registry Service Database

#### New Tables

```sql
-- Module registry and lifecycle management
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    version VARCHAR(20) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    author VARCHAR(100),
    homepage_url VARCHAR(500),
    documentation_url VARCHAR(500),
    manifest_schema JSONB NOT NULL,
    package_url VARCHAR(500),
    package_checksum VARCHAR(64),
    status VARCHAR(20) NOT NULL DEFAULT 'available',  -- available, installing, installed, disabled, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    framework_version VARCHAR(20) NOT NULL
);

CREATE INDEX idx_modules_name ON modules(name);
CREATE INDEX idx_modules_status ON modules(status);
CREATE INDEX idx_modules_created_at ON modules(created_at);

-- Module installations per company
CREATE TABLE module_installations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    company_id UUID NOT NULL,
    configuration JSONB DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'installing',  -- installing, installed, updating, failed, uninstalling
    installed_version VARCHAR(20) NOT NULL,
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_health_check TIMESTAMP WITH TIME ZONE,
    health_status VARCHAR(20) DEFAULT 'unknown',  -- healthy, unhealthy, unknown
    error_message TEXT,
    UNIQUE(module_id, company_id)
);

CREATE INDEX idx_module_installations_company ON module_installations(company_id);
CREATE INDEX idx_module_installations_status ON module_installations(status);
CREATE INDEX idx_module_installations_health ON module_installations(health_status);

-- Module dependencies
CREATE TABLE module_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    dependency_name VARCHAR(100) NOT NULL,
    dependency_version VARCHAR(20) NOT NULL,
    dependency_type VARCHAR(20) NOT NULL DEFAULT 'module',  -- module, service, library
    required BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_module_dependencies_module ON module_dependencies(module_id);
CREATE INDEX idx_module_dependencies_name ON module_dependencies(dependency_name);

-- Module API endpoints registration
CREATE TABLE module_endpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    path VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,  -- GET, POST, PUT, DELETE, PATCH
    handler_function VARCHAR(200) NOT NULL,
    permissions JSONB DEFAULT '[]',
    rate_limit_per_minute INTEGER DEFAULT 60,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_module_endpoints_module ON module_endpoints(module_id);
CREATE INDEX idx_module_endpoints_path ON module_endpoints(path);
```

### Purchasing Module Database

#### New Tables

```sql
-- Purchase orders
CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL,
    po_number VARCHAR(50) NOT NULL,
    supplier_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',  -- draft, pending_approval, approved, ordered, partially_received, received, cancelled
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    currency_id UUID NOT NULL,
    exchange_rate DECIMAL(10,6) DEFAULT 1.000000,
    requested_by UUID NOT NULL,  -- user_id
    approved_by UUID,  -- user_id
    ordered_date DATE,
    expected_delivery_date DATE,
    notes TEXT,
    terms_and_conditions TEXT,
    
    -- Framework fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_by UUID NOT NULL,
    framework_version VARCHAR(10) DEFAULT '1.0',
    
    UNIQUE(company_id, po_number)
);

CREATE INDEX idx_purchase_orders_company ON purchase_orders(company_id);
CREATE INDEX idx_purchase_orders_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX idx_purchase_orders_po_number ON purchase_orders(po_number);
CREATE INDEX idx_purchase_orders_requested_by ON purchase_orders(requested_by);

-- Purchase order line items
CREATE TABLE purchase_order_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL,
    purchase_order_id UUID NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    product_code VARCHAR(100),
    description VARCHAR(500) NOT NULL,
    quantity DECIMAL(10,3) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(15,2) NOT NULL,
    currency_id UUID NOT NULL,
    expected_delivery_date DATE,
    notes TEXT,
    
    -- Framework fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_by UUID NOT NULL,
    framework_version VARCHAR(10) DEFAULT '1.0',
    
    UNIQUE(purchase_order_id, line_number)
);

CREATE INDEX idx_purchase_order_lines_company ON purchase_order_lines(company_id);
CREATE INDEX idx_purchase_order_lines_po ON purchase_order_lines(purchase_order_id);
CREATE INDEX idx_purchase_order_lines_product ON purchase_order_lines(product_code);

-- Purchase order approvals
CREATE TABLE purchase_order_approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL,
    purchase_order_id UUID NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    approver_id UUID NOT NULL,  -- user_id
    approval_level INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, approved, rejected
    comments TEXT,
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Framework fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_by UUID NOT NULL,
    framework_version VARCHAR(10) DEFAULT '1.0',
    
    UNIQUE(purchase_order_id, approver_id)
);

CREATE INDEX idx_purchase_order_approvals_company ON purchase_order_approvals(company_id);
CREATE INDEX idx_purchase_order_approvals_po ON purchase_order_approvals(purchase_order_id);
CREATE INDEX idx_purchase_order_approvals_approver ON purchase_order_approvals(approver_id);
CREATE INDEX idx_purchase_order_approvals_status ON purchase_order_approvals(status);

-- Supplier evaluation and rating
CREATE TABLE supplier_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL,
    supplier_id UUID NOT NULL,
    evaluator_id UUID NOT NULL,  -- user_id
    evaluation_period_start DATE NOT NULL,
    evaluation_period_end DATE NOT NULL,
    quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5),
    delivery_rating INTEGER CHECK (delivery_rating >= 1 AND delivery_rating <= 5),
    service_rating INTEGER CHECK (service_rating >= 1 AND service_rating <= 5),
    overall_rating DECIMAL(3,2) GENERATED ALWAYS AS ((quality_rating + delivery_rating + service_rating) / 3.0) STORED,
    comments TEXT,
    
    -- Framework fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_by UUID NOT NULL,
    framework_version VARCHAR(10) DEFAULT '1.0'
);

CREATE INDEX idx_supplier_evaluations_company ON supplier_evaluations(company_id);
CREATE INDEX idx_supplier_evaluations_supplier ON supplier_evaluations(supplier_id);
CREATE INDEX idx_supplier_evaluations_period ON supplier_evaluations(evaluation_period_end);
CREATE INDEX idx_supplier_evaluations_rating ON supplier_evaluations(overall_rating);
```

## Database Migrations

### Module Registry Service Migration

```python
"""create_module_registry_tables

Revision ID: 20250802_120000_create_module_tables
Revises: previous_migration
Create Date: 2025-08-02 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20250802_120000_create_module_tables'
down_revision = 'previous_migration'
branch_labels = None
depends_on = None

def upgrade():
    # Enable uuid-ossp extension if not exists
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create modules table
    op.create_table('modules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('display_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('author', sa.String(100)),
        sa.Column('homepage_url', sa.String(500)),
        sa.Column('documentation_url', sa.String(500)),
        sa.Column('manifest_schema', postgresql.JSONB, nullable=False),
        sa.Column('package_url', sa.String(500)),
        sa.Column('package_checksum', sa.String(64)),
        sa.Column('status', sa.String(20), nullable=False, server_default='available'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('framework_version', sa.String(20), nullable=False),
        sa.UniqueConstraint('name')
    )
    
    # Create indexes for modules
    op.create_index('idx_modules_name', 'modules', ['name'])
    op.create_index('idx_modules_status', 'modules', ['status'])
    op.create_index('idx_modules_created_at', 'modules', ['created_at'])
    
    # Create module_installations table
    op.create_table('module_installations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('configuration', postgresql.JSONB, server_default='{}'),
        sa.Column('status', sa.String(20), nullable=False, server_default='installing'),
        sa.Column('installed_version', sa.String(20), nullable=False),
        sa.Column('installed_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('last_health_check', sa.TIMESTAMP(timezone=True)),
        sa.Column('health_status', sa.String(20), server_default='unknown'),
        sa.Column('error_message', sa.Text),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('module_id', 'company_id')
    )
    
    # Create remaining tables with similar pattern...
    
def downgrade():
    op.drop_table('module_endpoints')
    op.drop_table('module_dependencies')
    op.drop_table('module_installations')
    op.drop_table('modules')
```

### Purchasing Module Migration

```python
"""create_purchasing_tables

Revision ID: 20250802_130000_create_purchasing_tables
Revises: 20250802_120000_create_module_tables
Create Date: 2025-08-02 13:00:00.000000

"""

def upgrade():
    # Create purchase_orders table
    op.create_table('purchase_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('po_number', sa.String(50), nullable=False),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('total_amount', sa.DECIMAL(15,2), nullable=False, server_default='0.00'),
        sa.Column('currency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exchange_rate', sa.DECIMAL(10,6), server_default='1.000000'),
        # ... rest of columns
        sa.UniqueConstraint('company_id', 'po_number')
    )
    
    # Create remaining purchasing tables...
```

## Rationale

### Module Registry Design
- **UUID Primary Keys**: Consistent with existing framework pattern and enables distributed deployment
- **JSONB Configuration**: Flexible configuration storage with PostgreSQL native JSON querying capabilities
- **Company Isolation**: Per-company module installations enable multi-tenant module management
- **Health Monitoring**: Built-in health check infrastructure for proactive module management

### Purchasing Module Design
- **Framework Integration**: All tables follow Business Object Framework patterns for automatic audit and event integration
- **Multi-Currency Support**: Native currency support using existing currency service relationships
- **Approval Workflows**: Flexible approval system supporting multiple approval levels and parallel approvals
- **Performance Optimization**: Strategic indexing for common query patterns including company isolation and status filtering

### Data Integrity Considerations
- **Foreign Key Constraints**: Proper referential integrity with cascade deletes for cleanup
- **Check Constraints**: Data validation at database level for rating systems and status enums
- **Unique Constraints**: Business rule enforcement for PO numbers and approval uniqueness
- **Generated Columns**: Automatic calculation of derived values like overall ratings