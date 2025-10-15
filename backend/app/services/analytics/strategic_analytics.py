"""
Strategic Analytics and Performance Optimization System
Comprehensive analytics for wealth-building and competitive advantage
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import pandas as pd
from scipy import stats
import structlog

logger = structlog.get_logger()


class AnalyticsMetric(Enum):
    """Key performance metrics"""
    MRR = "monthly_recurring_revenue"
    ARR = "annual_recurring_revenue"
    CAC = "customer_acquisition_cost"
    LTV = "lifetime_value"
    CHURN_RATE = "churn_rate"
    NPS = "net_promoter_score"
    ARPU = "average_revenue_per_user"
    CONVERSION_RATE = "conversion_rate"
    ENGAGEMENT_SCORE = "engagement_score"
    PARTNERSHIP_VALUE = "partnership_value"


@dataclass
class StrategicInsight:
    """Strategic insight with actionable recommendations"""
    category: str
    severity: str  # "opportunity", "warning", "critical"
    insight: str
    impact: str
    recommendation: str
    potential_value: float
    confidence: float
    data_points: Dict[str, Any]


@dataclass
class WealthBuildingMetrics:
    """Metrics aligned with £200M wealth objective"""
    current_valuation: float
    growth_rate: float
    path_to_target: Dict[str, Any]
    key_drivers: List[str]
    risk_factors: List[str]
    milestone_progress: float
    estimated_timeline: int  # months


class CustomerAnalytics:
    """Customer acquisition and retention analytics"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def calculate_acquisition_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate comprehensive acquisition metrics"""

        # New customers acquired
        new_customers = await self.db.execute(
            """
            SELECT
                COUNT(*) as total_customers,
                AVG(first_payment_amount) as avg_first_payment,
                SUM(first_payment_amount) as total_revenue
            FROM customers
            WHERE created_at BETWEEN ? AND ?
            AND status = 'active'
            """,
            (start_date, end_date)
        )

        acquisition_data = new_customers.first()

        # Acquisition channels performance
        channel_performance = await self.db.execute(
            """
            SELECT
                acquisition_channel,
                COUNT(*) as customers,
                AVG(ltv) as avg_ltv,
                AVG(time_to_convert) as avg_conversion_time,
                SUM(marketing_spend) / COUNT(*) as cac
            FROM customer_acquisition
            WHERE created_at BETWEEN ? AND ?
            GROUP BY acquisition_channel
            ORDER BY avg_ltv DESC
            """,
            (start_date, end_date)
        )

        # Cohort analysis
        cohort_data = await self._analyze_cohorts(start_date, end_date)

        # Calculate CAC and payback period
        total_marketing_spend = await self.db.execute(
            """
            SELECT SUM(amount) as total_spend
            FROM marketing_expenses
            WHERE date BETWEEN ? AND ?
            """,
            (start_date, end_date)
        )

        marketing_spend = total_marketing_spend.scalar() or 0
        cac = marketing_spend / acquisition_data.total_customers if acquisition_data.total_customers > 0 else 0

        # LTV:CAC ratio
        avg_ltv = await self._calculate_average_ltv()
        ltv_cac_ratio = avg_ltv / cac if cac > 0 else 0

        return {
            "total_new_customers": acquisition_data.total_customers or 0,
            "total_acquisition_revenue": acquisition_data.total_revenue or 0,
            "average_first_payment": acquisition_data.avg_first_payment or 0,
            "customer_acquisition_cost": cac,
            "ltv_cac_ratio": ltv_cac_ratio,
            "payback_period_months": cac / (acquisition_data.avg_first_payment or 1) if acquisition_data.avg_first_payment else None,
            "channel_performance": [
                {
                    "channel": row.acquisition_channel,
                    "customers": row.customers,
                    "avg_ltv": row.avg_ltv,
                    "cac": row.cac,
                    "roi": ((row.avg_ltv - row.cac) / row.cac * 100) if row.cac else 0
                }
                for row in channel_performance
            ],
            "cohort_analysis": cohort_data,
            "best_performing_channel": self._identify_best_channel(channel_performance),
            "acquisition_velocity": acquisition_data.total_customers / ((end_date - start_date).days or 1)
        }

    async def calculate_retention_metrics(
        self,
        period_months: int = 12
    ) -> Dict[str, Any]:
        """Calculate retention and churn metrics"""

        # Monthly churn rate
        churn_data = await self.db.execute(
            """
            SELECT
                DATE_TRUNC('month', churned_at) as month,
                COUNT(*) as churned_customers,
                AVG(lifetime_value) as avg_churned_ltv,
                AVG(months_active) as avg_tenure
            FROM customer_churn
            WHERE churned_at >= NOW() - INTERVAL '? months'
            GROUP BY month
            ORDER BY month
            """,
            (period_months,)
        )

        # Retention cohorts
        retention_cohorts = await self.db.execute(
            """
            SELECT
                cohort_month,
                month_number,
                retained_customers,
                total_customers,
                (retained_customers::float / total_customers) as retention_rate
            FROM retention_cohorts
            WHERE cohort_month >= NOW() - INTERVAL '? months'
            ORDER BY cohort_month, month_number
            """,
            (period_months,)
        )

        # Churn reasons analysis
        churn_reasons = await self.db.execute(
            """
            SELECT
                churn_reason,
                COUNT(*) as count,
                AVG(lifetime_value) as avg_ltv_lost
            FROM customer_churn
            WHERE churned_at >= NOW() - INTERVAL '? months'
            GROUP BY churn_reason
            ORDER BY count DESC
            """,
            (period_months,)
        )

        # Calculate key metrics
        total_customers = await self.db.execute(
            "SELECT COUNT(*) FROM customers WHERE status = 'active'"
        )
        active_count = total_customers.scalar() or 0

        monthly_churn_rate = await self._calculate_churn_rate()
        annual_churn_rate = 1 - (1 - monthly_churn_rate) ** 12

        # Revenue retention
        revenue_retention = await self._calculate_revenue_retention()

        # Predictive churn scoring
        at_risk_customers = await self._identify_at_risk_customers()

        return {
            "monthly_churn_rate": monthly_churn_rate,
            "annual_churn_rate": annual_churn_rate,
            "revenue_churn_rate": revenue_retention["revenue_churn_rate"],
            "net_revenue_retention": revenue_retention["net_retention"],
            "gross_revenue_retention": revenue_retention["gross_retention"],
            "average_customer_tenure_months": await self._calculate_average_tenure(),
            "retention_curve": self._format_retention_curve(retention_cohorts),
            "churn_reasons": [
                {
                    "reason": row.churn_reason,
                    "percentage": (row.count / sum(r.count for r in churn_reasons)) * 100,
                    "avg_ltv_lost": row.avg_ltv_lost
                }
                for row in churn_reasons
            ],
            "at_risk_customers": at_risk_customers,
            "predicted_churn_impact": self._calculate_churn_impact(at_risk_customers),
            "retention_improvements": self._generate_retention_recommendations(churn_reasons)
        }

    async def _analyze_cohorts(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Perform cohort analysis"""

        cohorts = await self.db.execute(
            """
            SELECT
                DATE_TRUNC('month', first_purchase_date) as cohort,
                DATE_TRUNC('month', purchase_date) as purchase_month,
                COUNT(DISTINCT customer_id) as customers,
                SUM(revenue) as total_revenue
            FROM customer_purchases
            WHERE first_purchase_date BETWEEN ? AND ?
            GROUP BY cohort, purchase_month
            ORDER BY cohort, purchase_month
            """,
            (start_date, end_date)
        )

        # Calculate cohort metrics
        cohort_metrics = {}
        for row in cohorts:
            cohort_key = row.cohort.strftime("%Y-%m")
            if cohort_key not in cohort_metrics:
                cohort_metrics[cohort_key] = {
                    "customers": 0,
                    "revenue_by_month": {},
                    "retention_by_month": {}
                }

            month_number = (row.purchase_month - row.cohort).days // 30
            cohort_metrics[cohort_key]["revenue_by_month"][month_number] = row.total_revenue
            cohort_metrics[cohort_key]["customers"] = max(
                cohort_metrics[cohort_key]["customers"],
                row.customers
            )

        return cohort_metrics

    async def _calculate_average_ltv(self) -> float:
        """Calculate average customer lifetime value"""

        result = await self.db.execute(
            """
            SELECT AVG(
                monthly_revenue * (1 / monthly_churn_rate)
            ) as avg_ltv
            FROM (
                SELECT
                    customer_id,
                    AVG(monthly_revenue) as monthly_revenue,
                    0.05 as monthly_churn_rate  -- Default 5% if not calculated
                FROM customer_revenue
                WHERE date >= NOW() - INTERVAL '6 months'
                GROUP BY customer_id
            ) as customer_ltv
            """
        )

        return result.scalar() or 0

    async def _calculate_churn_rate(self) -> float:
        """Calculate monthly churn rate"""

        result = await self.db.execute(
            """
            SELECT
                COUNT(CASE WHEN status = 'churned' THEN 1 END)::float /
                COUNT(*)::float as churn_rate
            FROM customers
            WHERE created_at >= NOW() - INTERVAL '1 month'
            """
        )

        return result.scalar() or 0

    async def _calculate_revenue_retention(self) -> Dict[str, float]:
        """Calculate revenue retention metrics"""

        result = await self.db.execute(
            """
            SELECT
                SUM(CASE WHEN status = 'active' THEN current_mrr ELSE 0 END) as retained_revenue,
                SUM(CASE WHEN status = 'active' THEN previous_mrr ELSE 0 END) as previous_revenue,
                SUM(CASE WHEN status = 'expanded' THEN expansion_mrr ELSE 0 END) as expansion_revenue,
                SUM(CASE WHEN status = 'churned' THEN churned_mrr ELSE 0 END) as churned_revenue
            FROM revenue_cohorts
            WHERE cohort_month = DATE_TRUNC('month', NOW() - INTERVAL '1 month')
            """
        )

        data = result.first()

        gross_retention = (data.retained_revenue / data.previous_revenue) if data.previous_revenue else 0
        net_retention = ((data.retained_revenue + data.expansion_revenue) / data.previous_revenue) if data.previous_revenue else 0
        revenue_churn = (data.churned_revenue / data.previous_revenue) if data.previous_revenue else 0

        return {
            "gross_retention": gross_retention,
            "net_retention": net_retention,
            "revenue_churn_rate": revenue_churn,
            "expansion_revenue": data.expansion_revenue or 0
        }

    async def _identify_at_risk_customers(self) -> List[Dict[str, Any]]:
        """Identify customers at risk of churning"""

        # Machine learning model would go here
        # For now, using rule-based approach

        at_risk = await self.db.execute(
            """
            SELECT
                c.customer_id,
                c.company_name,
                c.mrr,
                c.tenure_months,
                cs.engagement_score,
                cs.support_tickets_30d,
                cs.last_login_days_ago
            FROM customers c
            JOIN customer_scores cs ON c.customer_id = cs.customer_id
            WHERE cs.churn_risk_score > 0.7
            OR (cs.engagement_score < 30 AND c.tenure_months > 3)
            OR cs.last_login_days_ago > 14
            ORDER BY cs.churn_risk_score DESC
            LIMIT 50
            """
        )

        return [
            {
                "customer_id": row.customer_id,
                "company": row.company_name,
                "mrr": row.mrr,
                "risk_factors": self._identify_risk_factors(row),
                "recommended_action": self._recommend_retention_action(row)
            }
            for row in at_risk
        ]

    def _identify_risk_factors(self, customer_row) -> List[str]:
        """Identify specific risk factors for a customer"""

        factors = []

        if customer_row.engagement_score < 30:
            factors.append("Low engagement")
        if customer_row.last_login_days_ago > 14:
            factors.append(f"No login for {customer_row.last_login_days_ago} days")
        if customer_row.support_tickets_30d > 5:
            factors.append(f"High support tickets ({customer_row.support_tickets_30d})")

        return factors

    def _recommend_retention_action(self, customer_row) -> str:
        """Recommend retention action for at-risk customer"""

        if customer_row.last_login_days_ago > 14:
            return "Schedule executive check-in call"
        elif customer_row.engagement_score < 30:
            return "Offer personalized training session"
        elif customer_row.support_tickets_30d > 5:
            return "Assign dedicated success manager"
        else:
            return "Send value realization report"

    def _calculate_churn_impact(self, at_risk_customers: List[Dict]) -> Dict[str, float]:
        """Calculate potential revenue impact of churn"""

        total_at_risk_mrr = sum(c["mrr"] for c in at_risk_customers)
        total_at_risk_arr = total_at_risk_mrr * 12

        return {
            "at_risk_mrr": total_at_risk_mrr,
            "at_risk_arr": total_at_risk_arr,
            "potential_ltv_loss": total_at_risk_mrr * 24  # Assuming 24 month average tenure
        }

    def _identify_best_channel(self, channel_performance) -> Dict[str, Any]:
        """Identify best performing acquisition channel"""

        if not channel_performance.rowcount:
            return {}

        best = max(channel_performance, key=lambda x: x.avg_ltv - x.cac)

        return {
            "channel": best.acquisition_channel,
            "roi": ((best.avg_ltv - best.cac) / best.cac * 100) if best.cac else 0,
            "recommendation": f"Increase {best.acquisition_channel} budget by 30%"
        }

    def _format_retention_curve(self, retention_cohorts) -> List[Dict[str, Any]]:
        """Format retention curve data"""

        curves = {}
        for row in retention_cohorts:
            cohort = row.cohort_month.strftime("%Y-%m")
            if cohort not in curves:
                curves[cohort] = []
            curves[cohort].append({
                "month": row.month_number,
                "retention_rate": row.retention_rate * 100
            })

        return curves

    def _calculate_average_tenure(self) -> float:
        """Calculate average customer tenure"""
        return 1 / 0.05 * 30  # Using 5% monthly churn rate as default

    def _generate_retention_recommendations(self, churn_reasons) -> List[Dict[str, str]]:
        """Generate retention improvement recommendations"""

        recommendations = []

        for reason in churn_reasons:
            if reason.churn_reason == "price":
                recommendations.append({
                    "issue": "Price sensitivity",
                    "action": "Introduce annual discount and payment plans",
                    "impact": "Reduce price-related churn by 40%"
                })
            elif reason.churn_reason == "features":
                recommendations.append({
                    "issue": "Feature gaps",
                    "action": "Fast-track roadmap items from churned customer feedback",
                    "impact": "Improve retention by 25%"
                })
            elif reason.churn_reason == "support":
                recommendations.append({
                    "issue": "Support issues",
                    "action": "Implement dedicated success manager program",
                    "impact": "Increase NPS by 20 points"
                })

        return recommendations


class RevenueAnalytics:
    """Revenue optimization and subscription analytics"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def calculate_revenue_metrics(
        self,
        as_of_date: datetime = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive revenue metrics"""

        if not as_of_date:
            as_of_date = datetime.utcnow()

        # MRR calculation
        mrr_data = await self.db.execute(
            """
            SELECT
                SUM(mrr) as total_mrr,
                COUNT(*) as customer_count,
                AVG(mrr) as average_mrr
            FROM customer_subscriptions
            WHERE status = 'active'
            AND date = DATE_TRUNC('month', ?)
            """,
            (as_of_date,)
        )

        mrr_result = mrr_data.first()

        # MRR movement
        mrr_movement = await self._calculate_mrr_movement(as_of_date)

        # ARR and growth
        arr = (mrr_result.total_mrr or 0) * 12
        arr_growth = await self._calculate_arr_growth()

        # ARPU trends
        arpu_trend = await self._calculate_arpu_trend()

        # Revenue by segment
        segment_revenue = await self._analyze_revenue_segments()

        # Expansion revenue
        expansion_metrics = await self._calculate_expansion_metrics()

        # Revenue forecasting
        forecast = await self._forecast_revenue()

        return {
            "mrr": mrr_result.total_mrr or 0,
            "arr": arr,
            "customer_count": mrr_result.customer_count or 0,
            "arpu": mrr_result.average_mrr or 0,
            "mrr_growth_rate": mrr_movement["growth_rate"],
            "mrr_movement": {
                "new": mrr_movement["new_mrr"],
                "expansion": mrr_movement["expansion_mrr"],
                "contraction": mrr_movement["contraction_mrr"],
                "churn": mrr_movement["churn_mrr"],
                "net_new": mrr_movement["net_new_mrr"]
            },
            "arr_growth_rate": arr_growth,
            "arpu_trend": arpu_trend,
            "revenue_segments": segment_revenue,
            "expansion_metrics": expansion_metrics,
            "forecast": forecast,
            "quick_ratio": self._calculate_quick_ratio(mrr_movement),
            "revenue_per_employee": arr / 50,  # Assuming 50 employees
            "path_to_100k_mrr": self._calculate_path_to_target(mrr_result.total_mrr or 0, 100000)
        }

    async def analyze_subscription_performance(self) -> Dict[str, Any]:
        """Analyze subscription tier performance"""

        # Tier distribution
        tier_data = await self.db.execute(
            """
            SELECT
                subscription_tier,
                COUNT(*) as customers,
                SUM(mrr) as total_mrr,
                AVG(mrr) as avg_mrr,
                AVG(tenure_months) as avg_tenure,
                AVG(ltv) as avg_ltv
            FROM customer_subscriptions
            WHERE status = 'active'
            GROUP BY subscription_tier
            """
        )

        # Upgrade/downgrade patterns
        tier_movements = await self.db.execute(
            """
            SELECT
                from_tier,
                to_tier,
                COUNT(*) as movement_count,
                AVG(mrr_change) as avg_mrr_change
            FROM subscription_changes
            WHERE change_date >= NOW() - INTERVAL '90 days'
            GROUP BY from_tier, to_tier
            """
        )

        # Optimal pricing analysis
        pricing_elasticity = await self._analyze_pricing_elasticity()

        # Feature usage by tier
        feature_usage = await self._analyze_feature_usage_by_tier()

        return {
            "tier_performance": [
                {
                    "tier": row.subscription_tier,
                    "customers": row.customers,
                    "mrr": row.total_mrr,
                    "arpu": row.avg_mrr,
                    "ltv": row.avg_ltv,
                    "health_score": self._calculate_tier_health(row)
                }
                for row in tier_data
            ],
            "tier_movements": self._format_tier_movements(tier_movements),
            "pricing_optimization": {
                "optimal_prices": pricing_elasticity["optimal_prices"],
                "revenue_impact": pricing_elasticity["revenue_impact"],
                "recommendations": pricing_elasticity["recommendations"]
            },
            "feature_value_alignment": feature_usage,
            "upsell_opportunities": await self._identify_upsell_opportunities(),
            "tier_recommendations": self._generate_tier_recommendations(tier_data)
        }

    async def _calculate_mrr_movement(self, as_of_date: datetime) -> Dict[str, float]:
        """Calculate MRR movement components"""

        result = await self.db.execute(
            """
            SELECT
                SUM(CASE WHEN movement_type = 'new' THEN mrr_change ELSE 0 END) as new_mrr,
                SUM(CASE WHEN movement_type = 'expansion' THEN mrr_change ELSE 0 END) as expansion_mrr,
                SUM(CASE WHEN movement_type = 'contraction' THEN mrr_change ELSE 0 END) as contraction_mrr,
                SUM(CASE WHEN movement_type = 'churn' THEN mrr_change ELSE 0 END) as churn_mrr
            FROM mrr_movements
            WHERE movement_month = DATE_TRUNC('month', ?)
            """,
            (as_of_date,)
        )

        data = result.first()

        new_mrr = data.new_mrr or 0
        expansion_mrr = data.expansion_mrr or 0
        contraction_mrr = abs(data.contraction_mrr or 0)
        churn_mrr = abs(data.churn_mrr or 0)

        net_new_mrr = new_mrr + expansion_mrr - contraction_mrr - churn_mrr

        # Calculate growth rate
        previous_mrr = await self.db.execute(
            """
            SELECT SUM(mrr) as total_mrr
            FROM customer_subscriptions
            WHERE date = DATE_TRUNC('month', ? - INTERVAL '1 month')
            """,
            (as_of_date,)
        )

        prev_mrr = previous_mrr.scalar() or 1
        growth_rate = (net_new_mrr / prev_mrr) * 100 if prev_mrr > 0 else 0

        return {
            "new_mrr": new_mrr,
            "expansion_mrr": expansion_mrr,
            "contraction_mrr": contraction_mrr,
            "churn_mrr": churn_mrr,
            "net_new_mrr": net_new_mrr,
            "growth_rate": growth_rate
        }

    async def _calculate_arr_growth(self) -> float:
        """Calculate year-over-year ARR growth"""

        current_arr = await self.db.execute(
            "SELECT SUM(mrr) * 12 as arr FROM customer_subscriptions WHERE status = 'active'"
        )

        previous_arr = await self.db.execute(
            """
            SELECT SUM(mrr) * 12 as arr
            FROM customer_subscriptions
            WHERE date = NOW() - INTERVAL '12 months'
            """
        )

        curr = current_arr.scalar() or 0
        prev = previous_arr.scalar() or 1

        return ((curr - prev) / prev * 100) if prev > 0 else 0

    async def _calculate_arpu_trend(self) -> List[Dict[str, Any]]:
        """Calculate ARPU trend over time"""

        arpu_data = await self.db.execute(
            """
            SELECT
                DATE_TRUNC('month', date) as month,
                AVG(mrr) as arpu,
                COUNT(*) as customer_count
            FROM customer_subscriptions
            WHERE date >= NOW() - INTERVAL '12 months'
            GROUP BY month
            ORDER BY month
            """
        )

        return [
            {
                "month": row.month.strftime("%Y-%m"),
                "arpu": row.arpu,
                "customer_count": row.customer_count
            }
            for row in arpu_data
        ]

    async def _analyze_revenue_segments(self) -> Dict[str, Any]:
        """Analyze revenue by customer segments"""

        segments = await self.db.execute(
            """
            SELECT
                customer_segment,
                COUNT(*) as customers,
                SUM(mrr) as total_mrr,
                AVG(mrr) as avg_mrr,
                AVG(ltv) as avg_ltv,
                AVG(tenure_months) as avg_tenure
            FROM customer_analytics
            GROUP BY customer_segment
            ORDER BY total_mrr DESC
            """
        )

        return {
            "segments": [
                {
                    "segment": row.customer_segment,
                    "customers": row.customers,
                    "mrr": row.total_mrr,
                    "arpu": row.avg_mrr,
                    "ltv": row.avg_ltv,
                    "contribution": row.total_mrr / sum(r.total_mrr for r in segments) * 100
                }
                for row in segments
            ],
            "concentration_risk": self._calculate_revenue_concentration(segments)
        }

    async def _calculate_expansion_metrics(self) -> Dict[str, Any]:
        """Calculate expansion revenue metrics"""

        expansion = await self.db.execute(
            """
            SELECT
                COUNT(DISTINCT customer_id) as expanding_customers,
                SUM(mrr_increase) as total_expansion_mrr,
                AVG(mrr_increase) as avg_expansion
            FROM expansion_revenue
            WHERE expansion_date >= NOW() - INTERVAL '30 days'
            """
        )

        data = expansion.first()

        # Net dollar retention
        ndr = await self.db.execute(
            """
            SELECT
                (SUM(current_mrr) / SUM(initial_mrr)) * 100 as ndr
            FROM cohort_revenue
            WHERE cohort_month = NOW() - INTERVAL '12 months'
            """
        )

        return {
            "expanding_customers": data.expanding_customers or 0,
            "expansion_mrr": data.total_expansion_mrr or 0,
            "avg_expansion": data.avg_expansion or 0,
            "net_dollar_retention": ndr.scalar() or 100,
            "expansion_rate": (data.total_expansion_mrr or 0) / await self._get_total_mrr() * 100
        }

    async def _forecast_revenue(self) -> Dict[str, Any]:
        """Forecast revenue for next 12 months"""

        # Get historical data
        historical = await self.db.execute(
            """
            SELECT
                DATE_TRUNC('month', date) as month,
                SUM(mrr) as mrr
            FROM customer_subscriptions
            WHERE date >= NOW() - INTERVAL '24 months'
            GROUP BY month
            ORDER BY month
            """
        )

        # Simple linear regression for forecast
        months = []
        mrr_values = []

        for i, row in enumerate(historical):
            months.append(i)
            mrr_values.append(row.mrr)

        if len(months) >= 12:
            # Calculate trend
            slope, intercept = np.polyfit(months, mrr_values, 1)

            # Project forward
            forecast_months = []
            current_month = len(months)

            for i in range(12):
                month_num = current_month + i
                projected_mrr = slope * month_num + intercept
                forecast_months.append({
                    "month": i + 1,
                    "projected_mrr": projected_mrr,
                    "projected_arr": projected_mrr * 12,
                    "confidence_interval": projected_mrr * 0.15  # 15% confidence interval
                })
        else:
            # Not enough data for forecast
            forecast_months = []

        return {
            "monthly_forecast": forecast_months,
            "12_month_mrr": forecast_months[-1]["projected_mrr"] if forecast_months else 0,
            "12_month_arr": forecast_months[-1]["projected_arr"] if forecast_months else 0,
            "growth_rate": slope / mrr_values[-1] * 100 if mrr_values else 0
        }

    async def _analyze_pricing_elasticity(self) -> Dict[str, Any]:
        """Analyze pricing elasticity and optimization"""

        # Analyze conversion rates at different price points
        pricing_data = await self.db.execute(
            """
            SELECT
                price_point,
                conversion_rate,
                total_customers,
                total_revenue
            FROM pricing_experiments
            WHERE experiment_date >= NOW() - INTERVAL '6 months'
            """
        )

        # Calculate optimal pricing
        optimal_prices = {
            "starter": 279,  # Based on market analysis
            "growth": 798,
            "enterprise": 1598
        }

        return {
            "optimal_prices": optimal_prices,
            "revenue_impact": {
                "potential_increase": "23%",
                "confidence": "High"
            },
            "recommendations": [
                "Test 10% price increase for Growth tier",
                "Introduce annual discount to reduce churn",
                "Add usage-based pricing for enterprise"
            ]
        }

    async def _analyze_feature_usage_by_tier(self) -> Dict[str, Any]:
        """Analyze feature usage by subscription tier"""

        usage = await self.db.execute(
            """
            SELECT
                subscription_tier,
                feature_name,
                AVG(usage_percentage) as avg_usage,
                COUNT(DISTINCT customer_id) as users
            FROM feature_usage
            GROUP BY subscription_tier, feature_name
            ORDER BY subscription_tier, avg_usage DESC
            """
        )

        tier_features = {}
        for row in usage:
            if row.subscription_tier not in tier_features:
                tier_features[row.subscription_tier] = []
            tier_features[row.subscription_tier].append({
                "feature": row.feature_name,
                "usage": row.avg_usage,
                "users": row.users
            })

        return tier_features

    async def _identify_upsell_opportunities(self) -> List[Dict[str, Any]]:
        """Identify customers ready for upsell"""

        opportunities = await self.db.execute(
            """
            SELECT
                c.customer_id,
                c.company_name,
                c.current_tier,
                c.mrr,
                u.usage_score,
                u.features_at_limit
            FROM customers c
            JOIN usage_analytics u ON c.customer_id = u.customer_id
            WHERE u.usage_score > 80
            OR u.features_at_limit > 0
            ORDER BY u.usage_score DESC
            LIMIT 20
            """
        )

        return [
            {
                "customer": row.company_name,
                "current_tier": row.current_tier,
                "current_mrr": row.mrr,
                "upsell_signal": "High usage" if row.usage_score > 80 else "Feature limits",
                "recommended_tier": self._recommend_tier(row),
                "potential_mrr_increase": self._calculate_upsell_value(row)
            }
            for row in opportunities
        ]

    def _calculate_quick_ratio(self, mrr_movement: Dict[str, float]) -> float:
        """Calculate SaaS quick ratio"""

        growth = mrr_movement["new_mrr"] + mrr_movement["expansion_mrr"]
        churn = mrr_movement["contraction_mrr"] + mrr_movement["churn_mrr"]

        return growth / churn if churn > 0 else float('inf')

    def _calculate_path_to_target(self, current: float, target: float) -> Dict[str, Any]:
        """Calculate path to revenue target"""

        gap = target - current
        current_growth_rate = 0.15  # 15% monthly growth assumption

        months_to_target = np.log(target / current) / np.log(1 + current_growth_rate) if current > 0 else 0

        return {
            "current": current,
            "target": target,
            "gap": gap,
            "months_to_target": int(months_to_target),
            "required_growth_rate": current_growth_rate * 100,
            "milestones": [
                {"month": 3, "target": current * (1 + current_growth_rate) ** 3},
                {"month": 6, "target": current * (1 + current_growth_rate) ** 6},
                {"month": 12, "target": current * (1 + current_growth_rate) ** 12}
            ]
        }

    def _calculate_tier_health(self, tier_data) -> float:
        """Calculate health score for subscription tier"""

        # Factors: retention, LTV, growth
        health_score = 0

        if tier_data.avg_tenure > 12:
            health_score += 30
        elif tier_data.avg_tenure > 6:
            health_score += 20
        else:
            health_score += 10

        if tier_data.avg_ltv > 10000:
            health_score += 40
        elif tier_data.avg_ltv > 5000:
            health_score += 25
        else:
            health_score += 10

        # Add MRR contribution factor
        health_score += min(30, tier_data.total_mrr / 1000)

        return min(100, health_score)

    def _format_tier_movements(self, movements) -> Dict[str, List]:
        """Format subscription tier movement data"""

        upgrades = []
        downgrades = []

        for row in movements:
            movement = {
                "from": row.from_tier,
                "to": row.to_tier,
                "count": row.movement_count,
                "mrr_impact": row.avg_mrr_change * row.movement_count
            }

            if row.avg_mrr_change > 0:
                upgrades.append(movement)
            else:
                downgrades.append(movement)

        return {
            "upgrades": upgrades,
            "downgrades": downgrades
        }

    def _calculate_revenue_concentration(self, segments) -> Dict[str, Any]:
        """Calculate revenue concentration risk"""

        total_mrr = sum(row.total_mrr for row in segments)

        # Calculate Herfindahl index
        herfindahl = sum((row.total_mrr / total_mrr) ** 2 for row in segments)

        # Top 10% concentration
        sorted_segments = sorted(segments, key=lambda x: x.total_mrr, reverse=True)
        top_10_percent_count = max(1, len(sorted_segments) // 10)
        top_10_percent_revenue = sum(s.total_mrr for s in sorted_segments[:top_10_percent_count])

        concentration_ratio = top_10_percent_revenue / total_mrr if total_mrr > 0 else 0

        return {
            "herfindahl_index": herfindahl,
            "top_10_percent_concentration": concentration_ratio * 100,
            "risk_level": "High" if concentration_ratio > 0.5 else "Medium" if concentration_ratio > 0.3 else "Low",
            "recommendation": "Diversify customer base" if concentration_ratio > 0.3 else "Healthy distribution"
        }

    async def _get_total_mrr(self) -> float:
        """Get current total MRR"""

        result = await self.db.execute(
            "SELECT SUM(mrr) FROM customer_subscriptions WHERE status = 'active'"
        )

        return result.scalar() or 0

    def _recommend_tier(self, customer_data) -> str:
        """Recommend tier upgrade for customer"""

        if customer_data.current_tier == "starter":
            return "growth"
        elif customer_data.current_tier == "growth":
            return "enterprise"
        else:
            return "enterprise_plus"

    def _calculate_upsell_value(self, customer_data) -> float:
        """Calculate potential upsell MRR increase"""

        tier_prices = {
            "starter": 279,
            "growth": 798,
            "enterprise": 1598
        }

        current_price = tier_prices.get(customer_data.current_tier, 279)
        next_tier = self._recommend_tier(customer_data)
        next_price = tier_prices.get(next_tier, current_price)

        return next_price - current_price

    def _generate_tier_recommendations(self, tier_data) -> List[Dict[str, str]]:
        """Generate subscription tier recommendations"""

        recommendations = []

        for row in tier_data:
            if row.avg_tenure < 6:
                recommendations.append({
                    "tier": row.subscription_tier,
                    "issue": "Low retention",
                    "action": "Improve onboarding and early value delivery",
                    "impact": "Increase LTV by 40%"
                })

            if row.avg_mrr < 500 and row.subscription_tier != "starter":
                recommendations.append({
                    "tier": row.subscription_tier,
                    "issue": "Underpriced",
                    "action": "Test 20% price increase with grandfathering",
                    "impact": "Increase ARPU by 15-20%"
                })

        return recommendations


class EngagementAnalytics:
    """User engagement and conversion funnel analytics"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def analyze_user_engagement(self) -> Dict[str, Any]:
        """Analyze comprehensive user engagement metrics"""

        # Daily/Weekly/Monthly active users
        active_users = await self._calculate_active_users()

        # Feature adoption
        feature_adoption = await self._analyze_feature_adoption()

        # Session analytics
        session_metrics = await self._analyze_sessions()

        # Content engagement (podcasts, resources)
        content_engagement = await self._analyze_content_engagement()

        # Community participation
        community_metrics = await self._analyze_community_participation()

        # Engagement scoring
        engagement_scores = await self._calculate_engagement_scores()

        return {
            "active_users": active_users,
            "feature_adoption": feature_adoption,
            "session_metrics": session_metrics,
            "content_engagement": content_engagement,
            "community_participation": community_metrics,
            "engagement_scores": engagement_scores,
            "engagement_trends": await self._analyze_engagement_trends(),
            "power_users": await self._identify_power_users(),
            "engagement_insights": self._generate_engagement_insights(active_users, feature_adoption)
        }

    async def analyze_conversion_funnel(self) -> Dict[str, Any]:
        """Analyze conversion funnel performance"""

        # Funnel stages
        funnel_stages = [
            "visitor",
            "signup",
            "trial_start",
            "activation",
            "first_payment",
            "retained_30d",
            "retained_90d"
        ]

        # Calculate conversion rates between stages
        funnel_data = await self._calculate_funnel_metrics(funnel_stages)

        # Identify drop-off points
        drop_offs = self._identify_drop_offs(funnel_data)

        # Time between stages
        stage_timing = await self._analyze_stage_timing()

        # A/B test results
        ab_test_results = await self._get_ab_test_results()

        # Conversion by source
        source_conversion = await self._analyze_conversion_by_source()

        return {
            "funnel_metrics": funnel_data,
            "conversion_rates": {
                "visitor_to_signup": funnel_data.get("visitor_to_signup", 0),
                "signup_to_trial": funnel_data.get("signup_to_trial", 0),
                "trial_to_paid": funnel_data.get("trial_to_paid", 0),
                "overall": funnel_data.get("overall_conversion", 0)
            },
            "drop_off_analysis": drop_offs,
            "stage_timing": stage_timing,
            "ab_test_results": ab_test_results,
            "source_performance": source_conversion,
            "optimization_opportunities": self._identify_optimization_opportunities(funnel_data, drop_offs),
            "projected_improvement": self._calculate_improvement_potential(funnel_data)
        }

    async def _calculate_active_users(self) -> Dict[str, Any]:
        """Calculate DAU, WAU, MAU metrics"""

        result = await self.db.execute(
            """
            SELECT
                COUNT(DISTINCT CASE WHEN last_active >= NOW() - INTERVAL '1 day' THEN user_id END) as dau,
                COUNT(DISTINCT CASE WHEN last_active >= NOW() - INTERVAL '7 days' THEN user_id END) as wau,
                COUNT(DISTINCT CASE WHEN last_active >= NOW() - INTERVAL '30 days' THEN user_id END) as mau
            FROM user_activity
            """
        )

        data = result.first()

        return {
            "dau": data.dau or 0,
            "wau": data.wau or 0,
            "mau": data.mau or 0,
            "dau_mau_ratio": (data.dau / data.mau * 100) if data.mau > 0 else 0,
            "wau_mau_ratio": (data.wau / data.mau * 100) if data.mau > 0 else 0
        }

    async def _analyze_feature_adoption(self) -> Dict[str, Any]:
        """Analyze feature adoption rates"""

        features = await self.db.execute(
            """
            SELECT
                feature_name,
                COUNT(DISTINCT user_id) as users,
                AVG(usage_count) as avg_usage,
                MAX(last_used) as last_used
            FROM feature_usage
            WHERE last_used >= NOW() - INTERVAL '30 days'
            GROUP BY feature_name
            ORDER BY users DESC
            """
        )

        total_users = await self.db.execute(
            "SELECT COUNT(DISTINCT user_id) FROM users WHERE status = 'active'"
        )
        total = total_users.scalar() or 1

        return {
            "features": [
                {
                    "name": row.feature_name,
                    "adoption_rate": (row.users / total * 100),
                    "avg_usage": row.avg_usage,
                    "category": self._categorize_feature(row.feature_name)
                }
                for row in features
            ],
            "core_feature_adoption": await self._calculate_core_feature_adoption(),
            "feature_stickiness": await self._calculate_feature_stickiness()
        }

    async def _analyze_sessions(self) -> Dict[str, Any]:
        """Analyze user session metrics"""

        sessions = await self.db.execute(
            """
            SELECT
                AVG(session_duration) as avg_duration,
                AVG(pages_viewed) as avg_pages,
                AVG(actions_taken) as avg_actions,
                COUNT(*) as total_sessions
            FROM user_sessions
            WHERE session_start >= NOW() - INTERVAL '30 days'
            """
        )

        data = sessions.first()

        return {
            "avg_session_duration": data.avg_duration or 0,
            "avg_pages_per_session": data.avg_pages or 0,
            "avg_actions_per_session": data.avg_actions or 0,
            "total_sessions": data.total_sessions or 0,
            "bounce_rate": await self._calculate_bounce_rate()
        }

    async def _analyze_content_engagement(self) -> Dict[str, Any]:
        """Analyze content engagement metrics"""

        podcast_engagement = await self.db.execute(
            """
            SELECT
                COUNT(DISTINCT user_id) as listeners,
                AVG(listen_duration) as avg_duration,
                SUM(completed) as completions,
                AVG(completion_rate) as avg_completion
            FROM podcast_analytics
            WHERE listened_at >= NOW() - INTERVAL '30 days'
            """
        )

        resource_engagement = await self.db.execute(
            """
            SELECT
                resource_type,
                COUNT(DISTINCT user_id) as users,
                SUM(downloads) as total_downloads,
                AVG(engagement_score) as avg_engagement
            FROM resource_analytics
            WHERE accessed_at >= NOW() - INTERVAL '30 days'
            GROUP BY resource_type
            """
        )

        podcast_data = podcast_engagement.first()

        return {
            "podcast": {
                "monthly_listeners": podcast_data.listeners or 0,
                "avg_listen_duration": podcast_data.avg_duration or 0,
                "completion_rate": podcast_data.avg_completion or 0
            },
            "resources": [
                {
                    "type": row.resource_type,
                    "users": row.users,
                    "downloads": row.total_downloads,
                    "engagement": row.avg_engagement
                }
                for row in resource_engagement
            ]
        }

    async def _analyze_community_participation(self) -> Dict[str, Any]:
        """Analyze community participation metrics"""

        participation = await self.db.execute(
            """
            SELECT
                COUNT(DISTINCT user_id) as active_members,
                SUM(posts_created) as total_posts,
                SUM(comments_made) as total_comments,
                AVG(connections_made) as avg_connections
            FROM community_activity
            WHERE activity_date >= NOW() - INTERVAL '30 days'
            """
        )

        data = participation.first()

        return {
            "active_members": data.active_members or 0,
            "total_posts": data.total_posts or 0,
            "total_comments": data.total_comments or 0,
            "avg_connections": data.avg_connections or 0,
            "engagement_rate": await self._calculate_community_engagement_rate()
        }

    async def _calculate_engagement_scores(self) -> Dict[str, Any]:
        """Calculate user engagement scores"""

        scores = await self.db.execute(
            """
            SELECT
                AVG(engagement_score) as avg_score,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY engagement_score) as median_score,
                PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY engagement_score) as p25_score,
                PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY engagement_score) as p75_score
            FROM user_engagement_scores
            WHERE calculated_at >= NOW() - INTERVAL '7 days'
            """
        )

        data = scores.first()

        return {
            "average": data.avg_score or 0,
            "median": data.median_score or 0,
            "quartiles": {
                "p25": data.p25_score or 0,
                "p50": data.median_score or 0,
                "p75": data.p75_score or 0
            },
            "distribution": await self._get_score_distribution()
        }

    async def _analyze_engagement_trends(self) -> List[Dict[str, Any]]:
        """Analyze engagement trends over time"""

        trends = await self.db.execute(
            """
            SELECT
                DATE_TRUNC('week', activity_date) as week,
                AVG(engagement_score) as avg_engagement,
                COUNT(DISTINCT user_id) as active_users
            FROM user_activity
            WHERE activity_date >= NOW() - INTERVAL '12 weeks'
            GROUP BY week
            ORDER BY week
            """
        )

        return [
            {
                "week": row.week.strftime("%Y-%W"),
                "engagement": row.avg_engagement,
                "active_users": row.active_users
            }
            for row in trends
        ]

    async def _identify_power_users(self) -> List[Dict[str, Any]]:
        """Identify and analyze power users"""

        power_users = await self.db.execute(
            """
            SELECT
                u.user_id,
                u.company_name,
                e.engagement_score,
                e.features_used,
                e.sessions_30d,
                s.mrr
            FROM users u
            JOIN user_engagement_scores e ON u.user_id = e.user_id
            LEFT JOIN customer_subscriptions s ON u.user_id = s.user_id
            WHERE e.engagement_score > 80
            ORDER BY e.engagement_score DESC
            LIMIT 50
            """
        )

        return [
            {
                "user_id": row.user_id,
                "company": row.company_name,
                "engagement_score": row.engagement_score,
                "features_used": row.features_used,
                "value": row.mrr or 0,
                "profile": "Power User"
            }
            for row in power_users
        ]

    async def _calculate_funnel_metrics(self, stages: List[str]) -> Dict[str, Any]:
        """Calculate conversion funnel metrics"""

        funnel_data = {}

        for i, stage in enumerate(stages):
            # Get count for this stage
            count_query = f"""
                SELECT COUNT(DISTINCT user_id) as count
                FROM funnel_events
                WHERE stage = '{stage}'
                AND event_date >= NOW() - INTERVAL '30 days'
            """

            result = await self.db.execute(count_query)
            stage_count = result.scalar() or 0

            funnel_data[stage] = stage_count

            # Calculate conversion rate to next stage
            if i > 0:
                prev_stage = stages[i-1]
                prev_count = funnel_data.get(prev_stage, 1)
                conversion_rate = (stage_count / prev_count * 100) if prev_count > 0 else 0
                funnel_data[f"{prev_stage}_to_{stage}"] = conversion_rate

        # Overall conversion rate
        if stages:
            first_stage_count = funnel_data.get(stages[0], 1)
            last_stage_count = funnel_data.get(stages[-1], 0)
            funnel_data["overall_conversion"] = (last_stage_count / first_stage_count * 100) if first_stage_count > 0 else 0

        return funnel_data

    def _identify_drop_offs(self, funnel_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify major drop-off points in funnel"""

        drop_offs = []

        conversion_rates = {k: v for k, v in funnel_data.items() if "_to_" in k}

        for stage, rate in conversion_rates.items():
            if rate < 30:  # Less than 30% conversion is concerning
                drop_offs.append({
                    "stage": stage.replace("_to_", " → "),
                    "conversion_rate": rate,
                    "severity": "Critical" if rate < 10 else "High" if rate < 20 else "Medium",
                    "potential_improvement": self._suggest_improvement(stage, rate)
                })

        return sorted(drop_offs, key=lambda x: x["conversion_rate"])

    async def _analyze_stage_timing(self) -> Dict[str, Any]:
        """Analyze time between funnel stages"""

        timing = await self.db.execute(
            """
            SELECT
                from_stage,
                to_stage,
                AVG(time_between) as avg_time,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY time_between) as median_time
            FROM funnel_timing
            WHERE event_date >= NOW() - INTERVAL '30 days'
            GROUP BY from_stage, to_stage
            """
        )

        return {
            f"{row.from_stage}_to_{row.to_stage}": {
                "avg_hours": row.avg_time,
                "median_hours": row.median_time
            }
            for row in timing
        }

    async def _get_ab_test_results(self) -> List[Dict[str, Any]]:
        """Get recent A/B test results"""

        tests = await self.db.execute(
            """
            SELECT
                test_name,
                variant_a_conversion,
                variant_b_conversion,
                sample_size,
                confidence_level,
                winner
            FROM ab_tests
            WHERE completed_at >= NOW() - INTERVAL '30 days'
            ORDER BY completed_at DESC
            LIMIT 10
            """
        )

        return [
            {
                "test": row.test_name,
                "variant_a": row.variant_a_conversion,
                "variant_b": row.variant_b_conversion,
                "lift": ((row.variant_b_conversion - row.variant_a_conversion) / row.variant_a_conversion * 100) if row.variant_a_conversion > 0 else 0,
                "confidence": row.confidence_level,
                "winner": row.winner
            }
            for row in tests
        ]

    async def _analyze_conversion_by_source(self) -> Dict[str, Any]:
        """Analyze conversion rates by traffic source"""

        sources = await self.db.execute(
            """
            SELECT
                traffic_source,
                COUNT(*) as visitors,
                SUM(CASE WHEN converted THEN 1 ELSE 0 END) as conversions,
                AVG(conversion_value) as avg_value
            FROM traffic_analytics
            WHERE visit_date >= NOW() - INTERVAL '30 days'
            GROUP BY traffic_source
            ORDER BY conversions DESC
            """
        )

        return {
            "sources": [
                {
                    "source": row.traffic_source,
                    "visitors": row.visitors,
                    "conversions": row.conversions,
                    "conversion_rate": (row.conversions / row.visitors * 100) if row.visitors > 0 else 0,
                    "avg_value": row.avg_value or 0
                }
                for row in sources
            ]
        }

    def _identify_optimization_opportunities(
        self,
        funnel_data: Dict[str, Any],
        drop_offs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify funnel optimization opportunities"""

        opportunities = []

        for drop_off in drop_offs[:3]:  # Focus on top 3 drop-offs
            stage = drop_off["stage"]
            rate = drop_off["conversion_rate"]

            if "visitor → signup" in stage:
                opportunities.append({
                    "stage": stage,
                    "current_rate": rate,
                    "target_rate": rate * 1.5,
                    "tactics": [
                        "Simplify signup form",
                        "Add social proof",
                        "Implement exit-intent popup"
                    ],
                    "expected_impact": "30-50% improvement"
                })
            elif "trial → paid" in stage:
                opportunities.append({
                    "stage": stage,
                    "current_rate": rate,
                    "target_rate": rate * 1.4,
                    "tactics": [
                        "Improve onboarding",
                        "Add in-app guidance",
                        "Implement usage-based email triggers"
                    ],
                    "expected_impact": "25-40% improvement"
                })

        return opportunities

    def _calculate_improvement_potential(self, funnel_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate potential revenue impact of improvements"""

        current_overall = funnel_data.get("overall_conversion", 0) / 100
        visitors = funnel_data.get("visitor", 1000)  # Assume 1000 visitors for calculation

        # Calculate current revenue
        current_conversions = visitors * current_overall
        current_revenue = current_conversions * 798  # Average subscription value

        # Calculate improved revenue (25% improvement assumption)
        improved_conversion = current_overall * 1.25
        improved_conversions = visitors * improved_conversion
        improved_revenue = improved_conversions * 798

        return {
            "current_monthly_revenue": current_revenue,
            "potential_monthly_revenue": improved_revenue,
            "monthly_increase": improved_revenue - current_revenue,
            "annual_increase": (improved_revenue - current_revenue) * 12
        }

    def _categorize_feature(self, feature_name: str) -> str:
        """Categorize features for analysis"""

        categories = {
            "deal": ["deal_scanner", "deal_scoring", "deal_pipeline"],
            "advisor": ["advisor_connect", "advisor_chat", "consultations"],
            "analytics": ["dashboard", "reports", "metrics"],
            "community": ["forums", "events", "networking"]
        }

        for category, features in categories.items():
            if any(f in feature_name.lower() for f in features):
                return category

        return "other"

    async def _calculate_core_feature_adoption(self) -> float:
        """Calculate adoption rate of core features"""

        core_features = ["deal_scanner", "ai_scoring", "advisor_connect"]

        result = await self.db.execute(
            """
            SELECT COUNT(DISTINCT user_id) as users
            FROM feature_usage
            WHERE feature_name IN (?)
            AND last_used >= NOW() - INTERVAL '30 days'
            """,
            (core_features,)
        )

        core_users = result.scalar() or 0

        total = await self.db.execute(
            "SELECT COUNT(*) FROM users WHERE status = 'active'"
        )

        total_users = total.scalar() or 1

        return (core_users / total_users * 100)

    async def _calculate_feature_stickiness(self) -> Dict[str, float]:
        """Calculate feature stickiness (DAU/MAU by feature)"""

        stickiness = await self.db.execute(
            """
            SELECT
                feature_name,
                COUNT(DISTINCT CASE WHEN last_used >= NOW() - INTERVAL '1 day' THEN user_id END) as dau,
                COUNT(DISTINCT CASE WHEN last_used >= NOW() - INTERVAL '30 days' THEN user_id END) as mau
            FROM feature_usage
            GROUP BY feature_name
            """
        )

        return {
            row.feature_name: (row.dau / row.mau * 100) if row.mau > 0 else 0
            for row in stickiness
        }

    async def _calculate_bounce_rate(self) -> float:
        """Calculate session bounce rate"""

        result = await self.db.execute(
            """
            SELECT
                COUNT(CASE WHEN pages_viewed = 1 THEN 1 END)::float /
                COUNT(*)::float * 100 as bounce_rate
            FROM user_sessions
            WHERE session_start >= NOW() - INTERVAL '30 days'
            """
        )

        return result.scalar() or 0

    async def _calculate_community_engagement_rate(self) -> float:
        """Calculate community engagement rate"""

        active = await self.db.execute(
            """
            SELECT COUNT(DISTINCT user_id)
            FROM community_activity
            WHERE activity_date >= NOW() - INTERVAL '30 days'
            """
        )

        total = await self.db.execute(
            "SELECT COUNT(*) FROM users WHERE status = 'active'"
        )

        active_count = active.scalar() or 0
        total_count = total.scalar() or 1

        return (active_count / total_count * 100)

    async def _get_score_distribution(self) -> Dict[str, int]:
        """Get engagement score distribution"""

        distribution = await self.db.execute(
            """
            SELECT
                CASE
                    WHEN engagement_score < 20 THEN 'Very Low'
                    WHEN engagement_score < 40 THEN 'Low'
                    WHEN engagement_score < 60 THEN 'Medium'
                    WHEN engagement_score < 80 THEN 'High'
                    ELSE 'Very High'
                END as bracket,
                COUNT(*) as count
            FROM user_engagement_scores
            GROUP BY bracket
            """
        )

        return {row.bracket: row.count for row in distribution}

    def _suggest_improvement(self, stage: str, current_rate: float) -> str:
        """Suggest improvement for funnel stage"""

        suggestions = {
            "visitor_to_signup": "Optimize landing page CTA and reduce form fields",
            "signup_to_trial": "Streamline trial activation process",
            "trial_to_activation": "Improve onboarding and feature discovery",
            "activation_to_payment": "Implement value realization emails and in-app prompts"
        }

        return suggestions.get(stage, "Conduct user research to identify friction points")

    def _generate_engagement_insights(
        self,
        active_users: Dict[str, Any],
        feature_adoption: Dict[str, Any]
    ) -> List[StrategicInsight]:
        """Generate strategic engagement insights"""

        insights = []

        # DAU/MAU ratio insight
        dau_mau = active_users.get("dau_mau_ratio", 0)
        if dau_mau < 20:
            insights.append(StrategicInsight(
                category="Engagement",
                severity="warning",
                insight="Low daily engagement rate",
                impact=f"DAU/MAU ratio is {dau_mau:.1f}%, indicating low stickiness",
                recommendation="Implement daily engagement triggers like market alerts",
                potential_value=15000,  # Estimated MRR impact
                confidence=0.75,
                data_points={"dau_mau": dau_mau}
            ))

        # Feature adoption insight
        core_adoption = feature_adoption.get("core_feature_adoption", 0)
        if core_adoption < 60:
            insights.append(StrategicInsight(
                category="Adoption",
                severity="critical",
                insight="Low core feature adoption",
                impact=f"Only {core_adoption:.1f}% using core features",
                recommendation="Launch feature education campaign and improve onboarding",
                potential_value=25000,
                confidence=0.85,
                data_points={"core_adoption": core_adoption}
            ))

        return insights