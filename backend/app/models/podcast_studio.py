"""
Podcast Studio Models - StreamYard-level recording and AI automation
Database models for professional podcast hosting infrastructure
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid
import enum

from app.models.base import Base

class RecordingStatus(enum.Enum):
    """Recording session status enum"""
    READY = "ready"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPED = "stopped"
    PROCESSING = "processing"
    COMPLETED = "completed"
    LIVE = "live"
    ERROR = "error"

class AIJobStatus(enum.Enum):
    """AI processing job status enum"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AIJobType(enum.Enum):
    """AI processing job type enum"""
    TRANSCRIPTION = "transcription"
    SHOW_NOTES = "show_notes"
    SOCIAL_CLIPS = "social_clips"
    BLOG_POST = "blog_post"
    NEWSLETTER = "newsletter"
    SEO_OPTIMIZATION = "seo_optimization"
    HIGHLIGHTS = "highlights"

class StreamStatus(enum.Enum):
    """Live stream status enum"""
    OFFLINE = "offline"
    STARTING = "starting"
    LIVE = "live"
    ENDING = "ending"
    ENDED = "ended"
    ERROR = "error"

class RecordingSession(Base):
    """Recording session model with StreamYard-level features"""
    __tablename__ = "recording_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)

    # Ownership and organization
    host_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    # Session timing
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)

    # Session status and settings
    status = Column(Enum(RecordingStatus), default=RecordingStatus.READY, index=True)
    settings = Column(JSON, nullable=False, default={})  # Recording quality, format, AI settings

    # Participants and platforms
    guests = Column(JSON, default=[])  # List of guest participants
    platforms = Column(JSON, default=[])  # Live streaming platforms

    # Recording files and outputs
    recording_url = Column(String, nullable=True)  # Main recording file
    audio_url = Column(String, nullable=True)  # Audio-only version
    video_url = Column(String, nullable=True)  # Video version
    thumbnail_url = Column(String, nullable=True)  # Episode thumbnail

    # Analytics and engagement
    analytics = Column(JSON, default={})  # Viewer stats, engagement metrics
    total_viewers = Column(Integer, default=0)
    peak_viewers = Column(Integer, default=0)
    chat_messages = Column(Integer, default=0)

    # AI processing status
    ai_processing_status = Column(JSON, default={})  # Status of various AI jobs
    transcript_url = Column(String, nullable=True)  # Generated transcript
    show_notes = Column(Text, nullable=True)  # AI-generated show notes

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    host = relationship("User", foreign_keys=[host_user_id])
    organization = relationship("Organization", foreign_keys=[organization_id])
    ai_jobs = relationship("AIProcessingJob", back_populates="session")
    live_streams = relationship("LiveStream", back_populates="session")
    episodes = relationship("PodcastEpisode", back_populates="recording_session")

class LiveStream(Base):
    """Live streaming session to multiple platforms"""
    __tablename__ = "live_streams"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("recording_sessions.id"), nullable=False, index=True)

    # Platform details
    platform_id = Column(String, nullable=False)  # youtube, facebook, linkedin, etc.
    platform_name = Column(String(100), nullable=False)
    rtmp_url = Column(String, nullable=True)
    stream_key = Column(String, nullable=True)

    # Stream metadata
    title = Column(String(200), nullable=False)
    description = Column(Text)
    thumbnail_url = Column(String, nullable=True)

    # Stream timing and status
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(Enum(StreamStatus), default=StreamStatus.OFFLINE, index=True)

    # Analytics
    viewer_count = Column(Integer, default=0)
    peak_viewers = Column(Integer, default=0)
    total_watch_time = Column(Integer, default=0)  # Total watch time in minutes
    engagement_rate = Column(Float, default=0.0)

    # Technical details
    bitrate = Column(Integer, default=3000)  # kbps
    resolution = Column(String(20), default="1080p")  # 720p, 1080p, 4K
    frame_rate = Column(Integer, default=30)  # fps

    # Organization
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("RecordingSession", back_populates="live_streams")
    organization = relationship("Organization")

class AIProcessingJob(Base):
    """AI content processing jobs for podcast automation"""
    __tablename__ = "ai_processing_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("recording_sessions.id"), nullable=False, index=True)

    # Job details
    job_type = Column(Enum(AIJobType), nullable=False, index=True)
    status = Column(Enum(AIJobStatus), default=AIJobStatus.QUEUED, index=True)
    priority = Column(String(10), default="normal")  # low, normal, high

    # Processing details
    progress = Column(Float, default=0.0)  # 0-100 percentage
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    processing_time_seconds = Column(Integer, nullable=True)

    # Input and output
    input_data = Column(JSON, default={})  # Configuration for processing
    output_data = Column(JSON, default={})  # Results of processing
    output_url = Column(String, nullable=True)  # URL to generated content

    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # AI model details
    model_used = Column(String(100), nullable=True)  # claude-3-sonnet, gpt-4, etc.
    tokens_used = Column(Integer, nullable=True)  # For cost tracking

    # Organization
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("RecordingSession", back_populates="ai_jobs")
    organization = relationship("Organization")

class PodcastEpisode(Base):
    """Published podcast episode with full metadata"""
    __tablename__ = "podcast_episodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recording_session_id = Column(String, ForeignKey("recording_sessions.id"), nullable=True)

    # Episode metadata
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    episode_number = Column(Integer, nullable=True, index=True)
    season_number = Column(Integer, nullable=True)

    # Content URLs
    audio_url = Column(String, nullable=False)  # Primary audio file
    video_url = Column(String, nullable=True)  # Video version (if available)
    transcript_url = Column(String, nullable=True)  # Transcript file
    thumbnail_url = Column(String, nullable=True)  # Episode artwork

    # Episode details
    duration_seconds = Column(Integer, nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    audio_format = Column(String(10), default="mp3")  # mp3, wav, m4a

    # Publishing
    published_at = Column(DateTime, nullable=True, index=True)
    is_published = Column(Boolean, default=False, index=True)
    is_premium = Column(Boolean, default=False)  # Premium subscriber only

    # SEO and discovery
    slug = Column(String(250), nullable=True, unique=True, index=True)
    tags = Column(ARRAY(String), default=[])  # Searchable tags
    categories = Column(ARRAY(String), default=[])  # Podcast categories
    keywords = Column(Text, nullable=True)  # SEO keywords

    # Analytics
    download_count = Column(Integer, default=0)
    play_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)

    # AI-generated content
    show_notes = Column(Text, nullable=True)  # AI-generated show notes
    key_takeaways = Column(JSON, default=[])  # Bullet points of key insights
    timestamps = Column(JSON, default=[])  # Chapter markers with timestamps
    social_clips = Column(JSON, default=[])  # Generated social media clips

    # Distribution
    platform_distribution = Column(JSON, default={})  # Which platforms it's on
    rss_guid = Column(String, nullable=True, unique=True)  # RSS GUID

    # Organization and ownership
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recording_session = relationship("RecordingSession", back_populates="episodes")
    organization = relationship("Organization")
    creator = relationship("User", foreign_keys=[created_by])
    analytics = relationship("PodcastAnalytics", back_populates="episode")
    comments = relationship("PodcastComment", back_populates="episode")

class PodcastAnalytics(Base):
    """Detailed analytics for podcast episodes"""
    __tablename__ = "podcast_analytics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("podcast_episodes.id"), nullable=False, index=True)

    # Time-based metrics
    date = Column(DateTime, nullable=False, index=True)

    # Engagement metrics
    downloads = Column(Integer, default=0)
    unique_listeners = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)  # Percentage who finished
    average_listen_time = Column(Integer, default=0)  # Seconds

    # Geographic data
    country_breakdown = Column(JSON, default={})  # Country: listener_count
    city_breakdown = Column(JSON, default={})  # City: listener_count

    # Platform breakdown
    platform_breakdown = Column(JSON, default={})  # Platform: download_count
    device_breakdown = Column(JSON, default={})  # Device type: listener_count

    # Referral sources
    referral_sources = Column(JSON, default={})  # Source: traffic_count

    # Engagement actions
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    subscriptions_generated = Column(Integer, default=0)

    # Business metrics
    leads_generated = Column(Integer, default=0)  # CTA responses
    revenue_attributed = Column(Float, default=0.0)  # Revenue from episode
    conversion_rate = Column(Float, default=0.0)  # Lead conversion rate

    # Organization
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    episode = relationship("PodcastEpisode", back_populates="analytics")
    organization = relationship("Organization")

class PodcastComment(Base):
    """Comments and feedback on podcast episodes"""
    __tablename__ = "podcast_comments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("podcast_episodes.id"), nullable=False, index=True)

    # Comment details
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Registered user
    guest_name = Column(String(100), nullable=True)  # Non-registered commenter
    guest_email = Column(String(255), nullable=True)  # Non-registered commenter email

    # Comment content
    content = Column(Text, nullable=False)
    timestamp_seconds = Column(Integer, nullable=True)  # Comment on specific time

    # Moderation
    is_approved = Column(Boolean, default=True)
    is_flagged = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)  # Featured comment

    # Engagement
    like_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    parent_comment_id = Column(String, ForeignKey("podcast_comments.id"), nullable=True)

    # Organization
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    episode = relationship("PodcastEpisode", back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])
    organization = relationship("Organization")
    parent_comment = relationship("PodcastComment", remote_side=[id])
    replies = relationship("PodcastComment", remote_side=[parent_comment_id])

class PodcastShow(Base):
    """Podcast show/series configuration"""
    __tablename__ = "podcast_shows"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Show metadata
    title = Column(String(200), nullable=False)
    description = Column(Text)
    tagline = Column(String(500), nullable=True)  # Short description

    # Branding
    logo_url = Column(String, nullable=True)  # Show artwork
    cover_image_url = Column(String, nullable=True)  # Cover image
    primary_color = Column(String(7), nullable=True)  # Hex color code

    # Show details
    category = Column(String(100), nullable=False)  # Primary category
    subcategories = Column(ARRAY(String), default=[])  # Additional categories
    language = Column(String(10), default="en")  # Language code
    explicit = Column(Boolean, default=False)  # Explicit content flag

    # Publishing settings
    is_active = Column(Boolean, default=True)
    auto_publish = Column(Boolean, default=False)  # Auto-publish new episodes
    publish_schedule = Column(String(50), nullable=True)  # weekly, biweekly, etc.

    # RSS and distribution
    rss_url = Column(String, nullable=True)  # RSS feed URL
    website_url = Column(String, nullable=True)  # Show website
    distribution_platforms = Column(JSON, default={})  # Platform URLs

    # Analytics settings
    analytics_enabled = Column(Boolean, default=True)
    tracking_code = Column(String, nullable=True)  # Analytics tracking

    # Organization and ownership
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    creator = relationship("User", foreign_keys=[created_by])

# Create indexes for performance
# These would be created via Alembic migrations
from sqlalchemy import Index

# Indexes for common queries
Index('idx_recording_sessions_org_status', RecordingSession.organization_id, RecordingSession.status)
Index('idx_ai_jobs_session_type', AIProcessingJob.session_id, AIProcessingJob.job_type)
Index('idx_episodes_published', PodcastEpisode.organization_id, PodcastEpisode.is_published, PodcastEpisode.published_at)
Index('idx_analytics_episode_date', PodcastAnalytics.episode_id, PodcastAnalytics.date)