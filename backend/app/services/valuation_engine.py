"""
Valuation Engine Service
Comprehensive financial modeling and valuation for M&A transactions
Supports DCF, Comparable Company, Precedent Transaction, and LBO analyses
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
import logging

from ..models.financial_models import (
    ValuationModel, DCFModel, ComparableCompanyAnalysis,
    PrecedentTransactionAnalysis, LBOModel, MarketDataSnapshot,
    ValuationMethod, ScenarioType, TerminalValueMethod
)
from ..utils.financial_calculations import (
    calculate_wacc, calculate_cost_of_equity, calculate_terminal_value_perpetuity,
    calculate_terminal_value_exit_multiple, project_revenue, calculate_free_cash_flow,
    calculate_enterprise_value_from_dcf, calculate_equity_value, calculate_lbo_returns,
    calculate_comparable_multiples_stats, apply_control_premium, apply_marketability_discount,
    sensitivity_analysis, two_way_sensitivity_analysis, monte_carlo_valuation
)

logger = logging.getLogger(__name__)


class DCFValuationService:
    """Discounted Cash Flow valuation service"""

    def __init__(self, db: Session):
        self.db = db

    def create_dcf_model(
        self,
        valuation_id: str,
        organization_id: str,
        inputs: Dict[str, Any],
        scenario_type: ScenarioType = ScenarioType.BASE
    ) -> DCFModel:
        """
        Create and calculate DCF valuation model

        Args:
            valuation_id: Parent valuation ID
            organization_id: Organization ID
            inputs: Model inputs and assumptions
            scenario_type: Scenario type (base, optimistic, pessimistic)

        Returns:
            Calculated DCFModel
        """
        # Extract inputs
        projection_years = inputs.get("projection_years", 5)
        base_revenue = inputs["base_revenue"]
        revenue_growth_rates = inputs.get("revenue_growth_rates", [10, 8, 7, 6, 5])
        ebitda_margin = inputs.get("ebitda_margin", 20.0)
        tax_rate = inputs.get("tax_rate", 25.0)
        capex_percent_revenue = inputs.get("capex_percent_revenue", 3.0)
        depreciation_percent_revenue = inputs.get("depreciation_percent_revenue", 2.5)
        nwc_percent_revenue = inputs.get("nwc_percent_revenue", 10.0)

        # WACC components
        risk_free_rate = inputs.get("risk_free_rate", 4.0)
        beta = inputs.get("beta", 1.2)
        market_risk_premium = inputs.get("market_risk_premium", 6.0)
        cost_of_debt = inputs.get("cost_of_debt", 5.0)
        debt_to_equity = inputs.get("debt_to_equity", 0.5)

        # Terminal value
        terminal_value_method = inputs.get("terminal_value_method", TerminalValueMethod.PERPETUITY_GROWTH)
        terminal_growth_rate = inputs.get("terminal_growth_rate", 2.5)
        exit_multiple = inputs.get("exit_multiple", 10.0)

        # Calculate cost of equity
        cost_of_equity = calculate_cost_of_equity(
            risk_free_rate,
            beta,
            market_risk_premium
        )

        # Calculate WACC
        wacc = calculate_wacc(
            cost_of_equity,
            cost_of_debt,
            tax_rate,
            debt_to_equity
        )

        # Project revenues
        revenues = project_revenue(base_revenue, revenue_growth_rates, projection_years)

        # Calculate EBITDA projections
        ebitdas = [rev * (ebitda_margin / 100) for rev in revenues]

        # Calculate depreciation
        depreciations = [rev * (depreciation_percent_revenue / 100) for rev in revenues]

        # Calculate EBIT
        ebits = [ebitda - dep for ebitda, dep in zip(ebitdas, depreciations)]

        # Calculate NOPAT (Net Operating Profit After Tax)
        nopats = [ebit * (1 - tax_rate / 100) for ebit in ebits]

        # Calculate CapEx
        capexes = [rev * (capex_percent_revenue / 100) for rev in revenues]

        # Calculate working capital changes
        nwc_changes = []
        for i in range(len(revenues)):
            if i == 0:
                nwc_change = revenues[0] * (nwc_percent_revenue / 100)
            else:
                nwc_change = (revenues[i] - revenues[i-1]) * (nwc_percent_revenue / 100)
            nwc_changes.append(nwc_change)

        # Calculate Free Cash Flows
        free_cash_flows = []
        for i in range(len(revenues)):
            fcf = calculate_free_cash_flow(
                ebitdas[i],
                depreciations[i],
                tax_rate,
                capexes[i],
                nwc_changes[i]
            )
            free_cash_flows.append(fcf)

        # Calculate Terminal Value
        if terminal_value_method == TerminalValueMethod.PERPETUITY_GROWTH:
            terminal_value = calculate_terminal_value_perpetuity(
                free_cash_flows[-1],
                wacc,
                terminal_growth_rate
            )
        else:  # Exit multiple method
            terminal_value = calculate_terminal_value_exit_multiple(
                ebitdas[-1],
                exit_multiple
            )

        # Calculate Enterprise Value
        dcf_result = calculate_enterprise_value_from_dcf(
            free_cash_flows,
            terminal_value,
            wacc
        )

        enterprise_value = dcf_result["enterprise_value"]

        # Calculate Equity Value
        net_debt = inputs.get("net_debt", 0)
        equity_value = calculate_equity_value(
            enterprise_value,
            cash=inputs.get("cash", 0),
            debt=inputs.get("debt", net_debt)
        )

        # Create DCF model
        dcf_model = DCFModel(
            valuation_id=valuation_id,
            organization_id=organization_id,
            scenario_type=scenario_type,
            projection_years=projection_years,
            terminal_value_method=terminal_value_method,
            risk_free_rate=Decimal(str(risk_free_rate)),
            market_risk_premium=Decimal(str(market_risk_premium)),
            beta=Decimal(str(beta)),
            cost_of_equity=Decimal(str(cost_of_equity)),
            cost_of_debt=Decimal(str(cost_of_debt)),
            tax_rate=Decimal(str(tax_rate)),
            debt_to_equity=Decimal(str(debt_to_equity)),
            wacc=Decimal(str(wacc)),
            terminal_growth_rate=Decimal(str(terminal_growth_rate)) if terminal_value_method == TerminalValueMethod.PERPETUITY_GROWTH else None,
            exit_multiple=Decimal(str(exit_multiple)) if terminal_value_method == TerminalValueMethod.EXIT_MULTIPLE else None,
            terminal_value=Decimal(str(terminal_value)),
            enterprise_value=Decimal(str(enterprise_value)),
            equity_value=Decimal(str(equity_value)),
            net_debt=Decimal(str(net_debt)),
            revenue_projections=revenues,
            ebitda_projections=ebitdas,
            ebit_projections=ebits,
            nopat_projections=nopats,
            capex_projections=capexes,
            depreciation_projections=depreciations,
            working_capital_changes=nwc_changes,
            free_cash_flows=free_cash_flows,
            discount_factors=dcf_result["discount_factors"],
            present_values=dcf_result["pv_cash_flows"],
            revenue_growth_rates=revenue_growth_rates,
            ebitda_margin=Decimal(str(ebitda_margin)),
            capex_percent_revenue=Decimal(str(capex_percent_revenue)),
            working_capital_percent_revenue=Decimal(str(nwc_percent_revenue))
        )

        self.db.add(dcf_model)
        self.db.commit()
        self.db.refresh(dcf_model)

        return dcf_model

    def run_sensitivity_analysis(
        self,
        dcf_model: DCFModel,
        parameter: str,
        value_range: List[float]
    ) -> Dict[str, Any]:
        """
        Run sensitivity analysis on DCF model

        Args:
            dcf_model: DCF model to analyze
            parameter: Parameter to vary (wacc, terminal_growth_rate, etc.)
            value_range: Range of values to test

        Returns:
            Sensitivity analysis results
        """
        # Reconstruct inputs from DCF model
        base_assumptions = {
            "wacc": float(dcf_model.wacc),
            "terminal_growth_rate": float(dcf_model.terminal_growth_rate) if dcf_model.terminal_growth_rate else 2.5,
            "ebitda_margin": float(dcf_model.ebitda_margin),
        }

        # Valuation function
        def valuation_func(assumptions):
            # Recalculate with new assumption
            free_cash_flows = dcf_model.free_cash_flows

            if parameter == "terminal_growth_rate":
                terminal_value = calculate_terminal_value_perpetuity(
                    free_cash_flows[-1],
                    assumptions["wacc"],
                    assumptions["terminal_growth_rate"]
                )
            else:
                terminal_value = float(dcf_model.terminal_value)

            dcf_result = calculate_enterprise_value_from_dcf(
                free_cash_flows,
                terminal_value,
                assumptions.get("wacc", float(dcf_model.wacc))
            )

            return dcf_result["enterprise_value"]

        results = sensitivity_analysis(
            base_assumptions,
            parameter,
            value_range,
            valuation_func
        )

        return results


class ComparableCompanyService:
    """Comparable Company Analysis service"""

    def __init__(self, db: Session):
        self.db = db

    def create_comparable_analysis(
        self,
        valuation_id: str,
        organization_id: str,
        industry: str,
        comparable_companies: List[Dict[str, Any]],
        target_metrics: Dict[str, float],
        adjustments: Optional[Dict[str, float]] = None
    ) -> ComparableCompanyAnalysis:
        """
        Create comparable company analysis

        Args:
            valuation_id: Parent valuation ID
            organization_id: Organization ID
            industry: Industry sector
            comparable_companies: List of comparable company data
            target_metrics: Target company financial metrics
            adjustments: Size premium, liquidity discount, control premium

        Returns:
            ComparableCompanyAnalysis model
        """
        if adjustments is None:
            adjustments = {}

        # Calculate summary statistics
        stats = calculate_comparable_multiples_stats(comparable_companies)

        # Select median multiples (conservative approach)
        selected_ev_revenue = stats["ev_revenue"]["median"] if stats["ev_revenue"] else None
        selected_ev_ebitda = stats["ev_ebitda"]["median"] if stats["ev_ebitda"] else None
        selected_pe = stats["pe"]["median"] if stats["pe"] else None

        # Apply adjustments
        size_premium = adjustments.get("size_premium", 0)
        liquidity_discount = adjustments.get("liquidity_discount", 20.0)  # Default 20% for private companies
        control_premium = adjustments.get("control_premium", 30.0)  # Default 30% control premium

        # Calculate implied values
        target_revenue = target_metrics.get("revenue", 0)
        target_ebitda = target_metrics.get("ebitda", 0)

        if selected_ev_revenue:
            ev_from_revenue = target_revenue * selected_ev_revenue
        else:
            ev_from_revenue = 0

        if selected_ev_ebitda:
            ev_from_ebitda = target_ebitda * selected_ev_ebitda
        else:
            ev_from_ebitda = 0

        # Use average of multiple-based valuations
        base_ev = (ev_from_revenue + ev_from_ebitda) / 2 if (ev_from_revenue and ev_from_ebitda) else (ev_from_revenue or ev_from_ebitda)

        # Apply adjustments
        adjusted_ev = base_ev * (1 + size_premium / 100)
        adjusted_ev = apply_marketability_discount(adjusted_ev, liquidity_discount)
        implied_ev = apply_control_premium(adjusted_ev, control_premium)

        # Calculate implied equity value
        net_debt = target_metrics.get("net_debt", 0)
        implied_equity = calculate_equity_value(implied_ev, 0, net_debt)

        # Create analysis
        analysis = ComparableCompanyAnalysis(
            valuation_id=valuation_id,
            organization_id=organization_id,
            industry=industry,
            selection_criteria={
                "min_revenue": target_revenue * 0.5,
                "max_revenue": target_revenue * 2.0,
                "industry": industry
            },
            ev_revenue_mean=Decimal(str(stats["ev_revenue"]["mean"])) if stats["ev_revenue"] else None,
            ev_revenue_median=Decimal(str(stats["ev_revenue"]["median"])) if stats["ev_revenue"] else None,
            ev_revenue_min=Decimal(str(stats["ev_revenue"]["min"])) if stats["ev_revenue"] else None,
            ev_revenue_max=Decimal(str(stats["ev_revenue"]["max"])) if stats["ev_revenue"] else None,
            ev_ebitda_mean=Decimal(str(stats["ev_ebitda"]["mean"])) if stats["ev_ebitda"] else None,
            ev_ebitda_median=Decimal(str(stats["ev_ebitda"]["median"])) if stats["ev_ebitda"] else None,
            ev_ebitda_min=Decimal(str(stats["ev_ebitda"]["min"])) if stats["ev_ebitda"] else None,
            ev_ebitda_max=Decimal(str(stats["ev_ebitda"]["max"])) if stats["ev_ebitda"] else None,
            pe_mean=Decimal(str(stats["pe"]["mean"])) if stats["pe"] else None,
            pe_median=Decimal(str(stats["pe"]["median"])) if stats["pe"] else None,
            selected_ev_revenue=Decimal(str(selected_ev_revenue)) if selected_ev_revenue else None,
            selected_ev_ebitda=Decimal(str(selected_ev_ebitda)) if selected_ev_ebitda else None,
            selected_pe=Decimal(str(selected_pe)) if selected_pe else None,
            size_premium=Decimal(str(size_premium)),
            liquidity_discount=Decimal(str(liquidity_discount)),
            control_premium=Decimal(str(control_premium)),
            implied_enterprise_value=Decimal(str(implied_ev)),
            implied_equity_value=Decimal(str(implied_equity)),
            comparable_companies=comparable_companies
        )

        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)

        return analysis


class PrecedentTransactionService:
    """Precedent Transaction Analysis service"""

    def __init__(self, db: Session):
        self.db = db

    def create_precedent_analysis(
        self,
        valuation_id: str,
        organization_id: str,
        industry: str,
        precedent_transactions: List[Dict[str, Any]],
        target_metrics: Dict[str, float],
        adjustments: Optional[Dict[str, float]] = None
    ) -> PrecedentTransactionAnalysis:
        """
        Create precedent transaction analysis

        Args:
            valuation_id: Parent valuation ID
            organization_id: Organization ID
            industry: Industry sector
            precedent_transactions: List of comparable transactions
            target_metrics: Target company financial metrics
            adjustments: Market timing, buyer type premiums

        Returns:
            PrecedentTransactionAnalysis model
        """
        if adjustments is None:
            adjustments = {}

        # Calculate transaction multiples statistics
        stats = calculate_comparable_multiples_stats(precedent_transactions)

        # Select median multiples
        selected_ev_revenue = stats["ev_revenue"]["median"] if stats["ev_revenue"] else None
        selected_ev_ebitda = stats["ev_ebitda"]["median"] if stats["ev_ebitda"] else None

        # Calculate implied values
        target_revenue = target_metrics.get("revenue", 0)
        target_ebitda = target_metrics.get("ebitda", 0)

        if selected_ev_revenue:
            ev_from_revenue = target_revenue * selected_ev_revenue
        else:
            ev_from_revenue = 0

        if selected_ev_ebitda:
            ev_from_ebitda = target_ebitda * selected_ev_ebitda
        else:
            ev_from_ebitda = 0

        base_ev = (ev_from_revenue + ev_from_ebitda) / 2 if (ev_from_revenue and ev_from_ebitda) else (ev_from_revenue or ev_from_ebitda)

        # Apply market timing adjustment
        market_timing_adjustment = adjustments.get("market_timing_adjustment", 0)
        implied_ev = base_ev * (1 + market_timing_adjustment / 100)

        # Calculate implied equity value
        net_debt = target_metrics.get("net_debt", 0)
        implied_equity = calculate_equity_value(implied_ev, 0, net_debt)

        # Calculate average premiums
        strategic_premiums = [t.get("premium", 0) for t in precedent_transactions if t.get("buyer_type") == "strategic"]
        financial_premiums = [t.get("premium", 0) for t in precedent_transactions if t.get("buyer_type") == "financial"]

        strategic_avg = sum(strategic_premiums) / len(strategic_premiums) if strategic_premiums else 0
        financial_avg = sum(financial_premiums) / len(financial_premiums) if financial_premiums else 0

        # Create analysis
        analysis = PrecedentTransactionAnalysis(
            valuation_id=valuation_id,
            organization_id=organization_id,
            industry=industry,
            lookback_period_months=adjustments.get("lookback_period_months", 36),
            selection_criteria={
                "industry": industry,
                "min_revenue": target_revenue * 0.5,
                "max_revenue": target_revenue * 2.0
            },
            ev_revenue_mean=Decimal(str(stats["ev_revenue"]["mean"])) if stats["ev_revenue"] else None,
            ev_revenue_median=Decimal(str(stats["ev_revenue"]["median"])) if stats["ev_revenue"] else None,
            ev_revenue_min=Decimal(str(stats["ev_revenue"]["min"])) if stats["ev_revenue"] else None,
            ev_revenue_max=Decimal(str(stats["ev_revenue"]["max"])) if stats["ev_revenue"] else None,
            ev_ebitda_mean=Decimal(str(stats["ev_ebitda"]["mean"])) if stats["ev_ebitda"] else None,
            ev_ebitda_median=Decimal(str(stats["ev_ebitda"]["median"])) if stats["ev_ebitda"] else None,
            ev_ebitda_min=Decimal(str(stats["ev_ebitda"]["min"])) if stats["ev_ebitda"] else None,
            ev_ebitda_max=Decimal(str(stats["ev_ebitda"]["max"])) if stats["ev_ebitda"] else None,
            selected_ev_revenue=Decimal(str(selected_ev_revenue)) if selected_ev_revenue else None,
            selected_ev_ebitda=Decimal(str(selected_ev_ebitda)) if selected_ev_ebitda else None,
            strategic_buyer_premium=Decimal(str(strategic_avg)),
            financial_buyer_premium=Decimal(str(financial_avg)),
            market_timing_adjustment=Decimal(str(market_timing_adjustment)),
            implied_enterprise_value=Decimal(str(implied_ev)),
            implied_equity_value=Decimal(str(implied_equity)),
            precedent_transactions=precedent_transactions
        )

        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)

        return analysis


class LBOModelingService:
    """Leveraged Buyout modeling service"""

    def __init__(self, db: Session):
        self.db = db

    def create_lbo_model(
        self,
        valuation_id: str,
        organization_id: str,
        inputs: Dict[str, Any]
    ) -> LBOModel:
        """
        Create LBO financial model

        Args:
            valuation_id: Parent valuation ID
            organization_id: Organization ID
            inputs: Model inputs and assumptions

        Returns:
            Calculated LBOModel
        """
        # Transaction structure
        purchase_price = inputs["purchase_price"]
        entry_ebitda = inputs["entry_ebitda"]
        purchase_multiple = purchase_price / entry_ebitda if entry_ebitda > 0 else 0
        transaction_fees = inputs.get("transaction_fees", purchase_price * 0.02)  # 2% default

        # Capital structure
        equity_percent = inputs.get("equity_percent", 40.0)
        equity_investment = purchase_price * (equity_percent / 100)
        total_debt = purchase_price - equity_investment

        # Debt allocation (simplified)
        senior_debt = total_debt * 0.7  # 70% senior
        subordinated_debt = total_debt * 0.2  # 20% subordinated
        mezzanine_debt = total_debt * 0.1  # 10% mezzanine

        # Debt terms
        senior_rate = inputs.get("senior_debt_rate", 5.0)
        sub_rate = inputs.get("subordinated_debt_rate", 8.0)
        mezz_rate = inputs.get("mezzanine_rate", 12.0)

        # Operating projections
        hold_period = inputs.get("hold_period_years", 5)
        base_revenue = inputs["base_revenue"]
        revenue_growth = inputs.get("revenue_growth_rates", [8, 7, 6, 5, 5])
        ebitda_margin = inputs.get("ebitda_margin", 20.0)

        # Project revenues
        revenues = project_revenue(base_revenue, revenue_growth, hold_period)

        # Project EBITDA
        ebitdas = [rev * (ebitda_margin / 100) for rev in revenues]

        # Debt amortization (simplified - straight line over hold period)
        annual_amortization = total_debt / hold_period
        debt_balances = [total_debt - (annual_amortization * i) for i in range(hold_period + 1)]

        # Exit assumptions
        exit_year = hold_period
        exit_multiple = inputs.get("exit_multiple", purchase_multiple)  # Same as entry by default
        exit_ebitda = ebitdas[-1]
        exit_ev = exit_ebitda * exit_multiple
        exit_debt_balance = debt_balances[-1]
        exit_equity_value = exit_ev - exit_debt_balance

        # Returns calculation
        returns = calculate_lbo_returns(
            equity_investment,
            exit_equity_value,
            hold_period
        )

        # Management equity
        mgmt_equity_percent = inputs.get("management_equity_percent", 10.0)
        mgmt_investment = equity_investment * (mgmt_equity_percent / 100)
        mgmt_exit_proceeds = exit_equity_value * (mgmt_equity_percent / 100)

        # Create LBO model
        lbo_model = LBOModel(
            valuation_id=valuation_id,
            organization_id=organization_id,
            purchase_price=Decimal(str(purchase_price)),
            purchase_multiple=Decimal(str(purchase_multiple)),
            transaction_fees=Decimal(str(transaction_fees)),
            equity_investment=Decimal(str(equity_investment)),
            senior_debt=Decimal(str(senior_debt)),
            subordinated_debt=Decimal(str(subordinated_debt)),
            mezzanine_debt=Decimal(str(mezzanine_debt)),
            seller_note=Decimal(str(inputs.get("seller_note", 0))),
            total_debt=Decimal(str(total_debt)),
            debt_to_ebitda=Decimal(str(total_debt / entry_ebitda)) if entry_ebitda > 0 else Decimal("0"),
            senior_debt_rate=Decimal(str(senior_rate)),
            subordinated_debt_rate=Decimal(str(sub_rate)),
            mezzanine_rate=Decimal(str(mezz_rate)),
            debt_amortization_schedule=debt_balances,
            hold_period_years=hold_period,
            revenue_projections=revenues,
            ebitda_projections=ebitdas,
            capex_projections=[rev * 0.03 for rev in revenues],  # 3% of revenue
            working_capital_changes=[0] * hold_period,  # Simplified
            exit_year=exit_year,
            exit_multiple=Decimal(str(exit_multiple)),
            exit_ebitda=Decimal(str(exit_ebitda)),
            exit_enterprise_value=Decimal(str(exit_ev)),
            exit_debt_balance=Decimal(str(exit_debt_balance)),
            exit_equity_value=Decimal(str(exit_equity_value)),
            money_multiple=Decimal(str(returns["moic"])),
            irr=Decimal(str(returns["irr"])),
            cash_on_cash_return=Decimal(str(returns["cash_on_cash_return"])),
            management_equity_percent=Decimal(str(mgmt_equity_percent)),
            management_investment=Decimal(str(mgmt_investment)),
            management_exit_proceeds=Decimal(str(mgmt_exit_proceeds)),
            sensitivity_scenarios={},
            annual_cash_flows={}
        )

        self.db.add(lbo_model)
        self.db.commit()
        self.db.refresh(lbo_model)

        return lbo_model

    def run_lbo_sensitivity(
        self,
        lbo_model: LBOModel,
        exit_multiple_range: List[float],
        revenue_growth_range: List[float]
    ) -> Dict[str, Any]:
        """
        Run two-way sensitivity analysis on LBO returns

        Args:
            lbo_model: LBO model to analyze
            exit_multiple_range: Range of exit multiples to test
            revenue_growth_range: Range of revenue growth rates to test

        Returns:
            Two-way sensitivity results (IRR matrix)
        """
        base_assumptions = {
            "purchase_price": float(lbo_model.purchase_price),
            "equity_investment": float(lbo_model.equity_investment),
            "hold_period": lbo_model.hold_period_years,
            "exit_multiple": float(lbo_model.exit_multiple),
            "revenue_growth": sum(lbo_model.revenue_projections) / len(lbo_model.revenue_projections) / float(lbo_model.revenue_projections[0]) * 100 if lbo_model.revenue_projections else 5.0
        }

        def valuation_func(assumptions):
            exit_ebitda = lbo_model.ebitda_projections[-1]  # Simplified
            exit_ev = exit_ebitda * assumptions["exit_multiple"]
            exit_debt = lbo_model.debt_amortization_schedule[-1]
            exit_equity = exit_ev - exit_debt

            returns = calculate_lbo_returns(
                assumptions["equity_investment"],
                exit_equity,
                assumptions["hold_period"]
            )

            return returns["irr"]

        results = two_way_sensitivity_analysis(
            base_assumptions,
            "exit_multiple",
            exit_multiple_range,
            "revenue_growth",
            revenue_growth_range,
            valuation_func
        )

        return results


class MasterValuationService:
    """Master valuation service coordinating all methodologies"""

    def __init__(self, db: Session):
        self.db = db
        self.dcf_service = DCFValuationService(db)
        self.comparable_service = ComparableCompanyService(db)
        self.precedent_service = PrecedentTransactionService(db)
        self.lbo_service = LBOModelingService(db)

    def create_comprehensive_valuation(
        self,
        organization_id: str,
        company_name: str,
        industry: str,
        target_metrics: Dict[str, Any],
        dcf_inputs: Optional[Dict[str, Any]] = None,
        comparable_data: Optional[Dict[str, Any]] = None,
        precedent_data: Optional[Dict[str, Any]] = None,
        lbo_inputs: Optional[Dict[str, Any]] = None,
        created_by: str = None
    ) -> ValuationModel:
        """
        Create comprehensive valuation using multiple methodologies

        Args:
            organization_id: Organization ID
            company_name: Target company name
            industry: Industry sector
            target_metrics: Target company financial metrics
            dcf_inputs: DCF model inputs (optional)
            comparable_data: Comparable company data (optional)
            precedent_data: Precedent transaction data (optional)
            lbo_inputs: LBO model inputs (optional)
            created_by: User ID creating the valuation

        Returns:
            Master ValuationModel with all sub-analyses
        """
        # Create master valuation model
        valuation = ValuationModel(
            organization_id=organization_id,
            company_name=company_name,
            industry=industry,
            model_name=f"{company_name} Valuation - {datetime.utcnow().strftime('%Y-%m-%d')}",
            primary_method=ValuationMethod.DCF,  # Default to DCF
            target_revenue=Decimal(str(target_metrics.get("revenue", 0))),
            target_ebitda=Decimal(str(target_metrics.get("ebitda", 0))),
            created_by=created_by
        )

        self.db.add(valuation)
        self.db.commit()
        self.db.refresh(valuation)

        valuations = []

        # Run DCF if inputs provided
        if dcf_inputs:
            dcf_model = self.dcf_service.create_dcf_model(
                valuation.id,
                organization_id,
                dcf_inputs
            )
            valuations.append(float(dcf_model.enterprise_value))

        # Run Comparable Company Analysis if data provided
        if comparable_data:
            comp_analysis = self.comparable_service.create_comparable_analysis(
                valuation.id,
                organization_id,
                industry,
                comparable_data.get("companies", []),
                target_metrics,
                comparable_data.get("adjustments")
            )
            valuations.append(float(comp_analysis.implied_enterprise_value))

        # Run Precedent Transaction Analysis if data provided
        if precedent_data:
            prec_analysis = self.precedent_service.create_precedent_analysis(
                valuation.id,
                organization_id,
                industry,
                precedent_data.get("transactions", []),
                target_metrics,
                precedent_data.get("adjustments")
            )
            valuations.append(float(prec_analysis.implied_enterprise_value))

        # Run LBO if inputs provided
        if lbo_inputs:
            lbo_model = self.lbo_service.create_lbo_model(
                valuation.id,
                organization_id,
                lbo_inputs
            )

        # Update master valuation with summary
        if valuations:
            base_case_value = sum(valuations) / len(valuations)  # Average
            valuation.base_case_value = Decimal(str(base_case_value))

            # Calculate implied multiples
            if target_metrics.get("revenue"):
                valuation.ev_revenue_multiple = Decimal(str(base_case_value / target_metrics["revenue"]))
            if target_metrics.get("ebitda"):
                valuation.ev_ebitda_multiple = Decimal(str(base_case_value / target_metrics["ebitda"]))

        self.db.commit()
        self.db.refresh(valuation)

        return valuation
