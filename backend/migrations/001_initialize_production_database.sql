-- M&A SaaS Platform - Production Database Initialization
-- Generated: October 10, 2025
-- Platform: "100 Days and Beyond" M&A Ecosystem
-- Database: PostgreSQL with Vector Extensions

-- =============================================================================
-- VECTOR EXTENSIONS & AI CAPABILITIES
-- =============================================================================

-- Enable vector extension for AI-powered semantic search
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;
CREATE EXTENSION IF NOT EXISTS uuid-ossp;

-- =============================================================================
-- CORE ORGANIZATIONAL STRUCTURE
-- =============================================================================

-- Organizations (Multi-Tenant Architecture)
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'solo',
    subscription_status VARCHAR(50) DEFAULT 'trial',
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- Users with Clerk Integration
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    profile JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}'
);

-- =============================================================================
-- SUBSCRIPTION & PAYMENT MANAGEMENT
-- =============================================================================

-- Subscription Plans
CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    price_monthly INTEGER NOT NULL, -- in cents
    price_annual INTEGER, -- in cents (with discount)
    stripe_price_id VARCHAR(255),
    stripe_price_id_annual VARCHAR(255),
    features JSONB DEFAULT '[]',
    limits JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default subscription plans
INSERT INTO subscription_plans (name, slug, price_monthly, price_annual, features, limits) VALUES
('Solo Dealmaker', 'solo', 27900, 25110, 
 '["Basic M&A Tools", "Deal Tracking", "Community Access", "Weekly Podcast"]',
 '{"deals_per_month": 5, "team_members": 1, "storage_gb": 10}'),
('Growth Firm', 'growth', 79800, 71820,
 '["Advanced M&A Tools", "Team Collaboration", "Priority Support", "Event Access", "AI Insights"]',
 '{"deals_per_month": 25, "team_members": 10, "storage_gb": 100}'),
('Enterprise', 'enterprise', 159800, 143820,
 '["Full M&A Suite", "Unlimited Team", "White-label Options", "Custom Integrations", "Dedicated Support"]',
 '{"deals_per_month": -1, "team_members": -1, "storage_gb": 1000}');

-- Organization Subscriptions
CREATE TABLE IF NOT EXISTS organization_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES subscription_plans(id),
    stripe_subscription_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- M&A BUSINESS DOMAIN MODELS
-- =============================================================================

-- Deal Management
CREATE TABLE IF NOT EXISTS deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deal_type VARCHAR(50), -- 'acquisition', 'merger', 'divestiture'
    status VARCHAR(50) DEFAULT 'prospecting',
    target_company VARCHAR(255),
    industry VARCHAR(100),
    deal_size BIGINT, -- in cents
    probability INTEGER DEFAULT 50, -- 0-100
    expected_close_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    
    -- Vector embedding for AI-powered search
    embedding vector(1536)
);

-- Deal Participants
CREATE TABLE IF NOT EXISTS deal_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    role VARCHAR(50), -- 'lead', 'analyst', 'advisor'
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Opportunities (Deal Sourcing)
CREATE TABLE IF NOT EXISTS opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    revenue BIGINT,
    ebitda BIGINT,
    location VARCHAR(255),
    source VARCHAR(100), -- 'inbound', 'outbound', 'referral', 'ai_sourced'
    status VARCHAR(50) DEFAULT 'new',
    score INTEGER DEFAULT 0, -- AI-generated compatibility score
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Vector embedding for semantic matching
    embedding vector(1536),
    
    -- Full-text search
    search_vector tsvector
);

-- =============================================================================
-- COMMUNITY & ENGAGEMENT FEATURES
-- =============================================================================

-- Community Posts
CREATE TABLE IF NOT EXISTS community_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    post_type VARCHAR(50) DEFAULT 'discussion', -- 'discussion', 'question', 'announcement'
    is_pinned BOOLEAN DEFAULT false,
    is_featured BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Vector embedding for content discovery
    embedding vector(1536)
);

-- Events Management
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_type VARCHAR(50), -- 'webinar', 'workshop', 'networking'
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    max_attendees INTEGER,
    registration_required BOOLEAN DEFAULT true,
    zoom_meeting_id VARCHAR(255),
    teams_meeting_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Event Registrations
CREATE TABLE IF NOT EXISTS event_registrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    attendance_status VARCHAR(50) DEFAULT 'registered', -- 'registered', 'attended', 'no_show'
    feedback JSONB DEFAULT '{}'
);

-- =============================================================================
-- PODCAST & CONTENT MANAGEMENT
-- =============================================================================

-- Podcast Episodes
CREATE TABLE IF NOT EXISTS podcast_episodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    episode_number INTEGER,
    season_number INTEGER DEFAULT 1,
    audio_file_url TEXT,
    video_file_url TEXT,
    duration_seconds INTEGER,
    published_at TIMESTAMP WITH TIME ZONE,
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- SEO and discoverability
    seo_title VARCHAR(255),
    seo_description TEXT,
    keywords TEXT[],
    
    -- Vector embedding for content discovery
    embedding vector(1536)
);

-- =============================================================================
-- ANALYTICS & BUSINESS INTELLIGENCE
-- =============================================================================

-- User Activity Tracking
CREATE TABLE IF NOT EXISTS user_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    activity_data JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ecosystem Intelligence
CREATE TABLE IF NOT EXISTS ecosystem_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    insight_type VARCHAR(100), -- 'partnership_opportunity', 'market_trend', 'deal_prediction'
    title VARCHAR(255),
    description TEXT,
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Vector embedding for insight matching
    embedding vector(1536)
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- =============================================================================

-- Core entity indexes
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_users_clerk_id ON users(clerk_user_id);
CREATE INDEX IF NOT EXISTS idx_users_organization ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_deals_organization ON deals(organization_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_organization ON opportunities(organization_id);

-- Vector similarity search indexes
CREATE INDEX IF NOT EXISTS idx_deals_embedding ON deals USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_opportunities_embedding ON opportunities USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_community_posts_embedding ON community_posts USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_opportunities_search ON opportunities USING gin(search_vector);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_deals_status ON deals(status);
CREATE INDEX IF NOT EXISTS idx_deals_created_at ON deals(created_at);
CREATE INDEX IF NOT EXISTS idx_opportunities_score ON opportunities(score DESC);
CREATE INDEX IF NOT EXISTS idx_user_activities_created_at ON user_activities(created_at);

-- =============================================================================
-- TRIGGERS FOR AUTOMATED UPDATES
-- =============================================================================

-- Update timestamps automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply timestamp triggers
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_deals_updated_at BEFORE UPDATE ON deals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_opportunities_updated_at BEFORE UPDATE ON opportunities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update search vectors for full-text search
CREATE OR REPLACE FUNCTION update_opportunities_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', 
        COALESCE(NEW.company_name, '') || ' ' ||
        COALESCE(NEW.industry, '') || ' ' ||
        COALESCE(NEW.location, '')
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_opportunities_search_vector_trigger 
    BEFORE INSERT OR UPDATE ON opportunities 
    FOR EACH ROW EXECUTE FUNCTION update_opportunities_search_vector();

-- =============================================================================
-- SECURITY & ROW LEVEL SECURITY
-- =============================================================================

-- Enable RLS for multi-tenant isolation
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (will be implemented with application-level context)
-- Note: Actual RLS policies will be created after Clerk integration is complete

-- =============================================================================
-- INITIAL DATA & CONFIGURATION
-- =============================================================================

-- Create master admin organization for platform management
INSERT INTO organizations (id, name, slug, subscription_tier, subscription_status) 
VALUES (
    '00000000-0000-0000-0000-000000000000',
    'Platform Administration',
    'platform-admin',
    'enterprise',
    'active'
) ON CONFLICT (id) DO NOTHING;

-- =============================================================================
-- ANALYTICS & REPORTING VIEWS
-- =============================================================================

-- Organization performance summary
CREATE OR REPLACE VIEW organization_performance AS
SELECT 
    o.id,
    o.name,
    o.subscription_tier,
    COUNT(DISTINCT u.id) as user_count,
    COUNT(DISTINCT d.id) as deal_count,
    COUNT(DISTINCT op.id) as opportunity_count,
    AVG(op.score) as avg_opportunity_score,
    o.created_at
FROM organizations o
LEFT JOIN users u ON o.id = u.organization_id AND u.is_active = true
LEFT JOIN deals d ON o.id = d.organization_id
LEFT JOIN opportunities op ON o.id = op.organization_id
GROUP BY o.id, o.name, o.subscription_tier, o.created_at;

-- Deal pipeline summary
CREATE OR REPLACE VIEW deal_pipeline_summary AS
SELECT 
    organization_id,
    status,
    COUNT(*) as deal_count,
    SUM(deal_size) as total_value,
    AVG(probability) as avg_probability
FROM deals
GROUP BY organization_id, status;

-- =============================================================================
-- COMPLETION CONFIRMATION
-- =============================================================================

-- Log successful database initialization
INSERT INTO user_activities (
    user_id, 
    organization_id, 
    activity_type, 
    activity_data
) VALUES (
    NULL,
    '00000000-0000-0000-0000-000000000000',
    'database_initialization',
    '{"version": "1.0.0", "timestamp": "' || NOW() || '", "status": "complete"}'
);

-- Database initialization complete
SELECT 'M&A SaaS Platform Database Initialization Complete' as status;
