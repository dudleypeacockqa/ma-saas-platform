from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from ..core.database import get_db
from ..auth.clerk_auth import get_current_user, require_role
from ..models.deal_discovery import (
    Company, DealOpportunity, FinancialSnapshot,
    DealActivity, OpportunityEvaluation, MarketIntelligence,
    IndustryCategory, DealStage, FinancialHealth, OpportunitySource
)
from ..services.deal_screening import DealScreeningService
from ..schemas.deal_discovery import (
    CompanyCreate, CompanyUpdate, CompanyResponse,
    DealOpportunityCreate, DealOpportunityUpdate, DealOpportunityResponse,
    FinancialSnapshotCreate, FinancialSnapshotResponse,
    DealActivityCreate, DealActivityResponse,
    OpportunityEvaluationCreate, OpportunityEvaluationResponse,
    ScreeningFilters, OpportunityScoring, RankedOpportunity
)

router = APIRouter(prefix="/api/deal-discovery", tags=["Deal Discovery"])


@router.post("/companies", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new company for tracking"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    db_company = Company(
        tenant_id=uuid.UUID(tenant_id),
        **company.dict()
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)

    return db_company


@router.get("/companies", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    industry: Optional[IndustryCategory] = None,
    country: Optional[str] = None,
    revenue_min: Optional[float] = None,
    revenue_max: Optional[float] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List companies with optional filters"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    query = db.query(Company).filter(Company.tenant_id == uuid.UUID(tenant_id))

    if industry:
        query = query.filter(Company.industry == industry)
    if country:
        query = query.filter(Company.country == country)
    if revenue_min is not None:
        query = query.filter(Company.revenue_range_min >= revenue_min)
    if revenue_max is not None:
        query = query.filter(Company.revenue_range_max <= revenue_max)

    companies = query.offset(skip).limit(limit).all()
    return companies


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific company by ID"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    company = db.query(Company).filter(
        Company.id == company_id,
        Company.tenant_id == uuid.UUID(tenant_id)
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company


@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: uuid.UUID,
    company_update: CompanyUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update company information"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    company = db.query(Company).filter(
        Company.id == company_id,
        Company.tenant_id == uuid.UUID(tenant_id)
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    for key, value in company_update.dict(exclude_unset=True).items():
        setattr(company, key, value)

    company.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(company)

    return company


@router.post("/opportunities", response_model=DealOpportunityResponse)
async def create_opportunity(
    opportunity: DealOpportunityCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new deal opportunity"""
    tenant_id = current_user.get("tenant_id")
    user_id = current_user.get("user_id")

    if not tenant_id or not user_id:
        raise HTTPException(status_code=400, detail="User information incomplete")

    db_opportunity = DealOpportunity(
        tenant_id=uuid.UUID(tenant_id),
        user_id=user_id,
        **opportunity.dict()
    )
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)

    return db_opportunity


@router.get("/opportunities", response_model=List[DealOpportunityResponse])
async def list_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    stage: Optional[DealStage] = None,
    priority: Optional[int] = Query(None, ge=1, le=5),
    is_active: bool = Query(True),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List deal opportunities with filters"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    query = db.query(DealOpportunity).filter(
        DealOpportunity.tenant_id == uuid.UUID(tenant_id)
    )

    if stage:
        query = query.filter(DealOpportunity.stage == stage)
    if priority is not None:
        query = query.filter(DealOpportunity.priority == priority)
    query = query.filter(DealOpportunity.is_active == is_active)

    opportunities = query.offset(skip).limit(limit).all()
    return opportunities


@router.get("/opportunities/{opportunity_id}", response_model=DealOpportunityResponse)
async def get_opportunity(
    opportunity_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific opportunity"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    opportunity = db.query(DealOpportunity).filter(
        DealOpportunity.id == opportunity_id,
        DealOpportunity.tenant_id == uuid.UUID(tenant_id)
    ).first()

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    return opportunity


@router.put("/opportunities/{opportunity_id}", response_model=DealOpportunityResponse)
async def update_opportunity(
    opportunity_id: uuid.UUID,
    opportunity_update: DealOpportunityUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update opportunity information"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    opportunity = db.query(DealOpportunity).filter(
        DealOpportunity.id == opportunity_id,
        DealOpportunity.tenant_id == uuid.UUID(tenant_id)
    ).first()

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    for key, value in opportunity_update.dict(exclude_unset=True).items():
        setattr(opportunity, key, value)

    opportunity.updated_at = datetime.utcnow()
    opportunity.last_activity_date = datetime.utcnow()
    db.commit()
    db.refresh(opportunity)

    return opportunity


@router.patch("/opportunities/{opportunity_id}/stage")
async def update_opportunity_stage(
    opportunity_id: uuid.UUID,
    stage: DealStage = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the stage of an opportunity"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    opportunity = db.query(DealOpportunity).filter(
        DealOpportunity.id == opportunity_id,
        DealOpportunity.tenant_id == uuid.UUID(tenant_id)
    ).first()

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    opportunity.stage = stage
    opportunity.last_activity_date = datetime.utcnow()

    # Update relevant dates based on stage
    if stage == DealStage.INITIAL_REVIEW and not opportunity.first_contact_date:
        opportunity.first_contact_date = datetime.utcnow()
    elif stage == DealStage.COMPLETED and not opportunity.actual_closing_date:
        opportunity.actual_closing_date = datetime.utcnow()

    db.commit()

    return {"message": f"Opportunity stage updated to {stage.value}"}


@router.post("/opportunities/{opportunity_id}/activities", response_model=DealActivityResponse)
async def create_activity(
    opportunity_id: uuid.UUID,
    activity: DealActivityCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log an activity for an opportunity"""
    tenant_id = current_user.get("tenant_id")
    user_id = current_user.get("user_id")

    if not tenant_id or not user_id:
        raise HTTPException(status_code=400, detail="User information incomplete")

    # Verify opportunity exists and belongs to tenant
    opportunity = db.query(DealOpportunity).filter(
        DealOpportunity.id == opportunity_id,
        DealOpportunity.tenant_id == uuid.UUID(tenant_id)
    ).first()

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    db_activity = DealActivity(
        opportunity_id=opportunity_id,
        tenant_id=uuid.UUID(tenant_id),
        user_id=user_id,
        **activity.dict()
    )
    db.add(db_activity)

    # Update opportunity's last activity date
    opportunity.last_activity_date = datetime.utcnow()

    db.commit()
    db.refresh(db_activity)

    return db_activity


@router.get("/opportunities/{opportunity_id}/activities", response_model=List[DealActivityResponse])
async def list_activities(
    opportunity_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List activities for an opportunity"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    # Verify opportunity exists and belongs to tenant
    opportunity = db.query(DealOpportunity).filter(
        DealOpportunity.id == opportunity_id,
        DealOpportunity.tenant_id == uuid.UUID(tenant_id)
    ).first()

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    activities = db.query(DealActivity).filter(
        DealActivity.opportunity_id == opportunity_id
    ).order_by(DealActivity.activity_date.desc()).offset(skip).limit(limit).all()

    return activities


@router.post("/opportunities/{opportunity_id}/evaluate", response_model=OpportunityEvaluationResponse)
async def create_evaluation(
    opportunity_id: uuid.UUID,
    evaluation: OpportunityEvaluationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an evaluation for an opportunity"""
    tenant_id = current_user.get("tenant_id")
    user_id = current_user.get("user_id")

    if not tenant_id or not user_id:
        raise HTTPException(status_code=400, detail="User information incomplete")

    # Verify opportunity exists and belongs to tenant
    opportunity = db.query(DealOpportunity).filter(
        DealOpportunity.id == opportunity_id,
        DealOpportunity.tenant_id == uuid.UUID(tenant_id)
    ).first()

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    db_evaluation = OpportunityEvaluation(
        opportunity_id=opportunity_id,
        tenant_id=uuid.UUID(tenant_id),
        evaluator_id=user_id,
        **evaluation.dict()
    )
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)

    return db_evaluation


@router.post("/companies/{company_id}/financials", response_model=FinancialSnapshotResponse)
async def create_financial_snapshot(
    company_id: uuid.UUID,
    snapshot: FinancialSnapshotCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a financial snapshot for a company"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    # Verify company exists and belongs to tenant
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.tenant_id == uuid.UUID(tenant_id)
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    db_snapshot = FinancialSnapshot(
        company_id=company_id,
        tenant_id=uuid.UUID(tenant_id),
        **snapshot.dict()
    )
    db.add(db_snapshot)

    # Update company's latest financial metrics
    company.ebitda = snapshot.ebitda
    company.ebitda_margin = snapshot.ebitda_margin
    company.growth_rate = snapshot.revenue_growth
    company.last_data_refresh = datetime.utcnow()

    db.commit()
    db.refresh(db_snapshot)

    return db_snapshot


@router.get("/companies/{company_id}/financials", response_model=List[FinancialSnapshotResponse])
async def list_financial_snapshots(
    company_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List financial snapshots for a company"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    # Verify company exists and belongs to tenant
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.tenant_id == uuid.UUID(tenant_id)
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    snapshots = db.query(FinancialSnapshot).filter(
        FinancialSnapshot.company_id == company_id
    ).order_by(FinancialSnapshot.year.desc(), FinancialSnapshot.quarter.desc()).all()

    return snapshots


@router.post("/screen/companies", response_model=List[CompanyResponse])
async def screen_companies(
    filters: ScreeningFilters = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Screen companies based on criteria"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    screening_service = DealScreeningService(db)
    companies = screening_service.screen_companies(
        tenant_id=uuid.UUID(tenant_id),
        filters=filters.dict(exclude_unset=True)
    )

    return companies


@router.get("/screen/distressed", response_model=List[CompanyResponse])
async def find_distressed_companies(
    min_current_ratio: float = Query(1.0),
    max_debt_to_equity: float = Query(3.0),
    min_ebitda_margin: float = Query(0.05),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Find companies showing signs of distress"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    screening_service = DealScreeningService(db)
    companies = screening_service.identify_distressed_companies(
        tenant_id=uuid.UUID(tenant_id),
        threshold_metrics={
            'min_current_ratio': min_current_ratio,
            'max_debt_to_equity': max_debt_to_equity,
            'min_ebitda_margin': min_ebitda_margin,
            'negative_growth': True
        }
    )

    return companies


@router.get("/screen/succession", response_model=List[DealOpportunityResponse])
async def find_succession_opportunities(
    min_years_in_business: int = Query(20, ge=10),
    owner_age_threshold: int = Query(60, ge=50),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Find succession planning opportunities"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    screening_service = DealScreeningService(db)
    opportunities = screening_service.find_succession_opportunities(
        tenant_id=uuid.UUID(tenant_id),
        min_years_in_business=min_years_in_business,
        owner_age_threshold=owner_age_threshold
    )

    return opportunities


@router.post("/opportunities/{opportunity_id}/score", response_model=OpportunityScoring)
async def calculate_opportunity_score(
    opportunity_id: uuid.UUID,
    weights: Optional[Dict[str, float]] = Body(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate comprehensive score for an opportunity"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    opportunity = db.query(DealOpportunity).filter(
        DealOpportunity.id == opportunity_id,
        DealOpportunity.tenant_id == uuid.UUID(tenant_id)
    ).first()

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    screening_service = DealScreeningService(db)
    scoring = screening_service.calculate_opportunity_score(opportunity, weights)

    # Update opportunity with calculated scores
    opportunity.financial_score = scoring['financial_score']
    opportunity.strategic_fit_score = scoring['strategic_score']
    opportunity.risk_score = scoring['risk_score']
    opportunity.overall_score = scoring['overall_score']
    opportunity.scoring_rationale = scoring['breakdown']
    db.commit()

    return scoring


@router.get("/opportunities/ranked", response_model=List[RankedOpportunity])
async def get_ranked_opportunities(
    limit: int = Query(50, ge=1, le=200),
    stages: Optional[List[DealStage]] = Query(None),
    min_priority: Optional[int] = Query(None, ge=1, le=5),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ranked list of opportunities"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    filters = {}
    if stages:
        filters['stages'] = stages
    if min_priority is not None:
        filters['min_priority'] = min_priority

    screening_service = DealScreeningService(db)
    ranked = screening_service.rank_opportunities(
        tenant_id=uuid.UUID(tenant_id),
        filters=filters if filters else None,
        limit=limit
    )

    return ranked