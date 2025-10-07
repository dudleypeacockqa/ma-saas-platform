from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.database import get_db
from app.core.config import settings
from app.models.models import User, Tenant

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        tenant_id: int = payload.get("tenant_id")
        
        if email is None or user_id is None or tenant_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id, User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_tenant(current_user: User = Depends(get_current_user)) -> Tenant:
    """Get current user's tenant"""
    return current_user.tenant

def require_tenant_access(resource_tenant_id: int, current_user: User = Depends(get_current_user)):
    """Ensure user has access to the specified tenant's resources"""
    if current_user.role.value == "master_admin":
        return  # Master admin has access to all tenants
    
    if current_user.tenant_id != resource_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant's resources"
        )

def require_role(required_roles: list):
    """Decorator to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value not in required_roles and current_user.role.value != "master_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Common role requirements
require_admin = require_role(["master_admin", "tenant_admin"])
require_deal_manager = require_role(["master_admin", "tenant_admin", "deal_manager"])
require_analyst = require_role(["master_admin", "tenant_admin", "deal_manager", "analyst"])
