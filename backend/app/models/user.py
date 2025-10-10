"""
User and Role models
Handles user authentication, roles, and organization memberships
"""

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, String, Boolean, Integer, ForeignKey, DateTime,
    UniqueConstraint, CheckConstraint, JSON, Text, Index, Table
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from .base import BaseModel, SoftDeleteMixin, MetadataMixin, AuditableMixin

if TYPE_CHECKING:
    from .organization import Organization
    from .deal import Deal, DealTeamMember
    from .document import Document
    from .activity import ActivityLog


class UserRole(str, Enum):
    """System-wide user roles"""
    SUPER_ADMIN = "super_admin"
    SYSTEM_USER = "system_user"
    API_USER = "api_user"


class OrganizationRole(str, Enum):
    """Organization-specific roles"""
    OWNER = "org:owner"
    ADMIN = "org:admin"
    MANAGER = "org:manager"
    MEMBER = "org:member"
    VIEWER = "org:viewer"


# Many-to-many association table for user permissions
user_permissions = Table(
    'user_permissions',
    BaseModel.metadata,
    Column('user_id', UUID(as_uuid=False), ForeignKey('users.id', ondelete='CASCADE')),
    Column('permission_id', UUID(as_uuid=False), ForeignKey('permissions.id', ondelete='CASCADE')),
    UniqueConstraint('user_id', 'permission_id', name='uq_user_permission')
)


class User(BaseModel, SoftDeleteMixin, MetadataMixin):
    """
    User model
    Maps to Clerk users for authentication
    """
    __tablename__ = 'users'

    # Core fields
    clerk_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Clerk user ID"
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email address"
    )

    username = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
        comment="Username for display"
    )

    # Personal information
    first_name = Column(
        String(100),
        nullable=True,
        comment="First name"
    )

    last_name = Column(
        String(100),
        nullable=True,
        comment="Last name"
    )

    full_name = Column(
        String(255),
        nullable=True,
        comment="Full display name"
    )

    # Profile
    avatar_url = Column(
        String(500),
        nullable=True,
        comment="Profile picture URL"
    )

    phone = Column(
        String(50),
        nullable=True,
        comment="Phone number"
    )

    timezone = Column(
        String(50),
        nullable=False,
        default='UTC',
        comment="User timezone"
    )

    locale = Column(
        String(10),
        nullable=False,
        default='en-US',
        comment="User locale"
    )

    bio = Column(
        Text,
        nullable=True,
        comment="User biography"
    )

    # Professional information
    job_title = Column(
        String(100),
        nullable=True,
        comment="Job title"
    )

    department = Column(
        String(100),
        nullable=True,
        comment="Department"
    )

    linkedin_url = Column(
        String(255),
        nullable=True,
        comment="LinkedIn profile URL"
    )

    # Authentication and security
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Account active status"
    )

    is_email_verified = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Email verification status"
    )

    requires_2fa = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Requires two-factor authentication"
    )

    last_sign_in_at = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="Last sign-in timestamp"
    )

    sign_in_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Total sign-in count"
    )

    # System role (across all organizations)
    system_role = Column(
        String(50),
        nullable=True,
        comment="System-wide role"
    )

    # Preferences
    preferences = Column(
        JSON,
        nullable=True,
        default=dict,
        comment="User preferences and settings"
    )

    # Notification settings
    notification_preferences = Column(
        JSON,
        nullable=True,
        default=lambda: {
            "email": True,
            "sms": False,
            "in_app": True,
            "deal_updates": True,
            "team_mentions": True,
            "weekly_digest": True
        },
        comment="Notification preferences"
    )

    # Relationships
    organization_memberships = relationship(
        "OrganizationMembership",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    permissions = relationship(
        "Permission",
        secondary=user_permissions,
        back_populates="users",
        lazy="dynamic"
    )

    created_documents = relationship(
        "Document",
        foreign_keys="Document.uploaded_by",
        back_populates="uploader",
        lazy="dynamic"
    )

    deal_memberships = relationship(
        "DealTeamMember",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    activity_logs = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # Table constraints
    __table_args__ = (
        Index('ix_users_name_search', 'first_name', 'last_name'),
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'",
                       name='check_email_format'),
    )

    @validates('email')
    def validate_email(self, key, value):
        """Validate email format"""
        if value:
            return value.lower().strip()
        return value

    @validates('timezone')
    def validate_timezone(self, key, value):
        """Validate timezone"""
        import pytz
        if value and value not in pytz.all_timezones:
            raise ValueError(f"Invalid timezone: {value}")
        return value

    @property
    def display_name(self) -> str:
        """Get display name"""
        if self.full_name:
            return self.full_name
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        if self.username:
            return self.username
        return self.email.split('@')[0]

    @property
    def initials(self) -> str:
        """Get user initials"""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.display_name[:2].upper()

    @property
    def organizations(self) -> List['Organization']:
        """Get all organizations user belongs to"""
        return [m.organization for m in self.organization_memberships.filter_by(is_active=True)]

    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission"""
        return self.permissions.filter_by(name=permission_name).first() is not None

    def has_system_role(self, role: UserRole) -> bool:
        """Check if user has a specific system role"""
        return self.system_role == role.value

    def __repr__(self):
        return f"<User {self.email} ({self.id})>"


class OrganizationMembership(BaseModel, SoftDeleteMixin, AuditableMixin):
    """
    Organization membership model
    Links users to organizations with roles
    """
    __tablename__ = 'organization_memberships'

    # Foreign keys
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    organization_id = Column(
        UUID(as_uuid=False),
        ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    clerk_membership_id = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="Clerk membership ID"
    )

    # Role and permissions
    role = Column(
        String(50),
        nullable=False,
        default=OrganizationRole.MEMBER.value,
        comment="Role within organization"
    )

    custom_permissions = Column(
        JSON,
        nullable=True,
        comment="Additional custom permissions"
    )

    # Status
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Membership active status"
    )

    invited_at = Column(
        DateTime,
        nullable=True,
        comment="Invitation sent timestamp"
    )

    joined_at = Column(
        DateTime,
        nullable=True,
        comment="Membership accepted timestamp"
    )

    invited_by = Column(
        UUID(as_uuid=False),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    # Settings
    is_default = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Default organization for user"
    )

    # Relationships
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="organization_memberships"
    )

    organization = relationship(
        "Organization",
        back_populates="memberships"
    )

    inviter = relationship(
        "User",
        foreign_keys=[invited_by]
    )

    # Table constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='uq_user_organization'),
        Index('ix_membership_active', 'organization_id', 'is_active'),
        CheckConstraint(
            f"role IN ('{OrganizationRole.OWNER.value}', '{OrganizationRole.ADMIN.value}', "
            f"'{OrganizationRole.MANAGER.value}', '{OrganizationRole.MEMBER.value}', "
            f"'{OrganizationRole.VIEWER.value}')",
            name='check_valid_role'
        ),
    )

    def has_role(self, role: OrganizationRole) -> bool:
        """Check if membership has specific role"""
        return self.role == role.value

    def can_manage_team(self) -> bool:
        """Check if user can manage team members"""
        return self.role in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value,
                             OrganizationRole.MANAGER.value]

    def can_manage_deals(self) -> bool:
        """Check if user can manage deals"""
        return self.role != OrganizationRole.VIEWER.value

    def can_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]

    def __repr__(self):
        return f"<OrganizationMembership {self.user_id} in {self.organization_id} as {self.role}>"


class Permission(BaseModel):
    """
    Permission model for fine-grained access control
    """
    __tablename__ = 'permissions'

    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Permission name"
    )

    category = Column(
        String(50),
        nullable=False,
        comment="Permission category"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Permission description"
    )

    # Relationships
    users = relationship(
        "User",
        secondary=user_permissions,
        back_populates="permissions"
    )

    def __repr__(self):
        return f"<Permission {self.name}>"


class UserSession(BaseModel):
    """
    User session tracking for audit and security
    """
    __tablename__ = 'user_sessions'

    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    session_token = Column(
        String(500),
        unique=True,
        nullable=False,
        index=True,
        comment="Session token"
    )

    ip_address = Column(
        String(45),
        nullable=True,
        comment="Client IP address"
    )

    user_agent = Column(
        String(500),
        nullable=True,
        comment="User agent string"
    )

    device_info = Column(
        JSON,
        nullable=True,
        comment="Device information"
    )

    started_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Session start time"
    )

    last_activity_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Last activity timestamp"
    )

    ended_at = Column(
        DateTime,
        nullable=True,
        comment="Session end time"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Session active status"
    )

    # Relationships
    user = relationship("User")

    def end_session(self):
        """End the session"""
        self.is_active = False
        self.ended_at = datetime.utcnow()

    def __repr__(self):
        return f"<UserSession {self.user_id} - {self.started_at}>"