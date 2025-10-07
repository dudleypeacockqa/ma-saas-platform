"""
Enhanced Companies House API Integration
Advanced UK company data retrieval with filtering and financial analysis
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
import asyncio

from app.integrations.companies_house import CompaniesHouseAPI

logger = logging.getLogger(__name__)


class EnhancedCompaniesHouseAPI(CompaniesHouseAPI):
    """
    Enhanced Companies House API with advanced discovery features
    Extends base CompaniesHouseAPI with filtering and scoring capabilities
    """

    async def discover_opportunities(
        self,
        min_revenue_millions: float = 1.0,
        max_revenue_millions: float = 50.0,
        industries: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        min_employees: Optional[int] = None,
        max_employees: Optional[int] = None,
        company_status: str = "active",
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Discover M&A opportunities based on criteria

        Args:
            min_revenue_millions: Minimum revenue in millions
            max_revenue_millions: Maximum revenue in millions
            industries: List of SIC codes or industry sectors
            regions: List of UK regions
            min_employees: Minimum number of employees
            max_employees: Maximum number of employees
            company_status: Company status (active, dissolved, etc.)
            max_results: Maximum number of results to return

        Returns:
            List of company opportunities with scores
        """
        opportunities = []

        try:
            # Search for companies (iterative approach)
            search_terms = self._generate_search_terms(industries, regions)

            for search_term in search_terms[:10]:  # Limit search iterations
                try:
                    results = await self.search_companies(
                        query=search_term,
                        items_per_page=20,
                        active_only=(company_status == "active")
                    )

                    if results.get("items"):
                        for company in results["items"]:
                            # Get detailed company info
                            company_number = company.get("company_number")
                            if not company_number:
                                continue

                            detailed_company = await self.get_company_details(company_number)

                            if detailed_company:
                                # Filter by criteria
                                if await self._meets_criteria(
                                    detailed_company,
                                    min_revenue_millions,
                                    max_revenue_millions,
                                    min_employees,
                                    max_employees,
                                    industries,
                                    regions
                                ):
                                    opportunities.append(detailed_company)

                            # Respect rate limits
                            await asyncio.sleep(0.1)

                            if len(opportunities) >= max_results:
                                break

                    if len(opportunities) >= max_results:
                        break

                except Exception as e:
                    logger.error(f"Error searching with term '{search_term}': {e}")
                    continue

        except Exception as e:
            logger.error(f"Error discovering opportunities: {e}")

        return opportunities[:max_results]

    async def get_company_full_profile(
        self,
        company_number: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive company profile including financials, officers, and filings

        Args:
            company_number: Companies House company number

        Returns:
            Complete company profile with all available data
        """
        profile = {
            "company_details": None,
            "officers": [],
            "financials": {},
            "filing_history": [],
            "persons_with_significant_control": [],
            "charges": [],
            "insolvency": None
        }

        try:
            # Get basic company details
            profile["company_details"] = await self.get_company_details(company_number)

            # Get officers (directors)
            profile["officers"] = await self.get_company_officers(company_number)

            # Get accounts (financials)
            accounts = await self.get_company_accounts(company_number)
            if accounts:
                profile["financials"] = await self._parse_accounts(accounts, company_number)

            # Get filing history
            profile["filing_history"] = await self.get_filing_history(company_number)

            # Get PSC (Persons with Significant Control)
            profile["persons_with_significant_control"] = await self.get_psc(company_number)

            # Get charges (if any)
            profile["charges"] = await self.get_charges(company_number)

            # Get insolvency information
            profile["insolvency"] = await self.get_insolvency(company_number)

        except Exception as e:
            logger.error(f"Error getting company profile for {company_number}: {e}")

        return profile

    async def get_company_accounts(
        self,
        company_number: str
    ) -> Optional[Dict[str, Any]]:
        """Get company accounts/financial data"""
        try:
            url = f"{self.BASE_URL}/company/{company_number}/filing-history"
            params = {"category": "accounts"}

            response = await self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get("items", [])

        except Exception as e:
            logger.error(f"Error getting accounts for {company_number}: {e}")
            return None

    async def get_psc(
        self,
        company_number: str
    ) -> List[Dict[str, Any]]:
        """Get persons with significant control"""
        try:
            url = f"{self.BASE_URL}/company/{company_number}/persons-with-significant-control"

            response = await self.session.get(url)
            response.raise_for_status()

            data = response.json()
            return data.get("items", [])

        except Exception as e:
            logger.error(f"Error getting PSC for {company_number}: {e}")
            return []

    async def get_charges(
        self,
        company_number: str
    ) -> List[Dict[str, Any]]:
        """Get company charges (mortgages, etc.)"""
        try:
            url = f"{self.BASE_URL}/company/{company_number}/charges"

            response = await self.session.get(url)
            if response.status_code == 404:
                return []  # No charges

            response.raise_for_status()

            data = response.json()
            return data.get("items", [])

        except Exception as e:
            logger.error(f"Error getting charges for {company_number}: {e}")
            return []

    async def get_insolvency(
        self,
        company_number: str
    ) -> Optional[Dict[str, Any]]:
        """Get insolvency information"""
        try:
            # Insolvency info is typically in company profile
            profile = await self.get_company_details(company_number)
            return profile.get("insolvency_history") if profile else None

        except Exception as e:
            logger.error(f"Error getting insolvency for {company_number}: {e}")
            return None

    async def analyze_financial_health(
        self,
        company_number: str
    ) -> Dict[str, Any]:
        """
        Analyze company's financial health based on available data

        Returns:
            Financial health score and indicators
        """
        health_analysis = {
            "health_score": 0,  # 0-100
            "health_rating": "unknown",
            "indicators": [],
            "red_flags": [],
            "green_flags": [],
            "financial_ratios": {}
        }

        try:
            profile = await self.get_company_full_profile(company_number)

            # Check for red flags
            if profile.get("insolvency"):
                health_analysis["red_flags"].append("Insolvency history")
                health_analysis["health_score"] -= 30

            charges = profile.get("charges", [])
            if len(charges) > 5:
                health_analysis["red_flags"].append(f"Multiple charges ({len(charges)})")
                health_analysis["health_score"] -= 10

            # Check filing history for overdue accounts
            filing_history = profile.get("filing_history", [])
            overdue_filings = [f for f in filing_history if f.get("status") == "overdue"]
            if overdue_filings:
                health_analysis["red_flags"].append("Overdue filings")
                health_analysis["health_score"] -= 20

            # Check accounts status
            company_details = profile.get("company_details", {})
            accounts = company_details.get("accounts", {})
            if accounts.get("overdue"):
                health_analysis["red_flags"].append("Overdue accounts")
                health_analysis["health_score"] -= 15

            # Positive indicators
            if accounts.get("last_accounts"):
                health_analysis["green_flags"].append("Recent accounts filed")
                health_analysis["health_score"] += 10

            psc = profile.get("persons_with_significant_control", [])
            if psc:
                health_analysis["green_flags"].append("Clear ownership structure")
                health_analysis["health_score"] += 5

            # Normalize score to 0-100
            health_analysis["health_score"] = max(0, min(100, health_analysis["health_score"] + 50))

            # Determine rating
            score = health_analysis["health_score"]
            if score >= 80:
                health_analysis["health_rating"] = "excellent"
            elif score >= 60:
                health_analysis["health_rating"] = "good"
            elif score >= 40:
                health_analysis["health_rating"] = "fair"
            elif score >= 20:
                health_analysis["health_rating"] = "poor"
            else:
                health_analysis["health_rating"] = "distressed"

        except Exception as e:
            logger.error(f"Error analyzing financial health for {company_number}: {e}")

        return health_analysis

    def _generate_search_terms(
        self,
        industries: Optional[List[str]],
        regions: Optional[List[str]]
    ) -> List[str]:
        """Generate search terms based on criteria"""
        terms = []

        # Common business terms by industry
        industry_keywords = {
            "technology": ["software", "tech", "digital", "IT", "saas"],
            "healthcare": ["health", "medical", "pharma", "clinic"],
            "manufacturing": ["manufacturing", "factory", "production"],
            "services": ["services", "consulting", "solutions"],
            "retail": ["retail", "shop", "store", "commerce"]
        }

        if industries:
            for industry in industries:
                if industry.lower() in industry_keywords:
                    terms.extend(industry_keywords[industry.lower()])

        # Add region-based terms
        if regions:
            terms.extend(regions)

        # Default broad terms if none specified
        if not terms:
            terms = ["limited", "ltd", "plc", "group"]

        return terms

    async def _meets_criteria(
        self,
        company: Dict[str, Any],
        min_revenue: float,
        max_revenue: float,
        min_employees: Optional[int],
        max_employees: Optional[int],
        industries: Optional[List[str]],
        regions: Optional[List[str]]
    ) -> bool:
        """Check if company meets discovery criteria"""

        # For now, basic filtering - would need accounts data for revenue
        # This is a placeholder for more sophisticated filtering

        # Check employee count if available
        if min_employees is not None or max_employees is not None:
            # Employee count not directly available in basic search
            pass

        # Check region
        if regions:
            company_region = company.get("registered_office_address", {}).get("region", "")
            if not any(region.lower() in company_region.lower() for region in regions):
                return False

        # Check SIC codes for industry matching
        if industries:
            company_sic_codes = [str(code) for code in company.get("sic_codes", [])]
            # Industry matching would need SIC code mapping
            pass

        return True

    async def _parse_accounts(
        self,
        accounts: List[Dict[str, Any]],
        company_number: str
    ) -> Dict[str, Any]:
        """Parse accounts data to extract financial metrics"""
        financial_data = {
            "latest_year": None,
            "revenue": None,
            "profit": None,
            "assets": None,
            "liabilities": None,
            "accounts_available": False
        }

        if not accounts:
            return financial_data

        # Get most recent accounts
        latest = accounts[0] if accounts else None
        if latest:
            financial_data["accounts_available"] = True
            financial_data["latest_year"] = latest.get("date")

            # Note: Actual financial figures require downloading and parsing XBRL documents
            # This would be implemented in a production system

        return financial_data


# Singleton instance
_enhanced_ch_api: Optional[EnhancedCompaniesHouseAPI] = None


def get_companies_house_api() -> EnhancedCompaniesHouseAPI:
    """Get or create Companies House API instance"""
    global _enhanced_ch_api
    if _enhanced_ch_api is None:
        _enhanced_ch_api = EnhancedCompaniesHouseAPI()
    return _enhanced_ch_api
