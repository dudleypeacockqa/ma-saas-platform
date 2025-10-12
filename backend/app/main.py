"""
Complete FastAPI Application
Master Admin & Business Portal with all integrated systems
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import time
from contextlib import asynccontextmanager

# Core imports
from app.core.database import engine, Base
from app.core.config import settings
from app.auth.clerk_auth import ClerkUser, get_current_user

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
    integrations as integration_models,  # Multi-platform integrations
    integration_planning,  # Integration planning
    email_campaigns,  # Email campaign management
)

# NOTE: models.py contains legacy Tenant/User models that conflict with
# organization.py and user.py. Do NOT import models.py.
# Legacy code should be migrated to use the new models.

# NOW import APIs (after all models are registered)
from app.api import auth, tenants, users, content, marketing, integrations
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

# Initialize Sentry for error tracking
# from app.core.sentry import init_sentry  # Temporarily disabled - sentry_sdk not in requirements
# init_sentry()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting M&A SaaS Platform...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down M&A SaaS Platform...")

# Create FastAPI application
app = FastAPI(
    title="M&A SaaS Platform - Master Admin Portal",
    description="Comprehensive multi-tenant M&A SaaS platform with Master Admin & Business Portal",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://localhost:3000",
        "https://localhost:3001",
        "https://*.vercel.app",
        "https://*.netlify.app",
        settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Mount Socket.IO app for real-time communication
socket_app = socketio.ASGIApp(websocket_manager.sio, app)
app.mount("/socket.io", socket_app)

# Add authentication middleware
from app.middleware.auth_middleware import AuthenticationMiddleware
app.add_middleware(AuthenticationMiddleware)

# Add rate limiting middleware
from app.middleware.rate_limiter import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

# Add security headers and HTTPS enforcement
from app.middleware.security_middleware import SecurityHeadersMiddleware
app.add_middleware(
    SecurityHeadersMiddleware,
    enforce_https=True  # HTTPS enforcement for production
)

# Security
from fastapi.security import HTTPBearer
security = HTTPBearer()

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

# Include existing API routers
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
# app.include_router(payments.router)  # Temporarily disabled - needs StripeCustomer/Payment/WebhookEvent models
app.include_router(integrations.router)  # Platform integrations and workflows
app.include_router(opportunities.router, prefix="/api")  # M&A opportunity management
app.include_router(valuations.router, prefix="/api")  # Financial modeling and valuation
# app.include_router(arbitrage.router, prefix="/api")  # Temporarily disabled - requires pandas dependency
app.include_router(negotiations.router)  # Deal negotiation and structuring
app.include_router(term_sheets.router)  # Term sheet management with collaboration
app.include_router(v1_documents.router, prefix="/api/v1/documents")  # Document management with versioning and approvals
app.include_router(teams.router, prefix="/api")  # Team management and workflow orchestration
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
    logger.info("Static directory not found, skipping static file serving")

# ============================================================================
# STARTUP MESSAGE
# ============================================================================

@app.on_event("startup")
async def startup_message():
    """Log startup message"""
    logger.info("=" * 80)
    logger.info("M&A SAAS PLATFORM - MASTER ADMIN & BUSINESS PORTAL")
    logger.info("=" * 80)
    logger.info("🚀 Platform Status: OPERATIONAL")
    logger.info("📊 Master Admin Portal: ACTIVE")
    logger.info("💳 Subscription Management: ACTIVE")
    logger.info("🎥 Content Creation Suite: ACTIVE")
    logger.info("📅 Event Management: ACTIVE")
    logger.info("🎯 Lead Generation: ACTIVE")
    logger.info("=" * 80)
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Health Check: http://localhost:8000/health")
    logger.info("System Status: http://localhost:8000/status")
    logger.info("=" * 80)

    # Check required environment variables
    required_vars = [
        "CLERK_SECRET_KEY",
        "DATABASE_URL"
    ]

# ============================================================================
# DEVELOPMENT ENDPOINTS (Remove in production)
# ============================================================================

if settings.ENVIRONMENT == "development":
    
    @app.get("/dev/info")
    async def development_info():
        """Development information endpoint"""
        return {
            "environment": "development",
            "debug": True,
            "available_endpoints": [
                "/health",
                "/status",
                "/docs",
                "/redoc",
                "/api/auth/*",
                "/api/users/*",
                "/api/tenants/*",
                "/api/admin/*",
                "/api/subscriptions/*",
                "/api/content/*",
                "/api/events/*",
                "/api/leads/*"
            ],
            "features": {
                "master_admin_portal": True,
                "subscription_management": True,
                "content_creation_suite": True,
                "event_management": True,
                "lead_generation": True,
                "multi_tenant_support": True,
                "stripe_integration": True,
                "eventbrite_integration": True,
                "email_automation": True,
                "lead_scoring": True
            }
        }
    
    @app.get("/dev/test-auth")
    async def test_authentication(current_user: ClerkUser = Depends(get_current_user)):
        """Test authentication endpoint"""
        return {
            "authenticated": True,
            "user_id": current_user.user_id,
            "email": current_user.email,
            "roles": getattr(current_user, 'roles', []),
            "message": "Authentication successful"
        }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "M&A SaaS Platform - Master Admin Portal",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/health",
        "system_status": "/status",
        "features": [
            "Master Admin & Business Portal",
            "Multi-tenant Architecture",
            "Subscription Management",
            "Content Creation Suite",
            "Event Management with EventBrite",
            "Lead Generation & Marketing Automation",
            "Advanced Analytics & Reporting"
        ],
        "message": "Welcome to the M&A SaaS Platform Master Admin Portal"
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting M&A SaaS Platform in development mode...")
    uvicorn.run(
        "main_complete:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
