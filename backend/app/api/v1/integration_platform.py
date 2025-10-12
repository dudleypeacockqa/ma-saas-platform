"""
API endpoints for Advanced Post-Merger Integration & Value Creation Platform - Sprint 17
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.deps import get_current_user
from app.models.user import User
from app.integration_platform import (
    get_integration_engine,
    get_synergy_manager,
    get_cultural_integration_manager,
    get_performance_optimizer
)

router = APIRouter()

# Request/Response Models

class IntegrationConfigRequest(BaseModel):
    deal_id: str = Field(..., description="Deal ID for the integration")
    integration_name: str = Field(..., description="Name of the integration")
    integration_type: str = Field(..., description="Type of integration (merger, acquisition, joint_venture)")
    acquiring_organization_id: str = Field(..., description="ID of acquiring organization")
    target_organization_id: str = Field(..., description="ID of target organization")
    timeline_weeks: int = Field(52, description="Planned integration timeline in weeks")
    priority: str = Field("medium", description="Integration priority level")
    key_objectives: List[str] = Field(default_factory=list, description="Key integration objectives")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Integration constraints")

class SynergyManagementRequest(BaseModel):
    integration_id: str = Field(..., description="Integration ID")
    deal_data: Dict[str, Any] = Field(..., description="Deal financial and operational data")
    synergy_targets: Dict[str, float] = Field(default_factory=dict, description="Target synergy values")
    tracking_frequency: str = Field("monthly", description="Synergy tracking frequency")

class CulturalIntegrationRequest(BaseModel):
    integration_id: str = Field(..., description="Integration ID")
    acquiring_organization_id: str = Field(..., description="Acquiring organization ID")
    target_organization_id: str = Field(..., description="Target organization ID")
    acquiring_org_data: Dict[str, Any] = Field(..., description="Acquiring org cultural data")
    target_org_data: Dict[str, Any] = Field(..., description="Target org cultural data")
    sentiment_data_sources: Dict[str, Any] = Field(default_factory=dict, description="Employee sentiment data")

class PerformanceOptimizationRequest(BaseModel):
    integration_id: str = Field(..., description="Integration ID")
    metrics_data: Dict[str, Any] = Field(..., description="Performance metrics data")
    integration_context: Dict[str, Any] = Field(..., description="Integration context for benchmarking")
    optimization_goals: List[str] = Field(default_factory=list, description="Optimization objectives")

class IntegrationStatusResponse(BaseModel):
    integration_id: str
    status: str
    overall_progress: float
    key_metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    last_updated: datetime

# Integration Engine Endpoints

@router.post("/integration/initiate", tags=["Integration Engine"])
async def initiate_integration(
    request: IntegrationConfigRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Initiate a new post-merger integration process"""

    try:
        integration_engine = get_integration_engine()

        integration_config = {
            "integration_name": request.integration_name,
            "integration_type": request.integration_type,
            "acquiring_organization_id": request.acquiring_organization_id,
            "target_organization_id": request.target_organization_id,
            "timeline_weeks": request.timeline_weeks,
            "priority": request.priority,
            "key_objectives": request.key_objectives,
            "constraints": request.constraints,
            "initiated_by": current_user.id
        }

        result = await integration_engine.initiate_integration(
            request.deal_id, integration_config
        )

        return {
            "success": True,
            "integration_id": result.get("integration_id"),
            "status": result.get("status"),
            "integration_plan": result.get("integration_plan"),
            "milestone_roadmap": result.get("milestone_roadmap"),
            "message": "Integration process initiated successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate integration: {str(e)}"
        )

@router.get("/integration/{integration_id}/status", tags=["Integration Engine"])
async def get_integration_status(
    integration_id: str,
    current_user: User = Depends(get_current_user)
) -> IntegrationStatusResponse:
    """Get current status of an integration"""

    try:
        integration_engine = get_integration_engine()

        status_data = await integration_engine.get_integration_status(integration_id)

        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )

        return IntegrationStatusResponse(**status_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration status: {str(e)}"
        )

@router.put("/integration/{integration_id}/milestone/{milestone_id}/complete", tags=["Integration Engine"])
async def complete_milestone(
    integration_id: str,
    milestone_id: str,
    completion_data: Dict[str, Any] = {},
    current_user: User = Depends(get_current_user)
):
    """Mark a milestone as completed"""

    try:
        integration_engine = get_integration_engine()

        result = await integration_engine.complete_milestone(
            integration_id, milestone_id, completion_data
        )

        return {
            "success": True,
            "milestone_id": milestone_id,
            "completion_status": result.get("status"),
            "next_milestones": result.get("next_milestones"),
            "integration_progress": result.get("integration_progress")
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete milestone: {str(e)}"
        )

# Synergy Management Endpoints

@router.post("/synergy/initiate", tags=["Synergy Management"])
async def initiate_synergy_management(
    request: SynergyManagementRequest,
    current_user: User = Depends(get_current_user)
):
    """Initiate synergy identification and tracking"""

    try:
        synergy_manager = get_synergy_manager()

        result = await synergy_manager.initiate_synergy_management(
            request.integration_id, request.deal_data
        )

        return {
            "success": True,
            "synergy_analysis": result.get("synergy_analysis"),
            "tracking_setup": result.get("tracking_setup"),
            "roi_projections": result.get("roi_projections"),
            "message": "Synergy management initiated successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate synergy management: {str(e)}"
        )

@router.get("/synergy/{integration_id}/analysis", tags=["Synergy Management"])
async def get_synergy_analysis(
    integration_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive synergy analysis and tracking data"""

    try:
        synergy_manager = get_synergy_manager()

        analysis = await synergy_manager.get_synergy_analysis(integration_id)

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Synergy analysis not found for integration"
            )

        return {
            "success": True,
            "synergy_analysis": analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get synergy analysis: {str(e)}"
        )

@router.post("/synergy/{integration_id}/track", tags=["Synergy Management"])
async def track_synergy_realization(
    integration_id: str,
    tracking_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Track synergy realization progress"""

    try:
        synergy_manager = get_synergy_manager()

        result = await synergy_manager.track_synergy_realization(
            integration_id, tracking_data
        )

        return {
            "success": True,
            "tracking_results": result,
            "message": "Synergy tracking updated successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track synergy realization: {str(e)}"
        )

# Cultural Integration Endpoints

@router.post("/cultural/initiate", tags=["Cultural Integration"])
async def initiate_cultural_integration(
    request: CulturalIntegrationRequest,
    current_user: User = Depends(get_current_user)
):
    """Initiate cultural integration analysis and planning"""

    try:
        cultural_manager = get_cultural_integration_manager()

        cultural_data = {
            "acquiring_organization_id": request.acquiring_organization_id,
            "target_organization_id": request.target_organization_id,
            "acquiring_org_data": request.acquiring_org_data,
            "target_org_data": request.target_org_data,
            "sentiment_data_sources": request.sentiment_data_sources
        }

        result = await cultural_manager.initiate_cultural_integration(
            request.integration_id, cultural_data
        )

        return {
            "success": True,
            "cultural_assessment": result.get("cultural_assessment"),
            "sentiment_baseline": result.get("sentiment_baseline"),
            "change_program_overview": result.get("change_program_overview"),
            "next_steps": result.get("next_steps"),
            "message": "Cultural integration initiated successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate cultural integration: {str(e)}"
        )

@router.get("/cultural/{integration_id}/assessment", tags=["Cultural Integration"])
async def get_cultural_assessment(
    integration_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get cultural compatibility assessment"""

    try:
        cultural_manager = get_cultural_integration_manager()

        assessment = await cultural_manager.get_cultural_assessment(integration_id)

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cultural assessment not found for integration"
            )

        return {
            "success": True,
            "cultural_assessment": assessment
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cultural assessment: {str(e)}"
        )

@router.get("/cultural/{integration_id}/sentiment", tags=["Cultural Integration"])
async def get_sentiment_analysis(
    integration_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get employee sentiment analysis"""

    try:
        cultural_manager = get_cultural_integration_manager()

        sentiment = await cultural_manager.get_sentiment_analysis(integration_id)

        if not sentiment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sentiment analysis not found for integration"
            )

        return {
            "success": True,
            "sentiment_analysis": sentiment
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sentiment analysis: {str(e)}"
        )

# Performance Optimization Endpoints

@router.post("/performance/initiate", tags=["Performance Optimization"])
async def initiate_performance_optimization(
    request: PerformanceOptimizationRequest,
    current_user: User = Depends(get_current_user)
):
    """Initiate performance optimization analysis"""

    try:
        performance_optimizer = get_performance_optimizer()

        optimization_data = {
            "metrics_data": request.metrics_data,
            "integration_context": request.integration_context,
            "optimization_goals": request.optimization_goals
        }

        result = await performance_optimizer.initiate_performance_optimization(
            request.integration_id, optimization_data
        )

        return {
            "success": True,
            "performance_summary": result.get("performance_summary"),
            "benchmark_performance": result.get("benchmark_performance"),
            "optimization_overview": result.get("optimization_overview"),
            "next_steps": result.get("next_steps"),
            "message": "Performance optimization initiated successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate performance optimization: {str(e)}"
        )

@router.get("/performance/{integration_id}/dashboard", tags=["Performance Optimization"])
async def get_performance_dashboard(
    integration_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get performance analytics dashboard"""

    try:
        performance_optimizer = get_performance_optimizer()

        dashboard = await performance_optimizer.get_performance_dashboard(integration_id)

        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Performance dashboard not found for integration"
            )

        return {
            "success": True,
            "dashboard": dashboard
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance dashboard: {str(e)}"
        )

@router.get("/performance/{integration_id}/benchmarks", tags=["Performance Optimization"])
async def get_performance_benchmarks(
    integration_id: str,
    industry: Optional[str] = None,
    deal_size: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get performance benchmarks for integration"""

    try:
        performance_optimizer = get_performance_optimizer()

        integration_context = {}
        if industry:
            integration_context["industry"] = industry
        if deal_size:
            integration_context["deal_size_category"] = deal_size

        benchmarks = await performance_optimizer.get_benchmarks(
            integration_id, integration_context
        )

        return {
            "success": True,
            "benchmarks": benchmarks
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance benchmarks: {str(e)}"
        )

# Comprehensive Integration Analytics

@router.get("/analytics/{integration_id}/comprehensive", tags=["Integration Analytics"])
async def get_comprehensive_analytics(
    integration_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive integration analytics across all dimensions"""

    try:
        # Get data from all integration components
        integration_engine = get_integration_engine()
        synergy_manager = get_synergy_manager()
        cultural_manager = get_cultural_integration_manager()
        performance_optimizer = get_performance_optimizer()

        # Gather comprehensive analytics
        integration_status = await integration_engine.get_integration_status(integration_id)
        synergy_analysis = await synergy_manager.get_synergy_analysis(integration_id)
        cultural_assessment = await cultural_manager.get_cultural_assessment(integration_id)
        performance_dashboard = await performance_optimizer.get_performance_dashboard(integration_id)

        return {
            "success": True,
            "integration_id": integration_id,
            "comprehensive_analytics": {
                "integration_status": integration_status,
                "synergy_analysis": synergy_analysis,
                "cultural_assessment": cultural_assessment,
                "performance_dashboard": performance_dashboard,
                "generated_at": datetime.utcnow()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get comprehensive analytics: {str(e)}"
        )

@router.get("/analytics/{integration_id}/health-score", tags=["Integration Analytics"])
async def get_integration_health_score(
    integration_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get overall integration health score"""

    try:
        # Calculate composite health score from all components
        integration_engine = get_integration_engine()

        health_score = await integration_engine.calculate_integration_health_score(integration_id)

        return {
            "success": True,
            "integration_id": integration_id,
            "health_score": health_score,
            "calculated_at": datetime.utcnow()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate integration health score: {str(e)}"
        )