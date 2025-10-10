"""
Crunchbase API Integration
Startup and private company data retrieval for M&A sourcing
API Documentation: https://data.crunchbase.com/docs
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
import asyncio

logger = logging.getLogger(__name__)


class CrunchbaseAPI:
    """
    Integration with Crunchbase API for startup and private company data
    Provides funding history, company details, and M&A intelligence
    """

    BASE_URL = "https://api.crunchbase.com/api/v4"
    RATE_LIMIT_DELAY = 0.2  # Conservative rate limiting

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Crunchbase API client

        Args:
            api_key: Crunchbase API key (required for access)
        """
        self.api_key = api_key or os.getenv("CRUNCHBASE_API_KEY")

        if not self.api_key:
            logger.warning("CRUNCHBASE_API_KEY not set - Crunchbase integration disabled")

        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "100DaysAndBeyond/1.0",
                "Accept": "application/json"
            }
        )

        self.last_request_time = 0

    async def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - time_since_last)

        self.last_request_time = asyncio.get_event_loop().time()

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Crunchbase API

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            API response data
        """
        if not self.api_key:
            raise ValueError("Crunchbase API key not configured")

        await self._rate_limit()

        url = f"{self.BASE_URL}/{endpoint}"

        request_params = params or {}
        request_params["user_key"] = self.api_key

        try:
            response = await self.session.get(url, params=request_params)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Crunchbase API error: {e.response.status_code} - {e.response.text}")
            return {}
        except httpx.HTTPError as e:
            logger.error(f"Crunchbase request error: {e}")
            return {}

    async def search_organizations(
        self,
        query: str,
        location: Optional[str] = None,
        funding_min: Optional[int] = None,
        funding_max: Optional[int] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Search for organizations/companies

        Args:
            query: Search query (company name, keywords)
            location: Location filter (city, region, country)
            funding_min: Minimum total funding in USD
            funding_max: Maximum total funding in USD
            limit: Maximum number of results

        Returns:
            List of matching organizations
        """
        try:
            params = {
                "query": query,
                "limit": limit
            }

            if location:
                params["location_identifiers"] = location

            response = await self._request("searches/organizations", params)

            entities = response.get("entities", [])

            results = []
            for entity in entities:
                properties = entity.get("properties", {})

                org_data = {
                    "uuid": entity.get("uuid"),
                    "name": properties.get("name"),
                    "short_description": properties.get("short_description"),
                    "description": properties.get("description"),
                    "website": properties.get("website"),
                    "founded_on": properties.get("founded_on"),
                    "location": properties.get("location_identifiers", []),
                    "categories": properties.get("categories", []),
                    "num_employees": properties.get("num_employees_enum"),
                    "revenue_range": properties.get("revenue_range"),
                    "operating_status": properties.get("operating_status"),
                    "company_type": properties.get("company_type"),
                    "identifier": entity.get("identifier", {})
                }

                # Filter by funding if specified
                if funding_min or funding_max:
                    funding = properties.get("total_funding_usd", 0)
                    if funding_min and funding < funding_min:
                        continue
                    if funding_max and funding > funding_max:
                        continue
                    org_data["total_funding_usd"] = funding

                results.append(org_data)

            return results

        except Exception as e:
            logger.error(f"Error searching organizations: {e}")
            return []

    async def get_organization_details(
        self,
        org_uuid: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about an organization

        Args:
            org_uuid: Crunchbase organization UUID

        Returns:
            Detailed organization data
        """
        try:
            response = await self._request(f"entities/organizations/{org_uuid}")

            if not response or "properties" not in response:
                return {}

            properties = response.get("properties", {})
            cards = response.get("cards", {})

            details = {
                "uuid": org_uuid,
                "name": properties.get("name"),
                "legal_name": properties.get("legal_name"),
                "description": properties.get("description"),
                "short_description": properties.get("short_description"),
                "website": properties.get("website"),
                "linkedin_url": properties.get("linkedin_url"),
                "facebook_url": properties.get("facebook_url"),
                "twitter_url": properties.get("twitter_url"),
                "founded_on": properties.get("founded_on"),
                "closed_on": properties.get("closed_on"),
                "location": {
                    "city": properties.get("location_identifiers", [{}])[0] if properties.get("location_identifiers") else None,
                    "country": properties.get("location_identifiers", [{}])[0] if properties.get("location_identifiers") else None
                },
                "categories": properties.get("categories", []),
                "num_employees": properties.get("num_employees_enum"),
                "revenue_range": properties.get("revenue_range"),
                "operating_status": properties.get("operating_status"),
                "company_type": properties.get("company_type"),
                "contact_email": properties.get("contact_email"),
                "phone_number": properties.get("phone_number"),
                "ipo_status": properties.get("ipo_status"),
                "stock_symbol": properties.get("stock_symbol"),
                "last_funding_type": properties.get("last_funding_type"),
                "num_funding_rounds": properties.get("num_funding_rounds"),
                "total_funding_usd": properties.get("total_funding_usd"),
                "last_funding_at": properties.get("last_funding_at"),
                "funding_history": [],
                "acquisitions": [],
                "investors": [],
                "founders": []
            }

            # Extract funding rounds from cards
            if "funding_rounds" in cards:
                funding_rounds = cards["funding_rounds"]
                details["funding_history"] = [
                    {
                        "announced_on": round.get("properties", {}).get("announced_on"),
                        "funding_type": round.get("properties", {}).get("funding_type"),
                        "money_raised": round.get("properties", {}).get("money_raised"),
                        "num_investors": round.get("properties", {}).get("num_investors"),
                        "lead_investors": round.get("properties", {}).get("lead_investor_identifiers", [])
                    }
                    for round in funding_rounds
                ]

            # Extract acquisition history
            if "acquiree_acquisitions" in cards:
                acquisitions = cards["acquiree_acquisitions"]
                details["acquisitions"] = [
                    {
                        "announced_on": acq.get("properties", {}).get("announced_on"),
                        "acquirer": acq.get("properties", {}).get("acquirer_identifier"),
                        "price": acq.get("properties", {}).get("price_usd"),
                        "acquisition_type": acq.get("properties", {}).get("acquisition_type"),
                        "status": acq.get("properties", {}).get("acquisition_status")
                    }
                    for acq in acquisitions
                ]

            # Extract investors
            if "investors" in cards:
                investors = cards["investors"]
                details["investors"] = [
                    {
                        "name": inv.get("properties", {}).get("name"),
                        "investor_type": inv.get("properties", {}).get("investor_type"),
                        "uuid": inv.get("uuid")
                    }
                    for inv in investors
                ]

            # Extract founders
            if "founders" in cards:
                founders = cards["founders"]
                details["founders"] = [
                    {
                        "name": founder.get("properties", {}).get("name"),
                        "title": founder.get("properties", {}).get("title"),
                        "uuid": founder.get("uuid")
                    }
                    for founder in founders
                ]

            return details

        except Exception as e:
            logger.error(f"Error getting organization details for {org_uuid}: {e}")
            return {}

    async def discover_acquisition_targets(
        self,
        categories: Optional[List[str]] = None,
        min_funding: Optional[int] = None,
        max_funding: Optional[int] = None,
        employee_range: Optional[str] = None,
        revenue_range: Optional[str] = None,
        locations: Optional[List[str]] = None,
        operating_status: str = "active",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Discover potential acquisition targets based on criteria

        Args:
            categories: Industry categories
            min_funding: Minimum total funding in USD
            max_funding: Maximum total funding in USD
            employee_range: Employee count range (e.g., "11-50", "51-100")
            revenue_range: Revenue range
            locations: Geographic locations
            operating_status: Company status (active, closed, etc.)
            limit: Maximum number of results

        Returns:
            List of potential acquisition targets
        """
        targets = []

        try:
            # Build search parameters
            search_queries = []

            if categories:
                for category in categories[:5]:  # Limit category searches
                    search_queries.append(category)
            else:
                search_queries = ["technology", "software", "saas"]

            # Search for each category/query
            for query in search_queries:
                if len(targets) >= limit:
                    break

                results = await self.search_organizations(
                    query=query,
                    funding_min=min_funding,
                    funding_max=max_funding,
                    limit=25
                )

                for org in results:
                    if len(targets) >= limit:
                        break

                    # Apply additional filters
                    if employee_range and org.get("num_employees") != employee_range:
                        continue

                    if revenue_range and org.get("revenue_range") != revenue_range:
                        continue

                    if operating_status and org.get("operating_status") != operating_status:
                        continue

                    # Get detailed info
                    org_uuid = org.get("uuid")
                    if org_uuid:
                        detailed = await self.get_organization_details(org_uuid)
                        if detailed:
                            targets.append(detailed)

                    # Rate limiting
                    await asyncio.sleep(0.3)

        except Exception as e:
            logger.error(f"Error discovering acquisition targets: {e}")

        return targets[:limit]

    async def get_funding_trends(
        self,
        category: str,
        time_period_months: int = 12
    ) -> Dict[str, Any]:
        """
        Analyze funding trends for a specific category

        Args:
            category: Industry category
            time_period_months: Number of months to analyze

        Returns:
            Funding trend analysis
        """
        trends = {
            "category": category,
            "time_period_months": time_period_months,
            "total_funding": 0,
            "num_rounds": 0,
            "avg_round_size": 0,
            "top_funded_companies": [],
            "funding_by_stage": {}
        }

        try:
            # Search for companies in category
            companies = await self.search_organizations(query=category, limit=50)

            total_funding = 0
            num_rounds = 0
            stage_funding = {}

            for company in companies:
                org_uuid = company.get("uuid")
                if not org_uuid:
                    continue

                details = await self.get_organization_details(org_uuid)

                funding_history = details.get("funding_history", [])

                # Filter by time period
                cutoff_date = datetime.utcnow() - timedelta(days=time_period_months * 30)

                for round in funding_history:
                    announced_on = round.get("announced_on")
                    if not announced_on:
                        continue

                    round_date = datetime.fromisoformat(announced_on.split("T")[0])
                    if round_date < cutoff_date:
                        continue

                    money_raised = round.get("money_raised", {}).get("value", 0)
                    funding_type = round.get("funding_type", "unknown")

                    total_funding += money_raised
                    num_rounds += 1

                    stage_funding[funding_type] = stage_funding.get(funding_type, 0) + money_raised

            trends["total_funding"] = total_funding
            trends["num_rounds"] = num_rounds
            trends["avg_round_size"] = total_funding / num_rounds if num_rounds > 0 else 0
            trends["funding_by_stage"] = stage_funding

        except Exception as e:
            logger.error(f"Error analyzing funding trends: {e}")

        return trends

    async def close(self):
        """Close HTTP session"""
        await self.session.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Singleton instance
_crunchbase_api: Optional[CrunchbaseAPI] = None


def get_crunchbase_api() -> CrunchbaseAPI:
    """Get or create Crunchbase API instance"""
    global _crunchbase_api
    if _crunchbase_api is None:
        _crunchbase_api = CrunchbaseAPI()
    return _crunchbase_api
