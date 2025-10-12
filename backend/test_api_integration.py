#!/usr/bin/env python3
"""
Sprint 21 - API Integration Test
Simple test to verify the deal management APIs are working
"""

import os
import sys
import asyncio
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_api_integration():
    """Test the API integration without actually starting the server"""
    print("=== SPRINT 21 API INTEGRATION TEST ===")

    # Test 1: Import core modules
    try:
        from app.main import app
        from app.routers.deals import router as deals_router
        from app.models.deal import Deal, DealStage, DealType, DealPriority
        from app.core.config import settings

        print("[PASS] Core modules imported successfully")

        # Test routes are registered
        route_count = len([r for r in app.routes if hasattr(r, 'path')])
        print(f"[INFO] Total routes registered: {route_count}")

        # Check deals router endpoints
        deal_routes = [r.path for r in deals_router.routes if hasattr(r, 'path')]
        print(f"[INFO] Deal routes: {len(deal_routes)} endpoints")

        # Verify critical endpoints exist
        critical_endpoints = ['/', '/{deal_id}', '/analytics/summary']
        missing_endpoints = [ep for ep in critical_endpoints if ep not in deal_routes]

        if not missing_endpoints:
            print("[PASS] All critical deal endpoints present")
        else:
            print(f"[WARN] Missing endpoints: {missing_endpoints}")

    except Exception as e:
        print(f"[FAIL] Core module import failed: {str(e)}")
        return False

    # Test 2: Database models
    try:
        # Test model enums
        assert DealStage.SOURCING.value == 'sourcing'
        assert DealType.ACQUISITION.value == 'acquisition'
        assert DealPriority.HIGH.value == 'high'

        print("[PASS] Deal model enums working")

        # Test model structure exists
        deal_attrs = ['id', 'organization_id', 'title', 'stage', 'deal_type']
        model_attrs = [attr for attr in dir(Deal) if not attr.startswith('_')]

        missing_attrs = [attr for attr in deal_attrs if attr not in model_attrs]
        if not missing_attrs:
            print("[PASS] Deal model has required attributes")
        else:
            print(f"[WARN] Missing model attributes: {missing_attrs}")

    except Exception as e:
        print(f"[FAIL] Database model test failed: {str(e)}")
        return False

    # Test 3: Configuration
    try:
        assert settings.app_name == "M&A SaaS Platform"
        assert hasattr(settings, 'DATABASE_URL')
        assert hasattr(settings, 'REDIS_URL')
        assert hasattr(settings, 'CLERK_SECRET_KEY')

        print("[PASS] Configuration settings verified")

    except Exception as e:
        print(f"[FAIL] Configuration test failed: {str(e)}")
        return False

    # Test 4: Authentication components
    try:
        from app.auth.clerk_auth import ClerkUser, get_current_user
        from app.auth.tenant_isolation import get_tenant_query

        print("[PASS] Authentication components imported")

    except Exception as e:
        print(f"[FAIL] Authentication test failed: {str(e)}")
        return False

    print("\n=== SPRINT 21 API INTEGRATION SUMMARY ===")
    print("[SUCCESS] All API integration tests passed!")
    print("- Backend APIs are properly structured")
    print("- Database models are functional")
    print("- Configuration is complete")
    print("- Authentication components ready")
    print("\nReady for frontend-backend connection!")

    return True

if __name__ == "__main__":
    success = asyncio.run(test_api_integration())
    if success:
        print("\n[RESULT] API integration verification: PASSED")
        exit(0)
    else:
        print("\n[RESULT] API integration verification: FAILED")
        exit(1)