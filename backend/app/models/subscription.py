"""
Subscription and Payment Models
Database models for Stripe subscriptions, payments, and billing
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    PAUSED = "paused"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"


class PlanTier(str, enum.Enum):
    """Subscription plan tiers"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class StripeCustomer(Base):
    """Stripe customer information linked to Clerk organizations"""
    __tablename__ = "stripe_customers"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String, index=True, nullable=False, unique=True)
    stripe_customer_id = Column(String, index=True, nullable=False, unique=True)
    email = Column(String, nullable=False)
    name = Column(String)

    # Metadata
    metadata = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="customer", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="customer", cascade="all, delete-orphan")


class Subscription(Base):
    """Subscription information for organizations"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String, index=True, nullable=False)
    stripe_subscription_id = Column(String, index=True, nullable=False, unique=True)
    customer_id = Column(Integer, ForeignKey("stripe_customers.id"), nullable=False)

    # Subscription details
    plan_tier = Column(SQLEnum(PlanTier), nullable=False, default=PlanTier.FREE)
    stripe_price_id = Column(String, nullable=False)
    stripe_product_id = Column(String)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.INCOMPLETE)

    # Billing
    amount = Column(Integer, nullable=False)  # Amount in cents
    currency = Column(String, default="usd", nullable=False)
    interval = Column(String, default="month")  # month, year

    # Periods
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    trial_start = Column(DateTime)
    trial_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime)
    ended_at = Column(DateTime)

    # Usage limits (based on plan tier)
    max_deals = Column(Integer, default=10)
    max_users = Column(Integer, default=3)
    max_storage_gb = Column(Integer, default=5)
    ai_credits_per_month = Column(Integer, default=100)

    # Metadata
    metadata = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("StripeCustomer", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")


class Payment(Base):
    """Payment and invoice records"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("stripe_customers.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)

    # Payment details
    stripe_payment_intent_id = Column(String, index=True)
    stripe_invoice_id = Column(String, index=True)
    stripe_charge_id = Column(String)

    # Amount
    amount = Column(Integer, nullable=False)  # Amount in cents
    amount_refunded = Column(Integer, default=0)
    currency = Column(String, default="usd", nullable=False)

    # Status
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)

    # Payment method
    payment_method_type = Column(String)  # card, bank_account, etc.
    payment_method_last4 = Column(String)
    payment_method_brand = Column(String)

    # Metadata
    description = Column(Text)
    metadata = Column(JSON, default={})

    # Timestamps
    paid_at = Column(DateTime)
    refunded_at = Column(DateTime)
    failed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("StripeCustomer", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")


class WebhookEvent(Base):
    """Stripe webhook event log for debugging and auditing"""
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    stripe_event_id = Column(String, index=True, nullable=False, unique=True)
    event_type = Column(String, index=True, nullable=False)

    # Event data
    event_data = Column(JSON, nullable=False)

    # Processing
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)

    # Timestamps
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UsageMetrics(Base):
    """Track usage against subscription limits"""
    __tablename__ = "usage_metrics"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String, index=True, nullable=False)

    # Period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Usage counts
    deals_created = Column(Integer, default=0)
    ai_credits_used = Column(Integer, default=0)
    storage_used_gb = Column(Float, default=0.0)
    api_calls = Column(Integer, default=0)

    # Feature usage
    features_used = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Subscription plan configurations
SUBSCRIPTION_PLANS = {
    PlanTier.FREE: {
        "name": "Free Plan",
        "price": 0,
        "currency": "usd",
        "interval": "month",
        "features": {
            "max_deals": 3,
            "max_users": 1,
            "max_storage_gb": 1,
            "ai_credits_per_month": 50,
            "features": ["basic_deal_management", "limited_ai_insights"]
        }
    },
    PlanTier.STARTER: {
        "name": "Starter Plan",
        "price": 4900,  # $49/month in cents
        "currency": "usd",
        "interval": "month",
        "features": {
            "max_deals": 25,
            "max_users": 5,
            "max_storage_gb": 10,
            "ai_credits_per_month": 500,
            "features": [
                "deal_management",
                "ai_insights",
                "basic_analytics",
                "email_support"
            ]
        }
    },
    PlanTier.PROFESSIONAL: {
        "name": "Professional Plan",
        "price": 14900,  # $149/month in cents
        "currency": "usd",
        "interval": "month",
        "features": {
            "max_deals": 100,
            "max_users": 20,
            "max_storage_gb": 50,
            "ai_credits_per_month": 2000,
            "features": [
                "advanced_deal_management",
                "unlimited_ai_insights",
                "advanced_analytics",
                "workflow_automation",
                "priority_support",
                "api_access"
            ]
        }
    },
    PlanTier.ENTERPRISE: {
        "name": "Enterprise Plan",
        "price": 49900,  # $499/month in cents
        "currency": "usd",
        "interval": "month",
        "features": {
            "max_deals": -1,  # Unlimited
            "max_users": -1,  # Unlimited
            "max_storage_gb": 500,
            "ai_credits_per_month": -1,  # Unlimited
            "features": [
                "enterprise_deal_management",
                "unlimited_everything",
                "custom_integrations",
                "dedicated_support",
                "sla_guarantee",
                "white_label"
            ]
        }
    }
}
