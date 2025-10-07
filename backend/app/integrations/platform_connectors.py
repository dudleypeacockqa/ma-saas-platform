"""
Platform Connectors Base Classes
Standard interface for integrating with external platforms
"""

import os
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import httpx
import asyncio
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)


class PlatformType(str, Enum):
    """Supported platform types"""
    SOCIAL_MEDIA = "social_media"
    PODCAST = "podcast"
    CRM = "crm"
    ANALYTICS = "analytics"
    PAYMENT = "payment"
    STORAGE = "storage"
    COMMUNICATION = "communication"


class ConnectionStatus(str, Enum):
    """Connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    UNAUTHORIZED = "unauthorized"


class PlatformCredentials(BaseModel):
    """Platform authentication credentials"""
    platform_name: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    additional_config: Dict[str, Any] = {}


class SyncResult(BaseModel):
    """Result of a data synchronization operation"""
    success: bool
    items_synced: int
    items_failed: int
    errors: List[str] = []
    metadata: Dict[str, Any] = {}
    synced_at: datetime = datetime.utcnow()


class BasePlatformConnector(ABC):
    """
    Base class for all platform connectors
    Provides standard interface for authentication, data sync, and operations
    """

    def __init__(
        self,
        credentials: PlatformCredentials,
        organization_id: str,
        rate_limit_per_minute: int = 60
    ):
        self.credentials = credentials
        self.organization_id = organization_id
        self.rate_limit_per_minute = rate_limit_per_minute
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.last_sync: Optional[datetime] = None
        self.http_client: Optional[httpx.AsyncClient] = None

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Platform name identifier"""
        pass

    @property
    @abstractmethod
    def platform_type(self) -> PlatformType:
        """Type of platform"""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base API URL"""
        pass

    async def initialize(self) -> bool:
        """Initialize connection to platform"""
        try:
            self.http_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                headers=self._get_headers()
            )

            # Test connection
            is_connected = await self.test_connection()

            if is_connected:
                self.connection_status = ConnectionStatus.CONNECTED
                logger.info(f"Connected to {self.platform_name} for org {self.organization_id}")
                return True
            else:
                self.connection_status = ConnectionStatus.ERROR
                return False

        except Exception as e:
            logger.error(f"Failed to initialize {self.platform_name}: {e}")
            self.connection_status = ConnectionStatus.ERROR
            return False

    async def close(self):
        """Close connection"""
        if self.http_client:
            await self.http_client.aclose()
        self.connection_status = ConnectionStatus.DISCONNECTED

    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if connection is working"""
        pass

    @abstractmethod
    async def sync_data(
        self,
        sync_type: str,
        since: Optional[datetime] = None
    ) -> SyncResult:
        """Sync data from platform"""
        pass

    @abstractmethod
    async def push_data(
        self,
        data_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """Push data to platform"""
        pass

    async def refresh_token(self) -> bool:
        """Refresh access token if needed"""
        if not self.credentials.refresh_token:
            return False

        if self.credentials.token_expires_at and \
           self.credentials.token_expires_at > datetime.utcnow():
            return True  # Token still valid

        # Implement token refresh in subclass
        return False

    async def handle_rate_limit(self, retry_after: int = 60):
        """Handle rate limiting"""
        self.connection_status = ConnectionStatus.RATE_LIMITED
        logger.warning(f"{self.platform_name} rate limited, waiting {retry_after}s")
        await asyncio.sleep(retry_after)
        self.connection_status = ConnectionStatus.CONNECTED

    async def execute_with_retry(
        self,
        func: Callable,
        max_retries: int = 3,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retry logic"""
        for attempt in range(max_retries):
            try:
                result = await func(*args, **kwargs)
                return result

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limited
                    retry_after = int(e.response.headers.get("Retry-After", 60))
                    await self.handle_rate_limit(retry_after)

                elif e.response.status_code in [401, 403]:  # Unauthorized
                    self.connection_status = ConnectionStatus.UNAUTHORIZED
                    if await self.refresh_token():
                        continue  # Retry with new token
                    else:
                        raise

                elif attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    raise

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.error(f"Error: {e}, retrying after {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    raise

        return None

    def get_status(self) -> Dict[str, Any]:
        """Get connector status"""
        return {
            "platform_name": self.platform_name,
            "platform_type": self.platform_type.value,
            "connection_status": self.connection_status.value,
            "organization_id": self.organization_id,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "credentials_valid": bool(self.credentials.access_token)
        }


class OAuthPlatformConnector(BasePlatformConnector):
    """
    Base class for OAuth2-based platform connectors
    """

    @property
    @abstractmethod
    def oauth_authorize_url(self) -> str:
        """OAuth authorization URL"""
        pass

    @property
    @abstractmethod
    def oauth_token_url(self) -> str:
        """OAuth token exchange URL"""
        pass

    @property
    @abstractmethod
    def oauth_scopes(self) -> List[str]:
        """Required OAuth scopes"""
        pass

    async def get_authorization_url(
        self,
        redirect_uri: str,
        state: Optional[str] = None
    ) -> str:
        """Generate OAuth authorization URL"""
        params = {
            "client_id": self.credentials.api_key,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.oauth_scopes),
            "response_type": "code"
        }

        if state:
            params["state"] = state

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.oauth_authorize_url}?{query_string}"

    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> bool:
        """Exchange authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.oauth_token_url,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "client_id": self.credentials.api_key,
                        "client_secret": self.credentials.api_secret
                    }
                )

                if response.status_code == 200:
                    token_data = response.json()
                    self.credentials.access_token = token_data.get("access_token")
                    self.credentials.refresh_token = token_data.get("refresh_token")

                    if "expires_in" in token_data:
                        self.credentials.token_expires_at = datetime.utcnow() + \
                            timedelta(seconds=token_data["expires_in"])

                    return True

        except Exception as e:
            logger.error(f"Token exchange failed: {e}")

        return False

    async def refresh_token(self) -> bool:
        """Refresh OAuth access token"""
        if not self.credentials.refresh_token:
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.oauth_token_url,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": self.credentials.refresh_token,
                        "client_id": self.credentials.api_key,
                        "client_secret": self.credentials.api_secret
                    }
                )

                if response.status_code == 200:
                    token_data = response.json()
                    self.credentials.access_token = token_data.get("access_token")

                    if "refresh_token" in token_data:
                        self.credentials.refresh_token = token_data["refresh_token"]

                    if "expires_in" in token_data:
                        self.credentials.token_expires_at = datetime.utcnow() + \
                            timedelta(seconds=token_data["expires_in"])

                    logger.info(f"Token refreshed for {self.platform_name}")
                    return True

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")

        return False


class APIKeyPlatformConnector(BasePlatformConnector):
    """
    Base class for API key-based platform connectors
    """

    def _get_headers(self) -> Dict[str, str]:
        """Standard API key headers"""
        return {
            "Authorization": f"Bearer {self.credentials.api_key}",
            "Content-Type": "application/json"
        }

    async def refresh_token(self) -> bool:
        """API key doesn't need refresh"""
        return True


class WebhookHandler(ABC):
    """
    Base class for handling platform webhooks
    """

    @abstractmethod
    async def verify_webhook(
        self,
        payload: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """Verify webhook signature"""
        pass

    @abstractmethod
    async def process_webhook(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process webhook event"""
        pass
