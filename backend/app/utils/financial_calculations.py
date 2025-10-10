"""
Financial Calculations Utilities
Core financial formulas for valuation and modeling
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal


def calculate_wacc(
    cost_of_equity: float,
    cost_of_debt: float,
    tax_rate: float,
    debt_to_equity: float
) -> float:
    """
    Calculate Weighted Average Cost of Capital

    WACC = (E/V) * Re + (D/V) * Rd * (1 - Tc)

    Args:
        cost_of_equity: Cost of equity (%)
        cost_of_debt: Cost of debt (%)
        tax_rate: Corporate tax rate (%)
        debt_to_equity: Debt-to-equity ratio

    Returns:
        WACC as percentage
    """
    # Convert D/E ratio to weights
    equity_weight = 1 / (1 + debt_to_equity)
    debt_weight = debt_to_equity / (1 + debt_to_equity)

    wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate / 100))

    return round(wacc, 4)


def calculate_cost_of_equity(
    risk_free_rate: float,
    beta: float,
    market_risk_premium: float
) -> float:
    """
    Calculate Cost of Equity using CAPM

    Re = Rf + β * (Rm - Rf)

    Args:
        risk_free_rate: Risk-free rate (%)
        beta: Company beta
        market_risk_premium: Market risk premium (%)

    Returns:
        Cost of equity as percentage
    """
    cost_of_equity = risk_free_rate + (beta * market_risk_premium)
    return round(cost_of_equity, 4)


def calculate_npv(cash_flows: List[float], discount_rate: float) -> float:
    """
    Calculate Net Present Value

    NPV = Σ [CFt / (1 + r)^t]

    Args:
        cash_flows: List of cash flows (index 0 is year 0)
        discount_rate: Discount rate as decimal (e.g., 0.10 for 10%)

    Returns:
        Net present value
    """
    npv = sum(cf / ((1 + discount_rate) ** t) for t, cf in enumerate(cash_flows))
    return round(npv, 2)


def calculate_irr(cash_flows: List[float], guess: float = 0.1) -> float:
    """
    Calculate Internal Rate of Return using Newton-Raphson method

    Args:
        cash_flows: List of cash flows (index 0 is initial investment, negative)
        guess: Initial guess for IRR

    Returns:
        IRR as decimal (e.g., 0.15 for 15%)
    """
    try:
        # Use numpy's IRR calculation
        irr = np.irr(cash_flows)
        return round(irr * 100, 2)  # Return as percentage
    except:
        # Fallback to manual Newton-Raphson
        rate = guess
        max_iterations = 1000
        tolerance = 1e-6

        for _ in range(max_iterations):
            npv = sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cash_flows))
            npv_derivative = sum(-t * cf / ((1 + rate) ** (t + 1)) for t, cf in enumerate(cash_flows))

            if abs(npv) < tolerance:
                return round(rate * 100, 2)

            rate = rate - npv / npv_derivative

        return round(rate * 100, 2)


def calculate_terminal_value_perpetuity(
    final_cash_flow: float,
    discount_rate: float,
    perpetual_growth_rate: float
) -> float:
    """
    Calculate Terminal Value using Perpetuity Growth Method

    TV = FCFn * (1 + g) / (WACC - g)

    Args:
        final_cash_flow: Final year free cash flow
        discount_rate: WACC or discount rate (%)
        perpetual_growth_rate: Long-term growth rate (%)

    Returns:
        Terminal value
    """
    if discount_rate <= perpetual_growth_rate:
        raise ValueError("Discount rate must be greater than perpetual growth rate")

    discount_decimal = discount_rate / 100
    growth_decimal = perpetual_growth_rate / 100

    tv = (final_cash_flow * (1 + growth_decimal)) / (discount_decimal - growth_decimal)

    return round(tv, 2)


def calculate_terminal_value_exit_multiple(
    final_ebitda: float,
    exit_multiple: float
) -> float:
    """
    Calculate Terminal Value using Exit Multiple Method

    TV = Final EBITDA * Exit Multiple

    Args:
        final_ebitda: Final year EBITDA
        exit_multiple: Exit EBITDA multiple

    Returns:
        Terminal value
    """
    return round(final_ebitda * exit_multiple, 2)


def project_revenue(
    base_revenue: float,
    growth_rates: List[float],
    years: int
) -> List[float]:
    """
    Project revenue based on growth rates

    Args:
        base_revenue: Starting revenue
        growth_rates: List of growth rates (%) for each year
        years: Number of years to project

    Returns:
        List of projected revenues
    """
    projections = [base_revenue]

    for i in range(years):
        if i < len(growth_rates):
            growth_rate = growth_rates[i] / 100
        else:
            growth_rate = growth_rates[-1] / 100  # Use last rate if not enough provided

        next_revenue = projections[-1] * (1 + growth_rate)
        projections.append(round(next_revenue, 2))

    return projections[1:]  # Return only projected years, not base


def calculate_free_cash_flow(
    ebitda: float,
    depreciation: float,
    tax_rate: float,
    capex: float,
    change_in_nwc: float
) -> float:
    """
    Calculate Unlevered Free Cash Flow

    FCF = EBITDA - D&A - Tax + D&A - CapEx - ΔNWC
        = EBITDA * (1 - Tax Rate) + D&A * Tax Rate - CapEx - ΔNWC

    Args:
        ebitda: Earnings before interest, taxes, depreciation, and amortization
        depreciation: Depreciation and amortization
        tax_rate: Tax rate (%)
        capex: Capital expenditures
        change_in_nwc: Change in net working capital

    Returns:
        Free cash flow
    """
    ebit = ebitda - depreciation
    nopat = ebit * (1 - tax_rate / 100)
    fcf = nopat + depreciation - capex - change_in_nwc

    return round(fcf, 2)


def calculate_enterprise_value_from_dcf(
    projected_cash_flows: List[float],
    terminal_value: float,
    wacc: float
) -> Dict[str, Any]:
    """
    Calculate Enterprise Value from DCF

    Args:
        projected_cash_flows: List of projected FCFs
        terminal_value: Terminal value
        wacc: Weighted average cost of capital (%)

    Returns:
        Dict with PV of cash flows, PV of terminal value, and enterprise value
    """
    wacc_decimal = wacc / 100

    # Calculate discount factors
    discount_factors = [(1 / ((1 + wacc_decimal) ** (t + 1))) for t in range(len(projected_cash_flows))]

    # PV of cash flows
    pv_cash_flows = [cf * df for cf, df in zip(projected_cash_flows, discount_factors)]

    # PV of terminal value
    terminal_year = len(projected_cash_flows)
    terminal_discount_factor = 1 / ((1 + wacc_decimal) ** terminal_year)
    pv_terminal_value = terminal_value * terminal_discount_factor

    # Enterprise Value
    enterprise_value = sum(pv_cash_flows) + pv_terminal_value

    return {
        "discount_factors": [round(df, 4) for df in discount_factors],
        "pv_cash_flows": [round(pv, 2) for pv in pv_cash_flows],
        "sum_pv_cash_flows": round(sum(pv_cash_flows), 2),
        "terminal_discount_factor": round(terminal_discount_factor, 4),
        "pv_terminal_value": round(pv_terminal_value, 2),
        "enterprise_value": round(enterprise_value, 2)
    }


def calculate_equity_value(
    enterprise_value: float,
    cash: float,
    debt: float,
    minority_interest: float = 0,
    preferred_stock: float = 0
) -> float:
    """
    Calculate Equity Value from Enterprise Value

    Equity Value = EV + Cash - Debt - Minority Interest - Preferred Stock

    Args:
        enterprise_value: Enterprise value
        cash: Cash and cash equivalents
        debt: Total debt
        minority_interest: Minority interest (optional)
        preferred_stock: Preferred stock (optional)

    Returns:
        Equity value
    """
    equity_value = enterprise_value + cash - debt - minority_interest - preferred_stock
    return round(equity_value, 2)


def calculate_lbo_returns(
    initial_equity: float,
    exit_equity_value: float,
    hold_period_years: int,
    annual_distributions: Optional[List[float]] = None
) -> Dict[str, float]:
    """
    Calculate LBO returns (MOIC and IRR)

    Args:
        initial_equity: Initial equity investment
        exit_equity_value: Equity value at exit
        hold_period_years: Holding period in years
        annual_distributions: Annual dividend distributions (optional)

    Returns:
        Dict with MOIC, IRR, and cash-on-cash return
    """
    if annual_distributions is None:
        annual_distributions = [0] * hold_period_years

    # Money Multiple (MOIC)
    total_distributions = sum(annual_distributions)
    moic = (exit_equity_value + total_distributions) / initial_equity

    # IRR calculation
    cash_flows = [-initial_equity] + annual_distributions + [exit_equity_value]
    irr = calculate_irr(cash_flows)

    # Cash-on-cash return
    coc_return = ((exit_equity_value + total_distributions - initial_equity) / initial_equity) * 100

    return {
        "moic": round(moic, 2),
        "irr": round(irr, 2),
        "cash_on_cash_return": round(coc_return, 2),
        "total_distributions": round(total_distributions, 2)
    }


def monte_carlo_valuation(
    base_assumptions: Dict[str, float],
    assumptions_distribution: Dict[str, Tuple[float, float]],
    valuation_function: callable,
    iterations: int = 10000
) -> Dict[str, Any]:
    """
    Run Monte Carlo simulation for valuation sensitivity

    Args:
        base_assumptions: Base case assumptions
        assumptions_distribution: Dict of {param: (mean, std_dev)}
        valuation_function: Function that takes assumptions and returns valuation
        iterations: Number of simulation iterations

    Returns:
        Dict with percentiles and distribution statistics
    """
    results = []

    for _ in range(iterations):
        # Sample from distributions
        sampled_assumptions = base_assumptions.copy()
        for param, (mean, std_dev) in assumptions_distribution.items():
            sampled_assumptions[param] = np.random.normal(mean, std_dev)

        # Run valuation
        valuation = valuation_function(sampled_assumptions)
        results.append(valuation)

    results_array = np.array(results)

    return {
        "mean": round(float(np.mean(results_array)), 2),
        "median": round(float(np.median(results_array)), 2),
        "std_dev": round(float(np.std(results_array)), 2),
        "percentile_10": round(float(np.percentile(results_array, 10)), 2),
        "percentile_25": round(float(np.percentile(results_array, 25)), 2),
        "percentile_75": round(float(np.percentile(results_array, 75)), 2),
        "percentile_90": round(float(np.percentile(results_array, 90)), 2),
        "min": round(float(np.min(results_array)), 2),
        "max": round(float(np.max(results_array)), 2),
        "distribution": results[:100]  # Sample of results for visualization
    }


def sensitivity_analysis(
    base_assumptions: Dict[str, float],
    sensitive_param: str,
    param_range: List[float],
    valuation_function: callable
) -> Dict[str, List[float]]:
    """
    Run sensitivity analysis for one parameter

    Args:
        base_assumptions: Base case assumptions
        sensitive_param: Parameter to vary
        param_range: Range of values to test
        valuation_function: Function that takes assumptions and returns valuation

    Returns:
        Dict with parameter values and corresponding valuations
    """
    valuations = []

    for value in param_range:
        assumptions = base_assumptions.copy()
        assumptions[sensitive_param] = value
        valuation = valuation_function(assumptions)
        valuations.append(round(valuation, 2))

    return {
        "parameter": sensitive_param,
        "values": param_range,
        "valuations": valuations
    }


def two_way_sensitivity_analysis(
    base_assumptions: Dict[str, float],
    param1: str,
    param1_range: List[float],
    param2: str,
    param2_range: List[float],
    valuation_function: callable
) -> Dict[str, Any]:
    """
    Run two-way sensitivity analysis (data table)

    Args:
        base_assumptions: Base case assumptions
        param1: First parameter to vary
        param1_range: Range for first parameter
        param2: Second parameter to vary
        param2_range: Range for second parameter
        valuation_function: Function that takes assumptions and returns valuation

    Returns:
        Dict with matrix of valuations
    """
    results_matrix = []

    for p1_val in param1_range:
        row = []
        for p2_val in param2_range:
            assumptions = base_assumptions.copy()
            assumptions[param1] = p1_val
            assumptions[param2] = p2_val
            valuation = valuation_function(assumptions)
            row.append(round(valuation, 2))
        results_matrix.append(row)

    return {
        "param1": param1,
        "param1_range": param1_range,
        "param2": param2,
        "param2_range": param2_range,
        "results_matrix": results_matrix
    }


def calculate_comparable_multiples_stats(
    comparables_data: List[Dict[str, float]]
) -> Dict[str, Dict[str, float]]:
    """
    Calculate summary statistics for comparable company multiples

    Args:
        comparables_data: List of dicts with company financial data

    Returns:
        Dict with mean, median, min, max for each multiple
    """
    multiples = {
        "ev_revenue": [],
        "ev_ebitda": [],
        "pe": []
    }

    # Extract multiples
    for comp in comparables_data:
        if comp.get("ev_revenue"):
            multiples["ev_revenue"].append(comp["ev_revenue"])
        if comp.get("ev_ebitda"):
            multiples["ev_ebitda"].append(comp["ev_ebitda"])
        if comp.get("pe"):
            multiples["pe"].append(comp["pe"])

    # Calculate statistics
    stats = {}
    for multiple_type, values in multiples.items():
        if values:
            stats[multiple_type] = {
                "mean": round(float(np.mean(values)), 2),
                "median": round(float(np.median(values)), 2),
                "min": round(float(np.min(values)), 2),
                "max": round(float(np.max(values)), 2),
                "std_dev": round(float(np.std(values)), 2),
                "count": len(values)
            }
        else:
            stats[multiple_type] = None

    return stats


def apply_control_premium(
    minority_value: float,
    control_premium_percent: float
) -> float:
    """
    Apply control premium to minority interest valuation

    Args:
        minority_value: Valuation based on minority interest
        control_premium_percent: Control premium as percentage

    Returns:
        Adjusted value with control premium
    """
    control_value = minority_value * (1 + control_premium_percent / 100)
    return round(control_value, 2)


def apply_marketability_discount(
    marketable_value: float,
    discount_percent: float
) -> float:
    """
    Apply discount for lack of marketability

    Args:
        marketable_value: Value assuming marketability
        discount_percent: Marketability discount as percentage

    Returns:
        Adjusted value with marketability discount
    """
    discounted_value = marketable_value * (1 - discount_percent / 100)
    return round(discounted_value, 2)
