"""
Strategic Recommendation Engine for M&A Platform

This module provides comprehensive strategic recommendations that synthesize insights from
all intelligence systems to provide actionable guidance for wealth-building optimization.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.cluster import KMeans
import logging

logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    COMPETITIVE = "competitive"
    INVESTMENT = "investment"
    PARTNERSHIP = "partnership"
    RISK_MITIGATION = "risk_mitigation"
    INNOVATION = "innovation"


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TimeHorizon(Enum):
    IMMEDIATE = "immediate"  # 0-30 days
    SHORT_TERM = "short_term"  # 1-6 months
    MEDIUM_TERM = "medium_term"  # 6-18 months
    LONG_TERM = "long_term"  # 18+ months


class ImplementationComplexity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class StrategicRecommendation:
    """Individual strategic recommendation"""
    recommendation_id: str
    title: str
    type: RecommendationType
    priority: Priority
    time_horizon: TimeHorizon
    complexity: ImplementationComplexity
    description: str
    rationale: str
    expected_impact: float  # 0-1 scale
    success_probability: float  # 0-1 scale
    confidence_level: float  # 0-1 scale
    investment_required: float
    expected_roi: float
    implementation_steps: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    alternative_options: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    resources_required: Dict[str, Any] = field(default_factory=dict)
    timeline_milestones: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecommendationBundle:
    """Bundle of related recommendations"""
    bundle_id: str
    name: str
    theme: str
    recommendations: List[StrategicRecommendation]
    synergy_score: float
    combined_impact: float
    implementation_sequence: List[str]
    total_investment: float
    total_roi: float
    bundle_risk: float
    estimated_timeline: int  # days


@dataclass
class StrategicInsight:
    """Strategic insight from intelligence analysis"""
    insight_id: str
    source: str  # Which intelligence system
    category: str
    insight: str
    impact_level: float
    urgency: float
    confidence: float
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    implications: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)


class StrategicRecommendationEngine:
    """Main strategic recommendation engine"""

    def __init__(self):
        self.recommendations: List[StrategicRecommendation] = []
        self.bundles: List[RecommendationBundle] = []
        self.insights: List[StrategicInsight] = []
        self.decision_model = None
        self.priority_model = None
        self.impact_model = None
        self._initialize_models()

    def _initialize_models(self):
        """Initialize ML models for recommendation engine"""
        self.decision_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            random_state=42
        )
        self.priority_model = KMeans(
            n_clusters=4,  # Critical, High, Medium, Low
            random_state=42
        )
        self.impact_model = DecisionTreeRegressor(
            max_depth=8,
            random_state=42
        )

    async def generate_strategic_recommendations(self,
                                               ecosystem_data: Dict[str, Any],
                                               partnership_data: Dict[str, Any],
                                               deal_data: Dict[str, Any],
                                               competitive_data: Dict[str, Any],
                                               wealth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive strategic recommendations"""
        try:
            # Synthesize insights from all intelligence systems
            insights = await self._synthesize_intelligence(
                ecosystem_data, partnership_data, deal_data,
                competitive_data, wealth_data
            )

            # Generate recommendations in parallel
            tasks = [
                self._generate_strategic_recommendations(insights),
                self._generate_operational_recommendations(insights),
                self._generate_financial_recommendations(insights),
                self._generate_competitive_recommendations(insights),
                self._generate_investment_recommendations(insights),
                self._generate_partnership_recommendations(insights),
                self._generate_risk_mitigation_recommendations(insights),
                self._generate_innovation_recommendations(insights)
            ]

            recommendation_sets = await asyncio.gather(*tasks, return_exceptions=True)

            # Combine all recommendations
            all_recommendations = []
            for rec_set in recommendation_sets:
                if isinstance(rec_set, list):
                    all_recommendations.extend(rec_set)

            # Prioritize and optimize recommendation portfolio
            optimized_recommendations = self._optimize_recommendation_portfolio(
                all_recommendations
            )

            # Create recommendation bundles
            bundles = self._create_recommendation_bundles(optimized_recommendations)

            # Generate execution roadmap
            roadmap = self._generate_execution_roadmap(optimized_recommendations, bundles)

            # Compile final output
            output = {
                "timestamp": datetime.utcnow().isoformat(),
                "executive_summary": self._generate_executive_summary(optimized_recommendations),
                "top_recommendations": optimized_recommendations[:10],
                "recommendation_bundles": bundles[:5],
                "execution_roadmap": roadmap,
                "strategic_insights": insights,
                "implementation_guide": self._create_implementation_guide(),
                "success_framework": self._create_success_framework(),
                "risk_assessment": self._assess_portfolio_risk(optimized_recommendations),
                "resource_requirements": self._calculate_resource_requirements(optimized_recommendations)
            }

            return output

        except Exception as e:
            logger.error(f"Strategic recommendation generation failed: {str(e)}")
            raise

    async def _synthesize_intelligence(self,
                                      ecosystem_data: Dict[str, Any],
                                      partnership_data: Dict[str, Any],
                                      deal_data: Dict[str, Any],
                                      competitive_data: Dict[str, Any],
                                      wealth_data: Dict[str, Any]) -> List[StrategicInsight]:
        """Synthesize insights from all intelligence systems"""
        insights = []

        # Extract insights from ecosystem intelligence
        if ecosystem_data:
            eco_insights = self._extract_ecosystem_insights(ecosystem_data)
            insights.extend(eco_insights)

        # Extract insights from partnership network
        if partnership_data:
            partner_insights = self._extract_partnership_insights(partnership_data)
            insights.extend(partner_insights)

        # Extract insights from deal flow optimization
        if deal_data:
            deal_insights = self._extract_deal_insights(deal_data)
            insights.extend(deal_insights)

        # Extract insights from competitive intelligence
        if competitive_data:
            competitive_insights = self._extract_competitive_insights(competitive_data)
            insights.extend(competitive_insights)

        # Extract insights from wealth analytics
        if wealth_data:
            wealth_insights = self._extract_wealth_insights(wealth_data)
            insights.extend(wealth_insights)

        # Cross-reference and validate insights
        validated_insights = self._validate_and_cross_reference_insights(insights)

        return validated_insights

    def _extract_ecosystem_insights(self, data: Dict[str, Any]) -> List[StrategicInsight]:
        """Extract insights from ecosystem intelligence"""
        insights = []

        # Market opportunities insights
        opportunities = data.get("opportunities", [])
        if opportunities:
            top_opportunity = opportunities[0]
            insights.append(StrategicInsight(
                insight_id="eco_01",
                source="ecosystem_intelligence",
                category="market_opportunity",
                insight=f"High-value market opportunity: {top_opportunity.get('description', 'Market expansion')}",
                impact_level=top_opportunity.get("value_potential", 0.8),
                urgency=0.8 if top_opportunity.get("time_sensitivity", "medium") == "high" else 0.6,
                confidence=top_opportunity.get("confidence", 0.75),
                supporting_data=top_opportunity,
                implications=["Accelerate market entry", "Allocate resources strategically"],
                recommended_actions=["Develop go-to-market strategy", "Secure market entry partnerships"]
            ))

        # Ecosystem gaps insights
        gaps = data.get("strategic_gaps", [])
        if gaps:
            critical_gaps = [g for g in gaps if g.get("impact", 0) > 0.7]
            if critical_gaps:
                insights.append(StrategicInsight(
                    insight_id="eco_02",
                    source="ecosystem_intelligence",
                    category="capability_gap",
                    insight=f"{len(critical_gaps)} critical ecosystem gaps identified",
                    impact_level=0.8,
                    urgency=0.9,
                    confidence=0.85,
                    supporting_data={"gaps": critical_gaps},
                    implications=["Address gaps urgently", "Risk of competitive disadvantage"],
                    recommended_actions=["Develop gap closure plan", "Accelerate capability building"]
                ))

        return insights

    def _extract_partnership_insights(self, data: Dict[str, Any]) -> List[StrategicInsight]:
        """Extract insights from partnership network analysis"""
        insights = []

        # Network opportunities
        opportunities = data.get("network_opportunities", [])
        if opportunities:
            high_value_opps = [o for o in opportunities if o.get("value", 0) > 0.8]
            if high_value_opps:
                insights.append(StrategicInsight(
                    insight_id="part_01",
                    source="partnership_network",
                    category="partnership_opportunity",
                    insight=f"{len(high_value_opps)} high-value partnership opportunities identified",
                    impact_level=0.85,
                    urgency=0.7,
                    confidence=0.8,
                    supporting_data={"opportunities": high_value_opps},
                    implications=["Accelerate partnership development", "Potential for significant value creation"],
                    recommended_actions=["Prioritize top partnerships", "Develop partnership strategy"]
                ))

        # Network vulnerabilities
        vulnerabilities = data.get("network_vulnerabilities", [])
        if vulnerabilities:
            critical_vulns = [v for v in vulnerabilities if v.get("severity", 0) > 0.7]
            if critical_vulns:
                insights.append(StrategicInsight(
                    insight_id="part_02",
                    source="partnership_network",
                    category="network_risk",
                    insight=f"{len(critical_vulns)} critical network vulnerabilities detected",
                    impact_level=0.7,
                    urgency=0.85,
                    confidence=0.8,
                    supporting_data={"vulnerabilities": critical_vulns},
                    implications=["Network risk exposure", "Potential partner dependencies"],
                    recommended_actions=["Diversify partner network", "Strengthen key relationships"]
                ))

        return insights

    def _extract_deal_insights(self, data: Dict[str, Any]) -> List[StrategicInsight]:
        """Extract insights from deal flow optimization"""
        insights = []

        # Pipeline optimization opportunities
        optimization = data.get("pipeline_optimization", {})
        if optimization:
            insights.append(StrategicInsight(
                insight_id="deal_01",
                source="deal_flow_optimization",
                category="operational_efficiency",
                insight="Significant deal pipeline optimization opportunity identified",
                impact_level=optimization.get("improvement_potential", 0.6),
                urgency=0.6,
                confidence=0.8,
                supporting_data=optimization,
                implications=["Improve deal conversion", "Increase revenue efficiency"],
                recommended_actions=["Implement pipeline automation", "Optimize deal scoring"]
            ))

        # Market timing insights
        timing = data.get("market_timing", {})
        if timing and timing.get("recommendation") == "accelerate":
            insights.append(StrategicInsight(
                insight_id="deal_02",
                source="deal_flow_optimization",
                category="market_timing",
                insight="Favorable market timing for deal acceleration",
                impact_level=0.8,
                urgency=0.9,
                confidence=timing.get("confidence", 0.7),
                supporting_data=timing,
                implications=["Market window opportunity", "Accelerate deal closure"],
                recommended_actions=["Increase deal velocity", "Capitalize on market conditions"]
            ))

        return insights

    def _extract_competitive_insights(self, data: Dict[str, Any]) -> List[StrategicInsight]:
        """Extract insights from competitive intelligence"""
        insights = []

        # Competitive threats
        threats = data.get("competitive_threats", {})
        immediate_threats = threats.get("immediate_threats", [])
        if immediate_threats:
            insights.append(StrategicInsight(
                insight_id="comp_01",
                source="competitive_intelligence",
                category="competitive_threat",
                insight=f"{len(immediate_threats)} immediate competitive threats identified",
                impact_level=0.8,
                urgency=0.95,
                confidence=0.85,
                supporting_data={"threats": immediate_threats},
                implications=["Competitive pressure increasing", "Market share at risk"],
                recommended_actions=["Implement competitive response", "Strengthen differentiation"]
            ))

        # Competitive advantages
        advantages = data.get("market_positioning", {}).get("competitive_advantages", [])
        if advantages:
            strong_advantages = [a for a in advantages if a.get("sustainability", 0) > 0.8]
            if strong_advantages:
                insights.append(StrategicInsight(
                    insight_id="comp_02",
                    source="competitive_intelligence",
                    category="competitive_advantage",
                    insight=f"Strong competitive advantages in {len(strong_advantages)} areas",
                    impact_level=0.85,
                    urgency=0.5,
                    confidence=0.8,
                    supporting_data={"advantages": strong_advantages},
                    implications=["Sustainable competitive position", "Leverage for growth"],
                    recommended_actions=["Amplify advantages", "Build on strengths"]
                ))

        return insights

    def _extract_wealth_insights(self, data: Dict[str, Any]) -> List[StrategicInsight]:
        """Extract insights from wealth analytics"""
        insights = []

        # Progress tracking insights
        progress = data.get("progress_tracking", {})
        if progress.get("acceleration_needed"):
            insights.append(StrategicInsight(
                insight_id="wealth_01",
                source="wealth_analytics",
                category="wealth_acceleration",
                insight="Wealth building acceleration required to meet targets",
                impact_level=0.9,
                urgency=0.85,
                confidence=0.8,
                supporting_data=progress,
                implications=["Behind wealth targets", "Need strategic intervention"],
                recommended_actions=["Implement acceleration tactics", "Optimize wealth strategy"]
            ))

        # Investment opportunities
        investments = data.get("investment_opportunities", [])
        if investments:
            high_roi_investments = [i for i in investments if i.get("risk_adjusted_return", 0) > 0.5]
            if high_roi_investments:
                insights.append(StrategicInsight(
                    insight_id="wealth_02",
                    source="wealth_analytics",
                    category="investment_opportunity",
                    insight=f"{len(high_roi_investments)} high-ROI investment opportunities available",
                    impact_level=0.8,
                    urgency=0.6,
                    confidence=0.75,
                    supporting_data={"opportunities": high_roi_investments},
                    implications=["Accelerate wealth growth", "Strategic investment potential"],
                    recommended_actions=["Evaluate top investments", "Allocate capital strategically"]
                ))

        return insights

    def _validate_and_cross_reference_insights(self, insights: List[StrategicInsight]) -> List[StrategicInsight]:
        """Validate and cross-reference insights across systems"""
        validated_insights = []

        # Remove duplicates and conflicts
        unique_insights = {}
        for insight in insights:
            key = f"{insight.category}_{insight.insight[:50]}"
            if key not in unique_insights or insight.confidence > unique_insights[key].confidence:
                unique_insights[key] = insight

        # Cross-reference for synergies
        for insight in unique_insights.values():
            # Add cross-references where applicable
            synergies = self._identify_insight_synergies(insight, list(unique_insights.values()))
            if synergies:
                insight.metadata["synergies"] = synergies

            validated_insights.append(insight)

        # Sort by impact and urgency
        validated_insights.sort(key=lambda x: x.impact_level * x.urgency, reverse=True)

        return validated_insights

    def _identify_insight_synergies(self, insight: StrategicInsight, all_insights: List[StrategicInsight]) -> List[str]:
        """Identify synergies between insights"""
        synergies = []

        for other in all_insights:
            if other.insight_id != insight.insight_id:
                # Check for thematic connections
                if insight.category == "partnership_opportunity" and other.category == "capability_gap":
                    synergies.append(f"Partnership could address capability gap: {other.insight_id}")
                elif insight.category == "competitive_advantage" and other.category == "market_opportunity":
                    synergies.append(f"Advantage supports market opportunity: {other.insight_id}")
                elif insight.category == "investment_opportunity" and other.category == "wealth_acceleration":
                    synergies.append(f"Investment supports wealth acceleration: {other.insight_id}")

        return synergies

    async def _generate_strategic_recommendations(self, insights: List[StrategicInsight]) -> List[StrategicRecommendation]:
        """Generate strategic recommendations"""
        recommendations = []

        # Market leadership strategy
        market_insights = [i for i in insights if "market" in i.category]
        if market_insights:
            recommendations.append(StrategicRecommendation(
                recommendation_id="strat_01",
                title="Accelerate Market Leadership Position",
                type=RecommendationType.STRATEGIC,
                priority=Priority.HIGH,
                time_horizon=TimeHorizon.MEDIUM_TERM,
                complexity=ImplementationComplexity.HIGH,
                description="Establish dominant market position through strategic initiatives and competitive advantages",
                rationale="Multiple market opportunities identified with strong competitive advantages",
                expected_impact=0.85,
                success_probability=0.75,
                confidence_level=0.80,
                investment_required=5000000,
                expected_roi=3.5,
                implementation_steps=[
                    "Conduct market entry analysis",
                    "Develop go-to-market strategy",
                    "Secure strategic partnerships",
                    "Execute market expansion plan",
                    "Monitor and optimize market position"
                ],
                success_metrics=[
                    "Market share increase to 25%",
                    "Revenue growth of 300%",
                    "Customer acquisition rate 5x"
                ],
                risk_factors=[
                    "Competitive response",
                    "Market conditions change",
                    "Execution challenges"
                ],
                stakeholders=["CEO", "VP Sales", "VP Marketing", "Product team"],
                timeline_milestones=[
                    {"milestone": "Strategy completion", "days": 30},
                    {"milestone": "Partnership agreements", "days": 90},
                    {"milestone": "Market entry", "days": 180},
                    {"milestone": "Leadership position", "days": 365}
                ]
            ))

        # Platform ecosystem strategy
        ecosystem_insights = [i for i in insights if i.source == "ecosystem_intelligence"]
        if ecosystem_insights:
            recommendations.append(StrategicRecommendation(
                recommendation_id="strat_02",
                title="Build Comprehensive Platform Ecosystem",
                type=RecommendationType.STRATEGIC,
                priority=Priority.HIGH,
                time_horizon=TimeHorizon.LONG_TERM,
                complexity=ImplementationComplexity.VERY_HIGH,
                description="Create comprehensive ecosystem that becomes the central hub for M&A activity",
                rationale="Network effects and ecosystem gaps present opportunity for platform dominance",
                expected_impact=0.90,
                success_probability=0.70,
                confidence_level=0.75,
                investment_required=10000000,
                expected_roi=5.0,
                implementation_steps=[
                    "Design ecosystem architecture",
                    "Develop core platform capabilities",
                    "Recruit ecosystem partners",
                    "Launch platform marketplace",
                    "Scale ecosystem network"
                ],
                success_metrics=[
                    "100+ ecosystem partners",
                    "10x transaction volume",
                    "Platform fee revenue $50M+"
                ],
                risk_factors=[
                    "Complex execution",
                    "Partner adoption challenges",
                    "Competitive ecosystem responses"
                ]
            ))

        return recommendations

    async def _generate_operational_recommendations(self, insights: List[StrategicInsight]) -> List[StrategicRecommendation]:
        """Generate operational recommendations"""
        recommendations = []

        # Process automation
        efficiency_insights = [i for i in insights if "efficiency" in i.category]
        if efficiency_insights:
            recommendations.append(StrategicRecommendation(
                recommendation_id="ops_01",
                title="Implement End-to-End Process Automation",
                type=RecommendationType.OPERATIONAL,
                priority=Priority.HIGH,
                time_horizon=TimeHorizon.SHORT_TERM,
                complexity=ImplementationComplexity.MEDIUM,
                description="Automate core M&A processes to improve efficiency and reduce costs",
                rationale="Operational efficiency gaps identified with high automation potential",
                expected_impact=0.70,
                success_probability=0.85,
                confidence_level=0.85,
                investment_required=500000,
                expected_roi=4.0,
                implementation_steps=[
                    "Map current processes",
                    "Identify automation opportunities",
                    "Develop automation systems",
                    "Test and validate automation",
                    "Deploy and monitor"
                ],
                success_metrics=[
                    "80% process automation",
                    "50% cost reduction",
                    "3x processing speed"
                ]
            ))

        # Customer success optimization
        recommendations.append(StrategicRecommendation(
            recommendation_id="ops_02",
            title="Optimize Customer Success Operations",
            type=RecommendationType.OPERATIONAL,
            priority=Priority.MEDIUM,
            time_horizon=TimeHorizon.SHORT_TERM,
            complexity=ImplementationComplexity.MEDIUM,
            description="Enhance customer success processes to improve retention and expansion",
            rationale="Customer lifetime value optimization opportunity identified",
            expected_impact=0.60,
            success_probability=0.80,
            confidence_level=0.80,
            investment_required=200000,
            expected_roi=6.0,
            implementation_steps=[
                "Analyze customer journey",
                "Implement success metrics",
                "Develop proactive support",
                "Create expansion playbooks",
                "Monitor and optimize"
            ],
            success_metrics=[
                "95% customer retention",
                "3x expansion revenue",
                "NPS score >70"
            ]
        ))

        return recommendations

    async def _generate_financial_recommendations(self, insights: List[StrategicInsight]) -> List[StrategicRecommendation]:
        """Generate financial recommendations"""
        recommendations = []

        # Revenue optimization
        wealth_insights = [i for i in insights if i.source == "wealth_analytics"]
        if wealth_insights:
            recommendations.append(StrategicRecommendation(
                recommendation_id="fin_01",
                title="Implement Multi-Tier Revenue Model",
                type=RecommendationType.FINANCIAL,
                priority=Priority.CRITICAL,
                time_horizon=TimeHorizon.IMMEDIATE,
                complexity=ImplementationComplexity.LOW,
                description="Launch premium pricing tiers and success-based fees to accelerate revenue",
                rationale="Wealth acceleration needed and revenue optimization opportunities identified",
                expected_impact=0.80,
                success_probability=0.90,
                confidence_level=0.85,
                investment_required=100000,
                expected_roi=10.0,
                implementation_steps=[
                    "Design pricing tiers",
                    "Develop premium features",
                    "Create success fee model",
                    "Launch to market",
                    "Optimize pricing"
                ],
                success_metrics=[
                    "200% revenue increase",
                    "50% margin improvement",
                    "3x ARPU growth"
                ]
            ))

        # Capital optimization
        recommendations.append(StrategicRecommendation(
            recommendation_id="fin_02",
            title="Optimize Capital Structure and Funding",
            type=RecommendationType.FINANCIAL,
            priority=Priority.HIGH,
            time_horizon=TimeHorizon.SHORT_TERM,
            complexity=ImplementationComplexity.HIGH,
            description="Optimize capital structure and secure growth funding for strategic initiatives",
            rationale="Growth capital needs identified for strategic execution",
            expected_impact=0.75,
            success_probability=0.75,
            confidence_level=0.70,
            investment_required=0,  # Structure optimization
            expected_roi=2.5,
            implementation_steps=[
                "Analyze capital needs",
                "Evaluate funding options",
                "Prepare funding materials",
                "Execute funding strategy",
                "Optimize capital deployment"
            ],
            success_metrics=[
                "$20M growth capital secured",
                "Optimal debt-equity ratio",
                "Reduced cost of capital"
            ]
        ))

        return recommendations

    async def _generate_competitive_recommendations(self, insights: List[StrategicInsight]) -> List[StrategicRecommendation]:
        """Generate competitive recommendations"""
        recommendations = []

        # Competitive response
        comp_insights = [i for i in insights if i.source == "competitive_intelligence"]
        threat_insights = [i for i in comp_insights if "threat" in i.category]
        if threat_insights:
            recommendations.append(StrategicRecommendation(
                recommendation_id="comp_01",
                title="Execute Competitive Defense Strategy",
                type=RecommendationType.COMPETITIVE,
                priority=Priority.CRITICAL,
                time_horizon=TimeHorizon.IMMEDIATE,
                complexity=ImplementationComplexity.MEDIUM,
                description="Implement immediate competitive response to protect market position",
                rationale="Immediate competitive threats identified requiring urgent response",
                expected_impact=0.70,
                success_probability=0.80,
                confidence_level=0.85,
                investment_required=1000000,
                expected_roi=3.0,
                implementation_steps=[
                    "Assess threat severity",
                    "Develop response strategy",
                    "Implement countermeasures",
                    "Monitor competitive dynamics",
                    "Adjust strategy as needed"
                ],
                success_metrics=[
                    "Market share defended",
                    "Customer retention >95%",
                    "Competitive parity maintained"
                ]
            ))

        # Differentiation strategy
        advantage_insights = [i for i in comp_insights if "advantage" in i.category]
        if advantage_insights:
            recommendations.append(StrategicRecommendation(
                recommendation_id="comp_02",
                title="Amplify Competitive Differentiation",
                type=RecommendationType.COMPETITIVE,
                priority=Priority.HIGH,
                time_horizon=TimeHorizon.SHORT_TERM,
                complexity=ImplementationComplexity.MEDIUM,
                description="Strengthen and amplify competitive advantages for market leadership",
                rationale="Strong competitive advantages identified that can be leveraged for growth",
                expected_impact=0.80,
                success_probability=0.85,
                confidence_level=0.80,
                investment_required=750000,
                expected_roi=4.0,
                implementation_steps=[
                    "Identify unique advantages",
                    "Develop amplification strategy",
                    "Enhance differentiating features",
                    "Market advantages effectively",
                    "Monitor competitive responses"
                ],
                success_metrics=[
                    "Brand differentiation score >80%",
                    "Premium pricing acceptance",
                    "Competitive wins 80%+"
                ]
            ))

        return recommendations

    async def _generate_investment_recommendations(self, insights: List[StrategicInsight]) -> List[StrategicRecommendation]:
        """Generate investment recommendations"""
        recommendations = []

        # Strategic acquisitions
        investment_insights = [i for i in insights if "investment" in i.category]
        if investment_insights:
            recommendations.append(StrategicRecommendation(
                recommendation_id="inv_01",
                title="Execute Strategic Acquisition Program",
                type=RecommendationType.INVESTMENT,
                priority=Priority.HIGH,
                time_horizon=TimeHorizon.MEDIUM_TERM,
                complexity=ImplementationComplexity.VERY_HIGH,
                description="Acquire strategic targets to accelerate growth and capabilities",
                rationale="High-ROI acquisition opportunities identified for strategic expansion",
                expected_impact=0.85,
                success_probability=0.65,
                confidence_level=0.70,
                investment_required=15000000,
                expected_roi=2.5,
                implementation_steps=[
                    "Develop acquisition criteria",
                    "Identify target companies",
                    "Conduct due diligence",
                    "Negotiate and close deals",
                    "Execute integration plan"
                ],
                success_metrics=[
                    "2-3 strategic acquisitions",
                    "Synergy realization $5M+",
                    "Market expansion achieved"
                ]
            ))

        # Technology investments
        recommendations.append(StrategicRecommendation(
            recommendation_id="inv_02",
            title="Accelerate AI and Technology Investment",
            type=RecommendationType.INVESTMENT,
            priority=Priority.HIGH,
            time_horizon=TimeHorizon.SHORT_TERM,
            complexity=ImplementationComplexity.HIGH,
            description="Invest in advanced AI and technology capabilities for competitive advantage",
            rationale="Technology leadership opportunity identified for sustainable differentiation",
            expected_impact=0.90,
            success_probability=0.80,
            confidence_level=0.85,
            investment_required=3000000,
            expected_roi=5.0,
            implementation_steps=[
                "Define technology roadmap",
                "Invest in AI research",
                "Hire technology talent",
                "Develop proprietary capabilities",
                "Deploy advanced features"
            ],
            success_metrics=[
                "AI capability leadership",
                "Patent portfolio growth",
                "Technology ROI >400%"
            ]
        ))

        return recommendations

    async def _generate_partnership_recommendations(self, insights: List[StrategicInsight]) -> List[StrategicRecommendation]:
        """Generate partnership recommendations"""
        recommendations = []

        # Strategic alliances
        partnership_insights = [i for i in insights if "partnership" in i.category]
        if partnership_insights:
            recommendations.append(StrategicRecommendation(
                recommendation_id="part_01",
                title="Build Strategic Alliance Network",
                type=RecommendationType.PARTNERSHIP,
                priority=Priority.HIGH,
                time_horizon=TimeHorizon.SHORT_TERM,
                complexity=ImplementationComplexity.MEDIUM,
                description="Establish strategic alliances with key ecosystem players",
                rationale="High-value partnership opportunities identified for mutual growth",
                expected_impact=0.80,
                success_probability=0.75,
                confidence_level=0.80,
                investment_required=500000,
                expected_roi=6.0,
                implementation_steps=[
                    "Identify strategic partners",
                    "Develop partnership strategy",
                    "Negotiate alliance agreements",
                    "Launch joint initiatives",
                    "Monitor partnership value"
                ],
                success_metrics=[
                    "5 strategic alliances signed",
                    "10x deal flow increase",
                    "Partnership revenue $10M+"
                ]
            ))

        return recommendations

    async def _generate_risk_mitigation_recommendations(self, insights: List[StrategicInsight]) -> List[StrategicRecommendation]:
        """Generate risk mitigation recommendations"""
        recommendations = []

        # Portfolio risk management
        risk_insights = [i for i in insights if "risk" in i.category]
        if risk_insights:
            recommendations.append(StrategicRecommendation(
                recommendation_id="risk_01",
                title="Implement Comprehensive Risk Management",
                type=RecommendationType.RISK_MITIGATION,
                priority=Priority.HIGH,
                time_horizon=TimeHorizon.SHORT_TERM,
                complexity=ImplementationComplexity.MEDIUM,
                description="Establish robust risk management framework across all operations",
                rationale="Risk exposures identified requiring systematic mitigation approach",
                expected_impact=0.60,
                success_probability=0.85,
                confidence_level=0.80,
                investment_required=300000,
                expected_roi=4.0,
                implementation_steps=[
                    "Assess risk landscape",
                    "Develop risk framework",
                    "Implement risk controls",
                    "Monitor risk metrics",
                    "Optimize risk profile"
                ],
                success_metrics=[
                    "Risk score <30%",
                    "Zero critical incidents",
                    "Risk-adjusted returns >20%"
                ]
            ))

        return recommendations

    async def _generate_innovation_recommendations(self, insights: List[StrategicInsight]) -> List[StrategicRecommendation]:
        """Generate innovation recommendations"""
        recommendations = []

        # Product innovation
        recommendations.append(StrategicRecommendation(
            recommendation_id="innov_01",
            title="Launch Innovation Lab and R&D Program",
            type=RecommendationType.INNOVATION,
            priority=Priority.MEDIUM,
            time_horizon=TimeHorizon.MEDIUM_TERM,
            complexity=ImplementationComplexity.HIGH,
            description="Establish dedicated innovation capabilities for breakthrough development",
            rationale="Innovation opportunities identified for sustainable competitive advantage",
            expected_impact=0.85,
            success_probability=0.70,
            confidence_level=0.75,
            investment_required=2000000,
            expected_roi=3.5,
            implementation_steps=[
                "Establish innovation lab",
                "Hire innovation talent",
                "Develop innovation process",
                "Launch innovation projects",
                "Commercialize innovations"
            ],
            success_metrics=[
                "10 innovation projects",
                "3 breakthrough products",
                "Innovation revenue $5M+"
            ]
        ))

        return recommendations

    def _optimize_recommendation_portfolio(self, recommendations: List[StrategicRecommendation]) -> List[StrategicRecommendation]:
        """Optimize the portfolio of recommendations"""
        # Calculate priority scores
        for rec in recommendations:
            rec.metadata["priority_score"] = self._calculate_priority_score(rec)

        # Remove conflicts and optimize portfolio
        optimized = self._resolve_conflicts_and_optimize(recommendations)

        # Sort by priority score
        optimized.sort(key=lambda x: x.metadata["priority_score"], reverse=True)

        return optimized

    def _calculate_priority_score(self, recommendation: StrategicRecommendation) -> float:
        """Calculate priority score for recommendation"""
        # Weight different factors
        weights = {
            "impact": 0.30,
            "probability": 0.25,
            "urgency": 0.20,
            "roi": 0.15,
            "confidence": 0.10
        }

        # Map priority to urgency score
        urgency_map = {
            Priority.CRITICAL: 1.0,
            Priority.HIGH: 0.8,
            Priority.MEDIUM: 0.5,
            Priority.LOW: 0.2
        }

        # Calculate components
        impact = recommendation.expected_impact
        probability = recommendation.success_probability
        urgency = urgency_map.get(recommendation.priority, 0.5)
        roi = min(recommendation.expected_roi / 10, 1.0)  # Normalize ROI
        confidence = recommendation.confidence_level

        # Calculate weighted score
        score = (
            impact * weights["impact"] +
            probability * weights["probability"] +
            urgency * weights["urgency"] +
            roi * weights["roi"] +
            confidence * weights["confidence"]
        )

        return round(score, 3)

    def _resolve_conflicts_and_optimize(self, recommendations: List[StrategicRecommendation]) -> List[StrategicRecommendation]:
        """Resolve conflicts and optimize recommendation portfolio"""
        # Simple conflict resolution - would be more sophisticated in production

        # Group by type
        by_type = {}
        for rec in recommendations:
            if rec.type not in by_type:
                by_type[rec.type] = []
            by_type[rec.type].append(rec)

        # Select best from each type (simplified)
        optimized = []
        for rec_type, recs in by_type.items():
            # Sort by priority score and take top recommendations
            recs.sort(key=lambda x: x.metadata.get("priority_score", 0), reverse=True)
            # Take top 2-3 from each category
            limit = 3 if rec_type == RecommendationType.STRATEGIC else 2
            optimized.extend(recs[:limit])

        return optimized

    def _create_recommendation_bundles(self, recommendations: List[StrategicRecommendation]) -> List[RecommendationBundle]:
        """Create bundles of synergistic recommendations"""
        bundles = []

        # Growth acceleration bundle
        growth_recs = [r for r in recommendations if any(
            keyword in r.description.lower()
            for keyword in ["growth", "revenue", "market", "customer"]
        )]

        if len(growth_recs) >= 2:
            bundles.append(RecommendationBundle(
                bundle_id="bundle_01",
                name="Growth Acceleration Bundle",
                theme="Accelerate revenue growth and market expansion",
                recommendations=growth_recs[:4],
                synergy_score=0.85,
                combined_impact=0.90,
                implementation_sequence=[r.recommendation_id for r in growth_recs[:4]],
                total_investment=sum(r.investment_required for r in growth_recs[:4]),
                total_roi=np.mean([r.expected_roi for r in growth_recs[:4]]),
                bundle_risk=0.4,
                estimated_timeline=180
            ))

        # Competitive advantage bundle
        comp_recs = [r for r in recommendations if any(
            keyword in r.description.lower()
            for keyword in ["competitive", "advantage", "differentiation", "leadership"]
        )]

        if len(comp_recs) >= 2:
            bundles.append(RecommendationBundle(
                bundle_id="bundle_02",
                name="Competitive Advantage Bundle",
                theme="Build sustainable competitive advantages",
                recommendations=comp_recs[:3],
                synergy_score=0.80,
                combined_impact=0.85,
                implementation_sequence=[r.recommendation_id for r in comp_recs[:3]],
                total_investment=sum(r.investment_required for r in comp_recs[:3]),
                total_roi=np.mean([r.expected_roi for r in comp_recs[:3]]),
                bundle_risk=0.5,
                estimated_timeline=270
            ))

        # Operational excellence bundle
        ops_recs = [r for r in recommendations if any(
            keyword in r.description.lower()
            for keyword in ["operational", "efficiency", "automation", "process"]
        )]

        if len(ops_recs) >= 2:
            bundles.append(RecommendationBundle(
                bundle_id="bundle_03",
                name="Operational Excellence Bundle",
                theme="Optimize operations for efficiency and scale",
                recommendations=ops_recs[:3],
                synergy_score=0.75,
                combined_impact=0.70,
                implementation_sequence=[r.recommendation_id for r in ops_recs[:3]],
                total_investment=sum(r.investment_required for r in ops_recs[:3]),
                total_roi=np.mean([r.expected_roi for r in ops_recs[:3]]),
                bundle_risk=0.3,
                estimated_timeline=120
            ))

        return bundles

    def _generate_execution_roadmap(self,
                                   recommendations: List[StrategicRecommendation],
                                   bundles: List[RecommendationBundle]) -> Dict[str, Any]:
        """Generate execution roadmap"""
        roadmap = {
            "phases": [],
            "critical_path": [],
            "resource_timeline": {},
            "milestone_calendar": [],
            "risk_windows": []
        }

        # Phase 1: Immediate (0-30 days)
        immediate_recs = [r for r in recommendations if r.time_horizon == TimeHorizon.IMMEDIATE]
        roadmap["phases"].append({
            "phase": "Phase 1: Immediate Actions",
            "timeframe": "0-30 days",
            "objectives": "Address critical and urgent items",
            "recommendations": [r.recommendation_id for r in immediate_recs],
            "key_outcomes": ["Revenue acceleration", "Competitive defense", "Risk mitigation"],
            "success_criteria": "All immediate actions completed on time"
        })

        # Phase 2: Short-term (1-6 months)
        short_term_recs = [r for r in recommendations if r.time_horizon == TimeHorizon.SHORT_TERM]
        roadmap["phases"].append({
            "phase": "Phase 2: Foundation Building",
            "timeframe": "1-6 months",
            "objectives": "Build capabilities and partnerships",
            "recommendations": [r.recommendation_id for r in short_term_recs],
            "key_outcomes": ["Operational efficiency", "Strategic partnerships", "Market position"],
            "success_criteria": "Foundation elements in place for scaling"
        })

        # Phase 3: Medium-term (6-18 months)
        medium_term_recs = [r for r in recommendations if r.time_horizon == TimeHorizon.MEDIUM_TERM]
        roadmap["phases"].append({
            "phase": "Phase 3: Scale and Expand",
            "timeframe": "6-18 months",
            "objectives": "Scale operations and expand market presence",
            "recommendations": [r.recommendation_id for r in medium_term_recs],
            "key_outcomes": ["Market leadership", "Ecosystem development", "Revenue scale"],
            "success_criteria": "Market leading position achieved"
        })

        # Phase 4: Long-term (18+ months)
        long_term_recs = [r for r in recommendations if r.time_horizon == TimeHorizon.LONG_TERM]
        roadmap["phases"].append({
            "phase": "Phase 4: Dominance and Optimization",
            "timeframe": "18+ months",
            "objectives": "Achieve market dominance and wealth targets",
            "recommendations": [r.recommendation_id for r in long_term_recs],
            "key_outcomes": ["Market dominance", "Wealth targets", "Exit readiness"],
            "success_criteria": "£200M wealth target achieved"
        })

        # Critical path analysis
        critical_recs = [r for r in recommendations if r.priority in [Priority.CRITICAL, Priority.HIGH]]
        roadmap["critical_path"] = [
            {
                "item": r.title,
                "id": r.recommendation_id,
                "start_offset": self._get_start_offset(r.time_horizon),
                "duration": self._estimate_duration(r.complexity),
                "dependencies": r.dependencies
            }
            for r in critical_recs
        ]

        # Resource timeline
        roadmap["resource_timeline"] = self._create_resource_timeline(recommendations)

        # Milestone calendar
        roadmap["milestone_calendar"] = self._create_milestone_calendar(recommendations, bundles)

        return roadmap

    def _get_start_offset(self, time_horizon: TimeHorizon) -> int:
        """Get start offset in days for time horizon"""
        offsets = {
            TimeHorizon.IMMEDIATE: 0,
            TimeHorizon.SHORT_TERM: 30,
            TimeHorizon.MEDIUM_TERM: 180,
            TimeHorizon.LONG_TERM: 540
        }
        return offsets.get(time_horizon, 0)

    def _estimate_duration(self, complexity: ImplementationComplexity) -> int:
        """Estimate duration in days based on complexity"""
        durations = {
            ImplementationComplexity.LOW: 30,
            ImplementationComplexity.MEDIUM: 90,
            ImplementationComplexity.HIGH: 180,
            ImplementationComplexity.VERY_HIGH: 365
        }
        return durations.get(complexity, 90)

    def _create_resource_timeline(self, recommendations: List[StrategicRecommendation]) -> Dict[str, Any]:
        """Create resource allocation timeline"""
        timeline = {
            "financial": {},
            "human": {},
            "technology": {}
        }

        # Aggregate by quarter
        quarters = ["Q1", "Q2", "Q3", "Q4"]
        for quarter in quarters:
            timeline["financial"][quarter] = 0
            timeline["human"][quarter] = 0
            timeline["technology"][quarter] = 0

        # Simple allocation - would be more sophisticated in production
        for rec in recommendations:
            quarter_index = min(self._get_start_offset(rec.time_horizon) // 90, 3)
            quarter = quarters[quarter_index]

            timeline["financial"][quarter] += rec.investment_required
            timeline["human"][quarter] += rec.resources_required.get("people", 5)
            timeline["technology"][quarter] += rec.resources_required.get("tech_budget", 100000)

        return timeline

    def _create_milestone_calendar(self,
                                  recommendations: List[StrategicRecommendation],
                                  bundles: List[RecommendationBundle]) -> List[Dict[str, Any]]:
        """Create milestone calendar"""
        milestones = []
        base_date = datetime.utcnow()

        # Add recommendation milestones
        for rec in recommendations:
            if rec.timeline_milestones:
                for milestone in rec.timeline_milestones:
                    milestones.append({
                        "date": (base_date + timedelta(days=milestone["days"])).isoformat(),
                        "milestone": milestone["milestone"],
                        "type": "recommendation",
                        "source": rec.recommendation_id,
                        "importance": "high" if rec.priority == Priority.CRITICAL else "medium"
                    })

        # Add bundle milestones
        for bundle in bundles:
            milestones.append({
                "date": (base_date + timedelta(days=bundle.estimated_timeline)).isoformat(),
                "milestone": f"{bundle.name} completion",
                "type": "bundle",
                "source": bundle.bundle_id,
                "importance": "high"
            })

        # Sort by date
        milestones.sort(key=lambda x: x["date"])

        return milestones

    def _generate_executive_summary(self, recommendations: List[StrategicRecommendation]) -> Dict[str, Any]:
        """Generate executive summary of recommendations"""
        summary = {
            "overview": "",
            "key_themes": [],
            "priority_actions": [],
            "investment_summary": {},
            "expected_outcomes": {},
            "success_timeline": ""
        }

        # Overview
        summary["overview"] = f"Strategic analysis identified {len(recommendations)} high-impact recommendations across {len(set(r.type for r in recommendations))} categories to accelerate wealth building and market position."

        # Key themes
        themes = {}
        for rec in recommendations:
            theme_key = rec.type.value.replace("_", " ").title()
            if theme_key not in themes:
                themes[theme_key] = 0
            themes[theme_key] += 1

        summary["key_themes"] = [
            {"theme": theme, "count": count}
            for theme, count in sorted(themes.items(), key=lambda x: x[1], reverse=True)
        ]

        # Priority actions (top 5)
        top_recs = recommendations[:5]
        summary["priority_actions"] = [
            {
                "action": rec.title,
                "timeline": rec.time_horizon.value,
                "impact": rec.expected_impact,
                "investment": rec.investment_required
            }
            for rec in top_recs
        ]

        # Investment summary
        total_investment = sum(r.investment_required for r in recommendations)
        weighted_roi = np.average([r.expected_roi for r in recommendations],
                                 weights=[r.investment_required for r in recommendations])

        summary["investment_summary"] = {
            "total_investment": total_investment,
            "weighted_average_roi": weighted_roi,
            "expected_returns": total_investment * weighted_roi,
            "payback_period": "12-18 months"
        }

        # Expected outcomes
        summary["expected_outcomes"] = {
            "revenue_growth": "300-500%",
            "market_position": "Top 3 player",
            "wealth_acceleration": "2-3x current trajectory",
            "competitive_advantage": "Sustainable differentiation",
            "platform_value": "£500M+ valuation"
        }

        # Success timeline
        summary["success_timeline"] = "18-24 months to achieve market leadership position and wealth targets"

        return summary

    def _create_implementation_guide(self) -> Dict[str, Any]:
        """Create implementation guide"""
        return {
            "getting_started": {
                "first_30_days": [
                    "Form strategic implementation team",
                    "Prioritize critical recommendations",
                    "Secure initial funding",
                    "Begin immediate actions"
                ],
                "success_factors": [
                    "Executive commitment",
                    "Resource availability",
                    "Clear accountability",
                    "Regular monitoring"
                ]
            },
            "execution_principles": [
                "Start with high-impact, low-complexity items",
                "Build momentum through early wins",
                "Monitor progress against milestones",
                "Adapt strategy based on results",
                "Maintain focus on wealth objectives"
            ],
            "governance": {
                "steering_committee": "CEO, CFO, VP Strategy",
                "review_frequency": "Weekly for critical items, monthly for others",
                "decision_authority": "Clear RACI matrix for all recommendations",
                "escalation_process": "Issues escalated within 48 hours"
            },
            "change_management": {
                "communication": "Regular all-hands updates on progress",
                "training": "Skills development for new capabilities",
                "culture": "Innovation and execution mindset",
                "resistance": "Address concerns proactively"
            }
        }

    def _create_success_framework(self) -> Dict[str, Any]:
        """Create success measurement framework"""
        return {
            "kpi_dashboard": {
                "financial": [
                    "Monthly Recurring Revenue",
                    "Customer Acquisition Cost",
                    "Lifetime Value",
                    "Gross Margin",
                    "Cash Flow"
                ],
                "operational": [
                    "Deal Conversion Rate",
                    "Time to Close",
                    "Customer Satisfaction",
                    "Employee Productivity",
                    "System Uptime"
                ],
                "strategic": [
                    "Market Share",
                    "Competitive Position",
                    "Brand Recognition",
                    "Partnership Value",
                    "Innovation Index"
                ]
            },
            "milestone_tracking": {
                "monthly": "Progress against immediate actions",
                "quarterly": "Major milestone achievement",
                "annually": "Strategic objective completion"
            },
            "success_criteria": {
                "threshold": "Minimum acceptable performance",
                "target": "Expected performance",
                "stretch": "Exceptional performance"
            },
            "course_correction": {
                "triggers": "Performance below threshold for 2 periods",
                "process": "Root cause analysis and strategy adjustment",
                "approval": "Steering committee review and approval"
            }
        }

    def _assess_portfolio_risk(self, recommendations: List[StrategicRecommendation]) -> Dict[str, Any]:
        """Assess risk of recommendation portfolio"""
        risks = {
            "overall_risk_score": 0.0,
            "risk_categories": {},
            "mitigation_strategies": [],
            "contingency_plans": []
        }

        # Calculate overall risk
        investment_weights = [r.investment_required for r in recommendations]
        total_investment = sum(investment_weights)

        if total_investment > 0:
            risk_scores = []
            for rec in recommendations:
                rec_risk = 1 - rec.success_probability
                weight = rec.investment_required / total_investment
                risk_scores.append(rec_risk * weight)

            risks["overall_risk_score"] = sum(risk_scores)

        # Risk by category
        risk_by_type = {}
        for rec in recommendations:
            rec_type = rec.type.value
            if rec_type not in risk_by_type:
                risk_by_type[rec_type] = []
            risk_by_type[rec_type].append(1 - rec.success_probability)

        for rec_type, type_risks in risk_by_type.items():
            risks["risk_categories"][rec_type] = np.mean(type_risks)

        # Mitigation strategies
        risks["mitigation_strategies"] = [
            "Phased implementation to reduce execution risk",
            "Regular progress monitoring and early intervention",
            "Diversified recommendation portfolio",
            "Strong governance and decision-making processes",
            "Contingency planning for high-risk items"
        ]

        # Contingency plans
        risks["contingency_plans"] = [
            {
                "scenario": "Market downturn",
                "probability": 0.3,
                "impact": "Delay growth initiatives",
                "response": "Focus on efficiency and cash preservation"
            },
            {
                "scenario": "Competitive disruption",
                "probability": 0.4,
                "impact": "Accelerate defensive strategies",
                "response": "Implement competitive response bundle"
            },
            {
                "scenario": "Execution delays",
                "probability": 0.5,
                "impact": "Timeline extension",
                "response": "Re-prioritize and add resources"
            }
        ]

        return risks

    def _calculate_resource_requirements(self, recommendations: List[StrategicRecommendation]) -> Dict[str, Any]:
        """Calculate total resource requirements"""
        requirements = {
            "financial": {
                "total_investment": sum(r.investment_required for r in recommendations),
                "by_category": {},
                "by_timeline": {}
            },
            "human_resources": {
                "additional_hires": 0,
                "skill_requirements": [],
                "leadership_needs": []
            },
            "technology": {
                "infrastructure_investment": 0,
                "software_licenses": 0,
                "development_resources": 0
            },
            "external": {
                "consultants": 0,
                "vendors": 0,
                "partnerships": 0
            }
        }

        # Financial by category
        by_category = {}
        for rec in recommendations:
            category = rec.type.value
            if category not in by_category:
                by_category[category] = 0
            by_category[category] += rec.investment_required
        requirements["financial"]["by_category"] = by_category

        # Financial by timeline
        by_timeline = {}
        for rec in recommendations:
            timeline = rec.time_horizon.value
            if timeline not in by_timeline:
                by_timeline[timeline] = 0
            by_timeline[timeline] += rec.investment_required
        requirements["financial"]["by_timeline"] = by_timeline

        # Human resources (estimated)
        requirements["human_resources"]["additional_hires"] = len(recommendations) * 2
        requirements["human_resources"]["skill_requirements"] = [
            "Strategic planning", "Project management", "Technology development",
            "Business development", "Data analytics", "Customer success"
        ]
        requirements["human_resources"]["leadership_needs"] = [
            "VP of Strategy", "Head of Partnerships", "Head of Product"
        ]

        # Technology investment (estimated)
        tech_recs = [r for r in recommendations if "technology" in r.description.lower()]
        requirements["technology"]["infrastructure_investment"] = sum(
            r.investment_required * 0.3 for r in tech_recs
        )

        return requirements


class StrategicRecommendationSystem:
    """System for managing strategic recommendations"""

    def __init__(self):
        self.engine = StrategicRecommendationEngine()
        self.recommendations_cache = {}
        self.last_update = datetime.utcnow()

    async def generate_recommendations(self,
                                     intelligence_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate strategic recommendations from all intelligence systems"""

        # Extract data from each system
        ecosystem_data = intelligence_data.get("ecosystem", {})
        partnership_data = intelligence_data.get("partnerships", {})
        deal_data = intelligence_data.get("deals", {})
        competitive_data = intelligence_data.get("competitive", {})
        wealth_data = intelligence_data.get("wealth", {})

        # Generate recommendations
        recommendations = await self.engine.generate_strategic_recommendations(
            ecosystem_data, partnership_data, deal_data,
            competitive_data, wealth_data
        )

        # Add meta information
        recommendations["meta"] = {
            "generation_timestamp": datetime.utcnow().isoformat(),
            "data_sources": list(intelligence_data.keys()),
            "total_recommendations": len(recommendations.get("top_recommendations", [])),
            "total_investment": recommendations.get("resource_requirements", {}).get("financial", {}).get("total_investment", 0),
            "expected_timeline": "18-24 months",
            "confidence_level": 0.80
        }

        # Cache results
        self.recommendations_cache = recommendations

        return recommendations

    def get_cached_recommendations(self) -> Dict[str, Any]:
        """Get cached recommendations"""
        return self.recommendations_cache