# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-08-04-enhanced-partner-management/spec.md

> Created: 2025-08-04
> Version: 1.0.0

## Schema Changes

### New Tables

#### partner_contacts
```sql
CREATE TABLE partner_contacts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    partner_id INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    mobile VARCHAR(50),
    role VARCHAR(100), -- 'primary', 'billing', 'technical', 'sales', 'support', etc.
    is_primary BOOLEAN DEFAULT FALSE,
    notes TEXT,
    active BOOLEAN DEFAULT TRUE,
    framework_version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    
    CONSTRAINT fk_partner_contacts_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT fk_partner_contacts_partner FOREIGN KEY (partner_id) REFERENCES partners(id)
);

CREATE INDEX idx_partner_contacts_company_id ON partner_contacts(company_id);
CREATE INDEX idx_partner_contacts_partner_id ON partner_contacts(partner_id);
CREATE INDEX idx_partner_contacts_role ON partner_contacts(role);
CREATE INDEX idx_partner_contacts_active ON partner_contacts(active);
```

#### partner_addresses
```sql
CREATE TABLE partner_addresses (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    partner_id INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'billing', 'shipping', 'headquarters', 'branch', 'other'
    name VARCHAR(255), -- Optional address name/label
    street1 VARCHAR(255) NOT NULL,
    street2 VARCHAR(255),
    city VARCHAR(255) NOT NULL,
    state_province VARCHAR(255),
    postal_code VARCHAR(50),
    country VARCHAR(3) NOT NULL DEFAULT 'USA', -- ISO 3166-1 alpha-3
    is_default BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    framework_version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    
    CONSTRAINT fk_partner_addresses_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT fk_partner_addresses_partner FOREIGN KEY (partner_id) REFERENCES partners(id)
);

CREATE INDEX idx_partner_addresses_company_id ON partner_addresses(company_id);
CREATE INDEX idx_partner_addresses_partner_id ON partner_addresses(partner_id);
CREATE INDEX idx_partner_addresses_type ON partner_addresses(type);
CREATE INDEX idx_partner_addresses_country ON partner_addresses(country);
CREATE INDEX idx_partner_addresses_active ON partner_addresses(active);
```

#### partner_categories
```sql
CREATE TABLE partner_categories (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    color VARCHAR(7), -- Hex color code for UI display
    parent_id INTEGER REFERENCES partner_categories(id) ON DELETE SET NULL,
    active BOOLEAN DEFAULT TRUE,
    framework_version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    
    CONSTRAINT fk_partner_categories_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT fk_partner_categories_parent FOREIGN KEY (parent_id) REFERENCES partner_categories(id),
    CONSTRAINT unique_category_name_per_company UNIQUE (company_id, name)
);

CREATE INDEX idx_partner_categories_company_id ON partner_categories(company_id);
CREATE INDEX idx_partner_categories_parent_id ON partner_categories(parent_id);
CREATE INDEX idx_partner_categories_active ON partner_categories(active);
```

#### partner_category_assignments
```sql
CREATE TABLE partner_category_assignments (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    partner_id INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES partner_categories(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER,
    
    CONSTRAINT fk_partner_category_assignments_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT fk_partner_category_assignments_partner FOREIGN KEY (partner_id) REFERENCES partners(id),
    CONSTRAINT fk_partner_category_assignments_category FOREIGN KEY (category_id) REFERENCES partner_categories(id),
    CONSTRAINT unique_partner_category UNIQUE (partner_id, category_id)
);

CREATE INDEX idx_partner_category_assignments_company_id ON partner_category_assignments(company_id);
CREATE INDEX idx_partner_category_assignments_partner_id ON partner_category_assignments(partner_id);
CREATE INDEX idx_partner_category_assignments_category_id ON partner_category_assignments(category_id);
```

#### partner_relationships
```sql
CREATE TABLE partner_relationships (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    parent_partner_id INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    child_partner_id INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL, -- 'subsidiary', 'branch', 'division', 'affiliate', etc.
    active BOOLEAN DEFAULT TRUE,
    framework_version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    
    CONSTRAINT fk_partner_relationships_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT fk_partner_relationships_parent FOREIGN KEY (parent_partner_id) REFERENCES partners(id),
    CONSTRAINT fk_partner_relationships_child FOREIGN KEY (child_partner_id) REFERENCES partners(id),
    CONSTRAINT unique_partner_relationship UNIQUE (parent_partner_id, child_partner_id),
    CONSTRAINT prevent_self_reference CHECK (parent_partner_id != child_partner_id)
);

CREATE INDEX idx_partner_relationships_company_id ON partner_relationships(company_id);
CREATE INDEX idx_partner_relationships_parent ON partner_relationships(parent_partner_id);
CREATE INDEX idx_partner_relationships_child ON partner_relationships(child_partner_id);
CREATE INDEX idx_partner_relationships_type ON partner_relationships(relationship_type);
CREATE INDEX idx_partner_relationships_active ON partner_relationships(active);
```

#### partner_communications
```sql
CREATE TABLE partner_communications (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    partner_id INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    contact_id INTEGER REFERENCES partner_contacts(id) ON DELETE SET NULL,
    communication_type VARCHAR(50) NOT NULL, -- 'email', 'phone', 'meeting', 'note', 'letter', etc.
    subject VARCHAR(500),
    content TEXT,
    direction VARCHAR(20) NOT NULL, -- 'inbound', 'outbound'
    communication_date TIMESTAMP WITH TIME ZONE NOT NULL,
    follow_up_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'completed', -- 'completed', 'pending_follow_up', 'cancelled'
    framework_version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    updated_by INTEGER,
    
    CONSTRAINT fk_partner_communications_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT fk_partner_communications_partner FOREIGN KEY (partner_id) REFERENCES partners(id),
    CONSTRAINT fk_partner_communications_contact FOREIGN KEY (contact_id) REFERENCES partner_contacts(id)
);

CREATE INDEX idx_partner_communications_company_id ON partner_communications(company_id);
CREATE INDEX idx_partner_communications_partner_id ON partner_communications(partner_id);
CREATE INDEX idx_partner_communications_contact_id ON partner_communications(contact_id);
CREATE INDEX idx_partner_communications_type ON partner_communications(communication_type);
CREATE INDEX idx_partner_communications_date ON partner_communications(communication_date);
CREATE INDEX idx_partner_communications_status ON partner_communications(status);
```

## Migration Script Requirements

- Create Alembic migration file with proper upgrade and downgrade functions
- Ensure all foreign key constraints are properly established
- Add framework_version column to all new tables for Business Object Framework compatibility
- Include proper indexing for performance optimization
- Validate data integrity constraints during migration
- Support rollback functionality for all schema changes

## Data Integrity Rules

- Ensure referential integrity between all partner-related entities
- Implement cascade delete for child records when parent partner is deleted
- Prevent circular references in partner relationships through database constraints
- Maintain company-level data isolation across all new tables
- Validate address format requirements based on country standards
- Ensure at least one default address per partner for billing operations