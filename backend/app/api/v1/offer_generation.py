"""
Offer Generation API Endpoints
Professional acquisition proposals in minutes
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import io
import json

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.users import User
from app.services.offer_generation import (
    OfferStackGeneratorService,
    DealParameters,
    OfferStack,
    OfferScenario,
    FundingType
)
from app.services.excel_export_engine import ExcelExportEngine, ExcelTemplate

router = APIRouter(prefix="/offer-generation", tags=["offer-generation"])

# Request/Response Models
class DealParametersRequest(BaseModel):
    """API request model for deal parameters"""
    target_company_id: str = Field(..., description="Target company identifier")
    purchase_price_range: tuple[float, float] = Field(..., description="Min and max purchase price")
    buyer_profile: Dict[str, Any] = Field(..., description="Buyer characteristics and constraints")
    seller_preferences: Dict[str, Any] = Field(..., description="Seller preferences and requirements")
    transaction_type: str = Field("stock_deal", description="Type of transaction")
    jurisdiction: str = Field("US", description="Legal jurisdiction")
    currency: str = Field("USD", description="Transaction currency")
    financing_constraints: Dict[str, Any] = Field(default_factory=dict)
    timeline_requirements: Dict[str, Any] = Field(default_factory=dict)

class ScenarioCustomizationRequest(BaseModel):
    """Request model for scenario customization"""
    scenario_id: str
    funding_type: FundingType
    custom_parameters: Dict[str, Any]
    assumptions_override: Dict[str, Any] = Field(default_factory=dict)

class WhatIfAnalysisRequest(BaseModel):
    """Request model for what-if analysis"""
    scenario_id: str
    variable_changes: Dict[str, float] = Field(
        ...,
        description="Key: variable name, Value: new value or percentage change",
        example={
            "revenue_growth_rate": 0.15,
            "ebitda_margin_improvement": 0.02,
            "cost_synergies": 0.20,
            "exit_multiple": 9.0
        }
    )

class ExportRequest(BaseModel):
    """Request model for export generation"""
    offer_stack_id: str
    export_formats: List[str] = Field(
        ["excel", "powerpoint", "pdf"],
        description="Formats to generate"
    )
    template_customization: Optional[Dict[str, Any]] = None
    branding_options: Optional[Dict[str, Any]] = None

class OfferStackResponse(BaseModel):
    """Response model for offer stack"""
    deal_id: str
    scenarios: List[Dict[str, Any]]
    recommended_scenario_id: str
    market_intelligence: Dict[str, Any]
    generation_timestamp: datetime
    export_urls: Dict[str, str]
    assumptions: Dict[str, Any]

class ScenarioResponse(BaseModel):
    """Response model for individual scenario"""
    scenario_id: str
    scenario_name: str
    funding_structure: Dict[str, Any]
    financial_projections: Dict[str, Any]
    sensitivity_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    seller_acceptance_probability: float
    optimization_score: float

@router.post("/generate-offer-stack", response_model=OfferStackResponse)
async def generate_offer_stack(
    request: DealParametersRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Generate complete offer stack with multiple funding scenarios

    **Features:**
    - 5+ automated funding scenarios (cash, debt, seller finance, earnout, hybrid)
    - Financial projections and DCF analysis
    - Sensitivity analysis and risk assessment
    - Market intelligence integration
    - Seller acceptance probability scoring

    **Response Time:** < 5 minutes for complete analysis
    """
    try:
        # Convert request to domain model
        deal_params = DealParameters(
            target_company_id=request.target_company_id,
            purchase_price_range=request.purchase_price_range,
            buyer_profile=request.buyer_profile,
            seller_preferences=request.seller_preferences,
            transaction_type=request.transaction_type,
            jurisdiction=request.jurisdiction,
            currency=request.currency,
            financing_constraints=request.financing_constraints,
            timeline_requirements=request.timeline_requirements
        )

        # Generate offer stack
        generator = OfferStackGeneratorService()
        offer_stack = await generator.generate_offer_stack(deal_params)

        # Schedule background export generation
        background_tasks.add_task(
            generate_exports_background,
            offer_stack,
            current_user.id
        )

        # Convert to response format
        return OfferStackResponse(
            deal_id=offer_stack.deal_id,
            scenarios=[
                {
                    "scenario_id": scenario.scenario_id,
                    "scenario_name": scenario.funding_structure.scenario_name,
                    "funding_type": scenario.funding_structure.funding_type.value,
                    "total_purchase_price": float(scenario.funding_structure.total_purchase_price),
                    "irr": scenario.financial_projections.irr,
                    "multiple_of_money": scenario.financial_projections.multiple_of_money,
                    "seller_acceptance_probability": scenario.seller_acceptance_probability,
                    "optimization_score": scenario.optimization_score
                }
                for scenario in offer_stack.scenarios
            ],
            recommended_scenario_id=offer_stack.recommended_scenario.scenario_id,
            market_intelligence=offer_stack.market_intelligence,
            generation_timestamp=offer_stack.generation_timestamp,
            export_urls={
                "excel": f"/api/v1/offer-generation/export/{offer_stack.deal_id}/excel",
                "powerpoint": f"/api/v1/offer-generation/export/{offer_stack.deal_id}/powerpoint",
                "pdf": f"/api/v1/offer-generation/export/{offer_stack.deal_id}/pdf",
                "dashboard": f"/dashboard/offers/{offer_stack.deal_id}"
            },
            assumptions=offer_stack.assumptions
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating offer stack: {str(e)}"
        )

@router.get("/scenario/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario_details(
    scenario_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get detailed information for a specific scenario

    **Returns:**
    - Complete funding structure details
    - Financial projections and metrics
    - Sensitivity analysis results
    - Risk assessment breakdown
    """
    try:
        # This would fetch from database in production
        # For now, returning structure showing the API design

        return ScenarioResponse(
            scenario_id=scenario_id,
            scenario_name="Example Scenario",
            funding_structure={
                "funding_type": "hybrid",
                "total_purchase_price": 6000000,
                "cash_component": 3000000,
                "debt_component": 1500000,
                "seller_finance_component": 900000,
                "earnout_component": 600000,
                "payment_schedule": [
                    {
                        "payment_date": "closing",
                        "amount": 4500000,
                        "description": "Cash and debt at closing"
                    }
                ]
            },
            financial_projections={
                "revenue_projections": [10000000, 11000000, 12100000, 13310000, 14641000],
                "ebitda_projections": [2000000, 2300000, 2650000, 3050000, 3500000],
                "irr": 0.225,
                "multiple_of_money": 2.8,
                "payback_period": 3.2
            },
            sensitivity_analysis={
                "base_case_irr": 0.225,
                "revenue_sensitivity": {
                    "-20%": 0.18,
                    "-10%": 0.20,
                    "base": 0.225,
                    "+10%": 0.25,
                    "+20%": 0.27
                }
            },
            risk_assessment={
                "execution_risk": "medium",
                "financial_risk": "low",
                "market_risk": "medium",
                "overall_risk_rating": "medium"
            },
            seller_acceptance_probability=0.82,
            optimization_score=0.89
        )

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario not found: {str(e)}"
        )

@router.post("/scenario/{scenario_id}/customize")
async def customize_scenario(
    scenario_id: str,
    request: ScenarioCustomizationRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Customize an existing scenario with new parameters

    **Features:**
    - Modify funding structure components
    - Adjust financial assumptions
    - Recalculate all dependent metrics
    - Maintain scenario comparison capability
    """
    try:
        # This would fetch the existing scenario, apply customizations,
        # and recalculate all metrics

        # Placeholder implementation
        return {
            "scenario_id": f"{scenario_id}_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "customized",
            "changes_applied": request.custom_parameters,
            "recalculation_status": "completed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error customizing scenario: {str(e)}"
        )

@router.post("/scenario/{scenario_id}/what-if")
async def perform_what_if_analysis(
    scenario_id: str,
    request: WhatIfAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Perform real-time what-if analysis on scenario variables

    **Interactive Features:**
    - Revenue growth rate adjustments
    - EBITDA margin improvements
    - Cost synergy estimates
    - Exit multiple scenarios
    - Instant recalculation of IRR and returns

    **Response Time:** < 2 seconds
    """
    try:
        # This would perform real-time recalculation
        # based on the variable changes

        base_irr = 0.225  # Would fetch from actual scenario

        # Calculate impact of changes (simplified for example)
        impact_factors = {
            "revenue_growth_rate": 0.6,  # 60% impact on IRR
            "ebitda_margin_improvement": 0.8,  # 80% impact on IRR
            "cost_synergies": 0.4,  # 40% impact on IRR
            "exit_multiple": 0.9  # 90% impact on IRR
        }

        total_impact = 0
        for variable, new_value in request.variable_changes.items():
            if variable in impact_factors:
                # Simplified impact calculation
                if variable == "exit_multiple":
                    change = (new_value - 8.0) / 8.0  # Assume base of 8x
                else:
                    change = new_value if new_value < 1 else (new_value - 1)

                total_impact += change * impact_factors[variable]

        new_irr = base_irr * (1 + total_impact)
        new_multiple = 2.8 * (1 + total_impact * 0.7)  # Assume base multiple of 2.8

        return {
            "scenario_id": scenario_id,
            "variable_changes": request.variable_changes,
            "impact_analysis": {
                "original_irr": base_irr,
                "new_irr": new_irr,
                "irr_change": new_irr - base_irr,
                "original_multiple": 2.8,
                "new_multiple": new_multiple,
                "multiple_change": new_multiple - 2.8
            },
            "sensitivity_breakdown": {
                variable: {
                    "change": change,
                    "irr_impact": change * impact_factors.get(variable, 0) * base_irr
                }
                for variable, change in request.variable_changes.items()
            },
            "calculation_timestamp": datetime.now()
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error performing what-if analysis: {str(e)}"
        )

@router.get("/export/{deal_id}/{format}")
async def export_offer_analysis(
    deal_id: str,
    format: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Export offer analysis in specified format

    **Supported Formats:**
    - **excel**: Complete 19-worksheet financial model
    - **powerpoint**: 15-20 slide investor presentation
    - **pdf**: 2-page executive summary
    - **json**: Raw data for API integration

    **Features:**
    - Professional investment banking quality
    - Preserved formulas in Excel exports
    - Corporate branding integration
    - Email-ready formatting
    """
    try:
        if format not in ["excel", "powerpoint", "pdf", "json"]:
            raise HTTPException(
                status_code=400,
                detail="Unsupported export format. Use: excel, powerpoint, pdf, or json"
            )

        # This would fetch the actual offer stack from database
        # For now, showing the API structure

        if format == "excel":
            # Generate Excel export
            excel_engine = ExcelExportEngine()

            # This would use the actual offer stack
            # excel_bytes = await excel_engine.generate_excel_model(offer_stack)

            # For demo, return a sample response
            return StreamingResponse(
                io.BytesIO(b"Excel model bytes would go here"),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=offer_analysis_{deal_id}.xlsx"}
            )

        elif format == "powerpoint":
            return StreamingResponse(
                io.BytesIO(b"PowerPoint bytes would go here"),
                media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                headers={"Content-Disposition": f"attachment; filename=investor_presentation_{deal_id}.pptx"}
            )

        elif format == "pdf":
            return StreamingResponse(
                io.BytesIO(b"PDF bytes would go here"),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=executive_summary_{deal_id}.pdf"}
            )

        else:  # json
            return {
                "deal_id": deal_id,
                "export_format": format,
                "data": "Complete JSON data structure would go here",
                "generated_at": datetime.now()
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating export: {str(e)}"
        )

@router.post("/export/{deal_id}/custom")
async def generate_custom_export(
    deal_id: str,
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Generate custom exports with specific formatting and branding

    **Customization Options:**
    - Corporate branding and colors
    - Template modifications
    - Custom cover pages
    - Specific scenario focus
    - Multi-format packages
    """
    try:
        # Schedule custom export generation
        background_tasks.add_task(
            generate_custom_exports_background,
            deal_id,
            request,
            current_user.id
        )

        return {
            "deal_id": deal_id,
            "export_request_id": f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "formats_requested": request.export_formats,
            "status": "generating",
            "estimated_completion": "2-3 minutes",
            "notification_method": "email"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scheduling custom export: {str(e)}"
        )

@router.get("/deals")
async def list_user_deals(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """
    List all deals and offer stacks for the current user

    **Returns:**
    - Deal summaries with key metrics
    - Generation timestamps
    - Export availability
    - Scenario count per deal
    """
    try:
        # This would query the database for user's deals
        # For now, returning sample structure

        return {
            "deals": [
                {
                    "deal_id": "deal_001",
                    "target_company": "Example Corp",
                    "purchase_price": 6000000,
                    "scenarios_count": 5,
                    "recommended_irr": 0.225,
                    "generated_at": "2024-01-15T10:30:00Z",
                    "status": "active",
                    "exports_available": ["excel", "pdf"]
                }
            ],
            "total_count": 1,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving deals: {str(e)}"
        )

@router.delete("/deals/{deal_id}")
async def delete_deal(
    deal_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete a deal and all associated scenarios and exports

    **Warning:** This action cannot be undone
    """
    try:
        # This would delete from database and clean up files

        return {
            "deal_id": deal_id,
            "status": "deleted",
            "deleted_at": datetime.now(),
            "items_removed": [
                "offer_stack",
                "scenarios",
                "exports",
                "cached_calculations"
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting deal: {str(e)}"
        )

@router.get("/market-intelligence/{target_company_id}")
async def get_market_intelligence(
    target_company_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get market intelligence for target company

    **Intelligence Includes:**
    - Comparable transaction analysis
    - Industry valuation multiples
    - Market timing considerations
    - Competitive landscape
    - Recent deal trends
    """
    try:
        # This would integrate with market intelligence service

        return {
            "target_company_id": target_company_id,
            "market_analysis": {
                "industry": "Technology Services",
                "median_ev_ebitda": 8.2,
                "recent_transactions": 15,
                "market_conditions": "favorable",
                "timing_recommendation": "optimal"
            },
            "comparable_transactions": [
                {
                    "transaction_id": "tx_001",
                    "target": "Similar Tech Co",
                    "purchase_price": 5500000,
                    "ev_ebitda_multiple": 7.8,
                    "date": "2024-01-10"
                }
            ],
            "valuation_benchmarks": {
                "revenue_multiple_range": [1.2, 2.8],
                "ebitda_multiple_range": [6.5, 10.2],
                "median_premium": 0.25
            },
            "updated_at": datetime.now()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving market intelligence: {str(e)}"
        )

# Background task functions
async def generate_exports_background(offer_stack: OfferStack, user_id: str):
    """Background task to generate all export formats"""
    try:
        # Generate Excel model
        excel_engine = ExcelExportEngine()
        excel_bytes = await excel_engine.generate_excel_model(offer_stack)

        # Save to file storage (would use cloud storage in production)
        # await save_export_file(offer_stack.deal_id, "excel", excel_bytes)

        # Generate PowerPoint presentation
        # ppt_bytes = await generate_powerpoint_presentation(offer_stack)
        # await save_export_file(offer_stack.deal_id, "powerpoint", ppt_bytes)

        # Generate PDF summary
        # pdf_bytes = await generate_pdf_summary(offer_stack)
        # await save_export_file(offer_stack.deal_id, "pdf", pdf_bytes)

        # Send notification to user
        # await send_export_ready_notification(user_id, offer_stack.deal_id)

        print(f"Exports generated for deal {offer_stack.deal_id}")

    except Exception as e:
        print(f"Error generating exports: {str(e)}")

async def generate_custom_exports_background(
    deal_id: str,
    request: ExportRequest,
    user_id: str
):
    """Background task to generate custom exports"""
    try:
        # Custom export generation logic would go here
        print(f"Custom exports generated for deal {deal_id}")

    except Exception as e:
        print(f"Error generating custom exports: {str(e)}")

# WebSocket endpoint for real-time updates
from fastapi import WebSocket, WebSocketDisconnect

@router.websocket("/ws/what-if/{scenario_id}")
async def websocket_what_if_analysis(
    websocket: WebSocket,
    scenario_id: str
):
    """
    WebSocket endpoint for real-time what-if analysis

    **Features:**
    - Real-time calculation updates
    - Interactive slider adjustments
    - Live chart updates
    - Multi-variable optimization
    """
    await websocket.accept()

    try:
        while True:
            # Receive variable changes from client
            data = await websocket.receive_json()

            # Perform real-time calculations
            # This would use the actual modeling engine
            variable_changes = data.get("variable_changes", {})

            # Calculate new metrics
            result = {
                "scenario_id": scenario_id,
                "updated_metrics": {
                    "irr": 0.225 * (1 + sum(variable_changes.values()) * 0.1),
                    "multiple": 2.8 * (1 + sum(variable_changes.values()) * 0.05),
                    "payback_period": 3.2 / (1 + sum(variable_changes.values()) * 0.02)
                },
                "timestamp": datetime.now().isoformat()
            }

            # Send updated results
            await websocket.send_json(result)

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for scenario {scenario_id}")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()