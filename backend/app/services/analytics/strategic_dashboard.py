"""
Strategic Dashboard and Wealth-Building Intelligence System
Executive dashboard for £200M wealth-building optimization
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from .strategic_analytics import (
    CustomerAnalytics,
    RevenueAnalytics,
    EngagementAnalytics,
    StrategicInsight
)
from .partnership_analytics import (
    PartnershipAnalytics,
    EcosystemIntelligence,
    PartnershipOpportunity
)

logger = structlog.get_logger()


class DashboardView(Enum):
    """Dashboard view types"""
    EXECUTIVE = "executive"
    REVENUE = "revenue"
    GROWTH = "growth"
    PARTNERSHIPS = "partnerships"
    CUSTOMER = "customer"
    COMPETITIVE = "competitive"
    WEALTH_BUILDING = "wealth_building"


@dataclass
class WealthBuildingProgress:
    """Progress toward £200M wealth objective"""
    current_valuation: float
    target_valuation: float
    progress_percentage: float
    months_elapsed: int
    months_remaining: int
    required_growth_rate: float
    current_growth_rate: float
    key_milestones: List[Dict[str, Any]]
    critical_path: List[str]
    risk_factors: List[Dict[str, Any]]
    acceleration_opportunities: List[Dict[str, Any]]


@dataclass
class ExecutiveSummary:
    """Executive dashboard summary"""
    period: str
    mrr: float
    mrr_growth: float
    customer_count: int
    churn_rate: float
    ltv_cac_ratio: float
    runway_months: float
    valuation_estimate: float
    key_metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]


class StrategicDashboard:
    """Main strategic dashboard orchestrator"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.customer_analytics = CustomerAnalytics(db_session)
        self.revenue_analytics = RevenueAnalytics(db_session)
        self.engagement_analytics = EngagementAnalytics(db_session)
        self.partnership_analytics = PartnershipAnalytics(db_session)
        self.ecosystem_intelligence = EcosystemIntelligence(db_session)

    async def get_executive_dashboard(self) -> ExecutiveSummary:
        """Get executive dashboard with key metrics"""

        # Get core metrics in parallel
        tasks = [
            self.revenue_analytics.calculate_revenue_metrics(),
            self.customer_analytics.calculate_retention_metrics(),
            self.engagement_analytics.analyze_user_engagement(),
            self._calculate_runway(),
            self._estimate_valuation()
        ]

        results = await asyncio.gather(*tasks)

        revenue_metrics = results[0]
        retention_metrics = results[1]
        engagement_metrics = results[2]
        runway = results[3]
        valuation = results[4]

        # Generate alerts
        alerts = await self._generate_executive_alerts(
            revenue_metrics,
            retention_metrics,
            engagement_metrics
        )

        # Identify opportunities
        opportunities = await self._identify_top_opportunities()

        return ExecutiveSummary(
            period="Last 30 days",
            mrr=revenue_metrics["mrr"],
            mrr_growth=revenue_metrics["mrr_growth_rate"],
            customer_count=revenue_metrics["customer_count"],
            churn_rate=retention_metrics["monthly_churn_rate"],
            ltv_cac_ratio=await self._calculate_ltv_cac_ratio(),
            runway_months=runway,
            valuation_estimate=valuation,
            key_metrics={
                "arr": revenue_metrics["arr"],
                "arpu": revenue_metrics["arpu"],
                "nps": await self._get_nps_score(),
                "dau_mau": engagement_metrics["active_users"]["dau_mau_ratio"],
                "quick_ratio": revenue_metrics["quick_ratio"]
            },
            alerts=alerts,
            opportunities=opportunities
        )

    async def get_wealth_building_dashboard(self) -> WealthBuildingProgress:
        """Get wealth-building progress dashboard"""

        # Current valuation
        current_valuation = await self._estimate_valuation()

        # Target
        target_valuation = 200_000_000  # £200M

        # Progress calculation
        progress = (current_valuation / target_valuation) * 100

        # Timeline analysis
        start_date = datetime(2024, 1, 1)
        months_elapsed = (datetime.utcnow() - start_date).days / 30
        target_months = 120  # 10 years
        months_remaining = target_months - months_elapsed

        # Growth rate analysis
        current_growth = await self._calculate_valuation_growth_rate()
        required_growth = self._calculate_required_growth_rate(
            current_valuation,
            target_valuation,
            months_remaining
        )

        # Milestones
        milestones = self._generate_wealth_milestones(
            current_valuation,
            target_valuation
        )

        # Critical path
        critical_path = await self._identify_critical_path()

        # Risk factors
        risk_factors = await self._identify_wealth_risks()

        # Acceleration opportunities
        opportunities = await self._identify_acceleration_opportunities()

        return WealthBuildingProgress(
            current_valuation=current_valuation,
            target_valuation=target_valuation,
            progress_percentage=progress,
            months_elapsed=int(months_elapsed),
            months_remaining=int(months_remaining),
            required_growth_rate=required_growth,
            current_growth_rate=current_growth,
            key_milestones=milestones,
            critical_path=critical_path,
            risk_factors=risk_factors,
            acceleration_opportunities=opportunities
        )

    async def get_strategic_insights(self) -> List[StrategicInsight]:
        """Get prioritized strategic insights"""

        insights = []

        # Revenue insights
        revenue_insights = await self._generate_revenue_insights()
        insights.extend(revenue_insights)

        # Customer insights
        customer_insights = await self._generate_customer_insights()
        insights.extend(customer_insights)

        # Partnership insights
        partnership_insights = await self.ecosystem_intelligence.generate_strategic_insights()
        insights.extend(partnership_insights)

        # Growth insights
        growth_insights = await self._generate_growth_insights()
        insights.extend(growth_insights)

        # Sort by potential value and confidence
        insights.sort(key=lambda x: x.potential_value * x.confidence, reverse=True)

        return insights[:20]  # Top 20 insights

    async def get_dashboard_view(self, view_type: DashboardView) -> Dict[str, Any]:
        """Get specific dashboard view"""

        if view_type == DashboardView.EXECUTIVE:
            return await self._get_executive_view()
        elif view_type == DashboardView.REVENUE:
            return await self._get_revenue_view()
        elif view_type == DashboardView.GROWTH:
            return await self._get_growth_view()
        elif view_type == DashboardView.PARTNERSHIPS:
            return await self._get_partnerships_view()
        elif view_type == DashboardView.CUSTOMER:
            return await self._get_customer_view()
        elif view_type == DashboardView.COMPETITIVE:
            return await self._get_competitive_view()
        elif view_type == DashboardView.WEALTH_BUILDING:
            return await self._get_wealth_building_view()
        else:
            return {}

    async def _get_executive_view(self) -> Dict[str, Any]:
        """Get executive dashboard view"""

        summary = await self.get_executive_dashboard()

        return {
            "summary": {
                "mrr": f"£{summary.mrr:,.0f}",
                "growth": f"{summary.mrr_growth:.1f}%",
                "customers": summary.customer_count,
                "churn": f"{summary.churn_rate:.1f}%",
                "ltv_cac": f"{summary.ltv_cac_ratio:.1f}x",
                "runway": f"{summary.runway_months:.0f} months",
                "valuation": f"£{summary.valuation_estimate:,.0f}"
            },
            "charts": {
                "mrr_trend": await self._get_mrr_trend_chart(),
                "customer_growth": await self._get_customer_growth_chart(),
                "churn_cohorts": await self._get_churn_cohort_chart(),
                "revenue_segments": await self._get_revenue_segment_chart()
            },
            "alerts": summary.alerts,
            "opportunities": summary.opportunities,
            "key_metrics": summary.key_metrics
        }

    async def _get_revenue_view(self) -> Dict[str, Any]:
        """Get revenue dashboard view"""

        revenue_metrics = await self.revenue_analytics.calculate_revenue_metrics()
        subscription_performance = await self.revenue_analytics.analyze_subscription_performance()

        return {
            "current_metrics": {
                "mrr": revenue_metrics["mrr"],
                "arr": revenue_metrics["arr"],
                "arpu": revenue_metrics["arpu"],
                "quick_ratio": revenue_metrics["quick_ratio"]
            },
            "mrr_movement": revenue_metrics["mrr_movement"],
            "subscription_tiers": subscription_performance["tier_performance"],
            "expansion_metrics": revenue_metrics["expansion_metrics"],
            "forecast": revenue_metrics["forecast"],
            "charts": {
                "mrr_waterfall": await self._get_mrr_waterfall_chart(),
                "arpu_trend": revenue_metrics["arpu_trend"],
                "revenue_forecast": await self._get_revenue_forecast_chart(),
                "tier_distribution": await self._get_tier_distribution_chart()
            },
            "upsell_opportunities": subscription_performance["upsell_opportunities"],
            "pricing_optimization": subscription_performance["pricing_optimization"]
        }

    async def _get_growth_view(self) -> Dict[str, Any]:
        """Get growth dashboard view"""

        acquisition = await self.customer_analytics.calculate_acquisition_metrics(
            datetime.utcnow() - timedelta(days=30),
            datetime.utcnow()
        )

        engagement = await self.engagement_analytics.analyze_user_engagement()
        funnel = await self.engagement_analytics.analyze_conversion_funnel()

        return {
            "acquisition": {
                "new_customers": acquisition["total_new_customers"],
                "cac": acquisition["customer_acquisition_cost"],
                "ltv_cac": acquisition["ltv_cac_ratio"],
                "velocity": acquisition["acquisition_velocity"]
            },
            "engagement": {
                "dau": engagement["active_users"]["dau"],
                "mau": engagement["active_users"]["mau"],
                "stickiness": engagement["active_users"]["dau_mau_ratio"],
                "power_users": len(engagement["power_users"])
            },
            "conversion_funnel": funnel["funnel_metrics"],
            "channel_performance": acquisition["channel_performance"],
            "charts": {
                "growth_accounting": await self._get_growth_accounting_chart(),
                "cohort_retention": await self._get_cohort_retention_chart(),
                "funnel_visualization": await self._get_funnel_visualization(),
                "channel_roi": await self._get_channel_roi_chart()
            },
            "optimization_opportunities": funnel["optimization_opportunities"],
            "growth_experiments": await self._get_active_experiments()
        }

    async def _get_partnerships_view(self) -> Dict[str, Any]:
        """Get partnerships dashboard view"""

        ecosystem = await self.partnership_analytics.analyze_partnership_ecosystem()
        opportunities = await self.partnership_analytics.identify_strategic_partners({
            "industries": ["technology", "finance", "consulting"],
            "target_segments": ["enterprise", "mid-market"]
        })

        return {
            "ecosystem_metrics": ecosystem["ecosystem_map"],
            "active_partnerships": ecosystem["partnership_performance"],
            "opportunities": [
                {
                    "company": opp.company_name,
                    "type": opp.partnership_type.value,
                    "score": opp.opportunity_score,
                    "value": opp.potential_value,
                    "next_steps": opp.next_steps
                }
                for opp in opportunities[:10]
            ],
            "partnership_roi": ecosystem["partnership_roi"],
            "relationship_health": ecosystem["relationship_health"],
            "charts": {
                "partner_network": await self._get_partner_network_visualization(),
                "partnership_value": await self._get_partnership_value_chart(),
                "partner_performance": await self._get_partner_performance_chart()
            },
            "strategic_recommendations": ecosystem["strategic_recommendations"]
        }

    async def _get_customer_view(self) -> Dict[str, Any]:
        """Get customer dashboard view"""

        retention = await self.customer_analytics.calculate_retention_metrics()
        engagement = await self.engagement_analytics.analyze_user_engagement()

        return {
            "retention_metrics": {
                "monthly_churn": retention["monthly_churn_rate"],
                "annual_churn": retention["annual_churn_rate"],
                "net_retention": retention["net_revenue_retention"],
                "avg_tenure": retention["average_customer_tenure_months"]
            },
            "at_risk_customers": retention["at_risk_customers"],
            "churn_reasons": retention["churn_reasons"],
            "engagement_scores": engagement["engagement_scores"],
            "feature_adoption": engagement["feature_adoption"],
            "charts": {
                "retention_curve": retention["retention_curve"],
                "churn_prediction": await self._get_churn_prediction_chart(),
                "engagement_distribution": await self._get_engagement_distribution_chart(),
                "customer_journey": await self._get_customer_journey_map()
            },
            "retention_improvements": retention["retention_improvements"],
            "customer_success_actions": await self._get_customer_success_actions()
        }

    async def _get_competitive_view(self) -> Dict[str, Any]:
        """Get competitive intelligence view"""

        position = await self.ecosystem_intelligence.analyze_market_position()
        landscape = await self.ecosystem_intelligence.analyze_competitive_landscape()

        return {
            "market_position": {
                "market_share": position.market_share,
                "influence_score": position.influence_score,
                "centrality": position.centrality_score,
                "growth_trajectory": position.growth_trajectory
            },
            "competitive_advantages": position.competitive_advantages,
            "market_gaps": position.market_gaps,
            "competitors": landscape["competitors"],
            "market_trends": landscape["market_trends"],
            "threats": landscape["threats"],
            "opportunities": landscape["opportunities"],
            "charts": {
                "market_share": await self._get_market_share_chart(),
                "competitive_matrix": await self._get_competitive_matrix(),
                "trend_analysis": await self._get_trend_analysis_chart()
            },
            "strategic_positioning": landscape["strategic_positioning"],
            "differentiation_strategy": landscape["differentiation_strategy"]
        }

    async def _get_wealth_building_view(self) -> Dict[str, Any]:
        """Get wealth-building dashboard view"""

        progress = await self.get_wealth_building_dashboard()

        return {
            "progress": {
                "current_valuation": f"£{progress.current_valuation:,.0f}",
                "target": f"£{progress.target_valuation:,.0f}",
                "percentage": f"{progress.progress_percentage:.1f}%",
                "timeline": f"{progress.months_remaining} months remaining"
            },
            "growth_analysis": {
                "current_rate": f"{progress.current_growth_rate:.1f}%",
                "required_rate": f"{progress.required_growth_rate:.1f}%",
                "gap": f"{progress.required_growth_rate - progress.current_growth_rate:.1f}%"
            },
            "milestones": progress.key_milestones,
            "critical_path": progress.critical_path,
            "risk_factors": progress.risk_factors,
            "acceleration_opportunities": progress.acceleration_opportunities,
            "charts": {
                "valuation_trajectory": await self._get_valuation_trajectory_chart(),
                "milestone_progress": await self._get_milestone_progress_chart(),
                "scenario_analysis": await self._get_scenario_analysis_chart()
            },
            "strategic_initiatives": await self._get_strategic_initiatives(),
            "investment_requirements": await self._calculate_investment_requirements()
        }

    async def _calculate_runway(self) -> float:
        """Calculate months of runway"""

        cash = await self.db.execute(
            "SELECT balance FROM cash_balance ORDER BY date DESC LIMIT 1"
        )

        burn_rate = await self.db.execute(
            """
            SELECT AVG(monthly_burn) as avg_burn
            FROM (
                SELECT SUM(expenses) - SUM(revenue) as monthly_burn
                FROM financial_data
                WHERE date >= NOW() - INTERVAL '6 months'
                GROUP BY DATE_TRUNC('month', date)
            ) as monthly_burns
            """
        )

        cash_balance = cash.scalar() or 1000000  # Default £1M
        monthly_burn = burn_rate.scalar() or 50000  # Default £50K

        return cash_balance / monthly_burn if monthly_burn > 0 else 999

    async def _estimate_valuation(self) -> float:
        """Estimate company valuation"""

        # Revenue multiple method
        arr = await self.db.execute(
            "SELECT SUM(mrr) * 12 FROM customer_subscriptions WHERE status = 'active'"
        )

        annual_revenue = arr.scalar() or 0

        # Growth rate multiplier
        growth_rate = await self._calculate_revenue_growth_rate()

        # Base multiple for SaaS
        base_multiple = 5

        # Adjust for growth
        if growth_rate > 100:
            multiple = base_multiple * 3
        elif growth_rate > 50:
            multiple = base_multiple * 2
        elif growth_rate > 30:
            multiple = base_multiple * 1.5
        else:
            multiple = base_multiple

        # Additional factors
        factors = await self._get_valuation_factors()
        multiple *= factors

        return annual_revenue * multiple

    async def _calculate_ltv_cac_ratio(self) -> float:
        """Calculate LTV:CAC ratio"""

        ltv = await self.db.execute(
            """
            SELECT AVG(lifetime_value) as avg_ltv
            FROM customer_analytics
            WHERE created_at >= NOW() - INTERVAL '6 months'
            """
        )

        cac = await self.db.execute(
            """
            SELECT AVG(acquisition_cost) as avg_cac
            FROM customer_acquisition
            WHERE created_at >= NOW() - INTERVAL '6 months'
            """
        )

        avg_ltv = ltv.scalar() or 5000
        avg_cac = cac.scalar() or 1000

        return avg_ltv / avg_cac if avg_cac > 0 else 0

    async def _get_nps_score(self) -> float:
        """Get Net Promoter Score"""

        nps = await self.db.execute(
            """
            SELECT
                (SUM(CASE WHEN score >= 9 THEN 1 ELSE 0 END) -
                 SUM(CASE WHEN score <= 6 THEN 1 ELSE 0 END))::float /
                COUNT(*)::float * 100 as nps
            FROM nps_surveys
            WHERE survey_date >= NOW() - INTERVAL '30 days'
            """
        )

        return nps.scalar() or 0

    async def _generate_executive_alerts(
        self,
        revenue_metrics: Dict[str, Any],
        retention_metrics: Dict[str, Any],
        engagement_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate executive alerts"""

        alerts = []

        # Churn alert
        if retention_metrics["monthly_churn_rate"] > 5:
            alerts.append({
                "severity": "critical",
                "category": "retention",
                "message": f"Monthly churn at {retention_metrics['monthly_churn_rate']:.1f}% (target: <5%)",
                "action": "Review at-risk customers and implement retention campaign"
            })

        # Growth alert
        if revenue_metrics["mrr_growth_rate"] < 10:
            alerts.append({
                "severity": "warning",
                "category": "growth",
                "message": f"MRR growth at {revenue_metrics['mrr_growth_rate']:.1f}% (target: >10%)",
                "action": "Accelerate acquisition and expansion initiatives"
            })

        # Engagement alert
        if engagement_metrics["active_users"]["dau_mau_ratio"] < 20:
            alerts.append({
                "severity": "warning",
                "category": "engagement",
                "message": f"DAU/MAU ratio at {engagement_metrics['active_users']['dau_mau_ratio']:.1f}% (target: >20%)",
                "action": "Implement daily engagement features"
            })

        return alerts

    async def _identify_top_opportunities(self) -> List[Dict[str, Any]]:
        """Identify top opportunities"""

        opportunities = []

        # Upsell opportunity
        upsell_value = await self.db.execute(
            """
            SELECT SUM(potential_mrr_increase) as total
            FROM upsell_opportunities
            WHERE confidence > 0.7
            """
        )

        if upsell_value.scalar() > 10000:
            opportunities.append({
                "type": "upsell",
                "value": upsell_value.scalar(),
                "description": f"£{upsell_value.scalar():,.0f} MRR from high-confidence upsells",
                "action": "Launch targeted upsell campaign",
                "timeline": "This month"
            })

        # Partnership opportunity
        opportunities.append({
            "type": "partnership",
            "value": 50000,
            "description": "5 strategic partnerships ready to close",
            "action": "Fast-track partnership agreements",
            "timeline": "Next 2 weeks"
        })

        # Market expansion
        opportunities.append({
            "type": "expansion",
            "value": 200000,
            "description": "US market entry opportunity",
            "action": "Prepare market entry strategy",
            "timeline": "Q2 2025"
        })

        return opportunities

    async def _calculate_valuation_growth_rate(self) -> float:
        """Calculate valuation growth rate"""

        current = await self._estimate_valuation()

        # Get valuation 12 months ago (simplified)
        previous = current * 0.5  # Assuming 100% growth

        return ((current - previous) / previous * 100) if previous > 0 else 0

    def _calculate_required_growth_rate(
        self,
        current: float,
        target: float,
        months: float
    ) -> float:
        """Calculate required monthly growth rate"""

        if months <= 0 or current <= 0:
            return 0

        years = months / 12
        required_multiplier = target / current
        monthly_rate = (required_multiplier ** (1 / months) - 1) * 100

        return monthly_rate

    def _generate_wealth_milestones(
        self,
        current: float,
        target: float
    ) -> List[Dict[str, Any]]:
        """Generate wealth-building milestones"""

        milestones = [
            {"value": 1_000_000, "label": "£1M", "achieved": current >= 1_000_000},
            {"value": 5_000_000, "label": "£5M", "achieved": current >= 5_000_000},
            {"value": 10_000_000, "label": "£10M", "achieved": current >= 10_000_000},
            {"value": 25_000_000, "label": "£25M", "achieved": current >= 25_000_000},
            {"value": 50_000_000, "label": "£50M", "achieved": current >= 50_000_000},
            {"value": 100_000_000, "label": "£100M", "achieved": current >= 100_000_000},
            {"value": 200_000_000, "label": "£200M", "achieved": current >= 200_000_000},
        ]

        for milestone in milestones:
            if not milestone["achieved"]:
                gap = milestone["value"] - current
                milestone["gap"] = gap
                milestone["progress"] = (current / milestone["value"]) * 100

        return milestones

    async def _identify_critical_path(self) -> List[str]:
        """Identify critical path to £200M"""

        return [
            "Achieve £100K MRR (Platform sustainability)",
            "Launch US market expansion (3x TAM)",
            "Build partnership ecosystem (Network effects)",
            "Achieve £1M MRR (Series A readiness)",
            "Develop AI moat (Defensibility)",
            "Scale to 1,000 customers (Market validation)",
            "International expansion (10x TAM)",
            "Strategic acquisition (Accelerated growth)",
            "IPO or strategic exit (Liquidity event)"
        ]

    async def _identify_wealth_risks(self) -> List[Dict[str, Any]]:
        """Identify risks to wealth-building"""

        return [
            {
                "risk": "Competition from established players",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Build defensible moats and network effects"
            },
            {
                "risk": "Market downturn affecting M&A activity",
                "probability": "Low",
                "impact": "High",
                "mitigation": "Diversify revenue streams and build reserves"
            },
            {
                "risk": "Key person dependency",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Build strong leadership team and succession plan"
            },
            {
                "risk": "Technology disruption",
                "probability": "Low",
                "impact": "High",
                "mitigation": "Continuous innovation and AI investment"
            }
        ]

    async def _identify_acceleration_opportunities(self) -> List[Dict[str, Any]]:
        """Identify opportunities to accelerate wealth-building"""

        return [
            {
                "opportunity": "Strategic acquisition of competitor",
                "impact": "2x revenue overnight",
                "investment": "£5M",
                "timeline": "6-12 months",
                "confidence": "Medium"
            },
            {
                "opportunity": "AI breakthrough in deal matching",
                "impact": "10x conversion rates",
                "investment": "£500K",
                "timeline": "3-6 months",
                "confidence": "High"
            },
            {
                "opportunity": "White-label enterprise offering",
                "impact": "£5M ARR from 10 customers",
                "investment": "£200K",
                "timeline": "6 months",
                "confidence": "High"
            },
            {
                "opportunity": "Podcast network acquisition",
                "impact": "100K new leads",
                "investment": "£1M",
                "timeline": "3 months",
                "confidence": "Medium"
            }
        ]

    async def _calculate_revenue_growth_rate(self) -> float:
        """Calculate year-over-year revenue growth rate"""

        current = await self.db.execute(
            "SELECT SUM(revenue) FROM revenue WHERE date >= NOW() - INTERVAL '12 months'"
        )

        previous = await self.db.execute(
            """
            SELECT SUM(revenue)
            FROM revenue
            WHERE date >= NOW() - INTERVAL '24 months'
            AND date < NOW() - INTERVAL '12 months'
            """
        )

        curr = current.scalar() or 0
        prev = previous.scalar() or 1

        return ((curr - prev) / prev * 100) if prev > 0 else 0

    async def _get_valuation_factors(self) -> float:
        """Get valuation adjustment factors"""

        factor = 1.0

        # Recurring revenue quality
        nrr = await self.db.execute(
            "SELECT net_revenue_retention FROM metrics WHERE metric = 'nrr'"
        )

        if nrr.scalar() and nrr.scalar() > 110:
            factor *= 1.2

        # Technology differentiation
        ai_advantage = True  # We have AI advantage
        if ai_advantage:
            factor *= 1.3

        # Market position
        market_leader = False  # Not yet
        if market_leader:
            factor *= 1.5

        return factor

    async def _generate_revenue_insights(self) -> List[StrategicInsight]:
        """Generate revenue insights"""

        insights = []

        # Quick ratio insight
        quick_ratio = await self.db.execute(
            "SELECT quick_ratio FROM metrics WHERE date = CURRENT_DATE"
        )

        if quick_ratio.scalar() and quick_ratio.scalar() < 2:
            insights.append(StrategicInsight(
                category="Revenue",
                severity="warning",
                insight="Quick ratio below healthy threshold",
                impact="Unsustainable unit economics",
                recommendation="Focus on reducing churn over new acquisition",
                potential_value=-500000,
                confidence=0.85,
                data_points={"quick_ratio": quick_ratio.scalar()}
            ))

        return insights

    async def _generate_customer_insights(self) -> List[StrategicInsight]:
        """Generate customer insights"""

        insights = []

        # Feature adoption insight
        adoption = await self.db.execute(
            """
            SELECT AVG(features_used)::float / total_features * 100 as adoption_rate
            FROM feature_analytics
            """
        )

        if adoption.scalar() and adoption.scalar() < 40:
            insights.append(StrategicInsight(
                category="Customer",
                severity="warning",
                insight="Low feature adoption limiting value realization",
                impact=f"Only {adoption.scalar():.0f}% feature utilization",
                recommendation="Launch feature education campaign",
                potential_value=200000,
                confidence=0.75,
                data_points={"adoption_rate": adoption.scalar()}
            ))

        return insights

    async def _generate_growth_insights(self) -> List[StrategicInsight]:
        """Generate growth insights"""

        insights = []

        # Viral coefficient
        viral = await self.db.execute(
            "SELECT viral_coefficient FROM growth_metrics WHERE date = CURRENT_DATE"
        )

        if viral.scalar() and viral.scalar() < 0.5:
            insights.append(StrategicInsight(
                category="Growth",
                severity="opportunity",
                insight="Low viral coefficient limiting organic growth",
                impact="Missing 50% potential organic acquisition",
                recommendation="Implement referral program with incentives",
                potential_value=1000000,
                confidence=0.7,
                data_points={"viral_coefficient": viral.scalar()}
            ))

        return insights

    # Chart generation methods (simplified representations)
    async def _get_mrr_trend_chart(self) -> Dict[str, Any]:
        """Get MRR trend chart data"""
        return {"type": "line", "data": [], "title": "MRR Trend"}

    async def _get_customer_growth_chart(self) -> Dict[str, Any]:
        """Get customer growth chart data"""
        return {"type": "line", "data": [], "title": "Customer Growth"}

    async def _get_churn_cohort_chart(self) -> Dict[str, Any]:
        """Get churn cohort chart data"""
        return {"type": "heatmap", "data": [], "title": "Churn Cohorts"}

    async def _get_revenue_segment_chart(self) -> Dict[str, Any]:
        """Get revenue segment chart data"""
        return {"type": "pie", "data": [], "title": "Revenue Segments"}

    async def _get_mrr_waterfall_chart(self) -> Dict[str, Any]:
        """Get MRR waterfall chart data"""
        return {"type": "waterfall", "data": [], "title": "MRR Movement"}

    async def _get_revenue_forecast_chart(self) -> Dict[str, Any]:
        """Get revenue forecast chart data"""
        return {"type": "line", "data": [], "title": "Revenue Forecast"}

    async def _get_tier_distribution_chart(self) -> Dict[str, Any]:
        """Get tier distribution chart data"""
        return {"type": "bar", "data": [], "title": "Tier Distribution"}

    async def _get_growth_accounting_chart(self) -> Dict[str, Any]:
        """Get growth accounting chart data"""
        return {"type": "stacked_bar", "data": [], "title": "Growth Accounting"}

    async def _get_cohort_retention_chart(self) -> Dict[str, Any]:
        """Get cohort retention chart data"""
        return {"type": "cohort", "data": [], "title": "Cohort Retention"}

    async def _get_funnel_visualization(self) -> Dict[str, Any]:
        """Get funnel visualization data"""
        return {"type": "funnel", "data": [], "title": "Conversion Funnel"}

    async def _get_channel_roi_chart(self) -> Dict[str, Any]:
        """Get channel ROI chart data"""
        return {"type": "bar", "data": [], "title": "Channel ROI"}

    async def _get_partner_network_visualization(self) -> Dict[str, Any]:
        """Get partner network visualization data"""
        return {"type": "network", "data": [], "title": "Partner Network"}

    async def _get_partnership_value_chart(self) -> Dict[str, Any]:
        """Get partnership value chart data"""
        return {"type": "bar", "data": [], "title": "Partnership Value"}

    async def _get_partner_performance_chart(self) -> Dict[str, Any]:
        """Get partner performance chart data"""
        return {"type": "scatter", "data": [], "title": "Partner Performance"}

    async def _get_churn_prediction_chart(self) -> Dict[str, Any]:
        """Get churn prediction chart data"""
        return {"type": "risk_matrix", "data": [], "title": "Churn Prediction"}

    async def _get_engagement_distribution_chart(self) -> Dict[str, Any]:
        """Get engagement distribution chart data"""
        return {"type": "histogram", "data": [], "title": "Engagement Distribution"}

    async def _get_customer_journey_map(self) -> Dict[str, Any]:
        """Get customer journey map data"""
        return {"type": "journey", "data": [], "title": "Customer Journey"}

    async def _get_market_share_chart(self) -> Dict[str, Any]:
        """Get market share chart data"""
        return {"type": "pie", "data": [], "title": "Market Share"}

    async def _get_competitive_matrix(self) -> Dict[str, Any]:
        """Get competitive matrix data"""
        return {"type": "matrix", "data": [], "title": "Competitive Position"}

    async def _get_trend_analysis_chart(self) -> Dict[str, Any]:
        """Get trend analysis chart data"""
        return {"type": "multi_line", "data": [], "title": "Market Trends"}

    async def _get_valuation_trajectory_chart(self) -> Dict[str, Any]:
        """Get valuation trajectory chart data"""
        return {"type": "projection", "data": [], "title": "Valuation Path"}

    async def _get_milestone_progress_chart(self) -> Dict[str, Any]:
        """Get milestone progress chart data"""
        return {"type": "milestone", "data": [], "title": "Milestone Progress"}

    async def _get_scenario_analysis_chart(self) -> Dict[str, Any]:
        """Get scenario analysis chart data"""
        return {"type": "scenario", "data": [], "title": "Growth Scenarios"}

    async def _get_active_experiments(self) -> List[Dict[str, Any]]:
        """Get active growth experiments"""
        return [
            {
                "name": "Podcast CTA optimization",
                "status": "Running",
                "duration": "14 days",
                "metric": "Conversion rate",
                "current_result": "+12%"
            }
        ]

    async def _get_customer_success_actions(self) -> List[Dict[str, Any]]:
        """Get customer success action items"""
        return [
            {
                "priority": "High",
                "customer": "Enterprise Corp",
                "action": "Schedule QBR",
                "due_date": "This week"
            }
        ]

    async def _get_strategic_initiatives(self) -> List[Dict[str, Any]]:
        """Get strategic initiatives"""
        return [
            {
                "initiative": "AI Patent Filing",
                "status": "In Progress",
                "impact": "Defensible moat",
                "timeline": "Q1 2025"
            }
        ]

    async def _calculate_investment_requirements(self) -> Dict[str, Any]:
        """Calculate investment requirements"""
        return {
            "next_round": "Series A",
            "target_raise": "£5M",
            "valuation": "£25M",
            "use_of_funds": [
                {"category": "Engineering", "amount": "£2M"},
                {"category": "Sales & Marketing", "amount": "£2M"},
                {"category": "Operations", "amount": "£1M"}
            ],
            "timeline": "Q3 2025"
        }