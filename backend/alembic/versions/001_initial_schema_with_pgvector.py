"""Initial database schema with pgvector support

Revision ID: 001
Revises:
Create Date: 2025-10-10 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema with pgvector extension"""

    # Create pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('domain', sa.String(200)),
        sa.Column('industry', sa.String(100)),
        sa.Column('size', sa.String(50)),
        sa.Column('description', sa.Text()),
        sa.Column('metadata', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_organizations_name', 'organizations', ['name'])
    op.create_index('ix_organizations_domain', 'organizations', ['domain'])

    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('clerk_user_id', sa.String(255), unique=True),
        sa.Column('full_name', sa.String(200)),
        sa.Column('role', sa.String(50), nullable=False, default='member'),
        sa.Column('permissions', postgresql.JSON()),
        sa.Column('last_login', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_clerk_id', 'users', ['clerk_user_id'])
    op.create_index('ix_users_org', 'users', ['organization_id'])

    # Create deals table
    op.create_table('deals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('deal_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='pipeline'),
        sa.Column('value', sa.Numeric(20, 2)),
        sa.Column('currency', sa.String(3), default='USD'),
        sa.Column('target_company', sa.String(200)),
        sa.Column('acquirer_company', sa.String(200)),
        sa.Column('description', sa.Text()),
        sa.Column('terms', postgresql.JSON()),
        sa.Column('financials', postgresql.JSON()),
        sa.Column('key_metrics', postgresql.JSON()),
        sa.Column('ai_analysis', postgresql.JSON()),
        sa.Column('confidence_score', sa.Float()),
        sa.Column('strategic_value', sa.Float()),
        sa.Column('risk_assessment', postgresql.JSON()),
        sa.Column('expected_close_date', sa.Date()),
        sa.Column('actual_close_date', sa.Date()),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_deals_org', 'deals', ['organization_id'])
    op.create_index('ix_deals_status', 'deals', ['status'])
    op.create_index('ix_deals_type', 'deals', ['deal_type'])

    # Create partnerships table
    op.create_table('partnerships',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('partner_name', sa.String(200), nullable=False),
        sa.Column('partner_type', sa.String(50)),
        sa.Column('status', sa.String(50), default='potential'),
        sa.Column('compatibility_score', sa.Float()),
        sa.Column('strategic_fit', sa.Float()),
        sa.Column('influence_score', sa.Float()),
        sa.Column('synergy_areas', postgresql.JSON()),
        sa.Column('potential_value', sa.String(200)),
        sa.Column('risk_factors', postgresql.JSON()),
        sa.Column('engagement_history', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_partnerships_org', 'partnerships', ['organization_id'])
    op.create_index('ix_partnerships_status', 'partnerships', ['status'])

    # Create documents table with vector embeddings
    op.create_table('documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('source', sa.String(200)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('embedding', Vector(1536)),  # OpenAI text-embedding-3-small
        sa.Column('embedding_model', sa.String(100), default='text-embedding-3-small'),
        sa.Column('embedding_generated_at', sa.DateTime()),
        sa.Column('entities', postgresql.JSON()),
        sa.Column('metadata', postgresql.JSON()),
        sa.Column('tags', postgresql.JSON()),
        sa.Column('deal_id', postgresql.UUID(as_uuid=True)),
        sa.Column('partnership_id', postgresql.UUID(as_uuid=True)),
        sa.Column('relevance_score', sa.Float()),
        sa.Column('view_count', sa.Integer(), default=0),
        sa.Column('last_accessed', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ),
        sa.ForeignKeyConstraint(['partnership_id'], ['partnerships.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_documents_org_type', 'documents', ['organization_id', 'document_type'])
    op.create_index('ix_documents_org_created', 'documents', ['organization_id', 'created_at'])

    # Create vector similarity index using IVFFlat
    op.execute("""
        CREATE INDEX ix_documents_embedding
        ON documents
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)

    # Create full-text search index
    op.execute("""
        CREATE INDEX ix_documents_content_search
        ON documents
        USING gin(to_tsvector('english', title || ' ' || content))
    """)

    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stripe_customer_id', sa.String(255)),
        sa.Column('stripe_subscription_id', sa.String(255)),
        sa.Column('tier', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('billing_cycle', sa.String(20), default='monthly'),
        sa.Column('current_period_start', sa.DateTime()),
        sa.Column('current_period_end', sa.DateTime()),
        sa.Column('cancel_at', sa.DateTime()),
        sa.Column('canceled_at', sa.DateTime()),
        sa.Column('trial_end', sa.DateTime()),
        sa.Column('metadata', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subscriptions_org', 'subscriptions', ['organization_id'], unique=True)
    op.create_index('ix_subscriptions_stripe_customer', 'subscriptions', ['stripe_customer_id'])
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'])

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True)),
        sa.Column('user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50)),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True)),
        sa.Column('changes', postgresql.JSON()),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_org', 'audit_logs', ['organization_id'])
    op.create_index('ix_audit_logs_user', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_created', 'audit_logs', ['created_at'])


def downgrade() -> None:
    """Drop all tables and extensions"""
    op.drop_table('audit_logs')
    op.drop_table('subscriptions')
    op.drop_table('documents')
    op.drop_table('partnerships')
    op.drop_table('deals')
    op.drop_table('users')
    op.drop_table('organizations')
    op.execute('DROP EXTENSION IF EXISTS vector')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')