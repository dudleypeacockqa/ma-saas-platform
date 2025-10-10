"""
Base models and mixins for the M&A SaaS platform
Provides common functionality for all database models
"""

import uuid
from datetime import datetime
from typing import Any, Optional
from sqlalchemy import Column, String, DateTime, Boolean, Index, event, JSON, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session

Base = declarative_base()


def generate_uuid() -> str:
    """Generate a UUID string for primary keys"""
    return str(uuid.uuid4())


class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps"""

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        index=True
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality"""

    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True, index=True)
    deleted_by = Column(UUID(as_uuid=False), nullable=True)

    def soft_delete(self, deleted_by_id: Optional[str] = None) -> None:
        """Mark the record as deleted"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        if deleted_by_id:
            self.deleted_by = deleted_by_id

    def restore(self) -> None:
        """Restore a soft-deleted record"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None


class TenantMixin:
    """Mixin for tenant isolation"""

    @declared_attr
    def organization_id(cls):
        return Column(
            UUID(as_uuid=False),
            nullable=False,
            index=True
        )


class UUIDPrimaryKeyMixin:
    """Mixin for UUID primary keys"""

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        default=generate_uuid,
        nullable=False
    )


class BaseModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Base model with UUID primary key and timestamps"""
    __abstract__ = True

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result

    def update(self, **kwargs) -> None:
        """Update model attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class TenantModel(BaseModel, TenantMixin, SoftDeleteMixin):
    """Base model for tenant-scoped entities"""
    __abstract__ = True

    @declared_attr
    def __table_args__(cls):
        """Add composite indexes for tenant queries"""
        if hasattr(cls, '__tablename__'):
            return (
                Index(f'ix_{cls.__tablename__}_org_id_created', 'organization_id', 'created_at'),
                Index(f'ix_{cls.__tablename__}_org_id_deleted', 'organization_id', 'is_deleted'),
            )
        return tuple()


class AuditableMixin:
    """Mixin for tracking who created/modified records"""

    @declared_attr
    def created_by(cls):
        return Column(UUID(as_uuid=False), nullable=True, index=True)

    @declared_attr
    def updated_by(cls):
        return Column(UUID(as_uuid=False), nullable=True, index=True)


class MetadataMixin:
    """Mixin for storing arbitrary JSON metadata"""

    metadata_json = Column(
        JSON,
        nullable=True,
        default=dict,
        comment="Flexible JSON storage for additional data"
    )

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value by key"""
        if self.metadata_json is None:
            return default
        return self.metadata_json.get(key, default)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value"""
        if self.metadata_json is None:
            self.metadata_json = {}
        self.metadata_json[key] = value

    def update_metadata(self, data: dict) -> None:
        """Update multiple metadata values"""
        if self.metadata_json is None:
            self.metadata_json = {}
        self.metadata_json.update(data)


class SearchableMixin:
    """Mixin for full-text search support"""

    search_vector = Column(
        TSVECTOR,
        nullable=True,
        comment="Full-text search vector"
    )

    @declared_attr
    def __table_args__(cls):
        """Add GIN index for full-text search"""
        return (
            Index(
                f'ix_{cls.__tablename__}_search',
                'search_vector',
                postgresql_using='gin'
            ),
        )


class VersionedMixin:
    """Mixin for optimistic locking with version numbers"""

    version = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Version number for optimistic locking"
    )

    def increment_version(self) -> None:
        """Increment the version number"""
        self.version = (self.version or 0) + 1


# Event listeners for automatic functionality
@event.listens_for(TimestampMixin, 'before_update', propagate=True)
def receive_before_update(mapper, connection, target):
    """Automatically update updated_at timestamp"""
    target.updated_at = datetime.utcnow()


@event.listens_for(VersionedMixin, 'before_update', propagate=True)
def increment_version_on_update(mapper, connection, target):
    """Automatically increment version on update"""
    if hasattr(target, 'version'):
        target.increment_version()


# Utility functions for tenant isolation
def apply_tenant_filter(query, model_class, organization_id: str):
    """Apply tenant filter to a query"""
    if hasattr(model_class, 'organization_id'):
        return query.filter(model_class.organization_id == organization_id)
    return query


def apply_soft_delete_filter(query, model_class, include_deleted: bool = False):
    """Apply soft delete filter to a query"""
    if not include_deleted and hasattr(model_class, 'is_deleted'):
        return query.filter(model_class.is_deleted == False)
    return query


class TenantScopedSession:
    """Session wrapper that automatically applies tenant filters"""

    def __init__(self, session: Session, organization_id: str):
        self.session = session
        self.organization_id = organization_id

    def query(self, model_class):
        """Create a query with automatic tenant filtering"""
        query = self.session.query(model_class)
        query = apply_tenant_filter(query, model_class, self.organization_id)
        query = apply_soft_delete_filter(query, model_class)
        return query

    def add(self, instance):
        """Add an instance with automatic tenant assignment"""
        if hasattr(instance, 'organization_id') and not instance.organization_id:
            instance.organization_id = self.organization_id
        return self.session.add(instance)

    def commit(self):
        """Commit the session"""
        return self.session.commit()

    def rollback(self):
        """Rollback the session"""
        return self.session.rollback()

    def close(self):
        """Close the session"""
        return self.session.close()