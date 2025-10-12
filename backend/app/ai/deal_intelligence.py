"""
AI-Powered Deal Intelligence
Sprint 23: Advanced deal scoring, risk assessment, and intelligent recommendations
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import math
import json
from enum import Enum

from .ai_service import AIService, AIRequest, AIResponse, AITask, AIModel


class DealRiskLevel(str, Enum):
    """Deal risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DealRecommendation(str, Enum):
    """Deal recommendation types"""
    PROCEED = "proceed"
    PROCEED_WITH_CAUTION = "proceed_with_caution"
    INVESTIGATE_FURTHER = "investigate_further"
    DECLINE = "decline"
    NEGOTIATE_TERMS = "negotiate_terms"


@dataclass
class DealScore:
    """Comprehensive deal scoring result"""
    overall_score: float  # 0-100
    financial_score: float  # 0-100
    strategic_score: float  # 0-100
    risk_score: float  # 0-100
    market_score: float  # 0-100
    team_score: float  # 0-100
    confidence: float  # 0-1


@dataclass
class RiskAssessment:
    """Deal risk assessment result"""
    overall_risk: DealRiskLevel
    risk_factors: List[Dict[str, Any]]
    mitigation_strategies: List[str]
    probability_of_success: float  # 0-1
    key_concerns: List[str]


@dataclass
class DealIntelligence:
    """Complete deal intelligence analysis"""
    deal_id: str
    score: DealScore
    risk_assessment: RiskAssessment
    recommendation: DealRecommendation
    market_insights: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    next_best_actions: List[str]
    confidence_level: float
    analysis_timestamp: datetime


class DealIntelligenceEngine:
    """Advanced AI-powered deal intelligence engine"""

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or AIService()
        self.scoring_weights = {
            "financial": 0.30,
            "strategic": 0.25,
            "risk": 0.20,
            "market": 0.15,
            "team": 0.10
        }

    async def analyze_deal(self, deal_data: Dict[str, Any]) -> DealIntelligence:
        """
        Perform comprehensive AI-powered deal analysis

        Args:
            deal_data: Complete deal information including financials, strategic fit, team, etc.

        Returns:
            DealIntelligence: Complete analysis with scores, risks, and recommendations
        """
        # Generate deal score
        deal_score = await self._calculate_deal_score(deal_data)

        # Perform risk assessment
        risk_assessment = await self._assess_deal_risks(deal_data, deal_score)

        # Generate market insights
        market_insights = await self._analyze_market_context(deal_data)

        # Competitive analysis
        competitive_analysis = await self._analyze_competition(deal_data)

        # Generate recommendation
        recommendation = self._generate_recommendation(deal_score, risk_assessment)

        # Next best actions
        next_actions = await self._generate_next_actions(deal_data, deal_score, risk_assessment)

        # Calculate overall confidence
        confidence = self._calculate_confidence(deal_score, risk_assessment, market_insights)

        return DealIntelligence(
            deal_id=deal_data.get("id", "unknown"),
            score=deal_score,
            risk_assessment=risk_assessment,
            recommendation=recommendation,
            market_insights=market_insights,
            competitive_analysis=competitive_analysis,
            next_best_actions=next_actions,
            confidence_level=confidence,
            analysis_timestamp=datetime.now()
        )

    async def _calculate_deal_score(self, deal_data: Dict[str, Any]) -> DealScore:
        """Calculate comprehensive deal score using AI"""

        # Financial scoring
        financial_score = await self._score_financial_metrics(deal_data)

        # Strategic fit scoring
        strategic_score = await self._score_strategic_fit(deal_data)

        # Risk scoring (lower risk = higher score)
        risk_score = await self._score_risk_factors(deal_data)

        # Market opportunity scoring
        market_score = await self._score_market_opportunity(deal_data)

        # Team and execution capability scoring
        team_score = await self._score_team_capability(deal_data)

        # Calculate weighted overall score
        overall_score = (
            financial_score * self.scoring_weights["financial"] +
            strategic_score * self.scoring_weights["strategic"] +
            risk_score * self.scoring_weights["risk"] +
            market_score * self.scoring_weights["market"] +
            team_score * self.scoring_weights["team"]
        )

        # Calculate confidence based on data completeness
        confidence = self._calculate_scoring_confidence(deal_data)

        return DealScore(
            overall_score=round(overall_score, 1),
            financial_score=round(financial_score, 1),
            strategic_score=round(strategic_score, 1),
            risk_score=round(risk_score, 1),
            market_score=round(market_score, 1),
            team_score=round(team_score, 1),
            confidence=confidence
        )

    async def _score_financial_metrics(self, deal_data: Dict[str, Any]) -> float:
        """Score financial performance and projections"""

        # Use AI to analyze financial data
        request = AIRequest(
            task=AITask.ANALYZE_DOCUMENT,
            model=AIModel.FINANCIAL_FORECASTER,
            input_data={
                "financials": deal_data.get("financials", {}),
                "valuation": deal_data.get("valuation"),
                "revenue": deal_data.get("revenue"),
                "growth_rate": deal_data.get("growth_rate"),
                "profit_margin": deal_data.get("profit_margin"),
                "debt_ratio": deal_data.get("debt_ratio")
            }
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            # Fallback to basic scoring
            return self._basic_financial_score(deal_data)

        # Extract AI-generated financial score
        ai_result = response.result
        return min(100, max(0, ai_result.get("financial_health_score", 50)))

    def _basic_financial_score(self, deal_data: Dict[str, Any]) -> float:
        """Basic financial scoring without AI"""
        score = 50  # Base score

        # Revenue growth scoring
        growth_rate = deal_data.get("growth_rate", 0)
        if growth_rate > 0.2:  # 20%+
            score += 20
        elif growth_rate > 0.1:  # 10-20%
            score += 10
        elif growth_rate < 0:  # Negative growth
            score -= 15

        # Profit margin scoring
        profit_margin = deal_data.get("profit_margin", 0)
        if profit_margin > 0.15:  # 15%+
            score += 15
        elif profit_margin > 0.05:  # 5-15%
            score += 8
        elif profit_margin < 0:  # Unprofitable
            score -= 20

        # Debt ratio scoring
        debt_ratio = deal_data.get("debt_ratio", 0.5)
        if debt_ratio < 0.3:  # Low debt
            score += 10
        elif debt_ratio > 0.7:  # High debt
            score -= 15

        return min(100, max(0, score))

    async def _score_strategic_fit(self, deal_data: Dict[str, Any]) -> float:
        """Score strategic alignment and synergies"""

        request = AIRequest(
            task=AITask.GENERATE_INSIGHTS,
            model=AIModel.RECOMMENDATION_ENGINE,
            input_data={
                "target_industry": deal_data.get("industry"),
                "target_geography": deal_data.get("geography"),
                "synergy_potential": deal_data.get("synergy_potential", {}),
                "strategic_rationale": deal_data.get("strategic_rationale"),
                "market_position": deal_data.get("market_position")
            }
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            return self._basic_strategic_score(deal_data)

        # Extract strategic fit score from AI analysis
        return min(100, max(0, response.result.get("strategic_alignment_score", 50)))

    def _basic_strategic_score(self, deal_data: Dict[str, Any]) -> float:
        """Basic strategic scoring without AI"""
        score = 50

        # Industry alignment
        if deal_data.get("industry_alignment", False):
            score += 20

        # Geographic fit
        if deal_data.get("geographic_fit", False):
            score += 15

        # Synergy potential
        synergy_score = deal_data.get("synergy_score", 0)
        score += synergy_score * 15  # Scale 0-1 to 0-15

        return min(100, max(0, score))

    async def _score_risk_factors(self, deal_data: Dict[str, Any]) -> float:
        """Score risk factors (higher score = lower risk)"""

        request = AIRequest(
            task=AITask.DETECT_ANOMALIES,
            model=AIModel.RISK_ASSESSOR,
            input_data={
                "financial_data": deal_data.get("financials", {}),
                "market_conditions": deal_data.get("market_conditions", {}),
                "regulatory_environment": deal_data.get("regulatory_environment"),
                "competitive_pressure": deal_data.get("competitive_pressure"),
                "execution_complexity": deal_data.get("execution_complexity")
            }
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            return self._basic_risk_score(deal_data)

        # Convert risk level to score (inverse relationship)
        risk_level = response.result.get("risk_level", 0.5)  # 0-1 scale
        return (1 - risk_level) * 100

    def _basic_risk_score(self, deal_data: Dict[str, Any]) -> float:
        """Basic risk scoring without AI"""
        score = 80  # Start with low risk assumption

        # Market volatility
        if deal_data.get("market_volatility", "medium") == "high":
            score -= 20
        elif deal_data.get("market_volatility") == "low":
            score += 10

        # Regulatory risk
        if deal_data.get("regulatory_risk", "medium") == "high":
            score -= 15
        elif deal_data.get("regulatory_risk") == "low":
            score += 5

        # Execution complexity
        complexity = deal_data.get("execution_complexity", "medium")
        if complexity == "high":
            score -= 25
        elif complexity == "low":
            score += 15

        return min(100, max(0, score))

    async def _score_market_opportunity(self, deal_data: Dict[str, Any]) -> float:
        """Score market size and growth potential"""

        request = AIRequest(
            task=AITask.GENERATE_INSIGHTS,
            model=AIModel.MARKET_INTELLIGENCE,
            input_data={
                "market_size": deal_data.get("market_size"),
                "market_growth": deal_data.get("market_growth"),
                "competitive_landscape": deal_data.get("competitive_landscape", {}),
                "market_trends": deal_data.get("market_trends", []),
                "target_market_share": deal_data.get("target_market_share")
            }
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            return self._basic_market_score(deal_data)

        return min(100, max(0, response.result.get("market_opportunity_score", 50)))

    def _basic_market_score(self, deal_data: Dict[str, Any]) -> float:
        """Basic market scoring without AI"""
        score = 50

        # Market size
        market_size = deal_data.get("market_size", "medium")
        if market_size == "large":
            score += 20
        elif market_size == "small":
            score -= 10

        # Market growth
        market_growth = deal_data.get("market_growth", 0.05)
        if market_growth > 0.1:
            score += 15
        elif market_growth < 0:
            score -= 20

        # Market position
        position = deal_data.get("market_position", "follower")
        if position == "leader":
            score += 20
        elif position == "challenger":
            score += 10

        return min(100, max(0, score))

    async def _score_team_capability(self, deal_data: Dict[str, Any]) -> float:
        """Score team quality and execution capability"""

        request = AIRequest(
            task=AITask.ANALYZE_DOCUMENT,
            model=AIModel.CONTENT_SUMMARIZER,
            input_data={
                "management_team": deal_data.get("management_team", {}),
                "team_experience": deal_data.get("team_experience"),
                "track_record": deal_data.get("track_record", {}),
                "key_personnel": deal_data.get("key_personnel", []),
                "cultural_fit": deal_data.get("cultural_fit")
            }
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            return self._basic_team_score(deal_data)

        return min(100, max(0, response.result.get("team_capability_score", 50)))

    def _basic_team_score(self, deal_data: Dict[str, Any]) -> float:
        """Basic team scoring without AI"""
        score = 50

        # Management experience
        mgmt_experience = deal_data.get("management_experience", "medium")
        if mgmt_experience == "high":
            score += 25
        elif mgmt_experience == "low":
            score -= 15

        # Track record
        track_record = deal_data.get("track_record_score", 0.5)  # 0-1 scale
        score += track_record * 20

        # Cultural fit
        cultural_fit = deal_data.get("cultural_fit_score", 0.5)  # 0-1 scale
        score += cultural_fit * 10

        return min(100, max(0, score))

    def _calculate_scoring_confidence(self, deal_data: Dict[str, Any]) -> float:
        """Calculate confidence based on data completeness"""
        required_fields = [
            "financials", "industry", "market_size", "management_team",
            "competitive_landscape", "strategic_rationale"
        ]

        available_fields = sum(1 for field in required_fields if deal_data.get(field))
        completeness = available_fields / len(required_fields)

        # Boost confidence for high-quality data
        if deal_data.get("due_diligence_complete", False):
            completeness += 0.1

        if deal_data.get("third_party_validation", False):
            completeness += 0.1

        return min(1.0, completeness)

    async def _assess_deal_risks(self, deal_data: Dict[str, Any], deal_score: DealScore) -> RiskAssessment:
        """Comprehensive risk assessment using AI"""

        request = AIRequest(
            task=AITask.DETECT_ANOMALIES,
            model=AIModel.RISK_ASSESSOR,
            input_data={
                "deal_data": deal_data,
                "financial_score": deal_score.financial_score,
                "market_conditions": deal_data.get("market_conditions", {}),
                "regulatory_factors": deal_data.get("regulatory_factors", [])
            }
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            return self._basic_risk_assessment(deal_data, deal_score)

        ai_result = response.result

        # Determine overall risk level
        risk_score = deal_score.risk_score
        if risk_score >= 80:
            overall_risk = DealRiskLevel.LOW
        elif risk_score >= 60:
            overall_risk = DealRiskLevel.MEDIUM
        elif risk_score >= 40:
            overall_risk = DealRiskLevel.HIGH
        else:
            overall_risk = DealRiskLevel.CRITICAL

        return RiskAssessment(
            overall_risk=overall_risk,
            risk_factors=ai_result.get("risk_factors", []),
            mitigation_strategies=ai_result.get("mitigation_strategies", []),
            probability_of_success=ai_result.get("success_probability", 0.7),
            key_concerns=ai_result.get("key_concerns", [])
        )

    def _basic_risk_assessment(self, deal_data: Dict[str, Any], deal_score: DealScore) -> RiskAssessment:
        """Basic risk assessment without AI"""

        risk_factors = []
        mitigation_strategies = []
        key_concerns = []

        # Financial risks
        if deal_score.financial_score < 60:
            risk_factors.append({
                "type": "financial",
                "description": "Weak financial performance",
                "severity": "high",
                "impact": "revenue_decline"
            })
            mitigation_strategies.append("Conduct detailed financial due diligence")
            key_concerns.append("Deteriorating financial metrics")

        # Market risks
        if deal_score.market_score < 50:
            risk_factors.append({
                "type": "market",
                "description": "Challenging market conditions",
                "severity": "medium",
                "impact": "growth_limitation"
            })
            mitigation_strategies.append("Develop market expansion strategy")
            key_concerns.append("Limited market opportunity")

        # Determine overall risk
        avg_score = (deal_score.financial_score + deal_score.strategic_score +
                    deal_score.risk_score + deal_score.market_score) / 4

        if avg_score >= 75:
            overall_risk = DealRiskLevel.LOW
        elif avg_score >= 60:
            overall_risk = DealRiskLevel.MEDIUM
        elif avg_score >= 45:
            overall_risk = DealRiskLevel.HIGH
        else:
            overall_risk = DealRiskLevel.CRITICAL

        return RiskAssessment(
            overall_risk=overall_risk,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies,
            probability_of_success=max(0.1, min(0.9, avg_score / 100)),
            key_concerns=key_concerns
        )

    async def _analyze_market_context(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market context and trends"""

        request = AIRequest(
            task=AITask.GENERATE_INSIGHTS,
            model=AIModel.MARKET_INTELLIGENCE,
            input_data={
                "industry": deal_data.get("industry"),
                "geography": deal_data.get("geography"),
                "market_data": deal_data.get("market_data", {}),
                "competitive_intelligence": deal_data.get("competitive_intelligence", {})
            }
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            return {
                "market_trends": ["Technology adoption", "Digital transformation"],
                "growth_drivers": ["Market expansion", "Product innovation"],
                "market_outlook": "stable",
                "key_indicators": {}
            }

        return response.result

    async def _analyze_competition(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive landscape"""

        request = AIRequest(
            task=AITask.GENERATE_INSIGHTS,
            model=AIModel.MARKET_INTELLIGENCE,
            input_data={
                "competitors": deal_data.get("competitors", []),
                "market_share": deal_data.get("market_share"),
                "competitive_advantages": deal_data.get("competitive_advantages", []),
                "differentiation": deal_data.get("differentiation")
            }
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            return {
                "competitive_position": "moderate",
                "key_competitors": [],
                "competitive_threats": [],
                "strategic_advantages": []
            }

        return response.result

    def _generate_recommendation(self, deal_score: DealScore, risk_assessment: RiskAssessment) -> DealRecommendation:
        """Generate deal recommendation based on scores and risks"""

        overall_score = deal_score.overall_score
        overall_risk = risk_assessment.overall_risk
        confidence = deal_score.confidence

        # High score + low risk = proceed
        if overall_score >= 80 and overall_risk in [DealRiskLevel.LOW, DealRiskLevel.MEDIUM]:
            return DealRecommendation.PROCEED

        # Good score + manageable risk = proceed with caution
        elif overall_score >= 65 and overall_risk != DealRiskLevel.CRITICAL:
            return DealRecommendation.PROCEED_WITH_CAUTION

        # Moderate score = investigate further
        elif overall_score >= 50:
            return DealRecommendation.INVESTIGATE_FURTHER

        # Poor score with high confidence = decline
        elif overall_score < 40 and confidence > 0.7:
            return DealRecommendation.DECLINE

        # Poor score with low confidence = investigate
        elif overall_score < 50:
            return DealRecommendation.INVESTIGATE_FURTHER

        # Default to negotiate terms
        else:
            return DealRecommendation.NEGOTIATE_TERMS

    async def _generate_next_actions(self, deal_data: Dict[str, Any],
                                   deal_score: DealScore,
                                   risk_assessment: RiskAssessment) -> List[str]:
        """Generate AI-powered next best actions"""

        request = AIRequest(
            task=AITask.RECOMMEND_ACTIONS,
            model=AIModel.RECOMMENDATION_ENGINE,
            input_data={
                "deal_score": deal_score.__dict__,
                "risk_assessment": {
                    "overall_risk": risk_assessment.overall_risk.value,
                    "risk_factors": risk_assessment.risk_factors,
                    "key_concerns": risk_assessment.key_concerns
                },
                "deal_stage": deal_data.get("stage", "initial_review")
            }
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            return self._basic_next_actions(deal_score, risk_assessment)

        return response.result.get("recommended_actions", [])

    def _basic_next_actions(self, deal_score: DealScore, risk_assessment: RiskAssessment) -> List[str]:
        """Generate basic next actions without AI"""
        actions = []

        # Financial actions
        if deal_score.financial_score < 60:
            actions.append("Conduct detailed financial due diligence")
            actions.append("Request additional financial documentation")

        # Risk mitigation actions
        if risk_assessment.overall_risk in [DealRiskLevel.HIGH, DealRiskLevel.CRITICAL]:
            actions.extend(risk_assessment.mitigation_strategies[:3])

        # Strategic actions
        if deal_score.strategic_score < 70:
            actions.append("Reassess strategic alignment and synergies")
            actions.append("Meet with management team for strategic discussion")

        # Market actions
        if deal_score.market_score < 60:
            actions.append("Conduct comprehensive market analysis")
            actions.append("Validate market assumptions with third-party research")

        return actions[:5]  # Limit to top 5 actions

    def _calculate_confidence(self, deal_score: DealScore,
                             risk_assessment: RiskAssessment,
                             market_insights: Dict[str, Any]) -> float:
        """Calculate overall analysis confidence"""

        # Base confidence from scoring
        score_confidence = deal_score.confidence

        # Risk assessment quality
        risk_confidence = 0.8 if len(risk_assessment.risk_factors) > 0 else 0.6

        # Market insights quality
        market_confidence = 0.9 if market_insights.get("key_indicators") else 0.7

        # Weighted average
        overall_confidence = (
            score_confidence * 0.5 +
            risk_confidence * 0.3 +
            market_confidence * 0.2
        )

        return round(overall_confidence, 2)


# Global deal intelligence engine instance
_deal_intelligence_engine: Optional[DealIntelligenceEngine] = None


def get_deal_intelligence_engine() -> DealIntelligenceEngine:
    """Get global deal intelligence engine instance"""
    global _deal_intelligence_engine
    if _deal_intelligence_engine is None:
        _deal_intelligence_engine = DealIntelligenceEngine()
    return _deal_intelligence_engine


# Utility function for quick deal analysis
async def analyze_deal_intelligence(deal_data: Dict[str, Any]) -> DealIntelligence:
    """Quick utility function for deal intelligence analysis"""
    engine = get_deal_intelligence_engine()
    return await engine.analyze_deal(deal_data)