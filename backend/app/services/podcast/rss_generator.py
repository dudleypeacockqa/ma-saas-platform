"""
Advanced RSS feed generation with SEO optimization and platform distribution
Replaces external services like Transistor.fm and Buzzsprout
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import hashlib
import re
from pathlib import Path
import json
import structlog
import aiohttp
from dataclasses import dataclass

logger = structlog.get_logger(__name__)


@dataclass
class PodcastMetadata:
    """Podcast metadata for RSS feed"""
    title: str
    description: str
    author: str
    email: str
    website: str
    language: str = "en"
    category: str = "Business"
    subcategory: str = "Entrepreneurship"
    explicit: bool = False
    copyright: str = ""
    keywords: List[str] = None
    artwork_url: str = ""
    owner_name: str = ""
    owner_email: str = ""


@dataclass
class EpisodeMetadata:
    """Episode metadata for RSS feed"""
    guid: str
    title: str
    description: str
    audio_url: str
    publish_date: datetime
    duration: int  # in seconds
    file_size: int  # in bytes
    episode_number: Optional[int] = None
    season_number: Optional[int] = None
    episode_type: str = "full"  # full, trailer, bonus
    explicit: bool = False
    keywords: List[str] = None
    transcript_url: Optional[str] = None
    chapters_url: Optional[str] = None
    artwork_url: Optional[str] = None


class RSSGenerator:
    """
    Professional RSS feed generator with platform optimization
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.namespaces = {
            'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
            'spotify': 'http://www.spotify.com/ns/rss',
            'googleplay': 'http://www.google.com/schemas/play-podcasts/1.0',
            'podcast': 'https://podcastindex.org/namespace/1.0',
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'atom': 'http://www.w3.org/2005/Atom'
        }

    def generate_feed(
        self,
        podcast: PodcastMetadata,
        episodes: List[EpisodeMetadata]
    ) -> str:
        """
        Generate optimized RSS feed for all major platforms
        """

        # Create root RSS element
        rss = ET.Element('rss', version='2.0')

        # Add namespaces
        for prefix, uri in self.namespaces.items():
            rss.set(f'xmlns:{prefix}', uri)

        # Create channel
        channel = ET.SubElement(rss, 'channel')

        # Add podcast metadata
        self._add_podcast_metadata(channel, podcast)

        # Add episodes
        for episode in episodes:
            self._add_episode(channel, episode)

        # Generate XML string
        xml_string = self._prettify_xml(rss)

        # Validate feed
        if not self._validate_feed(xml_string):
            logger.warning("RSS feed validation failed")

        return xml_string

    def _add_podcast_metadata(self, channel: ET.Element, podcast: PodcastMetadata):
        """
        Add comprehensive podcast metadata for all platforms
        """

        # Standard RSS elements
        ET.SubElement(channel, 'title').text = podcast.title
        ET.SubElement(channel, 'description').text = podcast.description
        ET.SubElement(channel, 'language').text = podcast.language
        ET.SubElement(channel, 'copyright').text = podcast.copyright or f"© {datetime.now().year} {podcast.author}"
        ET.SubElement(channel, 'link').text = podcast.website
        ET.SubElement(channel, 'lastBuildDate').text = self._format_rfc822_date(datetime.now(timezone.utc))

        # Atom link for feed URL
        atom_link = ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link')
        atom_link.set('href', f"{self.base_url}/feed.xml")
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')

        # iTunes/Apple Podcasts metadata
        ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text = podcast.author
        ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}summary').text = podcast.description
        ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit').text = 'yes' if podcast.explicit else 'no'
        ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}type').text = 'episodic'
        ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}complete').text = 'no'

        # iTunes category
        category = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}category')
        category.set('text', podcast.category)
        if podcast.subcategory:
            subcategory = ET.SubElement(category, '{http://www.itunes.com/dtds/podcast-1.0.dtd}category')
            subcategory.set('text', podcast.subcategory)

        # iTunes owner
        owner = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}owner')
        ET.SubElement(owner, '{http://www.itunes.com/dtds/podcast-1.0.dtd}name').text = podcast.owner_name or podcast.author
        ET.SubElement(owner, '{http://www.itunes.com/dtds/podcast-1.0.dtd}email').text = podcast.owner_email or podcast.email

        # iTunes image
        if podcast.artwork_url:
            image = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}image')
            image.set('href', podcast.artwork_url)

        # Spotify metadata
        ET.SubElement(channel, '{http://www.spotify.com/ns/rss}countryOfOrigin').text = 'US'
        ET.SubElement(channel, '{http://www.spotify.com/ns/rss}limit').text = '100'

        # Google Podcasts metadata
        ET.SubElement(channel, '{http://www.google.com/schemas/play-podcasts/1.0}author').text = podcast.author
        ET.SubElement(channel, '{http://www.google.com/schemas/play-podcasts/1.0}email').text = podcast.email

        google_category = ET.SubElement(channel, '{http://www.google.com/schemas/play-podcasts/1.0}category')
        google_category.set('text', podcast.category)

        # Podcast 2.0 namespace elements
        ET.SubElement(channel, '{https://podcastindex.org/namespace/1.0}locked').text = 'no'

        # SEO keywords
        if podcast.keywords:
            ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}keywords').text = ', '.join(podcast.keywords)

    def _add_episode(self, channel: ET.Element, episode: EpisodeMetadata):
        """
        Add episode with rich metadata
        """

        item = ET.SubElement(channel, 'item')

        # Standard RSS elements
        ET.SubElement(item, 'title').text = episode.title
        ET.SubElement(item, 'description').text = self._sanitize_html(episode.description)
        ET.SubElement(item, 'pubDate').text = self._format_rfc822_date(episode.publish_date)
        ET.SubElement(item, 'guid', isPermaLink='false').text = episode.guid
        ET.SubElement(item, 'link').text = f"{self.base_url}/episodes/{episode.guid}"

        # Enclosure (audio file)
        enclosure = ET.SubElement(item, 'enclosure')
        enclosure.set('url', episode.audio_url)
        enclosure.set('type', 'audio/mpeg')
        enclosure.set('length', str(episode.file_size))

        # iTunes metadata
        ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}title').text = episode.title
        ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}summary').text = self._create_summary(episode.description)
        ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}duration').text = self._format_duration(episode.duration)
        ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit').text = 'yes' if episode.explicit else 'no'
        ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}episodeType').text = episode.episode_type

        if episode.episode_number:
            ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}episode').text = str(episode.episode_number)

        if episode.season_number:
            ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}season').text = str(episode.season_number)

        if episode.artwork_url:
            image = ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}image')
            image.set('href', episode.artwork_url)

        # Podcast 2.0 features
        if episode.transcript_url:
            transcript = ET.SubElement(item, '{https://podcastindex.org/namespace/1.0}transcript')
            transcript.set('url', episode.transcript_url)
            transcript.set('type', 'text/vtt')

        if episode.chapters_url:
            chapters = ET.SubElement(item, '{https://podcastindex.org/namespace/1.0}chapters')
            chapters.set('url', episode.chapters_url)
            chapters.set('type', 'application/json+chapters')

        # SEO keywords
        if episode.keywords:
            ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}keywords').text = ', '.join(episode.keywords[:10])

        # Content:encoded for rich HTML content
        content_encoded = ET.SubElement(item, '{http://purl.org/rss/1.0/modules/content/}encoded')
        content_encoded.text = f'<![CDATA[{self._create_rich_content(episode)}]]>'

    def _create_rich_content(self, episode: EpisodeMetadata) -> str:
        """
        Create rich HTML content for episode
        """

        html = f"""
        <div class="episode-content">
            <h2>{episode.title}</h2>
            <p>{episode.description}</p>

            <div class="episode-links">
                <h3>Listen On:</h3>
                <ul>
                    <li><a href="{self.base_url}/episodes/{episode.guid}">Website</a></li>
                    <li><a href="https://podcasts.apple.com/podcast/{episode.guid}">Apple Podcasts</a></li>
                    <li><a href="https://open.spotify.com/episode/{episode.guid}">Spotify</a></li>
                </ul>
            </div>
        """

        if episode.transcript_url:
            html += f"""
            <div class="transcript">
                <h3>Transcript</h3>
                <p><a href="{episode.transcript_url}">View Full Transcript</a></p>
            </div>
            """

        if episode.chapters_url:
            html += f"""
            <div class="chapters">
                <h3>Chapters</h3>
                <p><a href="{episode.chapters_url}">View Chapter Markers</a></p>
            </div>
            """

        html += "</div>"

        return html

    def _format_duration(self, seconds: int) -> str:
        """
        Format duration for iTunes (HH:MM:SS)
        """

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def _format_rfc822_date(self, dt: datetime) -> str:
        """
        Format datetime to RFC 822 format for RSS
        """

        return dt.strftime('%a, %d %b %Y %H:%M:%S %z')

    def _sanitize_html(self, text: str) -> str:
        """
        Sanitize HTML for RSS feed
        """

        # Remove potentially dangerous tags
        text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)

        # Convert line breaks
        text = text.replace('\n', '<br/>')

        return text

    def _create_summary(self, description: str, max_length: int = 4000) -> str:
        """
        Create optimized summary for platforms
        """

        # Remove HTML tags for summary
        summary = re.sub(r'<[^>]+>', '', description)

        # Truncate if needed
        if len(summary) > max_length:
            summary = summary[:max_length-3] + '...'

        return summary

    def _prettify_xml(self, elem: ET.Element) -> str:
        """
        Return a pretty-printed XML string
        """

        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='UTF-8').decode('utf-8')

    def _validate_feed(self, xml_string: str) -> bool:
        """
        Validate RSS feed structure
        """

        try:
            # Basic XML validation
            ET.fromstring(xml_string)

            # Check for required elements
            root = ET.fromstring(xml_string)
            channel = root.find('channel')

            required = ['title', 'description', 'link', 'language']
            for element in required:
                if channel.find(element) is None:
                    logger.error(f"Missing required element: {element}")
                    return False

            return True

        except ET.ParseError as e:
            logger.error(f"XML validation failed: {e}")
            return False


class PodcastDistributor:
    """
    Automated distribution to podcast platforms
    """

    def __init__(self):
        self.platforms = {
            'apple_podcasts': 'https://podcastsconnect.apple.com/api/v1',
            'spotify': 'https://podcasters.spotify.com/api/v1',
            'google_podcasts': 'https://podcastsmanager.google.com/api/v1',
            'amazon_music': 'https://podcasters.amazon.com/api/v1',
            'stitcher': 'https://partners.stitcher.com/api/v1'
        }

    async def submit_to_platforms(self, feed_url: str) -> Dict[str, bool]:
        """
        Submit RSS feed to all major platforms
        """

        results = {}

        for platform, api_url in self.platforms.items():
            try:
                result = await self._submit_to_platform(platform, api_url, feed_url)
                results[platform] = result
                logger.info(f"Submitted to {platform}: {result}")
            except Exception as e:
                logger.error(f"Failed to submit to {platform}: {e}")
                results[platform] = False

        return results

    async def _submit_to_platform(
        self,
        platform: str,
        api_url: str,
        feed_url: str
    ) -> bool:
        """
        Submit feed to specific platform
        """

        # Platform-specific submission logic
        # This would integrate with each platform's API

        if platform == 'apple_podcasts':
            return await self._submit_to_apple(feed_url)
        elif platform == 'spotify':
            return await self._submit_to_spotify(feed_url)
        elif platform == 'google_podcasts':
            return await self._submit_to_google(feed_url)
        else:
            # Generic RSS submission
            return await self._generic_submission(api_url, feed_url)

    async def _submit_to_apple(self, feed_url: str) -> bool:
        """
        Submit to Apple Podcasts
        """

        # Apple Podcasts Connect API integration
        # Requires authentication token
        logger.info(f"Submitting to Apple Podcasts: {feed_url}")
        return True  # Placeholder

    async def _submit_to_spotify(self, feed_url: str) -> bool:
        """
        Submit to Spotify
        """

        # Spotify for Podcasters API integration
        logger.info(f"Submitting to Spotify: {feed_url}")
        return True  # Placeholder

    async def _submit_to_google(self, feed_url: str) -> bool:
        """
        Submit to Google Podcasts
        """

        # Google Podcasts Manager API integration
        logger.info(f"Submitting to Google Podcasts: {feed_url}")
        return True  # Placeholder

    async def _generic_submission(self, api_url: str, feed_url: str) -> bool:
        """
        Generic RSS feed submission
        """

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    api_url,
                    json={'feed_url': feed_url},
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    return response.status == 200
            except Exception as e:
                logger.error(f"Generic submission failed: {e}")
                return False


class SEOOptimizer:
    """
    SEO optimization for podcast discoverability
    """

    def __init__(self):
        self.keyword_weights = {
            'title': 1.0,
            'description': 0.7,
            'transcript': 0.5,
            'tags': 0.3
        }

    def optimize_episode_metadata(
        self,
        episode: EpisodeMetadata,
        target_keywords: List[str]
    ) -> EpisodeMetadata:
        """
        Optimize episode metadata for SEO
        """

        # Optimize title
        episode.title = self._optimize_title(episode.title, target_keywords)

        # Optimize description
        episode.description = self._optimize_description(
            episode.description,
            target_keywords
        )

        # Add relevant keywords
        episode.keywords = self._generate_keywords(episode, target_keywords)

        return episode

    def _optimize_title(self, title: str, keywords: List[str]) -> str:
        """
        Optimize title with keywords while maintaining readability
        """

        # Check if primary keyword is in title
        primary_keyword = keywords[0] if keywords else None

        if primary_keyword and primary_keyword.lower() not in title.lower():
            # Add keyword naturally
            if len(title) + len(primary_keyword) < 60:
                title = f"{title} - {primary_keyword.title()}"

        return title

    def _optimize_description(self, description: str, keywords: List[str]) -> str:
        """
        Optimize description with keyword density
        """

        # Calculate current keyword density
        words = description.lower().split()
        word_count = len(words)

        for keyword in keywords[:3]:  # Top 3 keywords
            keyword_count = description.lower().count(keyword.lower())
            density = keyword_count / max(word_count, 1)

            # Target 1-2% keyword density
            if density < 0.01:
                # Add keyword naturally
                description = f"{description} This episode covers {keyword}."

        return description

    def _generate_keywords(
        self,
        episode: EpisodeMetadata,
        target_keywords: List[str]
    ) -> List[str]:
        """
        Generate comprehensive keyword list
        """

        keywords = set(target_keywords)

        # Extract keywords from title
        title_words = [
            word for word in episode.title.split()
            if len(word) > 4
        ]
        keywords.update(title_words[:5])

        # Add category keywords
        keywords.update(['podcast', 'M&A', 'business', 'entrepreneurship'])

        return list(keywords)[:15]  # Limit to 15 keywords


# Global instances
rss_generator = RSSGenerator(base_url="https://podcast.masaas.com")
podcast_distributor = PodcastDistributor()
seo_optimizer = SEOOptimizer()