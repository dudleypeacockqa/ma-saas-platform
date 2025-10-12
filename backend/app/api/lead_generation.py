"""
Lead Generation and Marketing Automation API
Advanced lead scoring, multi-channel campaigns, and automated nurture sequences
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr
import logging
import json

from app.core.database import get_db
from app.auth.clerk_auth import ClerkUser, get_current_user, require_admin
from app.models.lead_generation import (
    Lead, LeadActivity, LeadScoringRule, LeadScoringHistory, MarketingCampaign,
    EmailCampaign, EmailList, EmailSubscription, EmailSend, MarketingAutomation,
    AutomationEnrollment, CampaignInteraction, AttributionModel,
    LeadSource, LeadStatus, LeadQuality, CampaignType, CampaignStatus,
    AutomationTrigger, EmailStatus
)
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/leads", tags=["lead-generation"])

# ============================================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE
# ============================================================================

class LeadCreate(BaseModel):
    """Create lead"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    source: LeadSource
    source_details: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    interested_products: Optional[List[str]] = None
    pain_points: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

class LeadUpdate(BaseModel):
    """Update lead"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    status: Optional[LeadStatus] = None
    quality: Optional[LeadQuality] = None
    qualification_notes: Optional[str] = None
    interested_products: Optional[List[str]] = None
    pain_points: Optional[List[str]] = None
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    decision_maker: Optional[bool] = None
    next_follow_up: Optional[datetime] = None

class MarketingCampaignCreate(BaseModel):
    """Create marketing campaign"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    campaign_type: CampaignType
    target_audience: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: float = 0.0
    lead_target: Optional[int] = None
    landing_page_url: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None

class EmailCampaignCreate(BaseModel):
    """Create email campaign"""
    parent_campaign_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    subject_line: str = Field(..., min_length=1, max_length=300)
    from_name: str = Field(..., min_length=1, max_length=100)
    from_email: EmailStr
    html_content: str
    text_content: Optional[str] = None
    recipient_list_id: Optional[str] = None
    scheduled_send_date: Optional[datetime] = None
    is_ab_test: bool = False

class LeadScoringRuleCreate(BaseModel):
    """Create lead scoring rule"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=100)
    criteria: Dict[str, Any]
    score_value: int
    is_recurring: bool = False
    max_score: Optional[int] = None

class MarketingAutomationCreate(BaseModel):
    """Create marketing automation"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    trigger_type: AutomationTrigger
    trigger_criteria: Dict[str, Any]
    workflow_steps: List[Dict[str, Any]]
    target_criteria: Optional[Dict[str, Any]] = None
    allow_re_enrollment: bool = False

# ============================================================================
# LEAD MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/", response_model=Dict[str, Any])
async def create_lead(
    lead_data: LeadCreate,
    background_tasks: BackgroundTasks,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new lead"""
    try:
        # Check for duplicate email
        existing_lead = db.query(Lead).filter(Lead.email == lead_data.email).first()
        if existing_lead:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lead with this email already exists"
            )
        
        lead = Lead(
            first_name=lead_data.first_name,
            last_name=lead_data.last_name,
            email=lead_data.email,
            phone=lead_data.phone,
            company=lead_data.company,
            job_title=lead_data.job_title,
            industry=lead_data.industry,
            company_size=lead_data.company_size,
            source=lead_data.source,
            source_details=lead_data.source_details,
            utm_campaign=lead_data.utm_campaign,
            utm_source=lead_data.utm_source,
            utm_medium=lead_data.utm_medium,
            interested_products=lead_data.interested_products,
            pain_points=lead_data.pain_points,
            custom_fields=lead_data.custom_fields,
            assigned_to=current_user.user_id
        )
        
        db.add(lead)
        db.commit()
        db.refresh(lead)
        
        # Create initial activity
        activity = LeadActivity(
            lead_id=lead.id,
            activity_type="lead_created",
            activity_description=f"Lead created from {lead_data.source.value}",
            activity_data={"source": lead_data.source.value, "created_by": current_user.user_id}
        )
        db.add(activity)
        db.commit()
        
        # Schedule lead scoring
        background_tasks.add_task(_calculate_lead_score, lead.id)
        
        # Check for automation triggers
        background_tasks.add_task(_check_automation_triggers, lead.id, "lead_created")
        
        return {
            "lead": lead,
            "message": "Lead created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create lead"
        )

@router.get("/")
async def get_leads(
    status: Optional[LeadStatus] = None,
    quality: Optional[LeadQuality] = None,
    source: Optional[LeadSource] = None,
    assigned_to: Optional[str] = None,
    min_score: Optional[int] = None,
    created_after: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leads with filtering"""
    try:
        query = db.query(Lead)
        
        if status:
            query = query.filter(Lead.status == status)
        if quality:
            query = query.filter(Lead.quality == quality)
        if source:
            query = query.filter(Lead.source == source)
        if assigned_to:
            query = query.filter(Lead.assigned_to == assigned_to)
        if min_score:
            query = query.filter(Lead.lead_score >= min_score)
        if created_after:
            query = query.filter(Lead.created_at >= created_after)
        
        total_count = query.count()
        leads = query.order_by(desc(Lead.lead_score), desc(Lead.created_at)).offset(offset).limit(limit).all()
        
        return {
            "leads": leads,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching leads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch leads"
        )

@router.get("/{lead_id}")
async def get_lead_details(
    lead_id: str,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed lead information"""
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        # Get recent activities
        recent_activities = db.query(LeadActivity).filter(
            LeadActivity.lead_id == lead_id
        ).order_by(desc(LeadActivity.activity_date)).limit(20).all()
        
        # Get scoring history
        scoring_history = db.query(LeadScoringHistory).filter(
            LeadScoringHistory.lead_id == lead_id
        ).order_by(desc(LeadScoringHistory.scored_at)).limit(10).all()
        
        # Get campaign interactions
        campaign_interactions = db.query(CampaignInteraction).filter(
            CampaignInteraction.lead_id == lead_id
        ).order_by(desc(CampaignInteraction.interaction_date)).limit(10).all()
        
        return {
            "lead": lead,
            "recent_activities": recent_activities,
            "scoring_history": scoring_history,
            "campaign_interactions": campaign_interactions
        }
        
    except Exception as e:
        logger.error(f"Error fetching lead details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch lead details"
        )

@router.put("/{lead_id}")
async def update_lead(
    lead_id: str,
    lead_update: LeadUpdate,
    background_tasks: BackgroundTasks,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update lead information"""
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        # Track changes for activity log
        changes = {}
        
        # Update fields
        update_data = lead_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(lead, field) and getattr(lead, field) != value:
                changes[field] = {"old": getattr(lead, field), "new": value}
                setattr(lead, field, value)
        
        lead.updated_at = datetime.utcnow()
        lead.last_activity_date = datetime.utcnow()
        
        db.commit()
        db.refresh(lead)
        
        # Log activity if there were changes
        if changes:
            activity = LeadActivity(
                lead_id=lead.id,
                activity_type="lead_updated",
                activity_description="Lead information updated",
                activity_data={"changes": changes, "updated_by": current_user.user_id}
            )
            db.add(activity)
            db.commit()
            
            # Recalculate lead score if relevant fields changed
            if any(field in changes for field in ['company_size', 'industry', 'job_title', 'budget_range']):
                background_tasks.add_task(_calculate_lead_score, lead.id)
        
        return {
            "lead": lead,
            "changes": changes,
            "message": "Lead updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating lead: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update lead"
        )

@router.post("/{lead_id}/activities")
async def add_lead_activity(
    lead_id: str,
    activity_type: str,
    activity_description: str,
    activity_data: Optional[Dict[str, Any]] = None,
    score_change: int = 0,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add activity to lead"""
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        activity = LeadActivity(
            lead_id=lead_id,
            activity_type=activity_type,
            activity_description=activity_description,
            activity_data=activity_data or {},
            score_change=score_change
        )
        
        db.add(activity)
        
        # Update lead score and activity date
        if score_change != 0:
            lead.lead_score += score_change
            
            # Create scoring history entry
            scoring_history = LeadScoringHistory(
                lead_id=lead_id,
                previous_score=lead.lead_score - score_change,
                score_change=score_change,
                new_score=lead.lead_score,
                reason=activity_description,
                activity_id=activity.id
            )
            db.add(scoring_history)
        
        lead.last_activity_date = datetime.utcnow()
        
        # Update engagement metrics based on activity type
        if activity_type == "email_open":
            lead.email_opens += 1
        elif activity_type == "email_click":
            lead.email_clicks += 1
        elif activity_type == "website_visit":
            lead.website_visits += 1
        elif activity_type == "content_download":
            lead.content_downloads += 1
        
        db.commit()
        db.refresh(activity)
        
        return {
            "activity": activity,
            "lead_score": lead.lead_score,
            "message": "Activity added successfully"
        }
        
    except Exception as e:
        logger.error(f"Error adding lead activity: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add lead activity"
        )

# ============================================================================
# LEAD SCORING ENDPOINTS
# ============================================================================

@router.post("/scoring-rules", response_model=Dict[str, Any])
async def create_scoring_rule(
    rule_data: LeadScoringRuleCreate,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create lead scoring rule"""
    try:
        rule = LeadScoringRule(
            name=rule_data.name,
            description=rule_data.description,
            category=rule_data.category,
            criteria=rule_data.criteria,
            score_value=rule_data.score_value,
            is_recurring=rule_data.is_recurring,
            max_score=rule_data.max_score,
            created_by=current_user.user_id
        )
        
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        return {
            "rule": rule,
            "message": "Scoring rule created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating scoring rule: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scoring rule"
        )

@router.get("/scoring-rules")
async def get_scoring_rules(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get lead scoring rules"""
    try:
        query = db.query(LeadScoringRule)
        
        if category:
            query = query.filter(LeadScoringRule.category == category)
        if is_active is not None:
            query = query.filter(LeadScoringRule.is_active == is_active)
        
        rules = query.order_by(LeadScoringRule.priority.desc(), LeadScoringRule.created_at).all()
        
        return {
            "rules": rules,
            "count": len(rules)
        }
        
    except Exception as e:
        logger.error(f"Error fetching scoring rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch scoring rules"
        )

@router.post("/{lead_id}/recalculate-score")
async def recalculate_lead_score(
    lead_id: str,
    background_tasks: BackgroundTasks,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recalculate lead score"""
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        # Schedule background score calculation
        background_tasks.add_task(_calculate_lead_score, lead_id)
        
        return {
            "message": "Lead score recalculation scheduled",
            "lead_id": lead_id
        }
        
    except Exception as e:
        logger.error(f"Error scheduling score recalculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule score recalculation"
        )

# ============================================================================
# MARKETING CAMPAIGN ENDPOINTS
# ============================================================================

@router.post("/campaigns", response_model=Dict[str, Any])
async def create_marketing_campaign(
    campaign_data: MarketingCampaignCreate,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create marketing campaign"""
    try:
        campaign = MarketingCampaign(
            name=campaign_data.name,
            description=campaign_data.description,
            campaign_type=campaign_data.campaign_type,
            target_audience=campaign_data.target_audience,
            start_date=campaign_data.start_date,
            end_date=campaign_data.end_date,
            budget=campaign_data.budget,
            lead_target=campaign_data.lead_target,
            landing_page_url=campaign_data.landing_page_url,
            utm_campaign=campaign_data.utm_campaign,
            utm_source=campaign_data.utm_source,
            utm_medium=campaign_data.utm_medium,
            created_by=current_user.user_id
        )
        
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        return {
            "campaign": campaign,
            "message": "Marketing campaign created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating marketing campaign: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create marketing campaign"
        )

@router.get("/campaigns")
async def get_marketing_campaigns(
    campaign_type: Optional[CampaignType] = None,
    status: Optional[CampaignStatus] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get marketing campaigns"""
    try:
        query = db.query(MarketingCampaign)
        
        if campaign_type:
            query = query.filter(MarketingCampaign.campaign_type == campaign_type)
        if status:
            query = query.filter(MarketingCampaign.status == status)
        
        total_count = query.count()
        campaigns = query.order_by(desc(MarketingCampaign.created_at)).offset(offset).limit(limit).all()
        
        return {
            "campaigns": campaigns,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching marketing campaigns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch marketing campaigns"
        )

@router.get("/campaigns/{campaign_id}/analytics")
async def get_campaign_analytics(
    campaign_id: str,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get campaign analytics"""
    try:
        campaign = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Get interaction statistics
        interactions = db.query(CampaignInteraction).filter(
            CampaignInteraction.campaign_id == campaign_id
        ).all()
        
        # Calculate metrics
        total_interactions = len(interactions)
        unique_leads = len(set(interaction.lead_id for interaction in interactions))
        
        interaction_types = {}
        for interaction in interactions:
            interaction_types[interaction.interaction_type] = interaction_types.get(interaction.interaction_type, 0) + 1
        
        # Get leads generated
        leads_generated = db.query(Lead).filter(
            Lead.utm_campaign == campaign.utm_campaign
        ).count() if campaign.utm_campaign else 0
        
        return {
            "campaign": campaign,
            "analytics": {
                "total_interactions": total_interactions,
                "unique_leads": unique_leads,
                "leads_generated": leads_generated,
                "interaction_breakdown": interaction_types,
                "cost_per_lead": campaign.total_cost / leads_generated if leads_generated > 0 else 0,
                "conversion_rate": (campaign.conversions / leads_generated * 100) if leads_generated > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching campaign analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch campaign analytics"
        )

# ============================================================================
# EMAIL CAMPAIGN ENDPOINTS
# ============================================================================

@router.post("/email-campaigns", response_model=Dict[str, Any])
async def create_email_campaign(
    campaign_data: EmailCampaignCreate,
    background_tasks: BackgroundTasks,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create email campaign"""
    try:
        campaign = EmailCampaign(
            parent_campaign_id=campaign_data.parent_campaign_id,
            name=campaign_data.name,
            subject_line=campaign_data.subject_line,
            from_name=campaign_data.from_name,
            from_email=campaign_data.from_email,
            html_content=campaign_data.html_content,
            text_content=campaign_data.text_content,
            recipient_list_id=campaign_data.recipient_list_id,
            scheduled_send_date=campaign_data.scheduled_send_date,
            is_ab_test=campaign_data.is_ab_test,
            created_by=current_user.user_id
        )
        
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        # Schedule sending if immediate or scheduled
        if not campaign_data.scheduled_send_date or campaign_data.scheduled_send_date <= datetime.utcnow():
            background_tasks.add_task(_send_email_campaign, campaign.id)
        
        return {
            "campaign": campaign,
            "message": "Email campaign created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating email campaign: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create email campaign"
        )

# ============================================================================
# MARKETING AUTOMATION ENDPOINTS
# ============================================================================

@router.post("/automations", response_model=Dict[str, Any])
async def create_marketing_automation(
    automation_data: MarketingAutomationCreate,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create marketing automation"""
    try:
        automation = MarketingAutomation(
            name=automation_data.name,
            description=automation_data.description,
            trigger_type=automation_data.trigger_type,
            trigger_criteria=automation_data.trigger_criteria,
            workflow_steps=automation_data.workflow_steps,
            target_criteria=automation_data.target_criteria,
            allow_re_enrollment=automation_data.allow_re_enrollment,
            created_by=current_user.user_id
        )
        
        db.add(automation)
        db.commit()
        db.refresh(automation)
        
        return {
            "automation": automation,
            "message": "Marketing automation created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating marketing automation: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create marketing automation"
        )

@router.get("/automations")
async def get_marketing_automations(
    is_active: Optional[bool] = None,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get marketing automations"""
    try:
        query = db.query(MarketingAutomation)
        
        if is_active is not None:
            query = query.filter(MarketingAutomation.is_active == is_active)
        
        automations = query.order_by(desc(MarketingAutomation.created_at)).all()
        
        return {
            "automations": automations,
            "count": len(automations)
        }
        
    except Exception as e:
        logger.error(f"Error fetching marketing automations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch marketing automations"
        )

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics/overview")
async def get_lead_analytics_overview(
    period: str = "30d",
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get lead generation analytics overview"""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Get lead statistics
        total_leads = db.query(Lead).count()
        new_leads = db.query(Lead).filter(Lead.created_at >= start_date).count()
        qualified_leads = db.query(Lead).filter(
            Lead.quality.in_([LeadQuality.HOT, LeadQuality.QUALIFIED])
        ).count()
        converted_leads = db.query(Lead).filter(Lead.converted_to_customer == True).count()
        
        # Get source breakdown
        source_breakdown = db.query(
            Lead.source,
            func.count(Lead.id).label("count")
        ).filter(Lead.created_at >= start_date).group_by(Lead.source).all()
        
        # Get quality distribution
        quality_breakdown = db.query(
            Lead.quality,
            func.count(Lead.id).label("count")
        ).group_by(Lead.quality).all()
        
        # Get average lead score
        avg_lead_score = db.query(func.avg(Lead.lead_score)).scalar() or 0
        
        # Get campaign performance
        campaign_performance = db.query(
            MarketingCampaign.name,
            MarketingCampaign.leads_generated,
            MarketingCampaign.cost_per_lead,
            MarketingCampaign.conversion_rate
        ).filter(
            MarketingCampaign.status == CampaignStatus.ACTIVE
        ).order_by(desc(MarketingCampaign.leads_generated)).limit(5).all()
        
        return {
            "period": period,
            "overview": {
                "total_leads": total_leads,
                "new_leads": new_leads,
                "qualified_leads": qualified_leads,
                "converted_leads": converted_leads,
                "conversion_rate": (converted_leads / total_leads * 100) if total_leads > 0 else 0,
                "average_lead_score": round(float(avg_lead_score), 1)
            },
            "source_breakdown": [
                {
                    "source": breakdown.source.value,
                    "count": breakdown.count
                }
                for breakdown in source_breakdown
            ],
            "quality_breakdown": [
                {
                    "quality": breakdown.quality.value,
                    "count": breakdown.count
                }
                for breakdown in quality_breakdown
            ],
            "top_campaigns": [
                {
                    "name": campaign.name,
                    "leads_generated": campaign.leads_generated,
                    "cost_per_lead": campaign.cost_per_lead,
                    "conversion_rate": campaign.conversion_rate
                }
                for campaign in campaign_performance
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching lead analytics overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch lead analytics overview"
        )

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def _calculate_lead_score(lead_id: str):
    """Calculate lead score based on scoring rules"""
    logger.info(f"Calculating lead score for {lead_id}")
    # This would implement the actual lead scoring logic

async def _check_automation_triggers(lead_id: str, trigger_event: str):
    """Check if lead should be enrolled in any automations"""
    logger.info(f"Checking automation triggers for lead {lead_id}, event: {trigger_event}")
    # This would implement automation trigger checking

async def _send_email_campaign(campaign_id: str):
    """Send email campaign to recipients"""
    logger.info(f"Sending email campaign {campaign_id}")
    # This would implement email sending logic
