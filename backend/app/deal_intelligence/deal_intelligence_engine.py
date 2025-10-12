"""
Deal Intelligence Engine - Advanced AI-powered deal analysis and scoring
Provides comprehensive deal intelligence capabilities for M&A transactions
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json
import math
import random
from abc import ABC, abstractmethod

# Data Models and Enums
class DealType(Enum):
    ACQUISITION = "acquisition"
    MERGER = "merger"
    JOINT_VENTURE = "joint_venture"
    STRATEGIC_PARTNERSHIP = "strategic_partnership"
    ASSET_PURCHASE = "asset_purchase"
    DIVESTITURE = "divestiture"

class DealStage(Enum):
    ORIGINATION = "origination"
    INITIAL_SCREENING = "initial_screening"
    PRELIMINARY_DUE_DILIGENCE = "preliminary_due_diligence"
    FORMAL_DUE_DILIGENCE = "formal_due_diligence"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    POST_CLOSE_INTEGRATION = "post_close_integration"

class IndustryVertical(Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCIAL_SERVICES = "financial_services"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    ENERGY = "energy"
    REAL_ESTATE = "real_estate"
    TELECOMMUNICATIONS = "telecommunications"

class DealComplexity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    COMPLEX = "complex"

class StrategicFitLevel(Enum):
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"

@dataclass
class DealProfile:
    """Comprehensive deal profile data"""
    deal_id: str
    deal_type: DealType
    target_company: str
    acquirer_company: str
    industry: IndustryVertical
    deal_value: float
    currency: str = "USD"
    stage: DealStage = DealStage.ORIGINATION
    expected_close_date: Optional[datetime] = None
    key_metrics: Dict[str, Any] = field(default_factory=dict)
    strategic_rationale: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class MarketContext:
    """Market intelligence and context data"""
    industry: IndustryVertical
    market_size: float
    growth_rate: float
    competitive_landscape: Dict[str, Any]
    regulatory_environment: Dict[str, Any]
    market_trends: List[str]
    valuation_multiples: Dict[str, float]

@dataclass
class DealScore:
    """AI-generated deal scoring results"""
    overall_score: float  # 0-100
    financial_score: float
    strategic_score: float
    execution_score: float
    risk_score: float
    market_score: float
    scoring_factors: Dict[str, float]
    confidence_level: float
    recommendations: List[str]
    risk_factors: List[str]

class DealScoringEngine:
    """Advanced AI-powered deal scoring and valuation engine"""

    def __init__(self):
        self.scoring_models = {}
        self.valuation_models = {}
        self.historical_data = defaultdict(list)
        self.market_benchmarks = {}

    def create_scoring_model(self, model_id: str, model_name: str,
                           industry: IndustryVertical) -> bool:
        """Create a new deal scoring model"""
        try:
            model = {
                "id": model_id,
                "name": model_name,
                "industry": industry,
                "weights": {
                    "financial": 0.25,
                    "strategic": 0.20,
                    "execution": 0.20,
                    "risk": 0.15,
                    "market": 0.20
                },
                "factors": {
                    "revenue_multiple": {"weight": 0.3, "benchmark": 5.0},
                    "ebitda_multiple": {"weight": 0.25, "benchmark": 12.0},
                    "growth_rate": {"weight": 0.2, "benchmark": 0.15},
                    "market_position": {"weight": 0.15, "benchmark": 0.7},
                    "synergy_potential": {"weight": 0.1, "benchmark": 0.8}
                },
                "created_at": datetime.now()
            }
            self.scoring_models[model_id] = model
            return True
        except Exception:
            return False

    def calculate_deal_score(self, deal_profile: DealProfile,
                           market_context: MarketContext,
                           model_id: Optional[str] = None) -> DealScore:
        """Calculate comprehensive AI-powered deal score"""

        if model_id and model_id in self.scoring_models:
            model = self.scoring_models[model_id]
        else:
            # Use default model
            model = self._get_default_model(deal_profile.industry)

        # Calculate individual scores
        financial_score = self._calculate_financial_score(deal_profile, market_context)
        strategic_score = self._calculate_strategic_score(deal_profile, market_context)
        execution_score = self._calculate_execution_score(deal_profile)
        risk_score = self._calculate_risk_score(deal_profile, market_context)
        market_score = self._calculate_market_score(market_context)

        # Calculate weighted overall score
        weights = model["weights"]
        overall_score = (
            financial_score * weights["financial"] +
            strategic_score * weights["strategic"] +
            execution_score * weights["execution"] +
            (100 - risk_score) * weights["risk"] +  # Invert risk score
            market_score * weights["market"]
        )

        # Generate scoring factors breakdown
        scoring_factors = {
            "financial_contribution": financial_score * weights["financial"],
            "strategic_contribution": strategic_score * weights["strategic"],
            "execution_contribution": execution_score * weights["execution"],
            "risk_contribution": (100 - risk_score) * weights["risk"],
            "market_contribution": market_score * weights["market"]
        }

        # Generate recommendations and risk factors
        recommendations = self._generate_recommendations(
            deal_profile, financial_score, strategic_score, execution_score,
            risk_score, market_score
        )
        risk_factors = self._identify_risk_factors(deal_profile, market_context, risk_score)

        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(
            deal_profile, market_context, overall_score
        )

        return DealScore(
            overall_score=round(overall_score, 2),
            financial_score=round(financial_score, 2),
            strategic_score=round(strategic_score, 2),
            execution_score=round(execution_score, 2),
            risk_score=round(risk_score, 2),
            market_score=round(market_score, 2),
            scoring_factors=scoring_factors,
            confidence_level=round(confidence_level, 2),
            recommendations=recommendations,
            risk_factors=risk_factors
        )

    def _calculate_financial_score(self, deal_profile: DealProfile,
                                 market_context: MarketContext) -> float:
        """Calculate financial attractiveness score"""
        score = 50.0  # Base score

        # Revenue multiple analysis
        if "revenue" in deal_profile.key_metrics:
            revenue_multiple = deal_profile.deal_value / deal_profile.key_metrics["revenue"]
            if revenue_multiple <= market_context.valuation_multiples.get("revenue", 5.0):
                score += 15
            elif revenue_multiple <= market_context.valuation_multiples.get("revenue", 5.0) * 1.2:
                score += 10
            else:
                score -= 5

        # EBITDA multiple analysis
        if "ebitda" in deal_profile.key_metrics:
            ebitda_multiple = deal_profile.deal_value / deal_profile.key_metrics["ebitda"]
            if ebitda_multiple <= market_context.valuation_multiples.get("ebitda", 12.0):
                score += 15
            elif ebitda_multiple <= market_context.valuation_multiples.get("ebitda", 12.0) * 1.3:
                score += 8
            else:
                score -= 8

        # Growth rate consideration
        if "growth_rate" in deal_profile.key_metrics:
            growth_rate = deal_profile.key_metrics["growth_rate"]
            if growth_rate >= 0.20:
                score += 20
            elif growth_rate >= 0.10:
                score += 15
            elif growth_rate >= 0.05:
                score += 10
            else:
                score -= 5

        return min(100, max(0, score))

    def _calculate_strategic_score(self, deal_profile: DealProfile,
                                 market_context: MarketContext) -> float:
        """Calculate strategic fit and synergy potential score"""
        score = 40.0  # Base score

        # Market expansion potential
        score += len(market_context.market_trends) * 5

        # Synergy potential
        if "synergy_potential" in deal_profile.key_metrics:
            synergy_score = deal_profile.key_metrics["synergy_potential"] * 30
            score += synergy_score

        # Industry consolidation benefits
        if deal_profile.deal_type in [DealType.ACQUISITION, DealType.MERGER]:
            score += 15

        # Strategic rationale strength
        if len(deal_profile.strategic_rationale) > 100:
            score += 10

        return min(100, max(0, score))

    def _calculate_execution_score(self, deal_profile: DealProfile) -> float:
        """Calculate execution complexity and feasibility score"""
        score = 60.0  # Base score

        # Deal size consideration
        if deal_profile.deal_value < 100_000_000:  # < $100M
            score += 20
        elif deal_profile.deal_value < 1_000_000_000:  # < $1B
            score += 10
        else:
            score -= 10

        # Deal type complexity
        complexity_scores = {
            DealType.ASSET_PURCHASE: 15,
            DealType.ACQUISITION: 10,
            DealType.STRATEGIC_PARTNERSHIP: 5,
            DealType.JOINT_VENTURE: 0,
            DealType.MERGER: -5,
            DealType.DIVESTITURE: -10
        }
        score += complexity_scores.get(deal_profile.deal_type, 0)

        # Timeline feasibility
        if deal_profile.expected_close_date:
            days_to_close = (deal_profile.expected_close_date - datetime.now()).days
            if days_to_close >= 180:
                score += 15
            elif days_to_close >= 90:
                score += 10
            elif days_to_close >= 30:
                score += 5
            else:
                score -= 15

        return min(100, max(0, score))

    def _calculate_risk_score(self, deal_profile: DealProfile,
                            market_context: MarketContext) -> float:
        """Calculate risk level (higher score = higher risk)"""
        score = 30.0  # Base risk

        # Regulatory risk
        reg_complexity = market_context.regulatory_environment.get("complexity", "medium")
        if reg_complexity == "high":
            score += 20
        elif reg_complexity == "medium":
            score += 10

        # Market volatility risk
        if market_context.growth_rate < 0:
            score += 25
        elif market_context.growth_rate < 0.03:
            score += 15

        # Deal size risk
        if deal_profile.deal_value > 5_000_000_000:  # > $5B
            score += 15

        # Industry-specific risks
        high_risk_industries = [IndustryVertical.ENERGY, IndustryVertical.HEALTHCARE]
        if deal_profile.industry in high_risk_industries:
            score += 10

        return min(100, max(0, score))

    def _calculate_market_score(self, market_context: MarketContext) -> float:
        """Calculate market attractiveness score"""
        score = 50.0  # Base score

        # Market growth
        if market_context.growth_rate >= 0.15:
            score += 25
        elif market_context.growth_rate >= 0.08:
            score += 15
        elif market_context.growth_rate >= 0.03:
            score += 10
        else:
            score -= 10

        # Market size
        if market_context.market_size >= 10_000_000_000:  # >= $10B
            score += 15
        elif market_context.market_size >= 1_000_000_000:  # >= $1B
            score += 10

        # Number of positive trends
        score += len(market_context.market_trends) * 3

        return min(100, max(0, score))

    def _get_default_model(self, industry: IndustryVertical) -> Dict[str, Any]:
        """Get default scoring model for industry"""
        return {
            "id": f"default_{industry.value}",
            "name": f"Default {industry.value.title()} Model",
            "industry": industry,
            "weights": {
                "financial": 0.25,
                "strategic": 0.20,
                "execution": 0.20,
                "risk": 0.15,
                "market": 0.20
            }
        }

    def _generate_recommendations(self, deal_profile: DealProfile,
                                financial_score: float, strategic_score: float,
                                execution_score: float, risk_score: float,
                                market_score: float) -> List[str]:
        """Generate AI-powered recommendations"""
        recommendations = []

        if financial_score < 60:
            recommendations.append("Consider renegotiating valuation terms")
            recommendations.append("Explore creative deal structures to improve returns")

        if strategic_score < 60:
            recommendations.append("Develop clearer synergy capture plan")
            recommendations.append("Assess strategic alternatives")

        if execution_score < 60:
            recommendations.append("Allocate additional integration resources")
            recommendations.append("Consider phased execution approach")

        if risk_score > 70:
            recommendations.append("Implement comprehensive risk mitigation plan")
            recommendations.append("Consider additional due diligence")

        if market_score < 50:
            recommendations.append("Reassess market timing")
            recommendations.append("Evaluate defensive positioning")

        return recommendations

    def _identify_risk_factors(self, deal_profile: DealProfile,
                             market_context: MarketContext, risk_score: float) -> List[str]:
        """Identify key risk factors"""
        risk_factors = []

        if risk_score > 70:
            risk_factors.append("High overall risk profile")

        if market_context.growth_rate < 0:
            risk_factors.append("Declining market conditions")

        if deal_profile.deal_value > 1_000_000_000:
            risk_factors.append("Large transaction size increases execution risk")

        reg_complexity = market_context.regulatory_environment.get("complexity", "medium")
        if reg_complexity == "high":
            risk_factors.append("Complex regulatory approval process")

        return risk_factors

    def _calculate_confidence_level(self, deal_profile: DealProfile,
                                  market_context: MarketContext,
                                  overall_score: float) -> float:
        """Calculate confidence in the scoring assessment"""
        confidence = 70.0  # Base confidence

        # Data completeness
        if len(deal_profile.key_metrics) >= 5:
            confidence += 15
        elif len(deal_profile.key_metrics) >= 3:
            confidence += 10

        # Market data quality
        if market_context.valuation_multiples:
            confidence += 10

        # Score consistency
        score_variance = self._calculate_score_variance(
            [overall_score, deal_profile.key_metrics.get("internal_score", overall_score)]
        )
        if score_variance < 10:
            confidence += 5

        return min(100, max(0, confidence))

    def _calculate_score_variance(self, scores: List[float]) -> float:
        """Calculate variance in scores"""
        if len(scores) < 2:
            return 0
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        return math.sqrt(variance)

class MarketIntelligence:
    """Advanced market intelligence and analysis engine"""

    def __init__(self):
        self.market_data = defaultdict(dict)
        self.competitive_intelligence = defaultdict(list)
        self.trend_analysis = defaultdict(list)
        self.intelligence_sources = []

    def analyze_market_conditions(self, industry: IndustryVertical,
                                region: str = "global") -> MarketContext:
        """Analyze current market conditions for industry"""

        # Simulate market intelligence gathering
        market_size = self._estimate_market_size(industry)
        growth_rate = self._calculate_growth_rate(industry)
        competitive_landscape = self._analyze_competitive_landscape(industry)
        regulatory_environment = self._assess_regulatory_environment(industry)
        market_trends = self._identify_market_trends(industry)
        valuation_multiples = self._get_valuation_multiples(industry)

        return MarketContext(
            industry=industry,
            market_size=market_size,
            growth_rate=growth_rate,
            competitive_landscape=competitive_landscape,
            regulatory_environment=regulatory_environment,
            market_trends=market_trends,
            valuation_multiples=valuation_multiples
        )

    def _estimate_market_size(self, industry: IndustryVertical) -> float:
        """Estimate total addressable market size"""
        # Industry-specific market size estimates (in billions USD)
        market_sizes = {
            IndustryVertical.TECHNOLOGY: 5000.0,
            IndustryVertical.HEALTHCARE: 4000.0,
            IndustryVertical.FINANCIAL_SERVICES: 3500.0,
            IndustryVertical.MANUFACTURING: 2800.0,
            IndustryVertical.RETAIL: 2500.0,
            IndustryVertical.ENERGY: 2000.0,
            IndustryVertical.REAL_ESTATE: 1800.0,
            IndustryVertical.TELECOMMUNICATIONS: 1500.0
        }
        base_size = market_sizes.get(industry, 1000.0)
        # Add some variance
        return base_size * (0.9 + random.random() * 0.2)

    def _calculate_growth_rate(self, industry: IndustryVertical) -> float:
        """Calculate industry growth rate"""
        # Industry-specific growth rates
        growth_rates = {
            IndustryVertical.TECHNOLOGY: 0.12,
            IndustryVertical.HEALTHCARE: 0.08,
            IndustryVertical.FINANCIAL_SERVICES: 0.05,
            IndustryVertical.MANUFACTURING: 0.04,
            IndustryVertical.RETAIL: 0.03,
            IndustryVertical.ENERGY: 0.02,
            IndustryVertical.REAL_ESTATE: 0.06,
            IndustryVertical.TELECOMMUNICATIONS: 0.04
        }
        base_rate = growth_rates.get(industry, 0.05)
        # Add market cycle variance
        return base_rate + (random.random() - 0.5) * 0.04

    def _analyze_competitive_landscape(self, industry: IndustryVertical) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        return {
            "concentration": random.choice(["low", "medium", "high"]),
            "barriers_to_entry": random.choice(["low", "medium", "high"]),
            "competitive_intensity": random.choice(["low", "medium", "high"]),
            "key_players": 5 + random.randint(0, 15),
            "market_leaders_share": 0.3 + random.random() * 0.4
        }

    def _assess_regulatory_environment(self, industry: IndustryVertical) -> Dict[str, Any]:
        """Assess regulatory environment complexity"""
        # Industry-specific regulatory complexity
        complexity_map = {
            IndustryVertical.HEALTHCARE: "high",
            IndustryVertical.FINANCIAL_SERVICES: "high",
            IndustryVertical.ENERGY: "high",
            IndustryVertical.TELECOMMUNICATIONS: "medium",
            IndustryVertical.TECHNOLOGY: "medium",
            IndustryVertical.MANUFACTURING: "medium",
            IndustryVertical.RETAIL: "low",
            IndustryVertical.REAL_ESTATE: "low"
        }

        return {
            "complexity": complexity_map.get(industry, "medium"),
            "approval_timeline": random.randint(30, 365),
            "key_regulators": random.randint(1, 4),
            "recent_changes": random.choice([True, False])
        }

    def _identify_market_trends(self, industry: IndustryVertical) -> List[str]:
        """Identify current market trends"""
        # Industry-specific trends
        trends_map = {
            IndustryVertical.TECHNOLOGY: [
                "AI/ML adoption acceleration",
                "Cloud-first strategies",
                "Cybersecurity focus",
                "Digital transformation"
            ],
            IndustryVertical.HEALTHCARE: [
                "Telemedicine expansion",
                "Personalized medicine",
                "AI diagnostics",
                "Value-based care"
            ],
            IndustryVertical.FINANCIAL_SERVICES: [
                "Fintech disruption",
                "Digital banking",
                "Regulatory compliance automation",
                "ESG integration"
            ]
        }

        all_trends = trends_map.get(industry, ["Market consolidation", "Digital adoption"])
        return random.sample(all_trends, min(len(all_trends), random.randint(2, 4)))

    def _get_valuation_multiples(self, industry: IndustryVertical) -> Dict[str, float]:
        """Get current valuation multiples for industry"""
        # Industry-specific valuation multiples
        multiples_map = {
            IndustryVertical.TECHNOLOGY: {"revenue": 6.5, "ebitda": 15.0},
            IndustryVertical.HEALTHCARE: {"revenue": 4.2, "ebitda": 12.5},
            IndustryVertical.FINANCIAL_SERVICES: {"revenue": 3.8, "ebitda": 11.0},
            IndustryVertical.MANUFACTURING: {"revenue": 2.5, "ebitda": 9.5},
            IndustryVertical.RETAIL: {"revenue": 1.8, "ebitda": 8.0},
            IndustryVertical.ENERGY: {"revenue": 2.2, "ebitda": 7.5},
            IndustryVertical.REAL_ESTATE: {"revenue": 4.0, "ebitda": 14.0},
            IndustryVertical.TELECOMMUNICATIONS: {"revenue": 3.2, "ebitda": 10.5}
        }

        base_multiples = multiples_map.get(industry, {"revenue": 3.0, "ebitda": 10.0})
        # Add market variance
        return {
            "revenue": base_multiples["revenue"] * (0.9 + random.random() * 0.2),
            "ebitda": base_multiples["ebitda"] * (0.9 + random.random() * 0.2)
        }

class DealIntelligenceEngine:
    """Main deal intelligence engine orchestrating all components"""

    def __init__(self):
        self.scoring_engine = DealScoringEngine()
        self.market_intelligence = MarketIntelligence()
        self.deal_database = {}
        self.intelligence_cache = {}

    async def analyze_deal_opportunity(self, deal_profile: DealProfile) -> Dict[str, Any]:
        """Comprehensive deal opportunity analysis"""

        # Get market context
        market_context = self.market_intelligence.analyze_market_conditions(
            deal_profile.industry
        )

        # Calculate deal score
        deal_score = self.scoring_engine.calculate_deal_score(
            deal_profile, market_context
        )

        # Assess strategic fit
        strategic_fit = self._assess_strategic_fit(deal_profile, market_context)

        # Estimate transaction probability
        transaction_probability = self._estimate_transaction_probability(
            deal_profile, deal_score, market_context
        )

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            deal_profile, deal_score, strategic_fit, transaction_probability
        )

        analysis_result = {
            "deal_id": deal_profile.deal_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "deal_score": deal_score.__dict__,
            "market_context": market_context.__dict__,
            "strategic_fit": strategic_fit,
            "transaction_probability": transaction_probability,
            "executive_summary": executive_summary,
            "next_steps": self._recommend_next_steps(deal_score, strategic_fit)
        }

        # Cache results
        self.intelligence_cache[deal_profile.deal_id] = analysis_result

        return analysis_result

    def _assess_strategic_fit(self, deal_profile: DealProfile,
                            market_context: MarketContext) -> Dict[str, Any]:
        """Assess strategic fit between organizations"""

        # Calculate fit score based on multiple factors
        fit_score = 50.0

        # Industry alignment
        fit_score += 20

        # Market position complementarity
        fit_score += random.uniform(5, 15)

        # Cultural fit (simulated)
        cultural_fit = random.choice(["poor", "fair", "good", "excellent"])
        cultural_scores = {"poor": -10, "fair": 0, "good": 10, "excellent": 20}
        fit_score += cultural_scores[cultural_fit]

        # Technology synergies
        tech_synergies = random.uniform(0, 15)
        fit_score += tech_synergies

        # Determine fit level
        if fit_score >= 80:
            fit_level = StrategicFitLevel.EXCELLENT
        elif fit_score >= 65:
            fit_level = StrategicFitLevel.GOOD
        elif fit_score >= 50:
            fit_level = StrategicFitLevel.FAIR
        else:
            fit_level = StrategicFitLevel.POOR

        return {
            "fit_level": fit_level.value,
            "fit_score": round(fit_score, 2),
            "cultural_fit": cultural_fit,
            "synergy_areas": [
                "Technology integration",
                "Market expansion",
                "Cost optimization",
                "Talent acquisition"
            ],
            "integration_complexity": random.choice(["low", "medium", "high"])
        }

    def _estimate_transaction_probability(self, deal_profile: DealProfile,
                                        deal_score: DealScore,
                                        market_context: MarketContext) -> Dict[str, Any]:
        """Estimate probability of successful transaction completion"""

        base_probability = 0.4  # 40% base probability

        # Adjust based on deal score
        if deal_score.overall_score >= 80:
            base_probability += 0.3
        elif deal_score.overall_score >= 60:
            base_probability += 0.2
        elif deal_score.overall_score >= 40:
            base_probability += 0.1

        # Adjust based on market conditions
        if market_context.growth_rate > 0.1:
            base_probability += 0.1
        elif market_context.growth_rate < 0:
            base_probability -= 0.2

        # Adjust based on deal characteristics
        if deal_profile.deal_value < 500_000_000:  # < $500M
            base_probability += 0.1
        elif deal_profile.deal_value > 5_000_000_000:  # > $5B
            base_probability -= 0.15

        # Stage-based adjustments
        stage_adjustments = {
            DealStage.ORIGINATION: -0.1,
            DealStage.INITIAL_SCREENING: 0.0,
            DealStage.PRELIMINARY_DUE_DILIGENCE: 0.1,
            DealStage.FORMAL_DUE_DILIGENCE: 0.2,
            DealStage.NEGOTIATION: 0.3,
            DealStage.CLOSING: 0.4
        }
        base_probability += stage_adjustments.get(deal_profile.stage, 0)

        final_probability = max(0.05, min(0.95, base_probability))

        return {
            "completion_probability": round(final_probability, 3),
            "probability_factors": {
                "deal_quality": deal_score.overall_score / 100,
                "market_conditions": max(0, market_context.growth_rate),
                "deal_stage": stage_adjustments.get(deal_profile.stage, 0),
                "deal_size_factor": self._get_size_factor(deal_profile.deal_value)
            },
            "estimated_timeline": self._estimate_completion_timeline(deal_profile),
            "key_success_factors": [
                "Regulatory approval",
                "Due diligence completion",
                "Financing availability",
                "Stakeholder alignment"
            ]
        }

    def _get_size_factor(self, deal_value: float) -> float:
        """Get size-based probability factor"""
        if deal_value < 100_000_000:
            return 0.1
        elif deal_value < 1_000_000_000:
            return 0.05
        elif deal_value < 5_000_000_000:
            return 0.0
        else:
            return -0.1

    def _estimate_completion_timeline(self, deal_profile: DealProfile) -> Dict[str, Any]:
        """Estimate deal completion timeline"""
        base_days = 180  # 6 months base

        # Adjust based on deal type
        type_adjustments = {
            DealType.ASSET_PURCHASE: -30,
            DealType.ACQUISITION: 0,
            DealType.STRATEGIC_PARTNERSHIP: -60,
            DealType.JOINT_VENTURE: -45,
            DealType.MERGER: 60,
            DealType.DIVESTITURE: 30
        }

        base_days += type_adjustments.get(deal_profile.deal_type, 0)

        # Adjust based on deal size
        if deal_profile.deal_value > 1_000_000_000:
            base_days += 90
        elif deal_profile.deal_value > 5_000_000_000:
            base_days += 180

        estimated_close = datetime.now() + timedelta(days=base_days)

        return {
            "estimated_days": base_days,
            "estimated_close_date": estimated_close.isoformat(),
            "timeline_confidence": random.uniform(0.6, 0.9)
        }

    def _generate_executive_summary(self, deal_profile: DealProfile,
                                  deal_score: DealScore,
                                  strategic_fit: Dict[str, Any],
                                  transaction_probability: Dict[str, Any]) -> str:
        """Generate AI-powered executive summary"""

        summary_parts = []

        # Deal overview
        summary_parts.append(
            f"Analysis of {deal_profile.deal_type.value} opportunity involving "
            f"{deal_profile.target_company} valued at ${deal_profile.deal_value/1e9:.1f}B "
            f"in the {deal_profile.industry.value} sector."
        )

        # Score assessment
        if deal_score.overall_score >= 75:
            score_assessment = "highly attractive"
        elif deal_score.overall_score >= 60:
            score_assessment = "moderately attractive"
        elif deal_score.overall_score >= 40:
            score_assessment = "marginal"
        else:
            score_assessment = "unattractive"

        summary_parts.append(
            f"The opportunity scores {deal_score.overall_score}/100, indicating a "
            f"{score_assessment} investment with {strategic_fit['fit_level']} strategic fit."
        )

        # Key strengths and risks
        if deal_score.financial_score >= 70:
            summary_parts.append("Financial metrics are strong with attractive valuation.")
        if deal_score.risk_score <= 40:
            summary_parts.append("Risk profile is manageable with identified mitigation strategies.")

        # Probability and recommendation
        prob = transaction_probability['completion_probability']
        summary_parts.append(
            f"Transaction completion probability is estimated at {prob*100:.0f}% "
            f"with an expected timeline of {transaction_probability['estimated_timeline']['estimated_days']} days."
        )

        return " ".join(summary_parts)

    def _recommend_next_steps(self, deal_score: DealScore,
                            strategic_fit: Dict[str, Any]) -> List[str]:
        """Recommend next steps based on analysis"""
        next_steps = []

        if deal_score.overall_score >= 70:
            next_steps.append("Proceed with formal due diligence")
            next_steps.append("Engage investment committee for approval")
        elif deal_score.overall_score >= 50:
            next_steps.append("Conduct additional preliminary analysis")
            next_steps.append("Negotiate improved terms")
        else:
            next_steps.append("Consider strategic alternatives")
            next_steps.append("Re-evaluate investment thesis")

        if strategic_fit['integration_complexity'] == 'high':
            next_steps.append("Develop detailed integration plan")

        if deal_score.risk_score > 60:
            next_steps.append("Implement comprehensive risk mitigation")

        return next_steps

# Service instance management
_deal_intelligence_engine_instance = None

def get_deal_intelligence_engine() -> DealIntelligenceEngine:
    """Get singleton deal intelligence engine instance"""
    global _deal_intelligence_engine_instance
    if _deal_intelligence_engine_instance is None:
        _deal_intelligence_engine_instance = DealIntelligenceEngine()
    return _deal_intelligence_engine_instance