"""
Synergy Tracking & Value Realization Engine - Advanced synergy management and ROI optimization
Provides comprehensive synergy identification, tracking, and value creation optimization
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json
import uuid
import math
import statistics
from abc import ABC, abstractmethod

# Data Models and Enums
class SynergyType(Enum):
    REVENUE_SYNERGY = "revenue_synergy"
    COST_SYNERGY = "cost_synergy"
    TAX_SYNERGY = "tax_synergy"
    FINANCIAL_SYNERGY = "financial_synergy"
    OPERATIONAL_SYNERGY = "operational_synergy"

class SynergyCategory(Enum):
    CROSS_SELLING = "cross_selling"
    PRICING_OPTIMIZATION = "pricing_optimization"
    MARKET_EXPANSION = "market_expansion"
    ECONOMIES_OF_SCALE = "economies_of_scale"
    PROCESS_OPTIMIZATION = "process_optimization"
    TECHNOLOGY_CONSOLIDATION = "technology_consolidation"
    OVERHEAD_REDUCTION = "overhead_reduction"
    PROCUREMENT_SAVINGS = "procurement_savings"
    TAX_OPTIMIZATION = "tax_optimization"
    WORKING_CAPITAL = "working_capital"

class RealizationStatus(Enum):
    IDENTIFIED = "identified"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    REALIZED = "realized"
    AT_RISK = "at_risk"
    DELAYED = "delayed"
    CANCELLED = "cancelled"

class ValueTrackingFrequency(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

@dataclass
class SynergyOpportunity:
    """Individual synergy opportunity identification"""
    synergy_id: str
    name: str
    description: str
    synergy_type: SynergyType
    category: SynergyCategory
    estimated_value: float
    realization_timeline_months: int
    confidence_level: float  # 0-1
    status: RealizationStatus = RealizationStatus.IDENTIFIED
    owner: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    implementation_plan: Optional[str] = None
    created_date: datetime = field(default_factory=datetime.now)
    target_realization_date: Optional[datetime] = None

@dataclass
class SynergyRealization:
    """Actual synergy realization tracking"""
    realization_id: str
    synergy_id: str
    period_start: datetime
    period_end: datetime
    realized_value: float
    planned_value: float
    variance: float
    variance_percentage: float
    realization_rate: float  # cumulative
    contributing_factors: List[str] = field(default_factory=list)
    challenges_encountered: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    recorded_date: datetime = field(default_factory=datetime.now)

@dataclass
class ValueCreationMetrics:
    """Comprehensive value creation metrics"""
    metrics_id: str
    integration_id: str
    measurement_period: Tuple[datetime, datetime]
    total_synergies_identified: float
    total_synergies_realized: float
    realization_rate: float
    roi_percentage: float
    value_creation_timeline: Dict[str, float]
    synergy_breakdown: Dict[SynergyType, float]
    performance_vs_plan: Dict[str, float]
    risk_adjusted_value: float
    net_present_value: float
    payback_period_months: float

class SynergyIdentificationEngine:
    """AI-powered synergy identification and quantification"""

    def __init__(self):
        self.synergy_models = {}
        self.industry_benchmarks = defaultdict(dict)
        self.historical_patterns = defaultdict(list)
        self.identification_algorithms = {}

    def identify_synergy_opportunities(self, deal_data: Dict[str, Any],
                                     target_data: Dict[str, Any],
                                     acquirer_data: Dict[str, Any]) -> List[SynergyOpportunity]:
        """Identify comprehensive synergy opportunities using AI"""

        opportunities = []

        # Revenue synergies
        revenue_synergies = self._identify_revenue_synergies(deal_data, target_data, acquirer_data)
        opportunities.extend(revenue_synergies)

        # Cost synergies
        cost_synergies = self._identify_cost_synergies(deal_data, target_data, acquirer_data)
        opportunities.extend(cost_synergies)

        # Tax synergies
        tax_synergies = self._identify_tax_synergies(deal_data, target_data, acquirer_data)
        opportunities.extend(tax_synergies)

        # Financial synergies
        financial_synergies = self._identify_financial_synergies(deal_data, target_data, acquirer_data)
        opportunities.extend(financial_synergies)

        # Operational synergies
        operational_synergies = self._identify_operational_synergies(deal_data, target_data, acquirer_data)
        opportunities.extend(operational_synergies)

        # Rank and prioritize opportunities
        opportunities = self._prioritize_synergies(opportunities)

        return opportunities

    def quantify_synergy_value(self, synergy_opportunity: SynergyOpportunity,
                             market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Quantify synergy value using advanced modeling"""

        base_value = synergy_opportunity.estimated_value
        confidence = synergy_opportunity.confidence_level

        # Risk adjustment
        risk_factors = len(synergy_opportunity.risks)
        risk_adjustment = max(0.7, 1.0 - (risk_factors * 0.05))

        # Market condition adjustment
        market_growth = market_data.get("market_growth_rate", 0.03)
        market_adjustment = 1.0 + market_growth

        # Timeline adjustment (longer timelines have more uncertainty)
        timeline_months = synergy_opportunity.realization_timeline_months
        timeline_adjustment = max(0.8, 1.0 - (timeline_months / 60 * 0.2))

        # Calculate adjusted values
        conservative_value = base_value * confidence * risk_adjustment * timeline_adjustment
        optimistic_value = base_value * market_adjustment * 1.2
        most_likely_value = base_value * confidence * risk_adjustment

        # NPV calculation
        discount_rate = market_data.get("discount_rate", 0.10)
        npv = self._calculate_npv(most_likely_value, timeline_months, discount_rate)

        quantification = {
            "base_value": base_value,
            "conservative_value": conservative_value,
            "most_likely_value": most_likely_value,
            "optimistic_value": optimistic_value,
            "risk_adjusted_value": most_likely_value,
            "net_present_value": npv,
            "confidence_interval": {
                "lower": conservative_value,
                "upper": optimistic_value
            },
            "sensitivity_analysis": {
                "risk_sensitivity": risk_adjustment,
                "timeline_sensitivity": timeline_adjustment,
                "market_sensitivity": market_adjustment
            },
            "value_distribution": {
                "p10": conservative_value,
                "p50": most_likely_value,
                "p90": optimistic_value
            }
        }

        return quantification

    def _identify_revenue_synergies(self, deal_data: Dict[str, Any],
                                  target_data: Dict[str, Any],
                                  acquirer_data: Dict[str, Any]) -> List[SynergyOpportunity]:
        """Identify revenue synergy opportunities"""

        synergies = []

        # Cross-selling opportunities
        if self._has_complementary_products(target_data, acquirer_data):
            cross_sell_value = self._estimate_cross_selling_value(target_data, acquirer_data)
            if cross_sell_value > 0:
                synergies.append(SynergyOpportunity(
                    synergy_id=f"revenue_cross_sell_{uuid.uuid4().hex[:8]}",
                    name="Cross-selling to Combined Customer Base",
                    description="Leverage combined customer base for cross-selling opportunities",
                    synergy_type=SynergyType.REVENUE_SYNERGY,
                    category=SynergyCategory.CROSS_SELLING,
                    estimated_value=cross_sell_value,
                    realization_timeline_months=12,
                    confidence_level=0.7,
                    success_criteria=[
                        "Customer segmentation analysis completed",
                        "Cross-sell campaign launched",
                        "Sales team training completed"
                    ],
                    risks=["Customer churn", "Product cannibalization"]
                ))

        # Pricing optimization
        pricing_value = self._estimate_pricing_synergies(target_data, acquirer_data)
        if pricing_value > 0:
            synergies.append(SynergyOpportunity(
                synergy_id=f"revenue_pricing_{uuid.uuid4().hex[:8]}",
                name="Pricing Power Enhancement",
                description="Optimize pricing through increased market power",
                synergy_type=SynergyType.REVENUE_SYNERGY,
                category=SynergyCategory.PRICING_OPTIMIZATION,
                estimated_value=pricing_value,
                realization_timeline_months=6,
                confidence_level=0.6,
                success_criteria=[
                    "Market analysis completed",
                    "Pricing strategy implemented",
                    "Customer acceptance validated"
                ],
                risks=["Customer pushback", "Competitive response"]
            ))

        # Market expansion
        market_expansion_value = self._estimate_market_expansion(target_data, acquirer_data)
        if market_expansion_value > 0:
            synergies.append(SynergyOpportunity(
                synergy_id=f"revenue_expansion_{uuid.uuid4().hex[:8]}",
                name="Geographic Market Expansion",
                description="Expand into new geographic markets using combined capabilities",
                synergy_type=SynergyType.REVENUE_SYNERGY,
                category=SynergyCategory.MARKET_EXPANSION,
                estimated_value=market_expansion_value,
                realization_timeline_months=18,
                confidence_level=0.5,
                success_criteria=[
                    "Market entry strategy developed",
                    "Local partnerships established",
                    "Regulatory approvals obtained"
                ],
                risks=["Regulatory barriers", "Local competition", "Cultural differences"]
            ))

        return synergies

    def _identify_cost_synergies(self, deal_data: Dict[str, Any],
                               target_data: Dict[str, Any],
                               acquirer_data: Dict[str, Any]) -> List[SynergyOpportunity]:
        """Identify cost synergy opportunities"""

        synergies = []

        # Economies of scale
        scale_savings = self._estimate_scale_economies(target_data, acquirer_data)
        if scale_savings > 0:
            synergies.append(SynergyOpportunity(
                synergy_id=f"cost_scale_{uuid.uuid4().hex[:8]}",
                name="Economies of Scale Realization",
                description="Achieve cost savings through increased operational scale",
                synergy_type=SynergyType.COST_SYNERGY,
                category=SynergyCategory.ECONOMIES_OF_SCALE,
                estimated_value=scale_savings,
                realization_timeline_months=12,
                confidence_level=0.8,
                success_criteria=[
                    "Operations consolidated",
                    "Volume discounts negotiated",
                    "Efficiency metrics improved"
                ],
                risks=["Integration complexity", "Quality degradation"]
            ))

        # Overhead reduction
        overhead_savings = self._estimate_overhead_reduction(target_data, acquirer_data)
        if overhead_savings > 0:
            synergies.append(SynergyOpportunity(
                synergy_id=f"cost_overhead_{uuid.uuid4().hex[:8]}",
                name="Corporate Overhead Reduction",
                description="Eliminate duplicate corporate functions and overhead",
                synergy_type=SynergyType.COST_SYNERGY,
                category=SynergyCategory.OVERHEAD_REDUCTION,
                estimated_value=overhead_savings,
                realization_timeline_months=9,
                confidence_level=0.9,
                success_criteria=[
                    "Organization structure optimized",
                    "Redundant roles eliminated",
                    "Systems consolidated"
                ],
                risks=["Employee morale", "Regulatory compliance"]
            ))

        # Technology consolidation
        tech_savings = self._estimate_technology_savings(target_data, acquirer_data)
        if tech_savings > 0:
            synergies.append(SynergyOpportunity(
                synergy_id=f"cost_technology_{uuid.uuid4().hex[:8]}",
                name="Technology Platform Consolidation",
                description="Consolidate technology platforms and eliminate redundancy",
                synergy_type=SynergyType.COST_SYNERGY,
                category=SynergyCategory.TECHNOLOGY_CONSOLIDATION,
                estimated_value=tech_savings,
                realization_timeline_months=15,
                confidence_level=0.7,
                success_criteria=[
                    "Technology audit completed",
                    "Migration plan executed",
                    "Legacy systems decommissioned"
                ],
                risks=["Data migration issues", "System downtime", "User adoption"]
            ))

        return synergies

    def _identify_tax_synergies(self, deal_data: Dict[str, Any],
                              target_data: Dict[str, Any],
                              acquirer_data: Dict[str, Any]) -> List[SynergyOpportunity]:
        """Identify tax synergy opportunities"""

        synergies = []

        # Tax optimization through structure
        tax_optimization_value = self._estimate_tax_optimization(deal_data, target_data, acquirer_data)
        if tax_optimization_value > 0:
            synergies.append(SynergyOpportunity(
                synergy_id=f"tax_optimization_{uuid.uuid4().hex[:8]}",
                name="Tax Structure Optimization",
                description="Optimize tax efficiency through combined entity structure",
                synergy_type=SynergyType.TAX_SYNERGY,
                category=SynergyCategory.TAX_OPTIMIZATION,
                estimated_value=tax_optimization_value,
                realization_timeline_months=6,
                confidence_level=0.8,
                success_criteria=[
                    "Tax strategy approved",
                    "Structure implemented",
                    "Compliance verified"
                ],
                risks=["Regulatory changes", "Audit scrutiny"]
            ))

        return synergies

    def _identify_financial_synergies(self, deal_data: Dict[str, Any],
                                    target_data: Dict[str, Any],
                                    acquirer_data: Dict[str, Any]) -> List[SynergyOpportunity]:
        """Identify financial synergy opportunities"""

        synergies = []

        # Working capital optimization
        working_capital_value = self._estimate_working_capital_optimization(target_data, acquirer_data)
        if working_capital_value > 0:
            synergies.append(SynergyOpportunity(
                synergy_id=f"financial_wc_{uuid.uuid4().hex[:8]}",
                name="Working Capital Optimization",
                description="Optimize working capital through improved processes",
                synergy_type=SynergyType.FINANCIAL_SYNERGY,
                category=SynergyCategory.WORKING_CAPITAL,
                estimated_value=working_capital_value,
                realization_timeline_months=12,
                confidence_level=0.7,
                success_criteria=[
                    "Working capital baseline established",
                    "Optimization processes implemented",
                    "Cash conversion cycle improved"
                ],
                risks=["Supplier relationships", "Customer payment terms"]
            ))

        return synergies

    def _identify_operational_synergies(self, deal_data: Dict[str, Any],
                                      target_data: Dict[str, Any],
                                      acquirer_data: Dict[str, Any]) -> List[SynergyOpportunity]:
        """Identify operational synergy opportunities"""

        synergies = []

        # Process optimization
        process_value = self._estimate_process_optimization(target_data, acquirer_data)
        if process_value > 0:
            synergies.append(SynergyOpportunity(
                synergy_id=f"operational_process_{uuid.uuid4().hex[:8]}",
                name="Business Process Optimization",
                description="Optimize business processes through best practice sharing",
                synergy_type=SynergyType.OPERATIONAL_SYNERGY,
                category=SynergyCategory.PROCESS_OPTIMIZATION,
                estimated_value=process_value,
                realization_timeline_months=15,
                confidence_level=0.6,
                success_criteria=[
                    "Process mapping completed",
                    "Best practices identified",
                    "Standardization implemented"
                ],
                risks=["Change resistance", "Process disruption"]
            ))

        return synergies

    def _has_complementary_products(self, target_data: Dict[str, Any],
                                  acquirer_data: Dict[str, Any]) -> bool:
        """Check if companies have complementary products"""
        target_products = set(target_data.get("product_categories", []))
        acquirer_products = set(acquirer_data.get("product_categories", []))
        return len(target_products.intersection(acquirer_products)) > 0

    def _estimate_cross_selling_value(self, target_data: Dict[str, Any],
                                    acquirer_data: Dict[str, Any]) -> float:
        """Estimate cross-selling value potential"""
        target_revenue = target_data.get("annual_revenue", 0)
        acquirer_revenue = acquirer_data.get("annual_revenue", 0)
        customer_overlap = target_data.get("customer_overlap", 0.1)

        # Simple estimation: 5-15% revenue uplift from cross-selling
        cross_sell_rate = 0.10 * (1 - customer_overlap)
        return (target_revenue + acquirer_revenue) * cross_sell_rate

    def _estimate_pricing_synergies(self, target_data: Dict[str, Any],
                                  acquirer_data: Dict[str, Any]) -> float:
        """Estimate pricing synergy value"""
        combined_revenue = target_data.get("annual_revenue", 0) + acquirer_data.get("annual_revenue", 0)
        market_share_increase = target_data.get("market_share", 0.05) + acquirer_data.get("market_share", 0.05)

        # Pricing power increases with market share
        if market_share_increase > 0.2:  # >20% market share
            pricing_uplift = 0.02  # 2% pricing improvement
        elif market_share_increase > 0.1:  # >10% market share
            pricing_uplift = 0.01  # 1% pricing improvement
        else:
            pricing_uplift = 0.005  # 0.5% pricing improvement

        return combined_revenue * pricing_uplift

    def _estimate_market_expansion(self, target_data: Dict[str, Any],
                                 acquirer_data: Dict[str, Any]) -> float:
        """Estimate market expansion value"""
        target_markets = set(target_data.get("geographic_markets", []))
        acquirer_markets = set(acquirer_data.get("geographic_markets", []))

        new_markets = target_markets.symmetric_difference(acquirer_markets)
        if len(new_markets) > 0:
            base_revenue = min(target_data.get("annual_revenue", 0), acquirer_data.get("annual_revenue", 0))
            expansion_rate = len(new_markets) * 0.05  # 5% per new market
            return base_revenue * expansion_rate

        return 0

    def _estimate_scale_economies(self, target_data: Dict[str, Any],
                                acquirer_data: Dict[str, Any]) -> float:
        """Estimate economies of scale savings"""
        target_costs = target_data.get("operating_costs", 0)
        acquirer_costs = acquirer_data.get("operating_costs", 0)
        combined_costs = target_costs + acquirer_costs

        # Scale economies: 3-8% cost reduction
        scale_savings_rate = 0.05
        return combined_costs * scale_savings_rate

    def _estimate_overhead_reduction(self, target_data: Dict[str, Any],
                                   acquirer_data: Dict[str, Any]) -> float:
        """Estimate overhead reduction savings"""
        target_overhead = target_data.get("overhead_costs", target_data.get("operating_costs", 0) * 0.15)
        acquirer_overhead = acquirer_data.get("overhead_costs", acquirer_data.get("operating_costs", 0) * 0.15)

        # Assume 30-50% overhead reduction possible
        overhead_reduction_rate = 0.4
        duplicate_overhead = min(target_overhead, acquirer_overhead)
        return duplicate_overhead * overhead_reduction_rate

    def _estimate_technology_savings(self, target_data: Dict[str, Any],
                                   acquirer_data: Dict[str, Any]) -> float:
        """Estimate technology consolidation savings"""
        target_tech_spend = target_data.get("technology_spend", target_data.get("operating_costs", 0) * 0.08)
        acquirer_tech_spend = acquirer_data.get("technology_spend", acquirer_data.get("operating_costs", 0) * 0.08)

        # Technology consolidation: 15-25% savings
        tech_savings_rate = 0.20
        combined_tech_spend = target_tech_spend + acquirer_tech_spend
        return combined_tech_spend * tech_savings_rate

    def _estimate_tax_optimization(self, deal_data: Dict[str, Any],
                                 target_data: Dict[str, Any],
                                 acquirer_data: Dict[str, Any]) -> float:
        """Estimate tax optimization value"""
        combined_pretax_income = (
            target_data.get("pretax_income", 0) +
            acquirer_data.get("pretax_income", 0)
        )

        # Tax optimization: 1-3% of pretax income
        tax_optimization_rate = 0.02
        return combined_pretax_income * tax_optimization_rate

    def _estimate_working_capital_optimization(self, target_data: Dict[str, Any],
                                             acquirer_data: Dict[str, Any]) -> float:
        """Estimate working capital optimization value"""
        target_wc = target_data.get("working_capital", target_data.get("annual_revenue", 0) * 0.15)
        acquirer_wc = acquirer_data.get("working_capital", acquirer_data.get("annual_revenue", 0) * 0.15)

        # Working capital optimization: 10-20% improvement
        wc_optimization_rate = 0.15
        combined_wc = target_wc + acquirer_wc
        return combined_wc * wc_optimization_rate

    def _estimate_process_optimization(self, target_data: Dict[str, Any],
                                     acquirer_data: Dict[str, Any]) -> float:
        """Estimate process optimization value"""
        combined_costs = (
            target_data.get("operating_costs", 0) +
            acquirer_data.get("operating_costs", 0)
        )

        # Process optimization: 2-5% cost reduction
        process_savings_rate = 0.035
        return combined_costs * process_savings_rate

    def _prioritize_synergies(self, synergies: List[SynergyOpportunity]) -> List[SynergyOpportunity]:
        """Prioritize synergies by value and feasibility"""

        # Calculate priority score for each synergy
        for synergy in synergies:
            value_score = synergy.estimated_value / 1_000_000  # Normalize to millions
            confidence_score = synergy.confidence_level * 10
            timeline_score = max(1, 25 - synergy.realization_timeline_months)  # Prefer shorter timelines
            risk_score = max(1, 10 - len(synergy.risks) * 2)  # Prefer lower risk

            priority_score = (value_score * 0.4 + confidence_score * 0.3 +
                            timeline_score * 0.2 + risk_score * 0.1)

            # Store priority score for sorting
            synergy.priority_score = priority_score

        # Sort by priority score (descending)
        synergies.sort(key=lambda x: getattr(x, 'priority_score', 0), reverse=True)

        return synergies

    def _calculate_npv(self, annual_value: float, timeline_months: int, discount_rate: float) -> float:
        """Calculate net present value of synergy"""
        if timeline_months <= 0:
            return 0

        monthly_value = annual_value / 12
        monthly_discount_rate = discount_rate / 12

        npv = 0
        for month in range(1, timeline_months + 1):
            npv += monthly_value / ((1 + monthly_discount_rate) ** month)

        return npv

class ValueTracker:
    """Real-time synergy value tracking and realization monitoring"""

    def __init__(self):
        self.realization_tracking = defaultdict(list)
        self.value_metrics = defaultdict(dict)
        self.performance_benchmarks = {}
        self.tracking_frequency = ValueTrackingFrequency.MONTHLY

    def track_synergy_realization(self, synergy_id: str, period_data: Dict[str, Any]) -> str:
        """Track actual synergy realization vs. plan"""

        realization_id = f"realization_{synergy_id}_{int(datetime.now().timestamp())}"

        period_start = datetime.fromisoformat(period_data["period_start"])
        period_end = datetime.fromisoformat(period_data["period_end"])
        realized_value = period_data["realized_value"]
        planned_value = period_data["planned_value"]

        # Calculate variance
        variance = realized_value - planned_value
        variance_percentage = (variance / planned_value * 100) if planned_value != 0 else 0

        # Calculate cumulative realization rate
        historical_realizations = self.realization_tracking[synergy_id]
        total_realized = sum(r.realized_value for r in historical_realizations) + realized_value
        total_planned = sum(r.planned_value for r in historical_realizations) + planned_value
        realization_rate = (total_realized / total_planned) if total_planned > 0 else 0

        realization = SynergyRealization(
            realization_id=realization_id,
            synergy_id=synergy_id,
            period_start=period_start,
            period_end=period_end,
            realized_value=realized_value,
            planned_value=planned_value,
            variance=variance,
            variance_percentage=variance_percentage,
            realization_rate=realization_rate,
            contributing_factors=period_data.get("contributing_factors", []),
            challenges_encountered=period_data.get("challenges_encountered", []),
            lessons_learned=period_data.get("lessons_learned", [])
        )

        self.realization_tracking[synergy_id].append(realization)

        return realization_id

    def calculate_portfolio_metrics(self, integration_id: str,
                                  synergies: List[SynergyOpportunity],
                                  period_start: datetime,
                                  period_end: datetime) -> ValueCreationMetrics:
        """Calculate comprehensive value creation metrics"""

        metrics_id = f"metrics_{integration_id}_{int(datetime.now().timestamp())}"

        # Total identified synergies
        total_identified = sum(s.estimated_value for s in synergies)

        # Total realized synergies
        total_realized = 0
        synergy_breakdown = defaultdict(float)

        for synergy in synergies:
            synergy_realizations = self.realization_tracking.get(synergy.synergy_id, [])
            period_realizations = [
                r for r in synergy_realizations
                if period_start <= r.period_start <= period_end
            ]

            synergy_realized = sum(r.realized_value for r in period_realizations)
            total_realized += synergy_realized
            synergy_breakdown[synergy.synergy_type] += synergy_realized

        # Calculate realization rate
        realization_rate = (total_realized / total_identified) if total_identified > 0 else 0

        # Calculate ROI
        integration_cost = self._estimate_integration_cost(total_identified)
        roi_percentage = ((total_realized - integration_cost) / integration_cost * 100) if integration_cost > 0 else 0

        # Value creation timeline
        value_timeline = self._calculate_value_timeline(synergies, period_start, period_end)

        # Performance vs. plan
        performance_vs_plan = self._calculate_performance_vs_plan(synergies)

        # Risk-adjusted value
        risk_adjusted_value = self._calculate_risk_adjusted_value(synergies, total_realized)

        # NPV calculation
        npv = self._calculate_portfolio_npv(synergies, total_realized)

        # Payback period
        payback_period = self._calculate_payback_period(total_realized, integration_cost)

        metrics = ValueCreationMetrics(
            metrics_id=metrics_id,
            integration_id=integration_id,
            measurement_period=(period_start, period_end),
            total_synergies_identified=total_identified,
            total_synergies_realized=total_realized,
            realization_rate=realization_rate,
            roi_percentage=roi_percentage,
            value_creation_timeline=value_timeline,
            synergy_breakdown=dict(synergy_breakdown),
            performance_vs_plan=performance_vs_plan,
            risk_adjusted_value=risk_adjusted_value,
            net_present_value=npv,
            payback_period_months=payback_period
        )

        return metrics

    def _estimate_integration_cost(self, total_synergy_value: float) -> float:
        """Estimate integration cost as percentage of synergy value"""
        # Typical integration costs: 10-20% of synergy value
        return total_synergy_value * 0.15

    def _calculate_value_timeline(self, synergies: List[SynergyOpportunity],
                                period_start: datetime, period_end: datetime) -> Dict[str, float]:
        """Calculate value creation timeline"""

        timeline = {}
        current_date = period_start

        while current_date <= period_end:
            month_key = current_date.strftime("%Y-%m")
            month_value = 0

            for synergy in synergies:
                # Check if synergy should be realizing value in this month
                if (synergy.target_realization_date and
                    synergy.target_realization_date <= current_date):

                    # Estimate monthly value (simplified)
                    monthly_value = synergy.estimated_value / max(1, synergy.realization_timeline_months)
                    month_value += monthly_value

            timeline[month_key] = month_value
            current_date = current_date.replace(day=1) + timedelta(days=32)
            current_date = current_date.replace(day=1)

        return timeline

    def _calculate_performance_vs_plan(self, synergies: List[SynergyOpportunity]) -> Dict[str, float]:
        """Calculate performance vs. plan metrics"""

        total_planned = sum(s.estimated_value for s in synergies)
        total_realized = 0

        on_track_count = 0
        delayed_count = 0

        for synergy in synergies:
            synergy_realizations = self.realization_tracking.get(synergy.synergy_id, [])
            if synergy_realizations:
                latest_realization = synergy_realizations[-1]
                total_realized += latest_realization.realized_value

                if latest_realization.variance_percentage >= -10:  # Within 10% of plan
                    on_track_count += 1
                else:
                    delayed_count += 1

        return {
            "value_realization": (total_realized / total_planned) if total_planned > 0 else 0,
            "synergies_on_track": (on_track_count / len(synergies)) if synergies else 0,
            "synergies_delayed": (delayed_count / len(synergies)) if synergies else 0
        }

    def _calculate_risk_adjusted_value(self, synergies: List[SynergyOpportunity],
                                     total_realized: float) -> float:
        """Calculate risk-adjusted value"""

        weighted_confidence = 0
        total_value = 0

        for synergy in synergies:
            weighted_confidence += synergy.estimated_value * synergy.confidence_level
            total_value += synergy.estimated_value

        avg_confidence = weighted_confidence / total_value if total_value > 0 else 0
        return total_realized * avg_confidence

    def _calculate_portfolio_npv(self, synergies: List[SynergyOpportunity],
                               total_realized: float) -> float:
        """Calculate portfolio NPV"""

        # Simplified NPV calculation
        discount_rate = 0.10
        avg_timeline_years = statistics.mean([s.realization_timeline_months / 12 for s in synergies]) if synergies else 1

        npv = total_realized / ((1 + discount_rate) ** avg_timeline_years)
        return npv

    def _calculate_payback_period(self, total_realized: float, integration_cost: float) -> float:
        """Calculate payback period in months"""

        if total_realized <= 0:
            return float('inf')

        # Assuming linear value realization
        monthly_value = total_realized / 12
        payback_months = integration_cost / monthly_value if monthly_value > 0 else float('inf')

        return min(payback_months, 120)  # Cap at 10 years

class ROIAnalyzer:
    """Advanced ROI analysis and optimization"""

    def __init__(self):
        self.roi_models = {}
        self.benchmark_data = defaultdict(dict)
        self.scenario_analyses = defaultdict(list)

    def calculate_integration_roi(self, integration_data: Dict[str, Any],
                                synergy_metrics: ValueCreationMetrics) -> Dict[str, Any]:
        """Calculate comprehensive integration ROI"""

        # Basic ROI calculation
        total_investment = integration_data.get("total_integration_cost", 0)
        total_benefits = synergy_metrics.total_synergies_realized
        basic_roi = ((total_benefits - total_investment) / total_investment * 100) if total_investment > 0 else 0

        # Risk-adjusted ROI
        risk_factor = integration_data.get("risk_factor", 0.2)
        risk_adjusted_roi = basic_roi * (1 - risk_factor)

        # Time-adjusted ROI (annualized)
        integration_period_years = integration_data.get("integration_period_months", 12) / 12
        annualized_roi = basic_roi / integration_period_years if integration_period_years > 0 else basic_roi

        # Industry benchmark comparison
        industry = integration_data.get("industry", "technology")
        benchmark_roi = self._get_industry_benchmark_roi(industry)
        roi_vs_benchmark = basic_roi - benchmark_roi

        # Value driver analysis
        value_drivers = self._analyze_value_drivers(synergy_metrics)

        # Sensitivity analysis
        sensitivity_analysis = self._perform_roi_sensitivity_analysis(
            total_investment, total_benefits, integration_data
        )

        roi_analysis = {
            "basic_roi_percentage": round(basic_roi, 2),
            "risk_adjusted_roi_percentage": round(risk_adjusted_roi, 2),
            "annualized_roi_percentage": round(annualized_roi, 2),
            "roi_vs_benchmark": round(roi_vs_benchmark, 2),
            "industry_benchmark": round(benchmark_roi, 2),
            "net_value_created": total_benefits - total_investment,
            "payback_period_months": synergy_metrics.payback_period_months,
            "value_drivers": value_drivers,
            "sensitivity_analysis": sensitivity_analysis,
            "roi_category": self._categorize_roi_performance(basic_roi, benchmark_roi)
        }

        return roi_analysis

    def _get_industry_benchmark_roi(self, industry: str) -> float:
        """Get industry benchmark ROI for M&A integrations"""

        industry_benchmarks = {
            "technology": 15.5,
            "healthcare": 12.8,
            "financial_services": 11.2,
            "manufacturing": 13.5,
            "retail": 10.8,
            "energy": 14.2
        }

        return industry_benchmarks.get(industry, 12.5)

    def _analyze_value_drivers(self, metrics: ValueCreationMetrics) -> Dict[str, Any]:
        """Analyze key value drivers"""

        total_synergies = metrics.total_synergies_realized

        if total_synergies <= 0:
            return {}

        # Synergy type contribution
        synergy_contributions = {}
        for synergy_type, value in metrics.synergy_breakdown.items():
            synergy_contributions[synergy_type.value] = {
                "absolute_value": value,
                "percentage_contribution": (value / total_synergies * 100)
            }

        # Top value drivers
        sorted_contributions = sorted(
            synergy_contributions.items(),
            key=lambda x: x[1]["absolute_value"],
            reverse=True
        )

        return {
            "synergy_type_contributions": synergy_contributions,
            "top_value_drivers": [item[0] for item in sorted_contributions[:3]],
            "diversification_score": len([v for v in synergy_contributions.values() if v["percentage_contribution"] > 10])
        }

    def _perform_roi_sensitivity_analysis(self, investment: float, benefits: float,
                                        integration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform ROI sensitivity analysis"""

        base_roi = ((benefits - investment) / investment * 100) if investment > 0 else 0

        # Scenario analysis
        scenarios = {
            "optimistic": {
                "investment_change": -0.10,  # 10% cost reduction
                "benefits_change": 0.20      # 20% benefits increase
            },
            "pessimistic": {
                "investment_change": 0.20,   # 20% cost increase
                "benefits_change": -0.30     # 30% benefits reduction
            },
            "realistic": {
                "investment_change": 0.05,   # 5% cost increase
                "benefits_change": -0.10     # 10% benefits reduction
            }
        }

        scenario_rois = {}
        for scenario_name, changes in scenarios.items():
            adjusted_investment = investment * (1 + changes["investment_change"])
            adjusted_benefits = benefits * (1 + changes["benefits_change"])
            scenario_roi = ((adjusted_benefits - adjusted_investment) / adjusted_investment * 100) if adjusted_investment > 0 else 0
            scenario_rois[scenario_name] = round(scenario_roi, 2)

        # Variable sensitivity
        sensitivity_vars = {
            "investment_10pct_increase": ((benefits - investment * 1.1) / (investment * 1.1) * 100),
            "benefits_10pct_decrease": ((benefits * 0.9 - investment) / investment * 100),
            "timeline_delay_6months": base_roi * 0.9,  # Simplified time impact
        }

        return {
            "base_case_roi": round(base_roi, 2),
            "scenario_analysis": scenario_rois,
            "sensitivity_variables": {k: round(v, 2) for k, v in sensitivity_vars.items()},
            "roi_range": {
                "minimum": round(min(scenario_rois.values()), 2),
                "maximum": round(max(scenario_rois.values()), 2)
            }
        }

    def _categorize_roi_performance(self, actual_roi: float, benchmark_roi: float) -> str:
        """Categorize ROI performance"""

        if actual_roi >= benchmark_roi * 1.5:
            return "exceptional"
        elif actual_roi >= benchmark_roi * 1.2:
            return "strong"
        elif actual_roi >= benchmark_roi:
            return "above_average"
        elif actual_roi >= benchmark_roi * 0.8:
            return "average"
        else:
            return "below_average"

class SynergyManager:
    """Main synergy management orchestrator"""

    def __init__(self):
        self.synergy_identification = SynergyIdentificationEngine()
        self.value_tracker = ValueTracker()
        self.roi_analyzer = ROIAnalyzer()
        self.synergy_portfolio = defaultdict(dict)

    async def initiate_synergy_management(self, integration_id: str, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate comprehensive synergy management"""

        # Identify synergy opportunities
        synergies = self.synergy_identification.identify_synergy_opportunities(
            deal_data=deal_data,
            target_data=deal_data.get("target_company_data", {}),
            acquirer_data=deal_data.get("acquirer_company_data", {})
        )

        # Quantify synergy values
        quantified_synergies = []
        for synergy in synergies:
            quantification = self.synergy_identification.quantify_synergy_value(
                synergy, deal_data.get("market_data", {})
            )
            quantified_synergies.append({
                "synergy": synergy.__dict__,
                "quantification": quantification
            })

        # Store in portfolio
        self.synergy_portfolio[integration_id] = {
            "synergies": synergies,
            "quantified_synergies": quantified_synergies,
            "initiated_date": datetime.now()
        }

        # Generate initial metrics
        initial_metrics = self.value_tracker.calculate_portfolio_metrics(
            integration_id=integration_id,
            synergies=synergies,
            period_start=datetime.now(),
            period_end=datetime.now() + timedelta(days=30)
        )

        return {
            "integration_id": integration_id,
            "synergies_identified": len(synergies),
            "total_synergy_value": sum(s.estimated_value for s in synergies),
            "high_confidence_synergies": len([s for s in synergies if s.confidence_level >= 0.8]),
            "synergy_breakdown": {
                synergy_type.value: len([s for s in synergies if s.synergy_type == synergy_type])
                for synergy_type in SynergyType
            },
            "quantified_synergies": quantified_synergies,
            "initial_metrics": initial_metrics.__dict__,
            "next_steps": [
                "Review and approve synergy opportunities",
                "Assign synergy owners and teams",
                "Develop detailed realization plans",
                "Set up tracking and monitoring"
            ]
        }

    async def get_synergy_dashboard(self, integration_id: str) -> Dict[str, Any]:
        """Get comprehensive synergy management dashboard"""

        if integration_id not in self.synergy_portfolio:
            raise ValueError(f"Integration {integration_id} not found")

        portfolio_data = self.synergy_portfolio[integration_id]
        synergies = portfolio_data["synergies"]

        # Calculate current metrics
        current_metrics = self.value_tracker.calculate_portfolio_metrics(
            integration_id=integration_id,
            synergies=synergies,
            period_start=datetime.now() - timedelta(days=90),
            period_end=datetime.now()
        )

        # Calculate ROI analysis
        roi_analysis = self.roi_analyzer.calculate_integration_roi(
            integration_data={
                "total_integration_cost": current_metrics.total_synergies_identified * 0.15,
                "integration_period_months": 24,
                "industry": "technology"
            },
            synergy_metrics=current_metrics
        )

        # Generate insights and recommendations
        insights = self._generate_synergy_insights(synergies, current_metrics)

        dashboard = {
            "integration_id": integration_id,
            "dashboard_timestamp": datetime.now().isoformat(),
            "portfolio_summary": {
                "total_synergies": len(synergies),
                "total_identified_value": current_metrics.total_synergies_identified,
                "total_realized_value": current_metrics.total_synergies_realized,
                "realization_rate": current_metrics.realization_rate,
                "npv": current_metrics.net_present_value
            },
            "performance_metrics": current_metrics.__dict__,
            "roi_analysis": roi_analysis,
            "synergy_status_breakdown": self._get_synergy_status_breakdown(synergies),
            "value_realization_trend": self._get_value_realization_trend(integration_id, synergies),
            "insights_and_recommendations": insights
        }

        return dashboard

    def _generate_synergy_insights(self, synergies: List[SynergyOpportunity],
                                 metrics: ValueCreationMetrics) -> Dict[str, Any]:
        """Generate AI-powered insights and recommendations"""

        insights = {
            "key_insights": [],
            "risks_and_opportunities": [],
            "recommendations": []
        }

        # Performance insights
        if metrics.realization_rate >= 0.8:
            insights["key_insights"].append("Synergy realization is exceeding expectations")
        elif metrics.realization_rate >= 0.6:
            insights["key_insights"].append("Synergy realization is on track")
        else:
            insights["key_insights"].append("Synergy realization is below target")

        # Risk identification
        high_risk_synergies = [s for s in synergies if len(s.risks) > 3]
        if high_risk_synergies:
            insights["risks_and_opportunities"].append(
                f"{len(high_risk_synergies)} synergies have high risk profiles requiring attention"
            )

        # Opportunity identification
        high_value_synergies = [s for s in synergies if s.estimated_value > 10_000_000]
        if high_value_synergies:
            insights["risks_and_opportunities"].append(
                f"{len(high_value_synergies)} high-value synergies represent significant upside potential"
            )

        # Recommendations
        if metrics.realization_rate < 0.7:
            insights["recommendations"].append("Accelerate synergy realization through dedicated task forces")

        insights["recommendations"].extend([
            "Implement monthly synergy tracking reviews",
            "Establish synergy-based incentive programs",
            "Create cross-functional synergy realization teams"
        ])

        return insights

    def _get_synergy_status_breakdown(self, synergies: List[SynergyOpportunity]) -> Dict[str, int]:
        """Get breakdown of synergy statuses"""

        status_counts = defaultdict(int)
        for synergy in synergies:
            status_counts[synergy.status.value] += 1

        return dict(status_counts)

    def _get_value_realization_trend(self, integration_id: str,
                                   synergies: List[SynergyOpportunity]) -> Dict[str, float]:
        """Get value realization trend over time"""

        # Simplified trend data (would use actual tracking data)
        trend_data = {}
        start_date = datetime.now() - timedelta(days=180)

        for i in range(6):  # 6 months of data
            month_date = start_date + timedelta(days=30 * i)
            month_key = month_date.strftime("%Y-%m")

            # Simulate progressive value realization
            progress_factor = (i + 1) / 6
            total_value = sum(s.estimated_value for s in synergies)
            realized_value = total_value * progress_factor * 0.7  # 70% realization curve

            trend_data[month_key] = round(realized_value, 2)

        return trend_data

# Service instance management
_synergy_manager_instance = None

def get_synergy_manager() -> SynergyManager:
    """Get singleton synergy manager instance"""
    global _synergy_manager_instance
    if _synergy_manager_instance is None:
        _synergy_manager_instance = SynergyManager()
    return _synergy_manager_instance