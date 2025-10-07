"""
Prospect and Lead Management Models
Handles subscriber acquisition, lead scoring, and conversion tracking
"""
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, JSON, Enum as SQLEnum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
from app.models.base import BaseModel, UUIDPrimaryKeyMixin, TimestampMixin

class ProspectSource(str, enum.Enum):
    """Source of prospect acquisition"""
    LINKEDIN = "linkedin"
    WEBSITE = "website"
    REFERRAL = "referral"
    PODCAST = "podcast"
    CONTENT = "content"
    WEBINAR = "webinar"
    PAID_AD = "paid_ad"
    ORGANIC_SEARCH = "organic_search"
    EMAIL_CAMPAIGN = "email_campaign"
    PARTNER = "partner"
    MANUAL = "manual"

class ProspectStatus(str, enum.Enum):
    """Prospect lifecycle status"""
    NEW = "new"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    QUALIFIED = "qualified"
    TRIAL = "trial"
    CUSTOMER = "customer"
    LOST = "lost"
    UNSUBSCRIBED = "unsubscribed"
    BLACKLISTED = "blacklisted"

class LeadScore(str, enum.Enum):
    """Lead quality scoring"""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    UNQUALIFIED = "unqualified"

class IndustrySegment(str, enum.Enum):
    """Target industry segments"""
    PRIVATE_EQUITY = "private_equity"
    INVESTMENT_BANKING = "investment_banking"
    CORPORATE_DEVELOPMENT = "corporate_development"
    BUSINESS_BROKER = "business_broker"
    ADVISORY_FIRM = "advisory_firm"
    VENTURE_CAPITAL = "venture_capital"
    FAMILY_OFFICE = "family_office"
    SEARCH_FUND = "search_fund"
    OTHER = "other"

class Prospect(BaseModel, UUIDPrimaryKeyMixin, TimestampMixin):
    """Prospect information and tracking"""
    __tablename__ = "prospects"

    # Contact Information
    email = Column(String(255), nullable=False, unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    title = Column(String(200))
    company = Column(String(200))
    company_size = Column(String(50))  # 1-10, 11-50, 51-200, 201-500, 500+
    industry_segment = Column(SQLEnum(IndustrySegment))
    phone = Column(String(50))
    timezone = Column(String(50))

    # LinkedIn Information
    linkedin_url = Column(String(500))
    linkedin_id = Column(String(100), unique=True, sparse=True)
    linkedin_connections = Column(Integer)
    linkedin_headline = Column(String(500))
    linkedin_summary = Column(Text)

    # Lead Qualification
    status = Column(SQLEnum(ProspectStatus), default=ProspectStatus.NEW)
    lead_score = Column(Float, default=0.0)
    lead_grade = Column(SQLEnum(LeadScore), default=LeadScore.COLD)
    qualification_notes = Column(Text)
    ideal_customer_profile_match = Column(Float)  # 0-100 percentage

    # Acquisition Information
    source = Column(SQLEnum(ProspectSource), nullable=False)
    source_detail = Column(String(500))  # Specific campaign, referrer, etc.
    acquisition_date = Column(DateTime, default=datetime.utcnow)
    acquisition_channel = Column(String(100))
    acquisition_campaign = Column(String(200))
    acquisition_cost = Column(Float, default=0.0)

    # Engagement Metrics
    website_visits = Column(Integer, default=0)
    page_views = Column(Integer, default=0)
    content_downloads = Column(Integer, default=0)
    email_opens = Column(Integer, default=0)
    email_clicks = Column(Integer, default=0)
    last_activity_date = Column(DateTime)
    engagement_score = Column(Float, default=0.0)

    # Preferences
    contact_preferences = Column(JSON, default=dict)  # email, linkedin, phone
    content_interests = Column(JSON, default=list)  # Topics of interest
    product_interests = Column(JSON, default=list)  # Specific features/tiers

    # Compliance
    gdpr_consent = Column(Boolean, default=False)
    gdpr_consent_date = Column(DateTime)
    marketing_consent = Column(Boolean, default=True)
    do_not_contact = Column(Boolean, default=False)
    unsubscribe_date = Column(DateTime)
    unsubscribe_reason = Column(Text)

    # Conversion Tracking
    trial_start_date = Column(DateTime)
    trial_end_date = Column(DateTime)
    conversion_date = Column(DateTime)
    customer_id = Column(String(100))  # Reference to customer record
    lifetime_value = Column(Float, default=0.0)

    # Custom Fields
    tags = Column(JSON, default=list)
    custom_fields = Column(JSON, default=dict)
    notes = Column(Text)

    # Relationships
    outreach_attempts = relationship("OutreachAttempt", back_populates="prospect")
    activities = relationship("ProspectActivity", back_populates="prospect")
    campaigns = relationship("CampaignProspect", back_populates="prospect")

    # Indexes
    __table_args__ = (
        Index('ix_prospect_email', 'email'),
        Index('ix_prospect_status', 'status'),
        Index('ix_prospect_lead_score', 'lead_score'),
        Index('ix_prospect_source', 'source'),
        Index('ix_prospect_company', 'company'),
    )

class OutreachAttempt(BaseModel, UUIDPrimaryKeyMixin, TimestampMixin):
    """Track outreach attempts to prospects"""
    __tablename__ = "outreach_attempts"

    # Foreign Keys
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("outreach_campaigns.id"))

    # Outreach Details
    channel = Column(String(50), nullable=False)  # email, linkedin, phone
    attempt_number = Column(Integer, default=1)
    message_template_id = Column(String(100))
    personalized_message = Column(Text)
    subject_line = Column(String(500))

    # Status
    status = Column(String(50), default="pending")  # pending, sent, delivered, opened, clicked, replied
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    replied_at = Column(DateTime)
    bounced = Column(Boolean, default=False)
    bounce_reason = Column(String(500))

    # Response
    response_received = Column(Boolean, default=False)
    response_sentiment = Column(String(50))  # positive, neutral, negative
    response_text = Column(Text)
    requires_follow_up = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)

    # Metrics
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)

    # Relationships
    prospect = relationship("Prospect", back_populates="outreach_attempts")
    campaign = relationship("OutreachCampaign", back_populates="attempts")

    # Indexes
    __table_args__ = (
        Index('ix_outreach_prospect', 'prospect_id'),
        Index('ix_outreach_campaign', 'campaign_id'),
        Index('ix_outreach_status', 'status'),
        Index('ix_outreach_sent_at', 'sent_at'),
    )

class OutreachCampaign(BaseModel, UUIDPrimaryKeyMixin, TimestampMixin):
    """Automated outreach campaigns"""
    __tablename__ = "outreach_campaigns"

    # Campaign Information
    name = Column(String(200), nullable=False)
    description = Column(Text)
    campaign_type = Column(String(50))  # cold_outreach, nurture, trial_conversion
    status = Column(String(50), default="draft")  # draft, active, paused, completed

    # Target Criteria
    target_segment = Column(SQLEnum(IndustrySegment))
    target_criteria = Column(JSON)  # Complex filtering criteria
    target_count = Column(Integer, default=0)

    # Campaign Settings
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    daily_limit = Column(Integer, default=50)
    total_limit = Column(Integer)

    # Message Templates
    templates = Column(JSON, default=list)  # List of template configurations
    personalization_rules = Column(JSON, default=dict)
    follow_up_sequence = Column(JSON, default=list)

    # Performance Metrics
    prospects_contacted = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    reply_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)

    # A/B Testing
    ab_test_enabled = Column(Boolean, default=False)
    ab_test_variants = Column(JSON, default=list)
    winning_variant = Column(String(100))

    # Budget
    budget_allocated = Column(Float, default=0.0)
    budget_spent = Column(Float, default=0.0)
    cost_per_acquisition = Column(Float, default=0.0)

    # Compliance
    compliance_checked = Column(Boolean, default=False)
    gdpr_compliant = Column(Boolean, default=True)
    can_spam_compliant = Column(Boolean, default=True)

    # Relationships
    attempts = relationship("OutreachAttempt", back_populates="campaign")
    prospects = relationship("CampaignProspect", back_populates="campaign")

    # Indexes
    __table_args__ = (
        Index('ix_campaign_status', 'status'),
        Index('ix_campaign_start_date', 'start_date'),
    )

class CampaignProspect(BaseModel, UUIDPrimaryKeyMixin):
    """Many-to-many relationship between campaigns and prospects"""
    __tablename__ = "campaign_prospects"

    campaign_id = Column(UUID(as_uuid=True), ForeignKey("outreach_campaigns.id"), nullable=False)
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.id"), nullable=False)

    added_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")
    last_contact_date = Column(DateTime)
    next_contact_date = Column(DateTime)

    # Relationships
    campaign = relationship("OutreachCampaign", back_populates="prospects")
    prospect = relationship("Prospect", back_populates="campaigns")

    # Constraints
    __table_args__ = (
        UniqueConstraint('campaign_id', 'prospect_id', name='uq_campaign_prospect'),
        Index('ix_campaign_prospect_campaign', 'campaign_id'),
        Index('ix_campaign_prospect_prospect', 'prospect_id'),
    )

class ProspectActivity(BaseModel, UUIDPrimaryKeyMixin, TimestampMixin):
    """Track all prospect activities and interactions"""
    __tablename__ = "prospect_activities"

    # Foreign Keys
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.id"), nullable=False)

    # Activity Information
    activity_type = Column(String(50), nullable=False)  # website_visit, email_open, link_click, form_submit
    activity_detail = Column(String(500))
    page_url = Column(String(500))
    referrer_url = Column(String(500))

    # Session Information
    session_id = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    device_type = Column(String(50))
    browser = Column(String(50))

    # Engagement Metrics
    duration_seconds = Column(Integer)
    pages_viewed = Column(Integer)
    actions_taken = Column(JSON, default=list)

    # Lead Scoring Impact
    score_impact = Column(Float, default=0.0)
    score_reason = Column(String(200))

    # Relationships
    prospect = relationship("Prospect", back_populates="activities")

    # Indexes
    __table_args__ = (
        Index('ix_activity_prospect', 'prospect_id'),
        Index('ix_activity_type', 'activity_type'),
        Index('ix_activity_created', 'created_at'),
    )

class MessageTemplate(BaseModel, UUIDPrimaryKeyMixin, TimestampMixin):
    """Reusable message templates for outreach"""
    __tablename__ = "message_templates"

    # Template Information
    name = Column(String(200), nullable=False)
    channel = Column(String(50), nullable=False)  # email, linkedin
    template_type = Column(String(50))  # initial, follow_up, nurture

    # Content
    subject_line = Column(String(500))
    body_template = Column(Text, nullable=False)
    personalization_tokens = Column(JSON, default=list)  # Available merge fields

    # Performance
    usage_count = Column(Integer, default=0)
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    reply_rate = Column(Float, default=0.0)

    # Settings
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(100))
    approved_date = Column(DateTime)

    # A/B Testing
    is_variant = Column(Boolean, default=False)
    parent_template_id = Column(UUID(as_uuid=True), ForeignKey("message_templates.id"))
    variant_name = Column(String(100))

    # Compliance
    compliance_reviewed = Column(Boolean, default=False)
    compliance_notes = Column(Text)

    # Indexes
    __table_args__ = (
        Index('ix_template_channel', 'channel'),
        Index('ix_template_type', 'template_type'),
        Index('ix_template_active', 'is_active'),
    )