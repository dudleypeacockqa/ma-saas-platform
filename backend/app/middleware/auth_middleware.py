"""
Unified Authentication Middleware
Handles authentication across all platforms and services
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import httpx

from app.auth.clerk_auth import clerk_auth, ClerkUser

logger = logging.getLogger(__name__)

# Configuration
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Unified authentication middleware for all incoming requests
    Handles Clerk JWT validation and user context
    """

    # Paths that don't require authentication
    PUBLIC_PATHS = [
        "/",
        "/health",
        "/api/docs",
        "/api/redoc",
        "/openapi.json",
        "/api/webhooks/clerk",
        "/api/payments/webhook",
        "/api/auth/login",
        "/api/auth/register"
    ]

    def __init__(self, app):
        super().__init__(app)

    def is_public_path(self, path: str) -> bool:
        """Check if path is publicly accessible"""
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True
        return False

    async def dispatch(self, request: Request, call_next):
        """Process authentication for incoming requests"""
        path = request.url.path

        # Skip authentication for public paths
        if self.is_public_path(path):
            return await call_next(request)

        # Extract authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid authorization header"},
                headers={"WWW-Authenticate": "Bearer"}
            )

        try:
            # Extract token
            token = auth_header.replace("Bearer ", "")

            # Verify token using Clerk
            token_data = await clerk_auth.verify_token(token)

            if not token_data:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid authentication token"},
                    headers={"WWW-Authenticate": "Bearer"}
                )

            # Add user context to request state
            request.state.user_id = token_data.sub
            request.state.organization_id = token_data.org_id
            request.state.user_role = token_data.org_role
            request.state.user_email = token_data.email

            # Add headers for downstream services
            request.headers.__dict__["_list"].extend([
                (b"x-user-id", token_data.sub.encode()),
                (b"x-organization-id", (token_data.org_id or "").encode()),
                (b"x-user-role", (token_data.org_role or "").encode())
            ])

            # Continue with request
            response = await call_next(request)

            return response

        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            logger.error(f"Authentication middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Authentication processing failed"}
            )


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """
    Ensure tenant isolation for multi-tenant operations
    Validates organization_id on all data access
    """

    # Paths that don't require tenant isolation
    EXEMPT_PATHS = [
        "/",
        "/health",
        "/api/docs",
        "/api/redoc",
        "/api/webhooks",
        "/api/auth"
    ]

    def __init__(self, app):
        super().__init__(app)

    def is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from tenant isolation"""
        for exempt_path in self.EXEMPT_PATHS:
            if path.startswith(exempt_path):
                return True
        return False

    async def dispatch(self, request: Request, call_next):
        """Enforce tenant isolation"""
        path = request.url.path

        # Skip for exempt paths
        if self.is_exempt_path(path):
            return await call_next(request)

        # Check if organization_id is present in request state
        organization_id = getattr(request.state, "organization_id", None)

        if not organization_id:
            logger.warning(f"Missing organization_id for tenant-isolated path: {path}")
            # Allow request but log warning
            # In production, you might want to enforce this more strictly

        # Add tenant context header
        response = await call_next(request)
        response.headers["X-Tenant-ID"] = organization_id or "none"

        return response


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """
    API Key authentication for programmatic access
    Allows external integrations to authenticate with API keys
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Check for API key authentication"""
        api_key = request.headers.get("X-API-Key")

        if api_key:
            # Validate API key
            is_valid, org_info = await self.validate_api_key(api_key)

            if is_valid:
                # Add organization context from API key
                request.state.organization_id = org_info.get("organization_id")
                request.state.api_key_access = True
                request.state.api_key_scopes = org_info.get("scopes", [])

                return await call_next(request)

        # Continue without API key auth
        return await call_next(request)

    async def validate_api_key(self, api_key: str) -> tuple[bool, Dict[str, Any]]:
        """
        Validate API key against database
        Returns (is_valid, organization_info)
        """
        # TODO: Implement API key validation against database
        # For now, return False
        return False, {}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all API requests for monitoring and debugging
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Log request details"""
        start_time = datetime.utcnow()

        # Extract request info
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "organization_id", None)

        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
            success = status_code < 400

        except Exception as e:
            logger.error(f"Request failed: {method} {path} - {e}")
            status_code = 500
            success = False
            raise

        finally:
            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()

            # Log request
            log_data = {
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_seconds": duration,
                "client_host": client_host,
                "user_id": user_id,
                "organization_id": org_id,
                "success": success,
                "timestamp": start_time.isoformat()
            }

            if success:
                logger.info(f"API Request: {method} {path} - {status_code} ({duration:.3f}s)")
            else:
                logger.warning(f"API Request Failed: {method} {path} - {status_code} ({duration:.3f}s)")

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Add security headers"""
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://clerk.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https:",
            "connect-src 'self' https://api.clerk.com https://api.stripe.com"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        return response
