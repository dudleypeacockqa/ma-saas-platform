"""
Podcast models for self-hosted podcast system
Handles podcast episodes, RSS feed generation, and audio file management
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, String, Integer, Boolean, ForeignKey, DateTime,
    Text, JSON, Numeric, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from .base import BaseModel, SoftDeleteMixin, MetadataMixin, TenantMixin
import xml.etree.ElementTree as ET
from xml.dom import minidom


class EpisodeStatus(str, Enum):
    """Episode status values"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PodcastCategory(str, Enum):
    """iTunes podcast categories"""
    BUSINESS = "Business"
    BUSINESS_INVESTING = "Business:Investing"
    BUSINESS_MANAGEMENT = "Business:Management"
    BUSINESS_MARKETING = "Business:Marketing"
    BUSINESS_ENTREPRENEURSHIP = "Business:Entrepreneurship"
    NEWS = "News"
    NEWS_BUSINESS = "News:Business News"
    EDUCATION = "Education"
    TECHNOLOGY = "Technology"


class Podcast(BaseModel, SoftDeleteMixin, MetadataMixin, TenantMixin):
    """
    Podcast model
    Represents a podcast show with metadata and settings
    """
    __tablename__ = 'podcasts'

    # Basic information
    title = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Podcast title"
    )

    subtitle = Column(
        String(255),
        nullable=True,
        comment="Podcast subtitle"
    )

    description = Column(
        Text,
        nullable=False,
        comment="Podcast description"
    )

    summary = Column(
        Text,
        nullable=True,
        comment="Podcast summary (longer description)"
    )

    # Author and ownership
    author = Column(
        String(255),
        nullable=False,
        comment="Podcast author/host"
    )

    owner_name = Column(
        String(255),
        nullable=False,
        comment="Podcast owner name"
    )

    owner_email = Column(
        String(255),
        nullable=False,
        comment="Podcast owner email"
    )

    # Categorization
    category = Column(
        String(100),
        nullable=False,
        default=PodcastCategory.BUSINESS.value,
        comment="Primary iTunes category"
    )

    subcategory = Column(
        String(100),
        nullable=True,
        comment="iTunes subcategory"
    )

    keywords = Column(
        JSON,
        nullable=True,
        comment="Podcast keywords for discovery"
    )

    # Media and branding
    cover_art_url = Column(
        String(500),
        nullable=True,
        comment="Podcast cover art URL"
    )

    website_url = Column(
        String(500),
        nullable=True,
        comment="Podcast website URL"
    )

    # Settings
    language = Column(
        String(10),
        nullable=False,
        default='en-US',
        comment="Podcast language (ISO code)"
    )

    copyright_text = Column(
        String(255),
        nullable=True,
        comment="Copyright notice"
    )

    is_explicit = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Contains explicit content"
    )

    is_complete = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Podcast is complete (no more episodes)"
    )

    # RSS feed settings
    feed_url = Column(
        String(500),
        nullable=True,
        comment="RSS feed URL"
    )

    feed_guid = Column(
        String(255),
        nullable=True,
        unique=True,
        comment="Unique feed identifier"
    )

    # Publishing
    is_published = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Podcast is published and visible"
    )

    published_at = Column(
        DateTime,
        nullable=True,
        comment="First publication date"
    )

    last_build_date = Column(
        DateTime,
        nullable=True,
        comment="Last RSS feed build date"
    )

    # Statistics
    total_episodes = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of episodes"
    )

    total_downloads = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Total download count"
    )

    # Relationships
    episodes = relationship(
        "PodcastEpisode",
        back_populates="podcast",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="desc(PodcastEpisode.episode_number)"
    )

    @validates('category')
    def validate_category(self, key, value):
        """Validate podcast category"""
        valid_categories = [cat.value for cat in PodcastCategory]
        if value not in valid_categories:
            raise ValueError(f"Invalid category: {value}")
        return value

    @property
    def published_episodes(self):
        """Get published episodes"""
        return self.episodes.filter_by(
            status=EpisodeStatus.PUBLISHED.value,
            is_deleted=False
        ).order_by("desc(episode_number)")

    @property
    def latest_episode(self):
        """Get the latest published episode"""
        return self.published_episodes.first()

    def generate_rss_feed(self, base_url: str) -> str:
        """Generate RSS feed XML for the podcast"""
        # Create RSS root element
        rss = ET.Element("rss")
        rss.set("version", "2.0")
        rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
        rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
        rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")

        # Create channel element
        channel = ET.SubElement(rss, "channel")

        # Basic channel information
        ET.SubElement(channel, "title").text = self.title
        ET.SubElement(channel, "description").text = self.description
        ET.SubElement(channel, "link").text = self.website_url or base_url
        ET.SubElement(channel, "language").text = self.language
        ET.SubElement(channel, "copyright").text = self.copyright_text or f"© {datetime.now().year} {self.owner_name}"
        ET.SubElement(channel, "managingEditor").text = f"{self.owner_email} ({self.owner_name})"
        ET.SubElement(channel, "webMaster").text = f"{self.owner_email} ({self.owner_name})"
        
        # iTunes-specific elements
        ET.SubElement(channel, "itunes:author").text = self.author
        ET.SubElement(channel, "itunes:summary").text = self.summary or self.description
        ET.SubElement(channel, "itunes:subtitle").text = self.subtitle or ""
        ET.SubElement(channel, "itunes:explicit").text = "yes" if self.is_explicit else "no"
        ET.SubElement(channel, "itunes:complete").text = "yes" if self.is_complete else "no"

        # iTunes owner
        owner = ET.SubElement(channel, "itunes:owner")
        ET.SubElement(owner, "itunes:name").text = self.owner_name
        ET.SubElement(owner, "itunes:email").text = self.owner_email

        # iTunes category
        category_elem = ET.SubElement(channel, "itunes:category")
        category_elem.set("text", self.category)
        if self.subcategory:
            subcategory_elem = ET.SubElement(category_elem, "itunes:category")
            subcategory_elem.set("text", self.subcategory)

        # Cover art
        if self.cover_art_url:
            ET.SubElement(channel, "itunes:image").set("href", self.cover_art_url)
            image = ET.SubElement(channel, "image")
            ET.SubElement(image, "url").text = self.cover_art_url
            ET.SubElement(image, "title").text = self.title
            ET.SubElement(image, "link").text = self.website_url or base_url

        # Atom self link
        atom_link = ET.SubElement(channel, "atom:link")
        atom_link.set("href", f"{base_url}/api/podcast/{self.id}/rss")
        atom_link.set("rel", "self")
        atom_link.set("type", "application/rss+xml")

        # Build date
        build_date = self.last_build_date or datetime.utcnow()
        ET.SubElement(channel, "lastBuildDate").text = build_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        ET.SubElement(channel, "pubDate").text = (self.published_at or self.created_at).strftime("%a, %d %b %Y %H:%M:%S GMT")

        # Add episodes
        for episode in self.published_episodes.limit(100):  # Limit to recent episodes
            item = ET.SubElement(channel, "item")
            
            ET.SubElement(item, "title").text = episode.title
            ET.SubElement(item, "description").text = episode.description
            ET.SubElement(item, "link").text = episode.episode_url or f"{base_url}/podcast/{self.id}/episode/{episode.id}"
            ET.SubElement(item, "guid").text = episode.guid or f"{base_url}/podcast/{self.id}/episode/{episode.id}"
            ET.SubElement(item, "pubDate").text = episode.published_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
            
            # iTunes episode-specific elements
            ET.SubElement(item, "itunes:author").text = episode.author or self.author
            ET.SubElement(item, "itunes:subtitle").text = episode.subtitle or ""
            ET.SubElement(item, "itunes:summary").text = episode.summary or episode.description
            ET.SubElement(item, "itunes:explicit").text = "yes" if episode.is_explicit else "no"
            ET.SubElement(item, "itunes:duration").text = episode.duration_formatted
            ET.SubElement(item, "itunes:episode").text = str(episode.episode_number)
            if episode.season_number:
                ET.SubElement(item, "itunes:season").text = str(episode.season_number)

            # Enclosure (audio file)
            if episode.audio_url:
                enclosure = ET.SubElement(item, "enclosure")
                enclosure.set("url", episode.audio_url)
                enclosure.set("type", episode.audio_type or "audio/mpeg")
                enclosure.set("length", str(episode.audio_size or 0))

        # Convert to pretty XML string
        rough_string = ET.tostring(rss, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def __repr__(self):
        return f"<Podcast {self.title} ({self.id})>"


class PodcastEpisode(BaseModel, SoftDeleteMixin, MetadataMixin):
    """
    Podcast episode model
    Represents individual podcast episodes
    """
    __tablename__ = 'podcast_episodes'

    # Podcast relationship
    podcast_id = Column(
        UUID(as_uuid=False),
        ForeignKey('podcasts.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Podcast this episode belongs to"
    )

    # Episode identification
    episode_number = Column(
        Integer,
        nullable=False,
        comment="Episode number"
    )

    season_number = Column(
        Integer,
        nullable=True,
        comment="Season number (optional)"
    )

    guid = Column(
        String(255),
        nullable=True,
        unique=True,
        comment="Unique episode identifier"
    )

    # Content
    title = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Episode title"
    )

    subtitle = Column(
        String(255),
        nullable=True,
        comment="Episode subtitle"
    )

    description = Column(
        Text,
        nullable=False,
        comment="Episode description"
    )

    summary = Column(
        Text,
        nullable=True,
        comment="Episode summary (longer description)"
    )

    show_notes = Column(
        Text,
        nullable=True,
        comment="Detailed show notes"
    )

    transcript = Column(
        Text,
        nullable=True,
        comment="Episode transcript"
    )

    # Author and guest information
    author = Column(
        String(255),
        nullable=True,
        comment="Episode author/host"
    )

    guests = Column(
        JSON,
        nullable=True,
        comment="List of episode guests"
    )

    # Audio file information
    audio_url = Column(
        String(500),
        nullable=True,
        comment="Audio file URL"
    )

    audio_file_path = Column(
        String(500),
        nullable=True,
        comment="Local audio file path"
    )

    audio_size = Column(
        Integer,
        nullable=True,
        comment="Audio file size in bytes"
    )

    audio_type = Column(
        String(50),
        nullable=True,
        default="audio/mpeg",
        comment="Audio MIME type"
    )

    duration_seconds = Column(
        Integer,
        nullable=True,
        comment="Episode duration in seconds"
    )

    # Episode metadata
    keywords = Column(
        JSON,
        nullable=True,
        comment="Episode keywords"
    )

    is_explicit = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Contains explicit content"
    )

    # Publishing
    status = Column(
        String(50),
        nullable=False,
        default=EpisodeStatus.DRAFT.value,
        index=True,
        comment="Episode status"
    )

    scheduled_at = Column(
        DateTime,
        nullable=True,
        comment="Scheduled publication date"
    )

    published_at = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="Actual publication date"
    )

    # URLs and links
    episode_url = Column(
        String(500),
        nullable=True,
        comment="Episode webpage URL"
    )

    # Statistics
    download_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Episode download count"
    )

    play_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Episode play count"
    )

    # Relationships
    podcast = relationship(
        "Podcast",
        back_populates="episodes"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint('episode_number > 0', name='check_episode_number_positive'),
        CheckConstraint('season_number IS NULL OR season_number > 0', name='check_season_number_positive'),
        CheckConstraint('duration_seconds IS NULL OR duration_seconds > 0', name='check_duration_positive'),
        CheckConstraint('audio_size IS NULL OR audio_size > 0', name='check_audio_size_positive'),
    )

    @validates('status')
    def validate_status(self, key, value):
        """Validate episode status"""
        valid_statuses = [status.value for status in EpisodeStatus]
        if value not in valid_statuses:
            raise ValueError(f"Invalid status: {value}")
        return value

    @property
    def duration_formatted(self) -> str:
        """Get formatted duration (HH:MM:SS)"""
        if not self.duration_seconds:
            return "00:00:00"
        
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @property
    def is_published(self) -> bool:
        """Check if episode is published"""
        return self.status == EpisodeStatus.PUBLISHED.value and self.published_at is not None

    def publish(self) -> None:
        """Publish the episode"""
        self.status = EpisodeStatus.PUBLISHED.value
        if not self.published_at:
            self.published_at = datetime.utcnow()

    def schedule(self, scheduled_at: datetime) -> None:
        """Schedule the episode for publication"""
        self.status = EpisodeStatus.SCHEDULED.value
        self.scheduled_at = scheduled_at

    def archive(self) -> None:
        """Archive the episode"""
        self.status = EpisodeStatus.ARCHIVED.value

    def __repr__(self):
        return f"<PodcastEpisode {self.episode_number}: {self.title} ({self.status})>"


class PodcastDownload(BaseModel):
    """
    Podcast download tracking
    Records download events for analytics
    """
    __tablename__ = 'podcast_downloads'

    # Episode relationship
    episode_id = Column(
        UUID(as_uuid=False),
        ForeignKey('podcast_episodes.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Episode that was downloaded"
    )

    # Download metadata
    ip_address = Column(
        String(45),
        nullable=True,
        comment="Client IP address (IPv4 or IPv6)"
    )

    user_agent = Column(
        String(500),
        nullable=True,
        comment="Client user agent string"
    )

    referer = Column(
        String(500),
        nullable=True,
        comment="HTTP referer header"
    )

    # Geographic information
    country = Column(
        String(2),
        nullable=True,
        comment="Country code (ISO 3166-1 alpha-2)"
    )

    city = Column(
        String(100),
        nullable=True,
        comment="City name"
    )

    # Download details
    bytes_downloaded = Column(
        Integer,
        nullable=True,
        comment="Number of bytes downloaded"
    )

    download_completed = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether download was completed"
    )

    # Relationships
    episode = relationship(
        "PodcastEpisode",
        backref="downloads"
    )

    def __repr__(self):
        return f"<PodcastDownload {self.episode_id} at {self.created_at}>"
