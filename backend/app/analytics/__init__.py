"""
Advanced Real-Time Analytics & Intelligence Dashboard Platform - Sprint 13
Real-time analytics, intelligent dashboards, and comprehensive reporting for the M&A SaaS platform
"""

from .real_time_analytics import (
    RealTimeAnalyticsEngine, MetricProcessor, EventStream,
    get_real_time_analytics_engine
)
from .dashboard_system import (
    DashboardSystem, DashboardManager, VisualizationEngine,
    get_dashboard_system
)
from .reporting_engine import (
    ReportingEngine, ReportGenerator, TemplateManager,
    get_reporting_engine
)
from .performance_monitor import (
    PerformanceMonitor, SystemHealthMonitor, AlertManager,
    get_performance_monitor
)
from .portfolio.portfolio_intelligence import (
    PortfolioIntelligenceService, SynergyEngine, RiskAnalyzer,
    get_portfolio_intelligence_service
)
from .market.intelligence_engine import (
    MarketIntelligenceEngine, CompetitiveAnalyzer, PredictiveModels,
    get_market_intelligence_engine
)
from .ml.prediction_models import (
    PredictionEngine, DealSuccessPredictor, TimingOptimizer, ValuationGapBridger,
    get_prediction_engine
)
from .competitive.intelligence_system import (
    CompetitiveIntelligenceService, ThreatAssessmentEngine, StrategicResponseOptimizer,
    get_competitive_intelligence_service
)
from .reporting.insights_engine import (
    ReportingEngine as CustomReportingEngine, NaturalLanguageProcessor,
    ReportType, VisualizationType, DeliveryFrequency, AIInsight, ExecutiveReport,
    get_reporting_engine as get_custom_reporting_engine
)

__all__ = [
    "RealTimeAnalyticsEngine",
    "MetricProcessor",
    "EventStream",
    "get_real_time_analytics_engine",
    "DashboardSystem",
    "DashboardManager",
    "VisualizationEngine",
    "get_dashboard_system",
    "ReportingEngine",
    "ReportGenerator",
    "TemplateManager",
    "get_reporting_engine",
    "PerformanceMonitor",
    "SystemHealthMonitor",
    "AlertManager",
    "get_performance_monitor",
    "PortfolioIntelligenceService",
    "SynergyEngine",
    "RiskAnalyzer",
    "get_portfolio_intelligence_service",
    "MarketIntelligenceEngine",
    "CompetitiveAnalyzer",
    "PredictiveModels",
    "get_market_intelligence_engine",
    "PredictionEngine",
    "DealSuccessPredictor",
    "TimingOptimizer",
    "ValuationGapBridger",
    "get_prediction_engine",
    "CompetitiveIntelligenceService",
    "ThreatAssessmentEngine",
    "StrategicResponseOptimizer",
    "get_competitive_intelligence_service",
    "CustomReportingEngine",
    "NaturalLanguageProcessor",
    "ReportType",
    "VisualizationType",
    "DeliveryFrequency",
    "AIInsight",
    "ExecutiveReport",
    "get_custom_reporting_engine"
]

# Advanced Analytics Configuration
ADVANCED_ANALYTICS_CONFIG = {
    "portfolio": {
        "real_time_updates": True,
        "benchmark_refresh_interval": 3600,  # 1 hour
        "risk_alert_thresholds": {
            "concentration_limit": 0.25,  # 25% max single position
            "correlation_warning": 0.8,
            "volatility_threshold": 0.3
        },
        "performance_calculation_interval": 300,  # 5 minutes
        "synergy_detection_confidence": 0.7
    },
    "market_intelligence": {
        "data_refresh_interval": 900,  # 15 minutes
        "prediction_horizon_days": 365,
        "confidence_threshold": 0.75,
        "competitive_monitoring_interval": 3600,  # 1 hour
        "trend_analysis_window_days": 90
    },
    "predictive": {
        "model_retrain_frequency": "weekly",
        "prediction_accuracy_threshold": 0.95,  # 95% for superhuman accuracy
        "ensemble_models": ["random_forest", "gradient_boost", "neural_network", "transformer"],
        "backtesting_window_years": 3
    },
    "reporting": {
        "auto_report_generation": True,
        "report_delivery_time": "09:00",  # 9 AM daily
        "executive_summary_length": 500,  # words
        "insight_confidence_threshold": 0.8
    }
]