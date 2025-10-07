"""
Deal Management API Endpoints
Comprehensive CRUD operations for M&A deals with tenant isolation
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from pydantic import BaseModel, Field, validator

from ..database import get_db
from ..models.deal import (
    Deal, DealStage, DealType, DealPriority,
    DealTeamMember, DealValuation, DealActivity, DealMilestone,
    DealDocument, DealFinancialModel
)
from ..auth.clerk_auth import ClerkUser, get_current_organization_user
from ..auth.tenant_isolation import get_tenant_query, TenantAwareQuery

router = APIRouter(prefix="/api/deals", tags=["deals"])

# Pydantic models
class DealCreate(BaseModel):
    """Deal creation model"""
    title: str = Field(..., min_length=1, max_length=255)
    code_name: Optional[str] = None
    deal_type: str = DealType.ACQUISITION.value
    stage: str = DealStage.SOURCING.value
    priority: str = DealPriority.MEDIUM.value

    # Target company
    target_company_name: str
    target_company_website: Optional[str] = None
    target_company_description: Optional[str] = None
    target_industry: Optional[str] = None
    target_country: Optional[str] = Field(None, max_length=2)
    target_employees: Optional[int] = None

    # Financial
    deal_value: Optional[Decimal] = None
    deal_currency: str = "USD"
    enterprise_value: Optional[Decimal] = None
    equity_value: Optional[Decimal] = None
    debt_assumed: Optional[Decimal] = None
    revenue_multiple: Optional[Decimal] = None
    ebitda_multiple: Optional[Decimal] = None
    target_revenue: Optional[Decimal] = None
    target_ebitda: Optional[Decimal] = None

    # Structure
    cash_consideration: Optional[Decimal] = None
    stock_consideration: Optional[Decimal] = None
    earnout_consideration: Optional[Decimal] = None
    ownership_percentage: Optional[Decimal] = Field(None, ge=0, le=100)

    # Dates
    initial_contact_date: Optional[date] = None
    expected_close_date: Optional[date] = None

    # Team
    deal_lead_id: Optional[str] = None

    # Tracking
    probability_of_close: int = Field(50, ge=0, le=100)
    risk_level: Optional[str] = None

    # Notes
    executive_summary: Optional[str] = None
    investment_thesis: Optional[str] = None
    key_risks: List[str] = []
    key_opportunities: List[str] = []
    next_steps: Optional[str] = None

    tags: List[str] = []


class DealUpdate(DealCreate):
    """Deal update model - all fields optional"""
    title: Optional[str] = None
    target_company_name: Optional[str] = None
    deal_currency: Optional[str] = None
    probability_of_close: Optional[int] = Field(None, ge=0, le=100)


class DealResponse(BaseModel):
    """Deal response model"""
    id: str
    deal_number: str
    title: str
    code_name: Optional[str]
    deal_type: str
    stage: str
    priority: str

    target_company_name: str
    target_company_website: Optional[str]
    target_industry: Optional[str]

    deal_value: Optional[Decimal]
    deal_currency: str
    enterprise_value: Optional[Decimal]

    probability_of_close: int
    risk_level: Optional[str]

    deal_lead_id: Optional[str]
    deal_lead_name: Optional[str]

    days_in_pipeline: int
    is_active: bool

    created_at: datetime
    updated_at: datetime

    team_member_count: int = 0
    document_count: int = 0
    activity_count: int = 0

    class Config:
        orm_mode = True


class DealStageUpdate(BaseModel):
    """Model for updating deal stage"""
    stage: str
    notes: Optional[str] = None


class DealTeamMemberAdd(BaseModel):
    """Model for adding team member"""
    user_id: str
    role: str
    responsibilities: Optional[str] = None
    time_allocation_percentage: Optional[int] = Field(None, ge=0, le=100)


class DealActivityCreate(BaseModel):
    """Model for creating deal activity"""
    activity_type: str
    subject: str
    description: Optional[str] = None
    participants: List[str] = []
    outcome: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[date] = None


class DealValuationCreate(BaseModel):
    """Model for creating deal valuation"""
    valuation_date: date
    valuation_method: str
    enterprise_value_low: Optional[Decimal] = None
    enterprise_value_mid: Optional[Decimal] = None
    enterprise_value_high: Optional[Decimal] = None
    assumptions: Dict[str, Any] = {}
    notes: Optional[str] = None


class DealAnalytics(BaseModel):
    """Deal analytics response"""
    total_deals: int
    active_deals: int
    total_pipeline_value: Decimal
    average_deal_size: Decimal
    average_days_to_close: int
    win_rate: float
    deals_by_stage: Dict[str, int]
    deals_by_priority: Dict[str, int]
    deals_by_industry: Dict[str, int]
    monthly_deal_flow: List[Dict[str, Any]]
    top_deal_leads: List[Dict[str, Any]]


# Endpoints
@router.get("/", response_model=List[DealResponse])
async def list_deals(
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    stage: Optional[str] = None,
    priority: Optional[str] = None,
    is_active: Optional[bool] = True,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|deal_value|probability_of_close)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    """List all deals with filtering and pagination"""
    query = tenant_query.query(Deal)

    # Apply filters
    if stage:
        query = query.filter(Deal.stage == stage)
    if priority:
        query = query.filter(Deal.priority == priority)
    if is_active is not None:
        query = query.filter(Deal.is_active == is_active)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Deal.title.ilike(search_term),
                Deal.target_company_name.ilike(search_term),
                Deal.deal_number.ilike(search_term),
                Deal.code_name.ilike(search_term)
            )
        )

    # Apply sorting
    order_column = getattr(Deal, sort_by)
    if sort_order == "desc":
        order_column = order_column.desc()
    query = query.order_by(order_column)

    # Execute query with pagination
    deals = query.offset(skip).limit(limit).all()

    # Convert to response model
    results = []
    for deal in deals:
        deal_dict = deal.to_dict()
        deal_dict['team_member_count'] = deal.team_members.count()
        deal_dict['document_count'] = deal.documents.count()
        deal_dict['activity_count'] = deal.activities.count()
        if deal.deal_lead:
            deal_dict['deal_lead_name'] = deal.deal_lead.display_name
        results.append(DealResponse(**deal_dict))

    return results


@router.post("/", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal_data: DealCreate,
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Create a new deal"""
    # Generate deal number
    org_deals = tenant_query.query(Deal).count()
    deal_number = f"D-{datetime.now().year}-{str(org_deals + 1).zfill(4)}"

    # Create deal
    deal_dict = deal_data.dict()
    deal_dict['deal_number'] = deal_number
    deal_dict['created_by'] = current_user.user_id
    deal_dict['key_risks'] = deal_dict.get('key_risks', [])
    deal_dict['key_opportunities'] = deal_dict.get('key_opportunities', [])
    deal_dict['tags'] = deal_dict.get('tags', [])

    deal = tenant_query.create(Deal, **deal_dict)

    # Add creator as team member
    if current_user.user_id:
        team_member = DealTeamMember(
            deal_id=deal.id,
            user_id=current_user.user_id,
            role="Deal Lead",
            organization_id=current_user.organization_id
        )
        db.add(team_member)
        db.commit()

    # Create initial activity
    activity = DealActivity(
        deal_id=deal.id,
        activity_type="deal_created",
        subject="Deal Created",
        description=f"Deal '{deal.title}' was created",
        organization_id=current_user.organization_id,
        created_by=current_user.user_id
    )
    db.add(activity)
    db.commit()

    deal_dict = deal.to_dict()
    deal_dict['team_member_count'] = 1
    deal_dict['document_count'] = 0
    deal_dict['activity_count'] = 1

    return DealResponse(**deal_dict)


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: str,
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    """Get a specific deal"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    deal_dict = deal.to_dict()
    deal_dict['team_member_count'] = deal.team_members.count()
    deal_dict['document_count'] = deal.documents.count()
    deal_dict['activity_count'] = deal.activities.count()
    if deal.deal_lead:
        deal_dict['deal_lead_name'] = deal.deal_lead.display_name

    return DealResponse(**deal_dict)


@router.patch("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: str,
    deal_update: DealUpdate,
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Update a deal"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    # Track stage change
    old_stage = deal.stage

    # Update fields
    update_data = deal_update.dict(exclude_unset=True)
    update_data['updated_by'] = current_user.user_id

    deal = tenant_query.update(Deal, deal_id, **update_data)

    # Log stage change activity
    if 'stage' in update_data and update_data['stage'] != old_stage:
        activity = DealActivity(
            deal_id=deal.id,
            activity_type="stage_change",
            subject="Stage Changed",
            description=f"Stage changed from {old_stage} to {update_data['stage']}",
            organization_id=current_user.organization_id,
            created_by=current_user.user_id
        )
        db.add(activity)
        db.commit()

    deal_dict = deal.to_dict()
    deal_dict['team_member_count'] = deal.team_members.count()
    deal_dict['document_count'] = deal.documents.count()
    deal_dict['activity_count'] = deal.activities.count()

    return DealResponse(**deal_dict)


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    deal_id: str,
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    """Soft delete a deal"""
    deal = tenant_query.get_or_404(Deal, deal_id)
    deal.soft_delete(deleted_by_id=current_user.user_id)
    tenant_query.db.commit()
    return None


@router.post("/{deal_id}/stage", response_model=DealResponse)
async def update_deal_stage(
    deal_id: str,
    stage_update: DealStageUpdate,
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Update deal stage with activity logging"""
    deal = tenant_query.get_or_404(Deal, deal_id)
    old_stage = deal.stage

    # Update stage
    deal.stage = stage_update.stage
    deal.updated_by = current_user.user_id

    # Create activity
    activity = DealActivity(
        deal_id=deal.id,
        activity_type="stage_change",
        subject=f"Stage: {old_stage} → {stage_update.stage}",
        description=stage_update.notes,
        organization_id=current_user.organization_id,
        created_by=current_user.user_id
    )
    db.add(activity)
    db.commit()

    deal_dict = deal.to_dict()
    return DealResponse(**deal_dict)


@router.get("/{deal_id}/team", response_model=List[Dict[str, Any]])
async def get_deal_team(
    deal_id: str,
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    """Get deal team members"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    team_members = []
    for member in deal.team_members.filter_by(is_active=True):
        team_members.append({
            "id": member.id,
            "user_id": member.user_id,
            "user_name": member.user.display_name if member.user else "Unknown",
            "user_email": member.user.email if member.user else None,
            "role": member.role,
            "responsibilities": member.responsibilities,
            "time_allocation_percentage": member.time_allocation_percentage,
            "added_date": member.added_date
        })

    return team_members


@router.post("/{deal_id}/team", status_code=status.HTTP_201_CREATED)
async def add_team_member(
    deal_id: str,
    team_member: DealTeamMemberAdd,
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Add team member to deal"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    # Check if already a member
    existing = db.query(DealTeamMember).filter(
        and_(
            DealTeamMember.deal_id == deal_id,
            DealTeamMember.user_id == team_member.user_id,
            DealTeamMember.is_active == True
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a team member"
        )

    # Add team member
    new_member = DealTeamMember(
        deal_id=deal_id,
        user_id=team_member.user_id,
        role=team_member.role,
        responsibilities=team_member.responsibilities,
        time_allocation_percentage=team_member.time_allocation_percentage,
        organization_id=current_user.organization_id
    )
    db.add(new_member)

    # Log activity
    activity = DealActivity(
        deal_id=deal_id,
        activity_type="team_member_added",
        subject="Team Member Added",
        description=f"Added {team_member.user_id} as {team_member.role}",
        organization_id=current_user.organization_id,
        created_by=current_user.user_id
    )
    db.add(activity)
    db.commit()

    return {"message": "Team member added successfully"}


@router.get("/{deal_id}/activities", response_model=List[Dict[str, Any]])
async def get_deal_activities(
    deal_id: str,
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """Get deal activity timeline"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    activities = deal.activities.offset(skip).limit(limit).all()

    results = []
    for activity in activities:
        results.append({
            "id": activity.id,
            "activity_type": activity.activity_type,
            "activity_date": activity.activity_date,
            "subject": activity.subject,
            "description": activity.description,
            "participants": activity.participants,
            "outcome": activity.outcome,
            "follow_up_required": activity.follow_up_required,
            "follow_up_date": activity.follow_up_date,
            "created_by": activity.created_by
        })

    return results


@router.post("/{deal_id}/activities", status_code=status.HTTP_201_CREATED)
async def create_deal_activity(
    deal_id: str,
    activity_data: DealActivityCreate,
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Create deal activity"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    activity = DealActivity(
        deal_id=deal_id,
        **activity_data.dict(),
        organization_id=current_user.organization_id,
        created_by=current_user.user_id
    )
    db.add(activity)
    db.commit()

    return {"message": "Activity created successfully", "id": activity.id}


@router.get("/{deal_id}/valuations", response_model=List[Dict[str, Any]])
async def get_deal_valuations(
    deal_id: str,
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    """Get deal valuation history"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    valuations = []
    for valuation in deal.valuations:
        valuations.append({
            "id": valuation.id,
            "valuation_date": valuation.valuation_date,
            "valuation_method": valuation.valuation_method,
            "enterprise_value_low": valuation.enterprise_value_low,
            "enterprise_value_mid": valuation.enterprise_value_mid,
            "enterprise_value_high": valuation.enterprise_value_high,
            "assumptions": valuation.assumptions,
            "notes": valuation.notes,
            "prepared_by": valuation.prepared_by.display_name if valuation.prepared_by else None
        })

    return valuations


@router.post("/{deal_id}/valuations", status_code=status.HTTP_201_CREATED)
async def create_deal_valuation(
    deal_id: str,
    valuation_data: DealValuationCreate,
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Create deal valuation"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    valuation = DealValuation(
        deal_id=deal_id,
        **valuation_data.dict(),
        prepared_by_id=current_user.user_id,
        organization_id=current_user.organization_id,
        created_by=current_user.user_id
    )
    db.add(valuation)
    db.commit()

    return {"message": "Valuation created successfully", "id": valuation.id}


@router.get("/analytics/summary", response_model=DealAnalytics)
async def get_deal_analytics(
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Get deal analytics and insights"""
    # Base query
    query = tenant_query.query(Deal)

    # Calculate metrics
    total_deals = query.count()
    active_deals = query.filter(Deal.is_active == True).count()

    # Pipeline value
    pipeline_value = query.filter(
        Deal.is_active == True
    ).with_entities(func.sum(Deal.deal_value)).scalar() or Decimal('0')

    # Average deal size
    avg_deal_size = query.filter(
        Deal.deal_value.isnot(None)
    ).with_entities(func.avg(Deal.deal_value)).scalar() or Decimal('0')

    # Win rate
    closed_deals = query.filter(
        Deal.stage.in_([DealStage.CLOSED_WON.value, DealStage.CLOSED_LOST.value])
    ).count()

    won_deals = query.filter(
        Deal.stage == DealStage.CLOSED_WON.value
    ).count()

    win_rate = (won_deals / closed_deals * 100) if closed_deals > 0 else 0

    # Deals by stage
    deals_by_stage = {}
    for stage in DealStage:
        count = query.filter(Deal.stage == stage.value).count()
        deals_by_stage[stage.value] = count

    # Deals by priority
    deals_by_priority = {}
    for priority in DealPriority:
        count = query.filter(Deal.priority == priority.value).count()
        deals_by_priority[priority.value] = count

    # Deals by industry
    industry_stats = query.filter(
        Deal.target_industry.isnot(None)
    ).with_entities(
        Deal.target_industry,
        func.count(Deal.id)
    ).group_by(Deal.target_industry).all()

    deals_by_industry = {industry: count for industry, count in industry_stats}

    # Monthly deal flow (last 12 months)
    monthly_deal_flow = []
    for i in range(11, -1, -1):
        month_start = datetime.now().replace(day=1) - timedelta(days=i * 30)
        month_end = (month_start + timedelta(days=32)).replace(day=1)

        count = query.filter(
            and_(
                Deal.created_at >= month_start,
                Deal.created_at < month_end
            )
        ).count()

        monthly_deal_flow.append({
            "month": month_start.strftime("%Y-%m"),
            "count": count
        })

    # Top deal leads
    lead_stats = query.filter(
        Deal.deal_lead_id.isnot(None)
    ).with_entities(
        Deal.deal_lead_id,
        func.count(Deal.id),
        func.sum(Deal.deal_value)
    ).group_by(Deal.deal_lead_id).order_by(
        func.count(Deal.id).desc()
    ).limit(5).all()

    top_deal_leads = [
        {"user_id": lead_id, "deal_count": count, "total_value": value or 0}
        for lead_id, count, value in lead_stats
    ]

    # Average days to close
    closed_deals_with_dates = query.filter(
        and_(
            Deal.stage == DealStage.CLOSED_WON.value,
            Deal.initial_contact_date.isnot(None),
            Deal.actual_close_date.isnot(None)
        )
    ).all()

    if closed_deals_with_dates:
        total_days = sum(d.days_in_pipeline for d in closed_deals_with_dates)
        avg_days_to_close = total_days // len(closed_deals_with_dates)
    else:
        avg_days_to_close = 0

    return DealAnalytics(
        total_deals=total_deals,
        active_deals=active_deals,
        total_pipeline_value=pipeline_value,
        average_deal_size=avg_deal_size,
        average_days_to_close=avg_days_to_close,
        win_rate=win_rate,
        deals_by_stage=deals_by_stage,
        deals_by_priority=deals_by_priority,
        deals_by_industry=deals_by_industry,
        monthly_deal_flow=monthly_deal_flow,
        top_deal_leads=top_deal_leads
    )


# Milestone Management Endpoints

class DealMilestoneCreate(BaseModel):
    """Model for creating deal milestone"""
    title: str
    description: Optional[str] = None
    milestone_type: Optional[str] = None
    target_date: date
    owner_id: Optional[str] = None
    is_critical: bool = False
    dependencies: List[str] = []


class DealMilestoneUpdate(BaseModel):
    """Model for updating deal milestone"""
    title: Optional[str] = None
    description: Optional[str] = None
    milestone_type: Optional[str] = None
    target_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    status: Optional[str] = None
    owner_id: Optional[str] = None
    completion_notes: Optional[str] = None
    is_critical: Optional[bool] = None


@router.get("/{deal_id}/milestones", response_model=List[Dict[str, Any]])
async def get_deal_milestones(
    deal_id: str,
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    status: Optional[str] = None
):
    """Get deal milestones"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    query = deal.milestones
    if status:
        query = query.filter(DealMilestone.status == status)

    milestones = query.all()

    results = []
    for milestone in milestones:
        results.append({
            "id": milestone.id,
            "title": milestone.title,
            "description": milestone.description,
            "milestone_type": milestone.milestone_type,
            "target_date": milestone.target_date,
            "actual_completion_date": milestone.actual_completion_date,
            "status": milestone.status,
            "owner_id": milestone.owner_id,
            "owner_name": milestone.owner.display_name if milestone.owner else None,
            "completion_notes": milestone.completion_notes,
            "is_critical": milestone.is_critical,
            "is_overdue": milestone.is_overdue,
            "dependencies": milestone.dependencies,
            "created_at": milestone.created_at
        })

    return results


@router.post("/{deal_id}/milestones", status_code=status.HTTP_201_CREATED)
async def create_deal_milestone(
    deal_id: str,
    milestone_data: DealMilestoneCreate,
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Create deal milestone"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    milestone = DealMilestone(
        deal_id=deal_id,
        **milestone_data.dict(),
        organization_id=current_user.organization_id,
        created_by=current_user.user_id
    )
    db.add(milestone)

    # Log activity
    activity = DealActivity(
        deal_id=deal_id,
        activity_type="milestone_created",
        subject=f"Milestone Created: {milestone_data.title}",
        description=f"Target date: {milestone_data.target_date}",
        organization_id=current_user.organization_id,
        created_by=current_user.user_id
    )
    db.add(activity)
    db.commit()

    return {"message": "Milestone created successfully", "id": milestone.id}


@router.patch("/{deal_id}/milestones/{milestone_id}")
async def update_deal_milestone(
    deal_id: str,
    milestone_id: str,
    milestone_update: DealMilestoneUpdate,
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Update deal milestone"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    milestone = db.query(DealMilestone).filter(
        and_(
            DealMilestone.id == milestone_id,
            DealMilestone.deal_id == deal_id,
            DealMilestone.organization_id == current_user.organization_id
        )
    ).first()

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    # Update fields
    update_data = milestone_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(milestone, key, value)

    milestone.updated_by = current_user.user_id

    # Log if completed
    if update_data.get('status') == 'completed' or update_data.get('actual_completion_date'):
        activity = DealActivity(
            deal_id=deal_id,
            activity_type="milestone_completed",
            subject=f"Milestone Completed: {milestone.title}",
            description=milestone_update.completion_notes,
            organization_id=current_user.organization_id,
            created_by=current_user.user_id
        )
        db.add(activity)

    db.commit()

    return {"message": "Milestone updated successfully"}


@router.delete("/{deal_id}/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal_milestone(
    deal_id: str,
    milestone_id: str,
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Delete deal milestone"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    milestone = db.query(DealMilestone).filter(
        and_(
            DealMilestone.id == milestone_id,
            DealMilestone.deal_id == deal_id,
            DealMilestone.organization_id == current_user.organization_id
        )
    ).first()

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    milestone.soft_delete(deleted_by_id=current_user.user_id)
    db.commit()

    return None


# Document Management Endpoints

class DealDocumentCreate(BaseModel):
    """Model for creating deal document"""
    title: str
    description: Optional[str] = None
    category: str
    file_name: str
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    version: str = "1.0"
    is_confidential: bool = True
    access_level: str = "team"
    tags: List[str] = []


@router.get("/{deal_id}/documents", response_model=List[Dict[str, Any]])
async def get_deal_documents(
    deal_id: str,
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """Get deal documents"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    query = deal.documents
    if category:
        query = query.filter(DealDocument.category == category)

    documents = query.offset(skip).limit(limit).all()

    results = []
    for doc in documents:
        results.append({
            "id": doc.id,
            "title": doc.title,
            "description": doc.description,
            "category": doc.category,
            "file_name": doc.file_name,
            "file_path": doc.file_path,
            "file_url": doc.file_url,
            "file_size": doc.file_size,
            "file_type": doc.file_type,
            "version": doc.version,
            "is_confidential": doc.is_confidential,
            "access_level": doc.access_level,
            "tags": doc.tags,
            "uploaded_by": doc.uploaded_by.display_name if doc.uploaded_by else None,
            "upload_date": doc.upload_date,
            "reviewed_by": doc.reviewed_by.display_name if doc.reviewed_by else None,
            "review_date": doc.review_date,
            "created_at": doc.created_at
        })

    return results


@router.post("/{deal_id}/documents", status_code=status.HTTP_201_CREATED)
async def create_deal_document(
    deal_id: str,
    document_data: DealDocumentCreate,
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Create deal document record (file upload handled separately)"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    document = DealDocument(
        deal_id=deal_id,
        **document_data.dict(),
        uploaded_by_id=current_user.user_id,
        organization_id=current_user.organization_id,
        created_by=current_user.user_id
    )
    db.add(document)

    # Log activity
    activity = DealActivity(
        deal_id=deal_id,
        activity_type="document_uploaded",
        subject=f"Document Uploaded: {document_data.title}",
        description=f"Category: {document_data.category}",
        organization_id=current_user.organization_id,
        created_by=current_user.user_id
    )
    db.add(activity)
    db.commit()

    return {"message": "Document created successfully", "id": document.id}


@router.delete("/{deal_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal_document(
    deal_id: str,
    document_id: str,
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Delete deal document"""
    deal = tenant_query.get_or_404(Deal, deal_id)

    document = db.query(DealDocument).filter(
        and_(
            DealDocument.id == document_id,
            DealDocument.deal_id == deal_id,
            DealDocument.organization_id == current_user.organization_id
        )
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    document.soft_delete(deleted_by_id=current_user.user_id)
    db.commit()

    return None


# Deal Comparison Endpoint

@router.post("/compare")
async def compare_deals(
    deal_ids: List[str],
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Compare multiple deals side by side"""
    if len(deal_ids) < 2 or len(deal_ids) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select between 2 and 5 deals to compare"
        )

    deals = []
    for deal_id in deal_ids:
        deal = tenant_query.get_or_404(Deal, deal_id)
        deal_dict = deal.to_dict()

        # Add aggregated data
        deal_dict['team_member_count'] = deal.team_members.count()
        deal_dict['document_count'] = deal.documents.count()
        deal_dict['activity_count'] = deal.activities.count()
        deal_dict['milestone_count'] = deal.milestones.count()
        deal_dict['valuation_count'] = deal.valuations.count()

        # Latest valuation
        latest_valuation = deal.valuations.first()
        if latest_valuation:
            deal_dict['latest_valuation'] = {
                "method": latest_valuation.valuation_method,
                "ev_mid": latest_valuation.enterprise_value_mid,
                "date": latest_valuation.valuation_date
            }

        deals.append(deal_dict)

    return {
        "deals": deals,
        "comparison_date": datetime.utcnow(),
        "compared_by": current_user.user_id
    }