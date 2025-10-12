"""
AI-Powered Global Deal Marketplace
Primary source of M&A opportunities worldwide
"""

from .sourcing.ai_discovery import DealSourcingEngine
from .sourcing.financial_analysis import FinancialAnalysisService
from .sourcing.opportunity_detection import OpportunityDetectionService
from .matching.compatibility_engine import CompatibilityEngine
from .matching.strategic_fit import StrategicFitAnalyzer
from .matching.success_prediction import SuccessPredictionService
from .intelligence.market_trends import MarketTrendsService
from .intelligence.industry_analysis import IndustryAnalysisService
from .intelligence.regulatory_monitor import RegulatoryMonitorService
from .dealflow.notification_engine import NotificationEngine
from .dealflow.workflow_automation import WorkflowAutomationService
from .dealflow.document_management import DocumentManagementService
from .network.referral_system import ReferralSystemService
from .network.reputation_engine import ReputationEngine
from .network.community_features import CommunityFeaturesService

__all__ = [
    "DealSourcingEngine",
    "FinancialAnalysisService",
    "OpportunityDetectionService",
    "CompatibilityEngine",
    "StrategicFitAnalyzer",
    "SuccessPredictionService",
    "MarketTrendsService",
    "IndustryAnalysisService",
    "RegulatoryMonitorService",
    "NotificationEngine",
    "WorkflowAutomationService",
    "DocumentManagementService",
    "ReferralSystemService",
    "ReputationEngine",
    "CommunityFeaturesService"
]

# Marketplace configuration
MARKETPLACE_CONFIG = {
    "sourcing": {
        "data_refresh_interval": 3600,  # 1 hour
        "min_confidence_score": 0.75,
        "max_deals_per_batch": 1000
    },
    "matching": {
        "compatibility_threshold": 0.7,
        "max_matches_per_deal": 50,
        "success_probability_threshold": 0.6
    },
    "intelligence": {
        "trend_analysis_window": 90,  # days
        "prediction_horizon": 365,  # days
        "confidence_intervals": [0.68, 0.95, 0.99]
    },
    "dealflow": {
        "auto_outreach_enabled": True,
        "nda_expiry_days": 365,
        "followup_intervals": [1, 3, 7, 14, 30]  # days
    },
    "network": {
        "referral_commission_rate": 0.025,  # 2.5%
        "reputation_decay_rate": 0.95,  # annual
        "community_threshold": 10  # min interactions
    }
}