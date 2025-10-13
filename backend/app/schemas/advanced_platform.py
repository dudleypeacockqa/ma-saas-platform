"""
Pydantic schemas for advanced platform endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AdvancedDealIntelligenceRequest(BaseModel):
    """Payload for advanced deal intelligence analysis."""

    deal_id: str = Field(..., description="Unique deal identifier")
    deal_type: Optional[str] = Field(None, description="Deal type slug (e.g. acquisition)")
    target_company: Optional[str] = None
    acquirer_company: Optional[str] = None
    industry: Optional[str] = Field(None, description="Industry vertical key")
    deal_value: float = Field(..., description="Deal value in base currency")
    currency: str = Field("USD", description="Deal currency code")
    stage: Optional[str] = Field(None, description="Pipeline stage")
    expected_close_date: Optional[datetime] = Field(None, description="Expected close date")
    key_metrics: Dict[str, Any] = Field(default_factory=dict)
    strategic_rationale: Optional[str] = None
    generate_checklist: bool = Field(False, description="Whether to generate a due diligence checklist")
    predictive_features: Optional[Dict[str, Any]] = Field(
        None, description="Additional structured data for predictive analytics"
    )
    financials: Optional[Dict[str, Any]] = Field(None, description="Financial model inputs for validation")
    industry_details: Optional[str] = Field(None, description="Detailed industry description")


class AdvancedDealIntelligenceResponse(BaseModel):
    """Response containing comprehensive deal intelligence data."""

    deal_id: str
    analysis_timestamp: Optional[datetime]
    deal_score: Dict[str, Any]
    market_context: Dict[str, Any]
    strategic_fit: Dict[str, Any]
    transaction_probability: Dict[str, Any]
    executive_summary: Optional[str]
    next_steps: List[str]
    predictive_insights: Dict[str, Any]
    due_diligence_checklist: Optional[Dict[str, Any]]
    due_diligence_summary: Optional[Dict[str, Any]]
    financial_validation: Dict[str, Any]


class AdvancedDocumentProcessingRequest(BaseModel):
    """Request payload for advanced document processing."""

    document_id: str
    deal_id: str
    filename: Optional[str] = None
    document_type: Optional[str] = Field(None, description="Document type key")
    content: Optional[str] = Field(None, description="Raw document content or extracted text")
    uploaded_by: Optional[str] = Field(None, description="Uploader user identifier")
    folder_path: Optional[str] = Field(None, description="Data room folder path")
    data_room_id: Optional[str] = Field(None, description="Existing data room identifier")
    access_level: Optional[str] = Field(None, description="Uploader access level")
    permitted_folders: Optional[List[str]] = Field(None, description="Folders uploader can access")
    analysis_options: Optional[Dict[str, Any]] = Field(None, description="Analysis configuration flags")
    tags: Optional[List[str]] = None
    version: Optional[int] = Field(None, ge=1)
    file_size: Optional[int] = Field(None, ge=0)
    security_classification: Optional[str] = Field(
        None, description="Security classification label"
    )


class AdvancedDocumentProcessingResponse(BaseModel):
    """Document processing analysis summary."""

    document_id: str
    deal_id: str
    data_room_id: str
    analysis: Dict[str, Any]
    data_room: Dict[str, Any]
    version: Dict[str, Any]
    audit_trail: List[Dict[str, Any]]


class CollaborationSessionRequest(BaseModel):
    """Create a real-time collaboration session."""

    document_id: str
    user_id: str
    organization_id: Optional[str] = None
    permissions: Optional[str] = Field("write", description="Access level")
    user_name: Optional[str] = None
    user_role: Optional[str] = None


class CollaborationSessionResponse(BaseModel):
    """Session details for clients."""

    session: Dict[str, Any]
    realtime_channel: str
    websocket_endpoint: str
    document_state: Dict[str, Any]


class CollaborationCommentRequest(BaseModel):
    """Create a threaded comment."""

    entity_type: str = Field("document", description="Entity type (document, deal, etc.)")
    entity_id: str
    user_id: str
    body: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CollaborationCommentResponse(BaseModel):
    """Comment representation."""

    comment_id: str
    user_id: str
    body: str
    created_at: datetime
    status: str
    metadata: Dict[str, Any]
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None


class CollaborationResolveRequest(BaseModel):
    """Resolve comment payload."""

    entity_type: str = Field("document", description="Entity type")
    entity_id: str
    resolved_by: str


class TaskAutomationRequest(BaseModel):
    """Trigger workflow automation."""

    trigger: Optional[str] = Field(None, description="Workflow trigger identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Context data for workflow")
    organization_id: Optional[str] = None
    deal_id: Optional[str] = None


class TaskAutomationResponse(BaseModel):
    """Workflow trigger result."""

    workflow_id: Optional[str]
    trigger: str
    status: str


class VideoMeetingRequest(BaseModel):
    """Schedule video meeting payload."""

    meeting_id: Optional[str] = None
    title: str = Field(..., description="Meeting title")
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    organizer_email: str = Field(..., description="Organizer email")
    attendee_emails: List[str] = Field(default_factory=list)
    meeting_url: Optional[str] = None
    location: Optional[str] = None


class VideoMeetingResponse(BaseModel):
    """Meeting scheduling outcome."""

    success: bool
    meeting_id: Optional[str] = None
    calendar_event_id: Optional[str] = None
    invites_sent: Optional[int] = None
    invites_failed: Optional[int] = None
    meeting_url: Optional[str] = None
    error: Optional[str] = None


class IntegrationStatusResponse(BaseModel):
    """Integration status payload."""

    retrieved_at: datetime
    integrations: List[Dict[str, Any]]


class AdvancedAnalyticsOverviewResponse(BaseModel):
    """Advanced analytics overview."""

    generated_at: datetime
    kpis: List[Dict[str, Any]]
    insights: List[Dict[str, Any]]
    active_alerts: List[Dict[str, Any]]
    processing_stats: Dict[str, Any]
    team_performance: Dict[str, Any]
    report_preview: Optional[Dict[str, Any]] = None
