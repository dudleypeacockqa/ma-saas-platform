"""
Event Management System Models
Professional event management with EventBrite integration for M&A SaaS platform
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

class EventType(enum.Enum):
    WEBINAR = "webinar"
    WORKSHOP = "workshop"
    CONFERENCE = "conference"
    NETWORKING = "networking"
    MASTERCLASS = "masterclass"
    PANEL_DISCUSSION = "panel_discussion"
    ROUNDTABLE = "roundtable"
    VIRTUAL_SUMMIT = "virtual_summit"
    LIVE_PODCAST = "live_podcast"
    DEMO_SESSION = "demo_session"

class EventStatus(enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"

class EventFormat(enum.Enum):
    VIRTUAL = "virtual"
    IN_PERSON = "in_person"
    HYBRID = "hybrid"

class TicketType(enum.Enum):
    FREE = "free"
    PAID = "paid"
    VIP = "vip"
    EARLY_BIRD = "early_bird"
    GROUP_DISCOUNT = "group_discount"

class AttendeeStatus(enum.Enum):
    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    ATTENDED = "attended"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class EventbriteStatus(enum.Enum):
    NOT_SYNCED = "not_synced"
    SYNCING = "syncing"
    SYNCED = "synced"
    SYNC_ERROR = "sync_error"

class LeadQuality(enum.Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"

# ============================================================================
# EVENT MODELS
# ============================================================================

class Event(Base):
    """Main event model"""
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic event information
    title = Column(String(300), nullable=False)
    description = Column(Text)
    short_description = Column(String(500))
    
    # Event details
    event_type = Column(Enum(EventType), nullable=False)
    event_format = Column(Enum(EventFormat), default=EventFormat.VIRTUAL)
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT)
    
    # Scheduling
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    timezone = Column(String(50), default="Europe/London")
    duration_minutes = Column(Integer)
    
    # Location/Platform
    venue_name = Column(String(200))
    venue_address = Column(Text)
    virtual_platform = Column(String(100))  # Zoom, Teams, etc.
    meeting_url = Column(String(500))
    meeting_id = Column(String(100))
    meeting_password = Column(String(50))
    
    # Capacity and registration
    max_capacity = Column(Integer)
    registration_required = Column(Boolean, default=True)
    registration_deadline = Column(DateTime)
    early_bird_deadline = Column(DateTime)
    
    # Pricing
    is_free = Column(Boolean, default=True)
    base_price = Column(Float, default=0.0)
    currency = Column(String(3), default="GBP")
    
    # Content and branding
    banner_image_url = Column(String(500))
    thumbnail_url = Column(String(500))
    agenda = Column(JSON)  # Structured agenda
    speakers = Column(JSON)  # Speaker information
    sponsors = Column(JSON)  # Sponsor information
    
    # SEO and marketing
    seo_title = Column(String(300))
    seo_description = Column(String(500))
    keywords = Column(JSON)  # List of keywords
    tags = Column(JSON)  # Event tags
    
    # EventBrite integration
    eventbrite_event_id = Column(String(50))
    eventbrite_status = Column(Enum(EventbriteStatus), default=EventbriteStatus.NOT_SYNCED)
    eventbrite_url = Column(String(500))
    eventbrite_sync_error = Column(Text)
    last_eventbrite_sync = Column(DateTime)
    
    # Analytics and tracking
    total_registrations = Column(Integer, default=0)
    total_attendees = Column(Integer, default=0)
    no_show_count = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    
    # Lead generation
    leads_generated = Column(Integer, default=0)
    qualified_leads = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    
    # Settings
    auto_record = Column(Boolean, default=True)
    send_reminders = Column(Boolean, default=True)
    collect_feedback = Column(Boolean, default=True)
    require_approval = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    creator = relationship("User")
    tickets = relationship("EventTicket", back_populates="event")
    registrations = relationship("EventRegistration", back_populates="event")
    sessions = relationship("EventSession", back_populates="event")
    analytics = relationship("EventAnalytics", back_populates="event")
    feedback = relationship("EventFeedback", back_populates="event")
    leads = relationship("EventLead", back_populates="event")

# ============================================================================
# TICKET MODELS
# ============================================================================

class EventTicket(Base):
    """Event ticket types and pricing"""
    __tablename__ = "event_tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    
    # Ticket details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    ticket_type = Column(Enum(TicketType), nullable=False)
    
    # Pricing
    price = Column(Float, nullable=False, default=0.0)
    currency = Column(String(3), default="GBP")
    
    # Availability
    quantity_total = Column(Integer)  # Total available
    quantity_sold = Column(Integer, default=0)
    quantity_available = Column(Integer)  # Remaining
    
    # Sales period
    sales_start = Column(DateTime)
    sales_end = Column(DateTime)
    
    # EventBrite integration
    eventbrite_ticket_id = Column(String(50))
    eventbrite_ticket_class_id = Column(String(50))
    
    # Settings
    is_visible = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    min_quantity = Column(Integer, default=1)
    max_quantity = Column(Integer, default=10)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event = relationship("Event", back_populates="tickets")
    registrations = relationship("EventRegistration", back_populates="ticket")

# ============================================================================
# REGISTRATION MODELS
# ============================================================================

class EventRegistration(Base):
    """Event registrations and attendees"""
    __tablename__ = "event_registrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("event_tickets.id"))
    
    # Attendee information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    company = Column(String(200))
    job_title = Column(String(200))
    
    # Registration details
    status = Column(Enum(AttendeeStatus), default=AttendeeStatus.REGISTERED)
    registration_date = Column(DateTime, default=datetime.utcnow)
    confirmation_date = Column(DateTime)
    
    # Attendance tracking
    checked_in = Column(Boolean, default=False)
    check_in_time = Column(DateTime)
    attendance_duration = Column(Integer)  # Minutes attended
    
    # Payment information
    payment_status = Column(String(50), default="pending")
    payment_amount = Column(Float, default=0.0)
    payment_method = Column(String(50))
    transaction_id = Column(String(100))
    
    # EventBrite integration
    eventbrite_attendee_id = Column(String(50))
    eventbrite_order_id = Column(String(50))
    
    # Additional data
    custom_questions = Column(JSON)  # Custom registration questions
    dietary_requirements = Column(String(500))
    accessibility_needs = Column(String(500))
    
    # Marketing consent
    marketing_consent = Column(Boolean, default=False)
    communication_preferences = Column(JSON)
    
    # Source tracking
    referral_source = Column(String(100))
    utm_campaign = Column(String(100))
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event = relationship("Event", back_populates="registrations")
    ticket = relationship("EventTicket", back_populates="registrations")

# ============================================================================
# EVENT SESSION MODELS
# ============================================================================

class EventSession(Base):
    """Individual sessions within an event"""
    __tablename__ = "event_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    
    # Session details
    title = Column(String(300), nullable=False)
    description = Column(Text)
    session_type = Column(String(50))  # presentation, panel, workshop, etc.
    
    # Scheduling
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer)
    
    # Speakers and content
    speakers = Column(JSON)  # Speaker information
    materials = Column(JSON)  # Session materials, slides, etc.
    
    # Recording
    recording_url = Column(String(500))
    recording_available = Column(Boolean, default=False)
    
    # Attendance
    attendee_count = Column(Integer, default=0)
    engagement_score = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event = relationship("Event", back_populates="sessions")

# ============================================================================
# ANALYTICS MODELS
# ============================================================================

class EventAnalytics(Base):
    """Event performance analytics"""
    __tablename__ = "event_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    
    # Date and time
    analytics_date = Column(DateTime, nullable=False)
    
    # Registration metrics
    daily_registrations = Column(Integer, default=0)
    total_registrations = Column(Integer, default=0)
    registration_conversion_rate = Column(Float)
    
    # Attendance metrics
    attendee_count = Column(Integer, default=0)
    attendance_rate = Column(Float)  # Percentage
    average_attendance_duration = Column(Integer)  # Minutes
    
    # Engagement metrics
    questions_asked = Column(Integer, default=0)
    chat_messages = Column(Integer, default=0)
    polls_participated = Column(Integer, default=0)
    engagement_score = Column(Float)
    
    # Lead generation
    leads_generated = Column(Integer, default=0)
    qualified_leads = Column(Integer, default=0)
    demo_requests = Column(Integer, default=0)
    
    # Revenue metrics
    revenue_generated = Column(Float, default=0.0)
    average_ticket_price = Column(Float)
    
    # Traffic sources
    traffic_sources = Column(JSON)  # Breakdown of registration sources
    
    # Geographic data
    attendee_countries = Column(JSON)
    attendee_cities = Column(JSON)
    
    # Device and platform data
    device_breakdown = Column(JSON)
    platform_usage = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    event = relationship("Event", back_populates="analytics")

# ============================================================================
# FEEDBACK MODELS
# ============================================================================

class EventFeedback(Base):
    """Event feedback and ratings"""
    __tablename__ = "event_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    
    # Attendee information
    attendee_email = Column(String(255), nullable=False)
    attendee_name = Column(String(200))
    
    # Ratings (1-5 scale)
    overall_rating = Column(Integer)
    content_rating = Column(Integer)
    speaker_rating = Column(Integer)
    platform_rating = Column(Integer)
    organization_rating = Column(Integer)
    
    # Feedback text
    what_liked = Column(Text)
    what_improved = Column(Text)
    additional_comments = Column(Text)
    
    # Recommendations
    would_recommend = Column(Boolean)
    likely_to_attend_future = Column(Boolean)
    
    # Net Promoter Score
    nps_score = Column(Integer)  # 0-10 scale
    
    # Follow-up interest
    interested_in_demo = Column(Boolean, default=False)
    interested_in_consultation = Column(Boolean, default=False)
    interested_in_newsletter = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    event = relationship("Event", back_populates="feedback")

# ============================================================================
# LEAD GENERATION MODELS
# ============================================================================

class EventLead(Base):
    """Leads generated from events"""
    __tablename__ = "event_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    
    # Lead information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    company = Column(String(200))
    job_title = Column(String(200))
    company_size = Column(String(50))
    industry = Column(String(100))
    
    # Lead qualification
    lead_quality = Column(Enum(LeadQuality), default=LeadQuality.COLD)
    lead_score = Column(Integer, default=0)
    qualification_notes = Column(Text)
    
    # Interest and needs
    interested_products = Column(JSON)  # List of products/services
    pain_points = Column(JSON)  # List of pain points
    budget_range = Column(String(50))
    timeline = Column(String(50))
    decision_maker = Column(Boolean, default=False)
    
    # Engagement tracking
    attended_event = Column(Boolean, default=True)
    engagement_level = Column(String(50))  # high, medium, low
    questions_asked = Column(Integer, default=0)
    materials_downloaded = Column(JSON)
    
    # Follow-up actions
    demo_requested = Column(Boolean, default=False)
    consultation_requested = Column(Boolean, default=False)
    follow_up_scheduled = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    
    # CRM integration
    crm_contact_id = Column(String(100))
    crm_sync_status = Column(String(50), default="pending")
    
    # Source attribution
    lead_source = Column(String(100), default="event")
    utm_campaign = Column(String(100))
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    
    # Status and assignment
    status = Column(String(50), default="new")
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event = relationship("Event", back_populates="leads")
    assigned_user = relationship("User")

# ============================================================================
# EVENTBRITE INTEGRATION MODELS
# ============================================================================

class EventbriteIntegration(Base):
    """EventBrite integration settings and sync status"""
    __tablename__ = "eventbrite_integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # API credentials
    api_key = Column(String(200))
    organization_id = Column(String(100))
    user_id = Column(String(100))
    
    # Sync settings
    auto_sync_enabled = Column(Boolean, default=True)
    sync_frequency = Column(String(50), default="hourly")  # hourly, daily, manual
    last_sync = Column(DateTime)
    next_sync = Column(DateTime)
    
    # Sync status
    sync_status = Column(String(50), default="active")
    sync_errors = Column(JSON)  # List of recent sync errors
    
    # Mapping settings
    field_mappings = Column(JSON)  # Custom field mappings
    default_settings = Column(JSON)  # Default EventBrite settings
    
    # Statistics
    events_synced = Column(Integer, default=0)
    last_successful_sync = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    creator = relationship("User")

# ============================================================================
# EVENT TEMPLATES MODELS
# ============================================================================

class EventTemplate(Base):
    """Reusable event templates"""
    __tablename__ = "event_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    event_type = Column(Enum(EventType), nullable=False)
    category = Column(String(100))
    
    # Template structure
    template_data = Column(JSON)  # Complete event configuration
    default_duration = Column(Integer)  # Minutes
    
    # Pricing template
    pricing_structure = Column(JSON)  # Default ticket types and pricing
    
    # Content templates
    description_template = Column(Text)
    agenda_template = Column(JSON)
    email_templates = Column(JSON)  # Registration, reminder, follow-up emails
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float)  # Based on event performance
    
    # Template settings
    is_public = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    creator = relationship("User")

# ============================================================================
# EMAIL AUTOMATION MODELS
# ============================================================================

class EventEmailAutomation(Base):
    """Automated email campaigns for events"""
    __tablename__ = "event_email_automations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    
    # Email campaign details
    campaign_name = Column(String(200), nullable=False)
    email_type = Column(String(50), nullable=False)  # registration_confirmation, reminder, follow_up, etc.
    
    # Email content
    subject_line = Column(String(300), nullable=False)
    email_body = Column(Text, nullable=False)
    email_template = Column(String(100))
    
    # Scheduling
    trigger_type = Column(String(50), nullable=False)  # immediate, scheduled, conditional
    trigger_condition = Column(JSON)  # Conditions for sending
    send_time = Column(DateTime)  # For scheduled emails
    delay_hours = Column(Integer)  # Delay after trigger
    
    # Targeting
    target_audience = Column(String(100))  # all_registrants, attendees, no_shows, etc.
    audience_filters = Column(JSON)  # Additional filtering criteria
    
    # Personalization
    personalization_fields = Column(JSON)  # Fields to personalize
    dynamic_content = Column(JSON)  # Dynamic content rules
    
    # Status and statistics
    is_active = Column(Boolean, default=True)
    emails_sent = Column(Integer, default=0)
    open_rate = Column(Float)
    click_rate = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event = relationship("Event")
