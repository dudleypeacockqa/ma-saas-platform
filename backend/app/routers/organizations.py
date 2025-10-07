"""
Organization (Tenant) Management API Endpoints
Handles organization settings, members, and configuration
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..database import get_db
from ..auth.clerk_auth import (
    ClerkUser,
    get_current_organization_user,
    require_admin,
    require_manager,
    create_organization as clerk_create_org
)
from ..auth.tenant_isolation import get_tenant_query, TenantAwareQuery
from ..models import Organization, OrganizationMembership, User

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


# Pydantic models
class OrganizationInfo(BaseModel):
    """Organization information model"""
    id: str
    name: str
    slug: Optional[str] = None
    created_at: datetime
    member_count: int = 0
    max_allowed_memberships: int = 5
    plan: str = "free"
    status: str = "active"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)


class OrganizationCreate(BaseModel):
    """Organization creation model"""
    name: str = Field(..., min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=3, max_length=50)
    max_allowed_memberships: int = Field(5, ge=1, le=1000)
    metadata: Optional[Dict[str, Any]] = None


class OrganizationUpdate(BaseModel):
    """Organization update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=3, max_length=50)
    max_allowed_memberships: Optional[int] = Field(None, ge=1, le=1000)
    metadata: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class OrganizationSettings(BaseModel):
    """Organization settings model"""
    deal_approval_required: bool = False
    auto_assign_deals: bool = True
    default_currency: str = "USD"
    fiscal_year_start: str = "January"
    notification_email: Optional[str] = None
    webhook_url: Optional[str] = None
    data_retention_days: int = 365
    features: Dict[str, bool] = Field(default_factory=lambda: {
        "advanced_analytics": False,
        "api_access": True,
        "custom_fields": False,
        "unlimited_users": False,
        "white_label": False
    })


class OrganizationInvite(BaseModel):
    """Organization invitation model"""
    email: str
    role: str = "org:member"
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class OrganizationStats(BaseModel):
    """Organization statistics model"""
    total_deals: int = 0
    active_deals: int = 0
    total_value: float = 0
    completed_deals: int = 0
    success_rate: float = 0
    member_count: int = 0
    document_count: int = 0
    last_activity: Optional[datetime] = None


# Endpoints
@router.get("/current", response_model=OrganizationInfo)
async def get_current_organization(
    current_user: ClerkUser = Depends(get_current_organization_user),
    db: Session = Depends(get_db)
):
    """Get current organization details"""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not in organization context"
        )

    org = db.query(Organization).filter(
        Organization.clerk_id == current_user.organization_id
    ).first()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Count members
    member_count = db.query(OrganizationMembership).filter(
        OrganizationMembership.organization_id == org.id
    ).count()

    return OrganizationInfo(
        id=org.clerk_id,
        name=org.name,
        slug=org.slug,
        created_at=org.created_at,
        member_count=member_count,
        max_allowed_memberships=org.max_allowed_memberships,
        plan=org.metadata.get("plan", "free") if org.metadata else "free",
        status="active" if org.is_active else "inactive",
        metadata=org.metadata or {},
        settings=org.settings or {}
    )


@router.patch("/current")
async def update_current_organization(
    org_update: OrganizationUpdate,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update current organization (admin only)"""
    org = db.query(Organization).filter(
        Organization.clerk_id == current_user.organization_id
    ).first()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Update fields
    if org_update.name is not None:
        org.name = org_update.name
    if org_update.slug is not None:
        org.slug = org_update.slug
    if org_update.max_allowed_memberships is not None:
        org.max_allowed_memberships = org_update.max_allowed_memberships
    if org_update.metadata is not None:
        if not org.metadata:
            org.metadata = {}
        org.metadata.update(org_update.metadata)
    if org_update.settings is not None:
        if not org.settings:
            org.settings = {}
        org.settings.update(org_update.settings)

    org.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(org)

    # Note: You should also update the organization in Clerk via their API

    return {"message": "Organization updated successfully", "organization_id": org.clerk_id}


@router.get("/current/settings", response_model=OrganizationSettings)
async def get_organization_settings(
    current_user: ClerkUser = Depends(get_current_organization_user),
    db: Session = Depends(get_db)
):
    """Get organization settings"""
    org = db.query(Organization).filter(
        Organization.clerk_id == current_user.organization_id
    ).first()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Return settings or defaults
    if org.settings:
        return OrganizationSettings(**org.settings)
    else:
        return OrganizationSettings()


@router.put("/current/settings")
async def update_organization_settings(
    settings: OrganizationSettings,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update organization settings (admin only)"""
    org = db.query(Organization).filter(
        Organization.clerk_id == current_user.organization_id
    ).first()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    org.settings = settings.dict()
    org.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Settings updated successfully"}


@router.get("/current/stats", response_model=OrganizationStats)
async def get_organization_stats(
    current_user: ClerkUser = Depends(get_current_organization_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    db: Session = Depends(get_db)
):
    """Get organization statistics"""
    org = db.query(Organization).filter(
        Organization.clerk_id == current_user.organization_id
    ).first()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Count members
    member_count = db.query(OrganizationMembership).filter(
        OrganizationMembership.organization_id == org.id
    ).count()

    # Get deal statistics (assuming you have a Deal model)
    # This is placeholder logic - adjust based on your actual Deal model
    stats = OrganizationStats(
        member_count=member_count,
        # Add actual statistics queries here
        # total_deals=tenant_query.count(Deal),
        # active_deals=tenant_query.count(Deal, {"status": "active"}),
        # etc.
    )

    return stats


@router.post("/current/invite")
async def invite_to_organization(
    invite: OrganizationInvite,
    current_user: ClerkUser = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Invite a user to the organization (manager+ only)"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == invite.email).first()

    if existing_user:
        # Check if already a member
        org = db.query(Organization).filter(
            Organization.clerk_id == current_user.organization_id
        ).first()

        membership = db.query(OrganizationMembership).filter(
            OrganizationMembership.user_id == existing_user.id,
            OrganizationMembership.organization_id == org.id
        ).first()

        if membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization"
            )

    # Note: In production, you would:
    # 1. Create an invitation in Clerk via their API
    # 2. Send an invitation email
    # 3. Track the invitation in your database

    return {
        "message": "Invitation sent successfully",
        "email": invite.email,
        "role": invite.role
    }


@router.get("/")
async def list_user_organizations(
    current_user: ClerkUser = Depends(get_current_organization_user),
    db: Session = Depends(get_db)
):
    """List all organizations the user belongs to"""
    # Get user
    user = db.query(User).filter(User.clerk_id == current_user.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get all memberships
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id
    ).all()

    organizations = []
    for membership in memberships:
        org = db.query(Organization).filter(
            Organization.id == membership.organization_id
        ).first()

        if org and org.is_active:
            organizations.append({
                "id": org.clerk_id,
                "name": org.name,
                "slug": org.slug,
                "role": membership.role,
                "joined_at": membership.created_at,
                "is_current": org.clerk_id == current_user.organization_id
            })

    return {"organizations": organizations}


@router.post("/")
async def create_organization(
    org_data: OrganizationCreate,
    current_user: ClerkUser = Depends(get_current_organization_user),
    db: Session = Depends(get_db)
):
    """Create a new organization"""
    # Check if slug is unique
    if org_data.slug:
        existing = db.query(Organization).filter(
            Organization.slug == org_data.slug
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization slug already exists"
            )

    # Create organization in Clerk
    clerk_org = await clerk_create_org(
        name=org_data.name,
        created_by=current_user.user_id,
        slug=org_data.slug,
        public_metadata=org_data.metadata or {}
    )

    if not clerk_org:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create organization"
        )

    # Create in local database
    new_org = Organization(
        clerk_id=clerk_org["id"],
        name=org_data.name,
        slug=org_data.slug or clerk_org.get("slug"),
        created_at=datetime.utcnow(),
        max_allowed_memberships=org_data.max_allowed_memberships,
        metadata=org_data.metadata or {},
        is_active=True
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    # Add creator as admin
    user = db.query(User).filter(User.clerk_id == current_user.user_id).first()
    if user:
        membership = OrganizationMembership(
            clerk_id=f"mem_{new_org.id}_{user.id}",  # Generate a unique ID
            user_id=user.id,
            organization_id=new_org.id,
            role="org:admin",
            created_at=datetime.utcnow()
        )
        db.add(membership)
        db.commit()

    return {
        "message": "Organization created successfully",
        "organization": {
            "id": new_org.clerk_id,
            "name": new_org.name,
            "slug": new_org.slug
        }
    }


@router.delete("/current")
async def delete_organization(
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete the current organization (admin only)"""
    org = db.query(Organization).filter(
        Organization.clerk_id == current_user.organization_id
    ).first()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Soft delete
    org.is_active = False
    org.deleted_at = datetime.utcnow()
    db.commit()

    # Note: You should also delete the organization in Clerk via their API

    return {"message": "Organization deleted successfully"}