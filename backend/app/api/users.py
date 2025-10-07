from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.models.models import User, UserRole
from app.services.tenant_service import get_current_user, require_admin

router = APIRouter()

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    tenant_id: int

@router.get("/", response_model=List[UserResponse])
async def get_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users in the current tenant"""
    if current_user.role.value == "master_admin":
        # Master admin can see all users
        users = db.query(User).all()
    else:
        # Tenant admin can only see users in their tenant
        users = db.query(User).filter(User.tenant_id == current_user.tenant_id).all()
    
    return [UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        tenant_id=user.tenant_id
    ) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check access permissions
    if (current_user.role.value not in ["master_admin", "tenant_admin"] and 
        current_user.id != user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if (current_user.role.value == "tenant_admin" and 
        user.tenant_id != current_user.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        tenant_id=user.tenant_id
    )
