"""
Salesforce CRM Integration
Bidirectional sync with deal data, opportunities, and account management
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import aiohttp
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceError

from ..core.integration_manager import (
    BaseIntegration, IntegrationConfig, SyncResult, WebhookEvent,
    SyncDirection, IntegrationStatus
)
from ...core.database import get_db
from ...models.deal import Deal
from ...models.contact import Contact
from ...models.organization import Organization

logger = logging.getLogger(__name__)


class SalesforceIntegration(BaseIntegration):
    """Salesforce CRM integration with bidirectional data sync"""

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.sf: Optional[Salesforce] = None
        self.field_mappings = {
            # Deal mappings
            "deal": {
                "ma_platform_field": "salesforce_field",
                "title": "Name",
                "deal_value": "Amount",
                "probability_of_close": "Probability",
                "stage": "StageName",
                "close_date": "CloseDate",
                "description": "Description",
                "created_at": "CreatedDate",
                "updated_at": "LastModifiedDate"
            },
            # Contact mappings
            "contact": {
                "first_name": "FirstName",
                "last_name": "LastName",
                "email": "Email",
                "phone": "Phone",
                "title": "Title",
                "company": "Account.Name",
                "created_at": "CreatedDate",
                "updated_at": "LastModifiedDate"
            },
            # Organization mappings
            "organization": {
                "name": "Name",
                "industry": "Industry",
                "website": "Website",
                "phone": "Phone",
                "annual_revenue": "AnnualRevenue",
                "employee_count": "NumberOfEmployees",
                "billing_address": "BillingAddress",
                "created_at": "CreatedDate",
                "updated_at": "LastModifiedDate"
            }
        }

    async def authenticate(self) -> bool:
        """Authenticate with Salesforce using OAuth2"""
        try:
            credentials = self.config.credentials

            if self.config.auth_type == "oauth2":
                # OAuth2 authentication
                self.sf = Salesforce(
                    username=credentials["username"],
                    password=credentials["password"],
                    security_token=credentials["security_token"],
                    domain=credentials.get("domain", "login"),
                    consumer_key=credentials["client_id"],
                    consumer_secret=credentials["client_secret"]
                )
            elif self.config.auth_type == "session_id":
                # Session ID authentication
                self.sf = Salesforce(
                    session_id=credentials["session_id"],
                    instance_url=credentials["instance_url"]
                )
            else:
                logger.error(f"Unsupported auth type: {self.config.auth_type}")
                return False

            return True

        except SalesforceError as e:
            logger.error(f"Salesforce authentication failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def test_connection(self) -> bool:
        """Test Salesforce connection"""
        try:
            if not self.sf:
                return False

            # Test with a simple query
            result = self.sf.query("SELECT Id FROM User LIMIT 1")
            return bool(result.get("records"))

        except Exception as e:
            logger.error(f"Salesforce connection test failed: {str(e)}")
            return False

    async def sync_data(self, direction: SyncDirection) -> SyncResult:
        """Synchronize data with Salesforce"""
        sync_id = f"sf_sync_{datetime.now().timestamp()}"
        start_time = datetime.now()

        result = SyncResult(
            sync_id=sync_id,
            integration_id=self.config.integration_id,
            direction=direction,
            records_processed=0,
            records_created=0,
            records_updated=0,
            records_failed=0,
            conflicts_detected=0,
            start_time=start_time,
            end_time=start_time,
            errors=[],
            success=False
        )

        try:
            if not self.sf:
                result.errors.append("Not authenticated with Salesforce")
                result.end_time = datetime.now()
                return result

            self.status = IntegrationStatus.SYNCING

            if direction in [SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL]:
                # Sync from Salesforce to M&A platform
                inbound_result = await self._sync_from_salesforce()
                result.records_processed += inbound_result["processed"]
                result.records_created += inbound_result["created"]
                result.records_updated += inbound_result["updated"]
                result.records_failed += inbound_result["failed"]
                result.errors.extend(inbound_result["errors"])

            if direction in [SyncDirection.OUTBOUND, SyncDirection.BIDIRECTIONAL]:
                # Sync from M&A platform to Salesforce
                outbound_result = await self._sync_to_salesforce()
                result.records_processed += outbound_result["processed"]
                result.records_created += outbound_result["created"]
                result.records_updated += outbound_result["updated"]
                result.records_failed += outbound_result["failed"]
                result.errors.extend(outbound_result["errors"])

            result.success = result.records_failed == 0
            result.end_time = datetime.now()
            self.last_sync = result.end_time
            self.status = IntegrationStatus.CONNECTED

            logger.info(f"Salesforce sync completed: {result.records_processed} processed, {result.records_failed} failed")

        except Exception as e:
            logger.error(f"Salesforce sync error: {str(e)}")
            result.errors.append(str(e))
            result.end_time = datetime.now()
            self.status = IntegrationStatus.ERROR

        return result

    async def _sync_from_salesforce(self) -> Dict[str, Any]:
        """Sync opportunities and accounts from Salesforce"""
        result = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }

        try:
            # Sync opportunities (deals)
            opportunities_result = await self._sync_opportunities_from_sf()
            for key in result:
                if key in opportunities_result:
                    result[key] += opportunities_result[key]

            # Sync accounts (organizations)
            accounts_result = await self._sync_accounts_from_sf()
            for key in result:
                if key in accounts_result:
                    result[key] += accounts_result[key]

            # Sync contacts
            contacts_result = await self._sync_contacts_from_sf()
            for key in result:
                if key in contacts_result:
                    result[key] += contacts_result[key]

        except Exception as e:
            result["errors"].append(f"Inbound sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_opportunities_from_sf(self) -> Dict[str, Any]:
        """Sync Salesforce opportunities to M&A platform deals"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            # Get recent opportunities from Salesforce
            last_sync_time = self.last_sync or (datetime.now() - timedelta(days=30))
            query = f"""
                SELECT Id, Name, Amount, Probability, StageName, CloseDate,
                       Description, CreatedDate, LastModifiedDate, AccountId
                FROM Opportunity
                WHERE LastModifiedDate >= {last_sync_time.isoformat()}
                ORDER BY LastModifiedDate ASC
            """

            opportunities = self.sf.query_all(query)["records"]

            async with get_db() as db:
                for opp in opportunities:
                    try:
                        result["processed"] += 1

                        # Check if deal already exists (by external_id or similar matching logic)
                        existing_deal = await self._find_existing_deal(db, opp["Id"])

                        deal_data = {
                            "title": opp["Name"],
                            "deal_value": opp.get("Amount", 0),
                            "probability_of_close": opp.get("Probability", 0) / 100.0,
                            "stage": self._map_sf_stage_to_platform(opp.get("StageName")),
                            "expected_close_date": self._parse_sf_date(opp.get("CloseDate")),
                            "description": opp.get("Description", ""),
                            "external_id": opp["Id"],
                            "external_source": "salesforce",
                            "updated_at": datetime.now()
                        }

                        if existing_deal:
                            # Update existing deal
                            for field, value in deal_data.items():
                                setattr(existing_deal, field, value)
                            result["updated"] += 1
                        else:
                            # Create new deal
                            deal_data.update({
                                "created_at": self._parse_sf_date(opp["CreatedDate"]) or datetime.now(),
                                "is_active": True
                            })
                            new_deal = Deal(**deal_data)
                            db.add(new_deal)
                            result["created"] += 1

                    except Exception as e:
                        result["failed"] += 1
                        result["errors"].append(f"Failed to sync opportunity {opp.get('Id', 'unknown')}: {str(e)}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Opportunities sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_accounts_from_sf(self) -> Dict[str, Any]:
        """Sync Salesforce accounts to M&A platform organizations"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            last_sync_time = self.last_sync or (datetime.now() - timedelta(days=30))
            query = f"""
                SELECT Id, Name, Industry, Website, Phone, AnnualRevenue,
                       NumberOfEmployees, BillingAddress, CreatedDate, LastModifiedDate
                FROM Account
                WHERE LastModifiedDate >= {last_sync_time.isoformat()}
                ORDER BY LastModifiedDate ASC
            """

            accounts = self.sf.query_all(query)["records"]

            async with get_db() as db:
                for acc in accounts:
                    try:
                        result["processed"] += 1

                        existing_org = await self._find_existing_organization(db, acc["Id"])

                        org_data = {
                            "name": acc["Name"],
                            "industry": acc.get("Industry"),
                            "website": acc.get("Website"),
                            "phone": acc.get("Phone"),
                            "annual_revenue": acc.get("AnnualRevenue"),
                            "employee_count": acc.get("NumberOfEmployees"),
                            "external_id": acc["Id"],
                            "external_source": "salesforce",
                            "updated_at": datetime.now()
                        }

                        if existing_org:
                            for field, value in org_data.items():
                                setattr(existing_org, field, value)
                            result["updated"] += 1
                        else:
                            org_data.update({
                                "created_at": self._parse_sf_date(acc["CreatedDate"]) or datetime.now()
                            })
                            new_org = Organization(**org_data)
                            db.add(new_org)
                            result["created"] += 1

                    except Exception as e:
                        result["failed"] += 1
                        result["errors"].append(f"Failed to sync account {acc.get('Id', 'unknown')}: {str(e)}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Accounts sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_contacts_from_sf(self) -> Dict[str, Any]:
        """Sync Salesforce contacts to M&A platform contacts"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            last_sync_time = self.last_sync or (datetime.now() - timedelta(days=30))
            query = f"""
                SELECT Id, FirstName, LastName, Email, Phone, Title,
                       Account.Name, CreatedDate, LastModifiedDate
                FROM Contact
                WHERE LastModifiedDate >= {last_sync_time.isoformat()}
                ORDER BY LastModifiedDate ASC
            """

            contacts = self.sf.query_all(query)["records"]

            async with get_db() as db:
                for contact in contacts:
                    try:
                        result["processed"] += 1

                        existing_contact = await self._find_existing_contact(db, contact["Id"])

                        contact_data = {
                            "first_name": contact.get("FirstName"),
                            "last_name": contact.get("LastName"),
                            "email": contact.get("Email"),
                            "phone": contact.get("Phone"),
                            "title": contact.get("Title"),
                            "external_id": contact["Id"],
                            "external_source": "salesforce",
                            "updated_at": datetime.now()
                        }

                        if existing_contact:
                            for field, value in contact_data.items():
                                setattr(existing_contact, field, value)
                            result["updated"] += 1
                        else:
                            contact_data.update({
                                "created_at": self._parse_sf_date(contact["CreatedDate"]) or datetime.now()
                            })
                            new_contact = Contact(**contact_data)
                            db.add(new_contact)
                            result["created"] += 1

                    except Exception as e:
                        result["failed"] += 1
                        result["errors"].append(f"Failed to sync contact {contact.get('Id', 'unknown')}: {str(e)}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Contacts sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_to_salesforce(self) -> Dict[str, Any]:
        """Sync M&A platform data to Salesforce"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            # Sync deals to opportunities
            deals_result = await self._sync_deals_to_sf()
            for key in result:
                if key in deals_result:
                    result[key] += deals_result[key]

            # Sync organizations to accounts
            orgs_result = await self._sync_organizations_to_sf()
            for key in result:
                if key in orgs_result:
                    result[key] += orgs_result[key]

        except Exception as e:
            result["errors"].append(f"Outbound sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_deals_to_sf(self) -> Dict[str, Any]:
        """Sync M&A platform deals to Salesforce opportunities"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            async with get_db() as db:
                # Get deals modified since last sync
                last_sync_time = self.last_sync or (datetime.now() - timedelta(days=30))

                deals_query = select(Deal).where(
                    Deal.updated_at >= last_sync_time,
                    Deal.is_active == True
                )
                result_deals = await db.execute(deals_query)
                deals = result_deals.scalars().all()

                for deal in deals:
                    try:
                        result["processed"] += 1

                        # Convert deal to Salesforce opportunity format
                        opp_data = {
                            "Name": deal.title,
                            "Amount": float(deal.deal_value) if deal.deal_value else None,
                            "Probability": int(deal.probability_of_close * 100) if deal.probability_of_close else 0,
                            "StageName": self._map_platform_stage_to_sf(deal.stage),
                            "CloseDate": deal.expected_close_date.isoformat() if deal.expected_close_date else None,
                            "Description": deal.description
                        }

                        # Remove None values
                        opp_data = {k: v for k, v in opp_data.items() if v is not None}

                        if deal.external_id and deal.external_source == "salesforce":
                            # Update existing Salesforce opportunity
                            self.sf.Opportunity.update(deal.external_id, opp_data)
                            result["updated"] += 1
                        else:
                            # Create new Salesforce opportunity
                            sf_result = self.sf.Opportunity.create(opp_data)
                            if sf_result.get("success"):
                                # Update deal with Salesforce ID
                                deal.external_id = sf_result["id"]
                                deal.external_source = "salesforce"
                                result["created"] += 1

                    except Exception as e:
                        result["failed"] += 1
                        result["errors"].append(f"Failed to sync deal {deal.id}: {str(e)}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Deals to SF sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_organizations_to_sf(self) -> Dict[str, Any]:
        """Sync M&A platform organizations to Salesforce accounts"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            async with get_db() as db:
                last_sync_time = self.last_sync or (datetime.now() - timedelta(days=30))

                orgs_query = select(Organization).where(
                    Organization.updated_at >= last_sync_time
                )
                result_orgs = await db.execute(orgs_query)
                organizations = result_orgs.scalars().all()

                for org in organizations:
                    try:
                        result["processed"] += 1

                        account_data = {
                            "Name": org.name,
                            "Industry": org.industry,
                            "Website": org.website,
                            "Phone": org.phone,
                            "AnnualRevenue": float(org.annual_revenue) if org.annual_revenue else None,
                            "NumberOfEmployees": org.employee_count
                        }

                        # Remove None values
                        account_data = {k: v for k, v in account_data.items() if v is not None}

                        if org.external_id and org.external_source == "salesforce":
                            # Update existing Salesforce account
                            self.sf.Account.update(org.external_id, account_data)
                            result["updated"] += 1
                        else:
                            # Create new Salesforce account
                            sf_result = self.sf.Account.create(account_data)
                            if sf_result.get("success"):
                                org.external_id = sf_result["id"]
                                org.external_source = "salesforce"
                                result["created"] += 1

                    except Exception as e:
                        result["failed"] += 1
                        result["errors"].append(f"Failed to sync organization {org.id}: {str(e)}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Organizations to SF sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def handle_webhook(self, event: WebhookEvent) -> bool:
        """Handle Salesforce webhook events"""
        try:
            event_type = event.event_type
            payload = event.payload

            if event_type in ["opportunity_created", "opportunity_updated"]:
                await self._handle_opportunity_webhook(payload)
            elif event_type in ["account_created", "account_updated"]:
                await self._handle_account_webhook(payload)
            elif event_type in ["contact_created", "contact_updated"]:
                await self._handle_contact_webhook(payload)

            return True

        except Exception as e:
            logger.error(f"Salesforce webhook handling error: {str(e)}")
            return False

    async def _handle_opportunity_webhook(self, payload: Dict[str, Any]):
        """Handle opportunity webhook events"""
        # Trigger immediate sync for the specific opportunity
        await self.sync_data(SyncDirection.INBOUND)

    async def _handle_account_webhook(self, payload: Dict[str, Any]):
        """Handle account webhook events"""
        # Trigger immediate sync for the specific account
        await self.sync_data(SyncDirection.INBOUND)

    async def _handle_contact_webhook(self, payload: Dict[str, Any]):
        """Handle contact webhook events"""
        # Trigger immediate sync for the specific contact
        await self.sync_data(SyncDirection.INBOUND)

    async def get_supported_entities(self) -> List[str]:
        """Get list of entities this integration can sync"""
        return ["deals", "organizations", "contacts", "opportunities", "accounts"]

    # Helper methods

    async def _find_existing_deal(self, db: AsyncSession, external_id: str) -> Optional[Deal]:
        """Find existing deal by external ID"""
        query = select(Deal).where(
            Deal.external_id == external_id,
            Deal.external_source == "salesforce"
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _find_existing_organization(self, db: AsyncSession, external_id: str) -> Optional[Organization]:
        """Find existing organization by external ID"""
        query = select(Organization).where(
            Organization.external_id == external_id,
            Organization.external_source == "salesforce"
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _find_existing_contact(self, db: AsyncSession, external_id: str) -> Optional[Contact]:
        """Find existing contact by external ID"""
        query = select(Contact).where(
            Contact.external_id == external_id,
            Contact.external_source == "salesforce"
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    def _map_sf_stage_to_platform(self, sf_stage: Optional[str]) -> str:
        """Map Salesforce stage to platform stage"""
        stage_mapping = {
            "Prospecting": "sourcing",
            "Qualification": "initial_review",
            "Proposal/Price Quote": "valuation",
            "Negotiation/Review": "negotiation",
            "Closed Won": "closed_won",
            "Closed Lost": "closed_lost"
        }
        return stage_mapping.get(sf_stage, "sourcing")

    def _map_platform_stage_to_sf(self, platform_stage: Optional[str]) -> str:
        """Map platform stage to Salesforce stage"""
        stage_mapping = {
            "sourcing": "Prospecting",
            "initial_review": "Qualification",
            "valuation": "Proposal/Price Quote",
            "negotiation": "Negotiation/Review",
            "closed_won": "Closed Won",
            "closed_lost": "Closed Lost"
        }
        return stage_mapping.get(platform_stage, "Prospecting")

    def _parse_sf_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Salesforce date string to datetime"""
        if not date_str:
            return None

        try:
            # Salesforce typically returns ISO format dates
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None