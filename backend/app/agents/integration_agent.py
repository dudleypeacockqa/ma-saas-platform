"""
Integration Orchestration Agent
Manages and coordinates all platform integrations, data synchronization, and workflows
"""

import os
import logging
from typing import Dict, List, Optional, Any, Type
from datetime import datetime, timedelta
import asyncio
from enum import Enum

from app.integrations.platform_connectors import (
    BasePlatformConnector,
    PlatformCredentials,
    PlatformType,
    ConnectionStatus
)
from app.integrations.stripe_service import stripe_service
from app.integrations.social_media_apis import (
    LinkedInConnector,
    TwitterConnector,
    YouTubeConnector
)
from app.integrations.buzzsprout_api import BuzzsproutConnector, CaptivateConnector
from app.integrations.crm_apis import HubSpotConnector, PipedriveConnector

logger = logging.getLogger(__name__)


class IntegrationPlatform(str, Enum):
    """Supported integration platforms"""
    STRIPE = "stripe"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    BUZZSPROUT = "buzzsprout"
    CAPTIVATE = "captivate"
    HUBSPOT = "hubspot"
    PIPEDRIVE = "pipedrive"


class IntegrationAgent:
    """
    Central agent for managing all platform integrations
    Orchestrates connections, data sync, and cross-platform workflows
    """

    # Platform connector registry
    CONNECTOR_REGISTRY: Dict[str, Type[BasePlatformConnector]] = {
        IntegrationPlatform.LINKEDIN: LinkedInConnector,
        IntegrationPlatform.TWITTER: TwitterConnector,
        IntegrationPlatform.YOUTUBE: YouTubeConnector,
        IntegrationPlatform.BUZZSPROUT: BuzzsproutConnector,
        IntegrationPlatform.CAPTIVATE: CaptivateConnector,
        IntegrationPlatform.HUBSPOT: HubSpotConnector,
        IntegrationPlatform.PIPEDRIVE: PipedriveConnector
    }

    def __init__(self, organization_id: str):
        self.organization_id = organization_id
        self.connectors: Dict[str, BasePlatformConnector] = {}
        self.sync_tasks: Dict[str, asyncio.Task] = {}
        self._initialized = False

    async def initialize(self, credentials_map: Dict[str, PlatformCredentials]) -> bool:
        """
        Initialize all platform connections

        Args:
            credentials_map: Dict mapping platform names to credentials

        Returns:
            True if at least one platform connected successfully
        """
        success_count = 0

        for platform_name, credentials in credentials_map.items():
            try:
                success = await self.connect_platform(platform_name, credentials)
                if success:
                    success_count += 1
                    logger.info(f"Connected to {platform_name} for org {self.organization_id}")
                else:
                    logger.warning(f"Failed to connect to {platform_name} for org {self.organization_id}")

            except Exception as e:
                logger.error(f"Error initializing {platform_name}: {e}")

        self._initialized = success_count > 0
        return self._initialized

    async def connect_platform(
        self,
        platform_name: str,
        credentials: PlatformCredentials,
        **kwargs
    ) -> bool:
        """Connect to a specific platform"""
        connector_class = self.CONNECTOR_REGISTRY.get(platform_name)

        if not connector_class:
            logger.error(f"Unknown platform: {platform_name}")
            return False

        try:
            # Create connector instance
            connector = connector_class(
                credentials=credentials,
                organization_id=self.organization_id,
                **kwargs
            )

            # Initialize connection
            connected = await connector.initialize()

            if connected:
                self.connectors[platform_name] = connector
                return True

        except Exception as e:
            logger.error(f"Failed to connect to {platform_name}: {e}")

        return False

    async def disconnect_platform(self, platform_name: str) -> bool:
        """Disconnect from a platform"""
        if platform_name in self.connectors:
            try:
                await self.connectors[platform_name].close()
                del self.connectors[platform_name]

                # Cancel any running sync tasks
                if platform_name in self.sync_tasks:
                    self.sync_tasks[platform_name].cancel()
                    del self.sync_tasks[platform_name]

                return True

            except Exception as e:
                logger.error(f"Error disconnecting from {platform_name}: {e}")

        return False

    async def sync_platform_data(
        self,
        platform_name: str,
        sync_type: str,
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Sync data from a specific platform"""
        connector = self.connectors.get(platform_name)

        if not connector:
            return {
                "success": False,
                "error": f"Platform {platform_name} not connected"
            }

        try:
            result = await connector.sync_data(sync_type, since=since)

            return {
                "success": result.success,
                "items_synced": result.items_synced,
                "items_failed": result.items_failed,
                "errors": result.errors,
                "synced_at": result.synced_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Sync failed for {platform_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def sync_all_platforms(
        self,
        sync_configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Sync data from all connected platforms

        Args:
            sync_configs: Dict mapping platform names to sync config
                          e.g., {"linkedin": {"sync_type": "posts", "since": datetime}}

        Returns:
            Summary of sync results for all platforms
        """
        results = {}

        # Create sync tasks for all platforms
        sync_tasks = []
        platform_names = []

        for platform_name, config in sync_configs.items():
            if platform_name in self.connectors:
                task = self.sync_platform_data(
                    platform_name=platform_name,
                    sync_type=config.get("sync_type", "all"),
                    since=config.get("since")
                )
                sync_tasks.append(task)
                platform_names.append(platform_name)

        # Execute all syncs concurrently
        if sync_tasks:
            sync_results = await asyncio.gather(*sync_tasks, return_exceptions=True)

            for platform_name, result in zip(platform_names, sync_results):
                if isinstance(result, Exception):
                    results[platform_name] = {
                        "success": False,
                        "error": str(result)
                    }
                else:
                    results[platform_name] = result

        return {
            "organization_id": self.organization_id,
            "sync_time": datetime.utcnow().isoformat(),
            "platforms_synced": len(results),
            "results": results
        }

    async def push_to_platform(
        self,
        platform_name: str,
        data_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """Push data to a specific platform"""
        connector = self.connectors.get(platform_name)

        if not connector:
            logger.error(f"Platform {platform_name} not connected")
            return False

        try:
            return await connector.push_data(data_type, data)

        except Exception as e:
            logger.error(f"Failed to push data to {platform_name}: {e}")
            return False

    async def cross_platform_publish(
        self,
        content: str,
        platforms: List[str],
        content_type: str = "post",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """
        Publish content to multiple platforms simultaneously

        Args:
            content: Content to publish
            platforms: List of platform names
            content_type: Type of content (post, tweet, video, etc.)
            metadata: Platform-specific metadata

        Returns:
            Dict mapping platform names to success status
        """
        results = {}
        publish_tasks = []
        platform_list = []

        for platform_name in platforms:
            if platform_name in self.connectors:
                # Prepare platform-specific data
                platform_data = {
                    "text": content,
                    **(metadata or {})
                }

                task = self.push_to_platform(
                    platform_name=platform_name,
                    data_type=content_type,
                    data=platform_data
                )
                publish_tasks.append(task)
                platform_list.append(platform_name)

        # Execute all publishes concurrently
        if publish_tasks:
            publish_results = await asyncio.gather(*publish_tasks, return_exceptions=True)

            for platform_name, result in zip(platform_list, publish_results):
                if isinstance(result, Exception):
                    results[platform_name] = False
                    logger.error(f"Failed to publish to {platform_name}: {result}")
                else:
                    results[platform_name] = result

        return results

    async def schedule_periodic_sync(
        self,
        platform_name: str,
        sync_type: str,
        interval_minutes: int = 60
    ):
        """Schedule periodic data synchronization for a platform"""
        async def sync_loop():
            while True:
                try:
                    await asyncio.sleep(interval_minutes * 60)
                    await self.sync_platform_data(platform_name, sync_type)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Periodic sync error for {platform_name}: {e}")

        # Cancel existing task if any
        if platform_name in self.sync_tasks:
            self.sync_tasks[platform_name].cancel()

        # Start new sync task
        task = asyncio.create_task(sync_loop())
        self.sync_tasks[platform_name] = task

    def get_platform_status(self, platform_name: Optional[str] = None) -> Dict[str, Any]:
        """Get status of one or all platforms"""
        if platform_name:
            connector = self.connectors.get(platform_name)
            if connector:
                return connector.get_status()
            return {"error": f"Platform {platform_name} not connected"}

        # Return status of all platforms
        return {
            platform_name: connector.get_status()
            for platform_name, connector in self.connectors.items()
        }

    def get_connected_platforms(self) -> List[str]:
        """Get list of connected platform names"""
        return list(self.connectors.keys())

    def is_platform_connected(self, platform_name: str) -> bool:
        """Check if a platform is connected"""
        connector = self.connectors.get(platform_name)
        if connector:
            return connector.connection_status == ConnectionStatus.CONNECTED
        return False

    async def test_all_connections(self) -> Dict[str, bool]:
        """Test all platform connections"""
        results = {}

        for platform_name, connector in self.connectors.items():
            try:
                is_connected = await connector.test_connection()
                results[platform_name] = is_connected
            except Exception as e:
                logger.error(f"Connection test failed for {platform_name}: {e}")
                results[platform_name] = False

        return results

    async def shutdown(self):
        """Shutdown all connections and tasks"""
        # Cancel all sync tasks
        for task in self.sync_tasks.values():
            task.cancel()

        self.sync_tasks.clear()

        # Close all connections
        for platform_name in list(self.connectors.keys()):
            await self.disconnect_platform(platform_name)

        logger.info(f"Integration agent shutdown for org {self.organization_id}")


# Global registry of integration agents by organization
_agent_registry: Dict[str, IntegrationAgent] = {}


def get_integration_agent(organization_id: str) -> IntegrationAgent:
    """Get or create integration agent for an organization"""
    if organization_id not in _agent_registry:
        _agent_registry[organization_id] = IntegrationAgent(organization_id)

    return _agent_registry[organization_id]


async def cleanup_agent(organization_id: str):
    """Cleanup and remove integration agent"""
    if organization_id in _agent_registry:
        agent = _agent_registry[organization_id]
        await agent.shutdown()
        del _agent_registry[organization_id]
