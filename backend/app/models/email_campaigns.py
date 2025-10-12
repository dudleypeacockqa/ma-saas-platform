"""
Email Campaign Models for M&A SaaS Platform
Tracks email campaigns, templates, and subscriber management
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class CampaignType(str, enum.Enum):
    WELCOME = "welcome"
    NEWSLETTER = "newsletter" 
    DEAL_NOTIFICATION = "deal_notification"
    MARKET_INSIGHTS = "market_insights"
    TRANSACTIONAL = "transactional"
    PROMOTIONAL = "promotional"
    ONBOARDING = "onboarding"

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

class EmailCampaign(Base):
    """Email campaign tracking"""
    __tablename__ = "email_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    campaign_type = Column(Enum(CampaignType), nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Campaign content
    subject = Column(String(500), nullable=False)
    html_content = Column(Text)
    plain_content = Column(Text)
    template_id = Column(String(100))  # SendGrid template ID
    dynamic_template_data = Column(JSON)
    
    # Targeting
    target_segments = Column(JSON)  # List of segments to target
    recipient_count = Column(Integer, default=0)
    
    # Scheduling
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    
    # Tracking
    sendgrid_campaign_id = Column(String(100))
    categories = Column(JSON)  # SendGrid categories
    custom_args = Column(JSON)
    
    # Statistics
    delivered_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    bounced_count = Column(Integer, default=0)
    unsubscribed_count = Column(Integer, default=0)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="email_campaigns")
    organization = relationship("Organization")
    email_logs = relationship("EmailLog", back_populates="campaign")

class EmailTemplate(Base):
    """Email template management"""
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    template_type = Column(Enum(CampaignType), nullable=False)
    
    # Template content
    subject_template = Column(String(500))
    html_template = Column(Text)
    plain_template = Column(Text)
    sendgrid_template_id = Column(String(100))
    
    # Template variables
    variables = Column(JSON)  # Available template variables
    default_data = Column(JSON)  # Default template data
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")
    organization = relationship("Organization")

class EmailSubscriber(Base):
    """Email subscriber management"""
    __tablename__ = "email_subscribers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # Subscription preferences
    subscribed_to_newsletter = Column(Boolean, default=True)
    subscribed_to_deal_notifications = Column(Boolean, default=True)
    subscribed_to_market_insights = Column(Boolean, default=True)
    subscribed_to_promotional = Column(Boolean, default=False)
    
    # Segmentation
    segments = Column(JSON)  # List of segments this subscriber belongs to
    subscription_tier = Column(String(50))  # trial, premium, enterprise
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Status
    is_active = Column(Boolean, default=True)
    unsubscribed_at = Column(DateTime)
    bounce_count = Column(Integer, default=0)
    last_engagement_at = Column(DateTime)
    
    # Metadata
    subscribed_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    email_logs = relationship("EmailLog", back_populates="subscriber")

class EmailLog(Base):
    """Email delivery and engagement tracking"""
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Email identification
    sendgrid_message_id = Column(String(100), index=True)
    campaign_id = Column(Integer, ForeignKey("email_campaigns.id"))
    subscriber_id = Column(Integer, ForeignKey("email_subscribers.id"))
    
    # Email details
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(500))
    email_type = Column(Enum(CampaignType))
    
    # Delivery status
    status = Column(String(50))  # delivered, bounced, dropped, etc.
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    first_click_at = Column(DateTime)
    
    # Engagement metrics
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    last_opened_at = Column(DateTime)
    last_clicked_at = Column(DateTime)
    
    # Error tracking
    bounce_reason = Column(String(500))
    error_message = Column(Text)
    
    # Metadata
    sent_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("EmailCampaign", back_populates="email_logs")
    subscriber = relationship("EmailSubscriber", back_populates="email_logs")

class EmailAutomation(Base):
    """Email automation workflows"""
    __tablename__ = "email_automations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    automation_type = Column(String(100))  # welcome_series, deal_follow_up, nurture_sequence
    
    # Trigger conditions
    trigger_event = Column(String(100))  # user_signup, deal_created, trial_expiring
    trigger_conditions = Column(JSON)
    
    # Email sequence
    email_sequence = Column(JSON)  # List of emails with delays and conditions
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Statistics
    triggered_count = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")
    organization = relationship("Organization")

class EmailAutomationExecution(Base):
    """Track automation execution for individual subscribers"""
    __tablename__ = "email_automation_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    automation_id = Column(Integer, ForeignKey("email_automations.id"))
    subscriber_id = Column(Integer, ForeignKey("email_subscribers.id"))
    
    # Execution status
    current_step = Column(Integer, default=0)
    status = Column(String(50))  # active, completed, paused, cancelled
    
    # Scheduling
    next_email_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Metadata
    started_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    automation = relationship("EmailAutomation")
    subscriber = relationship("EmailSubscriber")
