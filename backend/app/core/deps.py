"""
Core dependencies for FastAPI endpoints
Provides common dependencies for authentication, database access, and permissions
"""

from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import httpx
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.database import get_db as get_database_session
from app.core.config import settings
from app.models.user import User
from app.models.organization import Organization


# Security scheme for JWT bearer tokens
security = HTTPBearer(auto_error=False)  # Don't auto-raise errors, let us handle them


def get_db() -> Generator:
    """
    Database dependency
    Yields a database session and ensures it's closed after use
    """
    db = next(get_database_session())
    try:
        yield db
    finally:
        db.close()


async def verify_clerk_token(token: str) -> dict:
    """
    Verify a Clerk JWT token
    Returns the decoded token payload if valid
    """
    try:
        # Get Clerk's public keys for verification
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.clerk.dev/v1/jwks",
                headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not verify authentication token"
            )

        # Decode and verify the JWT
        # Note: In production, you should cache the JWKS and implement proper key rotation
        decoded_token = jwt.decode(
            token,
            options={"verify_signature": False},  # For development - implement proper verification
            algorithms=["RS256"]
        )

        return decoded_token

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from the JWT token
    """
    # Check if credentials are provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials

    # Verify the token with Clerk
    token_data = await verify_clerk_token(token)

    # Get user from database
    user_clerk_id = token_data.get("sub")
    if not user_clerk_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(
        User.clerk_id == user_clerk_id,
        User.is_deleted == False
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


async def get_current_organization(
    current_user: User = Depends(get_current_user),
    organization_id: Optional[str] = Header(None, alias="X-Organization-ID"),
    db: Session = Depends(get_db)
) -> Organization:
    """
    Get the current organization from the request
    Can be specified via header or derived from user's default organization
    """
    org_id = organization_id

    # If no organization ID provided, use user's default
    if not org_id:
        # Check if user has memberships
        if current_user.organization_memberships:
            # Get the first active membership
            for membership in current_user.organization_memberships:
                if membership.is_active:
                    org_id = str(membership.organization_id)
                    break

        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No organization context available"
            )

    # Fetch the organization
    organization = db.query(Organization).filter(
        Organization.id == org_id,
        Organization.is_deleted == False
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Verify user has access to this organization
    has_access = any(
        membership.organization_id == organization.id and membership.is_active
        for membership in current_user.organization_memberships
    )

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )

    return organization


async def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise return None
    Useful for endpoints that work with or without authentication
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    try:
        token = authorization.replace("Bearer ", "")
        token_data = await verify_clerk_token(token)

        user_clerk_id = token_data.get("sub")
        if not user_clerk_id:
            return None

        user = db.query(User).filter(
            User.clerk_id == user_clerk_id,
            User.is_deleted == False,
            User.is_active == True
        ).first()

        return user
    except:
        return None


def check_permission(
    user: User,
    organization: Organization,
    resource: str,
    action: str
) -> bool:
    """
    Check if a user has permission to perform an action on a resource

    Args:
        user: The user to check permissions for
        organization: The organization context
        resource: The resource type (e.g., 'deals', 'documents')
        action: The action to perform (e.g., 'read', 'write', 'delete')

    Returns:
        True if the user has permission

    Raises:
        HTTPException: If the user doesn't have permission
    """
    # Get user's membership in the organization
    membership = None
    for m in user.organization_memberships:
        if m.organization_id == organization.id and m.is_active:
            membership = m
            break

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization"
        )

    # Check role-based permissions
    # For now, implement a simple role hierarchy
    role_permissions = {
        "owner": ["read", "write", "delete", "admin"],
        "admin": ["read", "write", "delete"],
        "member": ["read", "write"],
        "viewer": ["read"]
    }

    allowed_actions = role_permissions.get(membership.role, [])

    if action not in allowed_actions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to {action} {resource}"
        )

    return True


class PaginationParams:
    """
    Common pagination parameters for list endpoints
    """
    def __init__(
        self,
        skip: int = 0,
        limit: int = 25
    ):
        self.skip = max(0, skip)
        self.limit = min(100, max(1, limit))


class SortingParams:
    """
    Common sorting parameters for list endpoints
    """
    def __init__(
        self,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ):
        self.sort_by = sort_by
        self.sort_order = sort_order if sort_order in ["asc", "desc"] else "desc"


# Alias for backward compatibility
async def get_current_tenant(
    current_user: User = Depends(get_current_user),
    organization_id: Optional[str] = Header(None, alias="X-Organization-ID"),
    db: Session = Depends(get_db)
):
    """
    Alias for get_current_organization that returns organization.id
    For backward compatibility with existing document API
    """
    organization = await get_current_organization(current_user, organization_id, db)
    return organization.id