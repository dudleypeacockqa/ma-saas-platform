"""
Marketing API endpoints for subscriber acquisition and campaign management.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import json

from app.core.database import get_db
from app.models.prospects import (
    Prospect, OutreachCampaign, OutreachAttempt,
    ProspectActivity, MessageTemplate
)
from app.auth.clerk_auth import ClerkUser, get_current_user, require_admin
from app.agents.acquisition_agent import SubscriberAcquisitionAgent
from app.services.outreach_service import OutreachAutomation, EmailService
from app.integrations.linkedin_api import LinkedInAPI
from pydantic import BaseModel, Field, EmailStr

router = APIRouter(prefix="/api/marketing", tags=["marketing"])

# Request/Response models
class ProspectCreate(BaseModel):
    """Model for creating a new prospect."""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    linkedin_url: Optional[str] = None
    source: str = Field(default="manual", pattern="^(linkedin|website|referral|content|manual)$")
    tags: List[str] = []
    custom_data: Dict[str, Any] = {}

class CampaignCreate(BaseModel):
    """Model for creating a new outreach campaign."""
    name: str
    type: str = Field(pattern="^(email|linkedin|multi_channel)$")
    template_id: Optional[UUID] = None
    target_tags: List[str] = []
    schedule_type: str = Field(default="immediate", pattern="^(immediate|scheduled|recurring)$")
    schedule_config: Dict[str, Any] = {}
    settings: Dict[str, Any] = {}

class MessageTemplateCreate(BaseModel):
    """Model for creating a message template."""
    name: str
    type: str = Field(pattern="^(email|linkedin)$")
    subject: Optional[str] = None
    body: str
    variables: List[str] = []
    tags: List[str] = []

class TrackingEvent(BaseModel):
    """Model for tracking events."""
    event_type: str = Field(pattern="^(email_open|link_click|reply|unsubscribe)$")
    prospect_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    attempt_id: Optional[UUID] = None
    metadata: Dict[str, Any] = {}

# Initialize services
acquisition_agent = None
outreach_automation = None
email_service = None

def get_acquisition_agent(db: Session) -> SubscriberAcquisitionAgent:
    """Get or create acquisition agent instance."""
    global acquisition_agent
    if not acquisition_agent:
        acquisition_agent = SubscriberAcquisitionAgent(db)
    return acquisition_agent

def get_outreach_automation(db: Session) -> OutreachAutomation:
    """Get or create outreach automation instance."""
    global outreach_automation
    if not outreach_automation:
        outreach_automation = OutreachAutomation(db)
    return outreach_automation

# Prospect Management Endpoints
@router.get("/prospects")
async def list_prospects(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    tags: Optional[str] = None
):
    """List all prospects with filtering options."""
    query = db.query(Prospect).filter(
        Prospect.organization_id == current_user.organization_id
    )

    if status:
        query = query.filter(Prospect.status == status)

    if tags:
        tag_list = tags.split(",")
        query = query.filter(Prospect.tags.contains(tag_list))

    prospects = query.offset(skip).limit(limit).all()
    total = query.count()

    return {
        "prospects": prospects,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/prospects")
async def create_prospect(
    prospect: ProspectCreate,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Create a new prospect."""
    db_prospect = Prospect(
        organization_id=current_user.organization_id,
        email=prospect.email,
        first_name=prospect.first_name,
        last_name=prospect.last_name,
        company_name=prospect.company_name,
        job_title=prospect.job_title,
        linkedin_url=prospect.linkedin_url,
        source=prospect.source,
        tags=prospect.tags,
        custom_data=prospect.custom_data,
        lead_score=0,
        status="new"
    )

    db.add(db_prospect)
    db.commit()
    db.refresh(db_prospect)

    # Enrich prospect data in background
    agent = get_acquisition_agent(db)
    background_tasks.add_task(
        agent.prospect_identifier.enrich_prospect,
        db_prospect.id
    )

    return db_prospect

@router.get("/prospects/{prospect_id}")
async def get_prospect(
    prospect_id: UUID,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific prospect by ID."""
    prospect = db.query(Prospect).filter(
        Prospect.id == prospect_id,
        Prospect.organization_id == current_user.organization_id
    ).first()

    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")

    # Include activity history
    activities = db.query(ProspectActivity).filter(
        ProspectActivity.prospect_id == prospect_id
    ).order_by(ProspectActivity.created_at.desc()).limit(20).all()

    return {
        "prospect": prospect,
        "activities": activities
    }

@router.delete("/prospects/{prospect_id}")
async def delete_prospect(
    prospect_id: UUID,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a prospect (soft delete)."""
    prospect = db.query(Prospect).filter(
        Prospect.id == prospect_id,
        Prospect.organization_id == current_user.organization_id
    ).first()

    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")

    prospect.deleted_at = datetime.utcnow()
    db.commit()

    return {"message": "Prospect deleted successfully"}

# Campaign Management Endpoints
@router.get("/campaigns")
async def list_campaigns(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: Optional[str] = None
):
    """List all outreach campaigns."""
    query = db.query(OutreachCampaign).filter(
        OutreachCampaign.organization_id == current_user.organization_id
    )

    if status:
        query = query.filter(OutreachCampaign.status == status)

    campaigns = query.all()

    # Add performance metrics
    for campaign in campaigns:
        attempts = db.query(OutreachAttempt).filter(
            OutreachAttempt.campaign_id == campaign.id
        ).all()

        campaign.metrics = {
            "total_sent": len(attempts),
            "opened": sum(1 for a in attempts if a.opened_at),
            "clicked": sum(1 for a in attempts if a.clicked_at),
            "replied": sum(1 for a in attempts if a.replied_at),
            "open_rate": (sum(1 for a in attempts if a.opened_at) / len(attempts) * 100) if attempts else 0,
            "click_rate": (sum(1 for a in attempts if a.clicked_at) / len(attempts) * 100) if attempts else 0
        }

    return campaigns

@router.post("/campaigns")
async def create_campaign(
    campaign: CampaignCreate,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Create a new outreach campaign."""
    db_campaign = OutreachCampaign(
        organization_id=current_user.organization_id,
        name=campaign.name,
        type=campaign.type,
        template_id=campaign.template_id,
        target_audience={"tags": campaign.target_tags},
        schedule=campaign.schedule_config,
        settings=campaign.settings,
        status="draft",
        metrics={}
    )

    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)

    return db_campaign

@router.post("/campaigns/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: UUID,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Launch an outreach campaign."""
    campaign = db.query(OutreachCampaign).filter(
        OutreachCampaign.id == campaign_id,
        OutreachCampaign.organization_id == current_user.organization_id
    ).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status != "draft":
        raise HTTPException(status_code=400, detail="Campaign already launched")

    # Update status
    campaign.status = "active"
    campaign.started_at = datetime.utcnow()
    db.commit()

    # Execute campaign in background
    automation = get_outreach_automation(db)
    background_tasks.add_task(
        automation.execute_campaign,
        campaign_id
    )

    return {"message": "Campaign launched successfully", "campaign_id": campaign_id}

@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: UUID,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pause an active campaign."""
    campaign = db.query(OutreachCampaign).filter(
        OutreachCampaign.id == campaign_id,
        OutreachCampaign.organization_id == current_user.organization_id
    ).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status != "active":
        raise HTTPException(status_code=400, detail="Campaign not active")

    campaign.status = "paused"
    db.commit()

    return {"message": "Campaign paused successfully"}

# Template Management Endpoints
@router.get("/templates")
async def list_templates(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    type: Optional[str] = None
):
    """List all message templates."""
    query = db.query(MessageTemplate).filter(
        MessageTemplate.organization_id == current_user.organization_id
    )

    if type:
        query = query.filter(MessageTemplate.type == type)

    templates = query.all()
    return templates

@router.post("/templates")
async def create_template(
    template: MessageTemplateCreate,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new message template."""
    db_template = MessageTemplate(
        organization_id=current_user.organization_id,
        name=template.name,
        type=template.type,
        subject=template.subject,
        body=template.body,
        variables=template.variables,
        tags=template.tags,
        performance_metrics={}
    )

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return db_template

# Tracking Endpoints
@router.post("/track/open")
async def track_email_open(
    request: Request,
    tracking_id: str,
    db: Session = Depends(get_db)
):
    """Track email open events."""
    # Parse tracking ID
    try:
        data = json.loads(tracking_id)
        attempt_id = data.get("attempt_id")
        prospect_id = data.get("prospect_id")
    except:
        raise HTTPException(status_code=400, detail="Invalid tracking ID")

    # Update attempt
    attempt = db.query(OutreachAttempt).filter(
        OutreachAttempt.id == attempt_id
    ).first()

    if attempt and not attempt.opened_at:
        attempt.opened_at = datetime.utcnow()

        # Log activity
        activity = ProspectActivity(
            prospect_id=prospect_id,
            type="email_opened",
            description=f"Opened email from campaign",
            metadata={"ip": request.client.host}
        )
        db.add(activity)
        db.commit()

    # Return 1x1 transparent pixel
    return Response(
        content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B',
        media_type="image/gif"
    )

@router.post("/track/click")
async def track_link_click(
    tracking_id: str,
    url: str,
    db: Session = Depends(get_db)
):
    """Track link click events."""
    try:
        data = json.loads(tracking_id)
        attempt_id = data.get("attempt_id")
        prospect_id = data.get("prospect_id")
    except:
        raise HTTPException(status_code=400, detail="Invalid tracking ID")

    # Update attempt
    attempt = db.query(OutreachAttempt).filter(
        OutreachAttempt.id == attempt_id
    ).first()

    if attempt:
        attempt.clicked_at = datetime.utcnow()

        # Log activity
        activity = ProspectActivity(
            prospect_id=prospect_id,
            type="link_clicked",
            description=f"Clicked link: {url}",
            metadata={"url": url}
        )
        db.add(activity)
        db.commit()

    # Redirect to actual URL
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=url)

@router.post("/track/unsubscribe")
async def handle_unsubscribe(
    email: EmailStr,
    db: Session = Depends(get_db)
):
    """Handle unsubscribe requests."""
    prospect = db.query(Prospect).filter(
        Prospect.email == email
    ).first()

    if prospect:
        prospect.status = "unsubscribed"
        prospect.unsubscribed_at = datetime.utcnow()

        # Log activity
        activity = ProspectActivity(
            prospect_id=prospect.id,
            type="unsubscribed",
            description="Unsubscribed from all communications"
        )
        db.add(activity)
        db.commit()

    return {"message": "Successfully unsubscribed"}

# Analytics Endpoints
@router.get("/analytics/overview")
async def get_analytics_overview(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """Get marketing analytics overview."""
    since = datetime.utcnow() - timedelta(days=days)

    # Prospect metrics
    total_prospects = db.query(Prospect).filter(
        Prospect.organization_id == current_user.organization_id
    ).count()

    new_prospects = db.query(Prospect).filter(
        Prospect.organization_id == current_user.organization_id,
        Prospect.created_at >= since
    ).count()

    # Campaign metrics
    campaigns = db.query(OutreachCampaign).filter(
        OutreachCampaign.organization_id == current_user.organization_id,
        OutreachCampaign.started_at >= since
    ).all()

    total_sent = 0
    total_opened = 0
    total_clicked = 0
    total_replied = 0

    for campaign in campaigns:
        attempts = db.query(OutreachAttempt).filter(
            OutreachAttempt.campaign_id == campaign.id
        ).all()

        total_sent += len(attempts)
        total_opened += sum(1 for a in attempts if a.opened_at)
        total_clicked += sum(1 for a in attempts if a.clicked_at)
        total_replied += sum(1 for a in attempts if a.replied_at)

    # Conversion metrics
    qualified_leads = db.query(Prospect).filter(
        Prospect.organization_id == current_user.organization_id,
        Prospect.status == "qualified",
        Prospect.updated_at >= since
    ).count()

    converted = db.query(Prospect).filter(
        Prospect.organization_id == current_user.organization_id,
        Prospect.status == "converted",
        Prospect.updated_at >= since
    ).count()

    return {
        "prospects": {
            "total": total_prospects,
            "new": new_prospects,
            "qualified": qualified_leads,
            "converted": converted
        },
        "campaigns": {
            "total": len(campaigns),
            "emails_sent": total_sent,
            "opens": total_opened,
            "clicks": total_clicked,
            "replies": total_replied,
            "open_rate": (total_opened / total_sent * 100) if total_sent else 0,
            "click_rate": (total_clicked / total_sent * 100) if total_sent else 0,
            "reply_rate": (total_replied / total_sent * 100) if total_sent else 0
        },
        "conversion": {
            "lead_rate": (qualified_leads / new_prospects * 100) if new_prospects else 0,
            "conversion_rate": (converted / qualified_leads * 100) if qualified_leads else 0
        },
        "period_days": days
    }

@router.get("/analytics/funnel")
async def get_funnel_metrics(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversion funnel metrics."""
    statuses = ["new", "contacted", "engaged", "qualified", "negotiating", "converted"]
    funnel = {}

    for status in statuses:
        count = db.query(Prospect).filter(
            Prospect.organization_id == current_user.organization_id,
            Prospect.status == status
        ).count()
        funnel[status] = count

    return funnel

# Automation Endpoints
@router.post("/automation/identify-prospects")
async def identify_prospects(
    source: str,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Trigger prospect identification from various sources."""
    agent = get_acquisition_agent(db)

    if source == "linkedin":
        background_tasks.add_task(
            agent.prospect_identifier.find_linkedin_prospects,
            current_user.organization_id
        )
    elif source == "website":
        background_tasks.add_task(
            agent.prospect_identifier.identify_website_visitors,
            current_user.organization_id
        )
    elif source == "content":
        background_tasks.add_task(
            agent.prospect_identifier.track_content_engagement,
            current_user.organization_id
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid source")

    return {"message": f"Prospect identification started for {source}"}

@router.post("/automation/score-leads")
async def score_all_leads(
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Recalculate lead scores for all prospects."""
    agent = get_acquisition_agent(db)

    prospects = db.query(Prospect).filter(
        Prospect.organization_id == current_user.organization_id,
        Prospect.status.in_(["contacted", "engaged", "qualified"])
    ).all()

    for prospect in prospects:
        background_tasks.add_task(
            agent.prospect_identifier.enrich_prospect,
            prospect.id
        )

    return {"message": f"Lead scoring initiated for {len(prospects)} prospects"}

# Add required imports for Response
from fastapi.responses import Response