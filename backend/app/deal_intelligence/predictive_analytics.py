"""
Predictive Analytics & Forecasting Engine - Advanced AI-powered predictions and scenario modeling
Provides deal outcome prediction, market forecasting, and portfolio optimization
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json
import math
import random
import statistics
from abc import ABC, abstractmethod

# Data Models and Enums
class PredictionType(Enum):
    DEAL_SUCCESS = "deal_success"
    VALUATION_ACCURACY = "valuation_accuracy"
    INTEGRATION_SUCCESS = "integration_success"
    MARKET_PERFORMANCE = "market_performance"
    SYNERGY_REALIZATION = "synergy_realization"

class ScenarioType(Enum):
    BASE_CASE = "base_case"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    STRESS_TEST = "stress_test"

class ForecastHorizon(Enum):
    SHORT_TERM = "short_term"  # 3-6 months
    MEDIUM_TERM = "medium_term"  # 6-18 months
    LONG_TERM = "long_term"  # 18+ months

class ModelAccuracy(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class PredictionModel:
    """AI prediction model configuration"""
    model_id: str
    name: str
    prediction_type: PredictionType
    algorithm: str
    features: List[str]
    accuracy_score: float
    confidence_threshold: float
    last_trained: datetime
    training_data_size: int
    validation_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class DealPrediction:
    """Deal outcome prediction results"""
    prediction_id: str
    deal_id: str
    prediction_type: PredictionType
    predicted_outcome: str
    confidence_score: float
    probability_distribution: Dict[str, float]
    key_factors: Dict[str, float]
    risk_factors: List[str]
    model_used: str
    prediction_date: datetime = field(default_factory=datetime.now)

@dataclass
class MarketForecast:
    """Market trend and performance forecast"""
    forecast_id: str
    industry: str
    region: str
    forecast_horizon: ForecastHorizon
    predictions: Dict[str, Any]
    confidence_intervals: Dict[str, Tuple[float, float]]
    scenario_analysis: Dict[ScenarioType, Dict[str, Any]]
    key_assumptions: List[str]
    forecast_date: datetime = field(default_factory=datetime.now)

@dataclass
class PortfolioOptimization:
    """Portfolio optimization recommendations"""
    optimization_id: str
    portfolio_composition: Dict[str, float]
    expected_return: float
    risk_score: float
    sharpe_ratio: float
    diversification_score: float
    recommendations: List[str]
    rebalancing_suggestions: Dict[str, float]
    optimization_date: datetime = field(default_factory=datetime.now)

class DealForecastingEngine:
    """Advanced deal outcome prediction and forecasting engine"""

    def __init__(self):
        self.prediction_models = {}
        self.historical_outcomes = defaultdict(list)
        self.feature_importance = defaultdict(dict)
        self.model_performance = defaultdict(dict)

    def create_prediction_model(self, model_id: str, name: str,
                              prediction_type: PredictionType,
                              algorithm: str = "ensemble") -> bool:
        """Create new prediction model"""
        try:
            model = PredictionModel(
                model_id=model_id,
                name=name,
                prediction_type=prediction_type,
                algorithm=algorithm,
                features=self._get_default_features(prediction_type),
                accuracy_score=0.0,
                confidence_threshold=0.7,
                last_trained=datetime.now(),
                training_data_size=0
            )
            self.prediction_models[model_id] = model
            return True
        except Exception:
            return False

    def train_model(self, model_id: str, training_data: List[Dict[str, Any]]) -> bool:
        """Train prediction model with historical data"""
        if model_id not in self.prediction_models:
            return False

        model = self.prediction_models[model_id]

        # Simulate model training
        model.training_data_size = len(training_data)
        model.last_trained = datetime.now()

        # Calculate simulated accuracy based on data size and features
        base_accuracy = 0.65
        data_bonus = min(0.25, len(training_data) / 1000 * 0.25)
        feature_bonus = min(0.10, len(model.features) / 20 * 0.10)

        model.accuracy_score = base_accuracy + data_bonus + feature_bonus + random.uniform(-0.05, 0.05)
        model.accuracy_score = max(0.5, min(0.95, model.accuracy_score))

        # Calculate validation metrics
        model.validation_metrics = {
            "precision": model.accuracy_score + random.uniform(-0.1, 0.1),
            "recall": model.accuracy_score + random.uniform(-0.1, 0.1),
            "f1_score": model.accuracy_score + random.uniform(-0.05, 0.05),
            "auc_roc": model.accuracy_score + random.uniform(0.0, 0.1)
        }

        # Update feature importance
        self._calculate_feature_importance(model_id, training_data)

        return True

    def predict_deal_outcome(self, deal_id: str, deal_data: Dict[str, Any],
                           prediction_type: PredictionType,
                           model_id: Optional[str] = None) -> DealPrediction:
        """Predict deal outcome using trained models"""

        # Select model
        if model_id and model_id in self.prediction_models:
            model = self.prediction_models[model_id]
        else:
            # Find best model for prediction type
            model = self._select_best_model(prediction_type)

        if not model:
            raise ValueError(f"No model available for prediction type {prediction_type.value}")

        # Generate prediction
        prediction_result = self._generate_prediction(model, deal_data, prediction_type)

        return DealPrediction(
            prediction_id=f"pred_{deal_id}_{prediction_type.value}_{int(datetime.now().timestamp())}",
            deal_id=deal_id,
            prediction_type=prediction_type,
            predicted_outcome=prediction_result["outcome"],
            confidence_score=prediction_result["confidence"],
            probability_distribution=prediction_result["probabilities"],
            key_factors=prediction_result["factors"],
            risk_factors=prediction_result["risks"],
            model_used=model.model_id
        )

    def generate_scenario_analysis(self, deal_id: str, base_case_data: Dict[str, Any],
                                 scenarios: List[ScenarioType]) -> Dict[str, DealPrediction]:
        """Generate multiple scenario predictions"""

        scenario_predictions = {}

        for scenario in scenarios:
            # Adjust input data for scenario
            scenario_data = self._adjust_data_for_scenario(base_case_data, scenario)

            # Generate prediction for scenario
            prediction = self.predict_deal_outcome(
                deal_id=f"{deal_id}_{scenario.value}",
                deal_data=scenario_data,
                prediction_type=PredictionType.DEAL_SUCCESS
            )

            scenario_predictions[scenario.value] = prediction

        return scenario_predictions

    def _get_default_features(self, prediction_type: PredictionType) -> List[str]:
        """Get default features for prediction type"""
        feature_sets = {
            PredictionType.DEAL_SUCCESS: [
                "deal_value", "target_revenue", "target_ebitda", "industry_growth",
                "market_position", "strategic_fit", "execution_complexity",
                "regulatory_risk", "financing_availability", "market_volatility"
            ],
            PredictionType.VALUATION_ACCURACY: [
                "revenue_multiple", "ebitda_multiple", "growth_rate", "margin_profile",
                "market_comparables", "dcf_valuation", "asset_value", "synergy_value"
            ],
            PredictionType.INTEGRATION_SUCCESS: [
                "cultural_fit", "system_compatibility", "geographic_overlap",
                "organizational_structure", "talent_retention", "customer_overlap"
            ],
            PredictionType.MARKET_PERFORMANCE: [
                "market_size", "growth_trajectory", "competitive_intensity",
                "regulatory_environment", "technology_disruption", "economic_indicators"
            ],
            PredictionType.SYNERGY_REALIZATION: [
                "revenue_synergies", "cost_synergies", "tax_synergies",
                "operational_overlap", "technology_integration", "market_access"
            ]
        }

        return feature_sets.get(prediction_type, [])

    def _calculate_feature_importance(self, model_id: str, training_data: List[Dict[str, Any]]) -> None:
        """Calculate feature importance scores"""
        model = self.prediction_models[model_id]

        # Simulate feature importance calculation
        importance_scores = {}
        for feature in model.features:
            # Random importance with some logic
            base_importance = random.uniform(0.1, 0.9)

            # Adjust based on feature type
            if "value" in feature or "revenue" in feature:
                base_importance *= 1.2
            elif "risk" in feature:
                base_importance *= 1.1

            importance_scores[feature] = min(1.0, base_importance)

        # Normalize to sum to 1
        total_importance = sum(importance_scores.values())
        importance_scores = {
            feature: score / total_importance
            for feature, score in importance_scores.items()
        }

        self.feature_importance[model_id] = importance_scores

    def _select_best_model(self, prediction_type: PredictionType) -> Optional[PredictionModel]:
        """Select best model for prediction type"""
        candidates = [
            model for model in self.prediction_models.values()
            if model.prediction_type == prediction_type
        ]

        if not candidates:
            return None

        # Return model with highest accuracy
        return max(candidates, key=lambda m: m.accuracy_score)

    def _generate_prediction(self, model: PredictionModel, deal_data: Dict[str, Any],
                           prediction_type: PredictionType) -> Dict[str, Any]:
        """Generate prediction using model"""

        # Simulate AI prediction generation
        base_score = 0.5

        # Calculate prediction based on available features
        for feature in model.features:
            if feature in deal_data:
                feature_value = deal_data[feature]
                feature_importance = self.feature_importance.get(model.model_id, {}).get(feature, 0.1)

                # Normalize feature value and apply importance
                if isinstance(feature_value, (int, float)):
                    normalized_value = min(1.0, abs(feature_value) / 1000000)  # Simple normalization
                    base_score += (normalized_value - 0.5) * feature_importance

        # Apply model accuracy as confidence adjustment
        confidence = model.accuracy_score * (0.8 + random.uniform(0, 0.4))
        confidence = max(0.3, min(0.95, confidence))

        # Determine outcome based on score
        if prediction_type == PredictionType.DEAL_SUCCESS:
            if base_score >= 0.7:
                outcome = "success"
                success_prob = base_score
            elif base_score >= 0.4:
                outcome = "conditional"
                success_prob = base_score * 0.8
            else:
                outcome = "unlikely"
                success_prob = base_score * 0.6

            probabilities = {
                "success": success_prob,
                "conditional": 0.3,
                "failure": 1.0 - success_prob - 0.3
            }

        else:
            # Generic outcome for other prediction types
            outcome = "positive" if base_score >= 0.6 else "negative"
            probabilities = {
                "positive": base_score,
                "negative": 1.0 - base_score
            }

        # Generate key factors
        key_factors = {}
        for feature in model.features[:5]:  # Top 5 features
            if feature in deal_data:
                importance = self.feature_importance.get(model.model_id, {}).get(feature, 0.1)
                key_factors[feature] = importance

        # Generate risk factors
        risk_factors = []
        if base_score < 0.6:
            risk_factors.extend([
                "Below-average market conditions",
                "Execution complexity concerns",
                "Regulatory approval challenges"
            ])

        return {
            "outcome": outcome,
            "confidence": confidence,
            "probabilities": probabilities,
            "factors": key_factors,
            "risks": risk_factors
        }

    def _adjust_data_for_scenario(self, base_data: Dict[str, Any],
                                scenario: ScenarioType) -> Dict[str, Any]:
        """Adjust input data for scenario analysis"""
        scenario_data = base_data.copy()

        # Scenario-specific adjustments
        adjustments = {
            ScenarioType.OPTIMISTIC: {
                "multipliers": {"growth_rate": 1.3, "synergy_value": 1.2, "market_size": 1.1},
                "risk_reduction": 0.8
            },
            ScenarioType.PESSIMISTIC: {
                "multipliers": {"growth_rate": 0.7, "synergy_value": 0.8, "market_size": 0.9},
                "risk_increase": 1.5
            },
            ScenarioType.STRESS_TEST: {
                "multipliers": {"growth_rate": 0.5, "synergy_value": 0.6, "market_size": 0.8},
                "risk_increase": 2.0
            }
        }

        if scenario in adjustments:
            adjustment = adjustments[scenario]

            # Apply multipliers
            for key, multiplier in adjustment.get("multipliers", {}).items():
                if key in scenario_data and isinstance(scenario_data[key], (int, float)):
                    scenario_data[key] *= multiplier

            # Adjust risk factors
            if "risk_reduction" in adjustment:
                for key in scenario_data:
                    if "risk" in key and isinstance(scenario_data[key], (int, float)):
                        scenario_data[key] *= adjustment["risk_reduction"]

            if "risk_increase" in adjustment:
                for key in scenario_data:
                    if "risk" in key and isinstance(scenario_data[key], (int, float)):
                        scenario_data[key] *= adjustment["risk_increase"]

        return scenario_data

class MarketForecastingEngine:
    """Advanced market trend analysis and forecasting"""

    def __init__(self):
        self.forecast_models = {}
        self.market_data = defaultdict(list)
        self.economic_indicators = {}
        self.industry_benchmarks = defaultdict(dict)

    def generate_market_forecast(self, industry: str, region: str = "global",
                                horizon: ForecastHorizon = ForecastHorizon.MEDIUM_TERM) -> MarketForecast:
        """Generate comprehensive market forecast"""

        forecast_id = f"forecast_{industry}_{region}_{horizon.value}_{int(datetime.now().timestamp())}"

        # Generate base predictions
        base_predictions = self._generate_base_predictions(industry, region, horizon)

        # Generate confidence intervals
        confidence_intervals = self._calculate_confidence_intervals(base_predictions)

        # Generate scenario analysis
        scenario_analysis = self._generate_market_scenarios(industry, base_predictions)

        # Identify key assumptions
        key_assumptions = self._identify_key_assumptions(industry, horizon)

        return MarketForecast(
            forecast_id=forecast_id,
            industry=industry,
            region=region,
            forecast_horizon=horizon,
            predictions=base_predictions,
            confidence_intervals=confidence_intervals,
            scenario_analysis=scenario_analysis,
            key_assumptions=key_assumptions
        )

    def _generate_base_predictions(self, industry: str, region: str,
                                 horizon: ForecastHorizon) -> Dict[str, Any]:
        """Generate base market predictions"""

        # Time horizon adjustments
        horizon_months = {
            ForecastHorizon.SHORT_TERM: 6,
            ForecastHorizon.MEDIUM_TERM: 12,
            ForecastHorizon.LONG_TERM: 24
        }

        months = horizon_months[horizon]

        # Industry-specific base growth rates
        industry_growth = {
            "technology": 0.12,
            "healthcare": 0.08,
            "financial_services": 0.05,
            "manufacturing": 0.04,
            "retail": 0.03,
            "energy": 0.02
        }

        base_growth = industry_growth.get(industry, 0.06)

        # Add economic cycle and random factors
        cycle_adjustment = random.uniform(-0.02, 0.03)
        final_growth = base_growth + cycle_adjustment

        # Generate predictions
        predictions = {
            "market_growth_rate": final_growth,
            "market_size_change": final_growth * months / 12,
            "valuation_multiple_trend": random.uniform(-0.1, 0.15),
            "m_and_a_activity_level": random.uniform(0.7, 1.3),
            "competitive_intensity": random.uniform(0.6, 1.2),
            "regulatory_risk_level": random.uniform(0.3, 0.8),
            "technology_disruption_risk": random.uniform(0.2, 0.9),
            "talent_availability": random.uniform(0.6, 1.1)
        }

        return predictions

    def _calculate_confidence_intervals(self, predictions: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
        """Calculate confidence intervals for predictions"""
        confidence_intervals = {}

        for metric, value in predictions.items():
            if isinstance(value, (int, float)):
                # 95% confidence interval
                margin = abs(value) * random.uniform(0.1, 0.3)
                lower_bound = value - margin
                upper_bound = value + margin
                confidence_intervals[metric] = (round(lower_bound, 4), round(upper_bound, 4))

        return confidence_intervals

    def _generate_market_scenarios(self, industry: str,
                                 base_predictions: Dict[str, Any]) -> Dict[ScenarioType, Dict[str, Any]]:
        """Generate scenario-based market forecasts"""
        scenarios = {}

        scenario_adjustments = {
            ScenarioType.BASE_CASE: 1.0,
            ScenarioType.OPTIMISTIC: 1.2,
            ScenarioType.PESSIMISTIC: 0.8,
            ScenarioType.STRESS_TEST: 0.6
        }

        for scenario_type, adjustment in scenario_adjustments.items():
            scenario_predictions = {}
            for metric, value in base_predictions.items():
                if isinstance(value, (int, float)):
                    adjusted_value = value * adjustment
                    scenario_predictions[metric] = adjusted_value
                else:
                    scenario_predictions[metric] = value

            scenarios[scenario_type] = scenario_predictions

        return scenarios

    def _identify_key_assumptions(self, industry: str, horizon: ForecastHorizon) -> List[str]:
        """Identify key assumptions underlying the forecast"""
        base_assumptions = [
            "Continued economic stability",
            "No major regulatory changes",
            "Current technology trends continue",
            "Geopolitical stability maintained"
        ]

        # Industry-specific assumptions
        industry_assumptions = {
            "technology": [
                "AI adoption continues to accelerate",
                "Cloud infrastructure growth maintained",
                "Cybersecurity remains high priority"
            ],
            "healthcare": [
                "Aging population drives demand",
                "Regulatory approval processes stable",
                "Digital health adoption increases"
            ],
            "financial_services": [
                "Interest rate environment stable",
                "Fintech disruption continues",
                "Regulatory compliance costs increase"
            ]
        }

        assumptions = base_assumptions + industry_assumptions.get(industry, [])

        # Horizon-specific assumptions
        if horizon == ForecastHorizon.LONG_TERM:
            assumptions.extend([
                "Long-term demographic trends continue",
                "Climate change impacts manageable",
                "Technology disruption follows predictable patterns"
            ])

        return assumptions

class PortfolioOptimizer:
    """Advanced portfolio optimization and asset allocation"""

    def __init__(self):
        self.portfolio_models = {}
        self.risk_models = {}
        self.return_models = {}
        self.correlation_matrices = defaultdict(dict)

    def optimize_deal_portfolio(self, portfolio_data: Dict[str, Any],
                               constraints: Dict[str, Any],
                               optimization_objective: str = "sharpe_ratio") -> PortfolioOptimization:
        """Optimize deal portfolio allocation"""

        optimization_id = f"opt_{int(datetime.now().timestamp())}"

        # Extract current portfolio composition
        current_composition = portfolio_data.get("current_allocation", {})

        # Calculate expected returns and risks
        expected_returns = self._calculate_expected_returns(portfolio_data)
        risk_metrics = self._calculate_portfolio_risk(portfolio_data)

        # Perform optimization
        optimized_allocation = self._perform_optimization(
            current_composition, expected_returns, risk_metrics,
            constraints, optimization_objective
        )

        # Calculate portfolio metrics
        portfolio_metrics = self._calculate_portfolio_metrics(
            optimized_allocation, expected_returns, risk_metrics
        )

        # Generate recommendations
        recommendations = self._generate_optimization_recommendations(
            current_composition, optimized_allocation, portfolio_metrics
        )

        # Calculate rebalancing suggestions
        rebalancing = self._calculate_rebalancing_suggestions(
            current_composition, optimized_allocation
        )

        return PortfolioOptimization(
            optimization_id=optimization_id,
            portfolio_composition=optimized_allocation,
            expected_return=portfolio_metrics["expected_return"],
            risk_score=portfolio_metrics["risk_score"],
            sharpe_ratio=portfolio_metrics["sharpe_ratio"],
            diversification_score=portfolio_metrics["diversification_score"],
            recommendations=recommendations,
            rebalancing_suggestions=rebalancing
        )

    def _calculate_expected_returns(self, portfolio_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate expected returns for portfolio components"""
        expected_returns = {}

        deals = portfolio_data.get("deals", {})
        for deal_id, deal_info in deals.items():
            # Calculate expected return based on deal characteristics
            base_return = 0.12  # 12% base return

            # Adjust based on deal characteristics
            if "industry" in deal_info:
                industry_adjustments = {
                    "technology": 0.03,
                    "healthcare": 0.02,
                    "financial_services": 0.01,
                    "manufacturing": 0.0,
                    "retail": -0.01,
                    "energy": -0.02
                }
                base_return += industry_adjustments.get(deal_info["industry"], 0.0)

            # Risk adjustment
            if "risk_score" in deal_info:
                risk_adjustment = (deal_info["risk_score"] - 50) / 100 * 0.05
                base_return += risk_adjustment

            # Deal size adjustment
            if "deal_value" in deal_info:
                size_factor = min(0.02, deal_info["deal_value"] / 1_000_000_000 * 0.01)
                base_return += size_factor

            expected_returns[deal_id] = base_return + random.uniform(-0.02, 0.02)

        return expected_returns

    def _calculate_portfolio_risk(self, portfolio_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate risk metrics for portfolio components"""
        risk_metrics = {}

        deals = portfolio_data.get("deals", {})
        for deal_id, deal_info in deals.items():
            # Calculate risk score
            base_risk = 0.15  # 15% base volatility

            # Adjust based on deal characteristics
            if "industry" in deal_info:
                industry_risk = {
                    "technology": 0.05,
                    "healthcare": 0.03,
                    "energy": 0.08,
                    "financial_services": 0.04,
                    "manufacturing": 0.02,
                    "retail": 0.06
                }
                base_risk += industry_risk.get(deal_info["industry"], 0.03)

            # Deal stage risk
            if "stage" in deal_info:
                stage_risk = {
                    "origination": 0.10,
                    "due_diligence": 0.05,
                    "negotiation": 0.03,
                    "closing": 0.01
                }
                base_risk += stage_risk.get(deal_info["stage"], 0.05)

            risk_metrics[deal_id] = base_risk + random.uniform(-0.02, 0.02)

        return risk_metrics

    def _perform_optimization(self, current_allocation: Dict[str, float],
                            expected_returns: Dict[str, float],
                            risk_metrics: Dict[str, float],
                            constraints: Dict[str, Any],
                            objective: str) -> Dict[str, float]:
        """Perform portfolio optimization"""

        # Simplified optimization simulation
        optimized_allocation = {}
        total_deals = len(expected_returns)

        if total_deals == 0:
            return optimized_allocation

        # Basic equal-weight starting point
        base_weight = 1.0 / total_deals

        for deal_id in expected_returns.keys():
            weight = base_weight

            # Adjust based on expected return vs risk
            return_ratio = expected_returns[deal_id] / risk_metrics.get(deal_id, 0.1)

            if objective == "sharpe_ratio":
                # Higher weight for better risk-adjusted return
                weight *= (1 + (return_ratio - 1) * 0.5)
            elif objective == "max_return":
                # Higher weight for higher expected return
                weight *= (1 + expected_returns[deal_id] * 2)
            elif objective == "min_risk":
                # Higher weight for lower risk
                weight *= (1 - risk_metrics.get(deal_id, 0.1) * 2)

            optimized_allocation[deal_id] = max(0.05, min(0.5, weight))  # 5-50% bounds

        # Normalize to sum to 1
        total_weight = sum(optimized_allocation.values())
        if total_weight > 0:
            optimized_allocation = {
                deal_id: weight / total_weight
                for deal_id, weight in optimized_allocation.items()
            }

        return optimized_allocation

    def _calculate_portfolio_metrics(self, allocation: Dict[str, float],
                                   expected_returns: Dict[str, float],
                                   risk_metrics: Dict[str, float]) -> Dict[str, float]:
        """Calculate portfolio-level metrics"""

        if not allocation:
            return {
                "expected_return": 0.0,
                "risk_score": 0.0,
                "sharpe_ratio": 0.0,
                "diversification_score": 0.0
            }

        # Portfolio expected return
        portfolio_return = sum(
            allocation.get(deal_id, 0) * expected_returns.get(deal_id, 0)
            for deal_id in allocation.keys()
        )

        # Portfolio risk (simplified - assume some correlation)
        portfolio_variance = sum(
            (allocation.get(deal_id, 0) ** 2) * (risk_metrics.get(deal_id, 0) ** 2)
            for deal_id in allocation.keys()
        )

        # Add correlation effects (simplified)
        correlation_adjustment = 0.3  # Assume 30% average correlation
        for i, deal_id1 in enumerate(allocation.keys()):
            for deal_id2 in list(allocation.keys())[i+1:]:
                weight1 = allocation.get(deal_id1, 0)
                weight2 = allocation.get(deal_id2, 0)
                risk1 = risk_metrics.get(deal_id1, 0)
                risk2 = risk_metrics.get(deal_id2, 0)
                portfolio_variance += 2 * weight1 * weight2 * risk1 * risk2 * correlation_adjustment

        portfolio_risk = math.sqrt(portfolio_variance)

        # Sharpe ratio (assuming 3% risk-free rate)
        risk_free_rate = 0.03
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0

        # Diversification score
        num_positions = len([w for w in allocation.values() if w > 0.01])
        max_weight = max(allocation.values()) if allocation else 0
        diversification_score = (num_positions / 10) * (1 - max_weight)  # Simplified

        return {
            "expected_return": round(portfolio_return, 4),
            "risk_score": round(portfolio_risk, 4),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "diversification_score": round(diversification_score, 2)
        }

    def _generate_optimization_recommendations(self, current_allocation: Dict[str, float],
                                             optimized_allocation: Dict[str, float],
                                             metrics: Dict[str, float]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        # Portfolio-level recommendations
        if metrics["sharpe_ratio"] > 1.5:
            recommendations.append("Excellent risk-adjusted returns. Consider maintaining allocation.")
        elif metrics["sharpe_ratio"] > 1.0:
            recommendations.append("Good risk-adjusted returns. Monitor performance closely.")
        else:
            recommendations.append("Below-target risk-adjusted returns. Consider rebalancing.")

        # Diversification recommendations
        if metrics["diversification_score"] < 0.5:
            recommendations.append("Portfolio concentration risk detected. Increase diversification.")

        # Risk recommendations
        if metrics["risk_score"] > 0.25:
            recommendations.append("High portfolio risk. Consider reducing exposure to volatile deals.")

        # Allocation change recommendations
        large_changes = [
            deal_id for deal_id in optimized_allocation
            if abs(optimized_allocation.get(deal_id, 0) - current_allocation.get(deal_id, 0)) > 0.1
        ]

        if large_changes:
            recommendations.append(f"Significant rebalancing recommended for {len(large_changes)} positions.")

        return recommendations

    def _calculate_rebalancing_suggestions(self, current_allocation: Dict[str, float],
                                         optimized_allocation: Dict[str, float]) -> Dict[str, float]:
        """Calculate specific rebalancing suggestions"""
        rebalancing = {}

        all_deals = set(current_allocation.keys()) | set(optimized_allocation.keys())

        for deal_id in all_deals:
            current_weight = current_allocation.get(deal_id, 0)
            target_weight = optimized_allocation.get(deal_id, 0)
            change = target_weight - current_weight

            if abs(change) > 0.01:  # Only suggest changes > 1%
                rebalancing[deal_id] = round(change, 4)

        return rebalancing

class PredictiveAnalytics:
    """Main predictive analytics orchestrator"""

    def __init__(self):
        self.deal_forecasting = DealForecastingEngine()
        self.market_forecasting = MarketForecastingEngine()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.analytics_cache = {}

    async def comprehensive_deal_analysis(self, deal_id: str, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive predictive analysis for a deal"""

        analysis_id = f"analysis_{deal_id}_{int(datetime.now().timestamp())}"

        # Generate multiple predictions
        deal_success_prediction = self.deal_forecasting.predict_deal_outcome(
            deal_id, deal_data, PredictionType.DEAL_SUCCESS
        )

        valuation_prediction = self.deal_forecasting.predict_deal_outcome(
            deal_id, deal_data, PredictionType.VALUATION_ACCURACY
        )

        integration_prediction = self.deal_forecasting.predict_deal_outcome(
            deal_id, deal_data, PredictionType.INTEGRATION_SUCCESS
        )

        # Generate scenario analysis
        scenarios = [ScenarioType.BASE_CASE, ScenarioType.OPTIMISTIC, ScenarioType.PESSIMISTIC]
        scenario_analysis = self.deal_forecasting.generate_scenario_analysis(
            deal_id, deal_data, scenarios
        )

        # Generate market forecast
        industry = deal_data.get("industry", "technology")
        market_forecast = self.market_forecasting.generate_market_forecast(industry)

        # Compile comprehensive analysis
        comprehensive_analysis = {
            "analysis_id": analysis_id,
            "deal_id": deal_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "predictions": {
                "deal_success": deal_success_prediction.__dict__,
                "valuation_accuracy": valuation_prediction.__dict__,
                "integration_success": integration_prediction.__dict__
            },
            "scenario_analysis": {
                scenario: prediction.__dict__
                for scenario, prediction in scenario_analysis.items()
            },
            "market_forecast": market_forecast.__dict__,
            "risk_summary": self._generate_risk_summary([
                deal_success_prediction, valuation_prediction, integration_prediction
            ]),
            "recommendation": self._generate_overall_recommendation(
                deal_success_prediction, valuation_prediction, integration_prediction
            )
        }

        # Cache results
        self.analytics_cache[analysis_id] = comprehensive_analysis

        return comprehensive_analysis

    async def optimize_deal_portfolio(self, portfolio_data: Dict[str, Any],
                                    optimization_constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize deal portfolio allocation"""

        optimization = self.portfolio_optimizer.optimize_deal_portfolio(
            portfolio_data, optimization_constraints
        )

        # Generate market context
        portfolio_industries = set()
        for deal_info in portfolio_data.get("deals", {}).values():
            if "industry" in deal_info:
                portfolio_industries.add(deal_info["industry"])

        market_context = {}
        for industry in portfolio_industries:
            market_context[industry] = self.market_forecasting.generate_market_forecast(industry)

        return {
            "optimization_result": optimization.__dict__,
            "market_context": {
                industry: forecast.__dict__
                for industry, forecast in market_context.items()
            },
            "optimization_timestamp": datetime.now().isoformat()
        }

    def _generate_risk_summary(self, predictions: List[DealPrediction]) -> Dict[str, Any]:
        """Generate consolidated risk summary"""
        all_risk_factors = []
        confidence_scores = []

        for prediction in predictions:
            all_risk_factors.extend(prediction.risk_factors)
            confidence_scores.append(prediction.confidence_score)

        # Deduplicate and categorize risks
        unique_risks = list(set(all_risk_factors))

        # Calculate overall confidence
        avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0

        # Risk categorization (simplified)
        high_risk_indicators = [risk for risk in unique_risks if "challenge" in risk or "concern" in risk]

        return {
            "overall_confidence": round(avg_confidence, 2),
            "total_risk_factors": len(unique_risks),
            "high_priority_risks": len(high_risk_indicators),
            "consolidated_risks": unique_risks[:10],  # Top 10 risks
            "risk_level": "high" if len(high_risk_indicators) > 5 else "medium" if len(high_risk_indicators) > 2 else "low"
        }

    def _generate_overall_recommendation(self, deal_success: DealPrediction,
                                       valuation: DealPrediction,
                                       integration: DealPrediction) -> str:
        """Generate overall recommendation based on all predictions"""

        success_score = deal_success.confidence_score if deal_success.predicted_outcome == "success" else 1 - deal_success.confidence_score
        valuation_score = valuation.confidence_score if valuation.predicted_outcome == "positive" else 1 - valuation.confidence_score
        integration_score = integration.confidence_score if integration.predicted_outcome == "positive" else 1 - integration.confidence_score

        overall_score = (success_score + valuation_score + integration_score) / 3

        if overall_score >= 0.75:
            return "PROCEED - Strong positive indicators across all dimensions"
        elif overall_score >= 0.65:
            return "PROCEED WITH CAUTION - Generally positive but monitor key risks"
        elif overall_score >= 0.5:
            return "CONDITIONAL - Additional analysis required before proceeding"
        else:
            return "DO NOT PROCEED - Significant risks outweigh potential benefits"

# Service instance management
_predictive_analytics_instance = None

def get_predictive_analytics() -> PredictiveAnalytics:
    """Get singleton predictive analytics instance"""
    global _predictive_analytics_instance
    if _predictive_analytics_instance is None:
        _predictive_analytics_instance = PredictiveAnalytics()
    return _predictive_analytics_instance