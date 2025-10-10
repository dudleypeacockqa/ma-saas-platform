"""
Integration Planning API Endpoints
REST API for post-acquisition integration management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime
from enum import Enum

from ..core.database import get_db
from ..auth.clerk_auth import get_current_user, ClerkUser
from ..models.integration import (
    IntegrationProject, IntegrationMilestone, SynergyOpportunity, IntegrationWorkstream,
    IntegrationTask, CulturalAssessment, ChangeInitiative, PerformanceMetric,
    IntegrationRisk, IntegrationDocument,
    IntegrationApproach, SynergyType, WorkstreamType, IntegrationStatus,
    TaskStatus, TaskPriority, RiskLevel, RiskStatus, MilestoneStatus, MilestoneType,
    SynergyStatus, ChangeType, DocumentType
)
from ..services.integration_management import (
    IntegrationProjectService,
    SynergyTrackingService,
    WorkstreamManagementService,
    RiskManagementService,
    PerformanceTrackingService
)

router = APIRouter(prefix="/integration", tags=["Integration Planning"])


# ==================== Request/Response Models ====================

class IntegrationProjectCreate(BaseModel):
    deal_id: str
    project_name: Optional[str] = None
    project_code: Optional[str] = None
    integration_approach: IntegrationApproach
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    integration_lead_user_id: Optional[str] = None
    steering_committee: Optional[List[dict]] = []
    target_synergies: Optional[float] = None
    integration_budget: Optional[float] = None
    executive_summary: Optional[str] = None


class IntegrationProjectResponse(BaseModel):
    id: str
    deal_id: str
    project_name: str
    project_code: Optional[str]
    integration_approach: str
    status: str
    overall_progress_percent: Optional[int]
    overall_health_score: Optional[int]
    target_synergies: Optional[float]
    realized_synergies: Optional[float]
    start_date: Optional[datetime]
    target_completion_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SynergyCreate(BaseModel):
    synergy_name: str
    description: Optional[str] = None
    synergy_type: SynergyType
    target_value: float
    currency: Optional[str] = "USD"
    target_realization_date: datetime
    realization_period_months: Optional[int] = None
    confidence_level: Optional[int] = 50
    implementation_plan: Optional[str] = None
    owner_user_id: Optional[str] = None
    responsible_team: Optional[str] = None


class SynergyResponse(BaseModel):
    id: str
    synergy_name: str
    synergy_type: str
    target_value: float
    realized_value: Optional[float]
    status: str
    confidence_level: Optional[int]
    target_realization_date: Optional[datetime]
    actual_realization_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SynergyRealizationCreate(BaseModel):
    reporting_period: str
    period_start_date: date
    period_end_date: date
    target_value: float
    actual_value: Optional[float] = None
    run_rate_value: Optional[float] = None
    evidence_description: Optional[str] = None
    supporting_data: Optional[dict] = {}
    notes: Optional[str] = None


class TaskCreate(BaseModel):
    task_name: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to_user_id: Optional[str] = None
    assigned_team: Optional[str] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    predecessor_tasks: Optional[List[str]] = []
    acceptance_criteria: Optional[List[str]] = []


class TaskResponse(BaseModel):
    id: str
    task_name: str
    status: str
    priority: str
    assigned_to_user_id: Optional[str]
    planned_end_date: Optional[datetime]
    completion_percent: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class RiskCreate(BaseModel):
    risk_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    probability: Optional[str] = "medium"  # very_low, low, medium, high, very_high
    impact: Optional[str] = "medium"  # very_low, low, medium, high, very_high
    potential_impact: Optional[str] = None
    financial_impact: Optional[float] = None
    mitigation_strategy: Optional[str] = None
    contingency_plan: Optional[str] = None
    owner_user_id: Optional[str] = None


# ==================== Integration Project Endpoints ====================

@router.post("/projects", response_model=IntegrationProjectResponse)
async def create_integration_project(
    project_data: IntegrationProjectCreate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Create a new integration project for a closed deal"""
    try:
        service = IntegrationProjectService(db)
        project = service.create_integration_project(
            organization_id=current_user.organization_id,
            deal_id=project_data.deal_id,
            project_data=project_data.model_dump()
        )
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects", response_model=List[IntegrationProjectResponse])
async def list_integration_projects(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user),
    status: Optional[IntegrationStatus] = None
):
    """List all integration projects for the organization"""
    query = db.query(IntegrationProject).filter(
        IntegrationProject.organization_id == current_user.organization_id,
        IntegrationProject.deleted_at.is_(None)
    )

    if status:
        query = query.filter(IntegrationProject.status == status)

    projects = query.order_by(IntegrationProject.created_at.desc()).all()
    return projects


@router.get("/projects/{project_id}", response_model=IntegrationProjectResponse)
async def get_integration_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get integration project details"""
    project = db.query(IntegrationProject).filter(
        IntegrationProject.id == project_id,
        IntegrationProject.organization_id == current_user.organization_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Integration project not found")

    return project


@router.get("/projects/{project_id}/dashboard")
async def get_project_dashboard(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get comprehensive project dashboard metrics"""
    service = IntegrationProjectService(db)
    try:
        dashboard = service.get_project_dashboard(
            project_id=project_id,
            organization_id=current_user.organization_id
        )
        return dashboard
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/projects/{project_id}/update-health")
async def update_project_health(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Recalculate and update project health score"""
    service = IntegrationProjectService(db)
    try:
        health_score = service.update_project_health(
            project_id=project_id,
            organization_id=current_user.organization_id
        )
        return {"health_score": health_score}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Synergy Management Endpoints ====================

@router.post("/projects/{project_id}/synergies", response_model=SynergyResponse)
async def create_synergy(
    project_id: str,
    synergy_data: SynergyCreate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Identify and create a new synergy opportunity"""
    service = SynergyTrackingService(db)
    try:
        synergy = service.create_synergy(
            organization_id=current_user.organization_id,
            project_id=project_id,
            synergy_data=synergy_data.model_dump()
        )
        return synergy
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/synergies", response_model=List[SynergyResponse])
async def list_synergies(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user),
    synergy_type: Optional[SynergyType] = None,
    status: Optional[SynergyStatus] = None
):
    """List synergies for an integration project"""
    query = db.query(SynergyOpportunity).filter(
        SynergyOpportunity.project_id == project_id,
        SynergyOpportunity.organization_id == current_user.organization_id,
        SynergyOpportunity.deleted_at.is_(None)
    )

    if synergy_type:
        query = query.filter(SynergyOpportunity.synergy_type == synergy_type)

    if status:
        query = query.filter(SynergyOpportunity.status == status)

    synergies = query.order_by(SynergyOpportunity.target_value.desc()).all()
    return synergies


@router.patch("/synergies/{synergy_id}/realization")
async def update_synergy_realization(
    synergy_id: str,
    realized_value: float,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Update synergy realization value"""
    service = SynergyTrackingService(db)
    try:
        from decimal import Decimal
        synergy = service.update_synergy_realization(
            synergy_id=synergy_id,
            organization_id=current_user.organization_id,
            realized_value=Decimal(str(realized_value)),
            notes=notes
        )
        return synergy
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/synergies/trends")
async def get_synergy_trends(
    project_id: str,
    months: int = 12,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get synergy realization trends over time"""
    service = SynergyTrackingService(db)
    try:
        trends = service.get_synergy_trends(
            project_id=project_id,
            organization_id=current_user.organization_id,
            months=months
        )
        return trends
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Workstream & Task Endpoints ====================

@router.get("/projects/{project_id}/workstreams")
async def list_workstreams(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user),
    workstream_type: Optional[WorkstreamType] = None
):
    """List workstreams for an integration project"""
    query = db.query(IntegrationWorkstream).filter(
        IntegrationWorkstream.project_id == project_id,
        IntegrationWorkstream.organization_id == current_user.organization_id,
        IntegrationWorkstream.deleted_at.is_(None)
    )

    if workstream_type:
        query = query.filter(IntegrationWorkstream.workstream_type == workstream_type)

    workstreams = query.all()
    return workstreams


@router.get("/workstreams/{workstream_id}/summary")
async def get_workstream_summary(
    workstream_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get comprehensive workstream summary"""
    service = WorkstreamManagementService(db)
    try:
        summary = service.get_workstream_summary(
            workstream_id=workstream_id,
            organization_id=current_user.organization_id
        )
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/workstreams/{workstream_id}/tasks", response_model=TaskResponse)
async def create_task(
    workstream_id: str,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Create a new integration task"""
    service = WorkstreamManagementService(db)
    try:
        task = service.create_task(
            organization_id=current_user.organization_id,
            workstream_id=workstream_id,
            task_data=task_data.model_dump()
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user),
    workstream_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    assigned_to_user_id: Optional[str] = None
):
    """List tasks for an integration project"""
    query = db.query(IntegrationTask).join(IntegrationWorkstream).filter(
        IntegrationWorkstream.project_id == project_id,
        IntegrationTask.organization_id == current_user.organization_id,
        IntegrationTask.deleted_at.is_(None)
    )

    if workstream_id:
        query = query.filter(IntegrationTask.workstream_id == workstream_id)

    if status:
        query = query.filter(IntegrationTask.status == status)

    if assigned_to_user_id:
        query = query.filter(IntegrationTask.assigned_to_user_id == assigned_to_user_id)

    tasks = query.order_by(IntegrationTask.planned_end_date).all()
    return tasks


@router.patch("/tasks/{task_id}")
async def update_task(
    task_id: str,
    status: TaskStatus,
    completion_percent: Optional[int] = None,
    update_note: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Update task status and completion"""
    service = WorkstreamManagementService(db)
    try:
        task = service.update_task_status(
            task_id=task_id,
            organization_id=current_user.organization_id,
            status=status,
            completion_percent=completion_percent,
            update_note=update_note
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Milestone Endpoints ====================

@router.get("/projects/{project_id}/milestones")
async def list_milestones(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user),
    milestone_type: Optional[MilestoneType] = None,
    status: Optional[MilestoneStatus] = None
):
    """List milestones for an integration project"""
    query = db.query(IntegrationMilestone).filter(
        IntegrationMilestone.project_id == project_id,
        IntegrationMilestone.organization_id == current_user.organization_id,
        IntegrationMilestone.deleted_at.is_(None)
    )

    if milestone_type:
        query = query.filter(IntegrationMilestone.milestone_type == milestone_type)

    if status:
        query = query.filter(IntegrationMilestone.status == status)

    milestones = query.order_by(IntegrationMilestone.target_date).all()
    return milestones


# ==================== Cultural Assessment & Change Management ====================

@router.get("/projects/{project_id}/cultural-assessments")
async def list_cultural_assessments(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """List cultural assessments for an integration project"""
    assessments = db.query(CulturalAssessment).filter(
        CulturalAssessment.project_id == project_id,
        CulturalAssessment.organization_id == current_user.organization_id,
        CulturalAssessment.deleted_at.is_(None)
    ).order_by(CulturalAssessment.assessment_date.desc()).all()

    return assessments


@router.get("/projects/{project_id}/change-initiatives")
async def list_change_initiatives(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user),
    change_type: Optional[ChangeType] = None,
    status: Optional[IntegrationStatus] = None
):
    """List change initiatives for an integration project"""
    query = db.query(ChangeInitiative).filter(
        ChangeInitiative.project_id == project_id,
        ChangeInitiative.organization_id == current_user.organization_id,
        ChangeInitiative.deleted_at.is_(None)
    )

    if change_type:
        query = query.filter(ChangeInitiative.change_type == change_type)

    if status:
        query = query.filter(ChangeInitiative.status == status)

    initiatives = query.all()
    return initiatives


# ==================== Performance Metrics Monitoring ====================

@router.get("/projects/{project_id}/metrics")
async def list_performance_metrics(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user),
    metric_category: Optional[str] = None
):
    """List performance metrics for an integration project"""
    query = db.query(PerformanceMetric).filter(
        PerformanceMetric.project_id == project_id,
        PerformanceMetric.organization_id == current_user.organization_id,
        PerformanceMetric.deleted_at.is_(None)
    )

    if metric_category:
        query = query.filter(PerformanceMetric.metric_category == metric_category)

    metrics = query.all()
    return metrics


@router.patch("/metrics/{metric_id}/value")
async def update_metric_value(
    metric_id: str,
    value: float,
    measurement_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Update performance metric with new measurement"""
    service = PerformanceTrackingService(db)
    try:
        from decimal import Decimal
        metric = service.record_metric_value(
            metric_id=metric_id,
            organization_id=current_user.organization_id,
            value=Decimal(str(value)),
            measurement_date=measurement_date
        )
        return metric
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Risk Management ====================

@router.post("/projects/{project_id}/risks")
async def create_risk(
    project_id: str,
    risk_data: RiskCreate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Identify and create a new integration risk"""
    service = RiskManagementService(db)
    try:
        risk = service.create_risk(
            organization_id=current_user.organization_id,
            project_id=project_id,
            risk_data=risk_data.model_dump()
        )
        return risk
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/risks")
async def list_risks(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user),
    risk_level: Optional[RiskLevel] = None,
    status: Optional[RiskStatus] = None,
    is_active: Optional[bool] = True
):
    """List risks for an integration project"""
    query = db.query(IntegrationRisk).filter(
        IntegrationRisk.project_id == project_id,
        IntegrationRisk.organization_id == current_user.organization_id,
        IntegrationRisk.deleted_at.is_(None)
    )

    if risk_level:
        query = query.filter(IntegrationRisk.risk_level == risk_level)

    if status:
        query = query.filter(IntegrationRisk.status == status)

    if is_active is not None:
        query = query.filter(IntegrationRisk.is_active == is_active)

    risks = query.order_by(IntegrationRisk.risk_score.desc()).all()
    return risks


@router.get("/projects/{project_id}/risks/matrix")
async def get_risk_matrix(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get 5x5 risk matrix visualization data"""
    service = RiskManagementService(db)
    try:
        matrix = service.get_risk_matrix(
            project_id=project_id,
            organization_id=current_user.organization_id
        )
        return matrix
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Documents & Knowledge Base ====================

@router.get("/projects/{project_id}/documents")
async def list_integration_documents(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user),
    document_type: Optional[DocumentType] = None,
    workstream_type: Optional[WorkstreamType] = None
):
    """List integration documents for a project"""
    query = db.query(IntegrationDocument).filter(
        IntegrationDocument.project_id == project_id,
        IntegrationDocument.organization_id == current_user.organization_id,
        IntegrationDocument.deleted_at.is_(None)
    )

    if document_type:
        query = query.filter(IntegrationDocument.document_type == document_type)

    if workstream_type:
        query = query.filter(IntegrationDocument.workstream_type == workstream_type)

    documents = query.order_by(IntegrationDocument.created_at.desc()).all()
    return documents
