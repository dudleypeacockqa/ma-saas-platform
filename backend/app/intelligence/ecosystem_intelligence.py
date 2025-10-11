"""
Ecosystem Intelligence Platform
Comprehensive market analysis and opportunity identification for M&A ecosystem
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import numpy as np
import networkx as nx
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import DBSCAN
import pandas as pd
import structlog

logger = structlog.get_logger()


class MarketSegment(Enum):
    """M&A market segments"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    SERVICES = "services"
    REAL_ESTATE = "real_estate"
    ENERGY = "energy"


class OpportunityType(Enum):
    """Types of market opportunities"""
    ACQUISITION = "acquisition"
    PARTNERSHIP = "partnership"
    MARKET_ENTRY = "market_entry"
    CONSOLIDATION = "consolidation"
    DISRUPTION = "disruption"
    INTEGRATION = "integration"


@dataclass
class MarketOpportunity:
    """Market opportunity identification"""
    opportunity_id: str
    type: OpportunityType
    segment: MarketSegment
    value_potential: float  # £ millions
    probability: float  # 0-1
    time_horizon: int  # months
    key_players: List[str]
    entry_barriers: List[str]
    success_factors: List[str]
    risk_assessment: Dict[str, float]
    action_items: List[str]
    confidence_score: float


@dataclass
class EcosystemInsight:
    """Strategic ecosystem insight"""
    category: str
    insight: str
    impact: str
    opportunity_value: float
    implementation_difficulty: str
    time_to_value: int  # days
    confidence: float
    supporting_data: Dict[str, Any]
    recommendations: List[str]


class EcosystemIntelligence:
    """Main ecosystem intelligence engine"""

    def __init__(self, db_session):
        self.db = db_session
        self.market_graph = nx.DiGraph()
        self.ml_models = {}
        self.market_data_cache = {}
        self.opportunity_scorer = OpportunityScorer()
        self.trend_analyzer = MarketTrendAnalyzer()
        self.network_analyzer = EcosystemNetworkAnalyzer()

    async def analyze_ecosystem(self) -> Dict[str, Any]:
        """Comprehensive ecosystem analysis"""

        # Parallel analysis tasks
        tasks = [
            self._analyze_market_dynamics(),
            self._identify_opportunities(),
            self._assess_competitive_landscape(),
            self._analyze_value_chains(),
            self._predict_market_evolution(),
            self._identify_strategic_gaps()
        ]

        results = await asyncio.gather(*tasks)

        # Combine insights
        ecosystem_analysis = {
            "market_dynamics": results[0],
            "opportunities": results[1],
            "competitive_landscape": results[2],
            "value_chains": results[3],
            "market_predictions": results[4],
            "strategic_gaps": results[5],
            "ecosystem_health": await self._calculate_ecosystem_health(),
            "strategic_insights": await self._generate_strategic_insights(results),
            "action_plan": self._create_action_plan(results)
        }

        return ecosystem_analysis

    async def _analyze_market_dynamics(self) -> Dict[str, Any]:
        """Analyze market dynamics and trends"""

        # Fetch market data
        market_data = await self._fetch_market_data()

        # Analyze segments
        segment_analysis = {}
        for segment in MarketSegment:
            segment_data = market_data.get(segment.value, {})

            segment_analysis[segment.value] = {
                "size": segment_data.get("market_size", 0),
                "growth_rate": segment_data.get("growth_rate", 0),
                "deal_volume": segment_data.get("deal_volume", 0),
                "avg_deal_size": segment_data.get("avg_deal_size", 0),
                "key_trends": await self._identify_segment_trends(segment),
                "disruption_risk": self._assess_disruption_risk(segment_data),
                "consolidation_index": self._calculate_consolidation_index(segment_data),
                "entry_difficulty": self._assess_entry_difficulty(segment_data)
            }

        # Identify cross-segment opportunities
        cross_segment = await self._analyze_cross_segment_opportunities(segment_analysis)

        return {
            "segments": segment_analysis,
            "cross_segment_opportunities": cross_segment,
            "market_velocity": self._calculate_market_velocity(market_data),
            "liquidity_index": self._calculate_liquidity_index(market_data),
            "innovation_index": await self._calculate_innovation_index()
        }

    async def _identify_opportunities(self) -> List[MarketOpportunity]:
        """Identify market opportunities using AI"""

        opportunities = []

        # Analyze each segment for opportunities
        for segment in MarketSegment:
            segment_opportunities = await self._analyze_segment_opportunities(segment)
            opportunities.extend(segment_opportunities)

        # Score and rank opportunities
        scored_opportunities = []
        for opp in opportunities:
            score = await self.opportunity_scorer.score(opp)
            opp.confidence_score = score
            scored_opportunities.append(opp)

        # Sort by value potential * probability * confidence
        scored_opportunities.sort(
            key=lambda x: x.value_potential * x.probability * x.confidence_score,
            reverse=True
        )

        return scored_opportunities[:20]  # Top 20 opportunities

    async def _analyze_segment_opportunities(
        self,
        segment: MarketSegment
    ) -> List[MarketOpportunity]:
        """Analyze opportunities within a market segment"""

        opportunities = []

        # Consolidation opportunities
        if await self._is_fragmented_market(segment):
            opportunities.append(MarketOpportunity(
                opportunity_id=f"consolidation_{segment.value}_{datetime.utcnow().timestamp()}",
                type=OpportunityType.CONSOLIDATION,
                segment=segment,
                value_potential=await self._estimate_consolidation_value(segment),
                probability=0.7,
                time_horizon=24,
                key_players=await self._identify_consolidation_targets(segment),
                entry_barriers=["Capital requirements", "Integration complexity"],
                success_factors=["Operational synergies", "Market position"],
                risk_assessment={"execution": 0.3, "market": 0.2, "regulatory": 0.1},
                action_items=["Identify top 5 targets", "Assess synergies", "Secure funding"],
                confidence_score=0.0  # Will be scored
            ))

        # Disruption opportunities
        disruption_potential = await self._assess_disruption_potential(segment)
        if disruption_potential > 0.6:
            opportunities.append(MarketOpportunity(
                opportunity_id=f"disruption_{segment.value}_{datetime.utcnow().timestamp()}",
                type=OpportunityType.DISRUPTION,
                segment=segment,
                value_potential=await self._estimate_disruption_value(segment),
                probability=disruption_potential,
                time_horizon=36,
                key_players=await self._identify_incumbents(segment),
                entry_barriers=["Technology development", "Market education"],
                success_factors=["Innovation capability", "Speed to market"],
                risk_assessment={"technology": 0.4, "adoption": 0.3, "competition": 0.2},
                action_items=["Develop MVP", "Validate market fit", "Build team"],
                confidence_score=0.0
            ))

        # Partnership opportunities
        partnership_gaps = await self._identify_partnership_gaps(segment)
        for gap in partnership_gaps:
            opportunities.append(MarketOpportunity(
                opportunity_id=f"partnership_{segment.value}_{gap}_{datetime.utcnow().timestamp()}",
                type=OpportunityType.PARTNERSHIP,
                segment=segment,
                value_potential=await self._estimate_partnership_value(segment, gap),
                probability=0.6,
                time_horizon=12,
                key_players=await self._identify_partnership_candidates(segment, gap),
                entry_barriers=["Relationship building", "Alignment of interests"],
                success_factors=["Complementary capabilities", "Cultural fit"],
                risk_assessment={"alignment": 0.2, "execution": 0.2, "competition": 0.1},
                action_items=["Map potential partners", "Initiate discussions", "Pilot program"],
                confidence_score=0.0
            ))

        return opportunities

    async def _assess_competitive_landscape(self) -> Dict[str, Any]:
        """Assess competitive landscape"""

        competitors = await self._identify_competitors()

        competitive_analysis = {
            "market_concentration": await self._calculate_market_concentration(),
            "competitive_intensity": await self._assess_competitive_intensity(),
            "barriers_to_entry": await self._identify_entry_barriers(),
            "substitution_threats": await self._assess_substitution_threats(),
            "competitor_profiles": [],
            "competitive_advantages": await self._identify_competitive_advantages(),
            "competitive_gaps": await self._identify_competitive_gaps()
        }

        # Analyze each competitor
        for competitor in competitors[:10]:  # Top 10 competitors
            profile = await self._analyze_competitor(competitor)
            competitive_analysis["competitor_profiles"].append(profile)

        # Strategic positioning
        competitive_analysis["strategic_position"] = await self._determine_strategic_position(
            competitive_analysis
        )

        return competitive_analysis

    async def _analyze_value_chains(self) -> Dict[str, Any]:
        """Analyze value chains in the ecosystem"""

        value_chains = {}

        for segment in MarketSegment:
            chain = await self._map_value_chain(segment)

            value_chains[segment.value] = {
                "stages": chain["stages"],
                "key_players": chain["players"],
                "value_distribution": chain["value_distribution"],
                "integration_opportunities": await self._identify_integration_opportunities(chain),
                "bottlenecks": self._identify_bottlenecks(chain),
                "optimization_potential": self._calculate_optimization_potential(chain)
            }

        return {
            "chains": value_chains,
            "cross_chain_synergies": await self._identify_cross_chain_synergies(value_chains),
            "value_migration_patterns": await self._analyze_value_migration(),
            "future_value_pools": await self._predict_future_value_pools()
        }

    async def _predict_market_evolution(self) -> Dict[str, Any]:
        """Predict market evolution using ML"""

        # Load or train prediction model
        if "market_evolution" not in self.ml_models:
            self.ml_models["market_evolution"] = await self._train_evolution_model()

        predictions = {
            "market_size_forecast": {},
            "segment_growth_rates": {},
            "consolidation_timeline": {},
            "disruption_probability": {},
            "regulatory_changes": []
        }

        for segment in MarketSegment:
            # Predict market size
            predictions["market_size_forecast"][segment.value] = await self._predict_market_size(
                segment, [3, 6, 12, 24, 36]  # months
            )

            # Predict growth rates
            predictions["segment_growth_rates"][segment.value] = await self._predict_growth_rate(
                segment
            )

            # Predict consolidation
            predictions["consolidation_timeline"][segment.value] = await self._predict_consolidation(
                segment
            )

            # Predict disruption
            predictions["disruption_probability"][segment.value] = await self._predict_disruption(
                segment
            )

        # Predict regulatory changes
        predictions["regulatory_changes"] = await self._predict_regulatory_changes()

        return predictions

    async def _identify_strategic_gaps(self) -> List[Dict[str, Any]]:
        """Identify strategic gaps in the market"""

        gaps = []

        # Technology gaps
        tech_gaps = await self._identify_technology_gaps()
        for gap in tech_gaps:
            gaps.append({
                "type": "technology",
                "description": gap["description"],
                "market_need": gap["market_need"],
                "current_solutions": gap["current_solutions"],
                "opportunity_size": gap["opportunity_size"],
                "development_cost": gap["development_cost"],
                "time_to_market": gap["time_to_market"]
            })

        # Service gaps
        service_gaps = await self._identify_service_gaps()
        gaps.extend(service_gaps)

        # Geographic gaps
        geo_gaps = await self._identify_geographic_gaps()
        gaps.extend(geo_gaps)

        # Customer segment gaps
        segment_gaps = await self._identify_segment_gaps()
        gaps.extend(segment_gaps)

        return gaps

    async def _calculate_ecosystem_health(self) -> Dict[str, float]:
        """Calculate ecosystem health metrics"""

        health_metrics = {
            "liquidity": await self._calculate_liquidity_score(),
            "innovation": await self._calculate_innovation_score(),
            "stability": await self._calculate_stability_score(),
            "growth": await self._calculate_growth_score(),
            "diversity": await self._calculate_diversity_score(),
            "resilience": await self._calculate_resilience_score()
        }

        # Overall health score (weighted average)
        weights = {
            "liquidity": 0.2,
            "innovation": 0.2,
            "stability": 0.15,
            "growth": 0.25,
            "diversity": 0.1,
            "resilience": 0.1
        }

        overall_score = sum(
            health_metrics[metric] * weight
            for metric, weight in weights.items()
        )

        health_metrics["overall"] = overall_score

        return health_metrics

    async def _generate_strategic_insights(
        self,
        analysis_results: List[Dict]
    ) -> List[EcosystemInsight]:
        """Generate strategic insights from analysis"""

        insights = []

        # Market dynamics insights
        market_dynamics = analysis_results[0]

        # High-growth segment insight
        highest_growth = max(
            market_dynamics["segments"].items(),
            key=lambda x: x[1]["growth_rate"]
        )

        if highest_growth[1]["growth_rate"] > 0.2:
            insights.append(EcosystemInsight(
                category="Market Growth",
                insight=f"{highest_growth[0]} showing {highest_growth[1]['growth_rate']*100:.1f}% growth",
                impact="First-mover advantage in high-growth segment",
                opportunity_value=highest_growth[1]["size"] * 0.1,  # 10% market share target
                implementation_difficulty="Medium",
                time_to_value=180,
                confidence=0.85,
                supporting_data={"segment": highest_growth[0], "metrics": highest_growth[1]},
                recommendations=[
                    f"Prioritize {highest_growth[0]} segment entry",
                    "Build specialized expertise",
                    "Establish strategic partnerships"
                ]
            ))

        # Consolidation opportunity insight
        opportunities = analysis_results[1]
        consolidation_opps = [o for o in opportunities if o.type == OpportunityType.CONSOLIDATION]

        if consolidation_opps:
            best_consolidation = consolidation_opps[0]
            insights.append(EcosystemInsight(
                category="Consolidation",
                insight=f"Prime consolidation opportunity in {best_consolidation.segment.value}",
                impact=f"Potential £{best_consolidation.value_potential:.1f}M value creation",
                opportunity_value=best_consolidation.value_potential,
                implementation_difficulty="High",
                time_to_value=best_consolidation.time_horizon * 30,
                confidence=best_consolidation.confidence_score,
                supporting_data={"opportunity": best_consolidation.__dict__},
                recommendations=best_consolidation.action_items
            ))

        # Competitive advantage insight
        competitive_landscape = analysis_results[2]
        advantages = competitive_landscape.get("competitive_advantages", [])

        if advantages:
            insights.append(EcosystemInsight(
                category="Competitive Position",
                insight="Unique positioning through integrated ecosystem approach",
                impact="Sustainable competitive advantage",
                opportunity_value=50.0,  # £50M value from differentiation
                implementation_difficulty="Medium",
                time_to_value=90,
                confidence=0.8,
                supporting_data={"advantages": advantages},
                recommendations=[
                    "Strengthen ecosystem integration",
                    "Build network effects",
                    "Create switching costs"
                ]
            ))

        # Value chain insight
        value_chains = analysis_results[3]
        integration_opps = []
        for segment, chain in value_chains["chains"].items():
            integration_opps.extend(chain.get("integration_opportunities", []))

        if integration_opps:
            insights.append(EcosystemInsight(
                category="Value Chain",
                insight="Vertical integration opportunities identified",
                impact="Control critical value chain stages",
                opportunity_value=30.0,
                implementation_difficulty="High",
                time_to_value=365,
                confidence=0.75,
                supporting_data={"opportunities": integration_opps[:3]},
                recommendations=[
                    "Evaluate make vs. buy decisions",
                    "Assess integration risks",
                    "Plan phased integration"
                ]
            ))

        return insights

    def _create_action_plan(self, analysis_results: List[Dict]) -> Dict[str, Any]:
        """Create strategic action plan"""

        # Prioritize opportunities
        opportunities = analysis_results[1]
        top_opportunities = opportunities[:5]

        # Create phased plan
        action_plan = {
            "immediate": [],  # 0-30 days
            "short_term": [],  # 1-3 months
            "medium_term": [],  # 3-12 months
            "long_term": []  # 12+ months
        }

        for opp in top_opportunities:
            if opp.time_horizon <= 1:
                phase = "immediate"
            elif opp.time_horizon <= 3:
                phase = "short_term"
            elif opp.time_horizon <= 12:
                phase = "medium_term"
            else:
                phase = "long_term"

            action_plan[phase].append({
                "opportunity": opp.opportunity_id,
                "type": opp.type.value,
                "value": opp.value_potential,
                "actions": opp.action_items,
                "resources_required": self._estimate_resources(opp),
                "success_metrics": self._define_success_metrics(opp)
            })

        # Add strategic initiatives
        action_plan["strategic_initiatives"] = [
            {
                "initiative": "Build ecosystem intelligence capabilities",
                "priority": "High",
                "timeline": "Immediate",
                "investment": "£500K",
                "expected_return": "10x"
            },
            {
                "initiative": "Establish strategic partnerships",
                "priority": "High",
                "timeline": "Short-term",
                "investment": "£200K",
                "expected_return": "5x"
            },
            {
                "initiative": "Develop proprietary deal flow",
                "priority": "Medium",
                "timeline": "Medium-term",
                "investment": "£1M",
                "expected_return": "20x"
            }
        ]

        return action_plan

    async def _fetch_market_data(self) -> Dict[str, Any]:
        """Fetch market data from various sources"""

        # In production, this would aggregate data from multiple sources
        # For now, return simulated data

        market_data = {}

        for segment in MarketSegment:
            market_data[segment.value] = {
                "market_size": np.random.uniform(10, 100) * 1000,  # £ millions
                "growth_rate": np.random.uniform(0.05, 0.3),
                "deal_volume": np.random.randint(50, 500),
                "avg_deal_size": np.random.uniform(1, 50),
                "market_cap": np.random.uniform(100, 1000) * 1000
            }

        return market_data

    async def _identify_segment_trends(self, segment: MarketSegment) -> List[str]:
        """Identify trends in market segment"""

        trends = []

        # Technology trends
        if segment == MarketSegment.TECHNOLOGY:
            trends = [
                "AI/ML integration driving valuations",
                "SaaS consolidation accelerating",
                "Cybersecurity premium increasing"
            ]
        elif segment == MarketSegment.HEALTHCARE:
            trends = [
                "Digital health transformation",
                "Regulatory changes driving consolidation",
                "Value-based care models emerging"
            ]
        # Add more segment-specific trends

        return trends

    def _assess_disruption_risk(self, segment_data: Dict) -> float:
        """Assess disruption risk for segment"""

        # Factors indicating disruption risk
        factors = {
            "high_margins": segment_data.get("avg_margins", 0) > 0.3,
            "low_innovation": segment_data.get("innovation_rate", 1) < 0.1,
            "customer_dissatisfaction": segment_data.get("nps", 50) < 30,
            "regulatory_pressure": segment_data.get("regulatory_changes", 0) > 2,
            "new_entrants": segment_data.get("new_entrants", 0) > 5
        }

        risk_score = sum(factors.values()) / len(factors)
        return risk_score

    def _calculate_consolidation_index(self, segment_data: Dict) -> float:
        """Calculate consolidation index for segment"""

        # Herfindahl-Hirschman Index calculation
        market_shares = segment_data.get("market_shares", [])

        if not market_shares:
            return 0.5  # Default medium concentration

        hhi = sum(share ** 2 for share in market_shares)

        # Normalize to 0-1 scale
        return min(hhi / 10000, 1.0)

    def _assess_entry_difficulty(self, segment_data: Dict) -> str:
        """Assess difficulty of market entry"""

        barriers = 0

        # Check various barriers
        if segment_data.get("capital_requirements", 0) > 10:  # £10M
            barriers += 2
        if segment_data.get("regulatory_requirements", 0) > 3:
            barriers += 2
        if segment_data.get("market_concentration", 0) > 0.7:
            barriers += 1
        if segment_data.get("brand_importance", 0) > 0.8:
            barriers += 1

        if barriers >= 4:
            return "High"
        elif barriers >= 2:
            return "Medium"
        else:
            return "Low"

    async def _analyze_cross_segment_opportunities(
        self,
        segment_analysis: Dict
    ) -> List[Dict[str, Any]]:
        """Analyze opportunities across segments"""

        opportunities = []

        # Find complementary segments
        for seg1 in MarketSegment:
            for seg2 in MarketSegment:
                if seg1 != seg2:
                    synergy = self._calculate_segment_synergy(
                        segment_analysis.get(seg1.value, {}),
                        segment_analysis.get(seg2.value, {})
                    )

                    if synergy > 0.7:
                        opportunities.append({
                            "segments": [seg1.value, seg2.value],
                            "synergy_score": synergy,
                            "opportunity_type": "cross-segment integration",
                            "value_potential": synergy * 100  # £M
                        })

        return opportunities

    def _calculate_segment_synergy(self, seg1_data: Dict, seg2_data: Dict) -> float:
        """Calculate synergy between segments"""

        # Simplified synergy calculation
        synergy_factors = []

        # Growth synergy
        growth_diff = abs(seg1_data.get("growth_rate", 0) - seg2_data.get("growth_rate", 0))
        synergy_factors.append(1 - growth_diff)

        # Size compatibility
        size_ratio = min(seg1_data.get("size", 1), seg2_data.get("size", 1)) / \
                    max(seg1_data.get("size", 1), seg2_data.get("size", 1))
        synergy_factors.append(size_ratio)

        return sum(synergy_factors) / len(synergy_factors)

    def _calculate_market_velocity(self, market_data: Dict) -> float:
        """Calculate market velocity (deal flow speed)"""

        total_deals = sum(d.get("deal_volume", 0) for d in market_data.values())
        avg_time_to_close = 90  # days, assumed

        # Velocity = deals per day
        velocity = total_deals / 365
        return velocity

    def _calculate_liquidity_index(self, market_data: Dict) -> float:
        """Calculate market liquidity index"""

        total_volume = sum(
            d.get("deal_volume", 0) * d.get("avg_deal_size", 0)
            for d in market_data.values()
        )

        total_market_cap = sum(d.get("market_cap", 0) for d in market_data.values())

        if total_market_cap > 0:
            return total_volume / total_market_cap
        return 0

    async def _calculate_innovation_index(self) -> float:
        """Calculate ecosystem innovation index"""

        # Factors for innovation
        patent_filings = 1000  # Example
        rd_spending = 0.15  # 15% of revenue
        startup_density = 50  # per 100k companies
        vc_investment = 1000  # £M

        # Weighted innovation score
        innovation_score = (
            (patent_filings / 10000) * 0.2 +
            rd_spending * 0.3 +
            (startup_density / 100) * 0.25 +
            (vc_investment / 5000) * 0.25
        )

        return min(innovation_score, 1.0)

    async def _is_fragmented_market(self, segment: MarketSegment) -> bool:
        """Check if market is fragmented"""

        # Get market concentration
        concentration = await self._get_market_concentration(segment)

        # Fragmented if HHI < 1500
        return concentration < 0.15

    async def _estimate_consolidation_value(self, segment: MarketSegment) -> float:
        """Estimate value from consolidation"""

        market_size = await self._get_segment_market_size(segment)
        fragmentation = await self._get_fragmentation_level(segment)

        # Higher fragmentation = higher consolidation value
        consolidation_value = market_size * fragmentation * 0.3  # 30% value capture

        return consolidation_value

    async def _identify_consolidation_targets(self, segment: MarketSegment) -> List[str]:
        """Identify potential consolidation targets"""

        # In production, would query real company data
        targets = [
            f"{segment.value}_company_1",
            f"{segment.value}_company_2",
            f"{segment.value}_company_3",
            f"{segment.value}_company_4",
            f"{segment.value}_company_5"
        ]

        return targets

    async def _assess_disruption_potential(self, segment: MarketSegment) -> float:
        """Assess potential for disruption"""

        factors = {
            "technology_change": 0.3,
            "customer_dissatisfaction": 0.2,
            "regulatory_change": 0.1,
            "new_business_models": 0.2,
            "capital_availability": 0.2
        }

        # Segment-specific adjustments
        if segment == MarketSegment.TECHNOLOGY:
            factors["technology_change"] = 0.8
        elif segment == MarketSegment.FINANCE:
            factors["regulatory_change"] = 0.5

        disruption_score = sum(factors.values()) / len(factors)
        return disruption_score

    async def _estimate_disruption_value(self, segment: MarketSegment) -> float:
        """Estimate value from disruption"""

        market_size = await self._get_segment_market_size(segment)
        incumbent_inefficiency = 0.4  # 40% inefficiency assumed

        disruption_value = market_size * incumbent_inefficiency * 0.2  # 20% capture

        return disruption_value

    async def _identify_incumbents(self, segment: MarketSegment) -> List[str]:
        """Identify incumbent players"""

        # In production, would query real data
        return [f"{segment.value}_incumbent_{i}" for i in range(1, 6)]

    async def _identify_partnership_gaps(self, segment: MarketSegment) -> List[str]:
        """Identify partnership gaps in segment"""

        gaps = []

        # Common partnership gaps
        if segment == MarketSegment.TECHNOLOGY:
            gaps = ["distribution", "enterprise_sales", "integration"]
        elif segment == MarketSegment.HEALTHCARE:
            gaps = ["regulatory", "clinical_validation", "payer_relationships"]
        else:
            gaps = ["market_access", "technology", "operations"]

        return gaps

    async def _estimate_partnership_value(self, segment: MarketSegment, gap: str) -> float:
        """Estimate value from partnership"""

        base_value = 10.0  # £10M base

        # Adjust by gap type
        multipliers = {
            "distribution": 3.0,
            "technology": 2.5,
            "market_access": 2.0,
            "regulatory": 1.5,
            "operations": 1.2
        }

        multiplier = multipliers.get(gap, 1.0)

        return base_value * multiplier

    async def _identify_partnership_candidates(
        self,
        segment: MarketSegment,
        gap: str
    ) -> List[str]:
        """Identify partnership candidates"""

        # In production, would use real matching algorithm
        return [f"{segment.value}_{gap}_partner_{i}" for i in range(1, 4)]

    async def _get_market_concentration(self, segment: MarketSegment) -> float:
        """Get market concentration for segment"""

        # Simulated - in production would calculate from real data
        return np.random.uniform(0.1, 0.8)

    async def _get_segment_market_size(self, segment: MarketSegment) -> float:
        """Get market size for segment"""

        # Simulated - in production would fetch real data
        sizes = {
            MarketSegment.TECHNOLOGY: 500000,  # £500B
            MarketSegment.HEALTHCARE: 300000,
            MarketSegment.FINANCE: 800000,
            MarketSegment.MANUFACTURING: 200000,
            MarketSegment.RETAIL: 150000,
            MarketSegment.SERVICES: 100000,
            MarketSegment.REAL_ESTATE: 400000,
            MarketSegment.ENERGY: 250000
        }

        return sizes.get(segment, 100000)

    async def _get_fragmentation_level(self, segment: MarketSegment) -> float:
        """Get market fragmentation level"""

        concentration = await self._get_market_concentration(segment)
        return 1 - concentration

    async def _identify_competitors(self) -> List[Dict[str, Any]]:
        """Identify main competitors"""

        # In production, would query competitor database
        competitors = [
            {"name": "DealCo", "market_share": 0.15, "strength": "Deal flow"},
            {"name": "M&A Plus", "market_share": 0.12, "strength": "Analytics"},
            {"name": "AcquireHub", "market_share": 0.10, "strength": "Network"},
            {"name": "DealMakers", "market_share": 0.08, "strength": "Advisors"},
            {"name": "ExitStrategy", "market_share": 0.06, "strength": "Valuation"}
        ]

        return competitors

    def _estimate_resources(self, opportunity: MarketOpportunity) -> Dict[str, Any]:
        """Estimate resources required for opportunity"""

        return {
            "capital": opportunity.value_potential * 0.2,  # 20% of value as investment
            "team_size": max(3, int(opportunity.value_potential / 10)),
            "expertise": ["M&A", "Integration", "Operations"],
            "timeline": f"{opportunity.time_horizon} months"
        }

    def _define_success_metrics(self, opportunity: MarketOpportunity) -> List[str]:
        """Define success metrics for opportunity"""

        base_metrics = [
            "ROI > 3x",
            f"Completion within {opportunity.time_horizon} months",
            "Integration success > 80%"
        ]

        if opportunity.type == OpportunityType.ACQUISITION:
            base_metrics.append("Retention of key talent > 90%")
        elif opportunity.type == OpportunityType.PARTNERSHIP:
            base_metrics.append("Revenue share achieved > target")

        return base_metrics


class OpportunityScorer:
    """ML-based opportunity scoring"""

    def __init__(self):
        self.model = None
        self.feature_importance = {}

    async def score(self, opportunity: MarketOpportunity) -> float:
        """Score opportunity using ML model"""

        # Extract features
        features = self._extract_features(opportunity)

        # Simple scoring formula (in production would use trained ML model)
        score = (
            opportunity.probability * 0.3 +
            min(opportunity.value_potential / 100, 1.0) * 0.3 +
            (1.0 / max(opportunity.time_horizon, 1)) * 0.2 +
            (1 - len(opportunity.entry_barriers) / 10) * 0.1 +
            (len(opportunity.success_factors) / 10) * 0.1
        )

        return min(score, 1.0)

    def _extract_features(self, opportunity: MarketOpportunity) -> np.ndarray:
        """Extract features from opportunity"""

        features = [
            opportunity.value_potential,
            opportunity.probability,
            opportunity.time_horizon,
            len(opportunity.key_players),
            len(opportunity.entry_barriers),
            len(opportunity.success_factors),
            sum(opportunity.risk_assessment.values())
        ]

        return np.array(features)


class MarketTrendAnalyzer:
    """Analyze market trends using time series analysis"""

    async def analyze_trends(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market trends"""

        trends = {
            "growth_trends": self._analyze_growth_trends(market_data),
            "cyclical_patterns": self._identify_cycles(market_data),
            "momentum_indicators": self._calculate_momentum(market_data),
            "inflection_points": self._identify_inflection_points(market_data)
        }

        return trends

    def _analyze_growth_trends(self, data: pd.DataFrame) -> Dict[str, float]:
        """Analyze growth trends"""

        # Calculate compound annual growth rate (CAGR)
        if len(data) < 2:
            return {"cagr": 0}

        start_value = data.iloc[0]["value"]
        end_value = data.iloc[-1]["value"]
        years = len(data) / 12  # Assuming monthly data

        if start_value > 0 and years > 0:
            cagr = (end_value / start_value) ** (1 / years) - 1
        else:
            cagr = 0

        return {
            "cagr": cagr,
            "trend_direction": "up" if cagr > 0 else "down",
            "trend_strength": abs(cagr)
        }

    def _identify_cycles(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Identify cyclical patterns"""

        # Simplified cycle detection
        # In production would use FFT or other signal processing

        return {
            "cycle_length": 12,  # months
            "amplitude": 0.1,
            "phase": "expansion"
        }

    def _calculate_momentum(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate momentum indicators"""

        if len(data) < 2:
            return {"momentum": 0}

        # Simple momentum calculation
        recent_growth = (data.iloc[-1]["value"] - data.iloc[-6]["value"]) / data.iloc[-6]["value"] \
                       if len(data) >= 6 else 0

        return {
            "momentum": recent_growth,
            "acceleration": 0  # Would calculate second derivative
        }

    def _identify_inflection_points(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify market inflection points"""

        inflection_points = []

        # Simplified inflection detection
        # In production would use more sophisticated methods

        return inflection_points


class EcosystemNetworkAnalyzer:
    """Analyze ecosystem network relationships"""

    def __init__(self):
        self.network = nx.DiGraph()

    async def analyze_network(self, entities: List[Dict]) -> Dict[str, Any]:
        """Analyze ecosystem network"""

        # Build network
        self._build_network(entities)

        analysis = {
            "network_metrics": self._calculate_network_metrics(),
            "key_players": self._identify_key_players(),
            "communities": self._detect_communities(),
            "influence_paths": self._analyze_influence_paths(),
            "network_vulnerabilities": self._identify_vulnerabilities()
        }

        return analysis

    def _build_network(self, entities: List[Dict]) -> None:
        """Build network graph from entities"""

        for entity in entities:
            self.network.add_node(entity["id"], **entity)

            for connection in entity.get("connections", []):
                self.network.add_edge(
                    entity["id"],
                    connection["target"],
                    weight=connection.get("strength", 1.0)
                )

    def _calculate_network_metrics(self) -> Dict[str, float]:
        """Calculate network metrics"""

        if self.network.number_of_nodes() == 0:
            return {}

        return {
            "density": nx.density(self.network),
            "avg_degree": sum(dict(self.network.degree()).values()) / self.network.number_of_nodes(),
            "clustering_coefficient": nx.average_clustering(self.network.to_undirected()),
            "avg_path_length": nx.average_shortest_path_length(self.network) if nx.is_connected(self.network.to_undirected()) else 0
        }

    def _identify_key_players(self) -> List[Dict[str, Any]]:
        """Identify key players in network"""

        if self.network.number_of_nodes() == 0:
            return []

        # Calculate centrality measures
        degree_centrality = nx.degree_centrality(self.network)
        betweenness_centrality = nx.betweenness_centrality(self.network)
        eigenvector_centrality = nx.eigenvector_centrality(self.network, max_iter=1000)

        key_players = []

        for node in self.network.nodes():
            influence_score = (
                degree_centrality.get(node, 0) * 0.3 +
                betweenness_centrality.get(node, 0) * 0.4 +
                eigenvector_centrality.get(node, 0) * 0.3
            )

            key_players.append({
                "entity": node,
                "influence_score": influence_score,
                "degree_centrality": degree_centrality.get(node, 0),
                "betweenness_centrality": betweenness_centrality.get(node, 0),
                "eigenvector_centrality": eigenvector_centrality.get(node, 0)
            })

        return sorted(key_players, key=lambda x: x["influence_score"], reverse=True)[:10]

    def _detect_communities(self) -> List[List[str]]:
        """Detect communities in network"""

        if self.network.number_of_nodes() == 0:
            return []

        # Use Louvain method for community detection
        communities = nx.community.greedy_modularity_communities(self.network.to_undirected())

        return [list(community) for community in communities]

    def _analyze_influence_paths(self) -> Dict[str, Any]:
        """Analyze influence propagation paths"""

        # Simplified influence analysis
        return {
            "max_influence_distance": 3,
            "influence_decay": 0.5,
            "critical_paths": []
        }

    def _identify_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Identify network vulnerabilities"""

        vulnerabilities = []

        # Check for single points of failure
        articulation_points = list(nx.articulation_points(self.network.to_undirected()))

        for point in articulation_points:
            vulnerabilities.append({
                "type": "single_point_of_failure",
                "entity": point,
                "impact": "high",
                "recommendation": f"Reduce dependency on {point}"
            })

        return vulnerabilities