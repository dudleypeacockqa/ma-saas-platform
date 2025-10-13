"""
Content Creation Suite Models
Professional podcast and video production system for M&A SaaS platform
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

class ContentType(enum.Enum):
    PODCAST = "podcast"
    VIDEO = "video"
    BLOG_POST = "blog_post"
    WEBINAR = "webinar"
    SHORT_FORM = "short_form"  # Social media clips
    NEWSLETTER = "newsletter"

class ContentStatus(enum.Enum):
    DRAFT = "draft"
    IN_PRODUCTION = "in_production"
    REVIEW = "review"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ProductionStage(enum.Enum):
    PLANNING = "planning"
    RECORDING = "recording"
    EDITING = "editing"
    POST_PRODUCTION = "post_production"
    APPROVAL = "approval"
    DISTRIBUTION = "distribution"
    COMPLETED = "completed"

class DistributionPlatform(enum.Enum):
    APPLE_PODCASTS = "apple_podcasts"
    SPOTIFY = "spotify"
    GOOGLE_PODCASTS = "google_podcasts"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    WEBSITE = "website"
    EMAIL = "email"

class RecordingQuality(enum.Enum):
    HD_720P = "hd_720p"
    FULL_HD_1080P = "full_hd_1080p"
    UHD_4K = "uhd_4k"
    AUDIO_ONLY = "audio_only"

# ============================================================================
# CONTENT SERIES MODELS
# ============================================================================

class ContentSeries(Base):
    """Content series/shows management"""
    __tablename__ = "content_series"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    content_type = Column(Enum(ContentType), nullable=False)
    
    # Branding
    logo_url = Column(String(500))
    banner_url = Column(String(500))
    brand_colors = Column(JSON)  # {"primary": "#hex", "secondary": "#hex"}
    
    # Publishing schedule
    publishing_schedule = Column(String(100))  # "Weekly on Wednesdays", "Bi-weekly", etc.
    target_duration = Column(Integer)  # Target duration in minutes
    
    # SEO and metadata
    seo_keywords = Column(JSON)  # List of keywords
    target_audience = Column(String(200))
    category = Column(String(100))
    
    # Analytics
    total_episodes = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    episodes = relationship("ContentEpisode", back_populates="series")
    creator = relationship("User")

# ============================================================================
# CONTENT EPISODE MODELS
# ============================================================================

class ContentEpisode(Base):
    """Individual content episodes/posts"""
    __tablename__ = "content_episodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    series_id = Column(UUID(as_uuid=True), ForeignKey("content_series.id"), nullable=False)
    
    # Episode details
    title = Column(String(300), nullable=False)
    description = Column(Text)
    episode_number = Column(Integer)
    season_number = Column(Integer, default=1)
    
    # Content
    content_type = Column(Enum(ContentType), nullable=False)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    production_stage = Column(Enum(ProductionStage), default=ProductionStage.PLANNING)
    
    # Media files
    audio_file_url = Column(String(500))
    video_file_url = Column(String(500))
    thumbnail_url = Column(String(500))
    transcript_url = Column(String(500))
    
    # Technical details
    duration_seconds = Column(Integer)
    file_size_mb = Column(Float)
    recording_quality = Column(Enum(RecordingQuality))
    
    # Publishing
    scheduled_publish_date = Column(DateTime)
    published_date = Column(DateTime)
    
    # SEO and metadata
    seo_title = Column(String(300))
    seo_description = Column(String(500))
    keywords = Column(JSON)  # List of keywords
    tags = Column(JSON)  # List of tags
    
    # Guest information
    guests = Column(JSON)  # List of guest details
    host_notes = Column(Text)
    
    # Analytics
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Engagement metrics
    average_watch_time = Column(Integer)  # Seconds
    completion_rate = Column(Float)  # Percentage
    engagement_score = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    series = relationship("ContentSeries", back_populates="episodes")
    creator = relationship("User")
    recording_sessions = relationship("ContentRecordingSession", back_populates="episode")
    distributions = relationship("ContentDistribution", back_populates="episode")
    analytics = relationship("ContentAnalytics", back_populates="episode")

# ============================================================================
# RECORDING SESSION MODELS
# ============================================================================

class ContentRecordingSession(Base):
    """Recording session management for content creation"""
    __tablename__ = "content_recording_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id = Column(UUID(as_uuid=True), ForeignKey("content_episodes.id"), nullable=False)
    
    # Session details
    session_name = Column(String(200), nullable=False)
    scheduled_start = Column(DateTime, nullable=False)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # Technical setup
    recording_quality = Column(Enum(RecordingQuality), default=RecordingQuality.FULL_HD_1080P)
    audio_quality = Column(String(50), default="48kHz/24-bit")
    video_codec = Column(String(50), default="H.264")
    
    # Participants
    host_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    participants = Column(JSON)  # List of participant details
    max_participants = Column(Integer, default=10)
    
    # Recording files
    raw_video_url = Column(String(500))
    raw_audio_url = Column(String(500))
    backup_recording_url = Column(String(500))
    
    # Session settings
    auto_recording = Column(Boolean, default=True)
    cloud_recording = Column(Boolean, default=True)
    live_streaming = Column(Boolean, default=False)
    
    # Live streaming settings
    stream_platforms = Column(JSON)  # List of platforms for live streaming
    stream_key = Column(String(200))
    rtmp_url = Column(String(500))
    
    # Session status
    status = Column(String(50), default="scheduled")  # scheduled, in_progress, completed, cancelled
    
    # Technical issues
    technical_issues = Column(JSON)  # List of issues encountered
    quality_score = Column(Float)  # Overall session quality score
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    episode = relationship("ContentEpisode", back_populates="recording_sessions")
    host = relationship("User")

# ============================================================================
# AI CONTENT PROCESSING MODELS
# ============================================================================

class AIContentProcessing(Base):
    """AI-powered content processing and enhancement"""
    __tablename__ = "ai_content_processing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id = Column(UUID(as_uuid=True), ForeignKey("content_episodes.id"), nullable=False)
    
    # Processing tasks
    transcription_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    transcription_accuracy = Column(Float)  # Percentage accuracy
    transcript_text = Column(Text)
    
    # AI enhancements
    auto_chapters = Column(JSON)  # Automatically generated chapters
    key_moments = Column(JSON)  # Important moments/highlights
    topic_extraction = Column(JSON)  # Extracted topics and themes
    sentiment_analysis = Column(JSON)  # Sentiment analysis results
    
    # Content generation
    auto_summary = Column(Text)  # AI-generated summary
    auto_show_notes = Column(Text)  # AI-generated show notes
    auto_social_posts = Column(JSON)  # Generated social media posts
    auto_blog_post = Column(Text)  # Generated blog post
    
    # SEO optimization
    suggested_keywords = Column(JSON)  # AI-suggested keywords
    seo_title_suggestions = Column(JSON)  # Title suggestions
    seo_description_suggestions = Column(JSON)  # Description suggestions
    
    # Short-form content
    highlight_clips = Column(JSON)  # Generated short clips for social media
    audiogram_timestamps = Column(JSON)  # Timestamps for audiogram creation
    
    # Processing metadata
    processing_start = Column(DateTime)
    processing_end = Column(DateTime)
    processing_duration = Column(Integer)  # Seconds
    ai_model_used = Column(String(100))  # Which AI model was used
    
    # Quality scores
    content_quality_score = Column(Float)
    engagement_prediction = Column(Float)
    virality_score = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    episode = relationship("ContentEpisode")

# ============================================================================
# CONTENT DISTRIBUTION MODELS
# ============================================================================

class ContentDistribution(Base):
    """Multi-platform content distribution"""
    __tablename__ = "content_distributions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id = Column(UUID(as_uuid=True), ForeignKey("content_episodes.id"), nullable=False)
    
    # Platform details
    platform = Column(Enum(DistributionPlatform), nullable=False)
    platform_episode_id = Column(String(200))  # Platform-specific ID
    platform_url = Column(String(500))
    
    # Distribution settings
    auto_publish = Column(Boolean, default=True)
    scheduled_publish_date = Column(DateTime)
    actual_publish_date = Column(DateTime)
    
    # Platform-specific metadata
    platform_title = Column(String(300))
    platform_description = Column(Text)
    platform_tags = Column(JSON)
    platform_category = Column(String(100))
    
    # Publishing status
    status = Column(String(50), default="pending")  # pending, publishing, published, failed
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Platform analytics
    platform_views = Column(Integer, default=0)
    platform_likes = Column(Integer, default=0)
    platform_comments = Column(Integer, default=0)
    platform_shares = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    episode = relationship("ContentEpisode", back_populates="distributions")

# ============================================================================
# CONTENT ANALYTICS MODELS
# ============================================================================

class ContentAnalytics(Base):
    """Detailed content performance analytics"""
    __tablename__ = "content_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id = Column(UUID(as_uuid=True), ForeignKey("content_episodes.id"), nullable=False)
    
    # Date and time
    analytics_date = Column(DateTime, nullable=False)
    
    # View/Download metrics
    daily_views = Column(Integer, default=0)
    daily_downloads = Column(Integer, default=0)
    unique_viewers = Column(Integer, default=0)
    returning_viewers = Column(Integer, default=0)
    
    # Engagement metrics
    average_watch_time = Column(Integer)  # Seconds
    completion_rate = Column(Float)  # Percentage
    like_rate = Column(Float)  # Percentage
    comment_rate = Column(Float)  # Percentage
    share_rate = Column(Float)  # Percentage
    
    # Audience demographics
    audience_demographics = Column(JSON)  # Age, gender, location breakdown
    traffic_sources = Column(JSON)  # Where viewers came from
    device_breakdown = Column(JSON)  # Desktop, mobile, tablet
    
    # Geographic data
    top_countries = Column(JSON)
    top_cities = Column(JSON)
    
    # Time-based analytics
    peak_viewing_hours = Column(JSON)
    drop_off_points = Column(JSON)  # Where viewers stop watching
    
    # Lead generation
    leads_generated = Column(Integer, default=0)
    conversion_rate = Column(Float)  # Percentage
    
    # Revenue attribution
    attributed_revenue = Column(Float, default=0.0)
    cost_per_acquisition = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    episode = relationship("ContentEpisode", back_populates="analytics")

# ============================================================================
# CONTENT TEMPLATES MODELS
# ============================================================================

class ContentTemplate(Base):
    """Reusable content templates"""
    __tablename__ = "content_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    content_type = Column(Enum(ContentType), nullable=False)
    category = Column(String(100))
    
    # Template structure
    template_structure = Column(JSON)  # Outline/structure
    default_duration = Column(Integer)  # Minutes
    
    # Content elements
    intro_template = Column(Text)
    outro_template = Column(Text)
    call_to_action_template = Column(Text)
    
    # Visual elements
    thumbnail_template_url = Column(String(500))
    graphics_package_url = Column(String(500))
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float)  # Based on performance of content using this template
    
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
# CONTENT COLLABORATION MODELS
# ============================================================================

class ContentCollaboration(Base):
    """Content collaboration and approval workflow"""
    __tablename__ = "content_collaborations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id = Column(UUID(as_uuid=True), ForeignKey("content_episodes.id"), nullable=False)
    
    # Collaboration details
    collaborator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)  # editor, reviewer, approver, guest
    
    # Permissions
    can_edit = Column(Boolean, default=False)
    can_approve = Column(Boolean, default=False)
    can_publish = Column(Boolean, default=False)
    
    # Status
    status = Column(String(50), default="pending")  # pending, accepted, declined
    feedback = Column(Text)
    
    # Approval workflow
    approval_required = Column(Boolean, default=False)
    approved = Column(Boolean, default=False)
    approved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    episode = relationship("ContentEpisode")
    collaborator = relationship("User")

# ============================================================================
# CONTENT MONETIZATION MODELS
# ============================================================================

class ContentMonetization(Base):
    """Content monetization tracking"""
    __tablename__ = "content_monetizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id = Column(UUID(as_uuid=True), ForeignKey("content_episodes.id"), nullable=False)
    
    # Monetization methods
    sponsorship_revenue = Column(Float, default=0.0)
    affiliate_revenue = Column(Float, default=0.0)
    subscription_revenue = Column(Float, default=0.0)
    merchandise_revenue = Column(Float, default=0.0)
    
    # Sponsor information
    sponsors = Column(JSON)  # List of sponsors and deals
    
    # Performance metrics
    revenue_per_view = Column(Float)
    revenue_per_download = Column(Float)
    total_revenue = Column(Float, default=0.0)
    
    # Attribution
    leads_generated = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    conversion_value = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    episode = relationship("ContentEpisode")
