"""
Opportunity Discovery Engine
Orchestrates multi-source deal discovery and company screening
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from sqlalchemy.orm import Session

from app.integrations.companies_house_enhanced import get_companies_house_api
from app.integrations.sec_edgar_enhanced import get_sec_edgar_api
from app.integrations.crunchbase import get_crunchbase_api
from app.integrations.news_api import get_news_api
from app.models.deal_discovery import (
    Company,
    DealOpportunity,
    FinancialSnapshot,
    MarketIntelligence,
    IndustryCategory,
    DealStage,
    OpportunitySource,
    FinancialHealth
)

logger = logging.getLogger(__name__)


class OpportunityDiscoveryEngine:
    """
    Multi-source opportunity discovery and screening engine
    Coordinates data gathering from multiple APIs and creates unified opportunities
    """

    def __init__(self):
        """Initialize discovery engine with API clients"""
        self.companies_house = get_companies_house_api()
        self.sec_edgar = get_sec_edgar_api()
        self.crunchbase = get_crunchbase_api()
        self.news = get_news_api()

    async def discover_opportunities(
        self,
        organization_id: str,
        user_id: str,
        db: Session,
        criteria: Dict[str, Any]
    ) -> List[DealOpportunity]:
        """
        Discover M&A opportunities based on search criteria

        Args:
            organization_id: Clerk organization ID (tenant isolation)
            user_id: Clerk user ID of requester
            db: Database session
            criteria: Search criteria dictionary
                - min_revenue_millions: float
                - max_revenue_millions: float
                - industries: List[str]
                - regions: List[str]
                - sources: List[str] (companies_house, sec_edgar, crunchbase)
                - min_growth_rate: Optional[float]
                - profitability_required: bool

        Returns:
            List of created DealOpportunity records
        """
        opportunities = []

        try:
            # Extract criteria
            min_revenue = criteria.get("min_revenue_millions", 1.0)
            max_revenue = criteria.get("max_revenue_millions", 50.0)
            industries = criteria.get("industries", [])
            regions = criteria.get("regions", [])
            sources = criteria.get("sources", ["companies_house", "sec_edgar", "crunchbase"])
            min_growth = criteria.get("min_growth_rate")
            profitability = criteria.get("profitability_required", False)
            max_results_per_source = criteria.get("max_results_per_source", 50)

            logger.info(f"Starting discovery for organization {organization_id} with criteria: {criteria}")

            # Discover from multiple sources in parallel
            discovery_tasks = []

            if "companies_house" in sources:
                discovery_tasks.append(
                    self._discover_from_companies_house(
                        min_revenue, max_revenue, industries, regions, max_results_per_source
                    )
                )

            if "sec_edgar" in sources:
                discovery_tasks.append(
                    self._discover_from_sec_edgar(
                        min_revenue, max_revenue, industries, min_growth, profitability, max_results_per_source
                    )
                )

            if "crunchbase" in sources:
                discovery_tasks.append(
                    self._discover_from_crunchbase(
                        industries, min_revenue, max_revenue, max_results_per_source
                    )
                )

            # Execute all discoveries in parallel
            results = await asyncio.gather(*discovery_tasks, return_exceptions=True)

            # Process results from each source
            for idx, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Discovery task {idx} failed: {result}")
                    continue

                companies_data = result
                logger.info(f"Source {idx} returned {len(companies_data)} companies")

                # Create Company and DealOpportunity records
                for company_data in companies_data:
                    try:
                        opportunity = await self._create_opportunity_from_data(
                            organization_id,
                            user_id,
                            company_data,
                            db
                        )

                        if opportunity:
                            opportunities.append(opportunity)

                    except Exception as e:
                        logger.error(f"Error creating opportunity: {e}")
                        continue

            # Commit all opportunities
            db.commit()

            logger.info(f"Discovery complete: {len(opportunities)} opportunities created")

        except Exception as e:
            logger.error(f"Error in opportunity discovery: {e}")
            db.rollback()

        return opportunities

    async def _discover_from_companies_house(
        self,
        min_revenue: float,
        max_revenue: float,
        industries: List[str],
        regions: List[str],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Discover opportunities from Companies House UK"""
        try:
            logger.info("Discovering from Companies House...")

            opportunities = await self.companies_house.discover_opportunities(
                min_revenue_millions=min_revenue,
                max_revenue_millions=max_revenue,
                industries=industries,
                regions=regions,
                max_results=max_results
            )

            # Enrich with full profiles
            enriched = []
            for opp in opportunities[:20]:  # Limit enrichment to top 20
                company_number = opp.get("company_number")
                if company_number:
                    profile = await self.companies_house.get_company_full_profile(company_number)
                    health = await self.companies_house.analyze_financial_health(company_number)

                    enriched.append({
                        "source": OpportunitySource.COMPANIES_HOUSE,
                        "external_id": company_number,
                        "data": profile,
                        "health_analysis": health
                    })

                    # Rate limiting
                    await asyncio.sleep(0.15)

            return enriched

        except Exception as e:
            logger.error(f"Error discovering from Companies House: {e}")
            return []

    async def _discover_from_sec_edgar(
        self,
        min_revenue: float,
        max_revenue: float,
        industries: List[str],
        min_growth: Optional[float],
        profitability: bool,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Discover opportunities from SEC EDGAR US"""
        try:
            logger.info("Discovering from SEC EDGAR...")

            opportunities = await self.sec_edgar.discover_opportunities(
                min_revenue_millions=min_revenue,
                max_revenue_millions=max_revenue,
                industries=industries,
                min_growth_rate=min_growth,
                profitability_required=profitability,
                max_results=max_results
            )

            # Enrich with full profiles
            enriched = []
            for opp in opportunities[:20]:  # Limit enrichment
                cik = opp.get("cik")
                if cik:
                    profile = await self.sec_edgar.get_company_full_profile(cik)

                    enriched.append({
                        "source": OpportunitySource.SEC_EDGAR,
                        "external_id": cik,
                        "data": profile,
                        "health_analysis": profile.get("financial_health", {})
                    })

                    # Rate limiting
                    await asyncio.sleep(0.15)

            return enriched

        except Exception as e:
            logger.error(f"Error discovering from SEC EDGAR: {e}")
            return []

    async def _discover_from_crunchbase(
        self,
        industries: List[str],
        min_revenue: float,
        max_revenue: float,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Discover opportunities from Crunchbase"""
        try:
            logger.info("Discovering from Crunchbase...")

            # Convert revenue to funding range (approximation)
            min_funding = int(min_revenue * 1_000_000 * 0.5)  # Assume funding is ~50% of revenue
            max_funding = int(max_revenue * 1_000_000 * 2)    # Upper bound

            opportunities = await self.crunchbase.discover_acquisition_targets(
                categories=industries,
                min_funding=min_funding,
                max_funding=max_funding,
                limit=max_results
            )

            # Format for consistency
            enriched = []
            for opp in opportunities:
                enriched.append({
                    "source": OpportunitySource.CRUNCHBASE,
                    "external_id": opp.get("uuid"),
                    "data": opp,
                    "health_analysis": None  # Crunchbase doesn't provide financial health
                })

            return enriched

        except Exception as e:
            logger.error(f"Error discovering from Crunchbase: {e}")
            return []

    async def _create_opportunity_from_data(
        self,
        organization_id: str,
        user_id: str,
        company_data: Dict[str, Any],
        db: Session
    ) -> Optional[DealOpportunity]:
        """
        Create Company and DealOpportunity records from discovered data

        Args:
            organization_id: Clerk organization ID
            user_id: Clerk user ID
            company_data: Discovered company data
            db: Database session

        Returns:
            Created DealOpportunity or None
        """
        try:
            source = company_data.get("source")
            external_id = company_data.get("external_id")
            data = company_data.get("data", {})
            health_analysis = company_data.get("health_analysis", {})

            # Check if company already exists
            existing_company = db.query(Company).filter(
                Company.organization_id == organization_id,
                Company.external_id == external_id,
                Company.data_source == source
            ).first()

            if existing_company:
                logger.debug(f"Company {external_id} already exists, skipping")
                return None

            # Extract company details based on source
            company_name = self._extract_company_name(source, data)
            description = self._extract_description(source, data)
            website = self._extract_website(source, data)
            industry = self._extract_industry(source, data)
            location = self._extract_location(source, data)
            financials = self._extract_financials(source, data)

            # Create Company record
            company = Company(
                organization_id=organization_id,
                name=company_name,
                legal_name=data.get("legal_name") or company_name,
                description=description,
                website=website,
                industry_category=industry,
                location_city=location.get("city"),
                location_region=location.get("region"),
                location_country=location.get("country"),
                data_source=source,
                external_id=external_id,
                raw_data=data
            )

            db.add(company)
            db.flush()  # Get company.id

            # Create FinancialSnapshot if financials available
            if financials:
                snapshot = FinancialSnapshot(
                    company_id=company.id,
                    period_year=financials.get("fiscal_year") or datetime.utcnow().year,
                    revenue=financials.get("revenue"),
                    ebitda=financials.get("ebitda"),
                    net_income=financials.get("net_income"),
                    total_assets=financials.get("total_assets"),
                    total_liabilities=financials.get("total_liabilities"),
                    cash_and_equivalents=financials.get("cash"),
                    profit_margin=financials.get("profit_margin"),
                    debt_to_equity_ratio=financials.get("debt_to_equity")
                )
                db.add(snapshot)

            # Determine initial opportunity score (0-100)
            initial_score = self._calculate_initial_score(health_analysis, financials)

            # Map health rating to enum
            health_rating_str = health_analysis.get("health_rating", "unknown")
            health_rating = self._map_health_rating(health_rating_str)

            # Create DealOpportunity
            opportunity = DealOpportunity(
                organization_id=organization_id,
                company_id=company.id,
                discovered_by=user_id,
                opportunity_name=f"M&A Opportunity: {company_name}",
                opportunity_score=initial_score,
                stage=DealStage.DISCOVERY,
                source=source,
                financial_health=health_rating,
                estimated_valuation=financials.get("revenue", 0) * 3 if financials else None,  # Simple 3x revenue multiple
                notes=f"Discovered via {source.value}"
            )

            db.add(opportunity)

            logger.info(f"Created opportunity for {company_name} (score: {initial_score})")

            return opportunity

        except Exception as e:
            logger.error(f"Error creating opportunity from data: {e}")
            return None

    def _extract_company_name(self, source: OpportunitySource, data: Dict[str, Any]) -> str:
        """Extract company name from source-specific data"""
        if source == OpportunitySource.COMPANIES_HOUSE:
            return data.get("company_details", {}).get("company_name", "Unknown")
        elif source == OpportunitySource.SEC_EDGAR:
            return data.get("company_info", {}).get("name", "Unknown")
        elif source == OpportunitySource.CRUNCHBASE:
            return data.get("name", "Unknown")
        return "Unknown"

    def _extract_description(self, source: OpportunitySource, data: Dict[str, Any]) -> Optional[str]:
        """Extract company description"""
        if source == OpportunitySource.CRUNCHBASE:
            return data.get("description")
        elif source == OpportunitySource.SEC_EDGAR:
            return data.get("company_info", {}).get("businessAddress")
        return None

    def _extract_website(self, source: OpportunitySource, data: Dict[str, Any]) -> Optional[str]:
        """Extract company website"""
        if source == OpportunitySource.CRUNCHBASE:
            return data.get("website")
        return None

    def _extract_industry(self, source: OpportunitySource, data: Dict[str, Any]) -> IndustryCategory:
        """Extract and map industry category"""
        if source == OpportunitySource.CRUNCHBASE:
            categories = data.get("categories", [])
            if categories:
                # Simple mapping - would be more sophisticated in production
                first_cat = categories[0].lower() if categories else ""
                if "tech" in first_cat or "software" in first_cat:
                    return IndustryCategory.TECHNOLOGY
                elif "health" in first_cat:
                    return IndustryCategory.HEALTHCARE

        return IndustryCategory.OTHER

    def _extract_location(self, source: OpportunitySource, data: Dict[str, Any]) -> Dict[str, str]:
        """Extract location information"""
        location = {"city": None, "region": None, "country": None}

        if source == OpportunitySource.COMPANIES_HOUSE:
            address = data.get("company_details", {}).get("registered_office_address", {})
            location["city"] = address.get("locality")
            location["region"] = address.get("region")
            location["country"] = address.get("country")

        elif source == OpportunitySource.SEC_EDGAR:
            address = data.get("company_info", {}).get("addresses", {}).get("business", {})
            location["city"] = address.get("city")
            location["region"] = address.get("stateOrCountry")
            location["country"] = "United States"

        elif source == OpportunitySource.CRUNCHBASE:
            loc_data = data.get("location", {})
            location["city"] = loc_data.get("city")
            location["country"] = loc_data.get("country")

        return location

    def _extract_financials(self, source: OpportunitySource, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract financial metrics"""
        if source == OpportunitySource.SEC_EDGAR:
            return data.get("financials", {})

        elif source == OpportunitySource.COMPANIES_HOUSE:
            return data.get("financials", {})

        return None

    def _calculate_initial_score(
        self,
        health_analysis: Optional[Dict[str, Any]],
        financials: Optional[Dict[str, Any]]
    ) -> int:
        """Calculate initial opportunity score (0-100)"""
        if health_analysis and "health_score" in health_analysis:
            return int(health_analysis["health_score"])

        # Fallback scoring based on financials
        if financials:
            score = 50  # Base score

            # Positive revenue
            if financials.get("revenue", 0) > 0:
                score += 10

            # Profitability
            if financials.get("net_income", 0) > 0:
                score += 15

            # Good profit margin
            profit_margin = financials.get("profit_margin", 0)
            if profit_margin > 0.1:
                score += 10

            # Low debt
            debt_to_equity = financials.get("debt_to_equity", 999)
            if debt_to_equity < 1.0:
                score += 15

            return min(100, score)

        return 50  # Default neutral score

    def _map_health_rating(self, rating_str: str) -> FinancialHealth:
        """Map health rating string to enum"""
        mapping = {
            "excellent": FinancialHealth.EXCELLENT,
            "good": FinancialHealth.GOOD,
            "fair": FinancialHealth.FAIR,
            "poor": FinancialHealth.POOR,
            "distressed": FinancialHealth.DISTRESSED,
            "unknown": FinancialHealth.UNKNOWN
        }
        return mapping.get(rating_str.lower(), FinancialHealth.UNKNOWN)

    async def enrich_opportunity(
        self,
        opportunity_id: str,
        db: Session
    ) -> DealOpportunity:
        """
        Enrich existing opportunity with additional data

        Args:
            opportunity_id: Opportunity UUID
            db: Database session

        Returns:
            Updated opportunity
        """
        opportunity = db.query(DealOpportunity).filter(
            DealOpportunity.id == opportunity_id
        ).first()

        if not opportunity:
            raise ValueError(f"Opportunity {opportunity_id} not found")

        company = opportunity.company

        try:
            # Fetch news intelligence
            news_data = await self.news.monitor_company(company.name)

            # Create MarketIntelligence record
            if news_data.get("recent_articles_count", 0) > 0:
                intel = MarketIntelligence(
                    company_id=company.id,
                    intelligence_type="news_monitoring",
                    source="news_api",
                    content=news_data,
                    relevance_score=0.8 if news_data.get("alerts") else 0.5
                )
                db.add(intel)

            # Update opportunity score based on news signals
            if news_data.get("signals_detected", {}).get("ma_activity"):
                opportunity.opportunity_score = min(100, opportunity.opportunity_score + 10)

            if news_data.get("signals_detected", {}).get("distress"):
                opportunity.opportunity_score = max(0, opportunity.opportunity_score - 15)

            db.commit()

        except Exception as e:
            logger.error(f"Error enriching opportunity {opportunity_id}: {e}")
            db.rollback()

        return opportunity


# Singleton instance
_discovery_engine: Optional[OpportunityDiscoveryEngine] = None


def get_discovery_engine() -> OpportunityDiscoveryEngine:
    """Get or create discovery engine instance"""
    global _discovery_engine
    if _discovery_engine is None:
        _discovery_engine = OpportunityDiscoveryEngine()
    return _discovery_engine
