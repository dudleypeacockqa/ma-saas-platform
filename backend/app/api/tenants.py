from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import Tenant, User
from app.services.tenant_service import get_current_user, require_admin

router = APIRouter()

class TenantResponse(BaseModel):
    id: int
    name: str
    subscription_plan: str
    is_active: bool
    user_count: int

@router.get("/", response_model=List[TenantResponse])
async def get_tenants(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all tenants (master admin only)"""
    if current_user.role.value != "master_admin":
        # Regular tenant admin can only see their own tenant
        tenant = current_user.tenant
        user_count = db.query(User).filter(User.tenant_id == tenant.id).count()
        return [TenantResponse(
            id=tenant.id,
            name=tenant.name,
            subscription_plan=tenant.subscription_plan.value,
            is_active=tenant.is_active,
            user_count=user_count
        )]
    
    # Master admin sees all tenants
    tenants = db.query(Tenant).all()
    tenant_responses = []
    
    for tenant in tenants:
        user_count = db.query(User).filter(User.tenant_id == tenant.id).count()
        tenant_responses.append(TenantResponse(
            id=tenant.id,
            name=tenant.name,
            subscription_plan=tenant.subscription_plan.value,
            is_active=tenant.is_active,
            user_count=user_count
        ))
    
    return tenant_responses

@router.get("/current", response_model=TenantResponse)
async def get_current_tenant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's tenant information"""
    tenant = current_user.tenant
    user_count = db.query(User).filter(User.tenant_id == tenant.id).count()
    
    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        subscription_plan=tenant.subscription_plan.value,
        is_active=tenant.is_active,
        user_count=user_count
    )
