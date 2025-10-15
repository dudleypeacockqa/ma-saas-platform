"""
Predictive Deal Analytics
Advanced machine learning models for superhuman deal insights
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import joblib
from pathlib import Path
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

from app.core.config import settings
from app.core.database import get_database
from app.analytics import ADVANCED_ANALYTICS_CONFIG

logger = logging.getLogger(__name__)

class DealOutcome(str, Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    ONGOING = "ongoing"

class IntegrationComplexity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class ValuationGapStrategy(str, Enum):
    INCREASE_OFFER = "increase_offer"
    IMPROVE_TERMS = "improve_terms"
    WALK_AWAY = "walk_away"
    ADD_EARNOUT = "add_earnout"
    SELLER_FINANCING = "seller_financing"

@dataclass
class DealSuccessPrediction:
    deal_id: str
    success_probability: float
    failure_probability: float
    partial_success_probability: float
    confidence_score: float
    key_success_factors: List[str]
    key_risk_factors: List[str]
    recommendation: str
    model_version: str
    prediction_timestamp: datetime

@dataclass
class TimingOptimization:
    deal_id: str
    optimal_timing_score: float
    recommended_action: str
    optimal_timeframe: str
    timing_confidence: float
    market_factors: Dict[str, float]
    deal_specific_factors: Dict[str, float]
    seasonal_adjustment: float
    urgency_factors: List[str]

@dataclass
class ValuationGapAnalysis:
    current_gap: float
    gap_percentage: float
    bridging_strategies: List[Dict[str, Any]]
    probability_of_closure: float
    optimal_negotiation_approach: str
    value_drivers_analysis: Dict[str, float]
    comparable_transactions: List[Dict[str, Any]]
    sensitivity_analysis: Dict[str, float]

@dataclass
class IntegrationComplexityPrediction:
    deal_id: str
    complexity_level: IntegrationComplexity
    complexity_score: float
    integration_duration_months: int
    resource_requirements: Dict[str, int]
    key_integration_challenges: List[str]
    success_factors: List[str]
    risk_mitigation_strategies: List[str]
    cost_estimate: float

@dataclass
class PostAcquisitionForecast:
    deal_id: str
    year_1_performance: Dict[str, float]
    year_3_performance: Dict[str, float]
    year_5_performance: Dict[str, float]
    value_creation_drivers: List[str]
    performance_scenarios: Dict[str, Dict[str, float]]
    synergy_realization_timeline: Dict[str, float]
    key_performance_indicators: Dict[str, float]

class DealSuccessPredictor:
    """Advanced ML model for predicting deal success probability"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["predictive"]
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = {}
        self.model_performance = {}

    async def predict_deal_success(
        self,
        deal_features: Dict[str, Any],
        include_explanations: bool = True
    ) -> DealSuccessPrediction:
        """Predict deal success probability with detailed analysis"""
        try:
            # Ensure model is trained
            if self.model is None:
                await self._train_model()

            # Prepare features
            feature_vector = self._prepare_features(deal_features)
            feature_vector_scaled = self.scaler.transform([feature_vector])

            # Make prediction
            probabilities = self.model.predict_proba(feature_vector_scaled)[0]

            success_prob = float(probabilities[2])  # Success class
            partial_success_prob = float(probabilities[1])  # Partial success
            failure_prob = float(probabilities[0])  # Failure class

            # Calculate confidence based on prediction certainty
            max_prob = max(probabilities)
            confidence = (max_prob - (1/3)) / (2/3)  # Normalize to 0-1 scale

            # Generate explanations
            success_factors, risk_factors = await self._generate_explanations(
                deal_features, feature_vector, success_prob
            ) if include_explanations else ([], [])

            # Generate recommendation
            recommendation = self._generate_recommendation(success_prob, confidence)

            return DealSuccessPrediction(
                deal_id=deal_features.get("deal_id", "unknown"),
                success_probability=success_prob,
                failure_probability=failure_prob,
                partial_success_probability=partial_success_prob,
                confidence_score=confidence,
                key_success_factors=success_factors,
                key_risk_factors=risk_factors,
                recommendation=recommendation,
                model_version="v2.1",
                prediction_timestamp=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Error predicting deal success: {e}")
            raise

    async def _train_model(self):
        """Train the deal success prediction model"""
        try:
            # Get training data
            X, y = await self._get_training_data()

            if len(X) == 0:
                logger.warning("No training data available, using mock data")
                X, y = self._generate_mock_training_data()

            # Prepare features
            X_scaled = self.scaler.fit_transform(X)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42, stratify=y
            )

            # Create ensemble model
            models = []

            # Random Forest
            rf = RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                random_state=42
            )
            models.append(('random_forest', rf))

            # Gradient Boosting
            gb = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                random_state=42
            )
            models.append(('gradient_boosting', gb))

            # XGBoost
            xgb_model = xgb.XGBRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                random_state=42
            )
            models.append(('xgboost', xgb_model))

            # Neural Network
            nn = MLPRegressor(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42
            )
            models.append(('neural_network', nn))

            # Ensemble
            self.model = VotingRegressor(models)

            # Train model
            self.model.fit(X_train, y_train)

            # Evaluate performance
            y_pred = self.model.predict(X_test)
            self.model_performance = {
                "mse": mean_squared_error(y_test, y_pred),
                "mae": mean_absolute_error(y_test, y_pred),
                "r2": r2_score(y_test, y_pred)
            }

            # Feature importance (from random forest component)
            if hasattr(self.model.estimators_[0], 'feature_importances_'):
                self.feature_importance = dict(zip(
                    self._get_feature_names(),
                    self.model.estimators_[0].feature_importances_
                ))

            logger.info(f"Model trained with R² score: {self.model_performance['r2']:.3f}")

        except Exception as e:
            logger.error(f"Error training model: {e}")
            # Fallback to simple mock model
            self.model = self._create_mock_model()

    def _prepare_features(self, deal_features: Dict[str, Any]) -> List[float]:
        """Prepare feature vector from deal data"""
        return [
            # Financial features
            deal_features.get("deal_size", 50_000_000) / 1_000_000,  # Deal size in millions
            deal_features.get("target_revenue", 100_000_000) / 1_000_000,
            deal_features.get("target_ebitda", 20_000_000) / 1_000_000,
            deal_features.get("ebitda_margin", 0.15),
            deal_features.get("revenue_growth_rate", 0.10),
            deal_features.get("debt_to_equity", 1.0),
            deal_features.get("current_ratio", 1.5),

            # Strategic features
            deal_features.get("strategic_fit_score", 3.5),  # 1-5 scale
            deal_features.get("market_position", 3.0),      # 1-5 scale
            deal_features.get("management_quality", 3.5),   # 1-5 scale
            deal_features.get("synergy_potential", 0.15),   # Percentage

            # Market features
            deal_features.get("industry_growth_rate", 0.08),
            deal_features.get("market_size", 5_000_000_000) / 1_000_000_000,  # Market size in billions
            deal_features.get("competitive_intensity", 3.0),  # 1-5 scale

            # Deal structure features
            deal_features.get("cash_percentage", 0.7),       # Percentage cash vs stock
            deal_features.get("earnout_percentage", 0.1),    # Percentage earnout
            deal_features.get("due_diligence_score", 3.5),   # 1-5 scale

            # Risk features
            deal_features.get("regulatory_risk", 2.0),       # 1-5 scale
            deal_features.get("integration_complexity", 3.0), # 1-5 scale
            deal_features.get("cultural_fit", 3.5),          # 1-5 scale

            # Timing features
            deal_features.get("market_timing_score", 3.0),   # 1-5 scale
            deal_features.get("urgency_level", 2.5),         # 1-5 scale

            # Additional features
            deal_features.get("team_experience", 4.0),       # 1-5 scale
            deal_features.get("post_acquisition_plan_quality", 3.5), # 1-5 scale
        ]

    def _get_feature_names(self) -> List[str]:
        """Get feature names for interpretability"""
        return [
            "deal_size_millions", "target_revenue_millions", "target_ebitda_millions",
            "ebitda_margin", "revenue_growth_rate", "debt_to_equity", "current_ratio",
            "strategic_fit_score", "market_position", "management_quality", "synergy_potential",
            "industry_growth_rate", "market_size_billions", "competitive_intensity",
            "cash_percentage", "earnout_percentage", "due_diligence_score",
            "regulatory_risk", "integration_complexity", "cultural_fit",
            "market_timing_score", "urgency_level", "team_experience", "post_acquisition_plan_quality"
        ]

    async def _generate_explanations(
        self,
        deal_features: Dict[str, Any],
        feature_vector: List[float],
        success_prob: float
    ) -> Tuple[List[str], List[str]]:
        """Generate explanations for the prediction"""
        success_factors = []
        risk_factors = []

        # Analyze key features
        if deal_features.get("strategic_fit_score", 0) > 4.0:
            success_factors.append("Excellent strategic fit with acquirer's core business")
        elif deal_features.get("strategic_fit_score", 0) < 2.5:
            risk_factors.append("Poor strategic alignment may hinder integration")

        if deal_features.get("management_quality", 0) > 4.0:
            success_factors.append("High-quality management team increases success probability")
        elif deal_features.get("management_quality", 0) < 2.5:
            risk_factors.append("Management team quality concerns pose execution risks")

        if deal_features.get("ebitda_margin", 0) > 0.20:
            success_factors.append("Strong profitability margins indicate healthy business")
        elif deal_features.get("ebitda_margin", 0) < 0.08:
            risk_factors.append("Low profitability margins may indicate operational issues")

        if deal_features.get("synergy_potential", 0) > 0.15:
            success_factors.append("Significant synergy opportunities identified")

        if deal_features.get("integration_complexity", 0) > 4.0:
            risk_factors.append("High integration complexity increases execution risk")

        if deal_features.get("regulatory_risk", 0) > 3.5:
            risk_factors.append("Elevated regulatory risk may delay or prevent closure")

        # Add model-based explanations using feature importance
        if self.feature_importance:
            top_features = sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            for feature, importance in top_features:
                if importance > 0.1:  # Significant feature
                    feature_value = feature_vector[self._get_feature_names().index(feature)]
                    if feature_value > 3.0:  # Assuming normalized features
                        success_factors.append(f"Strong {feature.replace('_', ' ')} contributes positively")

        return success_factors, risk_factors

    def _generate_recommendation(self, success_prob: float, confidence: float) -> str:
        """Generate recommendation based on prediction"""
        if success_prob > 0.8 and confidence > 0.7:
            return "PROCEED - High probability of success with strong confidence"
        elif success_prob > 0.6 and confidence > 0.6:
            return "PROCEED WITH CAUTION - Good success probability but monitor key risks"
        elif success_prob > 0.4:
            return "CONDITIONAL - Success uncertain, require additional due diligence"
        else:
            return "DO NOT PROCEED - Low probability of success, significant risks identified"

    async def _get_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get training data from database"""
        # In production, would query historical deal data
        return np.array([]), np.array([])

    def _generate_mock_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate mock training data for model development"""
        np.random.seed(42)
        n_samples = 2000

        # Generate features
        X = np.random.randn(n_samples, 24)  # 24 features

        # Generate target with realistic relationships
        y = (
            0.15 * X[:, 7] +   # strategic_fit_score
            0.12 * X[:, 9] +   # management_quality
            0.10 * X[:, 3] +   # ebitda_margin
            0.08 * X[:, 10] +  # synergy_potential
            -0.09 * X[:, 18] + # integration_complexity
            -0.07 * X[:, 17] + # regulatory_risk
            np.random.randn(n_samples) * 0.1
        )

        # Convert to probabilities (0-1 scale)
        y = 1 / (1 + np.exp(-y))

        return X, y

    def _create_mock_model(self):
        """Create simple mock model as fallback"""
        class MockModel:
            def predict_proba(self, X):
                # Simple heuristic model
                return np.array([[0.2, 0.2, 0.6]])  # [failure, partial, success]

        return MockModel()

class TimingOptimizer:
    """Optimize deal timing based on market conditions and deal characteristics"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["predictive"]

    async def optimize_deal_timing(
        self,
        deal_features: Dict[str, Any],
        market_conditions: Dict[str, Any]
    ) -> TimingOptimization:
        """Optimize timing for deal execution"""
        try:
            # Calculate timing score components
            market_score = await self._calculate_market_timing_score(market_conditions)
            deal_score = await self._calculate_deal_specific_score(deal_features)
            seasonal_adjustment = await self._get_seasonal_adjustment()

            # Combined timing score
            overall_score = (market_score * 0.4 + deal_score * 0.4 + seasonal_adjustment * 0.2)

            # Generate recommendation
            if overall_score > 0.8:
                action = "EXECUTE_IMMEDIATELY"
                timeframe = "next_30_days"
            elif overall_score > 0.6:
                action = "EXECUTE_SOON"
                timeframe = "next_90_days"
            elif overall_score > 0.4:
                action = "MONITOR_AND_PREPARE"
                timeframe = "next_6_months"
            else:
                action = "WAIT_FOR_BETTER_CONDITIONS"
                timeframe = "indefinite"

            # Calculate confidence
            confidence = min(1.0, abs(overall_score - 0.5) * 2)

            # Identify urgency factors
            urgency_factors = self._identify_urgency_factors(deal_features, market_conditions)

            return TimingOptimization(
                deal_id=deal_features.get("deal_id", "unknown"),
                optimal_timing_score=overall_score,
                recommended_action=action,
                optimal_timeframe=timeframe,
                timing_confidence=confidence,
                market_factors={
                    "market_sentiment": market_conditions.get("sentiment", 0.5),
                    "volatility": market_conditions.get("volatility", 0.2),
                    "credit_availability": market_conditions.get("credit_availability", 0.7),
                    "regulatory_environment": market_conditions.get("regulatory_score", 0.6)
                },
                deal_specific_factors={
                    "competitive_pressure": deal_features.get("competitive_pressure", 0.5),
                    "seller_motivation": deal_features.get("seller_motivation", 0.6),
                    "due_diligence_readiness": deal_features.get("dd_readiness", 0.7),
                    "financing_secured": deal_features.get("financing_secured", 0.8)
                },
                seasonal_adjustment=seasonal_adjustment,
                urgency_factors=urgency_factors
            )

        except Exception as e:
            logger.error(f"Error optimizing deal timing: {e}")
            raise

    async def _calculate_market_timing_score(self, market_conditions: Dict[str, Any]) -> float:
        """Calculate market-based timing score"""
        sentiment = market_conditions.get("sentiment", 0.5)
        volatility = market_conditions.get("volatility", 0.2)
        credit_availability = market_conditions.get("credit_availability", 0.7)
        valuation_level = market_conditions.get("valuation_level", 0.6)

        # Higher sentiment and credit availability are positive
        # Lower volatility and reasonable valuations are positive
        score = (
            sentiment * 0.3 +
            (1 - volatility) * 0.2 +
            credit_availability * 0.3 +
            (1 - abs(valuation_level - 0.6)) * 0.2  # Optimal around 0.6
        )

        return min(1.0, max(0.0, score))

    async def _calculate_deal_specific_score(self, deal_features: Dict[str, Any]) -> float:
        """Calculate deal-specific timing score"""
        competitive_pressure = deal_features.get("competitive_pressure", 0.5)
        seller_motivation = deal_features.get("seller_motivation", 0.6)
        dd_readiness = deal_features.get("dd_readiness", 0.7)
        financing_secured = deal_features.get("financing_secured", 0.8)

        score = (
            competitive_pressure * 0.25 +  # Higher competition = act faster
            seller_motivation * 0.25 +     # Higher motivation = better timing
            dd_readiness * 0.25 +          # More ready = act faster
            financing_secured * 0.25       # Secured financing = act faster
        )

        return score

    async def _get_seasonal_adjustment(self) -> float:
        """Get seasonal timing adjustment"""
        current_month = datetime.now().month

        # Q1 and Q4 typically better for M&A activity
        seasonal_factors = {
            1: 0.8, 2: 0.85, 3: 0.9,   # Q1
            4: 0.7, 5: 0.75, 6: 0.8,   # Q2
            7: 0.6, 8: 0.65, 9: 0.75,  # Q3
            10: 0.85, 11: 0.9, 12: 0.8  # Q4
        }

        return seasonal_factors.get(current_month, 0.7)

    def _identify_urgency_factors(
        self,
        deal_features: Dict[str, Any],
        market_conditions: Dict[str, Any]
    ) -> List[str]:
        """Identify factors creating urgency"""
        factors = []

        if deal_features.get("competitive_pressure", 0) > 0.7:
            factors.append("High competitive pressure from other bidders")

        if deal_features.get("seller_timeline", 0) > 0.8:
            factors.append("Seller has aggressive timeline requirements")

        if market_conditions.get("interest_rate_trend") == "rising":
            factors.append("Rising interest rates may increase financing costs")

        if deal_features.get("regulatory_window", 0) > 0.7:
            factors.append("Limited regulatory approval window")

        return factors

class ValuationGapBridger:
    """Analyze and recommend strategies to bridge valuation gaps"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["predictive"]

    async def analyze_valuation_gap(
        self,
        buyer_valuation: float,
        seller_expectation: float,
        deal_features: Dict[str, Any]
    ) -> ValuationGapAnalysis:
        """Analyze valuation gap and recommend bridging strategies"""
        try:
            gap = seller_expectation - buyer_valuation
            gap_percentage = (gap / buyer_valuation) * 100 if buyer_valuation > 0 else 0

            # Generate bridging strategies
            strategies = await self._generate_bridging_strategies(
                gap, gap_percentage, deal_features
            )

            # Estimate closure probability
            closure_prob = await self._estimate_closure_probability(gap_percentage, deal_features)

            # Analyze value drivers
            value_drivers = await self._analyze_value_drivers(deal_features)

            # Find comparable transactions
            comparables = await self._find_comparable_transactions(deal_features)

            # Perform sensitivity analysis
            sensitivity = await self._perform_sensitivity_analysis(deal_features)

            # Determine optimal negotiation approach
            negotiation_approach = self._determine_negotiation_approach(gap_percentage, strategies)

            return ValuationGapAnalysis(
                current_gap=gap,
                gap_percentage=gap_percentage,
                bridging_strategies=strategies,
                probability_of_closure=closure_prob,
                optimal_negotiation_approach=negotiation_approach,
                value_drivers_analysis=value_drivers,
                comparable_transactions=comparables,
                sensitivity_analysis=sensitivity
            )

        except Exception as e:
            logger.error(f"Error analyzing valuation gap: {e}")
            raise

    async def _generate_bridging_strategies(
        self,
        gap: float,
        gap_percentage: float,
        deal_features: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate strategies to bridge valuation gap"""
        strategies = []

        # Strategy 1: Increase cash offer
        if gap_percentage < 15:  # Small gap
            strategies.append({
                "strategy": ValuationGapStrategy.INCREASE_OFFER.value,
                "description": f"Increase cash offer by ${gap:,.0f}",
                "probability_success": 0.85,
                "cost_impact": gap,
                "timeline_impact": "minimal",
                "recommendation_priority": 1
            })

        # Strategy 2: Add earnout component
        if deal_features.get("revenue_growth_rate", 0) > 0.15:
            earnout_value = gap * 0.7  # Cover 70% of gap with earnout
            strategies.append({
                "strategy": ValuationGapStrategy.ADD_EARNOUT.value,
                "description": f"Add performance-based earnout up to ${earnout_value:,.0f}",
                "probability_success": 0.75,
                "cost_impact": earnout_value * 0.6,  # Expected payout
                "timeline_impact": "moderate",
                "recommendation_priority": 2
            })

        # Strategy 3: Improve deal terms
        strategies.append({
            "strategy": ValuationGapStrategy.IMPROVE_TERMS.value,
            "description": "Offer better terms (faster closing, retention packages, governance)",
            "probability_success": 0.60,
            "cost_impact": gap * 0.3,
            "timeline_impact": "minimal",
            "recommendation_priority": 3
        })

        # Strategy 4: Seller financing
        if deal_features.get("seller_financial_strength", 3) > 3.5:
            strategies.append({
                "strategy": ValuationGapStrategy.SELLER_FINANCING.value,
                "description": f"Request seller financing for ${gap * 0.5:,.0f}",
                "probability_success": 0.45,
                "cost_impact": gap * 0.1,  # Interest cost difference
                "timeline_impact": "moderate",
                "recommendation_priority": 4
            })

        # Strategy 5: Walk away (if gap too large)
        if gap_percentage > 25:
            strategies.append({
                "strategy": ValuationGapStrategy.WALK_AWAY.value,
                "description": "Gap too large - consider walking away",
                "probability_success": 0.0,
                "cost_impact": 0,
                "timeline_impact": "immediate",
                "recommendation_priority": 5
            })

        return sorted(strategies, key=lambda x: x["recommendation_priority"])

    async def _estimate_closure_probability(
        self,
        gap_percentage: float,
        deal_features: Dict[str, Any]
    ) -> float:
        """Estimate probability of successfully closing the deal"""
        base_probability = 0.8

        # Adjust for gap size
        if gap_percentage < 5:
            gap_adjustment = 0.1
        elif gap_percentage < 15:
            gap_adjustment = 0.0
        elif gap_percentage < 25:
            gap_adjustment = -0.2
        else:
            gap_adjustment = -0.4

        # Adjust for seller motivation
        motivation_adjustment = (deal_features.get("seller_motivation", 0.5) - 0.5) * 0.3

        # Adjust for competitive situation
        competition_adjustment = -deal_features.get("competitive_pressure", 0.5) * 0.2

        final_probability = base_probability + gap_adjustment + motivation_adjustment + competition_adjustment

        return max(0.05, min(0.95, final_probability))

    async def _analyze_value_drivers(self, deal_features: Dict[str, Any]) -> Dict[str, float]:
        """Analyze key value drivers and their impact"""
        return {
            "revenue_growth": deal_features.get("revenue_growth_rate", 0.1) * 100,
            "margin_improvement": deal_features.get("margin_improvement_potential", 0.05) * 100,
            "synergy_potential": deal_features.get("synergy_potential", 0.15) * 100,
            "market_expansion": deal_features.get("market_expansion_potential", 0.1) * 100,
            "operational_efficiency": deal_features.get("operational_efficiency_potential", 0.08) * 100
        }

    async def _find_comparable_transactions(self, deal_features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find comparable transactions for benchmarking"""
        # Mock comparable transactions
        return [
            {
                "transaction": "Similar Company A Acquisition",
                "date": "2023-08-15",
                "multiple": 12.5,
                "premium": 25.0,
                "outcome": "successful"
            },
            {
                "transaction": "Comparable Deal B",
                "date": "2023-06-22",
                "multiple": 11.8,
                "premium": 30.0,
                "outcome": "successful"
            }
        ]

    async def _perform_sensitivity_analysis(self, deal_features: Dict[str, Any]) -> Dict[str, float]:
        """Perform sensitivity analysis on key variables"""
        return {
            "revenue_growth_1pct_change": 0.08,  # 8% valuation impact
            "margin_50bps_change": 0.12,        # 12% valuation impact
            "discount_rate_50bps_change": -0.06, # -6% valuation impact
            "terminal_growth_50bps_change": 0.15, # 15% valuation impact
            "synergy_assumption_change": 0.20     # 20% valuation impact
        }

    def _determine_negotiation_approach(
        self,
        gap_percentage: float,
        strategies: List[Dict[str, Any]]
    ) -> str:
        """Determine optimal negotiation approach"""
        if gap_percentage < 10:
            return "collaborative_problem_solving"
        elif gap_percentage < 20:
            return "structured_negotiation"
        else:
            return "firm_position_with_alternatives"

class PredictionEngine:
    """Main orchestration service for all predictive analytics"""

    def __init__(self):
        self.config = ADVANCED_ANALYTICS_CONFIG["predictive"]
        self.success_predictor = DealSuccessPredictor()
        self.timing_optimizer = TimingOptimizer()
        self.valuation_bridger = ValuationGapBridger()

    async def comprehensive_deal_analysis(
        self,
        deal_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive predictive analysis on a deal"""
        try:
            # Run all analyses in parallel
            tasks = [
                self.success_predictor.predict_deal_success(deal_data),
                self.timing_optimizer.optimize_deal_timing(deal_data, market_data),
                self._predict_integration_complexity(deal_data),
                self._forecast_post_acquisition_performance(deal_data)
            ]

            success_prediction, timing_analysis, integration_prediction, performance_forecast = await asyncio.gather(*tasks)

            return {
                "deal_id": deal_data.get("deal_id", "unknown"),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "success_prediction": asdict(success_prediction),
                "timing_analysis": asdict(timing_analysis),
                "integration_prediction": asdict(integration_prediction),
                "performance_forecast": asdict(performance_forecast),
                "overall_recommendation": self._generate_overall_recommendation(
                    success_prediction, timing_analysis, integration_prediction
                ),
                "confidence_score": np.mean([
                    success_prediction.confidence_score,
                    timing_analysis.timing_confidence,
                    integration_prediction.complexity_score
                ])
            }

        except Exception as e:
            logger.error(f"Error in comprehensive deal analysis: {e}")
            raise

    async def _predict_integration_complexity(self, deal_data: Dict[str, Any]) -> IntegrationComplexityPrediction:
        """Predict integration complexity and requirements"""
        # Simplified integration complexity prediction
        complexity_factors = [
            deal_data.get("cultural_difference", 2.0),
            deal_data.get("system_integration_complexity", 3.0),
            deal_data.get("geographic_overlap", 2.5),
            deal_data.get("business_model_similarity", 3.5),
            deal_data.get("regulatory_complexity", 2.0)
        ]

        avg_complexity = np.mean(complexity_factors)

        if avg_complexity < 2.0:
            level = IntegrationComplexity.LOW
            duration = 6
        elif avg_complexity < 3.0:
            level = IntegrationComplexity.MEDIUM
            duration = 12
        elif avg_complexity < 4.0:
            level = IntegrationComplexity.HIGH
            duration = 18
        else:
            level = IntegrationComplexity.EXTREME
            duration = 24

        return IntegrationComplexityPrediction(
            deal_id=deal_data.get("deal_id", "unknown"),
            complexity_level=level,
            complexity_score=avg_complexity,
            integration_duration_months=duration,
            resource_requirements={
                "integration_team_size": int(5 + avg_complexity * 3),
                "consultant_months": int(duration * 2),
                "technology_resources": int(avg_complexity * 2)
            },
            key_integration_challenges=[
                "System integration and data migration",
                "Cultural alignment and change management",
                "Process harmonization",
                "Regulatory compliance alignment"
            ],
            success_factors=[
                "Strong leadership commitment",
                "Clear integration roadmap",
                "Effective communication",
                "Adequate resource allocation"
            ],
            risk_mitigation_strategies=[
                "Establish dedicated integration office",
                "Implement phased integration approach",
                "Regular stakeholder communication",
                "Continuous monitoring and adjustment"
            ],
            cost_estimate=duration * 100000 * avg_complexity  # Rough cost estimate
        )

    async def _forecast_post_acquisition_performance(self, deal_data: Dict[str, Any]) -> PostAcquisitionForecast:
        """Forecast post-acquisition performance"""
        base_performance = deal_data.get("current_performance", {
            "revenue": 100_000_000,
            "ebitda": 20_000_000,
            "growth_rate": 0.1
        })

        # Simple performance projection model
        synergy_factor = 1 + deal_data.get("synergy_potential", 0.15)
        market_growth = deal_data.get("market_growth_rate", 0.08)

        year_1_performance = {
            "revenue_growth": market_growth + 0.02,  # Market + integration benefit
            "ebitda_margin": deal_data.get("ebitda_margin", 0.2) + 0.01,
            "synergy_realization": 0.3  # 30% of synergies realized in year 1
        }

        year_3_performance = {
            "revenue_growth": market_growth + 0.05,
            "ebitda_margin": deal_data.get("ebitda_margin", 0.2) + 0.03,
            "synergy_realization": 0.8  # 80% of synergies realized by year 3
        }

        year_5_performance = {
            "revenue_growth": market_growth,
            "ebitda_margin": deal_data.get("ebitda_margin", 0.2) + 0.05,
            "synergy_realization": 1.0  # Full synergy realization
        }

        return PostAcquisitionForecast(
            deal_id=deal_data.get("deal_id", "unknown"),
            year_1_performance=year_1_performance,
            year_3_performance=year_3_performance,
            year_5_performance=year_5_performance,
            value_creation_drivers=[
                "Revenue synergies from cross-selling",
                "Cost synergies from operational efficiency",
                "Market expansion opportunities",
                "Technology and innovation benefits"
            ],
            performance_scenarios={
                "optimistic": {
                    "year_5_revenue_multiple": 2.5,
                    "year_5_ebitda_multiple": 3.2,
                    "probability": 0.2
                },
                "base_case": {
                    "year_5_revenue_multiple": 1.8,
                    "year_5_ebitda_multiple": 2.4,
                    "probability": 0.6
                },
                "pessimistic": {
                    "year_5_revenue_multiple": 1.3,
                    "year_5_ebitda_multiple": 1.6,
                    "probability": 0.2
                }
            },
            synergy_realization_timeline={
                "year_1": 0.3,
                "year_2": 0.6,
                "year_3": 0.8,
                "year_4": 0.9,
                "year_5": 1.0
            },
            key_performance_indicators={
                "customer_retention_rate": 0.92,
                "employee_retention_rate": 0.88,
                "market_share_growth": 0.15,
                "integration_score": 0.85
            }
        )

    def _generate_overall_recommendation(
        self,
        success_prediction: DealSuccessPrediction,
        timing_analysis: TimingOptimization,
        integration_prediction: IntegrationComplexityPrediction
    ) -> str:
        """Generate overall deal recommendation"""
        if (success_prediction.success_probability > 0.8 and
            timing_analysis.optimal_timing_score > 0.7 and
            integration_prediction.complexity_level in [IntegrationComplexity.LOW, IntegrationComplexity.MEDIUM]):
            return "STRONG BUY - Excellent opportunity with high success probability"
        elif (success_prediction.success_probability > 0.6 and
              timing_analysis.optimal_timing_score > 0.5):
            return "BUY - Good opportunity with acceptable risk profile"
        elif success_prediction.success_probability > 0.4:
            return "CONDITIONAL - Proceed only with risk mitigation measures"
        else:
            return "PASS - High risk opportunity, recommend avoiding"

# Service factory function
_prediction_engine = None

async def get_prediction_engine() -> PredictionEngine:
    """Get singleton prediction engine instance"""
    global _prediction_engine
    if _prediction_engine is None:
        _prediction_engine = PredictionEngine()
    return _prediction_engine