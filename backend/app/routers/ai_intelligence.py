"""
AI Intelligence API Endpoints
Sprint 23: AI-powered deal intelligence and pipeline predictions
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from ..auth.clerk_auth import get_current_user, ClerkUser as User
from ..ai.deal_intelligence import (
    DealIntelligenceEngine,
    get_deal_intelligence_engine,
    DealIntelligence,
    analyze_deal_intelligence
)
from ..ai.pipeline_intelligence import (
    PipelineIntelligenceEngine,
    get_pipeline_intelligence_engine,
    PipelinePredictions,
    analyze_pipeline_intelligence
)
from ..ai.ai_service import get_ai_service, AIRequest, AITask, AIModel


router = APIRouter(prefix="/api/ai", tags=["AI Intelligence"])


# Request/Response Models
class DealAnalysisRequest(BaseModel):
    """Request model for deal analysis"""
    deal_id: str
    deal_data: Dict[str, Any]
    include_market_analysis: bool = True
    include_competitive_analysis: bool = True


class DealAnalysisResponse(BaseModel):
    """Response model for deal analysis"""
    deal_id: str
    overall_score: float
    financial_score: float
    strategic_score: float
    risk_score: float
    market_score: float
    team_score: float
    recommendation: str
    risk_level: str
    market_insights: Dict[str, Any]
    next_actions: List[str]
    confidence: float
    analysis_timestamp: datetime


class PipelineAnalysisRequest(BaseModel):
    """Request model for pipeline analysis"""
    include_historical_data: bool = True
    date_range_days: int = 90
    include_forecasting: bool = True


class PipelineAnalysisResponse(BaseModel):
    """Response model for pipeline analysis"""
    velocity_metrics: Dict[str, Any]
    bottlenecks: List[Dict[str, Any]]
    revenue_forecast: Dict[str, Any]
    optimization_opportunities: List[str]
    prediction_timestamp: datetime


class AIInsightRequest(BaseModel):
    """Request model for AI insights"""
    context: str
    data: Dict[str, Any]
    insight_type: str = "general"


class AIInsightResponse(BaseModel):
    """Response model for AI insights"""
    insights: List[Dict[str, Any]]
    recommendations: List[str]
    confidence: float
    processing_time_ms: int


@router.post("/deals/{deal_id}/analyze", response_model=DealAnalysisResponse)
async def analyze_deal(
    deal_id: str,
    request: DealAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform comprehensive AI-powered deal analysis

    Returns:
        - Deal scoring across multiple dimensions
        - Risk assessment with mitigation strategies
        - Market insights and competitive analysis
        - AI-powered recommendations and next actions
    """
    try:
        # Get deal intelligence engine
        engine = get_deal_intelligence_engine()

        # Add user context to deal data
        enhanced_deal_data = request.deal_data.copy()
        enhanced_deal_data.update({
            "analyzed_by": current_user.user_id,
            "organization_id": current_user.organization_id,
            "analysis_timestamp": datetime.now().isoformat()
        })

        # Perform AI analysis
        intelligence = await engine.analyze_deal(enhanced_deal_data)

        return DealAnalysisResponse(
            deal_id=intelligence.deal_id,
            overall_score=intelligence.score.overall_score,
            financial_score=intelligence.score.financial_score,
            strategic_score=intelligence.score.strategic_score,
            risk_score=intelligence.score.risk_score,
            market_score=intelligence.score.market_score,
            team_score=intelligence.score.team_score,
            recommendation=intelligence.recommendation.value,
            risk_level=intelligence.risk_assessment.overall_risk.value,
            market_insights=intelligence.market_insights,
            next_actions=intelligence.next_best_actions,
            confidence=intelligence.confidence_level,
            analysis_timestamp=intelligence.analysis_timestamp
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deal analysis failed: {str(e)}")


@router.get("/deals/{deal_id}/score")
async def get_deal_score(
    deal_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get quick AI-powered deal score

    Returns basic scoring without full analysis for dashboard display
    """
    try:
        # This would typically fetch deal data from database
        # For now, return mock data structure
        ai_service = get_ai_service()

        # Mock deal data request
        request = AIRequest(
            task=AITask.SCORE_DEAL,
            model=AIModel.DEAL_SCORER,
            input_data={"deal_id": deal_id},
            user_id=current_user.user_id,
            organization_id=current_user.organization_id
        )

        response = await ai_service.process_request(request)

        if response.error:
            raise HTTPException(status_code=500, detail=response.error)

        return {
            "deal_id": deal_id,
            "score": response.result.get("overall_score", 75),
            "confidence": response.confidence,
            "last_updated": response.timestamp.isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deal scoring failed: {str(e)}")


@router.post("/pipeline/analyze", response_model=PipelineAnalysisResponse)
async def analyze_pipeline(
    request: PipelineAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform comprehensive AI-powered pipeline analysis

    Returns:
        - Pipeline velocity metrics and trends
        - Bottleneck identification and analysis
        - Revenue forecasting based on current pipeline
        - Optimization recommendations
    """
    try:
        # Get pipeline intelligence engine
        engine = get_pipeline_intelligence_engine()

        # This would typically fetch deals data from database
        # For demo purposes, we'll use mock data
        deals_data = await _get_user_deals_data(current_user.user_id, request.date_range_days)
        historical_data = await _get_historical_deals_data(current_user.user_id) if request.include_historical_data else None

        # Perform pipeline analysis
        predictions = await engine.analyze_pipeline(deals_data, historical_data)

        return PipelineAnalysisResponse(
            velocity_metrics={
                "average_days_per_stage": {k.value: v for k, v in predictions.velocity.average_days_per_stage.items()},
                "total_pipeline_duration": predictions.velocity.total_pipeline_duration,
                "velocity_trend": predictions.velocity.velocity_trend,
                "efficiency_score": predictions.velocity.efficiency_score,
                "bottleneck_stages": [stage.value for stage in predictions.velocity.bottleneck_stages]
            },
            bottlenecks=[
                {
                    "stage": bottleneck.bottleneck_stage.value,
                    "deals_affected": bottleneck.deals_affected,
                    "average_delay_days": bottleneck.average_delay_days,
                    "impact_on_revenue": bottleneck.impact_on_revenue,
                    "suggested_actions": bottleneck.suggested_actions,
                    "urgency_level": bottleneck.urgency_level
                }
                for bottleneck in predictions.bottlenecks
            ],
            revenue_forecast={
                "monthly_forecast": predictions.revenue_forecast.monthly_forecast,
                "quarterly_forecast": predictions.revenue_forecast.quarterly_forecast,
                "annual_forecast": predictions.revenue_forecast.annual_forecast,
                "confidence_intervals": predictions.revenue_forecast.confidence_intervals,
                "key_assumptions": predictions.revenue_forecast.key_assumptions
            } if request.include_forecasting else {},
            optimization_opportunities=predictions.optimization_opportunities,
            prediction_timestamp=predictions.prediction_timestamp
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline analysis failed: {str(e)}")


@router.get("/pipeline/velocity")
async def get_pipeline_velocity(
    current_user: User = Depends(get_current_user),
    days_back: int = Query(30, description="Number of days to analyze")
):
    """
    Get pipeline velocity metrics for dashboard

    Returns real-time pipeline velocity and efficiency metrics
    """
    try:
        engine = get_pipeline_intelligence_engine()
        deals_data = await _get_user_deals_data(current_user.user_id, days_back)

        velocity = await engine._analyze_pipeline_velocity(deals_data, None)

        return {
            "average_cycle_time": velocity.total_pipeline_duration,
            "velocity_trend": velocity.velocity_trend,
            "efficiency_score": velocity.efficiency_score,
            "bottleneck_count": len(velocity.bottleneck_stages),
            "stage_performance": {k.value: v for k, v in velocity.average_days_per_stage.items()}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Velocity analysis failed: {str(e)}")


@router.post("/insights/generate", response_model=AIInsightResponse)
async def generate_insights(
    request: AIInsightRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI-powered insights from data

    Accepts arbitrary data and generates intelligent insights and recommendations
    """
    try:
        ai_service = get_ai_service()

        # Create AI request
        ai_request = AIRequest(
            task=AITask.GENERATE_INSIGHTS,
            model=AIModel.MARKET_INTELLIGENCE,
            input_data=request.data,
            context={"analysis_context": request.context, "insight_type": request.insight_type},
            user_id=current_user.user_id,
            organization_id=current_user.organization_id
        )

        response = await ai_service.process_request(ai_request)

        if response.error:
            raise HTTPException(status_code=500, detail=response.error)

        return AIInsightResponse(
            insights=response.result.get("insights", []),
            recommendations=response.result.get("recommendations", []),
            confidence=response.confidence,
            processing_time_ms=response.processing_time_ms
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")


@router.get("/models/status")
async def get_ai_models_status(current_user: User = Depends(get_current_user)):
    """
    Get status of AI models and processing statistics

    Returns information about available AI models and their performance
    """
    try:
        ai_service = get_ai_service()

        return {
            "available_models": ai_service.get_available_models(),
            "processing_stats": ai_service.get_processing_stats(),
            "health_check": ai_service.health_check(),
            "capabilities": {
                model.value: ai_service.get_model_capabilities(model)
                for model in AIModel
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI status check failed: {str(e)}")


@router.post("/documents/analyze")
async def analyze_document(
    document_content: str,
    document_type: str = "unknown",
    current_user: User = Depends(get_current_user)
):
    """
    Analyze document using AI

    Extracts key information, generates summaries, and provides insights
    """
    try:
        ai_service = get_ai_service()

        request = AIRequest(
            task=AITask.ANALYZE_DOCUMENT,
            model=AIModel.DOCUMENT_ANALYZER,
            input_data={
                "content": document_content,
                "document_type": document_type
            },
            user_id=current_user.user_id,
            organization_id=current_user.organization_id
        )

        response = await ai_service.process_request(request)

        if response.error:
            raise HTTPException(status_code=500, detail=response.error)

        return {
            "analysis": response.result,
            "confidence": response.confidence,
            "processing_time_ms": response.processing_time_ms,
            "extracted_data": response.result.get("extracted_fields", {}),
            "summary": response.result.get("summary", ""),
            "key_metrics": response.result.get("key_metrics", {}),
            "risk_factors": response.result.get("risk_factors", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")


@router.get("/recommendations/{deal_id}")
async def get_deal_recommendations(
    deal_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered recommendations for a specific deal

    Returns personalized recommendations based on deal analysis
    """
    try:
        ai_service = get_ai_service()

        # This would fetch actual deal data from database
        request = AIRequest(
            task=AITask.RECOMMEND_ACTIONS,
            model=AIModel.RECOMMENDATION_ENGINE,
            input_data={"deal_id": deal_id},
            user_id=current_user.user_id,
            organization_id=current_user.organization_id
        )

        response = await ai_service.process_request(request)

        if response.error:
            raise HTTPException(status_code=500, detail=response.error)

        return {
            "deal_id": deal_id,
            "recommendations": response.result.get("recommended_actions", []),
            "priority_actions": response.result.get("priority_actions", []),
            "risk_mitigations": response.result.get("risk_mitigations", []),
            "optimization_suggestions": response.result.get("optimization_suggestions", []),
            "confidence": response.confidence,
            "last_updated": response.timestamp.isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")


# Helper functions (would typically interact with actual database)
async def _get_user_deals_data(user_id: str, days_back: int) -> List[Dict[str, Any]]:
    """Get user's deals data for analysis (mock implementation)"""
    # This would query the actual deals database
    return [
        {
            "id": "deal_1",
            "stage": "due_diligence",
            "valuation": 5000000,
            "industry": "technology",
            "created_at": "2024-10-01T00:00:00Z",
            "updated_at": "2024-10-10T00:00:00Z"
        },
        {
            "id": "deal_2",
            "stage": "valuation",
            "valuation": 3000000,
            "industry": "healthcare",
            "created_at": "2024-09-15T00:00:00Z",
            "updated_at": "2024-10-08T00:00:00Z"
        },
        {
            "id": "deal_3",
            "stage": "negotiation",
            "valuation": 8000000,
            "industry": "fintech",
            "created_at": "2024-08-20T00:00:00Z",
            "updated_at": "2024-10-05T00:00:00Z"
        }
    ]


async def _get_historical_deals_data(user_id: str) -> List[Dict[str, Any]]:
    """Get historical deals data for trend analysis (mock implementation)"""
    # This would query completed deals from database
    return [
        {
            "id": "completed_1",
            "final_stage": "closed_won",
            "total_duration_days": 120,
            "stage_history": [
                {"stage": "sourcing", "timestamp": "2024-06-01T00:00:00Z"},
                {"stage": "initial_review", "timestamp": "2024-06-08T00:00:00Z"},
                {"stage": "valuation", "timestamp": "2024-06-22T00:00:00Z"},
                {"stage": "due_diligence", "timestamp": "2024-07-15T00:00:00Z"},
                {"stage": "negotiation", "timestamp": "2024-08-20T00:00:00Z"},
                {"stage": "closing", "timestamp": "2024-09-15T00:00:00Z"},
                {"stage": "closed_won", "timestamp": "2024-09-30T00:00:00Z"}
            ]
        }
    ]