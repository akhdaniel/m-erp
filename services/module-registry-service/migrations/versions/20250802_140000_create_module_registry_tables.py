"""Create module registry tables

Revision ID: 20250802_140000
Revises: 
Create Date: 2025-08-02 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250802_140000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create modules table
    op.create_table('modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=False),
        sa.Column('author_email', sa.String(length=255), nullable=True),
        sa.Column('license', sa.String(length=100), nullable=True),
        sa.Column('homepage_url', sa.String(length=500), nullable=True),
        sa.Column('documentation_url', sa.String(length=500), nullable=True),
        sa.Column('repository_url', sa.String(length=500), nullable=True),
        sa.Column('module_type', sa.Enum('BUSINESS_OBJECT', 'WORKFLOW', 'INTEGRATION', 'REPORT', 'UI_COMPONENT', 'FULL_MODULE', name='moduletype'), nullable=False),
        sa.Column('status', sa.Enum('REGISTERED', 'APPROVED', 'REJECTED', 'DEPRECATED', name='modulestatus'), nullable=False),
        sa.Column('minimum_framework_version', sa.String(length=50), nullable=False),
        sa.Column('python_version', sa.String(length=50), nullable=False),
        sa.Column('manifest', sa.JSON(), nullable=False),
        sa.Column('package_data', sa.LargeBinary(), nullable=True),
        sa.Column('package_size', sa.Integer(), nullable=True),
        sa.Column('package_hash', sa.String(length=64), nullable=True),
        sa.Column('config_schema', sa.JSON(), nullable=True),
        sa.Column('default_config', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('requires_approval', sa.Boolean(), nullable=False),
        sa.Column('security_scan_status', sa.String(length=50), nullable=True),
        sa.Column('security_scan_date', sa.DateTime(), nullable=True),
        sa.Column('validation_errors', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_modules_name', 'modules', ['name'], unique=True)
    
    # Create module_dependencies table
    op.create_table('module_dependencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('dependency_id', sa.Integer(), nullable=True),
        sa.Column('dependency_type', sa.Enum('MODULE', 'SERVICE', 'PYTHON_PACKAGE', 'SYSTEM', name='dependencytype'), nullable=False),
        sa.Column('dependency_name', sa.String(length=255), nullable=False),
        sa.Column('version_constraint', sa.String(length=100), nullable=True),
        sa.Column('is_optional', sa.Boolean(), nullable=False),
        sa.Column('is_dev_dependency', sa.Boolean(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['dependency_id'], ['modules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_module_dependencies_dependency_id', 'module_dependencies', ['dependency_id'])
    op.create_index('ix_module_dependencies_dependency_name', 'module_dependencies', ['dependency_name'])
    op.create_index('ix_module_dependencies_module_id', 'module_dependencies', ['module_id'])
    
    # Create module_installations table
    op.create_table('module_installations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'INSTALLING', 'INSTALLED', 'FAILED', 'UNINSTALLING', 'UNINSTALLED', name='installationstatus'), nullable=False),
        sa.Column('installed_version', sa.String(length=50), nullable=False),
        sa.Column('installed_by', sa.String(length=255), nullable=False),
        sa.Column('installed_at', sa.DateTime(), nullable=True),
        sa.Column('uninstalled_at', sa.DateTime(), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('installation_log', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('last_health_check', sa.DateTime(), nullable=True),
        sa.Column('health_status', sa.String(length=50), nullable=True),
        sa.Column('health_details', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_module_installations_company_id', 'module_installations', ['company_id'])
    op.create_index('ix_module_installations_module_id', 'module_installations', ['module_id'])


def downgrade() -> None:
    op.drop_table('module_installations')
    op.drop_table('module_dependencies')
    op.drop_table('modules')
    op.execute('DROP TYPE IF EXISTS installationstatus')
    op.execute('DROP TYPE IF EXISTS dependencytype')
    op.execute('DROP TYPE IF EXISTS modulestatus')
    op.execute('DROP TYPE IF EXISTS moduletype')