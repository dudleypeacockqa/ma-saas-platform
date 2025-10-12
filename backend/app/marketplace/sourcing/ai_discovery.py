"""
AI-Powered Deal Sourcing Engine
Intelligent discovery of M&A opportunities globally
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import numpy as np
import pandas as pd
from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings
from app.services.financial_intelligence import FinancialIntelligenceService

logger = logging.getLogger(__name__)

Base = declarative_base()

class OpportunityType(Enum):
    """Types of M&A opportunities"""
    DISTRESSED = "distressed"
    GROWTH = "growth"
    SUCCESSION = "succession"
    STRATEGIC = "strategic"
    CROSS_BORDER = "cross_border"
    CONSOLIDATION = "consolidation"
    SPIN_OFF = "spin_off"

class DealStage(Enum):
    """Stages of deal readiness"""
    EARLY_STAGE = "early_stage"
    PREPARATION = "preparation"
    MARKET_READY = "market_ready"
    ACTIVE_PROCESS = "active_process"
    UNDER_LOI = "under_loi"

@dataclass
class CompanyProfile:
    """Company profile for M&A analysis"""
    company_id: str
    name: str
    industry: str
    sector: str
    geography: str
    revenue: float
    ebitda: float
    employees: int
    founded_year: int
    ownership_structure: str
    financial_health_score: float
    growth_trajectory: str

@dataclass
class OpportunitySignal:
    """M&A opportunity signal detected by AI"""
    signal_id: str
    company_id: str
    opportunity_type: OpportunityType
    confidence_score: float
    reasoning: str
    financial_indicators: Dict[str, float]
    market_indicators: Dict[str, Any]
    timing_score: float
    urgency_level: str

class DealOpportunity(Base):
    """Database model for discovered deal opportunities"""
    __tablename__ = "deal_opportunities"

    id = Column(String(64), primary_key=True)
    company_id = Column(String(64), nullable=False)
    opportunity_type = Column(String(50), nullable=False)
    deal_stage = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=False)
    ai_reasoning = Column(Text)
    financial_summary = Column(Text)  # JSON
    market_analysis = Column(Text)   # JSON
    discovered_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    views_count = Column(Integer, default=0)
    inquiries_count = Column(Integer, default=0)

class DealSourcingEngine:
    """
    AI-Powered Deal Sourcing Engine
    Discovers M&A opportunities through intelligent analysis
    """

    def __init__(self):
        self.financial_service = FinancialIntelligenceService()
        self.analysis_models = {}
        self.data_sources = [
            "pitchbook_api",
            "sp_capital_iq",
            "crunchbase_api",
            "bloomberg_terminal",
            "company_filings"
        ]

    async def discover_opportunities(
        self,
        search_criteria: Dict[str, Any],
        max_results: int = 1000
    ) -> List[OpportunitySignal]:
        """
        Discover M&A opportunities using AI analysis

        Args:
            search_criteria: Filtering and targeting criteria
            max_results: Maximum number of opportunities to return

        Returns:
            List of discovered opportunity signals
        """
        try:
            # Step 1: Gather company universe
            companies = await self._get_company_universe(search_criteria)
            logger.info(f"Analyzing {len(companies)} companies for M&A opportunities")

            # Step 2: Parallel analysis of different opportunity types
            analysis_tasks = [
                self._find_distressed_opportunities(companies),
                self._find_growth_opportunities(companies),
                self._find_succession_opportunities(companies),
                self._find_strategic_opportunities(companies),
                self._find_cross_border_opportunities(companies)
            ]

            # Execute analyses in parallel
            opportunity_sets = await asyncio.gather(*analysis_tasks)

            # Step 3: Combine and rank opportunities
            all_opportunities = []
            for opportunity_set in opportunity_sets:
                all_opportunities.extend(opportunity_set)

            # Step 4: Remove duplicates and rank by confidence
            unique_opportunities = self._deduplicate_opportunities(all_opportunities)
            ranked_opportunities = sorted(
                unique_opportunities,
                key=lambda x: x.confidence_score,
                reverse=True
            )

            return ranked_opportunities[:max_results]

        except Exception as e:
            logger.error(f"Deal discovery failed: {str(e)}")
            raise

    async def _find_distressed_opportunities(self, companies: List[CompanyProfile]) -> List[OpportunitySignal]:
        """
        Identify financially distressed companies using AI analysis

        Financial distress indicators:
        - Declining revenue/EBITDA trends
        - High debt-to-equity ratios
        - Cash flow problems
        - Covenant breaches
        - Credit rating downgrades
        """
        try:
            distressed_signals = []

            for company in companies:
                # Get comprehensive financial data
                financial_data = await self.financial_service.get_company_financials(company.company_id)

                # Calculate distress indicators
                distress_score = await self._calculate_distress_score(financial_data)

                if distress_score > 0.7:  # High distress probability
                    # Generate detailed reasoning
                    reasoning = await self._generate_distress_reasoning(financial_data, distress_score)

                    signal = OpportunitySignal(
                        signal_id=f"distressed_{company.company_id}_{int(datetime.now().timestamp())}",
                        company_id=company.company_id,
                        opportunity_type=OpportunityType.DISTRESSED,
                        confidence_score=distress_score,
                        reasoning=reasoning,
                        financial_indicators=self._extract_key_indicators(financial_data),
                        market_indicators=await self._get_market_context(company),
                        timing_score=self._calculate_timing_score(financial_data),
                        urgency_level="high" if distress_score > 0.85 else "medium"
                    )

                    distressed_signals.append(signal)

            logger.info(f"Found {len(distressed_signals)} distressed opportunities")
            return distressed_signals

        except Exception as e:
            logger.error(f"Distressed opportunity detection failed: {str(e)}")
            return []

    async def _find_growth_opportunities(self, companies: List[CompanyProfile]) -> List[OpportunitySignal]:
        """
        Identify high-growth companies suitable for acquisition

        Growth indicators:
        - Revenue growth rates above industry average
        - Market share expansion
        - Product innovation and R&D investment
        - Geographic expansion
        - Strong management team
        """
        try:
            growth_signals = []

            for company in companies:
                # Analyze growth trajectory
                growth_analysis = await self._analyze_growth_trajectory(company)

                if growth_analysis["growth_score"] > 0.75:  # High growth potential
                    reasoning = await self._generate_growth_reasoning(growth_analysis)

                    signal = OpportunitySignal(
                        signal_id=f"growth_{company.company_id}_{int(datetime.now().timestamp())}",
                        company_id=company.company_id,
                        opportunity_type=OpportunityType.GROWTH,
                        confidence_score=growth_analysis["growth_score"],
                        reasoning=reasoning,
                        financial_indicators=growth_analysis["financial_metrics"],
                        market_indicators=growth_analysis["market_metrics"],
                        timing_score=growth_analysis["timing_score"],
                        urgency_level="medium"
                    )

                    growth_signals.append(signal)

            logger.info(f"Found {len(growth_signals)} growth opportunities")
            return growth_signals

        except Exception as e:
            logger.error(f"Growth opportunity detection failed: {str(e)}")
            return []

    async def _find_succession_opportunities(self, companies: List[CompanyProfile]) -> List[OpportunitySignal]:
        """
        Identify succession planning opportunities

        Succession indicators:
        - Aging ownership (65+ years)
        - Family-owned businesses without clear succession
        - Founder-led companies seeking exit
        - Management buyout potential
        - Estate planning triggers
        """
        try:
            succession_signals = []

            for company in companies:
                # Analyze ownership structure and demographics
                succession_analysis = await self._analyze_succession_potential(company)

                if succession_analysis["succession_probability"] > 0.6:
                    reasoning = await self._generate_succession_reasoning(succession_analysis)

                    signal = OpportunitySignal(
                        signal_id=f"succession_{company.company_id}_{int(datetime.now().timestamp())}",
                        company_id=company.company_id,
                        opportunity_type=OpportunityType.SUCCESSION,
                        confidence_score=succession_analysis["succession_probability"],
                        reasoning=reasoning,
                        financial_indicators=succession_analysis["financial_health"],
                        market_indicators=succession_analysis["market_position"],
                        timing_score=succession_analysis["timing_urgency"],
                        urgency_level=succession_analysis["urgency_level"]
                    )

                    succession_signals.append(signal)

            logger.info(f"Found {len(succession_signals)} succession opportunities")
            return succession_signals

        except Exception as e:
            logger.error(f"Succession opportunity detection failed: {str(e)}")
            return []

    async def _find_strategic_opportunities(self, companies: List[CompanyProfile]) -> List[OpportunitySignal]:
        """
        Identify strategic acquisition opportunities

        Strategic indicators:
        - Complementary capabilities
        - Market consolidation potential
        - Technology acquisition targets
        - Vertical integration opportunities
        - Geographic expansion enablers
        """
        try:
            strategic_signals = []

            for company in companies:
                # Analyze strategic value
                strategic_analysis = await self._analyze_strategic_value(company)

                if strategic_analysis["strategic_score"] > 0.7:
                    reasoning = await self._generate_strategic_reasoning(strategic_analysis)

                    signal = OpportunitySignal(
                        signal_id=f"strategic_{company.company_id}_{int(datetime.now().timestamp())}",
                        company_id=company.company_id,
                        opportunity_type=OpportunityType.STRATEGIC,
                        confidence_score=strategic_analysis["strategic_score"],
                        reasoning=reasoning,
                        financial_indicators=strategic_analysis["financial_attractiveness"],
                        market_indicators=strategic_analysis["strategic_positioning"],
                        timing_score=strategic_analysis["acquisition_timing"],
                        urgency_level="low"  # Strategic deals are typically patient
                    )

                    strategic_signals.append(signal)

            logger.info(f"Found {len(strategic_signals)} strategic opportunities")
            return strategic_signals

        except Exception as e:
            logger.error(f"Strategic opportunity detection failed: {str(e)}")
            return []

    async def _find_cross_border_opportunities(self, companies: List[CompanyProfile]) -> List[OpportunitySignal]:
        """
        Identify cross-border expansion opportunities

        Cross-border indicators:
        - Strong domestic market position
        - Scalable business model
        - International expansion potential
        - Favorable regulatory environment
        - Currency arbitrage opportunities
        """
        try:
            cross_border_signals = []

            for company in companies:
                # Analyze cross-border potential
                cross_border_analysis = await self._analyze_cross_border_potential(company)

                if cross_border_analysis["expansion_score"] > 0.65:
                    reasoning = await self._generate_cross_border_reasoning(cross_border_analysis)

                    signal = OpportunitySignal(
                        signal_id=f"cross_border_{company.company_id}_{int(datetime.now().timestamp())}",
                        company_id=company.company_id,
                        opportunity_type=OpportunityType.CROSS_BORDER,
                        confidence_score=cross_border_analysis["expansion_score"],
                        reasoning=reasoning,
                        financial_indicators=cross_border_analysis["financial_metrics"],
                        market_indicators=cross_border_analysis["market_expansion"],
                        timing_score=cross_border_analysis["timing_score"],
                        urgency_level="medium"
                    )

                    cross_border_signals.append(signal)

            logger.info(f"Found {len(cross_border_signals)} cross-border opportunities")
            return cross_border_signals

        except Exception as e:
            logger.error(f"Cross-border opportunity detection failed: {str(e)}")
            return []

    async def _get_company_universe(self, criteria: Dict[str, Any]) -> List[CompanyProfile]:
        """Get universe of companies to analyze"""
        # This would integrate with data providers to get company data
        # For now, return a mock dataset
        return []

    async def _calculate_distress_score(self, financial_data: Dict[str, Any]) -> float:
        """Calculate financial distress probability using Altman Z-Score and other indicators"""
        try:
            # Altman Z-Score calculation
            working_capital = financial_data.get("working_capital", 0)
            total_assets = financial_data.get("total_assets", 1)
            retained_earnings = financial_data.get("retained_earnings", 0)
            ebit = financial_data.get("ebit", 0)
            market_value_equity = financial_data.get("market_value_equity", 0)
            total_liabilities = financial_data.get("total_liabilities", 0)
            sales = financial_data.get("sales", 0)

            if total_assets == 0:
                return 0.0

            z_score = (
                1.2 * (working_capital / total_assets) +
                1.4 * (retained_earnings / total_assets) +
                3.3 * (ebit / total_assets) +
                0.6 * (market_value_equity / total_liabilities) +
                1.0 * (sales / total_assets)
            )

            # Convert Z-score to distress probability
            if z_score < 1.8:
                distress_probability = 0.95  # Very high distress
            elif z_score < 3.0:
                distress_probability = 0.75  # Moderate distress
            else:
                distress_probability = 0.25  # Low distress

            # Adjust based on other indicators
            cash_flow_trend = financial_data.get("cash_flow_trend", 0)
            debt_service_coverage = financial_data.get("debt_service_coverage", 1)

            if cash_flow_trend < -0.2:  # Declining cash flow
                distress_probability += 0.1

            if debt_service_coverage < 1.25:  # Poor debt coverage
                distress_probability += 0.15

            return min(distress_probability, 1.0)

        except Exception as e:
            logger.error(f"Distress score calculation failed: {str(e)}")
            return 0.0

    async def _generate_distress_reasoning(self, financial_data: Dict[str, Any], score: float) -> str:
        """Generate AI reasoning for distress opportunity"""
        reasoning_factors = []

        if financial_data.get("cash_flow_trend", 0) < -0.1:
            reasoning_factors.append("declining cash flow trends")

        if financial_data.get("debt_to_equity", 0) > 3.0:
            reasoning_factors.append("high leverage ratios")

        if financial_data.get("current_ratio", 1) < 1.0:
            reasoning_factors.append("liquidity concerns")

        reasoning = f"Company shows {score:.0%} probability of financial distress based on {', '.join(reasoning_factors)}. "
        reasoning += f"Altman Z-Score indicates potential bankruptcy risk. "
        reasoning += f"This could create acquisition opportunity at attractive valuation."

        return reasoning

    def _extract_key_indicators(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract key financial indicators for opportunity assessment"""
        return {
            "revenue_growth": financial_data.get("revenue_growth", 0),
            "ebitda_margin": financial_data.get("ebitda_margin", 0),
            "debt_to_equity": financial_data.get("debt_to_equity", 0),
            "current_ratio": financial_data.get("current_ratio", 0),
            "cash_flow_yield": financial_data.get("cash_flow_yield", 0)
        }

    async def _get_market_context(self, company: CompanyProfile) -> Dict[str, Any]:
        """Get market context for the company"""
        return {
            "industry_growth_rate": 0.05,  # Mock data
            "market_volatility": 0.25,
            "competitive_intensity": 0.7,
            "regulatory_environment": "stable"
        }

    def _calculate_timing_score(self, financial_data: Dict[str, Any]) -> float:
        """Calculate timing score for opportunity (higher = more urgent)"""
        # Consider factors like cash runway, debt maturities, seasonal patterns
        cash_runway_months = financial_data.get("cash_runway_months", 12)
        debt_maturity_months = financial_data.get("next_debt_maturity_months", 24)

        # Higher score for shorter timeframes
        timing_score = 1.0 - min(cash_runway_months / 24, 1.0)  # 24 months max
        timing_score += 1.0 - min(debt_maturity_months / 36, 1.0)  # 36 months max

        return min(timing_score / 2, 1.0)  # Normalize to 0-1

    def _deduplicate_opportunities(self, opportunities: List[OpportunitySignal]) -> List[OpportunitySignal]:
        """Remove duplicate opportunities for the same company"""
        seen_companies = set()
        unique_opportunities = []

        # Sort by confidence score descending
        sorted_opportunities = sorted(opportunities, key=lambda x: x.confidence_score, reverse=True)

        for opportunity in sorted_opportunities:
            if opportunity.company_id not in seen_companies:
                unique_opportunities.append(opportunity)
                seen_companies.add(opportunity.company_id)

        return unique_opportunities

    # Additional analysis methods would be implemented here...
    async def _analyze_growth_trajectory(self, company: CompanyProfile) -> Dict[str, Any]:
        return {"growth_score": 0.8, "financial_metrics": {}, "market_metrics": {}, "timing_score": 0.7}

    async def _analyze_succession_potential(self, company: CompanyProfile) -> Dict[str, Any]:
        return {"succession_probability": 0.7, "financial_health": {}, "market_position": {}, "timing_urgency": 0.6, "urgency_level": "medium"}

    async def _analyze_strategic_value(self, company: CompanyProfile) -> Dict[str, Any]:
        return {"strategic_score": 0.75, "financial_attractiveness": {}, "strategic_positioning": {}, "acquisition_timing": 0.5}

    async def _analyze_cross_border_potential(self, company: CompanyProfile) -> Dict[str, Any]:
        return {"expansion_score": 0.7, "financial_metrics": {}, "market_expansion": {}, "timing_score": 0.6}

    async def _generate_growth_reasoning(self, analysis: Dict[str, Any]) -> str:
        return "High-growth company with strong market position and expansion potential."

    async def _generate_succession_reasoning(self, analysis: Dict[str, Any]) -> str:
        return "Succession planning opportunity with aging ownership and strong business fundamentals."

    async def _generate_strategic_reasoning(self, analysis: Dict[str, Any]) -> str:
        return "Strategic acquisition target with complementary capabilities and market synergies."

    async def _generate_cross_border_reasoning(self, analysis: Dict[str, Any]) -> str:
        return "Cross-border expansion opportunity with scalable business model and favorable market conditions."

# Global deal sourcing engine instance
deal_sourcing_engine = DealSourcingEngine()