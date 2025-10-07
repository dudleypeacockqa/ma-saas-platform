"""
Opportunities API Routes
Endpoints for M&A opportunity discovery, scoring, and pipeline management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..core.database import get_db
from ..auth.clerk_auth import get_current_user, ClerkUser
from ..services.deal_sourcing import (
    OpportunityDiscoveryService,
    OpportunityScoringService,
    OpportunityManagementService
)
from ..models.opportunities import (
    MarketOpportunity, OpportunityScore, OpportunityActivity,
    OpportunityStatus, CompanyRegion, IndustryVertical,
    SourceType, ActivityType
)

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


# ============================================================================
# Request/Response Models
# ============================================================================

class OpportunityCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    region: CompanyRegion
    industry_vertical: IndustryVertical
    company_registration_number: Optional[str] = None
    website: Optional[str] = None
    annual_revenue: Optional[float] = None
    ebitda: Optional[float] = None
    employee_count: Optional[int] = None
    source_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class OpportunityUpdate(BaseModel):
    status: Optional[OpportunityStatus] = None
    notes: Optional[str] = None
    annual_revenue: Optional[float] = None
    ebitda: Optional[float] = None
    employee_count: Optional[int] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class OpportunityResponse(BaseModel):
    id: str
    organization_id: str
    company_name: str
    region: CompanyRegion
    industry_vertical: IndustryVertical
    status: OpportunityStatus
    overall_score: Optional[float]
    financial_health_score: Optional[float]
    strategic_fit_score: Optional[float]
    annual_revenue: Optional[float]
    ebitda: Optional[float]
    employee_count: Optional[int]
    source_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ScanRequest(BaseModel):
    region: CompanyRegion
    industry_sic: Optional[str] = None
    industry_vertical: Optional[IndustryVertical] = None
    min_age_years: int = Field(default=3, ge=1, le=50)
    cik_list: Optional[List[str]] = None


class ScoreRequest(BaseModel):
    company_data: Dict[str, Any] = Field(
        ...,
        description="Company financial and operational data for scoring"
    )


class ConvertToDealRequest(BaseModel):
    deal_data: Optional[Dict[str, Any]] = None


class OpportunityScoreResponse(BaseModel):
    id: str
    opportunity_id: str
    overall_score: float
    financial_health_score: float
    growth_trajectory_score: float
    strategic_fit_score: float
    market_position_score: float
    risk_assessment_score: float
    ai_insights: Dict[str, Any]
    confidence_level: float
    scored_at: datetime

    class Config:
        from_attributes = True


class ActivityResponse(BaseModel):
    id: str
    opportunity_id: str
    user_id: str
    activity_type: ActivityType
    description: str
    metadata: Optional[Dict[str, Any]]
    occurred_at: datetime

    class Config:
        from_attributes = True


class PipelineMetricsResponse(BaseModel):
    total_opportunities: int
    status_breakdown: Dict[str, int]
    average_score: float
    qualified_count: int
    conversion_rate: float
    new_this_week: int


class ROIProjectionRequest(BaseModel):
    purchase_price: float = Field(..., gt=0)
    annual_revenue: float = Field(..., gt=0)
    ebitda: float
    growth_rate: float = Field(default=0.05, ge=-0.5, le=2.0)
    exit_multiple: float = Field(default=5.0, ge=1.0, le=20.0)
    hold_period_years: int = Field(default=5, ge=1, le=15)


# ============================================================================
# Opportunity Management Endpoints
# ============================================================================

@router.post("/", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opportunity: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Create a new M&A opportunity manually

    Creates a new opportunity record in the pipeline for tracking and analysis.
    """
    service = OpportunityManagementService(db)

    company_data = opportunity.model_dump()

    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required"
        )

    result = service.create_opportunity(
        organization_id=current_user.organization_id,
        company_data=company_data,
        user_id=current_user.user_id
    )

    return result


@router.get("/", response_model=List[OpportunityResponse])
async def list_opportunities(
    status: Optional[List[OpportunityStatus]] = Query(None),
    region: Optional[CompanyRegion] = None,
    industry_vertical: Optional[List[IndustryVertical]] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    max_score: Optional[float] = Query(None, ge=0, le=100),
    min_revenue: Optional[float] = Query(None, ge=0),
    max_revenue: Optional[float] = Query(None, ge=0),
    search: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(created_at|overall_score|annual_revenue|company_name)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    List and filter M&A opportunities

    Supports advanced filtering, searching, sorting, and pagination.
    """
    service = OpportunityManagementService(db)

    filters = {
        "status": status,
        "region": region,
        "industry_vertical": industry_vertical,
        "min_score": min_score,
        "max_score": max_score,
        "min_revenue": min_revenue,
        "max_revenue": max_revenue,
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "limit": limit,
        "offset": offset
    }

    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}

    opportunities = service.filter_opportunities(
        organization_id=tenant_id,
        filters=filters
    )

    return opportunities


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get a specific opportunity by ID

    Returns detailed information about a single opportunity.
    """
    opportunity = db.query(MarketOpportunity).filter(
        MarketOpportunity.id == opportunity_id,
        MarketOpportunity.organization_id == tenant_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )

    return opportunity


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: str,
    update: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Update an opportunity

    Update opportunity details including status, financials, and contact information.
    """
    service = OpportunityManagementService(db)

    # Verify opportunity exists and belongs to tenant
    opportunity = db.query(MarketOpportunity).filter(
        MarketOpportunity.id == opportunity_id,
        MarketOpportunity.organization_id == tenant_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )

    # Update status if provided
    if update.status:
        opportunity = service.update_opportunity_status(
            opportunity_id=opportunity_id,
            status=update.status,
            user_id=current_user["id"],
            notes=update.notes
        )

    # Update other fields
    update_data = update.model_dump(exclude_unset=True, exclude={"status", "notes"})
    for field, value in update_data.items():
        setattr(opportunity, field, value)

    db.commit()
    db.refresh(opportunity)

    return opportunity


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Delete an opportunity (soft delete)

    Marks the opportunity as deleted without removing from database.
    """
    opportunity = db.query(MarketOpportunity).filter(
        MarketOpportunity.id == opportunity_id,
        MarketOpportunity.organization_id == tenant_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )

    # Soft delete
    opportunity.deleted_at = datetime.utcnow()
    db.commit()

    return None


# ============================================================================
# Discovery & Scanning Endpoints
# ============================================================================

@router.post("/scan/companies-house", response_model=List[OpportunityResponse])
async def scan_companies_house(
    scan_request: ScanRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Scan Companies House for UK opportunities

    Discovers new M&A opportunities from Companies House public data.
    Looks for distressed companies, late filings, and other acquisition signals.
    """
    if scan_request.region != CompanyRegion.UK:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Companies House scan only supports UK region"
        )

    service = OpportunityDiscoveryService(db)

    filters = {
        "industry_sic": scan_request.industry_sic or "62",
        "min_age_years": scan_request.min_age_years
    }

    opportunities = await service.scan_companies_house(
        organization_id=tenant_id,
        filters=filters
    )

    return opportunities


@router.post("/scan/sec-edgar", response_model=List[OpportunityResponse])
async def scan_sec_edgar(
    scan_request: ScanRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Scan SEC EDGAR for US opportunities

    Discovers new M&A opportunities from SEC public filings.
    Analyzes 10-K filings, financials, and company fundamentals.
    """
    if scan_request.region != CompanyRegion.US:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SEC EDGAR scan only supports US region"
        )

    if not scan_request.cik_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cik_list is required for SEC EDGAR scan"
        )

    service = OpportunityDiscoveryService(db)

    filters = {
        "cik_list": scan_request.cik_list
    }

    opportunities = await service.scan_sec_edgar(
        organization_id=tenant_id,
        filters=filters
    )

    return opportunities


@router.post("/scan/distressed", response_model=List[OpportunityResponse])
async def identify_distressed_companies(
    region: CompanyRegion,
    industry: IndustryVertical,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Identify financially distressed companies

    Scans for companies showing distress signals such as late filings,
    declining revenue, or high debt ratios.
    """
    service = OpportunityDiscoveryService(db)

    opportunities = await service.identify_distressed_companies(
        organization_id=tenant_id,
        industry=industry.value,
        region=region
    )

    return opportunities


# ============================================================================
# Scoring & Analysis Endpoints
# ============================================================================

@router.post("/{opportunity_id}/score", response_model=OpportunityScoreResponse)
async def score_opportunity(
    opportunity_id: str,
    score_request: ScoreRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Calculate AI-powered opportunity score

    Analyzes financial health, growth trajectory, strategic fit, market position,
    and risk factors to generate a comprehensive opportunity score (0-100).
    """
    # Verify opportunity exists
    opportunity = db.query(MarketOpportunity).filter(
        MarketOpportunity.id == opportunity_id,
        MarketOpportunity.organization_id == tenant_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )

    service = OpportunityScoringService(db)

    score = await service.calculate_opportunity_score(
        opportunity_id=opportunity_id,
        company_data=score_request.company_data
    )

    return score


@router.get("/{opportunity_id}/score", response_model=OpportunityScoreResponse)
async def get_opportunity_score(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get existing opportunity score

    Returns the most recent scoring analysis for an opportunity.
    """
    # Verify opportunity belongs to tenant
    opportunity = db.query(MarketOpportunity).filter(
        MarketOpportunity.id == opportunity_id,
        MarketOpportunity.organization_id == tenant_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )

    score = db.query(OpportunityScore).filter(
        OpportunityScore.opportunity_id == opportunity_id
    ).order_by(OpportunityScore.scored_at.desc()).first()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No score found for opportunity {opportunity_id}"
        )

    return score


@router.post("/roi-projection", response_model=Dict[str, Any])
async def calculate_roi_projection(
    roi_request: ROIProjectionRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Calculate ROI projection for potential deal

    Estimates ROI percentage, IRR, and payback period based on deal assumptions.
    """
    service = OpportunityScoringService(db)

    projection = await service.estimate_roi_projection(
        assumptions=roi_request.model_dump()
    )

    return projection


# ============================================================================
# Pipeline Management Endpoints
# ============================================================================

@router.post("/{opportunity_id}/convert-to-deal", response_model=Dict[str, str])
async def convert_opportunity_to_deal(
    opportunity_id: str,
    convert_request: ConvertToDealRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Convert qualified opportunity to active deal

    Promotes an opportunity from the pipeline to an active deal for execution.
    """
    # Verify opportunity exists and is qualified
    opportunity = db.query(MarketOpportunity).filter(
        MarketOpportunity.id == opportunity_id,
        MarketOpportunity.organization_id == tenant_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )

    if opportunity.status not in [OpportunityStatus.QUALIFIED, OpportunityStatus.IN_DISCUSSION]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Opportunity must be in QUALIFIED or IN_DISCUSSION status to convert. Current status: {opportunity.status.value}"
        )

    service = OpportunityManagementService(db)

    deal_id = service.convert_to_deal(
        opportunity_id=opportunity_id,
        user_id=current_user["id"],
        deal_data=convert_request.deal_data
    )

    return {
        "opportunity_id": opportunity_id,
        "deal_id": deal_id,
        "message": "Opportunity successfully converted to deal"
    }


@router.get("/{opportunity_id}/timeline", response_model=List[ActivityResponse])
async def get_opportunity_timeline(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get activity timeline for opportunity

    Returns chronological list of all activities and status changes.
    """
    # Verify opportunity exists
    opportunity = db.query(MarketOpportunity).filter(
        MarketOpportunity.id == opportunity_id,
        MarketOpportunity.organization_id == tenant_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )

    service = OpportunityManagementService(db)
    activities = service.get_opportunity_timeline(opportunity_id)

    return activities


@router.get("/metrics/pipeline", response_model=PipelineMetricsResponse)
async def get_pipeline_metrics(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get pipeline metrics and analytics

    Returns aggregated statistics about the opportunity pipeline including
    status breakdown, conversion rates, and average scores.
    """
    service = OpportunityManagementService(db)
    metrics = service.get_pipeline_metrics(organization_id=tenant_id)

    return metrics
