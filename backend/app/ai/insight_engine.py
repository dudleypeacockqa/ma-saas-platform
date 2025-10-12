"""
Automated Insight Generation System
AI-powered insights for deals, markets, and performance optimization
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

from .prediction_models import DealOutcomePredictionModel, MarketTrendAnalyzer

logger = logging.getLogger(__name__)


class InsightType(str, Enum):
    """Types of insights generated"""
    DEAL_RISK = "deal_risk"
    OPPORTUNITY = "opportunity"
    PERFORMANCE = "performance"
    MARKET_TREND = "market_trend"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"
    OPTIMIZATION = "optimization"


class InsightPriority(str, Enum):
    """Priority levels for insights"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class AIInsight:
    """AI-generated insight"""
    insight_id: str
    insight_type: InsightType
    priority: InsightPriority
    title: str
    description: str
    context: Dict[str, Any]
    recommendations: List[str]
    impact_score: float  # 0.0 to 1.0
    confidence_score: float  # 0.0 to 1.0
    generated_at: datetime
    expires_at: Optional[datetime]
    related_entities: List[str]  # deal_ids, user_ids, etc.
    data_sources: List[str]
    tags: List[str]


class AutomatedInsightEngine:
    """Engine for generating automated AI insights"""

    def __init__(self):
        self.prediction_model = DealOutcomePredictionModel()
        self.trend_analyzer = MarketTrendAnalyzer()
        self.insight_cache = {}

    async def generate_organization_insights(
        self,
        organization_id: str,
        db: Session,
        include_types: Optional[List[InsightType]] = None
    ) -> List[AIInsight]:
        """Generate comprehensive insights for an organization"""

        insights = []

        try:
            # Get organization data
            org_data = await self._get_organization_data(organization_id, db)

            # Generate different types of insights
            if not include_types or InsightType.DEAL_RISK in include_types:
                deal_insights = await self._generate_deal_risk_insights(org_data, db)
                insights.extend(deal_insights)

            if not include_types or InsightType.OPPORTUNITY in include_types:
                opportunity_insights = await self._generate_opportunity_insights(org_data, db)
                insights.extend(opportunity_insights)

            if not include_types or InsightType.PERFORMANCE in include_types:
                performance_insights = await self._generate_performance_insights(org_data, db)
                insights.extend(performance_insights)

            if not include_types or InsightType.MARKET_TREND in include_types:
                market_insights = await self._generate_market_insights(org_data, db)
                insights.extend(market_insights)

            if not include_types or InsightType.OPTIMIZATION in include_types:
                optimization_insights = await self._generate_optimization_insights(org_data, db)
                insights.extend(optimization_insights)

            # Sort by priority and impact
            insights.sort(key=lambda x: (
                self._priority_weight(x.priority),
                -x.impact_score,
                -x.confidence_score
            ))

            return insights

        except Exception as e:
            logger.error(f"Failed to generate organization insights: {str(e)}")
            return []

    async def _get_organization_data(self, organization_id: str, db: Session) -> Dict[str, Any]:
        """Get comprehensive organization data for analysis"""

        try:
            # Get basic organization info
            org_query = text("""
                SELECT id, name, industry, created_at, subscription_tier
                FROM organizations
                WHERE id = :org_id
            """)
            org_result = db.execute(org_query, {"org_id": organization_id}).fetchone()

            if not org_result:
                raise ValueError(f"Organization {organization_id} not found")

            # Get deal statistics
            deals_query = text("""
                SELECT
                    COUNT(*) as total_deals,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_deals,
                    COUNT(CASE WHEN status IN ('prospecting', 'qualification', 'proposal', 'negotiation', 'due_diligence', 'closing') THEN 1 END) as active_deals,
                    AVG(estimated_value) as avg_deal_value,
                    SUM(estimated_value) as total_pipeline_value,
                    AVG(EXTRACT(DAY FROM (COALESCE(updated_at, NOW()) - created_at))) as avg_deal_age
                FROM deals
                WHERE organization_id = :org_id
                AND created_at >= :lookback_date
            """)

            lookback_date = datetime.utcnow() - timedelta(days=365)
            deals_result = db.execute(deals_query, {
                "org_id": organization_id,
                "lookback_date": lookback_date
            }).fetchone()

            # Get team statistics
            team_query = text("""
                SELECT COUNT(DISTINCT user_id) as team_size
                FROM deal_team_members dtm
                JOIN deals d ON dtm.deal_id = d.id
                WHERE d.organization_id = :org_id
                AND dtm.created_at >= :lookback_date
            """)
            team_result = db.execute(team_query, {
                "org_id": organization_id,
                "lookback_date": lookback_date
            }).fetchone()

            # Get activity statistics
            activity_query = text("""
                SELECT
                    COUNT(*) as total_activities,
                    COUNT(DISTINCT deal_id) as deals_with_activity
                FROM deal_activities da
                JOIN deals d ON da.deal_id = d.id
                WHERE d.organization_id = :org_id
                AND da.created_at >= :lookback_date
            """)
            activity_result = db.execute(activity_query, {
                "org_id": organization_id,
                "lookback_date": lookback_date
            }).fetchone()

            return {
                "organization": {
                    "id": org_result[0],
                    "name": org_result[1],
                    "industry": org_result[2],
                    "created_at": org_result[3],
                    "subscription_tier": org_result[4]
                },
                "deals": {
                    "total": int(deals_result[0] or 0),
                    "completed": int(deals_result[1] or 0),
                    "active": int(deals_result[2] or 0),
                    "avg_value": float(deals_result[3] or 0),
                    "total_pipeline_value": float(deals_result[4] or 0),
                    "avg_age_days": float(deals_result[5] or 0)
                },
                "team": {
                    "size": int(team_result[0] or 0) if team_result else 0
                },
                "activity": {
                    "total": int(activity_result[0] or 0) if activity_result else 0,
                    "deals_with_activity": int(activity_result[1] or 0) if activity_result else 0
                }
            }

        except Exception as e:
            logger.error(f"Failed to get organization data: {str(e)}")
            raise

    async def _generate_deal_risk_insights(
        self,
        org_data: Dict[str, Any],
        db: Session
    ) -> List[AIInsight]:
        """Generate deal risk insights"""

        insights = []

        try:
            # Get active deals for risk analysis
            active_deals_query = text("""
                SELECT id, title, status, estimated_value, created_at, industry
                FROM deals
                WHERE organization_id = :org_id
                AND status IN ('prospecting', 'qualification', 'proposal', 'negotiation', 'due_diligence', 'closing')
                ORDER BY estimated_value DESC
                LIMIT 10
            """)

            active_deals = db.execute(active_deals_query, {
                "org_id": org_data["organization"]["id"]
            }).fetchall()

            for deal in active_deals:
                deal_data = {
                    "id": deal[0],
                    "title": deal[1],
                    "status": deal[2],
                    "estimated_value": deal[3],
                    "created_at": deal[4].isoformat() if deal[4] else datetime.utcnow().isoformat(),
                    "industry": deal[5],
                    "organization_id": org_data["organization"]["id"]
                }

                # Get prediction for this deal
                prediction = await self.prediction_model.predict_deal_outcome(deal_data, db)

                # Generate risk insights based on prediction
                if prediction.risk_level.value in ["high", "critical"]:
                    priority = InsightPriority.CRITICAL if prediction.risk_level.value == "critical" else InsightPriority.HIGH

                    insights.append(AIInsight(
                        insight_id=f"RISK_{deal_data['id']}_{datetime.utcnow().strftime('%Y%m%d')}",
                        insight_type=InsightType.DEAL_RISK,
                        priority=priority,
                        title=f"High Risk Detected: {deal_data['title']}",
                        description=f"Deal shows {prediction.risk_level.value} risk level with {prediction.success_probability:.1%} success probability. Key risk factors: {', '.join(prediction.risk_factors[:2])}",
                        context={
                            "deal_id": deal_data['id'],
                            "risk_level": prediction.risk_level.value,
                            "success_probability": prediction.success_probability,
                            "risk_factors": prediction.risk_factors,
                            "predicted_completion": prediction.expected_completion_date.isoformat()
                        },
                        recommendations=prediction.recommendations[:3],
                        impact_score=1.0 - prediction.success_probability,
                        confidence_score=prediction.confidence_score,
                        generated_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=7),
                        related_entities=[deal_data['id']],
                        data_sources=["deal_prediction_model"],
                        tags=["risk", "deal", prediction.risk_level.value]
                    ))

                # Timeline risk insights
                days_old = (datetime.utcnow() - datetime.fromisoformat(deal_data["created_at"])).days
                if days_old > 90:
                    insights.append(AIInsight(
                        insight_id=f"TIMELINE_{deal_data['id']}_{datetime.utcnow().strftime('%Y%m%d')}",
                        insight_type=InsightType.ALERT,
                        priority=InsightPriority.MEDIUM,
                        title=f"Extended Timeline: {deal_data['title']}",
                        description=f"Deal has been active for {days_old} days, which exceeds typical timelines. Consider reviewing progress and identifying bottlenecks.",
                        context={
                            "deal_id": deal_data['id'],
                            "days_active": days_old,
                            "status": deal_data['status']
                        },
                        recommendations=[
                            "Review deal progress with team",
                            "Identify potential bottlenecks",
                            "Consider timeline acceleration strategies"
                        ],
                        impact_score=0.6,
                        confidence_score=0.9,
                        generated_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=14),
                        related_entities=[deal_data['id']],
                        data_sources=["deal_timeline_analysis"],
                        tags=["timeline", "delay", "review"]
                    ))

            return insights

        except Exception as e:
            logger.error(f"Failed to generate deal risk insights: {str(e)}")
            return []

    async def _generate_opportunity_insights(
        self,
        org_data: Dict[str, Any],
        db: Session
    ) -> List[AIInsight]:
        """Generate opportunity insights"""

        insights = []

        try:
            deals_data = org_data["deals"]

            # Pipeline value opportunity
            if deals_data["total_pipeline_value"] > 0:
                avg_success_rate = deals_data["completed"] / max(deals_data["total"], 1)
                expected_value = deals_data["total_pipeline_value"] * avg_success_rate

                if expected_value > deals_data["avg_value"] * 5:  # Significant opportunity
                    insights.append(AIInsight(
                        insight_id=f"OPPORTUNITY_PIPELINE_{datetime.utcnow().strftime('%Y%m%d')}",
                        insight_type=InsightType.OPPORTUNITY,
                        priority=InsightPriority.HIGH,
                        title="Significant Pipeline Value Opportunity",
                        description=f"Current pipeline represents ${expected_value/1_000_000:.1f}M in expected value based on historical success rates. Focus on pipeline acceleration could yield substantial returns.",
                        context={
                            "total_pipeline_value": deals_data["total_pipeline_value"],
                            "expected_value": expected_value,
                            "success_rate": avg_success_rate,
                            "active_deals": deals_data["active"]
                        },
                        recommendations=[
                            "Prioritize high-value deals for acceleration",
                            "Implement pipeline velocity optimization",
                            "Consider resource allocation to maximize conversion"
                        ],
                        impact_score=0.8,
                        confidence_score=0.7,
                        generated_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=30),
                        related_entities=[org_data["organization"]["id"]],
                        data_sources=["pipeline_analysis"],
                        tags=["opportunity", "pipeline", "value"]
                    ))

            # Team utilization opportunity
            team_size = org_data["team"]["size"]
            active_deals = deals_data["active"]

            if team_size > 0:
                deals_per_person = active_deals / team_size
                if deals_per_person < 2:  # Underutilized team
                    insights.append(AIInsight(
                        insight_id=f"OPPORTUNITY_UTILIZATION_{datetime.utcnow().strftime('%Y%m%d')}",
                        insight_type=InsightType.OPPORTUNITY,
                        priority=InsightPriority.MEDIUM,
                        title="Team Capacity Available for Growth",
                        description=f"Current team utilization shows capacity for additional deals. With {team_size} team members handling {active_deals} active deals, there's opportunity for expansion.",
                        context={
                            "team_size": team_size,
                            "active_deals": active_deals,
                            "deals_per_person": deals_per_person
                        },
                        recommendations=[
                            "Explore new deal sourcing opportunities",
                            "Consider marketing initiatives to increase leads",
                            "Evaluate team capacity for strategic expansion"
                        ],
                        impact_score=0.6,
                        confidence_score=0.8,
                        generated_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=30),
                        related_entities=[org_data["organization"]["id"]],
                        data_sources=["team_utilization_analysis"],
                        tags=["opportunity", "capacity", "growth"]
                    ))

            return insights

        except Exception as e:
            logger.error(f"Failed to generate opportunity insights: {str(e)}")
            return []

    async def _generate_performance_insights(
        self,
        org_data: Dict[str, Any],
        db: Session
    ) -> List[AIInsight]:
        """Generate performance insights"""

        insights = []

        try:
            deals_data = org_data["deals"]

            # Success rate analysis
            if deals_data["total"] > 5:  # Enough data for meaningful analysis
                success_rate = deals_data["completed"] / deals_data["total"]

                if success_rate < 0.4:  # Below average performance
                    insights.append(AIInsight(
                        insight_id=f"PERFORMANCE_SUCCESS_{datetime.utcnow().strftime('%Y%m%d')}",
                        insight_type=InsightType.PERFORMANCE,
                        priority=InsightPriority.HIGH,
                        title="Below Average Success Rate Detected",
                        description=f"Current success rate of {success_rate:.1%} is below industry benchmarks. Focus on process improvement and deal qualification could enhance performance.",
                        context={
                            "success_rate": success_rate,
                            "total_deals": deals_data["total"],
                            "completed_deals": deals_data["completed"],
                            "benchmark": 0.65  # Industry benchmark
                        },
                        recommendations=[
                            "Review deal qualification criteria",
                            "Implement enhanced due diligence processes",
                            "Analyze failed deals for common patterns",
                            "Consider training on negotiation and closing techniques"
                        ],
                        impact_score=0.7,
                        confidence_score=0.8,
                        generated_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=30),
                        related_entities=[org_data["organization"]["id"]],
                        data_sources=["success_rate_analysis"],
                        tags=["performance", "success_rate", "improvement"]
                    ))

                elif success_rate > 0.8:  # Excellent performance
                    insights.append(AIInsight(
                        insight_id=f"PERFORMANCE_EXCELLENT_{datetime.utcnow().strftime('%Y%m%d')}",
                        insight_type=InsightType.PERFORMANCE,
                        priority=InsightPriority.MEDIUM,
                        title="Excellent Success Rate Achievement",
                        description=f"Outstanding success rate of {success_rate:.1%} significantly exceeds industry benchmarks. Consider scaling successful practices.",
                        context={
                            "success_rate": success_rate,
                            "total_deals": deals_data["total"],
                            "completed_deals": deals_data["completed"]
                        },
                        recommendations=[
                            "Document and standardize successful practices",
                            "Consider mentoring other teams",
                            "Explore opportunities for increased deal volume",
                            "Share best practices across organization"
                        ],
                        impact_score=0.5,
                        confidence_score=0.9,
                        generated_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=30),
                        related_entities=[org_data["organization"]["id"]],
                        data_sources=["success_rate_analysis"],
                        tags=["performance", "excellence", "best_practices"]
                    ))

            # Activity engagement analysis
            activity_data = org_data["activity"]
            if deals_data["active"] > 0:
                activity_ratio = activity_data["deals_with_activity"] / deals_data["active"]

                if activity_ratio < 0.7:  # Low engagement
                    insights.append(AIInsight(
                        insight_id=f"PERFORMANCE_ENGAGEMENT_{datetime.utcnow().strftime('%Y%m%d')}",
                        insight_type=InsightType.PERFORMANCE,
                        priority=InsightPriority.MEDIUM,
                        title="Low Deal Engagement Detected",
                        description=f"Only {activity_ratio:.1%} of active deals show recent activity. Increased engagement could improve deal velocity and success rates.",
                        context={
                            "activity_ratio": activity_ratio,
                            "active_deals": deals_data["active"],
                            "deals_with_activity": activity_data["deals_with_activity"],
                            "total_activities": activity_data["total"]
                        },
                        recommendations=[
                            "Implement regular deal review processes",
                            "Set minimum activity requirements for active deals",
                            "Provide training on stakeholder engagement",
                            "Consider workflow automation to prompt activities"
                        ],
                        impact_score=0.6,
                        confidence_score=0.7,
                        generated_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=21),
                        related_entities=[org_data["organization"]["id"]],
                        data_sources=["activity_engagement_analysis"],
                        tags=["performance", "engagement", "activity"]
                    ))

            return insights

        except Exception as e:
            logger.error(f"Failed to generate performance insights: {str(e)}")
            return []

    async def _generate_market_insights(
        self,
        org_data: Dict[str, Any],
        db: Session
    ) -> List[AIInsight]:
        """Generate market trend insights"""

        insights = []

        try:
            industry = org_data["organization"]["industry"]

            if industry:
                # Analyze market trends for the organization's industry
                market_trend = await self.trend_analyzer.analyze_market_trends(industry, "quarterly", db)

                if market_trend.trend_direction in ["upward", "volatile"]:
                    priority = InsightPriority.HIGH if market_trend.trend_direction == "upward" else InsightPriority.MEDIUM

                    insights.append(AIInsight(
                        insight_id=f"MARKET_{industry}_{datetime.utcnow().strftime('%Y%m%d')}",
                        insight_type=InsightType.MARKET_TREND,
                        priority=priority,
                        title=f"{industry.title()} Market Trend: {market_trend.trend_direction.title()}",
                        description=f"Market analysis shows {market_trend.trend_direction} trend with {market_trend.trend_strength:.1%} strength. Consider adjusting strategy to capitalize on market conditions.",
                        context={
                            "industry": industry,
                            "trend_direction": market_trend.trend_direction,
                            "trend_strength": market_trend.trend_strength,
                            "confidence": market_trend.confidence_level,
                            "key_indicators": market_trend.key_indicators[:3]
                        },
                        recommendations=[
                            f"Adjust deal strategy for {market_trend.trend_direction} market",
                            "Monitor market indicators closely",
                            "Consider timing optimization for deal execution"
                        ],
                        impact_score=0.5 + (market_trend.trend_strength * 0.3),
                        confidence_score=market_trend.confidence_level,
                        generated_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=60),
                        related_entities=[org_data["organization"]["id"]],
                        data_sources=["market_trend_analysis"],
                        tags=["market", "trend", industry, market_trend.trend_direction]
                    ))

                # Predictions insights
                for prediction in market_trend.predictions[:2]:  # Top 2 predictions
                    if abs(prediction["predicted_volume_change"]) > 10:  # Significant change predicted
                        insights.append(AIInsight(
                            insight_id=f"PREDICTION_{industry}_{prediction['period']}_{datetime.utcnow().strftime('%Y%m%d')}",
                            insight_type=InsightType.MARKET_TREND,
                            priority=InsightPriority.MEDIUM,
                            title=f"Market Prediction: {prediction['period'].replace('_', ' ').title()}",
                            description=f"Predicted {prediction['predicted_volume_change']:+.1f}% change in deal volume for {prediction['period']} with {prediction['confidence']:.1%} confidence.",
                            context={
                                "period": prediction["period"],
                                "volume_change": prediction["predicted_volume_change"],
                                "value_change": prediction["predicted_value_change"],
                                "prediction_confidence": prediction["confidence"]
                            },
                            recommendations=[
                                "Adjust pipeline planning based on predictions",
                                "Consider resource allocation optimization",
                                "Monitor actual vs predicted performance"
                            ],
                            impact_score=abs(prediction["predicted_volume_change"]) / 100,
                            confidence_score=prediction["confidence"],
                            generated_at=datetime.utcnow(),
                            expires_at=datetime.utcnow() + timedelta(days=90),
                            related_entities=[org_data["organization"]["id"]],
                            data_sources=["market_prediction_analysis"],
                            tags=["prediction", "market", prediction["period"]]
                        ))

            return insights

        except Exception as e:
            logger.error(f"Failed to generate market insights: {str(e)}")
            return []

    async def _generate_optimization_insights(
        self,
        org_data: Dict[str, Any],
        db: Session
    ) -> List[AIInsight]:
        """Generate optimization insights"""

        insights = []

        try:
            deals_data = org_data["deals"]

            # Deal value optimization
            if deals_data["total"] > 3 and deals_data["avg_value"] > 0:
                # Check for value consistency
                value_query = text("""
                    SELECT estimated_value
                    FROM deals
                    WHERE organization_id = :org_id
                    AND estimated_value > 0
                    ORDER BY created_at DESC
                    LIMIT 10
                """)

                recent_values = db.execute(value_query, {
                    "org_id": org_data["organization"]["id"]
                }).fetchall()

                if recent_values and len(recent_values) > 3:
                    values = [float(row[0]) for row in recent_values]
                    import numpy as np
                    coefficient_of_variation = np.std(values) / np.mean(values)

                    if coefficient_of_variation > 1.0:  # High variance in deal values
                        insights.append(AIInsight(
                            insight_id=f"OPTIMIZATION_VALUE_{datetime.utcnow().strftime('%Y%m%d')}",
                            insight_type=InsightType.OPTIMIZATION,
                            priority=InsightPriority.MEDIUM,
                            title="Deal Value Optimization Opportunity",
                            description=f"High variance in deal values detected (CV: {coefficient_of_variation:.2f}). Standardizing value assessment could improve predictability and planning.",
                            context={
                                "coefficient_of_variation": coefficient_of_variation,
                                "avg_value": deals_data["avg_value"],
                                "recent_values": values[:5]
                            },
                            recommendations=[
                                "Develop standardized valuation methodology",
                                "Implement value assessment training",
                                "Create deal value benchmarking process",
                                "Consider value-based deal qualification"
                            ],
                            impact_score=0.6,
                            confidence_score=0.7,
                            generated_at=datetime.utcnow(),
                            expires_at=datetime.utcnow() + timedelta(days=45),
                            related_entities=[org_data["organization"]["id"]],
                            data_sources=["value_variance_analysis"],
                            tags=["optimization", "value", "standardization"]
                        ))

            # Timeline optimization
            if deals_data["avg_age_days"] > 60:  # Deals taking longer than expected
                insights.append(AIInsight(
                    insight_id=f"OPTIMIZATION_TIMELINE_{datetime.utcnow().strftime('%Y%m%d')}",
                    insight_type=InsightType.OPTIMIZATION,
                    priority=InsightPriority.HIGH,
                    title="Deal Timeline Optimization Needed",
                    description=f"Average deal age of {deals_data['avg_age_days']:.0f} days exceeds optimal timelines. Process optimization could accelerate deal velocity.",
                    context={
                        "avg_age_days": deals_data["avg_age_days"],
                        "active_deals": deals_data["active"],
                        "benchmark": 45  # Industry benchmark
                    },
                    recommendations=[
                        "Analyze bottlenecks in deal process",
                        "Implement milestone-based tracking",
                        "Consider workflow automation",
                        "Set timeline targets for each deal stage"
                    ],
                    impact_score=0.7,
                    confidence_score=0.8,
                    generated_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(days=30),
                    related_entities=[org_data["organization"]["id"]],
                    data_sources=["timeline_analysis"],
                    tags=["optimization", "timeline", "velocity"]
                ))

            return insights

        except Exception as e:
            logger.error(f"Failed to generate optimization insights: {str(e)}")
            return []

    def _priority_weight(self, priority: InsightPriority) -> int:
        """Convert priority to weight for sorting"""
        weights = {
            InsightPriority.CRITICAL: 5,
            InsightPriority.HIGH: 4,
            InsightPriority.MEDIUM: 3,
            InsightPriority.LOW: 2,
            InsightPriority.INFO: 1
        }
        return weights.get(priority, 3)

    async def get_insight_by_id(self, insight_id: str) -> Optional[AIInsight]:
        """Retrieve a specific insight by ID"""
        return self.insight_cache.get(insight_id)

    async def cache_insights(self, insights: List[AIInsight]) -> None:
        """Cache generated insights"""
        for insight in insights:
            self.insight_cache[insight.insight_id] = insight

    async def cleanup_expired_insights(self) -> None:
        """Remove expired insights from cache"""
        current_time = datetime.utcnow()
        expired_ids = [
            insight_id for insight_id, insight in self.insight_cache.items()
            if insight.expires_at and insight.expires_at < current_time
        ]

        for insight_id in expired_ids:
            del self.insight_cache[insight_id]