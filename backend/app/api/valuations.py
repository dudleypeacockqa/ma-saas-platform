"""
Valuation API Routes
REST endpoints for financial modeling and valuation
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..core.database import get_db
from ..auth.clerk_auth import get_current_user
from ..services.tenant_service import get_current_tenant
from ..services.valuation_engine import (
    DCFValuationService,
    ComparableCompanyService,
    PrecedentTransactionService,
    LBOModelingService,
    MasterValuationService
)
from ..models.financial_models import (
    ValuationModel, DCFModel, ComparableCompanyAnalysis,
    PrecedentTransactionAnalysis, LBOModel,
    ValuationMethod, ScenarioType, TerminalValueMethod, ReportStatus
)

router = APIRouter(prefix="/valuations", tags=["valuations"])


# ============================================================================
# Request/Response Models
# ============================================================================

class DCFInputs(BaseModel):
    base_revenue: float = Field(..., gt=0)
    projection_years: int = Field(default=5, ge=3, le=10)
    revenue_growth_rates: List[float] = Field(..., min_items=1)
    ebitda_margin: float = Field(..., ge=0, le=100)
    tax_rate: float = Field(default=25.0, ge=0, le=50)
    capex_percent_revenue: float = Field(default=3.0, ge=0, le=20)
    depreciation_percent_revenue: float = Field(default=2.5, ge=0, le=10)
    nwc_percent_revenue: float = Field(default=10.0, ge=0, le=50)

    # WACC components
    risk_free_rate: float = Field(default=4.0, ge=0, le=10)
    beta: float = Field(default=1.2, ge=0, le=3)
    market_risk_premium: float = Field(default=6.0, ge=0, le=15)
    cost_of_debt: float = Field(default=5.0, ge=0, le=20)
    debt_to_equity: float = Field(default=0.5, ge=0, le=5)

    # Terminal value
    terminal_value_method: TerminalValueMethod = TerminalValueMethod.PERPETUITY_GROWTH
    terminal_growth_rate: Optional[float] = Field(default=2.5, ge=0, le=5)
    exit_multiple: Optional[float] = Field(default=10.0, ge=1, le=30)

    # Balance sheet
    cash: float = Field(default=0, ge=0)
    debt: float = Field(default=0, ge=0)
    net_debt: float = Field(default=0)


class ComparableCompanyData(BaseModel):
    company_name: str
    revenue: float
    ebitda: float
    enterprise_value: float
    market_cap: Optional[float] = None
    ev_revenue: float
    ev_ebitda: float
    pe: Optional[float] = None


class ComparableAnalysisRequest(BaseModel):
    industry: str
    comparable_companies: List[ComparableCompanyData]
    target_revenue: float
    target_ebitda: float
    target_net_debt: float = 0
    size_premium: float = Field(default=0, ge=-50, le=50)
    liquidity_discount: float = Field(default=20.0, ge=0, le=50)
    control_premium: float = Field(default=30.0, ge=0, le=100)


class PrecedentTransactionData(BaseModel):
    target_company: str
    acquirer: str
    transaction_date: str
    revenue: float
    ebitda: float
    purchase_price: float
    ev_revenue: float
    ev_ebitda: float
    buyer_type: str  # strategic or financial
    premium: Optional[float] = None


class PrecedentAnalysisRequest(BaseModel):
    industry: str
    precedent_transactions: List[PrecedentTransactionData]
    target_revenue: float
    target_ebitda: float
    target_net_debt: float = 0
    lookback_period_months: int = Field(default=36, ge=12, le=120)
    market_timing_adjustment: float = Field(default=0, ge=-30, le=30)


class LBOInputs(BaseModel):
    purchase_price: float = Field(..., gt=0)
    entry_ebitda: float = Field(..., gt=0)
    base_revenue: float = Field(..., gt=0)
    transaction_fees: Optional[float] = None

    # Capital structure
    equity_percent: float = Field(default=40.0, ge=10, le=100)
    senior_debt_rate: float = Field(default=5.0, ge=0, le=15)
    subordinated_debt_rate: float = Field(default=8.0, ge=0, le=20)
    mezzanine_rate: float = Field(default=12.0, ge=0, le=25)

    # Operating assumptions
    hold_period_years: int = Field(default=5, ge=3, le=10)
    revenue_growth_rates: List[float]
    ebitda_margin: float = Field(..., ge=0, le=100)

    # Exit
    exit_multiple: Optional[float] = Field(default=None, ge=1, le=30)
    management_equity_percent: float = Field(default=10.0, ge=0, le=50)


class ComprehensiveValuationRequest(BaseModel):
    company_name: str
    industry: str
    opportunity_id: Optional[str] = None
    deal_id: Optional[str] = None

    # Target metrics
    target_revenue: float
    target_ebitda: float
    target_net_debt: float = 0

    # Method-specific inputs
    dcf_inputs: Optional[DCFInputs] = None
    comparable_data: Optional[ComparableAnalysisRequest] = None
    precedent_data: Optional[PrecedentAnalysisRequest] = None
    lbo_inputs: Optional[LBOInputs] = None


class DCFResponse(BaseModel):
    id: str
    valuation_id: str
    scenario_type: ScenarioType
    projection_years: int
    wacc: float
    terminal_value: float
    enterprise_value: float
    equity_value: float
    revenue_projections: List[float]
    ebitda_projections: List[float]
    free_cash_flows: List[float]

    class Config:
        from_attributes = True


class ComparableAnalysisResponse(BaseModel):
    id: str
    valuation_id: str
    industry: str
    ev_revenue_median: Optional[float]
    ev_ebitda_median: Optional[float]
    selected_ev_revenue: Optional[float]
    selected_ev_ebitda: Optional[float]
    implied_enterprise_value: float
    implied_equity_value: float

    class Config:
        from_attributes = True


class LBOResponse(BaseModel):
    id: str
    valuation_id: str
    purchase_price: float
    purchase_multiple: float
    equity_investment: float
    total_debt: float
    exit_enterprise_value: float
    exit_equity_value: float
    money_multiple: float
    irr: float

    class Config:
        from_attributes = True


class ValuationResponse(BaseModel):
    id: str
    organization_id: str
    company_name: str
    industry: str
    primary_method: ValuationMethod
    base_case_value: Optional[float]
    optimistic_value: Optional[float]
    pessimistic_value: Optional[float]
    ev_revenue_multiple: Optional[float]
    ev_ebitda_multiple: Optional[float]
    status: ReportStatus
    valuation_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SensitivityRequest(BaseModel):
    parameter: str
    min_value: float
    max_value: float
    steps: int = Field(default=10, ge=5, le=50)


class TwoWaySensitivityRequest(BaseModel):
    param1: str
    param1_min: float
    param1_max: float
    param1_steps: int = Field(default=5, ge=3, le=20)
    param2: str
    param2_min: float
    param2_max: float
    param2_steps: int = Field(default=5, ge=3, le=20)


# ============================================================================
# DCF Endpoints
# ============================================================================

@router.post("/dcf", response_model=DCFResponse, status_code=status.HTTP_201_CREATED)
async def create_dcf_valuation(
    valuation_id: str,
    dcf_inputs: DCFInputs,
    scenario_type: ScenarioType = ScenarioType.BASE,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Create DCF valuation model

    Calculates enterprise value using discounted cash flow analysis with
    revenue projections, EBITDA margins, and terminal value.
    """
    # Verify valuation exists
    valuation = db.query(ValuationModel).filter(
        ValuationModel.id == valuation_id,
        ValuationModel.organization_id == tenant_id
    ).first()

    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Valuation {valuation_id} not found"
        )

    service = DCFValuationService(db)

    dcf_model = service.create_dcf_model(
        valuation_id=valuation_id,
        organization_id=tenant_id,
        inputs=dcf_inputs.model_dump(),
        scenario_type=scenario_type
    )

    return dcf_model


@router.get("/dcf/{dcf_id}", response_model=DCFResponse)
async def get_dcf_model(
    dcf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get DCF model by ID"""
    dcf_model = db.query(DCFModel).filter(
        DCFModel.id == dcf_id,
        DCFModel.organization_id == tenant_id
    ).first()

    if not dcf_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DCF model {dcf_id} not found"
        )

    return dcf_model


@router.post("/dcf/{dcf_id}/sensitivity", response_model=Dict[str, Any])
async def run_dcf_sensitivity(
    dcf_id: str,
    sensitivity_request: SensitivityRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Run sensitivity analysis on DCF model

    Varies a single parameter and shows impact on enterprise value.
    """
    dcf_model = db.query(DCFModel).filter(
        DCFModel.id == dcf_id,
        DCFModel.organization_id == tenant_id
    ).first()

    if not dcf_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DCF model {dcf_id} not found"
        )

    service = DCFValuationService(db)

    # Generate value range
    value_range = [
        sensitivity_request.min_value + (sensitivity_request.max_value - sensitivity_request.min_value) * i / (sensitivity_request.steps - 1)
        for i in range(sensitivity_request.steps)
    ]

    results = service.run_sensitivity_analysis(
        dcf_model,
        sensitivity_request.parameter,
        value_range
    )

    return results


# ============================================================================
# Comparable Company Endpoints
# ============================================================================

@router.post("/comparable", response_model=ComparableAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_comparable_analysis(
    valuation_id: str,
    comp_request: ComparableAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Create comparable company analysis

    Analyzes public company trading multiples to derive valuation.
    """
    # Verify valuation exists
    valuation = db.query(ValuationModel).filter(
        ValuationModel.id == valuation_id,
        ValuationModel.organization_id == tenant_id
    ).first()

    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Valuation {valuation_id} not found"
        )

    service = ComparableCompanyService(db)

    # Convert comparable companies to dict format
    comparable_companies = [comp.model_dump() for comp in comp_request.comparable_companies]

    target_metrics = {
        "revenue": comp_request.target_revenue,
        "ebitda": comp_request.target_ebitda,
        "net_debt": comp_request.target_net_debt
    }

    adjustments = {
        "size_premium": comp_request.size_premium,
        "liquidity_discount": comp_request.liquidity_discount,
        "control_premium": comp_request.control_premium
    }

    analysis = service.create_comparable_analysis(
        valuation_id=valuation_id,
        organization_id=tenant_id,
        industry=comp_request.industry,
        comparable_companies=comparable_companies,
        target_metrics=target_metrics,
        adjustments=adjustments
    )

    return analysis


# ============================================================================
# Precedent Transaction Endpoints
# ============================================================================

@router.post("/precedent", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_precedent_analysis(
    valuation_id: str,
    prec_request: PrecedentAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Create precedent transaction analysis

    Analyzes historical M&A transactions to derive valuation benchmarks.
    """
    # Verify valuation exists
    valuation = db.query(ValuationModel).filter(
        ValuationModel.id == valuation_id,
        ValuationModel.organization_id == tenant_id
    ).first()

    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Valuation {valuation_id} not found"
        )

    service = PrecedentTransactionService(db)

    # Convert transactions to dict format
    transactions = [txn.model_dump() for txn in prec_request.precedent_transactions]

    target_metrics = {
        "revenue": prec_request.target_revenue,
        "ebitda": prec_request.target_ebitda,
        "net_debt": prec_request.target_net_debt
    }

    adjustments = {
        "lookback_period_months": prec_request.lookback_period_months,
        "market_timing_adjustment": prec_request.market_timing_adjustment
    }

    analysis = service.create_precedent_analysis(
        valuation_id=valuation_id,
        organization_id=tenant_id,
        industry=prec_request.industry,
        precedent_transactions=transactions,
        target_metrics=target_metrics,
        adjustments=adjustments
    )

    return analysis


# ============================================================================
# LBO Model Endpoints
# ============================================================================

@router.post("/lbo", response_model=LBOResponse, status_code=status.HTTP_201_CREATED)
async def create_lbo_model(
    valuation_id: str,
    lbo_inputs: LBOInputs,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Create LBO financial model

    Models leveraged buyout returns including debt structure,
    cash flows, and IRR/MOIC calculations.
    """
    # Verify valuation exists
    valuation = db.query(ValuationModel).filter(
        ValuationModel.id == valuation_id,
        ValuationModel.organization_id == tenant_id
    ).first()

    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Valuation {valuation_id} not found"
        )

    service = LBOModelingService(db)

    lbo_model = service.create_lbo_model(
        valuation_id=valuation_id,
        organization_id=tenant_id,
        inputs=lbo_inputs.model_dump()
    )

    return lbo_model


@router.post("/lbo/{lbo_id}/sensitivity", response_model=Dict[str, Any])
async def run_lbo_sensitivity(
    lbo_id: str,
    sensitivity_request: TwoWaySensitivityRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Run two-way sensitivity analysis on LBO returns

    Creates data table showing IRR for different exit multiples
    and revenue growth scenarios.
    """
    lbo_model = db.query(LBOModel).filter(
        LBOModel.id == lbo_id,
        LBOModel.organization_id == tenant_id
    ).first()

    if not lbo_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LBO model {lbo_id} not found"
        )

    service = LBOModelingService(db)

    # Generate value ranges
    param1_range = [
        sensitivity_request.param1_min + (sensitivity_request.param1_max - sensitivity_request.param1_min) * i / (sensitivity_request.param1_steps - 1)
        for i in range(sensitivity_request.param1_steps)
    ]

    param2_range = [
        sensitivity_request.param2_min + (sensitivity_request.param2_max - sensitivity_request.param2_min) * i / (sensitivity_request.param2_steps - 1)
        for i in range(sensitivity_request.param2_steps)
    ]

    results = service.run_lbo_sensitivity(
        lbo_model,
        param1_range,
        param2_range
    )

    return results


# ============================================================================
# Comprehensive Valuation Endpoints
# ============================================================================

@router.post("/comprehensive", response_model=ValuationResponse, status_code=status.HTTP_201_CREATED)
async def create_comprehensive_valuation(
    request: ComprehensiveValuationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Create comprehensive valuation using multiple methodologies

    Runs DCF, comparable company, precedent transaction, and/or LBO
    analyses and provides blended valuation.
    """
    service = MasterValuationService(db)

    target_metrics = {
        "revenue": request.target_revenue,
        "ebitda": request.target_ebitda,
        "net_debt": request.target_net_debt
    }

    # Prepare method-specific inputs
    dcf_inputs = request.dcf_inputs.model_dump() if request.dcf_inputs else None

    comparable_data = None
    if request.comparable_data:
        comparable_data = {
            "companies": [comp.model_dump() for comp in request.comparable_data.comparable_companies],
            "adjustments": {
                "size_premium": request.comparable_data.size_premium,
                "liquidity_discount": request.comparable_data.liquidity_discount,
                "control_premium": request.comparable_data.control_premium
            }
        }

    precedent_data = None
    if request.precedent_data:
        precedent_data = {
            "transactions": [txn.model_dump() for txn in request.precedent_data.precedent_transactions],
            "adjustments": {
                "lookback_period_months": request.precedent_data.lookback_period_months,
                "market_timing_adjustment": request.precedent_data.market_timing_adjustment
            }
        }

    lbo_inputs = request.lbo_inputs.model_dump() if request.lbo_inputs else None

    valuation = service.create_comprehensive_valuation(
        organization_id=tenant_id,
        company_name=request.company_name,
        industry=request.industry,
        target_metrics=target_metrics,
        dcf_inputs=dcf_inputs,
        comparable_data=comparable_data,
        precedent_data=precedent_data,
        lbo_inputs=lbo_inputs,
        created_by=current_user["id"]
    )

    return valuation


@router.get("/", response_model=List[ValuationResponse])
async def list_valuations(
    company_name: Optional[str] = None,
    status: Optional[ReportStatus] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    List all valuations for organization

    Supports filtering by company name and status.
    """
    query = db.query(ValuationModel).filter(
        ValuationModel.organization_id == tenant_id
    )

    if company_name:
        query = query.filter(ValuationModel.company_name.ilike(f"%{company_name}%"))

    if status:
        query = query.filter(ValuationModel.status == status)

    query = query.order_by(ValuationModel.valuation_date.desc())

    valuations = query.offset(offset).limit(limit).all()

    return valuations


@router.get("/{valuation_id}", response_model=ValuationResponse)
async def get_valuation(
    valuation_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get valuation by ID with all sub-analyses"""
    valuation = db.query(ValuationModel).filter(
        ValuationModel.id == valuation_id,
        ValuationModel.organization_id == tenant_id
    ).first()

    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Valuation {valuation_id} not found"
        )

    return valuation


@router.delete("/{valuation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_valuation(
    valuation_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """Delete valuation (soft delete)"""
    valuation = db.query(ValuationModel).filter(
        ValuationModel.id == valuation_id,
        ValuationModel.organization_id == tenant_id
    ).first()

    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Valuation {valuation_id} not found"
        )

    valuation.deleted_at = datetime.utcnow()
    db.commit()

    return None


@router.patch("/{valuation_id}/status", response_model=ValuationResponse)
async def update_valuation_status(
    valuation_id: str,
    new_status: ReportStatus,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """Update valuation status (draft, in_review, approved, final)"""
    valuation = db.query(ValuationModel).filter(
        ValuationModel.id == valuation_id,
        ValuationModel.organization_id == tenant_id
    ).first()

    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Valuation {valuation_id} not found"
        )

    valuation.status = new_status

    if new_status == ReportStatus.APPROVED:
        valuation.approved_by = current_user["id"]

    db.commit()
    db.refresh(valuation)

    return valuation
