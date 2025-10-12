"""
Auth API endpoints for Clerk-based authentication
Provides auth status and user info endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from app.auth.clerk_auth import ClerkUser, get_current_user
from app.models.user import OrganizationRole

router = APIRouter()

class AuthStatusResponse(BaseModel):
    authenticated: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    organization_id: Optional[str] = None
    organization_role: Optional[str] = None

class UserInfoResponse(BaseModel):
    user_id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization_id: Optional[str] = None
    organization_role: Optional[str] = None
    permissions: list[str] = []

@router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status(current_user: Optional[ClerkUser] = Depends(get_current_user)):
    """Get authentication status"""
    if current_user:
        return AuthStatusResponse(
            authenticated=True,
            user_id=current_user.user_id,
            email=current_user.email,
            organization_id=current_user.organization_id,
            organization_role=current_user.organization_role
        )
    else:
        return AuthStatusResponse(authenticated=False)

@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(current_user: ClerkUser = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserInfoResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        organization_id=current_user.organization_id,
        organization_role=current_user.organization_role,
        permissions=[]  # TODO: Load from database based on role
    )

@router.get("/roles")
async def get_available_roles():
    """Get available organization roles"""
    return {
        "roles": [
            {
                "value": role.value,
                "name": role.value.replace("ma:", "").replace("_", " ").title(),
                "description": f"M&A {role.value.replace('ma:', '').replace('_', ' ').title()}"
            }
            for role in OrganizationRole
            if role.value.startswith("ma:")
        ]
    }
