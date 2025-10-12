"""
Deal Outcome Prediction Models
ML models for predicting M&A deal success, timeline, and value optimization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class DealOutcome(str, Enum):
    """Possible deal outcomes"""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DealPrediction:
    """Deal outcome prediction result"""
    deal_id: str
    predicted_outcome: DealOutcome
    success_probability: float
    failure_probability: float
    expected_completion_date: datetime
    predicted_value: float
    risk_level: RiskLevel
    risk_factors: List[str]
    confidence_score: float
    model_version: str
    prediction_date: datetime
    key_insights: List[str]
    recommendations: List[str]


@dataclass
class MarketTrend:
    """Market trend analysis result"""
    trend_id: str
    market_segment: str
    trend_direction: str  # "upward", "downward", "stable", "volatile"
    trend_strength: float  # 0.0 to 1.0
    confidence_level: float
    timeframe: str
    key_indicators: List[Dict[str, Any]]
    predictions: List[Dict[str, Any]]
    analysis_date: datetime


class DealOutcomePredictionModel:
    """ML model for predicting deal outcomes using historical data"""

    def __init__(self):
        self.model_version = "1.0.0"
        self.feature_weights = {
            "deal_value": 0.25,
            "industry_sector": 0.20,
            "deal_stage": 0.15,
            "team_experience": 0.15,
            "market_conditions": 0.10,
            "regulatory_complexity": 0.10,
            "timeline_pressure": 0.05
        }

    async def predict_deal_outcome(
        self,
        deal_data: Dict[str, Any],
        db: Session
    ) -> DealPrediction:
        """Predict deal outcome based on current deal data"""
        try:
            # Extract features from deal data
            features = await self._extract_deal_features(deal_data, db)

            # Calculate prediction scores
            success_prob = await self._calculate_success_probability(features)
            failure_prob = 1.0 - success_prob

            # Predict completion timeline
            expected_completion = await self._predict_completion_date(features, deal_data)

            # Predict deal value
            predicted_value = await self._predict_deal_value(features, deal_data)

            # Assess risk level
            risk_level, risk_factors = await self._assess_deal_risks(features, deal_data)

            # Calculate confidence score
            confidence = await self._calculate_confidence_score(features)

            # Generate insights and recommendations
            insights = await self._generate_key_insights(features, success_prob)
            recommendations = await self._generate_recommendations(features, risk_level)

            # Determine predicted outcome
            if success_prob > 0.7:
                predicted_outcome = DealOutcome.SUCCESS
            elif success_prob < 0.3:
                predicted_outcome = DealOutcome.FAILURE
            else:
                predicted_outcome = DealOutcome.PENDING

            return DealPrediction(
                deal_id=deal_data.get("id", ""),
                predicted_outcome=predicted_outcome,
                success_probability=success_prob,
                failure_probability=failure_prob,
                expected_completion_date=expected_completion,
                predicted_value=predicted_value,
                risk_level=risk_level,
                risk_factors=risk_factors,
                confidence_score=confidence,
                model_version=self.model_version,
                prediction_date=datetime.utcnow(),
                key_insights=insights,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Deal prediction failed: {str(e)}")
            raise

    async def _extract_deal_features(
        self,
        deal_data: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Extract relevant features from deal data"""

        # Basic deal features
        features = {
            "deal_value": float(deal_data.get("estimated_value", 0)) / 1_000_000,  # Normalize to millions
            "deal_age_days": (datetime.utcnow() - datetime.fromisoformat(
                deal_data.get("created_at", datetime.utcnow().isoformat())
            )).days,
            "stage_progress": self._calculate_stage_progress(deal_data.get("status", "")),
            "industry_risk_score": self._get_industry_risk_score(deal_data.get("industry", "")),
            "team_size": len(deal_data.get("team_members", [])),
            "document_count": deal_data.get("document_count", 0),
            "activity_count": deal_data.get("activity_count", 0)
        }

        # Historical performance features
        historical_features = await self._get_historical_features(deal_data, db)
        features.update(historical_features)

        # Market condition features
        market_features = await self._get_market_condition_features(deal_data)
        features.update(market_features)

        return features

    def _calculate_stage_progress(self, status: str) -> float:
        """Calculate progress based on deal stage"""
        stage_weights = {
            "prospecting": 0.1,
            "initial_contact": 0.2,
            "qualification": 0.3,
            "proposal": 0.5,
            "negotiation": 0.7,
            "due_diligence": 0.8,
            "closing": 0.9,
            "completed": 1.0,
            "lost": 0.0
        }
        return stage_weights.get(status.lower(), 0.5)

    def _get_industry_risk_score(self, industry: str) -> float:
        """Get risk score based on industry sector"""
        industry_risks = {
            "technology": 0.6,
            "healthcare": 0.4,
            "financial_services": 0.3,
            "manufacturing": 0.5,
            "energy": 0.7,
            "retail": 0.8,
            "real_estate": 0.5,
            "telecommunications": 0.4
        }
        return industry_risks.get(industry.lower(), 0.5)

    async def _get_historical_features(
        self,
        deal_data: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Extract features from historical deal performance"""
        try:
            # Get organization's historical deal performance
            org_id = deal_data.get("organization_id")

            query = text("""
                SELECT
                    COUNT(*) as total_deals,
                    AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_rate,
                    AVG(estimated_value) as avg_deal_value,
                    AVG(EXTRACT(DAY FROM (updated_at - created_at))) as avg_duration
                FROM deals
                WHERE organization_id = :org_id
                AND created_at < :current_deal_date
            """)

            result = db.execute(query, {
                "org_id": org_id,
                "current_deal_date": deal_data.get("created_at", datetime.utcnow())
            }).fetchone()

            if result and result[0] > 0:
                return {
                    "historical_success_rate": float(result[1] or 0),
                    "historical_avg_value": float(result[2] or 0) / 1_000_000,
                    "historical_avg_duration": float(result[3] or 30),
                    "organization_experience": min(float(result[0]), 100) / 100  # Cap at 100 deals
                }
            else:
                return {
                    "historical_success_rate": 0.5,  # Neutral for new organizations
                    "historical_avg_value": 1.0,
                    "historical_avg_duration": 30,
                    "organization_experience": 0.1
                }

        except Exception as e:
            logger.warning(f"Could not fetch historical features: {str(e)}")
            return {
                "historical_success_rate": 0.5,
                "historical_avg_value": 1.0,
                "historical_avg_duration": 30,
                "organization_experience": 0.1
            }

    async def _get_market_condition_features(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract market condition features"""
        # Simplified market conditions - in production, this would use real market data
        current_month = datetime.utcnow().month

        # Seasonal factors (Q4 typically has higher deal activity)
        seasonal_factor = 1.2 if current_month in [10, 11, 12] else 1.0

        return {
            "market_volatility": 0.5,  # Would use real market volatility index
            "sector_performance": 0.6,  # Would use sector-specific performance data
            "seasonal_factor": seasonal_factor,
            "regulatory_environment": 0.5  # Would use regulatory complexity index
        }

    async def _calculate_success_probability(self, features: Dict[str, Any]) -> float:
        """Calculate deal success probability using weighted features"""

        # Feature scoring (0.0 to 1.0)
        scores = {}

        # Deal value scoring (higher value = higher probability up to a point)
        deal_value = features.get("deal_value", 1.0)
        scores["value_score"] = min(deal_value / 10, 1.0) * 0.8 + 0.2

        # Stage progress scoring
        scores["stage_score"] = features.get("stage_progress", 0.5)

        # Experience scoring
        scores["experience_score"] = features.get("organization_experience", 0.1)

        # Historical success rate
        scores["history_score"] = features.get("historical_success_rate", 0.5)

        # Market conditions scoring
        market_score = (
            features.get("seasonal_factor", 1.0) * 0.4 +
            (1 - features.get("market_volatility", 0.5)) * 0.3 +
            features.get("sector_performance", 0.5) * 0.3
        ) / 1.0
        scores["market_score"] = min(market_score, 1.0)

        # Industry risk (inverse scoring)
        scores["industry_score"] = 1.0 - features.get("industry_risk_score", 0.5)

        # Team and activity scoring
        team_size = features.get("team_size", 1)
        activity_count = features.get("activity_count", 0)
        scores["engagement_score"] = min((team_size * 0.1 + activity_count * 0.01), 1.0)

        # Weighted average
        weights = {
            "value_score": 0.2,
            "stage_score": 0.25,
            "experience_score": 0.15,
            "history_score": 0.15,
            "market_score": 0.1,
            "industry_score": 0.1,
            "engagement_score": 0.05
        }

        probability = sum(scores[key] * weights[key] for key in scores.keys())

        # Apply noise and bounds
        probability = max(0.05, min(0.95, probability))

        return round(probability, 3)

    async def _predict_completion_date(
        self,
        features: Dict[str, Any],
        deal_data: Dict[str, Any]
    ) -> datetime:
        """Predict expected completion date"""

        # Base timeline by deal value (larger deals take longer)
        deal_value = features.get("deal_value", 1.0)
        base_days = 30 + (deal_value * 10)  # 30-130 days base

        # Adjust for stage progress
        stage_progress = features.get("stage_progress", 0.5)
        remaining_progress = 1.0 - stage_progress
        adjusted_days = base_days * remaining_progress

        # Adjust for team size (more team members = faster)
        team_size = features.get("team_size", 1)
        team_factor = max(0.7, 1.0 - (team_size - 1) * 0.05)
        adjusted_days *= team_factor

        # Adjust for industry complexity
        industry_risk = features.get("industry_risk_score", 0.5)
        industry_factor = 1.0 + (industry_risk * 0.5)
        adjusted_days *= industry_factor

        # Adjust for organization experience
        experience = features.get("organization_experience", 0.1)
        experience_factor = max(0.8, 1.0 - experience * 0.3)
        adjusted_days *= experience_factor

        # Add some randomness and round
        final_days = max(7, int(adjusted_days))

        start_date = datetime.fromisoformat(
            deal_data.get("created_at", datetime.utcnow().isoformat())
        )

        return start_date + timedelta(days=final_days)

    async def _predict_deal_value(
        self,
        features: Dict[str, Any],
        deal_data: Dict[str, Any]
    ) -> float:
        """Predict final deal value"""

        current_value = float(deal_data.get("estimated_value", 0))

        if current_value == 0:
            # Use historical average if no current estimate
            return features.get("historical_avg_value", 1.0) * 1_000_000

        # Adjust based on success probability and market conditions
        success_prob = await self._calculate_success_probability(features)
        market_factor = features.get("seasonal_factor", 1.0) * features.get("sector_performance", 0.5)

        # Higher success probability and better market conditions = higher value
        value_multiplier = 0.8 + (success_prob * 0.3) + (market_factor * 0.2)

        predicted_value = current_value * value_multiplier

        return round(predicted_value, 2)

    async def _assess_deal_risks(
        self,
        features: Dict[str, Any],
        deal_data: Dict[str, Any]
    ) -> Tuple[RiskLevel, List[str]]:
        """Assess deal risk level and identify risk factors"""

        risk_factors = []
        risk_score = 0.0

        # Value-based risks
        deal_value = features.get("deal_value", 1.0)
        if deal_value > 50:  # $50M+
            risk_score += 0.2
            risk_factors.append("High deal value increases execution complexity")

        # Timeline risks
        deal_age = features.get("deal_age_days", 0)
        if deal_age > 90:
            risk_score += 0.15
            risk_factors.append("Extended timeline may indicate execution challenges")

        # Experience risks
        experience = features.get("organization_experience", 0.1)
        if experience < 0.3:
            risk_score += 0.2
            risk_factors.append("Limited organizational deal experience")

        # Historical performance risks
        historical_success = features.get("historical_success_rate", 0.5)
        if historical_success < 0.4:
            risk_score += 0.15
            risk_factors.append("Below-average historical success rate")

        # Industry risks
        industry_risk = features.get("industry_risk_score", 0.5)
        if industry_risk > 0.6:
            risk_score += 0.1
            risk_factors.append("High-risk industry sector")

        # Market condition risks
        market_volatility = features.get("market_volatility", 0.5)
        if market_volatility > 0.7:
            risk_score += 0.1
            risk_factors.append("High market volatility")

        # Team engagement risks
        team_size = features.get("team_size", 1)
        activity_count = features.get("activity_count", 0)
        if team_size < 2 or activity_count < 5:
            risk_score += 0.1
            risk_factors.append("Low team engagement or activity level")

        # Determine risk level
        if risk_score >= 0.6:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 0.4:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.2:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        return risk_level, risk_factors

    async def _calculate_confidence_score(self, features: Dict[str, Any]) -> float:
        """Calculate confidence in the prediction"""

        # Confidence based on data availability and quality
        confidence_factors = []

        # Historical data availability
        experience = features.get("organization_experience", 0.1)
        confidence_factors.append(min(experience * 2, 1.0))

        # Deal maturity (more mature deals have higher confidence)
        stage_progress = features.get("stage_progress", 0.5)
        confidence_factors.append(stage_progress)

        # Activity level (more activity = better data)
        activity_count = features.get("activity_count", 0)
        activity_confidence = min(activity_count / 20, 1.0)
        confidence_factors.append(activity_confidence)

        # Team engagement
        team_size = features.get("team_size", 1)
        team_confidence = min(team_size / 5, 1.0)
        confidence_factors.append(team_confidence)

        # Data recency (newer data = higher confidence)
        deal_age = features.get("deal_age_days", 0)
        recency_confidence = max(0.3, 1.0 - (deal_age / 365))
        confidence_factors.append(recency_confidence)

        # Average confidence with minimum threshold
        confidence = max(0.4, np.mean(confidence_factors))

        return round(confidence, 3)

    async def _generate_key_insights(
        self,
        features: Dict[str, Any],
        success_probability: float
    ) -> List[str]:
        """Generate key insights about the deal"""

        insights = []

        # Success probability insights
        if success_probability > 0.8:
            insights.append("Strong likelihood of successful completion based on current metrics")
        elif success_probability > 0.6:
            insights.append("Moderate to high probability of success with careful execution")
        elif success_probability > 0.4:
            insights.append("Mixed signals - requires close monitoring and risk mitigation")
        else:
            insights.append("Significant challenges identified - consider strategy revision")

        # Experience insights
        experience = features.get("organization_experience", 0.1)
        if experience < 0.3:
            insights.append("Limited deal experience may benefit from external advisory support")
        elif experience > 0.7:
            insights.append("Strong organizational experience provides competitive advantage")

        # Timeline insights
        deal_age = features.get("deal_age_days", 0)
        if deal_age > 120:
            insights.append("Extended timeline suggests potential execution bottlenecks")

        # Market insights
        seasonal_factor = features.get("seasonal_factor", 1.0)
        if seasonal_factor > 1.1:
            insights.append("Favorable seasonal conditions for deal completion")

        # Value insights
        deal_value = features.get("deal_value", 1.0)
        historical_avg = features.get("historical_avg_value", 1.0)
        if deal_value > historical_avg * 2:
            insights.append("Deal value significantly above historical average - ensure adequate resources")

        return insights

    async def _generate_recommendations(
        self,
        features: Dict[str, Any],
        risk_level: RiskLevel
    ) -> List[str]:
        """Generate actionable recommendations"""

        recommendations = []

        # Risk-based recommendations
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Implement enhanced risk monitoring and mitigation protocols")
            recommendations.append("Consider engaging external advisors for specialized expertise")

        # Experience-based recommendations
        experience = features.get("organization_experience", 0.1)
        if experience < 0.3:
            recommendations.append("Establish mentor relationships with experienced deal teams")
            recommendations.append("Implement structured deal process and documentation standards")

        # Team engagement recommendations
        team_size = features.get("team_size", 1)
        activity_count = features.get("activity_count", 0)
        if team_size < 3:
            recommendations.append("Consider expanding deal team for better coverage and expertise")
        if activity_count < 10:
            recommendations.append("Increase deal activity and stakeholder engagement")

        # Timeline recommendations
        deal_age = features.get("deal_age_days", 0)
        if deal_age > 90:
            recommendations.append("Review timeline and identify acceleration opportunities")
            recommendations.append("Assess for scope creep or requirement changes")

        # Market timing recommendations
        market_volatility = features.get("market_volatility", 0.5)
        if market_volatility > 0.6:
            recommendations.append("Monitor market conditions closely and prepare contingency plans")

        # Value optimization recommendations
        success_prob = await self._calculate_success_probability(features)
        if success_prob > 0.7:
            recommendations.append("Explore value optimization opportunities given strong success indicators")

        return recommendations


class MarketTrendAnalyzer:
    """Analyzer for market trends and predictions"""

    def __init__(self):
        self.analysis_version = "1.0.0"

    async def analyze_market_trends(
        self,
        market_segment: str,
        timeframe: str = "quarterly",
        db: Session = None
    ) -> MarketTrend:
        """Analyze market trends for a specific segment"""

        try:
            # Get historical deal data for the segment
            trend_data = await self._get_trend_data(market_segment, timeframe, db)

            # Analyze trend direction and strength
            direction, strength = await self._analyze_trend_direction(trend_data)

            # Calculate confidence level
            confidence = await self._calculate_trend_confidence(trend_data)

            # Identify key indicators
            indicators = await self._identify_key_indicators(trend_data)

            # Generate predictions
            predictions = await self._generate_trend_predictions(trend_data, direction, strength)

            return MarketTrend(
                trend_id=f"TREND_{market_segment}_{datetime.utcnow().strftime('%Y%m%d')}",
                market_segment=market_segment,
                trend_direction=direction,
                trend_strength=strength,
                confidence_level=confidence,
                timeframe=timeframe,
                key_indicators=indicators,
                predictions=predictions,
                analysis_date=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Market trend analysis failed: {str(e)}")
            raise

    async def _get_trend_data(
        self,
        market_segment: str,
        timeframe: str,
        db: Session
    ) -> Dict[str, Any]:
        """Get historical trend data for analysis"""

        # Simplified trend data - in production, this would use real market data
        # For now, generate synthetic trend data based on patterns

        periods = 12 if timeframe == "monthly" else 4  # quarters
        trend_data = {
            "periods": periods,
            "deal_volumes": [],
            "deal_values": [],
            "success_rates": [],
            "avg_timelines": []
        }

        # Generate synthetic data with realistic patterns
        base_volume = 100
        base_value = 5_000_000

        for i in range(periods):
            # Add seasonal and growth patterns
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * i / periods)
            growth_factor = 1 + 0.05 * i  # 5% growth per period
            noise = 1 + 0.1 * (np.random.random() - 0.5)

            volume = int(base_volume * seasonal_factor * growth_factor * noise)
            value = base_value * seasonal_factor * growth_factor * noise
            success_rate = min(0.9, 0.6 + 0.1 * np.random.random())
            timeline = 45 + 15 * np.random.random()

            trend_data["deal_volumes"].append(volume)
            trend_data["deal_values"].append(value)
            trend_data["success_rates"].append(success_rate)
            trend_data["avg_timelines"].append(timeline)

        return trend_data

    async def _analyze_trend_direction(
        self,
        trend_data: Dict[str, Any]
    ) -> Tuple[str, float]:
        """Analyze trend direction and strength"""

        volumes = np.array(trend_data["deal_volumes"])
        values = np.array(trend_data["deal_values"])

        # Calculate linear regression slopes
        periods = len(volumes)
        x = np.arange(periods)

        volume_slope = np.polyfit(x, volumes, 1)[0]
        value_slope = np.polyfit(x, values, 1)[0]

        # Normalize slopes to percentage change
        volume_trend = volume_slope / np.mean(volumes) * 100
        value_trend = value_slope / np.mean(values) * 100

        # Combine trends (weighted average)
        overall_trend = (volume_trend * 0.6 + value_trend * 0.4)

        # Determine direction
        if abs(overall_trend) < 2:
            direction = "stable"
            strength = 0.3
        elif overall_trend > 0:
            direction = "upward"
            strength = min(1.0, abs(overall_trend) / 10)
        else:
            direction = "downward"
            strength = min(1.0, abs(overall_trend) / 10)

        # Check for volatility
        volume_std = np.std(volumes) / np.mean(volumes)
        if volume_std > 0.3:
            direction = "volatile"
            strength = volume_std

        return direction, round(strength, 3)

    async def _calculate_trend_confidence(self, trend_data: Dict[str, Any]) -> float:
        """Calculate confidence in trend analysis"""

        # Confidence based on data consistency and sample size
        periods = trend_data["periods"]

        # Sample size factor
        size_confidence = min(1.0, periods / 12)

        # Data consistency factor
        volumes = np.array(trend_data["deal_volumes"])
        coefficient_of_variation = np.std(volumes) / np.mean(volumes)
        consistency_confidence = max(0.3, 1.0 - coefficient_of_variation)

        # Combined confidence
        confidence = (size_confidence * 0.4 + consistency_confidence * 0.6)

        return round(confidence, 3)

    async def _identify_key_indicators(
        self,
        trend_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify key market indicators"""

        volumes = trend_data["deal_volumes"]
        values = trend_data["deal_values"]
        success_rates = trend_data["success_rates"]
        timelines = trend_data["avg_timelines"]

        indicators = [
            {
                "indicator": "Deal Volume",
                "current_value": volumes[-1],
                "trend": "increasing" if volumes[-1] > volumes[0] else "decreasing",
                "change_percent": round((volumes[-1] - volumes[0]) / volumes[0] * 100, 1)
            },
            {
                "indicator": "Average Deal Value",
                "current_value": values[-1],
                "trend": "increasing" if values[-1] > values[0] else "decreasing",
                "change_percent": round((values[-1] - values[0]) / values[0] * 100, 1)
            },
            {
                "indicator": "Success Rate",
                "current_value": success_rates[-1],
                "trend": "improving" if success_rates[-1] > np.mean(success_rates[:-1]) else "declining",
                "change_percent": round((success_rates[-1] - np.mean(success_rates[:-1])) * 100, 1)
            },
            {
                "indicator": "Average Timeline",
                "current_value": timelines[-1],
                "trend": "shortening" if timelines[-1] < np.mean(timelines[:-1]) else "lengthening",
                "change_percent": round((timelines[-1] - np.mean(timelines[:-1])) / np.mean(timelines[:-1]) * 100, 1)
            }
        ]

        return indicators

    async def _generate_trend_predictions(
        self,
        trend_data: Dict[str, Any],
        direction: str,
        strength: float
    ) -> List[Dict[str, Any]]:
        """Generate future trend predictions"""

        current_volume = trend_data["deal_volumes"][-1]
        current_value = trend_data["deal_values"][-1]

        predictions = []

        # Next period predictions
        for period in ["next_quarter", "next_6_months", "next_year"]:
            if direction == "upward":
                volume_change = strength * 10
                value_change = strength * 8
            elif direction == "downward":
                volume_change = -strength * 10
                value_change = -strength * 8
            elif direction == "volatile":
                volume_change = 0
                value_change = 0
            else:  # stable
                volume_change = 2
                value_change = 3

            # Adjust for time horizon
            if period == "next_6_months":
                volume_change *= 1.5
                value_change *= 1.5
            elif period == "next_year":
                volume_change *= 2.5
                value_change *= 2.5

            predictions.append({
                "period": period,
                "predicted_volume_change": round(volume_change, 1),
                "predicted_value_change": round(value_change, 1),
                "confidence": max(0.4, 0.8 - (0.1 * len(predictions)))
            })

        return predictions