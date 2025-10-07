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
    TaskStatus, RiskLevel, MilestoneStatus, SynergyStatus
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
    title: str
    description: Optional[str] = None
    milestone_id: Optional[str] = None
    workstream_id: Optional[str] = None
    priority: IssuePriority = IssuePriority.MEDIUM
    assigned_to_id: Optional[str] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    is_critical_path: bool = False
    is_day_1_critical: bool = False
    depends_on_task_ids: Optional[List[str]] = []
    meta_data: Optional[dict] = {}


class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    completion_percentage: Optional[int] = None
    actual_hours: Optional[float] = None
    notes: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    status: str
    priority: str
    assigned_to_id: Optional[str]
    due_date: Optional[date]
    completion_percentage: int
    is_critical_path: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CulturalAssessmentCreate(BaseModel):
    assessment_name: str
    assessment_date: Optional[date] = None
    leadership_style_score: Optional[int] = None
    decision_making_score: Optional[int] = None
    communication_style_score: Optional[int] = None
    work_life_balance_score: Optional[int] = None
    innovation_score: Optional[int] = None
    risk_tolerance_score: Optional[int] = None
    collaboration_score: Optional[int] = None
    hierarchy_score: Optional[int] = None
    identified_gaps: Optional[List[dict]] = []
    gap_severity: Optional[str] = None
    integration_recommendations: Optional[List[dict]] = []
    change_initiatives_needed: Optional[List[dict]] = []
    acquirer_sentiment_score: Optional[int] = None
    target_sentiment_score: Optional[int] = None
    survey_responses: Optional[int] = None
    survey_response_rate: Optional[float] = None
    key_strengths: Optional[List[dict]] = []
    key_risks: Optional[List[dict]] = []
    meta_data: Optional[dict] = {}


class ChangeInitiativeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    initiative_type: str
    target_audience: Optional[str] = None
    impacted_employee_count: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    initiative_lead_id: Optional[str] = None
    executive_sponsor_id: Optional[str] = None
    planned_activities: Optional[List[dict]] = []
    communication_channels: Optional[List[str]] = []
    communication_frequency: Optional[str] = None
    training_modules: Optional[List[dict]] = []
    allocated_budget: Optional[float] = None
    meta_data: Optional[dict] = {}


class KPICreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    workstream_id: Optional[str] = None
    measurement_unit: Optional[str] = None
    measurement_frequency: Optional[str] = None
    baseline_value: Optional[float] = None
    target_value: float
    current_value: Optional[float] = None
    threshold_green: Optional[float] = None
    threshold_yellow: Optional[float] = None
    threshold_red: Optional[float] = None
    owner_id: Optional[str] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    calculation_method: Optional[str] = None
    data_source: Optional[str] = None
    meta_data: Optional[dict] = {}


class KPIUpdate(BaseModel):
    current_value: float
    measurement_date: date


class RiskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    workstream_id: Optional[str] = None
    severity: RiskSeverity
    probability: int
    impact_score: int
    risk_owner_id: Optional[str] = None
    mitigation_plan: Optional[str] = None
    mitigation_actions: Optional[List[dict]] = []
    mitigation_owner_id: Optional[str] = None
    mitigation_deadline: Optional[date] = None
    mitigation_budget: Optional[float] = None
    contingency_plan: Optional[str] = None
    review_frequency_days: int = 7
    meta_data: Optional[dict] = {}


class IssueCreate(BaseModel):
    title: str
    description: Optional[str] = None
    workstream_id: Optional[str] = None
    related_task_id: Optional[str] = None
    issue_type: Optional[str] = None
    priority: IssuePriority
    impact_level: Optional[str] = None
    assigned_to_id: Optional[str] = None
    due_date: Optional[date] = None
    impacted_tasks: Optional[List[str]] = []
    impacted_milestones: Optional[List[str]] = []
    delay_days: Optional[int] = None
    cost_impact: Optional[float] = None
    meta_data: Optional[dict] = {}


# ==================== Integration Project Endpoints ====================

@router.post("/projects", response_model=IntegrationProjectResponse)
async def create_integration_project(
    project_data: IntegrationProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    current_org: str = Depends(get_current_org)
):
    """Create a new integration project for a closed deal"""
    try:
        service = IntegrationProjectService(db)
        project = service.create_integration_project(
            organization_id=current_org,
            deal_id=project_data.deal_id,
            project_data=project_data.model_dump()
        )
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects", response_model=List[IntegrationProjectResponse])
async def list_integration_projects(
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org),
    status: Optional[IntegrationStatus] = None
):
    """List all integration projects for the organization"""
    query = db.query(IntegrationProject).filter(
        IntegrationProject.organization_id == current_org,
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
    current_org: str = Depends(get_current_org)
):
    """Get integration plan details"""
    plan = db.query(IntegrationPlan).filter(
        IntegrationPlan.id == plan_id,
        IntegrationPlan.organization_id == current_org
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Integration plan not found")

    return plan


@router.post("/plans/{plan_id}/refresh-progress")
async def refresh_plan_progress(
    plan_id: str,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org)
):
    """Recalculate and update plan progress metrics"""
    try:
        plan = await IntegrationPlanningService.update_plan_progress(
            db=db,
            plan_id=plan_id,
            organization_id=current_org
        )
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Synergy Management Endpoints ====================

@router.post("/plans/{plan_id}/synergies", response_model=SynergyResponse)
async def create_synergy(
    plan_id: str,
    synergy_data: SynergyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    current_org: str = Depends(get_current_org)
):
    """Identify and create a new synergy opportunity"""
    try:
        synergy = await SynergyManagementService.identify_synergy(
            db=db,
            plan_id=plan_id,
            organization_id=current_org,
            synergy_data=synergy_data.model_dump(),
            user_id=current_user["user_id"]
        )
        return synergy
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans/{plan_id}/synergies", response_model=List[SynergyResponse])
async def list_synergies(
    plan_id: str,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org),
    synergy_type: Optional[SynergyType] = None,
    status: Optional[str] = None
):
    """List synergies for an integration plan"""
    query = db.query(SynergyOpportunity).filter(
        SynergyOpportunity.plan_id == plan_id,
        SynergyOpportunity.organization_id == current_org,
        SynergyOpportunity.deleted_at.is_(None)
    )

    if synergy_type:
        query = query.filter(SynergyOpportunity.synergy_type == synergy_type)

    if status:
        query = query.filter(SynergyOpportunity.status == status)

    synergies = query.order_by(SynergyOpportunity.target_value.desc()).all()
    return synergies


@router.post("/synergies/{synergy_id}/realizations")
async def record_synergy_realization(
    synergy_id: str,
    realization_data: SynergyRealizationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    current_org: str = Depends(get_current_org)
):
    """Record actual synergy realization for a period"""
    try:
        realization = await SynergyManagementService.record_synergy_realization(
            db=db,
            synergy_id=synergy_id,
            organization_id=current_org,
            realization_data=realization_data.model_dump(),
            user_id=current_user["user_id"]
        )
        return realization
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans/{plan_id}/synergies/waterfall")
async def get_synergy_waterfall(
    plan_id: str,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org)
):
    """Get synergy waterfall chart data"""
    waterfall_data = await SynergyManagementService.get_synergy_waterfall(
        db=db,
        plan_id=plan_id,
        organization_id=current_org
    )
    return waterfall_data


# ==================== Workstream & Task Endpoints ====================

@router.get("/plans/{plan_id}/workstreams")
async def list_workstreams(
    plan_id: str,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org),
    workstream_type: Optional[WorkstreamType] = None
):
    """List workstreams for an integration plan"""
    query = db.query(IntegrationWorkstream).filter(
        IntegrationWorkstream.plan_id == plan_id,
        IntegrationWorkstream.organization_id == current_org,
        IntegrationWorkstream.deleted_at.is_(None)
    )

    if workstream_type:
        query = query.filter(IntegrationWorkstream.workstream_type == workstream_type)

    workstreams = query.all()
    return workstreams


@router.post("/plans/{plan_id}/tasks", response_model=TaskResponse)
async def create_task(
    plan_id: str,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    current_org: str = Depends(get_current_org)
):
    """Create a new integration task"""
    try:
        task = await WorkstreamManagementService.create_task(
            db=db,
            plan_id=plan_id,
            organization_id=current_org,
            task_data=task_data.model_dump(),
            user_id=current_user["user_id"]
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans/{plan_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    plan_id: str,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org),
    workstream_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    assigned_to_id: Optional[str] = None,
    is_critical_path: Optional[bool] = None
):
    """List tasks for an integration plan"""
    query = db.query(IntegrationTask).filter(
        IntegrationTask.plan_id == plan_id,
        IntegrationTask.organization_id == current_org,
        IntegrationTask.deleted_at.is_(None)
    )

    if workstream_id:
        query = query.filter(IntegrationTask.workstream_id == workstream_id)

    if status:
        query = query.filter(IntegrationTask.status == status)

    if assigned_to_id:
        query = query.filter(IntegrationTask.assigned_to_id == assigned_to_id)

    if is_critical_path is not None:
        query = query.filter(IntegrationTask.is_critical_path == is_critical_path)

    tasks = query.order_by(IntegrationTask.due_date).all()
    return tasks


@router.patch("/tasks/{task_id}")
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org)
):
    """Update task status and completion"""
    try:
        task = await WorkstreamManagementService.update_task_status(
            db=db,
            task_id=task_id,
            organization_id=current_org,
            status=task_update.status,
            completion_percentage=task_update.completion_percentage,
            actual_hours=task_update.actual_hours
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Milestone Endpoints ====================

@router.get("/plans/{plan_id}/milestones")
async def list_milestones(
    plan_id: str,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org),
    phase: Optional[IntegrationPhase] = None,
    is_completed: Optional[bool] = None
):
    """List milestones for an integration plan"""
    query = db.query(IntegrationMilestone).filter(
        IntegrationMilestone.plan_id == plan_id,
        IntegrationMilestone.organization_id == current_org
    )

    if phase:
        query = query.filter(IntegrationMilestone.phase == phase)

    if is_completed is not None:
        query = query.filter(IntegrationMilestone.is_completed == is_completed)

    milestones = query.order_by(IntegrationMilestone.target_date).all()
    return milestones


# ==================== Cultural Assessment & Change Management ====================

@router.post("/plans/{plan_id}/cultural-assessments")
async def create_cultural_assessment(
    plan_id: str,
    assessment_data: CulturalAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    current_org: str = Depends(get_current_org)
):
    """Conduct and record cultural assessment"""
    try:
        assessment = await ChangeManagementService.conduct_cultural_assessment(
            db=db,
            plan_id=plan_id,
            organization_id=current_org,
            assessment_data=assessment_data.model_dump(),
            user_id=current_user["user_id"]
        )
        return assessment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans/{plan_id}/cultural-assessments")
async def list_cultural_assessments(
    plan_id: str,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org)
):
    """List cultural assessments for an integration plan"""
    assessments = db.query(CulturalAssessment).filter(
        CulturalAssessment.plan_id == plan_id,
        CulturalAssessment.organization_id == current_org
    ).order_by(CulturalAssessment.assessment_date.desc()).all()

    return assessments


@router.post("/plans/{plan_id}/change-initiatives")
async def create_change_initiative(
    plan_id: str,
    initiative_data: ChangeInitiativeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    current_org: str = Depends(get_current_org)
):
    """Create a new change management initiative"""
    try:
        initiative = await ChangeManagementService.create_change_initiative(
            db=db,
            plan_id=plan_id,
            organization_id=current_org,
            initiative_data=initiative_data.model_dump(),
            user_id=current_user["user_id"]
        )
        return initiative
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans/{plan_id}/change-initiatives")
async def list_change_initiatives(
    plan_id: str,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org),
    initiative_type: Optional[str] = None,
    status: Optional[str] = None
):
    """List change initiatives for an integration plan"""
    query = db.query(ChangeInitiative).filter(
        ChangeInitiative.plan_id == plan_id,
        ChangeInitiative.organization_id == current_org,
        ChangeInitiative.deleted_at.is_(None)
    )

    if initiative_type:
        query = query.filter(ChangeInitiative.initiative_type == initiative_type)

    if status:
        query = query.filter(ChangeInitiative.status == status)

    initiatives = query.all()
    return initiatives


# ==================== KPI & Performance Monitoring ====================

@router.post("/plans/{plan_id}/kpis")
async def create_kpi(
    plan_id: str,
    kpi_data: KPICreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    current_org: str = Depends(get_current_org)
):
    """Create a new integration KPI"""
    try:
        kpi = await PerformanceMonitoringService.create_kpi(
            db=db,
            plan_id=plan_id,
            organization_id=current_org,
            kpi_data=kpi_data.model_dump(),
            user_id=current_user["user_id"]
        )
        return kpi
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans/{plan_id}/kpis")
async def list_kpis(
    plan_id: str,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org),
    category: Optional[str] = None,
    workstream_id: Optional[str] = None,
    health_indicator: Optional[str] = None
):
    """List KPIs for an integration plan"""
    query = db.query(IntegrationKPI).filter(
        IntegrationKPI.plan_id == plan_id,
        IntegrationKPI.organization_id == current_org
    )

    if category:
        query = query.filter(IntegrationKPI.category == category)

    if workstream_id:
        query = query.filter(IntegrationKPI.workstream_id == workstream_id)

    if health_indicator:
        query = query.filter(IntegrationKPI.health_indicator == health_indicator)

    kpis = query.all()
    return kpis


@router.patch("/kpis/{kpi_id}/value")
async def update_kpi_value(
    kpi_id: str,
    kpi_update: KPIUpdate,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org)
):
    """Update KPI with new measurement"""
    try:
        kpi = await PerformanceMonitoringService.update_kpi_value(
            db=db,
            kpi_id=kpi_id,
            organization_id=current_org,
            current_value=kpi_update.current_value,
            measurement_date=kpi_update.measurement_date
        )
        return kpi
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Risk & Issue Management ====================

@router.post("/plans/{plan_id}/risks")
async def create_risk(
    plan_id: str,
    risk_data: RiskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    current_org: str = Depends(get_current_org)
):
    """Identify and create a new integration risk"""
    try:
        risk = await RiskManagementService.create_risk(
            db=db,
            plan_id=plan_id,
            organization_id=current_org,
            risk_data=risk_data.model_dump(),
            user_id=current_user["user_id"]
        )
        return risk
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans/{plan_id}/risks")
async def list_risks(
    plan_id: str,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org),
    severity: Optional[RiskSeverity] = None,
    status: Optional[str] = None,
    workstream_id: Optional[str] = None
):
    """List risks for an integration plan"""
    query = db.query(IntegrationRisk).filter(
        IntegrationRisk.plan_id == plan_id,
        IntegrationRisk.organization_id == current_org,
        IntegrationRisk.deleted_at.is_(None)
    )

    if severity:
        query = query.filter(IntegrationRisk.severity == severity)

    if status:
        query = query.filter(IntegrationRisk.status == status)

    if workstream_id:
        query = query.filter(IntegrationRisk.workstream_id == workstream_id)

    risks = query.order_by(IntegrationRisk.risk_score.desc()).all()
    return risks


@router.post("/plans/{plan_id}/issues")
async def create_issue(
    plan_id: str,
    issue_data: IssueCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    current_org: str = Depends(get_current_org)
):
    """Create a new integration issue"""
    try:
        issue = await RiskManagementService.create_issue(
            db=db,
            plan_id=plan_id,
            organization_id=current_org,
            issue_data=issue_data.model_dump(),
            user_id=current_user["user_id"]
        )
        return issue
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans/{plan_id}/issues")
async def list_issues(
    plan_id: str,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org),
    priority: Optional[IssuePriority] = None,
    status: Optional[str] = None,
    workstream_id: Optional[str] = None
):
    """List issues for an integration plan"""
    query = db.query(IntegrationIssue).filter(
        IntegrationIssue.plan_id == plan_id,
        IntegrationIssue.organization_id == current_org,
        IntegrationIssue.deleted_at.is_(None)
    )

    if priority:
        query = query.filter(IntegrationIssue.priority == priority)

    if status:
        query = query.filter(IntegrationIssue.status == status)

    if workstream_id:
        query = query.filter(IntegrationIssue.workstream_id == workstream_id)

    issues = query.order_by(IntegrationIssue.reported_date.desc()).all()
    return issues


# ==================== Dashboard & Analytics ====================

@router.get("/plans/{plan_id}/dashboard")
async def get_integration_dashboard(
    plan_id: str,
    db: Session = Depends(get_db),
    current_org: str = Depends(get_current_org)
):
    """Get comprehensive dashboard data for integration plan"""
    plan = db.query(IntegrationPlan).filter(
        IntegrationPlan.id == plan_id,
        IntegrationPlan.organization_id == current_org
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Integration plan not found")

    # Gather dashboard metrics
    dashboard = {
        "plan": plan,
        "milestones": {
            "total": plan.milestones_total,
            "completed": plan.milestones_completed,
            "completion_rate": (plan.milestones_completed / plan.milestones_total * 100) if plan.milestones_total > 0 else 0
        },
        "tasks": {
            "total": plan.tasks_total,
            "completed": plan.tasks_completed,
            "in_progress": db.query(IntegrationTask).filter(
                IntegrationTask.plan_id == plan_id,
                IntegrationTask.status == TaskStatus.IN_PROGRESS
            ).count(),
            "at_risk": db.query(IntegrationTask).filter(
                IntegrationTask.plan_id == plan_id,
                IntegrationTask.status == TaskStatus.AT_RISK
            ).count()
        },
        "synergies": {
            "total_target": plan.total_synergy_target,
            "total_realized": plan.synergy_realized,
            "capture_rate": plan.synergy_capture_rate,
            "count": db.query(SynergyOpportunity).filter(
                SynergyOpportunity.plan_id == plan_id
            ).count()
        },
        "budget": {
            "total": plan.total_budget,
            "spent": plan.budget_spent,
            "remaining": plan.budget_remaining,
            "utilization_rate": (plan.budget_spent / plan.total_budget * 100) if plan.total_budget > 0 else 0
        },
        "risks": {
            "critical": db.query(IntegrationRisk).filter(
                IntegrationRisk.plan_id == plan_id,
                IntegrationRisk.severity == RiskSeverity.CRITICAL,
                IntegrationRisk.status != "closed"
            ).count(),
            "high": db.query(IntegrationRisk).filter(
                IntegrationRisk.plan_id == plan_id,
                IntegrationRisk.severity == RiskSeverity.HIGH,
                IntegrationRisk.status != "closed"
            ).count(),
            "total_open": db.query(IntegrationRisk).filter(
                IntegrationRisk.plan_id == plan_id,
                IntegrationRisk.status != "closed"
            ).count()
        },
        "issues": {
            "urgent": db.query(IntegrationIssue).filter(
                IntegrationIssue.plan_id == plan_id,
                IntegrationIssue.priority == IssuePriority.URGENT,
                IntegrationIssue.status.in_(["open", "in_progress"])
            ).count(),
            "total_open": db.query(IntegrationIssue).filter(
                IntegrationIssue.plan_id == plan_id,
                IntegrationIssue.status.in_(["open", "in_progress"])
            ).count()
        },
        "health": {
            "status": plan.health_status,
            "is_on_track": plan.is_on_track,
            "overall_progress": plan.overall_progress_percentage,
            "current_phase": plan.current_phase.value if hasattr(plan.current_phase, 'value') else str(plan.current_phase)
        }
    }

    return dashboard
