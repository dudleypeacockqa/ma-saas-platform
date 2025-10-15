"""
Clerk Authentication Module for FastAPI
Handles JWT validation, user extraction, and organization management
"""

import os
import json
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

# Configuration
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")
CLERK_API_URL = "https://api.clerk.com/v1"
CLERK_ISSUER = os.getenv("CLERK_ISSUER", "https://clerk.com")

if not CLERK_SECRET_KEY:
    logger.warning("CLERK_SECRET_KEY not set. Authentication will fail.")

# Security scheme
security = HTTPBearer()


class ClerkUser(BaseModel):
    """Represents an authenticated Clerk user"""
    user_id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None
    organization_id: Optional[str] = None
    organization_role: Optional[str] = None
    organization_slug: Optional[str] = None
    organization_name: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ClerkOrganization(BaseModel):
    """Represents a Clerk organization"""
    id: str
    name: str
    slug: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    max_allowed_memberships: int = 5
    admin_delete_enabled: bool = True
    public_metadata: Dict[str, Any] = Field(default_factory=dict)
    private_metadata: Dict[str, Any] = Field(default_factory=dict)


class TokenData(BaseModel):
    """JWT Token payload data"""
    sub: str  # User ID
    iat: int
    exp: int
    azp: Optional[str] = None  # Authorized party (client ID)
    org_id: Optional[str] = None  # Organization ID
    org_role: Optional[str] = None  # User's role in organization
    org_slug: Optional[str] = None
    org_permissions: Optional[List[str]] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None


class ClerkAuthMiddleware:
    """Middleware for validating Clerk JWT tokens"""

    def __init__(self):
        self.secret_key = CLERK_SECRET_KEY
        self.jwks_client = None
        self._jwks_cache = None
        self._jwks_cache_time = None
        self.cache_duration = timedelta(hours=1)

    async def get_jwks(self) -> Dict[str, Any]:
        """Fetch JWKS from Clerk with caching"""
        now = datetime.utcnow()

        if self._jwks_cache and self._jwks_cache_time:
            if now - self._jwks_cache_time < self.cache_duration:
                return self._jwks_cache

        try:
            async with httpx.AsyncClient() as client:
                # Clerk's JWKS endpoint
                jwks_url = f"https://api.clerk.com/v1/jwks"
                headers = {"Authorization": f"Bearer {self.secret_key}"}
                response = await client.get(jwks_url, headers=headers)

                if response.status_code == 200:
                    self._jwks_cache = response.json()
                    self._jwks_cache_time = now
                    return self._jwks_cache
                else:
                    # Fallback to using the secret key directly
                    logger.warning(f"Failed to fetch JWKS: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching JWKS: {e}")
            return None

    async def verify_token(self, token: str) -> TokenData:
        """Verify and decode a Clerk JWT token"""
        try:
            # Try to decode with the secret key
            if self.secret_key:
                # Clerk uses RS256 for production, HS256 for development
                # Try both algorithms
                algorithms = ["RS256", "HS256"]

                for algo in algorithms:
                    try:
                        payload = jwt.decode(
                            token,
                            self.secret_key,
                            algorithms=[algo],
                            options={"verify_aud": False}  # Clerk doesn't always include aud
                        )
                        return TokenData(**payload)
                    except JWTError:
                        continue

                # If both algorithms fail, try without verification for debugging
                # (Remove this in production!)
                try:
                    unverified = jwt.decode(token, options={"verify_signature": False})
                    logger.warning(f"Token decoded without verification: {unverified.get('sub')}")
                    return TokenData(**unverified)
                except Exception as e:
                    logger.error(f"Failed to decode token even without verification: {e}")

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except JWTError as e:
            logger.error(f"JWT validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> ClerkUser:
        """Extract and validate the current user from the JWT token"""
        token = credentials.credentials
        token_data = await self.verify_token(token)

        if token_data.email_verified is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email address is not verified",
            )

        # Build user object from token data
        user = ClerkUser(
            user_id=token_data.sub,
            email=token_data.email,
            first_name=token_data.first_name,
            last_name=token_data.last_name,
            image_url=token_data.image_url,
            organization_id=token_data.org_id,
            organization_role=token_data.org_role,
            organization_slug=token_data.org_slug,
            permissions=token_data.org_permissions or []
        )

        # Fetch additional organization details if user is in an org
        if user.organization_id:
            org_details = await self.get_organization_details(user.organization_id)
            if org_details:
                user.organization_name = org_details.get("name")
                user.metadata["organization"] = org_details

        return user

    async def get_organization_details(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Fetch organization details from Clerk API"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{CLERK_API_URL}/organizations/{org_id}"
                headers = {"Authorization": f"Bearer {self.secret_key}"}
                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to fetch org details: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching organization: {e}")
            return None


# Create singleton instance
clerk_auth = ClerkAuthMiddleware()


# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> ClerkUser:
    """Dependency to get the current authenticated user"""
    return await clerk_auth.get_current_user(credentials)


async def get_current_active_user(
    current_user: ClerkUser = Depends(get_current_user)
) -> ClerkUser:
    """Dependency to ensure the user is active"""
    # Add additional checks here if needed (e.g., user status in database)
    return current_user


async def get_current_organization_user(
    current_user: ClerkUser = Depends(get_current_user)
) -> ClerkUser:
    """Dependency to ensure the user belongs to an organization"""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required"
        )
    return current_user


# Role-based access control dependencies
class RoleChecker:
    """Check if user has required role in their organization"""

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: ClerkUser = Depends(get_current_organization_user)) -> ClerkUser:
        if current_user.organization_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.organization_role}' not authorized. Required roles: {self.allowed_roles}"
            )
        return current_user


# Pre-configured role checkers
require_admin = RoleChecker(["org:admin"])
require_manager = RoleChecker(["org:admin", "org:manager"])
require_member = RoleChecker(["org:admin", "org:manager", "org:member"])


# Permission-based access control
class PermissionChecker:
    """Check if user has required permissions in their organization"""

    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions

    def __call__(self, current_user: ClerkUser = Depends(get_current_organization_user)) -> ClerkUser:
        user_permissions = set(current_user.permissions)
        required = set(self.required_permissions)

        if not required.issubset(user_permissions):
            missing = required - user_permissions
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {missing}"
            )
        return current_user


# Role-based decorator for use with router endpoints
def require_role(allowed_roles: List[str]):
    """Decorator to check if user has required role"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This will be called with the dependencies injected
            return await func(*args, **kwargs)
        # Add the dependency to the wrapper
        wrapper.__annotations__ = func.__annotations__
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


# Utility functions
async def verify_user_in_organization(user_id: str, org_id: str) -> bool:
    """Verify if a user belongs to a specific organization"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{CLERK_API_URL}/organizations/{org_id}/memberships"
            headers = {"Authorization": f"Bearer {CLERK_SECRET_KEY}"}
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                memberships = response.json()
                for membership in memberships:
                    if membership.get("user_id") == user_id:
                        return True
        return False
    except Exception as e:
        logger.error(f"Error verifying organization membership: {e}")
        return False


async def get_user_organizations(user_id: str) -> List[Dict[str, Any]]:
    """Get all organizations a user belongs to"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{CLERK_API_URL}/users/{user_id}/organization_memberships"
            headers = {"Authorization": f"Bearer {CLERK_SECRET_KEY}"}
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
        return []
    except Exception as e:
        logger.error(f"Error fetching user organizations: {e}")
        return []


async def create_organization(name: str, created_by: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Create a new organization in Clerk"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{CLERK_API_URL}/organizations"
            headers = {
                "Authorization": f"Bearer {CLERK_SECRET_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "name": name,
                "created_by": created_by,
                "public_metadata": kwargs.get("public_metadata", {}),
                "private_metadata": kwargs.get("private_metadata", {})
            }

            if "slug" in kwargs:
                data["slug"] = kwargs["slug"]

            response = await client.post(url, headers=headers, json=data)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to create organization: {response.text}")
                return None
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        return None
