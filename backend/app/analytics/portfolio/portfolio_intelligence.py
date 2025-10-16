"""
Portfolio Intelligence Service
Real-time portfolio analytics with superhuman market intelligence
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from scipy.stats import pearsonr
from scipy.optimize import minimize
import aiohttp
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings
from app.core.database import get_database
from app.analytics import ADVANCED_ANALYTICS_CONFIG

logger = logging.getLogger(__name__)

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SynergyType(str, Enum):
    REVENUE = "revenue"
    COST = "cost"
    TECHNOLOGY = "technology"
    TALENT = "talent"
    SUPPLY_CHAIN = "supply_chain"

class AssetClass(str, Enum):
    PRIVATE_EQUITY = "private_equity"
    VENTURE_CAPITAL = "venture_capital"
    GROWTH_EQUITY = "growth_equity"
    BUYOUT = "buyout"
    DISTRESSED = "distressed"

@dataclass
class PortfolioMetrics:
    total_value: float
    invested_capital: float
    realized_value: float
    unrealized_value: float
    irr: float
    moic: float  # Multiple of Invested Capital
    dpi: float   # Distributions to Paid-In
    rvpi: float  # Residual Value to Paid-In
    sharpe_ratio: float
    alpha: float
    beta: float
    volatility: float
    max_drawdown: float
    number_of_investments: int
    active_investments: int
    fully_realized: int

@dataclass
class DealPerformance:
    deal_id: str
    company_name: str
    initial_investment: float
    current_value: float
    realized_returns: float
    total_return: float
    irr: float
    moic: float
    investment_date: datetime
    exit_date: Optional[datetime]
    holding_period_years: float
    sector: str
    geography: str
    stage: str
    performance_quartile: int
    value_creation_drivers: List[str]
    risk_factors: List[str]

@dataclass
class SynergyOpportunity:
    synergy_id: str
    synergy_type: SynergyType
    company_a_id: str
    company_b_id: str
    company_a_name: str
    company_b_name: str
    description: str
    estimated_value: float
    confidence_score: float
    implementation_complexity: str
    timeline_months: int
    required_resources: List[str]
    success_probability: float
    risk_factors: List[str]
    implementation_plan: Dict[str, Any]

@dataclass
class RiskAnalysis:
    overall_risk_score: float
    geographic_concentration: float
    sector_concentration: float
    vintage_concentration: float
    single_asset_exposure: float
    correlation_risk: float
    liquidity_risk: float
    esg_risk_score: float
    regulatory_risk_score: float
    market_risk_factors: List[str]
    mitigation_strategies: List[str]

@dataclass
class PerformanceAttribution:
    alpha_sources: Dict[str, float]
    sector_allocation_effect: float
    security_selection_effect: float
    timing_effect: float
    currency_effect: float
    leverage_effect: float
    fee_impact: float
    total_attribution: float

@dataclass
class BenchmarkComparison:
    benchmark_name: str
    portfolio_return: float
    benchmark_return: float
    excess_return: float
    tracking_error: float
    information_ratio: float
    up_capture: float
    down_capture: float
    quartile_ranking: int
    percentile_ranking: float

@dataclass
class PortfolioIntelligenceReport:
    portfolio_id: str
    as_of_date: datetime
    portfolio_metrics: PortfolioMetrics
    deal_performances: List[DealPerformance]
    synergy_opportunities: List[SynergyOpportunity]
    risk_analysis: RiskAnalysis
    performance_attribution: PerformanceAttribution
    benchmark_comparisons: List[BenchmarkComparison]
    key_insights: List[str]
    recommended_actions: List[str]
    market_outlook: Dict[str, Any]

class SynergyEngine:
    """AI-powered synergy identification and quantification engine"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["portfolio"]
        self.scaler = StandardScaler()

    async def identify_synergy_opportunities(
        self,
        portfolio_companies: List[Dict[str, Any]]
    ) -> List[SynergyOpportunity]:
        """Identify potential synergies between portfolio companies using AI"""
        opportunities = []

        # Calculate company similarity matrix
        similarity_matrix = await self._calculate_company_similarities(portfolio_companies)

        # Identify high-similarity pairs for synergy analysis
        for i, company_a in enumerate(portfolio_companies):
            for j, company_b in enumerate(portfolio_companies[i+1:], i+1):
                similarity_score = similarity_matrix[i][j]

                if similarity_score > self.config["synergy_detection_confidence"]:
                    synergies = await self._analyze_synergy_potential(
                        company_a, company_b, similarity_score
                    )
                    opportunities.extend(synergies)

        return sorted(opportunities, key=lambda x: x.estimated_value, reverse=True)

    async def _calculate_company_similarities(
        self,
        companies: List[Dict[str, Any]]
    ) -> np.ndarray:
        """Calculate similarity matrix between companies using multiple dimensions"""
        features = []

        for company in companies:
            # Extract feature vector for each company
            feature_vector = [
                company.get("revenue", 0),
                company.get("ebitda", 0),
                company.get("employees", 0),
                len(company.get("products", [])),
                len(company.get("markets", [])),
                len(company.get("technologies", [])),
                company.get("growth_rate", 0),
                company.get("margin", 0)
            ]

            # Add categorical features (one-hot encoded)
            sector_features = self._encode_categorical(
                company.get("sector", ""), ["technology", "healthcare", "financial", "industrial"]
            )
            geo_features = self._encode_categorical(
                company.get("geography", ""), ["north_america", "europe", "asia", "other"]
            )

            feature_vector.extend(sector_features + geo_features)
            features.append(feature_vector)

        # Calculate cosine similarity matrix
        features_array = np.array(features)
        features_scaled = self.scaler.fit_transform(features_array)

        return cosine_similarity(features_scaled)

    def _encode_categorical(self, value: str, categories: List[str]) -> List[int]:
        """One-hot encode categorical variables"""
        return [1 if cat in value.lower() else 0 for cat in categories]

    async def _analyze_synergy_potential(
        self,
        company_a: Dict[str, Any],
        company_b: Dict[str, Any],
        similarity_score: float
    ) -> List[SynergyOpportunity]:
        """Analyze specific synergy opportunities between two companies"""
        synergies = []

        # Revenue synergies
        revenue_synergy = await self._calculate_revenue_synergy(company_a, company_b)
        if revenue_synergy["value"] > 0:
            synergies.append(SynergyOpportunity(
                synergy_id=f"rev_{company_a['id']}_{company_b['id']}",
                synergy_type=SynergyType.REVENUE,
                company_a_id=company_a["id"],
                company_b_id=company_b["id"],
                company_a_name=company_a["name"],
                company_b_name=company_b["name"],
                description=revenue_synergy["description"],
                estimated_value=revenue_synergy["value"],
                confidence_score=similarity_score * revenue_synergy["confidence"],
                implementation_complexity=revenue_synergy["complexity"],
                timeline_months=revenue_synergy["timeline"],
                required_resources=revenue_synergy["resources"],
                success_probability=revenue_synergy["success_prob"],
                risk_factors=revenue_synergy["risks"],
                implementation_plan=revenue_synergy["plan"]
            ))

        # Cost synergies
        cost_synergy = await self._calculate_cost_synergy(company_a, company_b)
        if cost_synergy["value"] > 0:
            synergies.append(SynergyOpportunity(
                synergy_id=f"cost_{company_a['id']}_{company_b['id']}",
                synergy_type=SynergyType.COST,
                company_a_id=company_a["id"],
                company_b_id=company_b["id"],
                company_a_name=company_a["name"],
                company_b_name=company_b["name"],
                description=cost_synergy["description"],
                estimated_value=cost_synergy["value"],
                confidence_score=similarity_score * cost_synergy["confidence"],
                implementation_complexity=cost_synergy["complexity"],
                timeline_months=cost_synergy["timeline"],
                required_resources=cost_synergy["resources"],
                success_probability=cost_synergy["success_prob"],
                risk_factors=cost_synergy["risks"],
                implementation_plan=cost_synergy["plan"]
            ))

        return synergies

    async def _calculate_revenue_synergy(
        self,
        company_a: Dict[str, Any],
        company_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate revenue synergy potential"""
        # Cross-selling opportunities
        cross_sell_value = 0
        if set(company_a.get("markets", [])) & set(company_b.get("markets", [])):
            cross_sell_value = min(company_a.get("revenue", 0), company_b.get("revenue", 0)) * 0.05

        # Market expansion
        expansion_value = 0
        unique_markets = set(company_a.get("markets", [])) ^ set(company_b.get("markets", []))
        if unique_markets:
            expansion_value = len(unique_markets) * 2_000_000  # $2M per new market

        total_value = cross_sell_value + expansion_value

        return {
            "value": total_value,
            "description": f"Cross-selling and market expansion opportunities worth ${total_value:,.0f}",
            "confidence": 0.7,
            "complexity": "medium",
            "timeline": 12,
            "resources": ["sales team", "marketing", "integration"],
            "success_prob": 0.65,
            "risks": ["customer overlap", "channel conflict"],
            "plan": {"phase1": "market analysis", "phase2": "pilot programs", "phase3": "full rollout"}
        }

    async def _calculate_cost_synergy(
        self,
        company_a: Dict[str, Any],
        company_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate cost synergy potential"""
        # Operational efficiency improvements
        combined_revenue = company_a.get("revenue", 0) + company_b.get("revenue", 0)
        cost_savings = combined_revenue * 0.03  # 3% cost savings through scale

        # Technology synergies
        tech_overlap = set(company_a.get("technologies", [])) & set(company_b.get("technologies", []))
        tech_savings = len(tech_overlap) * 500_000  # $500K per shared technology

        total_value = cost_savings + tech_savings

        return {
            "value": total_value,
            "description": f"Operational and technology cost savings worth ${total_value:,.0f}",
            "confidence": 0.8,
            "complexity": "high",
            "timeline": 18,
            "resources": ["operations team", "IT integration", "change management"],
            "success_prob": 0.75,
            "risks": ["integration complexity", "employee resistance"],
            "plan": {"phase1": "systems audit", "phase2": "integration planning", "phase3": "execution"}
        }

class RiskAnalyzer:
    """Advanced risk analysis and concentration monitoring"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["portfolio"]

    async def analyze_portfolio_risk(
        self,
        portfolio_data: Dict[str, Any]
    ) -> RiskAnalysis:
        """Comprehensive risk analysis of portfolio composition and performance"""
        deals = portfolio_data.get("deals", [])

        # Calculate various risk metrics
        geographic_risk = self._calculate_geographic_concentration(deals)
        sector_risk = self._calculate_sector_concentration(deals)
        vintage_risk = self._calculate_vintage_concentration(deals)
        single_asset_risk = self._calculate_single_asset_exposure(deals)
        correlation_risk = await self._calculate_correlation_risk(deals)
        liquidity_risk = self._calculate_liquidity_risk(deals)
        esg_risk = await self._calculate_esg_risk(deals)
        regulatory_risk = await self._calculate_regulatory_risk(deals)

        # Aggregate overall risk score
        overall_risk = self._calculate_overall_risk_score([
            geographic_risk, sector_risk, vintage_risk, single_asset_risk,
            correlation_risk, liquidity_risk, esg_risk, regulatory_risk
        ])

        # Generate risk factors and mitigation strategies
        risk_factors = self._identify_key_risk_factors(deals)
        mitigation_strategies = self._recommend_mitigation_strategies(deals)

        return RiskAnalysis(
            overall_risk_score=overall_risk,
            geographic_concentration=geographic_risk,
            sector_concentration=sector_risk,
            vintage_concentration=vintage_risk,
            single_asset_exposure=single_asset_risk,
            correlation_risk=correlation_risk,
            liquidity_risk=liquidity_risk,
            esg_risk_score=esg_risk,
            regulatory_risk_score=regulatory_risk,
            market_risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies
        )

    def _calculate_geographic_concentration(self, deals: List[Dict[str, Any]]) -> float:
        """Calculate geographic concentration using Herfindahl-Hirschman Index"""
        if not deals:
            return 0.0

        geo_values = {}
        total_value = sum(deal.get("current_value", 0) for deal in deals)

        for deal in deals:
            geo = deal.get("geography", "unknown")
            geo_values[geo] = geo_values.get(geo, 0) + deal.get("current_value", 0)

        # Calculate HHI
        hhi = sum((value / total_value) ** 2 for value in geo_values.values()) if total_value > 0 else 0
        return min(1.0, hhi * 2)  # Normalize to 0-1 scale

    def _calculate_sector_concentration(self, deals: List[Dict[str, Any]]) -> float:
        """Calculate sector concentration risk"""
        if not deals:
            return 0.0

        sector_values = {}
        total_value = sum(deal.get("current_value", 0) for deal in deals)

        for deal in deals:
            sector = deal.get("sector", "unknown")
            sector_values[sector] = sector_values.get(sector, 0) + deal.get("current_value", 0)

        # Calculate HHI for sectors
        hhi = sum((value / total_value) ** 2 for value in sector_values.values()) if total_value > 0 else 0
        return min(1.0, hhi * 2)

    def _calculate_vintage_concentration(self, deals: List[Dict[str, Any]]) -> float:
        """Calculate vintage year concentration risk"""
        if not deals:
            return 0.0

        vintage_values = {}
        total_value = sum(deal.get("current_value", 0) for deal in deals)

        for deal in deals:
            vintage = deal.get("investment_date", "")[:4] if deal.get("investment_date") else "unknown"
            vintage_values[vintage] = vintage_values.get(vintage, 0) + deal.get("current_value", 0)

        hhi = sum((value / total_value) ** 2 for value in vintage_values.values()) if total_value > 0 else 0
        return min(1.0, hhi * 2)

    def _calculate_single_asset_exposure(self, deals: List[Dict[str, Any]]) -> float:
        """Calculate largest single asset exposure"""
        if not deals:
            return 0.0

        total_value = sum(deal.get("current_value", 0) for deal in deals)
        if total_value == 0:
            return 0.0

        max_exposure = max(deal.get("current_value", 0) for deal in deals)
        return max_exposure / total_value

    async def _calculate_correlation_risk(self, deals: List[Dict[str, Any]]) -> float:
        """Calculate correlation risk between portfolio companies"""
        # Simplified correlation risk - would use actual return correlations in production
        if len(deals) < 2:
            return 0.0

        # Mock correlation calculation based on sector similarity
        correlations = []
        for i, deal_a in enumerate(deals):
            for deal_b in deals[i+1:]:
                if deal_a.get("sector") == deal_b.get("sector"):
                    correlations.append(0.7)  # High correlation for same sector
                else:
                    correlations.append(0.2)  # Low correlation for different sectors

        avg_correlation = np.mean(correlations) if correlations else 0
        return max(0, avg_correlation - 0.3)  # Risk increases above 0.3 correlation

    def _calculate_liquidity_risk(self, deals: List[Dict[str, Any]]) -> float:
        """Calculate portfolio liquidity risk"""
        if not deals:
            return 0.0

        illiquid_value = 0
        total_value = sum(deal.get("current_value", 0) for deal in deals)

        for deal in deals:
            # Consider deals over 5 years old as less liquid
            investment_date = deal.get("investment_date")
            if investment_date:
                years_held = (datetime.now() - datetime.fromisoformat(investment_date[:10])).days / 365
                if years_held > 5:
                    illiquid_value += deal.get("current_value", 0)

        return illiquid_value / total_value if total_value > 0 else 0

    async def _calculate_esg_risk(self, deals: List[Dict[str, Any]]) -> float:
        """Calculate ESG risk score for portfolio"""
        # Mock ESG risk calculation - would integrate with ESG data providers
        high_risk_sectors = ["oil_gas", "mining", "tobacco", "weapons"]

        high_risk_value = 0
        total_value = sum(deal.get("current_value", 0) for deal in deals)

        for deal in deals:
            sector = deal.get("sector", "").lower()
            if any(risk_sector in sector for risk_sector in high_risk_sectors):
                high_risk_value += deal.get("current_value", 0)

        return high_risk_value / total_value if total_value > 0 else 0

    async def _calculate_regulatory_risk(self, deals: List[Dict[str, Any]]) -> float:
        """Calculate regulatory risk exposure"""
        # Mock regulatory risk calculation
        high_reg_risk_sectors = ["financial", "healthcare", "utilities", "telecommunications"]

        high_risk_value = 0
        total_value = sum(deal.get("current_value", 0) for deal in deals)

        for deal in deals:
            sector = deal.get("sector", "").lower()
            if any(risk_sector in sector for risk_sector in high_reg_risk_sectors):
                high_risk_value += deal.get("current_value", 0)

        return high_risk_value / total_value if total_value > 0 else 0

    def _calculate_overall_risk_score(self, risk_components: List[float]) -> float:
        """Calculate weighted overall risk score"""
        weights = [0.15, 0.15, 0.1, 0.2, 0.15, 0.1, 0.1, 0.05]  # Adjust weights as needed
        weighted_score = sum(r * w for r, w in zip(risk_components, weights))
        return min(1.0, weighted_score)

    def _identify_key_risk_factors(self, deals: List[Dict[str, Any]]) -> List[str]:
        """Identify key risk factors affecting the portfolio"""
        risk_factors = []

        # Analyze concentration risks
        if self._calculate_geographic_concentration(deals) > 0.5:
            risk_factors.append("High geographic concentration in single market")

        if self._calculate_sector_concentration(deals) > 0.4:
            risk_factors.append("Sector concentration risk in primary industry")

        if self._calculate_single_asset_exposure(deals) > 0.25:
            risk_factors.append("Single asset concentration above 25% threshold")

        # Market-specific risks
        risk_factors.extend([
            "Interest rate sensitivity for leveraged positions",
            "Economic cycle dependency",
            "Currency exposure in international investments",
            "Regulatory changes in key sectors"
        ])

        return risk_factors

    def _recommend_mitigation_strategies(self, deals: List[Dict[str, Any]]) -> List[str]:
        """Recommend risk mitigation strategies"""
        strategies = [
            "Diversify across geographies to reduce concentration risk",
            "Consider hedging interest rate exposure for leveraged deals",
            "Implement ESG screening and monitoring processes",
            "Regular stress testing of portfolio under adverse scenarios",
            "Maintain adequate cash reserves for liquidity needs",
            "Monitor regulatory developments in key sectors",
            "Consider correlation risk when making new investments"
        ]

        return strategies

class PortfolioIntelligenceService:
    """Main service orchestrating portfolio intelligence and analytics"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["portfolio"]
        self.synergy_engine = SynergyEngine()
        self.risk_analyzer = RiskAnalyzer()

    async def generate_portfolio_intelligence_report(
        self,
        portfolio_id: str,
        include_predictions: bool = True
    ) -> PortfolioIntelligenceReport:
        """Generate comprehensive portfolio intelligence report"""
        try:
            logger.info(f"Generating portfolio intelligence report for portfolio {portfolio_id}")

            # Gather portfolio data
            portfolio_data = await self._get_portfolio_data(portfolio_id)

            # Calculate core metrics
            portfolio_metrics = await self._calculate_portfolio_metrics(portfolio_data)

            # Analyze deal performances
            deal_performances = await self._analyze_deal_performances(portfolio_data)

            # Identify synergy opportunities
            synergy_opportunities = await self.synergy_engine.identify_synergy_opportunities(
                portfolio_data.get("companies", [])
            )

            # Perform risk analysis
            risk_analysis = await self.risk_analyzer.analyze_portfolio_risk(portfolio_data)

            # Calculate performance attribution
            performance_attribution = await self._calculate_performance_attribution(portfolio_data)

            # Benchmark comparisons
            benchmark_comparisons = await self._perform_benchmark_comparisons(portfolio_data)

            # Generate AI insights
            key_insights = await self._generate_key_insights(
                portfolio_metrics, deal_performances, synergy_opportunities, risk_analysis
            )

            # Recommend actions
            recommended_actions = await self._recommend_actions(
                portfolio_data, risk_analysis, synergy_opportunities
            )

            # Market outlook
            market_outlook = await self._generate_market_outlook(portfolio_data)

            return PortfolioIntelligenceReport(
                portfolio_id=portfolio_id,
                as_of_date=datetime.utcnow(),
                portfolio_metrics=portfolio_metrics,
                deal_performances=deal_performances,
                synergy_opportunities=synergy_opportunities,
                risk_analysis=risk_analysis,
                performance_attribution=performance_attribution,
                benchmark_comparisons=benchmark_comparisons,
                key_insights=key_insights,
                recommended_actions=recommended_actions,
                market_outlook=market_outlook
            )

        except Exception as e:
            logger.error(f"Error generating portfolio intelligence report: {e}")
            raise

    async def _get_portfolio_data(self, portfolio_id: str) -> Dict[str, Any]:
        """Retrieve comprehensive portfolio data"""
        # Mock data - would integrate with actual database
        return {
            "portfolio_id": portfolio_id,
            "name": "Growth Equity Fund III",
            "fund_size": 500_000_000,
            "invested_capital": 350_000_000,
            "deals": [
                {
                    "id": "deal_001",
                    "company_name": "TechCorp Solutions",
                    "sector": "technology",
                    "geography": "north_america",
                    "initial_investment": 25_000_000,
                    "current_value": 45_000_000,
                    "investment_date": "2020-03-15",
                    "stage": "series_b",
                    "revenue": 50_000_000,
                    "ebitda": 12_500_000,
                    "employees": 200,
                    "products": ["SaaS platform", "Analytics tools"],
                    "markets": ["north_america", "europe"],
                    "technologies": ["AI/ML", "Cloud computing"]
                },
                {
                    "id": "deal_002",
                    "company_name": "HealthTech Innovations",
                    "sector": "healthcare",
                    "geography": "north_america",
                    "initial_investment": 30_000_000,
                    "current_value": 55_000_000,
                    "investment_date": "2021-06-10",
                    "stage": "series_c",
                    "revenue": 75_000_000,
                    "ebitda": 18_750_000,
                    "employees": 350,
                    "products": ["Medical devices", "Diagnostics"],
                    "markets": ["north_america"],
                    "technologies": ["Biotech", "AI diagnostics"]
                }
            ],
            "companies": [
                {
                    "id": "deal_001",
                    "name": "TechCorp Solutions",
                    "sector": "technology",
                    "geography": "north_america",
                    "revenue": 50_000_000,
                    "ebitda": 12_500_000,
                    "employees": 200,
                    "products": ["SaaS platform", "Analytics tools"],
                    "markets": ["north_america", "europe"],
                    "technologies": ["AI/ML", "Cloud computing"],
                    "growth_rate": 0.35,
                    "margin": 0.25
                },
                {
                    "id": "deal_002",
                    "name": "HealthTech Innovations",
                    "sector": "healthcare",
                    "geography": "north_america",
                    "revenue": 75_000_000,
                    "ebitda": 18_750_000,
                    "employees": 350,
                    "products": ["Medical devices", "Diagnostics"],
                    "markets": ["north_america"],
                    "technologies": ["Biotech", "AI diagnostics"],
                    "growth_rate": 0.28,
                    "margin": 0.25
                }
            ]
        }

    async def _calculate_portfolio_metrics(self, portfolio_data: Dict[str, Any]) -> PortfolioMetrics:
        """Calculate comprehensive portfolio performance metrics"""
        deals = portfolio_data.get("deals", [])

        total_value = sum(deal.get("current_value", 0) for deal in deals)
        invested_capital = sum(deal.get("initial_investment", 0) for deal in deals)
        realized_value = sum(deal.get("realized_returns", 0) for deal in deals)
        unrealized_value = total_value - realized_value

        # Calculate IRR (simplified)
        if invested_capital > 0:
            moic = total_value / invested_capital
            # Simplified IRR calculation - would use actual cash flow timing in production
            avg_holding_period = 3.5  # years
            irr = (moic ** (1/avg_holding_period)) - 1 if moic > 0 else 0
        else:
            moic = 0
            irr = 0

        # Calculate DPI and RVPI
        dpi = realized_value / invested_capital if invested_capital > 0 else 0
        rvpi = unrealized_value / invested_capital if invested_capital > 0 else 0

        # Risk-adjusted metrics (simplified)
        sharpe_ratio = 1.2  # Would calculate from actual returns
        alpha = 0.05       # Excess return over benchmark
        beta = 1.1         # Market sensitivity
        volatility = 0.18  # Annual volatility
        max_drawdown = 0.12  # Maximum drawdown

        return PortfolioMetrics(
            total_value=total_value,
            invested_capital=invested_capital,
            realized_value=realized_value,
            unrealized_value=unrealized_value,
            irr=irr,
            moic=moic,
            dpi=dpi,
            rvpi=rvpi,
            sharpe_ratio=sharpe_ratio,
            alpha=alpha,
            beta=beta,
            volatility=volatility,
            max_drawdown=max_drawdown,
            number_of_investments=len(deals),
            active_investments=len([d for d in deals if not d.get("exit_date")]),
            fully_realized=len([d for d in deals if d.get("exit_date")])
        )

    async def _analyze_deal_performances(self, portfolio_data: Dict[str, Any]) -> List[DealPerformance]:
        """Analyze individual deal performances"""
        performances = []

        for deal in portfolio_data.get("deals", []):
            investment_date = datetime.fromisoformat(deal["investment_date"])
            holding_period = (datetime.now() - investment_date).days / 365

            initial_investment = deal.get("initial_investment", 0)
            current_value = deal.get("current_value", 0)
            realized_returns = deal.get("realized_returns", 0)
            total_return = (current_value + realized_returns - initial_investment)

            # Calculate deal-level metrics
            deal_moic = current_value / initial_investment if initial_investment > 0 else 0
            deal_irr = (deal_moic ** (1/max(holding_period, 0.1))) - 1 if deal_moic > 0 else 0

            # Determine performance quartile (simplified)
            performance_quartile = 1 if deal_irr > 0.25 else 2 if deal_irr > 0.15 else 3 if deal_irr > 0.10 else 4

            performances.append(DealPerformance(
                deal_id=deal["id"],
                company_name=deal["company_name"],
                initial_investment=initial_investment,
                current_value=current_value,
                realized_returns=realized_returns,
                total_return=total_return,
                irr=deal_irr,
                moic=deal_moic,
                investment_date=investment_date,
                exit_date=None,  # Would parse if available
                holding_period_years=holding_period,
                sector=deal.get("sector", ""),
                geography=deal.get("geography", ""),
                stage=deal.get("stage", ""),
                performance_quartile=performance_quartile,
                value_creation_drivers=["revenue growth", "margin expansion", "market expansion"],
                risk_factors=["competition", "regulation", "key person risk"]
            ))

        return performances

    async def _calculate_performance_attribution(self, portfolio_data: Dict[str, Any]) -> PerformanceAttribution:
        """Calculate performance attribution across factors"""
        # Simplified attribution analysis - would be more sophisticated in production
        return PerformanceAttribution(
            alpha_sources={
                "sector_selection": 0.02,
                "timing": 0.015,
                "value_creation": 0.03,
                "multiple_expansion": 0.01
            },
            sector_allocation_effect=0.008,
            security_selection_effect=0.025,
            timing_effect=0.012,
            currency_effect=-0.003,
            leverage_effect=0.005,
            fee_impact=-0.015,
            total_attribution=0.072
        )

    async def _perform_benchmark_comparisons(self, portfolio_data: Dict[str, Any]) -> List[BenchmarkComparison]:
        """Compare portfolio performance against relevant benchmarks"""
        # Mock benchmark data - would integrate with index providers
        return [
            BenchmarkComparison(
                benchmark_name="Cambridge Associates US PE Index",
                portfolio_return=0.18,
                benchmark_return=0.14,
                excess_return=0.04,
                tracking_error=0.05,
                information_ratio=0.8,
                up_capture=1.15,
                down_capture=0.85,
                quartile_ranking=1,
                percentile_ranking=0.85
            ),
            BenchmarkComparison(
                benchmark_name="Burgiss All Private Equity",
                portfolio_return=0.18,
                benchmark_return=0.16,
                excess_return=0.02,
                tracking_error=0.04,
                information_ratio=0.5,
                up_capture=1.08,
                down_capture=0.92,
                quartile_ranking=2,
                percentile_ranking=0.65
            )
        ]

    async def _generate_key_insights(
        self,
        metrics: PortfolioMetrics,
        performances: List[DealPerformance],
        synergies: List[SynergyOpportunity],
        risk_analysis: RiskAnalysis
    ) -> List[str]:
        """Generate AI-powered insights from portfolio analysis"""
        insights = []

        # Performance insights
        if metrics.irr > 0.20:
            insights.append(f"Portfolio delivering exceptional returns with {metrics.irr:.1%} IRR, placing it in top quartile performance")

        if metrics.moic > 2.0:
            insights.append(f"Strong value creation with {metrics.moic:.1f}x MOIC, indicating effective investment selection and value-add strategies")

        # Synergy insights
        high_value_synergies = [s for s in synergies if s.estimated_value > 5_000_000]
        if high_value_synergies:
            total_synergy_value = sum(s.estimated_value for s in high_value_synergies)
            insights.append(f"Identified ${total_synergy_value:,.0f} in high-value synergy opportunities across {len(high_value_synergies)} portfolio company pairs")

        # Risk insights
        if risk_analysis.overall_risk_score > 0.7:
            insights.append("Portfolio shows elevated risk concentration - recommend diversification across geography and sectors")

        # Performance attribution
        top_performers = [p for p in performances if p.performance_quartile == 1]
        if top_performers:
            insights.append(f"{len(top_performers)} investments are first quartile performers, contributing significantly to portfolio alpha")

        return insights

    async def _recommend_actions(
        self,
        portfolio_data: Dict[str, Any],
        risk_analysis: RiskAnalysis,
        synergies: List[SynergyOpportunity]
    ) -> List[str]:
        """Generate actionable recommendations"""
        actions = []

        # Risk-based actions
        if risk_analysis.geographic_concentration > 0.5:
            actions.append("Consider geographic diversification for future investments to reduce concentration risk")

        if risk_analysis.single_asset_exposure > 0.25:
            actions.append("Monitor largest position closely and consider partial realization to reduce single-asset risk")

        # Synergy-based actions
        top_synergies = sorted(synergies, key=lambda x: x.estimated_value, reverse=True)[:3]
        for synergy in top_synergies:
            actions.append(f"Prioritize {synergy.synergy_type.value} synergy between {synergy.company_a_name} and {synergy.company_b_name} - estimated value ${synergy.estimated_value:,.0f}")

        # Portfolio optimization
        actions.append("Initiate quarterly business reviews with portfolio company management teams")
        actions.append("Consider ESG enhancement initiatives to improve risk profile and exit valuations")

        return actions

    async def _generate_market_outlook(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market outlook relevant to portfolio"""
        return {
            "overall_sentiment": "cautiously_optimistic",
            "key_trends": [
                "AI adoption accelerating across portfolio sectors",
                "ESG considerations increasingly important for exits",
                "Public market volatility creating private market opportunities"
            ],
            "sector_outlooks": {
                "technology": "strong_growth_expected",
                "healthcare": "stable_with_innovation_premium",
                "financial_services": "consolidation_opportunities"
            },
            "exit_environment": "favorable_for_high_quality_assets",
            "fundraising_outlook": "competitive_but_opportunities_exist"
        }

# Service factory function
_portfolio_intelligence_service = None

async def get_portfolio_intelligence_service() -> PortfolioIntelligenceService:
    """Get singleton portfolio intelligence service instance"""
    global _portfolio_intelligence_service
    if _portfolio_intelligence_service is None:
        _portfolio_intelligence_service = PortfolioIntelligenceService()
    return _portfolio_intelligence_service