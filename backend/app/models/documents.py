"""
Document Management Models for M&A SaaS Platform
Advanced document handling with versioning, approvals, and e-signature integration
"""

import enum
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, String, Text, Integer, Numeric, Date, DateTime, Boolean,
    ForeignKey, Enum, JSON, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, validates

from .base import TenantModel, AuditableMixin


class DocumentCategory(enum.Enum):
    """Document categories for organization"""
    TERM_SHEET = "term_sheet"
    LOI = "loi"
    NDA = "nda"
    PURCHASE_AGREEMENT = "purchase_agreement"
    DISCLOSURE_SCHEDULE = "disclosure_schedule"
    EMPLOYMENT_AGREEMENT = "employment_agreement"
    ESCROW_AGREEMENT = "escrow_agreement"
    FINANCING_DOCUMENT = "financing_document"
    REGULATORY_FILING = "regulatory_filing"
    DUE_DILIGENCE = "due_diligence"
    LEGAL_OPINION = "legal_opinion"
    VALUATION_REPORT = "valuation_report"
    OTHER = "other"


class DocumentStatus(enum.Enum):
    """Document lifecycle status"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    READY_FOR_SIGNATURE = "ready_for_signature"
    IN_SIGNATURE = "in_signature"
    PARTIALLY_SIGNED = "partially_signed"
    FULLY_EXECUTED = "fully_executed"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class ApprovalStatus(enum.Enum):
    """Individual approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"
    EXPIRED = "expired"


class SignatureStatus(enum.Enum):
    """E-signature status"""
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class AccessLevel(enum.Enum):
    """Document access levels"""
    PUBLIC = "public"
    TEAM = "team"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    TOP_SECRET = "top_secret"


class Document(TenantModel, AuditableMixin):
    """
    Enhanced document model with versioning and workflow support
    """
    __tablename__ = "documents"

    # Basic Information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(Enum(DocumentCategory), nullable=False, index=True)
    document_type = Column(String(100), comment="Specific document type within category")

    # Relationships
    negotiation_id = Column(UUID(as_uuid=False), ForeignKey("negotiations.id"), index=True)
    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id"), index=True)
    term_sheet_id = Column(UUID(as_uuid=False), ForeignKey("term_sheets.id"), index=True)

    # File Information
    file_name = Column(String(255), nullable=False)
    original_file_name = Column(String(255))
    file_path = Column(String(1000), comment="Storage path")
    file_url = Column(String(1000), comment="Access URL")
    file_size = Column(Integer, comment="Size in bytes")
    mime_type = Column(String(100))
    file_hash = Column(String(64), comment="SHA-256 hash for integrity")

    # Version Control
    version_number = Column(Integer, default=1, nullable=False)
    is_current_version = Column(Boolean, default=True, index=True)
    parent_document_id = Column(UUID(as_uuid=False), ForeignKey("documents.id"))
    version_notes = Column(Text, comment="Changes in this version")

    # Status and Workflow
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT, index=True)
    workflow_stage = Column(String(100), comment="Current workflow stage")
    requires_approval = Column(Boolean, default=False)
    requires_signature = Column(Boolean, default=False)

    # Access Control
    access_level = Column(Enum(AccessLevel), default=AccessLevel.TEAM, index=True)
    is_confidential = Column(Boolean, default=True)
    viewer_restrictions = Column(JSON, default=dict, comment="Specific viewer permissions")

    # Important Dates
    effective_date = Column(Date)
    expiration_date = Column(Date)
    due_date = Column(Date, comment="When document action is due")

    # Content Analysis
    page_count = Column(Integer)
    word_count = Column(Integer)
    key_terms_extracted = Column(JSON, default=list, comment="AI-extracted key terms")
    content_summary = Column(Text, comment="AI-generated summary")

    # Metadata and Tags
    tags = Column(ARRAY(String(50)), default=list, index=True)
    custom_metadata = Column(JSON, default=dict)
    external_references = Column(JSON, default=list, comment="References to external documents")

    # Tracking
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    last_viewed_date = Column(DateTime)
    last_downloaded_date = Column(DateTime)

    # Relationships
    negotiation = relationship("Negotiation", backref="documents")
    deal = relationship("Deal", backref="related_documents")
    term_sheet = relationship("TermSheet", backref="related_documents")
    parent_document = relationship("Document", remote_side="Document.id", backref="versions")
    approvals = relationship("DocumentApproval", back_populates="document", lazy="dynamic")
    signatures = relationship("DocumentSignature", back_populates="document", lazy="dynamic")
    activities = relationship("DocumentActivity", back_populates="document", lazy="dynamic")

    # Organization relationship
    organization = relationship("Organization", back_populates="documents")

    __table_args__ = (
        Index('ix_documents_negotiation_category', 'negotiation_id', 'category'),
        Index('ix_documents_deal_category', 'deal_id', 'category'),
        Index('ix_documents_term_sheet_category', 'term_sheet_id', 'category'),
        Index('ix_documents_version', 'parent_document_id', 'version_number'),
        Index('ix_documents_status', 'status'),
        Index('ix_documents_access_level', 'access_level'),
        Index('ix_documents_due_date', 'due_date'),
    )

    @property
    def is_current(self) -> bool:
        """Check if this is the current version"""
        return self.is_current_version

    @property
    def is_overdue(self) -> bool:
        """Check if document action is overdue"""
        if not self.due_date:
            return False
        return datetime.utcnow().date() > self.due_date

    @property
    def total_versions(self) -> int:
        """Get total number of versions for this document"""
        if self.parent_document_id:
            return len(self.parent_document.versions) + 1
        return len(self.versions) + 1


class DocumentApproval(TenantModel, AuditableMixin):
    """Document approval workflow tracking"""
    __tablename__ = "document_approvals"

    document_id = Column(UUID(as_uuid=False), ForeignKey("documents.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    approver_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    # Approval Details
    approval_level = Column(Integer, default=1, comment="Order in approval sequence")
    role_required = Column(String(100), comment="Required role for approval")
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True)

    # Dates
    requested_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime)
    response_date = Column(DateTime)

    # Response
    comments = Column(Text)
    conditions = Column(Text, comment="Conditions for approval")
    rejection_reason = Column(Text)

    # Delegation
    delegated_to_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    delegation_reason = Column(Text)

    # Notification
    reminder_sent_count = Column(Integer, default=0)
    last_reminder_date = Column(DateTime)

    # Relationships
    document = relationship("Document", back_populates="approvals")
    approver = relationship("User", foreign_keys=[approver_id], backref="document_approvals")
    delegated_to = relationship("User", foreign_keys=[delegated_to_id])

    __table_args__ = (
        Index('ix_document_approvals_status', 'status'),
        Index('ix_document_approvals_due_date', 'due_date'),
        Index('ix_document_approvals_level', 'approval_level'),
    )

    @property
    def is_overdue(self) -> bool:
        """Check if approval is overdue"""
        if self.status != ApprovalStatus.PENDING or not self.due_date:
            return False
        return datetime.utcnow() > self.due_date

    @property
    def days_pending(self) -> int:
        """Calculate days since approval was requested"""
        if self.response_date:
            return (self.response_date.date() - self.requested_date.date()).days
        return (datetime.utcnow().date() - self.requested_date.date()).days


class DocumentSignature(TenantModel, AuditableMixin):
    """E-signature tracking for documents"""
    __tablename__ = "document_signatures"

    document_id = Column(UUID(as_uuid=False), ForeignKey("documents.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    signer_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Signer Information
    signer_name = Column(String(255), nullable=False)
    signer_email = Column(String(255), nullable=False)
    signer_title = Column(String(200))
    signer_company = Column(String(255))
    signer_role = Column(String(100), comment="buyer, seller, witness, etc.")

    # Signature Details
    signature_order = Column(Integer, default=1, comment="Order in signing sequence")
    status = Column(Enum(SignatureStatus), default=SignatureStatus.PENDING, index=True)

    # E-signature Platform Integration
    external_signature_id = Column(String(200), comment="ID from e-signature platform")
    signature_platform = Column(String(50), comment="DocuSign, HelloSign, etc.")
    signature_url = Column(String(1000), comment="Signing URL")

    # Dates
    sent_date = Column(DateTime)
    viewed_date = Column(DateTime)
    signed_date = Column(DateTime)
    declined_date = Column(DateTime)
    expiry_date = Column(DateTime)

    # Signature Verification
    signature_hash = Column(String(128), comment="Hash of signed document")
    ip_address = Column(String(45), comment="IP address when signed")
    authentication_method = Column(String(100), comment="SMS, email, etc.")
    certificate_id = Column(String(200), comment="Digital certificate ID")

    # Communication
    reminder_count = Column(Integer, default=0)
    last_reminder_date = Column(DateTime)
    decline_reason = Column(Text)

    # Relationships
    document = relationship("Document", back_populates="signatures")
    signer = relationship("User", backref="document_signatures")

    __table_args__ = (
        Index('ix_document_signatures_status', 'status'),
        Index('ix_document_signatures_order', 'signature_order'),
        Index('ix_document_signatures_sent_date', 'sent_date'),
    )

    @property
    def is_overdue(self) -> bool:
        """Check if signature is overdue"""
        if self.status not in [SignatureStatus.PENDING, SignatureStatus.IN_PROGRESS]:
            return False
        if not self.expiry_date:
            return False
        return datetime.utcnow() > self.expiry_date

    @property
    def days_pending(self) -> int:
        """Calculate days since signature was requested"""
        if not self.sent_date:
            return 0
        end_date = self.signed_date or datetime.utcnow()
        return (end_date.date() - self.sent_date.date()).days


class DocumentActivity(TenantModel, AuditableMixin):
    """Activity log for document interactions"""
    __tablename__ = "document_activities"

    document_id = Column(UUID(as_uuid=False), ForeignKey("documents.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Activity Details
    activity_type = Column(String(50), nullable=False, index=True,
                          comment="created, viewed, downloaded, approved, signed, etc.")
    activity_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    description = Column(Text)
    details = Column(JSON, default=dict, comment="Additional activity details")

    # Context
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    session_id = Column(String(100))

    # Relationships
    document = relationship("Document", back_populates="activities")
    user = relationship("User", backref="document_activities")

    __table_args__ = (
        Index('ix_document_activities_type', 'activity_type'),
        Index('ix_document_activities_date', 'activity_date'),
        Index('ix_document_activities_user', 'user_id'),
    )


class DocumentTemplate(TenantModel, AuditableMixin):
    """Templates for generating standard documents"""
    __tablename__ = "document_templates"

    # Template Information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(Enum(DocumentCategory), nullable=False, index=True)
    document_type = Column(String(100))

    # Template Content
    template_content = Column(Text, nullable=False, comment="Template with merge fields")
    merge_fields = Column(JSON, default=list, comment="Available merge field definitions")
    default_values = Column(JSON, default=dict, comment="Default values for fields")

    # Template Properties
    is_active = Column(Boolean, default=True, index=True)
    is_public = Column(Boolean, default=False, comment="Available to all organizations")
    version = Column(String(20), default="1.0")

    # Usage Tracking
    usage_count = Column(Integer, default=0)
    last_used_date = Column(DateTime)

    # Workflow Configuration
    default_approval_workflow = Column(JSON, default=list, comment="Default approval steps")
    default_signature_workflow = Column(JSON, default=list, comment="Default signature steps")
    requires_approval = Column(Boolean, default=False)
    requires_signature = Column(Boolean, default=False)

    # Metadata
    tags = Column(ARRAY(String(50)), default=list)
    industry = Column(String(100))
    jurisdiction = Column(String(100), comment="Legal jurisdiction for template")

    __table_args__ = (
        Index('ix_document_templates_category_active', 'category', 'is_active'),
        Index('ix_document_templates_industry', 'industry'),
        Index('ix_document_templates_public', 'is_public'),
    )


class DocumentComparison(TenantModel, AuditableMixin):
    """Document comparison and redlining results"""
    __tablename__ = "document_comparisons"

    # Documents being compared
    original_document_id = Column(UUID(as_uuid=False), ForeignKey("documents.id"), nullable=False)
    revised_document_id = Column(UUID(as_uuid=False), ForeignKey("documents.id"), nullable=False)

    # Comparison Details
    comparison_type = Column(String(50), default="version", comment="version, redline, contract")
    comparison_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Results
    changes_detected = Column(Boolean, default=False)
    change_count = Column(Integer, default=0)
    changes_summary = Column(Text)
    detailed_changes = Column(JSON, default=list, comment="Detailed change analysis")

    # Statistics
    additions_count = Column(Integer, default=0)
    deletions_count = Column(Integer, default=0)
    modifications_count = Column(Integer, default=0)
    formatting_changes_count = Column(Integer, default=0)

    # Generated Output
    redline_document_url = Column(String(1000), comment="URL to redlined version")
    comparison_report_url = Column(String(1000), comment="URL to comparison report")

    # Relationships
    original_document = relationship("Document", foreign_keys=[original_document_id])
    revised_document = relationship("Document", foreign_keys=[revised_document_id])

    __table_args__ = (
        Index('ix_document_comparisons_original', 'original_document_id'),
        Index('ix_document_comparisons_revised', 'revised_document_id'),
        Index('ix_document_comparisons_date', 'comparison_date'),
    )