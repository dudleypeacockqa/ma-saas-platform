"""
Advanced Platform API
High-level endpoints exposing AI intelligence, document automation, collaboration,
integration, and analytics capabilities for the M&A platform.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.auth.clerk_auth import ClerkUser, get_current_user
from app.core.database import get_db
from app.services.advanced_platform_service import AdvancedPlatformService
from app.schemas.advanced_platform import (
    AdvancedAnalyticsOverviewResponse,
    AdvancedDealIntelligenceRequest,
    AdvancedDealIntelligenceResponse,
    AdvancedDocumentProcessingRequest,
    AdvancedDocumentProcessingResponse,
    CollaborationCommentRequest,
    CollaborationCommentResponse,
    CollaborationResolveRequest,
    CollaborationSessionRequest,
    CollaborationSessionResponse,
    IntegrationStatusResponse,
    TaskAutomationRequest,
    TaskAutomationResponse,
    VideoMeetingRequest,
    VideoMeetingResponse,
)

router = APIRouter(prefix="/advanced", tags=["Advanced Platform"])


def get_service(db: Session = Depends(get_db)) -> AdvancedPlatformService:
    return AdvancedPlatformService(db)


@router.post(
    "/deal-intelligence",
    response_model=AdvancedDealIntelligenceResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_deal_intelligence(
    payload: AdvancedDealIntelligenceRequest,
    current_user: ClerkUser = Depends(get_current_user),
    service: AdvancedPlatformService = Depends(get_service),
) -> AdvancedDealIntelligenceResponse:
    """Run AI-powered deal intelligence for the requested deal."""

    try:
        result = await service.generate_deal_intelligence(payload.dict())
        return AdvancedDealIntelligenceResponse(**result)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate deal intelligence: {exc}",
        ) from exc


@router.post(
    "/documents/process",
    response_model=AdvancedDocumentProcessingResponse,
    status_code=status.HTTP_200_OK,
)
async def process_document(
    payload: AdvancedDocumentProcessingRequest,
    current_user: ClerkUser = Depends(get_current_user),
    service: AdvancedPlatformService = Depends(get_service),
) -> AdvancedDocumentProcessingResponse:
    """Process a document with OCR, extraction, versioning, and data room controls."""

    try:
        result = await service.process_document(payload.dict())
        return AdvancedDocumentProcessingResponse(**result)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {exc}",
        ) from exc


@router.post(
    "/collaboration/sessions",
    response_model=CollaborationSessionResponse,
    status_code=status.HTTP_200_OK,
)
async def start_collaboration_session(
    payload: CollaborationSessionRequest,
    current_user: ClerkUser = Depends(get_current_user),
    service: AdvancedPlatformService = Depends(get_service),
) -> CollaborationSessionResponse:
    """Create a real-time collaboration session for document editing."""

    result = await service.start_collaboration_session(payload.dict())
    return CollaborationSessionResponse(**result)


@router.post(
    "/collaboration/comments",
    response_model=CollaborationCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    payload: CollaborationCommentRequest,
    current_user: ClerkUser = Depends(get_current_user),
    service: AdvancedPlatformService = Depends(get_service),
) -> CollaborationCommentResponse:
    """Add a threaded collaboration comment."""

    comment = await service.add_comment(payload.dict())
    return CollaborationCommentResponse(**comment)


@router.post(
    "/collaboration/comments/{comment_id}/resolve",
    response_model=CollaborationCommentResponse,
    status_code=status.HTTP_200_OK,
)
async def resolve_comment(
    payload: CollaborationResolveRequest,
    comment_id: str = Path(..., description="Comment identifier to resolve"),
    current_user: ClerkUser = Depends(get_current_user),
    service: AdvancedPlatformService = Depends(get_service),
) -> CollaborationCommentResponse:
    """Resolve an existing collaboration comment."""

    resolution_payload = payload.dict()
    resolution_payload["comment_id"] = comment_id
    result = await service.resolve_comment(resolution_payload)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return CollaborationCommentResponse(**result)


@router.post(
    "/collaboration/tasks",
    response_model=TaskAutomationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_task_workflow(
    payload: TaskAutomationRequest,
    current_user: ClerkUser = Depends(get_current_user),
    service: AdvancedPlatformService = Depends(get_service),
) -> TaskAutomationResponse:
    """Trigger automation workflows for real-time collaboration tasks."""

    result = await service.trigger_task_workflow(payload.dict())
    return TaskAutomationResponse(**result)


@router.post(
    "/collaboration/video-meetings",
    response_model=VideoMeetingResponse,
    status_code=status.HTTP_200_OK,
)
async def schedule_video_meeting(
    payload: VideoMeetingRequest,
    current_user: ClerkUser = Depends(get_current_user),
    service: AdvancedPlatformService = Depends(get_service),
) -> VideoMeetingResponse:
    """Schedule a video-enabled meeting for deal stakeholders."""

    result = await service.schedule_video_meeting(payload.dict())
    return VideoMeetingResponse(**result)


@router.get(
    "/integrations/status",
    response_model=IntegrationStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_integration_status(
    current_user: ClerkUser = Depends(get_current_user),
    service: AdvancedPlatformService = Depends(get_service),
) -> IntegrationStatusResponse:
    """Retrieve status for enterprise integrations."""

    status_payload = await service.get_integration_status()
    return IntegrationStatusResponse(**status_payload)


@router.get(
    "/analytics/overview",
    response_model=AdvancedAnalyticsOverviewResponse,
    status_code=status.HTTP_200_OK,
)
async def get_analytics_overview(
    team_ids: Optional[str] = None,
    period_days: int = 30,
    current_user: ClerkUser = Depends(get_current_user),
    service: AdvancedPlatformService = Depends(get_service),
) -> AdvancedAnalyticsOverviewResponse:
    """Return real-time analytics, insights, and report previews."""

    payload: Dict[str, Any] = {
        "period_days": period_days,
    }
    if team_ids:
        payload["team_ids"] = [team_id.strip() for team_id in team_ids.split(",") if team_id.strip()]

    overview = await service.get_analytics_overview(payload)
    return AdvancedAnalyticsOverviewResponse(**overview)
