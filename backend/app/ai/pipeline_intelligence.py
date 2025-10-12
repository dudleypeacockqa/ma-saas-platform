"""
AI-Powered Pipeline Intelligence
Sprint 23: Smart pipeline predictions, velocity analysis, and bottleneck detection
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math
import statistics

from .ai_service import AIService, AIRequest, AIResponse, AITask, AIModel


class PipelineStage(str, Enum):
    """Deal pipeline stages"""
    SOURCING = "sourcing"
    INITIAL_REVIEW = "initial_review"
    VALUATION = "valuation"
    DUE_DILIGENCE = "due_diligence"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class PredictionConfidence(str, Enum):
    """Confidence levels for predictions"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class StageTransitionPrediction:
    """Prediction for deal stage transition"""
    deal_id: str
    current_stage: PipelineStage
    next_stage: PipelineStage
    probability: float  # 0-1
    estimated_days: int
    confidence: PredictionConfidence
    key_factors: List[str]


@dataclass
class PipelineVelocity:
    """Pipeline velocity metrics and predictions"""
    average_days_per_stage: Dict[PipelineStage, float]
    total_pipeline_duration: float
    velocity_trend: str  # "increasing", "decreasing", "stable"
    bottleneck_stages: List[PipelineStage]
    efficiency_score: float  # 0-100


@dataclass
class RevenueForecasting:
    """Revenue forecasting based on pipeline"""
    monthly_forecast: List[Dict[str, Any]]
    quarterly_forecast: List[Dict[str, Any]]
    annual_forecast: Dict[str, Any]
    confidence_intervals: Dict[str, Tuple[float, float]]
    key_assumptions: List[str]


@dataclass
class BottleneckAnalysis:
    """Pipeline bottleneck analysis"""
    bottleneck_stage: PipelineStage
    deals_affected: int
    average_delay_days: float
    impact_on_revenue: float
    suggested_actions: List[str]
    urgency_level: str  # "high", "medium", "low"


@dataclass
class PipelinePredictions:
    """Complete pipeline intelligence predictions"""
    velocity: PipelineVelocity
    stage_transitions: List[StageTransitionPrediction]
    revenue_forecast: RevenueForecasting
    bottlenecks: List[BottleneckAnalysis]
    optimization_opportunities: List[str]
    prediction_timestamp: datetime


class PipelineIntelligenceEngine:
    """AI-powered pipeline intelligence and prediction engine"""

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or AIService()

        # Standard stage durations (days) for baseline
        self.baseline_stage_durations = {
            PipelineStage.SOURCING: 14,
            PipelineStage.INITIAL_REVIEW: 7,
            PipelineStage.VALUATION: 21,
            PipelineStage.DUE_DILIGENCE: 45,
            PipelineStage.NEGOTIATION: 30,
            PipelineStage.CLOSING: 14
        }

        # Stage transition probabilities (baseline)
        self.baseline_transition_probabilities = {
            PipelineStage.SOURCING: 0.70,
            PipelineStage.INITIAL_REVIEW: 0.65,
            PipelineStage.VALUATION: 0.60,
            PipelineStage.DUE_DILIGENCE: 0.55,
            PipelineStage.NEGOTIATION: 0.75,
            PipelineStage.CLOSING: 0.85
        }

    async def analyze_pipeline(self, deals_data: List[Dict[str, Any]],
                              historical_data: Optional[List[Dict[str, Any]]] = None) -> PipelinePredictions:
        """
        Perform comprehensive pipeline intelligence analysis

        Args:
            deals_data: Current active deals in pipeline
            historical_data: Historical deal completion data

        Returns:
            PipelinePredictions: Complete pipeline intelligence analysis
        """

        # Analyze pipeline velocity
        velocity = await self._analyze_pipeline_velocity(deals_data, historical_data)

        # Predict stage transitions for active deals
        stage_transitions = await self._predict_stage_transitions(deals_data, velocity)

        # Generate revenue forecasting
        revenue_forecast = await self._forecast_revenue(deals_data, stage_transitions, historical_data)

        # Identify and analyze bottlenecks
        bottlenecks = await self._analyze_bottlenecks(deals_data, velocity, historical_data)

        # Generate optimization opportunities
        optimization_opportunities = await self._identify_optimization_opportunities(
            velocity, bottlenecks, historical_data
        )

        return PipelinePredictions(
            velocity=velocity,
            stage_transitions=stage_transitions,
            revenue_forecast=revenue_forecast,
            bottlenecks=bottlenecks,
            optimization_opportunities=optimization_opportunities,
            prediction_timestamp=datetime.now()
        )

    async def _analyze_pipeline_velocity(self, deals_data: List[Dict[str, Any]],
                                       historical_data: Optional[List[Dict[str, Any]]]) -> PipelineVelocity:
        """Analyze pipeline velocity using AI and historical data"""

        # Prepare data for AI analysis
        velocity_data = {
            "current_deals": len(deals_data),
            "deals_by_stage": self._group_deals_by_stage(deals_data),
            "historical_completions": historical_data or [],
            "baseline_durations": self.baseline_stage_durations
        }

        request = AIRequest(
            task=AITask.PREDICT_OUTCOME,
            model=AIModel.WORKFLOW_PREDICTOR,
            input_data=velocity_data
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            return self._calculate_basic_velocity(deals_data, historical_data)

        ai_result = response.result

        # Extract AI predictions
        avg_days_per_stage = ai_result.get("average_days_per_stage", {})

        # Convert string keys back to enums
        stage_durations = {}
        for stage_str, duration in avg_days_per_stage.items():
            try:
                stage = PipelineStage(stage_str)
                stage_durations[stage] = duration
            except ValueError:
                continue

        # Fill missing stages with baseline
        for stage in PipelineStage:
            if stage not in stage_durations:
                stage_durations[stage] = self.baseline_stage_durations.get(stage, 30)

        total_duration = sum(stage_durations.values())
        velocity_trend = ai_result.get("velocity_trend", "stable")
        efficiency_score = ai_result.get("efficiency_score", 70)

        # Identify bottleneck stages
        bottleneck_threshold = statistics.mean(stage_durations.values()) * 1.5
        bottleneck_stages = [
            stage for stage, duration in stage_durations.items()
            if duration > bottleneck_threshold
        ]

        return PipelineVelocity(
            average_days_per_stage=stage_durations,
            total_pipeline_duration=total_duration,
            velocity_trend=velocity_trend,
            bottleneck_stages=bottleneck_stages,
            efficiency_score=efficiency_score
        )

    def _calculate_basic_velocity(self, deals_data: List[Dict[str, Any]],
                                 historical_data: Optional[List[Dict[str, Any]]]) -> PipelineVelocity:
        """Calculate basic velocity without AI"""

        # Use historical data if available
        if historical_data:
            stage_durations = self._calculate_historical_durations(historical_data)
        else:
            stage_durations = self.baseline_stage_durations.copy()

        # Analyze current deals for trends
        current_stages = [deal.get("stage") for deal in deals_data if deal.get("stage")]
        stage_counts = {}
        for stage in current_stages:
            stage_counts[stage] = stage_counts.get(stage, 0) + 1

        # Simple bottleneck detection based on deal concentration
        total_deals = len(deals_data)
        bottleneck_stages = []
        if total_deals > 0:
            for stage_str, count in stage_counts.items():
                if count / total_deals > 0.4:  # More than 40% of deals in one stage
                    try:
                        bottleneck_stages.append(PipelineStage(stage_str))
                    except ValueError:
                        continue

        total_duration = sum(stage_durations.values())
        efficiency_score = max(50, min(100, 150 - (total_duration / 7)))  # Score based on weeks

        return PipelineVelocity(
            average_days_per_stage=stage_durations,
            total_pipeline_duration=total_duration,
            velocity_trend="stable",
            bottleneck_stages=bottleneck_stages,
            efficiency_score=efficiency_score
        )

    def _calculate_historical_durations(self, historical_data: List[Dict[str, Any]]) -> Dict[PipelineStage, float]:
        """Calculate average stage durations from historical data"""

        stage_durations = {}
        stage_data = {}

        for deal in historical_data:
            stages = deal.get("stage_history", [])

            for i, stage_entry in enumerate(stages[:-1]):
                stage = stage_entry.get("stage")
                if not stage:
                    continue

                try:
                    stage_enum = PipelineStage(stage)
                except ValueError:
                    continue

                start_date = datetime.fromisoformat(stage_entry.get("timestamp", ""))
                end_date = datetime.fromisoformat(stages[i + 1].get("timestamp", ""))

                duration = (end_date - start_date).days

                if stage_enum not in stage_data:
                    stage_data[stage_enum] = []
                stage_data[stage_enum].append(duration)

        # Calculate averages
        for stage in PipelineStage:
            if stage in stage_data and stage_data[stage]:
                stage_durations[stage] = statistics.mean(stage_data[stage])
            else:
                stage_durations[stage] = self.baseline_stage_durations.get(stage, 30)

        return stage_durations

    def _group_deals_by_stage(self, deals_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group deals by current stage"""
        stage_counts = {}
        for deal in deals_data:
            stage = deal.get("stage", "unknown")
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        return stage_counts

    async def _predict_stage_transitions(self, deals_data: List[Dict[str, Any]],
                                       velocity: PipelineVelocity) -> List[StageTransitionPrediction]:
        """Predict stage transitions for active deals"""

        predictions = []

        for deal in deals_data:
            current_stage_str = deal.get("stage")
            if not current_stage_str:
                continue

            try:
                current_stage = PipelineStage(current_stage_str)
            except ValueError:
                continue

            # Skip if already closed
            if current_stage in [PipelineStage.CLOSED_WON, PipelineStage.CLOSED_LOST]:
                continue

            prediction = await self._predict_deal_transition(deal, current_stage, velocity)
            if prediction:
                predictions.append(prediction)

        return predictions

    async def _predict_deal_transition(self, deal: Dict[str, Any],
                                     current_stage: PipelineStage,
                                     velocity: PipelineVelocity) -> Optional[StageTransitionPrediction]:
        """Predict next stage transition for a specific deal"""

        # Determine next stage
        stage_order = list(PipelineStage)
        try:
            current_index = stage_order.index(current_stage)
            if current_index >= len(stage_order) - 3:  # Near end stages
                next_stage = PipelineStage.CLOSED_WON  # Default optimistic
            else:
                next_stage = stage_order[current_index + 1]
        except (ValueError, IndexError):
            return None

        # Use AI to predict transition probability
        request = AIRequest(
            task=AITask.PREDICT_OUTCOME,
            model=AIModel.DEAL_SCORER,
            input_data={
                "deal": deal,
                "current_stage": current_stage.value,
                "next_stage": next_stage.value,
                "velocity_metrics": velocity.__dict__,
                "historical_probability": self.baseline_transition_probabilities.get(current_stage, 0.6)
            }
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            # Fallback to baseline probability
            probability = self.baseline_transition_probabilities.get(current_stage, 0.6)
            estimated_days = int(velocity.average_days_per_stage.get(current_stage, 30))
            key_factors = ["Standard transition probability"]
            confidence = PredictionConfidence.LOW
        else:
            ai_result = response.result
            probability = ai_result.get("transition_probability", 0.6)
            estimated_days = ai_result.get("estimated_days", 30)
            key_factors = ai_result.get("key_factors", [])

            # Determine confidence based on AI confidence
            ai_confidence = response.confidence
            if ai_confidence > 0.8:
                confidence = PredictionConfidence.HIGH
            elif ai_confidence > 0.6:
                confidence = PredictionConfidence.MEDIUM
            else:
                confidence = PredictionConfidence.LOW

        return StageTransitionPrediction(
            deal_id=deal.get("id", "unknown"),
            current_stage=current_stage,
            next_stage=next_stage,
            probability=probability,
            estimated_days=estimated_days,
            confidence=confidence,
            key_factors=key_factors
        )

    async def _forecast_revenue(self, deals_data: List[Dict[str, Any]],
                              stage_transitions: List[StageTransitionPrediction],
                              historical_data: Optional[List[Dict[str, Any]]]) -> RevenueForecasting:
        """Generate AI-powered revenue forecasting"""

        # Prepare forecasting data
        forecast_data = {
            "active_deals": deals_data,
            "transition_predictions": [t.__dict__ for t in stage_transitions],
            "historical_closures": historical_data or [],
            "current_pipeline_value": sum(deal.get("valuation", 0) for deal in deals_data)
        }

        request = AIRequest(
            task=AITask.PREDICT_OUTCOME,
            model=AIModel.FINANCIAL_FORECASTER,
            input_data=forecast_data
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            return self._generate_basic_forecast(deals_data, stage_transitions)

        ai_result = response.result

        return RevenueForecasting(
            monthly_forecast=ai_result.get("monthly_forecast", []),
            quarterly_forecast=ai_result.get("quarterly_forecast", []),
            annual_forecast=ai_result.get("annual_forecast", {}),
            confidence_intervals=ai_result.get("confidence_intervals", {}),
            key_assumptions=ai_result.get("key_assumptions", [])
        )

    def _generate_basic_forecast(self, deals_data: List[Dict[str, Any]],
                               stage_transitions: List[StageTransitionPrediction]) -> RevenueForecasting:
        """Generate basic revenue forecast without AI"""

        # Calculate expected revenue by month
        monthly_forecast = []
        quarterly_forecast = []

        # Simple probability-weighted revenue calculation
        total_pipeline_value = sum(deal.get("valuation", 0) for deal in deals_data)

        # Estimate closure probability by stage
        stage_close_probabilities = {
            PipelineStage.SOURCING: 0.15,
            PipelineStage.INITIAL_REVIEW: 0.25,
            PipelineStage.VALUATION: 0.35,
            PipelineStage.DUE_DILIGENCE: 0.50,
            PipelineStage.NEGOTIATION: 0.70,
            PipelineStage.CLOSING: 0.85
        }

        expected_revenue = 0
        for deal in deals_data:
            deal_value = deal.get("valuation", 0)
            stage_str = deal.get("stage", "")
            try:
                stage = PipelineStage(stage_str)
                probability = stage_close_probabilities.get(stage, 0.3)
                expected_revenue += deal_value * probability
            except ValueError:
                expected_revenue += deal_value * 0.3  # Default probability

        # Distribute over 12 months
        for month in range(12):
            monthly_forecast.append({
                "month": month + 1,
                "expected_revenue": expected_revenue / 12,
                "best_case": expected_revenue / 12 * 1.3,
                "worst_case": expected_revenue / 12 * 0.7
            })

        # Quarterly aggregation
        for quarter in range(4):
            start_month = quarter * 3
            quarterly_revenue = sum(
                monthly_forecast[i]["expected_revenue"]
                for i in range(start_month, min(start_month + 3, 12))
            )
            quarterly_forecast.append({
                "quarter": quarter + 1,
                "expected_revenue": quarterly_revenue,
                "deals_expected": len(deals_data) // 4
            })

        return RevenueForecasting(
            monthly_forecast=monthly_forecast,
            quarterly_forecast=quarterly_forecast,
            annual_forecast={
                "expected_revenue": expected_revenue,
                "pipeline_value": total_pipeline_value,
                "conversion_rate": 0.3
            },
            confidence_intervals={
                "annual": (expected_revenue * 0.7, expected_revenue * 1.3)
            },
            key_assumptions=[
                "Historical conversion rates apply",
                "No major market disruptions",
                "Current deal velocity maintained"
            ]
        )

    async def _analyze_bottlenecks(self, deals_data: List[Dict[str, Any]],
                                 velocity: PipelineVelocity,
                                 historical_data: Optional[List[Dict[str, Any]]]) -> List[BottleneckAnalysis]:
        """Analyze pipeline bottlenecks using AI"""

        bottlenecks = []

        for stage in velocity.bottleneck_stages:
            bottleneck = await self._analyze_stage_bottleneck(stage, deals_data, velocity, historical_data)
            if bottleneck:
                bottlenecks.append(bottleneck)

        return bottlenecks

    async def _analyze_stage_bottleneck(self, stage: PipelineStage,
                                      deals_data: List[Dict[str, Any]],
                                      velocity: PipelineVelocity,
                                      historical_data: Optional[List[Dict[str, Any]]]) -> Optional[BottleneckAnalysis]:
        """Analyze a specific stage bottleneck"""

        # Count deals in this stage
        deals_in_stage = [
            deal for deal in deals_data
            if deal.get("stage") == stage.value
        ]

        if not deals_in_stage:
            return None

        # Calculate impact
        stage_duration = velocity.average_days_per_stage.get(stage, 30)
        baseline_duration = self.baseline_stage_durations.get(stage, 30)
        delay_days = max(0, stage_duration - baseline_duration)

        # Estimate revenue impact
        total_value_affected = sum(deal.get("valuation", 0) for deal in deals_in_stage)

        # Use AI to analyze bottleneck causes and solutions
        request = AIRequest(
            task=AITask.DETECT_ANOMALIES,
            model=AIModel.WORKFLOW_PREDICTOR,
            input_data={
                "stage": stage.value,
                "deals_count": len(deals_in_stage),
                "average_duration": stage_duration,
                "baseline_duration": baseline_duration,
                "deals_data": deals_in_stage,
                "historical_data": historical_data or []
            }
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            suggested_actions = self._get_default_bottleneck_actions(stage)
        else:
            suggested_actions = response.result.get("suggested_actions", [])

        # Determine urgency
        if delay_days > 14 and len(deals_in_stage) > 5:
            urgency = "high"
        elif delay_days > 7 or len(deals_in_stage) > 3:
            urgency = "medium"
        else:
            urgency = "low"

        return BottleneckAnalysis(
            bottleneck_stage=stage,
            deals_affected=len(deals_in_stage),
            average_delay_days=delay_days,
            impact_on_revenue=total_value_affected,
            suggested_actions=suggested_actions,
            urgency_level=urgency
        )

    def _get_default_bottleneck_actions(self, stage: PipelineStage) -> List[str]:
        """Get default actions for bottleneck resolution"""

        default_actions = {
            PipelineStage.SOURCING: [
                "Increase sourcing team capacity",
                "Automate deal screening process",
                "Expand sourcing channels"
            ],
            PipelineStage.INITIAL_REVIEW: [
                "Streamline initial review checklist",
                "Add more senior reviewers",
                "Implement automated screening tools"
            ],
            PipelineStage.VALUATION: [
                "Bring in additional valuation experts",
                "Standardize valuation methodology",
                "Use valuation automation tools"
            ],
            PipelineStage.DUE_DILIGENCE: [
                "Expand due diligence team",
                "Parallelize due diligence workstreams",
                "Use third-party DD providers"
            ],
            PipelineStage.NEGOTIATION: [
                "Involve experienced negotiators earlier",
                "Pre-agree on key terms",
                "Use structured negotiation framework"
            ],
            PipelineStage.CLOSING: [
                "Streamline legal documentation",
                "Parallel process regulatory approvals",
                "Early stakeholder alignment"
            ]
        }

        return default_actions.get(stage, ["Review stage process", "Add resources", "Remove blockers"])

    async def _identify_optimization_opportunities(self, velocity: PipelineVelocity,
                                                 bottlenecks: List[BottleneckAnalysis],
                                                 historical_data: Optional[List[Dict[str, Any]]]) -> List[str]:
        """Identify pipeline optimization opportunities using AI"""

        optimization_data = {
            "velocity_metrics": velocity.__dict__,
            "bottlenecks": [b.__dict__ for b in bottlenecks],
            "efficiency_score": velocity.efficiency_score,
            "historical_performance": historical_data or []
        }

        request = AIRequest(
            task=AITask.RECOMMEND_ACTIONS,
            model=AIModel.RECOMMENDATION_ENGINE,
            input_data=optimization_data
        )

        response = await self.ai_service.process_request(request)

        if response.error:
            return self._get_default_optimization_opportunities(velocity, bottlenecks)

        return response.result.get("optimization_opportunities", [])

    def _get_default_optimization_opportunities(self, velocity: PipelineVelocity,
                                              bottlenecks: List[BottleneckAnalysis]) -> List[str]:
        """Get default optimization opportunities"""

        opportunities = []

        # Efficiency-based opportunities
        if velocity.efficiency_score < 70:
            opportunities.append("Implement pipeline automation tools")
            opportunities.append("Standardize stage transition criteria")

        # Bottleneck-based opportunities
        if len(bottlenecks) > 2:
            opportunities.append("Conduct comprehensive process review")
            opportunities.append("Rebalance team resources across stages")

        # Velocity-based opportunities
        if velocity.velocity_trend == "decreasing":
            opportunities.append("Investigate process degradation causes")
            opportunities.append("Refresh team training and tools")

        # Stage-specific opportunities
        total_duration = velocity.total_pipeline_duration
        if total_duration > 150:  # More than ~5 months
            opportunities.append("Parallel process development")
            opportunities.append("Early stakeholder engagement")

        return opportunities[:5]  # Limit to top 5


# Global pipeline intelligence engine instance
_pipeline_intelligence_engine: Optional[PipelineIntelligenceEngine] = None


def get_pipeline_intelligence_engine() -> PipelineIntelligenceEngine:
    """Get global pipeline intelligence engine instance"""
    global _pipeline_intelligence_engine
    if _pipeline_intelligence_engine is None:
        _pipeline_intelligence_engine = PipelineIntelligenceEngine()
    return _pipeline_intelligence_engine


# Utility function for quick pipeline analysis
async def analyze_pipeline_intelligence(deals_data: List[Dict[str, Any]],
                                      historical_data: Optional[List[Dict[str, Any]]] = None) -> PipelinePredictions:
    """Quick utility function for pipeline intelligence analysis"""
    engine = get_pipeline_intelligence_engine()
    return await engine.analyze_pipeline(deals_data, historical_data)