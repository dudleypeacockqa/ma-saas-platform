"""Main API router aggregating all endpoints"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai,
    auth,
    deals,
    organizations,
    partnerships,
    payments,
    search,
    users,
    webhooks
)

api_router = APIRouter()

# AI and Claude MCP endpoints
api_router.include_router(ai.router, prefix="/ai", tags=["AI Intelligence"])

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Deal management endpoints
api_router.include_router(deals.router, prefix="/deals", tags=["Deals"])

# Organization management
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])

# Partnership recommendations
api_router.include_router(partnerships.router, prefix="/partnerships", tags=["Partnerships"])

# Payment and subscription management
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])

# Search and semantic queries
api_router.include_router(search.router, prefix="/search", tags=["Search"])

# User management
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Webhook handlers
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])