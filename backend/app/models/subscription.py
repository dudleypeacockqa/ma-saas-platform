"""
Subscription models for Clerk integration
Handles subscription plans, billing, and feature access
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, String, Integer, Boolean, ForeignKey, DateTime,
    Numeric, JSON, Text, CheckConstraint, Float
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from .base import BaseModel, SoftDeleteMixin, MetadataMixin


class SubscriptionStatus(str, Enum):
    """Subscription status values"""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAUSED = "paused"


class SubscriptionPlan(str, Enum):
    """Available subscription plans"""
    SOLO = "solo"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


class BillingInterval(str, Enum):
    """Billing intervals"""
    MONTHLY = "month"
    YEARLY = "year"


class Subscription(BaseModel, SoftDeleteMixin, MetadataMixin):
    """
    Subscription model
    Tracks organization subscriptions and billing
    """
    __tablename__ = 'subscriptions'

    # Organization relationship
    organization_id = Column(
        UUID(as_uuid=False),
        ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Organization this subscription belongs to"
    )

    # Clerk subscription details
    clerk_subscription_id = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="Clerk subscription ID"
    )

    clerk_customer_id = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Clerk customer ID"
    )

    # Plan details
    plan = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Subscription plan"
    )

    plan_name = Column(
        String(100),
        nullable=False,
        comment="Human-readable plan name"
    )

    billing_interval = Column(
        String(20),
        nullable=False,
        default=BillingInterval.MONTHLY.value,
        comment="Billing frequency"
    )

    # Pricing
    amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Subscription amount"
    )

    currency = Column(
        String(3),
        nullable=False,
        default='USD',
        comment="Currency code"
    )

    # Status and dates
    status = Column(
        String(50),
        nullable=False,
        default=SubscriptionStatus.INCOMPLETE.value,
        index=True,
        comment="Current subscription status"
    )

    current_period_start = Column(
        DateTime,
        nullable=True,
        comment="Current billing period start"
    )

    current_period_end = Column(
        DateTime,
        nullable=True,
        comment="Current billing period end"
    )

    trial_start = Column(
        DateTime,
        nullable=True,
        comment="Trial period start"
    )

    trial_end = Column(
        DateTime,
        nullable=True,
        comment="Trial period end"
    )

    canceled_at = Column(
        DateTime,
        nullable=True,
        comment="Cancellation timestamp"
    )

    ended_at = Column(
        DateTime,
        nullable=True,
        comment="Subscription end timestamp"
    )

    # Feature limits based on plan
    max_users = Column(
        Integer,
        nullable=False,
        default=5,
        comment="Maximum users allowed"
    )

    max_deals = Column(
        Integer,
        nullable=True,
        comment="Maximum active deals (null = unlimited)"
    )

    storage_quota_gb = Column(
        Numeric(10, 2),
        nullable=False,
        default=10.0,
        comment="Storage quota in GB"
    )

    api_requests_per_month = Column(
        Integer,
        nullable=True,
        comment="API request limit per month"
    )

    # Feature flags
    features = Column(
        JSON,
        nullable=True,
        default=dict,
        comment="Enabled features for this plan"
    )

    # Billing information
    next_billing_date = Column(
        DateTime,
        nullable=True,
        comment="Next billing date"
    )

    last_payment_date = Column(
        DateTime,
        nullable=True,
        comment="Last successful payment"
    )

    payment_method_id = Column(
        String(255),
        nullable=True,
        comment="Payment method identifier"
    )

    # Discount and promotions
    discount_percent = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Discount percentage"
    )

    discount_amount = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Fixed discount amount"
    )

    coupon_code = Column(
        String(100),
        nullable=True,
        comment="Applied coupon code"
    )

    # Relationships
    organization = relationship(
        "Organization",
        back_populates="subscriptions"
    )

    invoices = relationship(
        "Invoice",
        back_populates="subscription",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    usage_records = relationship(
        "UsageRecord",
        back_populates="subscription",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint('amount >= 0', name='check_amount_non_negative'),
        CheckConstraint('max_users >= 1', name='check_max_users_positive'),
        CheckConstraint('storage_quota_gb >= 0', name='check_storage_quota_non_negative'),
        CheckConstraint(
            'discount_percent IS NULL OR (discount_percent >= 0 AND discount_percent <= 100)',
            name='check_discount_percent_valid'
        ),
    )

    @validates('plan')
    def validate_plan(self, key, value):
        """Validate subscription plan"""
        valid_plans = [plan.value for plan in SubscriptionPlan]
        if value not in valid_plans:
            raise ValueError(f"Invalid plan: {value}. Must be one of {valid_plans}")
        return value

    @validates('status')
    def validate_status(self, key, value):
        """Validate subscription status"""
        valid_statuses = [status.value for status in SubscriptionStatus]
        if value not in valid_statuses:
            raise ValueError(f"Invalid status: {value}. Must be one of {valid_statuses}")
        return value

    @validates('billing_interval')
    def validate_billing_interval(self, key, value):
        """Validate billing interval"""
        valid_intervals = [interval.value for interval in BillingInterval]
        if value not in valid_intervals:
            raise ValueError(f"Invalid billing interval: {value}. Must be one of {valid_intervals}")
        return value

    @property
    def is_active(self) -> bool:
        """Check if subscription is active"""
        return self.status in [SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIALING.value]

    @property
    def is_trial(self) -> bool:
        """Check if subscription is in trial"""
        return self.status == SubscriptionStatus.TRIALING.value

    @property
    def days_until_renewal(self) -> Optional[int]:
        """Calculate days until next renewal"""
        if not self.current_period_end:
            return None
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)

    @property
    def is_past_due(self) -> bool:
        """Check if subscription is past due"""
        return self.status == SubscriptionStatus.PAST_DUE.value

    def get_feature(self, feature_name: str, default: Any = False) -> Any:
        """Get feature flag value"""
        if not self.features:
            return default
        return self.features.get(feature_name, default)

    def has_feature(self, feature_name: str) -> bool:
        """Check if feature is enabled"""
        return bool(self.get_feature(feature_name, False))

    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel the subscription"""
        self.status = SubscriptionStatus.CANCELED.value
        self.canceled_at = datetime.utcnow()
        if reason:
            self.set_metadata('cancellation_reason', reason)

    def reactivate(self) -> None:
        """Reactivate a canceled subscription"""
        self.status = SubscriptionStatus.ACTIVE.value
        self.canceled_at = None
        self.ended_at = None

    @classmethod
    def get_plan_config(cls, plan: str) -> Dict[str, Any]:
        """Get configuration for a subscription plan"""
        configs = {
            SubscriptionPlan.SOLO.value: {
                'name': 'Solo Dealmaker',
                'monthly_price': 279,
                'yearly_price': 2790,  # 10% discount
                'max_users': 3,
                'max_deals': 10,
                'storage_quota_gb': 50,
                'api_requests_per_month': 10000,
                'features': {
                    'deal_management': True,
                    'document_storage': True,
                    'basic_analytics': True,
                    'email_support': True,
                    'ai_insights': False,
                    'advanced_analytics': False,
                    'priority_support': False,
                    'custom_integrations': False,
                }
            },
            SubscriptionPlan.GROWTH.value: {
                'name': 'Growth Firm',
                'monthly_price': 798,
                'yearly_price': 7980,  # 10% discount
                'max_users': 15,
                'max_deals': 50,
                'storage_quota_gb': 200,
                'api_requests_per_month': 50000,
                'features': {
                    'deal_management': True,
                    'document_storage': True,
                    'basic_analytics': True,
                    'email_support': True,
                    'ai_insights': True,
                    'advanced_analytics': True,
                    'priority_support': True,
                    'custom_integrations': False,
                    'team_collaboration': True,
                    'workflow_automation': True,
                }
            },
            SubscriptionPlan.ENTERPRISE.value: {
                'name': 'Enterprise',
                'monthly_price': 1598,
                'yearly_price': 15980,  # 10% discount
                'max_users': None,  # Unlimited
                'max_deals': None,  # Unlimited
                'storage_quota_gb': 1000,
                'api_requests_per_month': None,  # Unlimited
                'features': {
                    'deal_management': True,
                    'document_storage': True,
                    'basic_analytics': True,
                    'email_support': True,
                    'ai_insights': True,
                    'advanced_analytics': True,
                    'priority_support': True,
                    'custom_integrations': True,
                    'team_collaboration': True,
                    'workflow_automation': True,
                    'white_labeling': True,
                    'dedicated_support': True,
                    'sso_integration': True,
                    'audit_logs': True,
                }
            }
        }
        return configs.get(plan, {})

    def __repr__(self):
        return f"<Subscription {self.plan} for {self.organization_id} ({self.status})>"


class Invoice(BaseModel, SoftDeleteMixin):
    """
    Invoice model
    Tracks billing history
    """
    __tablename__ = 'invoices'

    # Subscription relationship
    subscription_id = Column(
        UUID(as_uuid=False),
        ForeignKey('subscriptions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Invoice details
    clerk_invoice_id = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="Clerk invoice ID"
    )

    invoice_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Invoice number"
    )

    # Amounts
    subtotal = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Subtotal amount"
    )

    tax_amount = Column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="Tax amount"
    )

    discount_amount = Column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="Discount amount"
    )

    total_amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Total amount"
    )

    currency = Column(
        String(3),
        nullable=False,
        default='USD'
    )

    # Dates
    invoice_date = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    due_date = Column(
        DateTime,
        nullable=True
    )

    paid_at = Column(
        DateTime,
        nullable=True
    )

    # Status
    status = Column(
        String(50),
        nullable=False,
        default='draft',
        index=True
    )

    # Billing period
    period_start = Column(
        DateTime,
        nullable=True
    )

    period_end = Column(
        DateTime,
        nullable=True
    )

    # Additional data
    line_items = Column(
        JSON,
        nullable=True,
        comment="Invoice line items"
    )

    payment_details = Column(
        JSON,
        nullable=True,
        comment="Payment method and transaction details"
    )

    # Relationships
    subscription = relationship(
        "Subscription",
        back_populates="invoices"
    )

    @property
    def is_paid(self) -> bool:
        """Check if invoice is paid"""
        return self.status == 'paid' and self.paid_at is not None

    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue"""
        if not self.due_date or self.is_paid:
            return False
        return datetime.utcnow() > self.due_date

    def __repr__(self):
        return f"<Invoice {self.invoice_number} ({self.status})>"


class UsageRecord(BaseModel):
    """
    Usage tracking for metered billing
    """
    __tablename__ = 'usage_records'

    # Subscription relationship
    subscription_id = Column(
        UUID(as_uuid=False),
        ForeignKey('subscriptions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Usage details
    metric_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Usage metric name (e.g., 'api_requests', 'storage_gb')"
    )

    quantity = Column(
        Numeric(15, 4),
        nullable=False,
        comment="Usage quantity"
    )

    unit = Column(
        String(50),
        nullable=True,
        comment="Unit of measurement"
    )

    # Time period
    usage_date = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    billing_period_start = Column(
        DateTime,
        nullable=False,
        index=True
    )

    billing_period_end = Column(
        DateTime,
        nullable=False,
        index=True
    )

    # Additional context
    resource_id = Column(
        String(255),
        nullable=True,
        comment="ID of the resource that generated usage"
    )

    metadata_json = Column(
        JSON,
        nullable=True,
        comment="Additional usage metadata"
    )

    # Relationships
    subscription = relationship(
        "Subscription",
        back_populates="usage_records"
    )

    def __repr__(self):
        return f"<UsageRecord {self.metric_name}: {self.quantity} on {self.usage_date}>"
