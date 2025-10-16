"""
Market Intelligence Engine
Comprehensive market analysis with superhuman insights for M&A professionals
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import aiohttp
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import yfinance as yf  # For market data
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

from app.core.config import settings
from app.core.database import get_database
from app.analytics import ADVANCED_ANALYTICS_CONFIG

logger = logging.getLogger(__name__)

class MarketCondition(str, Enum):
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    VOLATILE = "volatile"
    STABLE = "stable"
    RECESSION = "recession"

class DealVelocity(str, Enum):
    ACCELERATING = "accelerating"
    STABLE = "stable"
    DECLINING = "declining"
    STALLED = "stalled"

class TimingRecommendation(str, Enum):
    BUY_NOW = "buy_now"
    BUY_SOON = "buy_soon"
    WAIT = "wait"
    SELL_NOW = "sell_now"
    HOLD = "hold"

@dataclass
class MarketSegmentAnalysis:
    segment: str
    market_size: float
    growth_rate: float
    valuation_multiple_median: float
    valuation_multiple_trend: str
    deal_count_12m: int
    deal_velocity: DealVelocity
    consolidation_activity: str
    regulatory_environment: str
    key_trends: List[str]
    major_players: List[str]
    emerging_opportunities: List[str]

@dataclass
class ValuationTrend:
    metric: str  # ev_revenue, ev_ebitda, price_book
    current_median: float
    twelve_month_high: float
    twelve_month_low: float
    trend_direction: str
    volatility: float
    sector_breakdown: Dict[str, float]
    size_segmentation: Dict[str, float]
    geographic_variation: Dict[str, float]

@dataclass
class DealTimingAnalysis:
    overall_market_condition: MarketCondition
    optimal_deal_timing: TimingRecommendation
    market_cycle_position: str
    expected_market_direction: str
    timing_confidence: float
    key_timing_factors: List[str]
    seasonal_patterns: Dict[str, float]
    economic_indicators_alignment: Dict[str, float]

@dataclass
class CompetitiveLandscape:
    total_active_players: int
    top_5_players: List[Dict[str, Any]]
    market_concentration: float
    new_entrants_12m: int
    strategic_partnerships: List[Dict[str, Any]]
    acquisition_patterns: Dict[str, Any]
    competitive_advantages: List[str]
    market_gaps: List[str]

@dataclass
class EconomicCorrelation:
    indicator: str
    correlation_with_deal_activity: float
    current_value: float
    trend: str
    impact_on_valuations: float
    predictive_power: float
    lag_months: int

@dataclass
class MarketIntelligenceReport:
    generated_at: datetime
    market_segments: List[MarketSegmentAnalysis]
    valuation_trends: List[ValuationTrend]
    timing_analysis: DealTimingAnalysis
    competitive_landscape: CompetitiveLandscape
    economic_correlations: List[EconomicCorrelation]
    regulatory_updates: List[Dict[str, Any]]
    key_insights: List[str]
    strategic_recommendations: List[str]
    market_forecast: Dict[str, Any]

class CompetitiveAnalyzer:
    """Advanced competitive intelligence and market positioning analysis"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["market_intelligence"]

    async def analyze_competitive_landscape(
        self,
        sector: str,
        geography: Optional[str] = None
    ) -> CompetitiveLandscape:
        """Analyze competitive landscape for a specific sector"""
        try:
            # Mock competitive data - would integrate with industry databases
            competitors = await self._get_competitive_data(sector, geography)

            # Calculate market concentration (HHI)
            market_shares = [comp.get("market_share", 0) for comp in competitors]
            hhi = sum(share ** 2 for share in market_shares)

            # Identify top players
            top_players = sorted(competitors, key=lambda x: x.get("revenue", 0), reverse=True)[:5]

            # Analyze acquisition patterns
            acquisition_patterns = await self._analyze_acquisition_patterns(competitors)

            # Identify strategic partnerships
            partnerships = await self._identify_partnerships(competitors)

            # Market gaps analysis
            market_gaps = await self._identify_market_gaps(sector, competitors)

            return CompetitiveLandscape(
                total_active_players=len(competitors),
                top_5_players=[
                    {
                        "name": player.get("name", ""),
                        "revenue": player.get("revenue", 0),
                        "market_share": player.get("market_share", 0),
                        "growth_rate": player.get("growth_rate", 0),
                        "key_strengths": player.get("strengths", []),
                        "recent_acquisitions": player.get("acquisitions", [])
                    }
                    for player in top_players
                ],
                market_concentration=hhi,
                new_entrants_12m=len([c for c in competitors if c.get("years_in_market", 10) <= 1]),
                strategic_partnerships=partnerships,
                acquisition_patterns=acquisition_patterns,
                competitive_advantages=["technology_leadership", "distribution_network", "brand_recognition"],
                market_gaps=market_gaps
            )

        except Exception as e:
            logger.error(f"Error analyzing competitive landscape: {e}")
            raise

    async def _get_competitive_data(self, sector: str, geography: Optional[str]) -> List[Dict[str, Any]]:
        """Get competitive intelligence data"""
        # Mock data - would integrate with competitive intelligence APIs
        return [
            {
                "name": "Market Leader Corp",
                "revenue": 2_500_000_000,
                "market_share": 0.22,
                "growth_rate": 0.15,
                "years_in_market": 15,
                "strengths": ["technology", "distribution", "brand"],
                "acquisitions": ["TechStartup A", "RegionalPlayer B"]
            },
            {
                "name": "Innovation Challenger",
                "revenue": 1_800_000_000,
                "market_share": 0.18,
                "growth_rate": 0.28,
                "years_in_market": 8,
                "strengths": ["innovation", "agility", "customer_focus"],
                "acquisitions": ["AI Company C"]
            },
            {
                "name": "Traditional Player",
                "revenue": 1_200_000_000,
                "market_share": 0.12,
                "growth_rate": 0.08,
                "years_in_market": 25,
                "strengths": ["relationships", "experience", "stability"],
                "acquisitions": []
            }
        ]

    async def _analyze_acquisition_patterns(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze acquisition patterns in the competitive landscape"""
        total_acquisitions = sum(len(comp.get("acquisitions", [])) for comp in competitors)
        active_acquirers = len([comp for comp in competitors if comp.get("acquisitions", [])])

        return {
            "total_acquisitions_12m": total_acquisitions,
            "active_acquirers": active_acquirers,
            "average_acquisitions_per_player": total_acquisitions / len(competitors) if competitors else 0,
            "consolidation_trend": "accelerating" if total_acquisitions > 10 else "moderate",
            "strategic_rationale": ["technology_acquisition", "market_expansion", "talent_acquisition"]
        }

    async def _identify_partnerships(self, competitors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify strategic partnerships"""
        return [
            {
                "partners": ["Market Leader Corp", "Technology Partner X"],
                "partnership_type": "technology_alliance",
                "announcement_date": "2023-09-15",
                "strategic_value": "cloud_platform_integration"
            },
            {
                "partners": ["Innovation Challenger", "Distribution Partner Y"],
                "partnership_type": "channel_partnership",
                "announcement_date": "2023-11-02",
                "strategic_value": "market_expansion"
            }
        ]

    async def _identify_market_gaps(self, sector: str, competitors: List[Dict[str, Any]]) -> List[str]:
        """Identify gaps in the competitive landscape"""
        return [
            "AI-powered automation solutions",
            "Small business market segment",
            "Emerging markets expansion",
            "Sustainability-focused offerings",
            "Mobile-first customer experience"
        ]

class PredictiveModels:
    """Machine learning models for market prediction and optimization"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["predictive"]
        self.models = {}
        self.scalers = {}

    async def predict_deal_success_probability(
        self,
        deal_features: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """Predict deal success probability with feature importance"""
        try:
            # Prepare features
            feature_vector = self._prepare_deal_features(deal_features)

            # Use ensemble model
            probabilities = []
            feature_importances = {}

            for model_name in self.config["ensemble_models"]:
                model = await self._get_or_train_model(model_name, "deal_success")
                prob = model.predict_proba([feature_vector])[0][1]  # Probability of success
                probabilities.append(prob)

                # Get feature importance (for tree-based models)
                if hasattr(model, 'feature_importances_'):
                    importance = model.feature_importances_
                    feature_names = self._get_feature_names()
                    for i, name in enumerate(feature_names):
                        feature_importances[name] = feature_importances.get(name, 0) + importance[i] / len(self.config["ensemble_models"])

            # Ensemble prediction
            final_probability = np.mean(probabilities)

            return final_probability, feature_importances

        except Exception as e:
            logger.error(f"Error predicting deal success: {e}")
            return 0.5, {}

    async def predict_optimal_timing(
        self,
        market_conditions: Dict[str, Any],
        deal_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict optimal timing for deal execution"""
        try:
            # Prepare features for timing model
            timing_features = self._prepare_timing_features(market_conditions, deal_characteristics)

            # Predict using timing model
            timing_model = await self._get_or_train_model("timing_optimization", "timing")
            timing_score = timing_model.predict([timing_features])[0]

            # Convert to recommendation
            if timing_score > 0.8:
                recommendation = TimingRecommendation.BUY_NOW
                rationale = "Favorable market conditions and deal characteristics align for immediate action"
            elif timing_score > 0.6:
                recommendation = TimingRecommendation.BUY_SOON
                rationale = "Good timing window expected within next 3 months"
            elif timing_score > 0.4:
                recommendation = TimingRecommendation.HOLD
                rationale = "Mixed signals suggest maintaining current position"
            elif timing_score > 0.2:
                recommendation = TimingRecommendation.WAIT
                rationale = "Unfavorable conditions suggest delaying action"
            else:
                recommendation = TimingRecommendation.SELL_NOW
                rationale = "Challenging market conditions favor immediate exit if possible"

            return {
                "recommendation": recommendation.value,
                "confidence": abs(timing_score - 0.5) * 2,  # Confidence based on distance from neutral
                "timing_score": timing_score,
                "rationale": rationale,
                "optimal_timeframe": self._estimate_optimal_timeframe(timing_score),
                "key_factors": self._identify_key_timing_factors(market_conditions)
            }

        except Exception as e:
            logger.error(f"Error predicting optimal timing: {e}")
            return {
                "recommendation": "hold",
                "confidence": 0.5,
                "rationale": "Unable to determine optimal timing"
            }

    def _prepare_deal_features(self, deal_features: Dict[str, Any]) -> List[float]:
        """Prepare feature vector for deal success prediction"""
        return [
            deal_features.get("deal_size", 0) / 1_000_000,  # Deal size in millions
            deal_features.get("target_revenue", 0) / 1_000_000,
            deal_features.get("target_ebitda_margin", 0),
            deal_features.get("market_position", 3),  # 1-5 scale
            deal_features.get("management_quality", 3),  # 1-5 scale
            deal_features.get("industry_growth_rate", 0.05),
            deal_features.get("competitive_intensity", 3),  # 1-5 scale
            deal_features.get("regulatory_risk", 2),  # 1-5 scale
            len(deal_features.get("strategic_rationale", [])),
            deal_features.get("synergy_potential", 0.1)
        ]

    def _prepare_timing_features(self, market_conditions: Dict[str, Any], deal_chars: Dict[str, Any]) -> List[float]:
        """Prepare features for timing optimization"""
        return [
            market_conditions.get("market_sentiment", 0.5),
            market_conditions.get("volatility", 0.2),
            market_conditions.get("liquidity", 0.7),
            market_conditions.get("valuation_level", 0.6),
            market_conditions.get("credit_availability", 0.8),
            deal_chars.get("urgency", 0.3),
            deal_chars.get("competition", 0.4),
            deal_chars.get("complexity", 0.5)
        ]

    async def _get_or_train_model(self, model_name: str, model_type: str):
        """Get existing model or train new one"""
        model_key = f"{model_type}_{model_name}"

        if model_key not in self.models:
            # Train new model with mock data
            self.models[model_key] = await self._train_model(model_name, model_type)

        return self.models[model_key]

    async def _train_model(self, model_name: str, model_type: str):
        """Train machine learning model with historical data"""
        # Mock training data - would use real historical data in production
        if model_type == "deal_success":
            X, y = self._generate_mock_deal_data()
        else:  # timing
            X, y = self._generate_mock_timing_data()

        if model_name == "random_forest":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_name == "gradient_boost":
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        else:
            model = RandomForestRegressor(n_estimators=50, random_state=42)

        model.fit(X, y)
        return model

    def _generate_mock_deal_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate mock deal success training data"""
        np.random.seed(42)
        n_samples = 1000

        # Generate features
        X = np.random.randn(n_samples, 10)

        # Generate target with some logic
        y = (
            0.3 * X[:, 0] +  # Deal size effect
            0.2 * X[:, 2] +  # EBITDA margin effect
            0.25 * X[:, 3] + # Market position effect
            0.15 * X[:, 4] + # Management quality
            np.random.randn(n_samples) * 0.1
        )
        y = 1 / (1 + np.exp(-y))  # Sigmoid to get probabilities

        return X, y

    def _generate_mock_timing_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate mock timing optimization training data"""
        np.random.seed(42)
        n_samples = 800

        X = np.random.randn(n_samples, 8)
        y = (
            0.4 * X[:, 0] +  # Market sentiment
            -0.3 * X[:, 1] + # Volatility (negative)
            0.2 * X[:, 2] +  # Liquidity
            -0.1 * X[:, 3] + # Valuation level
            np.random.randn(n_samples) * 0.15
        )
        y = 1 / (1 + np.exp(-y))  # Sigmoid

        return X, y

    def _get_feature_names(self) -> List[str]:
        """Get feature names for interpretability"""
        return [
            "deal_size", "target_revenue", "ebitda_margin", "market_position",
            "management_quality", "industry_growth", "competitive_intensity",
            "regulatory_risk", "strategic_rationale_count", "synergy_potential"
        ]

    def _estimate_optimal_timeframe(self, timing_score: float) -> str:
        """Estimate optimal timeframe based on timing score"""
        if timing_score > 0.8:
            return "immediate_action"
        elif timing_score > 0.6:
            return "next_3_months"
        elif timing_score > 0.4:
            return "next_6_months"
        else:
            return "wait_for_better_conditions"

    def _identify_key_timing_factors(self, market_conditions: Dict[str, Any]) -> List[str]:
        """Identify key factors affecting timing decision"""
        factors = []

        if market_conditions.get("market_sentiment", 0.5) > 0.7:
            factors.append("positive_market_sentiment")
        if market_conditions.get("volatility", 0.2) < 0.15:
            factors.append("low_volatility_environment")
        if market_conditions.get("credit_availability", 0.8) > 0.75:
            factors.append("favorable_credit_conditions")

        return factors

class MarketIntelligenceEngine:
    """Main service orchestrating comprehensive market intelligence"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["market_intelligence"]
        self.competitive_analyzer = CompetitiveAnalyzer()
        self.predictive_models = PredictiveModels()

    async def generate_market_intelligence_report(
        self,
        sectors: Optional[List[str]] = None,
        include_predictions: bool = True
    ) -> MarketIntelligenceReport:
        """Generate comprehensive market intelligence report"""
        try:
            logger.info("Generating comprehensive market intelligence report")

            target_sectors = sectors or ["technology", "healthcare", "financial_services", "industrials"]

            # Gather market intelligence components
            tasks = [
                self._analyze_market_segments(target_sectors),
                self._analyze_valuation_trends(target_sectors),
                self._analyze_deal_timing(),
                self._get_economic_correlations(),
                self._get_regulatory_updates(),
                self._generate_market_forecast() if include_predictions else self._empty_forecast()
            ]

            (market_segments, valuation_trends, timing_analysis,
             economic_correlations, regulatory_updates, market_forecast) = await asyncio.gather(*tasks)

            # Generate competitive landscape for top sector
            competitive_landscape = await self.competitive_analyzer.analyze_competitive_landscape(
                target_sectors[0] if target_sectors else "technology"
            )

            # Generate insights and recommendations
            key_insights = await self._generate_key_insights(
                market_segments, valuation_trends, timing_analysis, competitive_landscape
            )

            strategic_recommendations = await self._generate_strategic_recommendations(
                market_segments, timing_analysis, competitive_landscape
            )

            return MarketIntelligenceReport(
                generated_at=datetime.utcnow(),
                market_segments=market_segments,
                valuation_trends=valuation_trends,
                timing_analysis=timing_analysis,
                competitive_landscape=competitive_landscape,
                economic_correlations=economic_correlations,
                regulatory_updates=regulatory_updates,
                key_insights=key_insights,
                strategic_recommendations=strategic_recommendations,
                market_forecast=market_forecast
            )

        except Exception as e:
            logger.error(f"Error generating market intelligence report: {e}")
            raise

    async def _analyze_market_segments(self, sectors: List[str]) -> List[MarketSegmentAnalysis]:
        """Analyze market segments with comprehensive data"""
        segment_analyses = []

        for sector in sectors:
            # Mock data - would integrate with industry databases
            segment_data = await self._get_segment_data(sector)

            analysis = MarketSegmentAnalysis(
                segment=sector,
                market_size=segment_data["market_size"],
                growth_rate=segment_data["growth_rate"],
                valuation_multiple_median=segment_data["valuation_multiple"],
                valuation_multiple_trend=segment_data["multiple_trend"],
                deal_count_12m=segment_data["deal_count"],
                deal_velocity=DealVelocity(segment_data["velocity"]),
                consolidation_activity=segment_data["consolidation"],
                regulatory_environment=segment_data["regulatory"],
                key_trends=segment_data["trends"],
                major_players=segment_data["players"],
                emerging_opportunities=segment_data["opportunities"]
            )
            segment_analyses.append(analysis)

        return segment_analyses

    async def _get_segment_data(self, sector: str) -> Dict[str, Any]:
        """Get market segment data"""
        # Mock data - would integrate with market research APIs
        segment_data = {
            "technology": {
                "market_size": 5_200_000_000_000,
                "growth_rate": 0.125,
                "valuation_multiple": 8.2,
                "multiple_trend": "stable",
                "deal_count": 1247,
                "velocity": "accelerating",
                "consolidation": "active",
                "regulatory": "increasing_scrutiny",
                "trends": ["AI adoption", "Cloud migration", "Cybersecurity focus"],
                "players": ["Microsoft", "Google", "Amazon", "Meta"],
                "opportunities": ["Edge computing", "Quantum technologies", "Green tech"]
            },
            "healthcare": {
                "market_size": 4_500_000_000_000,
                "growth_rate": 0.087,
                "valuation_multiple": 6.8,
                "multiple_trend": "increasing",
                "deal_count": 892,
                "velocity": "stable",
                "consolidation": "moderate",
                "regulatory": "stable",
                "trends": ["Digital health", "Personalized medicine", "Telehealth"],
                "players": ["UnitedHealth", "Johnson & Johnson", "Pfizer"],
                "opportunities": ["AI diagnostics", "Gene therapy", "Remote monitoring"]
            }
        }

        return segment_data.get(sector, {
            "market_size": 1_000_000_000_000,
            "growth_rate": 0.065,
            "valuation_multiple": 7.5,
            "multiple_trend": "stable",
            "deal_count": 500,
            "velocity": "stable",
            "consolidation": "moderate",
            "regulatory": "stable",
            "trends": ["Digital transformation", "Sustainability"],
            "players": ["Industry Leader"],
            "opportunities": ["Innovation", "Efficiency"]
        })

    async def _analyze_valuation_trends(self, sectors: List[str]) -> List[ValuationTrend]:
        """Analyze valuation trends across metrics and segments"""
        trends = []

        valuation_metrics = ["ev_revenue", "ev_ebitda", "price_book"]

        for metric in valuation_metrics:
            # Mock valuation data
            current_median = 8.2 if metric == "ev_revenue" else 15.5 if metric == "ev_ebitda" else 2.8
            twelve_month_high = current_median * 1.25
            twelve_month_low = current_median * 0.75
            volatility = np.random.uniform(0.15, 0.35)

            sector_breakdown = {sector: current_median * np.random.uniform(0.8, 1.2) for sector in sectors}
            size_segmentation = {
                "small_cap": current_median * 0.85,
                "mid_cap": current_median * 1.0,
                "large_cap": current_median * 1.15
            }
            geographic_variation = {
                "north_america": current_median * 1.05,
                "europe": current_median * 0.95,
                "asia": current_median * 1.10
            }

            trend = ValuationTrend(
                metric=metric,
                current_median=current_median,
                twelve_month_high=twelve_month_high,
                twelve_month_low=twelve_month_low,
                trend_direction="stable" if volatility < 0.2 else "volatile",
                volatility=volatility,
                sector_breakdown=sector_breakdown,
                size_segmentation=size_segmentation,
                geographic_variation=geographic_variation
            )
            trends.append(trend)

        return trends

    async def _analyze_deal_timing(self) -> DealTimingAnalysis:
        """Analyze current deal timing conditions"""
        # Mock market analysis - would integrate with economic data APIs
        market_indicators = await self._get_market_indicators()

        # Determine overall market condition
        if market_indicators["sentiment"] > 0.7 and market_indicators["volatility"] < 0.2:
            condition = MarketCondition.BULL_MARKET
        elif market_indicators["sentiment"] < 0.3 or market_indicators["volatility"] > 0.4:
            condition = MarketCondition.BEAR_MARKET
        elif market_indicators["volatility"] > 0.3:
            condition = MarketCondition.VOLATILE
        else:
            condition = MarketCondition.STABLE

        # Determine timing recommendation
        if condition == MarketCondition.BULL_MARKET:
            timing = TimingRecommendation.BUY_NOW
        elif condition == MarketCondition.STABLE:
            timing = TimingRecommendation.BUY_SOON
        elif condition == MarketCondition.VOLATILE:
            timing = TimingRecommendation.WAIT
        else:
            timing = TimingRecommendation.HOLD

        return DealTimingAnalysis(
            overall_market_condition=condition,
            optimal_deal_timing=timing,
            market_cycle_position="mid_cycle",
            expected_market_direction="cautiously_positive",
            timing_confidence=0.75,
            key_timing_factors=[
                "Interest rate environment",
                "Credit availability",
                "Regulatory environment",
                "Economic indicators"
            ],
            seasonal_patterns={
                "Q1": 0.85,
                "Q2": 1.10,
                "Q3": 0.95,
                "Q4": 1.05
            },
            economic_indicators_alignment={
                "gdp_growth": 0.75,
                "employment": 0.82,
                "inflation": 0.65,
                "interest_rates": 0.68
            }
        )

    async def _get_market_indicators(self) -> Dict[str, float]:
        """Get current market indicators"""
        return {
            "sentiment": 0.65,
            "volatility": 0.22,
            "liquidity": 0.78,
            "credit_spreads": 0.15,
            "equity_risk_premium": 0.06
        }

    async def _get_economic_correlations(self) -> List[EconomicCorrelation]:
        """Analyze correlation between economic indicators and M&A activity"""
        correlations = []

        indicators = [
            ("gdp_growth", 0.72, 2.8, "increasing", 0.15, 0.68, 2),
            ("unemployment_rate", -0.65, 3.7, "decreasing", -0.12, 0.62, 3),
            ("interest_rates", -0.58, 5.25, "stable", -0.18, 0.71, 1),
            ("corporate_bond_spreads", -0.45, 1.85, "decreasing", -0.08, 0.55, 1),
            ("dollar_index", -0.38, 103.2, "strengthening", -0.05, 0.48, 2)
        ]

        for indicator, correlation, current, trend, impact, power, lag in indicators:
            correlations.append(EconomicCorrelation(
                indicator=indicator,
                correlation_with_deal_activity=correlation,
                current_value=current,
                trend=trend,
                impact_on_valuations=impact,
                predictive_power=power,
                lag_months=lag
            ))

        return correlations

    async def _get_regulatory_updates(self) -> List[Dict[str, Any]]:
        """Get recent regulatory updates affecting M&A"""
        return [
            {
                "title": "EU Digital Services Act Implementation",
                "description": "New compliance requirements for tech acquisitions in EU",
                "effective_date": "2024-02-17",
                "impact_level": "high",
                "affected_sectors": ["technology"],
                "implications": ["Extended review periods", "Enhanced due diligence requirements"]
            },
            {
                "title": "US CFIUS Review Expansion",
                "description": "Expanded foreign investment review for critical infrastructure",
                "effective_date": "2024-03-01",
                "impact_level": "medium",
                "affected_sectors": ["technology", "healthcare", "energy"],
                "implications": ["Additional filing requirements", "Longer approval timelines"]
            }
        ]

    async def _generate_market_forecast(self) -> Dict[str, Any]:
        """Generate market forecast using predictive models"""
        return {
            "next_12_months": {
                "expected_deal_volume_change": 0.125,  # 12.5% increase
                "expected_valuation_change": -0.05,    # 5% decrease
                "confidence_interval": [0.08, 0.17]
            },
            "key_drivers": [
                "Economic policy normalization",
                "Corporate earnings growth",
                "Interest rate stabilization",
                "Geopolitical developments"
            ],
            "scenario_analysis": {
                "bull_case": {"deal_volume": 0.25, "valuations": 0.10},
                "base_case": {"deal_volume": 0.125, "valuations": -0.05},
                "bear_case": {"deal_volume": -0.05, "valuations": -0.15}
            },
            "sector_outlook": {
                "technology": "strong_growth",
                "healthcare": "moderate_growth",
                "financial_services": "consolidation_opportunities"
            }
        }

    async def _empty_forecast(self) -> Dict[str, Any]:
        """Return empty forecast when predictions not requested"""
        return {}

    async def _generate_key_insights(
        self,
        market_segments: List[MarketSegmentAnalysis],
        valuation_trends: List[ValuationTrend],
        timing_analysis: DealTimingAnalysis,
        competitive_landscape: CompetitiveLandscape
    ) -> List[str]:
        """Generate AI-powered key insights"""
        insights = []

        # Market timing insights
        if timing_analysis.optimal_deal_timing in [TimingRecommendation.BUY_NOW, TimingRecommendation.BUY_SOON]:
            insights.append(f"Current market conditions favor {timing_analysis.optimal_deal_timing.value.replace('_', ' ')} with {timing_analysis.timing_confidence:.0%} confidence")

        # Valuation insights
        high_volatility_metrics = [t for t in valuation_trends if t.volatility > 0.3]
        if high_volatility_metrics:
            insights.append(f"High valuation volatility in {len(high_volatility_metrics)} key metrics suggests opportunities for skilled acquirers")

        # Competitive insights
        if competitive_landscape.market_concentration > 2000:  # HHI threshold
            insights.append(f"Market shows high concentration with {competitive_landscape.total_active_players} active players - consolidation opportunities exist")

        # Growth insights
        high_growth_segments = [s for s in market_segments if s.growth_rate > 0.10]
        if high_growth_segments:
            insights.append(f"{len(high_growth_segments)} market segments showing >10% growth rates present premium acquisition opportunities")

        return insights

    async def _generate_strategic_recommendations(
        self,
        market_segments: List[MarketSegmentAnalysis],
        timing_analysis: DealTimingAnalysis,
        competitive_landscape: CompetitiveLandscape
    ) -> List[str]:
        """Generate strategic recommendations based on market intelligence"""
        recommendations = []

        # Timing-based recommendations
        if timing_analysis.optimal_deal_timing == TimingRecommendation.BUY_NOW:
            recommendations.append("Execute high-priority acquisitions immediately while market conditions remain favorable")
        elif timing_analysis.optimal_deal_timing == TimingRecommendation.WAIT:
            recommendations.append("Delay non-critical acquisitions and focus on due diligence and pipeline development")

        # Market-based recommendations
        accelerating_segments = [s for s in market_segments if s.deal_velocity == DealVelocity.ACCELERATING]
        if accelerating_segments:
            recommendations.append(f"Prioritize deals in {', '.join([s.segment for s in accelerating_segments])} sectors with accelerating deal velocity")

        # Competitive recommendations
        if competitive_landscape.new_entrants_12m > 5:
            recommendations.append("Monitor new market entrants for potential acquisition or partnership opportunities")

        # Gap-based recommendations
        if competitive_landscape.market_gaps:
            recommendations.append(f"Explore opportunities in underserved areas: {', '.join(competitive_landscape.market_gaps[:3])}")

        return recommendations

# Service factory function
_market_intelligence_engine = None

async def get_market_intelligence_engine() -> MarketIntelligenceEngine:
    """Get singleton market intelligence engine instance"""
    global _market_intelligence_engine
    if _market_intelligence_engine is None:
        _market_intelligence_engine = MarketIntelligenceEngine()
    return _market_intelligence_engine