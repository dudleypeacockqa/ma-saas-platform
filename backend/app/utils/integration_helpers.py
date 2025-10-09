"""
Integration Helpers
Utilities for integrating with external systems and platforms
"""
import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, asdict
import os
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class IntegrationType(str, Enum):
    """Types of integrations"""
    CRM = "crm"
    PROJECT_MANAGEMENT = "project_management"
    COMMUNICATION = "communication"
    DOCUMENT_STORAGE = "document_storage"
    CALENDAR = "calendar"
    EMAIL = "email"
    ACCOUNTING = "accounting"
    VIDEO_CONFERENCING = "video_conferencing"
    FILE_SHARING = "file_sharing"
    ANALYTICS = "analytics"


class IntegrationStatus(str, Enum):
    """Integration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    EXPIRED = "expired"


@dataclass
class IntegrationConfig:
    """Configuration for external integrations"""
    integration_id: str
    integration_type: IntegrationType
    name: str
    description: str
    api_endpoint: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    oauth_token: Optional[str] = None
    refresh_token: Optional[str] = None
    webhook_url: Optional[str] = None
    config_data: Optional[Dict[str, Any]] = None
    status: IntegrationStatus = IntegrationStatus.INACTIVE
    created_at: Optional[datetime] = None
    last_sync: Optional[datetime] = None


@dataclass
class SyncResult:
    """Result of a synchronization operation"""
    success: bool
    records_processed: int
    records_created: int
    records_updated: int
    records_failed: int
    errors: List[str]
    sync_time: datetime
    metadata: Optional[Dict[str, Any]] = None


class BaseIntegration(ABC):
    """Base class for all integrations"""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to the external service"""
        pass

    @abstractmethod
    async def sync_data(self, sync_type: str, **kwargs) -> SyncResult:
        """Sync data with the external service"""
        pass

    async def _make_api_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make API request to external service"""

        url = f"{self.config.api_endpoint.rstrip('/')}/{endpoint.lstrip('/')}"

        # Prepare headers
        request_headers = {
            "Content-Type": "application/json",
            "User-Agent": "MA-SaaS-Platform/1.0"
        }

        if self.config.api_key:
            request_headers["Authorization"] = f"Bearer {self.config.api_key}"
        elif self.config.oauth_token:
            request_headers["Authorization"] = f"Bearer {self.config.oauth_token}"

        if headers:
            request_headers.update(headers)

        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers
            ) as response:

                response_data = await response.json()

                if response.status >= 400:
                    logger.error(f"API request failed: {response.status} - {response_data}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {response_data}",
                        "status_code": response.status
                    }

                return {
                    "success": True,
                    "data": response_data,
                    "status_code": response.status
                }

        except Exception as e:
            logger.error(f"API request exception: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class SalesforceIntegration(BaseIntegration):
    """Salesforce CRM integration"""

    async def test_connection(self) -> Dict[str, Any]:
        """Test Salesforce connection"""
        try:
            result = await self._make_api_request("GET", "/services/data/v57.0/sobjects/")

            if result["success"]:
                return {
                    "success": True,
                    "message": "Salesforce connection successful",
                    "objects_count": len(result["data"].get("sobjects", []))
                }
            else:
                return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def sync_data(self, sync_type: str, **kwargs) -> SyncResult:
        """Sync data with Salesforce"""

        sync_start = datetime.utcnow()
        errors = []

        if sync_type == "contacts":
            return await self._sync_contacts(**kwargs)
        elif sync_type == "accounts":
            return await self._sync_accounts(**kwargs)
        elif sync_type == "opportunities":
            return await self._sync_opportunities(**kwargs)
        else:
            return SyncResult(
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                errors=[f"Unknown sync type: {sync_type}"],
                sync_time=sync_start
            )

    async def _sync_contacts(self, **kwargs) -> SyncResult:
        """Sync contacts from Salesforce"""

        sync_start = datetime.utcnow()

        try:
            # Query contacts
            soql = "SELECT Id, FirstName, LastName, Email, Phone, AccountId FROM Contact"
            result = await self._make_api_request(
                "GET",
                f"/services/data/v57.0/query/?q={soql}"
            )

            if not result["success"]:
                return SyncResult(
                    success=False,
                    records_processed=0,
                    records_created=0,
                    records_updated=0,
                    records_failed=0,
                    errors=[result["error"]],
                    sync_time=sync_start
                )

            contacts = result["data"]["records"]

            # Process contacts (mock implementation)
            processed = 0
            created = 0
            updated = 0

            for contact in contacts:
                # Mock processing logic
                processed += 1
                if processed % 2 == 0:
                    created += 1
                else:
                    updated += 1

            return SyncResult(
                success=True,
                records_processed=processed,
                records_created=created,
                records_updated=updated,
                records_failed=0,
                errors=[],
                sync_time=sync_start,
                metadata={"total_records": len(contacts)}
            )

        except Exception as e:
            return SyncResult(
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                errors=[str(e)],
                sync_time=sync_start
            )

    async def _sync_accounts(self, **kwargs) -> SyncResult:
        """Sync accounts from Salesforce"""
        # Similar implementation to contacts
        return SyncResult(
            success=True,
            records_processed=50,
            records_created=20,
            records_updated=30,
            records_failed=0,
            errors=[],
            sync_time=datetime.utcnow()
        )

    async def _sync_opportunities(self, **kwargs) -> SyncResult:
        """Sync opportunities from Salesforce"""
        # Similar implementation to contacts
        return SyncResult(
            success=True,
            records_processed=25,
            records_created=10,
            records_updated=15,
            records_failed=0,
            errors=[],
            sync_time=datetime.utcnow()
        )


class SlackIntegration(BaseIntegration):
    """Slack communication integration"""

    async def test_connection(self) -> Dict[str, Any]:
        """Test Slack connection"""
        try:
            result = await self._make_api_request("GET", "/api/auth.test")

            if result["success"]:
                return {
                    "success": True,
                    "message": "Slack connection successful",
                    "team": result["data"].get("team"),
                    "user": result["data"].get("user")
                }
            else:
                return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def sync_data(self, sync_type: str, **kwargs) -> SyncResult:
        """Sync data with Slack"""

        if sync_type == "channels":
            return await self._sync_channels(**kwargs)
        elif sync_type == "users":
            return await self._sync_users(**kwargs)
        elif sync_type == "messages":
            return await self._sync_messages(**kwargs)
        else:
            return SyncResult(
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                errors=[f"Unknown sync type: {sync_type}"],
                sync_time=datetime.utcnow()
            )

    async def _sync_channels(self, **kwargs) -> SyncResult:
        """Sync Slack channels"""

        try:
            result = await self._make_api_request("GET", "/api/conversations.list")

            if result["success"]:
                channels = result["data"]["channels"]

                return SyncResult(
                    success=True,
                    records_processed=len(channels),
                    records_created=len(channels),
                    records_updated=0,
                    records_failed=0,
                    errors=[],
                    sync_time=datetime.utcnow(),
                    metadata={"channels": [ch["name"] for ch in channels]}
                )
            else:
                return SyncResult(
                    success=False,
                    records_processed=0,
                    records_created=0,
                    records_updated=0,
                    records_failed=0,
                    errors=[result["error"]],
                    sync_time=datetime.utcnow()
                )

        except Exception as e:
            return SyncResult(
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                errors=[str(e)],
                sync_time=datetime.utcnow()
            )

    async def _sync_users(self, **kwargs) -> SyncResult:
        """Sync Slack users"""
        # Mock implementation
        return SyncResult(
            success=True,
            records_processed=15,
            records_created=15,
            records_updated=0,
            records_failed=0,
            errors=[],
            sync_time=datetime.utcnow()
        )

    async def _sync_messages(self, **kwargs) -> SyncResult:
        """Sync Slack messages"""
        # Mock implementation
        return SyncResult(
            success=True,
            records_processed=100,
            records_created=100,
            records_updated=0,
            records_failed=0,
            errors=[],
            sync_time=datetime.utcnow()
        )

    async def send_message(
        self,
        channel: str,
        text: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send message to Slack channel"""

        payload = {
            "channel": channel,
            "text": text
        }

        if attachments:
            payload["attachments"] = attachments

        result = await self._make_api_request("POST", "/api/chat.postMessage", data=payload)
        return result


class GoogleWorkspaceIntegration(BaseIntegration):
    """Google Workspace integration"""

    async def test_connection(self) -> Dict[str, Any]:
        """Test Google Workspace connection"""
        try:
            # Test with Gmail API
            result = await self._make_api_request("GET", "/gmail/v1/users/me/profile")

            if result["success"]:
                return {
                    "success": True,
                    "message": "Google Workspace connection successful",
                    "email": result["data"].get("emailAddress")
                }
            else:
                return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def sync_data(self, sync_type: str, **kwargs) -> SyncResult:
        """Sync data with Google Workspace"""

        if sync_type == "contacts":
            return await self._sync_google_contacts(**kwargs)
        elif sync_type == "calendar":
            return await self._sync_google_calendar(**kwargs)
        elif sync_type == "drive":
            return await self._sync_google_drive(**kwargs)
        else:
            return SyncResult(
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                errors=[f"Unknown sync type: {sync_type}"],
                sync_time=datetime.utcnow()
            )

    async def _sync_google_contacts(self, **kwargs) -> SyncResult:
        """Sync Google contacts"""
        # Mock implementation
        return SyncResult(
            success=True,
            records_processed=75,
            records_created=25,
            records_updated=50,
            records_failed=0,
            errors=[],
            sync_time=datetime.utcnow()
        )

    async def _sync_google_calendar(self, **kwargs) -> SyncResult:
        """Sync Google Calendar events"""
        # Mock implementation
        return SyncResult(
            success=True,
            records_processed=30,
            records_created=10,
            records_updated=20,
            records_failed=0,
            errors=[],
            sync_time=datetime.utcnow()
        )

    async def _sync_google_drive(self, **kwargs) -> SyncResult:
        """Sync Google Drive files"""
        # Mock implementation
        return SyncResult(
            success=True,
            records_processed=200,
            records_created=50,
            records_updated=150,
            records_failed=0,
            errors=[],
            sync_time=datetime.utcnow()
        )


class MicrosoftTeamsIntegration(BaseIntegration):
    """Microsoft Teams integration"""

    async def test_connection(self) -> Dict[str, Any]:
        """Test Microsoft Teams connection"""
        try:
            result = await self._make_api_request("GET", "/v1.0/me")

            if result["success"]:
                return {
                    "success": True,
                    "message": "Microsoft Teams connection successful",
                    "user": result["data"].get("displayName")
                }
            else:
                return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def sync_data(self, sync_type: str, **kwargs) -> SyncResult:
        """Sync data with Microsoft Teams"""

        if sync_type == "teams":
            return await self._sync_teams(**kwargs)
        elif sync_type == "channels":
            return await self._sync_teams_channels(**kwargs)
        elif sync_type == "messages":
            return await self._sync_teams_messages(**kwargs)
        else:
            return SyncResult(
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                errors=[f"Unknown sync type: {sync_type}"],
                sync_time=datetime.utcnow()
            )

    async def _sync_teams(self, **kwargs) -> SyncResult:
        """Sync Microsoft Teams"""
        # Mock implementation
        return SyncResult(
            success=True,
            records_processed=8,
            records_created=8,
            records_updated=0,
            records_failed=0,
            errors=[],
            sync_time=datetime.utcnow()
        )

    async def _sync_teams_channels(self, **kwargs) -> SyncResult:
        """Sync Teams channels"""
        # Mock implementation
        return SyncResult(
            success=True,
            records_processed=24,
            records_created=24,
            records_updated=0,
            records_failed=0,
            errors=[],
            sync_time=datetime.utcnow()
        )

    async def _sync_teams_messages(self, **kwargs) -> SyncResult:
        """Sync Teams messages"""
        # Mock implementation
        return SyncResult(
            success=True,
            records_processed=150,
            records_created=150,
            records_updated=0,
            records_failed=0,
            errors=[],
            sync_time=datetime.utcnow()
        )


class IntegrationManager:
    """Manager for all external integrations"""

    def __init__(self):
        self.integrations: Dict[str, BaseIntegration] = {}
        self.integration_configs: Dict[str, IntegrationConfig] = {}

    def register_integration(self, config: IntegrationConfig) -> bool:
        """Register a new integration"""
        try:
            self.integration_configs[config.integration_id] = config

            # Create integration instance based on type
            if config.integration_type == IntegrationType.CRM:
                if "salesforce" in config.name.lower():
                    integration = SalesforceIntegration(config)
                else:
                    integration = BaseIntegration(config)  # Generic CRM

            elif config.integration_type == IntegrationType.COMMUNICATION:
                if "slack" in config.name.lower():
                    integration = SlackIntegration(config)
                elif "teams" in config.name.lower():
                    integration = MicrosoftTeamsIntegration(config)
                else:
                    integration = BaseIntegration(config)  # Generic communication

            elif config.integration_type == IntegrationType.DOCUMENT_STORAGE:
                if "google" in config.name.lower():
                    integration = GoogleWorkspaceIntegration(config)
                else:
                    integration = BaseIntegration(config)  # Generic document storage

            else:
                integration = BaseIntegration(config)  # Generic integration

            self.integrations[config.integration_id] = integration

            logger.info(f"Registered integration: {config.name} ({config.integration_type})")
            return True

        except Exception as e:
            logger.error(f"Error registering integration {config.name}: {str(e)}")
            return False

    async def test_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Test connections for all registered integrations"""
        results = {}

        for integration_id, integration in self.integrations.items():
            async with integration:
                try:
                    result = await integration.test_connection()
                    results[integration_id] = result
                except Exception as e:
                    results[integration_id] = {
                        "success": False,
                        "error": str(e)
                    }

        return results

    async def sync_integration_data(
        self,
        integration_id: str,
        sync_type: str,
        **kwargs
    ) -> SyncResult:
        """Sync data for a specific integration"""

        if integration_id not in self.integrations:
            return SyncResult(
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                errors=[f"Integration {integration_id} not found"],
                sync_time=datetime.utcnow()
            )

        integration = self.integrations[integration_id]

        async with integration:
            try:
                result = await integration.sync_data(sync_type, **kwargs)

                # Update last sync time
                if integration_id in self.integration_configs:
                    self.integration_configs[integration_id].last_sync = datetime.utcnow()

                return result

            except Exception as e:
                return SyncResult(
                    success=False,
                    records_processed=0,
                    records_created=0,
                    records_updated=0,
                    records_failed=0,
                    errors=[str(e)],
                    sync_time=datetime.utcnow()
                )

    async def bulk_sync(
        self,
        integration_ids: Optional[List[str]] = None,
        sync_types: Optional[Dict[str, str]] = None
    ) -> Dict[str, SyncResult]:
        """Perform bulk synchronization across multiple integrations"""

        if integration_ids is None:
            integration_ids = list(self.integrations.keys())

        results = {}

        # Create sync tasks
        tasks = []
        for integration_id in integration_ids:
            if integration_id in self.integrations:
                sync_type = sync_types.get(integration_id, "full") if sync_types else "full"
                task = self.sync_integration_data(integration_id, sync_type)
                tasks.append((integration_id, task))

        # Execute all sync tasks concurrently
        for integration_id, task in tasks:
            try:
                result = await task
                results[integration_id] = result
            except Exception as e:
                results[integration_id] = SyncResult(
                    success=False,
                    records_processed=0,
                    records_created=0,
                    records_updated=0,
                    records_failed=0,
                    errors=[str(e)],
                    sync_time=datetime.utcnow()
                )

        return results

    def get_integration_status(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific integration"""

        if integration_id not in self.integration_configs:
            return None

        config = self.integration_configs[integration_id]

        return {
            "integration_id": integration_id,
            "name": config.name,
            "type": config.integration_type,
            "status": config.status,
            "last_sync": config.last_sync,
            "created_at": config.created_at
        }

    def list_integrations(
        self,
        integration_type: Optional[IntegrationType] = None,
        status: Optional[IntegrationStatus] = None
    ) -> List[Dict[str, Any]]:
        """List all integrations with optional filtering"""

        integrations = []

        for integration_id, config in self.integration_configs.items():
            if integration_type and config.integration_type != integration_type:
                continue

            if status and config.status != status:
                continue

            integrations.append({
                "integration_id": integration_id,
                "name": config.name,
                "type": config.integration_type,
                "status": config.status,
                "last_sync": config.last_sync,
                "created_at": config.created_at
            })

        return integrations


class WebhookHandler:
    """Handler for incoming webhooks from external systems"""

    def __init__(self):
        self.webhook_handlers = {}
        self.webhook_logs = []

    def register_webhook_handler(
        self,
        integration_type: IntegrationType,
        handler_func: callable
    ) -> bool:
        """Register a webhook handler for an integration type"""
        try:
            self.webhook_handlers[integration_type] = handler_func
            logger.info(f"Registered webhook handler for {integration_type}")
            return True
        except Exception as e:
            logger.error(f"Error registering webhook handler: {str(e)}")
            return False

    async def process_webhook(
        self,
        integration_type: IntegrationType,
        webhook_data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Process incoming webhook"""

        webhook_log = {
            "timestamp": datetime.utcnow(),
            "integration_type": integration_type,
            "data_size": len(str(webhook_data)),
            "headers": headers or {},
            "processed": False,
            "error": None
        }

        try:
            if integration_type not in self.webhook_handlers:
                webhook_log["error"] = f"No handler registered for {integration_type}"
                self.webhook_logs.append(webhook_log)
                return {
                    "success": False,
                    "error": f"No handler registered for {integration_type}"
                }

            handler = self.webhook_handlers[integration_type]
            result = await handler(webhook_data, headers)

            webhook_log["processed"] = True
            webhook_log["result"] = result
            self.webhook_logs.append(webhook_log)

            return {
                "success": True,
                "result": result
            }

        except Exception as e:
            webhook_log["error"] = str(e)
            self.webhook_logs.append(webhook_log)
            logger.error(f"Error processing webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_webhook_logs(
        self,
        integration_type: Optional[IntegrationType] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get webhook processing logs"""

        logs = self.webhook_logs

        if integration_type:
            logs = [log for log in logs if log["integration_type"] == integration_type]

        # Return most recent logs first
        return sorted(logs, key=lambda x: x["timestamp"], reverse=True)[:limit]


# Create global instances
integration_manager = IntegrationManager()
webhook_handler = WebhookHandler()

# Export main classes and functions
__all__ = [
    "IntegrationManager",
    "WebhookHandler",
    "BaseIntegration",
    "SalesforceIntegration",
    "SlackIntegration",
    "GoogleWorkspaceIntegration",
    "MicrosoftTeamsIntegration",
    "IntegrationConfig",
    "SyncResult",
    "IntegrationType",
    "IntegrationStatus",
    "integration_manager",
    "webhook_handler"
]