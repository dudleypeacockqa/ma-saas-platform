"""
Content Creation API
Professional podcast and video production endpoints for Master Admin Portal
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging
import json

from app.core.database import get_db
from app.auth.clerk_auth import ClerkUser, get_current_user, require_admin
from app.models.content_creation import (
    ContentSeries, ContentEpisode, RecordingSession, AIContentProcessing,
    ContentDistribution, ContentAnalytics, ContentTemplate, ContentCollaboration,
    ContentMonetization, ContentType, ContentStatus, ProductionStage,
    DistributionPlatform, RecordingQuality
)
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/content", tags=["content-creation"])

# ============================================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE
# ============================================================================

class ContentSeriesCreate(BaseModel):
    """Create content series"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    content_type: ContentType
    publishing_schedule: Optional[str] = None
    target_duration: Optional[int] = Field(None, description="Target duration in minutes")
    target_audience: Optional[str] = None
    category: Optional[str] = None
    seo_keywords: Optional[List[str]] = None

class ContentEpisodeCreate(BaseModel):
    """Create content episode"""
    series_id: str
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    episode_number: Optional[int] = None
    season_number: int = Field(1, ge=1)
    content_type: ContentType
    scheduled_publish_date: Optional[datetime] = None
    guests: Optional[List[Dict[str, Any]]] = None
    keywords: Optional[List[str]] = None
    tags: Optional[List[str]] = None

class RecordingSessionCreate(BaseModel):
    """Create recording session"""
    episode_id: str
    session_name: str = Field(..., min_length=1, max_length=200)
    scheduled_start: datetime
    recording_quality: RecordingQuality = RecordingQuality.FULL_HD_1080P
    participants: Optional[List[Dict[str, Any]]] = None
    max_participants: int = Field(10, ge=1, le=50)
    auto_recording: bool = True
    cloud_recording: bool = True
    live_streaming: bool = False
    stream_platforms: Optional[List[str]] = None

class ContentDistributionCreate(BaseModel):
    """Create content distribution"""
    episode_id: str
    platform: DistributionPlatform
    auto_publish: bool = True
    scheduled_publish_date: Optional[datetime] = None
    platform_title: Optional[str] = None
    platform_description: Optional[str] = None
    platform_tags: Optional[List[str]] = None

class ContentTemplateCreate(BaseModel):
    """Create content template"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    content_type: ContentType
    category: Optional[str] = None
    template_structure: Optional[Dict[str, Any]] = None
    default_duration: Optional[int] = None
    intro_template: Optional[str] = None
    outro_template: Optional[str] = None
    call_to_action_template: Optional[str] = None
    is_public: bool = False

# ============================================================================
# CONTENT SERIES ENDPOINTS
# ============================================================================

@router.post("/series", response_model=Dict[str, Any])
async def create_content_series(
    series_data: ContentSeriesCreate,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new content series"""
    try:
        series = ContentSeries(
            name=series_data.name,
            description=series_data.description,
            content_type=series_data.content_type,
            publishing_schedule=series_data.publishing_schedule,
            target_duration=series_data.target_duration,
            target_audience=series_data.target_audience,
            category=series_data.category,
            seo_keywords=series_data.seo_keywords,
            created_by=current_user.user_id
        )
        
        db.add(series)
        db.commit()
        db.refresh(series)
        
        return {
            "series": series,
            "message": "Content series created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating content series: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content series"
        )

@router.get("/series")
async def get_content_series(
    content_type: Optional[ContentType] = None,
    is_active: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get content series with filtering"""
    try:
        query = db.query(ContentSeries)
        
        if content_type:
            query = query.filter(ContentSeries.content_type == content_type)
        if is_active is not None:
            query = query.filter(ContentSeries.is_active == is_active)
        
        total_count = query.count()
        series = query.order_by(desc(ContentSeries.created_at)).offset(offset).limit(limit).all()
        
        return {
            "series": series,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching content series: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch content series"
        )

@router.get("/series/{series_id}")
async def get_content_series_details(
    series_id: str,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed content series information"""
    try:
        series = db.query(ContentSeries).filter(ContentSeries.id == series_id).first()
        
        if not series:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content series not found"
            )
        
        # Get recent episodes
        recent_episodes = db.query(ContentEpisode).filter(
            ContentEpisode.series_id == series_id
        ).order_by(desc(ContentEpisode.created_at)).limit(10).all()
        
        # Get analytics summary
        analytics_summary = db.query(
            func.sum(ContentEpisode.view_count).label("total_views"),
            func.sum(ContentEpisode.download_count).label("total_downloads"),
            func.avg(ContentEpisode.engagement_score).label("avg_engagement")
        ).filter(ContentEpisode.series_id == series_id).first()
        
        return {
            "series": series,
            "recent_episodes": recent_episodes,
            "analytics": {
                "total_views": analytics_summary.total_views or 0,
                "total_downloads": analytics_summary.total_downloads or 0,
                "average_engagement": float(analytics_summary.avg_engagement or 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching series details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch series details"
        )

# ============================================================================
# CONTENT EPISODE ENDPOINTS
# ============================================================================

@router.post("/episodes", response_model=Dict[str, Any])
async def create_content_episode(
    episode_data: ContentEpisodeCreate,
    background_tasks: BackgroundTasks,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new content episode"""
    try:
        # Verify series exists
        series = db.query(ContentSeries).filter(ContentSeries.id == episode_data.series_id).first()
        if not series:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content series not found"
            )
        
        # Auto-generate episode number if not provided
        if not episode_data.episode_number:
            last_episode = db.query(ContentEpisode).filter(
                ContentEpisode.series_id == episode_data.series_id,
                ContentEpisode.season_number == episode_data.season_number
            ).order_by(desc(ContentEpisode.episode_number)).first()
            
            episode_data.episode_number = (last_episode.episode_number + 1) if last_episode else 1
        
        episode = ContentEpisode(
            series_id=episode_data.series_id,
            title=episode_data.title,
            description=episode_data.description,
            episode_number=episode_data.episode_number,
            season_number=episode_data.season_number,
            content_type=episode_data.content_type,
            scheduled_publish_date=episode_data.scheduled_publish_date,
            guests=episode_data.guests,
            keywords=episode_data.keywords,
            tags=episode_data.tags,
            created_by=current_user.user_id
        )
        
        db.add(episode)
        db.commit()
        db.refresh(episode)
        
        # Update series episode count
        series.total_episodes += 1
        db.commit()
        
        # Schedule AI content processing
        background_tasks.add_task(_schedule_ai_processing, episode.id)
        
        return {
            "episode": episode,
            "message": "Content episode created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating content episode: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content episode"
        )

@router.get("/episodes")
async def get_content_episodes(
    series_id: Optional[str] = None,
    status: Optional[ContentStatus] = None,
    content_type: Optional[ContentType] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get content episodes with filtering"""
    try:
        query = db.query(ContentEpisode)
        
        if series_id:
            query = query.filter(ContentEpisode.series_id == series_id)
        if status:
            query = query.filter(ContentEpisode.status == status)
        if content_type:
            query = query.filter(ContentEpisode.content_type == content_type)
        
        total_count = query.count()
        episodes = query.order_by(desc(ContentEpisode.created_at)).offset(offset).limit(limit).all()
        
        return {
            "episodes": episodes,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching content episodes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch content episodes"
        )

@router.put("/episodes/{episode_id}/status")
async def update_episode_status(
    episode_id: str,
    new_status: ContentStatus,
    production_stage: Optional[ProductionStage] = None,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update episode status and production stage"""
    try:
        episode = db.query(ContentEpisode).filter(ContentEpisode.id == episode_id).first()
        
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Episode not found"
            )
        
        episode.status = new_status
        if production_stage:
            episode.production_stage = production_stage
        
        # Set published date when status changes to published
        if new_status == ContentStatus.PUBLISHED and not episode.published_date:
            episode.published_date = datetime.utcnow()
        
        db.commit()
        db.refresh(episode)
        
        return {
            "episode": episode,
            "message": "Episode status updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating episode status: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update episode status"
        )

# ============================================================================
# RECORDING SESSION ENDPOINTS
# ============================================================================

@router.post("/recording-sessions", response_model=Dict[str, Any])
async def create_recording_session(
    session_data: RecordingSessionCreate,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new recording session"""
    try:
        # Verify episode exists
        episode = db.query(ContentEpisode).filter(ContentEpisode.id == session_data.episode_id).first()
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Episode not found"
            )
        
        session = RecordingSession(
            episode_id=session_data.episode_id,
            session_name=session_data.session_name,
            scheduled_start=session_data.scheduled_start,
            recording_quality=session_data.recording_quality,
            participants=session_data.participants,
            max_participants=session_data.max_participants,
            auto_recording=session_data.auto_recording,
            cloud_recording=session_data.cloud_recording,
            live_streaming=session_data.live_streaming,
            stream_platforms=session_data.stream_platforms,
            host_id=current_user.user_id
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {
            "session": session,
            "message": "Recording session created successfully",
            "join_url": f"/recording/join/{session.id}",  # Frontend would handle this
            "stream_settings": {
                "quality": session_data.recording_quality.value,
                "live_streaming": session_data.live_streaming,
                "platforms": session_data.stream_platforms
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating recording session: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create recording session"
        )

@router.get("/recording-sessions")
async def get_recording_sessions(
    episode_id: Optional[str] = None,
    status: Optional[str] = None,
    upcoming_only: bool = False,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recording sessions"""
    try:
        query = db.query(RecordingSession)
        
        if episode_id:
            query = query.filter(RecordingSession.episode_id == episode_id)
        if status:
            query = query.filter(RecordingSession.status == status)
        if upcoming_only:
            query = query.filter(RecordingSession.scheduled_start > datetime.utcnow())
        
        sessions = query.order_by(asc(RecordingSession.scheduled_start)).all()
        
        return {
            "sessions": sessions,
            "count": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Error fetching recording sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recording sessions"
        )

@router.post("/recording-sessions/{session_id}/start")
async def start_recording_session(
    session_id: str,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start recording session"""
    try:
        session = db.query(RecordingSession).filter(RecordingSession.id == session_id).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recording session not found"
            )
        
        # Update session status
        session.status = "in_progress"
        session.actual_start = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": "Recording session started",
            "session_id": session_id,
            "start_time": session.actual_start,
            "recording_settings": {
                "quality": session.recording_quality.value,
                "auto_recording": session.auto_recording,
                "cloud_recording": session.cloud_recording
            }
        }
        
    except Exception as e:
        logger.error(f"Error starting recording session: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start recording session"
        )

# ============================================================================
# CONTENT DISTRIBUTION ENDPOINTS
# ============================================================================

@router.post("/distributions", response_model=Dict[str, Any])
async def create_content_distribution(
    distribution_data: ContentDistributionCreate,
    background_tasks: BackgroundTasks,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create content distribution to platform"""
    try:
        # Verify episode exists
        episode = db.query(ContentEpisode).filter(ContentEpisode.id == distribution_data.episode_id).first()
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Episode not found"
            )
        
        distribution = ContentDistribution(
            episode_id=distribution_data.episode_id,
            platform=distribution_data.platform,
            auto_publish=distribution_data.auto_publish,
            scheduled_publish_date=distribution_data.scheduled_publish_date,
            platform_title=distribution_data.platform_title or episode.title,
            platform_description=distribution_data.platform_description or episode.description,
            platform_tags=distribution_data.platform_tags or episode.tags
        )
        
        db.add(distribution)
        db.commit()
        db.refresh(distribution)
        
        # Schedule distribution if auto-publish is enabled
        if distribution_data.auto_publish:
            background_tasks.add_task(_schedule_content_distribution, distribution.id)
        
        return {
            "distribution": distribution,
            "message": "Content distribution created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating content distribution: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content distribution"
        )

@router.get("/distributions")
async def get_content_distributions(
    episode_id: Optional[str] = None,
    platform: Optional[DistributionPlatform] = None,
    status: Optional[str] = None,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get content distributions"""
    try:
        query = db.query(ContentDistribution)
        
        if episode_id:
            query = query.filter(ContentDistribution.episode_id == episode_id)
        if platform:
            query = query.filter(ContentDistribution.platform == platform)
        if status:
            query = query.filter(ContentDistribution.status == status)
        
        distributions = query.order_by(desc(ContentDistribution.created_at)).all()
        
        return {
            "distributions": distributions,
            "count": len(distributions)
        }
        
    except Exception as e:
        logger.error(f"Error fetching content distributions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch content distributions"
        )

# ============================================================================
# CONTENT ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics/overview")
async def get_content_analytics_overview(
    period: str = "30d",
    content_type: Optional[ContentType] = None,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get content analytics overview"""
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
        
        # Base query
        query = db.query(ContentAnalytics).filter(
            ContentAnalytics.analytics_date >= start_date
        )
        
        if content_type:
            query = query.join(ContentEpisode).filter(
                ContentEpisode.content_type == content_type
            )
        
        analytics = query.all()
        
        # Calculate totals
        total_views = sum(a.daily_views for a in analytics)
        total_downloads = sum(a.daily_downloads for a in analytics)
        total_leads = sum(a.leads_generated for a in analytics)
        total_revenue = sum(a.attributed_revenue for a in analytics)
        
        # Calculate averages
        avg_watch_time = sum(a.average_watch_time for a in analytics) / len(analytics) if analytics else 0
        avg_completion_rate = sum(a.completion_rate for a in analytics) / len(analytics) if analytics else 0
        avg_engagement_rate = (
            sum(a.like_rate + a.comment_rate + a.share_rate for a in analytics) / len(analytics)
        ) if analytics else 0
        
        return {
            "period": period,
            "overview": {
                "total_views": total_views,
                "total_downloads": total_downloads,
                "total_leads_generated": total_leads,
                "total_attributed_revenue": total_revenue,
                "average_watch_time_seconds": int(avg_watch_time),
                "average_completion_rate": round(avg_completion_rate, 2),
                "average_engagement_rate": round(avg_engagement_rate, 2)
            },
            "daily_breakdown": [
                {
                    "date": a.analytics_date.isoformat(),
                    "views": a.daily_views,
                    "downloads": a.daily_downloads,
                    "leads": a.leads_generated,
                    "revenue": a.attributed_revenue
                }
                for a in analytics
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching content analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch content analytics"
        )

# ============================================================================
# CONTENT TEMPLATES ENDPOINTS
# ============================================================================

@router.post("/templates", response_model=Dict[str, Any])
async def create_content_template(
    template_data: ContentTemplateCreate,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create content template"""
    try:
        template = ContentTemplate(
            name=template_data.name,
            description=template_data.description,
            content_type=template_data.content_type,
            category=template_data.category,
            template_structure=template_data.template_structure,
            default_duration=template_data.default_duration,
            intro_template=template_data.intro_template,
            outro_template=template_data.outro_template,
            call_to_action_template=template_data.call_to_action_template,
            is_public=template_data.is_public,
            created_by=current_user.user_id
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return {
            "template": template,
            "message": "Content template created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating content template: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content template"
        )

@router.get("/templates")
async def get_content_templates(
    content_type: Optional[ContentType] = None,
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get content templates"""
    try:
        query = db.query(ContentTemplate)
        
        if content_type:
            query = query.filter(ContentTemplate.content_type == content_type)
        if category:
            query = query.filter(ContentTemplate.category == category)
        if is_public is not None:
            query = query.filter(ContentTemplate.is_public == is_public)
        
        # Show user's own templates plus public templates
        query = query.filter(
            or_(
                ContentTemplate.created_by == current_user.user_id,
                ContentTemplate.is_public == True
            )
        )
        
        templates = query.order_by(desc(ContentTemplate.usage_count)).all()
        
        return {
            "templates": templates,
            "count": len(templates)
        }
        
    except Exception as e:
        logger.error(f"Error fetching content templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch content templates"
        )

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def _schedule_ai_processing(episode_id: str):
    """Schedule AI processing for content episode"""
    logger.info(f"Scheduling AI processing for episode {episode_id}")
    # This would integrate with AI services for transcription, content generation, etc.

async def _schedule_content_distribution(distribution_id: str):
    """Schedule content distribution to platform"""
    logger.info(f"Scheduling content distribution {distribution_id}")
    # This would integrate with platform APIs for publishing
