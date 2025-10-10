"""
Podcast API endpoints
Handles podcast management, episode publishing, and RSS feed generation
"""

import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.core.database import get_db
from app.models.podcast import Podcast, PodcastEpisode, PodcastDownload, EpisodeStatus
from app.models.organization import Organization
from app.core.auth import get_current_user, get_current_organization
from app.core.config import settings
from pydantic import BaseModel, Field
import uuid
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/podcast", tags=["podcast"])

# Pydantic models for API
class PodcastCreate(BaseModel):
    title: str = Field(..., max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    description: str
    summary: Optional[str] = None
    author: str = Field(..., max_length=255)
    owner_name: str = Field(..., max_length=255)
    owner_email: str = Field(..., max_length=255)
    category: str = Field(..., max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    keywords: Optional[List[str]] = None
    website_url: Optional[str] = Field(None, max_length=500)
    language: str = Field(default="en-US", max_length=10)
    copyright_text: Optional[str] = Field(None, max_length=255)
    is_explicit: bool = False


class PodcastUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = Field(None, max_length=255)
    owner_name: Optional[str] = Field(None, max_length=255)
    owner_email: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    keywords: Optional[List[str]] = None
    website_url: Optional[str] = Field(None, max_length=500)
    language: Optional[str] = Field(None, max_length=10)
    copyright_text: Optional[str] = Field(None, max_length=255)
    is_explicit: Optional[bool] = None
    is_published: Optional[bool] = None


class EpisodeCreate(BaseModel):
    title: str = Field(..., max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    description: str
    summary: Optional[str] = None
    show_notes: Optional[str] = None
    transcript: Optional[str] = None
    author: Optional[str] = Field(None, max_length=255)
    guests: Optional[List[Dict[str, str]]] = None
    episode_number: int = Field(..., gt=0)
    season_number: Optional[int] = Field(None, gt=0)
    keywords: Optional[List[str]] = None
    is_explicit: bool = False
    episode_url: Optional[str] = Field(None, max_length=500)
    scheduled_at: Optional[datetime] = None


class EpisodeUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    summary: Optional[str] = None
    show_notes: Optional[str] = None
    transcript: Optional[str] = None
    author: Optional[str] = Field(None, max_length=255)
    guests: Optional[List[Dict[str, str]]] = None
    episode_number: Optional[int] = Field(None, gt=0)
    season_number: Optional[int] = Field(None, gt=0)
    keywords: Optional[List[str]] = None
    is_explicit: Optional[bool] = None
    episode_url: Optional[str] = Field(None, max_length=500)
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None


class PodcastResponse(BaseModel):
    id: str
    title: str
    subtitle: Optional[str]
    description: str
    author: str
    category: str
    is_published: bool
    total_episodes: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EpisodeResponse(BaseModel):
    id: str
    title: str
    subtitle: Optional[str]
    description: str
    episode_number: int
    season_number: Optional[int]
    status: str
    duration_formatted: str
    published_at: Optional[datetime]
    download_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# Podcast management endpoints
@router.post("/", response_model=PodcastResponse)
async def create_podcast(
    podcast_data: PodcastCreate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Create a new podcast"""
    
    # Check if organization already has a podcast
    existing_podcast = db.query(Podcast).filter(
        and_(
            Podcast.organization_id == current_org.id,
            Podcast.is_deleted == False
        )
    ).first()
    
    if existing_podcast:
        raise HTTPException(
            status_code=400,
            detail="Organization already has a podcast. Only one podcast per organization is allowed."
        )
    
    # Create podcast
    podcast = Podcast(
        organization_id=current_org.id,
        **podcast_data.dict()
    )
    
    # Generate feed GUID
    podcast.feed_guid = f"podcast-{podcast.id}"
    
    db.add(podcast)
    db.commit()
    db.refresh(podcast)
    
    logger.info(f"Created podcast {podcast.id} for organization {current_org.id}")
    return podcast


@router.get("/", response_model=Optional[PodcastResponse])
async def get_organization_podcast(
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get the organization's podcast"""
    
    podcast = db.query(Podcast).filter(
        and_(
            Podcast.organization_id == current_org.id,
            Podcast.is_deleted == False
        )
    ).first()
    
    return podcast


@router.get("/{podcast_id}", response_model=PodcastResponse)
async def get_podcast(
    podcast_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get a specific podcast"""
    
    podcast = db.query(Podcast).filter(
        and_(
            Podcast.id == podcast_id,
            Podcast.organization_id == current_org.id,
            Podcast.is_deleted == False
        )
    ).first()
    
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    
    return podcast


@router.put("/{podcast_id}", response_model=PodcastResponse)
async def update_podcast(
    podcast_id: str,
    podcast_data: PodcastUpdate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Update a podcast"""
    
    podcast = db.query(Podcast).filter(
        and_(
            Podcast.id == podcast_id,
            Podcast.organization_id == current_org.id,
            Podcast.is_deleted == False
        )
    ).first()
    
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    
    # Update fields
    update_data = podcast_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(podcast, field, value)
    
    # Update last build date if published
    if podcast.is_published:
        podcast.last_build_date = datetime.utcnow()
    
    db.commit()
    db.refresh(podcast)
    
    logger.info(f"Updated podcast {podcast_id}")
    return podcast


@router.delete("/{podcast_id}")
async def delete_podcast(
    podcast_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Delete a podcast (soft delete)"""
    
    podcast = db.query(Podcast).filter(
        and_(
            Podcast.id == podcast_id,
            Podcast.organization_id == current_org.id,
            Podcast.is_deleted == False
        )
    ).first()
    
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    
    podcast.soft_delete()
    db.commit()
    
    logger.info(f"Deleted podcast {podcast_id}")
    return {"message": "Podcast deleted successfully"}


# Episode management endpoints
@router.post("/{podcast_id}/episodes", response_model=EpisodeResponse)
async def create_episode(
    podcast_id: str,
    episode_data: EpisodeCreate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Create a new podcast episode"""
    
    # Verify podcast exists and belongs to organization
    podcast = db.query(Podcast).filter(
        and_(
            Podcast.id == podcast_id,
            Podcast.organization_id == current_org.id,
            Podcast.is_deleted == False
        )
    ).first()
    
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    
    # Check if episode number already exists
    existing_episode = db.query(PodcastEpisode).filter(
        and_(
            PodcastEpisode.podcast_id == podcast_id,
            PodcastEpisode.episode_number == episode_data.episode_number,
            PodcastEpisode.is_deleted == False
        )
    ).first()
    
    if existing_episode:
        raise HTTPException(
            status_code=400,
            detail=f"Episode number {episode_data.episode_number} already exists"
        )
    
    # Create episode
    episode = PodcastEpisode(
        podcast_id=podcast_id,
        **episode_data.dict()
    )
    
    # Generate GUID
    episode.guid = f"episode-{episode.id}"
    
    # Set status based on scheduled_at
    if episode_data.scheduled_at:
        episode.schedule(episode_data.scheduled_at)
    
    db.add(episode)
    
    # Update podcast episode count
    podcast.total_episodes = db.query(PodcastEpisode).filter(
        and_(
            PodcastEpisode.podcast_id == podcast_id,
            PodcastEpisode.is_deleted == False
        )
    ).count() + 1
    
    db.commit()
    db.refresh(episode)
    
    logger.info(f"Created episode {episode.id} for podcast {podcast_id}")
    return episode


@router.get("/{podcast_id}/episodes", response_model=List[EpisodeResponse])
async def get_episodes(
    podcast_id: str,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get podcast episodes"""
    
    # Verify podcast exists and belongs to organization
    podcast = db.query(Podcast).filter(
        and_(
            Podcast.id == podcast_id,
            Podcast.organization_id == current_org.id,
            Podcast.is_deleted == False
        )
    ).first()
    
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    
    # Build query
    query = db.query(PodcastEpisode).filter(
        and_(
            PodcastEpisode.podcast_id == podcast_id,
            PodcastEpisode.is_deleted == False
        )
    )
    
    if status:
        query = query.filter(PodcastEpisode.status == status)
    
    episodes = query.order_by(desc(PodcastEpisode.episode_number)).offset(offset).limit(limit).all()
    
    return episodes


@router.get("/{podcast_id}/episodes/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    podcast_id: str,
    episode_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Get a specific episode"""
    
    episode = db.query(PodcastEpisode).join(Podcast).filter(
        and_(
            PodcastEpisode.id == episode_id,
            PodcastEpisode.podcast_id == podcast_id,
            Podcast.organization_id == current_org.id,
            PodcastEpisode.is_deleted == False,
            Podcast.is_deleted == False
        )
    ).first()
    
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    return episode


@router.put("/{podcast_id}/episodes/{episode_id}", response_model=EpisodeResponse)
async def update_episode(
    podcast_id: str,
    episode_id: str,
    episode_data: EpisodeUpdate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Update an episode"""
    
    episode = db.query(PodcastEpisode).join(Podcast).filter(
        and_(
            PodcastEpisode.id == episode_id,
            PodcastEpisode.podcast_id == podcast_id,
            Podcast.organization_id == current_org.id,
            PodcastEpisode.is_deleted == False,
            Podcast.is_deleted == False
        )
    ).first()
    
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    # Update fields
    update_data = episode_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value == "published":
            episode.publish()
        elif field == "scheduled_at" and value:
            episode.schedule(value)
        else:
            setattr(episode, field, value)
    
    db.commit()
    db.refresh(episode)
    
    logger.info(f"Updated episode {episode_id}")
    return episode


@router.post("/{podcast_id}/episodes/{episode_id}/upload-audio")
async def upload_episode_audio(
    podcast_id: str,
    episode_id: str,
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """Upload audio file for an episode"""
    
    episode = db.query(PodcastEpisode).join(Podcast).filter(
        and_(
            PodcastEpisode.id == episode_id,
            PodcastEpisode.podcast_id == podcast_id,
            Podcast.organization_id == current_org.id,
            PodcastEpisode.is_deleted == False,
            Podcast.is_deleted == False
        )
    ).first()
    
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    # Validate file type
    allowed_types = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/m4a"]
    if audio_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Create upload directory
    upload_dir = Path(settings.MEDIA_ROOT) / "podcast" / str(current_org.id) / str(podcast_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    file_extension = Path(audio_file.filename).suffix
    filename = f"episode_{episode.episode_number}_{episode.id}{file_extension}"
    file_path = upload_dir / filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        # Update episode with file information
        episode.audio_file_path = str(file_path)
        episode.audio_url = f"{settings.BASE_URL}/api/podcast/{podcast_id}/episodes/{episode_id}/audio"
        episode.audio_size = file_path.stat().st_size
        episode.audio_type = audio_file.content_type
        
        # TODO: Extract duration from audio file using ffprobe or similar
        # For now, set a placeholder duration
        episode.duration_seconds = 1800  # 30 minutes placeholder
        
        db.commit()
        
        logger.info(f"Uploaded audio for episode {episode_id}")
        return {"message": "Audio uploaded successfully", "audio_url": episode.audio_url}
        
    except Exception as e:
        logger.error(f"Error uploading audio: {e}")
        raise HTTPException(status_code=500, detail="Error uploading audio file")


@router.get("/{podcast_id}/episodes/{episode_id}/audio")
async def get_episode_audio(
    podcast_id: str,
    episode_id: str,
    db: Session = Depends(get_db)
):
    """Serve episode audio file and track download"""
    
    episode = db.query(PodcastEpisode).join(Podcast).filter(
        and_(
            PodcastEpisode.id == episode_id,
            PodcastEpisode.podcast_id == podcast_id,
            PodcastEpisode.is_deleted == False,
            Podcast.is_deleted == False,
            Podcast.is_published == True,
            PodcastEpisode.status == EpisodeStatus.PUBLISHED.value
        )
    ).first()
    
    if not episode or not episode.audio_file_path:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Check if file exists
    if not os.path.exists(episode.audio_file_path):
        raise HTTPException(status_code=404, detail="Audio file not found on disk")
    
    # Track download (simplified - in production, you'd want more sophisticated tracking)
    episode.download_count += 1
    db.commit()
    
    # Return file
    return FileResponse(
        episode.audio_file_path,
        media_type=episode.audio_type or "audio/mpeg",
        filename=f"episode_{episode.episode_number}.mp3"
    )


# RSS feed endpoints
@router.get("/{podcast_id}/rss", response_class=PlainTextResponse)
async def get_podcast_rss_feed(
    podcast_id: str,
    db: Session = Depends(get_db)
):
    """Generate and serve RSS feed for a podcast"""
    
    podcast = db.query(Podcast).filter(
        and_(
            Podcast.id == podcast_id,
            Podcast.is_deleted == False,
            Podcast.is_published == True
        )
    ).first()
    
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found or not published")
    
    # Update last build date
    podcast.last_build_date = datetime.utcnow()
    db.commit()
    
    # Generate RSS feed
    rss_content = podcast.generate_rss_feed(settings.BASE_URL)
    
    return Response(
        content=rss_content,
        media_type="application/rss+xml",
        headers={"Content-Disposition": f"inline; filename={podcast.title.replace(' ', '_')}.xml"}
    )


# Public endpoints (no authentication required)
@router.get("/public/{podcast_id}/rss", response_class=PlainTextResponse)
async def get_public_podcast_rss_feed(
    podcast_id: str,
    db: Session = Depends(get_db)
):
    """Public RSS feed endpoint (no authentication required)"""
    return await get_podcast_rss_feed(podcast_id, db)


@router.get("/public/{podcast_id}/episodes/{episode_id}/audio")
async def get_public_episode_audio(
    podcast_id: str,
    episode_id: str,
    db: Session = Depends(get_db)
):
    """Public audio endpoint (no authentication required)"""
    return await get_episode_audio(podcast_id, episode_id, db)
