"""
Financial Modeling Engine for M&A Transactions
DCF, LBO, Comparables, and Scenario Analysis
"""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ModelAssumptions:
    """Base assumptions for financial models"""
    projection_years: int = 5
    terminal_growth_rate: float = 0.025
    tax_rate: float = 0.21
    working_capital_pct_revenue: float = 0.10
    capex_pct_revenue: float = 0.03
    depreciation_pct_revenue: float = 0.02

@dataclass
class DCFInputs:
    """Inputs for DCF model"""
    revenue_base: float
    revenue_growth_rates: List[float]
    ebitda_margins: List[float]
    wacc: float
    terminal_growth: float
    tax_rate: float
    nwc_pct_revenue: float
    capex_pct_revenue: float

@dataclass
class LBOInputs:
    """Inputs for LBO model"""
    purchase_price: float
    equity_pct: float
    debt_cost: float
    exit_multiple: float
    holding_period: int
    revenue_base: float
    revenue_growth_rates: List[float]
    ebitda_margins: List[float]
    tax_rate: float

class FinancialModelingEngine:
    """
    Comprehensive financial modeling engine for M&A transactions
    """

    def __init__(self):
        self.assumptions = ModelAssumptions()

    def dcf_model(self, inputs: DCFInputs) -> Dict[str, Any]:
        """
        Discounted Cash Flow valuation model
        """
        try:
            # Build revenue projections
            revenues = self._project_revenues(
                inputs.revenue_base,
                inputs.revenue_growth_rates
            )

            # Calculate EBITDA
            ebitda = [rev * margin for rev, margin in zip(revenues, inputs.ebitda_margins)]

            # Calculate EBIT (EBITDA - D&A)
            depreciation = [rev * self.assumptions.depreciation_pct_revenue for rev in revenues]
            ebit = [e - d for e, d in zip(ebitda, depreciation)]

            # Calculate NOPAT (EBIT * (1 - tax))
            nopat = [e * (1 - inputs.tax_rate) for e in ebit]

            # Add back depreciation
            cash_flow_ops = [n + d for n, d in zip(nopat, depreciation)]

            # Subtract CapEx
            capex = [rev * inputs.capex_pct_revenue for rev in revenues]

            # Calculate change in NWC
            nwc_levels = [rev * inputs.nwc_pct_revenue for rev in revenues]
            nwc_changes = [0] + [nwc_levels[i] - nwc_levels[i-1] for i in range(1, len(nwc_levels))]

            # Calculate FCFF (Free Cash Flow to Firm)
            fcff = [cf - cx - nwc for cf, cx, nwc in zip(cash_flow_ops, capex, nwc_changes)]

            # Calculate terminal value
            terminal_fcf = fcff[-1] * (1 + inputs.terminal_growth)
            terminal_value = terminal_fcf / (inputs.wacc - inputs.terminal_growth)

            # Discount cash flows
            discount_factors = [(1 / (1 + inputs.wacc) ** i) for i in range(1, len(fcff) + 1)]
            pv_fcff = [cf * df for cf, df in zip(fcff, discount_factors)]

            # Discount terminal value
            pv_terminal = terminal_value * discount_factors[-1]

            # Calculate enterprise value
            enterprise_value = sum(pv_fcff) + pv_terminal

            # Sensitivity analysis
            sensitivity = self._dcf_sensitivity_analysis(
                inputs,
                enterprise_value
            )

            return {
                "enterprise_value": enterprise_value,
                "terminal_value": terminal_value,
                "fcff": fcff,
                "pv_fcff": pv_fcff,
                "pv_terminal": pv_terminal,
                "revenues": revenues,
                "ebitda": ebitda,
                "wacc": inputs.wacc,
                "terminal_growth": inputs.terminal_growth,
                "sensitivity_analysis": sensitivity,
                "implied_ebitda_multiple": enterprise_value / ebitda[0] if ebitda[0] > 0 else None,
                "implied_revenue_multiple": enterprise_value / revenues[0] if revenues[0] > 0 else None
            }

        except Exception as e:
            logger.error(f"DCF model error: {str(e)}")
            raise

    def lbo_model(self, inputs: LBOInputs) -> Dict[str, Any]:
        """
        Leveraged Buyout model with returns analysis
        """
        try:
            # Calculate initial capital structure
            equity_investment = inputs.purchase_price * inputs.equity_pct
            debt_amount = inputs.purchase_price * (1 - inputs.equity_pct)

            # Build projections
            revenues = self._project_revenues(
                inputs.revenue_base,
                inputs.revenue_growth_rates[:inputs.holding_period]
            )

            ebitda = [rev * margin for rev, margin in
                     zip(revenues, inputs.ebitda_margins[:inputs.holding_period])]

            # Calculate debt service
            interest_expense = [debt_amount * inputs.debt_cost for _ in range(inputs.holding_period)]

            # Simple debt paydown schedule (could be more sophisticated)
            annual_paydown = debt_amount * 0.1  # 10% annual paydown
            debt_schedule = [debt_amount - (annual_paydown * i)
                           for i in range(inputs.holding_period + 1)]

            # Calculate exit value
            exit_ebitda = ebitda[-1]
            exit_enterprise_value = exit_ebitda * inputs.exit_multiple
            exit_debt = debt_schedule[-1]
            exit_equity_value = exit_enterprise_value - exit_debt

            # Calculate returns
            irr = self._calculate_irr(
                -equity_investment,
                exit_equity_value,
                inputs.holding_period
            )

            moic = exit_equity_value / equity_investment if equity_investment > 0 else 0

            # Build sources and uses
            sources_uses = {
                "sources": {
                    "equity": equity_investment,
                    "debt": debt_amount,
                    "total": inputs.purchase_price
                },
                "uses": {
                    "purchase_price": inputs.purchase_price,
                    "fees": inputs.purchase_price * 0.02,  # 2% transaction fees
                    "total": inputs.purchase_price * 1.02
                }
            }

            # Sensitivity on exit multiple and EBITDA growth
            irr_sensitivity = self._lbo_sensitivity_analysis(
                inputs,
                equity_investment,
                debt_schedule[-1]
            )

            return {
                "equity_investment": equity_investment,
                "debt_amount": debt_amount,
                "leverage_ratio": debt_amount / ebitda[0] if ebitda[0] > 0 else None,
                "exit_enterprise_value": exit_enterprise_value,
                "exit_equity_value": exit_equity_value,
                "irr": irr,
                "moic": moic,
                "revenues": revenues,
                "ebitda": ebitda,
                "debt_schedule": debt_schedule,
                "sources_uses": sources_uses,
                "sensitivity_analysis": irr_sensitivity,
                "credit_metrics": {
                    "debt_to_ebitda": [d / e if e > 0 else None
                                      for d, e in zip(debt_schedule[:-1], ebitda)],
                    "ebitda_to_interest": [e / i if i > 0 else None
                                          for e, i in zip(ebitda, interest_expense)]
                }
            }

        except Exception as e:
            logger.error(f"LBO model error: {str(e)}")
            raise

    def comparable_company_analysis(
        self,
        target_metrics: Dict[str, float],
        comparables: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Comparable company valuation analysis
        """
        try:
            if not comparables:
                raise ValueError("No comparable companies provided")

            # Calculate multiples for comparables
            comp_multiples = []
            for comp in comparables:
                multiples = {
                    "company": comp.get("name", "Unknown"),
                    "ev_revenue": comp["enterprise_value"] / comp["revenue"] if comp.get("revenue") else None,
                    "ev_ebitda": comp["enterprise_value"] / comp["ebitda"] if comp.get("ebitda") else None,
                    "ev_ebit": comp["enterprise_value"] / comp["ebit"] if comp.get("ebit") else None,
                    "pe_ratio": comp["market_cap"] / comp["net_income"] if comp.get("net_income") else None
                }
                comp_multiples.append(multiples)

            # Calculate statistics for each multiple
            stats = {}
            for multiple_type in ["ev_revenue", "ev_ebitda", "ev_ebit", "pe_ratio"]:
                values = [m[multiple_type] for m in comp_multiples if m[multiple_type] is not None]
                if values:
                    stats[multiple_type] = {
                        "mean": np.mean(values),
                        "median": np.median(values),
                        "25th_percentile": np.percentile(values, 25),
                        "75th_percentile": np.percentile(values, 75),
                        "min": np.min(values),
                        "max": np.max(values),
                        "std": np.std(values)
                    }

            # Apply multiples to target
            valuations = {}
            if "revenue" in target_metrics and "ev_revenue" in stats:
                valuations["ev_from_revenue"] = {
                    "mean": target_metrics["revenue"] * stats["ev_revenue"]["mean"],
                    "median": target_metrics["revenue"] * stats["ev_revenue"]["median"],
                    "range": [
                        target_metrics["revenue"] * stats["ev_revenue"]["25th_percentile"],
                        target_metrics["revenue"] * stats["ev_revenue"]["75th_percentile"]
                    ]
                }

            if "ebitda" in target_metrics and "ev_ebitda" in stats:
                valuations["ev_from_ebitda"] = {
                    "mean": target_metrics["ebitda"] * stats["ev_ebitda"]["mean"],
                    "median": target_metrics["ebitda"] * stats["ev_ebitda"]["median"],
                    "range": [
                        target_metrics["ebitda"] * stats["ev_ebitda"]["25th_percentile"],
                        target_metrics["ebitda"] * stats["ev_ebitda"]["75th_percentile"]
                    ]
                }

            # Calculate football field valuation range
            all_valuations = []
            for method, values in valuations.items():
                all_valuations.extend([values["mean"], values["median"]])
                all_valuations.extend(values["range"])

            if all_valuations:
                valuation_range = {
                    "low": np.min(all_valuations),
                    "high": np.max(all_valuations),
                    "midpoint": np.median(all_valuations)
                }
            else:
                valuation_range = None

            return {
                "comparable_multiples": comp_multiples,
                "multiple_statistics": stats,
                "target_valuations": valuations,
                "valuation_range": valuation_range,
                "selected_comps_count": len(comparables)
            }

        except Exception as e:
            logger.error(f"Comparable analysis error: {str(e)}")
            raise

    def precedent_transaction_analysis(
        self,
        target_metrics: Dict[str, float],
        precedent_deals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Precedent transaction valuation analysis
        """
        try:
            if not precedent_deals:
                raise ValueError("No precedent transactions provided")

            # Calculate multiples for precedent transactions
            precedent_multiples = []
            for deal in precedent_deals:
                multiples = {
                    "deal": deal.get("target_name", "Unknown"),
                    "date": deal.get("announcement_date"),
                    "ev_revenue": deal["deal_value"] / deal["target_revenue"] if deal.get("target_revenue") else None,
                    "ev_ebitda": deal["deal_value"] / deal["target_ebitda"] if deal.get("target_ebitda") else None,
                    "premium": deal.get("premium_paid"),
                    "strategic_buyer": deal.get("buyer_type") == "strategic"
                }
                precedent_multiples.append(multiples)

            # Calculate statistics with time weighting (more recent = higher weight)
            stats = self._calculate_weighted_statistics(precedent_multiples)

            # Apply to target with control premium
            control_premium = 1.25  # 25% control premium
            valuations = {}

            if "revenue" in target_metrics and stats.get("ev_revenue"):
                valuations["ev_from_revenue"] = {
                    "base": target_metrics["revenue"] * stats["ev_revenue"]["weighted_mean"],
                    "with_premium": target_metrics["revenue"] * stats["ev_revenue"]["weighted_mean"] * control_premium
                }

            if "ebitda" in target_metrics and stats.get("ev_ebitda"):
                valuations["ev_from_ebitda"] = {
                    "base": target_metrics["ebitda"] * stats["ev_ebitda"]["weighted_mean"],
                    "with_premium": target_metrics["ebitda"] * stats["ev_ebitda"]["weighted_mean"] * control_premium
                }

            return {
                "precedent_multiples": precedent_multiples,
                "multiple_statistics": stats,
                "target_valuations": valuations,
                "average_premium": np.mean([d["premium"] for d in precedent_multiples
                                           if d.get("premium") is not None]),
                "transaction_count": len(precedent_deals)
            }

        except Exception as e:
            logger.error(f"Precedent transaction analysis error: {str(e)}")
            raise

    def monte_carlo_simulation(
        self,
        base_case: Dict[str, Any],
        variables: Dict[str, Dict[str, float]],
        iterations: int = 10000
    ) -> Dict[str, Any]:
        """
        Monte Carlo simulation for valuation uncertainty
        """
        try:
            results = []

            for _ in range(iterations):
                # Sample from distributions for each variable
                scenario = {}
                for var_name, var_params in variables.items():
                    if var_params["distribution"] == "normal":
                        value = np.random.normal(
                            var_params["mean"],
                            var_params["std"]
                        )
                    elif var_params["distribution"] == "uniform":
                        value = np.random.uniform(
                            var_params["min"],
                            var_params["max"]
                        )
                    elif var_params["distribution"] == "triangular":
                        value = np.random.triangular(
                            var_params["min"],
                            var_params["mode"],
                            var_params["max"]
                        )
                    else:
                        value = var_params["mean"]

                    scenario[var_name] = value

                # Calculate valuation for this scenario
                if "dcf" in base_case:
                    # Recalculate DCF with sampled parameters
                    inputs = DCFInputs(
                        revenue_base=base_case["revenue_base"],
                        revenue_growth_rates=[scenario.get("revenue_growth", 0.05)] * 5,
                        ebitda_margins=[scenario.get("ebitda_margin", 0.20)] * 5,
                        wacc=scenario.get("wacc", 0.10),
                        terminal_growth=scenario.get("terminal_growth", 0.025),
                        tax_rate=scenario.get("tax_rate", 0.21),
                        nwc_pct_revenue=0.10,
                        capex_pct_revenue=0.03
                    )
                    dcf_result = self.dcf_model(inputs)
                    results.append(dcf_result["enterprise_value"])

            # Calculate statistics
            results_array = np.array(results)
            percentiles = np.percentile(results_array, [5, 25, 50, 75, 95])

            return {
                "iterations": iterations,
                "mean": np.mean(results_array),
                "std": np.std(results_array),
                "min": np.min(results_array),
                "max": np.max(results_array),
                "percentiles": {
                    "5th": percentiles[0],
                    "25th": percentiles[1],
                    "50th": percentiles[2],
                    "75th": percentiles[3],
                    "95th": percentiles[4]
                },
                "probability_above_base": np.mean(results_array > base_case.get("base_value", 0)),
                "var_95": percentiles[0],  # Value at Risk (5th percentile)
                "histogram_data": np.histogram(results_array, bins=50)
            }

        except Exception as e:
            logger.error(f"Monte Carlo simulation error: {str(e)}")
            raise

    def merger_model(
        self,
        acquirer: Dict[str, float],
        target: Dict[str, float],
        deal_terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merger model with accretion/dilution analysis
        """
        try:
            # Calculate combined entity metrics
            combined_revenue = acquirer["revenue"] + target["revenue"]
            combined_ebitda = acquirer["ebitda"] + target["ebitda"]

            # Add synergies
            revenue_synergies = combined_revenue * deal_terms.get("revenue_synergy_pct", 0)
            cost_synergies = combined_ebitda * deal_terms.get("cost_synergy_pct", 0)

            pro_forma_revenue = combined_revenue + revenue_synergies
            pro_forma_ebitda = combined_ebitda + cost_synergies

            # Calculate financing impact
            if deal_terms["consideration_type"] == "cash":
                # Cash deal - calculate interest expense
                cash_used = deal_terms["purchase_price"]
                debt_raised = cash_used * deal_terms.get("debt_financing_pct", 0.5)
                interest_expense = debt_raised * deal_terms.get("debt_cost", 0.05)

                # Impact on EPS
                pro_forma_net_income = (pro_forma_ebitda - acquirer.get("depreciation", 0)
                                       - target.get("depreciation", 0) - interest_expense) * (1 - 0.21)
                pro_forma_shares = acquirer["shares_outstanding"]

            elif deal_terms["consideration_type"] == "stock":
                # Stock deal - calculate dilution
                exchange_ratio = deal_terms.get("exchange_ratio", 1.0)
                new_shares_issued = target["shares_outstanding"] * exchange_ratio
                pro_forma_shares = acquirer["shares_outstanding"] + new_shares_issued

                pro_forma_net_income = (pro_forma_ebitda - acquirer.get("depreciation", 0)
                                       - target.get("depreciation", 0)) * (1 - 0.21)

            else:  # Mixed consideration
                # Simplified mixed calculation
                cash_portion = deal_terms["purchase_price"] * deal_terms.get("cash_pct", 0.5)
                stock_portion = deal_terms["purchase_price"] * (1 - deal_terms.get("cash_pct", 0.5))

                debt_raised = cash_portion * 0.5
                interest_expense = debt_raised * deal_terms.get("debt_cost", 0.05)

                new_shares_value = stock_portion
                new_shares_issued = new_shares_value / acquirer["share_price"]
                pro_forma_shares = acquirer["shares_outstanding"] + new_shares_issued

                pro_forma_net_income = (pro_forma_ebitda - acquirer.get("depreciation", 0)
                                       - target.get("depreciation", 0) - interest_expense) * (1 - 0.21)

            # Calculate accretion/dilution
            acquirer_eps = acquirer["net_income"] / acquirer["shares_outstanding"]
            pro_forma_eps = pro_forma_net_income / pro_forma_shares
            eps_accretion = (pro_forma_eps - acquirer_eps) / acquirer_eps

            return {
                "pro_forma_revenue": pro_forma_revenue,
                "pro_forma_ebitda": pro_forma_ebitda,
                "pro_forma_net_income": pro_forma_net_income,
                "pro_forma_eps": pro_forma_eps,
                "acquirer_eps": acquirer_eps,
                "eps_accretion_pct": eps_accretion * 100,
                "is_accretive": eps_accretion > 0,
                "pro_forma_shares": pro_forma_shares,
                "synergies": {
                    "revenue": revenue_synergies,
                    "cost": cost_synergies,
                    "total": revenue_synergies + cost_synergies
                },
                "payback_period": deal_terms["purchase_price"] / (revenue_synergies + cost_synergies)
                                  if (revenue_synergies + cost_synergies) > 0 else None
            }

        except Exception as e:
            logger.error(f"Merger model error: {str(e)}")
            raise

    # Helper methods
    def _project_revenues(
        self,
        base: float,
        growth_rates: List[float]
    ) -> List[float]:
        """Project revenues based on growth rates"""
        revenues = [base]
        for rate in growth_rates:
            revenues.append(revenues[-1] * (1 + rate))
        return revenues[1:]  # Return projected years only

    def _calculate_irr(
        self,
        initial_investment: float,
        exit_value: float,
        years: int
    ) -> float:
        """Simple IRR calculation"""
        if initial_investment >= 0:
            return 0.0
        return (exit_value / abs(initial_investment)) ** (1 / years) - 1

    def _dcf_sensitivity_analysis(
        self,
        inputs: DCFInputs,
        base_ev: float
    ) -> Dict[str, Any]:
        """Sensitivity analysis for DCF model"""
        wacc_range = np.arange(inputs.wacc - 0.02, inputs.wacc + 0.02, 0.005)
        terminal_growth_range = np.arange(inputs.terminal_growth - 0.01, inputs.terminal_growth + 0.01, 0.0025)

        sensitivity_matrix = []
        for tg in terminal_growth_range:
            row = []
            for wacc in wacc_range:
                modified_inputs = DCFInputs(
                    revenue_base=inputs.revenue_base,
                    revenue_growth_rates=inputs.revenue_growth_rates,
                    ebitda_margins=inputs.ebitda_margins,
                    wacc=wacc,
                    terminal_growth=tg,
                    tax_rate=inputs.tax_rate,
                    nwc_pct_revenue=inputs.nwc_pct_revenue,
                    capex_pct_revenue=inputs.capex_pct_revenue
                )
                result = self.dcf_model(modified_inputs)
                row.append(result["enterprise_value"])
            sensitivity_matrix.append(row)

        return {
            "wacc_range": wacc_range.tolist(),
            "terminal_growth_range": terminal_growth_range.tolist(),
            "valuation_matrix": sensitivity_matrix,
            "base_case": base_ev
        }

    def _lbo_sensitivity_analysis(
        self,
        inputs: LBOInputs,
        equity_investment: float,
        exit_debt: float
    ) -> Dict[str, Any]:
        """Sensitivity analysis for LBO model"""
        exit_multiple_range = np.arange(inputs.exit_multiple - 2, inputs.exit_multiple + 2, 0.5)
        ebitda_growth_range = np.arange(-0.05, 0.15, 0.025)

        irr_matrix = []
        for growth in ebitda_growth_range:
            row = []
            for multiple in exit_multiple_range:
                # Calculate exit EBITDA with growth
                exit_ebitda = inputs.revenue_base * (1 + growth) ** inputs.holding_period * inputs.ebitda_margins[-1]
                exit_ev = exit_ebitda * multiple
                exit_equity = exit_ev - exit_debt

                irr = self._calculate_irr(-equity_investment, exit_equity, inputs.holding_period)
                row.append(irr)
            irr_matrix.append(row)

        return {
            "exit_multiple_range": exit_multiple_range.tolist(),
            "ebitda_growth_range": ebitda_growth_range.tolist(),
            "irr_matrix": irr_matrix
        }

    def _calculate_weighted_statistics(
        self,
        multiples: List[Dict]
    ) -> Dict[str, Dict]:
        """Calculate time-weighted statistics for precedent transactions"""
        stats = {}

        for metric in ["ev_revenue", "ev_ebitda"]:
            values = []
            weights = []

            for m in multiples:
                if m.get(metric) is not None:
                    values.append(m[metric])
                    # Weight by recency (if date available)
                    if m.get("date"):
                        days_ago = (datetime.now() - m["date"]).days if isinstance(m["date"], datetime) else 365
                        weight = max(0.1, 1 - (days_ago / 1095))  # 3-year decay
                    else:
                        weight = 0.5
                    weights.append(weight)

            if values:
                values = np.array(values)
                weights = np.array(weights)
                weights = weights / weights.sum()  # Normalize

                stats[metric] = {
                    "weighted_mean": np.average(values, weights=weights),
                    "median": np.median(values),
                    "std": np.std(values)
                }

        return stats