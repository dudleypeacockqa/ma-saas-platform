from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.content import Content, PodcastEpisode, ContentTemplate, ContentType, ContentStatus
from app.agents.content_agent import ContentCreationAgent
import logging

logger = logging.getLogger(__name__)


class ContentService:
    """Service layer for content management and generation."""

    def __init__(self, db: Session):
        self.db = db
        self.agent = ContentCreationAgent()

    # CRUD Operations

    def create_content(
        self,
        tenant_id: int,
        user_id: int,
        title: str,
        content_type: ContentType,
        content_body: str,
        metadata: Optional[Dict] = None,
        status: ContentStatus = ContentStatus.DRAFT
    ) -> Content:
        """Create a new content item."""
        content = Content(
            tenant_id=tenant_id,
            user_id=user_id,
            title=title,
            content_type=content_type,
            content_body=content_body,
            metadata=metadata or {},
            status=status
        )
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    def get_content_by_id(self, content_id: int, tenant_id: int) -> Optional[Content]:
        """Get content by ID with tenant isolation."""
        return self.db.query(Content).filter(
            Content.id == content_id,
            Content.tenant_id == tenant_id
        ).first()

    def list_contents(
        self,
        tenant_id: int,
        content_type: Optional[ContentType] = None,
        status: Optional[ContentStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Content]:
        """List contents with filters."""
        query = self.db.query(Content).filter(Content.tenant_id == tenant_id)

        if content_type:
            query = query.filter(Content.content_type == content_type)
        if status:
            query = query.filter(Content.status == status)

        return query.order_by(Content.created_at.desc()).offset(offset).limit(limit).all()

    def update_content(
        self,
        content_id: int,
        tenant_id: int,
        **updates
    ) -> Optional[Content]:
        """Update content item."""
        content = self.get_content_by_id(content_id, tenant_id)
        if not content:
            return None

        for key, value in updates.items():
            if hasattr(content, key):
                setattr(content, key, value)

        self.db.commit()
        self.db.refresh(content)
        return content

    def delete_content(self, content_id: int, tenant_id: int) -> bool:
        """Delete content item."""
        content = self.get_content_by_id(content_id, tenant_id)
        if not content:
            return False

        self.db.delete(content)
        self.db.commit()
        return True

    # Podcast Episode Operations

    def create_podcast_episode(
        self,
        tenant_id: int,
        episode_title: str,
        transcript_text: Optional[str] = None,
        guest_name: Optional[str] = None,
        guest_company: Optional[str] = None,
        episode_number: Optional[int] = None,
        **kwargs
    ) -> PodcastEpisode:
        """Create a podcast episode."""
        episode = PodcastEpisode(
            tenant_id=tenant_id,
            episode_title=episode_title,
            transcript_text=transcript_text,
            guest_name=guest_name,
            guest_company=guest_company,
            episode_number=episode_number,
            **kwargs
        )
        self.db.add(episode)
        self.db.commit()
        self.db.refresh(episode)
        return episode

    def get_podcast_episode(self, episode_id: int, tenant_id: int) -> Optional[PodcastEpisode]:
        """Get podcast episode by ID."""
        return self.db.query(PodcastEpisode).filter(
            PodcastEpisode.id == episode_id,
            PodcastEpisode.tenant_id == tenant_id
        ).first()

    def list_podcast_episodes(
        self,
        tenant_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[PodcastEpisode]:
        """List podcast episodes."""
        return self.db.query(PodcastEpisode).filter(
            PodcastEpisode.tenant_id == tenant_id
        ).order_by(PodcastEpisode.created_at.desc()).offset(offset).limit(limit).all()

    # AI Content Generation

    async def generate_podcast_show_notes(
        self,
        tenant_id: int,
        user_id: int,
        episode_id: int
    ) -> Content:
        """Generate show notes for a podcast episode using AI."""
        episode = self.get_podcast_episode(episode_id, tenant_id)
        if not episode or not episode.transcript_text:
            raise ValueError("Episode not found or missing transcript")

        try:
            # Generate show notes using AI agent
            show_notes_data = await self.agent.generate_podcast_show_notes(
                transcript=episode.transcript_text,
                episode_title=episode.episode_title,
                guest_name=episode.guest_name,
                guest_company=episode.guest_company,
                episode_number=episode.episode_number
            )

            # Format show notes content
            content_body = self._format_show_notes(show_notes_data)

            # Create content record
            content = self.create_content(
                tenant_id=tenant_id,
                user_id=user_id,
                title=show_notes_data.get("title", episode.episode_title),
                content_type=ContentType.PODCAST_SHOW_NOTES,
                content_body=content_body,
                metadata=show_notes_data,
                status=ContentStatus.PENDING_REVIEW
            )

            # Link content to episode
            episode.content_id = content.id
            episode.timestamps = show_notes_data.get("timestamps", [])
            episode.key_takeaways = show_notes_data.get("key_takeaways", [])
            episode.guest_bio = show_notes_data.get("guest_bio", "")
            self.db.commit()

            return content

        except Exception as e:
            logger.error(f"Error generating show notes: {str(e)}")
            raise

    async def generate_social_media_content(
        self,
        tenant_id: int,
        user_id: int,
        source_content_id: int,
        platform: str  # "linkedin", "twitter", "youtube", "instagram"
    ) -> Content:
        """Generate social media content from source content."""
        source = self.get_content_by_id(source_content_id, tenant_id)
        if not source:
            raise ValueError("Source content not found")

        try:
            content_type_map = {
                "linkedin": ContentType.LINKEDIN_POST,
                "twitter": ContentType.TWITTER_THREAD,
                "youtube": ContentType.YOUTUBE_DESCRIPTION,
                "instagram": ContentType.INSTAGRAM_CAPTION
            }

            content_type = content_type_map.get(platform)
            if not content_type:
                raise ValueError(f"Invalid platform: {platform}")

            # Generate platform-specific content
            if platform == "linkedin":
                result = await self.agent.generate_linkedin_post(source.content_body)
                content_body = f"{result['post_text']}\n\n{' '.join(result.get('hashtags', []))}"
                metadata = result

            elif platform == "twitter":
                result = await self.agent.generate_twitter_thread(source.content_body)
                content_body = "\n\n".join([
                    f"{i+1}/{len(result['tweets'])} {tweet}"
                    for i, tweet in enumerate(result['tweets'])
                ])
                metadata = result

            elif platform == "youtube":
                episode = self.db.query(PodcastEpisode).filter(
                    PodcastEpisode.content_id == source_content_id
                ).first()

                result = await self.agent.generate_youtube_description(
                    video_title=source.title,
                    transcript=source.content_body,
                    timestamps=episode.timestamps if episode else None
                )
                content_body = result['description']
                metadata = result

            else:  # instagram
                result = await self.agent.generate_linkedin_post(
                    source.content_body,
                    include_hashtags=True
                )
                content_body = result['post_text'][:2200]  # Instagram limit
                metadata = result

            # Create content record
            content = self.create_content(
                tenant_id=tenant_id,
                user_id=user_id,
                title=f"{platform.title()} Post - {source.title[:100]}",
                content_type=content_type,
                content_body=content_body,
                metadata=metadata,
                status=ContentStatus.PENDING_REVIEW
            )

            return content

        except Exception as e:
            logger.error(f"Error generating {platform} content: {str(e)}")
            raise

    async def generate_blog_article(
        self,
        tenant_id: int,
        user_id: int,
        topic: str,
        source_content_id: Optional[int] = None,
        seo_keywords: Optional[List[str]] = None
    ) -> Content:
        """Generate a blog article using AI."""
        source_content = None
        if source_content_id:
            source_content = self.get_content_by_id(source_content_id, tenant_id)

        try:
            result = await self.agent.generate_blog_article(
                topic=topic,
                source_content=source_content.content_body if source_content else None,
                seo_keywords=seo_keywords
            )

            content = self.create_content(
                tenant_id=tenant_id,
                user_id=user_id,
                title=result.get("title", topic),
                content_type=ContentType.BLOG_ARTICLE,
                content_body=result.get("content", ""),
                metadata={
                    "slug": result.get("slug"),
                    "meta_description": result.get("meta_description"),
                    "excerpt": result.get("excerpt"),
                    "seo_keywords": result.get("seo_keywords", [])
                },
                status=ContentStatus.PENDING_REVIEW
            )

            return content

        except Exception as e:
            logger.error(f"Error generating blog article: {str(e)}")
            raise

    async def generate_newsletter(
        self,
        tenant_id: int,
        user_id: int,
        recent_episode_ids: List[int],
        market_insights: Optional[str] = None
    ) -> Content:
        """Generate email newsletter content."""
        try:
            episodes = []
            for ep_id in recent_episode_ids:
                episode = self.get_podcast_episode(ep_id, tenant_id)
                if episode:
                    episodes.append({
                        "title": episode.episode_title,
                        "guest": episode.guest_name or "N/A"
                    })

            result = await self.agent.generate_newsletter_content(
                recent_episodes=episodes,
                market_insights=market_insights
            )

            content = self.create_content(
                tenant_id=tenant_id,
                user_id=user_id,
                title=result.get("subject_line", "Weekly Newsletter"),
                content_type=ContentType.EMAIL_NEWSLETTER,
                content_body=result.get("content", ""),
                metadata={
                    "subject_line": result.get("subject_line"),
                    "preview_text": result.get("preview_text")
                },
                status=ContentStatus.PENDING_REVIEW
            )

            return content

        except Exception as e:
            logger.error(f"Error generating newsletter: {str(e)}")
            raise

    async def validate_and_score_content(
        self,
        content_id: int,
        tenant_id: int
    ) -> Dict[str, Any]:
        """Validate content quality and get improvement suggestions."""
        content = self.get_content_by_id(content_id, tenant_id)
        if not content:
            raise ValueError("Content not found")

        try:
            validation_result = await self.agent.validate_content_quality(
                content=content.content_body,
                content_type=content.content_type.value
            )

            # Update content metadata with quality scores
            metadata = content.metadata or {}
            metadata["quality_score"] = validation_result.get("quality_score")
            metadata["seo_score"] = validation_result.get("seo_score")
            metadata["last_validated"] = datetime.utcnow().isoformat()

            self.update_content(content_id, tenant_id, metadata=metadata)

            return validation_result

        except Exception as e:
            logger.error(f"Error validating content: {str(e)}")
            raise

    # Helper Methods

    def _format_show_notes(self, show_notes_data: Dict[str, Any]) -> str:
        """Format show notes data into markdown."""
        content = f"# {show_notes_data.get('title', '')}\n\n"
        content += f"{show_notes_data.get('summary', '')}\n\n"

        if show_notes_data.get('guest_bio'):
            content += f"## About the Guest\n\n{show_notes_data['guest_bio']}\n\n"

        if show_notes_data.get('timestamps'):
            content += "## Timestamps\n\n"
            for ts in show_notes_data['timestamps']:
                if isinstance(ts, dict):
                    content += f"- {ts.get('time', '')} - {ts.get('topic', '')}\n"
                else:
                    content += f"- {ts}\n"
            content += "\n"

        if show_notes_data.get('key_takeaways'):
            content += "## Key Takeaways\n\n"
            for takeaway in show_notes_data['key_takeaways']:
                content += f"- {takeaway}\n"
            content += "\n"

        if show_notes_data.get('resources'):
            content += "## Resources Mentioned\n\n"
            for resource in show_notes_data['resources']:
                content += f"- {resource}\n"
            content += "\n"

        if show_notes_data.get('cta'):
            content += f"## {show_notes_data['cta']}\n"

        return content
