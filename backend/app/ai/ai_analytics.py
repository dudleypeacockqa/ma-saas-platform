"""
AI Analytics Service
Advanced AI-powered analytics and predictive insights
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics
import json
from .ai_service import AIService, AIRequest, AIResponse, AITask, AIModel, get_ai_service

class AnalyticsType(str, Enum):
    """Types of analytics that can be generated"""
    DEAL_PERFORMANCE = "deal_performance"
    USER_BEHAVIOR = "user_behavior"
    MARKET_TRENDS = "market_trends"
    PREDICTIVE_INSIGHTS = "predictive_insights"
    RISK_ANALYSIS = "risk_analysis"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    OPERATIONAL_METRICS = "operational_metrics"

class MetricType(str, Enum):
    """Types of performance metrics"""
    CONVERSION_RATE = "conversion_rate"
    TIME_TO_CLOSE = "time_to_close"
    DEAL_VALUE = "deal_value"
    SUCCESS_RATE = "success_rate"
    USER_ENGAGEMENT = "user_engagement"
    DOCUMENT_USAGE = "document_usage"
    COLLABORATION_INDEX = "collaboration_index"
    EFFICIENCY_SCORE = "efficiency_score"

class InsightCategory(str, Enum):
    """Categories of AI insights"""
    TREND = "trend"
    ANOMALY = "anomaly"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    RECOMMENDATION = "recommendation"
    PREDICTION = "prediction"
    PATTERN = "pattern"
    CORRELATION = "correlation"

@dataclass
class PredictiveInsight:
    """AI-generated predictive insight"""
    insight_id: str
    category: InsightCategory
    title: str
    description: str
    confidence_score: float  # 0.0-1.0
    impact_level: str  # low, medium, high
    time_horizon: str  # short, medium, long term
    supporting_data: Dict[str, Any]
    recommended_actions: List[str]
    related_entities: List[str]  # deals, users, documents, etc.
    created_at: datetime
    expires_at: Optional[datetime] = None
    
@dataclass
class PerformanceMetric:
    """Performance metric with AI analysis"""
    metric_id: str
    metric_type: MetricType
    current_value: float
    previous_value: Optional[float]
    target_value: Optional[float]
    trend_direction: str  # up, down, stable
    change_percentage: float
    ai_analysis: str
    benchmark_comparison: Dict[str, float]
    calculated_at: datetime
    
@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    report_id: str
    report_type: AnalyticsType
    title: str
    executive_summary: str
    key_insights: List[PredictiveInsight]
    performance_metrics: List[PerformanceMetric]
    trends_analysis: Dict[str, Any]
    recommendations: List[str]
    data_sources: List[str]
    confidence_score: float
    generated_at: datetime
    report_period: Dict[str, datetime]
    
class AIAnalyticsService:
    """AI-powered analytics and insights service"""
    
    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or get_ai_service()
        self.insight_history: List[PredictiveInsight] = []
        self.metric_history: List[PerformanceMetric] = []
        self.report_cache: Dict[str, AnalyticsReport] = {}
        
    async def generate_predictive_insights(self, data_context: Dict[str, Any],
                                         insight_types: List[InsightCategory] = None,
                                         user_id: Optional[str] = None,
                                         organization_id: Optional[str] = None) -> List[PredictiveInsight]:
        """Generate AI-powered predictive insights"""
        if insight_types is None:
            insight_types = [InsightCategory.TREND, InsightCategory.OPPORTUNITY, InsightCategory.RISK]
        
        insights = []
        
        for insight_category in insight_types:
            ai_request = AIRequest(
                task=AITask.GENERATE_INSIGHTS,
                model=AIModel.MARKET_INTELLIGENCE,
                input_data={
                    "context": data_context,
                    "insight_category": insight_category.value,
                    "analysis_depth": "comprehensive"
                },
                context={
                    "generate_predictions": True,
                    "include_recommendations": True,
                    "time_horizons": ["short", "medium", "long"]
                },
                user_id=user_id,
                organization_id=organization_id
            )
            
            ai_response = await self.ai_service.process_request(ai_request)
            ai_insights = ai_response.result.get("insights", [])
            
            for ai_insight in ai_insights:
                insight = PredictiveInsight(
                    insight_id=f"insight_{int(datetime.now().timestamp())}_{len(insights)}",
                    category=insight_category,
                    title=ai_insight.get("title", f"AI {insight_category.value.title()} Insight"),
                    description=ai_insight.get("description", ""),
                    confidence_score=ai_response.confidence,
                    impact_level=ai_insight.get("impact", "medium"),
                    time_horizon=ai_insight.get("timeline", "medium"),
                    supporting_data=ai_insight.get("supporting_data", {}),
                    recommended_actions=ai_response.result.get("recommendations", []),
                    related_entities=self._extract_related_entities(data_context),
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=30)
                )
                insights.append(insight)
        
        # Store insights in history
        self.insight_history.extend(insights)
        
        # Keep only recent insights (last 1000)
        if len(self.insight_history) > 1000:
            self.insight_history = self.insight_history[-1000:]
        
        return insights
    
    async def analyze_performance_metrics(self, metrics_data: Dict[str, Any],
                                        metric_types: List[MetricType] = None,
                                        user_id: Optional[str] = None,
                                        organization_id: Optional[str] = None) -> List[PerformanceMetric]:
        """Analyze performance metrics with AI insights"""
        if metric_types is None:
            metric_types = [MetricType.CONVERSION_RATE, MetricType.TIME_TO_CLOSE, MetricType.SUCCESS_RATE]
        
        metrics = []
        
        for metric_type in metric_types:
            # Extract current and historical values
            current_value = self._calculate_metric_value(metric_type, metrics_data)
            previous_value = self._get_previous_metric_value(metric_type, metrics_data)
            target_value = self._get_target_value(metric_type)
            
            # Calculate trend and change
            if previous_value is not None:
                change_percentage = ((current_value - previous_value) / previous_value) * 100
                trend_direction = "up" if change_percentage > 5 else ("down" if change_percentage < -5 else "stable")
            else:
                change_percentage = 0.0
                trend_direction = "stable"
            
            # Use AI to analyze the metric
            ai_request = AIRequest(
                task=AITask.GENERATE_INSIGHTS,
                model=AIModel.MARKET_INTELLIGENCE,
                input_data={
                    "metric_type": metric_type.value,
                    "current_value": current_value,
                    "previous_value": previous_value,
                    "target_value": target_value,
                    "trend_direction": trend_direction,
                    "change_percentage": change_percentage,
                    "context_data": metrics_data
                },
                user_id=user_id,
                organization_id=organization_id
            )
            
            ai_response = await self.ai_service.process_request(ai_request)
            ai_analysis = ai_response.result.get("analysis", f"Metric {metric_type.value} analysis complete")
            
            # Get benchmark comparison
            benchmark_comparison = self._get_benchmark_comparison(metric_type, current_value)
            
            metric = PerformanceMetric(
                metric_id=f"metric_{metric_type.value}_{int(datetime.now().timestamp())}",
                metric_type=metric_type,
                current_value=current_value,
                previous_value=previous_value,
                target_value=target_value,
                trend_direction=trend_direction,
                change_percentage=change_percentage,
                ai_analysis=ai_analysis,
                benchmark_comparison=benchmark_comparison,
                calculated_at=datetime.now()
            )
            
            metrics.append(metric)
        
        # Store metrics in history
        self.metric_history.extend(metrics)
        
        # Keep only recent metrics (last 1000)
        if len(self.metric_history) > 1000:
            self.metric_history = self.metric_history[-1000:]
        
        return metrics
    
    async def generate_analytics_report(self, report_type: AnalyticsType,
                                      data_sources: List[str],
                                      report_period: Dict[str, datetime],
                                      user_id: Optional[str] = None,
                                      organization_id: Optional[str] = None) -> AnalyticsReport:
        """Generate comprehensive analytics report"""
        report_id = f"report_{report_type.value}_{int(datetime.now().timestamp())}"
        
        # Check cache first
        cache_key = f"{report_type.value}_{hash(str(report_period))}"
        if cache_key in self.report_cache:
            cached_report = self.report_cache[cache_key]
            if (datetime.now() - cached_report.generated_at).total_seconds() < 3600:  # 1 hour cache
                return cached_report
        
        # Gather data for the report
        report_data = await self._gather_report_data(report_type, data_sources, report_period)
        
        # Generate insights
        insights = await self.generate_predictive_insights(
            data_context=report_data,
            user_id=user_id,
            organization_id=organization_id
        )
        
        # Analyze metrics
        metrics = await self.analyze_performance_metrics(
            metrics_data=report_data,
            user_id=user_id,
            organization_id=organization_id
        )
        
        # Use AI to generate executive summary
        ai_request = AIRequest(
            task=AITask.SUMMARIZE_CONTENT,
            model=AIModel.CONTENT_SUMMARIZER,
            input_data={
                "report_type": report_type.value,
                "insights": [insight.__dict__ for insight in insights],
                "metrics": [metric.__dict__ for metric in metrics],
                "report_period": report_period,
                "data_sources": data_sources
            },
            context={"summary_type": "executive", "audience": "leadership"},
            user_id=user_id,
            organization_id=organization_id
        )
        
        ai_response = await self.ai_service.process_request(ai_request)
        executive_summary = ai_response.result.get("executive_summary", "Analytics report generated")
        
        # Generate trends analysis
        trends_analysis = self._analyze_trends(report_data, insights, metrics)
        
        # Compile recommendations
        recommendations = self._compile_recommendations(insights, metrics)
        
        # Calculate overall confidence
        confidence_scores = [insight.confidence_score for insight in insights] + [ai_response.confidence]
        overall_confidence = statistics.mean(confidence_scores) if confidence_scores else 0.5
        
        report = AnalyticsReport(
            report_id=report_id,
            report_type=report_type,
            title=f"{report_type.value.replace('_', ' ').title()} Analytics Report",
            executive_summary=executive_summary,
            key_insights=insights,
            performance_metrics=metrics,
            trends_analysis=trends_analysis,
            recommendations=recommendations,
            data_sources=data_sources,
            confidence_score=overall_confidence,
            generated_at=datetime.now(),
            report_period=report_period
        )
        
        # Cache the report
        self.report_cache[cache_key] = report
        
        return report
    
    async def detect_anomalies(self, data: Dict[str, Any],
                             sensitivity: float = 0.5,
                             user_id: Optional[str] = None,
                             organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Detect anomalies in data using AI"""
        ai_request = AIRequest(
            task=AITask.DETECT_ANOMALIES,
            model=AIModel.RISK_ASSESSOR,
            input_data={
                "data": data,
                "sensitivity": sensitivity,
                "detection_types": ["statistical", "pattern", "trend"]
            },
            user_id=user_id,
            organization_id=organization_id
        )
        
        ai_response = await self.ai_service.process_request(ai_request)
        anomalies = ai_response.result.get("anomalies", [])
        
        # Enhance anomalies with additional metadata
        enhanced_anomalies = []
        for anomaly in anomalies:
            enhanced_anomaly = {
                "anomaly_id": f"anomaly_{int(datetime.now().timestamp())}_{len(enhanced_anomalies)}",
                "type": anomaly.get("type", "unknown"),
                "description": anomaly.get("description", ""),
                "severity": anomaly.get("severity", "medium"),
                "confidence": ai_response.confidence,
                "affected_metrics": anomaly.get("affected_metrics", []),
                "suggested_investigation": anomaly.get("investigation_steps", []),
                "detected_at": datetime.now(),
                "context": anomaly.get("context", {})
            }
            enhanced_anomalies.append(enhanced_anomaly)
        
        return enhanced_anomalies
    
    def _calculate_metric_value(self, metric_type: MetricType, data: Dict[str, Any]) -> float:
        """Calculate the current value of a specific metric"""
        if metric_type == MetricType.CONVERSION_RATE:
            successful_deals = data.get("successful_deals", 0)
            total_deals = data.get("total_deals", 1)
            return (successful_deals / total_deals) * 100 if total_deals > 0 else 0.0
        
        elif metric_type == MetricType.TIME_TO_CLOSE:
            close_times = data.get("deal_close_times", [])
            return statistics.mean(close_times) if close_times else 0.0
        
        elif metric_type == MetricType.DEAL_VALUE:
            deal_values = data.get("deal_values", [])
            return statistics.mean(deal_values) if deal_values else 0.0
        
        elif metric_type == MetricType.SUCCESS_RATE:
            successful_outcomes = data.get("successful_outcomes", 0)
            total_outcomes = data.get("total_outcomes", 1)
            return (successful_outcomes / total_outcomes) * 100 if total_outcomes > 0 else 0.0
        
        elif metric_type == MetricType.USER_ENGAGEMENT:
            active_sessions = data.get("active_sessions", 0)
            total_users = data.get("total_users", 1)
            return (active_sessions / total_users) * 100 if total_users > 0 else 0.0
        
        else:
            return data.get(metric_type.value, 0.0)
    
    def _get_previous_metric_value(self, metric_type: MetricType, data: Dict[str, Any]) -> Optional[float]:
        """Get the previous period value for comparison"""
        previous_data = data.get("previous_period", {})
        if previous_data:
            return self._calculate_metric_value(metric_type, previous_data)
        return None
    
    def _get_target_value(self, metric_type: MetricType) -> Optional[float]:
        """Get target value for a metric type"""
        targets = {
            MetricType.CONVERSION_RATE: 15.0,  # 15%
            MetricType.TIME_TO_CLOSE: 45.0,    # 45 days
            MetricType.SUCCESS_RATE: 70.0,     # 70%
            MetricType.USER_ENGAGEMENT: 80.0   # 80%
        }
        return targets.get(metric_type)
    
    def _get_benchmark_comparison(self, metric_type: MetricType, current_value: float) -> Dict[str, float]:
        """Get benchmark comparison for a metric"""
        # Industry benchmarks (mock data)
        benchmarks = {
            MetricType.CONVERSION_RATE: {"industry_average": 12.5, "top_quartile": 18.0, "bottom_quartile": 8.0},
            MetricType.TIME_TO_CLOSE: {"industry_average": 52.0, "top_quartile": 35.0, "bottom_quartile": 75.0},
            MetricType.SUCCESS_RATE: {"industry_average": 65.0, "top_quartile": 75.0, "bottom_quartile": 55.0},
            MetricType.USER_ENGAGEMENT: {"industry_average": 70.0, "top_quartile": 85.0, "bottom_quartile": 55.0}
        }
        
        metric_benchmarks = benchmarks.get(metric_type, {})
        metric_benchmarks["current_value"] = current_value
        
        # Calculate percentile ranking
        if "industry_average" in metric_benchmarks:
            if current_value >= metric_benchmarks["top_quartile"]:
                metric_benchmarks["percentile_rank"] = 75
            elif current_value >= metric_benchmarks["industry_average"]:
                metric_benchmarks["percentile_rank"] = 50
            elif current_value >= metric_benchmarks["bottom_quartile"]:
                metric_benchmarks["percentile_rank"] = 25
            else:
                metric_benchmarks["percentile_rank"] = 10
        
        return metric_benchmarks
    
    def _extract_related_entities(self, data_context: Dict[str, Any]) -> List[str]:
        """Extract related entities from data context"""
        entities = []
        
        if "deal_ids" in data_context:
            entities.extend([f"deal:{deal_id}" for deal_id in data_context["deal_ids"]])
        
        if "user_ids" in data_context:
            entities.extend([f"user:{user_id}" for user_id in data_context["user_ids"]])
        
        if "document_ids" in data_context:
            entities.extend([f"document:{doc_id}" for doc_id in data_context["document_ids"]])
        
        return entities[:10]  # Limit to 10 entities
    
    async def _gather_report_data(self, report_type: AnalyticsType, 
                                data_sources: List[str], 
                                report_period: Dict[str, datetime]) -> Dict[str, Any]:
        """Gather data for report generation"""
        # In a real implementation, this would query various data sources
        # For now, we'll return mock data
        return {
            "report_type": report_type.value,
            "data_sources": data_sources,
            "period": report_period,
            "total_deals": 125,
            "successful_deals": 89,
            "deal_values": [1.5, 2.3, 0.8, 3.2, 1.9],  # Millions
            "deal_close_times": [42, 38, 65, 29, 51],  # Days
            "active_users": 87,
            "total_users": 120,
            "documents_processed": 342,
            "collaboration_events": 1567
        }
    
    def _analyze_trends(self, report_data: Dict[str, Any], 
                       insights: List[PredictiveInsight], 
                       metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Analyze trends from insights and metrics"""
        trends = {
            "overall_trend": "positive",
            "key_trends": [],
            "trend_indicators": {}
        }
        
        # Analyze metric trends
        positive_trends = sum(1 for metric in metrics if metric.trend_direction == "up")
        negative_trends = sum(1 for metric in metrics if metric.trend_direction == "down")
        
        if positive_trends > negative_trends:
            trends["overall_trend"] = "positive"
        elif negative_trends > positive_trends:
            trends["overall_trend"] = "negative"
        else:
            trends["overall_trend"] = "stable"
        
        # Extract key trends from insights
        trend_insights = [insight for insight in insights if insight.category == InsightCategory.TREND]
        trends["key_trends"] = [insight.title for insight in trend_insights]
        
        # Calculate trend indicators
        trends["trend_indicators"] = {
            "metrics_improving": positive_trends,
            "metrics_declining": negative_trends,
            "trend_insights_count": len(trend_insights),
            "average_confidence": statistics.mean([insight.confidence_score for insight in trend_insights]) if trend_insights else 0.5
        }
        
        return trends
    
    def _compile_recommendations(self, insights: List[PredictiveInsight], 
                               metrics: List[PerformanceMetric]) -> List[str]:
        """Compile recommendations from insights and metrics"""
        recommendations = set()
        
        # Add recommendations from insights
        for insight in insights:
            recommendations.update(insight.recommended_actions)
        
        # Add metric-based recommendations
        for metric in metrics:
            if metric.trend_direction == "down" and metric.target_value:
                if metric.current_value < metric.target_value * 0.8:  # More than 20% below target
                    recommendations.add(f"Urgent action needed to improve {metric.metric_type.value}")
                else:
                    recommendations.add(f"Monitor and improve {metric.metric_type.value}")
        
        return list(recommendations)[:10]  # Limit to 10 recommendations
    
    def get_recent_insights(self, limit: int = 20, 
                          category: Optional[InsightCategory] = None) -> List[PredictiveInsight]:
        """Get recent insights, optionally filtered by category"""
        insights = self.insight_history
        
        if category:
            insights = [insight for insight in insights if insight.category == category]
        
        # Sort by creation date and return most recent
        insights.sort(key=lambda x: x.created_at, reverse=True)
        return insights[:limit]
    
    def get_metric_trends(self, metric_type: MetricType, 
                         days: int = 30) -> List[PerformanceMetric]:
        """Get metric trends over a period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_metrics = [
            metric for metric in self.metric_history
            if metric.metric_type == metric_type and metric.calculated_at >= cutoff_date
        ]
        
        return sorted(filtered_metrics, key=lambda x: x.calculated_at)
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary of analytics service status"""
        recent_insights = self.get_recent_insights(limit=10)
        
        return {
            "total_insights_generated": len(self.insight_history),
            "total_metrics_analyzed": len(self.metric_history),
            "cached_reports": len(self.report_cache),
            "recent_insights_count": len(recent_insights),
            "insight_categories": list(set(insight.category.value for insight in recent_insights)),
            "ai_service_stats": self.ai_service.get_processing_stats(),
            "service_status": "active"
        }

# Global AI analytics service
_ai_analytics_service: Optional[AIAnalyticsService] = None

def get_ai_analytics_service() -> AIAnalyticsService:
    """Get global AI analytics service instance"""
    global _ai_analytics_service
    if _ai_analytics_service is None:
        _ai_analytics_service = AIAnalyticsService()
    return _ai_analytics_service