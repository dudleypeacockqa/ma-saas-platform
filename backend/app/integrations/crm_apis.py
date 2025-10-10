"""
CRM Platform Integrations
HubSpot and Pipedrive connectors for customer relationship management
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx

from app.integrations.platform_connectors import (
    APIKeyPlatformConnector,
    OAuthPlatformConnector,
    PlatformType,
    PlatformCredentials,
    SyncResult
)

logger = logging.getLogger(__name__)


class HubSpotConnector(OAuthPlatformConnector):
    """HubSpot CRM API connector"""

    @property
    def platform_name(self) -> str:
        return "hubspot"

    @property
    def platform_type(self) -> PlatformType:
        return PlatformType.CRM

    @property
    def base_url(self) -> str:
        return "https://api.hubapi.com"

    @property
    def oauth_authorize_url(self) -> str:
        return "https://app.hubspot.com/oauth/authorize"

    @property
    def oauth_token_url(self) -> str:
        return "https://api.hubapi.com/oauth/v1/token"

    @property
    def oauth_scopes(self) -> List[str]:
        return [
            "crm.objects.contacts.read",
            "crm.objects.contacts.write",
            "crm.objects.companies.read",
            "crm.objects.companies.write",
            "crm.objects.deals.read",
            "crm.objects.deals.write"
        ]

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.credentials.access_token}",
            "Content-Type": "application/json"
        }

    async def test_connection(self) -> bool:
        """Test HubSpot API connection"""
        try:
            response = await self.http_client.get("/crm/v3/objects/contacts")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"HubSpot connection test failed: {e}")
            return False

    async def get_contacts(
        self,
        limit: int = 100,
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get contacts from HubSpot"""
        try:
            params = {"limit": limit}
            if after:
                params["after"] = after

            response = await self.http_client.get(
                "/crm/v3/objects/contacts",
                params=params
            )

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get contacts: {e}")

        return {"results": [], "paging": {}}

    async def create_contact(
        self,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        **properties
    ) -> Optional[Dict[str, Any]]:
        """Create a contact in HubSpot"""
        try:
            contact_data = {
                "properties": {
                    "email": email,
                    **properties
                }
            }

            if first_name:
                contact_data["properties"]["firstname"] = first_name

            if last_name:
                contact_data["properties"]["lastname"] = last_name

            response = await self.http_client.post(
                "/crm/v3/objects/contacts",
                json=contact_data
            )

            if response.status_code == 201:
                return response.json()

        except Exception as e:
            logger.error(f"Failed to create contact: {e}")

        return None

    async def get_deals(
        self,
        limit: int = 100,
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get deals from HubSpot"""
        try:
            params = {"limit": limit}
            if after:
                params["after"] = after

            response = await self.http_client.get(
                "/crm/v3/objects/deals",
                params=params
            )

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get deals: {e}")

        return {"results": [], "paging": {}}

    async def create_deal(
        self,
        dealname: str,
        amount: Optional[float] = None,
        dealstage: Optional[str] = None,
        **properties
    ) -> Optional[Dict[str, Any]]:
        """Create a deal in HubSpot"""
        try:
            deal_data = {
                "properties": {
                    "dealname": dealname,
                    **properties
                }
            }

            if amount is not None:
                deal_data["properties"]["amount"] = str(amount)

            if dealstage:
                deal_data["properties"]["dealstage"] = dealstage

            response = await self.http_client.post(
                "/crm/v3/objects/deals",
                json=deal_data
            )

            if response.status_code == 201:
                return response.json()

        except Exception as e:
            logger.error(f"Failed to create deal: {e}")

        return None

    async def sync_data(
        self,
        sync_type: str,
        since: Optional[datetime] = None
    ) -> SyncResult:
        """Sync HubSpot data"""
        synced_count = 0
        errors = []

        try:
            if sync_type == "contacts":
                result = await self.get_contacts(limit=100)
                synced_count = len(result.get("results", []))

            elif sync_type == "deals":
                result = await self.get_deals(limit=100)
                synced_count = len(result.get("results", []))

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
        """Push data to HubSpot"""
        if data_type == "contact":
            result = await self.create_contact(
                email=data.get("email"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                **{k: v for k, v in data.items() if k not in ["email", "first_name", "last_name"]}
            )
            return result is not None

        elif data_type == "deal":
            result = await self.create_deal(
                dealname=data.get("dealname"),
                amount=data.get("amount"),
                dealstage=data.get("dealstage"),
                **{k: v for k, v in data.items() if k not in ["dealname", "amount", "dealstage"]}
            )
            return result is not None

        return False


class PipedriveConnector(APIKeyPlatformConnector):
    """Pipedrive CRM API connector"""

    @property
    def platform_name(self) -> str:
        return "pipedrive"

    @property
    def platform_type(self) -> PlatformType:
        return PlatformType.CRM

    @property
    def base_url(self) -> str:
        company_domain = self.credentials.additional_config.get("company_domain", "api")
        return f"https://{company_domain}.pipedrive.com/v1"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json"
        }

    async def test_connection(self) -> bool:
        """Test Pipedrive API connection"""
        try:
            response = await self.http_client.get(
                "/users/me",
                params={"api_token": self.credentials.api_key}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Pipedrive connection test failed: {e}")
            return False

    async def get_deals(
        self,
        start: int = 0,
        limit: int = 100,
        status: str = "all_not_deleted"
    ) -> List[Dict[str, Any]]:
        """Get deals from Pipedrive"""
        try:
            response = await self.http_client.get(
                "/deals",
                params={
                    "api_token": self.credentials.api_key,
                    "start": start,
                    "limit": limit,
                    "status": status
                }
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])

        except Exception as e:
            logger.error(f"Failed to get deals: {e}")

        return []

    async def create_deal(
        self,
        title: str,
        value: Optional[float] = None,
        currency: str = "USD",
        person_id: Optional[int] = None,
        org_id: Optional[int] = None,
        **custom_fields
    ) -> Optional[Dict[str, Any]]:
        """Create a deal in Pipedrive"""
        try:
            deal_data = {
                "title": title,
                **custom_fields
            }

            if value is not None:
                deal_data["value"] = value
                deal_data["currency"] = currency

            if person_id:
                deal_data["person_id"] = person_id

            if org_id:
                deal_data["org_id"] = org_id

            response = await self.http_client.post(
                "/deals",
                params={"api_token": self.credentials.api_key},
                json=deal_data
            )

            if response.status_code == 201:
                data = response.json()
                return data.get("data")

        except Exception as e:
            logger.error(f"Failed to create deal: {e}")

        return None

    async def get_persons(
        self,
        start: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get persons (contacts) from Pipedrive"""
        try:
            response = await self.http_client.get(
                "/persons",
                params={
                    "api_token": self.credentials.api_key,
                    "start": start,
                    "limit": limit
                }
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])

        except Exception as e:
            logger.error(f"Failed to get persons: {e}")

        return []

    async def sync_data(
        self,
        sync_type: str,
        since: Optional[datetime] = None
    ) -> SyncResult:
        """Sync Pipedrive data"""
        synced_count = 0
        errors = []

        try:
            if sync_type == "deals":
                deals = await self.get_deals(limit=500)
                synced_count = len(deals)

            elif sync_type == "persons":
                persons = await self.get_persons(limit=500)
                synced_count = len(persons)

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
        """Push data to Pipedrive"""
        if data_type == "deal":
            result = await self.create_deal(
                title=data.get("title"),
                value=data.get("value"),
                currency=data.get("currency", "USD"),
                person_id=data.get("person_id"),
                org_id=data.get("org_id"),
                **{k: v for k, v in data.items() if k not in ["title", "value", "currency", "person_id", "org_id"]}
            )
            return result is not None

        return False
