-- Migration: Add Financial Snapshots to Opportunities System
-- Description: Add FinancialSnapshot table to existing opportunities system
-- Date: 2025-10-07

-- Financial Health enum (if not already exists)
DO $$ BEGIN
    CREATE TYPE financial_health AS ENUM (
        'excellent', 'good', 'fair', 'poor', 'distressed', 'unknown'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Financial Snapshots table (extends opportunities system)
CREATE TABLE IF NOT EXISTS financial_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    opportunity_id UUID NOT NULL REFERENCES market_opportunities(id),

    -- Period Information
    year INTEGER NOT NULL,
    quarter INTEGER,
    period_end_date TIMESTAMP,

    -- Income Statement
    revenue DECIMAL(20,2),
    gross_profit DECIMAL(20,2),
    operating_income DECIMAL(20,2),
    ebitda DECIMAL(20,2),
    net_income DECIMAL(20,2),

    -- Balance Sheet
    total_assets DECIMAL(20,2),
    current_assets DECIMAL(20,2),
    total_liabilities DECIMAL(20,2),
    current_liabilities DECIMAL(20,2),
    shareholders_equity DECIMAL(20,2),
    cash_and_equivalents DECIMAL(20,2),

    -- Cash Flow
    operating_cash_flow DECIMAL(20,2),
    free_cash_flow DECIMAL(20,2),
    capital_expenditures DECIMAL(20,2),

    -- Key Ratios
    gross_margin DECIMAL(5,4),
    ebitda_margin DECIMAL(5,4),
    net_margin DECIMAL(5,4),
    current_ratio DECIMAL(5,2),
    debt_to_equity DECIMAL(5,2),
    return_on_assets DECIMAL(5,4),
    return_on_equity DECIMAL(5,4),

    -- Growth Metrics
    revenue_growth DECIMAL(5,4),
    ebitda_growth DECIMAL(5,4),
    profit_growth DECIMAL(5,4),

    -- Health Assessment
    financial_health financial_health,
    health_score FLOAT,
    distress_indicators JSONB,

    -- Data Quality & Source
    data_source VARCHAR(255),
    data_quality_score FLOAT,
    is_audited BOOLEAN DEFAULT FALSE,
    filing_date TIMESTAMP,
    currency VARCHAR(3) DEFAULT 'GBP',

    -- Analysis
    peer_comparison_percentile INTEGER,
    valuation_multiple_revenue DECIMAL(5,2),
    valuation_multiple_ebitda DECIMAL(5,2),

    -- Metadata
    analyst_notes TEXT,
    red_flags JSONB,
    opportunities_identified JSONB,

    -- Standard fields
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT check_valid_quarter CHECK (quarter IS NULL OR (quarter >= 1 AND quarter <= 4)),
    CONSTRAINT check_valid_year CHECK (year >= 1900 AND year <= 2100)
);

-- Create indexes for the financial snapshots
CREATE INDEX IF NOT EXISTS idx_financial_opportunity_year ON financial_snapshots(opportunity_id, year);
CREATE INDEX IF NOT EXISTS idx_financial_health_score ON financial_snapshots(financial_health, health_score);
CREATE INDEX IF NOT EXISTS idx_financial_organization_id ON financial_snapshots(organization_id);
CREATE INDEX IF NOT EXISTS idx_financial_year ON financial_snapshots(year DESC);