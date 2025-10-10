"""
Due Diligence Management Models
Handles checklists, document requests, reviews, and risk assessments
"""
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    DateTime, ForeignKey, JSON, Enum as SQLEnum,
    UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
from typing import Dict, List, Optional
from app.models.base import TenantModel, UUIDPrimaryKeyMixin, SoftDeleteMixin

class DocumentCategory(str, enum.Enum):
    """Document categories for due diligence"""
    FINANCIAL = "financial"
    LEGAL = "legal"
    OPERATIONAL = "operational"
    COMMERCIAL = "commercial"
    HR = "hr"
    IT = "it"
    ENVIRONMENTAL = "environmental"
    INTELLECTUAL_PROPERTY = "ip"
    REGULATORY = "regulatory"
    TAX = "tax"
    INSURANCE = "insurance"
    REAL_ESTATE = "real_estate"
    CONTRACTS = "contracts"
    COMPLIANCE = "compliance"
    OTHER = "other"

class DocumentStatus(str, enum.Enum):
    """Document review status"""
    NOT_REQUESTED = "not_requested"
    REQUESTED = "requested"
    UPLOADED = "uploaded"
    UNDER_REVIEW = "under_review"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CLARIFICATION = "requires_clarification"

class RiskLevel(str, enum.Enum):
    """Risk assessment levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class ChecklistType(str, enum.Enum):
    """Types of due diligence checklists"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    FINANCIAL_SERVICES = "financial_services"
    REAL_ESTATE = "real_estate"
    ENERGY = "energy"
    CONSUMER = "consumer"
    B2B_SAAS = "b2b_saas"
    MARKETPLACE = "marketplace"
    CUSTOM = "custom"

class DueDiligenceChecklist(TenantModel, UUIDPrimaryKeyMixin, SoftDeleteMixin):
    """Due diligence checklist templates"""
    __tablename__ = "due_diligence_checklists"

    # Basic Information
    name = Column(String(200), nullable=False)
    description = Column(Text)
    checklist_type = Column(SQLEnum(ChecklistType), nullable=False)
    industry = Column(String(100))
    is_template = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    # Template Data
    categories = Column(JSON, default=list)  # List of categories to include
    custom_fields = Column(JSON, default=dict)  # Additional custom fields

    # Version Control
    version = Column(String(20), default="1.0.0")
    parent_template_id = Column(UUID(as_uuid=True), ForeignKey("due_diligence_checklists.id"))

    # Usage Tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)

    # Relationships
    parent_template = relationship("DueDiligenceChecklist", remote_side="DueDiligenceChecklist.id")
    checklist_items = relationship("DueDiligenceItem", back_populates="checklist", cascade="all, delete-orphan")
    processes = relationship("DueDiligenceProcess", back_populates="checklist")

    # Indexes
    __table_args__ = (
        Index("ix_dd_checklist_type", "checklist_type"),
        Index("ix_dd_checklist_template", "is_template", "is_active"),
        UniqueConstraint("organization_id", "name", "version", name="uq_checklist_name_version"),
    )

class DueDiligenceItem(TenantModel, UUIDPrimaryKeyMixin):
    """Individual items in a due diligence checklist"""
    __tablename__ = "due_diligence_items"

    # Foreign Keys
    checklist_id = Column(UUID(as_uuid=True), ForeignKey("due_diligence_checklists.id"), nullable=False)

    # Item Details
    category = Column(SQLEnum(DocumentCategory), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    is_required = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)

    # Requirements
    document_types = Column(JSON, default=list)  # Expected document types
    validation_rules = Column(JSON, default=dict)  # Validation criteria
    review_guidelines = Column(Text)  # Guidelines for reviewers

    # Risk Assessment
    risk_weight = Column(Float, default=1.0)  # Weight in risk calculation
    critical_item = Column(Boolean, default=False)

    # Relationships
    checklist = relationship("DueDiligenceChecklist", back_populates="checklist_items")

    # Indexes
    __table_args__ = (
        Index("ix_dd_item_checklist", "checklist_id"),
        Index("ix_dd_item_category", "category"),
        Index("ix_dd_item_order", "checklist_id", "order_index"),
    )

class DueDiligenceProcess(TenantModel, UUIDPrimaryKeyMixin, SoftDeleteMixin):
    """Due diligence process for a specific deal"""
    __tablename__ = "due_diligence_processes"

    # Foreign Keys
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=False)
    checklist_id = Column(UUID(as_uuid=True), ForeignKey("due_diligence_checklists.id"), nullable=False)

    # Process Information
    name = Column(String(200), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    target_completion_date = Column(DateTime)
    actual_completion_date = Column(DateTime)

    # Status
    status = Column(String(50), default="in_progress")
    completion_percentage = Column(Float, default=0.0)

    # Team
    lead_reviewer_id = Column(String(100))  # Clerk user ID
    assigned_team = Column(JSON, default=list)  # List of reviewer IDs

    # Risk Assessment
    overall_risk_score = Column(Float, default=0.0)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.MEDIUM)
    risk_factors = Column(JSON, default=dict)

    # Metadata
    notes = Column(Text)
    tags = Column(JSON, default=list)

    # Relationships
    deal = relationship("Deal", backref=backref("due_diligence_processes", cascade="all, delete-orphan"))
    checklist = relationship("DueDiligenceChecklist", back_populates="processes")
    document_requests = relationship("DocumentRequest", back_populates="process", cascade="all, delete-orphan")
    documents = relationship("DueDiligenceDocument", back_populates="process", cascade="all, delete-orphan")
    reviews = relationship("DocumentReview", back_populates="process")

    # Indexes
    __table_args__ = (
        Index("ix_dd_process_deal", "deal_id"),
        Index("ix_dd_process_status", "status"),
        Index("ix_dd_process_risk", "risk_level"),
        UniqueConstraint("deal_id", "name", name="uq_process_deal_name"),
    )

class DocumentRequest(TenantModel, UUIDPrimaryKeyMixin):
    """Document requests for due diligence"""
    __tablename__ = "document_requests"

    # Foreign Keys
    process_id = Column(UUID(as_uuid=True), ForeignKey("due_diligence_processes.id"), nullable=False)
    checklist_item_id = Column(UUID(as_uuid=True), ForeignKey("due_diligence_items.id"))

    # Request Details
    title = Column(String(300), nullable=False)
    description = Column(Text)
    category = Column(SQLEnum(DocumentCategory), nullable=False)

    # Status
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.NOT_REQUESTED)
    priority = Column(String(20), default="normal")  # critical, high, normal, low

    # Timing
    requested_date = Column(DateTime)
    requested_by = Column(String(100))  # Clerk user ID
    due_date = Column(DateTime)
    fulfilled_date = Column(DateTime)

    # Response
    response_notes = Column(Text)
    rejection_reason = Column(Text)

    # Metadata
    tags = Column(JSON, default=list)
    custom_fields = Column(JSON, default=dict)

    # Relationships
    process = relationship("DueDiligenceProcess", back_populates="document_requests")
    documents = relationship("DueDiligenceDocument", back_populates="request")

    # Indexes
    __table_args__ = (
        Index("ix_doc_request_process", "process_id"),
        Index("ix_doc_request_status", "status"),
        Index("ix_doc_request_category", "category"),
        Index("ix_doc_request_priority", "priority"),
    )

class DueDiligenceDocument(TenantModel, UUIDPrimaryKeyMixin, SoftDeleteMixin):
    """Documents uploaded for due diligence"""
    __tablename__ = "due_diligence_documents"

    # Foreign Keys
    process_id = Column(UUID(as_uuid=True), ForeignKey("due_diligence_processes.id"), nullable=False)
    request_id = Column(UUID(as_uuid=True), ForeignKey("document_requests.id"))

    # Document Information
    name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # in bytes
    file_type = Column(String(50))
    mime_type = Column(String(100))

    # Categorization
    category = Column(SQLEnum(DocumentCategory), nullable=False)
    subcategory = Column(String(100))
    tags = Column(JSON, default=list)

    # Version Control
    version = Column(String(20), default="1.0")
    is_latest = Column(Boolean, default=True)
    parent_document_id = Column(UUID(as_uuid=True), ForeignKey("due_diligence_documents.id"))

    # Upload Details
    uploaded_by = Column(String(100), nullable=False)  # Clerk user ID
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Review Status
    review_status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED)
    reviewed_by = Column(String(100))
    reviewed_at = Column(DateTime)

    # Risk Assessment
    risk_flags = Column(JSON, default=list)
    risk_score = Column(Float, default=0.0)

    # Metadata
    description = Column(Text)
    notes = Column(Text)
    custom_fields = Column(JSON, default=dict)

    # Relationships
    process = relationship("DueDiligenceProcess", back_populates="documents")
    request = relationship("DocumentRequest", back_populates="documents")
    parent_document = relationship("DueDiligenceDocument", remote_side="DueDiligenceDocument.id")
    reviews = relationship("DocumentReview", back_populates="document", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_dd_doc_process", "process_id"),
        Index("ix_dd_doc_request", "request_id"),
        Index("ix_dd_doc_category", "category"),
        Index("ix_dd_doc_status", "review_status"),
        Index("ix_dd_doc_latest", "is_latest"),
    )

class DocumentReview(TenantModel, UUIDPrimaryKeyMixin):
    """Reviews of due diligence documents"""
    __tablename__ = "document_reviews"

    # Foreign Keys
    document_id = Column(UUID(as_uuid=True), ForeignKey("due_diligence_documents.id"), nullable=False)
    process_id = Column(UUID(as_uuid=True), ForeignKey("due_diligence_processes.id"), nullable=False)

    # Review Details
    reviewer_id = Column(String(100), nullable=False)  # Clerk user ID
    reviewer_name = Column(String(200))
    review_date = Column(DateTime, default=datetime.utcnow)

    # Assessment
    status = Column(SQLEnum(DocumentStatus), nullable=False)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW)
    confidence_score = Column(Float)  # 0-100 confidence in assessment

    # Findings
    findings = Column(Text)
    issues_identified = Column(JSON, default=list)
    recommendations = Column(Text)
    action_items = Column(JSON, default=list)

    # Flags
    requires_follow_up = Column(Boolean, default=False)
    is_blocking = Column(Boolean, default=False)
    escalation_required = Column(Boolean, default=False)

    # Metadata
    review_type = Column(String(50))  # initial, follow_up, final
    time_spent_minutes = Column(Integer)
    attachments = Column(JSON, default=list)

    # Relationships
    document = relationship("DueDiligenceDocument", back_populates="reviews")
    process = relationship("DueDiligenceProcess", back_populates="reviews")

    # Indexes
    __table_args__ = (
        Index("ix_doc_review_document", "document_id"),
        Index("ix_doc_review_process", "process_id"),
        Index("ix_doc_review_reviewer", "reviewer_id"),
        Index("ix_doc_review_status", "status"),
        Index("ix_doc_review_risk", "risk_level"),
        UniqueConstraint("document_id", "reviewer_id", "review_type", name="uq_document_reviewer_type"),
    )

class RiskAssessment(TenantModel, UUIDPrimaryKeyMixin):
    """Risk assessments for due diligence process"""
    __tablename__ = "risk_assessments"

    # Foreign Keys
    process_id = Column(UUID(as_uuid=True), ForeignKey("due_diligence_processes.id"), nullable=False)

    # Assessment Details
    assessment_date = Column(DateTime, default=datetime.utcnow)
    assessor_id = Column(String(100), nullable=False)  # Clerk user ID

    # Risk Categories
    financial_risk = Column(Float, default=0.0)
    legal_risk = Column(Float, default=0.0)
    operational_risk = Column(Float, default=0.0)
    market_risk = Column(Float, default=0.0)
    regulatory_risk = Column(Float, default=0.0)
    reputation_risk = Column(Float, default=0.0)

    # Overall Assessment
    overall_risk_score = Column(Float, nullable=False)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    confidence_level = Column(Float)  # 0-100

    # Details
    key_risks = Column(JSON, default=list)
    mitigation_strategies = Column(JSON, default=list)
    recommendations = Column(Text)

    # Deal Impact
    deal_recommendation = Column(String(50))  # proceed, proceed_with_conditions, renegotiate, abandon
    conditions = Column(JSON, default=list)
    price_adjustment_recommendation = Column(Float)  # Percentage adjustment

    # Metadata
    methodology = Column(String(100))
    assumptions = Column(JSON, default=dict)
    supporting_documents = Column(JSON, default=list)

    # Indexes
    __table_args__ = (
        Index("ix_risk_assessment_process", "process_id"),
        Index("ix_risk_assessment_level", "risk_level"),
        Index("ix_risk_assessment_date", "assessment_date"),
    )