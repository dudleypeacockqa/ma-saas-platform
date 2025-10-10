"""
Initial migration: Create multi-tenant schema
Creates the core tables for organizations, users, and subscriptions
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create the multi-tenant schema"""
    
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('clerk_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('company_size', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('primary_contact_email', sa.String(length=255), nullable=True),
        sa.Column('primary_contact_name', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address_line1', sa.String(length=255), nullable=True),
        sa.Column('address_line2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state_province', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('subscription_tier', sa.String(length=50), nullable=False),
        sa.Column('max_users', sa.Integer(), nullable=False),
        sa.Column('max_deals', sa.Integer(), nullable=True),
        sa.Column('storage_quota_gb', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('storage_used_gb', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('data_retention_days', sa.Integer(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('requires_2fa', sa.Boolean(), nullable=False),
        sa.Column('allowed_domains', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('suspended_at', sa.DateTime(), nullable=True),
        sa.Column('suspended_reason', sa.Text(), nullable=True),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('max_users >= 1', name='check_max_users_positive'),
        sa.CheckConstraint('storage_quota_gb >= storage_used_gb', name='check_storage_within_quota'),
        sa.CheckConstraint('storage_used_gb >= 0', name='check_storage_non_negative')
    )
    
    # Create indexes for organizations
    op.create_index('ix_organizations_clerk_id', 'organizations', ['clerk_id'], unique=True)
    op.create_index('ix_organizations_name', 'organizations', ['name'])
    op.create_index('ix_organizations_slug', 'organizations', ['slug'], unique=True)
    op.create_index('ix_organizations_is_active', 'organizations', ['is_active'])
    op.create_index('ix_organizations_is_deleted', 'organizations', ['is_deleted'])
    op.create_index('ix_organizations_created_at', 'organizations', ['created_at'])
    op.create_index('ix_organizations_updated_at', 'organizations', ['updated_at'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('clerk_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('locale', sa.String(length=10), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=False),
        sa.Column('phone_verified', sa.Boolean(), nullable=False),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=False),
        sa.Column('system_role', sa.String(length=50), nullable=False),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for users
    op.create_index('ix_users_clerk_id', 'users', ['clerk_id'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    op.create_index('ix_users_is_deleted', 'users', ['is_deleted'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])
    op.create_index('ix_users_updated_at', 'users', ['updated_at'])

    # Create organization_memberships table
    op.create_table(
        'organization_memberships',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.Column('left_at', sa.DateTime(), nullable=True),
        sa.Column('invited_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('invitation_accepted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'user_id', name='uq_org_user_membership')
    )
    
    # Create indexes for organization_memberships
    op.create_index('ix_org_memberships_org_id', 'organization_memberships', ['organization_id'])
    op.create_index('ix_org_memberships_user_id', 'organization_memberships', ['user_id'])
    op.create_index('ix_org_memberships_role', 'organization_memberships', ['role'])
    op.create_index('ix_org_memberships_is_active', 'organization_memberships', ['is_active'])

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('clerk_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('clerk_customer_id', sa.String(length=255), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=False),
        sa.Column('plan_name', sa.String(length=100), nullable=False),
        sa.Column('billing_interval', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('trial_start', sa.DateTime(), nullable=True),
        sa.Column('trial_end', sa.DateTime(), nullable=True),
        sa.Column('canceled_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('max_users', sa.Integer(), nullable=False),
        sa.Column('max_deals', sa.Integer(), nullable=True),
        sa.Column('storage_quota_gb', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('api_requests_per_month', sa.Integer(), nullable=True),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('next_billing_date', sa.DateTime(), nullable=True),
        sa.Column('last_payment_date', sa.DateTime(), nullable=True),
        sa.Column('payment_method_id', sa.String(length=255), nullable=True),
        sa.Column('discount_percent', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('discount_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('coupon_code', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('amount >= 0', name='check_amount_non_negative'),
        sa.CheckConstraint('max_users >= 1', name='check_max_users_positive'),
        sa.CheckConstraint('storage_quota_gb >= 0', name='check_storage_quota_non_negative'),
        sa.CheckConstraint(
            'discount_percent IS NULL OR (discount_percent >= 0 AND discount_percent <= 100)',
            name='check_discount_percent_valid'
        )
    )
    
    # Create indexes for subscriptions
    op.create_index('ix_subscriptions_org_id', 'subscriptions', ['organization_id'])
    op.create_index('ix_subscriptions_clerk_sub_id', 'subscriptions', ['clerk_subscription_id'], unique=True)
    op.create_index('ix_subscriptions_clerk_customer_id', 'subscriptions', ['clerk_customer_id'])
    op.create_index('ix_subscriptions_plan', 'subscriptions', ['plan'])
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'])
    op.create_index('ix_subscriptions_is_deleted', 'subscriptions', ['is_deleted'])

    # Create organization_settings table
    op.create_table(
        'organization_settings',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('deal_approval_required', sa.Boolean(), nullable=False),
        sa.Column('deal_auto_numbering', sa.Boolean(), nullable=False),
        sa.Column('deal_number_prefix', sa.String(length=10), nullable=True),
        sa.Column('deal_stages', sa.JSON(), nullable=True),
        sa.Column('notification_emails', sa.JSON(), nullable=True),
        sa.Column('webhook_url', sa.String(length=500), nullable=True),
        sa.Column('slack_webhook', sa.String(length=500), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('brand_color', sa.String(length=7), nullable=True),
        sa.Column('integrations', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', name='uq_org_settings')
    )
    
    # Create index for organization_settings
    op.create_index('ix_org_settings_org_id', 'organization_settings', ['organization_id'], unique=True)

    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('clerk_invoice_id', sa.String(length=255), nullable=True),
        sa.Column('invoice_number', sa.String(length=100), nullable=False),
        sa.Column('subtotal', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('discount_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('invoice_date', sa.DateTime(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=True),
        sa.Column('period_end', sa.DateTime(), nullable=True),
        sa.Column('line_items', sa.JSON(), nullable=True),
        sa.Column('payment_details', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for invoices
    op.create_index('ix_invoices_subscription_id', 'invoices', ['subscription_id'])
    op.create_index('ix_invoices_clerk_invoice_id', 'invoices', ['clerk_invoice_id'], unique=True)
    op.create_index('ix_invoices_invoice_number', 'invoices', ['invoice_number'], unique=True)
    op.create_index('ix_invoices_status', 'invoices', ['status'])
    op.create_index('ix_invoices_is_deleted', 'invoices', ['is_deleted'])

    # Create usage_records table
    op.create_table(
        'usage_records',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('usage_date', sa.DateTime(), nullable=False),
        sa.Column('billing_period_start', sa.DateTime(), nullable=False),
        sa.Column('billing_period_end', sa.DateTime(), nullable=False),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for usage_records
    op.create_index('ix_usage_records_subscription_id', 'usage_records', ['subscription_id'])
    op.create_index('ix_usage_records_metric_name', 'usage_records', ['metric_name'])
    op.create_index('ix_usage_records_usage_date', 'usage_records', ['usage_date'])
    op.create_index('ix_usage_records_billing_period', 'usage_records', ['billing_period_start', 'billing_period_end'])


def downgrade():
    """Drop the multi-tenant schema"""
    op.drop_table('usage_records')
    op.drop_table('invoices')
    op.drop_table('organization_settings')
    op.drop_table('subscriptions')
    op.drop_table('organization_memberships')
    op.drop_table('users')
    op.drop_table('organizations')
