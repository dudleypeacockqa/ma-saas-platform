from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel, SoftDeleteMixin


class ContentType(str, enum.Enum):
    PODCAST_SHOW_NOTES = "podcast_show_notes"
    LINKEDIN_POST = "linkedin_post"
    TWITTER_THREAD = "twitter_thread"
    YOUTUBE_DESCRIPTION = "youtube_description"
    INSTAGRAM_CAPTION = "instagram_caption"
    BLOG_ARTICLE = "blog_article"
    EMAIL_NEWSLETTER = "email_newsletter"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Content(BaseModel, SoftDeleteMixin):
    __tablename__ = "contents"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    # Content metadata
    title = Column(String(500), nullable=False)
    content_type = Column(SQLEnum(ContentType), nullable=False, index=True)
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.DRAFT, index=True)

    # Content data
    content_body = Column(Text, nullable=False)
    metadata = Column(JSON)  # Stores timestamps, keywords, SEO data, etc.

    # Source information
    source_type = Column(String(100))  # e.g., "audio_transcript", "video", "manual"
    source_file_url = Column(String(1000))

    # SEO and publishing
    seo_keywords = Column(JSON)
    published_url = Column(String(1000))
    published_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    user = relationship("User")


class PodcastEpisode(BaseModel, SoftDeleteMixin):
    __tablename__ = "podcast_episodes"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=False), ForeignKey("contents.id"), unique=True)

    # Episode details
    episode_number = Column(Integer)
    episode_title = Column(String(500), nullable=False)
    guest_name = Column(String(200))
    guest_bio = Column(Text)
    guest_company = Column(String(200))

    # Media files
    audio_url = Column(String(1000))
    video_url = Column(String(1000))
    transcript_text = Column(Text)

    # Episode metadata
    duration_seconds = Column(Integer)
    timestamps = Column(JSON)  # List of {time: "00:00", topic: "Introduction"}
    key_takeaways = Column(JSON)  # List of key points
    resources_mentioned = Column(JSON)  # Links and resources

    # Publishing
    publish_date = Column(DateTime)
    platforms = Column(JSON)  # {spotify: "url", apple: "url", youtube: "url"}

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    content = relationship("Content")


class ContentTemplate(BaseModel, SoftDeleteMixin):
    __tablename__ = "content_templates"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    name = Column(String(200), nullable=False)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    template_body = Column(Text, nullable=False)
    variables = Column(JSON)  # List of template variables

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
