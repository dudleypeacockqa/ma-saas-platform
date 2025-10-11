"""
Document model for file storage and management
Story 3.1: Document Upload API - Database model
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date,
    Text, JSON, ForeignKey, Enum, Index, CheckConstraint, UUID as UUID_TYPE
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
import enum

from app.models.base import Base


class DocumentType(str, enum.Enum):
    """Types of documents in M&A deals"""
    NDA = "nda"
    LOI = "loi"
    TERM_SHEET = "term_sheet"
    DUE_DILIGENCE = "due_diligence"
    FINANCIAL_STATEMENT = "financial_statement"
    LEGAL_DOCUMENT = "legal_document"
    PRESENTATION = "presentation"
    REPORT = "report"
    CONTRACT = "contract"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    """Document status"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    AVAILABLE = "available"
    ARCHIVED = "archived"
    DELETED = "deleted"
    FAILED = "failed"


class Document(Base):
    """
    Document model for storing deal-related files
    Supports versioning, folders, and access control
    """
    __tablename__ = "documents"

    # Primary key
    id = Column(UUID_TYPE(as_uuid=True), primary_key=True, default=uuid4)

    # Multi-tenancy
    organization_id = Column(UUID_TYPE(as_uuid=True), nullable=False, index=True)

    # Document metadata
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_extension = Column(String(10), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes

    # S3 storage information
    s3_bucket = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=False, unique=True)
    s3_url = Column(Text, nullable=True)
    s3_etag = Column(String(255), nullable=True)

    # Document classification
    document_type = Column(Enum(DocumentType), default=DocumentType.OTHER, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADING, nullable=False)

    # Folder organization
    folder_path = Column(String(500), default="/", nullable=False)
    parent_folder_id = Column(UUID_TYPE(as_uuid=True), nullable=True)

    # Relationships
    deal_id = Column(UUID_TYPE(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=True, index=True)
    uploaded_by = Column(UUID_TYPE(as_uuid=True), nullable=False)

    # Versioning
    version = Column(Integer, default=1, nullable=False)
    parent_document_id = Column(UUID_TYPE(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    is_latest_version = Column(Boolean, default=True, nullable=False)

    # Security
    is_confidential = Column(Boolean, default=True, nullable=False)
    is_encrypted = Column(Boolean, default=True, nullable=False)
    encryption_key_id = Column(String(255), nullable=True)

    # Access control
    access_level = Column(String(50), default="private", nullable=False)  # private, team, organization
    allowed_users = Column(JSON, default=list)  # List of user IDs with access
    allowed_roles = Column(JSON, default=list)  # List of roles with access

    # Document metadata
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)  # Additional metadata like page count, author, etc.

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    accessed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    download_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    last_accessed_by = Column(UUID_TYPE(as_uuid=True), nullable=True)

    # Relationships
    deal = relationship("Deal", back_populates="documents")
    versions = relationship("Document", backref="parent_document", remote_side=[id])

    # Indexes for performance
    __table_args__ = (
        Index('idx_documents_organization_deal', 'organization_id', 'deal_id'),
        Index('idx_documents_folder_path', 'organization_id', 'folder_path'),
        Index('idx_documents_type_status', 'document_type', 'status'),
        Index('idx_documents_uploaded_by', 'uploaded_by'),
        CheckConstraint('file_size > 0', name='check_positive_file_size'),
        CheckConstraint('version > 0', name='check_positive_version'),
    )

    def __repr__(self):
        return f"<Document {self.filename} ({self.id})>"

    def to_dict(self):
        """Convert document to dictionary"""
        return {
            'id': str(self.id),
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_extension': self.file_extension,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'document_type': self.document_type.value if self.document_type else None,
            'status': self.status.value if self.status else None,
            'folder_path': self.folder_path,
            'deal_id': str(self.deal_id) if self.deal_id else None,
            'version': self.version,
            'is_latest_version': self.is_latest_version,
            'is_confidential': self.is_confidential,
            'title': self.title,
            'description': self.description,
            'tags': self.tags,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
            'download_count': self.download_count,
            'view_count': self.view_count,
        }


class DocumentFolder(Base):
    """
    Folder structure for organizing documents
    """
    __tablename__ = "document_folders"

    # Primary key
    id = Column(UUID_TYPE(as_uuid=True), primary_key=True, default=uuid4)

    # Multi-tenancy
    organization_id = Column(UUID_TYPE(as_uuid=True), nullable=False, index=True)

    # Folder information
    name = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False, unique=True)
    parent_id = Column(UUID_TYPE(as_uuid=True), ForeignKey("document_folders.id"), nullable=True)

    # Relationships
    deal_id = Column(UUID_TYPE(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=True, index=True)
    created_by = Column(UUID_TYPE(as_uuid=True), nullable=False)

    # Metadata
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color for UI
    icon = Column(String(50), nullable=True)  # Icon name for UI

    # Permissions
    is_system_folder = Column(Boolean, default=False, nullable=False)
    is_readonly = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Statistics
    document_count = Column(Integer, default=0, nullable=False)
    total_size = Column(Integer, default=0, nullable=False)  # Total size in bytes

    # Relationships
    subfolders = relationship("DocumentFolder", backref="parent_folder", remote_side=[id])

    # Indexes
    __table_args__ = (
        Index('idx_folders_organization_path', 'organization_id', 'path'),
        Index('idx_folders_deal', 'deal_id'),
    )

    def __repr__(self):
        return f"<DocumentFolder {self.name} ({self.path})>"