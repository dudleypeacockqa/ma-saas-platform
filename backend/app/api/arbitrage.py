"""
M&A Arbitrage & Investment Strategy API
REST endpoints for arbitrage analysis, portfolio optimization, and risk management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..core.database import get_db
from ..auth.clerk_auth import get_current_user, ClerkUser
from ..services.investment_strategy import (
    ArbitrageAnalysisService,
    PortfolioOptimizationService,
    RiskManagementService
)
from ..models.arbitrage import (
    AnnouncedDeal, ArbitragePosition, InvestmentPortfolio,
    DealUpdate, PortfolioSnapshot, PortfolioRebalancing,
    DealStatus, ArbitrageStrategy, RiskLevel, PortfolioStrategy
)
from ..utils.portfolio_optimization import OptimizationObjective, ConstraintType

router = APIRouter(prefix="/arbitrage", tags=["arbitrage"])


# ============================================================================
# Request/Response Models
# ============================================================================

class AnnouncedDealCreate(BaseModel):
    """Request model for creating announced deal"""
    opportunity_id: Optional[str] = None
    target_company: str = Field(..., min_length=1, max_length=255)
    acquirer_company: str = Field(..., min_length=1, max_length=255)
    target_ticker: Optional[str] = Field(None, max_length=20)
    acquirer_ticker: Optional[str] = Field(None, max_length=20)
    deal_value: Optional[float] = Field(None, gt=0)
    price_per_share: Optional[float] = Field(None, gt=0)
    currency: str = Field(default="USD", max_length=3)
    deal_type: str = Field(..., description="Cash, stock, or mixed deal")
    cash_component: Optional[float] = Field(None, ge=0, le=1)
    stock_component: Optional[float] = Field(None, ge=0, le=1)
    exchange_ratio: Optional[float] = Field(None, gt=0)
    announcement_date: date
    expected_close_date: Optional[date] = None
    completion_probability: Optional[float] = Field(None, ge=0, le=1)
    regulatory_approvals_required: Optional[List[str]] = None
    deal_description: Optional[str] = None


class AnnouncedDealResponse(BaseModel):
    """Response model for announced deal"""
    id: str
    organization_id: str
    opportunity_id: Optional[str]
    target_company: str
    acquirer_company: str
    target_ticker: Optional[str]
    acquirer_ticker: Optional[str]
    deal_value: Optional[float]
    price_per_share: Optional[float]
    currency: str
    deal_type: str
    current_status: str
    completion_probability: Optional[float]
    announcement_date: date
    expected_close_date: Optional[date]
    gross_spread: Optional[float]
    gross_spread_percentage: Optional[float]
    annualized_return: Optional[float]
    deal_break_risk: str
    regulatory_risk: str
    financing_risk: str
    overall_risk_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class ArbitrageAnalysisRequest(BaseModel):
    """Request for arbitrage analysis"""
    deal_id: str
    current_target_price: float = Field(..., gt=0)
    current_acquirer_price: Optional[float] = Field(None, gt=0)


class ArbitrageOpportunityResponse(BaseModel):
    """Response for arbitrage opportunity analysis"""
    deal_id: str
    target_company: str
    deal_type: str
    gross_spread: Optional[float]
    gross_spread_percentage: Optional[float]
    risk_adjusted_spread: Optional[float]
    annualized_return: Optional[float]
    days_to_close: Optional[int]
    risk_factors: Dict[str, Any]
    recommendation: str


class PortfolioCreateRequest(BaseModel):
    """Request to create investment portfolio"""
    portfolio_name: str = Field(..., min_length=1, max_length=255)
    portfolio_description: Optional[str] = None
    strategy_type: PortfolioStrategy = PortfolioStrategy.BALANCED
    investment_objective: Optional[str] = None
    initial_capital: float = Field(..., gt=0)
    max_position_size: float = Field(default=0.1, ge=0.01, le=1.0)
    max_sector_exposure: float = Field(default=0.3, ge=0.01, le=1.0)
    risk_tolerance: RiskLevel = RiskLevel.MEDIUM
    benchmark_index: Optional[str] = None


class PortfolioResponse(BaseModel):
    """Response for portfolio"""
    id: str
    organization_id: str
    portfolio_name: str
    strategy_type: str
    initial_capital: float
    current_capital: float
    available_capital: float
    committed_capital: float
    total_return: Optional[float]
    annualized_return: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    number_of_positions: int
    is_active: bool
    inception_date: date
    created_at: datetime

    class Config:
        from_attributes = True


class ArbitragePositionCreate(BaseModel):
    """Request to create arbitrage position"""
    announced_deal_id: str
    portfolio_id: Optional[str] = None
    strategy: ArbitrageStrategy = ArbitrageStrategy.MERGER_ARBITRAGE
    position_name: str = Field(..., min_length=1, max_length=255)
    capital_allocated: float = Field(..., gt=0)
    target_shares: Optional[int] = Field(None, gt=0)
    acquirer_shares: Optional[int] = Field(None, gt=0)
    stop_loss_level: Optional[float] = Field(None, gt=0)
    max_loss_limit: Optional[float] = Field(None, gt=0)


class ArbitragePositionResponse(BaseModel):
    """Response for arbitrage position"""
    id: str
    organization_id: str
    announced_deal_id: str
    portfolio_id: Optional[str]
    strategy: str
    position_name: str
    notional_value: float
    capital_allocated: float
    target_shares: Optional[int]
    acquirer_shares: Optional[int]
    entry_date: date
    entry_spread: Optional[float]
    entry_spread_percentage: Optional[float]
    current_spread: Optional[float]
    unrealized_pnl: Optional[float]
    total_pnl: Optional[float]
    pnl_percentage: Optional[float]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PortfolioOptimizationRequest(BaseModel):
    """Request for portfolio optimization"""
    portfolio_id: str
    optimization_objective: OptimizationObjective = OptimizationObjective.SHARPE_RATIO
    risk_aversion: float = Field(default=3.0, gt=0, le=10)
    constraints: Optional[List[Dict[str, Any]]] = None
    include_opportunity_ids: Optional[List[str]] = None
    exclude_opportunity_ids: Optional[List[str]] = None


class PortfolioOptimizationResponse(BaseModel):
    """Response for portfolio optimization"""
    portfolio_id: str
    optimization_objective: str
    total_expected_return: float
    total_risk: float
    sharpe_ratio: float
    allocations: List[Dict[str, Any]]
    constraints_satisfied: bool
    optimization_status: str


class RiskAnalysisRequest(BaseModel):
    """Request for risk analysis"""
    portfolio_id: str
    confidence_level: float = Field(default=0.95, gt=0.5, lt=1.0)
    stress_test: bool = Field(default=True)


class OpportunityScreenRequest(BaseModel):
    """Request for opportunity screening"""
    min_deal_value: Optional[float] = Field(None, gt=0)
    max_days_to_close: Optional[int] = Field(None, gt=0, le=1095)  # Max 3 years
    min_completion_probability: Optional[float] = Field(None, ge=0, le=1)
    min_annualized_return: Optional[float] = Field(None, ge=0)
    max_risk_level: Optional[RiskLevel] = None
    deal_types: Optional[List[str]] = None
    sectors: Optional[List[str]] = None


# ============================================================================
# Deal Discovery & Analysis Endpoints
# ============================================================================

@router.post("/deals", response_model=AnnouncedDealResponse, status_code=status.HTTP_201_CREATED)
async def create_announced_deal(
    deal: AnnouncedDealCreate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Create a new announced M&A deal for arbitrage analysis
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required"
        )

    try:
        new_deal = AnnouncedDeal(
            organization_id=current_user.organization_id,
            **deal.model_dump(exclude_unset=True)
        )

        db.add(new_deal)
        db.commit()
        db.refresh(new_deal)

        return new_deal

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create deal: {str(e)}"
        )


@router.get("/deals", response_model=List[AnnouncedDealResponse])
async def list_announced_deals(
    status_filter: Optional[List[DealStatus]] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    List announced M&A deals
    """
    query = db.query(AnnouncedDeal).filter(
        AnnouncedDeal.organization_id == current_user.organization_id
    )

    if status_filter:
        query = query.filter(AnnouncedDeal.current_status.in_(status_filter))

    deals = query.order_by(AnnouncedDeal.announcement_date.desc()).offset(offset).limit(limit).all()

    return deals


@router.get("/deals/{deal_id}", response_model=AnnouncedDealResponse)
async def get_announced_deal(
    deal_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get specific announced deal
    """
    deal = db.query(AnnouncedDeal).filter(
        AnnouncedDeal.id == deal_id,
        AnnouncedDeal.organization_id == current_user.organization_id
    ).first()

    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal {deal_id} not found"
        )

    return deal


@router.post("/analyze", response_model=ArbitrageOpportunityResponse)
async def analyze_arbitrage_opportunity(
    analysis_request: ArbitrageAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Analyze arbitrage opportunity for a specific deal
    """
    # Verify deal exists and belongs to user's organization
    deal = db.query(AnnouncedDeal).filter(
        AnnouncedDeal.id == analysis_request.deal_id,
        AnnouncedDeal.organization_id == current_user.organization_id
    ).first()

    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal {analysis_request.deal_id} not found"
        )

    try:
        arbitrage_service = ArbitrageAnalysisService(db)

        analysis = arbitrage_service.calculate_arbitrage_spread(
            deal=deal,
            current_target_price=analysis_request.current_target_price,
            current_acquirer_price=analysis_request.current_acquirer_price
        )

        return ArbitrageOpportunityResponse(**analysis)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/scan", response_model=List[ArbitrageOpportunityResponse])
async def scan_arbitrage_opportunities(
    screen_request: OpportunityScreenRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Scan for arbitrage opportunities based on criteria
    """
    try:
        arbitrage_service = ArbitrageAnalysisService(db)

        filters = screen_request.model_dump(exclude_unset=True)

        opportunities = arbitrage_service.scan_arbitrage_opportunities(
            organization_id=current_user.organization_id,
            filters=filters
        )

        return [ArbitrageOpportunityResponse(**opp) for opp in opportunities]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scan failed: {str(e)}"
        )


# ============================================================================
# Portfolio Management Endpoints
# ============================================================================

@router.post("/portfolios", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_investment_portfolio(
    portfolio_request: PortfolioCreateRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Create a new investment portfolio for arbitrage strategies
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required"
        )

    try:
        new_portfolio = InvestmentPortfolio(
            organization_id=current_user.organization_id,
            current_capital=portfolio_request.initial_capital,
            available_capital=portfolio_request.initial_capital,
            committed_capital=0,
            inception_date=date.today(),
            **portfolio_request.model_dump(exclude_unset=True)
        )

        db.add(new_portfolio)
        db.commit()
        db.refresh(new_portfolio)

        return new_portfolio

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create portfolio: {str(e)}"
        )


@router.get("/portfolios", response_model=List[PortfolioResponse])
async def list_investment_portfolios(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    List investment portfolios
    """
    query = db.query(InvestmentPortfolio).filter(
        InvestmentPortfolio.organization_id == current_user.organization_id
    )

    if active_only:
        query = query.filter(InvestmentPortfolio.is_active == True)

    portfolios = query.order_by(InvestmentPortfolio.inception_date.desc()).all()

    return portfolios


@router.get("/portfolios/{portfolio_id}", response_model=PortfolioResponse)
async def get_investment_portfolio(
    portfolio_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get specific investment portfolio
    """
    portfolio = db.query(InvestmentPortfolio).filter(
        InvestmentPortfolio.id == portfolio_id,
        InvestmentPortfolio.organization_id == current_user.organization_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found"
        )

    return portfolio


@router.post("/portfolios/{portfolio_id}/optimize", response_model=PortfolioOptimizationResponse)
async def optimize_portfolio(
    portfolio_id: str,
    optimization_request: PortfolioOptimizationRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Optimize portfolio allocation using modern portfolio theory
    """
    # Verify portfolio exists and belongs to user
    portfolio = db.query(InvestmentPortfolio).filter(
        InvestmentPortfolio.id == portfolio_id,
        InvestmentPortfolio.organization_id == current_user.organization_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found"
        )

    try:
        optimization_service = PortfolioOptimizationService(db)

        # Get available arbitrage opportunities
        arbitrage_service = ArbitrageAnalysisService(db)
        opportunities = arbitrage_service.scan_arbitrage_opportunities(
            organization_id=current_user.organization_id
        )

        # Filter opportunities if specified
        if optimization_request.include_opportunity_ids:
            opportunities = [
                opp for opp in opportunities
                if opp["deal_id"] in optimization_request.include_opportunity_ids
            ]

        if optimization_request.exclude_opportunity_ids:
            opportunities = [
                opp for opp in opportunities
                if opp["deal_id"] not in optimization_request.exclude_opportunity_ids
            ]

        if not opportunities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No eligible opportunities found for optimization"
            )

        # Perform optimization
        optimization_result = optimization_service.optimize_portfolio_allocation(
            portfolio_id=portfolio_id,
            opportunities=opportunities,
            optimization_objective=optimization_request.optimization_objective
        )

        return PortfolioOptimizationResponse(**optimization_result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Optimization failed: {str(e)}"
        )


# ============================================================================
# Position Management Endpoints
# ============================================================================

@router.post("/positions", response_model=ArbitragePositionResponse, status_code=status.HTTP_201_CREATED)
async def create_arbitrage_position(
    position_request: ArbitragePositionCreate,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Create a new arbitrage position
    """
    # Verify deal exists
    deal = db.query(AnnouncedDeal).filter(
        AnnouncedDeal.id == position_request.announced_deal_id,
        AnnouncedDeal.organization_id == current_user.organization_id
    ).first()

    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal {position_request.announced_deal_id} not found"
        )

    # Verify portfolio if specified
    if position_request.portfolio_id:
        portfolio = db.query(InvestmentPortfolio).filter(
            InvestmentPortfolio.id == position_request.portfolio_id,
            InvestmentPortfolio.organization_id == current_user.organization_id
        ).first()

        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {position_request.portfolio_id} not found"
            )

    try:
        new_position = ArbitragePosition(
            organization_id=current_user.organization_id,
            entry_date=date.today(),
            notional_value=position_request.capital_allocated,
            **position_request.model_dump(exclude_unset=True)
        )

        db.add(new_position)
        db.commit()
        db.refresh(new_position)

        return new_position

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create position: {str(e)}"
        )


@router.get("/positions", response_model=List[ArbitragePositionResponse])
async def list_arbitrage_positions(
    portfolio_id: Optional[str] = Query(None),
    active_only: bool = Query(True),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    List arbitrage positions
    """
    query = db.query(ArbitragePosition).filter(
        ArbitragePosition.organization_id == current_user.organization_id
    )

    if portfolio_id:
        query = query.filter(ArbitragePosition.portfolio_id == portfolio_id)

    if active_only:
        query = query.filter(ArbitragePosition.is_active == True)

    positions = query.order_by(ArbitragePosition.entry_date.desc()).offset(offset).limit(limit).all()

    return positions


@router.get("/positions/{position_id}", response_model=ArbitragePositionResponse)
async def get_arbitrage_position(
    position_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get specific arbitrage position
    """
    position = db.query(ArbitragePosition).filter(
        ArbitragePosition.id == position_id,
        ArbitragePosition.organization_id == current_user.organization_id
    ).first()

    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Position {position_id} not found"
        )

    return position


# ============================================================================
# Risk Management Endpoints
# ============================================================================

@router.post("/portfolios/{portfolio_id}/risk-analysis", response_model=Dict[str, Any])
async def analyze_portfolio_risk(
    portfolio_id: str,
    risk_request: RiskAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Perform comprehensive portfolio risk analysis
    """
    # Verify portfolio exists
    portfolio = db.query(InvestmentPortfolio).filter(
        InvestmentPortfolio.id == portfolio_id,
        InvestmentPortfolio.organization_id == current_user.organization_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found"
        )

    try:
        risk_service = RiskManagementService(db)

        risk_analysis = risk_service.calculate_portfolio_risk(
            portfolio_id=portfolio_id,
            confidence_level=risk_request.confidence_level
        )

        # Generate risk alerts
        alerts = risk_service.generate_risk_alerts(portfolio_id, risk_analysis)
        risk_analysis["alerts"] = alerts

        return risk_analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Risk analysis failed: {str(e)}"
        )


@router.post("/portfolios/{portfolio_id}/rebalance", response_model=Dict[str, Any])
async def rebalance_portfolio(
    portfolio_id: str,
    trigger_type: str = "manual",
    rebalancing_threshold: float = Query(0.05, ge=0.01, le=0.5),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Rebalance portfolio allocation
    """
    # Verify portfolio exists
    portfolio = db.query(InvestmentPortfolio).filter(
        InvestmentPortfolio.id == portfolio_id,
        InvestmentPortfolio.organization_id == current_user.organization_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found"
        )

    try:
        optimization_service = PortfolioOptimizationService(db)

        rebalancing_result = optimization_service.rebalance_portfolio(
            portfolio_id=portfolio_id,
            trigger_type=trigger_type,
            rebalancing_threshold=rebalancing_threshold
        )

        return rebalancing_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rebalancing failed: {str(e)}"
        )


# ============================================================================
# Analytics & Reporting Endpoints
# ============================================================================

@router.get("/portfolios/{portfolio_id}/performance", response_model=Dict[str, Any])
async def get_portfolio_performance(
    portfolio_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    benchmark: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get comprehensive portfolio performance analytics
    """
    # Verify portfolio exists
    portfolio = db.query(InvestmentPortfolio).filter(
        InvestmentPortfolio.id == portfolio_id,
        InvestmentPortfolio.organization_id == current_user.organization_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found"
        )

    try:
        # Get portfolio snapshots for the specified period
        query = db.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.portfolio_id == portfolio_id
        )

        if start_date:
            query = query.filter(PortfolioSnapshot.snapshot_date >= start_date)

        if end_date:
            query = query.filter(PortfolioSnapshot.snapshot_date <= end_date)

        snapshots = query.order_by(PortfolioSnapshot.snapshot_date).all()

        if not snapshots:
            return {
                "portfolio_id": portfolio_id,
                "message": "No performance data available for the specified period"
            }

        # Calculate performance metrics
        performance_data = {
            "portfolio_id": portfolio_id,
            "period_start": snapshots[0].snapshot_date.isoformat(),
            "period_end": snapshots[-1].snapshot_date.isoformat(),
            "total_return": portfolio.total_return,
            "annualized_return": portfolio.annualized_return,
            "sharpe_ratio": portfolio.sharpe_ratio,
            "max_drawdown": portfolio.max_drawdown,
            "volatility": None,  # Would calculate from snapshots
            "win_rate": portfolio.win_rate,
            "current_positions": portfolio.number_of_positions,
            "snapshots_count": len(snapshots)
        }

        # Add time series data
        performance_data["time_series"] = [
            {
                "date": snapshot.snapshot_date.isoformat(),
                "total_value": float(snapshot.total_value),
                "daily_return": float(snapshot.daily_return) if snapshot.daily_return else None,
                "cumulative_return": float(snapshot.cumulative_return) if snapshot.cumulative_return else None
            }
            for snapshot in snapshots
        ]

        return performance_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Performance analysis failed: {str(e)}"
        )


@router.get("/deals/{deal_id}/updates", response_model=List[Dict[str, Any]])
async def get_deal_updates(
    deal_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get updates and news for a specific deal
    """
    # Verify deal exists
    deal = db.query(AnnouncedDeal).filter(
        AnnouncedDeal.id == deal_id,
        AnnouncedDeal.organization_id == current_user.organization_id
    ).first()

    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal {deal_id} not found"
        )

    updates = db.query(DealUpdate).filter(
        DealUpdate.announced_deal_id == deal_id
    ).order_by(DealUpdate.update_date.desc()).limit(limit).all()

    return [
        {
            "id": str(update.id),
            "update_type": update.update_type,
            "update_title": update.update_title,
            "update_content": update.update_content,
            "update_date": update.update_date.isoformat(),
            "impact_on_probability": float(update.impact_on_probability) if update.impact_on_probability else None,
            "sentiment_score": float(update.sentiment_score) if update.sentiment_score else None,
            "source_type": update.source_type,
            "regulatory_related": update.regulatory_related
        }
        for update in updates
    ]


@router.get("/analytics/market-overview", response_model=Dict[str, Any])
async def get_market_overview(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    """
    Get market overview and arbitrage analytics
    """
    try:
        # Get deal statistics
        total_deals = db.query(AnnouncedDeal).filter(
            AnnouncedDeal.organization_id == current_user.organization_id
        ).count()

        active_deals = db.query(AnnouncedDeal).filter(
            AnnouncedDeal.organization_id == current_user.organization_id,
            AnnouncedDeal.current_status.in_([
                DealStatus.ANNOUNCED,
                DealStatus.REGULATORY_REVIEW,
                DealStatus.SHAREHOLDER_APPROVAL
            ])
        ).count()

        # Get position statistics
        total_positions = db.query(ArbitragePosition).filter(
            ArbitragePosition.organization_id == current_user.organization_id
        ).count()

        active_positions = db.query(ArbitragePosition).filter(
            ArbitragePosition.organization_id == current_user.organization_id,
            ArbitragePosition.is_active == True
        ).count()

        # Get portfolio statistics
        total_portfolios = db.query(InvestmentPortfolio).filter(
            InvestmentPortfolio.organization_id == current_user.organization_id
        ).count()

        active_portfolios = db.query(InvestmentPortfolio).filter(
            InvestmentPortfolio.organization_id == current_user.organization_id,
            InvestmentPortfolio.is_active == True
        ).count()

        return {
            "deals": {
                "total": total_deals,
                "active": active_deals,
                "completion_rate": None  # Would calculate from historical data
            },
            "positions": {
                "total": total_positions,
                "active": active_positions
            },
            "portfolios": {
                "total": total_portfolios,
                "active": active_portfolios
            },
            "market_conditions": {
                "volatility_regime": "NORMAL",  # Would calculate from market data
                "deal_flow": "MODERATE",  # Would analyze recent deal announcements
                "risk_environment": "STABLE"  # Would assess from various risk indicators
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Market overview failed: {str(e)}"
        )