from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import logging

from app.core.database import get_db, engine
from app.core.config import settings
from app.api import auth, tenants, users, content
# from app.api import ai  # Temporarily disabled - needs Deal model update
from app.routers import due_diligence, deals
from app.models import models

# Import Clerk authentication components
from app.auth.webhooks import router as webhook_router
from app.routers.users import router as users_router
from app.routers.organizations import router as organizations_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

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
app.include_router(due_diligence.router)  # Due diligence management
app.include_router(content.router)  # Content creation and management

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

# Import auth dependencies at the end to avoid circular imports
from app.auth.clerk_auth import ClerkUser, get_current_user, require_admin
from app.auth.tenant_isolation import TenantAwareQuery, get_tenant_query
from datetime import datetime