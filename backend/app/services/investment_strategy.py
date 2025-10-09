"""
Investment Strategy Optimization Service
Handles arbitrage analysis, portfolio optimization, and risk management
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from ..models.arbitrage import (
    AnnouncedDeal, ArbitragePosition, InvestmentPortfolio,
    DealUpdate, PortfolioSnapshot, PortfolioRebalancing,
    DealStatus, ArbitrageStrategy, RiskLevel, PortfolioStrategy
)
from ..models.opportunities import MarketOpportunity
from ..utils.portfolio_optimization import (
    PortfolioOptimizer, RiskModel, PerformanceAnalyzer
)

logger = logging.getLogger(__name__)


class ArbitrageAnalysisService:
    """
    Service for analyzing M&A arbitrage opportunities
    Calculates spreads, risks, and expected returns
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_arbitrage_spread(
        self,
        deal: AnnouncedDeal,
        current_target_price: float,
        current_acquirer_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate arbitrage spread and expected returns for a deal

        Args:
            deal: AnnouncedDeal instance
            current_target_price: Current market price of target
            current_acquirer_price: Current market price of acquirer (for stock deals)

        Returns:
            Dictionary with spread analysis
        """
        analysis = {
            "deal_id": str(deal.id),
            "target_company": deal.target_company,
            "deal_type": deal.deal_type,
            "gross_spread": None,
            "gross_spread_percentage": None,
            "risk_adjusted_spread": None,
            "annualized_return": None,
            "risk_factors": {},
            "recommendation": "HOLD"
        }

        try:
            # Calculate gross spread based on deal type
            if deal.deal_type.lower() == "cash":
                # Cash deal: spread = offer price - current price
                if deal.price_per_share and current_target_price:
                    gross_spread = float(deal.price_per_share) - current_target_price
                    gross_spread_percentage = gross_spread / current_target_price

                    analysis.update({
                        "gross_spread": gross_spread,
                        "gross_spread_percentage": gross_spread_percentage,
                        "offer_price": float(deal.price_per_share),
                        "current_price": current_target_price
                    })

            elif deal.deal_type.lower() in ["stock", "mixed"] and deal.exchange_ratio:
                # Stock deal: spread = (acquirer_price * ratio) - target_price
                if current_acquirer_price and current_target_price:
                    implied_value = current_acquirer_price * float(deal.exchange_ratio)
                    gross_spread = implied_value - current_target_price
                    gross_spread_percentage = gross_spread / current_target_price

                    analysis.update({
                        "gross_spread": gross_spread,
                        "gross_spread_percentage": gross_spread_percentage,
                        "implied_value": implied_value,
                        "exchange_ratio": float(deal.exchange_ratio),
                        "acquirer_price": current_acquirer_price,
                        "target_price": current_target_price
                    })

            # Calculate risk-adjusted spread
            if analysis["gross_spread_percentage"]:
                risk_adjustment = self._calculate_risk_adjustment(deal)
                analysis["risk_adjusted_spread"] = analysis["gross_spread_percentage"] * (1 - risk_adjustment)

            # Calculate annualized return
            if analysis["gross_spread_percentage"] and deal.expected_close_date:
                days_to_close = (deal.expected_close_date - date.today()).days
                if days_to_close > 0:
                    annualized_return = (analysis["gross_spread_percentage"] * 365) / days_to_close
                    analysis["annualized_return"] = annualized_return

            # Risk factor analysis
            analysis["risk_factors"] = self._analyze_risk_factors(deal)

            # Generate recommendation
            analysis["recommendation"] = self._generate_recommendation(analysis, deal)

        except Exception as e:
            logger.error(f"Error calculating arbitrage spread for deal {deal.id}: {e}")
            analysis["error"] = str(e)

        return analysis

    def _calculate_risk_adjustment(self, deal: AnnouncedDeal) -> float:
        """Calculate risk adjustment factor based on deal characteristics"""
        risk_factors = []

        # Regulatory risk
        if deal.regulatory_risk == RiskLevel.HIGH:
            risk_factors.append(0.3)
        elif deal.regulatory_risk == RiskLevel.MEDIUM:
            risk_factors.append(0.15)
        else:
            risk_factors.append(0.05)

        # Deal break risk
        if deal.deal_break_risk == RiskLevel.HIGH:
            risk_factors.append(0.25)
        elif deal.deal_break_risk == RiskLevel.MEDIUM:
            risk_factors.append(0.1)
        else:
            risk_factors.append(0.02)

        # Financing risk
        if deal.financing_risk == RiskLevel.HIGH:
            risk_factors.append(0.2)
        elif deal.financing_risk == RiskLevel.MEDIUM:
            risk_factors.append(0.08)
        else:
            risk_factors.append(0.01)

        # Time risk (deals taking longer have higher risk)
        if deal.days_to_close:
            if deal.days_to_close > 365:
                risk_factors.append(0.15)
            elif deal.days_to_close > 180:
                risk_factors.append(0.08)
            else:
                risk_factors.append(0.02)

        # Overall risk adjustment is max of individual risks
        return min(max(risk_factors), 0.8)  # Cap at 80% risk adjustment

    def _analyze_risk_factors(self, deal: AnnouncedDeal) -> Dict[str, Any]:
        """Analyze various risk factors for the deal"""
        risks = {
            "regulatory_approval": {
                "level": deal.regulatory_risk,
                "description": "Risk of regulatory approval delays or rejections"
            },
            "financing": {
                "level": deal.financing_risk,
                "description": "Risk of financing falling through"
            },
            "deal_break": {
                "level": deal.deal_break_risk,
                "description": "Risk of deal termination"
            },
            "timeline": {
                "level": "LOW" if deal.days_to_close and deal.days_to_close < 90 else "MEDIUM",
                "description": f"Expected timeline: {deal.days_to_close} days"
            }
        }

        # Add completion probability assessment
        if deal.completion_probability:
            if deal.completion_probability > 0.8:
                risks["completion"] = {"level": "LOW", "probability": deal.completion_probability}
            elif deal.completion_probability > 0.6:
                risks["completion"] = {"level": "MEDIUM", "probability": deal.completion_probability}
            else:
                risks["completion"] = {"level": "HIGH", "probability": deal.completion_probability}

        return risks

    def _generate_recommendation(self, analysis: Dict[str, Any], deal: AnnouncedDeal) -> str:
        """Generate buy/hold/sell recommendation based on analysis"""
        if not analysis.get("annualized_return"):
            return "INSUFFICIENT_DATA"

        annualized_return = analysis["annualized_return"]
        risk_adjusted_return = analysis.get("risk_adjusted_spread", 0)

        # Risk-return based recommendations
        if annualized_return > 0.15 and risk_adjusted_return > 0.05:  # 15% annual, 5% risk-adjusted
            return "STRONG_BUY"
        elif annualized_return > 0.08 and risk_adjusted_return > 0.03:  # 8% annual, 3% risk-adjusted
            return "BUY"
        elif annualized_return > 0.04:  # 4% annual return
            return "HOLD"
        else:
            return "AVOID"

    def scan_arbitrage_opportunities(
        self,
        organization_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Scan for new arbitrage opportunities based on criteria

        Args:
            organization_id: Organization ID for multi-tenancy
            filters: Optional filters for opportunity scanning

        Returns:
            List of arbitrage opportunities with analysis
        """
        filters = filters or {}

        query = self.db.query(AnnouncedDeal).filter(
            AnnouncedDeal.organization_id == organization_id,
            AnnouncedDeal.current_status.in_([
                DealStatus.ANNOUNCED,
                DealStatus.REGULATORY_REVIEW,
                DealStatus.SHAREHOLDER_APPROVAL
            ])
        )

        # Apply filters
        if "min_deal_value" in filters:
            query = query.filter(AnnouncedDeal.deal_value >= filters["min_deal_value"])

        if "max_days_to_close" in filters:
            cutoff_date = date.today() + timedelta(days=filters["max_days_to_close"])
            query = query.filter(AnnouncedDeal.expected_close_date <= cutoff_date)

        if "min_completion_probability" in filters:
            query = query.filter(AnnouncedDeal.completion_probability >= filters["min_completion_probability"])

        deals = query.all()
        opportunities = []

        for deal in deals:
            # Get current market prices (would integrate with market data provider)
            current_target_price = self._get_current_price(deal.target_ticker)
            current_acquirer_price = self._get_current_price(deal.acquirer_ticker) if deal.acquirer_ticker else None

            if current_target_price:
                analysis = self.calculate_arbitrage_spread(deal, current_target_price, current_acquirer_price)

                # Filter by minimum return threshold
                min_return = filters.get("min_annualized_return", 0.05)  # 5% default
                if analysis.get("annualized_return", 0) >= min_return:
                    opportunities.append(analysis)

        # Sort by risk-adjusted return
        opportunities.sort(key=lambda x: x.get("risk_adjusted_spread", 0), reverse=True)

        return opportunities

    def _get_current_price(self, ticker: Optional[str]) -> Optional[float]:
        """
        Get current market price for a ticker
        In production, this would integrate with market data providers
        """
        if not ticker:
            return None

        # Placeholder implementation
        # In production, integrate with:
        # - Bloomberg API
        # - Reuters
        # - Alpha Vantage
        # - Yahoo Finance
        # - IEX Cloud

        return None  # Would return actual market price

    def update_deal_probability(
        self,
        deal_id: str,
        organization_id: str,
        new_probability: float,
        reason: str
    ) -> bool:
        """Update deal completion probability based on new information"""
        try:
            deal = self.db.query(AnnouncedDeal).filter(
                AnnouncedDeal.id == deal_id,
                AnnouncedDeal.organization_id == organization_id
            ).first()

            if not deal:
                return False

            old_probability = deal.completion_probability
            deal.completion_probability = new_probability

            # Create update record
            update = DealUpdate(
                announced_deal_id=deal_id,
                update_type="probability_change",
                update_title=f"Completion probability updated to {new_probability:.1%}",
                update_content=f"Previous: {old_probability:.1%}, New: {new_probability:.1%}. Reason: {reason}",
                impact_on_probability=new_probability - (old_probability or 0),
                source_type="analyst_update"
            )

            self.db.add(update)
            self.db.commit()

            return True

        except Exception as e:
            logger.error(f"Error updating deal probability: {e}")
            self.db.rollback()
            return False


class PortfolioOptimizationService:
    """
    Service for portfolio optimization and allocation
    Implements modern portfolio theory for arbitrage strategies
    """

    def __init__(self, db: Session):
        self.db = db
        self.optimizer = PortfolioOptimizer()
        self.risk_model = RiskModel()
        self.performance_analyzer = PerformanceAnalyzer()

    def optimize_portfolio_allocation(
        self,
        portfolio_id: str,
        opportunities: List[Dict[str, Any]],
        optimization_objective: str = "sharpe_ratio"
    ) -> Dict[str, Any]:
        """
        Optimize portfolio allocation across arbitrage opportunities

        Args:
            portfolio_id: Portfolio to optimize
            opportunities: List of available arbitrage opportunities
            optimization_objective: Optimization target (sharpe_ratio, return, risk)

        Returns:
            Optimized allocation recommendations
        """
        portfolio = self.db.query(InvestmentPortfolio).filter(
            InvestmentPortfolio.id == portfolio_id
        ).first()

        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")

        # Prepare optimization inputs
        expected_returns = []
        risk_estimates = []
        correlation_matrix = None
        constraints = []

        for opp in opportunities:
            expected_returns.append(opp.get("annualized_return", 0))
            risk_estimates.append(self._estimate_position_risk(opp))

        # Generate correlation matrix
        correlation_matrix = self._estimate_correlation_matrix(opportunities)

        # Portfolio constraints
        constraints = self._get_portfolio_constraints(portfolio)

        # Perform optimization
        optimization_result = self.optimizer.optimize(
            expected_returns=np.array(expected_returns),
            risk_estimates=np.array(risk_estimates),
            correlation_matrix=correlation_matrix,
            constraints=constraints,
            objective=optimization_objective,
            available_capital=float(portfolio.available_capital)
        )

        # Format results
        allocation_result = {
            "portfolio_id": portfolio_id,
            "optimization_objective": optimization_objective,
            "total_expected_return": optimization_result["expected_return"],
            "total_risk": optimization_result["risk"],
            "sharpe_ratio": optimization_result["sharpe_ratio"],
            "allocations": [],
            "constraints_satisfied": optimization_result["constraints_satisfied"],
            "optimization_status": optimization_result["status"]
        }

        # Individual position allocations
        for i, (opp, weight) in enumerate(zip(opportunities, optimization_result["weights"])):
            if weight > 0.001:  # Only include meaningful allocations
                allocation = {
                    "deal_id": opp["deal_id"],
                    "target_company": opp["target_company"],
                    "weight": weight,
                    "capital_allocation": weight * float(portfolio.available_capital),
                    "expected_return": opp.get("annualized_return", 0),
                    "estimated_risk": risk_estimates[i],
                    "recommendation": opp.get("recommendation", "HOLD")
                }
                allocation_result["allocations"].append(allocation)

        return allocation_result

    def _estimate_position_risk(self, opportunity: Dict[str, Any]) -> float:
        """Estimate risk for individual arbitrage position"""
        base_risk = 0.1  # 10% base risk

        # Adjust based on risk factors
        risk_factors = opportunity.get("risk_factors", {})

        for factor, details in risk_factors.items():
            risk_level = details.get("level", "MEDIUM")
            if risk_level == "HIGH":
                base_risk += 0.05
            elif risk_level == "VERY_HIGH":
                base_risk += 0.1

        # Adjust based on time to close
        if opportunity.get("days_to_close"):
            days = opportunity["days_to_close"]
            if days > 365:
                base_risk += 0.03
            elif days < 30:
                base_risk += 0.02  # Very short deals have execution risk

        return min(base_risk, 0.5)  # Cap at 50% risk

    def _estimate_correlation_matrix(self, opportunities: List[Dict[str, Any]]) -> np.ndarray:
        """Estimate correlation matrix between arbitrage opportunities"""
        n = len(opportunities)
        correlation_matrix = np.eye(n)  # Start with identity matrix

        # Add correlations based on:
        # 1. Same industry
        # 2. Same acquirer
        # 3. Same regulatory environment
        # 4. Market conditions

        for i in range(n):
            for j in range(i + 1, n):
                correlation = 0.0

                # Industry correlation
                # Would implement based on industry classifications

                # Same acquirer correlation
                if opportunities[i].get("acquirer_company") == opportunities[j].get("acquirer_company"):
                    correlation += 0.3

                # Timeline correlation (deals closing at similar times)
                days_i = opportunities[i].get("days_to_close", 180)
                days_j = opportunities[j].get("days_to_close", 180)
                if abs(days_i - days_j) < 30:
                    correlation += 0.1

                correlation_matrix[i, j] = correlation
                correlation_matrix[j, i] = correlation

        return correlation_matrix

    def _get_portfolio_constraints(self, portfolio: InvestmentPortfolio) -> List[Dict[str, Any]]:
        """Get portfolio constraints for optimization"""
        constraints = []

        # Maximum position size constraint
        if portfolio.max_position_size:
            constraints.append({
                "type": "max_weight",
                "value": float(portfolio.max_position_size)
            })

        # Maximum sector exposure (would need sector mapping)
        if portfolio.max_sector_exposure:
            constraints.append({
                "type": "max_sector_exposure",
                "value": float(portfolio.max_sector_exposure)
            })

        # Risk budget constraint
        if portfolio.risk_tolerance:
            risk_limit = {
                "LOW": 0.1,
                "MEDIUM": 0.2,
                "HIGH": 0.35
            }.get(portfolio.risk_tolerance, 0.2)

            constraints.append({
                "type": "max_portfolio_risk",
                "value": risk_limit
            })

        return constraints

    def rebalance_portfolio(
        self,
        portfolio_id: str,
        trigger_type: str,
        rebalancing_threshold: float = 0.05
    ) -> Dict[str, Any]:
        """
        Rebalance portfolio based on drift from target allocation

        Args:
            portfolio_id: Portfolio to rebalance
            trigger_type: What triggered the rebalancing
            rebalancing_threshold: Minimum drift to trigger rebalancing

        Returns:
            Rebalancing recommendations and actions
        """
        portfolio = self.db.query(InvestmentPortfolio).filter(
            InvestmentPortfolio.id == portfolio_id
        ).first()

        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")

        # Get current positions
        current_positions = self.db.query(ArbitragePosition).filter(
            ArbitragePosition.portfolio_id == portfolio_id,
            ArbitragePosition.is_active == True
        ).all()

        # Calculate current allocation vs target
        current_allocation = self._calculate_current_allocation(current_positions)
        target_allocation = self._get_target_allocation(portfolio_id)

        # Check if rebalancing is needed
        allocation_drift = self._calculate_allocation_drift(current_allocation, target_allocation)

        rebalancing_needed = any(
            abs(drift) > rebalancing_threshold
            for drift in allocation_drift.values()
        )

        rebalancing_result = {
            "portfolio_id": portfolio_id,
            "rebalancing_needed": rebalancing_needed,
            "trigger_type": trigger_type,
            "current_allocation": current_allocation,
            "target_allocation": target_allocation,
            "allocation_drift": allocation_drift,
            "actions": []
        }

        if rebalancing_needed:
            # Generate rebalancing actions
            actions = self._generate_rebalancing_actions(
                current_positions, current_allocation, target_allocation
            )
            rebalancing_result["actions"] = actions

            # Record rebalancing decision
            self._record_rebalancing_decision(portfolio_id, trigger_type, rebalancing_result)

        return rebalancing_result

    def _calculate_current_allocation(self, positions: List[ArbitragePosition]) -> Dict[str, float]:
        """Calculate current portfolio allocation"""
        total_value = sum(float(pos.notional_value or 0) for pos in positions)

        if total_value == 0:
            return {}

        allocation = {}
        for position in positions:
            deal_id = str(position.announced_deal_id)
            weight = float(position.notional_value or 0) / total_value
            allocation[deal_id] = weight

        return allocation

    def _get_target_allocation(self, portfolio_id: str) -> Dict[str, float]:
        """Get target allocation for portfolio (from last optimization)"""
        # In production, this would retrieve the most recent optimization result
        # For now, return empty dict
        return {}

    def _calculate_allocation_drift(
        self,
        current: Dict[str, float],
        target: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate drift between current and target allocation"""
        drift = {}

        all_positions = set(current.keys()) | set(target.keys())

        for position in all_positions:
            current_weight = current.get(position, 0)
            target_weight = target.get(position, 0)
            drift[position] = current_weight - target_weight

        return drift

    def _generate_rebalancing_actions(
        self,
        current_positions: List[ArbitragePosition],
        current_allocation: Dict[str, float],
        target_allocation: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Generate specific rebalancing actions"""
        actions = []

        # Implementation would generate specific buy/sell orders
        # to move from current to target allocation

        return actions

    def _record_rebalancing_decision(
        self,
        portfolio_id: str,
        trigger_type: str,
        rebalancing_result: Dict[str, Any]
    ):
        """Record rebalancing decision in database"""
        rebalancing_record = PortfolioRebalancing(
            portfolio_id=portfolio_id,
            rebalancing_date=date.today(),
            trigger_type=trigger_type,
            trigger_description=f"Automatic rebalancing triggered by {trigger_type}",
            pre_allocations=rebalancing_result["current_allocation"],
            post_allocations=rebalancing_result["target_allocation"]
        )

        self.db.add(rebalancing_record)
        self.db.commit()


class RiskManagementService:
    """
    Service for portfolio risk management and monitoring
    Implements comprehensive risk controls and monitoring
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_portfolio_risk(
        self,
        portfolio_id: str,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive portfolio risk metrics

        Args:
            portfolio_id: Portfolio to analyze
            confidence_level: Confidence level for VaR calculation

        Returns:
            Portfolio risk analysis
        """
        portfolio = self.db.query(InvestmentPortfolio).filter(
            InvestmentPortfolio.id == portfolio_id
        ).first()

        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")

        # Get active positions
        positions = self.db.query(ArbitragePosition).filter(
            ArbitragePosition.portfolio_id == portfolio_id,
            ArbitragePosition.is_active == True
        ).all()

        risk_analysis = {
            "portfolio_id": portfolio_id,
            "analysis_date": datetime.now().isoformat(),
            "total_value": float(portfolio.current_capital),
            "number_of_positions": len(positions),
            "risk_metrics": {},
            "concentration_risks": {},
            "stress_tests": {},
            "risk_limits": {}
        }

        # Calculate basic risk metrics
        risk_analysis["risk_metrics"] = self._calculate_basic_risk_metrics(positions)

        # Concentration risk analysis
        risk_analysis["concentration_risks"] = self._analyze_concentration_risks(positions)

        # Stress testing
        risk_analysis["stress_tests"] = self._perform_stress_tests(positions)

        # Risk limit monitoring
        risk_analysis["risk_limits"] = self._check_risk_limits(portfolio, positions)

        return risk_analysis

    def _calculate_basic_risk_metrics(self, positions: List[ArbitragePosition]) -> Dict[str, Any]:
        """Calculate basic portfolio risk metrics"""
        if not positions:
            return {}

        # Portfolio value and P&L
        total_value = sum(float(pos.notional_value or 0) for pos in positions)
        total_pnl = sum(float(pos.total_pnl or 0) for pos in positions)
        unrealized_pnl = sum(float(pos.unrealized_pnl or 0) for pos in positions)

        # Calculate portfolio volatility (simplified)
        position_returns = []
        for pos in positions:
            if pos.pnl_percentage:
                position_returns.append(float(pos.pnl_percentage))

        volatility = np.std(position_returns) if position_returns else 0

        # Value at Risk (simplified calculation)
        var_95 = np.percentile(position_returns, 5) * total_value if position_returns else 0

        return {
            "total_value": total_value,
            "total_pnl": total_pnl,
            "unrealized_pnl": unrealized_pnl,
            "portfolio_volatility": volatility,
            "value_at_risk_95": abs(var_95),
            "expected_shortfall": abs(var_95) * 1.2,  # Simplified ES calculation
            "worst_position_loss": min(position_returns) if position_returns else 0
        }

    def _analyze_concentration_risks(self, positions: List[ArbitragePosition]) -> Dict[str, Any]:
        """Analyze portfolio concentration risks"""
        if not positions:
            return {}

        total_value = sum(float(pos.notional_value or 0) for pos in positions)

        # Position concentration
        position_weights = [float(pos.notional_value or 0) / total_value for pos in positions]
        position_weights.sort(reverse=True)

        concentration_metrics = {
            "largest_position": position_weights[0] if position_weights else 0,
            "top_3_concentration": sum(position_weights[:3]) if len(position_weights) >= 3 else sum(position_weights),
            "top_5_concentration": sum(position_weights[:5]) if len(position_weights) >= 5 else sum(position_weights),
            "herfindahl_index": sum(w**2 for w in position_weights)
        }

        # Industry/Sector concentration (would require industry mapping)
        # Geographic concentration (would require geographic mapping)
        # Acquirer concentration
        acquirer_exposure = {}
        for pos in positions:
            if hasattr(pos, 'announced_deal') and pos.announced_deal:
                acquirer = pos.announced_deal.acquirer_company
                weight = float(pos.notional_value or 0) / total_value
                acquirer_exposure[acquirer] = acquirer_exposure.get(acquirer, 0) + weight

        concentration_metrics["max_acquirer_exposure"] = max(acquirer_exposure.values()) if acquirer_exposure else 0

        return concentration_metrics

    def _perform_stress_tests(self, positions: List[ArbitragePosition]) -> Dict[str, Any]:
        """Perform portfolio stress tests"""
        stress_scenarios = {
            "deal_break_shock": self._stress_deal_breaks(positions),
            "market_crash": self._stress_market_crash(positions),
            "credit_crisis": self._stress_credit_crisis(positions),
            "regulatory_shock": self._stress_regulatory_shock(positions)
        }

        return stress_scenarios

    def _stress_deal_breaks(self, positions: List[ArbitragePosition]) -> Dict[str, Any]:
        """Stress test: What if deals break?"""
        total_value = sum(float(pos.notional_value or 0) for pos in positions)

        # Assume 20% of deals break, losing full spread
        stressed_loss = 0
        for pos in positions:
            if pos.entry_spread_percentage:
                potential_loss = float(pos.notional_value or 0) * float(pos.entry_spread_percentage) * 0.2
                stressed_loss += potential_loss

        return {
            "scenario": "20% of deals break",
            "estimated_loss": stressed_loss,
            "loss_percentage": stressed_loss / total_value if total_value > 0 else 0
        }

    def _stress_market_crash(self, positions: List[ArbitragePosition]) -> Dict[str, Any]:
        """Stress test: Market crash scenario"""
        # Simplified: assume 30% market decline affects all positions
        total_value = sum(float(pos.notional_value or 0) for pos in positions)
        market_impact = total_value * 0.15  # Arbitrage partially protected

        return {
            "scenario": "30% market decline",
            "estimated_loss": market_impact,
            "loss_percentage": 0.15
        }

    def _stress_credit_crisis(self, positions: List[ArbitragePosition]) -> Dict[str, Any]:
        """Stress test: Credit crisis affecting deal financing"""
        # Count positions with financing risk
        financing_risk_positions = 0
        financing_risk_value = 0

        for pos in positions:
            if hasattr(pos, 'announced_deal') and pos.announced_deal:
                if pos.announced_deal.financing_risk in ['HIGH', 'VERY_HIGH']:
                    financing_risk_positions += 1
                    financing_risk_value += float(pos.notional_value or 0)

        return {
            "scenario": "Credit crisis affects financing",
            "positions_at_risk": financing_risk_positions,
            "value_at_risk": financing_risk_value,
            "estimated_loss": financing_risk_value * 0.4  # 40% loss on financing-risk deals
        }

    def _stress_regulatory_shock(self, positions: List[ArbitragePosition]) -> Dict[str, Any]:
        """Stress test: Regulatory environment tightens"""
        regulatory_risk_value = 0

        for pos in positions:
            if hasattr(pos, 'announced_deal') and pos.announced_deal:
                if pos.announced_deal.regulatory_risk in ['HIGH', 'VERY_HIGH']:
                    regulatory_risk_value += float(pos.notional_value or 0)

        return {
            "scenario": "Regulatory environment tightens",
            "value_at_risk": regulatory_risk_value,
            "estimated_loss": regulatory_risk_value * 0.3  # 30% loss on high regulatory risk
        }

    def _check_risk_limits(
        self,
        portfolio: InvestmentPortfolio,
        positions: List[ArbitragePosition]
    ) -> Dict[str, Any]:
        """Check portfolio against risk limits"""
        limit_checks = {
            "position_size_limit": True,
            "sector_concentration_limit": True,
            "overall_risk_limit": True,
            "leverage_limit": True,
            "liquidity_limit": True
        }

        # Check maximum position size
        if portfolio.max_position_size and positions:
            total_value = sum(float(pos.notional_value or 0) for pos in positions)
            max_position_value = max(float(pos.notional_value or 0) for pos in positions)
            max_position_percentage = max_position_value / total_value if total_value > 0 else 0

            limit_checks["position_size_limit"] = max_position_percentage <= float(portfolio.max_position_size)
            limit_checks["max_position_percentage"] = max_position_percentage
            limit_checks["max_position_limit"] = float(portfolio.max_position_size)

        return limit_checks

    def generate_risk_alerts(
        self,
        portfolio_id: str,
        risk_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate risk alerts based on analysis"""
        alerts = []

        # Check for limit breaches
        risk_limits = risk_analysis.get("risk_limits", {})

        if not risk_limits.get("position_size_limit", True):
            alerts.append({
                "type": "POSITION_SIZE_BREACH",
                "severity": "HIGH",
                "message": f"Position size limit breached: {risk_limits.get('max_position_percentage', 0):.1%} > {risk_limits.get('max_position_limit', 0):.1%}",
                "action_required": "Reduce largest position size"
            })

        # Check concentration risks
        concentration = risk_analysis.get("concentration_risks", {})

        if concentration.get("largest_position", 0) > 0.2:  # 20% concentration threshold
            alerts.append({
                "type": "CONCENTRATION_RISK",
                "severity": "MEDIUM",
                "message": f"High concentration in single position: {concentration['largest_position']:.1%}",
                "action_required": "Consider diversification"
            })

        # Check stress test results
        stress_tests = risk_analysis.get("stress_tests", {})

        for scenario, results in stress_tests.items():
            loss_percentage = results.get("loss_percentage", 0)
            if loss_percentage > 0.15:  # 15% loss threshold
                alerts.append({
                    "type": "STRESS_TEST_FAILURE",
                    "severity": "MEDIUM",
                    "message": f"High loss in {scenario}: {loss_percentage:.1%}",
                    "action_required": "Review position sizing and hedging"
                })

        return alerts