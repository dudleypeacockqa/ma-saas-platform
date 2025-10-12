"""
Subscription Management Models
Advanced subscription and billing management for M&A SaaS platform
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

from app.models.base import Base

# ============================================================================
# ENUMS
# ============================================================================

class SubscriptionStatus(enum.Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"

class BillingCycle(enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"

class DiscountType(enum.Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

# ============================================================================
# SUBSCRIPTION PLAN MODELS
# ============================================================================

class SubscriptionPlan(Base):
    """Subscription plan definitions"""
    __tablename__ = "subscription_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Pricing
    monthly_price = Column(Float, nullable=False)
    quarterly_price = Column(Float)  # Optional quarterly pricing
    annual_price = Column(Float)     # Optional annual pricing
    
    # Features
    max_deals = Column(Integer)  # null = unlimited
    max_users = Column(Integer)  # null = unlimited
    max_storage_gb = Column(Integer)  # null = unlimited
    features = Column(JSON)  # List of feature flags
    
    # Plan metadata
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    stripe_price_id_monthly = Column(String(100))
    stripe_price_id_quarterly = Column(String(100))
    stripe_price_id_annual = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")

class Subscription(Base):
    """Customer subscriptions"""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    
    # Subscription details
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.TRIAL)
    billing_cycle = Column(Enum(BillingCycle), nullable=False, default=BillingCycle.MONTHLY)
    
    # Pricing
    monthly_amount = Column(Float, nullable=False)  # Actual amount being charged
    currency = Column(String(3), default="GBP")
    
    # Trial information
    trial_start_date = Column(DateTime)
    trial_end_date = Column(DateTime)
    
    # Billing dates
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    next_billing_date = Column(DateTime)
    
    # Cancellation
    cancelled_at = Column(DateTime)
    cancellation_reason = Column(String(500))
    cancel_at_period_end = Column(Boolean, default=False)
    
    # Stripe integration
    stripe_subscription_id = Column(String(100), unique=True)
    stripe_customer_id = Column(String(100))
    
    # Metadata
    metadata = Column(JSON)  # Additional subscription data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="subscription")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")
    usage_records = relationship("UsageRecord", back_populates="subscription")

# ============================================================================
# PROMOTIONAL CODE MODELS
# ============================================================================

class PromotionalCode(Base):
    """Promotional codes and discounts"""
    __tablename__ = "promotional_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True, index=True)
    
    # Discount details
    discount_type = Column(Enum(DiscountType), nullable=False)
    discount_value = Column(Float, nullable=False)  # Percentage (0-100) or fixed amount
    
    # Usage limits
    max_uses = Column(Integer)  # null = unlimited
    uses_count = Column(Integer, default=0)
    max_uses_per_customer = Column(Integer, default=1)
    
    # Validity
    start_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)
    
    # Applicable plans
    applicable_plans = Column(JSON)  # List of plan IDs, null = all plans
    
    # Metadata
    description = Column(String(500))
    internal_notes = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Stripe integration
    stripe_coupon_id = Column(String(100))
    
    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    usages = relationship("PromoCodeUsage", back_populates="promo_code")

class PromoCodeUsage(Base):
    """Track promotional code usage"""
    __tablename__ = "promo_code_usages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    promo_code_id = Column(UUID(as_uuid=True), ForeignKey("promotional_codes.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"))
    
    # Usage details
    discount_amount = Column(Float, nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow)
    
    # Stripe integration
    stripe_discount_id = Column(String(100))

    # Relationships
    promo_code = relationship("PromotionalCode", back_populates="usages")
    organization = relationship("Organization")
    subscription = relationship("Subscription")

# ============================================================================
# PAYMENT MODELS
# ============================================================================

class Payment(Base):
    """Payment records"""
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="GBP")
    status = Column(Enum(PaymentStatus), nullable=False)
    
    # Payment method
    payment_method_type = Column(String(50))  # card, bank_transfer, etc.
    last_four = Column(String(4))  # Last 4 digits of card
    brand = Column(String(20))  # visa, mastercard, etc.
    
    # Dates
    payment_date = Column(DateTime)
    due_date = Column(DateTime)
    
    # Stripe integration
    stripe_payment_intent_id = Column(String(100), unique=True)
    stripe_charge_id = Column(String(100))
    
    # Failure information
    failure_code = Column(String(50))
    failure_message = Column(String(500))
    
    # Metadata
    description = Column(String(500))
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription", back_populates="payments")

class PaymentMethod(Base):
    """Stored payment methods"""
    __tablename__ = "payment_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Payment method details
    type = Column(String(50), nullable=False)  # card, bank_account, etc.
    last_four = Column(String(4))
    brand = Column(String(20))  # visa, mastercard, etc.
    exp_month = Column(Integer)
    exp_year = Column(Integer)
    
    # Status
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Stripe integration
    stripe_payment_method_id = Column(String(100), unique=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")

# ============================================================================
# USAGE TRACKING MODELS
# ============================================================================

class UsageRecord(Base):
    """Track subscription usage for billing"""
    __tablename__ = "usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    
    # Usage metrics
    metric_name = Column(String(100), nullable=False)  # deals_created, users_added, etc.
    quantity = Column(Integer, nullable=False)
    
    # Time period
    usage_date = Column(DateTime, nullable=False)
    billing_period_start = Column(DateTime, nullable=False)
    billing_period_end = Column(DateTime, nullable=False)
    
    # Metadata
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription", back_populates="usage_records")

# ============================================================================
# BILLING MODELS
# ============================================================================

class Invoice(Base):
    """Generated invoices"""
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    
    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False)
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0)
    currency = Column(String(3), default="GBP")
    
    # Status
    status = Column(String(20), nullable=False)  # draft, open, paid, void, uncollectible
    
    # Dates
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    paid_at = Column(DateTime)
    
    # Period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Stripe integration
    stripe_invoice_id = Column(String(100), unique=True)
    
    # Invoice content
    line_items = Column(JSON)  # Invoice line items
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription")

class BillingAlert(Base):
    """Billing alerts and notifications"""
    __tablename__ = "billing_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # payment_failed, trial_ending, etc.
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Message
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Metadata
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription")

# ============================================================================
# CUSTOMER SUCCESS MODELS
# ============================================================================

class CustomerHealthScore(Base):
    """Customer health and success metrics"""
    __tablename__ = "customer_health_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Health metrics
    overall_score = Column(Integer, nullable=False)  # 0-100
    usage_score = Column(Integer, nullable=False)    # 0-100
    engagement_score = Column(Integer, nullable=False)  # 0-100
    support_score = Column(Integer, nullable=False)  # 0-100
    
    # Risk indicators
    churn_risk = Column(String(20), nullable=False)  # low, medium, high
    expansion_opportunity = Column(String(20), nullable=False)  # low, medium, high
    
    # Calculated metrics
    days_since_last_login = Column(Integer)
    feature_adoption_rate = Column(Float)  # 0-1
    support_tickets_count = Column(Integer, default=0)
    
    # Metadata
    calculation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")

class SubscriptionEvent(Base):
    """Track subscription lifecycle events"""
    __tablename__ = "subscription_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # created, upgraded, downgraded, cancelled, etc.
    event_data = Column(JSON)  # Additional event data
    
    # User context
    triggered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription")
    user = relationship("User")
