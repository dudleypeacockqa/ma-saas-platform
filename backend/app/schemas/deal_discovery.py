from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum


# Enums (matching the SQLAlchemy models)
class IndustryCategory(str, Enum):
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


class DealStage(str, Enum):
    DISCOVERY = "discovery"
    INITIAL_REVIEW = "initial_review"
    DUE_DILIGENCE = "due_diligence"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"


class FinancialHealth(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    DISTRESSED = "distressed"
    UNKNOWN = "unknown"


class OpportunitySource(str, Enum):
    DIRECT_APPROACH = "direct_approach"
    BROKER = "broker"
    INVESTMENT_BANK = "investment_bank"
    INDUSTRY_CONTACT = "industry_contact"
    SUCCESSION_PLANNING = "succession_planning"
    DISTRESSED_SALE = "distressed_sale"
    COMPETITOR = "competitor"
    MARKET_SCAN = "market_scan"
    OTHER = "other"


# Company Schemas
class CompanyBase(BaseModel):
    name: str
    registration_number: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[IndustryCategory] = None
    sub_industry: Optional[str] = None
    employee_count: Optional[int] = None
    year_founded: Optional[int] = None
    revenue_range_min: Optional[float] = None
    revenue_range_max: Optional[float] = None
    ebitda: Optional[float] = None
    ebitda_margin: Optional[float] = None
    growth_rate: Optional[float] = None
    ceo_name: Optional[str] = None
    cfo_name: Optional[str] = None
    key_contacts: Optional[List[Dict[str, Any]]] = None
    key_products: Optional[List[str]] = None
    key_customers: Optional[List[str]] = None
    competitors: Optional[List[str]] = None
    data_sources: Optional[List[str]] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    registration_number: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[IndustryCategory] = None
    sub_industry: Optional[str] = None
    employee_count: Optional[int] = None
    year_founded: Optional[int] = None
    revenue_range_min: Optional[float] = None
    revenue_range_max: Optional[float] = None
    ebitda: Optional[float] = None
    ebitda_margin: Optional[float] = None
    growth_rate: Optional[float] = None
    ceo_name: Optional[str] = None
    cfo_name: Optional[str] = None
    key_contacts: Optional[List[Dict[str, Any]]] = None
    key_products: Optional[List[str]] = None
    key_customers: Optional[List[str]] = None
    competitors: Optional[List[str]] = None
    data_sources: Optional[List[str]] = None


class CompanyResponse(CompanyBase):
    id: uuid.UUID
    tenant_id: int
    last_data_refresh: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Deal Opportunity Schemas
class DealOpportunityBase(BaseModel):
    company_id: uuid.UUID
    title: str
    description: Optional[str] = None
    source: Optional[OpportunitySource] = None
    stage: DealStage = DealStage.DISCOVERY
    priority: int = Field(3, ge=1, le=5)
    asking_price: Optional[float] = None
    estimated_valuation: Optional[float] = None
    target_irr: Optional[float] = None
    projected_roi: Optional[float] = None
    deal_structure: Optional[str] = None
    financing_required: Optional[float] = None
    financing_sources: Optional[List[str]] = None
    expected_closing_date: Optional[datetime] = None
    risk_factors: Optional[List[str]] = None
    mitigation_strategies: Optional[List[str]] = None
    internal_notes: Optional[str] = None
    next_steps: Optional[str] = None
    is_confidential: bool = False


class DealOpportunityCreate(DealOpportunityBase):
    pass


class DealOpportunityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    source: Optional[OpportunitySource] = None
    stage: Optional[DealStage] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    asking_price: Optional[float] = None
    estimated_valuation: Optional[float] = None
    target_irr: Optional[float] = None
    projected_roi: Optional[float] = None
    deal_structure: Optional[str] = None
    financing_required: Optional[float] = None
    financing_sources: Optional[List[str]] = None
    expected_closing_date: Optional[datetime] = None
    actual_closing_date: Optional[datetime] = None
    risk_factors: Optional[List[str]] = None
    mitigation_strategies: Optional[List[str]] = None
    internal_notes: Optional[str] = None
    next_steps: Optional[str] = None
    is_active: Optional[bool] = None
    is_confidential: Optional[bool] = None


class DealOpportunityResponse(DealOpportunityBase):
    id: uuid.UUID
    tenant_id: int
    user_id: str
    financial_score: Optional[float] = None
    strategic_fit_score: Optional[float] = None
    risk_score: Optional[float] = None
    overall_score: Optional[float] = None
    scoring_rationale: Optional[Dict[str, Any]] = None
    identified_date: datetime
    first_contact_date: Optional[datetime] = None
    loi_date: Optional[datetime] = None
    actual_closing_date: Optional[datetime] = None
    last_activity_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Financial Snapshot Schemas
class FinancialSnapshotBase(BaseModel):
    year: int
    quarter: Optional[int] = None
    revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_income: Optional[float] = None
    ebitda: Optional[float] = None
    net_income: Optional[float] = None
    total_assets: Optional[float] = None
    current_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    current_liabilities: Optional[float] = None
    equity: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None
    capex: Optional[float] = None
    gross_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    net_margin: Optional[float] = None
    current_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    return_on_assets: Optional[float] = None
    return_on_equity: Optional[float] = None
    revenue_growth: Optional[float] = None
    ebitda_growth: Optional[float] = None
    financial_health: Optional[FinancialHealth] = None
    health_indicators: Optional[Dict[str, Any]] = None
    data_source: Optional[str] = None
    is_audited: bool = False
    confidence_level: Optional[int] = Field(None, ge=1, le=5)


class FinancialSnapshotCreate(FinancialSnapshotBase):
    pass


class FinancialSnapshotResponse(FinancialSnapshotBase):
    id: uuid.UUID
    company_id: uuid.UUID
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Deal Activity Schemas
class DealActivityBase(BaseModel):
    activity_type: str
    title: str
    description: Optional[str] = None
    participants: Optional[List[str]] = None
    outcome: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None


class DealActivityCreate(DealActivityBase):
    pass


class DealActivityResponse(DealActivityBase):
    id: uuid.UUID
    opportunity_id: uuid.UUID
    tenant_id: int
    user_id: str
    activity_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Opportunity Evaluation Schemas
class OpportunityEvaluationBase(BaseModel):
    market_opportunity: Optional[int] = Field(None, ge=1, le=10)
    competitive_position: Optional[int] = Field(None, ge=1, le=10)
    management_quality: Optional[int] = Field(None, ge=1, le=10)
    financial_performance: Optional[int] = Field(None, ge=1, le=10)
    growth_potential: Optional[int] = Field(None, ge=1, le=10)
    risk_assessment: Optional[int] = Field(None, ge=1, le=10)
    strategic_fit: Optional[int] = Field(None, ge=1, le=10)
    recommendation: Optional[str] = None
    confidence_level: Optional[int] = Field(None, ge=1, le=5)
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    opportunities_list: Optional[List[str]] = None
    threats: Optional[List[str]] = None
    evaluation_notes: Optional[str] = None
    conditions: Optional[str] = None


class OpportunityEvaluationCreate(OpportunityEvaluationBase):
    pass


class OpportunityEvaluationResponse(OpportunityEvaluationBase):
    id: uuid.UUID
    opportunity_id: uuid.UUID
    tenant_id: int
    evaluator_id: str
    evaluation_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Screening and Scoring Schemas
class ScreeningFilters(BaseModel):
    revenue_min: Optional[float] = None
    revenue_max: Optional[float] = None
    industries: Optional[List[IndustryCategory]] = None
    countries: Optional[List[str]] = None
    employee_min: Optional[int] = None
    employee_max: Optional[int] = None
    growth_rate_min: Optional[float] = None
    ebitda_margin_min: Optional[float] = None
    financial_health: Optional[List[FinancialHealth]] = None


class OpportunityScoring(BaseModel):
    financial_score: float
    strategic_score: float
    risk_score: float
    growth_score: float
    overall_score: float
    breakdown: Dict[str, Dict[str, float]]


class RankedOpportunity(BaseModel):
    opportunity: DealOpportunityResponse
    company: CompanyResponse
    scores: OpportunityScoring
    overall_score: float