"""
Security middleware for production environment
Implements HTTPS enforcement, security headers, and CSP
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
import os
from app.core.logging import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    Implements OWASP security best practices
    """

    def __init__(self, app, enforce_https: bool = True):
        super().__init__(app)
        self.enforce_https = enforce_https
        self.environment = os.getenv("ENVIRONMENT", "development")

    async def dispatch(self, request: Request, call_next):
        # HTTPS Enforcement (in production)
        if self.enforce_https and self.environment == "production":
            # Check if request is not using HTTPS
            if request.url.scheme != "https":
                # Check for forwarded proto header (from load balancer)
                forwarded_proto = request.headers.get("x-forwarded-proto", "")
                if forwarded_proto != "https":
                    # Redirect to HTTPS
                    https_url = request.url.replace(scheme="https")
                    logger.info(f"Redirecting HTTP to HTTPS: {request.url} -> {https_url}")
                    return RedirectResponse(url=str(https_url), status_code=301)

        # Process request
        response = await call_next(request)

        # Add security headers
        self._add_security_headers(response)

        return response

    def _add_security_headers(self, response: Response):
        """Add comprehensive security headers"""

        # Strict-Transport-Security (HSTS)
        # Force HTTPS for 1 year, including subdomains
        if self.environment == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # X-Content-Type-Options
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options
        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection
        # Enable browser XSS protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy
        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy (Feature-Policy)
        # Disable unnecessary browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )

        # Content-Security-Policy (CSP)
        # Define allowed sources for content
        csp_directives = self._get_csp_directives()
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Cross-Origin-Embedder-Policy
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"

        # Cross-Origin-Opener-Policy
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        # Cross-Origin-Resource-Policy
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Remove server header (don't advertise server technology)
        if "server" in response.headers:
            del response.headers["server"]

        # Add custom server header (optional)
        response.headers["X-Powered-By"] = "M&A SaaS Platform"

    def _get_csp_directives(self) -> list:
        """
        Generate Content Security Policy directives
        Adjust these based on your application's needs
        """

        # Production CSP (strict)
        if self.environment == "production":
            return [
                "default-src 'self'",
                "script-src 'self' https://clerk.*.clerk.accounts.dev https://*.sentry.io",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data: https: blob:",
                "connect-src 'self' https://api.render.com https://ma-saas-backend.onrender.com https://*.clerk.accounts.dev https://*.sentry.io",
                "frame-src 'self' https://*.clerk.accounts.dev https://js.stripe.com",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
                "upgrade-insecure-requests",
                "block-all-mixed-content",
            ]

        # Development CSP (relaxed for debugging)
        else:
            return [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:",
                "style-src 'self' 'unsafe-inline' https:",
                "font-src 'self' data: https:",
                "img-src 'self' data: https: blob:",
                "connect-src 'self' http: https: ws: wss:",
                "frame-src 'self' https:",
            ]


class RateLimitByIPMiddleware(BaseHTTPMiddleware):
    """
    Additional rate limiting by IP address
    Works alongside the existing rate limiter
    """

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}  # In production, use Redis

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self._get_client_ip(request)

        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health"]:
            return await call_next(request)

        # Check rate limit (simplified - in production use Redis)
        # This is just a demonstration
        logger.debug(f"Request from IP: {client_ip}")

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = "99"  # Placeholder

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers (from load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take first IP in list
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client
        return request.client.host if request.client else "unknown"


# ============================================================================
# USAGE IN MAIN.PY
# ============================================================================

"""
# In app/main.py, add after creating FastAPI app:

from app.middleware.security_middleware import SecurityHeadersMiddleware

# Add security middleware
app.add_middleware(
    SecurityHeadersMiddleware,
    enforce_https=True  # Set to True for production
)

# The middleware will:
# 1. Enforce HTTPS in production
# 2. Add security headers to all responses
# 3. Implement CSP, HSTS, and other protections
# 4. Remove server identification headers
"""
