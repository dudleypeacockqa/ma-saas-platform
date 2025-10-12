"""
Market Trends Service
Real-time M&A market trend analysis and predictive analytics
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import aiohttp
import json

from app.core.config import settings
from app.core.database import get_database
from app.marketplace import MARKETPLACE_CONFIG

logger = logging.getLogger(__name__)

class TrendDirection(str, Enum):
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"

class MarketSegment(str, Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCIAL_SERVICES = "financial_services"
    MANUFACTURING = "manufacturing"
    CONSUMER_GOODS = "consumer_goods"
    ENERGY = "energy"
    REAL_ESTATE = "real_estate"
    TELECOMMUNICATIONS = "telecommunications"

@dataclass
class MarketTrend:
    segment: MarketSegment
    metric: str
    current_value: float
    trend_direction: TrendDirection
    change_percentage: float
    confidence_level: float
    prediction_horizon: int  # days
    predicted_value: float
    factors: List[str]
    timestamp: datetime

@dataclass
class DealFlowMetrics:
    total_deals: int
    total_value: float
    average_deal_size: float
    median_deal_size: float
    deal_velocity: float  # deals per day
    success_rate: float
    time_to_close: float  # average days
    segment_breakdown: Dict[str, int]
    geographic_distribution: Dict[str, int]

@dataclass
class PricingBenchmark:
    segment: MarketSegment
    metric_type: str  # ev_revenue, ev_ebitda, price_book, etc.
    current_multiple: float
    twelve_month_average: float
    percentile_25: float
    percentile_75: float
    trend_direction: TrendDirection
    factors_driving_change: List[str]

@dataclass
class MarketIntelligenceReport:
    generated_at: datetime
    market_trends: List[MarketTrend]
    deal_flow_metrics: DealFlowMetrics
    pricing_benchmarks: List[PricingBenchmark]
    economic_indicators: Dict[str, float]
    regulatory_alerts: List[Dict[str, Any]]
    market_outlook: Dict[str, Any]
    key_insights: List[str]

class MarketTrendsService:
    """Service for analyzing M&A market trends and generating predictive insights"""

    def __init__(self):
        self.config = MARKETPLACE_CONFIG["intelligence"]
        self.trend_window = self.config["trend_analysis_window"]
        self.prediction_horizon = self.config["prediction_horizon"]
        self.confidence_intervals = self.config["confidence_intervals"]
        self.scaler = StandardScaler()

    async def get_real_time_market_intelligence(
        self,
        segments: Optional[List[MarketSegment]] = None,
        include_predictions: bool = True
    ) -> MarketIntelligenceReport:
        """Generate comprehensive real-time market intelligence report"""
        try:
            logger.info("Generating real-time market intelligence report")

            # Gather data from multiple sources in parallel
            tasks = [
                self._analyze_market_trends(segments),
                self._calculate_deal_flow_metrics(),
                self._get_pricing_benchmarks(segments),
                self._fetch_economic_indicators(),
                self._check_regulatory_alerts(),
                self._generate_market_outlook(segments) if include_predictions else asyncio.create_task(self._empty_outlook())
            ]

            trends, deal_flow, pricing, economic, regulatory, outlook = await asyncio.gather(*tasks)

            # Generate key insights
            insights = await self._generate_key_insights(trends, deal_flow, pricing, economic)

            return MarketIntelligenceReport(
                generated_at=datetime.utcnow(),
                market_trends=trends,
                deal_flow_metrics=deal_flow,
                pricing_benchmarks=pricing,
                economic_indicators=economic,
                regulatory_alerts=regulatory,
                market_outlook=outlook,
                key_insights=insights
            )

        except Exception as e:
            logger.error(f"Error generating market intelligence: {e}")
            raise

    async def _analyze_market_trends(self, segments: Optional[List[MarketSegment]]) -> List[MarketTrend]:
        """Analyze market trends across different segments and metrics"""
        trends = []
        target_segments = segments or list(MarketSegment)

        for segment in target_segments:
            # Get historical data for trend analysis
            historical_data = await self._get_historical_market_data(segment)

            # Analyze different metrics
            metrics = ["deal_volume", "deal_value", "average_multiple", "success_rate"]

            for metric in metrics:
                try:
                    trend = await self._calculate_trend(segment, metric, historical_data)
                    if trend:
                        trends.append(trend)
                except Exception as e:
                    logger.warning(f"Error calculating trend for {segment}/{metric}: {e}")

        return trends

    async def _calculate_trend(
        self,
        segment: MarketSegment,
        metric: str,
        data: pd.DataFrame
    ) -> Optional[MarketTrend]:
        """Calculate trend for a specific segment and metric"""
        if data.empty or metric not in data.columns:
            return None

        # Prepare data for trend analysis
        values = data[metric].values
        dates = pd.to_datetime(data['date'])

        if len(values) < 5:  # Need minimum data points
            return None

        # Calculate trend using linear regression
        X = np.arange(len(values)).reshape(-1, 1)
        y = values

        model = LinearRegression()
        model.fit(X, y)

        # Determine trend direction and strength
        slope = model.coef_[0]
        current_value = float(values[-1])
        predicted_value = float(model.predict([[len(values) + self.prediction_horizon]])[0])

        # Calculate percentage change
        if current_value != 0:
            change_percentage = ((predicted_value - current_value) / current_value) * 100
        else:
            change_percentage = 0.0

        # Determine trend direction
        if abs(slope) < 0.01:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING

        # Check for volatility
        volatility = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
        if volatility > 0.3:
            direction = TrendDirection.VOLATILE

        # Calculate confidence level
        confidence = min(0.95, max(0.5, 1 - volatility))

        # Identify driving factors
        factors = await self._identify_trend_factors(segment, metric, direction)

        return MarketTrend(
            segment=segment,
            metric=metric,
            current_value=current_value,
            trend_direction=direction,
            change_percentage=change_percentage,
            confidence_level=confidence,
            prediction_horizon=self.prediction_horizon,
            predicted_value=predicted_value,
            factors=factors,
            timestamp=datetime.utcnow()
        )

    async def _calculate_deal_flow_metrics(self) -> DealFlowMetrics:
        """Calculate comprehensive deal flow metrics"""
        db = await get_database()

        # Get deals from last 30 days for velocity calculation
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # Mock data - in production this would query real deal database
        total_deals = 1247
        total_value = 45_800_000_000  # $45.8B
        average_deal_size = total_value / total_deals
        median_deal_size = 28_500_000  # $28.5M
        deal_velocity = total_deals / 30  # deals per day
        success_rate = 0.73  # 73%
        time_to_close = 89.5  # days

        segment_breakdown = {
            "technology": 387,
            "healthcare": 298,
            "financial_services": 156,
            "manufacturing": 203,
            "consumer_goods": 112,
            "energy": 91
        }

        geographic_distribution = {
            "north_america": 598,
            "europe": 356,
            "asia_pacific": 201,
            "latin_america": 67,
            "middle_east_africa": 25
        }

        return DealFlowMetrics(
            total_deals=total_deals,
            total_value=total_value,
            average_deal_size=average_deal_size,
            median_deal_size=median_deal_size,
            deal_velocity=deal_velocity,
            success_rate=success_rate,
            time_to_close=time_to_close,
            segment_breakdown=segment_breakdown,
            geographic_distribution=geographic_distribution
        )

    async def _get_pricing_benchmarks(self, segments: Optional[List[MarketSegment]]) -> List[PricingBenchmark]:
        """Get current pricing benchmarks and multiples"""
        benchmarks = []
        target_segments = segments or list(MarketSegment)

        # Mock pricing data - in production would integrate with financial data providers
        benchmark_data = {
            MarketSegment.TECHNOLOGY: {
                "ev_revenue": (8.2, 7.8, 6.1, 12.3),
                "ev_ebitda": (18.5, 17.2, 14.1, 25.8),
                "price_book": (4.7, 4.3, 3.2, 7.1)
            },
            MarketSegment.HEALTHCARE: {
                "ev_revenue": (5.8, 5.9, 4.2, 8.7),
                "ev_ebitda": (15.2, 14.8, 11.9, 19.3),
                "price_book": (3.1, 3.0, 2.1, 4.8)
            }
        }

        for segment in target_segments:
            if segment in benchmark_data:
                for metric_type, (current, avg_12m, p25, p75) in benchmark_data[segment].items():
                    trend_dir = TrendDirection.INCREASING if current > avg_12m else TrendDirection.DECREASING
                    if abs(current - avg_12m) / avg_12m < 0.05:
                        trend_dir = TrendDirection.STABLE

                    factors = ["Market sentiment", "Sector performance", "Interest rates", "Economic outlook"]

                    benchmarks.append(PricingBenchmark(
                        segment=segment,
                        metric_type=metric_type,
                        current_multiple=current,
                        twelve_month_average=avg_12m,
                        percentile_25=p25,
                        percentile_75=p75,
                        trend_direction=trend_dir,
                        factors_driving_change=factors
                    ))

        return benchmarks

    async def _fetch_economic_indicators(self) -> Dict[str, float]:
        """Fetch relevant economic indicators that impact M&A activity"""
        # Mock data - in production would integrate with economic data APIs
        indicators = {
            "gdp_growth_rate": 2.8,
            "unemployment_rate": 3.7,
            "inflation_rate": 2.4,
            "federal_funds_rate": 5.25,
            "corporate_bond_spreads": 1.85,
            "vix_volatility_index": 18.3,
            "dollar_index": 103.2,
            "credit_availability_index": 67.8
        }

        return indicators

    async def _check_regulatory_alerts(self) -> List[Dict[str, Any]]:
        """Check for regulatory changes that might impact M&A activity"""
        alerts = [
            {
                "id": "reg_001",
                "title": "EU Digital Services Act Implementation",
                "description": "New compliance requirements for tech acquisitions in EU",
                "impact_level": "high",
                "affected_segments": ["technology"],
                "effective_date": "2024-02-17",
                "requirements": ["Enhanced due diligence", "Regulatory approval timelines"]
            },
            {
                "id": "reg_002",
                "title": "US CFIUS Review Expansion",
                "description": "Expanded foreign investment review for critical infrastructure",
                "impact_level": "medium",
                "affected_segments": ["technology", "healthcare", "energy"],
                "effective_date": "2024-03-01",
                "requirements": ["Additional filing requirements", "Extended review periods"]
            }
        ]

        return alerts

    async def _generate_market_outlook(self, segments: Optional[List[MarketSegment]]) -> Dict[str, Any]:
        """Generate predictive market outlook"""
        outlook = {
            "overall_sentiment": "cautiously_optimistic",
            "predicted_deal_volume_change": 12.5,  # percentage
            "predicted_valuation_change": -3.2,    # percentage
            "key_growth_sectors": ["artificial_intelligence", "renewable_energy", "healthcare_technology"],
            "risk_factors": ["Interest rate volatility", "Geopolitical tensions", "Regulatory uncertainty"],
            "opportunities": ["Distressed assets", "Digital transformation", "ESG compliance solutions"],
            "timing_recommendations": {
                "best_months_to_buy": ["Q1", "Q4"],
                "best_months_to_sell": ["Q2", "Q3"],
                "expected_cycle_duration": "18-24 months"
            }
        }

        return outlook

    async def _generate_key_insights(
        self,
        trends: List[MarketTrend],
        deal_flow: DealFlowMetrics,
        pricing: List[PricingBenchmark],
        economic: Dict[str, float]
    ) -> List[str]:
        """Generate key insights from market analysis"""
        insights = []

        # Deal flow insights
        if deal_flow.deal_velocity > 40:
            insights.append(f"Market activity is {deal_flow.deal_velocity:.1f} deals/day, indicating strong M&A momentum")

        # Pricing insights
        tech_multiples = [p for p in pricing if p.segment == MarketSegment.TECHNOLOGY]
        if tech_multiples:
            avg_multiple = sum(p.current_multiple for p in tech_multiples) / len(tech_multiples)
            if avg_multiple > 15:
                insights.append("Technology sector trading at premium multiples - consider timing for exits")

        # Economic insights
        if economic.get("federal_funds_rate", 0) > 5:
            insights.append("High interest rates may pressure deal financing and valuations")

        # Trend insights
        increasing_trends = [t for t in trends if t.trend_direction == TrendDirection.INCREASING]
        if len(increasing_trends) > len(trends) * 0.6:
            insights.append("Majority of market metrics showing positive trends - favorable M&A environment")

        return insights

    async def _get_historical_market_data(self, segment: MarketSegment) -> pd.DataFrame:
        """Get historical market data for trend analysis"""
        # Mock data - in production would query historical database
        dates = pd.date_range(
            start=datetime.utcnow() - timedelta(days=self.trend_window),
            end=datetime.utcnow(),
            freq='D'
        )

        np.random.seed(42)  # For reproducible mock data
        n_points = len(dates)

        data = pd.DataFrame({
            'date': dates,
            'deal_volume': np.random.poisson(15, n_points) + np.random.randint(-3, 3, n_points),
            'deal_value': np.random.normal(1200, 300, n_points) * 1_000_000,
            'average_multiple': np.random.normal(12.5, 2.1, n_points),
            'success_rate': np.random.beta(8, 3, n_points)
        })

        return data

    async def _identify_trend_factors(
        self,
        segment: MarketSegment,
        metric: str,
        direction: TrendDirection
    ) -> List[str]:
        """Identify factors driving market trends"""
        factor_map = {
            MarketSegment.TECHNOLOGY: {
                TrendDirection.INCREASING: ["AI investment surge", "Digital transformation demand", "Cloud adoption"],
                TrendDirection.DECREASING: ["Interest rate pressure", "Regulatory scrutiny", "Valuation correction"],
            },
            MarketSegment.HEALTHCARE: {
                TrendDirection.INCREASING: ["Aging population", "Medical innovation", "Post-pandemic recovery"],
                TrendDirection.DECREASING: ["Regulatory approval delays", "Pricing pressure", "Patent cliffs"],
            }
        }

        return factor_map.get(segment, {}).get(direction, ["Market dynamics", "Economic conditions"])

    async def _empty_outlook(self) -> Dict[str, Any]:
        """Return empty outlook when predictions not requested"""
        return {}

    async def get_segment_deep_dive(self, segment: MarketSegment) -> Dict[str, Any]:
        """Get detailed analysis for a specific market segment"""
        return {
            "segment": segment.value,
            "market_size": await self._calculate_segment_market_size(segment),
            "growth_rate": await self._calculate_segment_growth_rate(segment),
            "competitive_landscape": await self._analyze_competitive_landscape(segment),
            "key_players": await self._identify_key_players(segment),
            "investment_themes": await self._identify_investment_themes(segment),
            "risk_factors": await self._analyze_segment_risks(segment),
            "opportunities": await self._identify_segment_opportunities(segment)
        }

    async def _calculate_segment_market_size(self, segment: MarketSegment) -> float:
        """Calculate total addressable market size for segment"""
        # Mock data - would integrate with market research APIs
        sizes = {
            MarketSegment.TECHNOLOGY: 8_500_000_000_000,  # $8.5T
            MarketSegment.HEALTHCARE: 4_200_000_000_000,  # $4.2T
            MarketSegment.FINANCIAL_SERVICES: 6_800_000_000_000,  # $6.8T
        }
        return sizes.get(segment, 1_000_000_000_000)

    async def _calculate_segment_growth_rate(self, segment: MarketSegment) -> float:
        """Calculate segment growth rate"""
        rates = {
            MarketSegment.TECHNOLOGY: 0.128,  # 12.8%
            MarketSegment.HEALTHCARE: 0.087,  # 8.7%
            MarketSegment.FINANCIAL_SERVICES: 0.054,  # 5.4%
        }
        return rates.get(segment, 0.065)

    async def _analyze_competitive_landscape(self, segment: MarketSegment) -> Dict[str, Any]:
        """Analyze competitive landscape for segment"""
        return {
            "concentration_level": "moderate",
            "barriers_to_entry": "high",
            "disruption_risk": "medium",
            "consolidation_trend": "active"
        }

    async def _identify_key_players(self, segment: MarketSegment) -> List[str]:
        """Identify key players in segment"""
        players = {
            MarketSegment.TECHNOLOGY: ["Microsoft", "Apple", "Google", "Amazon", "Meta"],
            MarketSegment.HEALTHCARE: ["UnitedHealth", "Johnson & Johnson", "Pfizer", "Roche", "Novartis"],
        }
        return players.get(segment, ["Market Leader 1", "Market Leader 2", "Market Leader 3"])

    async def _identify_investment_themes(self, segment: MarketSegment) -> List[str]:
        """Identify key investment themes for segment"""
        themes = {
            MarketSegment.TECHNOLOGY: ["Artificial Intelligence", "Cloud Infrastructure", "Cybersecurity"],
            MarketSegment.HEALTHCARE: ["Digital Health", "Precision Medicine", "Medical Devices"],
        }
        return themes.get(segment, ["Digital Transformation", "Sustainability", "Innovation"])

    async def _analyze_segment_risks(self, segment: MarketSegment) -> List[str]:
        """Analyze key risks for segment"""
        risks = {
            MarketSegment.TECHNOLOGY: ["Regulatory scrutiny", "Talent shortage", "Cybersecurity threats"],
            MarketSegment.HEALTHCARE: ["Regulatory approval risks", "Pricing pressure", "Clinical trial failures"],
        }
        return risks.get(segment, ["Economic downturn", "Competition", "Regulatory changes"])

    async def _identify_segment_opportunities(self, segment: MarketSegment) -> List[str]:
        """Identify opportunities in segment"""
        opportunities = {
            MarketSegment.TECHNOLOGY: ["AI adoption", "Edge computing", "Quantum computing"],
            MarketSegment.HEALTHCARE: ["Aging population", "Personalized medicine", "Digital therapeutics"],
        }
        return opportunities.get(segment, ["Market expansion", "Innovation", "Efficiency gains"])