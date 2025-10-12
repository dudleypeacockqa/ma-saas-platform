"""
AI Integration API - Sprint 9
API endpoints for AI-powered features and intelligent automation
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from app.core.deps import get_current_user, get_current_organization
from app.ai import (
    AIService, AIRequest, AIResponse, AITask, AIModel,
    DocumentIntelligenceService, DocumentAnalysis, ContentSummary,
    DealInsightsService, DealScore, MarketIntelligence,
    AutomationEngine, WorkflowTrigger, SmartNotification,
    AIAnalyticsService, PredictiveInsight, PerformanceMetric,
    get_ai_service, get_document_intelligence_service,
    get_deal_insights_service, get_automation_engine,
    get_ai_analytics_service
)
from app.ai.ai_service import analyze_document, score_deal, summarize_content, generate_insights
from app.ai.document_intelligence import DocumentType
from app.ai.deal_insights import DealCategory, IndustryVertical
from app.ai.automation_engine import TriggerType, ActionType, NotificationPriority
from app.ai.ai_analytics import AnalyticsType, MetricType, InsightCategory

router = APIRouter()

# ============================================================================
# CORE AI SERVICE ENDPOINTS
# ============================================================================

@router.get("/health")
async def ai_service_health():
    """Get AI service health status"""
    ai_service = get_ai_service()
    return ai_service.health_check()

@router.get("/models")
async def get_available_models(current_user = Depends(get_current_user)):
    """Get list of available AI models"""
    ai_service = get_ai_service()
    return {
        "models": ai_service.get_available_models(),
        "total_models": len(ai_service.processors)
    }

@router.get("/models/{model_id}/capabilities")
async def get_model_capabilities(model_id: str, current_user = Depends(get_current_user)):
    """Get capabilities of a specific AI model"""
    try:
        ai_service = get_ai_service()
        model = AIModel(model_id)
        capabilities = ai_service.get_model_capabilities(model)
        return {
            "model_id": model_id,
            "capabilities": capabilities
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Model not found")

@router.get("/stats")
async def get_ai_processing_stats(current_user = Depends(get_current_user)):
    """Get AI processing statistics"""
    ai_service = get_ai_service()
    return ai_service.get_processing_stats()

@router.post("/process")
async def process_ai_request(
    task: str,
    model: str,
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    priority: int = 5,
    timeout_seconds: int = 30,
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Process a general AI request"""
    try:
        ai_request = AIRequest(
            task=AITask(task),
            model=AIModel(model),
            input_data=input_data,
            context=context,
            user_id=current_user.id,
            organization_id=organization.id,
            priority=priority,
            timeout_seconds=timeout_seconds
        )
        
        ai_service = get_ai_service()
        response = await ai_service.process_request(ai_request)
        
        return {
            "task": response.task.value,
            "model": response.model.value,
            "result": response.result,
            "confidence": response.confidence,
            "processing_time_ms": response.processing_time_ms,
            "timestamp": response.timestamp.isoformat(),
            "error": response.error
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

# ============================================================================
# DOCUMENT INTELLIGENCE ENDPOINTS
# ============================================================================

@router.post("/documents/analyze")
async def analyze_document_content(
    content: str,
    document_id: str,
    document_type: Optional[str] = None,
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Analyze document content using AI"""
    try:
        doc_service = get_document_intelligence_service()
        
        hint_type = None
        if document_type:
            hint_type = DocumentType(document_type)
        
        analysis = await doc_service.analyze_document(
            content=content,
            document_id=document_id,
            hint_type=hint_type,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "document_id": analysis.document_id,
            "document_type": analysis.document_type.value,
            "content_summary": analysis.content_summary,
            "key_metrics": analysis.key_metrics,
            "risk_factors": analysis.risk_factors,
            "extracted_entities": analysis.extracted_entities,
            "sentiment_score": analysis.sentiment_score,
            "confidence_score": analysis.confidence_score,
            "processing_time_ms": analysis.processing_time_ms,
            "timestamp": analysis.timestamp.isoformat(),
            "metadata": analysis.metadata
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@router.post("/documents/summarize")
async def summarize_document_content(
    content: str,
    max_length: int = 500,
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Generate document summary using AI"""
    try:
        doc_service = get_document_intelligence_service()
        
        summary = await doc_service.summarize_document(
            content=content,
            max_length=max_length,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "executive_summary": summary.executive_summary,
            "key_points": summary.key_points,
            "action_items": summary.action_items,
            "important_dates": summary.important_dates,
            "financial_highlights": summary.financial_highlights,
            "risks_identified": summary.risks_identified,
            "word_count": summary.word_count,
            "reading_time_minutes": summary.reading_time_minutes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document summarization failed: {str(e)}")

@router.post("/documents/extract-data")
async def extract_structured_data(
    content: str,
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Extract structured data from document"""
    try:
        doc_service = get_document_intelligence_service()
        
        extraction = await doc_service.extract_structured_data(
            content=content,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "entities": extraction.entities,
            "financial_data": extraction.financial_data,
            "dates": extraction.dates,
            "contacts": extraction.contacts,
            "metrics": extraction.metrics,
            "confidence_scores": extraction.confidence_scores
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data extraction failed: {str(e)}")

@router.get("/documents/supported-types")
async def get_supported_document_types(current_user = Depends(get_current_user)):
    """Get list of supported document types"""
    doc_service = get_document_intelligence_service()
    return {
        "supported_types": doc_service.get_supported_document_types(),
        "service_stats": doc_service.get_service_stats()
    }

# ============================================================================
# DEAL INSIGHTS ENDPOINTS
# ============================================================================

@router.post("/deals/score")
async def score_deal_ai(
    deal_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Generate AI-powered deal score"""
    try:
        deal_service = get_deal_insights_service()
        
        score = await deal_service.score_deal(
            deal_data=deal_data,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "deal_id": score.deal_id,
            "overall_score": score.overall_score,
            "financial_score": score.financial_score,
            "strategic_score": score.strategic_score,
            "market_score": score.market_score,
            "risk_score": score.risk_score,
            "execution_score": score.execution_score,
            "recommendation": score.recommendation,
            "confidence_level": score.confidence_level,
            "key_strengths": score.key_strengths,
            "key_concerns": score.key_concerns,
            "score_breakdown": score.score_breakdown,
            "timestamp": score.timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deal scoring failed: {str(e)}")

@router.post("/deals/recommendations")
async def generate_deal_recommendations(
    deals_data: List[Dict[str, Any]],
    criteria: Optional[Dict[str, Any]] = None,
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Generate AI-powered deal recommendations"""
    try:
        deal_service = get_deal_insights_service()
        
        recommendations = await deal_service.generate_deal_recommendations(
            deals_data=deals_data,
            criteria=criteria,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "recommendations": [
                {
                    "deal_id": rec.deal_id,
                    "recommendation_type": rec.recommendation_type,
                    "priority_level": rec.priority_level,
                    "reasoning": rec.reasoning,
                    "suggested_actions": rec.suggested_actions,
                    "timeline_estimate": rec.timeline_estimate,
                    "resource_requirements": rec.resource_requirements,
                    "success_probability": rec.success_probability,
                    "generated_at": rec.generated_at.isoformat()
                }
                for rec in recommendations
            ],
            "total_deals_analyzed": len(deals_data),
            "recommendations_generated": len(recommendations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deal recommendations failed: {str(e)}")

@router.get("/market/intelligence/{industry}")
async def get_market_intelligence(
    industry: str,
    geographic_focus: Optional[str] = None,
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Get AI-powered market intelligence for an industry"""
    try:
        deal_service = get_deal_insights_service()
        industry_enum = IndustryVertical(industry)
        
        intelligence = await deal_service.analyze_market_intelligence(
            industry=industry_enum,
            geographic_focus=geographic_focus,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "industry": intelligence.industry.value,
            "market_trends": intelligence.market_trends,
            "competitive_landscape": intelligence.competitive_landscape,
            "valuation_benchmarks": intelligence.valuation_benchmarks,
            "growth_projections": intelligence.growth_projections,
            "risk_factors": intelligence.risk_factors,
            "opportunities": intelligence.opportunities,
            "market_sentiment": intelligence.market_sentiment,
            "confidence_score": intelligence.confidence_score,
            "analysis_date": intelligence.analysis_date.isoformat()
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid industry specified")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market intelligence analysis failed: {str(e)}")

@router.get("/deals/industries")
async def get_supported_industries(current_user = Depends(get_current_user)):
    """Get list of supported industries"""
    deal_service = get_deal_insights_service()
    return {
        "supported_industries": deal_service.get_supported_industries(),
        "scoring_methodology": deal_service.get_scoring_methodology(),
        "service_stats": deal_service.get_service_stats()
    }

@router.get("/deals/benchmarks/{industry}")
async def get_industry_benchmarks(
    industry: str,
    current_user = Depends(get_current_user)
):
    """Get industry benchmarks for deal analysis"""
    try:
        deal_service = get_deal_insights_service()
        industry_enum = IndustryVertical(industry)
        benchmarks = deal_service.get_industry_benchmarks(industry_enum)
        
        return {
            "industry": industry,
            "benchmarks": benchmarks
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid industry specified")

# ============================================================================
# AUTOMATION ENGINE ENDPOINTS
# ============================================================================

@router.post("/automation/triggers")
async def create_workflow_trigger(
    name: str,
    trigger_type: str,
    conditions: Dict[str, Any],
    actions: List[Dict[str, Any]],
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Create a new workflow automation trigger"""
    try:
        automation_engine = get_automation_engine()
        
        trigger = WorkflowTrigger(
            trigger_id=f"trigger_{int(datetime.now().timestamp())}",
            name=name,
            trigger_type=TriggerType(trigger_type),
            conditions=conditions,
            actions=actions,
            is_active=True,
            organization_id=organization.id,
            created_by=current_user.id,
            created_at=datetime.now()
        )
        
        success = await automation_engine.register_trigger(trigger)
        
        if success:
            return {
                "trigger_id": trigger.trigger_id,
                "name": trigger.name,
                "trigger_type": trigger.trigger_type.value,
                "is_active": trigger.is_active,
                "created_at": trigger.created_at.isoformat(),
                "message": "Workflow trigger created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to register trigger")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trigger creation failed: {str(e)}")

@router.get("/automation/triggers")
async def get_active_triggers(
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Get list of active automation triggers"""
    automation_engine = get_automation_engine()
    triggers = automation_engine.get_active_triggers()
    
    # Filter by organization
    org_triggers = [
        {
            "trigger_id": trigger.trigger_id,
            "name": trigger.name,
            "trigger_type": trigger.trigger_type.value,
            "is_active": trigger.is_active,
            "last_triggered": trigger.last_triggered.isoformat() if trigger.last_triggered else None,
            "trigger_count": trigger.trigger_count,
            "created_at": trigger.created_at.isoformat()
        }
        for trigger in triggers
        if trigger.organization_id == organization.id
    ]
    
    return {
        "triggers": org_triggers,
        "total_triggers": len(org_triggers)
    }

@router.post("/automation/events")
async def process_automation_event(
    event_type: str,
    event_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Process an automation event"""
    try:
        automation_engine = get_automation_engine()
        
        # Add user and organization context to event data
        event_data["user_id"] = current_user.id
        event_data["organization_id"] = organization.id
        event_data["event_type"] = event_type
        
        results = await automation_engine.process_event(event_type, event_data)
        
        return {
            "event_type": event_type,
            "triggers_activated": len(results),
            "results": [
                {
                    "automation_id": result.automation_id,
                    "trigger_id": result.trigger_id,
                    "success": result.success,
                    "actions_executed": result.actions_executed,
                    "notifications_sent": result.notifications_sent,
                    "errors": result.errors,
                    "execution_time_ms": result.execution_time_ms,
                    "timestamp": result.timestamp.isoformat()
                }
                for result in results
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event processing failed: {str(e)}")

@router.get("/automation/history")
async def get_automation_history(
    limit: int = 50,
    current_user = Depends(get_current_user)
):
    """Get automation execution history"""
    automation_engine = get_automation_engine()
    history = automation_engine.get_automation_history(limit=limit)
    
    return {
        "history": [
            {
                "automation_id": result.automation_id,
                "trigger_id": result.trigger_id,
                "success": result.success,
                "actions_executed": result.actions_executed,
                "execution_time_ms": result.execution_time_ms,
                "timestamp": result.timestamp.isoformat()
            }
            for result in history
        ],
        "total_records": len(history)
    }

@router.get("/automation/stats")
async def get_automation_stats(current_user = Depends(get_current_user)):
    """Get automation engine statistics"""
    automation_engine = get_automation_engine()
    return automation_engine.get_automation_stats()

# ============================================================================
# AI ANALYTICS ENDPOINTS
# ============================================================================

@router.post("/analytics/insights")
async def generate_predictive_insights(
    data_context: Dict[str, Any],
    insight_types: Optional[List[str]] = None,
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Generate AI-powered predictive insights"""
    try:
        analytics_service = get_ai_analytics_service()
        
        insight_categories = None
        if insight_types:
            insight_categories = [InsightCategory(category) for category in insight_types]
        
        insights = await analytics_service.generate_predictive_insights(
            data_context=data_context,
            insight_types=insight_categories,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "insights": [
                {
                    "insight_id": insight.insight_id,
                    "category": insight.category.value,
                    "title": insight.title,
                    "description": insight.description,
                    "confidence_score": insight.confidence_score,
                    "impact_level": insight.impact_level,
                    "time_horizon": insight.time_horizon,
                    "supporting_data": insight.supporting_data,
                    "recommended_actions": insight.recommended_actions,
                    "related_entities": insight.related_entities,
                    "created_at": insight.created_at.isoformat()
                }
                for insight in insights
            ],
            "total_insights": len(insights)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@router.post("/analytics/metrics")
async def analyze_performance_metrics(
    metrics_data: Dict[str, Any],
    metric_types: Optional[List[str]] = None,
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Analyze performance metrics with AI"""
    try:
        analytics_service = get_ai_analytics_service()
        
        metric_enums = None
        if metric_types:
            metric_enums = [MetricType(metric) for metric in metric_types]
        
        metrics = await analytics_service.analyze_performance_metrics(
            metrics_data=metrics_data,
            metric_types=metric_enums,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "metrics": [
                {
                    "metric_id": metric.metric_id,
                    "metric_type": metric.metric_type.value,
                    "current_value": metric.current_value,
                    "previous_value": metric.previous_value,
                    "target_value": metric.target_value,
                    "trend_direction": metric.trend_direction,
                    "change_percentage": metric.change_percentage,
                    "ai_analysis": metric.ai_analysis,
                    "benchmark_comparison": metric.benchmark_comparison,
                    "calculated_at": metric.calculated_at.isoformat()
                }
                for metric in metrics
            ],
            "total_metrics": len(metrics)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics analysis failed: {str(e)}")

@router.post("/analytics/reports")
async def generate_analytics_report(
    report_type: str,
    data_sources: List[str],
    start_date: datetime,
    end_date: datetime,
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Generate comprehensive analytics report"""
    try:
        analytics_service = get_ai_analytics_service()
        
        report = await analytics_service.generate_analytics_report(
            report_type=AnalyticsType(report_type),
            data_sources=data_sources,
            report_period={"start_date": start_date, "end_date": end_date},
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "report_id": report.report_id,
            "report_type": report.report_type.value,
            "title": report.title,
            "executive_summary": report.executive_summary,
            "key_insights": [
                {
                    "insight_id": insight.insight_id,
                    "category": insight.category.value,
                    "title": insight.title,
                    "description": insight.description,
                    "confidence_score": insight.confidence_score
                }
                for insight in report.key_insights
            ],
            "performance_metrics": [
                {
                    "metric_type": metric.metric_type.value,
                    "current_value": metric.current_value,
                    "trend_direction": metric.trend_direction,
                    "ai_analysis": metric.ai_analysis
                }
                for metric in report.performance_metrics
            ],
            "trends_analysis": report.trends_analysis,
            "recommendations": report.recommendations,
            "data_sources": report.data_sources,
            "confidence_score": report.confidence_score,
            "generated_at": report.generated_at.isoformat(),
            "report_period": {
                "start_date": report.report_period["start_date"].isoformat(),
                "end_date": report.report_period["end_date"].isoformat()
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.post("/analytics/anomalies")
async def detect_anomalies(
    data: Dict[str, Any],
    sensitivity: float = 0.5,
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Detect anomalies in data using AI"""
    try:
        analytics_service = get_ai_analytics_service()
        
        anomalies = await analytics_service.detect_anomalies(
            data=data,
            sensitivity=sensitivity,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "sensitivity": sensitivity
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

@router.get("/analytics/insights/recent")
async def get_recent_insights(
    limit: int = 20,
    category: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get recent AI insights"""
    try:
        analytics_service = get_ai_analytics_service()
        
        category_enum = None
        if category:
            category_enum = InsightCategory(category)
        
        insights = analytics_service.get_recent_insights(limit=limit, category=category_enum)
        
        return {
            "insights": [
                {
                    "insight_id": insight.insight_id,
                    "category": insight.category.value,
                    "title": insight.title,
                    "description": insight.description,
                    "confidence_score": insight.confidence_score,
                    "impact_level": insight.impact_level,
                    "created_at": insight.created_at.isoformat()
                }
                for insight in insights
            ],
            "total_insights": len(insights)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics/summary")
async def get_analytics_summary(current_user = Depends(get_current_user)):
    """Get analytics service summary"""
    analytics_service = get_ai_analytics_service()
    return analytics_service.get_analytics_summary()

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/types/analytics")
async def get_analytics_types(current_user = Depends(get_current_user)):
    """Get available analytics types"""
    return {
        "analytics_types": [atype.value for atype in AnalyticsType],
        "metric_types": [mtype.value for mtype in MetricType],
        "insight_categories": [category.value for category in InsightCategory]
    }

@router.get("/types/automation")
async def get_automation_types(current_user = Depends(get_current_user)):
    """Get available automation types"""
    return {
        "trigger_types": [ttype.value for ttype in TriggerType],
        "action_types": [atype.value for atype in ActionType],
        "notification_priorities": [priority.value for priority in NotificationPriority]
    }

@router.get("/types/documents")
async def get_document_types(current_user = Depends(get_current_user)):
    """Get available document types"""
    return {
        "document_types": [dtype.value for dtype in DocumentType],
        "deal_categories": [category.value for category in DealCategory],
        "industry_verticals": [industry.value for industry in IndustryVertical]
    }

# ============================================================================
# QUICK ACTION ENDPOINTS (Convenience methods)
# ============================================================================

@router.post("/quick/analyze-document")
async def quick_analyze_document(
    content: str,
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Quick document analysis (convenience endpoint)"""
    try:
        response = await analyze_document(
            document_content=content,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "analysis_result": response.result,
            "confidence": response.confidence,
            "processing_time_ms": response.processing_time_ms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")

@router.post("/quick/score-deal")
async def quick_score_deal(
    deal_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Quick deal scoring (convenience endpoint)"""
    try:
        response = await score_deal(
            deal_data=deal_data,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "score_result": response.result,
            "confidence": response.confidence,
            "processing_time_ms": response.processing_time_ms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick scoring failed: {str(e)}")

@router.post("/quick/summarize")
async def quick_summarize(
    content: str,
    max_length: int = 300,
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Quick content summarization (convenience endpoint)"""
    try:
        response = await summarize_content(
            content=content,
            max_length=max_length,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "summary_result": response.result,
            "confidence": response.confidence,
            "processing_time_ms": response.processing_time_ms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick summarization failed: {str(e)}")

@router.post("/quick/insights")
async def quick_generate_insights(
    data: Dict[str, Any],
    context: str = "general",
    current_user = Depends(get_current_user),
    organization = Depends(get_current_organization)
):
    """Quick insights generation (convenience endpoint)"""
    try:
        response = await generate_insights(
            data=data,
            context=context,
            user_id=current_user.id,
            organization_id=organization.id
        )
        
        return {
            "insights_result": response.result,
            "confidence": response.confidence,
            "processing_time_ms": response.processing_time_ms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick insights failed: {str(e)}")