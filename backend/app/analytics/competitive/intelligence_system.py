"""
Competitive Intelligence System
Advanced competitive monitoring and strategic move prediction
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import aiohttp
import json
import yfinance as yf
from textblob import TextBlob
import re
from collections import defaultdict

from app.core.config import settings
from app.core.database import get_database
from app.analytics import ADVANCED_ANALYTICS_CONFIG

logger = logging.getLogger(__name__)

class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CompetitiveAction(str, Enum):
    ACQUISITION = "acquisition"
    PARTNERSHIP = "partnership"
    PRODUCT_LAUNCH = "product_launch"
    MARKET_ENTRY = "market_entry"
    PRICE_CHANGE = "price_change"
    FUNDING_ROUND = "funding_round"

class StrategicResponse(str, Enum):
    AGGRESSIVE_COUNTER = "aggressive_counter"
    DEFENSIVE_POSITION = "defensive_position"
    DIFFERENTIATE = "differentiate"
    MONITOR_AND_WAIT = "monitor_and_wait"
    STRATEGIC_PARTNERSHIP = "strategic_partnership"

@dataclass
class CompetitorProfile:
    competitor_id: str
    company_name: str
    market_cap: float
    revenue: float
    growth_rate: float
    market_share: float
    competitive_strengths: List[str]
    competitive_weaknesses: List[str]
    recent_moves: List[Dict[str, Any]]
    financial_health_score: float
    innovation_index: float
    acquisition_activity_score: float
    strategic_focus: List[str]

@dataclass
class CompetitiveMove:
    move_id: str
    competitor_name: str
    action_type: CompetitiveAction
    description: str
    announcement_date: datetime
    estimated_impact: float
    threat_level: ThreatLevel
    affected_market_segments: List[str]
    strategic_rationale: str
    our_response_options: List[Dict[str, Any]]
    monitoring_priority: int

@dataclass
class MarketShareAnalysis:
    total_market_size: float
    our_market_share: float
    our_market_position: int
    top_competitors: List[Dict[str, Any]]
    market_share_trends: Dict[str, float]
    competitive_gaps: List[str]
    growth_opportunities: List[str]
    defensive_priorities: List[str]

@dataclass
class ThreatAssessment:
    threat_id: str
    threat_type: str
    threat_level: ThreatLevel
    likelihood: float
    potential_impact: float
    time_horizon: str
    description: str
    indicators: List[str]
    mitigation_strategies: List[str]
    monitoring_metrics: List[str]

@dataclass
class CompetitiveIntelligenceReport:
    generated_at: datetime
    market_overview: Dict[str, Any]
    competitor_profiles: List[CompetitorProfile]
    recent_competitive_moves: List[CompetitiveMove]
    market_share_analysis: MarketShareAnalysis
    threat_assessments: List[ThreatAssessment]
    strategic_recommendations: List[str]
    competitive_positioning: Dict[str, Any]
    market_predictions: Dict[str, Any]
    action_items: List[Dict[str, Any]]

class CompetitorMonitor:
    """Monitor competitor activities and strategic moves"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["market_intelligence"]

    async def monitor_competitor_activities(
        self,
        competitors: List[str],
        monitoring_period_days: int = 30
    ) -> List[CompetitiveMove]:
        """Monitor recent competitor activities and strategic moves"""
        try:
            competitive_moves = []

            for competitor in competitors:
                # Gather competitive intelligence data
                moves = await self._gather_competitor_data(competitor, monitoring_period_days)
                competitive_moves.extend(moves)

            # Sort by significance and recency
            competitive_moves.sort(key=lambda x: (x.threat_level.value, x.announcement_date), reverse=True)

            return competitive_moves

        except Exception as e:
            logger.error(f"Error monitoring competitor activities: {e}")
            raise

    async def _gather_competitor_data(self, competitor: str, days: int) -> List[CompetitiveMove]:
        """Gather competitive intelligence data for a specific competitor"""
        # Mock data - would integrate with news APIs, SEC filings, etc.
        mock_moves = [
            {
                "move_id": f"move_{competitor.lower().replace(' ', '_')}_001",
                "competitor_name": competitor,
                "action_type": CompetitiveAction.ACQUISITION,
                "description": f"{competitor} acquires AI startup for $150M to strengthen technology capabilities",
                "announcement_date": datetime.now() - timedelta(days=5),
                "estimated_impact": 0.15,
                "threat_level": ThreatLevel.HIGH,
                "affected_market_segments": ["artificial_intelligence", "automation"],
                "strategic_rationale": "Technology acquisition to enhance competitive position",
                "our_response_options": [
                    {
                        "response": "accelerate_internal_ai_development",
                        "timeline": "6_months",
                        "estimated_cost": 5_000_000,
                        "probability_success": 0.7
                    },
                    {
                        "response": "acquire_competing_ai_company",
                        "timeline": "3_months",
                        "estimated_cost": 200_000_000,
                        "probability_success": 0.8
                    }
                ],
                "monitoring_priority": 1
            },
            {
                "move_id": f"move_{competitor.lower().replace(' ', '_')}_002",
                "competitor_name": competitor,
                "action_type": CompetitiveAction.PARTNERSHIP,
                "description": f"{competitor} forms strategic partnership with major cloud provider",
                "announcement_date": datetime.now() - timedelta(days=12),
                "estimated_impact": 0.08,
                "threat_level": ThreatLevel.MEDIUM,
                "affected_market_segments": ["cloud_services", "enterprise_software"],
                "strategic_rationale": "Expand distribution channels and technical capabilities",
                "our_response_options": [
                    {
                        "response": "strengthen_existing_partnerships",
                        "timeline": "2_months",
                        "estimated_cost": 1_000_000,
                        "probability_success": 0.9
                    }
                ],
                "monitoring_priority": 2
            }
        ]

        moves = []
        for move_data in mock_moves:
            move = CompetitiveMove(**move_data)
            moves.append(move)

        return moves

    async def predict_competitor_moves(
        self,
        competitor_profiles: List[CompetitorProfile]
    ) -> List[Dict[str, Any]]:
        """Predict likely future moves by competitors"""
        predictions = []

        for competitor in competitor_profiles:
            # Analyze patterns and predict moves
            predicted_moves = await self._analyze_competitor_patterns(competitor)
            predictions.extend(predicted_moves)

        return sorted(predictions, key=lambda x: x["probability"], reverse=True)

    async def _analyze_competitor_patterns(self, competitor: CompetitorProfile) -> List[Dict[str, Any]]:
        """Analyze competitor patterns to predict future moves"""
        predictions = []

        # High acquisition activity score suggests more acquisitions
        if competitor.acquisition_activity_score > 0.7:
            predictions.append({
                "competitor": competitor.company_name,
                "predicted_action": "acquisition",
                "probability": 0.75,
                "timeframe": "next_6_months",
                "rationale": "High historical acquisition activity indicates likely continued M&A strategy",
                "potential_targets": ["AI startups", "Complementary technology companies"]
            })

        # High innovation index with market share pressure
        if competitor.innovation_index > 0.8 and competitor.market_share < 0.15:
            predictions.append({
                "competitor": competitor.company_name,
                "predicted_action": "product_launch",
                "probability": 0.65,
                "timeframe": "next_3_months",
                "rationale": "Strong innovation capabilities with need for market share growth",
                "potential_impact": "moderate_to_high"
            })

        return predictions

class StrategicPositioningAnalyzer:
    """Analyze competitive positioning and recommend strategic responses"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["market_intelligence"]

    async def analyze_competitive_positioning(
        self,
        our_company_data: Dict[str, Any],
        competitor_data: List[CompetitorProfile]
    ) -> Dict[str, Any]:
        """Analyze competitive positioning across multiple dimensions"""
        try:
            # Perform competitive analysis across key dimensions
            positioning_analysis = {
                "market_position": await self._analyze_market_position(our_company_data, competitor_data),
                "competitive_advantages": await self._identify_competitive_advantages(our_company_data, competitor_data),
                "competitive_gaps": await self._identify_competitive_gaps(our_company_data, competitor_data),
                "differentiation_opportunities": await self._find_differentiation_opportunities(competitor_data),
                "strategic_positioning_map": await self._create_positioning_map(our_company_data, competitor_data)
            }

            return positioning_analysis

        except Exception as e:
            logger.error(f"Error analyzing competitive positioning: {e}")
            raise

    async def _analyze_market_position(
        self,
        our_data: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> Dict[str, Any]:
        """Analyze our market position relative to competitors"""
        # Sort competitors by market share
        sorted_competitors = sorted(competitors, key=lambda x: x.market_share, reverse=True)

        our_market_share = our_data.get("market_share", 0.12)
        our_position = 1

        for i, competitor in enumerate(sorted_competitors):
            if competitor.market_share > our_market_share:
                our_position = i + 2  # +2 because we're behind this competitor

        return {
            "market_position": our_position,
            "market_share": our_market_share,
            "market_leader": sorted_competitors[0].company_name if sorted_competitors else "Unknown",
            "gap_to_leader": sorted_competitors[0].market_share - our_market_share if sorted_competitors else 0,
            "closest_competitor": self._find_closest_competitor(our_market_share, sorted_competitors)
        }

    def _find_closest_competitor(self, our_share: float, competitors: List[CompetitorProfile]) -> str:
        """Find the competitor closest to our market share"""
        closest_competitor = None
        smallest_gap = float('inf')

        for competitor in competitors:
            gap = abs(competitor.market_share - our_share)
            if gap < smallest_gap:
                smallest_gap = gap
                closest_competitor = competitor.company_name

        return closest_competitor or "Unknown"

    async def _identify_competitive_advantages(
        self,
        our_data: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> List[str]:
        """Identify our competitive advantages"""
        advantages = []

        our_strengths = set(our_data.get("competitive_strengths", []))

        # Find unique strengths
        competitor_strengths = set()
        for competitor in competitors:
            competitor_strengths.update(competitor.competitive_strengths)

        unique_strengths = our_strengths - competitor_strengths
        advantages.extend(list(unique_strengths))

        # Add performance-based advantages
        our_growth = our_data.get("growth_rate", 0.1)
        avg_competitor_growth = np.mean([c.growth_rate for c in competitors]) if competitors else 0

        if our_growth > avg_competitor_growth * 1.2:
            advantages.append("Superior growth rate performance")

        our_innovation = our_data.get("innovation_index", 0.6)
        avg_competitor_innovation = np.mean([c.innovation_index for c in competitors]) if competitors else 0

        if our_innovation > avg_competitor_innovation * 1.1:
            advantages.append("Higher innovation capability")

        return advantages

    async def _identify_competitive_gaps(
        self,
        our_data: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> List[str]:
        """Identify competitive gaps we need to address"""
        gaps = []

        # Find common competitor strengths we lack
        our_strengths = set(our_data.get("competitive_strengths", []))
        competitor_strengths = defaultdict(int)

        for competitor in competitors:
            for strength in competitor.competitive_strengths:
                if strength not in our_strengths:
                    competitor_strengths[strength] += 1

        # Gaps present in majority of competitors
        majority_threshold = len(competitors) // 2
        for strength, count in competitor_strengths.items():
            if count >= majority_threshold:
                gaps.append(f"Lack of {strength} relative to competitors")

        return gaps

    async def _find_differentiation_opportunities(
        self,
        competitors: List[CompetitorProfile]
    ) -> List[str]:
        """Find opportunities for differentiation"""
        opportunities = []

        # Analyze competitor weaknesses
        all_weaknesses = []
        for competitor in competitors:
            all_weaknesses.extend(competitor.competitive_weaknesses)

        # Common weaknesses across competitors
        weakness_counts = defaultdict(int)
        for weakness in all_weaknesses:
            weakness_counts[weakness] += 1

        # Opportunities where many competitors are weak
        for weakness, count in weakness_counts.items():
            if count >= len(competitors) // 2:  # Majority have this weakness
                opportunities.append(f"Opportunity to excel in {weakness}")

        return opportunities

    async def _create_positioning_map(
        self,
        our_data: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> Dict[str, Any]:
        """Create strategic positioning map"""
        # Simplified positioning map based on market share vs growth rate
        positioning_data = {
            "our_position": {
                "market_share": our_data.get("market_share", 0.12),
                "growth_rate": our_data.get("growth_rate", 0.15),
                "quadrant": self._determine_quadrant(
                    our_data.get("market_share", 0.12),
                    our_data.get("growth_rate", 0.15)
                )
            },
            "competitors": [
                {
                    "name": comp.company_name,
                    "market_share": comp.market_share,
                    "growth_rate": comp.growth_rate,
                    "quadrant": self._determine_quadrant(comp.market_share, comp.growth_rate)
                }
                for comp in competitors
            ]
        }

        return positioning_data

    def _determine_quadrant(self, market_share: float, growth_rate: float) -> str:
        """Determine strategic quadrant based on market share and growth"""
        avg_share = 0.15  # Threshold for high/low market share
        avg_growth = 0.12  # Threshold for high/low growth

        if market_share >= avg_share and growth_rate >= avg_growth:
            return "market_leaders"
        elif market_share < avg_share and growth_rate >= avg_growth:
            return "rising_stars"
        elif market_share >= avg_share and growth_rate < avg_growth:
            return "cash_cows"
        else:
            return "laggards"

class CompetitiveResponseOptimizer:
    """Optimize strategic responses to competitive threats"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["market_intelligence"]

    async def recommend_strategic_responses(
        self,
        competitive_threats: List[ThreatAssessment],
        our_capabilities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recommend optimal strategic responses to competitive threats"""
        try:
            responses = []

            for threat in competitive_threats:
                response_options = await self._generate_response_options(threat, our_capabilities)
                optimal_response = await self._select_optimal_response(response_options, threat)
                responses.append(optimal_response)

            return sorted(responses, key=lambda x: x["priority"], reverse=True)

        except Exception as e:
            logger.error(f"Error recommending strategic responses: {e}")
            raise

    async def _generate_response_options(
        self,
        threat: ThreatAssessment,
        our_capabilities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate response options for a specific threat"""
        options = []

        # Aggressive counter-move
        if our_capabilities.get("financial_strength", 0.5) > 0.7:
            options.append({
                "response_type": StrategicResponse.AGGRESSIVE_COUNTER.value,
                "description": "Launch aggressive competitive counter-move",
                "estimated_cost": threat.potential_impact * 1000000 * 2,  # 2x threat impact
                "timeline": "3_months",
                "success_probability": 0.6,
                "risk_level": "high"
            })

        # Defensive positioning
        options.append({
            "response_type": StrategicResponse.DEFENSIVE_POSITION.value,
            "description": "Strengthen defensive position and protect market share",
            "estimated_cost": threat.potential_impact * 1000000 * 0.8,
            "timeline": "2_months",
            "success_probability": 0.8,
            "risk_level": "medium"
        })

        # Differentiation strategy
        if our_capabilities.get("innovation_capability", 0.5) > 0.6:
            options.append({
                "response_type": StrategicResponse.DIFFERENTIATE.value,
                "description": "Differentiate offering to reduce competitive pressure",
                "estimated_cost": threat.potential_impact * 1000000 * 1.2,
                "timeline": "6_months",
                "success_probability": 0.7,
                "risk_level": "medium"
            })

        # Strategic partnership
        options.append({
            "response_type": StrategicResponse.STRATEGIC_PARTNERSHIP.value,
            "description": "Form strategic partnership to counter threat",
            "estimated_cost": threat.potential_impact * 1000000 * 0.5,
            "timeline": "4_months",
            "success_probability": 0.65,
            "risk_level": "low"
        })

        # Monitor and wait
        options.append({
            "response_type": StrategicResponse.MONITOR_AND_WAIT.value,
            "description": "Monitor threat development and prepare contingent responses",
            "estimated_cost": threat.potential_impact * 1000000 * 0.1,
            "timeline": "ongoing",
            "success_probability": 0.5,
            "risk_level": "low"
        })

        return options

    async def _select_optimal_response(
        self,
        options: List[Dict[str, Any]],
        threat: ThreatAssessment
    ) -> Dict[str, Any]:
        """Select optimal response based on threat characteristics"""
        # Score each option
        for option in options:
            score = (
                option["success_probability"] * 0.4 +
                (1 - self._normalize_cost(option["estimated_cost"])) * 0.3 +
                self._risk_adjustment(option["risk_level"]) * 0.3
            )
            option["optimization_score"] = score

        # Select best option
        optimal_option = max(options, key=lambda x: x["optimization_score"])

        return {
            "threat_id": threat.threat_id,
            "recommended_response": optimal_option["response_type"],
            "rationale": optimal_option["description"],
            "estimated_cost": optimal_option["estimated_cost"],
            "timeline": optimal_option["timeline"],
            "success_probability": optimal_option["success_probability"],
            "priority": self._calculate_priority(threat, optimal_option),
            "key_success_factors": self._identify_success_factors(optimal_option),
            "risk_mitigation": self._suggest_risk_mitigation(optimal_option)
        }

    def _normalize_cost(self, cost: float) -> float:
        """Normalize cost to 0-1 scale"""
        max_cost = 100_000_000  # $100M reference point
        return min(1.0, cost / max_cost)

    def _risk_adjustment(self, risk_level: str) -> float:
        """Convert risk level to numeric adjustment"""
        risk_scores = {
            "low": 0.9,
            "medium": 0.7,
            "high": 0.5
        }
        return risk_scores.get(risk_level, 0.7)

    def _calculate_priority(self, threat: ThreatAssessment, response: Dict[str, Any]) -> int:
        """Calculate response priority (1-5 scale)"""
        threat_urgency = {
            ThreatLevel.CRITICAL: 5,
            ThreatLevel.HIGH: 4,
            ThreatLevel.MEDIUM: 3,
            ThreatLevel.LOW: 2
        }

        base_priority = threat_urgency.get(threat.threat_level, 3)

        # Adjust based on success probability
        if response["success_probability"] > 0.8:
            base_priority += 1
        elif response["success_probability"] < 0.5:
            base_priority -= 1

        return max(1, min(5, base_priority))

    def _identify_success_factors(self, response: Dict[str, Any]) -> List[str]:
        """Identify key success factors for the response"""
        factors = [
            "Strong leadership commitment",
            "Adequate resource allocation",
            "Clear execution timeline",
            "Effective stakeholder communication"
        ]

        response_type = response["response_type"]
        if response_type == "aggressive_counter":
            factors.extend(["Competitive intelligence", "Speed of execution"])
        elif response_type == "differentiate":
            factors.extend(["Innovation capability", "Market understanding"])
        elif response_type == "strategic_partnership":
            factors.extend(["Partner alignment", "Integration planning"])

        return factors

    def _suggest_risk_mitigation(self, response: Dict[str, Any]) -> List[str]:
        """Suggest risk mitigation strategies"""
        mitigation_strategies = [
            "Regular progress monitoring and review",
            "Contingency planning for alternative scenarios",
            "Stakeholder alignment and communication"
        ]

        if response["risk_level"] == "high":
            mitigation_strategies.extend([
                "Phased implementation approach",
                "Additional risk assessment and planning",
                "Senior leadership oversight"
            ])

        return mitigation_strategies

class CompetitiveIntelligenceService:
    """Main service orchestrating competitive intelligence operations"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["market_intelligence"]
        self.competitor_monitor = CompetitorMonitor()
        self.positioning_analyzer = StrategicPositioningAnalyzer()
        self.response_optimizer = CompetitiveResponseOptimizer()

    async def generate_competitive_intelligence_report(
        self,
        our_company_data: Dict[str, Any],
        key_competitors: List[str],
        analysis_scope: str = "comprehensive"
    ) -> CompetitiveIntelligenceReport:
        """Generate comprehensive competitive intelligence report"""
        try:
            logger.info("Generating competitive intelligence report")

            # Gather competitive data
            tasks = [
                self._build_competitor_profiles(key_competitors),
                self.competitor_monitor.monitor_competitor_activities(key_competitors),
                self._analyze_market_share_dynamics(our_company_data, key_competitors),
                self._assess_competitive_threats(key_competitors),
                self._generate_market_predictions()
            ]

            (competitor_profiles, competitive_moves, market_share_analysis,
             threat_assessments, market_predictions) = await asyncio.gather(*tasks)

            # Analyze competitive positioning
            positioning_analysis = await self.positioning_analyzer.analyze_competitive_positioning(
                our_company_data, competitor_profiles
            )

            # Generate strategic recommendations
            strategic_responses = await self.response_optimizer.recommend_strategic_responses(
                threat_assessments, our_company_data
            )

            # Generate overall strategic recommendations
            strategic_recommendations = await self._generate_strategic_recommendations(
                competitor_profiles, competitive_moves, positioning_analysis
            )

            # Create action items
            action_items = await self._create_action_items(strategic_responses, competitive_moves)

            return CompetitiveIntelligenceReport(
                generated_at=datetime.utcnow(),
                market_overview=self._create_market_overview(competitor_profiles, market_share_analysis),
                competitor_profiles=competitor_profiles,
                recent_competitive_moves=competitive_moves,
                market_share_analysis=market_share_analysis,
                threat_assessments=threat_assessments,
                strategic_recommendations=strategic_recommendations,
                competitive_positioning=positioning_analysis,
                market_predictions=market_predictions,
                action_items=action_items
            )

        except Exception as e:
            logger.error(f"Error generating competitive intelligence report: {e}")
            raise

    async def _build_competitor_profiles(self, competitors: List[str]) -> List[CompetitorProfile]:
        """Build detailed competitor profiles"""
        profiles = []

        for competitor in competitors:
            profile_data = await self._get_competitor_data(competitor)
            profile = CompetitorProfile(**profile_data)
            profiles.append(profile)

        return profiles

    async def _get_competitor_data(self, competitor: str) -> Dict[str, Any]:
        """Get comprehensive competitor data"""
        # Mock competitor data - would integrate with financial APIs, industry databases
        competitor_data = {
            "TechCorp Alpha": {
                "competitor_id": "tech_alpha_001",
                "company_name": "TechCorp Alpha",
                "market_cap": 85_000_000_000,
                "revenue": 28_000_000_000,
                "growth_rate": 0.18,
                "market_share": 0.22,
                "competitive_strengths": ["technology_leadership", "brand_recognition", "distribution_network"],
                "competitive_weaknesses": ["high_cost_structure", "slow_decision_making"],
                "recent_moves": [
                    {"action": "acquisition", "target": "AI Startup Beta", "value": 2_800_000_000, "date": "2023-09-15"},
                    {"action": "partnership", "partner": "Cloud Provider X", "date": "2023-10-22"}
                ],
                "financial_health_score": 0.85,
                "innovation_index": 0.78,
                "acquisition_activity_score": 0.82,
                "strategic_focus": ["artificial_intelligence", "cloud_computing", "enterprise_software"]
            },
            "Innovation Challenger": {
                "competitor_id": "innov_chall_001",
                "company_name": "Innovation Challenger",
                "market_cap": 45_000_000_000,
                "revenue": 18_000_000_000,
                "growth_rate": 0.32,
                "market_share": 0.18,
                "competitive_strengths": ["innovation_speed", "customer_focus", "agility"],
                "competitive_weaknesses": ["limited_resources", "narrow_product_portfolio"],
                "recent_moves": [
                    {"action": "product_launch", "product": "Next-Gen Platform", "date": "2023-11-01"},
                    {"action": "funding_round", "amount": 1_500_000_000, "date": "2023-08-30"}
                ],
                "financial_health_score": 0.72,
                "innovation_index": 0.92,
                "acquisition_activity_score": 0.45,
                "strategic_focus": ["innovation", "customer_experience", "market_disruption"]
            }
        }

        return competitor_data.get(competitor, {
            "competitor_id": f"{competitor.lower().replace(' ', '_')}_001",
            "company_name": competitor,
            "market_cap": 15_000_000_000,
            "revenue": 5_000_000_000,
            "growth_rate": 0.15,
            "market_share": 0.08,
            "competitive_strengths": ["market_presence"],
            "competitive_weaknesses": ["competitive_pressure"],
            "recent_moves": [],
            "financial_health_score": 0.65,
            "innovation_index": 0.55,
            "acquisition_activity_score": 0.35,
            "strategic_focus": ["market_share_growth"]
        })

    async def _analyze_market_share_dynamics(
        self,
        our_data: Dict[str, Any],
        competitors: List[str]
    ) -> MarketShareAnalysis:
        """Analyze market share dynamics and trends"""
        # Mock market analysis
        return MarketShareAnalysis(
            total_market_size=125_000_000_000,  # $125B market
            our_market_share=our_data.get("market_share", 0.12),
            our_market_position=3,
            top_competitors=[
                {"name": "TechCorp Alpha", "share": 0.22, "trend": "stable"},
                {"name": "Innovation Challenger", "share": 0.18, "trend": "growing"},
                {"name": "Market Incumbent", "share": 0.15, "trend": "declining"}
            ],
            market_share_trends={
                "12_months": 0.02,    # 2% growth
                "24_months": 0.035,   # 3.5% growth over 2 years
                "trend_direction": "positive"
            },
            competitive_gaps=[
                "AI/ML capabilities lag behind leaders",
                "International presence limited",
                "Enterprise customer base smaller"
            ],
            growth_opportunities=[
                "Small/medium business segment underserved",
                "Emerging markets expansion potential",
                "Adjacent product categories"
            ],
            defensive_priorities=[
                "Protect core customer base",
                "Maintain technology competitiveness",
                "Strengthen partner relationships"
            ]
        )

    async def _assess_competitive_threats(self, competitors: List[str]) -> List[ThreatAssessment]:
        """Assess competitive threats and their implications"""
        threats = []

        # Technology disruption threat
        threats.append(ThreatAssessment(
            threat_id="tech_disruption_001",
            threat_type="technology_disruption",
            threat_level=ThreatLevel.HIGH,
            likelihood=0.75,
            potential_impact=0.85,
            time_horizon="6_to_12_months",
            description="Major competitors investing heavily in AI/ML capabilities that could disrupt our market position",
            indicators=[
                "Increased AI patent filings by competitors",
                "High-profile AI talent acquisitions",
                "Customer inquiries about AI features"
            ],
            mitigation_strategies=[
                "Accelerate internal AI development",
                "Strategic AI company acquisitions",
                "Partner with AI technology leaders"
            ],
            monitoring_metrics=[
                "Competitor AI patent counts",
                "Customer satisfaction scores",
                "Technology benchmark comparisons"
            ]
        ))

        # Market share erosion threat
        threats.append(ThreatAssessment(
            threat_id="market_erosion_001",
            threat_type="market_share_erosion",
            threat_level=ThreatLevel.MEDIUM,
            likelihood=0.65,
            potential_impact=0.60,
            time_horizon="12_to_18_months",
            description="Aggressive pricing and feature competition may erode market share",
            indicators=[
                "Competitor price reductions",
                "Enhanced feature offerings",
                "Customer churn increases"
            ],
            mitigation_strategies=[
                "Value-based differentiation",
                "Customer loyalty programs",
                "Competitive pricing analysis"
            ],
            monitoring_metrics=[
                "Market share trends",
                "Customer retention rates",
                "Competitive pricing analysis"
            ]
        ))

        return threats

    async def _generate_market_predictions(self) -> Dict[str, Any]:
        """Generate market predictions based on competitive analysis"""
        return {
            "market_consolidation": {
                "likelihood": 0.7,
                "timeframe": "18_months",
                "key_drivers": ["Technology convergence", "Scale economics", "Customer preferences"]
            },
            "technology_trends": {
                "ai_adoption": {"growth_rate": 0.45, "market_impact": "transformational"},
                "cloud_migration": {"growth_rate": 0.25, "market_impact": "significant"},
                "automation": {"growth_rate": 0.35, "market_impact": "high"}
            },
            "competitive_dynamics": {
                "new_entrants_expected": 3,
                "merger_probability": 0.4,
                "pricing_pressure": "increasing"
            }
        }

    async def _generate_strategic_recommendations(
        self,
        competitors: List[CompetitorProfile],
        moves: List[CompetitiveMove],
        positioning: Dict[str, Any]
    ) -> List[str]:
        """Generate strategic recommendations based on competitive analysis"""
        recommendations = []

        # Based on competitor moves
        high_threat_moves = [m for m in moves if m.threat_level == ThreatLevel.HIGH]
        if high_threat_moves:
            recommendations.append("Accelerate competitive response to high-threat competitor moves")

        # Based on positioning
        if positioning.get("competitive_gaps"):
            recommendations.append("Address identified competitive gaps through targeted investments")

        # Based on market dynamics
        fast_growing_competitors = [c for c in competitors if c.growth_rate > 0.25]
        if fast_growing_competitors:
            recommendations.append("Monitor and potentially counter fast-growing competitors")

        # Innovation recommendations
        high_innovation_competitors = [c for c in competitors if c.innovation_index > 0.8]
        if high_innovation_competitors:
            recommendations.append("Increase innovation investment to match competitive pace")

        return recommendations

    async def _create_action_items(
        self,
        strategic_responses: List[Dict[str, Any]],
        competitive_moves: List[CompetitiveMove]
    ) -> List[Dict[str, Any]]:
        """Create specific action items based on analysis"""
        action_items = []

        # High-priority responses
        high_priority_responses = [r for r in strategic_responses if r["priority"] >= 4]
        for response in high_priority_responses:
            action_items.append({
                "action_id": f"action_{len(action_items) + 1:03d}",
                "title": f"Implement {response['recommended_response']}",
                "description": response["rationale"],
                "priority": response["priority"],
                "assigned_to": "strategy_team",
                "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "success_metrics": ["implementation_completion", "impact_measurement"]
            })

        # Monitor critical competitive moves
        critical_moves = [m for m in competitive_moves if m.threat_level == ThreatLevel.CRITICAL]
        for move in critical_moves:
            action_items.append({
                "action_id": f"action_{len(action_items) + 1:03d}",
                "title": f"Monitor and respond to {move.competitor_name} {move.action_type.value}",
                "description": f"Track impact and implement response to {move.description}",
                "priority": 5,
                "assigned_to": "competitive_intelligence_team",
                "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "success_metrics": ["response_implementation", "threat_mitigation"]
            })

        return sorted(action_items, key=lambda x: x["priority"], reverse=True)

    def _create_market_overview(
        self,
        competitors: List[CompetitorProfile],
        market_analysis: MarketShareAnalysis
    ) -> Dict[str, Any]:
        """Create market overview summary"""
        return {
            "total_market_size": market_analysis.total_market_size,
            "number_of_competitors": len(competitors),
            "market_growth_rate": 0.15,  # 15% annual growth
            "competitive_intensity": "high",
            "key_trends": [
                "AI/ML adoption accelerating",
                "Cloud-first strategies dominant",
                "Customer experience differentiation"
            ],
            "market_maturity": "growth_phase"
        }

# Service factory function
_competitive_intelligence_service = None

async def get_competitive_intelligence_service() -> CompetitiveIntelligenceService:
    """Get singleton competitive intelligence service instance"""
    global _competitive_intelligence_service
    if _competitive_intelligence_service is None:
        _competitive_intelligence_service = CompetitiveIntelligenceService()
    return _competitive_intelligence_service