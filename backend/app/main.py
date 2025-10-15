from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import logging
from pathlib import Path
from typing import Optional

from app.core.database import get_db, engine
from app.core.config import settings
from app.core.db_init import init_database, verify_critical_tables, create_extensions

# CRITICAL: Import models BEFORE APIs to avoid duplicate table registration
# APIs import services, which import models. We must import models first.

# Import base module first to get unified Base class
from app.models import base

# Import ALL model modules to register tables with metadata
# IMPORTANT: Import order matters to avoid circular dependencies
from app.models import (
    # Core models (organization and user must come first for foreign keys)
    organization,  # Organization model (replaces legacy models.Tenant)
    user,  # User model (replaces legacy models.User)
    subscription,  # Subscription model

    # Business domain models
    deal,  # Deal management
    due_diligence as dd_models,  # Due diligence
    content as content_models,  # Content models
    analytics,  # Analytics
    prospects,  # Prospects
    transactions,  # Transactions
    # integration,  # Skip - conflicts with integration_planning.py (use integration_planning instead)

    # New M&A feature models
    financial_models,  # Valuation models
    opportunities as opportunity_models,  # Deal sourcing
    negotiations as negotiation_models,  # Negotiations (includes term sheets)
    documents as document_models,  # Documents
    arbitrage as arbitrage_models,  # Arbitrage
    teams as team_models,  # Teams
    # term_sheets,  # Part of negotiations.py
    episodes,  # Podcast production
    podcast_studio,  # StreamYard-level podcast recording and AI automation
    integrations as integration_models,  # Multi-platform integrations
    integration_planning,  # Integration planning
    email_campaigns,  # Email campaign management
    # waitlist,  # BMad Method: Premium event waitlist management - Temporarily disabled
)

# NOTE: models.py contains legacy Tenant/User models that conflict with
# organization.py and user.py. Do NOT import models.py.
# Legacy code should be migrated to use the new models.

# NOW import APIs (after all models are registered)
from app.api import auth, tenants, users, content, marketing, integrations, podcast_studio, stripe_events

# Advanced platform APIs pull in optional analytics dependencies that may not
# be present in lightweight deployments (like static marketing hosting). We
# import them lazily so the landing page can be served even if the analytics
# stack is unavailable.
advanced_platform = None
advanced_platform_import_error: Optional[ModuleNotFoundError] = None

try:
    from app.api import advanced_platform  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover
    advanced_platform_import_error = exc
# from app.api import waitlist  # Temporarily disabled - requires model fixes
# from app.api import master_admin  # Temporarily disabled - requires BusinessMetrics, RevenueAnalytics models
# from app.api import emails  # Temporarily disabled - needs ClerkUser migration
# from app.api import payments  # Temporarily disabled - needs StripeCustomer/Payment/WebhookEvent models
from app.api import opportunities, valuations, negotiations, term_sheets, teams
# from app.api import arbitrage  # Temporarily disabled - requires pandas dependency
# from app.api import ai  # Temporarily disabled - needs Deal model update
from app.routers import due_diligence, deals, ai_intelligence
from app.api.v1 import pipeline, analytics as pipeline_analytics, documents as v1_documents, analytics_advanced, reports, predictive_analytics, realtime_collaboration

# Import Clerk authentication components
from app.auth.webhooks import router as webhook_router
from app.routers.users import router as users_router
from app.routers.organizations import router as organizations_router

# Import WebSocket manager
from app.websockets.websocket_manager import websocket_manager
import socketio

# Import auth dependencies (needed for route handlers below)
from app.auth.clerk_auth import ClerkUser, get_current_user, require_admin
from app.auth.tenant_isolation import TenantAwareQuery, get_tenant_query
from datetime import datetime

# Configure structured logging
from app.core.logging import setup_logging, get_logger
setup_logging()
logger = get_logger(__name__)

if advanced_platform_import_error:
    logger.warning(
        "Advanced platform APIs disabled: %s",
        advanced_platform_import_error,
    )

# Resolve marketing site paths so the backend can serve the landing page
# Primary location is alongside the backend code (/app/website in production)
# We keep a fallback to project-root/website for local development before Docker build.
BASE_DIR = Path(__file__).resolve().parents[1]
WEBSITE_DIR = BASE_DIR / "website"

if not WEBSITE_DIR.exists():
    ALT_WEBSITE_DIR = Path(__file__).resolve().parents[2] / "website"
    if ALT_WEBSITE_DIR.exists():
        WEBSITE_DIR = ALT_WEBSITE_DIR

WEBSITE_INDEX = WEBSITE_DIR / "index.html"


class CacheControlStaticFiles(StaticFiles):
    """StaticFiles wrapper that applies Cache-Control headers when serving files."""

    def __init__(self, *args, cache_control: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_control = cache_control

    async def get_response(self, path: str, scope):  # type: ignore[override]
        response = await super().get_response(path, scope)
        if self.cache_control and response.status_code == 200:
            response.headers.setdefault("Cache-Control", self.cache_control)
        return response

# Initialize Sentry for error tracking
# from app.core.sentry import init_sentry  # Temporarily disabled - sentry_sdk not in requirements
# init_sentry()

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="M&A SaaS Platform",
    description="Multi-tenant SaaS application for M&A deal management with Clerk authentication",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)


def mount_marketing_dir(path: str, directory: Path, *, cache_control: Optional[str] = None, html: bool = False) -> None:
    """Safely mount static directories for the marketing site."""

    if directory.exists():
        app.mount(
            path,
            CacheControlStaticFiles(directory=str(directory), html=html, cache_control=cache_control),
            name=f"marketing-{path.strip('/') or 'root'}",
        )
        logger.info("Mounted marketing directory %s -> %s", path, directory)
    else:
        logger.debug("Marketing directory missing %s -> %s", path, directory)


if WEBSITE_DIR.exists():
    mount_marketing_dir(
        "/assets",
        WEBSITE_DIR / "assets",
        cache_control="public, max-age=31536000, immutable",
    )
    mount_marketing_dir(
        "/images",
        WEBSITE_DIR / "images",
        cache_control="public, max-age=86400",
    )
    mount_marketing_dir(
        "/blog",
        WEBSITE_DIR / "blog",
        cache_control="public, max-age=300",
        html=True,
    )
    mount_marketing_dir(
        "/podcast",
        WEBSITE_DIR / "podcast",
        cache_control="public, max-age=300",
        html=True,
    )
    mount_marketing_dir(
        "/legal",
        WEBSITE_DIR / "legal",
        cache_control="public, max-age=3600",
        html=True,
    )
else:
    logger.warning("Marketing site directory not found; landing page will fall back to API JSON response")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO app for real-time communication
socket_app = socketio.ASGIApp(websocket_manager.sio, app)
app.mount("/socket.io", socket_app)

# Add authentication middleware
from app.middleware.auth_middleware import AuthenticationMiddleware
app.add_middleware(AuthenticationMiddleware)

# Add rate limiting middleware
# from app.middleware.rate_limiter import RateLimitMiddleware  # Temporarily disabled - redis not installed
# app.add_middleware(RateLimitMiddleware)

# Add security headers and HTTPS enforcement
from app.middleware.security_middleware import SecurityHeadersMiddleware
app.add_middleware(
    SecurityHeadersMiddleware,
    enforce_https=True  # HTTPS enforcement for production
)

# Security
security = HTTPBearer()

# Include API routers with Clerk authentication
app.include_router(webhook_router)  # Clerk webhooks (no auth required)
app.include_router(users_router)    # User management (requires auth)
app.include_router(organizations_router)  # Organization management (requires auth)

# Include existing API routers
if advanced_platform:
    app.include_router(advanced_platform.router, prefix="/api", tags=["advanced-platform"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["tenants"])
app.include_router(deals.router)  # Deal management (prefix already defined in router)
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(ai_intelligence.router)  # AI intelligence and analytics
app.include_router(pipeline.router, prefix="/api/v1/pipeline", tags=["pipeline"])  # Pipeline board management
app.include_router(pipeline_analytics.router, prefix="/api/v1/analytics", tags=["analytics"])  # Pipeline analytics
app.include_router(analytics_advanced.router, prefix="/api/v1/analytics-advanced", tags=["analytics-advanced"])  # Sprint 5: Advanced Analytics
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])  # Sprint 5: Data Export & Reporting
app.include_router(predictive_analytics.router, prefix="/api/v1/predictive", tags=["predictive-analytics"])  # Sprint 6: Predictive Analytics
app.include_router(realtime_collaboration.router, prefix="/api/v1/collaboration", tags=["real-time-collaboration"])  # Sprint 7: Real-Time Collaboration
app.include_router(due_diligence.router)  # Due diligence management
app.include_router(content.router)  # Content creation and management
app.include_router(marketing.router)  # Marketing and subscriber acquisition
# app.include_router(master_admin.router)  # Master Admin Portal API - Temporarily disabled
app.include_router(podcast_studio.router)  # Podcast Studio - StreamYard-level recording API
# app.include_router(payments.router)  # Temporarily disabled - needs StripeCustomer/Payment/WebhookEvent models
app.include_router(stripe_events.router)  # Stripe Event Payments API - One-time event ticket purchases
app.include_router(integrations.router)  # Platform integrations and workflows
app.include_router(opportunities.router, prefix="/api")  # M&A opportunity management
app.include_router(valuations.router, prefix="/api")  # Financial modeling and valuation
# app.include_router(arbitrage.router, prefix="/api")  # Temporarily disabled - requires pandas dependency
app.include_router(negotiations.router)  # Deal negotiation and structuring
app.include_router(term_sheets.router)  # Term sheet management with collaboration
app.include_router(v1_documents.router, prefix="/api/v1/documents")  # Document management with versioning and approvals
app.include_router(teams.router, prefix="/api")  # Team management and workflow orchestration
# app.include_router(waitlist.router)  # BMad Method: Premium event waitlist management - Temporarily disabled
# app.include_router(emails.router)  # Email campaign management - Temporarily disabled - needs ClerkUser migration

# WebSocket status endpoint
@app.get("/api/websocket/status")
async def websocket_status():
    """Get WebSocket connection statistics"""
    return websocket_manager.get_connection_stats()

@app.get("/api/websocket/activity/{organization_id}")
async def websocket_activity(organization_id: str):
    """Get user activity for an organization"""
    return websocket_manager.get_user_activity(organization_id)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("M&A SaaS Platform API starting up...")

    # Initialize cache service
    try:
        from app.core.cache import cache_service
        await cache_service.initialize()
        logger.info("Cache service initialized")
    except Exception as e:
        logger.warning(f"Cache initialization failed: {e}. Continuing without cache.")

    # Check required environment variables
    required_vars = [
        "CLERK_SECRET_KEY",
        "DATABASE_URL"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")

    # Optional environment variables
    if not os.getenv("CLERK_WEBHOOK_SECRET"):
        logger.warning("CLERK_WEBHOOK_SECRET not set. Webhook verification will be disabled.")

    # Initialize database using SYNC operations only during startup
    # This prevents AsyncIO greenlet issues
    try:
        logger.info("Starting database initialization...")

        # Create required PostgreSQL extensions (sync operation)
        extensions_created = create_extensions(engine)
        if extensions_created:
            logger.info("Database extensions ready")

        # Initialize database schema with proper race condition handling (sync operation)
        schema_initialized = init_database(engine, base.Base.metadata)
        if schema_initialized:
            logger.info("Database schema initialized")

        # Verify critical tables exist (sync operation)
        critical_tables = ['organizations', 'users', 'deals', 'documents']
        tables_verified = verify_critical_tables(engine, critical_tables)
        if tables_verified:
            logger.info("Critical tables verified")

        logger.info("Database initialization completed successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("Application will continue with limited functionality")
        logger.warning("Database-dependent features may not work until database is available")
        # Don't fail startup - allow app to start even if DB is unavailable

    logger.info("API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown"""
    logger.info("M&A SaaS Platform API shutting down...")

@app.get("/", include_in_schema=False)
async def root():
    if WEBSITE_INDEX.exists():
        response = FileResponse(WEBSITE_INDEX, media_type="text/html")
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers.setdefault("X-Robots-Tag", "index,follow")
        return response

    logger.warning("Marketing index not found; returning API status JSON")
    return {
        "message": "M&A SaaS Platform API",
        "status": "running",
        "version": "2.0.0",
        "authentication": "Clerk",
        "documentation": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "clerk_configured": bool(os.getenv("CLERK_SECRET_KEY")),
        "database_configured": bool(os.getenv("DATABASE_URL")),
        "webhook_configured": bool(os.getenv("CLERK_WEBHOOK_SECRET"))
    }

@app.get("/api/protected-example")
async def protected_endpoint_example(
    current_user: ClerkUser = Depends(get_current_user)
):
    """Example of a protected endpoint requiring authentication"""
    return {
        "message": "This is a protected endpoint",
        "user_id": current_user.user_id,
        "email": current_user.email,
        "organization_id": current_user.organization_id,
        "organization_role": current_user.organization_role
    }

@app.get("/api/admin-example")
async def admin_endpoint_example(
    current_user: ClerkUser = Depends(require_admin)
):
    """Example of an admin-only endpoint"""
    return {
        "message": "This is an admin-only endpoint",
        "user_id": current_user.user_id,
        "role": current_user.organization_role
    }

@app.get("/api/tenant-example")
async def tenant_isolated_example(
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    """Example of tenant-isolated data access"""
    # This would only return data for the user's organization
    # deals = tenant_query.list(Deal, limit=10)
    return {
        "message": "This endpoint uses tenant isolation",
        "organization_id": tenant_query.organization_id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=bool(os.getenv("DEV_MODE", False))
    )
