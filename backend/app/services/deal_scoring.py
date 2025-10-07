"""
Deal Scoring Algorithm
Advanced scoring and ranking system for M&A opportunities
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.deal_discovery import (
    Company,
    DealOpportunity,
    FinancialSnapshot,
    MarketIntelligence,
    FinancialHealth,
    IndustryCategory
)

logger = logging.getLogger(__name__)


class DealScoringEngine:
    """
    Multi-factor scoring engine for M&A opportunity evaluation
    Generates comprehensive scores based on financial, strategic, and market factors
    """

    # Scoring weights (total = 100%)
    WEIGHTS = {
        "financial_health": 0.30,      # 30% - Financial metrics and health
        "growth_potential": 0.25,       # 25% - Revenue growth and market expansion
        "strategic_fit": 0.20,          # 20% - Industry alignment and synergies
        "market_conditions": 0.15,      # 15% - Market sentiment and timing
        "execution_risk": 0.10          # 10% - Risk factors and deal complexity
    }

    def __init__(self):
        """Initialize scoring engine"""
        pass

    def calculate_opportunity_score(
        self,
        opportunity: DealOpportunity,
        db: Session,
        buyer_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive opportunity score

        Args:
            opportunity: DealOpportunity to score
            db: Database session
            buyer_profile: Optional buyer criteria for strategic fit scoring

        Returns:
            Scoring breakdown and final score
        """
        try:
            company = opportunity.company

            # Get latest financial snapshot
            latest_financials = db.query(FinancialSnapshot).filter(
                FinancialSnapshot.company_id == company.id
            ).order_by(FinancialSnapshot.period_year.desc()).first()

            # Get market intelligence
            market_intel = db.query(MarketIntelligence).filter(
                MarketIntelligence.company_id == company.id
            ).order_by(MarketIntelligence.created_at.desc()).all()

            # Calculate component scores
            financial_score = self._score_financial_health(
                opportunity,
                latest_financials
            )

            growth_score = self._score_growth_potential(
                company,
                latest_financials,
                db
            )

            strategic_score = self._score_strategic_fit(
                company,
                buyer_profile
            )

            market_score = self._score_market_conditions(
                company,
                market_intel
            )

            risk_score = self._score_execution_risk(
                opportunity,
                company,
                latest_financials
            )

            # Calculate weighted total score
            total_score = (
                financial_score * self.WEIGHTS["financial_health"] +
                growth_score * self.WEIGHTS["growth_potential"] +
                strategic_score * self.WEIGHTS["strategic_fit"] +
                market_score * self.WEIGHTS["market_conditions"] +
                risk_score * self.WEIGHTS["execution_risk"]
            )

            # Generate recommendation
            recommendation = self._generate_recommendation(total_score)

            scoring_breakdown = {
                "total_score": round(total_score, 1),
                "recommendation": recommendation,
                "component_scores": {
                    "financial_health": {
                        "score": round(financial_score, 1),
                        "weight": self.WEIGHTS["financial_health"] * 100,
                        "weighted_contribution": round(financial_score * self.WEIGHTS["financial_health"], 1)
                    },
                    "growth_potential": {
                        "score": round(growth_score, 1),
                        "weight": self.WEIGHTS["growth_potential"] * 100,
                        "weighted_contribution": round(growth_score * self.WEIGHTS["growth_potential"], 1)
                    },
                    "strategic_fit": {
                        "score": round(strategic_score, 1),
                        "weight": self.WEIGHTS["strategic_fit"] * 100,
                        "weighted_contribution": round(strategic_score * self.WEIGHTS["strategic_fit"], 1)
                    },
                    "market_conditions": {
                        "score": round(market_score, 1),
                        "weight": self.WEIGHTS["market_conditions"] * 100,
                        "weighted_contribution": round(market_score * self.WEIGHTS["market_conditions"], 1)
                    },
                    "execution_risk": {
                        "score": round(risk_score, 1),
                        "weight": self.WEIGHTS["execution_risk"] * 100,
                        "weighted_contribution": round(risk_score * self.WEIGHTS["execution_risk"], 1)
                    }
                },
                "scored_at": datetime.utcnow().isoformat()
            }

            # Update opportunity score
            opportunity.opportunity_score = round(total_score, 1)

            return scoring_breakdown

        except Exception as e:
            logger.error(f"Error calculating opportunity score: {e}")
            return {"total_score": 50, "recommendation": "neutral", "error": str(e)}

    def _score_financial_health(
        self,
        opportunity: DealOpportunity,
        financials: Optional[FinancialSnapshot]
    ) -> float:
        """
        Score financial health (0-100)

        Factors:
        - Profitability metrics
        - Liquidity and cash position
        - Debt levels
        - Financial stability
        """
        score = 50.0  # Base score

        # Financial health rating
        health_rating = opportunity.financial_health
        if health_rating == FinancialHealth.EXCELLENT:
            score += 30
        elif health_rating == FinancialHealth.GOOD:
            score += 20
        elif health_rating == FinancialHealth.FAIR:
            score += 5
        elif health_rating == FinancialHealth.POOR:
            score -= 15
        elif health_rating == FinancialHealth.DISTRESSED:
            score -= 30

        if not financials:
            return max(0, min(100, score))

        # Profitability
        if financials.profit_margin:
            if financials.profit_margin > 0.15:
                score += 15
            elif financials.profit_margin > 0.10:
                score += 10
            elif financials.profit_margin > 0.05:
                score += 5
            elif financials.profit_margin < 0:
                score -= 20

        # ROA (Return on Assets)
        if financials.roa:
            if financials.roa > 0.10:
                score += 10
            elif financials.roa > 0.05:
                score += 5
            elif financials.roa < 0:
                score -= 10

        # Debt to Equity
        if financials.debt_to_equity_ratio:
            if financials.debt_to_equity_ratio < 0.5:
                score += 10
            elif financials.debt_to_equity_ratio > 2.0:
                score -= 15

        # Current Ratio (liquidity)
        if financials.current_ratio:
            if financials.current_ratio > 2.0:
                score += 10
            elif financials.current_ratio > 1.5:
                score += 5
            elif financials.current_ratio < 1.0:
                score -= 15

        return max(0, min(100, score))

    def _score_growth_potential(
        self,
        company: Company,
        latest_financials: Optional[FinancialSnapshot],
        db: Session
    ) -> float:
        """
        Score growth potential (0-100)

        Factors:
        - Revenue growth rate
        - Market expansion opportunities
        - Industry growth trends
        """
        score = 50.0

        if not latest_financials:
            return score

        # Get historical financials for growth calculation
        historical = db.query(FinancialSnapshot).filter(
            FinancialSnapshot.company_id == company.id
        ).order_by(FinancialSnapshot.period_year.desc()).limit(4).all()

        if len(historical) >= 2:
            # Calculate revenue CAGR
            latest = historical[0]
            oldest = historical[-1]

            if latest.revenue and oldest.revenue and oldest.revenue > 0:
                years = latest.period_year - oldest.period_year
                if years > 0:
                    cagr = (pow(latest.revenue / oldest.revenue, 1 / years) - 1)

                    if cagr > 0.30:  # 30%+ growth
                        score += 30
                    elif cagr > 0.20:  # 20-30% growth
                        score += 20
                    elif cagr > 0.10:  # 10-20% growth
                        score += 10
                    elif cagr < -0.05:  # Declining
                        score -= 20

        # Revenue growth year-over-year
        if latest_financials.revenue_growth_yoy:
            if latest_financials.revenue_growth_yoy > 0.25:
                score += 15
            elif latest_financials.revenue_growth_yoy > 0.15:
                score += 10
            elif latest_financials.revenue_growth_yoy < -0.10:
                score -= 15

        # Margin expansion
        if latest_financials.profit_margin and len(historical) >= 2:
            prev_financials = historical[1] if len(historical) > 1 else None
            if prev_financials and prev_financials.profit_margin:
                margin_change = latest_financials.profit_margin - prev_financials.profit_margin
                if margin_change > 0.02:  # 2% margin improvement
                    score += 10
                elif margin_change < -0.05:  # 5% margin decline
                    score -= 10

        return max(0, min(100, score))

    def _score_strategic_fit(
        self,
        company: Company,
        buyer_profile: Optional[Dict[str, Any]]
    ) -> float:
        """
        Score strategic fit (0-100)

        Factors:
        - Industry alignment
        - Geographic fit
        - Technology/capability synergies
        - Cultural compatibility
        """
        score = 50.0

        if not buyer_profile:
            # No buyer profile provided, return neutral score
            return score

        # Industry alignment
        target_industries = buyer_profile.get("target_industries", [])
        if company.industry_category.value in target_industries:
            score += 25
        elif company.industry_category == IndustryCategory.TECHNOLOGY:
            # Technology companies often have cross-industry appeal
            score += 10

        # Geographic preferences
        target_regions = buyer_profile.get("target_regions", [])
        company_region = company.location_region or company.location_country
        if company_region and any(region.lower() in company_region.lower() for region in target_regions):
            score += 15

        # Size fit (revenue range)
        min_revenue = buyer_profile.get("min_revenue_millions", 0)
        max_revenue = buyer_profile.get("max_revenue_millions", float('inf'))

        # Estimate revenue (would use actual from financials in production)
        estimated_revenue_millions = 10  # Placeholder

        if min_revenue <= estimated_revenue_millions <= max_revenue:
            score += 15
        else:
            score -= 10

        # Cultural fit indicators
        if buyer_profile.get("prefers_family_owned") and company.company_type == "private":
            score += 10

        return max(0, min(100, score))

    def _score_market_conditions(
        self,
        company: Company,
        market_intel: List[MarketIntelligence]
    ) -> float:
        """
        Score market conditions and timing (0-100)

        Factors:
        - Market sentiment
        - Industry trends
        - M&A activity in sector
        - Economic indicators
        """
        score = 50.0

        if not market_intel:
            return score

        # Analyze recent news sentiment
        recent_intel = [m for m in market_intel if m.created_at >= datetime.utcnow().replace(day=1)]

        positive_signals = 0
        negative_signals = 0

        for intel in recent_intel[:20]:  # Latest 20 items
            content = intel.content or {}

            # Check for positive signals
            if content.get("signals_detected", {}).get("growth"):
                positive_signals += 1

            if content.get("signals_detected", {}).get("ma_activity"):
                positive_signals += 1  # M&A activity in sector is positive

            # Check for negative signals
            if content.get("signals_detected", {}).get("distress"):
                negative_signals += 1

        # Adjust score based on signals
        net_signals = positive_signals - negative_signals
        if net_signals > 5:
            score += 25
        elif net_signals > 2:
            score += 15
        elif net_signals < -3:
            score -= 20

        # Relevance scoring
        high_relevance_intel = [m for m in market_intel if m.relevance_score and m.relevance_score > 0.7]
        if len(high_relevance_intel) > 5:
            score += 10

        return max(0, min(100, score))

    def _score_execution_risk(
        self,
        opportunity: DealOpportunity,
        company: Company,
        financials: Optional[FinancialSnapshot]
    ) -> float:
        """
        Score execution risk (lower risk = higher score) (0-100)

        Factors:
        - Deal complexity
        - Integration challenges
        - Regulatory considerations
        - Financial stability
        """
        score = 70.0  # Start optimistic

        # Size-based risk (very large or very small deals have higher risk)
        if opportunity.estimated_valuation:
            valuation_millions = opportunity.estimated_valuation / 1_000_000
            if valuation_millions > 100:  # Large deal
                score -= 10
            elif valuation_millions < 0.5:  # Very small
                score -= 15

        # Financial health risk
        if opportunity.financial_health == FinancialHealth.DISTRESSED:
            score -= 30
        elif opportunity.financial_health == FinancialHealth.POOR:
            score -= 15
        elif opportunity.financial_health == FinancialHealth.EXCELLENT:
            score += 10

        # Liquidity risk
        if financials and financials.current_ratio:
            if financials.current_ratio < 1.0:
                score -= 15  # Liquidity concerns
            elif financials.current_ratio > 2.0:
                score += 10  # Strong liquidity

        # Debt burden risk
        if financials and financials.debt_to_equity_ratio:
            if financials.debt_to_equity_ratio > 3.0:
                score -= 20  # High leverage risk
            elif financials.debt_to_equity_ratio < 0.3:
                score += 10  # Low debt

        # Geographic/regulatory risk
        if company.location_country:
            # Simplified risk assessment
            low_risk_countries = ["United States", "United Kingdom", "Canada", "Germany", "France"]
            if company.location_country not in low_risk_countries:
                score -= 10

        # Data completeness (missing data = higher risk)
        if not financials:
            score -= 20

        if not company.website:
            score -= 5

        return max(0, min(100, score))

    def _generate_recommendation(self, score: float) -> str:
        """Generate recommendation based on score"""
        if score >= 80:
            return "strong_buy"
        elif score >= 65:
            return "buy"
        elif score >= 50:
            return "consider"
        elif score >= 35:
            return "pass"
        else:
            return "avoid"

    def rank_opportunities(
        self,
        opportunities: List[DealOpportunity],
        db: Session,
        buyer_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank and score multiple opportunities

        Args:
            opportunities: List of opportunities to rank
            db: Database session
            buyer_profile: Optional buyer criteria

        Returns:
            Ranked list with scoring breakdowns
        """
        ranked = []

        for opp in opportunities:
            try:
                scoring = self.calculate_opportunity_score(opp, db, buyer_profile)

                ranked.append({
                    "opportunity_id": str(opp.id),
                    "company_name": opp.company.name,
                    "score": scoring["total_score"],
                    "recommendation": scoring["recommendation"],
                    "scoring_breakdown": scoring
                })

            except Exception as e:
                logger.error(f"Error ranking opportunity {opp.id}: {e}")
                continue

        # Sort by score descending
        ranked.sort(key=lambda x: x["score"], reverse=True)

        return ranked


# Singleton instance
_scoring_engine: Optional[DealScoringEngine] = None


def get_scoring_engine() -> DealScoringEngine:
    """Get or create scoring engine instance"""
    global _scoring_engine
    if _scoring_engine is None:
        _scoring_engine = DealScoringEngine()
    return _scoring_engine
