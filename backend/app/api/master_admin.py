"""
Master Admin & Business Portal API
Complete business management system for M&A SaaS platform
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.auth.clerk_auth import ClerkUser, get_current_user, require_admin
from app.auth.tenant_isolation import TenantAwareQuery, get_tenant_query
from app.models.subscription import Subscription, SubscriptionPlan
# PromotionalCode and PaymentMethod models need to be created
from app.models.user import User
from app.models.organization import Organization
from app.models.analytics import BusinessMetrics, RevenueAnalytics, CustomerAnalytics
from app.models.email_campaigns import EmailCampaign, EmailTemplate, LeadScore
from app.models.content import PodcastEpisode, VideoContent, BlogPost, ContentAnalytics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["master-admin"])

# ============================================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE
# ============================================================================

class DashboardMetrics(BaseModel):
    """Executive dashboard metrics"""
    mrr: float = Field(..., description="Monthly Recurring Revenue")
    arr: float = Field(..., description="Annual Recurring Revenue")
    active_subscribers: int = Field(..., description="Total active subscribers")
    churn_rate: float = Field(..., description="Monthly churn rate percentage")
    ltv: float = Field(..., description="Customer Lifetime Value")
    cac: float = Field(..., description="Customer Acquisition Cost")
    trial_conversion_rate: float = Field(..., description="Trial to paid conversion rate")
    revenue_growth: float = Field(..., description="Month-over-month revenue growth")

class SubscriptionMetrics(BaseModel):
    """Subscription analytics"""
    total_subscriptions: int
    active_subscriptions: int
    trial_subscriptions: int
    cancelled_subscriptions: int
    upgrade_rate: float
    downgrade_rate: float
    payment_failures: int
    revenue_by_plan: Dict[str, float]

class ContentMetrics(BaseModel):
    """Content performance metrics"""
    podcast_downloads: int
    video_views: int
    blog_post_views: int
    content_engagement_rate: float
    lead_generation_from_content: int
    top_performing_content: List[Dict[str, Any]]

class LeadGenerationMetrics(BaseModel):
    """Lead generation analytics"""
    total_leads: int
    qualified_leads: int
    conversion_rate: float
    lead_sources: Dict[str, int]
    pipeline_value: float
    average_deal_size: float

class EventMetrics(BaseModel):
    """Event management metrics"""
    upcoming_events: int
    total_attendees: int
    attendance_rate: float
    revenue_from_events: float
    member_engagement_score: float

class BusinessIntelligence(BaseModel):
    """Complete business intelligence dashboard"""
    dashboard_metrics: DashboardMetrics
    subscription_metrics: SubscriptionMetrics
    content_metrics: ContentMetrics
    lead_metrics: LeadGenerationMetrics
    event_metrics: EventMetrics
    last_updated: datetime

class PromotionalCodeCreate(BaseModel):
    """Create promotional code"""
    code: str = Field(..., min_length=3, max_length=50)
    discount_type: str = Field(..., description="percentage or fixed_amount")
    discount_value: float = Field(..., gt=0)
    max_uses: Optional[int] = Field(None, description="Maximum number of uses")
    expiry_date: Optional[datetime] = Field(None)
    applicable_plans: Optional[List[str]] = Field(None)
    description: Optional[str] = Field(None)

class SubscriptionUpdate(BaseModel):
    """Update subscription details"""
    plan_id: Optional[str] = None
    status: Optional[str] = None
    trial_end_date: Optional[datetime] = None
    billing_cycle: Optional[str] = None

class ContentCreationRequest(BaseModel):
    """Content creation request"""
    title: str = Field(..., min_length=1, max_length=200)
    content_type: str = Field(..., description="podcast, video, blog_post")
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    scheduled_publish_date: Optional[datetime] = None

class EmailCampaignCreate(BaseModel):
    """Create email campaign"""
    name: str = Field(..., min_length=1, max_length=100)
    subject: str = Field(..., min_length=1, max_length=200)
    template_id: Optional[str] = None
    recipient_segments: List[str] = Field(..., description="Target audience segments")
    scheduled_send_date: Optional[datetime] = None
    content: str = Field(..., description="Email content/body")

# ============================================================================
# EXECUTIVE DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/dashboard", response_model=BusinessIntelligence)
async def get_executive_dashboard(
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive executive dashboard with all business metrics
    Requires admin privileges
    """
    try:
        # Calculate dashboard metrics
        dashboard_metrics = await _calculate_dashboard_metrics(db)
        subscription_metrics = await _calculate_subscription_metrics(db)
        content_metrics = await _calculate_content_metrics(db)
        lead_metrics = await _calculate_lead_metrics(db)
        event_metrics = await _calculate_event_metrics(db)

        return BusinessIntelligence(
            dashboard_metrics=dashboard_metrics,
            subscription_metrics=subscription_metrics,
            content_metrics=content_metrics,
            lead_metrics=lead_metrics,
            event_metrics=event_metrics,
            last_updated=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Error fetching executive dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard metrics"
        )

@router.get("/metrics/revenue")
async def get_revenue_analytics(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d, 1y"),
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed revenue analytics and trends"""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            raise HTTPException(status_code=400, detail="Invalid period")

        # Query revenue data
        revenue_data = db.query(RevenueAnalytics).filter(
            and_(
                RevenueAnalytics.date >= start_date,
                RevenueAnalytics.date <= end_date
            )
        ).order_by(asc(RevenueAnalytics.date)).all()

        return {
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "revenue_data": revenue_data,
            "total_revenue": sum(r.daily_revenue for r in revenue_data),
            "average_daily_revenue": sum(r.daily_revenue for r in revenue_data) / len(revenue_data) if revenue_data else 0
        }

    except Exception as e:
        logger.error(f"Error fetching revenue analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch revenue analytics"
        )

# ============================================================================
# SUBSCRIPTION MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/subscriptions")
async def get_all_subscriptions(
    status: Optional[str] = Query(None, description="Filter by subscription status"),
    plan: Optional[str] = Query(None, description="Filter by subscription plan"),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all subscriptions with filtering and pagination"""
    try:
        query = db.query(Subscription).join(User).join(Organization)

        # Apply filters
        if status:
            query = query.filter(Subscription.status == status)
        if plan:
            query = query.filter(Subscription.plan_id == plan)

        # Get total count
        total_count = query.count()

        # Apply pagination
        subscriptions = query.offset(offset).limit(limit).all()

        return {
            "subscriptions": subscriptions,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error fetching subscriptions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscriptions"
        )

@router.put("/subscriptions/{subscription_id}")
async def update_subscription(
    subscription_id: str,
    subscription_update: SubscriptionUpdate,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update subscription details (admin only)"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )

        # Update fields
        if subscription_update.plan_id:
            subscription.plan_id = subscription_update.plan_id
        if subscription_update.status:
            subscription.status = subscription_update.status
        if subscription_update.trial_end_date:
            subscription.trial_end_date = subscription_update.trial_end_date
        if subscription_update.billing_cycle:
            subscription.billing_cycle = subscription_update.billing_cycle

        subscription.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(subscription)

        return subscription

    except Exception as e:
        logger.error(f"Error updating subscription: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription"
        )

@router.post("/promotional-codes")
async def create_promotional_code(
    promo_code: PromotionalCodeCreate,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new promotional code"""
    # TODO: PromotionalCode model needs to be created
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Promotional codes feature coming soon - model needs to be created"
    )

@router.get("/promotional-codes")
async def get_promotional_codes(
    active_only: bool = Query(False, description="Show only active codes"),
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all promotional codes"""
    # TODO: PromotionalCode model needs to be created
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Promotional codes feature coming soon - model needs to be created"
    )

# ============================================================================
# CONTENT CREATION & MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/content")
async def create_content(
    content_request: ContentCreationRequest,
    background_tasks: BackgroundTasks,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new content (podcast, video, blog post)"""
    try:
        if content_request.content_type == "podcast":
            content = PodcastEpisode(
                title=content_request.title,
                description=content_request.description,
                tags=content_request.tags,
                scheduled_publish_date=content_request.scheduled_publish_date,
                created_by=current_user.user_id,
                created_at=datetime.utcnow(),
                status="draft"
            )
        elif content_request.content_type == "video":
            content = VideoContent(
                title=content_request.title,
                description=content_request.description,
                tags=content_request.tags,
                scheduled_publish_date=content_request.scheduled_publish_date,
                created_by=current_user.user_id,
                created_at=datetime.utcnow(),
                status="draft"
            )
        elif content_request.content_type == "blog_post":
            content = BlogPost(
                title=content_request.title,
                description=content_request.description,
                tags=content_request.tags,
                scheduled_publish_date=content_request.scheduled_publish_date,
                created_by=current_user.user_id,
                created_at=datetime.utcnow(),
                status="draft"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content type"
            )

        db.add(content)
        db.commit()
        db.refresh(content)

        # Schedule background tasks for content processing
        if content_request.scheduled_publish_date:
            background_tasks.add_task(
                _schedule_content_publication,
                content.id,
                content_request.scheduled_publish_date
            )

        return content

    except Exception as e:
        logger.error(f"Error creating content: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content"
        )

@router.get("/content/analytics")
async def get_content_analytics(
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get content performance analytics"""
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
            raise HTTPException(status_code=400, detail="Invalid period")

        # Query content analytics
        query = db.query(ContentAnalytics).filter(
            and_(
                ContentAnalytics.date >= start_date,
                ContentAnalytics.date <= end_date
            )
        )

        if content_type:
            query = query.filter(ContentAnalytics.content_type == content_type)

        analytics = query.order_by(desc(ContentAnalytics.date)).all()

        return {
            "period": period,
            "content_type": content_type,
            "analytics": analytics,
            "total_views": sum(a.views for a in analytics),
            "total_engagement": sum(a.engagement_count for a in analytics),
            "average_engagement_rate": sum(a.engagement_rate for a in analytics) / len(analytics) if analytics else 0
        }

    except Exception as e:
        logger.error(f"Error fetching content analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch content analytics"
        )

# ============================================================================
# LEAD GENERATION & MARKETING ENDPOINTS
# ============================================================================

@router.post("/email-campaigns")
async def create_email_campaign(
    campaign: EmailCampaignCreate,
    background_tasks: BackgroundTasks,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create and schedule email campaign"""
    try:
        new_campaign = EmailCampaign(
            name=campaign.name,
            subject=campaign.subject,
            template_id=campaign.template_id,
            recipient_segments=campaign.recipient_segments,
            scheduled_send_date=campaign.scheduled_send_date,
            content=campaign.content,
            created_by=current_user.user_id,
            created_at=datetime.utcnow(),
            status="draft"
        )

        db.add(new_campaign)
        db.commit()
        db.refresh(new_campaign)

        # Schedule email sending if date is specified
        if campaign.scheduled_send_date:
            background_tasks.add_task(
                _schedule_email_campaign,
                new_campaign.id,
                campaign.scheduled_send_date
            )

        return new_campaign

    except Exception as e:
        logger.error(f"Error creating email campaign: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create email campaign"
        )

@router.get("/leads")
async def get_leads(
    status: Optional[str] = Query(None, description="Filter by lead status"),
    source: Optional[str] = Query(None, description="Filter by lead source"),
    score_min: Optional[int] = Query(None, description="Minimum lead score"),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get leads with filtering and scoring"""
    try:
        query = db.query(LeadScore).join(User)

        # Apply filters
        if status:
            query = query.filter(LeadScore.status == status)
        if source:
            query = query.filter(LeadScore.source == source)
        if score_min:
            query = query.filter(LeadScore.score >= score_min)

        # Get total count
        total_count = query.count()

        # Apply pagination and ordering
        leads = query.order_by(desc(LeadScore.score)).offset(offset).limit(limit).all()

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

# ============================================================================
# BUSINESS ANALYTICS HELPER FUNCTIONS
# ============================================================================

async def _calculate_dashboard_metrics(db: Session) -> DashboardMetrics:
    """Calculate executive dashboard metrics"""
    # Get current month data
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    previous_month = (current_month - timedelta(days=1)).replace(day=1)

    # Calculate MRR and ARR
    active_subscriptions = db.query(Subscription).filter(
        Subscription.status == "active"
    ).all()

    mrr = sum(sub.monthly_amount for sub in active_subscriptions)
    arr = mrr * 12

    # Calculate churn rate
    total_subs_start = db.query(Subscription).filter(
        Subscription.created_at < current_month
    ).count()

    churned_subs = db.query(Subscription).filter(
        and_(
            Subscription.cancelled_at >= current_month,
            Subscription.cancelled_at < datetime.utcnow()
        )
    ).count()

    churn_rate = (churned_subs / total_subs_start * 100) if total_subs_start > 0 else 0

    # Calculate LTV and CAC (simplified)
    avg_monthly_revenue = mrr / len(active_subscriptions) if active_subscriptions else 0
    avg_customer_lifespan = 24  # months (assumption)
    ltv = avg_monthly_revenue * avg_customer_lifespan

    # CAC calculation would need marketing spend data
    cac = 150.0  # placeholder

    # Trial conversion rate
    trial_subs = db.query(Subscription).filter(
        Subscription.status == "trial"
    ).count()

    converted_trials = db.query(Subscription).filter(
        and_(
            Subscription.status == "active",
            Subscription.trial_end_date.isnot(None)
        )
    ).count()

    trial_conversion_rate = (converted_trials / (trial_subs + converted_trials) * 100) if (trial_subs + converted_trials) > 0 else 0

    # Revenue growth
    previous_month_revenue = db.query(func.sum(RevenueAnalytics.daily_revenue)).filter(
        and_(
            RevenueAnalytics.date >= previous_month,
            RevenueAnalytics.date < current_month
        )
    ).scalar() or 0

    current_month_revenue = db.query(func.sum(RevenueAnalytics.daily_revenue)).filter(
        RevenueAnalytics.date >= current_month
    ).scalar() or 0

    revenue_growth = ((current_month_revenue - previous_month_revenue) / previous_month_revenue * 100) if previous_month_revenue > 0 else 0

    return DashboardMetrics(
        mrr=mrr,
        arr=arr,
        active_subscribers=len(active_subscriptions),
        churn_rate=churn_rate,
        ltv=ltv,
        cac=cac,
        trial_conversion_rate=trial_conversion_rate,
        revenue_growth=revenue_growth
    )

async def _calculate_subscription_metrics(db: Session) -> SubscriptionMetrics:
    """Calculate subscription-specific metrics"""
    total_subs = db.query(Subscription).count()
    active_subs = db.query(Subscription).filter(Subscription.status == "active").count()
    trial_subs = db.query(Subscription).filter(Subscription.status == "trial").count()
    cancelled_subs = db.query(Subscription).filter(Subscription.status == "cancelled").count()

    # Revenue by plan
    revenue_by_plan = {}
    plans = db.query(SubscriptionPlan).all()
    for plan in plans:
        plan_revenue = db.query(func.sum(Subscription.monthly_amount)).filter(
            and_(
                Subscription.plan_id == plan.id,
                Subscription.status == "active"
            )
        ).scalar() or 0
        revenue_by_plan[plan.name] = float(plan_revenue)

    return SubscriptionMetrics(
        total_subscriptions=total_subs,
        active_subscriptions=active_subs,
        trial_subscriptions=trial_subs,
        cancelled_subscriptions=cancelled_subs,
        upgrade_rate=5.2,  # placeholder
        downgrade_rate=2.1,  # placeholder
        payment_failures=3,  # placeholder
        revenue_by_plan=revenue_by_plan
    )

async def _calculate_content_metrics(db: Session) -> ContentMetrics:
    """Calculate content performance metrics"""
    # These would be calculated from actual content analytics
    return ContentMetrics(
        podcast_downloads=15420,
        video_views=8750,
        blog_post_views=12300,
        content_engagement_rate=7.8,
        lead_generation_from_content=245,
        top_performing_content=[
            {"title": "M&A Valuation Masterclass", "type": "video", "views": 2100},
            {"title": "Due Diligence Checklist", "type": "blog", "views": 1850},
            {"title": "Private Equity Trends 2025", "type": "podcast", "downloads": 3200}
        ]
    )

async def _calculate_lead_metrics(db: Session) -> LeadGenerationMetrics:
    """Calculate lead generation metrics"""
    total_leads = db.query(LeadScore).count()
    qualified_leads = db.query(LeadScore).filter(LeadScore.score >= 70).count()
    conversion_rate = (qualified_leads / total_leads * 100) if total_leads > 0 else 0

    return LeadGenerationMetrics(
        total_leads=total_leads,
        qualified_leads=qualified_leads,
        conversion_rate=conversion_rate,
        lead_sources={"website": 45, "podcast": 23, "linkedin": 18, "referral": 14},
        pipeline_value=125000.0,
        average_deal_size=2500.0
    )

async def _calculate_event_metrics(db: Session) -> EventMetrics:
    """Calculate event management metrics"""
    # These would be calculated from actual event data
    return EventMetrics(
        upcoming_events=4,
        total_attendees=156,
        attendance_rate=78.5,
        revenue_from_events=12500.0,
        member_engagement_score=8.2
    )

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def _schedule_content_publication(content_id: str, publish_date: datetime):
    """Background task to schedule content publication"""
    # This would integrate with content management system
    logger.info(f"Scheduling content {content_id} for publication at {publish_date}")

async def _schedule_email_campaign(campaign_id: str, send_date: datetime):
    """Background task to schedule email campaign"""
    # This would integrate with email service provider
    logger.info(f"Scheduling email campaign {campaign_id} for sending at {send_date}")
