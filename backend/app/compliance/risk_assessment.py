"""
Risk Assessment Framework - Sprint 15
Advanced risk modeling, assessment, monitoring, and mitigation for M&A transactions
"""

from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import json
import uuid
import statistics
from collections import defaultdict, deque

class RiskCategory(Enum):
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    LEGAL = "legal"
    REGULATORY = "regulatory"
    TECHNOLOGY = "technology"
    MARKET = "market"
    REPUTATION = "reputation"
    CYBER_SECURITY = "cyber_security"
    ESG = "environmental_social_governance"

class RiskLevel(Enum):
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    CRITICAL = 6

class RiskStatus(Enum):
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    TRANSFERRED = "transferred"
    AVOIDED = "avoided"
    MONITORING = "monitoring"

class MitigationStrategy(Enum):
    ACCEPT = "accept"
    AVOID = "avoid"
    TRANSFER = "transfer"
    MITIGATE = "mitigate"
    MONITOR = "monitor"

class RiskImpactType(Enum):
    FINANCIAL_LOSS = "financial_loss"
    OPERATIONAL_DISRUPTION = "operational_disruption"
    REGULATORY_PENALTY = "regulatory_penalty"
    REPUTATION_DAMAGE = "reputation_damage"
    STRATEGIC_FAILURE = "strategic_failure"
    COMPLIANCE_VIOLATION = "compliance_violation"

@dataclass
class RiskFactor:
    """Individual risk factor"""
    factor_id: str
    name: str
    description: str
    category: RiskCategory
    weight: float  # 0.0 to 1.0
    measurement_method: str
    data_sources: List[str] = field(default_factory=list)
    threshold_values: Dict[str, float] = field(default_factory=dict)

@dataclass
class RiskScenario:
    """Risk scenario definition"""
    scenario_id: str
    name: str
    description: str
    category: RiskCategory
    probability: float  # 0.0 to 1.0
    impact_score: float  # 0.0 to 100.0
    factors: List[RiskFactor] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    time_horizon: str = "12_months"

@dataclass
class RiskMetric:
    """Risk measurement metric"""
    metric_id: str
    name: str
    description: str
    category: RiskCategory
    calculation_method: str
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    unit: str = ""
    frequency: str = "daily"

@dataclass
class RiskAssessmentResult:
    """Risk assessment result"""
    assessment_id: str
    entity_id: str
    entity_type: str
    assessment_date: datetime
    risk_category: RiskCategory
    risk_level: RiskLevel
    risk_score: float  # 0.0 to 100.0
    probability: float
    impact: float
    factors_evaluated: List[str] = field(default_factory=list)
    scenarios_analyzed: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_review_date: Optional[datetime] = None
    assessor: str = ""

@dataclass
class RiskMitigationPlan:
    """Risk mitigation plan"""
    plan_id: str
    risk_assessment_id: str
    strategy: MitigationStrategy
    actions: List[str] = field(default_factory=list)
    responsible_party: str = ""
    target_completion: Optional[datetime] = None
    estimated_cost: Optional[float] = None
    expected_impact_reduction: float = 0.0
    status: str = "planned"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class RiskEvent:
    """Risk event occurrence"""
    event_id: str
    risk_category: RiskCategory
    severity: RiskLevel
    description: str
    occurred_at: datetime
    entity_id: str
    entity_type: str
    impact_realized: float = 0.0
    impact_type: RiskImpactType = RiskImpactType.FINANCIAL_LOSS
    mitigation_actions_taken: List[str] = field(default_factory=list)
    lessons_learned: str = ""
    status: str = "occurred"

@dataclass
class RiskModel:
    """Risk assessment model"""
    model_id: str
    name: str
    description: str
    category: RiskCategory
    factors: List[RiskFactor] = field(default_factory=list)
    scenarios: List[RiskScenario] = field(default_factory=list)
    metrics: List[RiskMetric] = field(default_factory=list)
    calculation_algorithm: str = "weighted_average"
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

class RiskCalculator:
    """Calculates risk scores and levels"""

    def __init__(self):
        self.calculation_methods = {}
        self._register_default_methods()

    def calculate_risk_score(self, model: RiskModel, entity_data: Dict[str, Any]) -> float:
        """Calculate overall risk score using specified model"""
        method = self.calculation_methods.get(
            model.calculation_algorithm,
            self.calculation_methods["weighted_average"]
        )

        return method(model, entity_data)

    def calculate_probability(self, scenarios: List[RiskScenario],
                            entity_data: Dict[str, Any]) -> float:
        """Calculate probability based on scenarios"""
        if not scenarios:
            return 0.0

        total_probability = 0.0
        for scenario in scenarios:
            scenario_probability = self._evaluate_scenario_probability(scenario, entity_data)
            total_probability += scenario_probability

        return min(1.0, total_probability / len(scenarios))

    def calculate_impact(self, scenarios: List[RiskScenario],
                        entity_data: Dict[str, Any]) -> float:
        """Calculate potential impact"""
        if not scenarios:
            return 0.0

        impacts = []
        for scenario in scenarios:
            scenario_impact = self._evaluate_scenario_impact(scenario, entity_data)
            impacts.append(scenario_impact)

        return statistics.mean(impacts) if impacts else 0.0

    def determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from score"""
        if risk_score >= 90:
            return RiskLevel.CRITICAL
        elif risk_score >= 75:
            return RiskLevel.VERY_HIGH
        elif risk_score >= 60:
            return RiskLevel.HIGH
        elif risk_score >= 40:
            return RiskLevel.MEDIUM
        elif risk_score >= 20:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW

    def _register_default_methods(self):
        """Register default calculation methods"""

        def weighted_average_method(model: RiskModel, entity_data: Dict[str, Any]) -> float:
            total_score = 0.0
            total_weight = 0.0

            for factor in model.factors:
                factor_value = self._evaluate_factor(factor, entity_data)
                total_score += factor_value * factor.weight
                total_weight += factor.weight

            return (total_score / total_weight) * 100 if total_weight > 0 else 0.0

        def monte_carlo_method(model: RiskModel, entity_data: Dict[str, Any]) -> float:
            # Simplified Monte Carlo simulation
            simulations = 1000
            results = []

            for _ in range(simulations):
                score = 0.0
                for factor in model.factors:
                    # Add randomness to factor evaluation
                    base_value = self._evaluate_factor(factor, entity_data)
                    random_factor = 0.8 + (0.4 * hash(str(entity_data)) % 100 / 100)
                    score += base_value * factor.weight * random_factor

                results.append(score)

            return statistics.mean(results) * 100

        self.calculation_methods = {
            "weighted_average": weighted_average_method,
            "monte_carlo": monte_carlo_method
        }

    def _evaluate_factor(self, factor: RiskFactor, entity_data: Dict[str, Any]) -> float:
        """Evaluate individual risk factor"""
        # Simplified factor evaluation
        factor_data = entity_data.get(factor.name.lower().replace(" ", "_"), 0)

        if isinstance(factor_data, (int, float)):
            # Normalize to 0-1 scale
            max_threshold = factor.threshold_values.get("max", 100)
            return min(1.0, factor_data / max_threshold)

        return 0.5  # Default moderate risk

    def _evaluate_scenario_probability(self, scenario: RiskScenario,
                                     entity_data: Dict[str, Any]) -> float:
        """Evaluate scenario probability"""
        # Base probability from scenario definition
        base_probability = scenario.probability

        # Adjust based on factor values
        adjustment = 0.0
        for factor in scenario.factors:
            factor_value = self._evaluate_factor(factor, entity_data)
            adjustment += (factor_value - 0.5) * 0.1  # Small adjustment per factor

        return max(0.0, min(1.0, base_probability + adjustment))

    def _evaluate_scenario_impact(self, scenario: RiskScenario,
                                entity_data: Dict[str, Any]) -> float:
        """Evaluate scenario impact"""
        return scenario.impact_score

class RiskEngine:
    """Core risk assessment and management engine"""

    def __init__(self):
        self.risk_models = {}
        self.risk_calculator = RiskCalculator()
        self.assessments = {}
        self.mitigation_plans = {}
        self.risk_events = {}
        self._initialize_default_models()

    def create_risk_model(self, name: str, description: str,
                         category: RiskCategory) -> str:
        """Create a new risk model"""
        model_id = f"model_{uuid.uuid4().hex[:8]}"

        model = RiskModel(
            model_id=model_id,
            name=name,
            description=description,
            category=category
        )

        self.risk_models[model_id] = model
        return model_id

    def add_risk_factor(self, model_id: str, name: str, description: str,
                       category: RiskCategory, weight: float) -> bool:
        """Add risk factor to model"""
        if model_id not in self.risk_models:
            return False

        factor_id = f"factor_{uuid.uuid4().hex[:8]}"
        factor = RiskFactor(
            factor_id=factor_id,
            name=name,
            description=description,
            category=category,
            weight=weight,
            measurement_method="direct_observation"
        )

        self.risk_models[model_id].factors.append(factor)
        return True

    def add_risk_scenario(self, model_id: str, name: str, description: str,
                         category: RiskCategory, probability: float,
                         impact_score: float) -> bool:
        """Add risk scenario to model"""
        if model_id not in self.risk_models:
            return False

        scenario_id = f"scenario_{uuid.uuid4().hex[:8]}"
        scenario = RiskScenario(
            scenario_id=scenario_id,
            name=name,
            description=description,
            category=category,
            probability=probability,
            impact_score=impact_score
        )

        self.risk_models[model_id].scenarios.append(scenario)
        return True

    async def assess_risk(self, entity_id: str, entity_type: str,
                         entity_data: Dict[str, Any],
                         model_id: str) -> str:
        """Perform risk assessment"""
        if model_id not in self.risk_models:
            raise ValueError(f"Risk model {model_id} not found")

        assessment_id = f"assessment_{uuid.uuid4().hex[:8]}"
        model = self.risk_models[model_id]

        # Calculate risk components
        risk_score = self.risk_calculator.calculate_risk_score(model, entity_data)
        probability = self.risk_calculator.calculate_probability(model.scenarios, entity_data)
        impact = self.risk_calculator.calculate_impact(model.scenarios, entity_data)
        risk_level = self.risk_calculator.determine_risk_level(risk_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, model.category)

        # Create assessment result
        assessment = RiskAssessmentResult(
            assessment_id=assessment_id,
            entity_id=entity_id,
            entity_type=entity_type,
            assessment_date=datetime.now(),
            risk_category=model.category,
            risk_level=risk_level,
            risk_score=risk_score,
            probability=probability,
            impact=impact,
            factors_evaluated=[f.factor_id for f in model.factors],
            scenarios_analyzed=[s.scenario_id for s in model.scenarios],
            recommendations=recommendations,
            next_review_date=datetime.now() + timedelta(days=30)
        )

        self.assessments[assessment_id] = assessment
        return assessment_id

    def create_mitigation_plan(self, assessment_id: str, strategy: MitigationStrategy,
                              actions: List[str], responsible_party: str) -> str:
        """Create risk mitigation plan"""
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        plan = RiskMitigationPlan(
            plan_id=plan_id,
            risk_assessment_id=assessment_id,
            strategy=strategy,
            actions=actions,
            responsible_party=responsible_party,
            target_completion=datetime.now() + timedelta(days=30)
        )

        self.mitigation_plans[plan_id] = plan
        return plan_id

    def record_risk_event(self, category: RiskCategory, severity: RiskLevel,
                         description: str, entity_id: str, entity_type: str,
                         impact_realized: float = 0.0) -> str:
        """Record a risk event occurrence"""
        event_id = f"event_{uuid.uuid4().hex[:8]}"

        event = RiskEvent(
            event_id=event_id,
            risk_category=category,
            severity=severity,
            description=description,
            occurred_at=datetime.now(),
            entity_id=entity_id,
            entity_type=entity_type,
            impact_realized=impact_realized
        )

        self.risk_events[event_id] = event
        return event_id

    def _generate_recommendations(self, risk_level: RiskLevel,
                                category: RiskCategory) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []

        if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL]:
            recommendations.extend([
                "Immediate attention required",
                "Develop comprehensive mitigation plan",
                "Increase monitoring frequency",
                "Consider executive escalation"
            ])

            if category == RiskCategory.FINANCIAL:
                recommendations.extend([
                    "Review financial controls",
                    "Assess cash flow impact",
                    "Consider hedging strategies"
                ])
            elif category == RiskCategory.CYBER_SECURITY:
                recommendations.extend([
                    "Enhance security controls",
                    "Conduct security audit",
                    "Review incident response plan"
                ])

        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Monitor closely",
                "Develop contingency plans",
                "Regular status reviews"
            ])

        else:
            recommendations.extend([
                "Continue routine monitoring",
                "Periodic risk review"
            ])

        return recommendations

    def _initialize_default_models(self):
        """Initialize default risk models"""

        # Financial Risk Model
        financial_model_id = self.create_risk_model(
            "Financial Risk Model",
            "Comprehensive financial risk assessment",
            RiskCategory.FINANCIAL
        )

        self.add_risk_factor(
            financial_model_id, "Debt to Equity Ratio",
            "Company leverage ratio", RiskCategory.FINANCIAL, 0.3
        )
        self.add_risk_factor(
            financial_model_id, "Cash Flow Volatility",
            "Variability in cash flows", RiskCategory.FINANCIAL, 0.25
        )
        self.add_risk_factor(
            financial_model_id, "Market Exposure",
            "Exposure to market fluctuations", RiskCategory.FINANCIAL, 0.2
        )

        self.add_risk_scenario(
            financial_model_id, "Market Downturn",
            "Significant market decline", RiskCategory.FINANCIAL, 0.3, 75.0
        )

        # Operational Risk Model
        operational_model_id = self.create_risk_model(
            "Operational Risk Model",
            "Operational and process risks",
            RiskCategory.OPERATIONAL
        )

        self.add_risk_factor(
            operational_model_id, "Process Maturity",
            "Maturity of business processes", RiskCategory.OPERATIONAL, 0.4
        )
        self.add_risk_factor(
            operational_model_id, "Technology Dependence",
            "Reliance on technology systems", RiskCategory.OPERATIONAL, 0.3
        )

    def get_risk_assessment(self, assessment_id: str) -> Optional[RiskAssessmentResult]:
        """Get risk assessment by ID"""
        return self.assessments.get(assessment_id)

    def get_risk_models(self) -> List[RiskModel]:
        """Get all risk models"""
        return list(self.risk_models.values())

    def get_mitigation_plans(self, assessment_id: Optional[str] = None) -> List[RiskMitigationPlan]:
        """Get mitigation plans"""
        plans = list(self.mitigation_plans.values())
        if assessment_id:
            plans = [p for p in plans if p.risk_assessment_id == assessment_id]
        return plans

    def get_risk_events(self, entity_id: Optional[str] = None,
                       category: Optional[RiskCategory] = None) -> List[RiskEvent]:
        """Get risk events with optional filtering"""
        events = list(self.risk_events.values())

        if entity_id:
            events = [e for e in events if e.entity_id == entity_id]

        if category:
            events = [e for e in events if e.risk_category == category]

        return events

class RiskAssessment:
    """Main risk assessment coordination class"""

    def __init__(self):
        self.risk_engine = RiskEngine()
        self.risk_monitoring_active = False
        self.monitoring_queue = deque()
        self.risk_stats = {
            "assessments_completed": 0,
            "high_risk_entities": 0,
            "mitigation_plans_active": 0,
            "risk_events_recorded": 0
        }

    async def perform_risk_assessment(self, entity_id: str, entity_type: str,
                                    entity_data: Dict[str, Any],
                                    model_ids: List[str]) -> List[str]:
        """Perform comprehensive risk assessment"""
        assessment_ids = []

        for model_id in model_ids:
            try:
                assessment_id = await self.risk_engine.assess_risk(
                    entity_id, entity_type, entity_data, model_id
                )
                assessment_ids.append(assessment_id)
                self.risk_stats["assessments_completed"] += 1

                # Check if high risk
                assessment = self.risk_engine.get_risk_assessment(assessment_id)
                if assessment and assessment.risk_level.value >= RiskLevel.HIGH.value:
                    self.risk_stats["high_risk_entities"] += 1

            except Exception as e:
                print(f"Error in risk assessment for model {model_id}: {e}")

        return assessment_ids

    async def create_comprehensive_mitigation_plan(self, assessment_ids: List[str],
                                                 responsible_party: str) -> List[str]:
        """Create mitigation plans for multiple assessments"""
        plan_ids = []

        for assessment_id in assessment_ids:
            assessment = self.risk_engine.get_risk_assessment(assessment_id)
            if not assessment:
                continue

            # Determine strategy based on risk level
            if assessment.risk_level.value >= RiskLevel.HIGH.value:
                strategy = MitigationStrategy.MITIGATE
                actions = [
                    "Immediate review and action required",
                    "Implement enhanced controls",
                    "Increase monitoring frequency"
                ]
            elif assessment.risk_level == RiskLevel.MEDIUM:
                strategy = MitigationStrategy.MONITOR
                actions = [
                    "Regular monitoring",
                    "Develop contingency plans"
                ]
            else:
                strategy = MitigationStrategy.ACCEPT
                actions = ["Continue routine monitoring"]

            plan_id = self.risk_engine.create_mitigation_plan(
                assessment_id, strategy, actions, responsible_party
            )
            plan_ids.append(plan_id)
            self.risk_stats["mitigation_plans_active"] += 1

        return plan_ids

    async def start_risk_monitoring(self):
        """Start continuous risk monitoring"""
        self.risk_monitoring_active = True

        while self.risk_monitoring_active:
            await self._process_risk_monitoring()
            await asyncio.sleep(300)  # Check every 5 minutes

    async def _process_risk_monitoring(self):
        """Process risk monitoring queue"""
        while self.monitoring_queue:
            monitoring_task = self.monitoring_queue.popleft()
            await self._monitor_entity_risk(monitoring_task)

    async def _monitor_entity_risk(self, task: Dict[str, Any]):
        """Monitor individual entity for risk changes"""
        try:
            entity_id = task["entity_id"]
            entity_type = task["entity_type"]
            entity_data = task["entity_data"]
            model_ids = task["model_ids"]

            # Perform fresh assessment
            new_assessments = await self.perform_risk_assessment(
                entity_id, entity_type, entity_data, model_ids
            )

            # Compare with previous assessments and trigger alerts if needed
            # Implementation would compare risk levels and trigger notifications

        except Exception as e:
            print(f"Error monitoring entity risk: {e}")

    def queue_risk_monitoring(self, entity_id: str, entity_type: str,
                            entity_data: Dict[str, Any], model_ids: List[str]):
        """Queue entity for risk monitoring"""
        self.monitoring_queue.append({
            "entity_id": entity_id,
            "entity_type": entity_type,
            "entity_data": entity_data,
            "model_ids": model_ids,
            "queued_at": datetime.now()
        })

    def stop_risk_monitoring(self):
        """Stop risk monitoring"""
        self.risk_monitoring_active = False

    def get_risk_dashboard_data(self) -> Dict[str, Any]:
        """Get risk dashboard data"""
        all_assessments = list(self.risk_engine.assessments.values())

        risk_distribution = defaultdict(int)
        for assessment in all_assessments:
            risk_distribution[assessment.risk_level.name] += 1

        category_distribution = defaultdict(int)
        for assessment in all_assessments:
            category_distribution[assessment.risk_category.name] += 1

        return {
            "total_assessments": len(all_assessments),
            "risk_level_distribution": dict(risk_distribution),
            "risk_category_distribution": dict(category_distribution),
            "high_risk_count": len([a for a in all_assessments
                                  if a.risk_level.value >= RiskLevel.HIGH.value]),
            "recent_assessments": sorted(all_assessments,
                                       key=lambda x: x.assessment_date, reverse=True)[:10]
        }

    def get_risk_stats(self) -> Dict[str, Any]:
        """Get comprehensive risk statistics"""
        return {
            **self.risk_stats,
            "monitoring_queue_size": len(self.monitoring_queue),
            "total_models": len(self.risk_engine.risk_models),
            "monitoring_active": self.risk_monitoring_active
        }

# Singleton instance
_risk_assessment_instance: Optional[RiskAssessment] = None

def get_risk_assessment() -> RiskAssessment:
    """Get the singleton Risk Assessment instance"""
    global _risk_assessment_instance
    if _risk_assessment_instance is None:
        _risk_assessment_instance = RiskAssessment()
    return _risk_assessment_instance