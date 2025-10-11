"""Document model with vector embeddings support"""

from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime,
    ForeignKey, Boolean, JSON, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

from app.core.database import Base


class Document(Base):
    """
    Document model with vector embeddings for semantic search.
    Supports multi-tenant architecture with organization-based isolation.
    """
    __tablename__ = "documents"

    # Primary key and identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Document metadata
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String(50), nullable=False, index=True)  # deal, report, presentation, etc.
    source = Column(String(200))  # Original source or file path
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String(100))

    # Vector embedding for semantic search
    embedding = Column(Vector(1536))  # OpenAI text-embedding-3-small dimension
    embedding_model = Column(String(100), default="text-embedding-3-small")
    embedding_generated_at = Column(DateTime)

    # Extracted entities and metadata
    entities = Column(JSON)  # Extracted entities (companies, people, amounts, etc.)
    doc_metadata = Column(JSON)  # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    tags = Column(JSON)  # User-defined tags

    # Deal/Partnership associations
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=True)
    partnership_id = Column(UUID(as_uuid=True), ForeignKey("partnerships.id"), nullable=True)

    # Search and relevance
    relevance_score = Column(Float)  # Calculated relevance for search results
    view_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)

    # Audit fields
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)

    # Relationships
    organization = relationship("Organization", back_populates="documents")
    owner = relationship("User", back_populates="documents")
    deal = relationship("Deal", back_populates="documents")
    partnership = relationship("Partnership", back_populates="documents")

    # Indexes for performance
    __table_args__ = (
        # Multi-tenant index
        Index("ix_documents_org_type", "organization_id", "document_type"),
        Index("ix_documents_org_created", "organization_id", "created_at"),
        # Vector similarity search index (IVFFlat)
        Index("ix_documents_embedding", "embedding", postgresql_using="ivfflat", postgresql_ops={"embedding": "vector_cosine_ops"}),
        # Full-text search index
        Index("ix_documents_content_search", "title", "content", postgresql_using="gin"),
    )

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, org={self.organization_id})>"