"""
Teams API Routes
Endpoints for M&A team management, workflow orchestration, and collaboration
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..core.database import get_db
from ..auth.clerk_auth import get_current_user, ClerkUser
from ..services.workflow_management import (
    WorkflowManagementService,
    TeamFormationEngine,
    TaskOrchestrationEngine
)
from ..services.deal_team_integration import DealTeamIntegrationService
from ..models.teams import (
    Team, TeamMember, TeamTask, TeamMeeting, TeamChannel, TeamMessage,
    ExternalAdvisor, TeamMetrics, PerformanceReview, TaskSubtask, TaskTimeLog,
    Skill, UserSkill,
    TeamType, TeamStatus, TeamRole, TaskStatus, TaskPriority, SkillLevel,
    MeetingType, ChannelType, MessageType, PerformanceRating
)

router = APIRouter(prefix="/teams", tags=["teams"])


# ============================================================================
# Request/Response Models
# ============================================================================

class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    team_type: TeamType = TeamType.DEAL_TEAM
    deal_id: Optional[str] = None
    budget_allocated: Optional[Decimal] = None
    budget_limit: Optional[Decimal] = None
    target_completion_date: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TeamStatus] = None
    budget_allocated: Optional[Decimal] = None
    budget_limit: Optional[Decimal] = None
    target_completion_date: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = None


class TeamResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str]
    team_type: TeamType
    status: TeamStatus
    team_lead_id: str
    deal_id: Optional[str]
    member_count: int
    budget_allocated: Optional[Decimal]
    budget_used: Optional[Decimal]
    budget_limit: Optional[Decimal]
    target_completion_date: Optional[date]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TeamMemberAdd(BaseModel):
    user_id: str
    role: TeamRole = TeamRole.MEMBER
    hourly_rate: Optional[Decimal] = None
    expected_hours_per_week: Optional[int] = Field(None, ge=1, le=80)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class TeamMemberUpdate(BaseModel):
    role: Optional[TeamRole] = None
    hourly_rate: Optional[Decimal] = None
    expected_hours_per_week: Optional[int] = Field(None, ge=1, le=80)
    actual_hours_logged: Optional[Decimal] = None
    end_date: Optional[date] = None
    status: Optional[str] = None


class TeamMemberResponse(BaseModel):
    id: str
    team_id: str
    user_id: str
    role: TeamRole
    hourly_rate: Optional[Decimal]
    expected_hours_per_week: Optional[int]
    actual_hours_logged: Optional[Decimal]
    start_date: Optional[date]
    end_date: Optional[date]
    status: str
    joined_at: datetime

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to_id: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_hours: Optional[Decimal] = None
    parent_task_id: Optional[str] = None
    depends_on_tasks: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to_id: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    metadata: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    id: str
    team_id: str
    title: str
    description: Optional[str]
    assigned_to_id: Optional[str]
    status: TaskStatus
    due_date: Optional[datetime]
    priority: TaskPriority
    estimated_hours: Optional[Decimal]
    actual_hours: Optional[Decimal]
    progress_percentage: int
    parent_task_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class MeetingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    meeting_type: MeetingType = MeetingType.TEAM_STANDUP
    scheduled_start: datetime
    scheduled_end: datetime
    meeting_url: Optional[str] = None
    attendee_ids: Optional[List[str]] = None
    agenda: Optional[Dict[str, Any]] = None


class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    meeting_url: Optional[str] = None
    attendee_ids: Optional[List[str]] = None
    agenda: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class MeetingResponse(BaseModel):
    id: str
    team_id: str
    title: str
    description: Optional[str]
    meeting_type: MeetingType
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    meeting_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    channel_type: ChannelType = ChannelType.GENERAL
    is_private: bool = False
    member_ids: Optional[List[str]] = None


class ChannelResponse(BaseModel):
    id: str
    team_id: str
    name: str
    description: Optional[str]
    channel_type: ChannelType
    is_private: bool
    message_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.TEXT
    reply_to_id: Optional[str] = None
    attachments: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    id: str
    channel_id: str
    sender_id: str
    content: str
    message_type: MessageType
    reply_to_id: Optional[str]
    attachments: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class TeamFormationRequest(BaseModel):
    deal_id: Optional[str] = None
    required_skills: Optional[List[str]] = None
    team_size: int = Field(default=5, ge=2, le=20)
    budget_limit: Optional[Decimal] = None
    target_completion_date: Optional[date] = None
    include_external_advisors: bool = False


class TeamRecommendationResponse(BaseModel):
    recommended_members: List[Dict[str, Any]]
    total_estimated_cost: Decimal
    skill_coverage: Dict[str, float]
    team_composition_analysis: Dict[str, Any]
    confidence_score: float


class TaskOrchestrationRequest(BaseModel):
    tasks: List[TaskCreate]
    auto_assign: bool = True
    optimize_schedule: bool = True


class WorkflowTemplateRequest(BaseModel):
    workflow_type: str = Field(..., description="Type of workflow (e.g., 'due_diligence', 'negotiation')")
    customize_for_deal: bool = True


class PerformanceMetricsResponse(BaseModel):
    team_productivity_score: float
    task_completion_rate: float
    budget_utilization: float
    average_task_completion_time: float
    member_performance_scores: Dict[str, float]
    period_start: date
    period_end: date


# ============================================================================
# Team Management Endpoints
# ============================================================================

@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team: TeamCreate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Create a new team

    Creates a new team for deal management, functional work, or project collaboration.
    The creator becomes the team lead by default.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required"
        )

    service = WorkflowManagementService(db)

    team_data = team.model_dump()
    team_data["team_lead_id"] = current_user.user_id
    team_data["organization_id"] = current_user.organization_id

    new_team = service.create_team(team_data)

    # Add creator as team lead member
    service.add_team_member(
        team_id=new_team.id,
        user_id=current_user.user_id,
        role=TeamRole.LEAD,
        added_by_id=current_user.user_id
    )

    return new_team


@router.get("/", response_model=List[TeamResponse])
async def list_teams(
    team_type: Optional[TeamType] = None,
    status: Optional[TeamStatus] = None,
    deal_id: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(created_at|name|status|member_count)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    List teams with filtering and pagination

    Returns teams based on filters with optional search functionality.
    """
    filters = {
        "team_type": team_type,
        "status": status,
        "deal_id": deal_id,
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "limit": limit,
        "offset": offset
    }

    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}

    teams = db.query(Team).filter(
        Team.organization_id == current_user.organization_id
    )

    if team_type:
        teams = teams.filter(Team.team_type == team_type)
    if status:
        teams = teams.filter(Team.status == status)
    if deal_id:
        teams = teams.filter(Team.deal_id == deal_id)
    if search:
        teams = teams.filter(
            Team.name.ilike(f"%{search}%") |
            Team.description.ilike(f"%{search}%")
        )

    # Add sorting
    if sort_by == "name":
        teams = teams.order_by(Team.name.asc() if sort_order == "asc" else Team.name.desc())
    elif sort_by == "status":
        teams = teams.order_by(Team.status.asc() if sort_order == "asc" else Team.status.desc())
    else:
        teams = teams.order_by(Team.created_at.asc() if sort_order == "asc" else Team.created_at.desc())

    teams = teams.offset(offset).limit(limit).all()

    # Add member count to response
    result = []
    for team in teams:
        team_dict = team.__dict__.copy()
        team_dict["member_count"] = db.query(TeamMember).filter(
            TeamMember.team_id == team.id,
            TeamMember.status == "active"
        ).count()
        result.append(TeamResponse(**team_dict))

    return result


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get a specific team by ID

    Returns detailed information about a single team.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    # Add member count
    member_count = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.status == "active"
    ).count()

    team_dict = team.__dict__.copy()
    team_dict["member_count"] = member_count

    return TeamResponse(**team_dict)


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    update: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Update a team

    Update team details. Only team leads and admins can update teams.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    # Check permissions
    if team.team_lead_id != current_user.user_id:
        # Check if user is team admin
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.user_id,
            TeamMember.role.in_([TeamRole.LEAD, TeamRole.ADMIN])
        ).first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team leads and admins can update teams"
            )

    # Update fields
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(team, field, value)

    team.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(team)

    # Add member count
    member_count = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.status == "active"
    ).count()

    team_dict = team.__dict__.copy()
    team_dict["member_count"] = member_count

    return TeamResponse(**team_dict)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Delete a team (soft delete)

    Marks the team as deleted without removing from database.
    Only team leads can delete teams.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    # Check permissions
    if team.team_lead_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team leads can delete teams"
        )

    # Soft delete
    team.deleted_at = datetime.utcnow()
    team.status = TeamStatus.DISBANDED
    db.commit()

    return None


# ============================================================================
# Team Member Management Endpoints
# ============================================================================

@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: str,
    member: TeamMemberAdd,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Add a member to a team

    Add a new member to the team with specified role and details.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    # Check permissions
    if team.team_lead_id != current_user.user_id:
        member_check = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.user_id,
            TeamMember.role.in_([TeamRole.LEAD, TeamRole.ADMIN])
        ).first()

        if not member_check:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team leads and admins can add members"
            )

    service = WorkflowManagementService(db)

    member_data = member.model_dump()
    member_data["team_id"] = team_id
    member_data["added_by_id"] = current_user.user_id

    new_member = service.add_team_member(**member_data)
    return new_member


@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members(
    team_id: str,
    role: Optional[TeamRole] = None,
    status: Optional[str] = Query(None, regex="^(active|inactive|pending)$"),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    List team members

    Returns all members of a team with optional filtering by role and status.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    members = db.query(TeamMember).filter(TeamMember.team_id == team_id)

    if role:
        members = members.filter(TeamMember.role == role)
    if status:
        members = members.filter(TeamMember.status == status)

    return members.all()


@router.patch("/{team_id}/members/{member_id}", response_model=TeamMemberResponse)
async def update_team_member(
    team_id: str,
    member_id: str,
    update: TeamMemberUpdate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Update a team member

    Update member role, hourly rate, or other details.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    member = db.query(TeamMember).filter(
        TeamMember.id == member_id,
        TeamMember.team_id == team_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member {member_id} not found in team"
        )

    # Check permissions
    if team.team_lead_id != current_user.user_id and member.user_id != current_user.user_id:
        admin_check = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.user_id,
            TeamMember.role.in_([TeamRole.LEAD, TeamRole.ADMIN])
        ).first()

        if not admin_check:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update member"
            )

    # Update fields
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)

    db.commit()
    db.refresh(member)

    return member


@router.delete("/{team_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: str,
    member_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Remove a member from a team

    Remove a member from the team. Only team leads and admins can remove members.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    member = db.query(TeamMember).filter(
        TeamMember.id == member_id,
        TeamMember.team_id == team_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member {member_id} not found in team"
        )

    # Check permissions
    if team.team_lead_id != current_user.user_id:
        admin_check = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.user_id,
            TeamMember.role.in_([TeamRole.LEAD, TeamRole.ADMIN])
        ).first()

        if not admin_check:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team leads and admins can remove members"
            )

    # Set end date and mark as inactive
    member.end_date = date.today()
    member.status = "inactive"
    db.commit()

    return None


# ============================================================================
# Task Management Endpoints
# ============================================================================

@router.post("/{team_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    team_id: str,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Create a new task for a team

    Create a task and optionally assign it to a team member.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    service = WorkflowManagementService(db)

    task_data = task.model_dump()
    task_data["team_id"] = team_id
    task_data["created_by_id"] = current_user.user_id

    new_task = service.create_task(task_data)
    return new_task


@router.get("/{team_id}/tasks", response_model=List[TaskResponse])
async def list_team_tasks(
    team_id: str,
    status: Optional[TaskStatus] = None,
    assigned_to_id: Optional[str] = None,
    priority: Optional[TaskPriority] = None,
    overdue_only: bool = False,
    sort_by: str = Query("created_at", regex="^(created_at|due_date|priority|title)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    List tasks for a team

    Returns tasks with filtering, sorting, and pagination.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    tasks = db.query(TeamTask).filter(TeamTask.team_id == team_id)

    if status:
        tasks = tasks.filter(TeamTask.status == status)
    if assigned_to_id:
        tasks = tasks.filter(TeamTask.assigned_to_id == assigned_to_id)
    if priority:
        tasks = tasks.filter(TeamTask.priority == priority)
    if overdue_only:
        tasks = tasks.filter(
            TeamTask.due_date < datetime.utcnow(),
            TeamTask.status != TaskStatus.COMPLETED
        )

    # Add sorting
    if sort_by == "due_date":
        tasks = tasks.order_by(TeamTask.due_date.asc() if sort_order == "asc" else TeamTask.due_date.desc())
    elif sort_by == "priority":
        tasks = tasks.order_by(TeamTask.priority.asc() if sort_order == "asc" else TeamTask.priority.desc())
    elif sort_by == "title":
        tasks = tasks.order_by(TeamTask.title.asc() if sort_order == "asc" else TeamTask.title.desc())
    else:
        tasks = tasks.order_by(TeamTask.created_at.asc() if sort_order == "asc" else TeamTask.created_at.desc())

    return tasks.offset(offset).limit(limit).all()


@router.get("/{team_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    team_id: str,
    task_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get a specific task

    Returns detailed information about a single task.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    task = db.query(TeamTask).filter(
        TeamTask.id == task_id,
        TeamTask.team_id == team_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return task


@router.patch("/{team_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    team_id: str,
    task_id: str,
    update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Update a task

    Update task details, status, or assignment.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    task = db.query(TeamTask).filter(
        TeamTask.id == task_id,
        TeamTask.team_id == team_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Update fields
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)

    return task


# ============================================================================
# Meeting Management Endpoints
# ============================================================================

@router.post("/{team_id}/meetings", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def schedule_meeting(
    team_id: str,
    meeting: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Schedule a team meeting

    Create a new meeting for the team with specified attendees.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    new_meeting = TeamMeeting(
        team_id=team_id,
        organizer_id=current_user.user_id,
        **meeting.model_dump(exclude={"attendee_ids"})
    )

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return new_meeting


@router.get("/{team_id}/meetings", response_model=List[MeetingResponse])
async def list_team_meetings(
    team_id: str,
    meeting_type: Optional[MeetingType] = None,
    upcoming_only: bool = Query(False, description="Only return future meetings"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    List team meetings

    Returns meetings with optional filtering and pagination.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    meetings = db.query(TeamMeeting).filter(TeamMeeting.team_id == team_id)

    if meeting_type:
        meetings = meetings.filter(TeamMeeting.meeting_type == meeting_type)
    if upcoming_only:
        meetings = meetings.filter(TeamMeeting.scheduled_start > datetime.utcnow())

    return meetings.order_by(TeamMeeting.scheduled_start.desc()).offset(offset).limit(limit).all()


# ============================================================================
# Communication Endpoints
# ============================================================================

@router.post("/{team_id}/channels", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    team_id: str,
    channel: ChannelCreate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Create a communication channel

    Create a new channel for team communication.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    new_channel = TeamChannel(
        team_id=team_id,
        created_by_id=current_user.user_id,
        **channel.model_dump(exclude={"member_ids"})
    )

    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)

    # Add message count
    new_channel_dict = new_channel.__dict__.copy()
    new_channel_dict["message_count"] = 0

    return ChannelResponse(**new_channel_dict)


@router.get("/{team_id}/channels", response_model=List[ChannelResponse])
async def list_team_channels(
    team_id: str,
    channel_type: Optional[ChannelType] = None,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    List team channels

    Returns communication channels for the team.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    channels = db.query(TeamChannel).filter(TeamChannel.team_id == team_id)

    if channel_type:
        channels = channels.filter(TeamChannel.channel_type == channel_type)

    # Add message count to each channel
    result = []
    for channel in channels.all():
        message_count = db.query(TeamMessage).filter(TeamMessage.channel_id == channel.id).count()
        channel_dict = channel.__dict__.copy()
        channel_dict["message_count"] = message_count
        result.append(ChannelResponse(**channel_dict))

    return result


@router.post("/{team_id}/channels/{channel_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    team_id: str,
    channel_id: str,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Send a message to a channel

    Post a new message in the team channel.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    channel = db.query(TeamChannel).filter(
        TeamChannel.id == channel_id,
        TeamChannel.team_id == team_id
    ).first()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel {channel_id} not found"
        )

    new_message = TeamMessage(
        channel_id=channel_id,
        sender_id=current_user.user_id,
        **message.model_dump()
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message


@router.get("/{team_id}/channels/{channel_id}/messages", response_model=List[MessageResponse])
async def list_channel_messages(
    team_id: str,
    channel_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    List messages in a channel

    Returns messages with pagination, newest first.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    channel = db.query(TeamChannel).filter(
        TeamChannel.id == channel_id,
        TeamChannel.team_id == team_id
    ).first()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel {channel_id} not found"
        )

    messages = db.query(TeamMessage).filter(
        TeamMessage.channel_id == channel_id
    ).order_by(TeamMessage.created_at.desc()).offset(offset).limit(limit).all()

    return messages


# ============================================================================
# Advanced Workflow Endpoints
# ============================================================================

@router.post("/recommend", response_model=TeamRecommendationResponse)
async def recommend_team_composition(
    request: TeamFormationRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get AI-powered team composition recommendations

    Analyzes available team members and recommends optimal team composition
    based on skills, availability, and budget constraints.
    """
    service = WorkflowManagementService(db)
    engine = TeamFormationEngine(db)

    recommendation = engine.recommend_team_composition(
        organization_id=current_user.organization_id,
        deal_id=request.deal_id,
        required_skills=request.required_skills,
        team_size=request.team_size,
        budget_limit=request.budget_limit
    )

    return TeamRecommendationResponse(**recommendation)


@router.post("/{team_id}/orchestrate-tasks", response_model=Dict[str, Any])
async def orchestrate_tasks(
    team_id: str,
    request: TaskOrchestrationRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Orchestrate task dependencies and scheduling

    Automatically organizes tasks with dependencies, critical path analysis,
    and optimal scheduling based on team capacity.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    service = WorkflowManagementService(db)
    engine = TaskOrchestrationEngine(db)

    # Create tasks with orchestration
    task_data_list = []
    for task in request.tasks:
        task_dict = task.model_dump()
        task_dict["team_id"] = team_id
        task_dict["created_by_id"] = current_user.user_id
        task_data_list.append(task_dict)

    orchestration_result = engine.orchestrate_tasks(
        team_id=team_id,
        task_list=task_data_list,
        auto_assign=request.auto_assign,
        optimize_schedule=request.optimize_schedule
    )

    return orchestration_result


@router.post("/workflow-template", response_model=List[TaskResponse])
async def apply_workflow_template(
    team_id: str,
    request: WorkflowTemplateRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Apply predefined workflow template

    Creates a set of tasks and workflows based on common M&A process templates
    such as due diligence, negotiation, or integration workflows.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    service = WorkflowManagementService(db)

    tasks = service.apply_workflow_template(
        team_id=team_id,
        workflow_type=request.workflow_type,
        user_id=current_user.user_id,
        customize_for_deal=request.customize_for_deal,
        deal_id=team.deal_id
    )

    return tasks


@router.get("/{team_id}/metrics", response_model=PerformanceMetricsResponse)
async def get_team_performance_metrics(
    team_id: str,
    period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get team performance metrics

    Returns comprehensive analytics about team productivity, task completion
    rates, budget utilization, and individual performance scores.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    service = WorkflowManagementService(db)

    end_date = date.today()
    start_date = end_date - timedelta(days=period_days)

    metrics = service.calculate_team_performance_metrics(
        team_id=team_id,
        start_date=start_date,
        end_date=end_date
    )

    return PerformanceMetricsResponse(
        period_start=start_date,
        period_end=end_date,
        **metrics
    )


@router.post("/{team_id}/auto-form", response_model=TeamResponse)
async def auto_form_team(
    team_id: str,
    formation_request: TeamFormationRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Automatically form team with optimal composition

    Uses AI to automatically add the best available team members based on
    skills, availability, and other optimization criteria.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    service = WorkflowManagementService(db)
    engine = TeamFormationEngine(db)

    # Get recommendations
    recommendation = engine.recommend_team_composition(
        organization_id=current_user.organization_id,
        deal_id=formation_request.deal_id,
        required_skills=formation_request.required_skills,
        team_size=formation_request.team_size,
        budget_limit=formation_request.budget_limit
    )

    # Auto-add recommended members
    for member_data in recommendation["recommended_members"]:
        service.add_team_member(
            team_id=team_id,
            user_id=member_data["user_id"],
            role=TeamRole.MEMBER,
            hourly_rate=member_data.get("hourly_rate"),
            expected_hours_per_week=member_data.get("expected_hours_per_week"),
            added_by_id=current_user.user_id
        )

    # Return updated team
    db.refresh(team)
    member_count = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.status == "active"
    ).count()

    team_dict = team.__dict__.copy()
    team_dict["member_count"] = member_count

    return TeamResponse(**team_dict)


# ============================================================================
# Deal Integration Endpoints
# ============================================================================

@router.post("/deal/{deal_id}/create-team", response_model=Dict[str, Any])
async def create_team_for_deal(
    deal_id: str,
    team_name: Optional[str] = None,
    team_lead_id: Optional[str] = None,
    auto_populate: bool = True,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Create a dedicated team for a deal

    Automatically creates an enhanced team structure for a deal with optional
    migration of existing deal team members and stage-appropriate workflows.
    """
    integration_service = DealTeamIntegrationService(db)

    try:
        result = integration_service.create_team_for_deal(
            deal_id=deal_id,
            team_name=team_name,
            team_lead_id=team_lead_id or current_user.user_id,
            auto_populate=auto_populate
        )

        return {
            "success": True,
            "team_id": result["team"].id,
            "team_name": result["team"].name,
            "deal_id": deal_id,
            "members_migrated": result["members_migrated"],
            "initial_tasks_created": result["initial_tasks_created"],
            "message": f"Team '{result['team'].name}' created successfully for deal"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating team for deal: {str(e)}"
        )


@router.post("/deal/{deal_id}/sync", response_model=Dict[str, Any])
async def sync_deal_team(
    deal_id: str,
    team_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Synchronize deal team members with enhanced team structure

    Syncs existing deal team members with the enhanced team management system,
    creating team member records with appropriate roles and allocations.
    """
    integration_service = DealTeamIntegrationService(db)

    try:
        result = integration_service.sync_deal_team_with_enhanced_team(
            deal_id=deal_id,
            team_id=team_id
        )

        return {
            "success": True,
            "deal_id": deal_id,
            "team_id": result["team_id"],
            "sync_results": result["sync_results"],
            "message": f"Synchronized {result['sync_results']['added']} team members"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error syncing deal team: {str(e)}"
        )


@router.post("/deal/{deal_id}/create-workflow", response_model=Dict[str, Any])
async def create_deal_workflow(
    deal_id: str,
    team_id: Optional[str] = None,
    workflow_template: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Create workflow tasks based on deal stage

    Creates appropriate workflow tasks for the current deal stage, including
    due diligence checklists, valuation tasks, negotiation activities, etc.
    """
    integration_service = DealTeamIntegrationService(db)

    try:
        result = integration_service.create_deal_stage_workflow(
            deal_id=deal_id,
            team_id=team_id,
            workflow_template=workflow_template
        )

        return {
            "success": True,
            "deal_id": deal_id,
            "team_id": result["team_id"],
            "workflow_template": result["workflow_template"],
            "tasks_created": result["tasks_created"],
            "message": f"Created {result['tasks_created']} workflow tasks"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating deal workflow: {str(e)}"
        )


@router.get("/deal/{deal_id}/recommendations", response_model=Dict[str, Any])
async def get_deal_team_recommendations(
    deal_id: str,
    context: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get AI-powered team recommendations for a deal

    Analyzes deal characteristics and provides recommendations for optimal
    team composition, skills required, and resource allocation.
    """
    integration_service = DealTeamIntegrationService(db)

    try:
        recommendations = integration_service.generate_team_recommendations(
            deal_id=deal_id,
            context=context
        )

        return {
            "success": True,
            "deal_id": deal_id,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/deal/{deal_id}/performance", response_model=Dict[str, Any])
async def get_deal_team_performance(
    deal_id: str,
    period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get team performance metrics for a specific deal

    Returns comprehensive performance analytics including task completion rates,
    budget utilization, timeline adherence, and deal-specific metrics.
    """
    integration_service = DealTeamIntegrationService(db)

    try:
        performance = integration_service.get_team_performance_for_deal(
            deal_id=deal_id,
            period_days=period_days
        )

        if performance.get("status") == "no_team_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No team found for this deal"
            )

        return {
            "success": True,
            "deal_id": deal_id,
            "performance": performance,
            "analysis_period_days": period_days
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting performance metrics: {str(e)}"
        )


@router.get("/deal/{deal_id}/team", response_model=TeamResponse)
async def get_team_for_deal(
    deal_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get the enhanced team associated with a deal

    Returns the enhanced team structure for a deal, or suggests creating one
    if no enhanced team exists.
    """
    team = db.query(Team).filter(
        Team.deal_id == deal_id,
        Team.organization_id == current_user.organization_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No enhanced team found for deal {deal_id}. Consider creating one with POST /teams/deal/{deal_id}/create-team"
        )

    # Add member count
    member_count = db.query(TeamMember).filter(
        TeamMember.team_id == team.id,
        TeamMember.status == "active"
    ).count()

    team_dict = team.__dict__.copy()
    team_dict["member_count"] = member_count

    return TeamResponse(**team_dict)