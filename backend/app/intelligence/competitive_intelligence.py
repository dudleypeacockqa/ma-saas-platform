"""
Competitive Intelligence System for Strategic Market Positioning and Differentiation

This module provides comprehensive competitive analysis capabilities for the M&A platform,
enabling strategic positioning, market differentiation, and wealth-building optimization.
"""

import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import networkx as nx
import logging

logger = logging.getLogger(__name__)


class CompetitorType(Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    POTENTIAL = "potential"
    SUBSTITUTE = "substitute"
    NEW_ENTRANT = "new_entrant"


class StrategicAdvantage(Enum):
    COST_LEADERSHIP = "cost_leadership"
    DIFFERENTIATION = "differentiation"
    FOCUS = "focus"
    INNOVATION = "innovation"
    SPEED = "speed"
    NETWORK_EFFECTS = "network_effects"
    PLATFORM_ECOSYSTEM = "platform_ecosystem"


class MarketPosition(Enum):
    LEADER = "leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHER = "nicher"
    DISRUPTOR = "disruptor"


@dataclass
class CompetitorProfile:
    """Comprehensive competitor profile with strategic assessment"""
    competitor_id: str
    name: str
    type: CompetitorType
    market_position: MarketPosition
    market_share: float
    growth_rate: float
    revenue: float
    valuation: float
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)
    key_capabilities: Dict[str, float] = field(default_factory=dict)
    strategic_moves: List[Dict[str, Any]] = field(default_factory=list)
    partnerships: Set[str] = field(default_factory=set)
    technology_stack: Set[str] = field(default_factory=set)
    customer_segments: Set[str] = field(default_factory=set)
    geographic_presence: Set[str] = field(default_factory=set)
    competitive_score: float = 0.0
    threat_level: float = 0.0
    opportunity_level: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitiveStrategy:
    """Strategic positioning and differentiation strategy"""
    strategy_id: str
    name: str
    type: StrategicAdvantage
    description: str
    key_initiatives: List[Dict[str, Any]]
    resource_requirements: Dict[str, float]
    implementation_timeline: int  # days
    expected_impact: Dict[str, float]
    risk_factors: List[str]
    success_metrics: Dict[str, float]
    competitive_moat: float
    sustainability_score: float
    priority: int
    status: str = "proposed"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketIntelligence:
    """Market intelligence insights and trends"""
    market_id: str
    market_size: float
    growth_rate: float
    competitive_intensity: float
    entry_barriers: float
    customer_concentration: float
    supplier_power: float
    substitute_threat: float
    regulatory_complexity: float
    technology_disruption_risk: float
    market_trends: List[Dict[str, Any]] = field(default_factory=list)
    emerging_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    key_success_factors: List[str] = field(default_factory=list)
    value_chain_analysis: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CompetitiveIntelligence:
    """Main competitive intelligence system"""

    def __init__(self):
        self.competitors: Dict[str, CompetitorProfile] = {}
        self.strategies: List[CompetitiveStrategy] = []
        self.market_intelligence: Dict[str, MarketIntelligence] = {}
        self.competitive_network = nx.DiGraph()
        self.threat_model = None
        self.opportunity_model = None
        self.position_model = None
        self._initialize_models()

    def _initialize_models(self):
        """Initialize ML models for competitive analysis"""
        self.threat_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.opportunity_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.position_model = KMeans(
            n_clusters=5,
            random_state=42
        )
        self.scaler = StandardScaler()

    async def analyze_competitive_landscape(self) -> Dict[str, Any]:
        """Perform comprehensive competitive landscape analysis"""
        try:
            # Run analysis tasks in parallel
            tasks = [
                self._analyze_competitors(),
                self._assess_market_positioning(),
                self._identify_strategic_gaps(),
                self._evaluate_competitive_threats(),
                self._discover_opportunities(),
                self._generate_strategic_recommendations()
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Combine results
            analysis = {
                "timestamp": datetime.utcnow().isoformat(),
                "competitors": results[0],
                "market_positioning": results[1],
                "strategic_gaps": results[2],
                "competitive_threats": results[3],
                "opportunities": results[4],
                "recommendations": results[5],
                "competitive_advantage_score": self._calculate_competitive_advantage(),
                "market_leadership_potential": self._assess_leadership_potential(),
                "strategic_options": self._identify_strategic_options()
            }

            return analysis

        except Exception as e:
            logger.error(f"Competitive analysis failed: {str(e)}")
            raise

    async def _analyze_competitors(self) -> Dict[str, Any]:
        """Analyze competitor profiles and capabilities"""
        competitor_analysis = {
            "total_competitors": len(self.competitors),
            "by_type": {},
            "by_position": {},
            "top_threats": [],
            "weak_competitors": [],
            "competitive_dynamics": {}
        }

        # Analyze competitors by type and position
        for competitor in self.competitors.values():
            # Score competitor
            competitor.competitive_score = self._calculate_competitor_score(competitor)
            competitor.threat_level = self._assess_threat_level(competitor)
            competitor.opportunity_level = self._assess_opportunity_level(competitor)

            # Categorize
            comp_type = competitor.type.value
            if comp_type not in competitor_analysis["by_type"]:
                competitor_analysis["by_type"][comp_type] = []
            competitor_analysis["by_type"][comp_type].append({
                "id": competitor.competitor_id,
                "name": competitor.name,
                "score": competitor.competitive_score,
                "threat": competitor.threat_level
            })

            position = competitor.market_position.value
            if position not in competitor_analysis["by_position"]:
                competitor_analysis["by_position"][position] = []
            competitor_analysis["by_position"][position].append({
                "id": competitor.competitor_id,
                "name": competitor.name,
                "market_share": competitor.market_share
            })

        # Identify top threats and opportunities
        sorted_by_threat = sorted(
            self.competitors.values(),
            key=lambda x: x.threat_level,
            reverse=True
        )

        competitor_analysis["top_threats"] = [
            {
                "id": c.competitor_id,
                "name": c.name,
                "threat_level": c.threat_level,
                "key_strengths": c.strengths[:3]
            }
            for c in sorted_by_threat[:5]
        ]

        sorted_by_weakness = sorted(
            self.competitors.values(),
            key=lambda x: x.competitive_score
        )

        competitor_analysis["weak_competitors"] = [
            {
                "id": c.competitor_id,
                "name": c.name,
                "weaknesses": c.weaknesses[:3],
                "acquisition_potential": c.opportunity_level
            }
            for c in sorted_by_weakness[:5]
        ]

        # Analyze competitive dynamics
        competitor_analysis["competitive_dynamics"] = {
            "market_concentration": self._calculate_market_concentration(),
            "competitive_intensity": self._assess_competitive_intensity(),
            "disruption_risk": self._evaluate_disruption_risk(),
            "consolidation_potential": self._assess_consolidation_potential()
        }

        return competitor_analysis

    async def _assess_market_positioning(self) -> Dict[str, Any]:
        """Assess market positioning and differentiation"""
        positioning = {
            "current_position": None,
            "position_strength": 0.0,
            "differentiation_factors": [],
            "competitive_advantages": [],
            "position_vulnerabilities": [],
            "positioning_opportunities": []
        }

        # Determine current market position
        our_capabilities = self._get_our_capabilities()
        positioning["current_position"] = self._determine_market_position(our_capabilities)

        # Assess position strength
        positioning["position_strength"] = self._calculate_position_strength(
            our_capabilities
        )

        # Identify differentiation factors
        positioning["differentiation_factors"] = self._identify_differentiation_factors(
            our_capabilities
        )

        # Identify competitive advantages
        positioning["competitive_advantages"] = self._identify_competitive_advantages(
            our_capabilities
        )

        # Identify vulnerabilities
        positioning["position_vulnerabilities"] = self._identify_position_vulnerabilities(
            our_capabilities
        )

        # Identify positioning opportunities
        positioning["positioning_opportunities"] = self._identify_positioning_opportunities()

        return positioning

    async def _identify_strategic_gaps(self) -> List[Dict[str, Any]]:
        """Identify strategic gaps and improvement areas"""
        gaps = []

        # Capability gaps
        capability_gaps = self._identify_capability_gaps()
        for gap in capability_gaps:
            gaps.append({
                "type": "capability",
                "area": gap["area"],
                "current_level": gap["current"],
                "required_level": gap["required"],
                "impact": gap["impact"],
                "priority": gap["priority"],
                "closing_strategy": gap["strategy"]
            })

        # Market coverage gaps
        market_gaps = self._identify_market_gaps()
        for gap in market_gaps:
            gaps.append({
                "type": "market",
                "segment": gap["segment"],
                "opportunity_size": gap["size"],
                "entry_difficulty": gap["difficulty"],
                "strategic_fit": gap["fit"],
                "priority": gap["priority"]
            })

        # Technology gaps
        tech_gaps = self._identify_technology_gaps()
        for gap in tech_gaps:
            gaps.append({
                "type": "technology",
                "technology": gap["tech"],
                "importance": gap["importance"],
                "adoption_cost": gap["cost"],
                "time_to_implement": gap["time"],
                "competitive_impact": gap["impact"]
            })

        # Partnership gaps
        partnership_gaps = self._identify_partnership_gaps()
        for gap in partnership_gaps:
            gaps.append({
                "type": "partnership",
                "partner_type": gap["type"],
                "strategic_value": gap["value"],
                "availability": gap["availability"],
                "partnership_cost": gap["cost"],
                "synergy_potential": gap["synergy"]
            })

        # Sort by priority
        gaps.sort(key=lambda x: x.get("priority", 0), reverse=True)

        return gaps

    async def _evaluate_competitive_threats(self) -> Dict[str, Any]:
        """Evaluate competitive threats and risks"""
        threats = {
            "immediate_threats": [],
            "emerging_threats": [],
            "disruption_risks": [],
            "market_share_risks": [],
            "technology_threats": [],
            "regulatory_threats": [],
            "threat_mitigation_strategies": []
        }

        # Immediate competitive threats
        for competitor in self.competitors.values():
            if competitor.threat_level > 0.7:
                threats["immediate_threats"].append({
                    "source": competitor.name,
                    "threat_level": competitor.threat_level,
                    "threat_type": self._classify_threat_type(competitor),
                    "impact_areas": self._identify_impact_areas(competitor),
                    "response_urgency": "high",
                    "mitigation_options": self._generate_mitigation_options(competitor)
                })

        # Emerging threats
        emerging = self._identify_emerging_threats()
        threats["emerging_threats"] = [
            {
                "threat": threat["description"],
                "probability": threat["probability"],
                "time_horizon": threat["timeline"],
                "potential_impact": threat["impact"],
                "early_indicators": threat["indicators"]
            }
            for threat in emerging
        ]

        # Disruption risks
        disruption = self._assess_disruption_risks()
        threats["disruption_risks"] = disruption

        # Market share risks
        threats["market_share_risks"] = self._evaluate_market_share_risks()

        # Technology threats
        threats["technology_threats"] = self._identify_technology_threats()

        # Regulatory threats
        threats["regulatory_threats"] = self._identify_regulatory_threats()

        # Generate mitigation strategies
        threats["threat_mitigation_strategies"] = self._generate_threat_mitigation_strategies(
            threats
        )

        return threats

    async def _discover_opportunities(self) -> List[Dict[str, Any]]:
        """Discover competitive opportunities and advantages"""
        opportunities = []

        # Market opportunities
        market_opps = self._identify_market_opportunities()
        for opp in market_opps:
            opportunities.append({
                "type": "market",
                "opportunity": opp["description"],
                "value_potential": opp["value"],
                "competitive_advantage": opp["advantage"],
                "implementation_difficulty": opp["difficulty"],
                "time_to_market": opp["timeline"],
                "success_probability": opp["probability"],
                "key_requirements": opp["requirements"]
            })

        # Acquisition opportunities
        acquisition_opps = self._identify_acquisition_opportunities()
        for opp in acquisition_opps:
            opportunities.append({
                "type": "acquisition",
                "target": opp["target"],
                "strategic_value": opp["value"],
                "synergies": opp["synergies"],
                "valuation_estimate": opp["valuation"],
                "integration_complexity": opp["complexity"],
                "competitive_impact": opp["impact"]
            })

        # Partnership opportunities
        partnership_opps = self._identify_partnership_opportunities()
        for opp in partnership_opps:
            opportunities.append({
                "type": "partnership",
                "partner_profile": opp["profile"],
                "collaboration_areas": opp["areas"],
                "value_creation": opp["value"],
                "strategic_fit": opp["fit"],
                "partnership_model": opp["model"]
            })

        # Innovation opportunities
        innovation_opps = self._identify_innovation_opportunities()
        for opp in innovation_opps:
            opportunities.append({
                "type": "innovation",
                "innovation": opp["description"],
                "disruptive_potential": opp["disruption"],
                "competitive_advantage": opp["advantage"],
                "development_cost": opp["cost"],
                "time_to_market": opp["timeline"],
                "patent_potential": opp["patent"]
            })

        # Sort by value potential and probability
        opportunities.sort(
            key=lambda x: x.get("value_potential", 0) * x.get("success_probability", 1),
            reverse=True
        )

        return opportunities

    async def _generate_strategic_recommendations(self) -> List[Dict[str, Any]]:
        """Generate strategic recommendations for competitive advantage"""
        recommendations = []

        # Positioning recommendations
        position_recs = self._generate_positioning_recommendations()
        recommendations.extend(position_recs)

        # Differentiation recommendations
        diff_recs = self._generate_differentiation_recommendations()
        recommendations.extend(diff_recs)

        # Competitive response recommendations
        response_recs = self._generate_competitive_response_recommendations()
        recommendations.extend(response_recs)

        # Market entry/exit recommendations
        market_recs = self._generate_market_recommendations()
        recommendations.extend(market_recs)

        # Partnership and alliance recommendations
        partnership_recs = self._generate_partnership_recommendations()
        recommendations.extend(partnership_recs)

        # Technology and innovation recommendations
        tech_recs = self._generate_technology_recommendations()
        recommendations.extend(tech_recs)

        # Prioritize recommendations
        for rec in recommendations:
            rec["priority_score"] = self._calculate_recommendation_priority(rec)

        recommendations.sort(key=lambda x: x["priority_score"], reverse=True)

        return recommendations[:20]  # Return top 20 recommendations

    def _calculate_competitor_score(self, competitor: CompetitorProfile) -> float:
        """Calculate overall competitor strength score"""
        weights = {
            "market_share": 0.2,
            "growth_rate": 0.15,
            "capabilities": 0.2,
            "partnerships": 0.15,
            "technology": 0.15,
            "financial": 0.15
        }

        scores = {
            "market_share": min(competitor.market_share * 2, 1.0),
            "growth_rate": min(competitor.growth_rate / 0.3, 1.0),
            "capabilities": np.mean(list(competitor.key_capabilities.values())) if competitor.key_capabilities else 0.5,
            "partnerships": min(len(competitor.partnerships) / 20, 1.0),
            "technology": min(len(competitor.technology_stack) / 15, 1.0),
            "financial": min(competitor.valuation / 1000000000, 1.0)  # Normalized to $1B
        }

        total_score = sum(scores[key] * weights[key] for key in weights)
        return round(total_score, 3)

    def _assess_threat_level(self, competitor: CompetitorProfile) -> float:
        """Assess threat level posed by competitor"""
        threat_factors = {
            "competitive_score": competitor.competitive_score * 0.3,
            "growth_rate": min(competitor.growth_rate / 0.2, 1.0) * 0.2,
            "market_overlap": self._calculate_market_overlap(competitor) * 0.25,
            "capability_advantage": self._assess_capability_advantage(competitor) * 0.15,
            "aggressive_strategy": self._assess_strategic_aggressiveness(competitor) * 0.1
        }

        return round(sum(threat_factors.values()), 3)

    def _assess_opportunity_level(self, competitor: CompetitorProfile) -> float:
        """Assess opportunity level from competitor"""
        opportunity_factors = {
            "weakness_exploitation": len(competitor.weaknesses) / 10 * 0.3,
            "acquisition_potential": (1 - competitor.competitive_score) * 0.25,
            "partnership_potential": self._assess_partnership_compatibility(competitor) * 0.2,
            "market_learning": self._assess_learning_potential(competitor) * 0.15,
            "customer_overlap": self._calculate_customer_overlap(competitor) * 0.1
        }

        return round(sum(opportunity_factors.values()), 3)

    def _calculate_market_overlap(self, competitor: CompetitorProfile) -> float:
        """Calculate market overlap with competitor"""
        # Simplified calculation - would use actual data in production
        segment_overlap = len(competitor.customer_segments) / 10
        geographic_overlap = len(competitor.geographic_presence) / 20
        return min((segment_overlap + geographic_overlap) / 2, 1.0)

    def _assess_capability_advantage(self, competitor: CompetitorProfile) -> float:
        """Assess competitor's capability advantage"""
        if not competitor.key_capabilities:
            return 0.5

        our_capabilities = self._get_our_capabilities()
        advantages = []

        for capability, score in competitor.key_capabilities.items():
            our_score = our_capabilities.get(capability, 0.5)
            if score > our_score:
                advantages.append(score - our_score)

        return min(np.mean(advantages) if advantages else 0, 1.0)

    def _assess_strategic_aggressiveness(self, competitor: CompetitorProfile) -> float:
        """Assess competitor's strategic aggressiveness"""
        aggressive_indicators = 0
        total_indicators = 5

        # Check for aggressive moves
        if competitor.growth_rate > 0.3:
            aggressive_indicators += 1
        if len(competitor.strategic_moves) > 5:
            aggressive_indicators += 1
        if competitor.market_position == MarketPosition.CHALLENGER:
            aggressive_indicators += 1
        if competitor.market_position == MarketPosition.DISRUPTOR:
            aggressive_indicators += 2

        return aggressive_indicators / total_indicators

    def _assess_partnership_compatibility(self, competitor: CompetitorProfile) -> float:
        """Assess partnership compatibility with competitor"""
        compatibility_factors = {
            "complementary_capabilities": 0.3,
            "market_synergies": 0.25,
            "cultural_fit": 0.2,
            "strategic_alignment": 0.15,
            "trust_factor": 0.1
        }

        # Simplified scoring - would use actual assessment in production
        scores = {
            "complementary_capabilities": 0.7,
            "market_synergies": 0.6,
            "cultural_fit": 0.5,
            "strategic_alignment": 0.6,
            "trust_factor": 0.4
        }

        return sum(scores[key] * compatibility_factors[key] for key in compatibility_factors)

    def _assess_learning_potential(self, competitor: CompetitorProfile) -> float:
        """Assess potential to learn from competitor"""
        learning_factors = []

        # Superior capabilities to learn from
        if competitor.competitive_score > 0.7:
            learning_factors.append(0.8)

        # Innovative approaches
        if competitor.market_position == MarketPosition.DISRUPTOR:
            learning_factors.append(0.9)

        # Advanced technology stack
        if len(competitor.technology_stack) > 10:
            learning_factors.append(0.7)

        # Successful strategies
        if len(competitor.strategic_moves) > 3:
            learning_factors.append(0.6)

        return np.mean(learning_factors) if learning_factors else 0.3

    def _calculate_customer_overlap(self, competitor: CompetitorProfile) -> float:
        """Calculate customer segment overlap"""
        our_segments = {"enterprise", "mid_market", "smb", "startup"}
        overlap = len(our_segments.intersection(competitor.customer_segments))
        return overlap / len(our_segments) if our_segments else 0

    def _get_our_capabilities(self) -> Dict[str, float]:
        """Get our platform's capabilities"""
        return {
            "ai_analytics": 0.9,
            "deal_sourcing": 0.85,
            "due_diligence": 0.8,
            "valuation": 0.75,
            "integration": 0.7,
            "network_effects": 0.8,
            "automation": 0.85,
            "user_experience": 0.9,
            "data_quality": 0.85,
            "scalability": 0.9
        }

    def _calculate_market_concentration(self) -> float:
        """Calculate market concentration (HHI)"""
        if not self.competitors:
            return 0.0

        market_shares = [c.market_share for c in self.competitors.values()]
        hhi = sum(share ** 2 for share in market_shares) * 10000
        return min(hhi / 10000, 1.0)  # Normalize to 0-1

    def _assess_competitive_intensity(self) -> float:
        """Assess competitive intensity in the market"""
        factors = {
            "competitor_count": min(len(self.competitors) / 20, 1.0) * 0.2,
            "market_concentration": self._calculate_market_concentration() * 0.2,
            "price_competition": 0.6 * 0.15,  # Placeholder
            "innovation_rate": 0.7 * 0.15,  # Placeholder
            "customer_switching": 0.5 * 0.15,  # Placeholder
            "exit_barriers": 0.6 * 0.15  # Placeholder
        }

        return sum(factors.values())

    def _evaluate_disruption_risk(self) -> float:
        """Evaluate risk of market disruption"""
        disruption_indicators = {
            "new_entrants": len([c for c in self.competitors.values()
                                if c.type == CompetitorType.NEW_ENTRANT]) / 5 * 0.25,
            "technology_change": 0.7 * 0.25,  # Placeholder
            "business_model_innovation": 0.6 * 0.2,  # Placeholder
            "regulatory_changes": 0.4 * 0.15,  # Placeholder
            "customer_behavior_shift": 0.5 * 0.15  # Placeholder
        }

        return min(sum(disruption_indicators.values()), 1.0)

    def _assess_consolidation_potential(self) -> float:
        """Assess market consolidation potential"""
        consolidation_factors = {
            "market_fragmentation": (1 - self._calculate_market_concentration()) * 0.3,
            "weak_players": len([c for c in self.competitors.values()
                               if c.competitive_score < 0.4]) / 10 * 0.25,
            "acquisition_activity": 0.6 * 0.2,  # Placeholder
            "capital_availability": 0.7 * 0.15,  # Placeholder
            "synergy_potential": 0.8 * 0.1  # Placeholder
        }

        return sum(consolidation_factors.values())

    def _determine_market_position(self, capabilities: Dict[str, float]) -> str:
        """Determine our market position"""
        # Simplified positioning logic
        avg_capability = np.mean(list(capabilities.values()))

        if avg_capability > 0.8:
            return "leader"
        elif avg_capability > 0.65:
            return "challenger"
        elif avg_capability > 0.5:
            return "follower"
        else:
            return "nicher"

    def _calculate_position_strength(self, capabilities: Dict[str, float]) -> float:
        """Calculate strength of market position"""
        return round(np.mean(list(capabilities.values())), 3)

    def _identify_differentiation_factors(self, capabilities: Dict[str, float]) -> List[str]:
        """Identify key differentiation factors"""
        differentiators = []

        # Identify top capabilities
        sorted_capabilities = sorted(capabilities.items(), key=lambda x: x[1], reverse=True)
        for capability, score in sorted_capabilities[:5]:
            if score > 0.8:
                differentiators.append(f"Superior {capability.replace('_', ' ').title()}")

        # Add platform-specific differentiators
        differentiators.extend([
            "AI-Powered Deal Intelligence",
            "Comprehensive Ecosystem Integration",
            "End-to-End M&A Automation",
            "Predictive Analytics and Forecasting",
            "Network Effect Value Creation"
        ])

        return differentiators

    def _identify_competitive_advantages(self, capabilities: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify sustainable competitive advantages"""
        advantages = []

        # Capability advantages
        for capability, score in capabilities.items():
            if score > 0.85:
                advantages.append({
                    "advantage": capability.replace('_', ' ').title(),
                    "strength": score,
                    "sustainability": self._assess_advantage_sustainability(capability, score),
                    "value_creation": self._assess_advantage_value(capability, score)
                })

        # Strategic advantages
        strategic_advantages = [
            {
                "advantage": "Platform Network Effects",
                "strength": 0.9,
                "sustainability": 0.85,
                "value_creation": 0.95
            },
            {
                "advantage": "Data and AI Capabilities",
                "strength": 0.88,
                "sustainability": 0.8,
                "value_creation": 0.9
            },
            {
                "advantage": "Ecosystem Integration",
                "strength": 0.85,
                "sustainability": 0.75,
                "value_creation": 0.85
            }
        ]

        advantages.extend(strategic_advantages)
        advantages.sort(key=lambda x: x["value_creation"], reverse=True)

        return advantages

    def _identify_position_vulnerabilities(self, capabilities: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify position vulnerabilities"""
        vulnerabilities = []

        # Capability vulnerabilities
        for capability, score in capabilities.items():
            if score < 0.6:
                vulnerabilities.append({
                    "vulnerability": f"Weak {capability.replace('_', ' ').title()}",
                    "severity": 1 - score,
                    "competitive_impact": self._assess_vulnerability_impact(capability, score),
                    "mitigation_priority": self._calculate_mitigation_priority(capability, score)
                })

        # Strategic vulnerabilities
        strategic_vulns = [
            {
                "vulnerability": "Market Share Concentration",
                "severity": 0.6,
                "competitive_impact": 0.7,
                "mitigation_priority": 0.65
            },
            {
                "vulnerability": "Technology Dependency",
                "severity": 0.5,
                "competitive_impact": 0.6,
                "mitigation_priority": 0.55
            }
        ]

        vulnerabilities.extend(strategic_vulns)
        vulnerabilities.sort(key=lambda x: x["mitigation_priority"], reverse=True)

        return vulnerabilities

    def _identify_positioning_opportunities(self) -> List[Dict[str, Any]]:
        """Identify market positioning opportunities"""
        opportunities = [
            {
                "opportunity": "AI-First M&A Platform Leadership",
                "feasibility": 0.85,
                "competitive_impact": 0.9,
                "investment_required": 0.7,
                "time_to_position": 180  # days
            },
            {
                "opportunity": "Ecosystem Orchestrator Position",
                "feasibility": 0.8,
                "competitive_impact": 0.85,
                "investment_required": 0.6,
                "time_to_position": 270
            },
            {
                "opportunity": "Wealth-Building Platform Differentiation",
                "feasibility": 0.9,
                "competitive_impact": 0.95,
                "investment_required": 0.5,
                "time_to_position": 90
            },
            {
                "opportunity": "Global M&A Intelligence Hub",
                "feasibility": 0.75,
                "competitive_impact": 0.88,
                "investment_required": 0.8,
                "time_to_position": 365
            },
            {
                "opportunity": "SMB M&A Market Domination",
                "feasibility": 0.82,
                "competitive_impact": 0.8,
                "investment_required": 0.55,
                "time_to_position": 150
            }
        ]

        return opportunities

    def _identify_capability_gaps(self) -> List[Dict[str, Any]]:
        """Identify capability gaps compared to competitors"""
        gaps = []
        our_capabilities = self._get_our_capabilities()

        # Analyze competitor capabilities
        for competitor in self.competitors.values():
            if competitor.competitive_score > 0.7:
                for capability, their_score in competitor.key_capabilities.items():
                    our_score = our_capabilities.get(capability, 0.5)
                    if their_score > our_score + 0.2:
                        gaps.append({
                            "area": capability,
                            "current": our_score,
                            "required": their_score,
                            "impact": (their_score - our_score) * 0.8,
                            "priority": self._calculate_gap_priority(capability, their_score - our_score),
                            "strategy": self._suggest_gap_closing_strategy(capability)
                        })

        # Remove duplicates and keep highest priority
        unique_gaps = {}
        for gap in gaps:
            area = gap["area"]
            if area not in unique_gaps or gap["priority"] > unique_gaps[area]["priority"]:
                unique_gaps[area] = gap

        return list(unique_gaps.values())

    def _identify_market_gaps(self) -> List[Dict[str, Any]]:
        """Identify market coverage gaps"""
        return [
            {
                "segment": "Enterprise M&A",
                "size": 0.85,
                "difficulty": 0.7,
                "fit": 0.8,
                "priority": 0.78
            },
            {
                "segment": "Cross-Border Deals",
                "size": 0.75,
                "difficulty": 0.8,
                "fit": 0.7,
                "priority": 0.74
            },
            {
                "segment": "Distressed Assets",
                "size": 0.65,
                "difficulty": 0.6,
                "fit": 0.75,
                "priority": 0.66
            }
        ]

    def _identify_technology_gaps(self) -> List[Dict[str, Any]]:
        """Identify technology gaps"""
        return [
            {
                "tech": "Blockchain Smart Contracts",
                "importance": 0.7,
                "cost": 0.6,
                "time": 180,
                "impact": 0.75
            },
            {
                "tech": "Advanced NLP for Documents",
                "importance": 0.85,
                "cost": 0.5,
                "time": 120,
                "impact": 0.8
            },
            {
                "tech": "Real-time Market Data Feeds",
                "importance": 0.8,
                "cost": 0.4,
                "time": 60,
                "impact": 0.7
            }
        ]

    def _identify_partnership_gaps(self) -> List[Dict[str, Any]]:
        """Identify partnership gaps"""
        return [
            {
                "type": "Investment Banks",
                "value": 0.9,
                "availability": 0.6,
                "cost": 0.7,
                "synergy": 0.85
            },
            {
                "type": "Legal Tech Platforms",
                "value": 0.8,
                "availability": 0.75,
                "cost": 0.5,
                "synergy": 0.8
            },
            {
                "type": "Data Providers",
                "value": 0.85,
                "availability": 0.8,
                "cost": 0.6,
                "synergy": 0.75
            }
        ]

    def _classify_threat_type(self, competitor: CompetitorProfile) -> str:
        """Classify the type of threat posed by competitor"""
        if competitor.market_position == MarketPosition.DISRUPTOR:
            return "disruption"
        elif competitor.growth_rate > 0.3:
            return "aggressive_growth"
        elif competitor.competitive_score > 0.8:
            return "market_dominance"
        elif len(competitor.partnerships) > 15:
            return "ecosystem_control"
        else:
            return "direct_competition"

    def _identify_impact_areas(self, competitor: CompetitorProfile) -> List[str]:
        """Identify areas impacted by competitor threat"""
        areas = []

        if competitor.market_share > 0.2:
            areas.append("market_share")
        if competitor.growth_rate > 0.25:
            areas.append("customer_acquisition")
        if len(competitor.technology_stack) > 12:
            areas.append("technology_leadership")
        if len(competitor.partnerships) > 10:
            areas.append("partnership_network")
        if competitor.valuation > 500000000:
            areas.append("funding_advantage")

        return areas

    def _generate_mitigation_options(self, competitor: CompetitorProfile) -> List[str]:
        """Generate threat mitigation options"""
        options = []

        if competitor.threat_level > 0.8:
            options.append("Direct competitive response campaign")
            options.append("Accelerated product development")
            options.append("Strategic partnership to counter")

        if competitor.growth_rate > 0.3:
            options.append("Aggressive customer acquisition")
            options.append("Market expansion strategy")

        if len(competitor.weaknesses) > 3:
            options.append("Exploit competitor weaknesses")
            options.append("Targeted marketing campaign")

        options.append("Differentiation enhancement")
        options.append("Customer retention program")

        return options

    def _identify_emerging_threats(self) -> List[Dict[str, Any]]:
        """Identify emerging competitive threats"""
        return [
            {
                "description": "New AI-powered M&A platforms",
                "probability": 0.8,
                "timeline": "6-12 months",
                "impact": 0.75,
                "indicators": ["VC funding rounds", "Tech talent hiring", "Patent filings"]
            },
            {
                "description": "Big Tech entry into M&A space",
                "probability": 0.6,
                "timeline": "12-24 months",
                "impact": 0.9,
                "indicators": ["Strategic acquisitions", "Platform development", "Partnership signals"]
            },
            {
                "description": "Blockchain-based deal platforms",
                "probability": 0.5,
                "timeline": "18-36 months",
                "impact": 0.7,
                "indicators": ["Smart contract adoption", "Regulatory changes", "Industry pilots"]
            }
        ]

    def _assess_disruption_risks(self) -> List[Dict[str, Any]]:
        """Assess risks of market disruption"""
        return [
            {
                "risk": "AI automation replacing traditional M&A advisory",
                "probability": 0.7,
                "impact": 0.8,
                "timeline": "2-3 years",
                "mitigation": "Lead AI innovation in M&A"
            },
            {
                "risk": "Decentralized finance disrupting deal financing",
                "probability": 0.5,
                "impact": 0.6,
                "timeline": "3-5 years",
                "mitigation": "Integrate DeFi capabilities"
            },
            {
                "risk": "Open-source M&A tools commoditization",
                "probability": 0.4,
                "impact": 0.5,
                "timeline": "1-2 years",
                "mitigation": "Focus on proprietary data and network"
            }
        ]

    def _evaluate_market_share_risks(self) -> List[Dict[str, Any]]:
        """Evaluate risks to market share"""
        return [
            {
                "risk": "Customer defection to competitors",
                "current_impact": 0.2,
                "trend": "increasing",
                "affected_segments": ["SMB", "Mid-market"],
                "retention_strategy": "Enhanced customer success program"
            },
            {
                "risk": "New entrant market capture",
                "current_impact": 0.15,
                "trend": "stable",
                "affected_segments": ["Startup", "Tech"],
                "defense_strategy": "Rapid innovation and feature development"
            }
        ]

    def _identify_technology_threats(self) -> List[Dict[str, Any]]:
        """Identify technology-related threats"""
        return [
            {
                "threat": "Competitor AI superiority",
                "severity": 0.7,
                "timeline": "immediate",
                "response": "Accelerate AI research and development"
            },
            {
                "threat": "Technology platform obsolescence",
                "severity": 0.5,
                "timeline": "2-3 years",
                "response": "Continuous platform modernization"
            }
        ]

    def _identify_regulatory_threats(self) -> List[Dict[str, Any]]:
        """Identify regulatory threats"""
        return [
            {
                "threat": "Data privacy regulations",
                "probability": 0.8,
                "impact": 0.6,
                "regions": ["EU", "California"],
                "compliance_cost": 0.4
            },
            {
                "threat": "M&A regulatory restrictions",
                "probability": 0.4,
                "impact": 0.7,
                "regions": ["US", "UK"],
                "adaptation_required": 0.6
            }
        ]

    def _generate_threat_mitigation_strategies(self, threats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive threat mitigation strategies"""
        strategies = []

        # Immediate threat mitigation
        for threat in threats.get("immediate_threats", []):
            strategies.append({
                "strategy": f"Counter {threat['source']} threat",
                "actions": threat["mitigation_options"],
                "priority": "critical",
                "timeline": "30-60 days",
                "resource_requirement": "high",
                "success_metrics": ["Market share defense", "Customer retention", "Competitive parity"]
            })

        # Disruption mitigation
        for risk in threats.get("disruption_risks", []):
            strategies.append({
                "strategy": risk["mitigation"],
                "actions": ["Innovation investment", "Strategic partnerships", "Talent acquisition"],
                "priority": "high",
                "timeline": risk["timeline"],
                "resource_requirement": "medium",
                "success_metrics": ["Innovation index", "Market position", "Technology leadership"]
            })

        return strategies

    def _identify_market_opportunities(self) -> List[Dict[str, Any]]:
        """Identify market expansion opportunities"""
        return [
            {
                "description": "Untapped SMB M&A market",
                "value": 0.85,
                "advantage": 0.8,
                "difficulty": 0.4,
                "timeline": 90,
                "probability": 0.85,
                "requirements": ["Simplified platform", "Automated workflows", "Lower price point"]
            },
            {
                "description": "Cross-border deal facilitation",
                "value": 0.9,
                "advantage": 0.75,
                "difficulty": 0.7,
                "timeline": 180,
                "probability": 0.7,
                "requirements": ["Multi-currency support", "Regulatory compliance", "Local partnerships"]
            },
            {
                "description": "Industry-specific M&A solutions",
                "value": 0.8,
                "advantage": 0.85,
                "difficulty": 0.5,
                "timeline": 120,
                "probability": 0.8,
                "requirements": ["Domain expertise", "Specialized workflows", "Industry data"]
            }
        ]

    def _identify_acquisition_opportunities(self) -> List[Dict[str, Any]]:
        """Identify strategic acquisition opportunities"""
        opportunities = []

        for competitor in self.competitors.values():
            if competitor.competitive_score < 0.5 and competitor.opportunity_level > 0.6:
                opportunities.append({
                    "target": competitor.name,
                    "value": competitor.opportunity_level,
                    "synergies": self._calculate_acquisition_synergies(competitor),
                    "valuation": competitor.valuation,
                    "complexity": self._assess_integration_complexity(competitor),
                    "impact": self._assess_acquisition_impact(competitor)
                })

        opportunities.sort(key=lambda x: x["value"], reverse=True)
        return opportunities[:5]

    def _identify_partnership_opportunities(self) -> List[Dict[str, Any]]:
        """Identify strategic partnership opportunities"""
        return [
            {
                "profile": "Leading Investment Bank",
                "areas": ["Deal sourcing", "Client referrals", "Market intelligence"],
                "value": 0.9,
                "fit": 0.85,
                "model": "Strategic alliance"
            },
            {
                "profile": "AI Technology Provider",
                "areas": ["Advanced analytics", "ML models", "Data processing"],
                "value": 0.85,
                "fit": 0.8,
                "model": "Technology partnership"
            },
            {
                "profile": "Global Consulting Firm",
                "areas": ["Due diligence", "Integration planning", "Strategy"],
                "value": 0.8,
                "fit": 0.75,
                "model": "Service partnership"
            }
        ]

    def _identify_innovation_opportunities(self) -> List[Dict[str, Any]]:
        """Identify innovation opportunities for competitive advantage"""
        return [
            {
                "description": "AI-powered deal matching algorithm",
                "disruption": 0.8,
                "advantage": 0.9,
                "cost": 0.6,
                "timeline": 120,
                "patent": 0.7
            },
            {
                "description": "Blockchain-based escrow system",
                "disruption": 0.7,
                "advantage": 0.75,
                "cost": 0.7,
                "timeline": 180,
                "patent": 0.8
            },
            {
                "description": "Predictive valuation models",
                "disruption": 0.65,
                "advantage": 0.85,
                "cost": 0.5,
                "timeline": 90,
                "patent": 0.6
            }
        ]

    def _generate_positioning_recommendations(self) -> List[Dict[str, Any]]:
        """Generate market positioning recommendations"""
        return [
            {
                "recommendation": "Position as AI-First M&A Platform",
                "rationale": "Leverage superior AI capabilities for differentiation",
                "impact": 0.9,
                "feasibility": 0.85,
                "timeline": "3-6 months",
                "key_actions": [
                    "Enhance AI features visibility",
                    "Publish AI success metrics",
                    "Develop AI thought leadership"
                ]
            },
            {
                "recommendation": "Establish Wealth-Building Platform Leadership",
                "rationale": "Unique positioning in wealth creation through M&A",
                "impact": 0.95,
                "feasibility": 0.9,
                "timeline": "2-4 months",
                "key_actions": [
                    "Create wealth-building content",
                    "Showcase success stories",
                    "Build wealth-focused features"
                ]
            }
        ]

    def _generate_differentiation_recommendations(self) -> List[Dict[str, Any]]:
        """Generate differentiation recommendations"""
        return [
            {
                "recommendation": "Develop Proprietary Deal Intelligence",
                "rationale": "Create unique data-driven insights competitors can't match",
                "impact": 0.85,
                "feasibility": 0.8,
                "timeline": "4-6 months",
                "key_actions": [
                    "Build proprietary data sources",
                    "Develop unique analytics models",
                    "Create exclusive intelligence reports"
                ]
            }
        ]

    def _generate_competitive_response_recommendations(self) -> List[Dict[str, Any]]:
        """Generate competitive response recommendations"""
        return [
            {
                "recommendation": "Launch Competitive Displacement Campaign",
                "rationale": "Actively win customers from key competitors",
                "impact": 0.8,
                "feasibility": 0.75,
                "timeline": "2-3 months",
                "key_actions": [
                    "Identify competitor weaknesses",
                    "Create switching incentives",
                    "Develop comparison tools"
                ]
            }
        ]

    def _generate_market_recommendations(self) -> List[Dict[str, Any]]:
        """Generate market entry/exit recommendations"""
        return [
            {
                "recommendation": "Enter SMB M&A Market Segment",
                "rationale": "Large untapped market with limited competition",
                "impact": 0.85,
                "feasibility": 0.8,
                "timeline": "3-4 months",
                "key_actions": [
                    "Develop SMB-specific features",
                    "Create simplified pricing",
                    "Build SMB sales channel"
                ]
            }
        ]

    def _generate_partnership_recommendations(self) -> List[Dict[str, Any]]:
        """Generate partnership recommendations"""
        return [
            {
                "recommendation": "Form Strategic Alliance with Investment Banks",
                "rationale": "Access high-value deals and credibility",
                "impact": 0.9,
                "feasibility": 0.7,
                "timeline": "4-6 months",
                "key_actions": [
                    "Identify target partners",
                    "Develop partnership value proposition",
                    "Create integration roadmap"
                ]
            }
        ]

    def _generate_technology_recommendations(self) -> List[Dict[str, Any]]:
        """Generate technology recommendations"""
        return [
            {
                "recommendation": "Accelerate AI and ML Capabilities",
                "rationale": "Maintain technology leadership advantage",
                "impact": 0.9,
                "feasibility": 0.85,
                "timeline": "Ongoing",
                "key_actions": [
                    "Increase AI R&D investment",
                    "Hire ML experts",
                    "Develop proprietary models"
                ]
            }
        ]

    def _calculate_recommendation_priority(self, recommendation: Dict[str, Any]) -> float:
        """Calculate priority score for recommendation"""
        weights = {
            "impact": 0.4,
            "feasibility": 0.3,
            "urgency": 0.2,
            "resource_efficiency": 0.1
        }

        # Calculate urgency based on timeline
        timeline = recommendation.get("timeline", "")
        if "month" in timeline:
            months = int(timeline.split("-")[0])
            urgency = 1.0 - (months / 12)
        else:
            urgency = 0.5

        scores = {
            "impact": recommendation.get("impact", 0.5),
            "feasibility": recommendation.get("feasibility", 0.5),
            "urgency": urgency,
            "resource_efficiency": recommendation.get("feasibility", 0.5) / (1 + recommendation.get("impact", 0.5))
        }

        return sum(scores[key] * weights[key] for key in weights)

    def _calculate_competitive_advantage(self) -> float:
        """Calculate overall competitive advantage score"""
        our_capabilities = self._get_our_capabilities()
        avg_our = np.mean(list(our_capabilities.values()))

        if not self.competitors:
            return avg_our

        competitor_avgs = []
        for competitor in self.competitors.values():
            if competitor.key_capabilities:
                competitor_avgs.append(np.mean(list(competitor.key_capabilities.values())))

        if competitor_avgs:
            avg_competitors = np.mean(competitor_avgs)
            advantage = (avg_our - avg_competitors + 1) / 2  # Normalize to 0-1
            return round(min(max(advantage, 0), 1), 3)

        return avg_our

    def _assess_leadership_potential(self) -> float:
        """Assess potential for market leadership"""
        factors = {
            "competitive_advantage": self._calculate_competitive_advantage() * 0.3,
            "innovation_capability": 0.85 * 0.2,
            "market_position": 0.7 * 0.15,
            "growth_trajectory": 0.8 * 0.15,
            "resource_availability": 0.75 * 0.1,
            "strategic_vision": 0.9 * 0.1
        }

        return round(sum(factors.values()), 3)

    def _identify_strategic_options(self) -> List[Dict[str, Any]]:
        """Identify strategic options for competitive success"""
        return [
            {
                "option": "Aggressive Market Expansion",
                "description": "Rapidly expand into new market segments and geographies",
                "risk": 0.6,
                "reward": 0.9,
                "investment": 0.8,
                "timeline": "12-18 months"
            },
            {
                "option": "Platform Consolidation Strategy",
                "description": "Acquire smaller competitors to consolidate market",
                "risk": 0.7,
                "reward": 0.85,
                "investment": 0.9,
                "timeline": "18-24 months"
            },
            {
                "option": "Innovation Leadership",
                "description": "Focus on breakthrough innovation for competitive moat",
                "risk": 0.5,
                "reward": 0.95,
                "investment": 0.7,
                "timeline": "12-24 months"
            },
            {
                "option": "Ecosystem Orchestration",
                "description": "Build and control comprehensive M&A ecosystem",
                "risk": 0.4,
                "reward": 0.9,
                "investment": 0.6,
                "timeline": "18-36 months"
            },
            {
                "option": "Niche Domination",
                "description": "Dominate specific high-value market niches",
                "risk": 0.3,
                "reward": 0.75,
                "investment": 0.5,
                "timeline": "6-12 months"
            }
        ]

    def _assess_advantage_sustainability(self, capability: str, score: float) -> float:
        """Assess sustainability of competitive advantage"""
        # Factors that affect sustainability
        if capability in ["ai_analytics", "network_effects", "data_quality"]:
            return min(score + 0.1, 1.0)  # Hard to replicate
        elif capability in ["user_experience", "automation"]:
            return score * 0.9  # Moderately sustainable
        else:
            return score * 0.8  # More easily replicated

    def _assess_advantage_value(self, capability: str, score: float) -> float:
        """Assess value creation from competitive advantage"""
        value_multipliers = {
            "ai_analytics": 1.2,
            "deal_sourcing": 1.15,
            "network_effects": 1.25,
            "data_quality": 1.1,
            "user_experience": 1.05,
            "scalability": 1.15
        }

        multiplier = value_multipliers.get(capability, 1.0)
        return min(score * multiplier, 1.0)

    def _assess_vulnerability_impact(self, capability: str, score: float) -> float:
        """Assess impact of capability vulnerability"""
        critical_capabilities = ["ai_analytics", "deal_sourcing", "data_quality", "scalability"]

        if capability in critical_capabilities:
            return (1 - score) * 1.2
        else:
            return 1 - score

    def _calculate_mitigation_priority(self, capability: str, score: float) -> float:
        """Calculate priority for vulnerability mitigation"""
        impact = self._assess_vulnerability_impact(capability, score)
        urgency = 1 - score  # More urgent if capability is weaker
        feasibility = 0.7  # Assume moderate feasibility

        return (impact * 0.5 + urgency * 0.3 + feasibility * 0.2)

    def _calculate_gap_priority(self, capability: str, gap_size: float) -> float:
        """Calculate priority for closing capability gap"""
        importance = 0.8 if capability in ["ai_analytics", "deal_sourcing"] else 0.6
        return gap_size * importance

    def _suggest_gap_closing_strategy(self, capability: str) -> str:
        """Suggest strategy for closing capability gap"""
        strategies = {
            "ai_analytics": "Invest in AI research and talent acquisition",
            "deal_sourcing": "Build partnerships and enhance network effects",
            "technology": "Accelerate technology development and modernization",
            "partnerships": "Develop strategic alliance program",
            "default": "Develop targeted improvement program"
        }

        for key in strategies:
            if key in capability.lower():
                return strategies[key]
        return strategies["default"]

    def _calculate_acquisition_synergies(self, competitor: CompetitorProfile) -> float:
        """Calculate potential synergies from acquisition"""
        synergy_factors = {
            "customer_overlap": self._calculate_customer_overlap(competitor) * 0.3,
            "technology_complementarity": 0.7 * 0.25,
            "market_expansion": (1 - self._calculate_market_overlap(competitor)) * 0.2,
            "cost_savings": 0.6 * 0.15,
            "revenue_enhancement": 0.5 * 0.1
        }

        return sum(synergy_factors.values())

    def _assess_integration_complexity(self, competitor: CompetitorProfile) -> float:
        """Assess complexity of integrating acquired competitor"""
        complexity_factors = {
            "size_difference": min(competitor.revenue / 1000000, 1.0) * 0.25,
            "technology_differences": 0.6 * 0.25,
            "cultural_differences": 0.5 * 0.2,
            "geographic_spread": len(competitor.geographic_presence) / 10 * 0.15,
            "regulatory_issues": 0.4 * 0.15
        }

        return sum(complexity_factors.values())

    def _assess_acquisition_impact(self, competitor: CompetitorProfile) -> float:
        """Assess strategic impact of acquisition"""
        impact_factors = {
            "market_share_gain": competitor.market_share * 2,
            "capability_enhancement": 0.7,
            "competitive_elimination": competitor.threat_level,
            "ecosystem_expansion": len(competitor.partnerships) / 20,
            "technology_acquisition": len(competitor.technology_stack) / 15
        }

        return min(np.mean(list(impact_factors.values())), 1.0)


class CompetitiveIntelligenceEngine:
    """Engine for running competitive intelligence analysis"""

    def __init__(self):
        self.intelligence = CompetitiveIntelligence()
        self.analysis_cache = {}
        self.last_update = datetime.utcnow()

    async def run_analysis(self,
                          market_data: Dict[str, Any],
                          competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run comprehensive competitive intelligence analysis"""

        # Load competitor data
        for comp_data in competitor_data:
            competitor = CompetitorProfile(
                competitor_id=comp_data["id"],
                name=comp_data["name"],
                type=CompetitorType(comp_data.get("type", "direct")),
                market_position=MarketPosition(comp_data.get("position", "follower")),
                market_share=comp_data.get("market_share", 0.05),
                growth_rate=comp_data.get("growth_rate", 0.1),
                revenue=comp_data.get("revenue", 10000000),
                valuation=comp_data.get("valuation", 50000000),
                strengths=comp_data.get("strengths", []),
                weaknesses=comp_data.get("weaknesses", []),
                key_capabilities=comp_data.get("capabilities", {}),
                partnerships=set(comp_data.get("partnerships", [])),
                technology_stack=set(comp_data.get("technologies", [])),
                customer_segments=set(comp_data.get("segments", []))
            )
            self.intelligence.competitors[competitor.competitor_id] = competitor

        # Run competitive analysis
        analysis = await self.intelligence.analyze_competitive_landscape()

        # Generate strategic insights
        insights = self._generate_strategic_insights(analysis)

        # Cache results
        self.analysis_cache = {
            "analysis": analysis,
            "insights": insights,
            "timestamp": datetime.utcnow().isoformat()
        }

        return self.analysis_cache

    def _generate_strategic_insights(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate strategic insights from competitive analysis"""
        insights = []

        # Competitive positioning insights
        if analysis.get("competitive_advantage_score", 0) > 0.7:
            insights.append({
                "type": "strength",
                "insight": "Strong competitive advantage position",
                "recommendation": "Leverage advantages for aggressive growth",
                "confidence": 0.85
            })

        # Threat insights
        threats = analysis.get("competitive_threats", {})
        if threats.get("immediate_threats"):
            insights.append({
                "type": "warning",
                "insight": f"{len(threats['immediate_threats'])} immediate competitive threats identified",
                "recommendation": "Implement threat mitigation strategies urgently",
                "confidence": 0.9
            })

        # Opportunity insights
        opportunities = analysis.get("opportunities", [])
        if opportunities:
            top_opp = opportunities[0]
            insights.append({
                "type": "opportunity",
                "insight": f"High-value opportunity: {top_opp.get('opportunity', 'Market expansion')}",
                "recommendation": "Prioritize opportunity capture initiatives",
                "confidence": 0.8
            })

        # Strategic gap insights
        gaps = analysis.get("strategic_gaps", [])
        if gaps:
            critical_gaps = [g for g in gaps if g.get("priority", 0) > 0.8]
            if critical_gaps:
                insights.append({
                    "type": "action",
                    "insight": f"{len(critical_gaps)} critical strategic gaps identified",
                    "recommendation": "Address gaps to maintain competitive position",
                    "confidence": 0.85
                })

        return insights