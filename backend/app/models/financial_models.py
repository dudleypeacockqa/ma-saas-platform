"""
Financial Models and Valuation Database Models
Handles DCF, comparable company analysis, precedent transactions, and LBO models
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


class ValuationMethod(str, enum.Enum):
    """Valuation methodology types"""
    DCF = "dcf"
    COMPARABLE_COMPANY = "comparable_company"
    PRECEDENT_TRANSACTION = "precedent_transaction"
    LBO = "lbo"
    ASSET_BASED = "asset_based"
    OPTION_PRICING = "option_pricing"


class ScenarioType(str, enum.Enum):
    """Financial scenario types"""
    BASE = "base"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    DOWNSIDE = "downside"
    CUSTOM = "custom"


class TerminalValueMethod(str, enum.Enum):
    """Terminal value calculation methods"""
    PERPETUITY_GROWTH = "perpetuity_growth"
    EXIT_MULTIPLE = "exit_multiple"


class ReportStatus(str, enum.Enum):
    """Valuation report status"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    FINAL = "final"
    ARCHIVED = "archived"


class ValuationModel(BaseModel, SoftDeleteMixin):
    """
    Master valuation model combining multiple methodologies
    Links to opportunities or deals for comprehensive valuation
    """
    __tablename__ = "valuation_models"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Linked Entities
    opportunity_id = Column(UUID(as_uuid=False), ForeignKey("market_opportunities.id"), index=True)
    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id"), index=True)

    # Model Identification
    model_name = Column(String(255), nullable=False)
    model_description = Column(Text)
    version = Column(Integer, default=1, nullable=False)

    # Target Company
    company_name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100))
    target_revenue = Column(Numeric(20, 2))
    target_ebitda = Column(Numeric(20, 2))
    fiscal_year_end = Column(String(10))

    # Valuation Summary
    primary_method = Column(SQLEnum(ValuationMethod), nullable=False)
    valuation_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    base_case_value = Column(Numeric(20, 2), comment="Base case enterprise value")
    optimistic_value = Column(Numeric(20, 2))
    pessimistic_value = Column(Numeric(20, 2))

    # Multiples (for quick reference)
    ev_revenue_multiple = Column(Numeric(10, 2))
    ev_ebitda_multiple = Column(Numeric(10, 2))
    pe_multiple = Column(Numeric(10, 2))

    # Assumptions Summary
    wacc = Column(Numeric(10, 4), comment="Weighted Average Cost of Capital %")
    terminal_growth_rate = Column(Numeric(10, 4), comment="Perpetual growth rate %")
    discount_rate = Column(Numeric(10, 4))

    # Status and Ownership
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.DRAFT, nullable=False)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    approved_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Metadata
    assumptions = Column(JSON, comment="Key assumptions and inputs")
    sensitivity_results = Column(JSON, comment="Sensitivity analysis results")
    notes = Column(Text)
    tags = Column(ARRAY(String))

    # Relationships
    dcf_models = relationship("DCFModel", back_populates="valuation")
    comparable_analyses = relationship("ComparableCompanyAnalysis", back_populates="valuation")
    precedent_transactions = relationship("PrecedentTransactionAnalysis", back_populates="valuation")
    lbo_models = relationship("LBOModel", back_populates="valuation")

    __table_args__ = (
        Index('ix_valuation_company', 'company_name', 'valuation_date'),
        Index('ix_valuation_method', 'primary_method', 'status'),
    )


class DCFModel(BaseModel, SoftDeleteMixin):
    """
    Discounted Cash Flow valuation model
    Projects free cash flows and calculates present value
    """
    __tablename__ = "dcf_models"

    valuation_id = Column(UUID(as_uuid=False), ForeignKey("valuation_models.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Model Parameters
    scenario_type = Column(SQLEnum(ScenarioType), default=ScenarioType.BASE, nullable=False)
    projection_years = Column(Integer, default=5, nullable=False)
    terminal_value_method = Column(SQLEnum(TerminalValueMethod), default=TerminalValueMethod.PERPETUITY_GROWTH)

    # WACC Components
    risk_free_rate = Column(Numeric(10, 4), comment="Risk-free rate %")
    market_risk_premium = Column(Numeric(10, 4), comment="Market risk premium %")
    beta = Column(Numeric(10, 4), comment="Company beta")
    cost_of_equity = Column(Numeric(10, 4), comment="Cost of equity %")
    cost_of_debt = Column(Numeric(10, 4), comment="Cost of debt %")
    tax_rate = Column(Numeric(10, 4), comment="Corporate tax rate %")
    debt_to_equity = Column(Numeric(10, 4), comment="Target debt-to-equity ratio")
    wacc = Column(Numeric(10, 4), nullable=False, comment="Calculated WACC %")

    # Terminal Value
    terminal_growth_rate = Column(Numeric(10, 4), comment="Perpetual growth rate %")
    exit_multiple = Column(Numeric(10, 2), comment="Exit EBITDA multiple")
    terminal_value = Column(Numeric(20, 2))

    # Valuation Output
    enterprise_value = Column(Numeric(20, 2), nullable=False)
    equity_value = Column(Numeric(20, 2))
    net_debt = Column(Numeric(20, 2))

    # Cash Flow Projections (JSON arrays for each year)
    revenue_projections = Column(JSON, comment="Array of projected revenues")
    ebitda_projections = Column(JSON, comment="Array of projected EBITDA")
    ebit_projections = Column(JSON, comment="Array of projected EBIT")
    nopat_projections = Column(JSON, comment="Array of NOPAT (Net Operating Profit After Tax)")
    capex_projections = Column(JSON, comment="Array of capital expenditures")
    depreciation_projections = Column(JSON, comment="Array of depreciation")
    working_capital_changes = Column(JSON, comment="Array of working capital changes")
    free_cash_flows = Column(JSON, comment="Array of unlevered free cash flows")
    discount_factors = Column(JSON, comment="Array of discount factors")
    present_values = Column(JSON, comment="Array of PV of cash flows")

    # Growth Assumptions
    revenue_growth_rates = Column(JSON, comment="Array of revenue growth rates by year")
    ebitda_margin = Column(Numeric(10, 2), comment="Target EBITDA margin %")
    capex_percent_revenue = Column(Numeric(10, 2), comment="CapEx as % of revenue")
    working_capital_percent_revenue = Column(Numeric(10, 2))

    # Relationships
    valuation = relationship("ValuationModel", back_populates="dcf_models")


class ComparableCompanyAnalysis(BaseModel, SoftDeleteMixin):
    """
    Trading comparable company analysis
    Analyzes public company multiples for valuation
    """
    __tablename__ = "comparable_company_analyses"

    valuation_id = Column(UUID(as_uuid=False), ForeignKey("valuation_models.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Analysis Parameters
    industry = Column(String(100), nullable=False)
    selection_criteria = Column(JSON, comment="Criteria used to select comparables")

    # Valuation Multiples (Summary Statistics)
    ev_revenue_mean = Column(Numeric(10, 2))
    ev_revenue_median = Column(Numeric(10, 2))
    ev_revenue_min = Column(Numeric(10, 2))
    ev_revenue_max = Column(Numeric(10, 2))

    ev_ebitda_mean = Column(Numeric(10, 2))
    ev_ebitda_median = Column(Numeric(10, 2))
    ev_ebitda_min = Column(Numeric(10, 2))
    ev_ebitda_max = Column(Numeric(10, 2))

    pe_mean = Column(Numeric(10, 2))
    pe_median = Column(Numeric(10, 2))

    # Applied Multiples (after adjustments)
    selected_ev_revenue = Column(Numeric(10, 2), comment="Selected multiple for target")
    selected_ev_ebitda = Column(Numeric(10, 2))
    selected_pe = Column(Numeric(10, 2))

    # Adjustments
    size_premium = Column(Numeric(10, 2), comment="Premium/discount for size difference %")
    liquidity_discount = Column(Numeric(10, 2), comment="Discount for illiquidity %")
    control_premium = Column(Numeric(10, 2), comment="Premium for control %")

    # Valuation Output
    implied_enterprise_value = Column(Numeric(20, 2))
    implied_equity_value = Column(Numeric(20, 2))

    # Comparable Companies Data
    comparable_companies = Column(JSON, comment="Array of comparable company data")

    # Relationships
    valuation = relationship("ValuationModel", back_populates="comparable_analyses")


class PrecedentTransactionAnalysis(BaseModel, SoftDeleteMixin):
    """
    Precedent transaction analysis
    Analyzes historical M&A transactions for valuation benchmarks
    """
    __tablename__ = "precedent_transaction_analyses"

    valuation_id = Column(UUID(as_uuid=False), ForeignKey("valuation_models.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Analysis Parameters
    industry = Column(String(100), nullable=False)
    lookback_period_months = Column(Integer, default=36, comment="How many months back to analyze")
    selection_criteria = Column(JSON)

    # Transaction Multiples (Summary Statistics)
    ev_revenue_mean = Column(Numeric(10, 2))
    ev_revenue_median = Column(Numeric(10, 2))
    ev_revenue_min = Column(Numeric(10, 2))
    ev_revenue_max = Column(Numeric(10, 2))

    ev_ebitda_mean = Column(Numeric(10, 2))
    ev_ebitda_median = Column(Numeric(10, 2))
    ev_ebitda_min = Column(Numeric(10, 2))
    ev_ebitda_max = Column(Numeric(10, 2))

    # Applied Multiples
    selected_ev_revenue = Column(Numeric(10, 2))
    selected_ev_ebitda = Column(Numeric(10, 2))

    # Premiums and Adjustments
    strategic_buyer_premium = Column(Numeric(10, 2), comment="Average premium for strategic buyers %")
    financial_buyer_premium = Column(Numeric(10, 2), comment="Average premium for financial buyers %")
    market_timing_adjustment = Column(Numeric(10, 2), comment="Adjustment for market conditions %")

    # Valuation Output
    implied_enterprise_value = Column(Numeric(20, 2))
    implied_equity_value = Column(Numeric(20, 2))

    # Transaction Data
    precedent_transactions = Column(JSON, comment="Array of comparable transactions")

    # Relationships
    valuation = relationship("ValuationModel", back_populates="precedent_transactions")


class LBOModel(BaseModel, SoftDeleteMixin):
    """
    Leveraged Buyout model
    Analyzes potential returns for PE-backed acquisitions
    """
    __tablename__ = "lbo_models"

    valuation_id = Column(UUID(as_uuid=False), ForeignKey("valuation_models.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Transaction Assumptions
    purchase_price = Column(Numeric(20, 2), nullable=False)
    purchase_multiple = Column(Numeric(10, 2), comment="Entry EBITDA multiple")
    transaction_fees = Column(Numeric(20, 2))

    # Capital Structure
    equity_investment = Column(Numeric(20, 2), nullable=False)
    senior_debt = Column(Numeric(20, 2))
    subordinated_debt = Column(Numeric(20, 2))
    mezzanine_debt = Column(Numeric(20, 2))
    seller_note = Column(Numeric(20, 2))

    total_debt = Column(Numeric(20, 2), nullable=False)
    debt_to_ebitda = Column(Numeric(10, 2), comment="Leverage ratio")

    # Debt Terms
    senior_debt_rate = Column(Numeric(10, 4), comment="Interest rate %")
    subordinated_debt_rate = Column(Numeric(10, 4))
    mezzanine_rate = Column(Numeric(10, 4))
    debt_amortization_schedule = Column(JSON, comment="Debt paydown by year")

    # Operating Assumptions
    hold_period_years = Column(Integer, default=5, nullable=False)
    revenue_projections = Column(JSON, comment="Revenue forecast")
    ebitda_projections = Column(JSON, comment="EBITDA forecast")
    capex_projections = Column(JSON)
    working_capital_changes = Column(JSON)

    # Exit Assumptions
    exit_year = Column(Integer, nullable=False)
    exit_multiple = Column(Numeric(10, 2), comment="Exit EBITDA multiple")
    exit_ebitda = Column(Numeric(20, 2))
    exit_enterprise_value = Column(Numeric(20, 2))
    exit_debt_balance = Column(Numeric(20, 2))
    exit_equity_value = Column(Numeric(20, 2))

    # Returns Analysis
    money_multiple = Column(Numeric(10, 2), comment="MOIC - Multiple of Invested Capital")
    irr = Column(Numeric(10, 2), comment="Internal Rate of Return %")
    cash_on_cash_return = Column(Numeric(10, 2))

    # Management Equity
    management_equity_percent = Column(Numeric(10, 2), comment="Management ownership %")
    management_investment = Column(Numeric(20, 2))
    management_exit_proceeds = Column(Numeric(20, 2))

    # Sensitivity Analysis
    sensitivity_scenarios = Column(JSON, comment="Array of sensitivity analysis results")

    # Cash Flow Detail
    annual_cash_flows = Column(JSON, comment="Detailed annual cash flows")

    # Relationships
    valuation = relationship("ValuationModel", back_populates="lbo_models")


class ValuationReport(BaseModel, SoftDeleteMixin):
    """
    Generated valuation reports
    PDF reports with charts, analysis, and recommendations
    """
    __tablename__ = "valuation_reports"

    valuation_id = Column(UUID(as_uuid=False), ForeignKey("valuation_models.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Report Metadata
    report_title = Column(String(255), nullable=False)
    report_type = Column(String(100), comment="Executive Summary, Full Report, etc.")
    report_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Report Content
    executive_summary = Column(Text)
    key_findings = Column(JSON, comment="Array of key findings")
    recommendations = Column(Text)

    # Report Status
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.DRAFT, nullable=False)
    generated_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    approved_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # File Storage
    pdf_url = Column(String(1000), comment="S3 URL or file path")
    excel_url = Column(String(1000), comment="Excel model URL")

    # Report Sections
    include_dcf = Column(Boolean, default=True)
    include_comparable = Column(Boolean, default=True)
    include_precedent = Column(Boolean, default=True)
    include_lbo = Column(Boolean, default=False)
    include_sensitivity = Column(Boolean, default=True)

    # Charts and Visualizations
    charts_config = Column(JSON, comment="Chart configuration and data")

    # Access Control
    is_confidential = Column(Boolean, default=True)
    shared_with = Column(ARRAY(UUID(as_uuid=False)), comment="User IDs with access")

    __table_args__ = (
        Index('ix_report_date', 'report_date', 'status'),
    )


class MarketDataSnapshot(BaseModel):
    """
    Market data snapshots for valuation
    Stores risk-free rates, market multiples, etc.
    """
    __tablename__ = "market_data_snapshots"

    # Date and Source
    snapshot_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    data_source = Column(String(100), comment="Bloomberg, Yahoo Finance, etc.")

    # Interest Rates
    risk_free_rate_10yr = Column(Numeric(10, 4), comment="10-year treasury yield %")
    risk_free_rate_5yr = Column(Numeric(10, 4))
    prime_rate = Column(Numeric(10, 4))
    libor_3m = Column(Numeric(10, 4))

    # Market Indices
    sp500_level = Column(Numeric(10, 2))
    sp500_pe_ratio = Column(Numeric(10, 2))
    market_risk_premium = Column(Numeric(10, 4), comment="Historical equity risk premium %")

    # Industry Multiples (by sector)
    industry_multiples = Column(JSON, comment="EV/Revenue and EV/EBITDA by industry")

    # Credit Spreads
    investment_grade_spread = Column(Numeric(10, 4))
    high_yield_spread = Column(Numeric(10, 4))

    # Additional Data
    extra_data = Column(JSON)

    __table_args__ = (
        Index('ix_market_snapshot_date', 'snapshot_date'),
    )


class FinancialStatement(BaseModel, SoftDeleteMixin):
    """
    Company financial statements for analysis
    Stores P&L, Balance Sheet, and Cash Flow data
    """
    __tablename__ = "financial_statements"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id"), index=True)

    # Statement Details
    statement_type = Column(String(50), nullable=False, comment="income_statement, balance_sheet, cash_flow")
    period_type = Column(String(20), nullable=False, comment="annual, quarterly, monthly")
    period_end_date = Column(DateTime, nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False)

    # Financial Data (stored as JSON for flexibility)
    financial_data = Column(JSON, nullable=False, comment="All financial line items")

    # Source Information
    data_source = Column(String(100), comment="xero, quickbooks, manual, etc.")
    currency = Column(String(3), default="GBP", nullable=False)

    # Metadata
    is_audited = Column(Boolean, default=False)
    auditor_notes = Column(Text)

    __table_args__ = (
        Index('ix_financial_statements_period', 'period_end_date', 'statement_type'),
    )


class CashFlowProjection(BaseModel, SoftDeleteMixin):
    """
    Future cash flow projections for DCF analysis
    """
    __tablename__ = "cash_flow_projections"

    valuation_id = Column(UUID(as_uuid=False), ForeignKey("valuation_models.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Projection Details
    projection_year = Column(Integer, nullable=False)
    scenario_type = Column(SQLEnum(ScenarioType), default=ScenarioType.BASE, nullable=False)

    # Cash Flow Components (in base currency)
    revenue = Column(Numeric(15, 2))
    gross_profit = Column(Numeric(15, 2))
    ebitda = Column(Numeric(15, 2))
    ebit = Column(Numeric(15, 2))
    taxes = Column(Numeric(15, 2))
    capex = Column(Numeric(15, 2))
    working_capital_change = Column(Numeric(15, 2))
    free_cash_flow = Column(Numeric(15, 2), nullable=False)

    # Growth Assumptions
    revenue_growth_rate = Column(Numeric(10, 4), comment="% growth rate")
    margin_assumptions = Column(JSON, comment="Detailed margin assumptions")

    __table_args__ = (
        Index('ix_cashflow_projection_year', 'valuation_id', 'projection_year'),
    )


class FinancialMetric(BaseModel, SoftDeleteMixin):
    """
    Calculated financial metrics and ratios
    """
    __tablename__ = "financial_metrics"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    financial_statement_id = Column(UUID(as_uuid=False), ForeignKey("financial_statements.id"), nullable=False)

    # Metric Details
    metric_name = Column(String(100), nullable=False)
    metric_category = Column(String(50), nullable=False, comment="liquidity, profitability, leverage, etc.")
    metric_value = Column(Numeric(15, 6), nullable=False)
    calculation_method = Column(Text, comment="How this metric was calculated")

    # Context
    period_end_date = Column(DateTime, nullable=False)
    currency = Column(String(3), default="GBP")

    __table_args__ = (
        Index('ix_financial_metrics_name', 'metric_name', 'period_end_date'),
    )


class RatioAnalysis(BaseModel, SoftDeleteMixin):
    """
    Financial ratio analysis results
    """
    __tablename__ = "ratio_analyses"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    analysis_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Ratio Categories
    liquidity_ratios = Column(JSON, comment="Current ratio, quick ratio, etc.")
    profitability_ratios = Column(JSON, comment="ROE, ROA, gross margin, etc.")
    leverage_ratios = Column(JSON, comment="Debt-to-equity, interest coverage, etc.")
    efficiency_ratios = Column(JSON, comment="Asset turnover, inventory turnover, etc.")

    # Analysis Results
    overall_score = Column(Numeric(5, 2), comment="Overall financial health score 0-100")
    key_strengths = Column(ARRAY(String), comment="Key financial strengths")
    key_weaknesses = Column(ARRAY(String), comment="Key financial weaknesses")
    recommendations = Column(Text)

    __table_args__ = (
        Index('ix_ratio_analysis_date', 'analysis_date'),
    )


class BenchmarkData(BaseModel, SoftDeleteMixin):
    """
    Industry benchmark data for comparison
    """
    __tablename__ = "benchmark_data"

    # Industry Classification
    industry_code = Column(String(10), nullable=False, comment="SIC or NAICS code")
    industry_name = Column(String(255), nullable=False)
    sub_industry = Column(String(255))

    # Geographic Scope
    geographic_scope = Column(String(50), default="UK", comment="UK, US, EU, Global")

    # Benchmark Metrics
    metric_name = Column(String(100), nullable=False)
    median_value = Column(Numeric(15, 6))
    percentile_25 = Column(Numeric(15, 6))
    percentile_75 = Column(Numeric(15, 6))
    sample_size = Column(Integer, comment="Number of companies in benchmark")

    # Data Source and Date
    data_source = Column(String(100), comment="Source of benchmark data")
    data_date = Column(DateTime, nullable=False)

    __table_args__ = (
        Index('ix_benchmark_industry_metric', 'industry_code', 'metric_name'),
    )
