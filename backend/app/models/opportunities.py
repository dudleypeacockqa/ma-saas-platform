"""
Market Opportunity and Research Models
Handles deal sourcing, company analysis, and investment research
"""
from sqlalchemy import (
    Column, String, Text, Integer, Numeric, Boolean, DateTime,
    ForeignKey, JSON, Enum as SQLEnum, Index, CheckConstraint, Float
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel, SoftDeleteMixin


class OpportunityStatus(str, enum.Enum):
    """Status of market opportunity"""
    NEW = "new"
    ANALYZING = "analyzing"
    QUALIFIED = "qualified"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED_TO_DEAL = "converted_to_deal"
    ARCHIVED = "archived"


class OpportunityPriority(str, enum.Enum):
    """Priority level for opportunities"""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    WATCH_LIST = "watch_list"


class CompanyRegion(str, enum.Enum):
    """Geographic regions"""
    UK = "uk"
    US = "us"
    EU = "eu"
    OTHER = "other"


class IndustryVertical(str, enum.Enum):
    """Target industry verticals"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    PROFESSIONAL_SERVICES = "professional_services"
    MANUFACTURING = "manufacturing"
    FINANCIAL_SERVICES = "financial_services"
    RETAIL = "retail"
    EDUCATION = "education"
    REAL_ESTATE = "real_estate"
    LOGISTICS = "logistics"
    OTHER = "other"


class DataSourceType(str, enum.Enum):
    """External data sources"""
    COMPANIES_HOUSE = "companies_house"
    SEC_EDGAR = "sec_edgar"
    NEWS_API = "news_api"
    LINKEDIN = "linkedin"
    MANUAL = "manual"
    WEB_SCRAPING = "web_scraping"
    INDUSTRY_REPORT = "industry_report"


class MarketOpportunity(BaseModel, SoftDeleteMixin):
    """
    Market opportunities discovered through automated scanning
    Represents potential M&A deals before formal deal creation
    """
    __tablename__ = "market_opportunities"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Company Identification
    company_name = Column(String(255), nullable=False, index=True)
    company_number = Column(String(100), index=True, comment="Companies House or SEC CIK")
    website = Column(String(500))
    headquarters_location = Column(String(255))
    region = Column(SQLEnum(CompanyRegion), nullable=False, index=True)

    # Industry Classification
    industry_vertical = Column(SQLEnum(IndustryVertical), nullable=False, index=True)
    industry_description = Column(Text)
    sic_codes = Column(ARRAY(String), comment="Standard Industrial Classification codes")

    # Company Size
    employee_count = Column(Integer)
    employee_count_range = Column(String(50))
    annual_revenue = Column(Numeric(20, 2))
    revenue_currency = Column(String(3), default="GBP")
    founded_year = Column(Integer)

    # Opportunity Classification
    status = Column(SQLEnum(OpportunityStatus), default=OpportunityStatus.NEW, nullable=False, index=True)
    priority = Column(SQLEnum(OpportunityPriority), default=OpportunityPriority.WARM, index=True)

    # Opportunity Details
    opportunity_type = Column(String(100), comment="Distressed, succession, growth, etc.")
    discovery_source = Column(SQLEnum(DataSourceType), nullable=False)
    discovery_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    discovery_notes = Column(Text)

    # Scoring
    overall_score = Column(Float, index=True, comment="AI-generated opportunity score 0-100")
    financial_health_score = Column(Float)
    strategic_fit_score = Column(Float)
    deal_complexity_score = Column(Float)
    market_conditions_score = Column(Float)

    # Key Metrics
    estimated_valuation_min = Column(Numeric(20, 2))
    estimated_valuation_max = Column(Numeric(20, 2))
    estimated_revenue_multiple = Column(Numeric(10, 2))
    estimated_ebitda_multiple = Column(Numeric(10, 2))

    # Flags and Signals
    is_distressed = Column(Boolean, default=False, index=True)
    is_succession_opportunity = Column(Boolean, default=False)
    is_growth_stage = Column(Boolean, default=False)
    has_competitive_bidding = Column(Boolean, default=False)

    # Tracking
    last_analyzed_at = Column(DateTime)
    analyzed_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    converted_to_deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id"))

    # Metadata
    metadata = Column(JSON, comment="Additional structured data")
    tags = Column(ARRAY(String))

    # Relationships
    organization = relationship("Organization")
    company_profile = relationship("CompanyProfile", back_populates="opportunity", uselist=False)
    research_reports = relationship("ResearchReport", back_populates="opportunity")
    scores = relationship("OpportunityScore", back_populates="opportunity")

    __table_args__ = (
        Index('ix_opportunity_region_industry', 'region', 'industry_vertical'),
        Index('ix_opportunity_score', 'overall_score', 'status'),
    )


class CompanyProfile(BaseModel, SoftDeleteMixin):
    """
    Detailed company analysis and profile
    Generated from various data sources and AI analysis
    """
    __tablename__ = "company_profiles"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    opportunity_id = Column(UUID(as_uuid=False), ForeignKey("market_opportunities.id"), unique=True)

    # Company Identifiers
    company_name = Column(String(255), nullable=False)
    legal_name = Column(String(255))
    company_number = Column(String(100), index=True)
    region = Column(SQLEnum(CompanyRegion), nullable=False)

    # Detailed Information
    business_description = Column(Text)
    products_services = Column(Text)
    target_markets = Column(ARRAY(String))
    competitive_advantages = Column(Text)

    # Financial Data (Latest Available)
    latest_revenue = Column(Numeric(20, 2))
    latest_ebitda = Column(Numeric(20, 2))
    latest_net_income = Column(Numeric(20, 2))
    latest_total_assets = Column(Numeric(20, 2))
    latest_total_liabilities = Column(Numeric(20, 2))
    latest_cash = Column(Numeric(20, 2))
    financial_year_end = Column(String(10))

    # Financial Ratios
    profit_margin = Column(Numeric(10, 4))
    debt_to_equity = Column(Numeric(10, 4))
    current_ratio = Column(Numeric(10, 4))
    roa = Column(Numeric(10, 4), comment="Return on Assets")
    roe = Column(Numeric(10, 4), comment="Return on Equity")

    # Growth Metrics
    revenue_growth_1yr = Column(Numeric(10, 4))
    revenue_growth_3yr_cagr = Column(Numeric(10, 4))
    revenue_growth_5yr_cagr = Column(Numeric(10, 4))
    employee_growth_1yr = Column(Numeric(10, 4))

    # Historical Financials (JSON)
    revenue_history = Column(JSON, comment="Array of {year, value}")
    ebitda_history = Column(JSON)
    employee_history = Column(JSON)

    # Leadership
    key_executives = Column(JSON, comment="Array of {name, title, tenure}")
    board_members = Column(JSON)
    major_shareholders = Column(JSON)

    # Market Position
    market_share_estimate = Column(Numeric(10, 4))
    key_competitors = Column(ARRAY(String))
    competitive_positioning = Column(Text)

    # Risk Factors
    risk_assessment = Column(Text)
    regulatory_risks = Column(ARRAY(String))
    market_risks = Column(ARRAY(String))
    operational_risks = Column(ARRAY(String))

    # Data Freshness
    last_data_update = Column(DateTime, default=datetime.utcnow)
    data_sources = Column(JSON, comment="Array of {source, date, fields}")

    # AI Analysis
    ai_summary = Column(Text, comment="Claude-generated executive summary")
    ai_strengths = Column(ARRAY(String))
    ai_weaknesses = Column(ARRAY(String))
    ai_opportunities = Column(ARRAY(String))
    ai_threats = Column(ARRAY(String))

    # Relationships
    organization = relationship("Organization")
    opportunity = relationship("MarketOpportunity", back_populates="company_profile")


class OpportunityScore(BaseModel):
    """
    Detailed scoring breakdown for opportunities
    Tracks scoring over time and by different algorithms
    """
    __tablename__ = "opportunity_scores"

    opportunity_id = Column(UUID(as_uuid=False), ForeignKey("market_opportunities.id"), nullable=False, index=True)

    # Score Components
    overall_score = Column(Float, nullable=False, index=True)
    financial_health_score = Column(Float, nullable=False)
    strategic_fit_score = Column(Float, nullable=False)
    deal_complexity_score = Column(Float, nullable=False)
    market_conditions_score = Column(Float, nullable=False)

    # Financial Health Breakdown
    revenue_growth_score = Column(Float)
    profitability_score = Column(Float)
    liquidity_score = Column(Float)
    leverage_score = Column(Float)

    # Strategic Fit Breakdown
    industry_alignment_score = Column(Float)
    geographic_fit_score = Column(Float)
    synergy_potential_score = Column(Float)
    market_position_score = Column(Float)

    # Scoring Metadata
    algorithm_version = Column(String(20), nullable=False)
    scored_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    scored_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Detailed Breakdown
    score_breakdown = Column(JSON, comment="Complete scoring details")
    recommendations = Column(JSON, comment="AI recommendations")

    # Relationships
    opportunity = relationship("MarketOpportunity", back_populates="scores")


class ResearchReport(BaseModel, SoftDeleteMixin):
    """
    AI-generated research reports for opportunities
    """
    __tablename__ = "research_reports"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    opportunity_id = Column(UUID(as_uuid=False), ForeignKey("market_opportunities.id"), nullable=False, index=True)

    # Report Metadata
    title = Column(String(500), nullable=False)
    report_type = Column(String(100), nullable=False, comment="Company Profile, Market Analysis, etc.")
    version = Column(Integer, default=1)

    # Report Content
    executive_summary = Column(Text)
    investment_thesis = Column(Text)
    company_overview = Column(Text)
    financial_analysis = Column(Text)
    market_analysis = Column(Text)
    competitive_analysis = Column(Text)
    risk_assessment = Column(Text)
    valuation_analysis = Column(Text)
    recommendations = Column(Text)

    # Structured Data
    key_findings = Column(JSON)
    financial_highlights = Column(JSON)
    valuation_range = Column(JSON, comment="{min, max, currency, method}")
    deal_structure_suggestions = Column(JSON)

    # Generation Details
    generated_by_ai = Column(Boolean, default=True)
    ai_model = Column(String(100))
    generation_prompt = Column(Text)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    generated_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Review and Approval
    reviewed_at = Column(DateTime)
    reviewed_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    is_approved = Column(Boolean, default=False)

    # Relationships
    organization = relationship("Organization")
    opportunity = relationship("MarketOpportunity", back_populates="research_reports")


class MarketIntelligence(BaseModel, SoftDeleteMixin):
    """
    Market trends, industry news, and intelligence reports
    """
    __tablename__ = "market_intelligence"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Intelligence Metadata
    title = Column(String(500), nullable=False)
    intelligence_type = Column(String(100), nullable=False, index=True, comment="News, Trend, Report")
    industry_vertical = Column(SQLEnum(IndustryVertical), index=True)
    region = Column(SQLEnum(CompanyRegion), index=True)

    # Content
    summary = Column(Text)
    full_content = Column(Text)
    key_insights = Column(JSON)

    # Source Information
    source_type = Column(SQLEnum(DataSourceType), nullable=False)
    source_url = Column(String(1000))
    source_name = Column(String(255))
    published_date = Column(DateTime, index=True)
    discovered_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relevance
    relevance_score = Column(Float, index=True)
    sentiment = Column(String(50), comment="Positive, Negative, Neutral")

    # Related Entities
    mentioned_companies = Column(ARRAY(String))
    mentioned_executives = Column(ARRAY(String))
    keywords = Column(ARRAY(String))

    # Metadata
    metadata = Column(JSON)

    # Relationships
    organization = relationship("Organization")

    __table_args__ = (
        Index('ix_market_intel_date_relevance', 'published_date', 'relevance_score'),
    )


class DataSource(BaseModel):
    """
    Track external data sources, API usage, and refresh schedules
    """
    __tablename__ = "data_sources"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Source Details
    source_type = Column(SQLEnum(DataSourceType), nullable=False, index=True)
    source_name = Column(String(255), nullable=False)
    api_endpoint = Column(String(1000))

    # Configuration
    api_key_name = Column(String(100), comment="Environment variable name")
    rate_limit = Column(Integer, comment="Requests per hour")
    is_active = Column(Boolean, default=True, index=True)

    # Usage Tracking
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    last_request_at = Column(DateTime)
    last_success_at = Column(DateTime)
    last_error = Column(Text)
    last_error_at = Column(DateTime)

    # Data Refresh
    refresh_frequency_hours = Column(Integer, default=24)
    last_refresh_at = Column(DateTime)
    next_refresh_at = Column(DateTime)

    # Metadata
    configuration = Column(JSON)
    metadata = Column(JSON)

    # Relationships
    organization = relationship("Organization")

    __table_args__ = (
        Index('ix_datasource_active_refresh', 'is_active', 'next_refresh_at'),
    )
