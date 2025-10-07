"""
Negotiation Models for M&A SaaS Platform
Comprehensive models for managing deal negotiations, term sheets, and structuring
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


class NegotiationStatus(enum.Enum):
    """Status of negotiation process"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    EXPIRED = "expired"


class ParticipantRole(enum.Enum):
    """Role of negotiation participant"""
    BUYER = "buyer"
    SELLER = "seller"
    ADVISOR = "advisor"
    LEGAL_COUNSEL = "legal_counsel"
    INVESTMENT_BANKER = "investment_banker"
    OBSERVER = "observer"
    FACILITATOR = "facilitator"


class PositionStatus(enum.Enum):
    """Status of negotiation position"""
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COUNTER_PROPOSED = "counter_proposed"
    WITHDRAWN = "withdrawn"


class MessageType(enum.Enum):
    """Type of negotiation message"""
    POSITION_UPDATE = "position_update"
    COUNTER_OFFER = "counter_offer"
    QUESTION = "question"
    CLARIFICATION = "clarification"
    INTERNAL_NOTE = "internal_note"
    SYSTEM_UPDATE = "system_update"
    DOCUMENT_SHARE = "document_share"


class TermSheetStatus(enum.Enum):
    """Status of term sheet"""
    DRAFT = "draft"
    IN_NEGOTIATION = "in_negotiation"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    EXECUTED = "executed"
    SUPERSEDED = "superseded"


class DealStructureType(enum.Enum):
    """Type of deal structure"""
    ASSET_PURCHASE = "asset_purchase"
    STOCK_PURCHASE = "stock_purchase"
    MERGER = "merger"
    LEVERAGED_BUYOUT = "leveraged_buyout"
    MANAGEMENT_BUYOUT = "management_buyout"
    ROLL_UP = "roll_up"
    JOINT_VENTURE = "joint_venture"


class Negotiation(TenantModel, AuditableMixin):
    """
    Core negotiation session tracking
    Manages the overall negotiation process for a deal
    """
    __tablename__ = "negotiations"

    # Basic Information
    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id"), nullable=False, index=True)
    negotiation_round = Column(Integer, default=1, comment="Round of negotiation (1, 2, 3...)")

    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(NegotiationStatus), default=NegotiationStatus.DRAFT, index=True)

    # Timeline
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    target_completion_date = Column(Date)
    actual_completion_date = Column(Date)
    last_activity_date = Column(DateTime, default=datetime.utcnow)

    # Lead negotiators
    buyer_lead_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    seller_lead_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Current state
    current_term_sheet_id = Column(UUID(as_uuid=False), ForeignKey("term_sheets.id"))
    total_positions = Column(Integer, default=0)
    resolved_positions = Column(Integer, default=0)
    open_issues_count = Column(Integer, default=0)

    # Progress tracking
    completion_percentage = Column(Integer, default=0, comment="0-100")
    priority_level = Column(String(20), default="medium", comment="low, medium, high, critical")

    # Communication settings
    auto_notifications = Column(Boolean, default=True)
    confidentiality_level = Column(String(20), default="standard", comment="standard, high, maximum")

    # Metadata
    custom_fields = Column(JSON, default=dict)
    tags = Column(ARRAY(String(50)), default=list)

    # Relationships
    deal = relationship("Deal", backref="negotiations")
    buyer_lead = relationship("User", foreign_keys=[buyer_lead_id])
    seller_lead = relationship("User", foreign_keys=[seller_lead_id])
    current_term_sheet = relationship("TermSheet", foreign_keys=[current_term_sheet_id])
    participants = relationship("NegotiationParticipant", back_populates="negotiation", lazy="dynamic")
    positions = relationship("NegotiationPosition", back_populates="negotiation", lazy="dynamic")
    messages = relationship("NegotiationMessage", back_populates="negotiation", lazy="dynamic")
    term_sheets = relationship("TermSheet", back_populates="negotiation", lazy="dynamic")

    __table_args__ = (
        CheckConstraint('completion_percentage >= 0 AND completion_percentage <= 100'),
        Index('ix_negotiations_deal_status', 'deal_id', 'status'),
        Index('ix_negotiations_org_active', 'organization_id', 'status'),
        Index('ix_negotiations_last_activity', 'last_activity_date'),
    )

    @validates('completion_percentage')
    def validate_completion(self, key, value):
        if value is not None and not (0 <= value <= 100):
            raise ValueError("Completion percentage must be between 0 and 100")
        return value

    @property
    def days_active(self) -> int:
        """Calculate days since negotiation started"""
        end_date = self.actual_completion_date or datetime.utcnow().date()
        return (end_date - self.start_date.date()).days

    @property
    def is_overdue(self) -> bool:
        """Check if negotiation is past target completion date"""
        if not self.target_completion_date or self.actual_completion_date:
            return False
        return datetime.utcnow().date() > self.target_completion_date


class NegotiationParticipant(TenantModel, AuditableMixin):
    """Participants in a negotiation with roles and permissions"""
    __tablename__ = "negotiation_participants"

    negotiation_id = Column(UUID(as_uuid=False), ForeignKey("negotiations.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)

    role = Column(Enum(ParticipantRole), nullable=False)
    party_name = Column(String(200), comment="Company or entity they represent")

    # Permissions
    can_make_offers = Column(Boolean, default=False)
    can_accept_terms = Column(Boolean, default=False)
    can_view_confidential = Column(Boolean, default=False)
    can_add_participants = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True)
    joined_date = Column(DateTime, default=datetime.utcnow)
    last_seen_date = Column(DateTime)

    # Communication preferences
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    notification_frequency = Column(String(20), default="realtime", comment="realtime, hourly, daily")

    # Relationships
    negotiation = relationship("Negotiation", back_populates="participants")
    user = relationship("User", backref="negotiation_participations")

    __table_args__ = (
        Index('ix_negotiation_participants_unique', 'negotiation_id', 'user_id', unique=True),
        Index('ix_negotiation_participants_role', 'role'),
    )


class NegotiationPosition(TenantModel, AuditableMixin):
    """Individual negotiation positions on specific terms"""
    __tablename__ = "negotiation_positions"

    negotiation_id = Column(UUID(as_uuid=False), ForeignKey("negotiations.id", ondelete="CASCADE"),
                           nullable=False, index=True)

    # Position details
    term_category = Column(String(100), nullable=False, index=True,
                          comment="purchase_price, payment_terms, representations, etc.")
    term_name = Column(String(200), nullable=False)
    term_description = Column(Text)

    # Current position
    current_value = Column(Text, comment="Current agreed or proposed value")
    status = Column(Enum(PositionStatus), default=PositionStatus.PROPOSED, index=True)

    # Negotiation history (stored as JSON array)
    position_history = Column(JSON, default=list, comment="Array of position changes")

    # Party positions
    buyer_position = Column(Text)
    seller_position = Column(Text)
    buyer_rationale = Column(Text)
    seller_rationale = Column(Text)

    # Priority and impact
    priority_level = Column(Integer, default=3, comment="1=critical, 2=high, 3=medium, 4=low, 5=nice-to-have")
    deal_breaker = Column(Boolean, default=False, comment="Is this a deal-breaking term?")
    financial_impact = Column(Numeric(20, 2), comment="Estimated financial impact")

    # Assignment
    assigned_to_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    target_resolution_date = Column(Date)
    actual_resolution_date = Column(Date)

    # Discussion
    open_questions = Column(ARRAY(Text), default=list)
    internal_notes = Column(Text)

    # Relationships
    negotiation = relationship("Negotiation", back_populates="positions")
    assigned_to = relationship("User", backref="assigned_positions")

    __table_args__ = (
        CheckConstraint('priority_level >= 1 AND priority_level <= 5'),
        Index('ix_negotiation_positions_category', 'term_category'),
        Index('ix_negotiation_positions_status_priority', 'status', 'priority_level'),
        Index('ix_negotiation_positions_deal_breaker', 'deal_breaker'),
    )

    @property
    def is_resolved(self) -> bool:
        """Check if position is resolved"""
        return self.status == PositionStatus.ACCEPTED

    @property
    def is_overdue(self) -> bool:
        """Check if position resolution is overdue"""
        if not self.target_resolution_date or self.actual_resolution_date:
            return False
        return datetime.utcnow().date() > self.target_resolution_date


class NegotiationMessage(TenantModel, AuditableMixin):
    """Communication log for negotiations"""
    __tablename__ = "negotiation_messages"

    negotiation_id = Column(UUID(as_uuid=False), ForeignKey("negotiations.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    sender_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    message_type = Column(Enum(MessageType), default=MessageType.QUESTION, index=True)
    subject = Column(String(255))
    content = Column(Text, nullable=False)

    # Threading
    parent_message_id = Column(UUID(as_uuid=False), ForeignKey("negotiation_messages.id"))
    thread_id = Column(UUID(as_uuid=False), comment="Groups related messages")

    # Related content
    related_position_id = Column(UUID(as_uuid=False), ForeignKey("negotiation_positions.id"))
    related_term_sheet_id = Column(UUID(as_uuid=False), ForeignKey("term_sheets.id"))

    # Message properties
    is_internal = Column(Boolean, default=False, comment="Internal team message")
    is_confidential = Column(Boolean, default=False)
    requires_response = Column(Boolean, default=False)
    response_deadline = Column(DateTime)

    # Attachments
    attachments = Column(JSON, default=list, comment="Array of attachment metadata")

    # Read receipts
    read_by = Column(JSON, default=dict, comment="User ID -> timestamp of when read")

    # Relationships
    negotiation = relationship("Negotiation", back_populates="messages")
    sender = relationship("User", backref="sent_negotiation_messages")
    parent_message = relationship("NegotiationMessage", remote_side="NegotiationMessage.id", backref="replies")
    related_position = relationship("NegotiationPosition", backref="messages")
    related_term_sheet = relationship("TermSheet", backref="messages")

    __table_args__ = (
        Index('ix_negotiation_messages_thread', 'thread_id'),
        Index('ix_negotiation_messages_type', 'message_type'),
        Index('ix_negotiation_messages_created', 'created_at'),
    )


class TermSheetTemplate(TenantModel, AuditableMixin):
    """Reusable term sheet templates"""
    __tablename__ = "term_sheet_templates"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    industry = Column(String(100), index=True)
    deal_type = Column(Enum(DealStructureType), index=True)

    # Template structure
    template_structure = Column(JSON, nullable=False, comment="Template field definitions")
    default_values = Column(JSON, default=dict, comment="Default values for fields")
    validation_rules = Column(JSON, default=dict, comment="Field validation rules")

    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_date = Column(DateTime)

    # Template properties
    is_public = Column(Boolean, default=False, comment="Available to all organizations")
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")

    # Categories and tags
    category = Column(String(100), comment="Asset Purchase, Stock Purchase, etc.")
    tags = Column(ARRAY(String(50)), default=list)

    # Relationships
    term_sheets = relationship("TermSheet", back_populates="template", lazy="dynamic")

    __table_args__ = (
        Index('ix_term_sheet_templates_industry_type', 'industry', 'deal_type'),
        Index('ix_term_sheet_templates_category', 'category'),
        Index('ix_term_sheet_templates_active', 'is_active'),
    )


class TermSheet(TenantModel, AuditableMixin):
    """Individual term sheets for negotiations"""
    __tablename__ = "term_sheets"

    negotiation_id = Column(UUID(as_uuid=False), ForeignKey("negotiations.id"), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=False), ForeignKey("term_sheet_templates.id"))

    title = Column(String(255), nullable=False)
    version = Column(String(20), default="1.0")
    status = Column(Enum(TermSheetStatus), default=TermSheetStatus.DRAFT, index=True)

    # Term sheet content
    terms = Column(JSON, nullable=False, comment="All term sheet terms and values")

    # Key financial terms (extracted for easy querying)
    purchase_price = Column(Numeric(20, 2))
    currency = Column(String(3), default="USD")
    cash_consideration = Column(Numeric(20, 2))
    stock_consideration = Column(Numeric(20, 2))
    earnout_amount = Column(Numeric(20, 2))

    # Important dates
    effective_date = Column(Date)
    expiration_date = Column(Date)
    closing_date = Column(Date)

    # Approval workflow
    submitted_for_approval = Column(Boolean, default=False)
    approval_workflow = Column(JSON, default=list, comment="Approval steps and status")
    approved_by = Column(JSON, default=list, comment="List of approver user IDs")
    rejected_by = Column(JSON, default=list, comment="List of rejector user IDs with reasons")

    # Document management
    document_url = Column(String(1000), comment="URL to generated document")
    document_version = Column(Integer, default=1)
    signature_status = Column(String(50), default="not_sent", comment="not_sent, sent, partial, complete")

    # Comparison and history
    previous_version_id = Column(UUID(as_uuid=False), ForeignKey("term_sheets.id"))
    change_summary = Column(Text, comment="Summary of changes from previous version")

    # Metadata
    custom_fields = Column(JSON, default=dict)
    notes = Column(Text)

    # Relationships
    negotiation = relationship("Negotiation", back_populates="term_sheets")
    template = relationship("TermSheetTemplate", back_populates="term_sheets")
    previous_version = relationship("TermSheet", remote_side="TermSheet.id", backref="newer_versions")

    __table_args__ = (
        Index('ix_term_sheets_negotiation_version', 'negotiation_id', 'version'),
        Index('ix_term_sheets_status', 'status'),
        Index('ix_term_sheets_expiration', 'expiration_date'),
    )

    @property
    def is_expired(self) -> bool:
        """Check if term sheet has expired"""
        if not self.expiration_date:
            return False
        return datetime.utcnow().date() > self.expiration_date

    @property
    def total_consideration(self) -> Optional[Decimal]:
        """Calculate total consideration amount"""
        total = Decimal('0')
        if self.cash_consideration:
            total += self.cash_consideration
        if self.stock_consideration:
            total += self.stock_consideration
        if self.earnout_amount:
            total += self.earnout_amount
        return total if total > 0 else None


class DealStructure(TenantModel, AuditableMixin):
    """Deal structuring options and analysis"""
    __tablename__ = "deal_structures"

    negotiation_id = Column(UUID(as_uuid=False), ForeignKey("negotiations.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    structure_type = Column(Enum(DealStructureType), nullable=False, index=True)
    description = Column(Text)

    # Structure details
    structure_details = Column(JSON, nullable=False, comment="Detailed structure configuration")

    # Financial analysis
    total_consideration = Column(Numeric(20, 2))
    cash_component = Column(Numeric(20, 2))
    stock_component = Column(Numeric(20, 2))
    debt_component = Column(Numeric(20, 2))
    earnout_component = Column(Numeric(20, 2))

    # Tax implications
    buyer_tax_impact = Column(JSON, default=dict, comment="Tax analysis for buyer")
    seller_tax_impact = Column(JSON, default=dict, comment="Tax analysis for seller")
    estimated_tax_savings = Column(Numeric(20, 2))

    # Risk analysis
    risk_factors = Column(ARRAY(Text), default=list)
    risk_mitigation = Column(JSON, default=dict)
    risk_score = Column(Integer, comment="1-10 risk rating")

    # Feasibility
    regulatory_considerations = Column(Text)
    implementation_complexity = Column(Integer, comment="1-5 complexity rating")
    estimated_timeline_days = Column(Integer)

    # Comparison metrics
    net_present_value = Column(Numeric(20, 2))
    internal_rate_of_return = Column(Numeric(5, 2))
    return_on_investment = Column(Numeric(5, 2))

    # Approval and selection
    is_recommended = Column(Boolean, default=False)
    selection_rationale = Column(Text)
    approved_for_negotiation = Column(Boolean, default=False)

    # Relationships
    negotiation = relationship("Negotiation", backref="deal_structures")

    __table_args__ = (
        CheckConstraint('risk_score >= 1 AND risk_score <= 10'),
        CheckConstraint('implementation_complexity >= 1 AND implementation_complexity <= 5'),
        Index('ix_deal_structures_type', 'structure_type'),
        Index('ix_deal_structures_recommended', 'is_recommended'),
    )

    @validates('risk_score')
    def validate_risk_score(self, key, value):
        if value is not None and not (1 <= value <= 10):
            raise ValueError("Risk score must be between 1 and 10")
        return value

    @validates('implementation_complexity')
    def validate_complexity(self, key, value):
        if value is not None and not (1 <= value <= 5):
            raise ValueError("Implementation complexity must be between 1 and 5")
        return value