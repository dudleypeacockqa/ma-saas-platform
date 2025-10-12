"""
Predictive Analytics API
AI-powered predictions, insights, and recommendations for M&A deals
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.auth.clerk_auth import ClerkUser, get_current_user
from app.auth.tenant_isolation import TenantAwareQuery, get_tenant_query
from app.core.permissions import PermissionChecker, ResourceType, Action
from app.ai.prediction_models import DealOutcomePredictionModel, MarketTrendAnalyzer
from app.ai.insight_engine import AutomatedInsightEngine, InsightType

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize AI models
prediction_model = DealOutcomePredictionModel()
trend_analyzer = MarketTrendAnalyzer()
insight_engine = AutomatedInsightEngine()


@router.get("/deals/{deal_id}/prediction")
async def predict_deal_outcome(
    deal_id: str,
    current_user: ClerkUser = Depends(get_current_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Predict deal outcome using AI models"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.ANALYTICS,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access predictive analytics"
            )

        # Get deal data
        deal = tenant_query.get_by_id("deals", deal_id)
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )

        # Convert deal to dict for prediction
        deal_data = {
            "id": deal.id,
            "title": deal.title,
            "status": deal.status,
            "estimated_value": float(deal.estimated_value or 0),
            "created_at": deal.created_at.isoformat() if deal.created_at else datetime.utcnow().isoformat(),
            "industry": deal.industry or "",
            "organization_id": current_user.organization_id,
            "team_members": [],  # Would populate from actual team data
            "document_count": 0,  # Would populate from actual document count
            "activity_count": 0   # Would populate from actual activity count
        }

        # Get prediction
        prediction = await prediction_model.predict_deal_outcome(deal_data, db)

        return {
            "deal_id": deal_id,
            "prediction": {
                "predicted_outcome": prediction.predicted_outcome.value,
                "success_probability": prediction.success_probability,
                "failure_probability": prediction.failure_probability,
                "expected_completion_date": prediction.expected_completion_date.isoformat(),
                "predicted_value": prediction.predicted_value,
                "risk_level": prediction.risk_level.value,
                "risk_factors": prediction.risk_factors,
                "confidence_score": prediction.confidence_score,
                "model_version": prediction.model_version,
                "prediction_date": prediction.prediction_date.isoformat(),
                "key_insights": prediction.key_insights,
                "recommendations": prediction.recommendations
            },
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "organization_id": current_user.organization_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deal prediction failed for {deal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate deal prediction"
        )


@router.get("/market-trends/{market_segment}")
async def analyze_market_trends(
    market_segment: str,
    timeframe: str = Query("quarterly", regex="^(monthly|quarterly|yearly)$"),
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze market trends for a specific segment"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.ANALYTICS,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access market analytics"
            )

        # Analyze market trends
        trend = await trend_analyzer.analyze_market_trends(market_segment, timeframe, db)

        return {
            "market_segment": market_segment,
            "timeframe": timeframe,
            "trend_analysis": {
                "trend_id": trend.trend_id,
                "trend_direction": trend.trend_direction,
                "trend_strength": trend.trend_strength,
                "confidence_level": trend.confidence_level,
                "key_indicators": trend.key_indicators,
                "predictions": trend.predictions,
                "analysis_date": trend.analysis_date.isoformat()
            },
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "organization_id": current_user.organization_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Market trend analysis failed for {market_segment}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze market trends"
        )


@router.get("/insights")
async def generate_organization_insights(
    insight_types: Optional[List[str]] = Query(None, description="Types of insights to generate"),
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered insights for the organization"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.ANALYTICS,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access insights"
            )

        # Parse insight types
        include_types = None
        if insight_types:
            try:
                include_types = [InsightType(t) for t in insight_types]
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid insight type: {str(e)}"
                )

        # Generate insights
        insights = await insight_engine.generate_organization_insights(
            current_user.organization_id,
            db,
            include_types
        )

        # Cache insights
        await insight_engine.cache_insights(insights)

        # Convert insights to dict format
        insights_data = []
        for insight in insights:
            insights_data.append({
                "insight_id": insight.insight_id,
                "insight_type": insight.insight_type.value,
                "priority": insight.priority.value,
                "title": insight.title,
                "description": insight.description,
                "context": insight.context,
                "recommendations": insight.recommendations,
                "impact_score": insight.impact_score,
                "confidence_score": insight.confidence_score,
                "generated_at": insight.generated_at.isoformat(),
                "expires_at": insight.expires_at.isoformat() if insight.expires_at else None,
                "related_entities": insight.related_entities,
                "data_sources": insight.data_sources,
                "tags": insight.tags
            })

        return {
            "insights": insights_data,
            "summary": {
                "total_insights": len(insights_data),
                "by_priority": {
                    "critical": len([i for i in insights if i.priority.value == "critical"]),
                    "high": len([i for i in insights if i.priority.value == "high"]),
                    "medium": len([i for i in insights if i.priority.value == "medium"]),
                    "low": len([i for i in insights if i.priority.value == "low"])
                },
                "by_type": {
                    insight_type.value: len([i for i in insights if i.insight_type == insight_type])
                    for insight_type in InsightType
                }
            },
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "organization_id": current_user.organization_id,
                "requested_types": insight_types or "all"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Insight generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate insights"
        )


@router.get("/insights/{insight_id}")
async def get_insight(
    insight_id: str,
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get a specific insight by ID"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.ANALYTICS,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access insights"
            )

        # Get insight from cache
        insight = await insight_engine.get_insight_by_id(insight_id)

        if not insight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Insight not found or expired"
            )

        return {
            "insight": {
                "insight_id": insight.insight_id,
                "insight_type": insight.insight_type.value,
                "priority": insight.priority.value,
                "title": insight.title,
                "description": insight.description,
                "context": insight.context,
                "recommendations": insight.recommendations,
                "impact_score": insight.impact_score,
                "confidence_score": insight.confidence_score,
                "generated_at": insight.generated_at.isoformat(),
                "expires_at": insight.expires_at.isoformat() if insight.expires_at else None,
                "related_entities": insight.related_entities,
                "data_sources": insight.data_sources,
                "tags": insight.tags
            },
            "metadata": {
                "retrieved_at": datetime.utcnow().isoformat(),
                "organization_id": current_user.organization_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve insight {insight_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve insight"
        )


@router.get("/recommendations/deal/{deal_id}")
async def get_deal_recommendations(
    deal_id: str,
    current_user: ClerkUser = Depends(get_current_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Get AI-powered recommendations for a specific deal"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.ANALYTICS,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access recommendations"
            )

        # Get deal data
        deal = tenant_query.get_by_id("deals", deal_id)
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )

        # Convert deal to dict for analysis
        deal_data = {
            "id": deal.id,
            "title": deal.title,
            "status": deal.status,
            "estimated_value": float(deal.estimated_value or 0),
            "created_at": deal.created_at.isoformat() if deal.created_at else datetime.utcnow().isoformat(),
            "industry": deal.industry or "",
            "organization_id": current_user.organization_id
        }

        # Get prediction for recommendations
        prediction = await prediction_model.predict_deal_outcome(deal_data, db)

        # Generate specific insights for this deal
        insights = await insight_engine.generate_organization_insights(
            current_user.organization_id,
            db,
            [InsightType.DEAL_RISK, InsightType.RECOMMENDATION, InsightType.OPTIMIZATION]
        )

        # Filter insights related to this deal
        deal_insights = [
            insight for insight in insights
            if deal_id in insight.related_entities
        ]

        # Compile recommendations
        all_recommendations = list(prediction.recommendations)
        for insight in deal_insights:
            all_recommendations.extend(insight.recommendations)

        # Remove duplicates while preserving order
        unique_recommendations = []
        seen = set()
        for rec in all_recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)

        return {
            "deal_id": deal_id,
            "recommendations": {
                "primary_recommendations": unique_recommendations[:5],
                "all_recommendations": unique_recommendations,
                "prediction_based": prediction.recommendations,
                "insight_based": [
                    {
                        "insight_id": insight.insight_id,
                        "insight_type": insight.insight_type.value,
                        "priority": insight.priority.value,
                        "recommendations": insight.recommendations
                    }
                    for insight in deal_insights
                ]
            },
            "context": {
                "predicted_outcome": prediction.predicted_outcome.value,
                "success_probability": prediction.success_probability,
                "risk_level": prediction.risk_level.value,
                "confidence_score": prediction.confidence_score,
                "related_insights_count": len(deal_insights)
            },
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "organization_id": current_user.organization_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate recommendations for deal {deal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )


@router.get("/dashboard/predictive")
async def get_predictive_dashboard(
    current_user: ClerkUser = Depends(get_current_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Get predictive analytics dashboard data"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.ANALYTICS,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access predictive dashboard"
            )

        # Get active deals for overview
        active_deals = tenant_query.list("deals", {"status": ["prospecting", "qualification", "proposal", "negotiation", "due_diligence", "closing"]})

        # Generate predictions for top deals (by value)
        deal_predictions = []
        sorted_deals = sorted(active_deals[:10], key=lambda d: float(d.estimated_value or 0), reverse=True)

        for deal in sorted_deals[:5]:  # Top 5 deals
            deal_data = {
                "id": deal.id,
                "title": deal.title,
                "status": deal.status,
                "estimated_value": float(deal.estimated_value or 0),
                "created_at": deal.created_at.isoformat() if deal.created_at else datetime.utcnow().isoformat(),
                "industry": deal.industry or "",
                "organization_id": current_user.organization_id
            }

            prediction = await prediction_model.predict_deal_outcome(deal_data, db)

            deal_predictions.append({
                "deal_id": deal.id,
                "deal_title": deal.title,
                "predicted_outcome": prediction.predicted_outcome.value,
                "success_probability": prediction.success_probability,
                "risk_level": prediction.risk_level.value,
                "predicted_value": prediction.predicted_value,
                "expected_completion": prediction.expected_completion_date.isoformat()
            })

        # Generate organization insights summary
        insights = await insight_engine.generate_organization_insights(
            current_user.organization_id,
            db
        )

        # Calculate dashboard metrics
        total_pipeline_value = sum(float(deal.estimated_value or 0) for deal in active_deals)
        avg_success_probability = sum(pred["success_probability"] for pred in deal_predictions) / max(len(deal_predictions), 1)
        high_risk_deals = len([pred for pred in deal_predictions if pred["risk_level"] in ["high", "critical"]])

        # Market trend for organization's primary industry
        org_industry = current_user.organization_role  # This would come from organization data
        market_trend = None
        if org_industry:
            try:
                market_trend = await trend_analyzer.analyze_market_trends(org_industry, "quarterly", db)
            except Exception:
                pass  # Market trend is optional

        return {
            "dashboard": {
                "summary_metrics": {
                    "total_active_deals": len(active_deals),
                    "total_pipeline_value": total_pipeline_value,
                    "average_success_probability": avg_success_probability,
                    "high_risk_deals_count": high_risk_deals,
                    "insights_count": len(insights)
                },
                "deal_predictions": deal_predictions,
                "top_insights": [
                    {
                        "insight_id": insight.insight_id,
                        "insight_type": insight.insight_type.value,
                        "priority": insight.priority.value,
                        "title": insight.title,
                        "description": insight.description,
                        "impact_score": insight.impact_score,
                        "confidence_score": insight.confidence_score
                    }
                    for insight in insights[:5]
                ],
                "market_trend": {
                    "trend_direction": market_trend.trend_direction if market_trend else "stable",
                    "trend_strength": market_trend.trend_strength if market_trend else 0.5,
                    "confidence_level": market_trend.confidence_level if market_trend else 0.5
                } if market_trend else None,
                "risk_distribution": {
                    "low": len([pred for pred in deal_predictions if pred["risk_level"] == "low"]),
                    "medium": len([pred for pred in deal_predictions if pred["risk_level"] == "medium"]),
                    "high": len([pred for pred in deal_predictions if pred["risk_level"] == "high"]),
                    "critical": len([pred for pred in deal_predictions if pred["risk_level"] == "critical"])
                }
            },
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "organization_id": current_user.organization_id,
                "data_freshness": "real_time"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate predictive dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate dashboard data"
        )


@router.post("/insights/refresh")
async def refresh_insights(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually refresh organization insights"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.ANALYTICS,
            Action.CREATE
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to refresh insights"
            )

        # Clean up expired insights first
        await insight_engine.cleanup_expired_insights()

        # Generate fresh insights
        insights = await insight_engine.generate_organization_insights(
            current_user.organization_id,
            db
        )

        # Cache new insights
        await insight_engine.cache_insights(insights)

        return {
            "status": "success",
            "insights_generated": len(insights),
            "breakdown": {
                "critical": len([i for i in insights if i.priority.value == "critical"]),
                "high": len([i for i in insights if i.priority.value == "high"]),
                "medium": len([i for i in insights if i.priority.value == "medium"]),
                "low": len([i for i in insights if i.priority.value == "low"])
            },
            "metadata": {
                "refreshed_at": datetime.utcnow().isoformat(),
                "organization_id": current_user.organization_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to refresh insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh insights"
        )