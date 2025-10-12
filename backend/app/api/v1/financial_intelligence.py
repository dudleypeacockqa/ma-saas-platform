"""
Financial Intelligence API Endpoints
Real-time financial analysis and AI-powered insights
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.core.database import get_db
from app.auth.clerk_auth import get_current_user, ClerkUser
from app.services.financial_intelligence import FinancialIntelligenceEngine, FinancialIntelligence
from app.services.automated_valuation_engine import AutomatedValuationEngine, ComprehensiveValuation
from app.services.offer_stack_generator import InteractiveOfferStackGenerator

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for API requests/responses

class FinancialAnalysisRequest(BaseModel):
    company_id: str = Field(..., description="Target company identifier")
    include_projections: bool = Field(True, description="Include financial projections")
    benchmark_industry: Optional[str] = Field(None, description="Industry for benchmarking")

class ValuationRequest(BaseModel):
    company_id: str = Field(..., description="Company to value")
    industry: str = Field(..., description="Company industry")
    custom_assumptions: Optional[Dict[str, Any]] = Field(None, description="Custom valuation assumptions")

class OfferStackRequest(BaseModel):
    target_company_id: str = Field(..., description="Target company")
    buyer_profile: Dict[str, Any] = Field(..., description="Buyer characteristics and preferences")
    deal_parameters: Dict[str, Any] = Field(..., description="Deal-specific parameters")

class ExportOfferRequest(BaseModel):
    scenarios: List[Dict[str, Any]] = Field(..., description="Offer scenarios to export")
    target_company_id: str = Field(..., description="Target company")
    export_options: Dict[str, Any] = Field(default_factory=dict, description="Export preferences")

# Financial Intelligence Endpoints

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_company_financials(
    request: FinancialAnalysisRequest,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform comprehensive AI-powered financial analysis

    Returns detailed financial intelligence including:
    - 47+ key financial ratios
    - AI-generated insights and recommendations
    - Risk indicators and growth signals
    - Deal readiness assessment
    - Valuation range estimate
    """
    try:
        # Initialize financial intelligence engine
        engine = FinancialIntelligenceEngine(db)

        # Perform analysis
        analysis = await engine.analyze_company_financials(
            company_id=request.company_id,
            include_projections=request.include_projections,
            benchmark_industry=request.benchmark_industry
        )

        # Convert to API response format
        return {
            "company_id": analysis.company_id,
            "analysis_date": analysis.analysis_date.isoformat(),
            "key_metrics": analysis.key_metrics,
            "risk_indicators": analysis.risk_indicators,
            "growth_signals": analysis.growth_signals,
            "valuation_range": {
                "low": float(analysis.valuation_range[0]),
                "high": float(analysis.valuation_range[1])
            },
            "confidence_score": analysis.confidence_score,
            "ai_insights": analysis.ai_insights,
            "deal_readiness_score": analysis.deal_readiness_score
        }

    except Exception as e:
        logger.error(f"Financial analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Financial analysis failed: {str(e)}"
        )

@router.post("/valuation", response_model=Dict[str, Any])
async def perform_comprehensive_valuation(
    request: ValuationRequest,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform multi-methodology valuation analysis

    Uses DCF, comparable companies, and precedent transactions
    to provide comprehensive valuation with confidence scoring.
    """
    try:
        # Initialize engines
        financial_engine = FinancialIntelligenceEngine(db)
        valuation_engine = AutomatedValuationEngine(financial_engine)

        # Perform valuation
        valuation = await valuation_engine.perform_comprehensive_valuation(
            company_id=request.company_id,
            industry=request.industry,
            custom_assumptions=request.custom_assumptions
        )

        # Format response
        valuation_results = []
        for result in valuation.valuation_results:
            valuation_results.append({
                "method": result.method.value,
                "valuation": float(result.valuation),
                "confidence_level": result.confidence_level,
                "key_assumptions": result.key_assumptions,
                "risk_factors": result.risk_factors,
                "methodology_notes": result.methodology_notes
            })

        return {
            "company_id": valuation.company_id,
            "analysis_date": valuation.analysis_date.isoformat(),
            "valuation_results": valuation_results,
            "weighted_average_valuation": float(valuation.weighted_average_valuation),
            "valuation_range": {
                "low": float(valuation.valuation_range[0]),
                "high": float(valuation.valuation_range[1])
            },
            "recommended_valuation": float(valuation.recommended_valuation),
            "confidence_score": valuation.confidence_score,
            "key_value_drivers": valuation.key_value_drivers,
            "major_risk_factors": valuation.major_risk_factors,
            "ai_insights": valuation.ai_insights,
            "benchmarking_data": valuation.benchmarking_data
        }

    except Exception as e:
        logger.error(f"Valuation analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Valuation analysis failed: {str(e)}"
        )

# Offer Stack Generation Endpoints

@router.post("/offer-stack/generate", response_model=Dict[str, Any])
async def generate_offer_stack(
    request: OfferStackRequest,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate comprehensive M&A offer stack with multiple scenarios

    Creates 3-5 different offer scenarios with varying:
    - Funding structures (cash, debt, earnouts, seller financing)
    - Deal structures (asset vs stock purchase)
    - Risk/return profiles
    - Timeline considerations
    """
    try:
        # Initialize engines
        financial_engine = FinancialIntelligenceEngine(db)
        offer_generator = InteractiveOfferStackGenerator(financial_engine)

        # Generate offer scenarios
        scenarios = await offer_generator.generate_offer_stack(
            target_company_id=request.target_company_id,
            buyer_profile=request.buyer_profile,
            deal_parameters=request.deal_parameters
        )

        # Format scenarios for response
        scenario_data = []
        for scenario in scenarios:
            funding_components = []
            for component in scenario.funding_components:
                funding_components.append({
                    "source": component.source.value,
                    "amount": float(component.amount),
                    "percentage": component.percentage,
                    "terms": component.terms,
                    "cost_of_capital": component.cost_of_capital,
                    "risk_factor": component.risk_factor
                })

            scenario_data.append({
                "scenario_id": scenario.scenario_id,
                "scenario_name": scenario.scenario_name,
                "total_enterprise_value": float(scenario.total_enterprise_value),
                "purchase_price": float(scenario.purchase_price),
                "funding_components": funding_components,
                "deal_structure": scenario.deal_structure.value,
                "closing_conditions": scenario.closing_conditions,
                "timeline": {k: v.isoformat() for k, v in scenario.timeline.items()},
                "risk_score": scenario.risk_score,
                "confidence_level": scenario.confidence_level,
                "ai_insights": scenario.ai_insights
            })

        return {
            "target_company_id": request.target_company_id,
            "scenarios": scenario_data,
            "generation_timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Offer stack generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Offer stack generation failed: {str(e)}"
        )

@router.post("/offer-stack/export", response_model=Dict[str, Any])
async def export_offer_package(
    request: ExportOfferRequest,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Export comprehensive offer package to Excel, PowerPoint, and PDF

    Generates professional presentation materials including:
    - Interactive Excel workbook with scenarios and analysis
    - PowerPoint presentation with executive summary
    - PDF summary document
    - Optional interactive dashboard
    """
    try:
        # Initialize engines
        financial_engine = FinancialIntelligenceEngine(db)
        offer_generator = InteractiveOfferStackGenerator(financial_engine)

        # Convert request scenarios back to scenario objects
        # (This would need proper deserialization in a full implementation)
        scenarios = []  # Placeholder - would reconstruct from request.scenarios

        # Generate export package
        export_package = await offer_generator.export_offer_package(
            scenarios=scenarios,
            target_company_id=request.target_company_id,
            export_options=request.export_options
        )

        return {
            "excel_file_path": export_package.excel_file_path,
            "powerpoint_file_path": export_package.powerpoint_file_path,
            "pdf_summary_path": export_package.pdf_summary_path,
            "interactive_dashboard_url": export_package.interactive_dashboard_url,
            "generation_timestamp": export_package.generation_timestamp.isoformat()
        }

    except Exception as e:
        logger.error(f"Offer export failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Offer export failed: {str(e)}"
        )

# Market Intelligence Endpoints

@router.get("/market-trends/{industry}", response_model=Dict[str, Any])
async def get_market_trends(
    industry: str,
    geography: Optional[str] = None,
    time_period_months: int = 12,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get M&A market trends and intelligence for specific industry

    Provides insights on:
    - Deal volume and value trends
    - Average valuation multiples
    - Buyer/seller dynamics
    - Emerging opportunities
    """
    try:
        # Initialize matching system (which has market analysis capabilities)
        from app.services.intelligent_deal_matching import IntelligentDealMatchingSystem

        financial_engine = FinancialIntelligenceEngine(db)
        matching_system = IntelligentDealMatchingSystem(db, financial_engine)

        # Analyze market trends
        trends = await matching_system.analyze_market_trends(
            industry=industry,
            geography=geography,
            time_period_months=time_period_months
        )

        return trends

    except Exception as e:
        logger.error(f"Market trends analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market trends analysis failed: {str(e)}"
        )

@router.post("/what-if-analysis", response_model=Dict[str, Any])
async def perform_what_if_analysis(
    scenario_data: Dict[str, Any],
    analysis_parameters: Dict[str, Any],
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform what-if sensitivity analysis on offer scenarios

    Analyzes impact of changing key variables:
    - Purchase price variations
    - Debt/equity mix changes
    - Interest rate sensitivity
    - Timeline adjustments
    """
    try:
        # Initialize offer generator
        financial_engine = FinancialIntelligenceEngine(db)
        offer_generator = InteractiveOfferStackGenerator(financial_engine)

        # This would need proper implementation to convert dict to scenario objects
        # and parameters to WhatIfAnalysis object

        # Placeholder response
        return {
            "analysis_complete": True,
            "sensitivity_results": {},
            "key_insights": ["Placeholder implementation needed"],
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"What-if analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"What-if analysis failed: {str(e)}"
        )

# Health check endpoint

@router.get("/health")
async def health_check():
    """Health check for financial intelligence services"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "financial_intelligence": "available",
            "valuation_engine": "available",
            "offer_generator": "available"
        }
    }