"""Add currency and currency rate tables

Revision ID: 20250730_1800
Revises: 20250729_120336
Create Date: 2025-07-30 18:04:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250730_1800'
down_revision = '20250729_1001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create currencies table
    op.create_table(
        'currencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=3), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('decimal_places', sa.Integer(), nullable=False, default=2),
        sa.Column('rounding', sa.Numeric(precision=10, scale=6), nullable=False, default=0.01),
        sa.Column('position', sa.String(length=10), nullable=False, default='before'),
        sa.Column('thousands_sep', sa.String(length=1), nullable=True, default=','),
        sa.Column('decimal_sep', sa.String(length=1), nullable=True, default='.'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_base', sa.Boolean(), nullable=False, default=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('LENGTH(code) = 3', name='currencies_code_length_check'),
        sa.CheckConstraint('LENGTH(name) >= 1', name='currencies_name_check'),
        sa.CheckConstraint('LENGTH(symbol) >= 1', name='currencies_symbol_check'),
        sa.CheckConstraint('decimal_places >= 0', name='currencies_decimal_places_check'),
        sa.CheckConstraint('decimal_places <= 6', name='currencies_decimal_places_max_check'),
        sa.CheckConstraint("position IN ('before', 'after')", name='currencies_position_check')
    )
    
    # Create indexes for currencies
    op.create_index(op.f('ix_currencies_code'), 'currencies', ['code'], unique=False)
    op.create_index(op.f('ix_currencies_is_active'), 'currencies', ['is_active'], unique=False)
    op.create_index(op.f('ix_currencies_is_base'), 'currencies', ['is_base'], unique=False)
    op.create_index('idx_currencies_active_base', 'currencies', ['is_active', 'is_base'], unique=False)
    op.create_index('idx_currencies_company_code', 'currencies', ['company_id', 'code'], unique=True)

    # Create currency_rates table
    op.create_table(
        'currency_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('currency_id', sa.Integer(), nullable=False),
        sa.Column('base_currency_id', sa.Integer(), nullable=False),
        sa.Column('rate', sa.Numeric(precision=20, scale=10), nullable=False),
        sa.Column('inverse_rate', sa.Numeric(precision=20, scale=10), nullable=False),
        sa.Column('date_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True, default='manual'),
        sa.Column('provider', sa.String(length=100), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('rate > 0', name='currency_rates_rate_positive_check'),
        sa.CheckConstraint('inverse_rate > 0', name='currency_rates_inverse_rate_positive_check'),
        sa.CheckConstraint('date_end IS NULL OR date_end > date_start', name='currency_rates_date_check')
    )
    
    # Create indexes for currency_rates
    op.create_index(op.f('ix_currency_rates_currency_id'), 'currency_rates', ['currency_id'], unique=False)
    op.create_index(op.f('ix_currency_rates_base_currency_id'), 'currency_rates', ['base_currency_id'], unique=False)
    op.create_index(op.f('ix_currency_rates_company_id'), 'currency_rates', ['company_id'], unique=False)
    op.create_index(op.f('ix_currency_rates_date_start'), 'currency_rates', ['date_start'], unique=False)
    op.create_index(op.f('ix_currency_rates_date_end'), 'currency_rates', ['date_end'], unique=False)
    op.create_index('idx_currency_rates_lookup', 'currency_rates', ['currency_id', 'base_currency_id', 'company_id', 'date_start'], unique=False)
    op.create_index('idx_currency_rates_current', 'currency_rates', ['currency_id', 'base_currency_id', 'company_id', 'date_end'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('currency_rates')
    op.drop_table('currencies')