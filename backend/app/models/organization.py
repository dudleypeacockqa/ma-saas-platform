"""
Organization and Tenant models
Maps to Clerk organizations and handles multi-tenancy
"""

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Boolean, ForeignKey, DateTime,
    UniqueConstraint, CheckConstraint, JSON, Text, Numeric
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from .base import BaseModel, SoftDeleteMixin, MetadataMixin, generate_uuid

if TYPE_CHECKING:
    from .user import User, OrganizationMembership
    from .deal import Deal
    from .subscription import Subscription


class Organization(BaseModel, SoftDeleteMixin, MetadataMixin):
    """
    Organization/Tenant model
    Maps to Clerk organizations for authentication
    """
    __tablename__ = 'organizations'

    # Core fields
    clerk_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Clerk organization ID"
    )

    name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Organization name"
    )

    slug = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
        comment="URL-friendly identifier"
    )

    # Organization details
    industry = Column(
        String(100),
        nullable=True,
        comment="Industry sector"
    )

    company_size = Column(
        String(50),
        nullable=True,
        comment="Company size category"
    )

    website = Column(
        String(255),
        nullable=True,
        comment="Company website"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Organization description"
    )

    # Contact information
    primary_contact_email = Column(
        String(255),
        nullable=True,
        comment="Primary contact email"
    )

    primary_contact_name = Column(
        String(255),
        nullable=True,
        comment="Primary contact person"
    )

    phone = Column(
        String(50),
        nullable=True,
        comment="Contact phone number"
    )

    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(2), nullable=True, comment="ISO country code")

    # Settings and configuration
    settings = Column(
        JSON,
        nullable=True,
        default=dict,
        comment="Organization-specific settings"
    )

    features = Column(
        JSON,
        nullable=True,
        default=dict,
        comment="Enabled features and limits"
    )

    # Subscription and limits
    subscription_tier = Column(
        String(50),
        nullable=False,
        default='free',
        comment="Current subscription tier"
    )

    max_users = Column(
        Integer,
        nullable=False,
        default=5,
        comment="Maximum allowed users"
    )

    max_deals = Column(
        Integer,
        nullable=True,
        comment="Maximum allowed active deals"
    )

    storage_quota_gb = Column(
        Numeric(10, 2),
        nullable=False,
        default=10.0,
        comment="Storage quota in GB"
    )

    storage_used_gb = Column(
        Numeric(10, 2),
        nullable=False,
        default=0.0,
        comment="Current storage usage in GB"
    )

    # Compliance and security
    data_retention_days = Column(
        Integer,
        nullable=False,
        default=365,
        comment="Data retention period in days"
    )

    is_verified = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Email/domain verification status"
    )

    requires_2fa = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Require 2FA for all users"
    )

    allowed_domains = Column(
        JSON,
        nullable=True,
        comment="List of allowed email domains for auto-join"
    )

    # Status
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Organization active status"
    )

    suspended_at = Column(
        DateTime,
        nullable=True,
        comment="Suspension timestamp"
    )

    suspended_reason = Column(
        Text,
        nullable=True,
        comment="Reason for suspension"
    )

    # Trial information
    trial_ends_at = Column(
        DateTime,
        nullable=True,
        comment="Trial expiration date"
    )

    # Relationships
    memberships = relationship(
        "OrganizationMembership",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    deals = relationship(
        "Deal",
        back_populates="organization",
        foreign_keys="Deal.organization_id",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    documents = relationship(
        "Document",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    subscriptions = relationship(
        "Subscription",
        back_populates="organization",
        order_by="desc(Subscription.created_at)",
        lazy="dynamic"
    )


    # Table constraints
    __table_args__ = (
        CheckConstraint('max_users >= 1', name='check_max_users_positive'),
        CheckConstraint('storage_quota_gb >= storage_used_gb', name='check_storage_within_quota'),
        CheckConstraint('storage_used_gb >= 0', name='check_storage_non_negative'),
    )

    @validates('slug')
    def validate_slug(self, key, value):
        """Validate slug format"""
        if value and not value.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Slug must contain only letters, numbers, hyphens, and underscores")
        return value.lower() if value else value

    @validates('country')
    def validate_country(self, key, value):
        """Validate country code"""
        if value and len(value) != 2:
            raise ValueError("Country must be a 2-letter ISO code")
        return value.upper() if value else value

    @property
    def is_on_trial(self) -> bool:
        """Check if organization is on trial"""
        if not self.trial_ends_at:
            return False
        return datetime.utcnow() < self.trial_ends_at

    @property
    def storage_used_percentage(self) -> float:
        """Calculate storage usage percentage"""
        if self.storage_quota_gb == 0:
            return 0.0
        return float((self.storage_used_gb / self.storage_quota_gb) * 100)

    @property
    def member_count(self) -> int:
        """Get current member count"""
        return self.memberships.filter_by(is_active=True).count()

    @property
    def is_at_user_limit(self) -> bool:
        """Check if organization has reached user limit"""
        return self.member_count >= self.max_users

    def can_add_user(self) -> bool:
        """Check if organization can add more users"""
        return not self.is_at_user_limit and self.is_active

    def suspend(self, reason: str) -> None:
        """Suspend the organization"""
        self.is_active = False
        self.suspended_at = datetime.utcnow()
        self.suspended_reason = reason

    def reactivate(self) -> None:
        """Reactivate a suspended organization"""
        self.is_active = True
        self.suspended_at = None
        self.suspended_reason = None

    def __repr__(self):
        return f"<Organization {self.name} ({self.id})>"


class OrganizationSettings(BaseModel):
    """
    Organization-specific settings
    Stores configuration that doesn't fit in the main model
    """
    __tablename__ = 'organization_settings'

    organization_id = Column(
        UUID(as_uuid=False),
        ForeignKey('organizations.id', ondelete='CASCADE'),
        unique=True,
        nullable=False,
        index=True
    )

    # Deal settings
    deal_approval_required = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Require approval for new deals"
    )

    deal_auto_numbering = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Auto-generate deal numbers"
    )

    deal_number_prefix = Column(
        String(10),
        nullable=True,
        comment="Prefix for deal numbers"
    )

    deal_stages = Column(
        JSON,
        nullable=True,
        comment="Custom deal pipeline stages"
    )

    # Notification settings
    notification_emails = Column(
        JSON,
        nullable=True,
        comment="List of emails for notifications"
    )

    webhook_url = Column(
        String(500),
        nullable=True,
        comment="Webhook URL for events"
    )

    slack_webhook = Column(
        String(500),
        nullable=True,
        comment="Slack integration webhook"
    )

    # Branding
    logo_url = Column(
        String(500),
        nullable=True,
        comment="Organization logo URL"
    )

    brand_color = Column(
        String(7),
        nullable=True,
        comment="Brand color hex code"
    )

    # Integrations
    integrations = Column(
        JSON,
        nullable=True,
        default=dict,
        comment="Third-party integration settings"
    )

    # Relationships
    organization = relationship(
        "Organization",
        back_populates="settings_record",
        uselist=False
    )


# Add relationship to Organization model
Organization.settings_record = relationship(
    "OrganizationSettings",
    back_populates="organization",
    uselist=False,
    cascade="all, delete-orphan"
)