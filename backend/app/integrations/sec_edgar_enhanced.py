"""
Enhanced SEC EDGAR API Integration
Advanced US company data retrieval with M&A-focused features
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
import asyncio
import re
from xml.etree import ElementTree as ET

from app.integrations.sec_edgar import SECEdgarAPI, SECEdgarDataParser

logger = logging.getLogger(__name__)


class EnhancedSECEdgarAPI(SECEdgarAPI):
    """
    Enhanced SEC EDGAR API with M&A discovery and analysis features
    Extends base SECEdgarAPI with filtering, screening, and transaction history
    """

    async def discover_opportunities(
        self,
        min_revenue_millions: float = 1.0,
        max_revenue_millions: float = 50.0,
        industries: Optional[List[str]] = None,
        min_growth_rate: Optional[float] = None,
        profitability_required: bool = False,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Discover M&A opportunities based on financial criteria

        Args:
            min_revenue_millions: Minimum revenue in millions USD
            max_revenue_millions: Maximum revenue in millions USD
            industries: List of SIC codes or industry sectors
            min_growth_rate: Minimum revenue growth rate (CAGR)
            profitability_required: Filter to profitable companies only
            max_results: Maximum number of results to return

        Returns:
            List of company opportunities with financial metrics
        """
        opportunities = []

        try:
            # Note: SEC doesn't provide direct search by financials
            # This implementation uses a combination of company facts retrieval
            # and filtering. In production, you'd want to maintain a local database
            # of company financials for efficient querying.

            # Get company tickers file for bulk processing
            tickers_data = await self._get_company_tickers()

            if not tickers_data:
                logger.warning("Could not retrieve company tickers")
                return []

            # Process companies in batches
            batch_size = 20
            companies_checked = 0

            for ticker_info in list(tickers_data.values())[:200]:  # Limit initial scan
                if len(opportunities) >= max_results:
                    break

                try:
                    cik = str(ticker_info.get("cik_str")).zfill(10)

                    # Get company facts
                    facts = await self.get_company_facts(cik)

                    if not facts:
                        continue

                    # Parse financial data
                    parsed = SECEdgarDataParser.parse_company_facts(facts)
                    financials = parsed.get("financials", {})

                    # Get latest revenue
                    revenue_data = (
                        financials.get("revenue") or
                        financials.get("revenue_alt")
                    )

                    if not revenue_data:
                        continue

                    revenue = revenue_data.get("value", 0)
                    revenue_millions = revenue / 1_000_000

                    # Filter by revenue range
                    if not (min_revenue_millions <= revenue_millions <= max_revenue_millions):
                        continue

                    # Check profitability if required
                    if profitability_required:
                        net_income_data = financials.get("net_income")
                        if not net_income_data or net_income_data.get("value", 0) <= 0:
                            continue

                    # Check growth rate if specified
                    if min_growth_rate:
                        growth = SECEdgarDataParser.calculate_revenue_growth(facts, years=3)
                        if not growth or growth < min_growth_rate:
                            continue

                    # Get additional company data
                    submissions = await self.get_company_submissions(cik)

                    company_profile = {
                        "source": "SEC_EDGAR",
                        "cik": cik,
                        "ticker": ticker_info.get("ticker"),
                        "company_name": facts.get("entityName"),
                        "sic_code": submissions.get("sic"),
                        "sic_description": submissions.get("sicDescription"),
                        "business_address": submissions.get("addresses", {}).get("business"),
                        "revenue": revenue,
                        "revenue_millions": revenue_millions,
                        "financials": financials,
                        "filing_date": revenue_data.get("filed_date"),
                        "fiscal_year": revenue_data.get("fiscal_year"),
                        "retrieved_at": datetime.utcnow().isoformat()
                    }

                    opportunities.append(company_profile)
                    companies_checked += 1

                    # Rate limiting
                    await asyncio.sleep(0.15)

                except Exception as e:
                    logger.error(f"Error processing CIK {cik}: {e}")
                    continue

            logger.info(f"Discovered {len(opportunities)} opportunities after checking {companies_checked} companies")

        except Exception as e:
            logger.error(f"Error discovering opportunities: {e}")

        return opportunities[:max_results]

    async def get_company_full_profile(
        self,
        cik: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive company profile including financials, filings, and M&A history

        Args:
            cik: Central Index Key (CIK) number

        Returns:
            Complete company profile with all available data
        """
        profile = {
            "cik": cik,
            "company_info": None,
            "financials": {},
            "recent_filings": [],
            "annual_reports": [],
            "quarterly_reports": [],
            "ma_activity": [],
            "risk_factors": [],
            "insider_transactions": [],
            "financial_health": {}
        }

        try:
            # Get comprehensive data
            comprehensive_data = await self.get_comprehensive_company_data(cik)

            profile["company_info"] = comprehensive_data.get("submissions", {})
            profile["annual_reports"] = comprehensive_data.get("annual_reports", [])
            profile["quarterly_reports"] = comprehensive_data.get("quarterly_reports", [])

            # Parse financials
            facts = comprehensive_data.get("company_facts", {})
            if facts:
                profile["financials"] = SECEdgarDataParser.extract_financial_metrics(
                    comprehensive_data
                )

            # Get M&A activity from 8-K filings
            profile["ma_activity"] = await self.get_ma_transactions(cik)

            # Analyze financial health
            profile["financial_health"] = await self.analyze_financial_health(cik, facts)

            # Get risk factors from recent 10-K
            if profile["annual_reports"]:
                latest_10k = profile["annual_reports"][0]
                profile["risk_factors"] = await self.extract_risk_factors(
                    cik,
                    latest_10k.get("accessionNumber")
                )

        except Exception as e:
            logger.error(f"Error getting company profile for CIK {cik}: {e}")

        return profile

    async def get_ma_transactions(
        self,
        cik: str,
        years_back: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Extract M&A transaction history from 8-K and other filings

        Args:
            cik: Central Index Key
            years_back: Number of years to look back

        Returns:
            List of M&A transactions and material events
        """
        transactions = []

        try:
            # Get 8-K filings (material events including M&A)
            filings_8k = await self.get_recent_filings(cik, "8-K", limit=50)

            # Get S-4 filings (mergers and acquisitions)
            filings_s4 = await self.get_recent_filings(cik, "S-4", limit=20)

            # Process 8-K filings for M&A activity
            for filing in filings_8k:
                filing_date = filing.get("filingDate")
                if not filing_date:
                    continue

                # Check if filing is within date range
                filing_datetime = datetime.fromisoformat(filing_date)
                cutoff_date = datetime.utcnow() - timedelta(days=years_back * 365)

                if filing_datetime < cutoff_date:
                    continue

                # Extract transaction info from filing
                transaction = {
                    "transaction_type": "material_event",
                    "filing_type": "8-K",
                    "filing_date": filing_date,
                    "accession_number": filing.get("accessionNumber"),
                    "description": filing.get("primaryDocDescription", ""),
                    "report_date": filing.get("reportDate")
                }

                transactions.append(transaction)

            # Process S-4 filings (merger/acquisition registrations)
            for filing in filings_s4:
                transaction = {
                    "transaction_type": "merger_acquisition",
                    "filing_type": "S-4",
                    "filing_date": filing.get("filingDate"),
                    "accession_number": filing.get("accessionNumber"),
                    "description": "Merger or Acquisition Registration",
                    "report_date": filing.get("reportDate")
                }

                transactions.append(transaction)

            # Sort by date
            transactions.sort(
                key=lambda x: x.get("filing_date", ""),
                reverse=True
            )

        except Exception as e:
            logger.error(f"Error extracting M&A transactions for CIK {cik}: {e}")

        return transactions

    async def extract_risk_factors(
        self,
        cik: str,
        accession_number: str
    ) -> List[str]:
        """
        Extract risk factors from 10-K filing

        Args:
            cik: Central Index Key
            accession_number: Filing accession number

        Returns:
            List of risk factors
        """
        risk_factors = []

        try:
            # Note: Full text extraction requires downloading and parsing HTML/XML
            # This is a simplified implementation
            # In production, you'd download the filing and extract Item 1A (Risk Factors)

            # For now, return placeholder indicating where risks would be found
            risk_factors.append(
                f"Risk factors available in 10-K filing {accession_number}"
            )

            # In a full implementation:
            # 1. Download filing using accession number
            # 2. Parse HTML/XML to find Item 1A section
            # 3. Extract and clean risk factor text
            # 4. Categorize risks (operational, financial, market, regulatory)

        except Exception as e:
            logger.error(f"Error extracting risk factors: {e}")

        return risk_factors

    async def analyze_financial_health(
        self,
        cik: str,
        facts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze company's financial health based on SEC filings

        Args:
            cik: Central Index Key
            facts: Pre-fetched company facts (optional)

        Returns:
            Financial health score and indicators
        """
        health_analysis = {
            "health_score": 0,  # 0-100
            "health_rating": "unknown",
            "indicators": [],
            "red_flags": [],
            "green_flags": [],
            "financial_ratios": {},
            "trend_analysis": {}
        }

        try:
            # Fetch facts if not provided
            if not facts:
                facts = await self.get_company_facts(cik)

            if not facts:
                return health_analysis

            # Parse financials
            parsed = SECEdgarDataParser.parse_company_facts(facts)
            financials = parsed.get("financials", {})

            # Calculate key ratios
            revenue = financials.get("revenue", {}).get("value")
            net_income = financials.get("net_income", {}).get("value")
            total_assets = financials.get("total_assets", {}).get("value")
            total_liabilities = financials.get("total_liabilities", {}).get("value")
            cash = financials.get("cash", {}).get("value")
            operating_income = financials.get("operating_income", {}).get("value")

            # Profitability analysis
            if revenue and net_income:
                profit_margin = (net_income / revenue) * 100
                health_analysis["financial_ratios"]["profit_margin"] = profit_margin

                if profit_margin > 10:
                    health_analysis["green_flags"].append(f"Strong profit margin: {profit_margin:.1f}%")
                    health_analysis["health_score"] += 15
                elif profit_margin > 5:
                    health_analysis["green_flags"].append(f"Healthy profit margin: {profit_margin:.1f}%")
                    health_analysis["health_score"] += 10
                elif profit_margin < 0:
                    health_analysis["red_flags"].append("Company is unprofitable")
                    health_analysis["health_score"] -= 20
                elif profit_margin < 2:
                    health_analysis["red_flags"].append("Low profit margin")
                    health_analysis["health_score"] -= 10

            # Liquidity analysis
            if total_assets and total_liabilities:
                equity = total_assets - total_liabilities

                if equity > 0:
                    debt_to_equity = total_liabilities / equity
                    health_analysis["financial_ratios"]["debt_to_equity"] = debt_to_equity

                    if debt_to_equity < 0.5:
                        health_analysis["green_flags"].append("Low debt levels")
                        health_analysis["health_score"] += 10
                    elif debt_to_equity > 2.0:
                        health_analysis["red_flags"].append("High debt burden")
                        health_analysis["health_score"] -= 15
                else:
                    health_analysis["red_flags"].append("Negative shareholder equity")
                    health_analysis["health_score"] -= 30

            # Cash position
            if cash and total_assets:
                cash_ratio = (cash / total_assets) * 100
                health_analysis["financial_ratios"]["cash_to_assets"] = cash_ratio

                if cash_ratio > 20:
                    health_analysis["green_flags"].append("Strong cash position")
                    health_analysis["health_score"] += 10
                elif cash_ratio < 5:
                    health_analysis["red_flags"].append("Low cash reserves")
                    health_analysis["health_score"] -= 10

            # Return on assets
            if total_assets and net_income:
                roa = (net_income / total_assets) * 100
                health_analysis["financial_ratios"]["roa"] = roa

                if roa > 10:
                    health_analysis["green_flags"].append("Excellent return on assets")
                    health_analysis["health_score"] += 10
                elif roa < 0:
                    health_analysis["red_flags"].append("Negative return on assets")
                    health_analysis["health_score"] -= 10

            # Growth analysis
            growth_3yr = SECEdgarDataParser.calculate_revenue_growth(facts, years=3)
            if growth_3yr is not None:
                growth_pct = growth_3yr * 100
                health_analysis["trend_analysis"]["revenue_cagr_3yr"] = growth_pct

                if growth_pct > 20:
                    health_analysis["green_flags"].append(f"Strong revenue growth: {growth_pct:.1f}% CAGR")
                    health_analysis["health_score"] += 15
                elif growth_pct > 10:
                    health_analysis["green_flags"].append(f"Healthy revenue growth: {growth_pct:.1f}% CAGR")
                    health_analysis["health_score"] += 10
                elif growth_pct < -5:
                    health_analysis["red_flags"].append(f"Declining revenue: {growth_pct:.1f}% CAGR")
                    health_analysis["health_score"] -= 15

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
            logger.error(f"Error analyzing financial health for CIK {cik}: {e}")

        return health_analysis

    async def _get_company_tickers(self) -> Dict[str, Any]:
        """
        Get company tickers JSON file from SEC

        Returns:
            Dictionary mapping CIK to company info
        """
        await self._rate_limit()

        url = f"{self.API_BASE}/files/company_tickers.json"

        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error fetching company tickers: {e}")
            return {}

    async def search_by_industry(
        self,
        sic_code: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search companies by SIC industry code

        Args:
            sic_code: Standard Industrial Classification code
            limit: Maximum number of results

        Returns:
            List of companies in the specified industry
        """
        companies = []

        try:
            # Get all company tickers
            tickers_data = await self._get_company_tickers()

            # Note: The tickers file doesn't include SIC codes
            # You'd need to fetch submissions for each company to filter by SIC
            # This is a simplified implementation

            logger.info(f"Industry search by SIC requires individual company lookups")

        except Exception as e:
            logger.error(f"Error searching by industry: {e}")

        return companies


# Singleton instance
_enhanced_sec_api: Optional[EnhancedSECEdgarAPI] = None


def get_sec_edgar_api() -> EnhancedSECEdgarAPI:
    """Get or create SEC EDGAR API instance"""
    global _enhanced_sec_api
    if _enhanced_sec_api is None:
        _enhanced_sec_api = EnhancedSECEdgarAPI()
    return _enhanced_sec_api
