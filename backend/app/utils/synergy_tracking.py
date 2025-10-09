"""
Synergy Tracking Utilities
Financial calculations and analysis for synergy valuation and realization
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal
import numpy as np
from datetime import date, datetime


def calculate_probability_weighted_value(target_value: float, probability: float) -> float:
    """
    Calculate probability-weighted synergy value

    Args:
        target_value: Expected synergy value
        probability: Probability of realization (0.0 to 1.0)

    Returns:
        Probability-weighted value
    """
    if target_value is None or probability is None:
        return 0.0

    return target_value * probability


def calculate_synergy_npv(
    target_value: float,
    realization_timeline_months: int,
    discount_rate: float = 0.10,
    upfront_investment: float = 0.0
) -> float:
    """
    Calculate NPV of synergy opportunity

    Args:
        target_value: Annual run-rate synergy value
        realization_timeline_months: Months to reach full run-rate
        discount_rate: Annual discount rate (default 10%)
        upfront_investment: Initial investment required

    Returns:
        Net present value of synergy
    """
    if target_value <= 0:
        return -upfront_investment

    # Monthly discount rate
    monthly_rate = discount_rate / 12

    # Assume linear ramp to full run-rate
    monthly_value = target_value / 12

    cash_flows = [-upfront_investment]  # Initial investment at t=0

    # Ramp-up period
    for month in range(1, realization_timeline_months + 1):
        ramp_percentage = month / realization_timeline_months
        monthly_synergy = monthly_value * ramp_percentage
        discount_factor = (1 + monthly_rate) ** month
        cash_flows.append(monthly_synergy / discount_factor)

    # Full run-rate for remaining 3 years (36 months)
    for month in range(realization_timeline_months + 1, realization_timeline_months + 37):
        discount_factor = (1 + monthly_rate) ** month
        cash_flows.append(monthly_value / discount_factor)

    return sum(cash_flows)


def calculate_payback_period(
    target_value: float,
    upfront_investment: float,
    realization_timeline_months: int
) -> Optional[float]:
    """
    Calculate payback period in months

    Args:
        target_value: Annual run-rate synergy value
        upfront_investment: Initial investment required
        realization_timeline_months: Months to reach full run-rate

    Returns:
        Payback period in months, or None if no payback
    """
    if target_value <= 0 or upfront_investment <= 0:
        return None

    monthly_value = target_value / 12
    cumulative_cash_flow = 0.0

    # During ramp-up period
    for month in range(1, realization_timeline_months + 1):
        ramp_percentage = month / realization_timeline_months
        monthly_synergy = monthly_value * ramp_percentage
        cumulative_cash_flow += monthly_synergy

        if cumulative_cash_flow >= upfront_investment:
            return month

    # After full run-rate
    for month in range(realization_timeline_months + 1, 61):  # Up to 5 years
        cumulative_cash_flow += monthly_value

        if cumulative_cash_flow >= upfront_investment:
            return month

    return None  # No payback within 5 years


def calculate_run_rate_savings(
    actual_monthly_values: List[float],
    lookback_months: int = 3
) -> float:
    """
    Calculate annualized run-rate savings based on recent performance

    Args:
        actual_monthly_values: List of actual monthly synergy values
        lookback_months: Number of recent months to average (default 3)

    Returns:
        Annualized run-rate value
    """
    if not actual_monthly_values:
        return 0.0

    # Take most recent months
    recent_values = actual_monthly_values[-lookback_months:]

    # Calculate average
    avg_monthly = sum(recent_values) / len(recent_values)

    # Annualize
    return avg_monthly * 12


def calculate_roic(
    synergy_value: float,
    invested_capital: float
) -> Optional[float]:
    """
    Calculate Return on Invested Capital for synergy

    Args:
        synergy_value: Annual synergy value realized
        invested_capital: Capital invested to realize synergy

    Returns:
        ROIC as percentage, or None if no investment
    """
    if invested_capital <= 0:
        return None

    return (synergy_value / invested_capital) * 100


def generate_waterfall_chart_data(
    synergies: List[Any],
    realizations: List[Any]
) -> Dict[str, Any]:
    """
    Generate data structure for synergy waterfall chart

    Args:
        synergies: List of SynergyOpportunity objects
        realizations: List of SynergyRealization objects

    Returns:
        Waterfall chart data with categories and values
    """
    # Group synergies by type
    synergy_by_type = {}
    for synergy in synergies:
        synergy_type = synergy.synergy_type.value if hasattr(synergy.synergy_type, 'value') else str(synergy.synergy_type)

        if synergy_type not in synergy_by_type:
            synergy_by_type[synergy_type] = {
                "target": 0.0,
                "probability_weighted": 0.0,
                "realized": 0.0,
                "synergy_ids": []
            }

        synergy_by_type[synergy_type]["target"] += synergy.target_value or 0.0
        synergy_by_type[synergy_type]["probability_weighted"] += synergy.probability_weighted_value or 0.0
        synergy_by_type[synergy_type]["synergy_ids"].append(synergy.id)

    # Add realized values from realizations
    realization_by_synergy = {}
    for realization in realizations:
        if realization.synergy_id not in realization_by_synergy:
            realization_by_synergy[realization.synergy_id] = 0.0
        realization_by_synergy[realization.synergy_id] += realization.actual_value or 0.0

    # Map realizations to synergy types
    for synergy in synergies:
        synergy_type = synergy.synergy_type.value if hasattr(synergy.synergy_type, 'value') else str(synergy.synergy_type)
        if synergy.id in realization_by_synergy:
            synergy_by_type[synergy_type]["realized"] += realization_by_synergy[synergy.id]

    # Build waterfall structure
    waterfall = {
        "total_target": sum(s["target"] for s in synergy_by_type.values()),
        "total_probability_weighted": sum(s["probability_weighted"] for s in synergy_by_type.values()),
        "total_realized": sum(s["realized"] for s in synergy_by_type.values()),
        "by_type": []
    }

    cumulative = 0.0
    for synergy_type, values in sorted(synergy_by_type.items()):
        waterfall["by_type"].append({
            "type": synergy_type,
            "target": values["target"],
            "probability_weighted": values["probability_weighted"],
            "realized": values["realized"],
            "cumulative_start": cumulative,
            "cumulative_end": cumulative + values["probability_weighted"],
            "capture_rate": (values["realized"] / values["target"] * 100) if values["target"] > 0 else 0
        })
        cumulative += values["probability_weighted"]

    # Calculate overall capture rate
    if waterfall["total_target"] > 0:
        waterfall["overall_capture_rate"] = (
            waterfall["total_realized"] / waterfall["total_target"] * 100
        )
    else:
        waterfall["overall_capture_rate"] = 0.0

    return waterfall


def calculate_synergy_confidence_score(
    synergy: Any,
    realization_history: List[Any]
) -> Dict[str, Any]:
    """
    Calculate confidence score for synergy realization

    Args:
        synergy: SynergyOpportunity object
        realization_history: List of SynergyRealization objects

    Returns:
        Confidence analysis with score and factors
    """
    confidence_factors = []
    confidence_score = 50  # Start at neutral 50%

    # Factor 1: Historical performance (if any realizations exist)
    if realization_history:
        on_track_count = sum(1 for r in realization_history if r.realization_status == "on_track")
        exceeded_count = sum(1 for r in realization_history if r.realization_status == "exceeded")
        total_count = len(realization_history)

        performance_rate = (on_track_count + exceeded_count) / total_count
        performance_adjustment = (performance_rate - 0.5) * 30  # +/- 15 points max

        confidence_score += performance_adjustment
        confidence_factors.append({
            "factor": "historical_performance",
            "impact": performance_adjustment,
            "description": f"{on_track_count + exceeded_count} of {total_count} periods on track"
        })

    # Factor 2: Probability assessment
    if hasattr(synergy, 'probability_percentage') and synergy.probability_percentage:
        probability_adjustment = (synergy.probability_percentage - 50) * 0.3  # +/- 15 points max
        confidence_score += probability_adjustment
        confidence_factors.append({
            "factor": "probability_assessment",
            "impact": probability_adjustment,
            "description": f"Initial probability: {synergy.probability_percentage}%"
        })

    # Factor 3: Required investment vs. value
    if hasattr(synergy, 'required_investment') and hasattr(synergy, 'target_value'):
        if synergy.required_investment and synergy.target_value:
            investment_ratio = synergy.required_investment / synergy.target_value

            if investment_ratio < 0.1:  # Low investment relative to value
                investment_adjustment = 10
            elif investment_ratio < 0.3:
                investment_adjustment = 5
            elif investment_ratio > 0.8:  # High investment risk
                investment_adjustment = -10
            else:
                investment_adjustment = 0

            confidence_score += investment_adjustment
            confidence_factors.append({
                "factor": "investment_ratio",
                "impact": investment_adjustment,
                "description": f"Investment is {investment_ratio:.1%} of target value"
            })

    # Factor 4: Implementation complexity (based on number of steps)
    if hasattr(synergy, 'implementation_steps') and synergy.implementation_steps:
        steps_count = len(synergy.implementation_steps)

        if steps_count <= 3:
            complexity_adjustment = 10
        elif steps_count <= 6:
            complexity_adjustment = 0
        else:
            complexity_adjustment = -5

        confidence_score += complexity_adjustment
        confidence_factors.append({
            "factor": "implementation_complexity",
            "impact": complexity_adjustment,
            "description": f"{steps_count} implementation steps"
        })

    # Factor 5: Time to full run-rate
    if hasattr(synergy, 'realization_start_date') and hasattr(synergy, 'full_run_rate_date'):
        if synergy.realization_start_date and synergy.full_run_rate_date:
            days_to_realize = (synergy.full_run_rate_date - synergy.realization_start_date).days

            if days_to_realize <= 90:  # Quick wins
                timeline_adjustment = 10
            elif days_to_realize <= 180:
                timeline_adjustment = 5
            elif days_to_realize > 365:  # Long-term uncertain
                timeline_adjustment = -5
            else:
                timeline_adjustment = 0

            confidence_score += timeline_adjustment
            confidence_factors.append({
                "factor": "realization_timeline",
                "impact": timeline_adjustment,
                "description": f"{days_to_realize} days to full run-rate"
            })

    # Clamp score between 0 and 100
    confidence_score = max(0, min(100, confidence_score))

    # Determine confidence level
    if confidence_score >= 75:
        confidence_level = "high"
    elif confidence_score >= 50:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    return {
        "confidence_score": round(confidence_score, 1),
        "confidence_level": confidence_level,
        "factors": confidence_factors,
        "recommendation": _get_confidence_recommendation(confidence_score, confidence_factors)
    }


def _get_confidence_recommendation(score: float, factors: List[Dict]) -> str:
    """Generate recommendation based on confidence analysis"""
    if score >= 75:
        return "High confidence - proceed with realization plan as scheduled"
    elif score >= 60:
        return "Good confidence - monitor progress closely against milestones"
    elif score >= 40:
        return "Moderate confidence - consider risk mitigation strategies"
    else:
        negative_factors = [f for f in factors if f["impact"] < 0]
        if negative_factors:
            main_issue = negative_factors[0]["factor"].replace("_", " ").title()
            return f"Low confidence - address {main_issue} before proceeding"
        return "Low confidence - reassess synergy feasibility and approach"


def calculate_synergy_variance_analysis(
    realizations: List[Any],
    target_value: float
) -> Dict[str, Any]:
    """
    Perform variance analysis on synergy realizations

    Args:
        realizations: List of SynergyRealization objects
        target_value: Target synergy value

    Returns:
        Variance analysis with trends and insights
    """
    if not realizations:
        return {
            "total_variance": 0.0,
            "variance_percentage": 0.0,
            "trend": "unknown",
            "insights": []
        }

    # Sort by period
    sorted_realizations = sorted(realizations, key=lambda r: r.period_end_date)

    total_target = sum(r.target_value or 0 for r in sorted_realizations)
    total_actual = sum(r.actual_value or 0 for r in sorted_realizations)
    total_variance = total_actual - total_target

    variance_pct = (total_variance / total_target * 100) if total_target > 0 else 0.0

    # Analyze trend
    recent_variances = [r.variance_percentage or 0 for r in sorted_realizations[-3:]]

    if len(recent_variances) >= 2:
        if all(recent_variances[i] < recent_variances[i+1] for i in range(len(recent_variances)-1)):
            trend = "improving"
        elif all(recent_variances[i] > recent_variances[i+1] for i in range(len(recent_variances)-1)):
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    # Generate insights
    insights = []

    if variance_pct > 10:
        insights.append({
            "type": "positive",
            "message": f"Exceeding target by {variance_pct:.1f}% - synergy realization ahead of plan"
        })
    elif variance_pct < -10:
        insights.append({
            "type": "negative",
            "message": f"Below target by {abs(variance_pct):.1f}% - action required to close gap"
        })

    if trend == "improving":
        insights.append({
            "type": "positive",
            "message": "Variance trend is improving - synergy capture accelerating"
        })
    elif trend == "declining":
        insights.append({
            "type": "warning",
            "message": "Variance trend is declining - review realization plan"
        })

    # Check consistency
    variance_std = np.std([r.variance_percentage or 0 for r in sorted_realizations])
    if variance_std > 20:
        insights.append({
            "type": "warning",
            "message": f"High variance volatility ({variance_std:.1f}%) - inconsistent realization"
        })

    return {
        "total_variance": total_variance,
        "variance_percentage": variance_pct,
        "trend": trend,
        "variance_std_dev": variance_std,
        "periods_analyzed": len(sorted_realizations),
        "insights": insights,
        "latest_period_variance": sorted_realizations[-1].variance_percentage if sorted_realizations else None
    }


def project_synergy_trajectory(
    realizations: List[Any],
    target_value: float,
    full_run_rate_date: date,
    projection_months: int = 12
) -> List[Dict[str, Any]]:
    """
    Project future synergy realization based on historical performance

    Args:
        realizations: List of SynergyRealization objects
        target_value: Full run-rate target value
        full_run_rate_date: Date when full run-rate is expected
        projection_months: Number of months to project forward

    Returns:
        List of projected monthly values with confidence intervals
    """
    if not realizations:
        return []

    # Calculate historical growth rate
    sorted_realizations = sorted(realizations, key=lambda r: r.period_end_date)

    if len(sorted_realizations) < 2:
        # Not enough data for projection
        return []

    # Extract actual values
    actual_values = [r.actual_value or 0 for r in sorted_realizations]

    # Simple linear regression
    x = np.arange(len(actual_values))
    y = np.array(actual_values)

    # Fit linear trend
    coefficients = np.polyfit(x, y, 1)
    slope = coefficients[0]
    intercept = coefficients[1]

    # Project future values
    projections = []
    last_date = sorted_realizations[-1].period_end_date
    last_value = actual_values[-1]

    for month in range(1, projection_months + 1):
        # Linear projection
        projected_value = slope * (len(actual_values) + month - 1) + intercept

        # Cap at target value (can't exceed full run-rate)
        projected_value = min(projected_value, target_value)

        # Calculate confidence interval (widens over time)
        std_dev = np.std(actual_values)
        confidence_interval = std_dev * (1 + month * 0.1)  # Increases with projection distance

        # Project date
        from datetime import timedelta
        projected_date = last_date + timedelta(days=30 * month)

        projections.append({
            "period": projected_date.strftime("%Y-%m"),
            "projected_value": round(projected_value, 2),
            "lower_bound": round(max(0, projected_value - confidence_interval), 2),
            "upper_bound": round(min(target_value, projected_value + confidence_interval), 2),
            "confidence": round(max(50, 100 - month * 3), 1)  # Decreases with time
        })

    return projections
