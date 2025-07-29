# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-07-29-company-partner-service/spec.md

> Created: 2025-07-29
> Version: 1.0.0

## Schema Changes

### New Tables

**companies**
- Primary table for storing company/legal entity information
- Serves as the foundation for multi-company data isolation
- Contains legal, contact, and configuration information

**partners**
- Primary table for business partner information (customers, suppliers, vendors)
- Links to companies for multi-company partner management
- Supports hierarchical partner relationships

**company_users** (Association Table)
- Links users from auth service to companies with role information
- Enables user access control across multiple companies
- Stores company-specific user roles and permissions

**partner_contacts**
- Extended contact information for partners
- Supports multiple contacts per partner
- Includes communication preferences and job titles

**partner_addresses**
- Multiple address types per partner (billing, shipping, etc.)
- Standardized address format with validation
- Geographic information for reporting and logistics

## Database Schema SQL

```sql
-- Companies table for multi-company support
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    website VARCHAR(255),
    tax_id VARCHAR(100),
    
    -- Address information
    street TEXT,
    street2 TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    zip VARCHAR(20),
    country VARCHAR(100),
    
    -- Configuration
    currency VARCHAR(3) DEFAULT 'USD',
    timezone VARCHAR(50) DEFAULT 'UTC',
    logo_url TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT companies_code_check CHECK (LENGTH(code) >= 2),
    CONSTRAINT companies_name_check CHECK (LENGTH(name) >= 1)
);

-- Company users association for multi-company access
CREATE TABLE company_users (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL, -- References users.id from auth service
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_default_company BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(company_id, user_id),
    CONSTRAINT company_users_role_check CHECK (role IN ('admin', 'manager', 'user', 'viewer'))
);

-- Partners table for customers, suppliers, vendors
CREATE TABLE partners (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Basic information
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    partner_type VARCHAR(20) NOT NULL DEFAULT 'customer',
    
    -- Contact information
    email VARCHAR(255),
    phone VARCHAR(50),
    mobile VARCHAR(50),
    website VARCHAR(255),
    
    -- Business information
    tax_id VARCHAR(100),
    industry VARCHAR(100),
    
    -- Relationship management
    parent_partner_id INTEGER REFERENCES partners(id) ON DELETE SET NULL,
    
    -- Settings
    is_company BOOLEAN DEFAULT FALSE,
    is_customer BOOLEAN DEFAULT TRUE,
    is_supplier BOOLEAN DEFAULT FALSE,
    is_vendor BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(company_id, code),
    CONSTRAINT partners_type_check CHECK (partner_type IN ('customer', 'supplier', 'vendor', 'both')),
    CONSTRAINT partners_name_check CHECK (LENGTH(name) >= 1)
);

-- Partner contacts for extended contact management
CREATE TABLE partner_contacts (
    id SERIAL PRIMARY KEY,
    partner_id INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    
    -- Contact information
    name VARCHAR(255) NOT NULL,
    title VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    mobile VARCHAR(50),
    
    -- Contact preferences
    is_primary BOOLEAN DEFAULT FALSE,
    department VARCHAR(100),
    notes TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT partner_contacts_name_check CHECK (LENGTH(name) >= 1)
);

-- Partner addresses for multiple address types
CREATE TABLE partner_addresses (
    id SERIAL PRIMARY KEY,
    partner_id INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    
    -- Address information
    address_type VARCHAR(20) NOT NULL DEFAULT 'default',
    street TEXT NOT NULL,
    street2 TEXT,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    zip VARCHAR(20),
    country VARCHAR(100) NOT NULL,
    
    -- Settings
    is_default BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT partner_addresses_type_check CHECK (address_type IN ('default', 'billing', 'shipping', 'other'))
);

-- Indexes for performance optimization
CREATE INDEX idx_companies_code ON companies(code);
CREATE INDEX idx_companies_active ON companies(is_active);

CREATE INDEX idx_company_users_company_id ON company_users(company_id);
CREATE INDEX idx_company_users_user_id ON company_users(user_id);

CREATE INDEX idx_partners_company_id ON partners(company_id);
CREATE INDEX idx_partners_code ON partners(company_id, code);
CREATE INDEX idx_partners_type ON partners(partner_type);
CREATE INDEX idx_partners_active ON partners(is_active);
CREATE INDEX idx_partners_parent ON partners(parent_partner_id);

CREATE INDEX idx_partner_contacts_partner_id ON partner_contacts(partner_id);
CREATE INDEX idx_partner_contacts_primary ON partner_contacts(partner_id, is_primary);

CREATE INDEX idx_partner_addresses_partner_id ON partner_addresses(partner_id);
CREATE INDEX idx_partner_addresses_type ON partner_addresses(partner_id, address_type);

-- Updated at trigger function (reuse from auth service pattern)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_users_updated_at BEFORE UPDATE ON company_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_partners_updated_at BEFORE UPDATE ON partners
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_partner_contacts_updated_at BEFORE UPDATE ON partner_contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_partner_addresses_updated_at BEFORE UPDATE ON partner_addresses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Migration Strategy

1. **Initial Migration:** Create all tables with proper constraints and indexes
2. **Seed Data:** Insert default company for existing data migration
3. **Data Validation:** Ensure all business rules are enforced at database level
4. **Performance Optimization:** Add composite indexes for common query patterns

## Data Integrity Rules

- All business objects must have valid company_id (enforced by foreign key)
- Partner codes must be unique within each company (enforced by unique constraint)
- Parent-child partner relationships cannot create cycles (enforced by application logic)
- Company users must reference valid users from auth service (enforced by application logic)
- Address and contact information maintains referential integrity (enforced by foreign keys)