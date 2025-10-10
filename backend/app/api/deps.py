"""API dependencies for authentication, rate limiting, and database access"""

from typing import Optional, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from datetime import datetime, timedelta
import redis.asyncio as redis
import structlog

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User


logger = structlog.get_logger(__name__)

# Security scheme
security = HTTPBearer()

# Redis client for rate limiting
redis_client = redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None


class CurrentUser:
    """Current authenticated user"""
    def __init__(self, id: str, email: str, organization_id: str, role: str):
        self.id = id
        self.email = email
        self.organization_id = organization_id
        self.role = role


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> CurrentUser:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: Bearer token from Authorization header
        db: Database session

    Returns:
        CurrentUser object

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        user = await db.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return CurrentUser(
            id=str(user.id),
            email=user.email,
            organization_id=str(user.organization_id),
            role=user.role
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """Ensure user is active"""
    return current_user


async def get_current_admin_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """Ensure user has admin role"""
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user


async def verify_api_key(api_key: str = Depends(security)) -> bool:
    """
    Verify API key for service-to-service authentication.

    Args:
        api_key: API key from Authorization header

    Returns:
        True if valid

    Raises:
        HTTPException: If API key is invalid
    """
    # This would validate against stored API keys
    # For now, just check format
    if not api_key or not api_key.credentials.startswith("sk_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return True


class RateLimiter:
    """Rate limiting dependency"""

    def __init__(self, requests_per_minute: int, requests_per_hour: int = None):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour or requests_per_minute * 60

    async def __call__(self, request: Request, current_user: CurrentUser = Depends(get_current_user)) -> None:
        """Check rate limits for user"""
        if not settings.RATE_LIMIT_ENABLED or not redis_client:
            return

        try:
            # Create rate limit keys
            minute_key = f"rate_limit:minute:{current_user.id}"
            hour_key = f"rate_limit:hour:{current_user.id}"

            # Check minute limit
            minute_count = await redis_client.incr(minute_key)
            if minute_count == 1:
                await redis_client.expire(minute_key, 60)

            if minute_count > self.requests_per_minute:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
                )

            # Check hour limit
            if self.requests_per_hour:
                hour_count = await redis_client.incr(hour_key)
                if hour_count == 1:
                    await redis_client.expire(hour_key, 3600)

                if hour_count > self.requests_per_hour:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded: {self.requests_per_hour} requests per hour"
                    )

        except redis.RedisError as e:
            # Log error but don't block request
            logger.error("Rate limiting error", error=str(e))
            return


# Pre-configured rate limiters
rate_limit_standard = RateLimiter(
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    requests_per_hour=settings.RATE_LIMIT_PER_HOUR
)

rate_limit_ai = RateLimiter(
    requests_per_minute=settings.AI_RATE_LIMIT_PER_MINUTE,
    requests_per_hour=settings.AI_RATE_LIMIT_PER_DAY // 24
)


async def get_organization_id(
    current_user: CurrentUser = Depends(get_current_user)
) -> str:
    """Get organization ID from current user"""
    return current_user.organization_id


async def validate_organization_access(
    resource_org_id: str,
    current_user: CurrentUser = Depends(get_current_user)
) -> None:
    """
    Validate user has access to organization resource.

    Args:
        resource_org_id: Organization ID of the resource
        current_user: Current authenticated user

    Raises:
        HTTPException: If user doesn't have access
    """
    if str(resource_org_id) != str(current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resource"
        )


class PaginationParams:
    """Common pagination parameters"""

    def __init__(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ):
        self.skip = skip
        self.limit = min(limit, 100)  # Max 100 items
        self.sort_by = sort_by
        self.sort_order = sort_order


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        user_id: User ID to encode in token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """
    Create JWT refresh token.

    Args:
        user_id: User ID to encode in token

    Returns:
        Encoded refresh token
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt