"""
Global Operations Module - Sprint 11
Advanced market intelligence and global operations for the M&A SaaS platform
"""

from .market_intelligence import (
    MarketIntelligenceEngine, MarketSector, GeographicRegion,
    get_market_intelligence_engine
)
from .global_operations import (
    GlobalOperationsHub, Currency, Jurisdiction,
    get_global_operations_hub
)
from .deal_matching import (
    DealMatchingEngine, DealType, MatchingCriteria,
    get_deal_matching_engine
)
from .regulatory_automation import (
    RegulatoryAutomationEngine, RegulatoryFramework,
    get_regulatory_automation_engine
)

__all__ = [
    "MarketIntelligenceEngine",
    "MarketSector",
    "GeographicRegion",
    "get_market_intelligence_engine",
    "GlobalOperationsHub",
    "Currency",
    "Jurisdiction",
    "get_global_operations_hub",
    "DealMatchingEngine",
    "DealType",
    "MatchingCriteria",
    "get_deal_matching_engine",
    "RegulatoryAutomationEngine",
    "RegulatoryFramework",
    "get_regulatory_automation_engine"
]