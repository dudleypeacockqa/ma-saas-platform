# M&A Platform - Database Architecture v2.0

**BMAD Phase:** Phase 2 Core Features
**Database:** PostgreSQL 15 with Extensions
**Architecture:** Multi-tenant with Row-Level Security
**Last Updated:** 2025-10-11

---

## Database Design Principles

### Core Architecture

```yaml
Pattern: Shared Database, Separate Schema
Isolation: Row-Level Security (RLS)
Scalability: Horizontal partitioning
Performance: Read replicas + caching
Backup: Point-in-time recovery
Compliance: Audit logging + encryption
```

### PostgreSQL Extensions

```sql
-- Required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";       -- Encryption
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";      -- Index optimization
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- Query analysis
CREATE EXTENSION IF NOT EXISTS "timescaledb";    -- Time-series data
CREATE EXTENSION IF NOT EXISTS "pgvector";       -- AI embeddings
CREATE EXTENSION IF NOT EXISTS "pg_cron";        -- Scheduled jobs
```

---

## Multi-Tenant Schema

### Tenant Management

```sql
-- Tenant configuration
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subdomain VARCHAR(63) UNIQUE NOT NULL CHECK (subdomain ~ '^[a-z0-9-]+$'),
    company_name VARCHAR(255) NOT NULL,

    -- Subscription
    plan VARCHAR(50) NOT NULL DEFAULT 'starter',
    stripe_customer_id VARCHAR(255) UNIQUE,
    stripe_subscription_id VARCHAR(255),
    trial_ends_at TIMESTAMPTZ,

    -- Configuration
    settings JSONB DEFAULT '{
        "features": {
            "ai_analysis": true,
            "data_rooms": true,
            "api_access": false
        },
        "limits": {
            "users": 5,
            "deals": 100,
            "storage_gb": 10
        }
    }'::jsonb,

    -- Metadata
    onboarding_completed BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Indexes
    INDEX idx_tenants_subdomain (subdomain),
    INDEX idx_tenants_active (is_active) WHERE is_active = TRUE
);

-- Tenant isolation function
CREATE OR REPLACE FUNCTION set_tenant_context(tenant_id UUID)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_tenant', tenant_id::text, false);
END;
$$ LANGUAGE plpgsql;

-- RLS policies
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON tenants
    USING (id = current_setting('app.current_tenant')::UUID);
```

### User Management

```sql
-- Users table with multi-tenant support
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,

    -- Profile
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url VARCHAR(500),
    title VARCHAR(100),
    phone VARCHAR(50),

    -- Permissions
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    permissions TEXT[] DEFAULT '{}',

    -- Settings
    preferences JSONB DEFAULT '{
        "notifications": {
            "email": true,
            "push": true,
            "sms": false
        },
        "timezone": "UTC",
        "locale": "en-US"
    }'::jsonb,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(tenant_id, email),

    -- Indexes
    INDEX idx_users_tenant (tenant_id),
    INDEX idx_users_clerk (clerk_id),
    INDEX idx_users_email (email)
);

-- User sessions for security
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_sessions_token (token_hash),
    INDEX idx_sessions_expires (expires_at)
);
```

---

## Core Business Tables

### Deals Schema

```sql
-- Main deals table
CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Basic info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    deal_type VARCHAR(50) NOT NULL DEFAULT 'acquisition',

    -- Pipeline
    stage VARCHAR(50) NOT NULL DEFAULT 'prospecting',
    stage_entered_at TIMESTAMPTZ DEFAULT NOW(),
    stage_history JSONB DEFAULT '[]'::jsonb,

    -- Financials
    value DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'GBP',
    probability INTEGER CHECK (probability >= 0 AND probability <= 100),
    expected_close_date DATE,
    actual_close_date DATE,

    -- Assignment
    owner_id UUID REFERENCES users(id),
    team_ids UUID[] DEFAULT '{}',

    -- Custom fields
    custom_fields JSONB DEFAULT '{}'::jsonb,
    tags TEXT[] DEFAULT '{}',

    -- AI fields
    ai_score DECIMAL(3,2) CHECK (ai_score >= 0 AND ai_score <= 1),
    ai_insights JSONB,
    ai_updated_at TIMESTAMPTZ,

    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    archived_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1,

    -- Constraints
    CONSTRAINT valid_stage CHECK (stage IN (
        'prospecting', 'qualification', 'analysis',
        'negotiation', 'due_diligence', 'closing',
        'closed_won', 'closed_lost'
    )),

    -- Indexes
    INDEX idx_deals_tenant_stage (tenant_id, stage) WHERE archived_at IS NULL,
    INDEX idx_deals_owner (owner_id) WHERE archived_at IS NULL,
    INDEX idx_deals_close_date (expected_close_date) WHERE archived_at IS NULL,
    INDEX idx_deals_value (value DESC) WHERE archived_at IS NULL,
    INDEX idx_deals_ai_score (ai_score DESC) WHERE ai_score IS NOT NULL,
    INDEX idx_deals_tags USING GIN (tags),
    INDEX idx_deals_search USING GIN (
        to_tsvector('english', name || ' ' || COALESCE(description, ''))
    )
);

-- Deal team members
CREATE TABLE deal_team_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    permissions TEXT[] DEFAULT '{}',
    added_by UUID REFERENCES users(id),
    added_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(deal_id, user_id),
    INDEX idx_deal_team_deal (deal_id),
    INDEX idx_deal_team_user (user_id)
);

-- Deal pipeline stages configuration
CREATE TABLE pipeline_stages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    order_index INTEGER NOT NULL,
    probability_default INTEGER,
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,

    UNIQUE(tenant_id, name),
    UNIQUE(tenant_id, order_index),
    INDEX idx_pipeline_tenant (tenant_id)
);
```

### Activities & Tasks

```sql
-- Activities tracking
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Associations
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Activity details
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,

    -- Timing
    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    duration INTEGER, -- minutes

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    attachments UUID[] DEFAULT '{}',

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    -- Constraints
    CONSTRAINT valid_activity_type CHECK (type IN (
        'email', 'call', 'meeting', 'note',
        'task', 'document', 'stage_change', 'system'
    )),

    -- Indexes
    INDEX idx_activities_deal (deal_id),
    INDEX idx_activities_user (user_id),
    INDEX idx_activities_occurred (occurred_at DESC),
    INDEX idx_activities_type (type)
);

-- Tasks management
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Task info
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) DEFAULT 'general',

    -- Associations
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_by UUID REFERENCES users(id),

    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',

    -- Timing
    due_date TIMESTAMPTZ,
    reminder_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    completed_by UUID REFERENCES users(id),

    -- Dependencies
    depends_on UUID[] DEFAULT '{}',
    blocks UUID[] DEFAULT '{}',

    -- Metadata
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_status CHECK (status IN (
        'pending', 'in_progress', 'completed', 'cancelled', 'blocked'
    )),
    CONSTRAINT valid_priority CHECK (priority IN (
        'low', 'medium', 'high', 'critical'
    )),

    -- Indexes
    INDEX idx_tasks_assigned (assigned_to) WHERE status != 'completed',
    INDEX idx_tasks_deal (deal_id),
    INDEX idx_tasks_due (due_date) WHERE status != 'completed',
    INDEX idx_tasks_status (status)
);
```

---

## Document Management

### Document Storage

```sql
-- Document metadata
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Associations
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    folder_id UUID REFERENCES document_folders(id) ON DELETE SET NULL,

    -- File info
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    mime_type VARCHAR(100),
    size_bytes BIGINT,

    -- Storage
    storage_key VARCHAR(500) NOT NULL UNIQUE,
    storage_bucket VARCHAR(100),
    cdn_url VARCHAR(500),

    -- Versioning
    version INTEGER DEFAULT 1,
    parent_version_id UUID REFERENCES documents(id),
    is_latest BOOLEAN DEFAULT TRUE,

    -- Security
    encryption_key VARCHAR(255),
    checksum VARCHAR(64),
    virus_scanned BOOLEAN DEFAULT FALSE,
    virus_scan_result JSONB,

    -- AI Processing
    ai_processed BOOLEAN DEFAULT FALSE,
    ai_summary TEXT,
    ai_entities JSONB,
    ai_risk_flags JSONB,
    embeddings vector(1536), -- OpenAI embeddings

    -- Metadata
    tags TEXT[] DEFAULT '{}',
    custom_metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    uploaded_by UUID REFERENCES users(id),
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ,
    access_count INTEGER DEFAULT 0,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', COALESCE(display_name, name)), 'A') ||
        setweight(to_tsvector('english', COALESCE(ai_summary, '')), 'B')
    ) STORED,

    -- Indexes
    INDEX idx_documents_deal (deal_id),
    INDEX idx_documents_folder (folder_id),
    INDEX idx_documents_latest (tenant_id, is_latest) WHERE is_latest = TRUE,
    INDEX idx_documents_search USING GIN (search_vector),
    INDEX idx_documents_embeddings USING ivfflat (embeddings vector_cosine_ops),
    INDEX idx_documents_tags USING GIN (tags)
);

-- Document folders
CREATE TABLE document_folders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES document_folders(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    path TEXT NOT NULL, -- Materialized path
    depth INTEGER NOT NULL DEFAULT 0,

    permissions JSONB DEFAULT '{}'::jsonb,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(parent_id, name),
    INDEX idx_folders_deal (deal_id),
    INDEX idx_folders_path (path)
);
```

### Data Rooms

```sql
-- Virtual data rooms
CREATE TABLE data_rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,

    -- Configuration
    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Security settings
    settings JSONB DEFAULT '{
        "watermarking": true,
        "download_enabled": false,
        "print_enabled": false,
        "expiry_date": null,
        "nda_required": true,
        "ip_restrictions": []
    }'::jsonb,

    -- Access
    access_code VARCHAR(20) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMPTZ,

    -- Statistics
    stats JSONB DEFAULT '{
        "total_views": 0,
        "unique_visitors": 0,
        "documents_downloaded": 0,
        "avg_time_spent": 0
    }'::jsonb,

    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_datarooms_deal (deal_id),
    INDEX idx_datarooms_active (is_active) WHERE is_active = TRUE,
    INDEX idx_datarooms_code (access_code) WHERE access_code IS NOT NULL
);

-- Data room permissions
CREATE TABLE data_room_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_room_id UUID REFERENCES data_rooms(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Permissions
    can_view BOOLEAN DEFAULT TRUE,
    can_download BOOLEAN DEFAULT FALSE,
    can_print BOOLEAN DEFAULT FALSE,
    can_annotate BOOLEAN DEFAULT FALSE,

    -- Folder-level permissions
    allowed_folders UUID[] DEFAULT '{}',
    denied_folders UUID[] DEFAULT '{}',

    -- Tracking
    expires_at TIMESTAMPTZ,
    last_accessed_at TIMESTAMPTZ,
    access_count INTEGER DEFAULT 0,

    -- Audit
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(data_room_id, user_id),
    INDEX idx_dr_permissions_room (data_room_id),
    INDEX idx_dr_permissions_user (user_id)
);
```

---

## AI & Analytics

### AI Analysis Storage

```sql
-- AI analysis results
CREATE TABLE ai_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Associations
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,

    -- Analysis info
    type VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),

    -- Input/Output
    input_data JSONB,
    results JSONB NOT NULL,
    confidence_score DECIMAL(3,2),

    -- Performance
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    cost_usd DECIMAL(10,4),

    -- Status
    status VARCHAR(50) DEFAULT 'completed',
    error_message TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT valid_analysis_type CHECK (type IN (
        'valuation', 'risk_assessment', 'document_analysis',
        'deal_scoring', 'market_analysis', 'comparable_analysis'
    )),

    -- Indexes
    INDEX idx_ai_analyses_deal (deal_id),
    INDEX idx_ai_analyses_document (document_id),
    INDEX idx_ai_analyses_type (type),
    INDEX idx_ai_analyses_created (created_at DESC)
);

-- Deal valuations
CREATE TABLE valuations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,

    -- Valuation details
    method VARCHAR(50) NOT NULL,
    base_value DECIMAL(15,2) NOT NULL,
    low_value DECIMAL(15,2),
    high_value DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'GBP',

    -- Assumptions
    assumptions JSONB NOT NULL,

    -- Calculations
    calculations JSONB,
    sensitivity_analysis JSONB,
    comparables UUID[], -- Reference to other deals

    -- Metadata
    confidence_score DECIMAL(3,2),
    notes TEXT,

    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,

    INDEX idx_valuations_deal (deal_id),
    INDEX idx_valuations_created (created_at DESC)
);
```

### Analytics Tables

```sql
-- Materialized view for pipeline analytics
CREATE MATERIALIZED VIEW pipeline_analytics AS
WITH stage_metrics AS (
    SELECT
        tenant_id,
        stage,
        COUNT(*) as deal_count,
        SUM(value) as total_value,
        AVG(value) as avg_value,
        AVG(probability) as avg_probability,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value) as median_value,
        AVG(EXTRACT(epoch FROM (NOW() - stage_entered_at))/86400)::INTEGER as avg_days_in_stage
    FROM deals
    WHERE archived_at IS NULL
    GROUP BY tenant_id, stage
),
conversion_rates AS (
    SELECT
        tenant_id,
        stage,
        deal_count,
        LEAD(deal_count) OVER (PARTITION BY tenant_id ORDER BY stage_order) as next_stage_count,
        CASE
            WHEN deal_count > 0 THEN
                LEAD(deal_count) OVER (PARTITION BY tenant_id ORDER BY stage_order)::DECIMAL / deal_count
            ELSE 0
        END as conversion_rate
    FROM stage_metrics sm
    JOIN pipeline_stages ps ON sm.tenant_id = ps.tenant_id AND sm.stage = ps.name
)
SELECT
    sm.*,
    cr.conversion_rate,
    NOW() as calculated_at
FROM stage_metrics sm
LEFT JOIN conversion_rates cr ON sm.tenant_id = cr.tenant_id AND sm.stage = cr.stage;

-- Indexes
CREATE INDEX ON pipeline_analytics(tenant_id);
CREATE INDEX ON pipeline_analytics(stage);

-- Refresh strategy (via pg_cron)
SELECT cron.schedule('refresh_pipeline_analytics', '*/15 * * * *',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY pipeline_analytics;'
);
```

---

## Time-Series Data

### Activity Timeline (TimescaleDB)

```sql
-- Create hypertable for time-series data
CREATE TABLE activity_timeline (
    time TIMESTAMPTZ NOT NULL,
    tenant_id UUID NOT NULL,
    user_id UUID,
    deal_id UUID,

    -- Event data
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,

    -- Metrics
    value_impacted DECIMAL(15,2),
    duration_seconds INTEGER,

    -- Context
    ip_address INET,
    user_agent TEXT,
    session_id UUID
);

-- Convert to hypertable
SELECT create_hypertable('activity_timeline', 'time');

-- Create indexes
CREATE INDEX ON activity_timeline (tenant_id, time DESC);
CREATE INDEX ON activity_timeline (deal_id, time DESC);
CREATE INDEX ON activity_timeline (user_id, time DESC);

-- Compression policy
ALTER TABLE activity_timeline SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'tenant_id'
);

SELECT add_compression_policy('activity_timeline', INTERVAL '7 days');

-- Retention policy
SELECT add_retention_policy('activity_timeline', INTERVAL '1 year');

-- Continuous aggregates
CREATE MATERIALIZED VIEW daily_activity_summary
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS day,
    tenant_id,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(DISTINCT deal_id) as active_deals,
    SUM(value_impacted) as total_value_impacted
FROM activity_timeline
GROUP BY day, tenant_id;
```

---

## Performance Optimization

### Indexing Strategy

```sql
-- Partial indexes for common queries
CREATE INDEX idx_deals_active_high_value
ON deals(value DESC)
WHERE archived_at IS NULL AND value > 1000000;

CREATE INDEX idx_deals_closing_soon
ON deals(expected_close_date)
WHERE archived_at IS NULL
  AND stage IN ('negotiation', 'due_diligence')
  AND expected_close_date BETWEEN NOW() AND NOW() + INTERVAL '30 days';

-- Covering indexes
CREATE INDEX idx_deals_dashboard
ON deals(tenant_id, stage, value, probability, expected_close_date)
INCLUDE (name, owner_id)
WHERE archived_at IS NULL;

-- Expression indexes
CREATE INDEX idx_deals_quarter
ON deals(tenant_id, date_trunc('quarter', expected_close_date))
WHERE archived_at IS NULL;

-- BRIN indexes for large tables
CREATE INDEX idx_activities_time_brin
ON activities USING BRIN(occurred_at);
```

### Query Optimization

```sql
-- Optimize common queries with CTEs
CREATE OR REPLACE FUNCTION get_deal_pipeline(p_tenant_id UUID)
RETURNS TABLE (
    stage VARCHAR,
    deal_count INTEGER,
    total_value DECIMAL,
    avg_days_in_stage INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH stage_data AS (
        SELECT
            d.stage,
            COUNT(*) as deal_count,
            SUM(d.value) as total_value,
            AVG(EXTRACT(epoch FROM (NOW() - d.stage_entered_at))/86400)::INTEGER as avg_days
        FROM deals d
        WHERE d.tenant_id = p_tenant_id
          AND d.archived_at IS NULL
        GROUP BY d.stage
    )
    SELECT * FROM stage_data
    ORDER BY
        CASE stage
            WHEN 'prospecting' THEN 1
            WHEN 'qualification' THEN 2
            WHEN 'analysis' THEN 3
            WHEN 'negotiation' THEN 4
            WHEN 'due_diligence' THEN 5
            WHEN 'closing' THEN 6
            ELSE 7
        END;
END;
$$ LANGUAGE plpgsql STABLE;
```

---

## Migration Scripts

### Phase 2 Migration

```sql
-- Migration: 2025_01_phase2_features.sql
BEGIN;

-- Add collaboration features
ALTER TABLE documents
ADD COLUMN IF NOT EXISTS locked_by UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS locked_at TIMESTAMPTZ;

-- Add real-time presence tracking
CREATE TABLE IF NOT EXISTS presence (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID NOT NULL,
    cursor_position JSONB,
    selection JSONB,
    last_ping TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (user_id, resource_type, resource_id),
    INDEX idx_presence_resource (resource_type, resource_id)
);

-- Add commenting system
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Polymorphic association
    commentable_type VARCHAR(50) NOT NULL,
    commentable_id UUID NOT NULL,

    -- Comment data
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,

    -- Status
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,

    -- Metadata
    mentions UUID[] DEFAULT '{}',
    reactions JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    edited_at TIMESTAMPTZ,

    INDEX idx_comments_commentable (commentable_type, commentable_id),
    INDEX idx_comments_parent (parent_id),
    INDEX idx_comments_user (user_id)
);

-- Add notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Notification data
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,

    -- Context
    resource_type VARCHAR(50),
    resource_id UUID,
    action_url VARCHAR(500),

    -- Status
    read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,

    -- Delivery
    channels TEXT[] DEFAULT '{in_app}',
    delivered_at JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,

    INDEX idx_notifications_user_unread (user_id, read) WHERE read = FALSE,
    INDEX idx_notifications_created (created_at DESC)
);

-- Update version
UPDATE tenants SET settings =
    jsonb_set(settings, '{version}', '"2.0.0"'::jsonb);

COMMIT;
```

### Rollback Script

```sql
-- Rollback: 2025_01_phase2_features_rollback.sql
BEGIN;

-- Remove new tables
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS presence CASCADE;

-- Remove columns
ALTER TABLE documents
DROP COLUMN IF EXISTS locked_by,
DROP COLUMN IF EXISTS locked_at;

-- Revert version
UPDATE tenants SET settings =
    jsonb_set(settings, '{version}', '"1.0.0"'::jsonb);

COMMIT;
```

---

## Backup & Recovery

### Backup Strategy

```yaml
Full Backup:
  Schedule: Daily at 2 AM UTC
  Retention: 30 days
  Storage: S3 with server-side encryption

Incremental Backup:
  Schedule: Every 6 hours
  Retention: 7 days
  Method: WAL archiving

Point-in-Time Recovery:
  Window: 7 days
  RPO: 5 minutes
  RTO: 1 hour
```

### Backup Script

```bash
#!/bin/bash
# backup.sh - Automated backup script

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
S3_BUCKET="s3://maplatform-backups"

# Full backup
pg_dump \
  --host=$DB_HOST \
  --username=$DB_USER \
  --dbname=$DB_NAME \
  --format=custom \
  --verbose \
  --file="${BACKUP_DIR}/full_${TIMESTAMP}.dump"

# Compress and encrypt
gzip "${BACKUP_DIR}/full_${TIMESTAMP}.dump"
gpg --encrypt --recipient backup@maplatform.com \
  "${BACKUP_DIR}/full_${TIMESTAMP}.dump.gz"

# Upload to S3
aws s3 cp \
  "${BACKUP_DIR}/full_${TIMESTAMP}.dump.gz.gpg" \
  "${S3_BUCKET}/full/" \
  --storage-class STANDARD_IA

# Cleanup old backups
find ${BACKUP_DIR} -name "*.dump*" -mtime +30 -delete
```

---

## Monitoring & Maintenance

### Performance Monitoring

```sql
-- Slow query analysis
CREATE OR REPLACE VIEW slow_queries AS
SELECT
    query,
    calls,
    total_time,
    mean_time,
    min_time,
    max_time,
    stddev_time
FROM pg_stat_statements
WHERE mean_time > 100 -- milliseconds
ORDER BY mean_time DESC
LIMIT 50;

-- Table bloat monitoring
CREATE OR REPLACE VIEW table_bloat AS
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    ROUND(100 * pg_total_relation_size(schemaname||'.'||tablename) /
          NULLIF(SUM(pg_total_relation_size(schemaname||'.'||tablename))
          OVER (), 0), 2) AS percentage
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Connection monitoring
CREATE OR REPLACE VIEW connection_stats AS
SELECT
    datname,
    numbackends,
    xact_commit,
    xact_rollback,
    blks_read,
    blks_hit,
    tup_returned,
    tup_fetched,
    tup_inserted,
    tup_updated,
    tup_deleted
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1', 'postgres');
```

### Maintenance Tasks

```sql
-- Vacuum and analyze schedule
SELECT cron.schedule('vacuum_analyze', '0 3 * * *', $$
    VACUUM ANALYZE deals;
    VACUUM ANALYZE activities;
    VACUUM ANALYZE documents;
$$);

-- Update table statistics
SELECT cron.schedule('update_statistics', '0 4 * * *', $$
    ANALYZE;
$$);

-- Clean up old sessions
SELECT cron.schedule('cleanup_sessions', '0 * * * *', $$
    DELETE FROM user_sessions WHERE expires_at < NOW();
$$);

-- Archive old activities
SELECT cron.schedule('archive_activities', '0 2 * * 0', $$
    INSERT INTO activities_archive
    SELECT * FROM activities
    WHERE occurred_at < NOW() - INTERVAL '1 year';

    DELETE FROM activities
    WHERE occurred_at < NOW() - INTERVAL '1 year';
$$);
```

---

_This database architecture provides a scalable, secure, and performant foundation for the M&A Platform Phase 2 features. The design supports multi-tenancy, real-time collaboration, AI integration, and comprehensive analytics while maintaining data integrity and compliance._
