"""
Advanced Transaction Models for M&A Deal Execution
Handles deal phases, integration planning, synergies, and financial modeling
"""
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, JSON, Enum as SQLEnum, UniqueConstraint, Index,
    Numeric, Date, CheckConstraint
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime, date
import enum
from decimal import Decimal
from app.models.base import TenantModel, UUIDPrimaryKeyMixin, AuditableMixin, SoftDeleteMixin

class TransactionPhaseType(str, enum.Enum):
    """Detailed transaction phases"""
    ORIGINATION = "origination"
    SCREENING = "screening"
    INITIAL_CONTACT = "initial_contact"
    CONFIDENTIALITY = "confidentiality"
    INFORMATION_EXCHANGE = "information_exchange"
    VALUATION_ANALYSIS = "valuation_analysis"
    INITIAL_OFFER = "initial_offer"
    DUE_DILIGENCE = "due_diligence"
    NEGOTIATION = "negotiation"
    FINAL_OFFER = "final_offer"
    DOCUMENTATION = "documentation"
    REGULATORY_APPROVAL = "regulatory_approval"
    FINANCING = "financing"
    CLOSING_PREPARATION = "closing_preparation"
    CLOSING = "closing"
    POST_CLOSING = "post_closing"
    INTEGRATION = "integration"

class ModelType(str, enum.Enum):
    """Types of financial models"""
    DCF = "dcf"
    LBO = "lbo"
    COMPARABLE_COMPANY = "comparable_company"
    PRECEDENT_TRANSACTION = "precedent_transaction"
    MERGER_MODEL = "merger_model"
    SYNERGY_ANALYSIS = "synergy_analysis"
    SENSITIVITY_ANALYSIS = "sensitivity_analysis"
    SCENARIO_PLANNING = "scenario_planning"
    MONTE_CARLO = "monte_carlo"

class VendorType(str, enum.Enum):
    """Types of third-party vendors"""
    LAW_FIRM = "law_firm"
    INVESTMENT_BANK = "investment_bank"
    ACCOUNTING_FIRM = "accounting_firm"
    CONSULTING_FIRM = "consulting_firm"
    VALUATION_EXPERT = "valuation_expert"
    INDUSTRY_EXPERT = "industry_expert"
    ENVIRONMENTAL_CONSULTANT = "environmental_consultant"
    IT_CONSULTANT = "it_consultant"
    HR_CONSULTANT = "hr_consultant"
    TAX_ADVISOR = "tax_advisor"
    INSURANCE_BROKER = "insurance_broker"

class SynergyType(str, enum.Enum):
    """Types of synergies in M&A"""
    REVENUE = "revenue"
    COST = "cost"
    TAX = "tax"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"

class IntegrationStatus(str, enum.Enum):
    """Integration milestone status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    AT_RISK = "at_risk"
    DELAYED = "delayed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TransactionPhase(TenantModel, UUIDPrimaryKeyMixin, AuditableMixin):
    """
    Detailed tracking of transaction phases and milestones
    """
    __tablename__ = "transaction_phases"

    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=False)
    phase_type = Column(SQLEnum(TransactionPhaseType), nullable=False)
    phase_name = Column(String(200), nullable=False)

    # Timeline
    planned_start_date = Column(Date)
    planned_end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    duration_days = Column(Integer)

    # Status and Progress
    is_active = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Integer, default=0)

    # Key Activities
    key_activities = Column(JSONB, default=list)  # List of activities with status
    deliverables = Column(JSONB, default=list)  # Required deliverables
    decision_points = Column(JSONB, default=list)  # Critical decisions

    # Success Criteria
    success_criteria = Column(Text)
    exit_criteria = Column(Text)

    # Risk and Issues
    risks_identified = Column(JSONB, default=list)
    issues_encountered = Column(JSONB, default=list)
    blockers = Column(JSONB, default=list)

    # Team and Responsibilities
    phase_lead_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    team_members = Column(ARRAY(UUID(as_uuid=True)), default=list)
    external_parties = Column(JSONB, default=list)

    # Documentation
    required_documents = Column(JSONB, default=list)
    completed_documents = Column(JSONB, default=list)

    # Notes and Comments
    notes = Column(Text)
    lessons_learned = Column(Text)

    # Relationships
    deal = relationship("Deal", backref="transaction_phases")
    phase_lead = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_transaction_phases_deal", "deal_id", "phase_type"),
        Index("idx_transaction_phases_active", "deal_id", "is_active"),
        CheckConstraint("completion_percentage >= 0 AND completion_percentage <= 100"),
    )

class FinancialModel(TenantModel, UUIDPrimaryKeyMixin, AuditableMixin):
    """
    Financial models for deal valuation and analysis
    """
    __tablename__ = "financial_models"

    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=False)
    model_type = Column(SQLEnum(ModelType), nullable=False)
    model_name = Column(String(200), nullable=False)
    version = Column(String(20), default="1.0")

    # Model Parameters
    base_assumptions = Column(JSONB, nullable=False)  # Key assumptions
    scenarios = Column(JSONB, default=dict)  # Multiple scenarios (base, upside, downside)

    # DCF Specific
    discount_rate = Column(Numeric(10, 4))
    terminal_growth_rate = Column(Numeric(10, 4))
    projection_years = Column(Integer)

    # LBO Specific
    entry_multiple = Column(Numeric(10, 2))
    exit_multiple = Column(Numeric(10, 2))
    leverage_ratio = Column(Numeric(10, 2))
    irr_target = Column(Numeric(10, 4))

    # Valuation Results
    enterprise_value = Column(Numeric(20, 2))
    equity_value = Column(Numeric(20, 2))
    implied_multiple = Column(Numeric(10, 2))
    valuation_range_low = Column(Numeric(20, 2))
    valuation_range_high = Column(Numeric(20, 2))

    # Sensitivity Analysis
    sensitivity_parameters = Column(JSONB, default=dict)  # Parameters to test
    sensitivity_results = Column(JSONB, default=dict)  # Results matrix

    # Model Data
    financial_projections = Column(JSONB)  # Detailed projections
    comparable_companies = Column(JSONB, default=list)  # For comps analysis
    precedent_transactions = Column(JSONB, default=list)  # For precedent analysis

    # Model Quality
    confidence_level = Column(Numeric(5, 2))  # 0-100
    data_quality_score = Column(Numeric(5, 2))  # 0-100
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Collaboration
    model_owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewers = Column(ARRAY(UUID(as_uuid=True)), default=list)
    approval_status = Column(String(50))
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)

    # Notes and Documentation
    assumptions_documentation = Column(Text)
    methodology_notes = Column(Text)
    caveats_and_limitations = Column(Text)

    # File Storage
    model_file_url = Column(String(500))  # Link to Excel/other model file
    supporting_files = Column(JSONB, default=list)

    # Relationships
    deal = relationship("Deal", backref="financial_models")
    model_owner = relationship("User", foreign_keys=[model_owner_id])
    approver = relationship("User", foreign_keys=[approved_by])

    # Indexes
    __table_args__ = (
        Index("idx_financial_models_deal", "deal_id", "model_type"),
        UniqueConstraint("deal_id", "model_name", "version"),
    )

class IntegrationPlan(TenantModel, UUIDPrimaryKeyMixin, AuditableMixin):
    """
    Post-acquisition integration planning and tracking
    """
    __tablename__ = "integration_plans"

    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=False)
    plan_name = Column(String(200), nullable=False)

    # Timeline
    integration_start_date = Column(Date)
    day_100_date = Column(Date)
    full_integration_target = Column(Date)

    # Integration Approach
    integration_type = Column(String(50))  # full, partial, standalone
    integration_speed = Column(String(50))  # fast, moderate, slow

    # Workstreams
    workstreams = Column(JSONB, default=dict)  # Key workstreams with leads and status

    # Key Milestones (First 100 Days)
    day_1_milestones = Column(JSONB, default=list)
    day_30_milestones = Column(JSONB, default=list)
    day_60_milestones = Column(JSONB, default=list)
    day_90_milestones = Column(JSONB, default=list)
    day_100_milestones = Column(JSONB, default=list)

    # Synergy Realization Plan
    synergy_targets = Column(JSONB, default=dict)
    synergy_tracking = Column(JSONB, default=dict)

    # Cultural Integration
    cultural_assessment = Column(JSONB, default=dict)
    cultural_integration_plan = Column(Text)
    communication_plan = Column(JSONB, default=dict)

    # Systems Integration
    it_integration_plan = Column(JSONB, default=dict)
    systems_to_integrate = Column(JSONB, default=list)
    data_migration_plan = Column(JSONB, default=dict)

    # Organization Design
    org_structure_changes = Column(JSONB, default=dict)
    retention_plan = Column(JSONB, default=dict)
    severance_estimates = Column(Numeric(20, 2))

    # Risk Management
    integration_risks = Column(JSONB, default=list)
    mitigation_strategies = Column(JSONB, default=list)
    contingency_plans = Column(JSONB, default=dict)

    # Success Metrics
    success_metrics = Column(JSONB, default=list)
    kpi_targets = Column(JSONB, default=dict)
    measurement_frequency = Column(String(50))

    # Status Tracking
    overall_status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.NOT_STARTED)
    completion_percentage = Column(Integer, default=0)
    budget_allocated = Column(Numeric(20, 2))
    budget_spent = Column(Numeric(20, 2))

    # Team
    integration_lead_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    steering_committee = Column(ARRAY(UUID(as_uuid=True)), default=list)

    # Relationships
    deal = relationship("Deal", backref="integration_plans")
    integration_lead = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_integration_plans_deal", "deal_id"),
        CheckConstraint("completion_percentage >= 0 AND completion_percentage <= 100"),
    )

class SynergyTracking(TenantModel, UUIDPrimaryKeyMixin, AuditableMixin):
    """
    Track and measure synergy realization
    """
    __tablename__ = "synergy_tracking"

    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=False)
    integration_plan_id = Column(UUID(as_uuid=True), ForeignKey("integration_plans.id"))

    # Synergy Details
    synergy_type = Column(SQLEnum(SynergyType), nullable=False)
    synergy_name = Column(String(200), nullable=False)
    description = Column(Text)

    # Financial Impact
    target_annual_value = Column(Numeric(20, 2), nullable=False)
    realized_to_date = Column(Numeric(20, 2), default=0)
    run_rate_achieved = Column(Numeric(20, 2), default=0)

    # Timeline
    identification_date = Column(Date)
    target_realization_date = Column(Date)
    actual_realization_date = Column(Date)

    # Implementation
    implementation_plan = Column(Text)
    required_investments = Column(Numeric(20, 2))
    one_time_costs = Column(Numeric(20, 2))

    # Tracking
    confidence_level = Column(Numeric(5, 2))  # 0-100
    realization_percentage = Column(Numeric(5, 2), default=0)  # 0-100
    tracking_metrics = Column(JSONB, default=list)
    measurement_method = Column(Text)

    # Risk and Dependencies
    implementation_risks = Column(JSONB, default=list)
    dependencies = Column(JSONB, default=list)
    blockers = Column(JSONB, default=list)

    # Ownership
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    workstream = Column(String(100))

    # Status
    status = Column(String(50), default="identified")  # identified, in_progress, realized, at_risk, cancelled
    priority = Column(String(20), default="medium")  # low, medium, high, critical

    # Documentation
    supporting_documentation = Column(JSONB, default=list)
    notes = Column(Text)

    # Relationships
    deal = relationship("Deal", backref="synergy_tracking")
    integration_plan = relationship("IntegrationPlan", backref="synergies")
    owner = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_synergy_tracking_deal", "deal_id", "synergy_type"),
        Index("idx_synergy_tracking_status", "status", "priority"),
    )

class VendorManagement(TenantModel, UUIDPrimaryKeyMixin, AuditableMixin):
    """
    Manage third-party vendors in deal execution
    """
    __tablename__ = "vendor_management"

    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=False)

    # Vendor Information
    vendor_type = Column(SQLEnum(VendorType), nullable=False)
    vendor_name = Column(String(200), nullable=False)
    contact_person = Column(String(200))
    contact_email = Column(String(200))
    contact_phone = Column(String(50))

    # Engagement Details
    engagement_date = Column(Date)
    scope_of_work = Column(Text, nullable=False)
    deliverables = Column(JSONB, default=list)
    timeline = Column(JSONB, default=dict)

    # Financial
    fee_structure = Column(String(100))  # fixed, hourly, success, retainer
    estimated_fees = Column(Numeric(20, 2))
    fee_cap = Column(Numeric(20, 2))
    actual_fees_to_date = Column(Numeric(20, 2), default=0)
    payment_terms = Column(String(200))

    # Performance
    performance_rating = Column(Numeric(3, 1))  # 1-5 stars
    kpi_metrics = Column(JSONB, default=dict)
    sla_compliance = Column(Numeric(5, 2))  # 0-100%

    # Documentation
    engagement_letter_url = Column(String(500))
    nda_signed = Column(Boolean, default=False)
    nda_date = Column(Date)
    contracts = Column(JSONB, default=list)  # List of contract documents

    # Work Product
    work_products = Column(JSONB, default=list)  # Deliverables received
    reports_submitted = Column(Integer, default=0)
    last_update_date = Column(Date)

    # Status
    engagement_status = Column(String(50), default="active")  # proposed, active, completed, terminated
    issues_encountered = Column(JSONB, default=list)
    satisfaction_notes = Column(Text)

    # Relationships
    deal = relationship("Deal", backref="vendors")

    # Indexes
    __table_args__ = (
        Index("idx_vendor_management_deal", "deal_id", "vendor_type"),
        Index("idx_vendor_management_status", "engagement_status"),
    )

class ClosingChecklist(TenantModel, UUIDPrimaryKeyMixin, AuditableMixin):
    """
    Deal closing checklist and conditions tracking
    """
    __tablename__ = "closing_checklists"

    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=False)

    # Checklist Item
    category = Column(String(100), nullable=False)  # legal, financial, regulatory, operational
    item_name = Column(String(500), nullable=False)
    description = Column(Text)

    # Requirements
    is_condition_precedent = Column(Boolean, default=False)
    is_material = Column(Boolean, default=False)
    required_by = Column(String(100))  # buyer, seller, both, regulatory

    # Responsibility
    responsible_party = Column(String(100))  # buyer, seller, joint
    responsible_person_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    responsible_vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor_management.id"))

    # Timeline
    due_date = Column(Date)
    reminder_date = Column(Date)
    completion_date = Column(Date)

    # Status
    status = Column(String(50), default="pending")  # pending, in_progress, completed, waived, deferred
    completion_percentage = Column(Integer, default=0)

    # Documentation
    required_documents = Column(JSONB, default=list)
    submitted_documents = Column(JSONB, default=list)

    # Review and Approval
    requires_approval = Column(Boolean, default=False)
    approvers = Column(ARRAY(UUID(as_uuid=True)), default=list)
    approval_status = Column(String(50))
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime)

    # Issues and Notes
    issues_identified = Column(JSONB, default=list)
    resolution_notes = Column(Text)
    waiver_reason = Column(Text)

    # Dependencies
    depends_on = Column(ARRAY(UUID(as_uuid=True)), default=list)  # Other checklist items
    blocks = Column(ARRAY(UUID(as_uuid=True)), default=list)  # Items this blocks

    # Relationships
    deal = relationship("Deal", backref="closing_checklist")
    responsible_person = relationship("User")
    responsible_vendor = relationship("VendorManagement")

    # Indexes
    __table_args__ = (
        Index("idx_closing_checklist_deal", "deal_id", "category"),
        Index("idx_closing_checklist_status", "status", "is_condition_precedent"),
        CheckConstraint("completion_percentage >= 0 AND completion_percentage <= 100"),
    )