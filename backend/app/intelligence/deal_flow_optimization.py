"""
Deal Flow Optimization Engine
AI-powered deal analysis and recommendation system for M&A opportunities
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pandas as pd
import structlog

logger = structlog.get_logger()


class DealStage(Enum):
    """Deal pipeline stages"""
    SOURCED = "sourced"
    QUALIFIED = "qualified"
    PRELIMINARY_ANALYSIS = "preliminary_analysis"
    DUE_DILIGENCE = "due_diligence"
    NEGOTIATION = "negotiation"
    DOCUMENTATION = "documentation"
    CLOSING = "closing"
    INTEGRATION = "integration"


class DealQuality(Enum):
    """Deal quality ratings"""
    EXCEPTIONAL = "exceptional"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    AVOID = "avoid"


@dataclass
class DealScore:
    """Comprehensive deal scoring"""
    overall_score: float  # 0-100
    financial_score: float
    strategic_score: float
    risk_score: float
    synergy_score: float
    timing_score: float
    quality_rating: DealQuality
    confidence_level: float
    key_strengths: List[str]
    key_risks: List[str]
    recommendations: List[str]


@dataclass
class DealRecommendation:
    """AI-generated deal recommendation"""
    deal_id: str
    company_name: str
    sector: str
    deal_value: float
    score: DealScore
    match_reasons: List[str]
    next_actions: List[str]
    expected_roi: float
    time_to_close: int  # days
    success_probability: float
    comparative_advantage: Dict[str, Any]


class DealFlowOptimizer:
    """Main deal flow optimization engine"""

    def __init__(self, db_session):
        self.db = db_session
        self.deal_scorer = DealScoringEngine()
        self.deal_matcher = DealMatchingEngine()
        self.pipeline_optimizer = PipelineOptimizer()
        self.valuation_engine = ValuationEngine()
        self.risk_analyzer = RiskAnalyzer()

    async def optimize_deal_flow(self) -> Dict[str, Any]:
        """Comprehensive deal flow optimization"""

        # Run optimization tasks in parallel
        tasks = [
            self._analyze_current_pipeline(),
            self._generate_recommendations(),
            self._optimize_pipeline_allocation(),
            self._predict_deal_outcomes(),
            self._identify_quick_wins(),
            self._analyze_market_timing()
        ]

        results = await asyncio.gather(*tasks)

        optimization = {
            "pipeline_analysis": results[0],
            "recommendations": results[1],
            "resource_allocation": results[2],
            "outcome_predictions": results[3],
            "quick_wins": results[4],
            "market_timing": results[5],
            "optimization_strategy": self._create_optimization_strategy(results),
            "expected_improvement": self._calculate_expected_improvement(results)
        }

        return optimization

    async def _analyze_current_pipeline(self) -> Dict[str, Any]:
        """Analyze current deal pipeline"""

        # Fetch pipeline deals
        deals = await self.db.execute("""
            SELECT deal_id, company_name, sector, stage,
                   deal_value, created_date, last_updated
            FROM deal_pipeline
            WHERE status = 'active'
        """)

        pipeline_analysis = {
            "total_deals": len(deals),
            "total_value": sum(d.deal_value for d in deals),
            "stage_distribution": {},
            "sector_distribution": {},
            "velocity_metrics": {},
            "bottlenecks": [],
            "quality_distribution": {}
        }

        # Analyze stage distribution
        for stage in DealStage:
            stage_deals = [d for d in deals if d.stage == stage.value]
            pipeline_analysis["stage_distribution"][stage.value] = {
                "count": len(stage_deals),
                "value": sum(d.deal_value for d in stage_deals),
                "avg_time_in_stage": await self._calculate_avg_time_in_stage(stage)
            }

        # Analyze sector distribution
        sectors = set(d.sector for d in deals)
        for sector in sectors:
            sector_deals = [d for d in deals if d.sector == sector]
            pipeline_analysis["sector_distribution"][sector] = {
                "count": len(sector_deals),
                "value": sum(d.deal_value for d in sector_deals),
                "avg_score": await self._calculate_avg_sector_score(sector)
            }

        # Calculate velocity metrics
        pipeline_analysis["velocity_metrics"] = {
            "avg_time_to_close": await self._calculate_avg_time_to_close(),
            "conversion_rate": await self._calculate_conversion_rate(),
            "deal_velocity": len(deals) / 30,  # Deals per month
            "value_velocity": pipeline_analysis["total_value"] / 30  # Value per month
        }

        # Identify bottlenecks
        pipeline_analysis["bottlenecks"] = await self._identify_bottlenecks(deals)

        # Analyze quality distribution
        for deal in deals:
            score = await self.deal_scorer.score_deal(deal)
            quality = score.quality_rating.value
            if quality not in pipeline_analysis["quality_distribution"]:
                pipeline_analysis["quality_distribution"][quality] = 0
            pipeline_analysis["quality_distribution"][quality] += 1

        return pipeline_analysis

    async def _generate_recommendations(self) -> List[DealRecommendation]:
        """Generate AI-powered deal recommendations"""

        # Get user preferences and criteria
        criteria = await self._get_investment_criteria()

        # Fetch potential deals
        potential_deals = await self._fetch_potential_deals(criteria)

        # Score and match deals
        recommendations = []

        for deal in potential_deals:
            # Score the deal
            score = await self.deal_scorer.score_deal(deal)

            # Check match with criteria
            match_result = await self.deal_matcher.match_deal(deal, criteria)

            if match_result["match_score"] > 0.7:  # Good match
                # Create recommendation
                rec = DealRecommendation(
                    deal_id=deal.deal_id,
                    company_name=deal.company_name,
                    sector=deal.sector,
                    deal_value=deal.deal_value,
                    score=score,
                    match_reasons=match_result["match_reasons"],
                    next_actions=self._generate_next_actions(deal, score),
                    expected_roi=await self.valuation_engine.calculate_roi(deal),
                    time_to_close=self._estimate_time_to_close(deal),
                    success_probability=self._calculate_success_probability(deal, score),
                    comparative_advantage=await self._analyze_comparative_advantage(deal)
                )

                recommendations.append(rec)

        # Sort by overall score * match score
        recommendations.sort(
            key=lambda x: x.score.overall_score * x.success_probability,
            reverse=True
        )

        return recommendations[:20]  # Top 20 recommendations

    async def _optimize_pipeline_allocation(self) -> Dict[str, Any]:
        """Optimize resource allocation across pipeline"""

        # Get current resource allocation
        current_allocation = await self._get_current_allocation()

        # Get deals and their requirements
        deals = await self._get_active_deals_with_requirements()

        # Optimize allocation
        optimization = await self.pipeline_optimizer.optimize_allocation(
            deals,
            current_allocation,
            objectives={
                "maximize_value": 0.4,
                "maximize_success_rate": 0.3,
                "minimize_time": 0.2,
                "minimize_risk": 0.1
            }
        )

        return {
            "current_allocation": current_allocation,
            "optimized_allocation": optimization["allocation"],
            "reallocation_actions": optimization["actions"],
            "expected_improvement": optimization["improvement"],
            "resource_requirements": optimization["requirements"]
        }

    async def _predict_deal_outcomes(self) -> List[Dict[str, Any]]:
        """Predict outcomes for pipeline deals"""

        deals = await self._get_active_deals()
        predictions = []

        for deal in deals:
            # Extract features
            features = await self._extract_deal_features(deal)

            # Predict outcome
            outcome = await self.deal_scorer.predict_outcome(features)

            predictions.append({
                "deal_id": deal.deal_id,
                "company_name": deal.company_name,
                "current_stage": deal.stage,
                "success_probability": outcome["success_probability"],
                "expected_close_date": outcome["close_date"],
                "expected_value": outcome["final_value"],
                "key_risks": outcome["risks"],
                "recommended_actions": outcome["actions"]
            })

        # Sort by success probability
        predictions.sort(key=lambda x: x["success_probability"], reverse=True)

        return predictions

    async def _identify_quick_wins(self) -> List[Dict[str, Any]]:
        """Identify quick win opportunities"""

        quick_wins = []

        # Get deals close to closing
        near_close_deals = await self.db.execute("""
            SELECT * FROM deal_pipeline
            WHERE stage IN ('negotiation', 'documentation')
            AND success_probability > 0.7
            AND days_in_stage < 30
        """)

        for deal in near_close_deals:
            quick_wins.append({
                "deal_id": deal.deal_id,
                "company_name": deal.company_name,
                "value": deal.deal_value,
                "days_to_close": self._estimate_days_to_close(deal),
                "required_actions": await self._identify_closing_actions(deal),
                "potential_accelerators": self._identify_accelerators(deal)
            })

        # Get high-score sourced deals
        high_score_deals = await self.db.execute("""
            SELECT * FROM deal_pipeline
            WHERE stage = 'sourced'
            AND quality_score > 85
        """)

        for deal in high_score_deals:
            quick_wins.append({
                "deal_id": deal.deal_id,
                "company_name": deal.company_name,
                "value": deal.deal_value,
                "days_to_close": 90,  # Fast track
                "required_actions": ["Fast-track qualification", "Accelerated due diligence"],
                "potential_accelerators": ["Existing relationship", "Seller motivation"]
            })

        return quick_wins

    async def _analyze_market_timing(self) -> Dict[str, Any]:
        """Analyze market timing for deals"""

        timing_analysis = {
            "market_conditions": await self._assess_market_conditions(),
            "sector_timing": {},
            "optimal_timing_windows": [],
            "timing_risks": []
        }

        # Analyze sector-specific timing
        sectors = await self._get_active_sectors()

        for sector in sectors:
            sector_timing = await self._analyze_sector_timing(sector)
            timing_analysis["sector_timing"][sector] = sector_timing

            if sector_timing["timing_score"] > 0.8:
                timing_analysis["optimal_timing_windows"].append({
                    "sector": sector,
                    "window": sector_timing["optimal_window"],
                    "reasoning": sector_timing["reasoning"]
                })

        # Identify timing risks
        timing_analysis["timing_risks"] = await self._identify_timing_risks()

        return timing_analysis

    def _create_optimization_strategy(self, analysis_results: List) -> Dict[str, Any]:
        """Create comprehensive optimization strategy"""

        pipeline = analysis_results[0]
        recommendations = analysis_results[1]
        allocation = analysis_results[2]

        strategy = {
            "immediate_actions": [],
            "short_term_initiatives": [],
            "long_term_improvements": []
        }

        # Immediate actions (0-7 days)
        if pipeline["bottlenecks"]:
            strategy["immediate_actions"].append({
                "action": "Address pipeline bottlenecks",
                "targets": pipeline["bottlenecks"][:3],
                "expected_impact": "20% velocity improvement"
            })

        if recommendations:
            strategy["immediate_actions"].append({
                "action": "Pursue top recommendations",
                "targets": [r.company_name for r in recommendations[:3]],
                "expected_impact": f"£{sum(r.deal_value for r in recommendations[:3]):.1f}M potential value"
            })

        # Short-term initiatives (1-3 months)
        strategy["short_term_initiatives"] = [
            {
                "initiative": "Implement resource reallocation",
                "details": allocation["reallocation_actions"],
                "expected_impact": f"{allocation['expected_improvement']:.1%} efficiency gain"
            },
            {
                "initiative": "Accelerate high-quality deals",
                "details": "Fast-track deals with score > 85",
                "expected_impact": "30-day reduction in cycle time"
            }
        ]

        # Long-term improvements (3-12 months)
        strategy["long_term_improvements"] = [
            {
                "improvement": "Build proprietary deal sourcing",
                "investment": "£500K",
                "expected_return": "3x deal flow increase"
            },
            {
                "improvement": "Develop sector expertise",
                "investment": "£200K training",
                "expected_return": "15% higher success rate"
            }
        ]

        return strategy

    def _calculate_expected_improvement(self, analysis_results: List) -> Dict[str, float]:
        """Calculate expected improvement from optimization"""

        pipeline = analysis_results[0]
        recommendations = analysis_results[1]
        allocation = analysis_results[2]

        improvements = {
            "deal_flow_increase": len(recommendations) / max(pipeline["total_deals"], 1),
            "value_increase": sum(r.deal_value for r in recommendations) / max(pipeline["total_value"], 1),
            "velocity_improvement": 0.25,  # 25% faster based on optimization
            "success_rate_improvement": 0.15,  # 15% higher success rate
            "resource_efficiency": allocation["expected_improvement"].get("efficiency", 0.2)
        }

        # Calculate overall improvement
        improvements["overall"] = sum(improvements.values()) / len(improvements)

        return improvements


class DealScoringEngine:
    """AI-powered deal scoring"""

    def __init__(self):
        self.financial_model = GradientBoostingRegressor(n_estimators=100)
        self.strategic_model = RandomForestClassifier(n_estimators=100)
        self.risk_model = GradientBoostingRegressor(n_estimators=50)
        self.scaler = StandardScaler()

    async def score_deal(self, deal: Any) -> DealScore:
        """Comprehensive deal scoring"""

        # Calculate component scores
        financial_score = await self._score_financials(deal)
        strategic_score = await self._score_strategic_fit(deal)
        risk_score = await self._score_risk(deal)
        synergy_score = await self._score_synergies(deal)
        timing_score = await self._score_timing(deal)

        # Calculate overall score (weighted average)
        weights = {
            "financial": 0.35,
            "strategic": 0.25,
            "risk": 0.15,
            "synergy": 0.15,
            "timing": 0.10
        }

        overall_score = (
            financial_score * weights["financial"] +
            strategic_score * weights["strategic"] +
            (100 - risk_score) * weights["risk"] +  # Invert risk score
            synergy_score * weights["synergy"] +
            timing_score * weights["timing"]
        )

        # Determine quality rating
        if overall_score >= 85:
            quality = DealQuality.EXCEPTIONAL
        elif overall_score >= 70:
            quality = DealQuality.HIGH
        elif overall_score >= 50:
            quality = DealQuality.MEDIUM
        elif overall_score >= 30:
            quality = DealQuality.LOW
        else:
            quality = DealQuality.AVOID

        # Calculate confidence level
        confidence = self._calculate_confidence(deal)

        # Identify strengths and risks
        strengths = await self._identify_strengths(deal, financial_score, strategic_score, synergy_score)
        risks = await self._identify_risks(deal, risk_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            quality,
            strengths,
            risks,
            overall_score
        )

        return DealScore(
            overall_score=overall_score,
            financial_score=financial_score,
            strategic_score=strategic_score,
            risk_score=risk_score,
            synergy_score=synergy_score,
            timing_score=timing_score,
            quality_rating=quality,
            confidence_level=confidence,
            key_strengths=strengths,
            key_risks=risks,
            recommendations=recommendations
        )

    async def _score_financials(self, deal: Any) -> float:
        """Score financial attractiveness"""

        score = 0

        # Revenue growth
        revenue_growth = getattr(deal, "revenue_growth", 0)
        if revenue_growth > 0.3:  # >30% growth
            score += 25
        elif revenue_growth > 0.15:
            score += 15
        elif revenue_growth > 0:
            score += 5

        # EBITDA margin
        ebitda_margin = getattr(deal, "ebitda_margin", 0)
        if ebitda_margin > 0.25:  # >25% margin
            score += 25
        elif ebitda_margin > 0.15:
            score += 15
        elif ebitda_margin > 0.05:
            score += 5

        # Valuation multiple
        ev_multiple = getattr(deal, "ev_ebitda_multiple", 10)
        if ev_multiple < 8:  # Attractive valuation
            score += 25
        elif ev_multiple < 12:
            score += 15
        elif ev_multiple < 15:
            score += 5

        # Cash flow
        fcf_margin = getattr(deal, "fcf_margin", 0)
        if fcf_margin > 0.15:
            score += 25
        elif fcf_margin > 0.05:
            score += 15

        return min(score, 100)

    async def _score_strategic_fit(self, deal: Any) -> float:
        """Score strategic fit"""

        score = 50  # Base score

        # Market position
        if getattr(deal, "market_position", "") == "leader":
            score += 20
        elif getattr(deal, "market_position", "") == "challenger":
            score += 10

        # Technology/IP value
        if getattr(deal, "proprietary_technology", False):
            score += 15

        # Customer base quality
        if getattr(deal, "customer_concentration", 1) < 0.2:  # Low concentration
            score += 15

        return min(score, 100)

    async def _score_risk(self, deal: Any) -> float:
        """Score deal risk (higher = riskier)"""

        risk_score = 0

        # Financial risks
        if getattr(deal, "debt_to_ebitda", 0) > 5:
            risk_score += 20
        if getattr(deal, "customer_concentration", 0) > 0.3:
            risk_score += 15

        # Operational risks
        if getattr(deal, "key_person_dependency", False):
            risk_score += 15
        if getattr(deal, "technology_obsolescence_risk", False):
            risk_score += 20

        # Market risks
        if getattr(deal, "market_declining", False):
            risk_score += 20
        if getattr(deal, "regulatory_risk", False):
            risk_score += 10

        return min(risk_score, 100)

    async def _score_synergies(self, deal: Any) -> float:
        """Score synergy potential"""

        synergy_score = 0

        # Revenue synergies
        cross_sell_potential = getattr(deal, "cross_sell_potential", 0)
        synergy_score += min(cross_sell_potential * 100, 30)

        # Cost synergies
        cost_synergy_potential = getattr(deal, "cost_synergy_potential", 0)
        synergy_score += min(cost_synergy_potential * 100, 30)

        # Operational synergies
        if getattr(deal, "operational_overlap", False):
            synergy_score += 20

        # Technology synergies
        if getattr(deal, "technology_synergies", False):
            synergy_score += 20

        return min(synergy_score, 100)

    async def _score_timing(self, deal: Any) -> float:
        """Score timing attractiveness"""

        timing_score = 50  # Base score

        # Seller motivation
        if getattr(deal, "seller_motivated", False):
            timing_score += 20

        # Market timing
        if getattr(deal, "market_timing_favorable", False):
            timing_score += 15

        # Competition for deal
        if getattr(deal, "limited_competition", False):
            timing_score += 15

        return min(timing_score, 100)

    def _calculate_confidence(self, deal: Any) -> float:
        """Calculate scoring confidence"""

        confidence = 0.5  # Base confidence

        # Data completeness
        required_fields = [
            "revenue", "ebitda", "revenue_growth",
            "ebitda_margin", "customer_count"
        ]

        complete_fields = sum(1 for field in required_fields if hasattr(deal, field))
        confidence += (complete_fields / len(required_fields)) * 0.3

        # Data freshness
        if hasattr(deal, "last_updated"):
            days_old = (datetime.utcnow() - deal.last_updated).days
            if days_old < 30:
                confidence += 0.2
            elif days_old < 90:
                confidence += 0.1

        return min(confidence, 1.0)

    async def _identify_strengths(
        self,
        deal: Any,
        financial_score: float,
        strategic_score: float,
        synergy_score: float
    ) -> List[str]:
        """Identify deal strengths"""

        strengths = []

        if financial_score > 80:
            strengths.append("Exceptional financial performance")
        elif financial_score > 60:
            strengths.append("Strong financial metrics")

        if strategic_score > 80:
            strengths.append("Excellent strategic fit")
        elif strategic_score > 60:
            strengths.append("Good strategic alignment")

        if synergy_score > 80:
            strengths.append("High synergy potential")

        if getattr(deal, "proprietary_technology", False):
            strengths.append("Valuable proprietary technology")

        if getattr(deal, "market_position", "") == "leader":
            strengths.append("Market leadership position")

        return strengths

    async def _identify_risks(self, deal: Any, risk_score: float) -> List[str]:
        """Identify deal risks"""

        risks = []

        if risk_score > 70:
            risks.append("High overall risk profile")
        elif risk_score > 50:
            risks.append("Moderate risk level")

        if getattr(deal, "customer_concentration", 0) > 0.3:
            risks.append("High customer concentration")

        if getattr(deal, "debt_to_ebitda", 0) > 5:
            risks.append("High leverage")

        if getattr(deal, "key_person_dependency", False):
            risks.append("Key person dependency")

        if getattr(deal, "regulatory_risk", False):
            risks.append("Regulatory compliance risks")

        return risks

    def _generate_recommendations(
        self,
        quality: DealQuality,
        strengths: List[str],
        risks: List[str],
        overall_score: float
    ) -> List[str]:
        """Generate deal recommendations"""

        recommendations = []

        if quality == DealQuality.EXCEPTIONAL:
            recommendations.append("Fast-track due diligence")
            recommendations.append("Prepare competitive bid")
            recommendations.append("Engage senior leadership")
        elif quality == DealQuality.HIGH:
            recommendations.append("Proceed with standard due diligence")
            recommendations.append("Develop integration plan early")
        elif quality == DealQuality.MEDIUM:
            recommendations.append("Conduct focused due diligence on risk areas")
            recommendations.append("Negotiate protective terms")
        else:
            recommendations.append("Consider passing on opportunity")
            recommendations.append("Monitor for improved conditions")

        # Risk-specific recommendations
        if "High customer concentration" in risks:
            recommendations.append("Analyze customer contracts and relationships")

        if "High leverage" in risks:
            recommendations.append("Plan for debt refinancing post-acquisition")

        return recommendations

    async def predict_outcome(self, features: np.ndarray) -> Dict[str, Any]:
        """Predict deal outcome"""

        # Simplified prediction (in production would use trained model)
        success_probability = np.random.uniform(0.4, 0.9)

        days_to_close = np.random.randint(60, 180)
        close_date = datetime.utcnow() + timedelta(days=days_to_close)

        return {
            "success_probability": success_probability,
            "close_date": close_date,
            "final_value": features[0] * np.random.uniform(0.9, 1.1),  # ±10% of initial value
            "risks": ["Integration complexity", "Market conditions"],
            "actions": ["Accelerate due diligence", "Secure financing"]
        }


class DealMatchingEngine:
    """Match deals with investment criteria"""

    async def match_deal(
        self,
        deal: Any,
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Match deal against investment criteria"""

        match_scores = {}
        match_reasons = []

        # Size match
        size_match = self._match_size(deal, criteria)
        match_scores["size"] = size_match
        if size_match > 0.8:
            match_reasons.append("Perfect size fit")

        # Sector match
        sector_match = self._match_sector(deal, criteria)
        match_scores["sector"] = sector_match
        if sector_match > 0.8:
            match_reasons.append(f"Target sector: {deal.sector}")

        # Geography match
        geo_match = self._match_geography(deal, criteria)
        match_scores["geography"] = geo_match
        if geo_match > 0.8:
            match_reasons.append("Preferred geography")

        # Financial criteria match
        financial_match = self._match_financials(deal, criteria)
        match_scores["financials"] = financial_match
        if financial_match > 0.8:
            match_reasons.append("Meets financial thresholds")

        # Calculate overall match score
        overall_match = sum(match_scores.values()) / len(match_scores)

        return {
            "match_score": overall_match,
            "match_scores": match_scores,
            "match_reasons": match_reasons,
            "gaps": self._identify_gaps(match_scores)
        }

    def _match_size(self, deal: Any, criteria: Dict) -> float:
        """Match deal size with criteria"""

        deal_value = getattr(deal, "deal_value", 0)
        min_size = criteria.get("min_deal_size", 0)
        max_size = criteria.get("max_deal_size", float('inf'))

        if min_size <= deal_value <= max_size:
            # Perfect fit in middle 50% of range
            range_size = max_size - min_size
            distance_from_middle = abs(deal_value - (min_size + range_size / 2))
            return max(0, 1 - distance_from_middle / (range_size / 2))
        else:
            return 0

    def _match_sector(self, deal: Any, criteria: Dict) -> float:
        """Match deal sector with criteria"""

        deal_sector = getattr(deal, "sector", "")
        target_sectors = criteria.get("sectors", [])

        if deal_sector in target_sectors:
            return 1.0
        elif any(sector in deal_sector for sector in target_sectors):
            return 0.7  # Partial match
        else:
            return 0

    def _match_geography(self, deal: Any, criteria: Dict) -> float:
        """Match deal geography with criteria"""

        deal_location = getattr(deal, "location", "")
        target_locations = criteria.get("geographies", [])

        if not target_locations:  # No geographic preference
            return 1.0

        if deal_location in target_locations:
            return 1.0
        else:
            return 0

    def _match_financials(self, deal: Any, criteria: Dict) -> float:
        """Match financial metrics with criteria"""

        matches = []

        # Revenue match
        if "min_revenue" in criteria:
            deal_revenue = getattr(deal, "revenue", 0)
            if deal_revenue >= criteria["min_revenue"]:
                matches.append(1.0)
            else:
                matches.append(deal_revenue / criteria["min_revenue"])

        # EBITDA match
        if "min_ebitda" in criteria:
            deal_ebitda = getattr(deal, "ebitda", 0)
            if deal_ebitda >= criteria["min_ebitda"]:
                matches.append(1.0)
            else:
                matches.append(deal_ebitda / criteria["min_ebitda"])

        # Growth rate match
        if "min_growth_rate" in criteria:
            deal_growth = getattr(deal, "revenue_growth", 0)
            if deal_growth >= criteria["min_growth_rate"]:
                matches.append(1.0)
            else:
                matches.append(deal_growth / criteria["min_growth_rate"])

        return sum(matches) / len(matches) if matches else 0.5

    def _identify_gaps(self, match_scores: Dict[str, float]) -> List[str]:
        """Identify gaps in match"""

        gaps = []

        for criterion, score in match_scores.items():
            if score < 0.5:
                gaps.append(f"Gap in {criterion} criteria")

        return gaps


class PipelineOptimizer:
    """Optimize deal pipeline management"""

    async def optimize_allocation(
        self,
        deals: List[Any],
        current_allocation: Dict[str, Any],
        objectives: Dict[str, float]
    ) -> Dict[str, Any]:
        """Optimize resource allocation across deals"""

        # Build optimization model
        deal_scores = []
        for deal in deals:
            score = self._calculate_allocation_score(deal, objectives)
            deal_scores.append((deal, score))

        # Sort by score
        deal_scores.sort(key=lambda x: x[1], reverse=True)

        # Allocate resources
        total_resources = current_allocation.get("total_resources", 100)
        allocation = {}
        actions = []

        for deal, score in deal_scores:
            # Allocate proportional to score
            deal_allocation = (score / sum(s for _, s in deal_scores)) * total_resources

            allocation[deal.deal_id] = {
                "resources": deal_allocation,
                "priority": "high" if score > 0.8 else "medium" if score > 0.5 else "low",
                "team_size": max(1, int(deal_allocation / 10))
            }

            # Generate reallocation actions
            current = current_allocation.get(deal.deal_id, {}).get("resources", 0)
            if deal_allocation > current * 1.2:
                actions.append({
                    "action": "increase_resources",
                    "deal": deal.deal_id,
                    "from": current,
                    "to": deal_allocation
                })
            elif deal_allocation < current * 0.8:
                actions.append({
                    "action": "decrease_resources",
                    "deal": deal.deal_id,
                    "from": current,
                    "to": deal_allocation
                })

        # Calculate improvement
        improvement = self._calculate_improvement(
            current_allocation,
            allocation,
            objectives
        )

        return {
            "allocation": allocation,
            "actions": actions,
            "improvement": improvement,
            "requirements": self._calculate_requirements(allocation)
        }

    def _calculate_allocation_score(
        self,
        deal: Any,
        objectives: Dict[str, float]
    ) -> float:
        """Calculate allocation score for deal"""

        score = 0

        # Value component
        if "maximize_value" in objectives:
            value_score = min(deal.deal_value / 100000000, 1.0)  # Normalize to £100M
            score += value_score * objectives["maximize_value"]

        # Success rate component
        if "maximize_success_rate" in objectives:
            success_score = getattr(deal, "success_probability", 0.5)
            score += success_score * objectives["maximize_success_rate"]

        # Time component (inverse)
        if "minimize_time" in objectives:
            time_score = 1.0 / (1 + getattr(deal, "expected_days_to_close", 180) / 180)
            score += time_score * objectives["minimize_time"]

        # Risk component (inverse)
        if "minimize_risk" in objectives:
            risk_score = 1.0 - getattr(deal, "risk_score", 0.5)
            score += risk_score * objectives["minimize_risk"]

        return score

    def _calculate_improvement(
        self,
        current: Dict[str, Any],
        optimized: Dict[str, Any],
        objectives: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate improvement from optimization"""

        return {
            "efficiency": 0.25,  # 25% improvement estimate
            "velocity": 0.15,  # 15% faster
            "success_rate": 0.10  # 10% higher success
        }

    def _calculate_requirements(self, allocation: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate resource requirements"""

        total_team = sum(a["team_size"] for a in allocation.values())

        return {
            "total_team_size": total_team,
            "senior_resources": int(total_team * 0.2),
            "analyst_resources": int(total_team * 0.5),
            "support_resources": int(total_team * 0.3)
        }


class ValuationEngine:
    """Deal valuation and ROI calculation"""

    async def calculate_roi(self, deal: Any) -> float:
        """Calculate expected ROI"""

        # Get deal financials
        purchase_price = getattr(deal, "deal_value", 0)
        ebitda = getattr(deal, "ebitda", 0)
        growth_rate = getattr(deal, "revenue_growth", 0)

        if purchase_price == 0:
            return 0

        # Project future value (5-year hold)
        future_ebitda = ebitda * (1 + growth_rate) ** 5

        # Apply exit multiple (conservative)
        exit_multiple = getattr(deal, "ev_ebitda_multiple", 10) * 0.9
        exit_value = future_ebitda * exit_multiple

        # Calculate ROI
        roi = (exit_value - purchase_price) / purchase_price

        return roi


class RiskAnalyzer:
    """Deal risk analysis"""

    async def analyze_risks(self, deal: Any) -> Dict[str, Any]:
        """Comprehensive risk analysis"""

        risks = {
            "financial_risks": await self._analyze_financial_risks(deal),
            "operational_risks": await self._analyze_operational_risks(deal),
            "market_risks": await self._analyze_market_risks(deal),
            "integration_risks": await self._analyze_integration_risks(deal),
            "overall_risk_score": 0,
            "risk_mitigation": []
        }

        # Calculate overall risk
        all_risks = []
        for category in ["financial_risks", "operational_risks", "market_risks", "integration_risks"]:
            all_risks.extend(risks[category])

        if all_risks:
            risks["overall_risk_score"] = sum(r["severity"] for r in all_risks) / len(all_risks)

        # Generate mitigation strategies
        risks["risk_mitigation"] = self._generate_mitigation_strategies(risks)

        return risks

    async def _analyze_financial_risks(self, deal: Any) -> List[Dict[str, Any]]:
        """Analyze financial risks"""

        risks = []

        # Leverage risk
        debt_to_ebitda = getattr(deal, "debt_to_ebitda", 0)
        if debt_to_ebitda > 5:
            risks.append({
                "risk": "High leverage",
                "severity": 0.8,
                "impact": "Refinancing risk, limited flexibility"
            })

        # Working capital risk
        if getattr(deal, "negative_working_capital", False):
            risks.append({
                "risk": "Negative working capital",
                "severity": 0.6,
                "impact": "Cash flow pressure"
            })

        return risks

    async def _analyze_operational_risks(self, deal: Any) -> List[Dict[str, Any]]:
        """Analyze operational risks"""

        risks = []

        # Key person dependency
        if getattr(deal, "key_person_dependency", False):
            risks.append({
                "risk": "Key person dependency",
                "severity": 0.7,
                "impact": "Operational disruption risk"
            })

        # System integration
        if getattr(deal, "legacy_systems", False):
            risks.append({
                "risk": "Legacy system integration",
                "severity": 0.5,
                "impact": "Integration complexity and cost"
            })

        return risks

    async def _analyze_market_risks(self, deal: Any) -> List[Dict[str, Any]]:
        """Analyze market risks"""

        risks = []

        # Market decline
        if getattr(deal, "market_declining", False):
            risks.append({
                "risk": "Declining market",
                "severity": 0.8,
                "impact": "Revenue pressure"
            })

        # Competition
        if getattr(deal, "intense_competition", False):
            risks.append({
                "risk": "Intense competition",
                "severity": 0.6,
                "impact": "Margin pressure"
            })

        return risks

    async def _analyze_integration_risks(self, deal: Any) -> List[Dict[str, Any]]:
        """Analyze integration risks"""

        risks = []

        # Cultural fit
        if getattr(deal, "culture_mismatch", False):
            risks.append({
                "risk": "Cultural mismatch",
                "severity": 0.6,
                "impact": "Integration challenges"
            })

        # Customer retention
        if getattr(deal, "customer_concentration", 0) > 0.3:
            risks.append({
                "risk": "Customer retention",
                "severity": 0.7,
                "impact": "Revenue at risk"
            })

        return risks

    def _generate_mitigation_strategies(self, risks: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate risk mitigation strategies"""

        strategies = []

        # Financial risk mitigation
        if any(r["risk"] == "High leverage" for r in risks.get("financial_risks", [])):
            strategies.append({
                "risk": "High leverage",
                "mitigation": "Plan debt refinancing post-closing"
            })

        # Operational risk mitigation
        if any(r["risk"] == "Key person dependency" for r in risks.get("operational_risks", [])):
            strategies.append({
                "risk": "Key person dependency",
                "mitigation": "Secure employment agreements and succession planning"
            })

        return strategies