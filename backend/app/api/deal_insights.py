from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.tenant_service import get_current_user
from app.services.deal_insight_service import DealInsightService

router = APIRouter(prefix="/api/deals", tags=["deal-insights"])


@router.get("/{deal_id}/insights")
def get_deal_insights(deal_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    service = DealInsightService(db)
    try:
        insights = service.generate_insights(deal_id=deal_id, organization_id=str(current_user.organization_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Deal not found")

    return {
        "deal_id": insights.deal_id,
        "win_probability": insights.win_probability,
        "confidence": insights.confidence,
        "risk_factors": insights.risk_factors,
        "recommended_actions": insights.recommended_actions,
        "next_milestone": insights.next_milestone,
    }

