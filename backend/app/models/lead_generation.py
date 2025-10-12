"""
Lead Generation and Marketing Automation Models
Advanced lead scoring, multi-channel campaigns, and automated nurture sequences
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

class LeadSource(enum.Enum):
    WEBSITE = "website"
    CONTENT_DOWNLOAD = "content_download"
    WEBINAR = "webinar"
    EVENT = "event"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    REFERRAL = "referral"
    PAID_ADS = "paid_ads"
    ORGANIC_SEARCH = "organic_search"
    DIRECT = "direct"
    PARTNER = "partner"
    COLD_OUTREACH = "cold_outreach"

class LeadStatus(enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    OPPORTUNITY = "opportunity"
    CUSTOMER = "customer"
    LOST = "lost"
    NURTURING = "nurturing"
    UNQUALIFIED = "unqualified"

class LeadQuality(enum.Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"

class CampaignType(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    CONTENT_MARKETING = "content_marketing"
    PAID_ADS = "paid_ads"
    WEBINAR = "webinar"
    EVENT = "event"
    DIRECT_MAIL = "direct_mail"
    RETARGETING = "retargeting"

class CampaignStatus(enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AutomationTrigger(enum.Enum):
    FORM_SUBMISSION = "form_submission"
    EMAIL_OPEN = "email_open"
    EMAIL_CLICK = "email_click"
    WEBSITE_VISIT = "website_visit"
    CONTENT_DOWNLOAD = "content_download"
    EVENT_REGISTRATION = "event_registration"
    SCORING_THRESHOLD = "scoring_threshold"
    TIME_DELAY = "time_delay"
    BEHAVIOR_TRIGGER = "behavior_trigger"

class EmailStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    UNSUBSCRIBED = "unsubscribed"
    COMPLAINED = "complained"

# ============================================================================
# LEAD MODELS
# ============================================================================

class Lead(Base):
    """Main lead model with comprehensive tracking"""
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50))
    company = Column(String(200))
    job_title = Column(String(200))
    industry = Column(String(100))
    company_size = Column(String(50))
    annual_revenue = Column(String(50))
    
    # Lead qualification
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    quality = Column(Enum(LeadQuality), default=LeadQuality.COLD)
    lead_score = Column(Integer, default=0)
    qualification_notes = Column(Text)
    
    # Source tracking
    source = Column(Enum(LeadSource), nullable=False)
    source_details = Column(String(200))  # Specific campaign, page, etc.
    utm_campaign = Column(String(100))
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_content = Column(String(100))
    utm_term = Column(String(100))
    
    # Geographic information
    country = Column(String(100))
    city = Column(String(100))
    region = Column(String(100))
    ip_address = Column(String(45))
    
    # Behavioral data
    website_visits = Column(Integer, default=0)
    page_views = Column(Integer, default=0)
    content_downloads = Column(Integer, default=0)
    email_opens = Column(Integer, default=0)
    email_clicks = Column(Integer, default=0)
    event_registrations = Column(Integer, default=0)
    
    # Engagement metrics
    first_touch_date = Column(DateTime, default=datetime.utcnow)
    last_activity_date = Column(DateTime, default=datetime.utcnow)
    total_engagement_score = Column(Float, default=0.0)
    days_since_last_activity = Column(Integer, default=0)
    
    # Interest and needs
    interested_products = Column(JSON)  # List of products/services
    pain_points = Column(JSON)  # List of pain points
    budget_range = Column(String(50))
    timeline = Column(String(50))
    decision_maker = Column(Boolean, default=False)
    buying_stage = Column(String(50))  # awareness, consideration, decision
    
    # Sales information
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    next_follow_up = Column(DateTime)
    last_contact_date = Column(DateTime)
    contact_attempts = Column(Integer, default=0)
    
    # Conversion tracking
    converted_to_customer = Column(Boolean, default=False)
    conversion_date = Column(DateTime)
    conversion_value = Column(Float)
    
    # CRM integration
    crm_contact_id = Column(String(100))
    crm_sync_status = Column(String(50), default="pending")
    crm_last_sync = Column(DateTime)
    
    # Custom fields
    custom_fields = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_user = relationship("User")
    activities = relationship("LeadActivity", back_populates="lead")
    scoring_history = relationship("LeadScoringHistory", back_populates="lead")
    campaign_interactions = relationship("CampaignInteraction", back_populates="lead")
    automation_enrollments = relationship("AutomationEnrollment", back_populates="lead")

# ============================================================================
# LEAD ACTIVITY TRACKING
# ============================================================================

class LeadActivity(Base):
    """Track all lead activities and interactions"""
    __tablename__ = "lead_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    
    # Activity details
    activity_type = Column(String(50), nullable=False)  # email_open, website_visit, form_submit, etc.
    activity_description = Column(Text)
    activity_data = Column(JSON)  # Additional activity-specific data
    
    # Context
    source_campaign_id = Column(UUID(as_uuid=True), ForeignKey("marketing_campaigns.id"))
    source_email_id = Column(UUID(as_uuid=True), ForeignKey("email_campaigns.id"))
    
    # Scoring impact
    score_change = Column(Integer, default=0)
    
    # Timestamps
    activity_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lead = relationship("Lead", back_populates="activities")
    source_campaign = relationship("MarketingCampaign")
    source_email = relationship("EmailCampaign")

# ============================================================================
# LEAD SCORING MODELS
# ============================================================================

class LeadScoringRule(Base):
    """Lead scoring rules and criteria"""
    __tablename__ = "lead_scoring_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Rule details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # demographic, behavioral, engagement
    
    # Scoring criteria
    criteria = Column(JSON, nullable=False)  # Conditions for scoring
    score_value = Column(Integer, nullable=False)
    is_recurring = Column(Boolean, default=False)  # Can score multiple times
    max_score = Column(Integer)  # Maximum score from this rule
    
    # Rule settings
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    creator = relationship("User")

class LeadScoringHistory(Base):
    """Track lead scoring changes over time"""
    __tablename__ = "lead_scoring_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    scoring_rule_id = Column(UUID(as_uuid=True), ForeignKey("lead_scoring_rules.id"))
    
    # Scoring details
    previous_score = Column(Integer, default=0)
    score_change = Column(Integer, nullable=False)
    new_score = Column(Integer, nullable=False)
    reason = Column(String(200))
    
    # Context
    activity_id = Column(UUID(as_uuid=True), ForeignKey("lead_activities.id"))
    
    # Timestamps
    scored_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lead = relationship("Lead", back_populates="scoring_history")
    scoring_rule = relationship("LeadScoringRule")
    activity = relationship("LeadActivity")

# ============================================================================
# MARKETING CAMPAIGN MODELS
# ============================================================================

class MarketingCampaign(Base):
    """Marketing campaigns and initiatives"""
    __tablename__ = "marketing_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Campaign details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    campaign_type = Column(Enum(CampaignType), nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Targeting
    target_audience = Column(JSON)  # Audience criteria
    audience_size = Column(Integer)
    
    # Scheduling
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    timezone = Column(String(50), default="Europe/London")
    
    # Budget and goals
    budget = Column(Float, default=0.0)
    cost_per_lead_target = Column(Float)
    lead_target = Column(Integer)
    conversion_target = Column(Integer)
    
    # Content
    creative_assets = Column(JSON)  # Images, videos, copy
    landing_page_url = Column(String(500))
    call_to_action = Column(String(200))
    
    # Tracking
    utm_campaign = Column(String(100))
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_content = Column(String(100))
    
    # Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    leads_generated = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Calculated metrics
    click_through_rate = Column(Float, default=0.0)
    cost_per_click = Column(Float, default=0.0)
    cost_per_lead = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    
    # Settings
    auto_optimize = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    creator = relationship("User")
    interactions = relationship("CampaignInteraction", back_populates="campaign")
    email_campaigns = relationship("EmailCampaign", back_populates="parent_campaign")

# ============================================================================
# EMAIL CAMPAIGN MODELS
# ============================================================================

class EmailCampaign(Base):
    """Email marketing campaigns"""
    __tablename__ = "email_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_campaign_id = Column(UUID(as_uuid=True), ForeignKey("marketing_campaigns.id"))
    
    # Email details
    name = Column(String(200), nullable=False)
    subject_line = Column(String(300), nullable=False)
    preview_text = Column(String(200))
    from_name = Column(String(100), nullable=False)
    from_email = Column(String(255), nullable=False)
    reply_to = Column(String(255))
    
    # Content
    html_content = Column(Text)
    text_content = Column(Text)
    template_id = Column(String(100))
    
    # Targeting
    recipient_list_id = Column(UUID(as_uuid=True), ForeignKey("email_lists.id"))
    audience_filters = Column(JSON)  # Additional filtering criteria
    
    # Scheduling
    send_type = Column(String(50), default="immediate")  # immediate, scheduled, triggered
    scheduled_send_date = Column(DateTime)
    timezone = Column(String(50), default="Europe/London")
    
    # A/B Testing
    is_ab_test = Column(Boolean, default=False)
    ab_test_percentage = Column(Integer, default=50)
    ab_test_winner_criteria = Column(String(50))  # open_rate, click_rate, conversion
    
    # Performance metrics
    recipients_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    bounced_count = Column(Integer, default=0)
    unsubscribed_count = Column(Integer, default=0)
    complained_count = Column(Integer, default=0)
    
    # Calculated rates
    delivery_rate = Column(Float, default=0.0)
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    bounce_rate = Column(Float, default=0.0)
    unsubscribe_rate = Column(Float, default=0.0)
    
    # Status
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    sent_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    parent_campaign = relationship("MarketingCampaign", back_populates="email_campaigns")
    recipient_list = relationship("EmailList")
    creator = relationship("User")
    email_sends = relationship("EmailSend", back_populates="email_campaign")

# ============================================================================
# EMAIL LIST MODELS
# ============================================================================

class EmailList(Base):
    """Email subscriber lists"""
    __tablename__ = "email_lists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # List details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # List criteria
    is_dynamic = Column(Boolean, default=False)
    criteria = Column(JSON)  # Dynamic list criteria
    
    # Statistics
    subscriber_count = Column(Integer, default=0)
    active_subscriber_count = Column(Integer, default=0)
    
    # Settings
    double_opt_in = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    creator = relationship("User")
    subscriptions = relationship("EmailSubscription", back_populates="email_list")

class EmailSubscription(Base):
    """Email list subscriptions"""
    __tablename__ = "email_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_list_id = Column(UUID(as_uuid=True), ForeignKey("email_lists.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    
    # Subscription details
    email = Column(String(255), nullable=False)
    status = Column(String(50), default="subscribed")  # subscribed, unsubscribed, bounced
    
    # Subscription tracking
    subscribed_date = Column(DateTime, default=datetime.utcnow)
    unsubscribed_date = Column(DateTime)
    source = Column(String(100))  # How they subscribed
    
    # Preferences
    preferences = Column(JSON)  # Email preferences
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    email_list = relationship("EmailList", back_populates="subscriptions")
    lead = relationship("Lead")

class EmailSend(Base):
    """Individual email sends and tracking"""
    __tablename__ = "email_sends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_campaign_id = Column(UUID(as_uuid=True), ForeignKey("email_campaigns.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    
    # Send details
    recipient_email = Column(String(255), nullable=False)
    status = Column(Enum(EmailStatus), default=EmailStatus.PENDING)
    
    # Delivery tracking
    sent_date = Column(DateTime)
    delivered_date = Column(DateTime)
    opened_date = Column(DateTime)
    first_click_date = Column(DateTime)
    
    # Engagement tracking
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    
    # Error tracking
    bounce_type = Column(String(50))  # hard, soft
    bounce_reason = Column(String(200))
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    email_campaign = relationship("EmailCampaign", back_populates="email_sends")
    lead = relationship("Lead")

# ============================================================================
# MARKETING AUTOMATION MODELS
# ============================================================================

class MarketingAutomation(Base):
    """Marketing automation workflows"""
    __tablename__ = "marketing_automations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Automation details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Trigger configuration
    trigger_type = Column(Enum(AutomationTrigger), nullable=False)
    trigger_criteria = Column(JSON, nullable=False)
    
    # Workflow configuration
    workflow_steps = Column(JSON, nullable=False)  # Sequence of actions
    
    # Targeting
    target_criteria = Column(JSON)  # Who can enter this automation
    
    # Settings
    is_active = Column(Boolean, default=True)
    max_enrollments = Column(Integer)  # Limit enrollments
    allow_re_enrollment = Column(Boolean, default=False)
    
    # Performance metrics
    total_enrollments = Column(Integer, default=0)
    active_enrollments = Column(Integer, default=0)
    completed_enrollments = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    creator = relationship("User")
    enrollments = relationship("AutomationEnrollment", back_populates="automation")

class AutomationEnrollment(Base):
    """Track leads enrolled in marketing automations"""
    __tablename__ = "automation_enrollments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    automation_id = Column(UUID(as_uuid=True), ForeignKey("marketing_automations.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    
    # Enrollment details
    enrolled_date = Column(DateTime, default=datetime.utcnow)
    current_step = Column(Integer, default=0)
    status = Column(String(50), default="active")  # active, completed, paused, cancelled
    
    # Progress tracking
    steps_completed = Column(Integer, default=0)
    next_action_date = Column(DateTime)
    
    # Completion tracking
    completed_date = Column(DateTime)
    completion_reason = Column(String(100))
    
    # Performance
    emails_sent = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    emails_clicked = Column(Integer, default=0)
    converted = Column(Boolean, default=False)
    conversion_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    automation = relationship("MarketingAutomation", back_populates="enrollments")
    lead = relationship("Lead", back_populates="automation_enrollments")

# ============================================================================
# CAMPAIGN INTERACTION MODELS
# ============================================================================

class CampaignInteraction(Base):
    """Track all campaign interactions"""
    __tablename__ = "campaign_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("marketing_campaigns.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    
    # Interaction details
    interaction_type = Column(String(50), nullable=False)  # impression, click, conversion, etc.
    interaction_data = Column(JSON)  # Additional interaction data
    
    # Context
    device_type = Column(String(50))
    browser = Column(String(100))
    operating_system = Column(String(100))
    referrer_url = Column(String(500))
    landing_page_url = Column(String(500))
    
    # Geographic data
    country = Column(String(100))
    city = Column(String(100))
    ip_address = Column(String(45))
    
    # Timestamps
    interaction_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    campaign = relationship("MarketingCampaign", back_populates="interactions")
    lead = relationship("Lead", back_populates="campaign_interactions")

# ============================================================================
# ATTRIBUTION MODELS
# ============================================================================

class AttributionModel(Base):
    """Marketing attribution tracking"""
    __tablename__ = "attribution_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    
    # Attribution details
    first_touch_campaign_id = Column(UUID(as_uuid=True), ForeignKey("marketing_campaigns.id"))
    last_touch_campaign_id = Column(UUID(as_uuid=True), ForeignKey("marketing_campaigns.id"))
    
    # Touch points
    total_touchpoints = Column(Integer, default=0)
    touchpoint_data = Column(JSON)  # Detailed touchpoint history
    
    # Attribution weights
    first_touch_attribution = Column(Float, default=0.0)
    last_touch_attribution = Column(Float, default=0.0)
    linear_attribution = Column(JSON)  # Linear attribution across touchpoints
    time_decay_attribution = Column(JSON)  # Time-decay attribution
    
    # Conversion tracking
    conversion_value = Column(Float)
    conversion_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lead = relationship("Lead")
    first_touch_campaign = relationship("MarketingCampaign", foreign_keys=[first_touch_campaign_id])
    last_touch_campaign = relationship("MarketingCampaign", foreign_keys=[last_touch_campaign_id])
