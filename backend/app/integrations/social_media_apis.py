"""
Social Media Platform Integrations
LinkedIn, Twitter/X, YouTube API connectors
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from urllib.parse import urlencode

from app.integrations.platform_connectors import (
    BasePlatformConnector,
    OAuthPlatformConnector,
    PlatformType,
    PlatformCredentials,
    SyncResult,
    ConnectionStatus
)

logger = logging.getLogger(__name__)


class LinkedInConnector(OAuthPlatformConnector):
    """LinkedIn API connector for profile, posts, and company data"""

    @property
    def platform_name(self) -> str:
        return "linkedin"

    @property
    def platform_type(self) -> PlatformType:
        return PlatformType.SOCIAL_MEDIA

    @property
    def base_url(self) -> str:
        return "https://api.linkedin.com/v2"

    @property
    def oauth_authorize_url(self) -> str:
        return "https://www.linkedin.com/oauth/v2/authorization"

    @property
    def oauth_token_url(self) -> str:
        return "https://www.linkedin.com/oauth/v2/accessToken"

    @property
    def oauth_scopes(self) -> List[str]:
        return [
            "r_liteprofile",
            "r_emailaddress",
            "w_member_social",
            "r_organization_social",
            "w_organization_social"
        ]

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.credentials.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

    async def test_connection(self) -> bool:
        """Test LinkedIn API connection"""
        try:
            response = await self.http_client.get("/me")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"LinkedIn connection test failed: {e}")
            return False

    async def get_profile(self) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        try:
            response = await self.http_client.get(
                "/me",
                params={
                    "projection": "(id,firstName,lastName,profilePicture(displayImage~:playableStreams))"
                }
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get LinkedIn profile: {e}")
        return None

    async def create_post(
        self,
        text: str,
        visibility: str = "PUBLIC",
        media_urls: Optional[List[str]] = None
    ) -> bool:
        """Create a LinkedIn post"""
        try:
            profile = await self.get_profile()
            if not profile:
                return False

            post_data = {
                "author": f"urn:li:person:{profile['id']}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }

            response = await self.http_client.post(
                "/ugcPosts",
                json=post_data
            )

            return response.status_code == 201

        except Exception as e:
            logger.error(f"Failed to create LinkedIn post: {e}")
            return False

    async def get_company_posts(
        self,
        company_id: str,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """Get posts from a company page"""
        try:
            response = await self.http_client.get(
                "/ugcPosts",
                params={
                    "q": "authors",
                    "authors": f"List(urn:li:organization:{company_id})",
                    "count": count
                }
            )

            if response.status_code == 200:
                return response.json().get("elements", [])

        except Exception as e:
            logger.error(f"Failed to get company posts: {e}")

        return []

    async def sync_data(
        self,
        sync_type: str,
        since: Optional[datetime] = None
    ) -> SyncResult:
        """Sync LinkedIn data"""
        synced_count = 0
        errors = []

        try:
            if sync_type == "profile":
                profile = await self.get_profile()
                if profile:
                    synced_count = 1
                else:
                    errors.append("Failed to sync profile")

            elif sync_type == "posts":
                posts = await self.get_company_posts("", count=50)
                synced_count = len(posts)

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
        """Push data to LinkedIn"""
        if data_type == "post":
            return await self.create_post(
                text=data.get("text", ""),
                visibility=data.get("visibility", "PUBLIC"),
                media_urls=data.get("media_urls")
            )
        return False


class TwitterConnector(OAuthPlatformConnector):
    """Twitter/X API connector"""

    @property
    def platform_name(self) -> str:
        return "twitter"

    @property
    def platform_type(self) -> PlatformType:
        return PlatformType.SOCIAL_MEDIA

    @property
    def base_url(self) -> str:
        return "https://api.twitter.com/2"

    @property
    def oauth_authorize_url(self) -> str:
        return "https://twitter.com/i/oauth2/authorize"

    @property
    def oauth_token_url(self) -> str:
        return "https://api.twitter.com/2/oauth2/token"

    @property
    def oauth_scopes(self) -> List[str]:
        return [
            "tweet.read",
            "tweet.write",
            "users.read",
            "offline.access"
        ]

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.credentials.access_token}",
            "Content-Type": "application/json"
        }

    async def test_connection(self) -> bool:
        """Test Twitter API connection"""
        try:
            response = await self.http_client.get("/users/me")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Twitter connection test failed: {e}")
            return False

    async def create_tweet(
        self,
        text: str,
        reply_to: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a tweet"""
        try:
            tweet_data = {"text": text}

            if reply_to:
                tweet_data["reply"] = {"in_reply_to_tweet_id": reply_to}

            response = await self.http_client.post(
                "/tweets",
                json=tweet_data
            )

            if response.status_code == 201:
                return response.json()

        except Exception as e:
            logger.error(f"Failed to create tweet: {e}")

        return None

    async def get_user_tweets(
        self,
        user_id: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user's tweets"""
        try:
            response = await self.http_client.get(
                f"/users/{user_id}/tweets",
                params={
                    "max_results": max_results,
                    "tweet.fields": "created_at,public_metrics,entities"
                }
            )

            if response.status_code == 200:
                return response.json().get("data", [])

        except Exception as e:
            logger.error(f"Failed to get tweets: {e}")

        return []

    async def sync_data(
        self,
        sync_type: str,
        since: Optional[datetime] = None
    ) -> SyncResult:
        """Sync Twitter data"""
        synced_count = 0
        errors = []

        try:
            if sync_type == "tweets":
                # Get authenticated user's tweets
                me_response = await self.http_client.get("/users/me")
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    tweets = await self.get_user_tweets(user_data["data"]["id"])
                    synced_count = len(tweets)
                else:
                    errors.append("Failed to get user info")

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
        """Push data to Twitter"""
        if data_type == "tweet":
            result = await self.create_tweet(
                text=data.get("text", ""),
                reply_to=data.get("reply_to")
            )
            return result is not None
        return False


class YouTubeConnector(OAuthPlatformConnector):
    """YouTube Data API connector"""

    @property
    def platform_name(self) -> str:
        return "youtube"

    @property
    def platform_type(self) -> PlatformType:
        return PlatformType.SOCIAL_MEDIA

    @property
    def base_url(self) -> str:
        return "https://www.googleapis.com/youtube/v3"

    @property
    def oauth_authorize_url(self) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth"

    @property
    def oauth_token_url(self) -> str:
        return "https://oauth2.googleapis.com/token"

    @property
    def oauth_scopes(self) -> List[str]:
        return [
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.force-ssl"
        ]

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.credentials.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def test_connection(self) -> bool:
        """Test YouTube API connection"""
        try:
            response = await self.http_client.get(
                "/channels",
                params={"part": "snippet", "mine": "true"}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"YouTube connection test failed: {e}")
            return False

    async def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """Get authenticated user's channel information"""
        try:
            response = await self.http_client.get(
                "/channels",
                params={
                    "part": "snippet,contentDetails,statistics",
                    "mine": "true"
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    return data["items"][0]

        except Exception as e:
            logger.error(f"Failed to get channel info: {e}")

        return None

    async def get_channel_videos(
        self,
        channel_id: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Get videos from a channel"""
        try:
            # First, get the uploads playlist ID
            channel_response = await self.http_client.get(
                "/channels",
                params={
                    "part": "contentDetails",
                    "id": channel_id
                }
            )

            if channel_response.status_code != 200:
                return []

            channel_data = channel_response.json()
            if not channel_data.get("items"):
                return []

            uploads_playlist = channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

            # Get videos from uploads playlist
            videos_response = await self.http_client.get(
                "/playlistItems",
                params={
                    "part": "snippet,contentDetails",
                    "playlistId": uploads_playlist,
                    "maxResults": max_results
                }
            )

            if videos_response.status_code == 200:
                return videos_response.json().get("items", [])

        except Exception as e:
            logger.error(f"Failed to get channel videos: {e}")

        return []

    async def get_video_analytics(
        self,
        video_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get analytics for a specific video"""
        try:
            response = await self.http_client.get(
                "/videos",
                params={
                    "part": "statistics,snippet",
                    "id": video_id
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    return data["items"][0]

        except Exception as e:
            logger.error(f"Failed to get video analytics: {e}")

        return None

    async def sync_data(
        self,
        sync_type: str,
        since: Optional[datetime] = None
    ) -> SyncResult:
        """Sync YouTube data"""
        synced_count = 0
        errors = []

        try:
            if sync_type == "channel":
                channel = await self.get_channel_info()
                if channel:
                    synced_count = 1
                else:
                    errors.append("Failed to sync channel info")

            elif sync_type == "videos":
                channel = await self.get_channel_info()
                if channel:
                    videos = await self.get_channel_videos(
                        channel["id"],
                        max_results=50
                    )
                    synced_count = len(videos)
                else:
                    errors.append("Failed to get channel for video sync")

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
        """Push data to YouTube (e.g., upload video)"""
        # YouTube video upload requires different handling
        # This would need multipart upload implementation
        logger.warning("YouTube push_data not yet implemented")
        return False
