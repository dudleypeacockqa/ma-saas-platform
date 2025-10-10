"""
Negotiation API endpoints for M&A SaaS Platform
Comprehensive API for managing deal negotiations with workflow automation
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal

from app.core.database import get_db
from app.models.negotiations import (
    Negotiation, NegotiationParticipant, NegotiationPosition, NegotiationMessage,
    NegotiationStatus, ParticipantRole, PositionStatus, MessageType,
    TermSheetStatus, DealStructureType
)
from app.services.negotiation_service import NegotiationService
from app.auth.clerk_auth import get_current_user, get_current_organization_user

router = APIRouter(prefix="/api/negotiations", tags=["negotiations"])


# Pydantic Schemas

class NegotiationBase(BaseModel):
    title: str
    description: Optional[str] = None
    buyer_lead_id: Optional[str] = None
    seller_lead_id: Optional[str] = None
    target_completion_date: Optional[date] = None


class NegotiationCreate(NegotiationBase):
    deal_id: str


class NegotiationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[NegotiationStatus] = None
    buyer_lead_id: Optional[str] = None
    seller_lead_id: Optional[str] = None
    target_completion_date: Optional[date] = None
    priority_level: Optional[str] = None


class NegotiationResponse(NegotiationBase):
    id: str
    deal_id: str
    organization_id: str
    negotiation_round: int
    status: NegotiationStatus
    start_date: datetime
    actual_completion_date: Optional[date] = None
    last_activity_date: datetime
    current_term_sheet_id: Optional[str] = None
    total_positions: int
    resolved_positions: int
    open_issues_count: int
    completion_percentage: int
    priority_level: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ParticipantBase(BaseModel):
    user_id: str
    role: ParticipantRole
    party_name: Optional[str] = None
    can_make_offers: bool = False
    can_accept_terms: bool = False
    can_view_confidential: bool = False


class ParticipantCreate(ParticipantBase):
    pass


class ParticipantUpdate(BaseModel):
    role: Optional[ParticipantRole] = None
    party_name: Optional[str] = None
    can_make_offers: Optional[bool] = None
    can_accept_terms: Optional[bool] = None
    can_view_confidential: Optional[bool] = None
    is_active: Optional[bool] = None


class ParticipantResponse(ParticipantBase):
    id: str
    negotiation_id: str
    is_active: bool
    joined_date: datetime
    last_seen_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PositionBase(BaseModel):
    term_category: str
    term_name: str
    term_description: Optional[str] = None
    buyer_position: Optional[str] = None
    seller_position: Optional[str] = None
    buyer_rationale: Optional[str] = None
    seller_rationale: Optional[str] = None
    priority_level: int = Field(default=3, ge=1, le=5)
    deal_breaker: bool = False
    financial_impact: Optional[Decimal] = None
    assigned_to_id: Optional[str] = None
    target_resolution_date: Optional[date] = None


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    term_description: Optional[str] = None
    current_value: Optional[str] = None
    status: Optional[PositionStatus] = None
    buyer_position: Optional[str] = None
    seller_position: Optional[str] = None
    buyer_rationale: Optional[str] = None
    seller_rationale: Optional[str] = None
    priority_level: Optional[int] = Field(None, ge=1, le=5)
    deal_breaker: Optional[bool] = None
    financial_impact: Optional[Decimal] = None
    assigned_to_id: Optional[str] = None
    target_resolution_date: Optional[date] = None
    internal_notes: Optional[str] = None


class PositionResponse(PositionBase):
    id: str
    negotiation_id: str
    current_value: Optional[str] = None
    status: PositionStatus
    position_history: Optional[List] = None
    open_questions: Optional[List[str]] = None
    internal_notes: Optional[str] = None
    actual_resolution_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str
    message_type: MessageType = MessageType.QUESTION
    subject: Optional[str] = None
    parent_message_id: Optional[str] = None
    related_position_id: Optional[str] = None
    is_internal: bool = False
    requires_response: bool = False
    response_deadline: Optional[datetime] = None


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: str
    negotiation_id: str
    sender_id: str
    thread_id: str
    is_confidential: bool
    read_by: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    include_progress: bool = True
    include_positions: bool = True
    include_participants: bool = True
    include_activity: bool = True


# API Endpoints

@router.post("/", response_model=NegotiationResponse, status_code=status.HTTP_201_CREATED)
async def create_negotiation(
    negotiation_data: NegotiationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Create a new negotiation session."""
    service = NegotiationService(db)
    negotiation = service.create_negotiation(
        organization_id=current_user["organization_id"],
        created_by_id=current_user["id"],
        **negotiation_data.model_dump()
    )
    return negotiation


@router.get("/", response_model=List[NegotiationResponse])
async def list_negotiations(
    deal_id: Optional[str] = None,
    status_filter: Optional[NegotiationStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """List all negotiations with optional filters."""
    service = NegotiationService(db)
    negotiations = service.list_negotiations(
        organization_id=current_user["organization_id"],
        deal_id=deal_id,
        status=status_filter,
        limit=limit,
        offset=offset
    )
    return negotiations


@router.get("/{negotiation_id}", response_model=NegotiationResponse)
async def get_negotiation(
    negotiation_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Get a specific negotiation by ID."""
    service = NegotiationService(db)
    negotiation = service.get_negotiation_by_id(
        negotiation_id,
        current_user["organization_id"]
    )
    if not negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negotiation not found"
        )
    return negotiation


@router.patch("/{negotiation_id}", response_model=NegotiationResponse)
async def update_negotiation(
    negotiation_id: str,
    updates: NegotiationUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Update a negotiation."""
    negotiation = (
        db.query(Negotiation)
        .filter(
            Negotiation.id == negotiation_id,
            Negotiation.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negotiation not found"
        )

    # Update fields
    for field, value in updates.model_dump(exclude_unset=True).items():
        if hasattr(negotiation, field):
            setattr(negotiation, field, value)

    negotiation.updated_by = current_user["id"]
    db.commit()
    db.refresh(negotiation)

    return negotiation


@router.get("/{negotiation_id}/analysis")
async def analyze_negotiation(
    negotiation_id: str,
    analysis_request: AnalysisRequest = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Get comprehensive analysis of negotiation progress."""
    service = NegotiationService(db)
    try:
        analysis = service.analyze_negotiation_progress(
            negotiation_id,
            current_user["organization_id"]
        )
        return analysis
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Participant endpoints

@router.post("/{negotiation_id}/participants", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
async def add_participant(
    negotiation_id: str,
    participant_data: ParticipantCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Add a participant to the negotiation."""
    service = NegotiationService(db)
    try:
        participant = service.add_participant(
            negotiation_id=negotiation_id,
            added_by_id=current_user["id"],
            **participant_data.model_dump()
        )
        return participant
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{negotiation_id}/participants", response_model=List[ParticipantResponse])
async def list_participants(
    negotiation_id: str,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """List participants in a negotiation."""
    query = (
        db.query(NegotiationParticipant)
        .filter(
            NegotiationParticipant.negotiation_id == negotiation_id,
            NegotiationParticipant.organization_id == current_user["organization_id"]
        )
    )

    if active_only:
        query = query.filter(NegotiationParticipant.is_active == True)

    participants = query.all()
    return participants


@router.patch("/{negotiation_id}/participants/{participant_id}", response_model=ParticipantResponse)
async def update_participant(
    negotiation_id: str,
    participant_id: str,
    updates: ParticipantUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Update a negotiation participant."""
    participant = (
        db.query(NegotiationParticipant)
        .filter(
            NegotiationParticipant.id == participant_id,
            NegotiationParticipant.negotiation_id == negotiation_id,
            NegotiationParticipant.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )

    # Update fields
    for field, value in updates.model_dump(exclude_unset=True).items():
        if hasattr(participant, field):
            setattr(participant, field, value)

    participant.updated_by = current_user["id"]
    db.commit()
    db.refresh(participant)

    return participant


# Position endpoints

@router.post("/{negotiation_id}/positions", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
async def create_position(
    negotiation_id: str,
    position_data: PositionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Create a new negotiation position."""
    service = NegotiationService(db)
    position = service.create_position(
        negotiation_id=negotiation_id,
        created_by_id=current_user["id"],
        **position_data.model_dump()
    )
    return position


@router.get("/{negotiation_id}/positions", response_model=List[PositionResponse])
async def list_positions(
    negotiation_id: str,
    status_filter: Optional[PositionStatus] = None,
    priority_levels: Optional[List[int]] = None,
    deal_breakers_only: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """List positions in a negotiation with filtering."""
    service = NegotiationService(db)
    positions = service.get_negotiation_positions(
        negotiation_id=negotiation_id,
        organization_id=current_user["organization_id"],
        status=status_filter,
        priority_levels=priority_levels,
        deal_breakers_only=deal_breakers_only
    )
    return positions


@router.get("/{negotiation_id}/positions/{position_id}", response_model=PositionResponse)
async def get_position(
    negotiation_id: str,
    position_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Get a specific negotiation position."""
    position = (
        db.query(NegotiationPosition)
        .filter(
            NegotiationPosition.id == position_id,
            NegotiationPosition.negotiation_id == negotiation_id,
            NegotiationPosition.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )

    return position


@router.patch("/{negotiation_id}/positions/{position_id}", response_model=PositionResponse)
async def update_position(
    negotiation_id: str,
    position_id: str,
    updates: PositionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Update a negotiation position with history tracking."""
    service = NegotiationService(db)
    try:
        position = service.update_position(
            position_id=position_id,
            organization_id=current_user["organization_id"],
            updates=updates.model_dump(exclude_unset=True),
            updated_by_id=current_user["id"]
        )
        return position
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Message endpoints

@router.post("/{negotiation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    negotiation_id: str,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Send a message in the negotiation."""
    service = NegotiationService(db)
    message = service.send_message(
        negotiation_id=negotiation_id,
        sender_id=current_user["id"],
        **message_data.model_dump()
    )
    return message


@router.get("/{negotiation_id}/messages", response_model=List[MessageResponse])
async def list_messages(
    negotiation_id: str,
    thread_id: Optional[str] = None,
    message_type: Optional[MessageType] = None,
    include_internal: bool = True,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """List messages in a negotiation with filtering."""
    service = NegotiationService(db)
    messages = service.get_negotiation_messages(
        negotiation_id=negotiation_id,
        organization_id=current_user["organization_id"],
        thread_id=thread_id,
        message_type=message_type,
        include_internal=include_internal,
        limit=limit,
        offset=offset
    )
    return messages


@router.patch("/{negotiation_id}/messages/{message_id}/read")
async def mark_message_read(
    negotiation_id: str,
    message_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Mark a message as read."""
    message = (
        db.query(NegotiationMessage)
        .filter(
            NegotiationMessage.id == message_id,
            NegotiationMessage.negotiation_id == negotiation_id,
            NegotiationMessage.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Update read status
    if not message.read_by:
        message.read_by = {}

    message.read_by[current_user["id"]] = datetime.utcnow().isoformat()

    db.commit()

    return {"status": "success", "message": "Message marked as read"}


# Workflow automation endpoints

@router.post("/{negotiation_id}/auto-assign-positions")
async def auto_assign_positions(
    negotiation_id: str,
    assignment_criteria: dict = {},
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Automatically assign positions based on criteria."""
    # Get unassigned positions
    positions = (
        db.query(NegotiationPosition)
        .filter(
            NegotiationPosition.negotiation_id == negotiation_id,
            NegotiationPosition.organization_id == current_user["organization_id"],
            NegotiationPosition.assigned_to_id.is_(None)
        )
        .all()
    )

    # Simple assignment logic (would be more sophisticated in production)
    participants = (
        db.query(NegotiationParticipant)
        .filter(
            NegotiationParticipant.negotiation_id == negotiation_id,
            NegotiationParticipant.is_active == True
        )
        .all()
    )

    if not participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active participants to assign positions to"
        )

    assigned_count = 0
    for i, position in enumerate(positions):
        # Round-robin assignment
        participant = participants[i % len(participants)]
        position.assigned_to_id = participant.user_id
        assigned_count += 1

    db.commit()

    return {
        "status": "success",
        "assigned_positions": assigned_count,
        "message": f"Automatically assigned {assigned_count} positions"
    }


@router.post("/{negotiation_id}/generate-summary")
async def generate_negotiation_summary(
    negotiation_id: str,
    include_sections: List[str] = ["overview", "positions", "progress", "next_steps"],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Generate a comprehensive negotiation summary."""
    service = NegotiationService(db)

    try:
        # Get analysis data
        analysis = service.analyze_negotiation_progress(
            negotiation_id,
            current_user["organization_id"]
        )

        negotiation = service.get_negotiation_by_id(
            negotiation_id,
            current_user["organization_id"]
        )

        summary = {
            "negotiation_id": negotiation_id,
            "title": negotiation.title,
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": current_user["id"]
        }

        if "overview" in include_sections:
            summary["overview"] = {
                "status": analysis["status"],
                "completion_percentage": analysis["completion_percentage"],
                "days_active": analysis["days_active"],
                "total_participants": len(negotiation.participants.all())
            }

        if "positions" in include_sections:
            summary["positions"] = {
                "total": analysis["total_positions"],
                "resolved": analysis["resolved_positions"],
                "deal_breakers": analysis["deal_breakers"],
                "overdue": analysis["overdue_positions"]
            }

        if "progress" in include_sections:
            summary["progress"] = {
                "momentum_score": analysis["momentum_score"],
                "recent_activity": analysis["recent_activity"],
                "status_breakdown": analysis["status_breakdown"]
            }

        if "next_steps" in include_sections:
            next_steps = []
            if analysis["overdue_positions"]["count"] > 0:
                next_steps.append("Address overdue positions")
            if analysis["deal_breakers"]["unresolved"] > 0:
                next_steps.append("Resolve deal-breaking issues")
            if analysis["completion_percentage"] > 80:
                next_steps.append("Prepare for final agreement")

            summary["next_steps"] = next_steps

        return summary

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )