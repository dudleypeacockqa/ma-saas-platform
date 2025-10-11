from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import logging

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
    integrations as integration_models,  # Multi-platform integrations
    integration_planning,  # Integration planning
)

# NOTE: models.py contains legacy Tenant/User models that conflict with
# organization.py and user.py. Do NOT import models.py.
# Legacy code should be migrated to use the new models.

# NOW import APIs (after all models are registered)
from app.api import auth, tenants, users, content, marketing, integrations
# from app.api import payments  # Temporarily disabled - needs StripeCustomer/Payment/WebhookEvent models
from app.api import opportunities, valuations, negotiations, term_sheets, documents, teams
# from app.api import arbitrage  # Temporarily disabled - requires pandas dependency
# from app.api import ai  # Temporarily disabled - needs Deal model update
from app.routers import due_diligence, deals
from app.api.v1 import pipeline, analytics as pipeline_analytics

# Import Clerk authentication components
from app.auth.webhooks import router as webhook_router
from app.routers.users import router as users_router
from app.routers.organizations import router as organizations_router

# Import auth dependencies (needed for route handlers below)
from app.auth.clerk_auth import ClerkUser, get_current_user, require_admin
from app.auth.tenant_isolation import TenantAwareQuery, get_tenant_query
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include API routers with Clerk authentication
app.include_router(webhook_router)  # Clerk webhooks (no auth required)
app.include_router(users_router)    # User management (requires auth)
app.include_router(organizations_router)  # Organization management (requires auth)

# Include existing API routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["tenants"])
app.include_router(deals.router)  # Deal management (prefix already defined in router)
app.include_router(users.router, prefix="/api/users", tags=["users"])
# app.include_router(ai.router, prefix="/api/ai", tags=["ai-analysis"])  # Temporarily disabled
app.include_router(pipeline.router, prefix="/api/v1/pipeline", tags=["pipeline"])  # Pipeline board management
app.include_router(pipeline_analytics.router, prefix="/api/v1/analytics", tags=["analytics"])  # Pipeline analytics
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
app.include_router(documents.router)  # Document management with versioning and approvals
app.include_router(teams.router, prefix="/api")  # Team management and workflow orchestration

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("M&A SaaS Platform API starting up...")

    # Check required environment variables
    required_vars = [
        "CLERK_SECRET_KEY",
        "CLERK_WEBHOOK_SECRET",
        "DATABASE_URL"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")

    # Create database tables using unified Base
    # This runs at startup, not import time, so the app can start even if DB is temporarily unavailable
    # Note: In production, use Alembic migrations instead of create_all()

    # Create required PostgreSQL extensions
    create_extensions(engine)

    # Initialize database schema with proper race condition handling
    init_database(engine, base.Base.metadata)

    # Verify critical tables exist
    critical_tables = ['organizations', 'users', 'deals']
    verify_critical_tables(engine, critical_tables)

    logger.info("API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown"""
    logger.info("M&A SaaS Platform API shutting down...")

@app.get("/")
async def root():
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