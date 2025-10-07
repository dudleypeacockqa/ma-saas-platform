"""
Deal Sourcing Service
Handles opportunity discovery, scoring, and pipeline management
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import anthropic
import os
import logging

from ..models.opportunities import (
    MarketOpportunity, CompanyProfile, OpportunityScore,
    OpportunityActivity, OpportunitySource, OpportunityStatus,
    CompanyRegion, IndustryVertical, SourceType, ActivityType
)
from ..integrations.companies_house import CompaniesHouseAPI
from ..integrations.sec_edgar import SECEdgarAPI

logger = logging.getLogger(__name__)


class OpportunityDiscoveryService:
    """Service for discovering M&A opportunities from multiple sources"""

    def __init__(self, db: Session):
        self.db = db
        self.companies_house = CompaniesHouseAPI()
        self.sec_edgar = SECEdgarAPI()

    async def scan_companies_house(
        self,
        organization_id: str,
        filters: Dict[str, Any]
    ) -> List[MarketOpportunity]:
        """
        Scan Companies House for UK opportunities

        Args:
            organization_id: Organization ID for multi-tenancy
            filters: Dict with industry_sic, min_age_years, max_employees, etc.

        Returns:
            List of created MarketOpportunity records
        """
        opportunities = []

        try:
            # Identify distressed companies
            industry_sic = filters.get("industry_sic", "62")  # IT services default
            min_age = filters.get("min_age_years", 3)

            distressed = await self.companies_house.identify_distressed_companies(
                industry_sic=industry_sic,
                min_age_years=min_age
            )

            for company_data in distressed[:50]:  # Limit batch size
                # Check if already exists
                existing = self.db.query(MarketOpportunity).filter(
                    and_(
                        MarketOpportunity.organization_id == organization_id,
                        MarketOpportunity.company_registration_number == company_data.get("company_number")
                    )
                ).first()

                if existing:
                    continue

                # Create opportunity
                opportunity = MarketOpportunity(
                    organization_id=organization_id,
                    company_name=company_data.get("company_name"),
                    region=CompanyRegion.UK,
                    industry_vertical=self._map_sic_to_vertical(industry_sic),
                    company_registration_number=company_data.get("company_number"),
                    status=OpportunityStatus.NEW,
                    source_url=f"https://find-and-update.company-information.service.gov.uk/company/{company_data.get('company_number')}",
                    metadata={
                        "source": "companies_house_scan",
                        "scan_date": datetime.utcnow().isoformat(),
                        "distressed_indicators": company_data.get("indicators", [])
                    }
                )

                self.db.add(opportunity)

                # Create source tracking
                source = OpportunitySource(
                    opportunity_id=opportunity.id,
                    source_type=SourceType.API_INTEGRATION,
                    source_name="Companies House",
                    source_url=opportunity.source_url,
                    discovered_at=datetime.utcnow()
                )
                self.db.add(source)

                opportunities.append(opportunity)

            self.db.commit()
            logger.info(f"Discovered {len(opportunities)} new UK opportunities")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error scanning Companies House: {str(e)}")
            raise

        return opportunities

    async def scan_sec_edgar(
        self,
        organization_id: str,
        filters: Dict[str, Any]
    ) -> List[MarketOpportunity]:
        """
        Scan SEC EDGAR for US opportunities

        Args:
            organization_id: Organization ID
            filters: Dict with industry_sic, market_cap_max, filing_age_days, etc.

        Returns:
            List of created MarketOpportunity records
        """
        opportunities = []

        try:
            # Search recent 10-K filings
            cik_list = filters.get("cik_list", [])

            for cik in cik_list[:20]:  # Limit batch size
                try:
                    # Get company facts
                    facts = await self.sec_edgar.get_company_facts(cik)

                    # Extract financials
                    financials = self._extract_sec_financials(facts)

                    if not financials.get("revenue"):
                        continue

                    # Check if already exists
                    existing = self.db.query(MarketOpportunity).filter(
                        and_(
                            MarketOpportunity.organization_id == organization_id,
                            MarketOpportunity.company_registration_number == cik
                        )
                    ).first()

                    if existing:
                        continue

                    # Create opportunity
                    opportunity = MarketOpportunity(
                        organization_id=organization_id,
                        company_name=facts.get("entityName", "Unknown"),
                        region=CompanyRegion.US,
                        industry_vertical=self._map_sic_to_vertical(facts.get("sic", "")),
                        company_registration_number=cik,
                        annual_revenue=Decimal(str(financials.get("revenue", 0))),
                        ebitda=Decimal(str(financials.get("ebitda", 0))),
                        employee_count=financials.get("employees"),
                        status=OpportunityStatus.NEW,
                        source_url=f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}",
                        metadata={
                            "source": "sec_edgar_scan",
                            "scan_date": datetime.utcnow().isoformat(),
                            "fiscal_year": financials.get("fiscal_year")
                        }
                    )

                    self.db.add(opportunity)

                    # Create source tracking
                    source = OpportunitySource(
                        opportunity_id=opportunity.id,
                        source_type=SourceType.API_INTEGRATION,
                        source_name="SEC EDGAR",
                        source_url=opportunity.source_url,
                        discovered_at=datetime.utcnow()
                    )
                    self.db.add(source)

                    opportunities.append(opportunity)

                except Exception as e:
                    logger.warning(f"Error processing CIK {cik}: {str(e)}")
                    continue

            self.db.commit()
            logger.info(f"Discovered {len(opportunities)} new US opportunities")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error scanning SEC EDGAR: {str(e)}")
            raise

        return opportunities

    async def monitor_news_for_opportunities(
        self,
        organization_id: str,
        keywords: List[str]
    ) -> List[MarketOpportunity]:
        """
        Monitor market news for M&A signals

        Args:
            organization_id: Organization ID
            keywords: List of keywords to monitor (e.g., "retirement", "succession")

        Returns:
            List of opportunities identified from news
        """
        # Placeholder for news monitoring integration
        # Would integrate with news APIs like NewsAPI, Bloomberg, etc.
        logger.info(f"News monitoring with keywords: {keywords}")
        return []

    async def identify_distressed_companies(
        self,
        organization_id: str,
        industry: str,
        region: CompanyRegion
    ) -> List[MarketOpportunity]:
        """
        Identify companies showing distress signals

        Args:
            organization_id: Organization ID
            industry: Industry vertical
            region: Geographic region

        Returns:
            List of distressed opportunities
        """
        if region == CompanyRegion.UK:
            filters = {
                "industry_sic": self._vertical_to_sic(industry),
                "min_age_years": 2
            }
            return await self.scan_companies_house(organization_id, filters)
        elif region == CompanyRegion.US:
            # Would implement distress scoring from SEC filings
            logger.info(f"Distress identification for US companies in {industry}")
            return []

        return []

    async def detect_succession_opportunities(
        self,
        organization_id: str,
        criteria: Dict[str, Any]
    ) -> List[MarketOpportunity]:
        """
        Detect companies with succession/retirement signals

        Args:
            organization_id: Organization ID
            criteria: Detection criteria (min_company_age, owner_age_threshold, etc.)

        Returns:
            List of succession opportunities
        """
        # Would integrate with leadership databases, company announcements
        logger.info(f"Succession detection with criteria: {criteria}")
        return []

    def _map_sic_to_vertical(self, sic_code: str) -> IndustryVertical:
        """Map SIC code to industry vertical"""
        sic_str = str(sic_code)

        if sic_str.startswith("62") or sic_str.startswith("63"):
            return IndustryVertical.TECHNOLOGY
        elif sic_str.startswith("45") or sic_str.startswith("46"):
            return IndustryVertical.MANUFACTURING
        elif sic_str.startswith("86"):
            return IndustryVertical.HEALTHCARE
        elif sic_str.startswith("52") or sic_str.startswith("53"):
            return IndustryVertical.RETAIL
        elif sic_str.startswith("70"):
            return IndustryVertical.PROFESSIONAL_SERVICES
        else:
            return IndustryVertical.OTHER

    def _vertical_to_sic(self, vertical: str) -> str:
        """Map industry vertical to SIC code"""
        mapping = {
            "technology": "62",
            "manufacturing": "45",
            "healthcare": "86",
            "retail": "52",
            "professional_services": "70"
        }
        return mapping.get(vertical.lower(), "62")

    def _extract_sec_financials(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key financial metrics from SEC company facts"""
        financials = {}

        try:
            # Navigate SEC EDGAR data structure
            facts_data = facts.get("facts", {})
            us_gaap = facts_data.get("us-gaap", {})

            # Revenue
            revenues = us_gaap.get("Revenues", {}).get("units", {}).get("USD", [])
            if revenues:
                latest = max(revenues, key=lambda x: x.get("end", ""))
                financials["revenue"] = latest.get("val", 0)
                financials["fiscal_year"] = latest.get("fy")

            # Net Income
            net_income = us_gaap.get("NetIncomeLoss", {}).get("units", {}).get("USD", [])
            if net_income:
                latest = max(net_income, key=lambda x: x.get("end", ""))
                financials["net_income"] = latest.get("val", 0)

            # Estimate EBITDA (simplified)
            if financials.get("net_income"):
                financials["ebitda"] = financials["net_income"] * 1.5  # Rough estimate

            # Employees
            employees = us_gaap.get("EntityCommonStockSharesOutstanding", {})
            if employees:
                financials["employees"] = None  # Would need different data source

        except Exception as e:
            logger.warning(f"Error extracting SEC financials: {str(e)}")

        return financials


class OpportunityScoringService:
    """Service for AI-based opportunity scoring and analysis"""

    def __init__(self, db: Session):
        self.db = db
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"

    async def calculate_opportunity_score(
        self,
        opportunity_id: str,
        company_data: Dict[str, Any]
    ) -> OpportunityScore:
        """
        Calculate comprehensive opportunity score using AI

        Args:
            opportunity_id: Opportunity ID
            company_data: Company financial and operational data

        Returns:
            OpportunityScore record
        """
        # Calculate individual components
        financial_score = await self.assess_financial_health(company_data)
        growth_score = await self.evaluate_growth_trajectory(company_data)
        strategic_score = await self.calculate_strategic_fit(company_data)
        market_score = self._calculate_market_position(company_data)
        risk_score = self._assess_risk_factors(company_data)

        # Calculate overall weighted score
        overall_score = (
            financial_score * 0.30 +
            growth_score * 0.25 +
            strategic_score * 0.25 +
            market_score * 0.10 +
            (100 - risk_score) * 0.10  # Lower risk = higher score
        )

        # Generate AI insights
        ai_insights = await self._generate_ai_insights(company_data, overall_score)

        # Create score record
        score = OpportunityScore(
            opportunity_id=opportunity_id,
            overall_score=round(overall_score, 2),
            financial_health_score=round(financial_score, 2),
            growth_trajectory_score=round(growth_score, 2),
            strategic_fit_score=round(strategic_score, 2),
            market_position_score=round(market_score, 2),
            risk_assessment_score=round(risk_score, 2),
            scoring_criteria={
                "methodology": "ai_weighted_composite",
                "weights": {
                    "financial": 0.30,
                    "growth": 0.25,
                    "strategic": 0.25,
                    "market": 0.10,
                    "risk": 0.10
                }
            },
            ai_insights=ai_insights,
            confidence_level=self._calculate_confidence(company_data),
            scored_at=datetime.utcnow()
        )

        self.db.add(score)

        # Update opportunity with overall score
        opportunity = self.db.query(MarketOpportunity).filter(
            MarketOpportunity.id == opportunity_id
        ).first()

        if opportunity:
            opportunity.overall_score = overall_score
            opportunity.financial_health_score = financial_score
            opportunity.strategic_fit_score = strategic_score

        self.db.commit()

        return score

    async def assess_financial_health(self, financials: Dict[str, Any]) -> float:
        """
        Assess financial health (0-100 score)

        Args:
            financials: Dict with revenue, ebitda, debt, cash_flow, etc.

        Returns:
            Financial health score 0-100
        """
        score = 50.0  # Start neutral

        # Revenue check
        revenue = float(financials.get("revenue", 0))
        if revenue > 0:
            if revenue >= 50_000_000:
                score += 15
            elif revenue >= 10_000_000:
                score += 10
            elif revenue >= 1_000_000:
                score += 5

        # EBITDA margin
        ebitda = float(financials.get("ebitda", 0))
        if revenue > 0 and ebitda > 0:
            margin = (ebitda / revenue) * 100
            if margin >= 20:
                score += 15
            elif margin >= 10:
                score += 10
            elif margin >= 5:
                score += 5
            elif margin < 0:
                score -= 15

        # Debt-to-equity ratio
        debt = float(financials.get("total_debt", 0))
        equity = float(financials.get("shareholders_equity", 0))
        if equity > 0:
            debt_ratio = debt / equity
            if debt_ratio < 0.5:
                score += 10
            elif debt_ratio < 1.0:
                score += 5
            elif debt_ratio > 2.0:
                score -= 10

        # Cash flow
        cash_flow = float(financials.get("operating_cash_flow", 0))
        if cash_flow > 0:
            score += 10
        elif cash_flow < 0:
            score -= 10

        return max(0.0, min(100.0, score))

    async def evaluate_growth_trajectory(self, historical_data: Dict[str, Any]) -> float:
        """
        Evaluate growth trajectory (0-100 score)

        Args:
            historical_data: Historical revenue, profit, and market data

        Returns:
            Growth score 0-100
        """
        score = 50.0

        # Revenue growth rate
        revenue_growth = float(historical_data.get("revenue_growth_rate", 0))
        if revenue_growth >= 30:
            score += 20
        elif revenue_growth >= 15:
            score += 15
        elif revenue_growth >= 5:
            score += 10
        elif revenue_growth < 0:
            score -= 15

        # Profit growth
        profit_growth = float(historical_data.get("profit_growth_rate", 0))
        if profit_growth >= 20:
            score += 15
        elif profit_growth >= 10:
            score += 10
        elif profit_growth < 0:
            score -= 10

        # Market share trend
        market_trend = historical_data.get("market_share_trend", "stable")
        if market_trend == "increasing":
            score += 15
        elif market_trend == "decreasing":
            score -= 15

        return max(0.0, min(100.0, score))

    async def calculate_strategic_fit(self, criteria: Dict[str, Any]) -> float:
        """
        Calculate strategic fit based on buyer criteria (0-100 score)

        Args:
            criteria: Strategic criteria (industry match, geography, synergies)

        Returns:
            Strategic fit score 0-100
        """
        score = 50.0

        # Industry alignment
        if criteria.get("industry_match", False):
            score += 20

        # Geographic fit
        if criteria.get("geography_match", False):
            score += 15

        # Synergy potential
        synergies = criteria.get("synergy_potential", "medium")
        if synergies == "high":
            score += 15
        elif synergies == "medium":
            score += 7

        return max(0.0, min(100.0, score))

    async def estimate_roi_projection(
        self,
        assumptions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Estimate ROI projection

        Args:
            assumptions: Deal assumptions (purchase_price, growth_rate, exit_multiple)

        Returns:
            Dict with roi_percentage, irr, payback_period, etc.
        """
        purchase_price = float(assumptions.get("purchase_price", 0))
        annual_revenue = float(assumptions.get("annual_revenue", 0))
        ebitda = float(assumptions.get("ebitda", 0))
        growth_rate = float(assumptions.get("growth_rate", 0.05))
        exit_multiple = float(assumptions.get("exit_multiple", 5.0))
        hold_period = int(assumptions.get("hold_period_years", 5))

        # Simple ROI calculation
        future_ebitda = ebitda * ((1 + growth_rate) ** hold_period)
        exit_value = future_ebitda * exit_multiple

        roi_percentage = ((exit_value - purchase_price) / purchase_price) * 100 if purchase_price > 0 else 0

        # Approximate IRR (simplified)
        irr = ((exit_value / purchase_price) ** (1/hold_period) - 1) * 100 if purchase_price > 0 and hold_period > 0 else 0

        # Payback period (simplified)
        annual_cash_flow = ebitda * 0.7  # Assume 70% converts to cash
        payback_period = purchase_price / annual_cash_flow if annual_cash_flow > 0 else 0

        return {
            "roi_percentage": round(roi_percentage, 2),
            "irr": round(irr, 2),
            "payback_period_years": round(payback_period, 2),
            "exit_value": round(exit_value, 2),
            "assumptions": assumptions
        }

    def _calculate_market_position(self, company_data: Dict[str, Any]) -> float:
        """Calculate market position score"""
        score = 50.0

        market_share = float(company_data.get("market_share_percentage", 0))
        if market_share >= 20:
            score += 20
        elif market_share >= 10:
            score += 15
        elif market_share >= 5:
            score += 10

        return max(0.0, min(100.0, score))

    def _assess_risk_factors(self, company_data: Dict[str, Any]) -> float:
        """Assess risk factors (higher = more risk)"""
        risk_score = 0.0

        # Customer concentration
        if company_data.get("customer_concentration", 0) > 50:
            risk_score += 20

        # Regulatory risk
        if company_data.get("high_regulatory_risk", False):
            risk_score += 15

        # Technology obsolescence
        if company_data.get("technology_age_years", 0) > 10:
            risk_score += 15

        # Management depth
        if not company_data.get("strong_management_team", False):
            risk_score += 10

        return min(100.0, risk_score)

    async def _generate_ai_insights(
        self,
        company_data: Dict[str, Any],
        overall_score: float
    ) -> Dict[str, Any]:
        """Generate AI-powered insights using Claude"""

        prompt = f"""Analyze this M&A opportunity and provide strategic insights:

Company Data:
- Revenue: ${company_data.get('revenue', 0):,.0f}
- EBITDA: ${company_data.get('ebitda', 0):,.0f}
- Industry: {company_data.get('industry', 'Unknown')}
- Region: {company_data.get('region', 'Unknown')}
- Employees: {company_data.get('employee_count', 'Unknown')}
- Overall Score: {overall_score:.1f}/100

Provide a JSON response with:
1. "key_strengths": [list of 3-5 key strengths]
2. "key_risks": [list of 3-5 key risks]
3. "strategic_rationale": string explaining why this is/isn't a good opportunity
4. "recommended_next_steps": [list of 3-5 recommended actions]
5. "valuation_range": {{"min": number, "max": number}} in millions

Be concise and focus on actionable insights."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text

            # Parse JSON from response
            import json
            import re

            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                insights = json.loads(json_match.group())
                return insights

        except Exception as e:
            logger.warning(f"Error generating AI insights: {str(e)}")

        # Fallback
        return {
            "key_strengths": ["Stable revenue base"],
            "key_risks": ["Limited data available"],
            "strategic_rationale": "Further analysis required",
            "recommended_next_steps": ["Conduct deeper due diligence"],
            "valuation_range": {"min": 0, "max": 0}
        }

    def _calculate_confidence(self, company_data: Dict[str, Any]) -> float:
        """Calculate confidence level based on data completeness"""
        required_fields = ["revenue", "ebitda", "industry", "region"]
        available = sum(1 for field in required_fields if company_data.get(field))
        return (available / len(required_fields)) * 100


class OpportunityManagementService:
    """Service for managing opportunities through the pipeline"""

    def __init__(self, db: Session):
        self.db = db
        self.scoring_service = OpportunityScoringService(db)

    def create_opportunity(
        self,
        organization_id: str,
        company_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> MarketOpportunity:
        """
        Create new opportunity record

        Args:
            organization_id: Organization ID
            company_data: Company information
            user_id: User creating the opportunity

        Returns:
            Created MarketOpportunity
        """
        opportunity = MarketOpportunity(
            organization_id=organization_id,
            company_name=company_data["company_name"],
            region=company_data.get("region", CompanyRegion.UK),
            industry_vertical=company_data.get("industry_vertical", IndustryVertical.OTHER),
            company_registration_number=company_data.get("registration_number"),
            website=company_data.get("website"),
            annual_revenue=company_data.get("annual_revenue"),
            ebitda=company_data.get("ebitda"),
            employee_count=company_data.get("employee_count"),
            status=OpportunityStatus.NEW,
            source_url=company_data.get("source_url"),
            metadata=company_data.get("metadata", {})
        )

        self.db.add(opportunity)
        self.db.commit()
        self.db.refresh(opportunity)

        # Track activity
        if user_id:
            self.track_activity(
                opportunity_id=opportunity.id,
                user_id=user_id,
                activity_type=ActivityType.STATUS_CHANGE,
                description="Opportunity created"
            )

        return opportunity

    def update_opportunity_status(
        self,
        opportunity_id: str,
        status: OpportunityStatus,
        user_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> MarketOpportunity:
        """
        Update opportunity status in pipeline

        Args:
            opportunity_id: Opportunity ID
            status: New status
            user_id: User making the change
            notes: Optional notes about status change

        Returns:
            Updated MarketOpportunity
        """
        opportunity = self.db.query(MarketOpportunity).filter(
            MarketOpportunity.id == opportunity_id
        ).first()

        if not opportunity:
            raise ValueError(f"Opportunity {opportunity_id} not found")

        old_status = opportunity.status
        opportunity.status = status

        # Update status-specific fields
        if status == OpportunityStatus.QUALIFIED:
            opportunity.qualified_at = datetime.utcnow()
        elif status == OpportunityStatus.CONTACTED:
            opportunity.first_contact_date = datetime.utcnow()
        elif status == OpportunityStatus.CONVERTED_TO_DEAL:
            opportunity.converted_to_deal_at = datetime.utcnow()

        self.db.commit()

        # Track activity
        if user_id:
            self.track_activity(
                opportunity_id=opportunity_id,
                user_id=user_id,
                activity_type=ActivityType.STATUS_CHANGE,
                description=f"Status changed from {old_status.value} to {status.value}",
                metadata={"notes": notes} if notes else None
            )

        return opportunity

    def filter_opportunities(
        self,
        organization_id: str,
        filters: Dict[str, Any]
    ) -> List[MarketOpportunity]:
        """
        Advanced filtering and search

        Args:
            organization_id: Organization ID
            filters: Dict with status, region, industry, min_score, max_score, etc.

        Returns:
            Filtered list of opportunities
        """
        query = self.db.query(MarketOpportunity).filter(
            MarketOpportunity.organization_id == organization_id
        )

        # Status filter
        if "status" in filters:
            if isinstance(filters["status"], list):
                query = query.filter(MarketOpportunity.status.in_(filters["status"]))
            else:
                query = query.filter(MarketOpportunity.status == filters["status"])

        # Region filter
        if "region" in filters:
            query = query.filter(MarketOpportunity.region == filters["region"])

        # Industry filter
        if "industry_vertical" in filters:
            if isinstance(filters["industry_vertical"], list):
                query = query.filter(MarketOpportunity.industry_vertical.in_(filters["industry_vertical"]))
            else:
                query = query.filter(MarketOpportunity.industry_vertical == filters["industry_vertical"])

        # Score range
        if "min_score" in filters:
            query = query.filter(MarketOpportunity.overall_score >= filters["min_score"])
        if "max_score" in filters:
            query = query.filter(MarketOpportunity.overall_score <= filters["max_score"])

        # Revenue range
        if "min_revenue" in filters:
            query = query.filter(MarketOpportunity.annual_revenue >= filters["min_revenue"])
        if "max_revenue" in filters:
            query = query.filter(MarketOpportunity.annual_revenue <= filters["max_revenue"])

        # Search by company name
        if "search" in filters:
            search_term = f"%{filters['search']}%"
            query = query.filter(MarketOpportunity.company_name.ilike(search_term))

        # Sorting
        sort_by = filters.get("sort_by", "created_at")
        sort_order = filters.get("sort_order", "desc")

        if sort_order == "desc":
            query = query.order_by(desc(getattr(MarketOpportunity, sort_by)))
        else:
            query = query.order_by(getattr(MarketOpportunity, sort_by))

        # Pagination
        limit = filters.get("limit", 50)
        offset = filters.get("offset", 0)

        return query.offset(offset).limit(limit).all()

    def convert_to_deal(
        self,
        opportunity_id: str,
        user_id: str,
        deal_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Convert qualified opportunity to active deal

        Args:
            opportunity_id: Opportunity ID
            user_id: User making the conversion
            deal_data: Optional additional deal data

        Returns:
            Created deal ID
        """
        opportunity = self.db.query(MarketOpportunity).filter(
            MarketOpportunity.id == opportunity_id
        ).first()

        if not opportunity:
            raise ValueError(f"Opportunity {opportunity_id} not found")

        # Update opportunity status
        opportunity.status = OpportunityStatus.CONVERTED_TO_DEAL
        opportunity.converted_to_deal_at = datetime.utcnow()

        # Would create Deal record here (importing from deal models)
        # For now, just return a placeholder
        deal_id = f"deal_{opportunity.id}"

        opportunity.metadata = opportunity.metadata or {}
        opportunity.metadata["converted_deal_id"] = deal_id

        self.db.commit()

        # Track activity
        self.track_activity(
            opportunity_id=opportunity_id,
            user_id=user_id,
            activity_type=ActivityType.CONVERTED_TO_DEAL,
            description=f"Converted to deal {deal_id}"
        )

        return deal_id

    def track_activity(
        self,
        opportunity_id: str,
        user_id: str,
        activity_type: ActivityType,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OpportunityActivity:
        """
        Track user activity on opportunity

        Args:
            opportunity_id: Opportunity ID
            user_id: User performing activity
            activity_type: Type of activity
            description: Activity description
            metadata: Optional additional data

        Returns:
            Created OpportunityActivity record
        """
        activity = OpportunityActivity(
            opportunity_id=opportunity_id,
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            metadata=metadata,
            occurred_at=datetime.utcnow()
        )

        self.db.add(activity)
        self.db.commit()

        return activity

    def get_opportunity_timeline(
        self,
        opportunity_id: str
    ) -> List[OpportunityActivity]:
        """Get activity timeline for opportunity"""
        return self.db.query(OpportunityActivity).filter(
            OpportunityActivity.opportunity_id == opportunity_id
        ).order_by(desc(OpportunityActivity.occurred_at)).all()

    def get_pipeline_metrics(
        self,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Get pipeline metrics and analytics

        Args:
            organization_id: Organization ID

        Returns:
            Dict with counts, averages, conversion rates
        """
        base_query = self.db.query(MarketOpportunity).filter(
            MarketOpportunity.organization_id == organization_id
        )

        # Status counts
        status_counts = {}
        for status in OpportunityStatus:
            count = base_query.filter(MarketOpportunity.status == status).count()
            status_counts[status.value] = count

        # Average score
        avg_score = base_query.filter(
            MarketOpportunity.overall_score.isnot(None)
        ).with_entities(func.avg(MarketOpportunity.overall_score)).scalar() or 0

        # Total opportunities
        total = base_query.count()

        # Qualified count
        qualified = base_query.filter(
            MarketOpportunity.status.in_([
                OpportunityStatus.QUALIFIED,
                OpportunityStatus.CONTACTED,
                OpportunityStatus.IN_DISCUSSION,
                OpportunityStatus.CONVERTED_TO_DEAL
            ])
        ).count()

        # Conversion rate
        conversion_rate = (qualified / total * 100) if total > 0 else 0

        return {
            "total_opportunities": total,
            "status_breakdown": status_counts,
            "average_score": round(avg_score, 2),
            "qualified_count": qualified,
            "conversion_rate": round(conversion_rate, 2),
            "new_this_week": base_query.filter(
                MarketOpportunity.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        }
