"""Deal insight service generating AI-style probability and recommendations without LLM."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.deal import Deal, DealStage, DealPriority


@dataclass
class DealInsights:
    deal_id: str
    win_probability: int
    confidence: str
    risk_factors: List[str]
    recommended_actions: List[str]
    next_milestone: Optional[dict]


class DealInsightService:
    """Rule-based insights that combine deal metadata with heuristic scoring."""

    STAGE_BASE = {
        DealStage.SOURCING: 0.05,
        DealStage.INITIAL_REVIEW: 0.12,
        DealStage.NDA_EXECUTION: 0.18,
        DealStage.PRELIMINARY_ANALYSIS: 0.25,
        DealStage.VALUATION: 0.32,
        DealStage.DUE_DILIGENCE: 0.48,
        DealStage.NEGOTIATION: 0.6,
        DealStage.LOI_DRAFTING: 0.68,
        DealStage.DOCUMENTATION: 0.75,
        DealStage.CLOSING: 0.85,
        DealStage.CLOSED_WON: 0.97,
        DealStage.CLOSED_LOST: 0.02,
        DealStage.ON_HOLD: 0.35,
    }

    PRIORITY_ADJUSTMENTS = {
        DealPriority.CRITICAL: 0.08,
        DealPriority.HIGH: 0.05,
        DealPriority.MEDIUM: 0.0,
        DealPriority.LOW: -0.05,
    }

    def __init__(self, db: Session):
        self.db = db

    def generate_insights(self, deal_id: str, organization_id: str) -> DealInsights:
        deal = (
            self.db.query(Deal)
            .filter(Deal.id == deal_id, Deal.organization_id == organization_id)
            .first()
        )

        if not deal:
            raise ValueError("deal_not_found")

        base_score = self.STAGE_BASE.get(deal.stage, 0.1)
        base_score += self.PRIORITY_ADJUSTMENTS.get(deal.priority, 0.0)

        risk_penalty, risk_factors = self._calculate_risk_penalty(deal)
        base_score -= risk_penalty

        probability = base_score * 100

        if deal.probability_of_close is not None:
            probability = (probability + float(deal.probability_of_close)) / 2

        probability = max(1, min(int(round(probability)), 99))

        confidence = self._determine_confidence(deal, probability)
        recommendations = self._generate_recommendations(deal, probability, risk_factors)
        milestone = self._format_next_milestone(deal)

        return DealInsights(
            deal_id=str(deal.id),
            win_probability=probability,
            confidence=confidence,
            risk_factors=risk_factors,
            recommended_actions=recommendations,
            next_milestone=milestone,
        )

    def _calculate_risk_penalty(self, deal: Deal) -> tuple[float, List[str]]:
        factors: List[str] = []
        penalty = 0.0

        if deal.stage == DealStage.CLOSED_LOST:
            return 0.0, ["Deal marked as lost"]

        if deal.risk_level:
            mapped = deal.risk_level.lower()
            if mapped in {"high", "critical"}:
                penalty += 0.15
                factors.append(f"Risk level flagged as {mapped}")
            elif mapped == "medium":
                penalty += 0.05

        if deal.key_risks:
            factors.extend(deal.key_risks)
            penalty += min(0.02 * len(deal.key_risks), 0.1)

        if deal.expected_close_date:
            today = date.today()
            if deal.expected_close_date < today:
                overdue_days = (today - deal.expected_close_date).days
                penalty += min(overdue_days / 365, 0.2)
                factors.append(f"Close date overdue by {overdue_days} days")
            elif deal.expected_close_date <= today + timedelta(days=14):
                factors.append("Close date within next two weeks — ensure diligence is complete")

        if deal.stage in {DealStage.DUE_DILIGENCE, DealStage.NEGOTIATION} and not deal.documents.count():
            penalty += 0.08
            factors.append("No diligence documents uploaded")

        return penalty, factors

    def _determine_confidence(self, deal: Deal, probability: int) -> str:
        coverage = 0
        total = 0

        for attr in [
            deal.deal_value,
            deal.enterprise_value,
            deal.target_revenue,
            deal.target_ebitda,
            deal.expected_close_date,
            deal.next_milestone_date,
        ]:
            total += 1
            if attr is not None:
                coverage += 1

        coverage_ratio = coverage / total if total else 0

        if coverage_ratio >= 0.7 and probability >= 60:
            return "high"
        if coverage_ratio >= 0.4:
            return "medium"
        return "low"

    def _generate_recommendations(
        self, deal: Deal, probability: int, risk_factors: List[str]
    ) -> List[str]:
        actions: List[str] = []

        if probability < 50:
            actions.append("Escalate to deal sponsor for remediation plan")

        if deal.stage in {DealStage.SOURCING, DealStage.INITIAL_REVIEW} and deal.target_revenue is None:
            actions.append("Capture target financials to improve underwriting confidence")

        if deal.stage == DealStage.DUE_DILIGENCE and not risk_factors:
            actions.append("Document diligence findings to maintain audit trail")

        if deal.next_milestone_date and deal.next_milestone_date <= date.today():
            actions.append("Update next milestone to reflect current timeline")

        if not actions:
            actions.append("Continue with current plan; monitor weekly")

        return actions

    def _format_next_milestone(self, deal: Deal) -> Optional[dict]:
        if not deal.next_milestone_date and not deal.next_milestone_description:
            return None

        return {
            "date": deal.next_milestone_date.isoformat() if deal.next_milestone_date else None,
            "description": deal.next_milestone_description,
        }
