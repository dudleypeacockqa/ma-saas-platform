"""
Deal Intelligence Platform API - Sprint 16
RESTful API endpoints for deal intelligence, transaction orchestration, predictive analytics, and due diligence automation
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Body, Path
from pydantic import BaseModel, Field

from app.deal_intelligence import (
    get_deal_intelligence_engine,
    get_transaction_orchestrator,
    get_predictive_analytics,
    get_due_diligence_automation
)
from app.deal_intelligence.deal_intelligence_engine import (
    DealType, DealStage, IndustryVertical, DealProfile, StrategicFitLevel
)
from app.deal_intelligence.transaction_orchestration import (
    WorkflowStatus, TaskStatus, TaskPriority, StakeholderRole
)
from app.deal_intelligence.predictive_analytics import (
    PredictionType, ScenarioType, ForecastHorizon
)
from app.deal_intelligence.due_diligence_automation import (
    DocumentType, RiskLevel, AnalysisStatus, DataRoomAccess, ReviewPriority
)

router = APIRouter()

# Request/Response Models for Deal Intelligence
class DealAnalysisRequest(BaseModel):
    deal_id: str
    deal_type: str
    target_company: str
    acquirer_company: str
    industry: str
    deal_value: float
    currency: str = "USD"
    key_metrics: Dict[str, Any] = Field(default_factory=dict)
    strategic_rationale: str = ""

class DealScoringRequest(BaseModel):
    deal_profile: DealAnalysisRequest
    market_region: str = "global"
    custom_weights: Optional[Dict[str, float]] = None

# Request/Response Models for Transaction Orchestration
class WorkflowCreationRequest(BaseModel):
    deal_id: str
    deal_type: str
    stakeholder_assignments: Dict[str, str]
    customizations: Optional[Dict[str, Any]] = None

class TaskUpdateRequest(BaseModel):
    task_updates: List[Dict[str, Any]]
    progress_message: Optional[str] = None
    notify_stakeholders: List[str] = Field(default_factory=list)

class StakeholderMeetingRequest(BaseModel):
    workflow_id: str
    participants: List[str]
    subject: str
    agenda: str
    scheduled_at: datetime

# Request/Response Models for Predictive Analytics
class DealPredictionRequest(BaseModel):
    deal_id: str
    deal_data: Dict[str, Any]
    prediction_types: List[str]
    include_scenarios: bool = True

class PortfolioOptimizationRequest(BaseModel):
    portfolio_data: Dict[str, Any]
    constraints: Dict[str, Any]
    optimization_objective: str = "sharpe_ratio"

class MarketForecastRequest(BaseModel):
    industry: str
    region: str = "global"
    forecast_horizon: str = "medium_term"

# Request/Response Models for Due Diligence
class DocumentBatchRequest(BaseModel):
    data_room_id: str
    documents: List[Dict[str, Any]]

class DataRoomCreationRequest(BaseModel):
    deal_id: str
    administrator: str
    users: List[Dict[str, Any]]

class QAItemRequest(BaseModel):
    question: str
    category: str
    priority: str
    assigned_to: Optional[str] = None

# Deal Intelligence Endpoints
@router.post("/deal-intelligence/analyze",
             summary="Analyze Deal Opportunity",
             description="Perform comprehensive AI-powered analysis of deal opportunity")
async def analyze_deal_opportunity(request: DealAnalysisRequest) -> Dict[str, Any]:
    deal_intelligence = get_deal_intelligence_engine()

    # Convert request to DealProfile
    deal_profile = DealProfile(
        deal_id=request.deal_id,
        deal_type=DealType(request.deal_type),
        target_company=request.target_company,
        acquirer_company=request.acquirer_company,
        industry=IndustryVertical(request.industry),
        deal_value=request.deal_value,
        currency=request.currency,
        key_metrics=request.key_metrics,
        strategic_rationale=request.strategic_rationale
    )

    try:
        analysis_result = await deal_intelligence.analyze_deal_opportunity(deal_profile)
        return {
            "status": "success",
            "analysis": analysis_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/deal-intelligence/score",
             summary="Score Deal Opportunity",
             description="Calculate AI-powered deal score and recommendations")
async def score_deal_opportunity(request: DealScoringRequest) -> Dict[str, Any]:
    deal_intelligence = get_deal_intelligence_engine()

    # Convert request to DealProfile
    deal_profile = DealProfile(
        deal_id=request.deal_profile.deal_id,
        deal_type=DealType(request.deal_profile.deal_type),
        target_company=request.deal_profile.target_company,
        acquirer_company=request.deal_profile.acquirer_company,
        industry=IndustryVertical(request.deal_profile.industry),
        deal_value=request.deal_profile.deal_value,
        currency=request.deal_profile.currency,
        key_metrics=request.deal_profile.key_metrics,
        strategic_rationale=request.deal_profile.strategic_rationale
    )

    try:
        # Get market context
        market_context = deal_intelligence.market_intelligence.analyze_market_conditions(
            deal_profile.industry, request.market_region
        )

        # Calculate deal score
        deal_score = deal_intelligence.scoring_engine.calculate_deal_score(
            deal_profile, market_context
        )

        return {
            "status": "success",
            "deal_score": deal_score.__dict__,
            "market_context": market_context.__dict__
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

@router.get("/deal-intelligence/market-analysis/{industry}",
            summary="Get Market Intelligence",
            description="Retrieve comprehensive market analysis for industry")
async def get_market_intelligence(
    industry: str = Path(..., description="Industry vertical"),
    region: str = Query("global", description="Geographic region")
) -> Dict[str, Any]:
    deal_intelligence = get_deal_intelligence_engine()

    try:
        industry_enum = IndustryVertical(industry)
        market_context = deal_intelligence.market_intelligence.analyze_market_conditions(
            industry_enum, region
        )

        return {
            "status": "success",
            "market_analysis": market_context.__dict__
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid industry: {industry}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market analysis failed: {str(e)}")

# Transaction Orchestration Endpoints
@router.post("/orchestration/workflows",
             summary="Create Transaction Workflow",
             description="Create and initiate transaction workflow with stakeholder assignments")
async def create_transaction_workflow(request: WorkflowCreationRequest) -> Dict[str, Any]:
    orchestrator = get_transaction_orchestrator()

    try:
        result = await orchestrator.orchestrate_transaction(
            deal_id=request.deal_id,
            deal_type=request.deal_type,
            stakeholder_assignments=request.stakeholder_assignments,
            customizations=request.customizations
        )

        return {
            "status": "success",
            "orchestration_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow creation failed: {str(e)}")

@router.get("/orchestration/workflows/{workflow_id}",
            summary="Get Workflow Status",
            description="Retrieve comprehensive workflow status and progress")
async def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    orchestrator = get_transaction_orchestrator()

    try:
        status = orchestrator.workflow_engine.get_workflow_status(workflow_id)
        if not status:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return {
            "status": "success",
            "workflow_status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@router.put("/orchestration/workflows/{workflow_id}/progress",
            summary="Update Workflow Progress",
            description="Update workflow progress with task completions and status changes")
async def update_workflow_progress(workflow_id: str, request: TaskUpdateRequest) -> Dict[str, Any]:
    orchestrator = get_transaction_orchestrator()

    try:
        result = await orchestrator.update_workflow_progress(
            workflow_id=workflow_id,
            updates=request.dict()
        )

        return {
            "status": "success",
            "update_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Progress update failed: {str(e)}")

@router.get("/orchestration/tasks",
            summary="Get Active Tasks",
            description="Retrieve active tasks, optionally filtered by assignee")
async def get_active_tasks(assignee: Optional[str] = Query(None)) -> Dict[str, Any]:
    orchestrator = get_transaction_orchestrator()

    try:
        tasks = orchestrator.workflow_engine.get_active_tasks(assignee)

        return {
            "status": "success",
            "active_tasks": tasks,
            "total_count": len(tasks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task retrieval failed: {str(e)}")

@router.get("/orchestration/dashboard",
            summary="Get Orchestration Dashboard",
            description="Comprehensive orchestration dashboard with metrics and activity")
async def get_orchestration_dashboard(stakeholder_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    orchestrator = get_transaction_orchestrator()

    try:
        dashboard = await orchestrator.get_orchestration_dashboard(stakeholder_id)

        return {
            "status": "success",
            "dashboard": dashboard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard retrieval failed: {str(e)}")

@router.post("/orchestration/meetings",
             summary="Schedule Stakeholder Meeting",
             description="Schedule video conference meeting for stakeholders")
async def schedule_stakeholder_meeting(request: StakeholderMeetingRequest) -> Dict[str, Any]:
    orchestrator = get_transaction_orchestrator()

    try:
        meeting_id = orchestrator.collaboration_hub.schedule_stakeholder_meeting(
            workflow_id=request.workflow_id,
            participants=request.participants,
            subject=request.subject,
            agenda=request.agenda,
            scheduled_at=request.scheduled_at
        )

        return {
            "status": "success",
            "meeting_id": meeting_id,
            "scheduled_at": request.scheduled_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meeting scheduling failed: {str(e)}")

@router.get("/orchestration/workflows/{workflow_id}/communications",
            summary="Get Workflow Communications",
            description="Retrieve communication history for workflow")
async def get_workflow_communications(
    workflow_id: str,
    event_type: Optional[str] = Query(None)
) -> Dict[str, Any]:
    orchestrator = get_transaction_orchestrator()

    try:
        from app.deal_intelligence.transaction_orchestration import CommunicationChannel
        channel_filter = CommunicationChannel(event_type) if event_type else None

        communications = orchestrator.collaboration_hub.get_workflow_communications(
            workflow_id, channel_filter
        )

        return {
            "status": "success",
            "communications": communications,
            "total_count": len(communications)
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Communications retrieval failed: {str(e)}")

# Predictive Analytics Endpoints
@router.post("/analytics/predict",
             summary="Generate Deal Predictions",
             description="Generate comprehensive AI predictions for deal outcomes")
async def predict_deal_outcomes(request: DealPredictionRequest) -> Dict[str, Any]:
    predictive_analytics = get_predictive_analytics()

    try:
        analysis = await predictive_analytics.comprehensive_deal_analysis(
            deal_id=request.deal_id,
            deal_data=request.deal_data
        )

        return {
            "status": "success",
            "prediction_analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/analytics/portfolio/optimize",
             summary="Optimize Deal Portfolio",
             description="Generate optimal portfolio allocation recommendations")
async def optimize_deal_portfolio(request: PortfolioOptimizationRequest) -> Dict[str, Any]:
    predictive_analytics = get_predictive_analytics()

    try:
        optimization = await predictive_analytics.optimize_deal_portfolio(
            portfolio_data=request.portfolio_data,
            optimization_constraints=request.constraints
        )

        return {
            "status": "success",
            "optimization_result": optimization
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio optimization failed: {str(e)}")

@router.post("/analytics/market/forecast",
             summary="Generate Market Forecast",
             description="Generate AI-powered market forecasts and trend analysis")
async def generate_market_forecast(request: MarketForecastRequest) -> Dict[str, Any]:
    predictive_analytics = get_predictive_analytics()

    try:
        forecast_horizon = ForecastHorizon(request.forecast_horizon)
        forecast = predictive_analytics.market_forecasting.generate_market_forecast(
            industry=request.industry,
            region=request.region,
            horizon=forecast_horizon
        )

        return {
            "status": "success",
            "market_forecast": forecast.__dict__
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid forecast horizon: {request.forecast_horizon}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market forecast failed: {str(e)}")

@router.post("/analytics/models/train",
             summary="Train Prediction Model",
             description="Train AI prediction model with historical data")
async def train_prediction_model(
    model_id: str = Query(..., description="Model identifier"),
    prediction_type: str = Query(..., description="Type of prediction"),
    training_data: List[Dict[str, Any]] = Body(..., description="Historical training data")
) -> Dict[str, Any]:
    predictive_analytics = get_predictive_analytics()

    try:
        prediction_type_enum = PredictionType(prediction_type)

        # Create model if doesn't exist
        model_created = predictive_analytics.deal_forecasting.create_prediction_model(
            model_id=model_id,
            name=f"Custom {prediction_type} Model",
            prediction_type=prediction_type_enum
        )

        # Train model
        training_success = predictive_analytics.deal_forecasting.train_model(
            model_id=model_id,
            training_data=training_data
        )

        return {
            "status": "success",
            "model_created": model_created,
            "training_completed": training_success,
            "training_data_size": len(training_data)
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid prediction type: {prediction_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")

@router.get("/analytics/models",
            summary="List Prediction Models",
            description="Retrieve list of available prediction models")
async def list_prediction_models() -> Dict[str, Any]:
    predictive_analytics = get_predictive_analytics()

    try:
        models = []
        for model_id, model in predictive_analytics.deal_forecasting.prediction_models.items():
            models.append({
                "model_id": model.model_id,
                "name": model.name,
                "prediction_type": model.prediction_type.value,
                "algorithm": model.algorithm,
                "accuracy_score": model.accuracy_score,
                "training_data_size": model.training_data_size,
                "last_trained": model.last_trained.isoformat()
            })

        return {
            "status": "success",
            "models": models,
            "total_count": len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model listing failed: {str(e)}")

# Due Diligence Automation Endpoints
@router.post("/due-diligence/initialize",
             summary="Initialize Due Diligence Process",
             description="Set up automated due diligence process with data room and analysis models")
async def initialize_due_diligence(request: DataRoomCreationRequest) -> Dict[str, Any]:
    dd_automation = get_due_diligence_automation()

    try:
        result = await dd_automation.initialize_due_diligence_process(
            deal_id=request.deal_id,
            data_room_config={
                "administrator": request.administrator,
                "users": request.users
            }
        )

        return {
            "status": "success",
            "initialization_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DD initialization failed: {str(e)}")

@router.post("/due-diligence/documents/batch-analyze",
             summary="Batch Analyze Documents",
             description="Perform AI-powered batch analysis of due diligence documents")
async def batch_analyze_documents(request: DocumentBatchRequest) -> Dict[str, Any]:
    dd_automation = get_due_diligence_automation()

    try:
        result = await dd_automation.process_document_batch(
            data_room_id=request.data_room_id,
            documents=request.documents
        )

        return {
            "status": "success",
            "analysis_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@router.post("/due-diligence/documents/{document_id}/analyze",
             summary="Analyze Single Document",
             description="Perform comprehensive AI analysis on single document")
async def analyze_single_document(
    document_id: str,
    document_content: str = Body(..., description="Document content"),
    document_type: str = Body(..., description="Document type"),
    analysis_types: List[str] = Body(..., description="Types of analysis to perform")
) -> Dict[str, Any]:
    dd_automation = get_due_diligence_automation()

    try:
        doc_type = DocumentType(document_type)
        analysis = dd_automation.document_analysis_engine.analyze_document(
            document_id=document_id,
            document_content=document_content,
            document_type=doc_type,
            analysis_types=analysis_types
        )

        return {
            "status": "success",
            "analysis": analysis.__dict__
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {document_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@router.get("/due-diligence/{deal_id}/summary",
            summary="Get Due Diligence Summary",
            description="Generate comprehensive due diligence summary and risk assessment")
async def get_due_diligence_summary(deal_id: str) -> Dict[str, Any]:
    dd_automation = get_due_diligence_automation()

    try:
        summary = await dd_automation.generate_due_diligence_summary(deal_id)

        return {
            "status": "success",
            "dd_summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DD summary generation failed: {str(e)}")

@router.get("/due-diligence/data-rooms/{data_room_id}/analytics",
            summary="Get Data Room Analytics",
            description="Retrieve comprehensive data room usage and activity analytics")
async def get_data_room_analytics(data_room_id: str) -> Dict[str, Any]:
    dd_automation = get_due_diligence_automation()

    try:
        analytics = dd_automation.data_room_manager.get_data_room_analytics(data_room_id)

        return {
            "status": "success",
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

@router.get("/due-diligence/data-rooms/{data_room_id}/documents",
            summary="Get User Accessible Documents",
            description="Retrieve documents accessible to specific user in data room")
async def get_user_documents(
    data_room_id: str,
    user_id: str = Query(..., description="User identifier")
) -> Dict[str, Any]:
    dd_automation = get_due_diligence_automation()

    try:
        documents = dd_automation.data_room_manager.get_user_accessible_documents(
            data_room_id, user_id
        )

        return {
            "status": "success",
            "documents": documents,
            "total_count": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document retrieval failed: {str(e)}")

@router.post("/due-diligence/qa/create",
             summary="Create Q&A Item",
             description="Create new question and answer item for due diligence")
async def create_qa_item(request: QAItemRequest) -> Dict[str, Any]:
    dd_automation = get_due_diligence_automation()

    try:
        from app.deal_intelligence.due_diligence_automation import QAItem
        import uuid

        qa_item = QAItem(
            qa_id=str(uuid.uuid4()),
            question=request.question,
            category=request.category,
            priority=ReviewPriority(request.priority),
            status="pending",
            assigned_to=request.assigned_to
        )

        created = dd_automation.qa_automation_engine.create_qa_item(qa_item)

        return {
            "status": "success",
            "qa_item_created": created,
            "qa_id": qa_item.qa_id
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid priority: {request.priority}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q&A creation failed: {str(e)}")

@router.get("/due-diligence/qa/pending",
            summary="Get Pending Q&A Items",
            description="Retrieve pending questions and answers")
async def get_pending_qa_items(
    assignee: Optional[str] = Query(None),
    priority: Optional[str] = Query(None)
) -> Dict[str, Any]:
    dd_automation = get_due_diligence_automation()

    try:
        priority_filter = ReviewPriority(priority) if priority else None
        pending_items = dd_automation.qa_automation_engine.get_pending_questions(
            assignee=assignee,
            priority=priority_filter
        )

        return {
            "status": "success",
            "pending_questions": pending_items,
            "total_count": len(pending_items)
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q&A retrieval failed: {str(e)}")

@router.post("/due-diligence/qa/{qa_id}/auto-response",
             summary="Generate Automated Response",
             description="Generate AI-powered automated response to Q&A item")
async def generate_auto_response(
    qa_id: str,
    include_document_analyses: bool = Query(True, description="Include document analysis data")
) -> Dict[str, Any]:
    dd_automation = get_due_diligence_automation()

    try:
        # Get document analyses if requested
        document_analyses = []
        if include_document_analyses:
            for analyses_list in dd_automation.document_analysis_engine.analysis_history.values():
                document_analyses.extend(analyses_list)

        response = dd_automation.qa_automation_engine.generate_automated_response(
            qa_id=qa_id,
            document_analyses=document_analyses
        )

        return {
            "status": "success",
            "response_generated": response is not None,
            "automated_response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-response generation failed: {str(e)}")

# Platform Analytics and Reporting
@router.get("/platform/analytics/overview",
            summary="Get Platform Analytics Overview",
            description="Comprehensive analytics overview across all platform components")
async def get_platform_analytics() -> Dict[str, Any]:
    deal_intelligence = get_deal_intelligence_engine()
    orchestrator = get_transaction_orchestrator()
    predictive_analytics = get_predictive_analytics()
    dd_automation = get_due_diligence_automation()

    try:
        # Deal intelligence metrics
        total_deals_analyzed = len(deal_intelligence.intelligence_cache)

        # Orchestration metrics
        orchestration_metrics = orchestrator._calculate_orchestration_metrics()

        # Predictive analytics metrics
        total_models = len(predictive_analytics.deal_forecasting.prediction_models)
        total_predictions = len(predictive_analytics.analytics_cache)

        # Due diligence metrics
        total_analyses = sum(
            len(analyses) for analyses in dd_automation.document_analysis_engine.analysis_history.values()
        )

        return {
            "status": "success",
            "platform_analytics": {
                "deal_intelligence": {
                    "total_deals_analyzed": total_deals_analyzed,
                    "intelligence_cache_size": len(deal_intelligence.intelligence_cache)
                },
                "transaction_orchestration": orchestration_metrics,
                "predictive_analytics": {
                    "total_models": total_models,
                    "total_predictions": total_predictions
                },
                "due_diligence": {
                    "total_document_analyses": total_analyses,
                    "total_data_rooms": len(dd_automation.data_room_manager.data_rooms)
                },
                "generated_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")

@router.get("/platform/health",
            summary="Platform Health Check",
            description="Check health status of all platform components")
async def platform_health_check() -> Dict[str, Any]:
    try:
        # Test each component
        components_status = {}

        # Deal Intelligence Engine
        try:
            deal_intelligence = get_deal_intelligence_engine()
            components_status["deal_intelligence"] = "healthy"
        except Exception as e:
            components_status["deal_intelligence"] = f"unhealthy: {str(e)}"

        # Transaction Orchestrator
        try:
            orchestrator = get_transaction_orchestrator()
            components_status["transaction_orchestration"] = "healthy"
        except Exception as e:
            components_status["transaction_orchestration"] = f"unhealthy: {str(e)}"

        # Predictive Analytics
        try:
            predictive_analytics = get_predictive_analytics()
            components_status["predictive_analytics"] = "healthy"
        except Exception as e:
            components_status["predictive_analytics"] = f"unhealthy: {str(e)}"

        # Due Diligence Automation
        try:
            dd_automation = get_due_diligence_automation()
            components_status["due_diligence_automation"] = "healthy"
        except Exception as e:
            components_status["due_diligence_automation"] = f"unhealthy: {str(e)}"

        # Overall health
        all_healthy = all(status == "healthy" for status in components_status.values())

        return {
            "status": "success",
            "overall_health": "healthy" if all_healthy else "degraded",
            "components": components_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")