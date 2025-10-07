-- Migration: Add Deal Discovery Tables
-- Description: Create tables for Deal Discovery & Sourcing System
-- Date: 2025-10-07

-- Create ENUM types
CREATE TYPE industry_category AS ENUM (
    'technology', 'healthcare', 'manufacturing', 'services',
    'retail', 'finance', 'real_estate', 'energy',
    'consumer_goods', 'other'
);

CREATE TYPE deal_stage AS ENUM (
    'discovery', 'initial_review', 'due_diligence',
    'negotiation', 'closing', 'completed',
    'rejected', 'on_hold'
);

CREATE TYPE financial_health AS ENUM (
    'excellent', 'good', 'fair', 'poor', 'distressed', 'unknown'
);

CREATE TYPE opportunity_source AS ENUM (
    'direct_approach', 'broker', 'investment_bank',
    'industry_contact', 'succession_planning', 'distressed_sale',
    'competitor', 'market_scan', 'other'
);

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(100),
    website VARCHAR(255),
    description TEXT,
    country VARCHAR(100),
    region VARCHAR(100),
    city VARCHAR(100),
    address TEXT,
    industry industry_category,
    sub_industry VARCHAR(100),
    employee_count INTEGER,
    year_founded INTEGER,
    revenue_range_min DECIMAL(15,2),
    revenue_range_max DECIMAL(15,2),
    ebitda DECIMAL(15,2),
    ebitda_margin DECIMAL(5,4),
    growth_rate DECIMAL(5,4),
    ceo_name VARCHAR(255),
    cfo_name VARCHAR(255),
    key_contacts JSONB,
    key_products JSONB,
    key_customers JSONB,
    competitors JSONB,
    data_sources JSONB,
    last_data_refresh TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Deal Opportunities table
CREATE TABLE IF NOT EXISTS deal_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    company_id UUID NOT NULL REFERENCES companies(id),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    source opportunity_source,
    stage deal_stage DEFAULT 'discovery',
    priority INTEGER CHECK (priority >= 1 AND priority <= 5) DEFAULT 3,
    asking_price DECIMAL(15,2),
    estimated_valuation DECIMAL(15,2),
    target_irr DECIMAL(5,4),
    projected_roi DECIMAL(5,4),
    financial_score DECIMAL(5,2),
    strategic_fit_score DECIMAL(5,2),
    risk_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    scoring_rationale JSONB,
    deal_structure VARCHAR(255),
    financing_required DECIMAL(15,2),
    financing_sources JSONB,
    identified_date TIMESTAMP DEFAULT NOW(),
    first_contact_date TIMESTAMP,
    loi_date TIMESTAMP,
    expected_closing_date TIMESTAMP,
    actual_closing_date TIMESTAMP,
    risk_factors JSONB,
    mitigation_strategies JSONB,
    documents JSONB,
    internal_notes TEXT,
    next_steps TEXT,
    last_activity_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_confidential BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Financial Snapshots table
CREATE TABLE IF NOT EXISTS financial_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    year INTEGER NOT NULL,
    quarter INTEGER,
    revenue DECIMAL(15,2),
    gross_profit DECIMAL(15,2),
    operating_income DECIMAL(15,2),
    ebitda DECIMAL(15,2),
    net_income DECIMAL(15,2),
    total_assets DECIMAL(15,2),
    current_assets DECIMAL(15,2),
    total_liabilities DECIMAL(15,2),
    current_liabilities DECIMAL(15,2),
    equity DECIMAL(15,2),
    operating_cash_flow DECIMAL(15,2),
    free_cash_flow DECIMAL(15,2),
    capex DECIMAL(15,2),
    gross_margin DECIMAL(5,4),
    ebitda_margin DECIMAL(5,4),
    net_margin DECIMAL(5,4),
    current_ratio DECIMAL(5,2),
    debt_to_equity DECIMAL(5,2),
    return_on_assets DECIMAL(5,4),
    return_on_equity DECIMAL(5,4),
    revenue_growth DECIMAL(5,4),
    ebitda_growth DECIMAL(5,4),
    financial_health financial_health,
    health_indicators JSONB,
    data_source VARCHAR(255),
    is_audited BOOLEAN DEFAULT FALSE,
    confidence_level INTEGER CHECK (confidence_level >= 1 AND confidence_level <= 5),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Deal Activities table
CREATE TABLE IF NOT EXISTS deal_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID NOT NULL REFERENCES deal_opportunities(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id VARCHAR(255) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    participants JSONB,
    outcome TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date TIMESTAMP,
    activity_date TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Opportunity Evaluations table
CREATE TABLE IF NOT EXISTS opportunity_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID NOT NULL REFERENCES deal_opportunities(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    evaluator_id VARCHAR(255) NOT NULL,
    market_opportunity INTEGER CHECK (market_opportunity >= 1 AND market_opportunity <= 10),
    competitive_position INTEGER CHECK (competitive_position >= 1 AND competitive_position <= 10),
    management_quality INTEGER CHECK (management_quality >= 1 AND management_quality <= 10),
    financial_performance INTEGER CHECK (financial_performance >= 1 AND financial_performance <= 10),
    growth_potential INTEGER CHECK (growth_potential >= 1 AND growth_potential <= 10),
    risk_assessment INTEGER CHECK (risk_assessment >= 1 AND risk_assessment <= 10),
    strategic_fit INTEGER CHECK (strategic_fit >= 1 AND strategic_fit <= 10),
    recommendation VARCHAR(100),
    confidence_level INTEGER CHECK (confidence_level >= 1 AND confidence_level <= 5),
    strengths JSONB,
    weaknesses JSONB,
    opportunities_list JSONB,
    threats JSONB,
    evaluation_notes TEXT,
    conditions TEXT,
    evaluation_date TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Market Intelligence table
CREATE TABLE IF NOT EXISTS market_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    intelligence_type VARCHAR(100),
    source VARCHAR(255),
    source_url VARCHAR(500),
    title VARCHAR(255) NOT NULL,
    summary TEXT,
    full_content TEXT,
    companies_mentioned JSONB,
    industries JSONB,
    keywords JSONB,
    sentiment VARCHAR(50),
    importance_score INTEGER CHECK (importance_score >= 1 AND importance_score <= 5),
    actionable BOOLEAN DEFAULT FALSE,
    action_items JSONB,
    published_date TIMESTAMP,
    collected_date TIMESTAMP DEFAULT NOW(),
    processed_date TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_companies_tenant_id ON companies(tenant_id);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_country ON companies(country);
CREATE INDEX idx_companies_revenue_range ON companies(revenue_range_min, revenue_range_max);

CREATE INDEX idx_deal_opportunities_tenant_id ON deal_opportunities(tenant_id);
CREATE INDEX idx_deal_opportunities_company_id ON deal_opportunities(company_id);
CREATE INDEX idx_deal_opportunities_stage ON deal_opportunities(stage);
CREATE INDEX idx_deal_opportunities_priority ON deal_opportunities(priority);
CREATE INDEX idx_deal_opportunities_is_active ON deal_opportunities(is_active);
CREATE INDEX idx_deal_opportunities_overall_score ON deal_opportunities(overall_score);

CREATE INDEX idx_financial_snapshots_company_id ON financial_snapshots(company_id);
CREATE INDEX idx_financial_snapshots_tenant_id ON financial_snapshots(tenant_id);
CREATE INDEX idx_financial_snapshots_year ON financial_snapshots(year DESC);

CREATE INDEX idx_deal_activities_opportunity_id ON deal_activities(opportunity_id);
CREATE INDEX idx_deal_activities_tenant_id ON deal_activities(tenant_id);
CREATE INDEX idx_deal_activities_activity_date ON deal_activities(activity_date DESC);

CREATE INDEX idx_opportunity_evaluations_opportunity_id ON opportunity_evaluations(opportunity_id);
CREATE INDEX idx_opportunity_evaluations_tenant_id ON opportunity_evaluations(tenant_id);

CREATE INDEX idx_market_intelligence_tenant_id ON market_intelligence(tenant_id);
CREATE INDEX idx_market_intelligence_collected_date ON market_intelligence(collected_date DESC);