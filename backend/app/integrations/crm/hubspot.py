"""
HubSpot CRM Integration
Lead management and deal pipeline synchronization with advanced automation
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import aiohttp
from hubspot import HubSpot
from hubspot.crm.deals import ApiException as DealsApiException
from hubspot.crm.companies import ApiException as CompaniesApiException
from hubspot.crm.contacts import ApiException as ContactsApiException

from ..core.integration_manager import (
    BaseIntegration, IntegrationConfig, SyncResult, WebhookEvent,
    SyncDirection, IntegrationStatus
)
from ...core.database import get_db
from ...models.deal import Deal
from ...models.contact import Contact
from ...models.organization import Organization
from ...models.lead import Lead

logger = logging.getLogger(__name__)


class HubSpotIntegration(BaseIntegration):
    """HubSpot CRM integration with lead management and deal automation"""

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.hubspot: Optional[HubSpot] = None
        self.field_mappings = {
            "deal": {
                "title": "dealname",
                "deal_value": "amount",
                "stage": "dealstage",
                "pipeline": "pipeline",
                "close_date": "closedate",
                "description": "description",
                "created_at": "createdate",
                "updated_at": "hs_lastmodifieddate",
                "source": "hs_deal_source"
            },
            "contact": {
                "first_name": "firstname",
                "last_name": "lastname",
                "email": "email",
                "phone": "phone",
                "company": "company",
                "title": "jobtitle",
                "lead_source": "hs_lead_source",
                "lifecycle_stage": "lifecyclestage",
                "created_at": "createdate",
                "updated_at": "lastmodifieddate"
            },
            "company": {
                "name": "name",
                "domain": "domain",
                "industry": "industry",
                "website": "website",
                "phone": "phone",
                "annual_revenue": "annualrevenue",
                "employee_count": "numberofemployees",
                "city": "city",
                "state": "state",
                "country": "country",
                "created_at": "createdate",
                "updated_at": "hs_lastmodifieddate"
            },
            "lead": {
                "email": "email",
                "first_name": "firstname",
                "last_name": "lastname",
                "company": "company",
                "phone": "phone",
                "source": "hs_lead_source",
                "score": "hubspotscore",
                "status": "hs_lead_status",
                "created_at": "createdate",
                "updated_at": "lastmodifieddate"
            }
        }

    async def authenticate(self) -> bool:
        """Authenticate with HubSpot using API key or OAuth2"""
        try:
            credentials = self.config.credentials

            if self.config.auth_type == "api_key":
                self.hubspot = HubSpot(api_key=credentials["api_key"])
            elif self.config.auth_type == "oauth2":
                self.hubspot = HubSpot(access_token=credentials["access_token"])
            else:
                logger.error(f"Unsupported auth type: {self.config.auth_type}")
                return False

            return True

        except Exception as e:
            logger.error(f"HubSpot authentication failed: {str(e)}")
            return False

    async def test_connection(self) -> bool:
        """Test HubSpot connection"""
        try:
            if not self.hubspot:
                return False

            # Test with a simple API call
            response = self.hubspot.crm.deals.basic_api.get_page(limit=1)
            return response is not None

        except Exception as e:
            logger.error(f"HubSpot connection test failed: {str(e)}")
            return False

    async def sync_data(self, direction: SyncDirection) -> SyncResult:
        """Synchronize data with HubSpot"""
        sync_id = f"hs_sync_{datetime.now().timestamp()}"
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
            if not self.hubspot:
                result.errors.append("Not authenticated with HubSpot")
                result.end_time = datetime.now()
                return result

            self.status = IntegrationStatus.SYNCING

            if direction in [SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL]:
                # Sync from HubSpot to M&A platform
                inbound_result = await self._sync_from_hubspot()
                result.records_processed += inbound_result["processed"]
                result.records_created += inbound_result["created"]
                result.records_updated += inbound_result["updated"]
                result.records_failed += inbound_result["failed"]
                result.errors.extend(inbound_result["errors"])

            if direction in [SyncDirection.OUTBOUND, SyncDirection.BIDIRECTIONAL]:
                # Sync from M&A platform to HubSpot
                outbound_result = await self._sync_to_hubspot()
                result.records_processed += outbound_result["processed"]
                result.records_created += outbound_result["created"]
                result.records_updated += outbound_result["updated"]
                result.records_failed += outbound_result["failed"]
                result.errors.extend(outbound_result["errors"])

            result.success = result.records_failed == 0
            result.end_time = datetime.now()
            self.last_sync = result.end_time
            self.status = IntegrationStatus.CONNECTED

            logger.info(f"HubSpot sync completed: {result.records_processed} processed, {result.records_failed} failed")

        except Exception as e:
            logger.error(f"HubSpot sync error: {str(e)}")
            result.errors.append(str(e))
            result.end_time = datetime.now()
            self.status = IntegrationStatus.ERROR

        return result

    async def _sync_from_hubspot(self) -> Dict[str, Any]:
        """Sync data from HubSpot to M&A platform"""
        result = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }

        try:
            # Sync deals
            deals_result = await self._sync_deals_from_hubspot()
            for key in result:
                if key in deals_result:
                    result[key] += deals_result[key]

            # Sync companies
            companies_result = await self._sync_companies_from_hubspot()
            for key in result:
                if key in companies_result:
                    result[key] += companies_result[key]

            # Sync contacts
            contacts_result = await self._sync_contacts_from_hubspot()
            for key in result:
                if key in contacts_result:
                    result[key] += contacts_result[key]

            # Sync leads
            leads_result = await self._sync_leads_from_hubspot()
            for key in result:
                if key in leads_result:
                    result[key] += leads_result[key]

        except Exception as e:
            result["errors"].append(f"Inbound sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_deals_from_hubspot(self) -> Dict[str, Any]:
        """Sync HubSpot deals to M&A platform"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            # Get recent deals from HubSpot
            last_sync_time = self.last_sync or (datetime.now() - timedelta(days=30))

            # Get all deals with required properties
            properties = list(self.field_mappings["deal"].values())

            # HubSpot pagination
            after = None
            has_more = True

            async with get_db() as db:
                while has_more:
                    try:
                        if after:
                            deals_page = self.hubspot.crm.deals.basic_api.get_page(
                                limit=100,
                                properties=properties,
                                after=after
                            )
                        else:
                            deals_page = self.hubspot.crm.deals.basic_api.get_page(
                                limit=100,
                                properties=properties
                            )

                        deals = deals_page.results
                        has_more = deals_page.paging is not None
                        after = deals_page.paging.next.after if has_more else None

                        for deal in deals:
                            try:
                                result["processed"] += 1

                                # Check if deal was modified since last sync
                                last_modified = self._parse_hubspot_date(
                                    deal.properties.get("hs_lastmodifieddate")
                                )

                                if last_modified and last_modified < last_sync_time:
                                    continue

                                # Check if deal already exists
                                existing_deal = await self._find_existing_deal(db, deal.id)

                                deal_data = {
                                    "title": deal.properties.get("dealname", ""),
                                    "deal_value": self._parse_amount(deal.properties.get("amount")),
                                    "stage": self._map_hubspot_stage_to_platform(
                                        deal.properties.get("dealstage")
                                    ),
                                    "expected_close_date": self._parse_hubspot_date(
                                        deal.properties.get("closedate")
                                    ),
                                    "description": deal.properties.get("description", ""),
                                    "external_id": deal.id,
                                    "external_source": "hubspot",
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
                                        "created_at": self._parse_hubspot_date(
                                            deal.properties.get("createdate")
                                        ) or datetime.now(),
                                        "is_active": True
                                    })
                                    new_deal = Deal(**deal_data)
                                    db.add(new_deal)
                                    result["created"] += 1

                            except Exception as e:
                                result["failed"] += 1
                                result["errors"].append(f"Failed to sync deal {deal.id}: {str(e)}")

                    except DealsApiException as e:
                        result["errors"].append(f"HubSpot API error: {str(e)}")
                        break

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Deals sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_companies_from_hubspot(self) -> Dict[str, Any]:
        """Sync HubSpot companies to M&A platform organizations"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            last_sync_time = self.last_sync or (datetime.now() - timedelta(days=30))
            properties = list(self.field_mappings["company"].values())

            after = None
            has_more = True

            async with get_db() as db:
                while has_more:
                    try:
                        if after:
                            companies_page = self.hubspot.crm.companies.basic_api.get_page(
                                limit=100,
                                properties=properties,
                                after=after
                            )
                        else:
                            companies_page = self.hubspot.crm.companies.basic_api.get_page(
                                limit=100,
                                properties=properties
                            )

                        companies = companies_page.results
                        has_more = companies_page.paging is not None
                        after = companies_page.paging.next.after if has_more else None

                        for company in companies:
                            try:
                                result["processed"] += 1

                                last_modified = self._parse_hubspot_date(
                                    company.properties.get("hs_lastmodifieddate")
                                )

                                if last_modified and last_modified < last_sync_time:
                                    continue

                                existing_org = await self._find_existing_organization(db, company.id)

                                org_data = {
                                    "name": company.properties.get("name", ""),
                                    "industry": company.properties.get("industry"),
                                    "website": company.properties.get("website"),
                                    "phone": company.properties.get("phone"),
                                    "annual_revenue": self._parse_amount(
                                        company.properties.get("annualrevenue")
                                    ),
                                    "employee_count": self._parse_number(
                                        company.properties.get("numberofemployees")
                                    ),
                                    "external_id": company.id,
                                    "external_source": "hubspot",
                                    "updated_at": datetime.now()
                                }

                                if existing_org:
                                    for field, value in org_data.items():
                                        setattr(existing_org, field, value)
                                    result["updated"] += 1
                                else:
                                    org_data.update({
                                        "created_at": self._parse_hubspot_date(
                                            company.properties.get("createdate")
                                        ) or datetime.now()
                                    })
                                    new_org = Organization(**org_data)
                                    db.add(new_org)
                                    result["created"] += 1

                            except Exception as e:
                                result["failed"] += 1
                                result["errors"].append(f"Failed to sync company {company.id}: {str(e)}")

                    except CompaniesApiException as e:
                        result["errors"].append(f"HubSpot Companies API error: {str(e)}")
                        break

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Companies sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_contacts_from_hubspot(self) -> Dict[str, Any]:
        """Sync HubSpot contacts to M&A platform"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            last_sync_time = self.last_sync or (datetime.now() - timedelta(days=30))
            properties = list(self.field_mappings["contact"].values())

            after = None
            has_more = True

            async with get_db() as db:
                while has_more:
                    try:
                        if after:
                            contacts_page = self.hubspot.crm.contacts.basic_api.get_page(
                                limit=100,
                                properties=properties,
                                after=after
                            )
                        else:
                            contacts_page = self.hubspot.crm.contacts.basic_api.get_page(
                                limit=100,
                                properties=properties
                            )

                        contacts = contacts_page.results
                        has_more = contacts_page.paging is not None
                        after = contacts_page.paging.next.after if has_more else None

                        for contact in contacts:
                            try:
                                result["processed"] += 1

                                last_modified = self._parse_hubspot_date(
                                    contact.properties.get("lastmodifieddate")
                                )

                                if last_modified and last_modified < last_sync_time:
                                    continue

                                existing_contact = await self._find_existing_contact(db, contact.id)

                                contact_data = {
                                    "first_name": contact.properties.get("firstname"),
                                    "last_name": contact.properties.get("lastname"),
                                    "email": contact.properties.get("email"),
                                    "phone": contact.properties.get("phone"),
                                    "title": contact.properties.get("jobtitle"),
                                    "external_id": contact.id,
                                    "external_source": "hubspot",
                                    "updated_at": datetime.now()
                                }

                                if existing_contact:
                                    for field, value in contact_data.items():
                                        setattr(existing_contact, field, value)
                                    result["updated"] += 1
                                else:
                                    contact_data.update({
                                        "created_at": self._parse_hubspot_date(
                                            contact.properties.get("createdate")
                                        ) or datetime.now()
                                    })
                                    new_contact = Contact(**contact_data)
                                    db.add(new_contact)
                                    result["created"] += 1

                            except Exception as e:
                                result["failed"] += 1
                                result["errors"].append(f"Failed to sync contact {contact.id}: {str(e)}")

                    except ContactsApiException as e:
                        result["errors"].append(f"HubSpot Contacts API error: {str(e)}")
                        break

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Contacts sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_leads_from_hubspot(self) -> Dict[str, Any]:
        """Sync HubSpot leads to M&A platform"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            # HubSpot doesn't have a separate leads object, so we sync contacts with lead status
            last_sync_time = self.last_sync or (datetime.now() - timedelta(days=30))
            properties = list(self.field_mappings["lead"].values())

            # Filter for contacts that are leads (lifecycle stage = lead)
            filter_group = {
                "filters": [{
                    "propertyName": "lifecyclestage",
                    "operator": "EQ",
                    "value": "lead"
                }]
            }

            async with get_db() as db:
                try:
                    # Use search API for filtered results
                    search_request = {
                        "filterGroups": [filter_group],
                        "properties": properties,
                        "limit": 100
                    }

                    search_response = self.hubspot.crm.contacts.search_api.do_search(
                        public_object_search_request=search_request
                    )

                    leads = search_response.results

                    for lead_contact in leads:
                        try:
                            result["processed"] += 1

                            last_modified = self._parse_hubspot_date(
                                lead_contact.properties.get("lastmodifieddate")
                            )

                            if last_modified and last_modified < last_sync_time:
                                continue

                            existing_lead = await self._find_existing_lead(db, lead_contact.id)

                            lead_data = {
                                "email": lead_contact.properties.get("email"),
                                "first_name": lead_contact.properties.get("firstname"),
                                "last_name": lead_contact.properties.get("lastname"),
                                "company": lead_contact.properties.get("company"),
                                "phone": lead_contact.properties.get("phone"),
                                "source": lead_contact.properties.get("hs_lead_source"),
                                "score": self._parse_number(
                                    lead_contact.properties.get("hubspotscore")
                                ),
                                "status": "new",  # Default status
                                "external_id": lead_contact.id,
                                "external_source": "hubspot",
                                "updated_at": datetime.now()
                            }

                            if existing_lead:
                                for field, value in lead_data.items():
                                    setattr(existing_lead, field, value)
                                result["updated"] += 1
                            else:
                                lead_data.update({
                                    "created_at": self._parse_hubspot_date(
                                        lead_contact.properties.get("createdate")
                                    ) or datetime.now()
                                })
                                new_lead = Lead(**lead_data)
                                db.add(new_lead)
                                result["created"] += 1

                        except Exception as e:
                            result["failed"] += 1
                            result["errors"].append(f"Failed to sync lead {lead_contact.id}: {str(e)}")

                except ContactsApiException as e:
                    result["errors"].append(f"HubSpot Leads search error: {str(e)}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Leads sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_to_hubspot(self) -> Dict[str, Any]:
        """Sync M&A platform data to HubSpot"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            # Sync deals to HubSpot
            deals_result = await self._sync_deals_to_hubspot()
            for key in result:
                if key in deals_result:
                    result[key] += deals_result[key]

            # Sync organizations to HubSpot companies
            companies_result = await self._sync_organizations_to_hubspot()
            for key in result:
                if key in companies_result:
                    result[key] += companies_result[key]

            # Sync leads to HubSpot contacts
            leads_result = await self._sync_leads_to_hubspot()
            for key in result:
                if key in leads_result:
                    result[key] += leads_result[key]

        except Exception as e:
            result["errors"].append(f"Outbound sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_deals_to_hubspot(self) -> Dict[str, Any]:
        """Sync M&A platform deals to HubSpot"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            async with get_db() as db:
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

                        deal_properties = {
                            "dealname": deal.title,
                            "amount": str(int(deal.deal_value)) if deal.deal_value else "0",
                            "dealstage": self._map_platform_stage_to_hubspot(deal.stage),
                            "closedate": deal.expected_close_date.isoformat() if deal.expected_close_date else None,
                            "description": deal.description or ""
                        }

                        # Remove None values
                        deal_properties = {k: v for k, v in deal_properties.items() if v is not None}

                        if deal.external_id and deal.external_source == "hubspot":
                            # Update existing HubSpot deal
                            self.hubspot.crm.deals.basic_api.update(
                                deal_id=deal.external_id,
                                simple_public_object_input={"properties": deal_properties}
                            )
                            result["updated"] += 1
                        else:
                            # Create new HubSpot deal
                            hs_result = self.hubspot.crm.deals.basic_api.create(
                                simple_public_object_input={"properties": deal_properties}
                            )
                            if hs_result.id:
                                deal.external_id = hs_result.id
                                deal.external_source = "hubspot"
                                result["created"] += 1

                    except Exception as e:
                        result["failed"] += 1
                        result["errors"].append(f"Failed to sync deal {deal.id}: {str(e)}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Deals to HubSpot sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_organizations_to_hubspot(self) -> Dict[str, Any]:
        """Sync M&A platform organizations to HubSpot companies"""
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

                        company_properties = {
                            "name": org.name,
                            "industry": org.industry,
                            "website": org.website,
                            "phone": org.phone,
                            "annualrevenue": str(int(org.annual_revenue)) if org.annual_revenue else None,
                            "numberofemployees": str(org.employee_count) if org.employee_count else None
                        }

                        # Remove None values
                        company_properties = {k: v for k, v in company_properties.items() if v is not None}

                        if org.external_id and org.external_source == "hubspot":
                            # Update existing HubSpot company
                            self.hubspot.crm.companies.basic_api.update(
                                company_id=org.external_id,
                                simple_public_object_input={"properties": company_properties}
                            )
                            result["updated"] += 1
                        else:
                            # Create new HubSpot company
                            hs_result = self.hubspot.crm.companies.basic_api.create(
                                simple_public_object_input={"properties": company_properties}
                            )
                            if hs_result.id:
                                org.external_id = hs_result.id
                                org.external_source = "hubspot"
                                result["created"] += 1

                    except Exception as e:
                        result["failed"] += 1
                        result["errors"].append(f"Failed to sync organization {org.id}: {str(e)}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Organizations to HubSpot sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_leads_to_hubspot(self) -> Dict[str, Any]:
        """Sync M&A platform leads to HubSpot contacts"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            async with get_db() as db:
                last_sync_time = self.last_sync or (datetime.now() - timedelta(days=30))

                leads_query = select(Lead).where(
                    Lead.updated_at >= last_sync_time
                )
                result_leads = await db.execute(leads_query)
                leads = result_leads.scalars().all()

                for lead in leads:
                    try:
                        result["processed"] += 1

                        contact_properties = {
                            "email": lead.email,
                            "firstname": lead.first_name,
                            "lastname": lead.last_name,
                            "company": lead.company,
                            "phone": lead.phone,
                            "hs_lead_source": lead.source,
                            "hubspotscore": str(lead.score) if lead.score else None,
                            "lifecyclestage": "lead"
                        }

                        # Remove None values
                        contact_properties = {k: v for k, v in contact_properties.items() if v is not None}

                        if lead.external_id and lead.external_source == "hubspot":
                            # Update existing HubSpot contact
                            self.hubspot.crm.contacts.basic_api.update(
                                contact_id=lead.external_id,
                                simple_public_object_input={"properties": contact_properties}
                            )
                            result["updated"] += 1
                        else:
                            # Create new HubSpot contact
                            hs_result = self.hubspot.crm.contacts.basic_api.create(
                                simple_public_object_input={"properties": contact_properties}
                            )
                            if hs_result.id:
                                lead.external_id = hs_result.id
                                lead.external_source = "hubspot"
                                result["created"] += 1

                    except Exception as e:
                        result["failed"] += 1
                        result["errors"].append(f"Failed to sync lead {lead.id}: {str(e)}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Leads to HubSpot sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def handle_webhook(self, event: WebhookEvent) -> bool:
        """Handle HubSpot webhook events"""
        try:
            event_type = event.event_type
            payload = event.payload

            if event_type.startswith("deal."):
                await self._handle_deal_webhook(payload)
            elif event_type.startswith("company."):
                await self._handle_company_webhook(payload)
            elif event_type.startswith("contact."):
                await self._handle_contact_webhook(payload)

            return True

        except Exception as e:
            logger.error(f"HubSpot webhook handling error: {str(e)}")
            return False

    async def _handle_deal_webhook(self, payload: Dict[str, Any]):
        """Handle deal webhook events"""
        # Trigger immediate sync for deals
        await self.sync_data(SyncDirection.INBOUND)

    async def _handle_company_webhook(self, payload: Dict[str, Any]):
        """Handle company webhook events"""
        # Trigger immediate sync for companies
        await self.sync_data(SyncDirection.INBOUND)

    async def _handle_contact_webhook(self, payload: Dict[str, Any]):
        """Handle contact webhook events"""
        # Trigger immediate sync for contacts
        await self.sync_data(SyncDirection.INBOUND)

    async def get_supported_entities(self) -> List[str]:
        """Get list of entities this integration can sync"""
        return ["deals", "companies", "contacts", "leads", "organizations"]

    # Helper methods

    async def _find_existing_deal(self, db, external_id: str) -> Optional[Deal]:
        """Find existing deal by external ID"""
        query = select(Deal).where(
            Deal.external_id == external_id,
            Deal.external_source == "hubspot"
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _find_existing_organization(self, db, external_id: str) -> Optional[Organization]:
        """Find existing organization by external ID"""
        query = select(Organization).where(
            Organization.external_id == external_id,
            Organization.external_source == "hubspot"
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _find_existing_contact(self, db, external_id: str) -> Optional[Contact]:
        """Find existing contact by external ID"""
        query = select(Contact).where(
            Contact.external_id == external_id,
            Contact.external_source == "hubspot"
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _find_existing_lead(self, db, external_id: str) -> Optional[Lead]:
        """Find existing lead by external ID"""
        query = select(Lead).where(
            Lead.external_id == external_id,
            Lead.external_source == "hubspot"
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    def _map_hubspot_stage_to_platform(self, hs_stage: Optional[str]) -> str:
        """Map HubSpot deal stage to platform stage"""
        stage_mapping = {
            "appointmentscheduled": "initial_review",
            "qualifiedtobuy": "preliminary_analysis",
            "presentationscheduled": "valuation",
            "decisionmakerboughtin": "due_diligence",
            "contractsent": "negotiation",
            "closedwon": "closed_won",
            "closedlost": "closed_lost"
        }
        return stage_mapping.get(hs_stage, "sourcing")

    def _map_platform_stage_to_hubspot(self, platform_stage: Optional[str]) -> str:
        """Map platform stage to HubSpot deal stage"""
        stage_mapping = {
            "sourcing": "appointmentscheduled",
            "initial_review": "appointmentscheduled",
            "preliminary_analysis": "qualifiedtobuy",
            "valuation": "presentationscheduled",
            "due_diligence": "decisionmakerboughtin",
            "negotiation": "contractsent",
            "closed_won": "closedwon",
            "closed_lost": "closedlost"
        }
        return stage_mapping.get(platform_stage, "appointmentscheduled")

    def _parse_hubspot_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse HubSpot date string to datetime"""
        if not date_str:
            return None

        try:
            # HubSpot returns timestamps in milliseconds
            timestamp = int(date_str) / 1000
            return datetime.fromtimestamp(timestamp)
        except (ValueError, TypeError):
            return None

    def _parse_amount(self, amount_str: Optional[str]) -> Optional[float]:
        """Parse amount string to float"""
        if not amount_str:
            return None

        try:
            return float(amount_str)
        except (ValueError, TypeError):
            return None

    def _parse_number(self, number_str: Optional[str]) -> Optional[int]:
        """Parse number string to int"""
        if not number_str:
            return None

        try:
            return int(float(number_str))
        except (ValueError, TypeError):
            return None