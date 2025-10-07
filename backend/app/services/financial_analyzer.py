"""
Financial Analyzer Service
Comprehensive financial analysis and modeling for M&A opportunities
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
import statistics

from app.models.deal_discovery import (
    Company,
    DealOpportunity,
    FinancialSnapshot,
    FinancialHealth
)

logger = logging.getLogger(__name__)


class FinancialAnalyzer:
    """
    Advanced financial analysis for M&A due diligence
    Provides ratio analysis, trend analysis, and valuation modeling
    """

    def __init__(self):
        """Initialize financial analyzer"""
        pass

    def analyze_company_financials(
        self,
        company_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Perform comprehensive financial analysis

        Args:
            company_id: Company UUID
            db: Database session

        Returns:
            Complete financial analysis report
        """
        try:
            company = db.query(Company).filter(Company.id == company_id).first()

            if not company:
                raise ValueError(f"Company {company_id} not found")

            # Get all financial snapshots
            financials = db.query(FinancialSnapshot).filter(
                FinancialSnapshot.company_id == company_id
            ).order_by(FinancialSnapshot.period_year.desc()).all()

            if not financials:
                return {
                    "company_id": company_id,
                    "company_name": company.name,
                    "analysis_date": datetime.utcnow().isoformat(),
                    "error": "No financial data available"
                }

            latest = financials[0]

            analysis = {
                "company_id": company_id,
                "company_name": company.name,
                "analysis_date": datetime.utcnow().isoformat(),
                "latest_period": latest.period_year,
                "profitability_analysis": self._analyze_profitability(financials),
                "liquidity_analysis": self._analyze_liquidity(financials),
                "leverage_analysis": self._analyze_leverage(financials),
                "efficiency_analysis": self._analyze_efficiency(financials),
                "growth_analysis": self._analyze_growth(financials),
                "trend_analysis": self._analyze_trends(financials),
                "valuation_estimates": self._estimate_valuation(company, latest),
                "financial_health_summary": self._summarize_financial_health(financials),
                "red_flags": self._identify_red_flags(financials),
                "strengths": self._identify_strengths(financials)
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing company financials: {e}")
            return {"error": str(e)}

    def _analyze_profitability(
        self,
        financials: List[FinancialSnapshot]
    ) -> Dict[str, Any]:
        """Analyze profitability metrics"""
        latest = financials[0]

        analysis = {
            "current_metrics": {},
            "historical_average": {},
            "trend": "stable"
        }

        # Current period metrics
        if latest.profit_margin is not None:
            analysis["current_metrics"]["profit_margin"] = float(latest.profit_margin)

        if latest.gross_profit_margin is not None:
            analysis["current_metrics"]["gross_profit_margin"] = float(latest.gross_profit_margin)

        if latest.ebitda_margin is not None:
            analysis["current_metrics"]["ebitda_margin"] = float(latest.ebitda_margin)

        if latest.roa is not None:
            analysis["current_metrics"]["roa"] = float(latest.roa)

        if latest.roe is not None:
            analysis["current_metrics"]["roe"] = float(latest.roe)

        # Historical averages (last 3 years)
        if len(financials) >= 2:
            profit_margins = [f.profit_margin for f in financials[:3] if f.profit_margin]
            if profit_margins:
                analysis["historical_average"]["profit_margin"] = statistics.mean(profit_margins)

            # Determine trend
            if len(profit_margins) >= 2:
                if profit_margins[0] > profit_margins[-1]:
                    analysis["trend"] = "improving"
                elif profit_margins[0] < profit_margins[-1]:
                    analysis["trend"] = "declining"

        # Rating
        current_pm = analysis["current_metrics"].get("profit_margin", 0)
        if current_pm > 0.15:
            analysis["rating"] = "excellent"
        elif current_pm > 0.10:
            analysis["rating"] = "good"
        elif current_pm > 0.05:
            analysis["rating"] = "fair"
        elif current_pm > 0:
            analysis["rating"] = "weak"
        else:
            analysis["rating"] = "poor"

        return analysis

    def _analyze_liquidity(
        self,
        financials: List[FinancialSnapshot]
    ) -> Dict[str, Any]:
        """Analyze liquidity position"""
        latest = financials[0]

        analysis = {
            "current_ratios": {},
            "assessment": "unknown"
        }

        if latest.current_ratio is not None:
            analysis["current_ratios"]["current_ratio"] = float(latest.current_ratio)

        if latest.quick_ratio is not None:
            analysis["current_ratios"]["quick_ratio"] = float(latest.quick_ratio)

        # Cash position
        if latest.cash_and_equivalents and latest.total_assets:
            cash_ratio = float(latest.cash_and_equivalents / latest.total_assets)
            analysis["current_ratios"]["cash_to_assets"] = cash_ratio

        # Working capital
        if latest.revenue and latest.cash_and_equivalents:
            days_cash = (float(latest.cash_and_equivalents) / float(latest.revenue)) * 365
            analysis["current_ratios"]["days_cash_on_hand"] = days_cash

        # Assessment
        current_ratio = analysis["current_ratios"].get("current_ratio", 0)
        if current_ratio >= 2.0:
            analysis["assessment"] = "strong"
        elif current_ratio >= 1.5:
            analysis["assessment"] = "adequate"
        elif current_ratio >= 1.0:
            analysis["assessment"] = "acceptable"
        else:
            analysis["assessment"] = "weak"

        return analysis

    def _analyze_leverage(
        self,
        financials: List[FinancialSnapshot]
    ) -> Dict[str, Any]:
        """Analyze debt and leverage"""
        latest = financials[0]

        analysis = {
            "current_ratios": {},
            "risk_level": "unknown"
        }

        if latest.debt_to_equity_ratio is not None:
            analysis["current_ratios"]["debt_to_equity"] = float(latest.debt_to_equity_ratio)

        if latest.debt_to_assets_ratio is not None:
            analysis["current_ratios"]["debt_to_assets"] = float(latest.debt_to_assets_ratio)

        # Interest coverage (if available)
        if latest.ebitda and latest.total_liabilities:
            # Simplified interest coverage estimate
            estimated_interest = float(latest.total_liabilities) * 0.05  # Assume 5% rate
            if estimated_interest > 0:
                interest_coverage = float(latest.ebitda) / estimated_interest
                analysis["current_ratios"]["estimated_interest_coverage"] = interest_coverage

        # Risk assessment
        debt_to_equity = analysis["current_ratios"].get("debt_to_equity", 0)
        if debt_to_equity < 0.5:
            analysis["risk_level"] = "low"
        elif debt_to_equity < 1.0:
            analysis["risk_level"] = "moderate"
        elif debt_to_equity < 2.0:
            analysis["risk_level"] = "elevated"
        else:
            analysis["risk_level"] = "high"

        return analysis

    def _analyze_efficiency(
        self,
        financials: List[FinancialSnapshot]
    ) -> Dict[str, Any]:
        """Analyze operational efficiency"""
        latest = financials[0]

        analysis = {
            "metrics": {},
            "performance": "unknown"
        }

        # Asset turnover
        if latest.revenue and latest.total_assets and latest.total_assets > 0:
            asset_turnover = float(latest.revenue / latest.total_assets)
            analysis["metrics"]["asset_turnover"] = asset_turnover

        # Days sales outstanding (if receivables available)
        # Would need accounts receivable data - placeholder for now
        analysis["metrics"]["estimated_collection_period"] = "data_unavailable"

        # Return on assets
        if latest.roa is not None:
            analysis["metrics"]["roa"] = float(latest.roa)

        # Return on equity
        if latest.roe is not None:
            analysis["metrics"]["roe"] = float(latest.roe)

        return analysis

    def _analyze_growth(
        self,
        financials: List[FinancialSnapshot]
    ) -> Dict[str, Any]:
        """Analyze growth metrics"""
        analysis = {
            "revenue_growth": {},
            "profitability_growth": {},
            "growth_rating": "unknown"
        }

        if len(financials) < 2:
            return analysis

        latest = financials[0]
        prior = financials[1]

        # Year-over-year growth
        if latest.revenue and prior.revenue and prior.revenue > 0:
            yoy_growth = ((latest.revenue - prior.revenue) / prior.revenue)
            analysis["revenue_growth"]["yoy"] = float(yoy_growth)

        # Multi-year CAGR
        if len(financials) >= 3:
            oldest = financials[min(3, len(financials) - 1)]
            if latest.revenue and oldest.revenue and oldest.revenue > 0:
                years = latest.period_year - oldest.period_year
                if years > 0:
                    cagr = (pow(float(latest.revenue / oldest.revenue), 1 / years) - 1)
                    analysis["revenue_growth"]["cagr_3yr"] = float(cagr)

        # Profit growth
        if latest.net_income and prior.net_income and prior.net_income != 0:
            profit_growth = ((latest.net_income - prior.net_income) / abs(prior.net_income))
            analysis["profitability_growth"]["yoy"] = float(profit_growth)

        # Growth rating
        cagr = analysis["revenue_growth"].get("cagr_3yr", 0)
        if cagr > 0.25:
            analysis["growth_rating"] = "high_growth"
        elif cagr > 0.15:
            analysis["growth_rating"] = "growing"
        elif cagr > 0.05:
            analysis["growth_rating"] = "stable"
        elif cagr < -0.05:
            analysis["growth_rating"] = "declining"
        else:
            analysis["growth_rating"] = "flat"

        return analysis

    def _analyze_trends(
        self,
        financials: List[FinancialSnapshot]
    ) -> Dict[str, Any]:
        """Analyze multi-year trends"""
        trends = {
            "revenue_trend": [],
            "margin_trend": [],
            "leverage_trend": [],
            "overall_trajectory": "insufficient_data"
        }

        if len(financials) < 2:
            return trends

        # Revenue trend
        for f in financials[:5]:  # Last 5 years
            if f.revenue:
                trends["revenue_trend"].append({
                    "year": f.period_year,
                    "revenue": float(f.revenue)
                })

        # Margin trend
        for f in financials[:5]:
            if f.profit_margin is not None:
                trends["margin_trend"].append({
                    "year": f.period_year,
                    "margin": float(f.profit_margin)
                })

        # Leverage trend
        for f in financials[:5]:
            if f.debt_to_equity_ratio is not None:
                trends["leverage_trend"].append({
                    "year": f.period_year,
                    "debt_to_equity": float(f.debt_to_equity_ratio)
                })

        # Overall trajectory assessment
        if len(trends["revenue_trend"]) >= 3:
            rev_values = [t["revenue"] for t in trends["revenue_trend"]]
            if all(rev_values[i] >= rev_values[i+1] for i in range(len(rev_values)-1)):
                trends["overall_trajectory"] = "consistent_growth"
            elif all(rev_values[i] <= rev_values[i+1] for i in range(len(rev_values)-1)):
                trends["overall_trajectory"] = "consistent_decline"
            else:
                trends["overall_trajectory"] = "volatile"

        return trends

    def _estimate_valuation(
        self,
        company: Company,
        latest_financials: FinancialSnapshot
    ) -> Dict[str, Any]:
        """Estimate company valuation using multiple methods"""
        valuation = {
            "estimates": {},
            "recommended_range": {},
            "methodology_notes": []
        }

        # Revenue multiple method
        if latest_financials.revenue:
            revenue = float(latest_financials.revenue)

            # Industry-specific multiples (simplified)
            revenue_multiples = {
                "technology": 3.0,
                "software": 4.0,
                "saas": 5.0,
                "healthcare": 2.5,
                "manufacturing": 1.5,
                "services": 2.0,
                "retail": 0.8,
                "other": 2.0
            }

            multiple = revenue_multiples.get(company.industry_category.value, 2.0)

            # Adjust for profitability
            if latest_financials.profit_margin:
                if latest_financials.profit_margin > 0.15:
                    multiple *= 1.2
                elif latest_financials.profit_margin < 0:
                    multiple *= 0.6

            revenue_valuation = revenue * multiple
            valuation["estimates"]["revenue_multiple"] = {
                "value": revenue_valuation,
                "multiple_used": multiple
            }
            valuation["methodology_notes"].append(
                f"Revenue multiple: {multiple}x applied to ${revenue:,.0f} revenue"
            )

        # EBITDA multiple method
        if latest_financials.ebitda and latest_financials.ebitda > 0:
            ebitda = float(latest_financials.ebitda)
            ebitda_multiple = 6.0  # Typical middle-market multiple

            # Adjust for size
            if ebitda > 10_000_000:  # $10M+ EBITDA
                ebitda_multiple = 8.0
            elif ebitda < 1_000_000:  # <$1M EBITDA
                ebitda_multiple = 4.0

            ebitda_valuation = ebitda * ebitda_multiple
            valuation["estimates"]["ebitda_multiple"] = {
                "value": ebitda_valuation,
                "multiple_used": ebitda_multiple
            }
            valuation["methodology_notes"].append(
                f"EBITDA multiple: {ebitda_multiple}x applied to ${ebitda:,.0f} EBITDA"
            )

        # Book value method
        if latest_financials.total_assets and latest_financials.total_liabilities:
            book_value = float(latest_financials.total_assets - latest_financials.total_liabilities)
            valuation["estimates"]["book_value"] = {
                "value": max(0, book_value)
            }

        # Calculate recommended range
        estimates = [v["value"] for v in valuation["estimates"].values() if isinstance(v, dict) and "value" in v]
        if estimates:
            avg_estimate = statistics.mean(estimates)
            valuation["recommended_range"] = {
                "low": avg_estimate * 0.8,
                "mid": avg_estimate,
                "high": avg_estimate * 1.2
            }

        return valuation

    def _summarize_financial_health(
        self,
        financials: List[FinancialSnapshot]
    ) -> Dict[str, Any]:
        """Provide overall financial health summary"""
        latest = financials[0]

        summary = {
            "overall_rating": FinancialHealth.UNKNOWN.value,
            "score": 50,
            "key_metrics": {}
        }

        score = 50  # Base score

        # Profitability
        if latest.profit_margin:
            if latest.profit_margin > 0.10:
                score += 15
            elif latest.profit_margin < 0:
                score -= 20

        # Liquidity
        if latest.current_ratio:
            if latest.current_ratio > 1.5:
                score += 10
            elif latest.current_ratio < 1.0:
                score -= 15

        # Leverage
        if latest.debt_to_equity_ratio:
            if latest.debt_to_equity_ratio < 1.0:
                score += 10
            elif latest.debt_to_equity_ratio > 2.5:
                score -= 15

        # Growth
        if len(financials) >= 2:
            if latest.revenue and financials[1].revenue:
                growth = (latest.revenue - financials[1].revenue) / financials[1].revenue
                if growth > 0.15:
                    score += 15
                elif growth < -0.05:
                    score -= 15

        summary["score"] = max(0, min(100, score))

        # Rating
        if score >= 80:
            summary["overall_rating"] = FinancialHealth.EXCELLENT.value
        elif score >= 60:
            summary["overall_rating"] = FinancialHealth.GOOD.value
        elif score >= 40:
            summary["overall_rating"] = FinancialHealth.FAIR.value
        elif score >= 20:
            summary["overall_rating"] = FinancialHealth.POOR.value
        else:
            summary["overall_rating"] = FinancialHealth.DISTRESSED.value

        return summary

    def _identify_red_flags(
        self,
        financials: List[FinancialSnapshot]
    ) -> List[str]:
        """Identify financial red flags"""
        red_flags = []
        latest = financials[0]

        # Unprofitable
        if latest.net_income and latest.net_income < 0:
            red_flags.append("Company is currently unprofitable")

        # High debt
        if latest.debt_to_equity_ratio and latest.debt_to_equity_ratio > 3.0:
            red_flags.append(f"Very high debt-to-equity ratio: {latest.debt_to_equity_ratio:.2f}")

        # Poor liquidity
        if latest.current_ratio and latest.current_ratio < 1.0:
            red_flags.append(f"Weak liquidity position (current ratio: {latest.current_ratio:.2f})")

        # Declining revenue
        if len(financials) >= 2:
            if latest.revenue and financials[1].revenue:
                if latest.revenue < financials[1].revenue * 0.9:  # 10%+ decline
                    red_flags.append("Significant revenue decline year-over-year")

        # Margin compression
        if len(financials) >= 2:
            if latest.profit_margin and financials[1].profit_margin:
                margin_change = latest.profit_margin - financials[1].profit_margin
                if margin_change < -0.05:  # 5% margin decline
                    red_flags.append("Margin compression detected")

        return red_flags

    def _identify_strengths(
        self,
        financials: List[FinancialSnapshot]
    ) -> List[str]:
        """Identify financial strengths"""
        strengths = []
        latest = financials[0]

        # Strong profitability
        if latest.profit_margin and latest.profit_margin > 0.15:
            strengths.append(f"Strong profit margins: {latest.profit_margin*100:.1f}%")

        # Low debt
        if latest.debt_to_equity_ratio and latest.debt_to_equity_ratio < 0.5:
            strengths.append("Conservative debt levels")

        # Strong liquidity
        if latest.current_ratio and latest.current_ratio > 2.0:
            strengths.append("Strong liquidity position")

        # Revenue growth
        if len(financials) >= 2:
            if latest.revenue and financials[1].revenue and financials[1].revenue > 0:
                growth = (latest.revenue - financials[1].revenue) / financials[1].revenue
                if growth > 0.20:
                    strengths.append(f"Strong revenue growth: {growth*100:.1f}%")

        # High ROE
        if latest.roe and latest.roe > 0.15:
            strengths.append(f"Excellent return on equity: {latest.roe*100:.1f}%")

        return strengths


# Singleton instance
_financial_analyzer: Optional[FinancialAnalyzer] = None


def get_financial_analyzer() -> FinancialAnalyzer:
    """Get or create financial analyzer instance"""
    global _financial_analyzer
    if _financial_analyzer is None:
        _financial_analyzer = FinancialAnalyzer()
    return _financial_analyzer
