# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-08-03-enhanced-partner-management/spec.md

> Created: 2025-08-03
> Version: 1.0.0

## Changes Required

### Partner Model Enhancements

**Modify existing partners table:**
- Add `industry` column for business classification
- Remove unused `partner_type` column (replaced by boolean flags)
- Add proper indexes for performance optimization

**New columns:**
```sql
ALTER TABLE partners ADD COLUMN industry VARCHAR(100);
CREATE INDEX idx_partners_industry ON partners(industry, company_id);
```

### Enable Model Relationships

**Activate SQLAlchemy relationships in Partner model:**
- Uncomment relationship definitions for contacts and addresses
- Enable parent-child partner relationships
- Add proper cascade delete behavior

**No SQL changes required** - relationships use existing foreign key columns.

### Contact Management Table

**The `partner_contacts` table already exists** with proper structure:
- `partner_id` foreign key with CASCADE delete
- Contact information fields (name, title, email, phone, mobile)
- Primary contact designation with `is_primary` boolean
- Department and notes fields for extended information
- Proper constraints and indexing

**No migration required** - table structure is complete.

### Address Management Table

**The `partner_addresses` table already exists** with proper structure:
- `partner_id` foreign key with CASCADE delete
- Address type categorization with check constraints
- Complete address fields (street, city, state, zip, country)
- Default address designation with `is_default` boolean
- Address type validation: 'default', 'billing', 'shipping', 'other'

**No migration required** - table structure is complete.

## Migration Specifications

### Migration File: `add_partner_industry_field.py`

```python
"""Add industry field to partners table

Revision ID: add_partner_industry
Revises: 20250730_180400_add_currency_tables
Create Date: 2025-08-03

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add industry column to partners table
    op.add_column('partners', sa.Column('industry', sa.String(100), nullable=True))
    
    # Add index for industry filtering with company_id
    op.create_index('idx_partners_industry', 'partners', ['industry', 'company_id'])

def downgrade():
    # Remove index and column
    op.drop_index('idx_partners_industry', 'partners')
    op.drop_column('partners', 'industry')
```

## Data Integrity Rules

### Contact Constraints
- **Primary Contact Uniqueness:** Only one primary contact allowed per partner
- **Contact Name Required:** Contact name cannot be empty
- **Email Format Validation:** Email must be valid format when provided

### Address Constraints  
- **Address Type Validation:** Must be one of: 'default', 'billing', 'shipping', 'other'
- **Required Fields:** street, city, and country are mandatory
- **Default Address Logic:** Only one default address allowed per partner per type

### Partner Constraints
- **Partner Name Required:** Partner name cannot be empty (existing constraint)
- **Company Scope:** All contacts and addresses inherit company_id from parent partner
- **Hierarchical Relationships:** Partners cannot be their own parent (circular reference prevention)

## Performance Considerations

### Existing Indexes (Already Implemented)
- `partners.company_id` - Multi-company data isolation
- `partners.is_active` - Active partner filtering
- `partners.partner_type` - Partner type filtering (to be removed)
- `partner_contacts.partner_id` - Contact lookup performance
- `partner_contacts.is_primary` - Primary contact queries
- `partner_addresses.partner_id` - Address lookup performance

### New Index
- `partners.industry + company_id` - Industry-based filtering within companies

## Migration Strategy

1. **Create migration file** for industry field addition
2. **Run database migration** using Alembic
3. **Update Partner model** to include industry field and activate relationships
4. **Update Pydantic schemas** to include new fields in API responses
5. **Test data integrity** with existing partner data