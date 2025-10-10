"""
SEC EDGAR API Integration
US Public Company data retrieval and analysis
API Documentation: https://www.sec.gov/edgar/sec-api-documentation
"""
import httpx
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import asyncio
from xml.etree import ElementTree as ET
import re

logger = logging.getLogger(__name__)


class SECEdgarAPI:
    """
    Integration with SEC EDGAR API
    Retrieves public company filings, financials, and insider transactions
    """

    BASE_URL = "https://www.sec.gov"
    API_BASE = "https://data.sec.gov"
    RATE_LIMIT_DELAY = 0.1  # 10 requests per second max

    def __init__(self, user_agent: Optional[str] = None):
        """
        Initialize SEC EDGAR API client

        Args:
            user_agent: User agent string (required by SEC)
                       Format: "Company Name Admin@email.com"
        """
        self.user_agent = user_agent or os.getenv(
            "SEC_EDGAR_USER_AGENT",
            "100DaysAndBeyond admin@100daysandbeyond.com"
        )

        if not self.user_agent or "@" not in self.user_agent:
            raise ValueError(
                "SEC_EDGAR_USER_AGENT must be set with format: 'Company Admin@email.com'"
            )

        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": self.user_agent,
                "Accept-Encoding": "gzip, deflate",
                "Host": "www.sec.gov"
            }
        )

        self.last_request_time = 0

    async def _rate_limit(self):
        """Enforce SEC rate limit (10 requests per second)"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - time_since_last)

        self.last_request_time = asyncio.get_event_loop().time()

    async def search_companies(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for companies by name or ticker

        Args:
            query: Company name or ticker symbol

        Returns:
            List of matching companies with CIK numbers
        """
        await self._rate_limit()

        url = f"{self.API_BASE}/cik-lookup-data.txt"

        try:
            response = await self.session.get(url)
            response.raise_for_status()

            # Parse the company list
            companies = []
            for line in response.text.split("\n"):
                if query.lower() in line.lower():
                    parts = line.split(":")
                    if len(parts) == 2:
                        company_name = parts[0].strip()
                        cik = parts[1].strip()
                        companies.append({
                            "company_name": company_name,
                            "cik": cik.zfill(10)  # Pad CIK to 10 digits
                        })

            return companies[:20]  # Return top 20 matches

        except httpx.HTTPError as e:
            logger.error(f"SEC EDGAR API error: {str(e)}")
            return []

    async def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """
        Get comprehensive company facts and financials

        Args:
            cik: Central Index Key (CIK) number

        Returns:
            Company facts data including all reported financial metrics
        """
        await self._rate_limit()

        # Ensure CIK is properly formatted (10 digits)
        cik = cik.zfill(10)
        url = f"{self.API_BASE}/api/xbrl/companyfacts/CIK{cik}.json"

        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Company facts not found for CIK {cik}")
                return {}
            raise

    async def get_company_submissions(self, cik: str) -> Dict[str, Any]:
        """
        Get company submission history

        Args:
            cik: Central Index Key

        Returns:
            Submission history including recent filings
        """
        await self._rate_limit()

        cik = cik.zfill(10)
        url = f"{self.API_BASE}/submissions/CIK{cik}.json"

        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error fetching submissions: {str(e)}")
            return {}

    async def get_recent_filings(
        self,
        cik: str,
        filing_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent filings for a company

        Args:
            cik: Central Index Key
            filing_type: Filter by filing type (e.g., '10-K', '10-Q', '8-K')
            limit: Number of filings to return

        Returns:
            List of recent filings
        """
        submissions = await self.get_company_submissions(cik)

        if not submissions:
            return []

        recent_filings = submissions.get("filings", {}).get("recent", {})

        if not recent_filings:
            return []

        # Combine arrays into list of dicts
        filings = []
        filing_count = len(recent_filings.get("accessionNumber", []))

        for i in range(filing_count):
            filing = {
                "accessionNumber": recent_filings["accessionNumber"][i],
                "filingDate": recent_filings["filingDate"][i],
                "reportDate": recent_filings["reportDate"][i],
                "form": recent_filings["form"][i],
                "primaryDocument": recent_filings["primaryDocument"][i],
                "primaryDocDescription": recent_filings.get("primaryDocDescription", [""])[i]
            }

            # Filter by type if specified
            if filing_type and filing["form"] != filing_type:
                continue

            filings.append(filing)

            if len(filings) >= limit:
                break

        return filings

    async def get_company_concept(
        self,
        cik: str,
        taxonomy: str,
        tag: str
    ) -> Dict[str, Any]:
        """
        Get specific financial concept data

        Args:
            cik: Central Index Key
            taxonomy: Taxonomy (e.g., 'us-gaap', 'ifrs-full', 'dei')
            tag: XBRL tag (e.g., 'Revenues', 'Assets')

        Returns:
            Financial concept data across all periods
        """
        await self._rate_limit()

        cik = cik.zfill(10)
        url = f"{self.API_BASE}/api/xbrl/companyconcept/CIK{cik}/{taxonomy}/{tag}.json"

        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error fetching concept {tag}: {str(e)}")
            return {}

    async def get_comprehensive_company_data(self, cik: str) -> Dict[str, Any]:
        """
        Fetch all available data for a company

        Args:
            cik: Central Index Key

        Returns:
            Comprehensive company data
        """
        cik = cik.zfill(10)

        # Fetch data concurrently
        facts_task = self.get_company_facts(cik)
        submissions_task = self.get_company_submissions(cik)
        filings_10k_task = self.get_recent_filings(cik, "10-K", 5)
        filings_10q_task = self.get_recent_filings(cik, "10-Q", 5)

        facts, submissions, filings_10k, filings_10q = await asyncio.gather(
            facts_task,
            submissions_task,
            filings_10k_task,
            filings_10q_task,
            return_exceptions=True
        )

        return {
            "cik": cik,
            "company_facts": facts if not isinstance(facts, Exception) else {},
            "submissions": submissions if not isinstance(submissions, Exception) else {},
            "annual_reports": filings_10k if not isinstance(filings_10k, Exception) else [],
            "quarterly_reports": filings_10q if not isinstance(filings_10q, Exception) else [],
            "retrieved_at": datetime.utcnow().isoformat()
        }

    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class SECEdgarDataParser:
    """
    Parse and normalize SEC EDGAR data
    """

    @staticmethod
    def parse_company_facts(facts: Dict[str, Any]) -> Dict[str, Any]:
        """Parse company facts into normalized financial data"""
        if not facts:
            return {}

        parsed = {
            "cik": facts.get("cik"),
            "entity_name": facts.get("entityName"),
            "financials": {}
        }

        # Extract US-GAAP facts
        us_gaap = facts.get("facts", {}).get("us-gaap", {})

        # Key financial metrics to extract
        metrics = {
            "Revenues": "revenue",
            "RevenueFromContractWithCustomerExcludingAssessedTax": "revenue_alt",
            "NetIncomeLoss": "net_income",
            "Assets": "total_assets",
            "Liabilities": "total_liabilities",
            "StockholdersEquity": "shareholders_equity",
            "CashAndCashEquivalentsAtCarryingValue": "cash",
            "EarningsPerShareBasic": "eps_basic",
            "OperatingIncomeLoss": "operating_income"
        }

        for xbrl_tag, normalized_name in metrics.items():
            if xbrl_tag in us_gaap:
                metric_data = us_gaap[xbrl_tag]

                # Get annual values (10-K filings)
                units = metric_data.get("units", {})

                # Most financial data is in USD
                usd_data = units.get("USD", [])

                if usd_data:
                    # Get most recent annual value
                    annual_values = [
                        item for item in usd_data
                        if item.get("form") == "10-K" and item.get("val")
                    ]

                    if annual_values:
                        # Sort by filed date
                        annual_values.sort(
                            key=lambda x: x.get("filed", ""),
                            reverse=True
                        )

                        parsed["financials"][normalized_name] = {
                            "value": annual_values[0]["val"],
                            "end_date": annual_values[0].get("end"),
                            "filed_date": annual_values[0].get("filed"),
                            "fiscal_year": annual_values[0].get("fy"),
                            "fiscal_period": annual_values[0].get("fp")
                        }

        return parsed

    @staticmethod
    def extract_financial_metrics(company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key financial metrics from comprehensive company data

        Args:
            company_data: Output from get_comprehensive_company_data()

        Returns:
            Normalized financial metrics
        """
        facts = company_data.get("company_facts", {})
        parsed_facts = SECEdgarDataParser.parse_company_facts(facts)

        financials = parsed_facts.get("financials", {})

        # Calculate derived metrics
        metrics = {
            "company_name": parsed_facts.get("entity_name"),
            "cik": parsed_facts.get("cik"),
            "latest_revenue": financials.get("revenue", {}).get("value") or
                            financials.get("revenue_alt", {}).get("value"),
            "latest_net_income": financials.get("net_income", {}).get("value"),
            "latest_total_assets": financials.get("total_assets", {}).get("value"),
            "latest_total_liabilities": financials.get("total_liabilities", {}).get("value"),
            "latest_shareholders_equity": financials.get("shareholders_equity", {}).get("value"),
            "latest_cash": financials.get("cash", {}).get("value"),
            "latest_operating_income": financials.get("operating_income", {}).get("value")
        }

        # Calculate ratios
        if metrics["latest_revenue"] and metrics["latest_net_income"]:
            metrics["profit_margin"] = (
                metrics["latest_net_income"] / metrics["latest_revenue"]
            )

        if metrics["latest_total_assets"]:
            if metrics["latest_net_income"]:
                metrics["roa"] = metrics["latest_net_income"] / metrics["latest_total_assets"]

            if metrics["latest_total_liabilities"]:
                equity = metrics["latest_total_assets"] - metrics["latest_total_liabilities"]
                if equity > 0:
                    metrics["debt_to_equity"] = metrics["latest_total_liabilities"] / equity

        return metrics

    @staticmethod
    def calculate_revenue_growth(facts: Dict[str, Any], years: int = 3) -> Optional[float]:
        """
        Calculate revenue CAGR

        Args:
            facts: Company facts from SEC
            years: Number of years for CAGR calculation

        Returns:
            Revenue CAGR as decimal (e.g., 0.15 for 15% growth)
        """
        us_gaap = facts.get("facts", {}).get("us-gaap", {})

        revenue_data = us_gaap.get("Revenues") or us_gaap.get(
            "RevenueFromContractWithCustomerExcludingAssessedTax"
        )

        if not revenue_data:
            return None

        usd_data = revenue_data.get("units", {}).get("USD", [])

        # Get annual values
        annual_values = [
            item for item in usd_data
            if item.get("form") == "10-K" and item.get("val") and item.get("fy")
        ]

        if len(annual_values) < years + 1:
            return None

        # Sort by fiscal year
        annual_values.sort(key=lambda x: int(x.get("fy", 0)), reverse=True)

        # Get most recent and oldest value
        latest = annual_values[0]["val"]
        oldest = annual_values[years]["val"]

        if oldest <= 0:
            return None

        # Calculate CAGR
        cagr = (pow(latest / oldest, 1 / years) - 1)

        return cagr

    @staticmethod
    def identify_growth_companies(
        facts: Dict[str, Any],
        min_growth_rate: float = 0.15
    ) -> bool:
        """
        Identify if company is high-growth

        Args:
            facts: Company facts from SEC
            min_growth_rate: Minimum CAGR threshold (default 15%)

        Returns:
            True if company meets growth criteria
        """
        growth_3yr = SECEdgarDataParser.calculate_revenue_growth(facts, years=3)

        if growth_3yr and growth_3yr >= min_growth_rate:
            return True

        return False
