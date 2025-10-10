"""
Buzzsprout Podcast Hosting API Integration
Manages podcast episodes, analytics, and distribution
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx

from app.integrations.platform_connectors import (
    APIKeyPlatformConnector,
    PlatformType,
    PlatformCredentials,
    SyncResult
)

logger = logging.getLogger(__name__)


class BuzzsproutConnector(APIKeyPlatformConnector):
    """Buzzsprout API connector for podcast management"""

    def __init__(
        self,
        credentials: PlatformCredentials,
        organization_id: str,
        podcast_id: str,
        rate_limit_per_minute: int = 60
    ):
        super().__init__(credentials, organization_id, rate_limit_per_minute)
        self.podcast_id = podcast_id

    @property
    def platform_name(self) -> str:
        return "buzzsprout"

    @property
    def platform_type(self) -> PlatformType:
        return PlatformType.PODCAST

    @property
    def base_url(self) -> str:
        return f"https://www.buzzsprout.com/api/{self.podcast_id}"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Token token={self.credentials.api_key}",
            "Content-Type": "application/json"
        }

    async def test_connection(self) -> bool:
        """Test Buzzsprout API connection"""
        try:
            response = await self.http_client.get("/episodes.json")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Buzzsprout connection test failed: {e}")
            return False

    async def get_episodes(
        self,
        limit: int = 10,
        published_since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get podcast episodes"""
        try:
            params = {}
            if published_since:
                params["since"] = published_since.isoformat()

            response = await self.http_client.get(
                "/episodes.json",
                params=params
            )

            if response.status_code == 200:
                episodes = response.json()
                return episodes[:limit] if limit else episodes

        except Exception as e:
            logger.error(f"Failed to get episodes: {e}")

        return []

    async def get_episode(self, episode_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific episode"""
        try:
            response = await self.http_client.get(f"/episodes/{episode_id}.json")

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get episode {episode_id}: {e}")

        return None

    async def create_episode(
        self,
        title: str,
        description: str,
        audio_url: Optional[str] = None,
        published_at: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Create a new podcast episode"""
        try:
            episode_data = {
                "title": title,
                "description": description
            }

            if audio_url:
                episode_data["audio_url"] = audio_url

            if published_at:
                episode_data["published_at"] = published_at.isoformat()

            if tags:
                episode_data["tags"] = ",".join(tags)

            # Add any additional fields
            episode_data.update(kwargs)

            response = await self.http_client.post(
                "/episodes.json",
                json=episode_data
            )

            if response.status_code == 201:
                return response.json()

        except Exception as e:
            logger.error(f"Failed to create episode: {e}")

        return None

    async def update_episode(
        self,
        episode_id: str,
        **updates
    ) -> Optional[Dict[str, Any]]:
        """Update an existing episode"""
        try:
            response = await self.http_client.put(
                f"/episodes/{episode_id}.json",
                json=updates
            )

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.error(f"Failed to update episode {episode_id}: {e}")

        return None

    async def delete_episode(self, episode_id: str) -> bool:
        """Delete an episode"""
        try:
            response = await self.http_client.delete(f"/episodes/{episode_id}.json")
            return response.status_code == 204

        except Exception as e:
            logger.error(f"Failed to delete episode {episode_id}: {e}")
            return False

    async def get_episode_stats(
        self,
        episode_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Get episode or show statistics"""
        try:
            endpoint = "/stats.json"
            params = {}

            if episode_id:
                params["episode_id"] = episode_id

            if start_date:
                params["start_date"] = start_date.strftime("%Y-%m-%d")

            if end_date:
                params["end_date"] = end_date.strftime("%Y-%m-%d")

            response = await self.http_client.get(endpoint, params=params)

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")

        return None

    async def get_downloads(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Get download statistics"""
        try:
            params = {}

            if start_date:
                params["start_date"] = start_date.strftime("%Y-%m-%d")

            if end_date:
                params["end_date"] = end_date.strftime("%Y-%m-%d")

            response = await self.http_client.get("/downloads.json", params=params)

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get downloads: {e}")

        return None

    async def sync_data(
        self,
        sync_type: str,
        since: Optional[datetime] = None
    ) -> SyncResult:
        """Sync Buzzsprout data"""
        synced_count = 0
        errors = []

        try:
            if sync_type == "episodes":
                episodes = await self.get_episodes(
                    limit=None,
                    published_since=since
                )
                synced_count = len(episodes)

            elif sync_type == "stats":
                stats = await self.get_episode_stats(
                    start_date=since or datetime.now() - timedelta(days=30)
                )
                if stats:
                    synced_count = 1
                else:
                    errors.append("Failed to sync stats")

            self.last_sync = datetime.utcnow()

        except Exception as e:
            errors.append(str(e))

        return SyncResult(
            success=len(errors) == 0,
            items_synced=synced_count,
            items_failed=len(errors),
            errors=errors
        )

    async def push_data(
        self,
        data_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """Push data to Buzzsprout"""
        if data_type == "episode":
            result = await self.create_episode(
                title=data.get("title", ""),
                description=data.get("description", ""),
                audio_url=data.get("audio_url"),
                published_at=data.get("published_at"),
                tags=data.get("tags"),
                **{k: v for k, v in data.items() if k not in ["title", "description", "audio_url", "published_at", "tags"]}
            )
            return result is not None

        elif data_type == "update":
            result = await self.update_episode(
                episode_id=data.get("episode_id"),
                **{k: v for k, v in data.items() if k != "episode_id"}
            )
            return result is not None

        return False


class CaptivateConnector(APIKeyPlatformConnector):
    """Captivate.fm podcast hosting integration (alternative to Buzzsprout)"""

    @property
    def platform_name(self) -> str:
        return "captivate"

    @property
    def platform_type(self) -> PlatformType:
        return PlatformType.PODCAST

    @property
    def base_url(self) -> str:
        return "https://api.captivate.fm/v1"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.credentials.api_key}",
            "Content-Type": "application/json"
        }

    async def test_connection(self) -> bool:
        """Test Captivate API connection"""
        try:
            response = await self.http_client.get("/shows")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Captivate connection test failed: {e}")
            return False

    async def get_shows(self) -> List[Dict[str, Any]]:
        """Get all shows"""
        try:
            response = await self.http_client.get("/shows")

            if response.status_code == 200:
                data = response.json()
                return data.get("shows", [])

        except Exception as e:
            logger.error(f"Failed to get shows: {e}")

        return []

    async def get_episodes(
        self,
        show_id: str,
        page: int = 1,
        per_page: int = 50
    ) -> List[Dict[str, Any]]:
        """Get episodes for a show"""
        try:
            response = await self.http_client.get(
                f"/shows/{show_id}/episodes",
                params={"page": page, "per_page": per_page}
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("episodes", [])

        except Exception as e:
            logger.error(f"Failed to get episodes: {e}")

        return []

    async def sync_data(
        self,
        sync_type: str,
        since: Optional[datetime] = None
    ) -> SyncResult:
        """Sync Captivate data"""
        synced_count = 0
        errors = []

        try:
            if sync_type == "shows":
                shows = await self.get_shows()
                synced_count = len(shows)

            elif sync_type == "episodes":
                shows = await self.get_shows()
                for show in shows:
                    episodes = await self.get_episodes(show["id"])
                    synced_count += len(episodes)

            self.last_sync = datetime.utcnow()

        except Exception as e:
            errors.append(str(e))

        return SyncResult(
            success=len(errors) == 0,
            items_synced=synced_count,
            items_failed=len(errors),
            errors=errors
        )

    async def push_data(
        self,
        data_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """Push data to Captivate"""
        # Implement based on Captivate API documentation
        logger.warning("Captivate push_data not yet implemented")
        return False
