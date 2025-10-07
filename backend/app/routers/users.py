"""
User Management API Endpoints
Handles user profiles, preferences, and settings
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from ..core.database import get_db
from ..auth.clerk_auth import (
    ClerkUser,
    get_current_user,
    get_current_active_user,
    get_current_organization_user,
    require_admin
)
from ..auth.tenant_isolation import get_tenant_query, TenantAwareQuery
from ..models import User, Organization, OrganizationMembership

router = APIRouter(prefix="/api/users", tags=["users"])


# Pydantic models
class UserProfile(BaseModel):
    """User profile response model"""
    id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    image_url: Optional[str] = None
    username: Optional[str] = None
    created_at: datetime
    last_sign_in_at: Optional[datetime] = None
    organizations: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UserProfileUpdate(BaseModel):
    """User profile update model"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UserPreferences(BaseModel):
    """User preferences model"""
    email_notifications: bool = True
    sms_notifications: bool = False
    deal_updates: bool = True
    team_updates: bool = True
    weekly_reports: bool = True
    monthly_reports: bool = False
    theme: str = "light"
    language: str = "en"
    timezone: str = "UTC"


class TeamMember(BaseModel):
    """Team member model for organization users"""
    id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    role: str
    joined_at: datetime
    last_active: Optional[datetime] = None
    status: str = "active"


# Endpoints
@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: ClerkUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    # Fetch user from database
    user = db.query(User).filter(User.clerk_id == current_user.user_id).first()

    if not user:
        # Create user if doesn't exist (should be created by webhook normally)
        user = User(
            clerk_id=current_user.user_id,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            image_url=current_user.image_url,
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Get user's organizations
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id
    ).all()

    organizations = []
    for membership in memberships:
        org = db.query(Organization).filter(
            Organization.id == membership.organization_id
        ).first()
        if org:
            organizations.append({
                "id": org.clerk_id,
                "name": org.name,
                "role": membership.role,
                "joined_at": membership.created_at
            })

    return UserProfile(
        id=user.clerk_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=f"{user.first_name} {user.last_name}".strip() if user.first_name or user.last_name else None,
        image_url=user.image_url,
        username=user.username,
        created_at=user.created_at,
        last_sign_in_at=user.last_sign_in_at,
        organizations=organizations,
        metadata=user.metadata or {}
    )


@router.patch("/me")
async def update_current_user_profile(
    profile_update: UserProfileUpdate,
    current_user: ClerkUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    user = db.query(User).filter(User.clerk_id == current_user.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    if profile_update.first_name is not None:
        user.first_name = profile_update.first_name
    if profile_update.last_name is not None:
        user.last_name = profile_update.last_name

    # Update metadata
    if profile_update.metadata:
        if not user.metadata:
            user.metadata = {}
        user.metadata.update(profile_update.metadata)

    # Store additional fields in metadata
    if profile_update.phone:
        user.metadata["phone"] = profile_update.phone
    if profile_update.location:
        user.metadata["location"] = profile_update.location
    if profile_update.bio:
        user.metadata["bio"] = profile_update.bio
    if profile_update.job_title:
        user.metadata["job_title"] = profile_update.job_title
    if profile_update.department:
        user.metadata["department"] = profile_update.department

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return {"message": "Profile updated successfully", "user_id": user.clerk_id}


@router.get("/me/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: ClerkUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's preferences"""
    user = db.query(User).filter(User.clerk_id == current_user.user_id).first()

    if not user or not user.preferences:
        # Return default preferences
        return UserPreferences()

    return UserPreferences(**user.preferences)


@router.put("/me/preferences")
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: ClerkUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user's preferences"""
    user = db.query(User).filter(User.clerk_id == current_user.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.preferences = preferences.dict()
    user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Preferences updated successfully"}


@router.get("/team", response_model=List[TeamMember])
async def list_team_members(
    current_user: ClerkUser = Depends(get_current_organization_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None
):
    """List all team members in the current organization"""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization context required"
        )

    # Get organization
    org = db.query(Organization).filter(
        Organization.clerk_id == current_user.organization_id
    ).first()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Get all memberships for the organization
    query = db.query(OrganizationMembership).filter(
        OrganizationMembership.organization_id == org.id
    )

    memberships = query.offset(skip).limit(limit).all()

    team_members = []
    for membership in memberships:
        user = db.query(User).filter(User.id == membership.user_id).first()
        if user:
            # Apply search filter if provided
            if search:
                search_lower = search.lower()
                if not any([
                    search_lower in (user.email or "").lower(),
                    search_lower in (user.first_name or "").lower(),
                    search_lower in (user.last_name or "").lower(),
                    search_lower in (user.username or "").lower()
                ]):
                    continue

            team_members.append(TeamMember(
                id=user.clerk_id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                full_name=f"{user.first_name} {user.last_name}".strip() if user.first_name or user.last_name else None,
                role=membership.role,
                joined_at=membership.created_at,
                last_active=user.last_sign_in_at,
                status="active" if user.is_active else "inactive"
            ))

    return team_members


@router.get("/team/{user_id}", response_model=TeamMember)
async def get_team_member(
    user_id: str,
    current_user: ClerkUser = Depends(get_current_organization_user),
    db: Session = Depends(get_db)
):
    """Get a specific team member's details"""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization context required"
        )

    # Get user
    user = db.query(User).filter(User.clerk_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get organization
    org = db.query(Organization).filter(
        Organization.clerk_id == current_user.organization_id
    ).first()

    # Check if user is member of the organization
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.organization_id == org.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of your organization"
        )

    return TeamMember(
        id=user.clerk_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=f"{user.first_name} {user.last_name}".strip() if user.first_name or user.last_name else None,
        role=membership.role,
        joined_at=membership.created_at,
        last_active=user.last_sign_in_at,
        status="active" if user.is_active else "inactive"
    )


@router.patch("/team/{user_id}/role")
async def update_team_member_role(
    user_id: str,
    role: str,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a team member's role (admin only)"""
    # Get user
    user = db.query(User).filter(User.clerk_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get organization
    org = db.query(Organization).filter(
        Organization.clerk_id == current_user.organization_id
    ).first()

    # Update membership role
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.organization_id == org.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of your organization"
        )

    # Validate role
    valid_roles = ["org:admin", "org:manager", "org:member"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )

    membership.role = role
    membership.updated_at = datetime.utcnow()
    db.commit()

    # Note: You should also update the role in Clerk via their API
    # This is just updating the local database copy

    return {"message": "Role updated successfully", "new_role": role}


@router.delete("/team/{user_id}")
async def remove_team_member(
    user_id: str,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Remove a team member from the organization (admin only)"""
    # Prevent self-removal
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove yourself from the organization"
        )

    # Get user
    user = db.query(User).filter(User.clerk_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get organization
    org = db.query(Organization).filter(
        Organization.clerk_id == current_user.organization_id
    ).first()

    # Delete membership
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.organization_id == org.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of your organization"
        )

    db.delete(membership)
    db.commit()

    # Note: You should also remove the member from Clerk via their API
    # This is just updating the local database copy

    return {"message": "Team member removed successfully"}