"""
AI & Machine Learning Module - Sprint 12
Advanced AI and machine learning capabilities for the M&A SaaS platform
"""

from .predictive_analytics import (
    PredictiveAnalyticsEngine, DealOutcomePredictor, ValuationForecaster,
    get_predictive_analytics_engine
)
from .nlp_hub import (
    NLPHub, DocumentAnalyzer, ContractIntelligence, SentimentAnalyzer,
    get_nlp_hub
)
from .computer_vision import (
    ComputerVisionEngine, DocumentClassifier, FinancialAnalyzer,
    get_computer_vision_engine
)
from .recommendation_engine import (
    AIRecommendationEngine, DealRecommender, StrategyRecommender,
    get_ai_recommendation_engine
)

__all__ = [
    "PredictiveAnalyticsEngine",
    "DealOutcomePredictor",
    "ValuationForecaster",
    "get_predictive_analytics_engine",
    "NLPHub",
    "DocumentAnalyzer",
    "ContractIntelligence",
    "SentimentAnalyzer",
    "get_nlp_hub",
    "ComputerVisionEngine",
    "DocumentClassifier",
    "FinancialAnalyzer",
    "get_computer_vision_engine",
    "AIRecommendationEngine",
    "DealRecommender",
    "StrategyRecommender",
    "get_ai_recommendation_engine"
]