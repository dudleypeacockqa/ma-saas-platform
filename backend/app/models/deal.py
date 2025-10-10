"""
Deal Models for M&A SaaS Platform
Comprehensive models for managing M&A deals, valuations, activities, and team members
"""

import enum
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, String, Text, Integer, Numeric, Date, DateTime, Boolean,
    ForeignKey, Enum, JSON, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, validates

from .base import TenantModel, AuditableMixin
from sqlalchemy.orm import backref


class DealStage(enum.Enum):
    """Deal pipeline stages"""
    SOURCING = "sourcing"
    INITIAL_REVIEW = "initial_review"
    NDA_EXECUTION = "nda_execution"
    PRELIMINARY_ANALYSIS = "preliminary_analysis"
    VALUATION = "valuation"
    DUE_DILIGENCE = "due_diligence"
    NEGOTIATION = "negotiation"
    LOI_DRAFTING = "loi_drafting"
    DOCUMENTATION = "documentation"
    CLOSING = "closing"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    ON_HOLD = "on_hold"


class DealType(enum.Enum):
    """Types of M&A transactions"""
    ACQUISITION = "acquisition"
    MERGER = "merger"
    DIVESTITURE = "divestiture"
    JOINT_VENTURE = "joint_venture"
    MANAGEMENT_BUYOUT = "management_buyout"
    LEVERAGED_BUYOUT = "leveraged_buyout"
    ASSET_PURCHASE = "asset_purchase"
    STOCK_PURCHASE = "stock_purchase"
    STRATEGIC_INVESTMENT = "strategic_investment"
    MINORITY_INVESTMENT = "minority_investment"


class DealPriority(enum.Enum):
    """Deal priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Deal(TenantModel, AuditableMixin):
    """
    Core Deal model for M&A transactions
    Tracks all aspects of deal lifecycle from sourcing to closing
    """
    __tablename__ = "deals"

    # Basic Information
    deal_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    code_name = Column(String(100), index=True, comment="Internal confidential name")
    deal_type = Column(Enum(DealType), nullable=False, default=DealType.ACQUISITION)
    stage = Column(Enum(DealStage), nullable=False, default=DealStage.SOURCING, index=True)
    priority = Column(Enum(DealPriority), nullable=False, default=DealPriority.MEDIUM, index=True)

    # Target Company Information
    target_company_name = Column(String(255), nullable=False, index=True)
    target_company_website = Column(String(500))
    target_company_description = Column(Text)
    target_industry = Column(String(100), index=True)
    target_country = Column(String(2), comment="ISO 3166-1 alpha-2 country code")
    target_employees = Column(Integer)
    target_headquarters_location = Column(String(255))
    target_founded_year = Column(Integer)

    # Financial Information
    deal_value = Column(Numeric(20, 2), index=True)
    deal_currency = Column(String(3), nullable=False, default="USD")
    enterprise_value = Column(Numeric(20, 2))
    equity_value = Column(Numeric(20, 2))
    debt_assumed = Column(Numeric(20, 2))

    # Financial Multiples
    revenue_multiple = Column(Numeric(10, 2))
    ebitda_multiple = Column(Numeric(10, 2))
    ebit_multiple = Column(Numeric(10, 2))

    # Target Financials
    target_revenue = Column(Numeric(20, 2))
    target_ebitda = Column(Numeric(20, 2))
    target_ebit = Column(Numeric(20, 2))
    target_net_income = Column(Numeric(20, 2))
    target_total_assets = Column(Numeric(20, 2))
    target_total_liabilities = Column(Numeric(20, 2))

    # Deal Structure
    cash_consideration = Column(Numeric(20, 2))
    stock_consideration = Column(Numeric(20, 2))
    earnout_consideration = Column(Numeric(20, 2))
    other_consideration = Column(Numeric(20, 2))
    ownership_percentage = Column(Numeric(5, 2), comment="Percentage of ownership being acquired")

    # Important Dates
    initial_contact_date = Column(Date)
    nda_signed_date = Column(Date)
    loi_signed_date = Column(Date)
    expected_close_date = Column(Date, index=True)
    actual_close_date = Column(Date)
    termination_date = Column(Date)

    # Team and Contacts
    deal_lead_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), index=True)
    sponsor_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Deal Status and Tracking
    probability_of_close = Column(Integer, default=50, comment="Percentage 0-100")
    risk_level = Column(String(20), comment="low, medium, high, critical")
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_confidential = Column(Boolean, default=True, nullable=False)

    # Strategic Information
    executive_summary = Column(Text)
    investment_thesis = Column(Text)
    strategic_rationale = Column(Text)
    synergies_expected = Column(Text)
    integration_plan_summary = Column(Text)

    # Lists stored as JSON arrays
    key_risks = Column(ARRAY(Text), default=list, comment="Array of key risk factors")
    key_opportunities = Column(ARRAY(Text), default=list, comment="Array of opportunities")
    competitive_landscape = Column(ARRAY(Text), default=list)

    # Metadata
    tags = Column(ARRAY(String(50)), default=list, index=True)
    custom_fields = Column(JSON, default=dict, comment="Flexible additional data")

    # Next Steps
    next_steps = Column(Text)
    next_milestone_date = Column(Date)
    next_milestone_description = Column(String(500))

    # Relationships
    deal_lead = relationship("User", foreign_keys=[deal_lead_id], backref="led_deals")
    sponsor = relationship("User", foreign_keys=[sponsor_id], backref="sponsored_deals")
    team_members = relationship("DealTeamMember", back_populates="deal", lazy="dynamic")
    activities = relationship("DealActivity", back_populates="deal", lazy="dynamic",
                             order_by="desc(DealActivity.activity_date)")
    valuations = relationship("DealValuation", back_populates="deal", lazy="dynamic",
                             order_by="desc(DealValuation.valuation_date)")
    milestones = relationship("DealMilestone", back_populates="deal", lazy="dynamic",
                             order_by="DealMilestone.target_date")
    documents = relationship("DealDocument", back_populates="deal", lazy="dynamic")
    financial_models = relationship("DealFinancialModel", back_populates="deal", lazy="dynamic")

    # Table constraints
    __table_args__ = (
        CheckConstraint('probability_of_close >= 0 AND probability_of_close <= 100',
                       name='check_probability_range'),
        CheckConstraint('ownership_percentage >= 0 AND ownership_percentage <= 100',
                       name='check_ownership_range'),
        Index('ix_deals_org_stage_active', 'organization_id', 'stage', 'is_active'),
        Index('ix_deals_org_priority', 'organization_id', 'priority'),
        Index('ix_deals_expected_close', 'expected_close_date'),
        Index('ix_deals_org_id_created', 'organization_id', 'created_at'),
        Index('ix_deals_org_id_deleted', 'organization_id', 'is_deleted'),
    )

    @validates('probability_of_close')
    def validate_probability(self, key, value):
        if value is not None and not (0 <= value <= 100):
            raise ValueError("Probability must be between 0 and 100")
        return value

    @validates('ownership_percentage')
    def validate_ownership(self, key, value):
        if value is not None and not (0 <= value <= 100):
            raise ValueError("Ownership percentage must be between 0 and 100")
        return value

    @property
    def days_in_pipeline(self) -> int:
        """Calculate days since deal was created"""
        if self.actual_close_date:
            return (self.actual_close_date - self.created_at.date()).days
        return (datetime.utcnow().date() - self.created_at.date()).days

    @property
    def days_to_expected_close(self) -> Optional[int]:
        """Calculate days until expected close date"""
        if not self.expected_close_date:
            return None
        return (self.expected_close_date - datetime.utcnow().date()).days

    @property
    def is_overdue(self) -> bool:
        """Check if deal is past expected close date"""
        if not self.expected_close_date:
            return False
        return datetime.utcnow().date() > self.expected_close_date and self.stage not in [
            DealStage.CLOSED_WON, DealStage.CLOSED_LOST
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary with computed fields"""
        result = super().to_dict()
        result['days_in_pipeline'] = self.days_in_pipeline
        result['days_to_expected_close'] = self.days_to_expected_close
        result['is_overdue'] = self.is_overdue
        return result


class DealTeamMember(TenantModel, AuditableMixin):
    """Team members assigned to deals with roles and responsibilities"""
    __tablename__ = "deal_team_members"

    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id", ondelete="CASCADE"),
                    nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)

    role = Column(String(100), nullable=False, comment="Deal Lead, Analyst, Legal, etc.")
    responsibilities = Column(Text)
    time_allocation_percentage = Column(Integer, comment="Percentage of time allocated to deal")

    added_date = Column(Date, default=date.today, nullable=False)
    removed_date = Column(Date)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    deal = relationship("Deal", back_populates="team_members")
    user = relationship("User", backref="deal_memberships")

    __table_args__ = (
        Index('ix_deal_team_deal_user', 'deal_id', 'user_id', unique=True),
        Index('ix_deal_team_members_org_id_created', 'organization_id', 'created_at'),
        Index('ix_deal_team_members_org_id_deleted', 'organization_id', 'is_deleted'),
    )


class DealActivity(TenantModel, AuditableMixin):
    """Activity timeline and interaction log for deals"""
    __tablename__ = "deal_activities"

    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id", ondelete="CASCADE"),
                    nullable=False, index=True)

    activity_type = Column(String(50), nullable=False, index=True,
                          comment="meeting, call, email, note, milestone, stage_change, etc.")
    activity_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    subject = Column(String(255), nullable=False)
    description = Column(Text)

    # Meeting/Call specific
    participants = Column(ARRAY(String(255)), default=list)
    location = Column(String(255))
    duration_minutes = Column(Integer)

    # Outcome tracking
    outcome = Column(Text)
    action_items = Column(ARRAY(Text), default=list)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)

    # Attachments/links
    attachments = Column(JSON, default=list, comment="Array of attachment metadata")
    external_links = Column(ARRAY(String(500)), default=list)

    # Relationships
    deal = relationship("Deal", back_populates="activities")

    __table_args__ = (
        Index('ix_deal_activities_deal_date', 'deal_id', 'activity_date'),
        Index('ix_deal_activities_type', 'activity_type'),
        Index('ix_deal_team_members_org_id_created', 'organization_id', 'created_at'),
        Index('ix_deal_team_members_org_id_deleted', 'organization_id', 'is_deleted'),
    )


class DealValuation(TenantModel, AuditableMixin):
    """Valuation analyses and financial models for deals"""
    __tablename__ = "deal_valuations"

    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id", ondelete="CASCADE"),
                    nullable=False, index=True)

    valuation_date = Column(Date, nullable=False, index=True)
    valuation_method = Column(String(100), nullable=False,
                             comment="DCF, Comparable Companies, Precedent Transactions, etc.")

    # Valuation ranges
    enterprise_value_low = Column(Numeric(20, 2))
    enterprise_value_mid = Column(Numeric(20, 2))
    enterprise_value_high = Column(Numeric(20, 2))

    equity_value_low = Column(Numeric(20, 2))
    equity_value_mid = Column(Numeric(20, 2))
    equity_value_high = Column(Numeric(20, 2))

    # Key assumptions
    wacc = Column(Numeric(5, 2), comment="Weighted Average Cost of Capital %")
    terminal_growth_rate = Column(Numeric(5, 2), comment="Terminal growth rate %")
    assumptions = Column(JSON, default=dict, comment="Detailed valuation assumptions")

    # Analysis
    sensitivity_analysis = Column(JSON, default=dict)
    notes = Column(Text)

    # Prepared by
    prepared_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    reviewed_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    approved_date = Column(Date)

    # Relationships
    deal = relationship("Deal", back_populates="valuations")
    prepared_by = relationship("User", foreign_keys=[prepared_by_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])

    __table_args__ = (
        Index('ix_deal_valuations_deal_date', 'deal_id', 'valuation_date'),
        Index('ix_deal_team_members_org_id_created', 'organization_id', 'created_at'),
        Index('ix_deal_team_members_org_id_deleted', 'organization_id', 'is_deleted'),
    )


class DealMilestone(TenantModel, AuditableMixin):
    """Key milestones and deadlines for deal execution"""
    __tablename__ = "deal_milestones"

    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id", ondelete="CASCADE"),
                    nullable=False, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text)
    milestone_type = Column(String(50), comment="regulatory, legal, financial, operational, etc.")

    target_date = Column(Date, nullable=False, index=True)
    actual_completion_date = Column(Date)

    status = Column(String(20), default="pending", nullable=False,
                   comment="pending, in_progress, completed, delayed, cancelled")

    owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    completion_notes = Column(Text)

    is_critical = Column(Boolean, default=False, comment="Critical path milestone")
    dependencies = Column(ARRAY(UUID(as_uuid=False)), default=list,
                         comment="IDs of prerequisite milestones")

    # Relationships
    deal = relationship("Deal", back_populates="milestones")
    owner = relationship("User", backref="owned_milestones")

    __table_args__ = (
        Index('ix_deal_milestones_deal_target', 'deal_id', 'target_date'),
        Index('ix_deal_milestones_status', 'status'),
        Index('ix_deal_team_members_org_id_created', 'organization_id', 'created_at'),
        Index('ix_deal_team_members_org_id_deleted', 'organization_id', 'is_deleted'),
    )

    @property
    def is_overdue(self) -> bool:
        """Check if milestone is overdue"""
        if self.actual_completion_date or self.status == "completed":
            return False
        return datetime.utcnow().date() > self.target_date


class DealDocument(TenantModel, AuditableMixin):
    """Document management for deals"""
    __tablename__ = "deal_documents"

    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id", ondelete="CASCADE"),
                    nullable=False, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), index=True,
                     comment="NDA, LOI, Financial Statements, Legal, Due Diligence, etc.")

    # File information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(1000), comment="Path in storage system")
    file_url = Column(String(1000), comment="URL to access file")
    file_size = Column(Integer, comment="Size in bytes")
    file_type = Column(String(100), comment="MIME type")

    # Version control
    version = Column(String(20), default="1.0")
    replaces_document_id = Column(UUID(as_uuid=False), ForeignKey("deal_documents.id"))

    # Access control
    is_confidential = Column(Boolean, default=True)
    access_level = Column(String(20), default="team",
                         comment="public, team, restricted, confidential")

    # Metadata
    uploaded_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    reviewed_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    review_date = Column(DateTime)

    tags = Column(ARRAY(String(50)), default=list)
    custom_metadata = Column(JSON, default=dict)

    # Relationships
    deal = relationship("Deal", back_populates="documents")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
    previous_version = relationship("DealDocument", remote_side="DealDocument.id",
                                   backref="newer_versions", uselist=False)

    __table_args__ = (
        Index('ix_deal_documents_deal_category', 'deal_id', 'category'),
        Index('ix_deal_documents_upload_date', 'upload_date'),
        Index('ix_deal_team_members_org_id_created', 'organization_id', 'created_at'),
        Index('ix_deal_team_members_org_id_deleted', 'organization_id', 'is_deleted'),
    )


class DealFinancialModel(TenantModel, AuditableMixin):
    """Financial models and projections for deals"""
    __tablename__ = "deal_financial_models"

    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id", ondelete="CASCADE"),
                    nullable=False, index=True)

    model_name = Column(String(255), nullable=False)
    model_type = Column(String(100), nullable=False,
                       comment="Base Case, Upside, Downside, Management Case, etc.")
    model_version = Column(String(20), default="1.0")

    # Projection period
    projection_start_date = Column(Date)
    projection_end_date = Column(Date)
    projection_years = Column(Integer, default=5)

    # Model data (stored as JSON for flexibility)
    revenue_projections = Column(JSON, default=dict)
    expense_projections = Column(JSON, default=dict)
    cash_flow_projections = Column(JSON, default=dict)
    balance_sheet_projections = Column(JSON, default=dict)

    # Key metrics
    irr = Column(Numeric(5, 2), comment="Internal Rate of Return %")
    moic = Column(Numeric(5, 2), comment="Multiple on Invested Capital")
    payback_period_years = Column(Numeric(4, 2))
    npv = Column(Numeric(20, 2), comment="Net Present Value")

    # Assumptions
    key_assumptions = Column(JSON, default=dict)
    growth_rates = Column(JSON, default=dict)
    margin_assumptions = Column(JSON, default=dict)

    # Notes
    notes = Column(Text)

    # Model file
    file_path = Column(String(1000), comment="Path to Excel/model file")
    file_url = Column(String(1000))

    # Ownership
    created_by_model_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    last_updated_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    approved_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    approved_date = Column(DateTime)

    # Relationships
    deal = relationship("Deal", back_populates="financial_models")
    model_creator = relationship("User", foreign_keys=[created_by_model_id])
    last_updater = relationship("User", foreign_keys=[last_updated_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])

    __table_args__ = (
        Index('ix_deal_financial_models_deal', 'deal_id'),
        Index('ix_deal_team_members_org_id_created', 'organization_id', 'created_at'),
        Index('ix_deal_team_members_org_id_deleted', 'organization_id', 'is_deleted'),
    )
