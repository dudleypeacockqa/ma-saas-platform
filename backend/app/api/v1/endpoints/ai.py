"""AI and Claude MCP API endpoints"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
import structlog

from app.services.claude_mcp import ClaudeMCPService, DealAnalysis, PartnershipRecommendation
from app.api.deps import get_current_user, rate_limit_ai
from app.core.security import verify_api_key


logger = structlog.get_logger(__name__)

router = APIRouter()


class DealAnalysisRequest(BaseModel):
    """Request model for deal analysis"""
    deal_data: Dict[str, Any] = Field(..., description="Deal information including financials, terms, and parties")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context like market conditions")
    include_optimization: bool = Field(False, description="Include deal structure optimization")


class DealAnalysisResponse(BaseModel):
    """Response model for deal analysis"""
    deal_id: str
    confidence_score: float
    strategic_value: float
    risk_assessment: Dict[str, float]
    recommendations: List[str]
    key_insights: List[str]
    red_flags: List[str]
    synergies: List[str]
    valuation_notes: str
    optimization: Optional[Dict[str, Any]] = None


class PartnershipSearchRequest(BaseModel):
    """Request model for partnership identification"""
    organization_profile: Dict[str, Any] = Field(..., description="Organization profile and objectives")
    search_criteria: Optional[Dict[str, Any]] = Field(None, description="Specific criteria for partner search")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of recommendations")


class PartnershipSearchResponse(BaseModel):
    """Response model for partnership recommendations"""
    recommendations: List[Dict[str, Any]]
    total_analyzed: int
    search_criteria: Dict[str, Any]


class StrategicInsightsRequest(BaseModel):
    """Request model for strategic insights generation"""
    ecosystem_data: Dict[str, Any] = Field(..., description="Market and ecosystem intelligence data")
    focus_areas: Optional[List[str]] = Field(None, description="Specific areas to focus analysis")


class IntegrationAssessmentRequest(BaseModel):
    """Request model for integration assessment"""
    acquirer_profile: Dict[str, Any] = Field(..., description="Acquiring company profile")
    target_profile: Dict[str, Any] = Field(..., description="Target company profile")


class BatchAnalysisRequest(BaseModel):
    """Request model for batch deal analysis"""
    deals: List[Dict[str, Any]] = Field(..., description="List of deals to analyze")
    batch_size: int = Field(5, ge=1, le=10, description="Number of concurrent analyses")


@router.post("/analyze-deal", response_model=DealAnalysisResponse)
async def analyze_deal(
    request: DealAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    _=Depends(rate_limit_ai)
):
    """
    Perform comprehensive M&A deal analysis with AI-powered insights.

    This endpoint leverages Claude's advanced capabilities to analyze deal structures,
    identify risks and opportunities, and provide strategic recommendations.
    """
    try:
        claude_service = ClaudeMCPService()

        # Perform deal analysis
        analysis = await claude_service.analyze_deal(
            deal_data=request.deal_data,
            context=request.context
        )

        response = DealAnalysisResponse(
            deal_id=analysis.deal_id,
            confidence_score=analysis.confidence_score,
            strategic_value=analysis.strategic_value,
            risk_assessment=analysis.risk_assessment,
            recommendations=analysis.recommendations,
            key_insights=analysis.key_insights,
            red_flags=analysis.red_flags,
            synergies=analysis.synergies,
            valuation_notes=analysis.valuation_notes
        )

        # Optionally include deal optimization
        if request.include_optimization:
            optimization = await claude_service.optimize_deal_structure(
                deal_parameters=request.deal_data,
                optimization_goals=["tax_efficiency", "risk_mitigation", "value_maximization"]
            )
            response.optimization = optimization

        # Log analysis for audit trail
        background_tasks.add_task(
            log_ai_analysis,
            user_id=current_user.id,
            analysis_type="deal_analysis",
            confidence=analysis.confidence_score
        )

        return response

    except Exception as e:
        logger.error("Deal analysis failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze deal. Please try again."
        )


@router.post("/identify-partnerships", response_model=PartnershipSearchResponse)
async def identify_partnerships(
    request: PartnershipSearchRequest,
    current_user=Depends(get_current_user),
    _=Depends(rate_limit_ai)
):
    """
    Identify and score potential strategic partnerships using AI-powered matching.

    This endpoint analyzes organization profiles and identifies compatible partners
    based on strategic fit, market position, and synergy potential.
    """
    try:
        claude_service = ClaudeMCPService()

        recommendations = await claude_service.identify_partnerships(
            organization_profile=request.organization_profile,
            search_criteria=request.search_criteria
        )

        # Limit results to requested maximum
        limited_recommendations = recommendations[:request.max_results]

        return PartnershipSearchResponse(
            recommendations=[
                {
                    "partner_id": rec.partner_id,
                    "compatibility_score": rec.compatibility_score,
                    "strategic_fit": rec.strategic_fit,
                    "influence_score": rec.influence_score,
                    "synergy_areas": rec.synergy_areas,
                    "potential_value": rec.potential_value,
                    "risk_factors": rec.risk_factors,
                    "recommended_actions": rec.recommended_actions
                }
                for rec in limited_recommendations
            ],
            total_analyzed=len(recommendations),
            search_criteria=request.search_criteria or {}
        )

    except Exception as e:
        logger.error("Partnership identification failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to identify partnerships. Please try again."
        )


@router.post("/generate-insights")
async def generate_strategic_insights(
    request: StrategicInsightsRequest,
    current_user=Depends(get_current_user),
    _=Depends(rate_limit_ai)
):
    """
    Generate strategic insights from ecosystem intelligence data.

    This endpoint analyzes market data, competitive dynamics, and ecosystem trends
    to provide actionable strategic recommendations.
    """
    try:
        claude_service = ClaudeMCPService()

        insights = await claude_service.generate_strategic_insights(
            ecosystem_data=request.ecosystem_data,
            focus_areas=request.focus_areas
        )

        return {
            "insights": insights,
            "generated_for": current_user.id,
            "focus_areas": request.focus_areas
        }

    except Exception as e:
        logger.error("Strategic insights generation failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate insights. Please try again."
        )


@router.post("/assess-integration")
async def assess_integration_readiness(
    request: IntegrationAssessmentRequest,
    current_user=Depends(get_current_user),
    _=Depends(rate_limit_ai)
):
    """
    Assess post-merger integration readiness and identify key challenges.

    This endpoint evaluates cultural fit, system compatibility, and operational
    alignment to provide a comprehensive integration roadmap.
    """
    try:
        claude_service = ClaudeMCPService()

        assessment = await claude_service.assess_integration_readiness(
            acquirer_profile=request.acquirer_profile,
            target_profile=request.target_profile
        )

        return assessment

    except Exception as e:
        logger.error("Integration assessment failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assess integration. Please try again."
        )


@router.post("/batch-analyze")
async def batch_analyze_deals(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    _=Depends(rate_limit_ai)
):
    """
    Analyze multiple deals in batch for portfolio assessment.

    This endpoint efficiently processes multiple deal analyses concurrently,
    ideal for portfolio companies or investment funds.
    """
    try:
        claude_service = ClaudeMCPService()

        analyses = await claude_service.batch_analyze_deals(
            deals=request.deals,
            batch_size=request.batch_size
        )

        # Convert to response format
        results = []
        for analysis in analyses:
            results.append({
                "deal_id": analysis.deal_id,
                "confidence_score": analysis.confidence_score,
                "strategic_value": analysis.strategic_value,
                "risk_assessment": analysis.risk_assessment,
                "key_insights": analysis.key_insights[:3],  # Top 3 insights
                "recommendation": analysis.recommendations[0] if analysis.recommendations else None
            })

        # Log batch analysis
        background_tasks.add_task(
            log_ai_analysis,
            user_id=current_user.id,
            analysis_type="batch_deal_analysis",
            count=len(results)
        )

        return {
            "analyses": results,
            "total_processed": len(results),
            "user_id": current_user.id
        }

    except Exception as e:
        logger.error("Batch analysis failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform batch analysis. Please try again."
        )


@router.get("/usage-stats")
async def get_ai_usage_stats(
    current_user=Depends(get_current_user)
):
    """
    Get AI usage statistics for the current user.

    Returns usage metrics, remaining quota, and historical analysis data.
    """
    # This would connect to a usage tracking service
    return {
        "user_id": current_user.id,
        "daily_analyses": 15,
        "daily_limit": 1000,
        "monthly_analyses": 342,
        "monthly_limit": 10000,
        "last_analysis": "2024-01-20T15:30:00Z",
        "most_used_features": ["deal_analysis", "partnership_identification"]
    }


async def log_ai_analysis(user_id: str, analysis_type: str, **kwargs):
    """Background task to log AI analysis for audit and usage tracking"""
    logger.info(
        "AI analysis logged",
        user_id=user_id,
        analysis_type=analysis_type,
        **kwargs
    )