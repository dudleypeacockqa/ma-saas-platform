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

# API routers
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.tenants import router as tenants_router
from app.api.master_admin import router as master_admin_router
from app.api.subscription_management import router as subscription_router
from app.api.content_creation import router as content_router
from app.api.event_management import router as event_router
from app.api.lead_generation import router as lead_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    return response

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "path": str(request.url)
        }
    )

# ============================================================================
# API ROUTES
# ============================================================================

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "M&A SaaS Platform - Master Admin Portal",
        "version": "1.0.0",
        "timestamp": time.time()
    }

# System status endpoint
@app.get("/status")
async def system_status(current_user: ClerkUser = Depends(get_current_user)):
    """System status endpoint (requires authentication)"""
    return {
        "status": "operational",
        "services": {
            "database": "connected",
            "authentication": "active",
            "master_admin": "active",
            "subscription_management": "active",
            "content_creation": "active",
            "event_management": "active",
            "lead_generation": "active"
        },
        "user": {
            "user_id": current_user.user_id,
            "email": current_user.email
        },
        "timestamp": time.time()
    }

# Include API routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(tenants_router, prefix="/api/tenants", tags=["tenants"])
app.include_router(master_admin_router, prefix="/api/admin", tags=["master-admin"])
app.include_router(subscription_router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(content_router, prefix="/api/content", tags=["content-creation"])
app.include_router(event_router, prefix="/api/events", tags=["events"])
app.include_router(lead_router, prefix="/api/leads", tags=["leads"])

# ============================================================================
# STATIC FILES AND FRONTEND SERVING
# ============================================================================

# Mount static files (if serving frontend from backend)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # Static directory doesn't exist, skip mounting
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
