"""
Portfolio Optimization Utilities
Mathematical foundation for M&A arbitrage portfolio optimization
Implements modern portfolio theory and advanced optimization techniques
"""

import numpy as np
import pandas as pd
from scipy import optimize
from scipy.stats import norm
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class OptimizationObjective(str, Enum):
    """Portfolio optimization objectives"""
    SHARPE_RATIO = "sharpe_ratio"
    RETURN_MAXIMIZATION = "return_maximization"
    RISK_MINIMIZATION = "risk_minimization"
    UTILITY_MAXIMIZATION = "utility_maximization"
    RISK_PARITY = "risk_parity"
    MEAN_VARIANCE = "mean_variance"


class ConstraintType(str, Enum):
    """Types of portfolio constraints"""
    MAX_WEIGHT = "max_weight"
    MIN_WEIGHT = "min_weight"
    MAX_SECTOR_EXPOSURE = "max_sector_exposure"
    MAX_PORTFOLIO_RISK = "max_portfolio_risk"
    LEVERAGE_LIMIT = "leverage_limit"
    TURNOVER_LIMIT = "turnover_limit"


@dataclass
class OptimizationResult:
    """Result of portfolio optimization"""
    weights: np.ndarray
    expected_return: float
    risk: float
    sharpe_ratio: float
    status: str
    constraints_satisfied: bool
    optimization_info: Dict[str, Any]


@dataclass
class RiskMetrics:
    """Portfolio risk metrics"""
    volatility: float
    var_95: float
    var_99: float
    expected_shortfall_95: float
    expected_shortfall_99: float
    max_drawdown: float
    beta: float
    correlation_to_market: float


class PortfolioOptimizer:
    """
    Advanced portfolio optimization engine
    Implements multiple optimization algorithms and objectives
    """

    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize portfolio optimizer

        Args:
            risk_free_rate: Risk-free rate for Sharpe ratio calculation
        """
        self.risk_free_rate = risk_free_rate
        self.optimization_methods = {
            OptimizationObjective.SHARPE_RATIO: self._optimize_sharpe_ratio,
            OptimizationObjective.RETURN_MAXIMIZATION: self._optimize_return,
            OptimizationObjective.RISK_MINIMIZATION: self._optimize_risk,
            OptimizationObjective.UTILITY_MAXIMIZATION: self._optimize_utility,
            OptimizationObjective.RISK_PARITY: self._optimize_risk_parity,
            OptimizationObjective.MEAN_VARIANCE: self._optimize_mean_variance
        }

    def optimize(
        self,
        expected_returns: np.ndarray,
        risk_estimates: np.ndarray,
        correlation_matrix: Optional[np.ndarray] = None,
        constraints: Optional[List[Dict[str, Any]]] = None,
        objective: str = OptimizationObjective.SHARPE_RATIO,
        available_capital: float = 1000000.0,
        risk_aversion: float = 3.0
    ) -> OptimizationResult:
        """
        Optimize portfolio allocation

        Args:
            expected_returns: Expected returns for each asset
            risk_estimates: Risk estimates for each asset
            correlation_matrix: Correlation matrix between assets
            constraints: List of optimization constraints
            objective: Optimization objective
            available_capital: Available capital for allocation
            risk_aversion: Risk aversion parameter for utility optimization

        Returns:
            OptimizationResult with optimal weights and metrics
        """
        try:
            n_assets = len(expected_returns)

            # Validate inputs
            if len(risk_estimates) != n_assets:
                raise ValueError("Expected returns and risk estimates must have same length")

            # Default correlation matrix to identity if not provided
            if correlation_matrix is None:
                correlation_matrix = np.eye(n_assets)

            # Build covariance matrix
            covariance_matrix = self._build_covariance_matrix(risk_estimates, correlation_matrix)

            # Parse constraints
            parsed_constraints = self._parse_constraints(constraints, n_assets)

            # Select optimization method
            optimization_method = self.optimization_methods.get(objective, self._optimize_sharpe_ratio)

            # Perform optimization
            result = optimization_method(
                expected_returns=expected_returns,
                covariance_matrix=covariance_matrix,
                constraints=parsed_constraints,
                available_capital=available_capital,
                risk_aversion=risk_aversion
            )

            # Validate result
            result = self._validate_optimization_result(result, parsed_constraints)

            return result

        except Exception as e:
            logger.error(f"Portfolio optimization failed: {e}")
            # Return equal-weight fallback
            return self._fallback_optimization(n_assets, expected_returns, covariance_matrix)

    def _build_covariance_matrix(
        self,
        risk_estimates: np.ndarray,
        correlation_matrix: np.ndarray
    ) -> np.ndarray:
        """Build covariance matrix from risk estimates and correlations"""
        # Convert volatilities to standard deviations
        std_devs = np.sqrt(risk_estimates)

        # Build covariance matrix: Cov = D * Corr * D (where D is diagonal matrix of std devs)
        covariance_matrix = np.outer(std_devs, std_devs) * correlation_matrix

        return covariance_matrix

    def _parse_constraints(
        self,
        constraints: Optional[List[Dict[str, Any]]],
        n_assets: int
    ) -> Dict[str, Any]:
        """Parse optimization constraints into scipy format"""
        parsed = {
            "bounds": [(0, 1) for _ in range(n_assets)],  # Default: no short selling, max 100% per asset
            "linear_constraints": [],
            "nonlinear_constraints": []
        }

        if not constraints:
            return parsed

        for constraint in constraints:
            constraint_type = constraint.get("type")
            value = constraint.get("value")

            if constraint_type == ConstraintType.MAX_WEIGHT:
                # Update bounds for all assets
                parsed["bounds"] = [(0, min(value, 1)) for _ in range(n_assets)]

            elif constraint_type == ConstraintType.MIN_WEIGHT:
                # Update lower bounds
                parsed["bounds"] = [(max(value, 0), bound[1]) for bound in parsed["bounds"]]

            elif constraint_type == ConstraintType.MAX_PORTFOLIO_RISK:
                # Portfolio risk constraint (nonlinear)
                parsed["max_portfolio_risk"] = value

            elif constraint_type == ConstraintType.LEVERAGE_LIMIT:
                # Sum of weights constraint
                parsed["max_leverage"] = value

        return parsed

    def _optimize_sharpe_ratio(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        constraints: Dict[str, Any],
        available_capital: float,
        risk_aversion: float
    ) -> OptimizationResult:
        """Optimize portfolio for maximum Sharpe ratio"""
        n_assets = len(expected_returns)

        def negative_sharpe_ratio(weights):
            """Objective function: negative Sharpe ratio (for minimization)"""
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))

            if portfolio_risk == 0:
                return -np.inf

            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk
            return -sharpe_ratio

        # Constraints
        scipy_constraints = []

        # Weights sum to 1 constraint
        scipy_constraints.append({
            'type': 'eq',
            'fun': lambda weights: np.sum(weights) - 1.0
        })

        # Portfolio risk constraint (if specified)
        if "max_portfolio_risk" in constraints:
            def risk_constraint(weights):
                portfolio_risk = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))
                return constraints["max_portfolio_risk"] - portfolio_risk

            scipy_constraints.append({
                'type': 'ineq',
                'fun': risk_constraint
            })

        # Initial guess: equal weights
        initial_weights = np.ones(n_assets) / n_assets

        # Optimize
        result = optimize.minimize(
            fun=negative_sharpe_ratio,
            x0=initial_weights,
            method='SLSQP',
            bounds=constraints["bounds"],
            constraints=scipy_constraints,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )

        if result.success:
            optimal_weights = result.x
            portfolio_return = np.dot(optimal_weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(optimal_weights, np.dot(covariance_matrix, optimal_weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0

            return OptimizationResult(
                weights=optimal_weights,
                expected_return=portfolio_return,
                risk=portfolio_risk,
                sharpe_ratio=sharpe_ratio,
                status="SUCCESS",
                constraints_satisfied=True,
                optimization_info={
                    "method": "Sharpe Ratio Optimization",
                    "iterations": result.nit,
                    "function_value": result.fun
                }
            )
        else:
            raise ValueError(f"Optimization failed: {result.message}")

    def _optimize_return(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        constraints: Dict[str, Any],
        available_capital: float,
        risk_aversion: float
    ) -> OptimizationResult:
        """Optimize portfolio for maximum expected return"""
        n_assets = len(expected_returns)

        def negative_return(weights):
            """Objective function: negative expected return"""
            return -np.dot(weights, expected_returns)

        # Constraints
        scipy_constraints = []

        # Weights sum to 1 constraint
        scipy_constraints.append({
            'type': 'eq',
            'fun': lambda weights: np.sum(weights) - 1.0
        })

        # Portfolio risk constraint (if specified)
        if "max_portfolio_risk" in constraints:
            def risk_constraint(weights):
                portfolio_risk = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))
                return constraints["max_portfolio_risk"] - portfolio_risk

            scipy_constraints.append({
                'type': 'ineq',
                'fun': risk_constraint
            })

        # Initial guess: equal weights
        initial_weights = np.ones(n_assets) / n_assets

        # Optimize
        result = optimize.minimize(
            fun=negative_return,
            x0=initial_weights,
            method='SLSQP',
            bounds=constraints["bounds"],
            constraints=scipy_constraints,
            options={'maxiter': 1000}
        )

        if result.success:
            optimal_weights = result.x
            portfolio_return = np.dot(optimal_weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(optimal_weights, np.dot(covariance_matrix, optimal_weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0

            return OptimizationResult(
                weights=optimal_weights,
                expected_return=portfolio_return,
                risk=portfolio_risk,
                sharpe_ratio=sharpe_ratio,
                status="SUCCESS",
                constraints_satisfied=True,
                optimization_info={
                    "method": "Return Maximization",
                    "iterations": result.nit
                }
            )
        else:
            raise ValueError(f"Optimization failed: {result.message}")

    def _optimize_risk(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        constraints: Dict[str, Any],
        available_capital: float,
        risk_aversion: float
    ) -> OptimizationResult:
        """Optimize portfolio for minimum risk"""
        n_assets = len(expected_returns)

        def portfolio_risk(weights):
            """Objective function: portfolio risk (variance)"""
            return np.dot(weights, np.dot(covariance_matrix, weights))

        # Constraints
        scipy_constraints = []

        # Weights sum to 1 constraint
        scipy_constraints.append({
            'type': 'eq',
            'fun': lambda weights: np.sum(weights) - 1.0
        })

        # Initial guess: equal weights
        initial_weights = np.ones(n_assets) / n_assets

        # Optimize
        result = optimize.minimize(
            fun=portfolio_risk,
            x0=initial_weights,
            method='SLSQP',
            bounds=constraints["bounds"],
            constraints=scipy_constraints,
            options={'maxiter': 1000}
        )

        if result.success:
            optimal_weights = result.x
            portfolio_return = np.dot(optimal_weights, expected_returns)
            portfolio_variance = np.dot(optimal_weights, np.dot(covariance_matrix, optimal_weights))
            portfolio_risk = np.sqrt(portfolio_variance)
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0

            return OptimizationResult(
                weights=optimal_weights,
                expected_return=portfolio_return,
                risk=portfolio_risk,
                sharpe_ratio=sharpe_ratio,
                status="SUCCESS",
                constraints_satisfied=True,
                optimization_info={
                    "method": "Risk Minimization",
                    "iterations": result.nit
                }
            )
        else:
            raise ValueError(f"Optimization failed: {result.message}")

    def _optimize_utility(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        constraints: Dict[str, Any],
        available_capital: float,
        risk_aversion: float
    ) -> OptimizationResult:
        """Optimize portfolio for maximum utility (mean-variance utility)"""
        n_assets = len(expected_returns)

        def negative_utility(weights):
            """Objective function: negative utility"""
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_variance = np.dot(weights, np.dot(covariance_matrix, weights))

            # Mean-variance utility: U = E[R] - (A/2) * Var[R]
            utility = portfolio_return - (risk_aversion / 2) * portfolio_variance
            return -utility

        # Constraints
        scipy_constraints = []

        # Weights sum to 1 constraint
        scipy_constraints.append({
            'type': 'eq',
            'fun': lambda weights: np.sum(weights) - 1.0
        })

        # Initial guess: equal weights
        initial_weights = np.ones(n_assets) / n_assets

        # Optimize
        result = optimize.minimize(
            fun=negative_utility,
            x0=initial_weights,
            method='SLSQP',
            bounds=constraints["bounds"],
            constraints=scipy_constraints,
            options={'maxiter': 1000}
        )

        if result.success:
            optimal_weights = result.x
            portfolio_return = np.dot(optimal_weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(optimal_weights, np.dot(covariance_matrix, optimal_weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0

            return OptimizationResult(
                weights=optimal_weights,
                expected_return=portfolio_return,
                risk=portfolio_risk,
                sharpe_ratio=sharpe_ratio,
                status="SUCCESS",
                constraints_satisfied=True,
                optimization_info={
                    "method": "Utility Maximization",
                    "risk_aversion": risk_aversion,
                    "iterations": result.nit
                }
            )
        else:
            raise ValueError(f"Optimization failed: {result.message}")

    def _optimize_risk_parity(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        constraints: Dict[str, Any],
        available_capital: float,
        risk_aversion: float
    ) -> OptimizationResult:
        """Optimize portfolio for equal risk contribution (risk parity)"""
        n_assets = len(expected_returns)

        def risk_parity_objective(weights):
            """Risk parity objective: minimize sum of squared differences in risk contributions"""
            portfolio_risk = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))

            if portfolio_risk == 0:
                return 1e6

            # Calculate marginal risk contributions
            marginal_contribs = np.dot(covariance_matrix, weights) / portfolio_risk

            # Risk contributions
            risk_contribs = weights * marginal_contribs

            # Target: equal risk contribution
            target_contrib = portfolio_risk / n_assets

            # Objective: minimize squared deviations from equal risk contribution
            return np.sum((risk_contribs - target_contrib) ** 2)

        # Constraints
        scipy_constraints = []

        # Weights sum to 1 constraint
        scipy_constraints.append({
            'type': 'eq',
            'fun': lambda weights: np.sum(weights) - 1.0
        })

        # Initial guess: equal weights
        initial_weights = np.ones(n_assets) / n_assets

        # Optimize
        result = optimize.minimize(
            fun=risk_parity_objective,
            x0=initial_weights,
            method='SLSQP',
            bounds=constraints["bounds"],
            constraints=scipy_constraints,
            options={'maxiter': 1000}
        )

        if result.success:
            optimal_weights = result.x
            portfolio_return = np.dot(optimal_weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(optimal_weights, np.dot(covariance_matrix, optimal_weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0

            return OptimizationResult(
                weights=optimal_weights,
                expected_return=portfolio_return,
                risk=portfolio_risk,
                sharpe_ratio=sharpe_ratio,
                status="SUCCESS",
                constraints_satisfied=True,
                optimization_info={
                    "method": "Risk Parity",
                    "iterations": result.nit
                }
            )
        else:
            raise ValueError(f"Optimization failed: {result.message}")

    def _optimize_mean_variance(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        constraints: Dict[str, Any],
        available_capital: float,
        risk_aversion: float
    ) -> OptimizationResult:
        """Classic mean-variance optimization (Markowitz)"""
        # This is equivalent to utility maximization with quadratic utility
        return self._optimize_utility(
            expected_returns, covariance_matrix, constraints,
            available_capital, risk_aversion
        )

    def _validate_optimization_result(
        self,
        result: OptimizationResult,
        constraints: Dict[str, Any]
    ) -> OptimizationResult:
        """Validate optimization result against constraints"""
        # Check weight bounds
        bounds = constraints.get("bounds", [])
        if bounds:
            for i, (lower, upper) in enumerate(bounds):
                if result.weights[i] < lower - 1e-6 or result.weights[i] > upper + 1e-6:
                    result.constraints_satisfied = False
                    break

        # Check weight sum
        weight_sum = np.sum(result.weights)
        if abs(weight_sum - 1.0) > 1e-6:
            result.constraints_satisfied = False

        # Check risk constraint
        if "max_portfolio_risk" in constraints:
            if result.risk > constraints["max_portfolio_risk"] + 1e-6:
                result.constraints_satisfied = False

        return result

    def _fallback_optimization(
        self,
        n_assets: int,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray
    ) -> OptimizationResult:
        """Fallback to equal-weight portfolio if optimization fails"""
        weights = np.ones(n_assets) / n_assets
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_risk = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0

        return OptimizationResult(
            weights=weights,
            expected_return=portfolio_return,
            risk=portfolio_risk,
            sharpe_ratio=sharpe_ratio,
            status="FALLBACK_EQUAL_WEIGHT",
            constraints_satisfied=True,
            optimization_info={"method": "Equal Weight Fallback"}
        )

    def efficient_frontier(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        num_points: int = 100,
        constraints: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate efficient frontier

        Args:
            expected_returns: Expected returns for each asset
            covariance_matrix: Covariance matrix
            num_points: Number of points on the frontier
            constraints: Portfolio constraints

        Returns:
            Tuple of (expected_returns, risks, sharpe_ratios) for efficient frontier
        """
        min_return = np.min(expected_returns)
        max_return = np.max(expected_returns)

        target_returns = np.linspace(min_return, max_return, num_points)
        efficient_risks = []
        efficient_returns = []
        efficient_sharpes = []

        for target_return in target_returns:
            try:
                # Add return target constraint
                target_constraints = constraints.copy() if constraints else []
                target_constraints.append({
                    "type": "target_return",
                    "value": target_return
                })

                result = self._optimize_risk_with_return_target(
                    expected_returns, covariance_matrix, target_return, constraints
                )

                efficient_returns.append(result.expected_return)
                efficient_risks.append(result.risk)
                efficient_sharpes.append(result.sharpe_ratio)

            except:
                # Skip if optimization fails for this target return
                continue

        return (
            np.array(efficient_returns),
            np.array(efficient_risks),
            np.array(efficient_sharpes)
        )

    def _optimize_risk_with_return_target(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        target_return: float,
        constraints: Optional[List[Dict[str, Any]]] = None
    ) -> OptimizationResult:
        """Minimize risk subject to target return constraint"""
        n_assets = len(expected_returns)

        def portfolio_risk(weights):
            return np.dot(weights, np.dot(covariance_matrix, weights))

        # Constraints
        scipy_constraints = []

        # Weights sum to 1 constraint
        scipy_constraints.append({
            'type': 'eq',
            'fun': lambda weights: np.sum(weights) - 1.0
        })

        # Target return constraint
        scipy_constraints.append({
            'type': 'eq',
            'fun': lambda weights: np.dot(weights, expected_returns) - target_return
        })

        # Parse additional constraints
        parsed_constraints = self._parse_constraints(constraints, n_assets)

        # Initial guess: equal weights
        initial_weights = np.ones(n_assets) / n_assets

        # Optimize
        result = optimize.minimize(
            fun=portfolio_risk,
            x0=initial_weights,
            method='SLSQP',
            bounds=parsed_constraints["bounds"],
            constraints=scipy_constraints,
            options={'maxiter': 1000}
        )

        if result.success:
            optimal_weights = result.x
            portfolio_return = np.dot(optimal_weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(optimal_weights, np.dot(covariance_matrix, optimal_weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0

            return OptimizationResult(
                weights=optimal_weights,
                expected_return=portfolio_return,
                risk=portfolio_risk,
                sharpe_ratio=sharpe_ratio,
                status="SUCCESS",
                constraints_satisfied=True,
                optimization_info={"method": "Risk Minimization with Return Target"}
            )
        else:
            raise ValueError(f"Optimization failed: {result.message}")


class RiskModel:
    """
    Risk modeling utilities for portfolio optimization
    Implements various risk estimation and decomposition methods
    """

    def __init__(self):
        pass

    def estimate_var(
        self,
        returns: np.ndarray,
        confidence_level: float = 0.05,
        method: str = "historical"
    ) -> float:
        """
        Estimate Value at Risk (VaR)

        Args:
            returns: Historical returns
            confidence_level: Confidence level (e.g., 0.05 for 95% VaR)
            method: Estimation method ("historical", "parametric", "monte_carlo")

        Returns:
            VaR estimate
        """
        if method == "historical":
            return np.percentile(returns, confidence_level * 100)

        elif method == "parametric":
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            return norm.ppf(confidence_level, mean_return, std_return)

        elif method == "monte_carlo":
            # Monte Carlo simulation
            n_simulations = 10000
            simulated_returns = np.random.normal(
                np.mean(returns), np.std(returns), n_simulations
            )
            return np.percentile(simulated_returns, confidence_level * 100)

        else:
            raise ValueError(f"Unknown VaR method: {method}")

    def estimate_expected_shortfall(
        self,
        returns: np.ndarray,
        confidence_level: float = 0.05
    ) -> float:
        """
        Estimate Expected Shortfall (Conditional VaR)

        Args:
            returns: Historical returns
            confidence_level: Confidence level

        Returns:
            Expected Shortfall estimate
        """
        var = self.estimate_var(returns, confidence_level, "historical")
        return np.mean(returns[returns <= var])

    def calculate_risk_decomposition(
        self,
        weights: np.ndarray,
        covariance_matrix: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """
        Decompose portfolio risk into individual contributions

        Args:
            weights: Portfolio weights
            covariance_matrix: Asset covariance matrix

        Returns:
            Risk decomposition metrics
        """
        portfolio_variance = np.dot(weights, np.dot(covariance_matrix, weights))
        portfolio_risk = np.sqrt(portfolio_variance)

        # Marginal risk contributions
        marginal_contribs = np.dot(covariance_matrix, weights) / portfolio_risk

        # Component risk contributions
        component_contribs = weights * marginal_contribs

        # Percentage risk contributions
        percent_contribs = component_contribs / portfolio_risk

        return {
            "marginal_contributions": marginal_contribs,
            "component_contributions": component_contribs,
            "percentage_contributions": percent_contribs,
            "portfolio_risk": portfolio_risk
        }

    def estimate_correlation_matrix(
        self,
        returns_matrix: np.ndarray,
        method: str = "pearson"
    ) -> np.ndarray:
        """
        Estimate correlation matrix from returns

        Args:
            returns_matrix: Matrix of asset returns (assets in columns)
            method: Correlation estimation method

        Returns:
            Correlation matrix
        """
        if method == "pearson":
            return np.corrcoef(returns_matrix, rowvar=False)

        elif method == "spearman":
            from scipy.stats import spearmanr
            corr_matrix, _ = spearmanr(returns_matrix)
            return corr_matrix

        elif method == "kendall":
            from scipy.stats import kendalltau
            n_assets = returns_matrix.shape[1]
            corr_matrix = np.eye(n_assets)

            for i in range(n_assets):
                for j in range(i + 1, n_assets):
                    tau, _ = kendalltau(returns_matrix[:, i], returns_matrix[:, j])
                    corr_matrix[i, j] = tau
                    corr_matrix[j, i] = tau

            return corr_matrix

        else:
            raise ValueError(f"Unknown correlation method: {method}")

    def stress_test_portfolio(
        self,
        weights: np.ndarray,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        stress_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform stress testing on portfolio

        Args:
            weights: Portfolio weights
            expected_returns: Expected returns
            covariance_matrix: Covariance matrix
            stress_scenarios: List of stress scenarios

        Returns:
            Stress test results
        """
        baseline_return = np.dot(weights, expected_returns)
        baseline_risk = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))

        stress_results = {
            "baseline": {
                "return": baseline_return,
                "risk": baseline_risk
            },
            "scenarios": {}
        }

        for scenario in stress_scenarios:
            scenario_name = scenario["name"]
            stressed_returns = expected_returns.copy()
            stressed_covariance = covariance_matrix.copy()

            # Apply stress to returns
            if "return_shocks" in scenario:
                for asset_idx, shock in scenario["return_shocks"].items():
                    stressed_returns[asset_idx] += shock

            # Apply stress to volatilities
            if "volatility_shocks" in scenario:
                for asset_idx, shock_multiplier in scenario["volatility_shocks"].items():
                    # Increase volatility
                    old_vol = np.sqrt(stressed_covariance[asset_idx, asset_idx])
                    new_vol = old_vol * shock_multiplier

                    # Update covariance matrix
                    vol_ratio = new_vol / old_vol
                    stressed_covariance[asset_idx, :] *= vol_ratio
                    stressed_covariance[:, asset_idx] *= vol_ratio

            # Calculate stressed portfolio metrics
            stressed_return = np.dot(weights, stressed_returns)
            stressed_risk = np.sqrt(np.dot(weights, np.dot(stressed_covariance, weights)))

            stress_results["scenarios"][scenario_name] = {
                "return": stressed_return,
                "risk": stressed_risk,
                "return_impact": stressed_return - baseline_return,
                "risk_impact": stressed_risk - baseline_risk
            }

        return stress_results


class PerformanceAnalyzer:
    """
    Portfolio performance analysis utilities
    Calculates comprehensive performance metrics and attribution
    """

    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate

    def calculate_performance_metrics(
        self,
        portfolio_returns: np.ndarray,
        benchmark_returns: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Calculate comprehensive performance metrics

        Args:
            portfolio_returns: Portfolio return time series
            benchmark_returns: Benchmark return time series

        Returns:
            Dictionary of performance metrics
        """
        metrics = {}

        # Basic return metrics
        metrics["total_return"] = np.prod(1 + portfolio_returns) - 1
        metrics["annualized_return"] = np.mean(portfolio_returns) * 252  # Assuming daily returns
        metrics["volatility"] = np.std(portfolio_returns) * np.sqrt(252)

        # Risk-adjusted metrics
        if metrics["volatility"] > 0:
            metrics["sharpe_ratio"] = (metrics["annualized_return"] - self.risk_free_rate) / metrics["volatility"]
        else:
            metrics["sharpe_ratio"] = 0

        # Drawdown metrics
        cumulative_returns = np.cumprod(1 + portfolio_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max

        metrics["max_drawdown"] = np.min(drawdown)
        metrics["current_drawdown"] = drawdown[-1]

        # Downside metrics
        negative_returns = portfolio_returns[portfolio_returns < 0]
        if len(negative_returns) > 0:
            metrics["downside_deviation"] = np.std(negative_returns) * np.sqrt(252)
            metrics["sortino_ratio"] = (metrics["annualized_return"] - self.risk_free_rate) / metrics["downside_deviation"]
        else:
            metrics["downside_deviation"] = 0
            metrics["sortino_ratio"] = np.inf

        # VaR and Expected Shortfall
        metrics["var_95"] = np.percentile(portfolio_returns, 5)
        metrics["expected_shortfall_95"] = np.mean(portfolio_returns[portfolio_returns <= metrics["var_95"]])

        # Benchmark-relative metrics
        if benchmark_returns is not None and len(benchmark_returns) == len(portfolio_returns):
            excess_returns = portfolio_returns - benchmark_returns

            metrics["alpha"] = np.mean(excess_returns) * 252
            metrics["tracking_error"] = np.std(excess_returns) * np.sqrt(252)

            if metrics["tracking_error"] > 0:
                metrics["information_ratio"] = metrics["alpha"] / metrics["tracking_error"]
            else:
                metrics["information_ratio"] = 0

            # Beta calculation
            covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)

            if benchmark_variance > 0:
                metrics["beta"] = covariance / benchmark_variance
            else:
                metrics["beta"] = 0

        return metrics

    def attribution_analysis(
        self,
        portfolio_weights: np.ndarray,
        asset_returns: np.ndarray,
        benchmark_weights: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Perform return attribution analysis

        Args:
            portfolio_weights: Portfolio weights over time
            asset_returns: Individual asset returns
            benchmark_weights: Benchmark weights (if available)

        Returns:
            Attribution analysis results
        """
        n_periods, n_assets = asset_returns.shape

        attribution = {
            "total_return": 0,
            "asset_allocation_effect": np.zeros(n_assets),
            "security_selection_effect": np.zeros(n_assets),
            "interaction_effect": np.zeros(n_assets)
        }

        if benchmark_weights is None:
            # Use equal weights as benchmark
            benchmark_weights = np.ones((n_periods, n_assets)) / n_assets

        for t in range(n_periods):
            # Portfolio return
            portfolio_return = np.dot(portfolio_weights[t], asset_returns[t])
            attribution["total_return"] += portfolio_return

            # Benchmark return
            benchmark_return = np.dot(benchmark_weights[t], asset_returns[t])

            # Weight differences
            weight_diff = portfolio_weights[t] - benchmark_weights[t]

            # Benchmark asset returns
            benchmark_asset_return = asset_returns[t]

            # Average benchmark return
            avg_benchmark_return = np.mean(benchmark_asset_return)

            # Attribution effects
            attribution["asset_allocation_effect"] += weight_diff * (benchmark_asset_return - avg_benchmark_return)
            attribution["security_selection_effect"] += benchmark_weights[t] * (asset_returns[t] - benchmark_asset_return)
            attribution["interaction_effect"] += weight_diff * (asset_returns[t] - benchmark_asset_return)

        return attribution

    def rolling_performance_analysis(
        self,
        portfolio_returns: np.ndarray,
        window_size: int = 252,  # 1 year window
        benchmark_returns: Optional[np.ndarray] = None
    ) -> Dict[str, np.ndarray]:
        """
        Calculate rolling performance metrics

        Args:
            portfolio_returns: Portfolio return time series
            window_size: Rolling window size
            benchmark_returns: Benchmark returns

        Returns:
            Rolling performance metrics
        """
        n_periods = len(portfolio_returns)
        n_windows = n_periods - window_size + 1

        rolling_metrics = {
            "rolling_return": np.zeros(n_windows),
            "rolling_volatility": np.zeros(n_windows),
            "rolling_sharpe": np.zeros(n_windows),
            "rolling_max_drawdown": np.zeros(n_windows)
        }

        if benchmark_returns is not None:
            rolling_metrics["rolling_alpha"] = np.zeros(n_windows)
            rolling_metrics["rolling_beta"] = np.zeros(n_windows)

        for i in range(n_windows):
            window_returns = portfolio_returns[i:i + window_size]

            # Calculate metrics for this window
            rolling_metrics["rolling_return"][i] = np.mean(window_returns) * 252
            rolling_metrics["rolling_volatility"][i] = np.std(window_returns) * np.sqrt(252)

            if rolling_metrics["rolling_volatility"][i] > 0:
                rolling_metrics["rolling_sharpe"][i] = (
                    rolling_metrics["rolling_return"][i] - self.risk_free_rate
                ) / rolling_metrics["rolling_volatility"][i]

            # Rolling max drawdown
            cumulative = np.cumprod(1 + window_returns)
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            rolling_metrics["rolling_max_drawdown"][i] = np.min(drawdown)

            # Benchmark-relative metrics
            if benchmark_returns is not None:
                window_benchmark = benchmark_returns[i:i + window_size]
                excess_returns = window_returns - window_benchmark

                rolling_metrics["rolling_alpha"][i] = np.mean(excess_returns) * 252

                # Rolling beta
                covariance = np.cov(window_returns, window_benchmark)[0, 1]
                benchmark_variance = np.var(window_benchmark)

                if benchmark_variance > 0:
                    rolling_metrics["rolling_beta"][i] = covariance / benchmark_variance

        return rolling_metrics