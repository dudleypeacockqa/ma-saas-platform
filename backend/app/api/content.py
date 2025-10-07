from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.database import get_db
from app.models.content import ContentType, ContentStatus
from app.services.content_service import ContentService
from app.api.auth import get_current_user, get_current_tenant

router = APIRouter(prefix="/api/content", tags=["content"])


# Pydantic Schemas

class ContentBase(BaseModel):
    title: str
    content_type: ContentType
    content_body: str
    metadata: Optional[dict] = None
    status: Optional[ContentStatus] = ContentStatus.DRAFT


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    content_body: Optional[str] = None
    metadata: Optional[dict] = None
    status: Optional[ContentStatus] = None
    published_url: Optional[str] = None


class ContentResponse(ContentBase):
    id: int
    tenant_id: int
    user_id: int
    source_type: Optional[str] = None
    source_file_url: Optional[str] = None
    seo_keywords: Optional[list] = None
    published_url: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PodcastEpisodeCreate(BaseModel):
    episode_title: str
    episode_number: Optional[int] = None
    guest_name: Optional[str] = None
    guest_bio: Optional[str] = None
    guest_company: Optional[str] = None
    transcript_text: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None


class PodcastEpisodeResponse(BaseModel):
    id: int
    tenant_id: int
    episode_number: Optional[int] = None
    episode_title: str
    guest_name: Optional[str] = None
    guest_bio: Optional[str] = None
    guest_company: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    timestamps: Optional[list] = None
    key_takeaways: Optional[list] = None
    resources_mentioned: Optional[list] = None
    publish_date: Optional[datetime] = None
    platforms: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenerateShowNotesRequest(BaseModel):
    episode_id: int


class GenerateSocialMediaRequest(BaseModel):
    source_content_id: int
    platform: str = Field(..., pattern="^(linkedin|twitter|youtube|instagram)$")


class GenerateBlogArticleRequest(BaseModel):
    topic: str
    source_content_id: Optional[int] = None
    seo_keywords: Optional[List[str]] = None


class GenerateNewsletterRequest(BaseModel):
    recent_episode_ids: List[int]
    market_insights: Optional[str] = None


class ValidationResponse(BaseModel):
    quality_score: int
    seo_score: int
    suggestions: List[str]
    feedback: str


# Content Endpoints

@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_data: ContentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Create a new content item."""
    service = ContentService(db)
    content = service.create_content(
        tenant_id=tenant_id,
        user_id=current_user["id"],
        **content_data.model_dump()
    )
    return content


@router.get("/", response_model=List[ContentResponse])
async def list_contents(
    content_type: Optional[ContentType] = None,
    status_filter: Optional[ContentStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant)
):
    """List all contents with optional filters."""
    service = ContentService(db)
    contents = service.list_contents(
        tenant_id=tenant_id,
        content_type=content_type,
        status=status_filter,
        limit=limit,
        offset=offset
    )
    return contents


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get a specific content item by ID."""
    service = ContentService(db)
    content = service.get_content_by_id(content_id, tenant_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    return content


@router.patch("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    updates: ContentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Update a content item."""
    service = ContentService(db)
    content = service.update_content(
        content_id=content_id,
        tenant_id=tenant_id,
        **updates.model_dump(exclude_unset=True)
    )
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    return content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant)
):
    """Delete a content item."""
    service = ContentService(db)
    deleted = service.delete_content(content_id, tenant_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )


# Podcast Episode Endpoints

@router.post("/podcast-episodes", response_model=PodcastEpisodeResponse, status_code=status.HTTP_201_CREATED)
async def create_podcast_episode(
    episode_data: PodcastEpisodeCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant)
):
    """Create a new podcast episode."""
    service = ContentService(db)
    episode = service.create_podcast_episode(
        tenant_id=tenant_id,
        **episode_data.model_dump()
    )
    return episode


@router.get("/podcast-episodes", response_model=List[PodcastEpisodeResponse])
async def list_podcast_episodes(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant)
):
    """List all podcast episodes."""
    service = ContentService(db)
    episodes = service.list_podcast_episodes(
        tenant_id=tenant_id,
        limit=limit,
        offset=offset
    )
    return episodes


@router.get("/podcast-episodes/{episode_id}", response_model=PodcastEpisodeResponse)
async def get_podcast_episode(
    episode_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get a specific podcast episode."""
    service = ContentService(db)
    episode = service.get_podcast_episode(episode_id, tenant_id)
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podcast episode not found"
        )
    return episode


# AI Content Generation Endpoints

@router.post("/generate/show-notes", response_model=ContentResponse)
async def generate_show_notes(
    request: GenerateShowNotesRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Generate podcast show notes using AI."""
    service = ContentService(db)
    try:
        content = await service.generate_podcast_show_notes(
            tenant_id=tenant_id,
            user_id=current_user["id"],
            episode_id=request.episode_id
        )
        return content
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate show notes: {str(e)}"
        )


@router.post("/generate/social-media", response_model=ContentResponse)
async def generate_social_media_content(
    request: GenerateSocialMediaRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Generate social media content from existing content."""
    service = ContentService(db)
    try:
        content = await service.generate_social_media_content(
            tenant_id=tenant_id,
            user_id=current_user["id"],
            source_content_id=request.source_content_id,
            platform=request.platform
        )
        return content
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate social media content: {str(e)}"
        )


@router.post("/generate/blog-article", response_model=ContentResponse)
async def generate_blog_article(
    request: GenerateBlogArticleRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Generate a blog article using AI."""
    service = ContentService(db)
    try:
        content = await service.generate_blog_article(
            tenant_id=tenant_id,
            user_id=current_user["id"],
            topic=request.topic,
            source_content_id=request.source_content_id,
            seo_keywords=request.seo_keywords
        )
        return content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate blog article: {str(e)}"
        )


@router.post("/generate/newsletter", response_model=ContentResponse)
async def generate_newsletter(
    request: GenerateNewsletterRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Generate email newsletter content."""
    service = ContentService(db)
    try:
        content = await service.generate_newsletter(
            tenant_id=tenant_id,
            user_id=current_user["id"],
            recent_episode_ids=request.recent_episode_ids,
            market_insights=request.market_insights
        )
        return content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate newsletter: {str(e)}"
        )


@router.post("/validate/{content_id}", response_model=ValidationResponse)
async def validate_content(
    content_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant)
):
    """Validate content quality and get improvement suggestions."""
    service = ContentService(db)
    try:
        validation_result = await service.validate_and_score_content(
            content_id=content_id,
            tenant_id=tenant_id
        )
        return validation_result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate content: {str(e)}"
        )
