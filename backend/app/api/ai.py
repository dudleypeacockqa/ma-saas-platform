from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.models.models import Deal, User
from app.services.tenant_service import get_current_user, require_analyst
from app.services.claude_service import (
    claude_service, 
    DealAnalysisRequest, 
    DealAnalysisResponse,
    MarketResearchRequest,
    MarketResearchResponse
)

router = APIRouter()

@router.post("/analyze-deal", response_model=DealAnalysisResponse)
async def analyze_deal(
    request: DealAnalysisRequest,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Analyze a deal using Claude AI"""
    
    # Check if user has access to Claude features based on subscription
    if current_user.tenant.subscription_plan.value == "solo" and not current_user.role.value in ["master_admin", "tenant_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI analysis requires Growth plan or higher"
        )
    
    try:
        analysis = await claude_service.analyze_deal(request)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/analyze-deal/{deal_id}", response_model=DealAnalysisResponse)
async def analyze_existing_deal(
    deal_id: int,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Analyze an existing deal from the database"""
    
    # Get the deal
    deal = db.query(Deal).filter(
        Deal.id == deal_id,
        Deal.tenant_id == current_user.tenant_id,
        Deal.is_active == True
    ).first()
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    # Check subscription access
    if current_user.tenant.subscription_plan.value == "solo" and not current_user.role.value in ["master_admin", "tenant_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI analysis requires Growth plan or higher"
        )
    
    # Create analysis request from deal data
    request = DealAnalysisRequest(
        deal_name=deal.name,
        target_company=deal.target_company or "Unknown",
        deal_value=float(deal.deal_value) if deal.deal_value else None,
        description=deal.description
    )
    
    try:
        analysis = await claude_service.analyze_deal(request)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/market-research", response_model=MarketResearchResponse)
async def research_market(
    request: MarketResearchRequest,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Research market conditions for M&A opportunities"""
    
    # Check subscription access
    if current_user.tenant.subscription_plan.value == "solo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Market research requires Growth plan or higher"
        )
    
    try:
        research = await claude_service.research_market(request)
        return research
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market research failed: {str(e)}"
        )

@router.post("/analyze-document")
async def analyze_document(
    document_content: str,
    document_type: str = "general",
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Analyze document content using Claude AI"""
    
    # Check subscription access
    if current_user.tenant.subscription_plan.value == "solo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document analysis requires Growth plan or higher"
        )
    
    if len(document_content) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document content too large (max 10,000 characters)"
        )
    
    try:
        analysis = await claude_service.analyze_document(document_content, document_type)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document analysis failed: {str(e)}"
        )

@router.get("/features")
async def get_ai_features(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get available AI features based on subscription plan"""
    
    subscription_plan = current_user.tenant.subscription_plan.value
    
    features = {
        "deal_analysis": False,
        "market_research": False,
        "document_analysis": False,
        "advanced_analytics": False,
        "api_access": False
    }
    
    if subscription_plan in ["growth", "enterprise", "custom"]:
        features.update({
            "deal_analysis": True,
            "market_research": True,
            "document_analysis": True
        })
    
    if subscription_plan in ["enterprise", "custom"]:
        features.update({
            "advanced_analytics": True,
            "api_access": True
        })
    
    # Master admin always has access to all features
    if current_user.role.value == "master_admin":
        features = {key: True for key in features}
    
    return {
        "subscription_plan": subscription_plan,
        "available_features": features,
        "upgrade_required": subscription_plan == "solo"
    }
