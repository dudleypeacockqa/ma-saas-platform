"""
Companies House API Integration
UK Company data retrieval and analysis
API Documentation: https://developer.company-information.service.gov.uk/
"""
import httpx
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from requests_ratelimiter import LimiterSession
import asyncio

logger = logging.getLogger(__name__)


class CompaniesHouseAPI:
    """
    Integration with UK Companies House API
    Retrieves company financials, directors, and filing information
    """

    BASE_URL = "https://api.company-information.service.gov.uk"
    RATE_LIMIT = 600  # 600 requests per 5 minutes

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("COMPANIES_HOUSE_API_KEY")
        if not self.api_key:
            raise ValueError("COMPANIES_HOUSE_API_KEY environment variable not set")

        # Rate-limited session
        self.session = httpx.AsyncClient(
            auth=(self.api_key, ""),
            timeout=30.0,
            headers={"User-Agent": "100DaysAndBeyond/1.0"}
        )

    async def search_companies(
        self,
        query: str,
        items_per_page: int = 20,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """
        Search for companies by name or number

        Args:
            query: Company name or number
            items_per_page: Number of results to return
            active_only: Filter to active companies only

        Returns:
            Dictionary containing search results
        """
        url = f"{self.BASE_URL}/search/companies"
        params = {
            "q": query,
            "items_per_page": items_per_page
        }

        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if active_only:
                # Filter to only active companies
                data['items'] = [
                    item for item in data.get('items', [])
                    if item.get('company_status') == 'active'
                ]

            return data

        except httpx.HTTPError as e:
            logger.error(f"Companies House API error: {str(e)}")
            raise

    async def get_company_profile(self, company_number: str) -> Dict[str, Any]:
        """
        Get detailed company profile

        Args:
            company_number: Companies House company number

        Returns:
            Company profile data
        """
        url = f"{self.BASE_URL}/company/{company_number}"

        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Company {company_number} not found")
                return {}
            raise

    async def get_company_officers(
        self,
        company_number: str,
        register_view: bool = False
    ) -> Dict[str, Any]:
        """
        Get company directors and officers

        Args:
            company_number: Companies House company number
            register_view: Include full register view

        Returns:
            Officers data
        """
        url = f"{self.BASE_URL}/company/{company_number}/officers"
        params = {"register_view": str(register_view).lower()}

        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error fetching officers for {company_number}: {str(e)}")
            return {"items": []}

    async def get_filing_history(
        self,
        company_number: str,
        category: Optional[str] = None,
        items_per_page: int = 25
    ) -> Dict[str, Any]:
        """
        Get company filing history

        Args:
            company_number: Companies House company number
            category: Filter by filing category (e.g., 'accounts', 'confirmation-statement')
            items_per_page: Number of results

        Returns:
            Filing history data
        """
        url = f"{self.BASE_URL}/company/{company_number}/filing-history"
        params = {"items_per_page": items_per_page}

        if category:
            params["category"] = category

        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error fetching filing history: {str(e)}")
            return {"items": []}

    async def get_company_financials(self, company_number: str) -> Optional[Dict[str, Any]]:
        """
        Extract financial data from company accounts

        Args:
            company_number: Companies House company number

        Returns:
            Parsed financial data
        """
        # Get filing history filtered to accounts
        filings = await self.get_filing_history(
            company_number,
            category="accounts"
        )

        if not filings.get("items"):
            logger.warning(f"No accounts found for company {company_number}")
            return None

        latest_accounts = filings["items"][0]

        # Note: Full financial statements require document download
        # This returns metadata about the latest accounts
        return {
            "filing_date": latest_accounts.get("date"),
            "filing_type": latest_accounts.get("type"),
            "description": latest_accounts.get("description"),
            "period_end": latest_accounts.get("made_up_to"),
            "document_available": latest_accounts.get("links", {}).get("document_metadata") is not None
        }

    async def get_company_persons_with_significant_control(
        self,
        company_number: str
    ) -> Dict[str, Any]:
        """
        Get persons with significant control (PSC) - ownership information

        Args:
            company_number: Companies House company number

        Returns:
            PSC data
        """
        url = f"{self.BASE_URL}/company/{company_number}/persons-with-significant-control"

        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error fetching PSC data: {str(e)}")
            return {"items": []}

    async def get_company_charges(self, company_number: str) -> Dict[str, Any]:
        """
        Get company charges (secured debts)

        Args:
            company_number: Companies House company number

        Returns:
            Charges data
        """
        url = f"{self.BASE_URL}/company/{company_number}/charges"

        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error fetching charges: {str(e)}")
            return {"items": []}

    async def get_comprehensive_company_data(
        self,
        company_number: str
    ) -> Dict[str, Any]:
        """
        Fetch all available data for a company in one call

        Args:
            company_number: Companies House company number

        Returns:
            Comprehensive company data
        """
        # Fetch all data concurrently
        profile_task = self.get_company_profile(company_number)
        officers_task = self.get_company_officers(company_number)
        filings_task = self.get_filing_history(company_number)
        financials_task = self.get_company_financials(company_number)
        psc_task = self.get_company_persons_with_significant_control(company_number)
        charges_task = self.get_company_charges(company_number)

        profile, officers, filings, financials, psc, charges = await asyncio.gather(
            profile_task,
            officers_task,
            filings_task,
            financials_task,
            psc_task,
            charges_task,
            return_exceptions=True
        )

        return {
            "company_number": company_number,
            "profile": profile if not isinstance(profile, Exception) else {},
            "officers": officers if not isinstance(officers, Exception) else {"items": []},
            "filing_history": filings if not isinstance(filings, Exception) else {"items": []},
            "latest_financials": financials if not isinstance(financials, Exception) else None,
            "persons_with_significant_control": psc if not isinstance(psc, Exception) else {"items": []},
            "charges": charges if not isinstance(charges, Exception) else {"items": []},
            "retrieved_at": datetime.utcnow().isoformat()
        }

    async def search_companies_by_sic(
        self,
        sic_code: str,
        items_per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search for companies by SIC code (industry classification)

        Args:
            sic_code: Standard Industrial Classification code
            items_per_page: Number of results

        Returns:
            Search results
        """
        url = f"{self.BASE_URL}/advanced-search/companies"
        params = {
            "sic_codes": sic_code,
            "size": items_per_page
        }

        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error searching by SIC: {str(e)}")
            return {"items": []}

    async def identify_distressed_companies(
        self,
        industry_sic: str,
        min_age_years: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Identify potentially distressed companies
        Based on filing patterns and company status

        Args:
            industry_sic: SIC code to search
            min_age_years: Minimum company age

        Returns:
            List of potentially distressed companies
        """
        companies = await self.search_companies_by_sic(industry_sic, items_per_page=100)
        distressed = []

        current_year = datetime.now().year

        for company in companies.get("items", []):
            company_number = company.get("company_number")
            if not company_number:
                continue

            # Check company age
            date_of_creation = company.get("date_of_creation")
            if date_of_creation:
                creation_year = int(date_of_creation.split("-")[0])
                if (current_year - creation_year) < min_age_years:
                    continue

            # Get filing history
            filings = await self.get_filing_history(company_number, category="accounts")

            # Indicators of distress:
            # - Overdue accounts
            # - Irregular filing patterns
            # - Qualified audit opinions (would need document analysis)

            if filings.get("overdue_count", 0) > 0:
                distressed.append({
                    "company_number": company_number,
                    "company_name": company.get("title"),
                    "status": company.get("company_status"),
                    "overdue_filings": filings.get("overdue_count"),
                    "distress_indicator": "overdue_filings"
                })

        return distressed

    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class CompaniesHouseDataParser:
    """
    Parse and normalize Companies House API responses
    """

    @staticmethod
    def parse_company_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
        """Parse company profile into normalized format"""
        return {
            "company_name": profile.get("company_name"),
            "company_number": profile.get("company_number"),
            "company_status": profile.get("company_status"),
            "company_type": profile.get("type"),
            "date_of_creation": profile.get("date_of_creation"),
            "registered_office_address": profile.get("registered_office_address"),
            "sic_codes": profile.get("sic_codes", []),
            "has_been_liquidated": profile.get("has_been_liquidated", False),
            "has_insolvency_history": profile.get("has_insolvency_history", False),
            "accounts": {
                "next_due": profile.get("accounts", {}).get("next_due"),
                "overdue": profile.get("accounts", {}).get("overdue", False),
                "last_made_up_to": profile.get("accounts", {}).get("last_accounts", {}).get("made_up_to")
            }
        }

    @staticmethod
    def extract_key_executives(officers: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key executives from officers data"""
        executives = []

        for officer in officers.get("items", []):
            if officer.get("resigned_on"):
                continue  # Skip resigned officers

            executives.append({
                "name": officer.get("name"),
                "officer_role": officer.get("officer_role"),
                "appointed_on": officer.get("appointed_on"),
                "occupation": officer.get("occupation"),
                "nationality": officer.get("nationality"),
                "date_of_birth": officer.get("date_of_birth")
            })

        return executives

    @staticmethod
    def identify_succession_opportunity(
        officers: Dict[str, Any],
        age_threshold: int = 65
    ) -> bool:
        """
        Identify if company may be a succession opportunity
        Based on director ages and tenure
        """
        current_year = datetime.now().year

        for officer in officers.get("items", []):
            if officer.get("resigned_on"):
                continue

            # Check if director is likely retirement age
            dob = officer.get("date_of_birth", {})
            if dob:
                birth_year = dob.get("year")
                if birth_year and (current_year - birth_year) >= age_threshold:
                    return True

            # Check for long tenure (15+ years)
            appointed = officer.get("appointed_on")
            if appointed:
                appointed_year = int(appointed.split("-")[0])
                if (current_year - appointed_year) >= 15:
                    return True

        return False
