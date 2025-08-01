# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-08-01-business-object-framework/spec.md

> Created: 2025-08-01
> Version: 1.0.0

## Schema Changes

### Enhanced Base Model Structure

The Business Object Framework will enhance the existing base model structure without breaking changes to existing tables. New framework features will be added through mixins and optional columns.

### New Framework Support Tables

#### business_object_extensions
```sql
CREATE TABLE business_object_extensions (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL,          -- e.g., 'partner', 'company', 'product'
    entity_id INTEGER NOT NULL,                 -- ID of the business object
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,           -- Name of the custom field
    field_type VARCHAR(50) NOT NULL,            -- 'string', 'integer', 'decimal', 'boolean', 'date'
    field_value TEXT,                           -- JSON-serialized field value
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    
    UNIQUE(entity_type, entity_id, field_name, company_id),
    INDEX idx_extensions_entity (entity_type, entity_id),
    INDEX idx_extensions_company (company_id),
    INDEX idx_extensions_field (field_name)
);
```

#### business_object_validators
```sql
CREATE TABLE business_object_validators (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL,          -- Business object type
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    validator_name VARCHAR(100) NOT NULL,       -- Name of the validator
    validator_type VARCHAR(50) NOT NULL,        -- 'required', 'format', 'range', 'custom'
    field_name VARCHAR(100),                    -- Target field (null for entity-level validators)
    validator_config TEXT,                      -- JSON configuration for the validator
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    
    UNIQUE(entity_type, company_id, validator_name, field_name),
    INDEX idx_validators_entity (entity_type),
    INDEX idx_validators_company (company_id)
);
```

### Enhanced Existing Tables

The framework will work with existing table structures but may add optional columns to support new features:

#### Optional Framework Columns (to be added via migrations)
```sql
-- These columns will be added to existing business object tables as needed
ALTER TABLE partners ADD COLUMN IF NOT EXISTS framework_version VARCHAR(10) DEFAULT '1.0';
ALTER TABLE companies ADD COLUMN IF NOT EXISTS framework_version VARCHAR(10) DEFAULT '1.0';

-- Indexes for framework queries
CREATE INDEX IF NOT EXISTS idx_partners_framework ON partners(framework_version, company_id);
CREATE INDEX IF NOT EXISTS idx_companies_framework ON companies(framework_version);
```

## Migration Strategy

### Phase 1: Framework Infrastructure
```sql
-- Create framework support tables
-- Migration: 20250801_100000_create_business_object_framework.py

BEGIN;

-- Create business object extensions table
CREATE TABLE business_object_extensions (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER NOT NULL,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50) NOT NULL DEFAULT 'string',
    field_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by INTEGER REFERENCES users(id),
    
    CONSTRAINT uq_extensions_entity_field UNIQUE(entity_type, entity_id, field_name, company_id)
);

-- Create indexes for performance
CREATE INDEX idx_extensions_entity ON business_object_extensions(entity_type, entity_id);
CREATE INDEX idx_extensions_company ON business_object_extensions(company_id);
CREATE INDEX idx_extensions_field ON business_object_extensions(field_name);

-- Create business object validators table
CREATE TABLE business_object_validators (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    validator_name VARCHAR(100) NOT NULL,
    validator_type VARCHAR(50) NOT NULL DEFAULT 'custom',
    field_name VARCHAR(100),
    validator_config TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by INTEGER REFERENCES users(id),
    
    CONSTRAINT uq_validators_entity_name UNIQUE(entity_type, company_id, validator_name, field_name)
);

-- Create indexes for validators
CREATE INDEX idx_validators_entity ON business_object_validators(entity_type);
CREATE INDEX idx_validators_company ON business_object_validators(company_id);
CREATE INDEX idx_validators_active ON business_object_validators(is_active, entity_type);

COMMIT;
```

### Phase 2: Existing Table Enhancement
```sql
-- Add framework columns to existing tables
-- Migration: 20250801_110000_add_framework_columns.py

BEGIN;

-- Add framework version tracking to existing tables
ALTER TABLE partners ADD COLUMN framework_version VARCHAR(10) DEFAULT '1.0';
ALTER TABLE companies ADD COLUMN framework_version VARCHAR(10) DEFAULT '1.0';

-- Add created_by tracking where missing (non-breaking)
ALTER TABLE partners ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id);

-- Create indexes for framework queries
CREATE INDEX idx_partners_framework ON partners(framework_version, company_id);
CREATE INDEX idx_companies_framework ON companies(framework_version);

COMMIT;
```

## Data Migration Considerations

### Existing Data Compatibility

- **No Breaking Changes** - All existing tables and data will continue to work unchanged
- **Progressive Enhancement** - Framework features can be enabled progressively per business object type
- **Backward Compatibility** - Services not yet migrated to the framework will continue to function normally

### Migration Scripts

#### Update Existing Records
```sql
-- Set framework version for existing records
UPDATE partners SET framework_version = '1.0' WHERE framework_version IS NULL;
UPDATE companies SET framework_version = '1.0' WHERE framework_version IS NULL;

-- Set created_by for existing records where possible (optional)
UPDATE partners SET created_by = (
    SELECT user_id FROM audit_logs 
    WHERE entity_type = 'partner' AND entity_id = partners.id 
    ORDER BY created_at ASC LIMIT 1
) WHERE created_by IS NULL;
```

### Data Integrity Rules

#### Referential Integrity
- All extension fields must reference valid business objects
- Company isolation must be maintained across all framework tables
- User references must exist in the users table

#### Validation Rules
- Entity types must match defined business object types
- Field types must be valid JSON-serializable types
- Validator configurations must be valid JSON

## Performance Considerations

### Indexing Strategy

- **Composite Indexes** - Multi-column indexes for common query patterns
- **Company Isolation** - All tables indexed by company_id for efficient filtering
- **Entity Lookups** - Optimized indexes for entity_type + entity_id queries

### Query Optimization

- **Lazy Loading** - Extension fields loaded only when explicitly requested
- **Bulk Operations** - Support for bulk extension field updates
- **Caching Strategy** - Validator configurations cached in memory for performance

### Storage Efficiency

- **JSON Storage** - Extension field values stored as efficient JSON
- **Null Handling** - Optional framework columns use NULL for unset values
- **Index Selectivity** - Indexes designed for high selectivity and low maintenance