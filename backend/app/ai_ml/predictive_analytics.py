"""
Predictive Analytics Engine - Sprint 12
Advanced machine learning models for deal prediction and forecasting
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json
import math
import numpy as np
from abc import ABC, abstractmethod


class PredictionType(str, Enum):
    DEAL_SUCCESS = "deal_success"
    VALUATION = "valuation"
    TIMELINE = "timeline"
    RISK_SCORE = "risk_score"
    MARKET_TIMING = "market_timing"
    SYNERGY_REALIZATION = "synergy_realization"
    INTEGRATION_SUCCESS = "integration_success"
    REGULATORY_APPROVAL = "regulatory_approval"


class ModelType(str, Enum):
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"
    TIME_SERIES = "time_series"


class ConfidenceLevel(str, Enum):
    HIGH = "high"          # >90%
    MEDIUM = "medium"      # 70-90%
    LOW = "low"           # 50-70%
    VERY_LOW = "very_low" # <50%


@dataclass
class PredictionInput:
    deal_id: str
    input_features: Dict[str, Any]
    historical_data: List[Dict[str, Any]]
    market_context: Dict[str, Any]
    timestamp: datetime


@dataclass
class PredictionResult:
    prediction_id: str
    deal_id: str
    prediction_type: PredictionType
    predicted_value: float
    confidence_score: float
    confidence_level: ConfidenceLevel
    prediction_range: Tuple[float, float]
    key_factors: List[Dict[str, Any]]
    model_used: ModelType
    feature_importance: Dict[str, float]
    prediction_date: datetime
    expiry_date: datetime


@dataclass
class ModelPerformance:
    model_id: str
    model_type: ModelType
    prediction_type: PredictionType
    accuracy_score: float
    precision: float
    recall: float
    f1_score: float
    mean_absolute_error: float
    training_samples: int
    last_trained: datetime
    validation_results: Dict[str, Any]


@dataclass
class FeatureEngineering:
    feature_id: str
    feature_name: str
    feature_type: str
    importance_score: float
    data_source: str
    calculation_method: str
    update_frequency: str
    dependencies: List[str]


class MLModel(ABC):
    """Abstract base class for machine learning models"""

    def __init__(self, model_type: ModelType):
        self.model_type = model_type
        self.is_trained = False
        self.training_data: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, float] = {}

    @abstractmethod
    def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train the model with provided data"""
        pass

    @abstractmethod
    def predict(self, input_features: Dict[str, Any]) -> Tuple[float, float]:
        """Make prediction and return value with confidence"""
        pass

    @abstractmethod
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        pass


class DealSuccessModel(MLModel):
    """Model for predicting deal success probability"""

    def __init__(self):
        super().__init__(ModelType.RANDOM_FOREST)
        self.feature_weights = {
            "deal_value": 0.15,
            "market_conditions": 0.12,
            "regulatory_complexity": 0.10,
            "financial_health_buyer": 0.10,
            "financial_health_seller": 0.10,
            "strategic_fit_score": 0.15,
            "management_support": 0.08,
            "market_timing": 0.08,
            "due_diligence_quality": 0.07,
            "cultural_alignment": 0.05
        }

    def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train deal success prediction model"""
        self.training_data = training_data

        # Simulate model training with historical data
        # In production, this would use actual ML libraries like scikit-learn
        self.performance_metrics = {
            "accuracy": 0.87,
            "precision": 0.84,
            "recall": 0.89,
            "f1_score": 0.86
        }

        self.is_trained = True
        return True

    def predict(self, input_features: Dict[str, Any]) -> Tuple[float, float]:
        """Predict deal success probability"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        # Calculate weighted score based on features
        score = 0.0
        confidence = 0.8  # Base confidence

        for feature, weight in self.feature_weights.items():
            if feature in input_features:
                feature_value = input_features[feature]

                # Normalize feature values to 0-1 scale
                if isinstance(feature_value, (int, float)):
                    normalized_value = min(max(feature_value / 100, 0), 1)
                    score += normalized_value * weight
                elif isinstance(feature_value, str):
                    # Convert categorical features to numeric
                    categorical_scores = {
                        "excellent": 1.0, "good": 0.8, "average": 0.6,
                        "poor": 0.4, "very_poor": 0.2
                    }
                    normalized_value = categorical_scores.get(feature_value.lower(), 0.5)
                    score += normalized_value * weight
            else:
                # Penalize missing features
                confidence -= 0.05

        # Apply market context adjustments
        market_conditions = input_features.get("market_conditions", 0.5)
        score *= (0.8 + 0.4 * market_conditions)

        # Ensure score is within valid range
        prediction = min(max(score, 0.0), 1.0)
        confidence = min(max(confidence, 0.3), 0.95)

        return prediction, confidence

    def get_feature_importance(self) -> Dict[str, float]:
        """Return feature importance scores"""
        return self.feature_weights.copy()


class ValuationModel(MLModel):
    """Model for predicting deal valuation"""

    def __init__(self):
        super().__init__(ModelType.GRADIENT_BOOSTING)
        self.valuation_factors = {
            "revenue": 0.20,
            "ebitda": 0.18,
            "growth_rate": 0.15,
            "market_position": 0.12,
            "industry_multiples": 0.10,
            "synergy_potential": 0.10,
            "risk_factors": -0.08,
            "market_conditions": 0.08,
            "competitive_intensity": -0.05
        }

    def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train valuation prediction model"""
        self.training_data = training_data

        # Simulate training process
        self.performance_metrics = {
            "mean_absolute_error": 0.12,  # 12% average error
            "r_squared": 0.82,
            "median_error": 0.08
        }

        self.is_trained = True
        return True

    def predict(self, input_features: Dict[str, Any]) -> Tuple[float, float]:
        """Predict deal valuation"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        # Base valuation calculation
        revenue = input_features.get("revenue", 0)
        ebitda = input_features.get("ebitda", 0)

        # Calculate base valuation using revenue multiple
        if revenue > 0:
            base_valuation = revenue * input_features.get("revenue_multiple", 3.0)
        elif ebitda > 0:
            base_valuation = ebitda * input_features.get("ebitda_multiple", 12.0)
        else:
            base_valuation = input_features.get("book_value", 0) * 1.5

        # Apply factor adjustments
        adjustment_factor = 1.0
        confidence = 0.75

        for factor, weight in self.valuation_factors.items():
            if factor in input_features:
                factor_value = input_features[factor]

                if isinstance(factor_value, (int, float)):
                    if factor in ["risk_factors", "competitive_intensity"]:
                        # Negative factors reduce valuation
                        adjustment_factor += weight * (factor_value / 100)
                    else:
                        # Positive factors increase valuation
                        adjustment_factor += weight * (factor_value / 100)
                    confidence += 0.02
            else:
                confidence -= 0.03

        predicted_valuation = base_valuation * adjustment_factor
        confidence = min(max(confidence, 0.4), 0.9)

        return predicted_valuation, confidence

    def get_feature_importance(self) -> Dict[str, float]:
        """Return feature importance for valuation"""
        return self.valuation_factors.copy()


class TimelineModel(MLModel):
    """Model for predicting deal completion timeline"""

    def __init__(self):
        super().__init__(ModelType.ENSEMBLE)
        self.timeline_factors = {
            "deal_complexity": 0.20,
            "regulatory_requirements": 0.18,
            "due_diligence_scope": 0.15,
            "financing_complexity": 0.12,
            "stakeholder_count": 0.10,
            "cross_border": 0.10,
            "market_conditions": 0.08,
            "management_cooperation": -0.07
        }

    def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train timeline prediction model"""
        self.training_data = training_data

        self.performance_metrics = {
            "mean_absolute_error": 18.5,  # Days
            "accuracy_within_30_days": 0.78,
            "accuracy_within_60_days": 0.92
        }

        self.is_trained = True
        return True

    def predict(self, input_features: Dict[str, Any]) -> Tuple[float, float]:
        """Predict deal completion timeline in days"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        # Base timeline estimation
        deal_type = input_features.get("deal_type", "acquisition")
        base_timelines = {
            "acquisition": 120,
            "merger": 180,
            "asset_purchase": 90,
            "joint_venture": 60,
            "strategic_partnership": 45
        }

        base_timeline = base_timelines.get(deal_type, 120)

        # Apply complexity factors
        complexity_multiplier = 1.0
        confidence = 0.7

        for factor, impact in self.timeline_factors.items():
            if factor in input_features:
                factor_value = input_features[factor]

                if isinstance(factor_value, bool):
                    if factor_value:
                        complexity_multiplier += abs(impact)
                elif isinstance(factor_value, (int, float)):
                    normalized_impact = (factor_value / 100) * impact
                    complexity_multiplier += normalized_impact

                confidence += 0.03
            else:
                confidence -= 0.02

        predicted_timeline = base_timeline * complexity_multiplier
        confidence = min(max(confidence, 0.4), 0.85)

        return predicted_timeline, confidence

    def get_feature_importance(self) -> Dict[str, float]:
        """Return timeline factor importance"""
        return self.timeline_factors.copy()


class DealOutcomePredictor:
    """Comprehensive deal outcome prediction system"""

    def __init__(self):
        self.models = {
            PredictionType.DEAL_SUCCESS: DealSuccessModel(),
            PredictionType.VALUATION: ValuationModel(),
            PredictionType.TIMELINE: TimelineModel()
        }
        self.prediction_history: List[PredictionResult] = []

    def train_models(self, training_data: Dict[PredictionType, List[Dict[str, Any]]]) -> Dict[PredictionType, bool]:
        """Train all prediction models"""
        results = {}

        for prediction_type, model in self.models.items():
            if prediction_type in training_data:
                success = model.train(training_data[prediction_type])
                results[prediction_type] = success
            else:
                results[prediction_type] = False

        return results

    def predict_deal_outcome(
        self,
        deal_id: str,
        input_features: Dict[str, Any],
        prediction_types: List[PredictionType]
    ) -> List[PredictionResult]:
        """Generate comprehensive deal outcome predictions"""

        results = []

        for prediction_type in prediction_types:
            if prediction_type not in self.models:
                continue

            model = self.models[prediction_type]

            try:
                predicted_value, confidence = model.predict(input_features)

                # Determine confidence level
                if confidence >= 0.9:
                    conf_level = ConfidenceLevel.HIGH
                elif confidence >= 0.7:
                    conf_level = ConfidenceLevel.MEDIUM
                elif confidence >= 0.5:
                    conf_level = ConfidenceLevel.LOW
                else:
                    conf_level = ConfidenceLevel.VERY_LOW

                # Calculate prediction range
                error_margin = (1 - confidence) * predicted_value
                pred_range = (
                    max(0, predicted_value - error_margin),
                    predicted_value + error_margin
                )

                # Get key factors
                feature_importance = model.get_feature_importance()
                key_factors = [
                    {
                        "factor": factor,
                        "importance": importance,
                        "current_value": input_features.get(factor, "N/A")
                    }
                    for factor, importance in sorted(
                        feature_importance.items(),
                        key=lambda x: abs(x[1]),
                        reverse=True
                    )[:5]
                ]

                prediction_result = PredictionResult(
                    prediction_id=f"pred_{deal_id}_{prediction_type.value}_{datetime.now().timestamp()}",
                    deal_id=deal_id,
                    prediction_type=prediction_type,
                    predicted_value=predicted_value,
                    confidence_score=confidence,
                    confidence_level=conf_level,
                    prediction_range=pred_range,
                    key_factors=key_factors,
                    model_used=model.model_type,
                    feature_importance=feature_importance,
                    prediction_date=datetime.now(),
                    expiry_date=datetime.now() + timedelta(days=30)
                )

                results.append(prediction_result)
                self.prediction_history.append(prediction_result)

            except Exception as e:
                # Log error and continue with other predictions
                continue

        return results

    def get_model_performance(self, prediction_type: PredictionType) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a specific model"""
        if prediction_type not in self.models:
            return None

        model = self.models[prediction_type]
        return {
            "model_type": model.model_type.value,
            "is_trained": model.is_trained,
            "performance_metrics": model.performance_metrics,
            "training_samples": len(model.training_data)
        }


class ValuationForecaster:
    """Advanced valuation forecasting with market dynamics"""

    def __init__(self):
        self.forecasting_models = {}
        self.market_indicators = {}
        self.valuation_history: List[Dict[str, Any]] = []

    def forecast_valuation_trends(
        self,
        industry_sector: str,
        time_horizon: int = 12,  # months
        scenario: str = "base_case"
    ) -> Dict[str, Any]:
        """Forecast valuation trends for industry sector"""

        # Generate synthetic forecast data
        # In production, this would use real market data and time series models
        current_multiple = 15.2  # Base EV/EBITDA multiple

        forecast_periods = []
        for month in range(1, time_horizon + 1):
            # Simulate market cycles and trends
            seasonal_factor = 1 + 0.05 * math.sin(month * math.pi / 6)  # Semi-annual cycle
            trend_factor = 1 + (month * 0.002)  # Slight upward trend
            volatility = 0.1 * (np.random.random() - 0.5) if 'np' in globals() else 0.05

            if scenario == "optimistic":
                scenario_factor = 1.15
            elif scenario == "pessimistic":
                scenario_factor = 0.85
            else:
                scenario_factor = 1.0

            predicted_multiple = current_multiple * seasonal_factor * trend_factor * scenario_factor * (1 + volatility)

            forecast_periods.append({
                "period": f"Month {month}",
                "date": (datetime.now() + timedelta(days=30 * month)).strftime("%Y-%m"),
                "ev_ebitda_multiple": round(predicted_multiple, 2),
                "confidence": max(0.9 - (month * 0.02), 0.6),  # Decreasing confidence over time
                "scenario_factors": {
                    "seasonal": seasonal_factor,
                    "trend": trend_factor,
                    "scenario": scenario_factor
                }
            })

        return {
            "industry_sector": industry_sector,
            "forecast_horizon": time_horizon,
            "scenario": scenario,
            "current_multiple": current_multiple,
            "forecast_periods": forecast_periods,
            "key_assumptions": [
                "Market volatility remains within historical ranges",
                "No major regulatory changes",
                "Economic conditions remain stable",
                "Industry fundamentals continue current trends"
            ],
            "risk_factors": [
                "Economic downturn",
                "Regulatory changes",
                "Industry disruption",
                "Market volatility spikes"
            ],
            "generated_at": datetime.now().isoformat()
        }

    def calculate_optimal_timing(
        self,
        deal_characteristics: Dict[str, Any],
        valuation_target: float
    ) -> Dict[str, Any]:
        """Calculate optimal timing for deal execution based on valuation forecasts"""

        deal_value = deal_characteristics.get("current_valuation", 100000000)
        industry = deal_characteristics.get("industry", "technology")

        # Generate timing analysis
        optimal_windows = []

        # Analyze next 18 months
        for month in range(1, 19):
            month_date = datetime.now() + timedelta(days=30 * month)

            # Simulate market conditions for each month
            market_favorability = 0.7 + 0.2 * math.sin(month * math.pi / 12)
            regulatory_calendar_impact = 1.0 if month % 6 != 0 else 0.8  # Avoid regulatory busy periods
            seasonal_impact = 1.1 if month in [3, 6, 9, 12] else 0.95  # Quarter-end effects

            overall_score = market_favorability * regulatory_calendar_impact * seasonal_impact

            # Calculate expected valuation
            expected_valuation = deal_value * overall_score
            meets_target = expected_valuation >= valuation_target

            optimal_windows.append({
                "month": month,
                "date": month_date.strftime("%Y-%m"),
                "market_favorability": round(market_favorability, 3),
                "expected_valuation": round(expected_valuation, 0),
                "meets_target": meets_target,
                "overall_score": round(overall_score, 3),
                "recommendation": "Optimal" if overall_score > 0.9 and meets_target else
                               "Good" if overall_score > 0.8 and meets_target else
                               "Consider" if meets_target else "Avoid"
            })

        # Find best windows
        optimal_periods = [w for w in optimal_windows if w["recommendation"] in ["Optimal", "Good"]]

        return {
            "deal_id": deal_characteristics.get("deal_id", "unknown"),
            "current_valuation": deal_value,
            "target_valuation": valuation_target,
            "analysis_horizon": "18 months",
            "optimal_windows": optimal_periods[:3],  # Top 3 windows
            "all_periods": optimal_windows,
            "recommendation_summary": {
                "best_month": optimal_periods[0]["month"] if optimal_periods else None,
                "expected_premium": max([w["overall_score"] for w in optimal_periods]) if optimal_periods else 0,
                "confidence_level": "high" if len(optimal_periods) >= 3 else "medium"
            },
            "analysis_date": datetime.now().isoformat()
        }

    def perform_sensitivity_analysis(
        self,
        base_valuation: float,
        sensitivity_factors: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis on valuation factors"""

        sensitivity_results = {}

        for factor_name, factor_scenarios in sensitivity_factors.items():
            factor_results = {}

            for scenario_name, factor_change in factor_scenarios.items():
                # Calculate impact on valuation
                if factor_name in ["revenue_multiple", "ebitda_multiple"]:
                    # Direct multiplier impact
                    adjusted_valuation = base_valuation * (1 + factor_change)
                elif factor_name in ["growth_rate", "market_position"]:
                    # Growth and position impact valuation premium
                    premium_impact = factor_change * 0.5  # 50% flow-through
                    adjusted_valuation = base_valuation * (1 + premium_impact)
                elif factor_name in ["risk_factors", "regulatory_risk"]:
                    # Risk factors reduce valuation
                    risk_discount = factor_change * -0.3  # 30% discount rate
                    adjusted_valuation = base_valuation * (1 + risk_discount)
                else:
                    # Default linear impact
                    adjusted_valuation = base_valuation * (1 + factor_change * 0.2)

                valuation_change = (adjusted_valuation - base_valuation) / base_valuation

                factor_results[scenario_name] = {
                    "factor_change": f"{factor_change:+.1%}",
                    "valuation_impact": f"{valuation_change:+.1%}",
                    "adjusted_valuation": round(adjusted_valuation, 0),
                    "sensitivity_ratio": abs(valuation_change / factor_change) if factor_change != 0 else 0
                }

            sensitivity_results[factor_name] = factor_results

        # Calculate overall sensitivity ranking
        factor_sensitivity = {}
        for factor_name, scenarios in sensitivity_results.items():
            avg_sensitivity = sum([s["sensitivity_ratio"] for s in scenarios.values()]) / len(scenarios)
            factor_sensitivity[factor_name] = avg_sensitivity

        # Sort by sensitivity (most sensitive first)
        sensitivity_ranking = sorted(factor_sensitivity.items(), key=lambda x: x[1], reverse=True)

        return {
            "base_valuation": base_valuation,
            "sensitivity_analysis": sensitivity_results,
            "sensitivity_ranking": [
                {"factor": factor, "sensitivity_score": score}
                for factor, score in sensitivity_ranking
            ],
            "key_insights": [
                f"Most sensitive to {sensitivity_ranking[0][0]} changes" if sensitivity_ranking else "No significant sensitivities",
                f"Top 3 factors: {', '.join([f[0] for f in sensitivity_ranking[:3]])}" if len(sensitivity_ranking) >= 3 else "",
                f"Overall volatility: {'High' if sensitivity_ranking[0][1] > 1.5 else 'Medium' if sensitivity_ranking[0][1] > 0.8 else 'Low'}" if sensitivity_ranking else ""
            ],
            "analysis_date": datetime.now().isoformat()
        }


class PredictiveAnalyticsEngine:
    """Main engine for predictive analytics and machine learning"""

    def __init__(self):
        self.deal_outcome_predictor = DealOutcomePredictor()
        self.valuation_forecaster = ValuationForecaster()
        self.model_registry: Dict[str, MLModel] = {}
        self.feature_store: Dict[str, FeatureEngineering] = {}

    def initialize_models(self) -> bool:
        """Initialize and train all ML models"""
        # Generate synthetic training data for demonstration
        # In production, this would use real historical deal data

        training_data = {
            PredictionType.DEAL_SUCCESS: self._generate_training_data("deal_success", 1000),
            PredictionType.VALUATION: self._generate_training_data("valuation", 800),
            PredictionType.TIMELINE: self._generate_training_data("timeline", 900)
        }

        results = self.deal_outcome_predictor.train_models(training_data)

        # Check if all models trained successfully
        return all(results.values())

    def generate_comprehensive_prediction(
        self,
        deal_id: str,
        deal_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive predictions for a deal"""

        # Prepare input features
        input_features = self._prepare_features(deal_characteristics)

        # Generate predictions for all types
        prediction_types = [
            PredictionType.DEAL_SUCCESS,
            PredictionType.VALUATION,
            PredictionType.TIMELINE
        ]

        predictions = self.deal_outcome_predictor.predict_deal_outcome(
            deal_id, input_features, prediction_types
        )

        # Generate valuation forecasts
        industry = deal_characteristics.get("industry", "technology")
        valuation_forecast = self.valuation_forecaster.forecast_valuation_trends(industry)

        # Calculate optimal timing
        current_valuation = deal_characteristics.get("current_valuation", 100000000)
        target_valuation = current_valuation * 1.2  # 20% premium target
        timing_analysis = self.valuation_forecaster.calculate_optimal_timing(
            deal_characteristics, target_valuation
        )

        # Compile comprehensive results
        return {
            "deal_id": deal_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "predictions": [
                {
                    "type": pred.prediction_type.value,
                    "predicted_value": pred.predicted_value,
                    "confidence_score": pred.confidence_score,
                    "confidence_level": pred.confidence_level.value,
                    "prediction_range": pred.prediction_range,
                    "key_factors": pred.key_factors,
                    "model_used": pred.model_used.value
                }
                for pred in predictions
            ],
            "valuation_forecast": valuation_forecast,
            "timing_analysis": timing_analysis,
            "risk_assessment": self._generate_risk_assessment(input_features),
            "recommendations": self._generate_recommendations(predictions, input_features)
        }

    def perform_model_validation(self) -> Dict[str, Any]:
        """Perform validation on all trained models"""
        validation_results = {}

        for prediction_type, model in self.deal_outcome_predictor.models.items():
            performance = self.deal_outcome_predictor.get_model_performance(prediction_type)
            validation_results[prediction_type.value] = performance

        return {
            "validation_timestamp": datetime.now().isoformat(),
            "model_performance": validation_results,
            "overall_health": "good" if all(
                r and r.get("is_trained", False)
                for r in validation_results.values()
            ) else "needs_attention"
        }

    def _prepare_features(self, deal_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and engineer features for ML models"""
        features = deal_characteristics.copy()

        # Feature engineering
        if "revenue" in features and "ebitda" in features:
            features["ebitda_margin"] = features["ebitda"] / features["revenue"] if features["revenue"] > 0 else 0

        if "deal_value" in features and "revenue" in features:
            features["revenue_multiple"] = features["deal_value"] / features["revenue"] if features["revenue"] > 0 else 0

        # Categorical encoding
        categorical_mappings = {
            "excellent": 100, "good": 80, "average": 60, "poor": 40, "very_poor": 20
        }

        for key, value in features.items():
            if isinstance(value, str) and value.lower() in categorical_mappings:
                features[f"{key}_encoded"] = categorical_mappings[value.lower()]

        return features

    def _generate_training_data(self, data_type: str, sample_count: int) -> List[Dict[str, Any]]:
        """Generate synthetic training data for model training"""
        training_samples = []

        for i in range(sample_count):
            # Generate synthetic deal data
            sample = {
                "deal_value": np.random.lognormal(18, 1) if 'np' in globals() else 100000000 + i * 1000000,
                "revenue": np.random.lognormal(17, 1) if 'np' in globals() else 50000000 + i * 500000,
                "ebitda": np.random.lognormal(16, 1) if 'np' in globals() else 10000000 + i * 100000,
                "market_conditions": np.random.random() if 'np' in globals() else 0.5 + (i % 10) * 0.05,
                "strategic_fit_score": np.random.random() if 'np' in globals() else 0.6 + (i % 8) * 0.05,
                "regulatory_complexity": np.random.random() if 'np' in globals() else 0.3 + (i % 6) * 0.1
            }

            # Generate target variable based on data type
            if data_type == "deal_success":
                # Success probability based on features
                success_factors = (
                    sample["market_conditions"] * 0.3 +
                    sample["strategic_fit_score"] * 0.4 +
                    (1 - sample["regulatory_complexity"]) * 0.3
                )
                sample["target"] = 1 if success_factors > 0.6 else 0

            elif data_type == "valuation":
                # Valuation based on fundamentals
                sample["target"] = sample["revenue"] * (2 + sample["strategic_fit_score"] * 2)

            elif data_type == "timeline":
                # Timeline based on complexity
                base_timeline = 120
                complexity_factor = 1 + sample["regulatory_complexity"]
                sample["target"] = base_timeline * complexity_factor

            training_samples.append(sample)

        return training_samples

    def _generate_risk_assessment(self, input_features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk assessment based on input features"""
        risk_factors = {
            "market_risk": input_features.get("market_conditions", 0.5),
            "regulatory_risk": input_features.get("regulatory_complexity", 0.3),
            "execution_risk": 1 - input_features.get("strategic_fit_score", 0.7),
            "financial_risk": 1 - input_features.get("financial_health_buyer", 0.8)
        }

        overall_risk = sum(risk_factors.values()) / len(risk_factors)

        return {
            "overall_risk_score": overall_risk,
            "risk_level": "high" if overall_risk > 0.7 else "medium" if overall_risk > 0.4 else "low",
            "risk_factors": risk_factors,
            "mitigation_recommendations": self._get_risk_mitigation_recommendations(risk_factors)
        }

    def _get_risk_mitigation_recommendations(self, risk_factors: Dict[str, float]) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []

        if risk_factors.get("market_risk", 0) > 0.6:
            recommendations.append("Consider market timing and hedging strategies")

        if risk_factors.get("regulatory_risk", 0) > 0.6:
            recommendations.append("Engage regulatory experts early in the process")

        if risk_factors.get("execution_risk", 0) > 0.6:
            recommendations.append("Develop detailed integration planning")

        if risk_factors.get("financial_risk", 0) > 0.6:
            recommendations.append("Conduct thorough financial due diligence")

        return recommendations

    def _generate_recommendations(
        self,
        predictions: List[PredictionResult],
        input_features: Dict[str, Any]
    ) -> List[str]:
        """Generate strategic recommendations based on predictions"""
        recommendations = []

        # Analyze predictions
        success_prediction = next((p for p in predictions if p.prediction_type == PredictionType.DEAL_SUCCESS), None)
        valuation_prediction = next((p for p in predictions if p.prediction_type == PredictionType.VALUATION), None)
        timeline_prediction = next((p for p in predictions if p.prediction_type == PredictionType.TIMELINE), None)

        if success_prediction:
            if success_prediction.predicted_value > 0.8:
                recommendations.append("High probability of success - proceed with confidence")
            elif success_prediction.predicted_value > 0.6:
                recommendations.append("Moderate success probability - address key risk factors")
            else:
                recommendations.append("Low success probability - consider restructuring or alternative approaches")

        if timeline_prediction:
            if timeline_prediction.predicted_value > 180:
                recommendations.append("Extended timeline expected - plan for longer process")
            elif timeline_prediction.predicted_value < 90:
                recommendations.append("Accelerated timeline possible - prepare for fast execution")

        if valuation_prediction and input_features.get("target_valuation"):
            target = input_features["target_valuation"]
            if valuation_prediction.predicted_value > target * 1.1:
                recommendations.append("Favorable valuation environment - consider premium pricing")
            elif valuation_prediction.predicted_value < target * 0.9:
                recommendations.append("Challenging valuation environment - adjust expectations")

        return recommendations if recommendations else ["Proceed with standard due diligence and planning"]


# Service instance and dependency injection
_predictive_analytics_engine: Optional[PredictiveAnalyticsEngine] = None


def get_predictive_analytics_engine() -> PredictiveAnalyticsEngine:
    """Get Predictive Analytics Engine instance"""
    global _predictive_analytics_engine
    if _predictive_analytics_engine is None:
        _predictive_analytics_engine = PredictiveAnalyticsEngine()
        # Initialize models on first access
        _predictive_analytics_engine.initialize_models()
    return _predictive_analytics_engine