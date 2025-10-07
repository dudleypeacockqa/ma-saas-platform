"""
Enhanced Podcast Episode Production Models
Complete workflow from pre-production to distribution and analytics
"""
from sqlalchemy import (
    Column, String, Text, Integer, Numeric, Boolean, DateTime,
    ForeignKey, JSON, Enum as SQLEnum, Index, Float, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel, SoftDeleteMixin


class EpisodeStatus(str, enum.Enum):
    """Complete episode production workflow states"""
    PLANNING = "planning"
    GUEST_CONFIRMED = "guest_confirmed"
    RECORDING_SCHEDULED = "recording_scheduled"
    RECORDED = "recorded"
    PROCESSING = "processing"
    TRANSCRIPTION = "transcription"
    CONTENT_GENERATION = "content_generation"
    READY_TO_PUBLISH = "ready_to_publish"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PodcastGuest(BaseModel, SoftDeleteMixin):
    """
    Podcast guest management and CRM
    Tracks all interactions and appearances
    """
    __tablename__ = "podcast_guests"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Contact Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50))
    linkedin_url = Column(String(500))
    twitter_handle = Column(String(100))

    # Professional Details
    title = Column(String(200))
    company = Column(String(255))
    company_url = Column(String(500))
    industry = Column(String(100))
    location = Column(String(255))

    # Bio and Expertise
    bio = Column(Text)
    expertise_areas = Column(ARRAY(String))
    previous_media_appearances = Column(JSON)  # [{outlet, date, url}]
    notable_achievements = Column(Text)

    # Relationship Management
    relationship_score = Column(Integer, default=50, comment="0-100 relationship strength")
    initial_contact_date = Column(DateTime)
    last_contact_date = Column(DateTime)
    referral_source = Column(String(255))
    notes = Column(Text)

    # Appearance History
    total_appearances = Column(Integer, default=0)
    first_appearance_date = Column(DateTime)
    last_appearance_date = Column(DateTime)

    # Communication Preferences
    preferred_contact_method = Column(String(50), default="email")
    timezone = Column(String(50), default="UTC")
    availability_notes = Column(Text)

    # Social Media Stats
    linkedin_followers = Column(Integer)
    twitter_followers = Column(Integer)
    instagram_followers = Column(Integer)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    blacklisted = Column(Boolean, default=False)
    blacklist_reason = Column(Text)

    # Metadata
    custom_fields = Column(JSON)
    tags = Column(ARRAY(String))

    # Relationships
    organization = relationship("Organization")
    episodes = relationship("Episode", back_populates="guest")
    communications = relationship("GuestCommunication", back_populates="guest")

    __table_args__ = (
        Index('ix_guest_name', 'first_name', 'last_name'),
        Index('ix_guest_company', 'company'),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class GuestCommunication(BaseModel):
    """Track all communications with guests"""
    __tablename__ = "guest_communications"

    guest_id = Column(UUID(as_uuid=False), ForeignKey("podcast_guests.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    communication_type = Column(String(50), nullable=False)  # email, phone, linkedin, etc
    subject = Column(String(500))
    message_content = Column(Text)
    direction = Column(String(20), nullable=False)  # inbound, outbound

    sent_at = Column(DateTime)
    read_at = Column(DateTime)
    responded_at = Column(DateTime)

    metadata = Column(JSON)

    # Relationships
    guest = relationship("PodcastGuest", back_populates="communications")


class Episode(BaseModel, SoftDeleteMixin):
    """
    Enhanced podcast episode with complete production workflow
    Extends the existing PodcastEpisode model
    """
    __tablename__ = "episodes"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=False), ForeignKey("contents.id"))

    # Basic Episode Info
    episode_number = Column(Integer, index=True)
    season_number = Column(Integer, default=1)
    title = Column(String(500), nullable=False)
    subtitle = Column(String(500))
    description = Column(Text)

    # Guest Information
    guest_id = Column(UUID(as_uuid=False), ForeignKey("podcast_guests.id"), index=True)
    co_hosts = Column(JSON)  # Array of {name, role}

    # Production Workflow
    status = Column(SQLEnum(EpisodeStatus), default=EpisodeStatus.PLANNING, nullable=False, index=True)
    priority = Column(String(20), default="medium")  # high, medium, low

    # Scheduling
    recording_scheduled_at = Column(DateTime, index=True)
    recording_location = Column(String(255))  # studio, remote, hybrid
    recording_platform = Column(String(100))  # Riverside, Zoom, StreamYard

    # Recording Details
    recorded_at = Column(DateTime)
    duration_seconds = Column(Integer)
    recording_quality_score = Column(Float)

    # Files - Raw
    raw_audio_url = Column(String(1000))
    raw_video_url = Column(String(1000))
    raw_file_size_mb = Column(Numeric(10, 2))

    # Files - Processed
    processed_audio_url = Column(String(1000))
    processed_video_url = Column(String(1000))
    podcast_audio_url = Column(String(1000), comment="Final published audio")
    youtube_video_url = Column(String(1000), comment="Final YouTube video")

    # Transcript
    transcript_url = Column(String(1000))
    transcript_text = Column(Text)
    transcript_accuracy = Column(Float, comment="0-100 accuracy score")
    transcript_generated_at = Column(DateTime)

    # Content Elements
    timestamps = Column(JSON)  # [{time: "00:00", topic: "Introduction"}]
    chapter_markers = Column(JSON)
    key_quotes = Column(JSON)  # Notable quotes for social media
    key_takeaways = Column(JSON)
    resources_mentioned = Column(JSON)

    # SEO and Metadata
    seo_title = Column(String(500))
    seo_description = Column(String(1000))
    keywords = Column(ARRAY(String))
    category = Column(String(100))  # Technology, Business, Education, etc

    # Publishing
    publish_date = Column(DateTime, index=True)
    platforms_published = Column(JSON)  # {spotify: "url", apple: "url", youtube: "url"}
    rss_guid = Column(String(255), unique=True)

    # Analytics Summary
    total_downloads = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    average_completion_rate = Column(Float)
    engagement_score = Column(Float)

    # Production Team
    producer_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    editor_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Quality Control
    qc_passed = Column(Boolean, default=False)
    qc_notes = Column(Text)
    qc_checked_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    qc_checked_at = Column(DateTime)

    # Technical Metadata
    audio_bitrate = Column(Integer)
    audio_sample_rate = Column(Integer)
    video_resolution = Column(String(20))
    video_framerate = Column(Integer)

    # Monetization
    is_sponsored = Column(Boolean, default=False)
    sponsor_names = Column(ARRAY(String))
    ad_markers = Column(JSON)  # [{time: "05:30", type: "pre-roll", sponsor: "Company"}]

    # Internal Notes
    pre_production_notes = Column(Text)
    post_production_notes = Column(Text)

    # Metadata
    metadata = Column(JSON)
    tags = Column(ARRAY(String))

    # Relationships
    organization = relationship("Organization")
    guest = relationship("PodcastGuest", back_populates="episodes")
    production = relationship("EpisodeProduction", back_populates="episode", uselist=False)
    social_clips = relationship("SocialClip", back_populates="episode")
    analytics = relationship("EpisodeAnalytics", back_populates="episode")

    __table_args__ = (
        Index('ix_episode_status_date', 'status', 'publish_date'),
        Index('ix_episode_guest', 'guest_id', 'status'),
    )


class EpisodeProduction(BaseModel):
    """
    Detailed production tracking and processing status
    """
    __tablename__ = "episode_productions"

    episode_id = Column(UUID(as_uuid=False), ForeignKey("episodes.id"), unique=True, nullable=False)

    # Processing Status
    audio_processing_status = Column(String(50), default="pending")  # pending, processing, complete, failed
    video_processing_status = Column(String(50), default="pending")
    transcription_status = Column(String(50), default="pending")
    content_generation_status = Column(String(50), default="pending")

    # Processing Progress
    audio_processing_progress = Column(Integer, default=0)  # 0-100%
    video_processing_progress = Column(Integer, default=0)
    transcription_progress = Column(Integer, default=0)

    # Processing Logs
    audio_processing_log = Column(Text)
    video_processing_log = Column(Text)
    transcription_log = Column(Text)
    error_log = Column(Text)

    # Started/Completed Times
    audio_processing_started_at = Column(DateTime)
    audio_processing_completed_at = Column(DateTime)
    video_processing_started_at = Column(DateTime)
    video_processing_completed_at = Column(DateTime)
    transcription_started_at = Column(DateTime)
    transcription_completed_at = Column(DateTime)

    # Quality Metrics
    audio_quality_score = Column(Float)
    video_quality_score = Column(Float)
    overall_quality_grade = Column(String(10))  # A+, A, B+, B, C+, C, F

    # File Information
    storage_location = Column(String(500))  # S3 bucket, GCS bucket
    backup_location = Column(String(500))
    total_storage_mb = Column(Numeric(10, 2))

    # Processing Settings Used
    audio_processing_preset = Column(String(100))
    video_template_id = Column(String(100))
    transcription_service = Column(String(50))  # whisper, assemblyai, etc

    # Metadata
    processing_metadata = Column(JSON)

    # Relationships
    episode = relationship("Episode", back_populates="production")


class SocialClip(BaseModel, SoftDeleteMixin):
    """
    Social media clips generated from episodes
    """
    __tablename__ = "social_clips"

    episode_id = Column(UUID(as_uuid=False), ForeignKey("episodes.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False)

    # Clip Details
    title = Column(String(500), nullable=False)
    description = Column(Text)

    # Timing
    start_time_seconds = Column(Integer, nullable=False)
    end_time_seconds = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=False)

    # Platform Optimization
    platform = Column(String(50), nullable=False, index=True)  # tiktok, instagram, linkedin, youtube_shorts
    aspect_ratio = Column(String(20), nullable=False)  # 9:16, 1:1, 16:9
    resolution = Column(String(20))  # 1080x1920, 1080x1080, etc

    # Content
    transcript_excerpt = Column(Text)
    captions_enabled = Column(Boolean, default=True)

    # Files
    video_file_url = Column(String(1000))
    thumbnail_url = Column(String(1000))
    audiogram_url = Column(String(1000))

    # Branding
    template_used = Column(String(100))
    has_watermark = Column(Boolean, default=True)

    # Publishing
    published_at = Column(DateTime)
    published_url = Column(String(1000))
    publishing_status = Column(String(50), default="draft")  # draft, scheduled, published
    scheduled_for = Column(DateTime)

    # Performance Metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    engagement_rate = Column(Float)

    # AI Scores
    viral_potential_score = Column(Float, comment="AI prediction of virality")
    quality_score = Column(Float)

    # Metadata
    metadata = Column(JSON)
    tags = Column(ARRAY(String))

    # Relationships
    episode = relationship("Episode", back_populates="social_clips")
    organization = relationship("Organization")

    __table_args__ = (
        Index('ix_clip_platform_status', 'platform', 'publishing_status'),
    )


class EpisodeAnalytics(BaseModel):
    """
    Detailed analytics per episode across all platforms
    """
    __tablename__ = "episode_analytics"

    episode_id = Column(UUID(as_uuid=False), ForeignKey("episodes.id"), nullable=False, index=True)

    # Date for time-series tracking
    date = Column(DateTime, nullable=False, index=True)

    # Platform-specific metrics
    spotify_downloads = Column(Integer, default=0)
    apple_podcasts_downloads = Column(Integer, default=0)
    google_podcasts_downloads = Column(Integer, default=0)
    youtube_views = Column(Integer, default=0)
    linkedin_views = Column(Integer, default=0)

    # Total Aggregates
    total_downloads = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_listens = Column(Integer, default=0)

    # Engagement
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    average_watch_time_seconds = Column(Integer)
    completion_rate = Column(Float)

    # Listener Demographics
    demographics = Column(JSON)  # {age_groups, gender, locations}

    # Traffic Sources
    traffic_sources = Column(JSON)  # {organic, social, direct, referral}

    # Subscriber Impact
    new_subscribers = Column(Integer, default=0)
    unsubscribes = Column(Integer, default=0)

    # Revenue (if monetized)
    ad_revenue = Column(Numeric(10, 2))
    sponsor_revenue = Column(Numeric(10, 2))

    # Metadata
    metadata = Column(JSON)

    # Relationships
    episode = relationship("Episode", back_populates="analytics")

    __table_args__ = (
        Index('ix_analytics_episode_date', 'episode_id', 'date'),
    )


class PodcastSeries(BaseModel, SoftDeleteMixin):
    """
    Podcast show/series configuration
    """
    __tablename__ = "podcast_series"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Series Information
    title = Column(String(255), nullable=False)
    subtitle = Column(String(500))
    description = Column(Text)

    # Hosts
    host_names = Column(ARRAY(String))
    host_bios = Column(JSON)

    # Branding
    logo_url = Column(String(1000))
    cover_art_url = Column(String(1000))
    color_scheme = Column(JSON)

    # Publishing Info
    language = Column(String(10), default="en")
    category = Column(String(100))
    subcategories = Column(ARRAY(String))
    explicit_content = Column(Boolean, default=False)

    # Schedule
    publishing_schedule = Column(String(100))  # "Tue/Fri", "Weekly Monday"
    typical_duration_minutes = Column(Integer)

    # Platform Links
    spotify_url = Column(String(500))
    apple_podcasts_url = Column(String(500))
    youtube_channel_url = Column(String(500))
    website_url = Column(String(500))
    rss_feed_url = Column(String(500))

    # Contact
    email = Column(String(255))
    social_media = Column(JSON)  # {twitter, linkedin, instagram}

    # Settings
    auto_publish = Column(Boolean, default=False)
    enable_analytics = Column(Boolean, default=True)
    enable_transcription = Column(Boolean, default=True)

    # Metadata
    metadata = Column(JSON)

    # Relationships
    organization = relationship("Organization")

    def __repr__(self):
        return f"<PodcastSeries {self.title}>"
