from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from .base import Base


class IndustryCategory(enum.Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    SERVICES = "services"
    RETAIL = "retail"
    FINANCE = "finance"
    REAL_ESTATE = "real_estate"
    ENERGY = "energy"
    CONSUMER_GOODS = "consumer_goods"
    OTHER = "other"


class DealStage(enum.Enum):
    DISCOVERY = "discovery"
    INITIAL_REVIEW = "initial_review"
    DUE_DILIGENCE = "due_diligence"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"


class FinancialHealth(enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    DISTRESSED = "distressed"
    UNKNOWN = "unknown"


class OpportunitySource(enum.Enum):
    DIRECT_APPROACH = "direct_approach"
    BROKER = "broker"
    INVESTMENT_BANK = "investment_bank"
    INDUSTRY_CONTACT = "industry_contact"
    SUCCESSION_PLANNING = "succession_planning"
    DISTRESSED_SALE = "distressed_sale"
    COMPETITOR = "competitor"
    MARKET_SCAN = "market_scan"
    OTHER = "other"


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    # Basic Information
    name = Column(String, nullable=False)
    registration_number = Column(String)
    website = Column(String)
    description = Column(Text)

    # Location
    country = Column(String)
    region = Column(String)
    city = Column(String)
    address = Column(Text)

    # Industry & Size
    industry = Column(SQLEnum(IndustryCategory))
    sub_industry = Column(String)
    employee_count = Column(Integer)
    year_founded = Column(Integer)

    # Financial Metrics
    revenue_range_min = Column(Float)  # In millions
    revenue_range_max = Column(Float)
    ebitda = Column(Float)
    ebitda_margin = Column(Float)
    growth_rate = Column(Float)  # Year-over-year percentage

    # Key People
    ceo_name = Column(String)
    cfo_name = Column(String)
    key_contacts = Column(JSON)  # List of contact dictionaries

    # Strategic Information
    key_products = Column(JSON)  # List of main products/services
    key_customers = Column(JSON)  # List of major customers
    competitors = Column(JSON)  # List of main competitors

    # Data Sources
    data_sources = Column(JSON)  # List of where data was sourced from
    last_data_refresh = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    opportunities = relationship("DealOpportunity", back_populates="company")
    financial_snapshots = relationship("FinancialSnapshot", back_populates="company")

    tenant = relationship("Tenant", back_populates="companies")


class DealOpportunity(Base):
    __tablename__ = "deal_opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    user_id = Column(String, nullable=False)  # Clerk user ID

    # Opportunity Details
    title = Column(String, nullable=False)
    description = Column(Text)
    source = Column(SQLEnum(OpportunitySource))
    stage = Column(SQLEnum(DealStage), default=DealStage.DISCOVERY)
    priority = Column(Integer, default=3)  # 1 (highest) to 5 (lowest)

    # Valuation & Pricing
    asking_price = Column(Float)  # In millions
    estimated_valuation = Column(Float)
    target_irr = Column(Float)  # Target Internal Rate of Return
    projected_roi = Column(Float)  # Projected Return on Investment

    # Scoring (0-100 scale)
    financial_score = Column(Float)
    strategic_fit_score = Column(Float)
    risk_score = Column(Float)  # Lower is better
    overall_score = Column(Float)
    scoring_rationale = Column(JSON)  # Detailed breakdown of scoring

    # Deal Terms
    deal_structure = Column(String)  # Asset purchase, stock purchase, merger, etc.
    financing_required = Column(Float)
    financing_sources = Column(JSON)  # List of potential financing sources

    # Key Dates
    identified_date = Column(DateTime, default=datetime.utcnow)
    first_contact_date = Column(DateTime)
    loi_date = Column(DateTime)  # Letter of Intent date
    expected_closing_date = Column(DateTime)
    actual_closing_date = Column(DateTime)

    # Risk Factors
    risk_factors = Column(JSON)  # List of identified risks
    mitigation_strategies = Column(JSON)  # Risk mitigation plans

    # Documents & Notes
    documents = Column(JSON)  # List of document references
    internal_notes = Column(Text)
    next_steps = Column(Text)

    # Tracking
    last_activity_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_confidential = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="opportunities")
    activities = relationship("DealActivity", back_populates="opportunity")
    evaluations = relationship("OpportunityEvaluation", back_populates="opportunity")

    tenant = relationship("Tenant", back_populates="deal_opportunities")


class FinancialSnapshot(Base):
    __tablename__ = "financial_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    # Period Information
    year = Column(Integer, nullable=False)
    quarter = Column(Integer)  # Optional for quarterly data

    # Income Statement
    revenue = Column(Float)
    gross_profit = Column(Float)
    operating_income = Column(Float)
    ebitda = Column(Float)
    net_income = Column(Float)

    # Balance Sheet
    total_assets = Column(Float)
    current_assets = Column(Float)
    total_liabilities = Column(Float)
    current_liabilities = Column(Float)
    equity = Column(Float)

    # Cash Flow
    operating_cash_flow = Column(Float)
    free_cash_flow = Column(Float)
    capex = Column(Float)

    # Key Ratios
    gross_margin = Column(Float)
    ebitda_margin = Column(Float)
    net_margin = Column(Float)
    current_ratio = Column(Float)
    debt_to_equity = Column(Float)
    return_on_assets = Column(Float)
    return_on_equity = Column(Float)

    # Growth Metrics
    revenue_growth = Column(Float)
    ebitda_growth = Column(Float)

    # Health Indicators
    financial_health = Column(SQLEnum(FinancialHealth))
    health_indicators = Column(JSON)  # Detailed health metrics

    # Source & Verification
    data_source = Column(String)
    is_audited = Column(Boolean, default=False)
    confidence_level = Column(Integer)  # 1-5 scale

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="financial_snapshots")
    tenant = relationship("Tenant", back_populates="financial_snapshots")


class DealActivity(Base):
    __tablename__ = "deal_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("deal_opportunities.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String, nullable=False)  # Clerk user ID

    # Activity Details
    activity_type = Column(String, nullable=False)  # Call, email, meeting, document review, etc.
    title = Column(String, nullable=False)
    description = Column(Text)

    # Participants
    participants = Column(JSON)  # List of participant names/emails

    # Outcomes
    outcome = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)

    # Metadata
    activity_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    opportunity = relationship("DealOpportunity", back_populates="activities")
    tenant = relationship("Tenant", back_populates="deal_activities")


class OpportunityEvaluation(Base):
    __tablename__ = "opportunity_evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("deal_opportunities.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    evaluator_id = Column(String, nullable=False)  # Clerk user ID

    # Evaluation Criteria
    market_opportunity = Column(Integer)  # 1-10 scale
    competitive_position = Column(Integer)
    management_quality = Column(Integer)
    financial_performance = Column(Integer)
    growth_potential = Column(Integer)
    risk_assessment = Column(Integer)
    strategic_fit = Column(Integer)

    # Overall Assessment
    recommendation = Column(String)  # Proceed, Pass, Need More Info
    confidence_level = Column(Integer)  # 1-5 scale

    # Detailed Analysis
    strengths = Column(JSON)  # List of strength points
    weaknesses = Column(JSON)  # List of weakness points
    opportunities_list = Column(JSON)  # List of opportunity points
    threats = Column(JSON)  # List of threat points

    # Comments
    evaluation_notes = Column(Text)
    conditions = Column(Text)  # Any conditions for proceeding

    # Metadata
    evaluation_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    opportunity = relationship("DealOpportunity", back_populates="evaluations")
    tenant = relationship("Tenant", back_populates="opportunity_evaluations")


class MarketIntelligence(Base):
    __tablename__ = "market_intelligence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    # Intelligence Type
    intelligence_type = Column(String)  # News, report, filing, announcement, etc.
    source = Column(String)
    source_url = Column(String)

    # Content
    title = Column(String, nullable=False)
    summary = Column(Text)
    full_content = Column(Text)

    # Relevance
    companies_mentioned = Column(JSON)  # List of company IDs or names
    industries = Column(JSON)  # List of relevant industries
    keywords = Column(JSON)  # List of relevant keywords

    # Analysis
    sentiment = Column(String)  # Positive, negative, neutral
    importance_score = Column(Integer)  # 1-5 scale
    actionable = Column(Boolean, default=False)
    action_items = Column(JSON)  # List of potential actions

    # Metadata
    published_date = Column(DateTime)
    collected_date = Column(DateTime, default=datetime.utcnow)
    processed_date = Column(DateTime)

    # Relationships
    tenant = relationship("Tenant", back_populates="market_intelligence")