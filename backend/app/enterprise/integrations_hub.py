"""
Enterprise Integrations Hub
Centralized management for all third-party integrations
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import json
import httpx
from abc import ABC, abstractmethod

class IntegrationProvider(str, Enum):
    """Supported integration providers"""
    # CRM Systems
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    PIPEDRIVE = "pipedrive"
    
    # Financial Data
    BLOOMBERG = "bloomberg"
    REFINITIV = "refinitiv"
    PITCHBOOK = "pitchbook"
    CAPITALIQ = "capitaliq"
    
    # Communication
    SLACK = "slack"
    MICROSOFT_TEAMS = "microsoft_teams"
    ZOOM = "zoom"
    
    # Document Storage
    SHAREPOINT = "sharepoint"
    BOX = "box"
    DROPBOX = "dropbox"
    GOOGLE_DRIVE = "google_drive"
    
    # Office Suites
    MICROSOFT_365 = "microsoft_365"
    GOOGLE_WORKSPACE = "google_workspace"
    
    # Authentication
    AZURE_AD = "azure_ad"
    OKTA = "okta"
    LDAP = "ldap"
    
    # Analytics
    TABLEAU = "tableau"
    POWER_BI = "power_bi"
    LOOKER = "looker"

class IntegrationStatus(str, Enum):
    """Integration status types"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    CONFIGURING = "configuring"
    AUTHENTICATING = "authenticating"

class SyncStatus(str, Enum):
    """Data synchronization status"""
    SYNCED = "synced"
    SYNCING = "syncing"
    FAILED = "failed"
    PENDING = "pending"
    NEVER_SYNCED = "never_synced"

@dataclass
class IntegrationConfig:
    """Configuration for a specific integration"""
    integration_id: str
    provider: IntegrationProvider
    organization_id: str
    name: str
    description: str
    config_data: Dict[str, Any]
    credentials: Dict[str, str]  # Encrypted in production
    status: IntegrationStatus
    sync_status: SyncStatus
    enabled_features: List[str]
    sync_schedule: Optional[str] = None  # Cron expression
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
@dataclass
class SyncResult:
    """Result of a data synchronization operation"""
    integration_id: str
    sync_type: str
    success: bool
    records_processed: int
    records_created: int
    records_updated: int
    records_failed: int
    duration_seconds: float
    start_time: datetime
    end_time: datetime
    error_details: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None
    
class IntegrationConnector(ABC):
    """Base class for integration connectors"""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with the external service"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test the connection to the external service"""
        pass
    
    @abstractmethod
    async def sync_data(self, sync_type: str, config: Dict[str, Any]) -> SyncResult:
        """Synchronize data with the external service"""
        pass
    
    @abstractmethod
    def get_supported_features(self) -> List[str]:
        """Get list of supported features for this connector"""
        pass
    
    @abstractmethod
    def get_required_credentials(self) -> List[str]:
        """Get list of required credential fields"""
        pass

class SalesforceConnector(IntegrationConnector):
    """Salesforce CRM integration connector"""
    
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.access_token: Optional[str] = None
        self.instance_url: Optional[str] = None
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Salesforce using OAuth2"""
        try:
            auth_url = "https://login.salesforce.com/services/oauth2/token"
            auth_data = {
                "grant_type": "password",
                "client_id": credentials.get("client_id"),
                "client_secret": credentials.get("client_secret"),
                "username": credentials.get("username"),
                "password": credentials.get("password") + credentials.get("security_token", "")
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(auth_url, data=auth_data)
                
            if response.status_code == 200:
                auth_result = response.json()
                self.access_token = auth_result.get("access_token")
                self.instance_url = auth_result.get("instance_url")
                return True
            
            return False
            
        except Exception:
            return False
    
    async def test_connection(self) -> bool:
        """Test Salesforce connection"""
        if not self.access_token or not self.instance_url:
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            url = f"{self.instance_url}/services/data/v58.0/sobjects/"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    async def sync_data(self, sync_type: str, config: Dict[str, Any]) -> SyncResult:
        """Sync data with Salesforce"""
        start_time = datetime.now()
        
        try:
            # Mock sync implementation
            await asyncio.sleep(0.5)  # Simulate API calls
            
            # In a real implementation, this would:
            # 1. Query Salesforce objects (Accounts, Contacts, Opportunities)
            # 2. Map Salesforce data to internal deal/contact models
            # 3. Create/update records in the local database
            # 4. Handle conflicts and duplicates
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return SyncResult(
                integration_id=config.get("integration_id", "unknown"),
                sync_type=sync_type,
                success=True,
                records_processed=25,
                records_created=5,
                records_updated=15,
                records_failed=0,
                duration_seconds=duration,
                start_time=start_time,
                end_time=end_time,
                metadata={"salesforce_version": "v58.0"}
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return SyncResult(
                integration_id=config.get("integration_id", "unknown"),
                sync_type=sync_type,
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                duration_seconds=duration,
                start_time=start_time,
                end_time=end_time,
                error_details=[str(e)]
            )
    
    def get_supported_features(self) -> List[str]:
        return [
            "contacts_sync",
            "accounts_sync",
            "opportunities_sync",
            "leads_sync",
            "custom_objects",
            "real_time_webhooks"
        ]
    
    def get_required_credentials(self) -> List[str]:
        return ["client_id", "client_secret", "username", "password", "security_token"]

class HubSpotConnector(IntegrationConnector):
    """HubSpot CRM integration connector"""
    
    def __init__(self):
        self.api_key: Optional[str] = None
        self.base_url = "https://api.hubapi.com"
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with HubSpot using API key"""
        self.api_key = credentials.get("api_key")
        return bool(self.api_key)
    
    async def test_connection(self) -> bool:
        """Test HubSpot connection"""
        if not self.api_key:
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            url = f"{self.base_url}/crm/v3/objects/contacts?limit=1"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    async def sync_data(self, sync_type: str, config: Dict[str, Any]) -> SyncResult:
        """Sync data with HubSpot"""
        start_time = datetime.now()
        
        try:
            # Mock sync implementation
            await asyncio.sleep(0.3)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return SyncResult(
                integration_id=config.get("integration_id", "unknown"),
                sync_type=sync_type,
                success=True,
                records_processed=18,
                records_created=3,
                records_updated=12,
                records_failed=1,
                duration_seconds=duration,
                start_time=start_time,
                end_time=end_time,
                warnings=["1 record failed validation"]
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return SyncResult(
                integration_id=config.get("integration_id", "unknown"),
                sync_type=sync_type,
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                duration_seconds=duration,
                start_time=start_time,
                end_time=end_time,
                error_details=[str(e)]
            )
    
    def get_supported_features(self) -> List[str]:
        return [
            "contacts_sync",
            "companies_sync",
            "deals_sync",
            "tickets_sync",
            "email_tracking",
            "form_submissions"
        ]
    
    def get_required_credentials(self) -> List[str]:
        return ["api_key"]

class SlackConnector(IntegrationConnector):
    """Slack communication integration connector"""
    
    def __init__(self):
        self.bot_token: Optional[str] = None
        self.base_url = "https://slack.com/api"
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Slack using bot token"""
        self.bot_token = credentials.get("bot_token")
        return bool(self.bot_token)
    
    async def test_connection(self) -> bool:
        """Test Slack connection"""
        if not self.bot_token:
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.bot_token}"}
            url = f"{self.base_url}/auth.test"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("ok", False)
            
            return False
            
        except Exception:
            return False
    
    async def sync_data(self, sync_type: str, config: Dict[str, Any]) -> SyncResult:
        """Sync data with Slack (primarily for notifications)"""
        start_time = datetime.now()
        
        try:
            # Mock sync implementation for Slack channels/users
            await asyncio.sleep(0.2)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return SyncResult(
                integration_id=config.get("integration_id", "unknown"),
                sync_type=sync_type,
                success=True,
                records_processed=10,
                records_created=2,
                records_updated=8,
                records_failed=0,
                duration_seconds=duration,
                start_time=start_time,
                end_time=end_time,
                metadata={"channels_synced": 5, "users_synced": 15}
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return SyncResult(
                integration_id=config.get("integration_id", "unknown"),
                sync_type=sync_type,
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                duration_seconds=duration,
                start_time=start_time,
                end_time=end_time,
                error_details=[str(e)]
            )
    
    def get_supported_features(self) -> List[str]:
        return [
            "notifications",
            "deal_alerts",
            "channel_sync",
            "user_sync",
            "file_sharing",
            "workflow_updates"
        ]
    
    def get_required_credentials(self) -> List[str]:
        return ["bot_token"]

class IntegrationsHub:
    """Central hub for managing all enterprise integrations"""
    
    def __init__(self):
        self.active_integrations: Dict[str, IntegrationConfig] = {}
        self.connectors: Dict[IntegrationProvider, IntegrationConnector] = {
            IntegrationProvider.SALESFORCE: SalesforceConnector(),
            IntegrationProvider.HUBSPOT: HubSpotConnector(),
            IntegrationProvider.SLACK: SlackConnector()
            # Add more connectors as needed
        }
        self.sync_history: List[SyncResult] = []
        self.sync_schedules: Dict[str, Dict[str, Any]] = {}
        
    async def add_integration(self, config: IntegrationConfig) -> bool:
        """Add a new integration to the hub"""
        try:
            # Get the appropriate connector
            connector = self.connectors.get(config.provider)
            if not connector:
                config.status = IntegrationStatus.ERROR
                config.error_message = f"No connector available for {config.provider}"
                return False
            
            # Test authentication
            config.status = IntegrationStatus.AUTHENTICATING
            auth_success = await connector.authenticate(config.credentials)
            
            if not auth_success:
                config.status = IntegrationStatus.ERROR
                config.error_message = "Authentication failed"
                return False
            
            # Test connection
            connection_success = await connector.test_connection()
            
            if not connection_success:
                config.status = IntegrationStatus.ERROR
                config.error_message = "Connection test failed"
                return False
            
            # Mark as active
            config.status = IntegrationStatus.ACTIVE
            config.sync_status = SyncStatus.NEVER_SYNCED
            config.created_at = datetime.now()
            config.updated_at = datetime.now()
            
            # Store the integration
            self.active_integrations[config.integration_id] = config
            
            return True
            
        except Exception as e:
            config.status = IntegrationStatus.ERROR
            config.error_message = str(e)
            return False
    
    async def configure_integration(
        self,
        provider: IntegrationProvider,
        organization_id: str,
        config: Dict[str, Any]
    ) -> str:
        """Configure a new integration"""
        integration_id = f"int_{provider.value}_{organization_id}_{datetime.now().timestamp()}"

        integration_config = IntegrationConfig(
            id=integration_id,
            provider=provider,
            organization_id=organization_id,
            config=config,
            status=IntegrationStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        success = await self.add_integration(integration_config)
        return integration_id if success else None

    def list_integrations(self, organization_id: str) -> List[Dict[str, Any]]:
        """List all integrations for an organization"""
        return [
            {
                "id": config.id,
                "provider": config.provider.value,
                "status": config.status.value,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat()
            }
            for config in self.get_organization_integrations(organization_id)
        ]

    def check_integration_health(self, integration_id: str, organization_id: str) -> Dict[str, Any]:
        """Check the health status of an integration"""
        integration = self.get_integration(integration_id)
        if not integration:
            return {"status": "not_found", "healthy": False}

        return {
            "status": integration.status.value,
            "healthy": integration.status == IntegrationStatus.ACTIVE,
            "last_sync": integration.last_sync.isoformat() if integration.last_sync else None,
            "error_count": 0
        }

    async def remove_integration(self, integration_id: str, organization_id: str = None) -> bool:
        """Remove an integration from the hub"""
        if integration_id in self.active_integrations:
            del self.active_integrations[integration_id]
            return True
        return False
    
    async def sync_integration(self, integration_id: str, organization_id: str, sync_type: str = "full") -> SyncResult:
        """Perform data synchronization for a specific integration"""
        integration = self.active_integrations.get(integration_id)
        if not integration:
            return SyncResult(
                integration_id=integration_id,
                sync_type=sync_type,
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                duration_seconds=0,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_details=["Integration not found"]
            )
        
        connector = self.connectors.get(integration.provider)
        if not connector:
            return SyncResult(
                integration_id=integration_id,
                sync_type=sync_type,
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                duration_seconds=0,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_details=["Connector not available"]
            )
        
        # Update sync status
        integration.sync_status = SyncStatus.SYNCING
        integration.updated_at = datetime.now()
        
        try:
            # Perform the sync
            sync_config = {
                "integration_id": integration_id,
                "enabled_features": integration.enabled_features,
                **integration.config_data
            }
            
            result = await connector.sync_data(sync_type, sync_config)
            
            # Update integration status
            if result.success:
                integration.sync_status = SyncStatus.SYNCED
                integration.last_sync = result.end_time
                integration.error_message = None
            else:
                integration.sync_status = SyncStatus.FAILED
                integration.error_message = "; ".join(result.error_details or [])
            
            integration.updated_at = datetime.now()
            
            # Store sync result
            self.sync_history.append(result)
            
            # Keep only last 1000 sync results
            if len(self.sync_history) > 1000:
                self.sync_history = self.sync_history[-1000:]
            
            return result
            
        except Exception as e:
            integration.sync_status = SyncStatus.FAILED
            integration.error_message = str(e)
            integration.updated_at = datetime.now()
            
            return SyncResult(
                integration_id=integration_id,
                sync_type=sync_type,
                success=False,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                duration_seconds=0,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_details=[str(e)]
            )
    
    async def sync_all_integrations(self, organization_id: str) -> List[SyncResult]:
        """Sync all active integrations for an organization"""
        org_integrations = [
            integration for integration in self.active_integrations.values()
            if integration.organization_id == organization_id and 
               integration.status == IntegrationStatus.ACTIVE
        ]
        
        sync_tasks = [
            self.sync_integration(integration.integration_id)
            for integration in org_integrations
        ]
        
        results = await asyncio.gather(*sync_tasks, return_exceptions=True)
        
        # Filter out exceptions and return only SyncResult objects
        return [result for result in results if isinstance(result, SyncResult)]
    
    def get_integration(self, integration_id: str) -> Optional[IntegrationConfig]:
        """Get a specific integration configuration"""
        return self.active_integrations.get(integration_id)
    
    def get_organization_integrations(self, organization_id: str) -> List[IntegrationConfig]:
        """Get all integrations for an organization"""
        return [
            integration for integration in self.active_integrations.values()
            if integration.organization_id == organization_id
        ]
    
    def get_provider_integrations(self, provider: IntegrationProvider) -> List[IntegrationConfig]:
        """Get all integrations for a specific provider"""
        return [
            integration for integration in self.active_integrations.values()
            if integration.provider == provider
        ]
    
    def get_sync_history(self, integration_id: Optional[str] = None, 
                        limit: int = 100) -> List[SyncResult]:
        """Get synchronization history"""
        history = self.sync_history
        
        if integration_id:
            history = [
                result for result in history 
                if result.integration_id == integration_id
            ]
        
        # Sort by start time, most recent first
        history.sort(key=lambda x: x.start_time, reverse=True)
        
        return history[:limit]
    
    def get_supported_providers(self) -> List[Dict[str, Any]]:
        """Get list of supported integration providers"""
        providers = []
        
        for provider in IntegrationProvider:
            connector = self.connectors.get(provider)
            if connector:
                providers.append({
                    "provider": provider.value,
                    "name": provider.value.replace("_", " ").title(),
                    "supported_features": connector.get_supported_features(),
                    "required_credentials": connector.get_required_credentials(),
                    "available": True
                })
            else:
                providers.append({
                    "provider": provider.value,
                    "name": provider.value.replace("_", " ").title(),
                    "supported_features": [],
                    "required_credentials": [],
                    "available": False
                })
        
        return providers
    
    def get_integration_stats(self, organization_id: Optional[str] = None) -> Dict[str, Any]:
        """Get integration statistics"""
        integrations = self.active_integrations.values()
        
        if organization_id:
            integrations = [
                integration for integration in integrations
                if integration.organization_id == organization_id
            ]
        
        total_integrations = len(integrations)
        active_integrations = sum(
            1 for integration in integrations 
            if integration.status == IntegrationStatus.ACTIVE
        )
        
        sync_stats = {
            "total_syncs": len(self.sync_history),
            "successful_syncs": sum(1 for result in self.sync_history if result.success),
            "failed_syncs": sum(1 for result in self.sync_history if not result.success),
            "last_24h_syncs": sum(
                1 for result in self.sync_history 
                if result.start_time > datetime.now() - timedelta(days=1)
            )
        }
        
        provider_stats = {}
        for integration in integrations:
            provider = integration.provider.value
            if provider not in provider_stats:
                provider_stats[provider] = {"count": 0, "active": 0}
            provider_stats[provider]["count"] += 1
            if integration.status == IntegrationStatus.ACTIVE:
                provider_stats[provider]["active"] += 1
        
        return {
            "total_integrations": total_integrations,
            "active_integrations": active_integrations,
            "sync_stats": sync_stats,
            "provider_stats": provider_stats,
            "supported_providers": len(IntegrationProvider),
            "available_connectors": len(self.connectors)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the integrations hub"""
        return {
            "status": "healthy",
            "active_integrations": len(self.active_integrations),
            "available_connectors": len(self.connectors),
            "sync_history_entries": len(self.sync_history),
            "timestamp": datetime.now().isoformat()
        }

# Global integrations hub instance
_integrations_hub: Optional[IntegrationsHub] = None

def get_integrations_hub() -> IntegrationsHub:
    """Get global integrations hub instance"""
    global _integrations_hub
    if _integrations_hub is None:
        _integrations_hub = IntegrationsHub()
    return _integrations_hub