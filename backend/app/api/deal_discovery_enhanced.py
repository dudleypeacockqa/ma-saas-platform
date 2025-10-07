"""
Enhanced Deal Discovery API Routes
Endpoints for the new Deal Discovery & Sourcing System
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from uuid import UUID

from app.core.database import get_db
from app.auth.clerk_auth import get_current_user, ClerkUser
from app.services.opportunity_discovery import get_discovery_engine
from app.services.deal_scoring import get_scoring_engine
from app.services.financial_analyzer import get_financial_analyzer
from app.models.deal_discovery import (
    DealOpportunity,
    Company,
    FinancialSnapshot,
    MarketIntelligence,
    DealStage,
    FinancialHealth,
    IndustryCategory,
    OpportunitySource
)
from app.tasks.deal_discovery_tasks import (
    discover_new_opportunities_task,
    enrich_opportunity_data_task,
    update_opportunity_scores_task,
    monitor_companies_task
)

router = APIRouter(prefix="/api/deal-discovery", tags=["deal-discovery"])


# ============================================================================
# Request/Response Models
# ============================================================================

class DiscoveryRequest(BaseModel):
    """Request model for opportunity discovery"""
    min_revenue_millions: float = Field(default=1.0, ge=0.1, le=1000.0)
    max_revenue_millions: float = Field(default=50.0, ge=1.0, le=10000.0)
    industries: Optional[List[str]] = Field(default=None)
    regions: Optional[List[str]] = Field(default=None)
    sources: List[str] = Field(default=["companies_house", "sec_edgar"])
    min_growth_rate: Optional[float] = Field(default=None, ge=-1.0, le=5.0)
    profitability_required: bool = Field(default=False)
    max_results_per_source: int = Field(default=50, ge=1, le=200)


class OpportunityResponse(BaseModel):
    """Response model for deal opportunity"""
    id: str
    company_name: str
    opportunity_name: str
    opportunity_score: float
    stage: str
    source: str
    financial_health: str
    estimated_valuation: Optional[float]
    discovered_at: datetime
    company_location: Optional[str]
    industry: Optional[str]

    class Config:
        from_attributes = True


class CompanyDetailResponse(BaseModel):
    """Response model for company details"""
    id: str
    name: str
    legal_name: Optional[str]
    description: Optional[str]
    website: Optional[str]
    industry_category: str
    location_city: Optional[str]
    location_region: Optional[str]
    location_country: Optional[str]
    data_source: str
    external_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ScoringResponse(BaseModel):
    """Response model for opportunity scoring"""
    opportunity_id: str
    total_score: float
    recommendation: str
    component_scores: Dict[str, Any]
    scored_at: str


class FinancialAnalysisResponse(BaseModel):
    """Response model for financial analysis"""
    company_id: str
    company_name: str
    analysis_date: str
    latest_period: int
    profitability_analysis: Dict[str, Any]
    liquidity_analysis: Dict[str, Any]
    leverage_analysis: Dict[str, Any]
    growth_analysis: Dict[str, Any]
    valuation_estimates: Dict[str, Any]
    red_flags: List[str]
    strengths: List[str]


# ============================================================================
# Discovery Endpoints
# ============================================================================

@router.post("/discover", response_model=Dict[str, Any], status_code=status.HTTP_202_ACCEPTED)
async def start_discovery(
    discovery_request: DiscoveryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Start opportunity discovery process (async)

    Initiates background task to discover M&A opportunities from multiple sources.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required"
        )

    criteria = discovery_request.model_dump()

    # Start background task
    background_tasks.add_task(
        discover_new_opportunities_task,
        organization_id=current_user.organization_id,
        user_id=current_user.user_id,
        criteria=criteria
    )

    return {
        "message": "Discovery process started",
        "organization_id": current_user.organization_id,
        "criteria": criteria,
        "status": "processing"
    }


@router.post("/discover/sync", response_model=List[OpportunityResponse])
async def discover_opportunities_sync(
    discovery_request: DiscoveryRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Discover opportunities synchronously (immediate response)

    Returns discovered opportunities immediately. Use for smaller searches.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required"
        )

    discovery_engine = get_discovery_engine()
    criteria = discovery_request.model_dump()

    opportunities = await discovery_engine.discover_opportunities(
        organization_id=current_user.organization_id,
        user_id=current_user.user_id,
        db=db,
        criteria=criteria
    )

    # Format response
    response = []
    for opp in opportunities:
        response.append({
            "id": str(opp.id),
            "company_name": opp.company.name,
            "opportunity_name": opp.opportunity_name,
            "opportunity_score": opp.opportunity_score,
            "stage": opp.stage.value,
            "source": opp.source.value,
            "financial_health": opp.financial_health.value,
            "estimated_valuation": opp.estimated_valuation,
            "discovered_at": opp.discovered_at,
            "company_location": f"{opp.company.location_city or ''}, {opp.company.location_country or ''}".strip(", "),
            "industry": opp.company.industry_category.value
        })

    return response


# ============================================================================
# Opportunity Management Endpoints
# ============================================================================

@router.get("/opportunities", response_model=List[OpportunityResponse])
async def list_opportunities(
    stage: Optional[List[DealStage]] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    source: Optional[List[OpportunitySource]] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    List M&A opportunities with filtering

    Returns all opportunities for the user's organization with optional filtering.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required"
        )

    query = db.query(DealOpportunity).filter(
        DealOpportunity.organization_id == current_user.organization_id
    )

    # Apply filters
    if stage:
        query = query.filter(DealOpportunity.stage.in_(stage))

    if min_score is not None:
        query = query.filter(DealOpportunity.opportunity_score >= min_score)

    if source:
        query = query.filter(DealOpportunity.source.in_(source))

    # Order by score descending
    query = query.order_by(DealOpportunity.opportunity_score.desc())

    # Pagination
    opportunities = query.offset(offset).limit(limit).all()

    # Format response
    response = []
    for opp in opportunities:
        response.append({
            "id": str(opp.id),
            "company_name": opp.company.name,
            "opportunity_name": opp.opportunity_name,
            "opportunity_score": opp.opportunity_score,
            "stage": opp.stage.value,
            "source": opp.source.value,
            "financial_health": opp.financial_health.value,
            "estimated_valuation": opp.estimated_valuation,
            "discovered_at": opp.discovered_at,
            "company_location": f"{opp.company.location_city or ''}, {opp.company.location_country or ''}".strip(", "),
            "industry": opp.company.industry_category.value
        })

    return response


@router.get("/opportunities/{opportunity_id}", response_model=Dict[str, Any])
async def get_opportunity_detail(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get detailed information about a specific opportunity

    Returns comprehensive details including company data, financials, and intelligence.
    """
    opportunity = db.query(DealOpportunity).filter(
        DealOpportunity.id == opportunity_id,
        DealOpportunity.organization_id == current_user.organization_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )

    company = opportunity.company

    # Get financial snapshots
    financials = db.query(FinancialSnapshot).filter(
        FinancialSnapshot.company_id == company.id
    ).order_by(FinancialSnapshot.period_year.desc()).limit(3).all()

    # Get market intelligence
    intelligence = db.query(MarketIntelligence).filter(
        MarketIntelligence.company_id == company.id
    ).order_by(MarketIntelligence.created_at.desc()).limit(10).all()

    return {
        "opportunity": {
            "id": str(opportunity.id),
            "opportunity_name": opportunity.opportunity_name,
            "opportunity_score": opportunity.opportunity_score,
            "stage": opportunity.stage.value,
            "source": opportunity.source.value,
            "financial_health": opportunity.financial_health.value,
            "estimated_valuation": opportunity.estimated_valuation,
            "notes": opportunity.notes,
            "discovered_at": opportunity.discovered_at
        },
        "company": {
            "id": str(company.id),
            "name": company.name,
            "legal_name": company.legal_name,
            "description": company.description,
            "website": company.website,
            "industry": company.industry_category.value,
            "location": {
                "city": company.location_city,
                "region": company.location_region,
                "country": company.location_country
            },
            "data_source": company.data_source.value,
            "external_id": company.external_id
        },
        "financials": [
            {
                "year": f.period_year,
                "revenue": float(f.revenue) if f.revenue else None,
                "ebitda": float(f.ebitda) if f.ebitda else None,
                "net_income": float(f.net_income) if f.net_income else None,
                "total_assets": float(f.total_assets) if f.total_assets else None,
                "profit_margin": float(f.profit_margin) if f.profit_margin else None
            }
            for f in financials
        ],
        "market_intelligence": [
            {
                "id": str(i.id),
                "type": i.intelligence_type,
                "source": i.source,
                "relevance_score": float(i.relevance_score) if i.relevance_score else None,
                "content_summary": str(i.content)[:200] + "..." if i.content and len(str(i.content)) > 200 else str(i.content),
                "created_at": i.created_at
            }
            for i in intelligence
        ]
    }


@router.patch("/opportunities/{opportunity_id}/stage")
async def update_opportunity_stage(
    opportunity_id: str,
    stage: DealStage,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Update opportunity pipeline stage

    Moves opportunity to a new stage in the deal pipeline.
    """
    opportunity = db.query(DealOpportunity).filter(
        DealOpportunity.id == opportunity_id,
        DealOpportunity.organization_id == current_user.organization_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )

    opportunity.stage = stage
    if notes:
        opportunity.notes = notes

    db.commit()

    return {
        "opportunity_id": str(opportunity.id),
        "stage": opportunity.stage.value,
        "updated_at": datetime.utcnow()
    }


# ============================================================================
# Scoring & Analysis Endpoints
# ============================================================================

@router.post("/opportunities/{opportunity_id}/score", response_model=ScoringResponse)
async def score_opportunity(
    opportunity_id: str,
    buyer_profile: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Calculate/recalculate opportunity score

    Generates comprehensive scoring based on financial, strategic, and market factors.
    """
    opportunity = db.query(DealOpportunity).filter(
        DealOpportunity.id == opportunity_id,
        DealOpportunity.organization_id == current_user.organization_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )

    scoring_engine = get_scoring_engine()

    scoring = scoring_engine.calculate_opportunity_score(
        opportunity=opportunity,
        db=db,
        buyer_profile=buyer_profile
    )

    db.commit()

    return {
        "opportunity_id": str(opportunity.id),
        "total_score": scoring["total_score"],
        "recommendation": scoring["recommendation"],
        "component_scores": scoring["component_scores"],
        "scored_at": scoring["scored_at"]
    }


@router.get("/opportunities/{opportunity_id}/financial-analysis", response_model=FinancialAnalysisResponse)
async def get_financial_analysis(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get comprehensive financial analysis

    Returns detailed financial analysis including ratios, trends, and valuation.
    """
    opportunity = db.query(DealOpportunity).filter(
        DealOpportunity.id == opportunity_id,
        DealOpportunity.organization_id == current_user.organization_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )

    financial_analyzer = get_financial_analyzer()

    analysis = financial_analyzer.analyze_company_financials(
        company_id=str(opportunity.company_id),
        db=db
    )

    return analysis


@router.post("/opportunities/rank", response_model=List[Dict[str, Any]])
async def rank_opportunities(
    opportunity_ids: List[str],
    buyer_profile: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Rank multiple opportunities

    Scores and ranks a list of opportunities for comparison.
    """
    opportunities = db.query(DealOpportunity).filter(
        DealOpportunity.id.in_(opportunity_ids),
        DealOpportunity.organization_id == current_user.organization_id
    ).all()

    if not opportunities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching opportunities found"
        )

    scoring_engine = get_scoring_engine()

    ranked = scoring_engine.rank_opportunities(
        opportunities=opportunities,
        db=db,
        buyer_profile=buyer_profile
    )

    return ranked


# ============================================================================
# Background Task Endpoints
# ============================================================================

@router.post("/opportunities/{opportunity_id}/enrich", status_code=status.HTTP_202_ACCEPTED)
async def enrich_opportunity(
    opportunity_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Enrich opportunity with additional data (async)

    Starts background task to fetch additional company data and market intelligence.
    """
    opportunity = db.query(DealOpportunity).filter(
        DealOpportunity.id == opportunity_id,
        DealOpportunity.organization_id == current_user.organization_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found"
        )

    background_tasks.add_task(enrich_opportunity_data_task, opportunity_id)

    return {
        "message": "Enrichment process started",
        "opportunity_id": opportunity_id,
        "status": "processing"
    }


@router.post("/refresh-scores", status_code=status.HTTP_202_ACCEPTED)
async def refresh_all_scores(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Refresh scores for all opportunities (async)

    Recalculates scores for all opportunities in the organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required"
        )

    background_tasks.add_task(
        update_opportunity_scores_task,
        organization_id=current_user.organization_id
    )

    return {
        "message": "Score refresh started",
        "organization_id": current_user.organization_id,
        "status": "processing"
    }


@router.post("/monitor", status_code=status.HTTP_202_ACCEPTED)
async def start_monitoring(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Start company monitoring (async)

    Monitors companies for news and market events.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required"
        )

    background_tasks.add_task(
        monitor_companies_task,
        organization_id=current_user.organization_id
    )

    return {
        "message": "Monitoring started",
        "organization_id": current_user.organization_id,
        "status": "processing"
    }


# ============================================================================
# Pipeline Analytics Endpoints
# ============================================================================

@router.get("/analytics/pipeline", response_model=Dict[str, Any])
async def get_pipeline_analytics(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get pipeline analytics and metrics

    Returns aggregated statistics about the opportunity pipeline.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required"
        )

    opportunities = db.query(DealOpportunity).filter(
        DealOpportunity.organization_id == current_user.organization_id
    ).all()

    # Calculate metrics
    total_count = len(opportunities)
    avg_score = sum(opp.opportunity_score for opp in opportunities) / total_count if total_count > 0 else 0

    stage_breakdown = {}
    for stage in DealStage:
        count = len([opp for opp in opportunities if opp.stage == stage])
        stage_breakdown[stage.value] = count

    source_breakdown = {}
    for source in OpportunitySource:
        count = len([opp for opp in opportunities if opp.source == source])
        source_breakdown[source.value] = count

    health_breakdown = {}
    for health in FinancialHealth:
        count = len([opp for opp in opportunities if opp.financial_health == health])
        health_breakdown[health.value] = count

    return {
        "total_opportunities": total_count,
        "average_score": round(avg_score, 1),
        "stage_breakdown": stage_breakdown,
        "source_breakdown": source_breakdown,
        "financial_health_breakdown": health_breakdown,
        "high_score_count": len([opp for opp in opportunities if opp.opportunity_score >= 75]),
        "qualified_count": len([opp for opp in opportunities if opp.stage == DealStage.INITIAL_REVIEW])
    }
