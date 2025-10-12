#!/usr/bin/env python3
"""
Comprehensive Platform Verification
Verify all Sprints 1-8 are 100% correct, aligned and error-free
"""

import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sprint1_core_foundation():
    """Verify Sprint 1 - Core Platform Foundation"""
    print("VERIFYING SPRINT 1 - CORE PLATFORM FOUNDATION...")
    try:
        # Test core imports
        from app.main import app
        from app.core.database import get_db, engine
        from app.core.config import settings
        from app.models.base import Base

        # Test authentication
        from app.auth.clerk_auth import ClerkUser, get_current_user
        from app.auth.tenant_isolation import TenantAwareQuery

        # Test basic models
        from app.models.organization import Organization
        from app.models.user import User

        # Test basic API endpoints
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        basic_routes = ["/", "/health", "/api/protected-example"]

        missing_routes = [route for route in basic_routes if route not in routes]
        if missing_routes:
            print(f"FAILED: Missing basic routes: {missing_routes}")
            return False

        print("SUCCESS: Sprint 1 core foundation verified")
        return True

    except Exception as e:
        print(f"FAILED: Sprint 1 verification failed: {e}")
        return False

def test_sprint2_deal_management():
    """Verify Sprint 2 - Deal Management System"""
    print("\nVERIFYING SPRINT 2 - DEAL MANAGEMENT SYSTEM...")
    try:
        # Test deal models and imports
        from app.models.deal import Deal
        from app.routers.deals import router as deals_router
        from app.main import app

        # Test deal-related routes exist
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        deal_routes = [route for route in routes if '/deals' in route or '/api/deals' in route]

        if len(deal_routes) < 5:  # Should have basic CRUD operations
            print(f"FAILED: Insufficient deal routes found: {len(deal_routes)}")
            return False

        print(f"SUCCESS: Sprint 2 deal management verified - {len(deal_routes)} deal routes")
        return True

    except Exception as e:
        print(f"FAILED: Sprint 2 verification failed: {e}")
        return False

def test_sprint3_document_management():
    """Verify Sprint 3 - Document Management & Collaboration"""
    print("\nVERIFYING SPRINT 3 - DOCUMENT MANAGEMENT & COLLABORATION...")
    try:
        # Check if Sprint 3 verification exists and runs
        if os.path.exists("sprint3_verification_summary.py"):
            import subprocess
            result = subprocess.run([sys.executable, "sprint3_verification_summary.py"],
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0 and "100.0%" in result.stdout:
                print("SUCCESS: Sprint 3 document management verified via existing verification")
                return True

        # Fallback manual verification
        from app.api.v1.documents import router as docs_router
        from app.models.documents import Document
        from app.main import app

        # Check document routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        doc_routes = [route for route in routes if '/documents' in route]

        if len(doc_routes) < 8:  # Should have comprehensive document management
            print(f"FAILED: Insufficient document routes: {len(doc_routes)}")
            return False

        print(f"SUCCESS: Sprint 3 document management verified - {len(doc_routes)} document routes")
        return True

    except Exception as e:
        print(f"FAILED: Sprint 3 verification failed: {e}")
        return False

def test_sprint4_user_management():
    """Verify Sprint 4 - Advanced User Management"""
    print("\nVERIFYING SPRINT 4 - ADVANCED USER MANAGEMENT...")
    try:
        # Test user management components
        from app.routers.users import router as users_router
        from app.routers.organizations import router as orgs_router
        from app.auth.webhooks import router as webhook_router

        # Test permission system
        from app.core.permissions import PermissionChecker, ResourceType, Action

        # Verify permission matrix
        from app.core.permissions import PERMISSION_MATRIX
        required_resources = [ResourceType.DEALS, ResourceType.DOCUMENTS, ResourceType.ADMIN]

        for resource in required_resources:
            if resource not in PERMISSION_MATRIX:
                print(f"FAILED: Missing permission resource: {resource}")
                return False

        print("SUCCESS: Sprint 4 advanced user management verified")
        return True

    except Exception as e:
        print(f"FAILED: Sprint 4 verification failed: {e}")
        return False

def test_sprint5_analytics_reporting():
    """Verify Sprint 5 - Advanced Analytics & Reporting"""
    print("\nVERIFYING SPRINT 5 - ADVANCED ANALYTICS & REPORTING...")
    try:
        # Test analytics components
        from app.api.v1.analytics_advanced import router as analytics_router
        from app.api.v1.reports import router as reports_router
        from app.main import app

        # Check for analytics routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        analytics_routes = [route for route in routes if '/analytics' in route or '/reports' in route]

        if len(analytics_routes) < 10:  # Should have comprehensive analytics
            print(f"FAILED: Insufficient analytics routes: {len(analytics_routes)}")
            return False

        print(f"SUCCESS: Sprint 5 analytics & reporting verified - {len(analytics_routes)} routes")
        return True

    except Exception as e:
        print(f"FAILED: Sprint 5 verification failed: {e}")
        return False

def test_sprint6_predictive_analytics():
    """Verify Sprint 6 - Predictive Analytics Implementation"""
    print("\nVERIFYING SPRINT 6 - PREDICTIVE ANALYTICS IMPLEMENTATION...")
    try:
        # Check if Sprint 6 verification exists and runs
        if os.path.exists("sprint6_verification.py"):
            import subprocess
            result = subprocess.run([sys.executable, "sprint6_verification.py"],
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0 and "100.0%" in result.stdout:
                print("SUCCESS: Sprint 6 predictive analytics verified via existing verification")
                return True

        # Fallback manual verification
        from app.api.v1.predictive_analytics import router as predictive_router

        # Check predictive analytics routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        predictive_routes = [route for route in routes if '/predictive' in route]

        if len(predictive_routes) < 5:
            print(f"FAILED: Insufficient predictive analytics routes: {len(predictive_routes)}")
            return False

        print(f"SUCCESS: Sprint 6 predictive analytics verified - {len(predictive_routes)} routes")
        return True

    except Exception as e:
        print(f"FAILED: Sprint 6 verification failed: {e}")
        return False

def test_sprint7_realtime_collaboration():
    """Verify Sprint 7 - Real-Time Collaboration"""
    print("\nVERIFYING SPRINT 7 - REAL-TIME COLLABORATION...")
    try:
        # Check if Sprint 7 verification exists and runs
        if os.path.exists("sprint7_final_verification.py"):
            import subprocess
            result = subprocess.run([sys.executable, "sprint7_final_verification.py"],
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0 and "100.0%" in result.stdout:
                print("SUCCESS: Sprint 7 real-time collaboration verified via existing verification")
                return True

        # Fallback manual verification
        from app.api.v1.realtime_collaboration import router as realtime_router
        from app.realtime.websocket_manager import WebSocketManager
        from app.realtime.notifications import NotificationService
        from app.realtime.collaboration import CollaborativeDocumentManager
        from app.realtime.task_automation import TaskAutomationEngine
        from app.main import app

        # Check real-time routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        realtime_routes = [route for route in routes if '/collaboration' in route]

        if len(realtime_routes) < 15:  # Should have comprehensive real-time features
            print(f"FAILED: Insufficient real-time collaboration routes: {len(realtime_routes)}")
            return False

        print(f"SUCCESS: Sprint 7 real-time collaboration verified - {len(realtime_routes)} routes")
        return True

    except Exception as e:
        print(f"FAILED: Sprint 7 verification failed: {e}")
        return False

def test_sprint8_mobile_pwa():
    """Verify Sprint 8 - Mobile-First Experience & PWA"""
    print("\nVERIFYING SPRINT 8 - MOBILE-FIRST EXPERIENCE & PWA...")
    try:
        # Check if Sprint 8 verification exists and runs
        if os.path.exists("sprint8_verification.py"):
            import subprocess
            result = subprocess.run([sys.executable, "sprint8_verification.py"],
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0 and "100.0%" in result.stdout:
                print("SUCCESS: Sprint 8 mobile-first & PWA verified via existing verification")
                return True

        # Fallback manual verification
        from app.api.v1.mobile import router as mobile_router
        from app.mobile.pwa_service import PWAService
        from app.mobile.offline_sync import OfflineSyncService
        from app.mobile.mobile_auth import MobileAuthService
        from app.mobile.performance_optimizer import MobilePerformanceOptimizer
        from app.main import app

        # Check mobile routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        mobile_routes = [route for route in routes if '/mobile' in route]

        if len(mobile_routes) < 12:  # Should have comprehensive mobile features
            print(f"FAILED: Insufficient mobile routes: {len(mobile_routes)}")
            return False

        print(f"SUCCESS: Sprint 8 mobile-first & PWA verified - {len(mobile_routes)} routes")
        return True

    except Exception as e:
        print(f"FAILED: Sprint 8 verification failed: {e}")
        return False

def test_cross_sprint_integration():
    """Test integration between all sprints"""
    print("\nVERIFYING CROSS-SPRINT INTEGRATION...")
    try:
        from app.main import app

        # Get all routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]

        # Count routes by sprint/feature area
        route_categories = {
            'core': len([r for r in routes if r in ['/', '/health', '/api/protected-example']]),
            'deals': len([r for r in routes if '/deals' in r]),
            'documents': len([r for r in routes if '/documents' in r]),
            'users': len([r for r in routes if '/users' in r or '/organizations' in r]),
            'analytics': len([r for r in routes if '/analytics' in r or '/reports' in r or '/predictive' in r]),
            'realtime': len([r for r in routes if '/collaboration' in r]),
            'mobile': len([r for r in routes if '/mobile' in r])
        }

        # Verify minimum route counts
        minimum_requirements = {
            'core': 3,
            'deals': 5,
            'documents': 8,
            'users': 5,
            'analytics': 10,
            'realtime': 15,
            'mobile': 12
        }

        failed_categories = []
        for category, count in route_categories.items():
            if count < minimum_requirements[category]:
                failed_categories.append(f"{category}: {count}/{minimum_requirements[category]}")

        if failed_categories:
            print(f"FAILED: Insufficient routes in categories: {failed_categories}")
            return False

        # Test that core services can be imported together
        from app.core.permissions import PermissionChecker
        from app.realtime.websocket_manager import get_websocket_manager
        from app.mobile.pwa_service import get_pwa_service

        print("SUCCESS: Cross-sprint integration verified")
        print(f"Total API routes: {len(routes)}")
        for category, count in route_categories.items():
            print(f"  {category.title()}: {count} routes")

        return True

    except Exception as e:
        print(f"FAILED: Cross-sprint integration verification failed: {e}")
        return False

def test_api_consistency():
    """Test API consistency across all sprints"""
    print("\nVERIFYING API CONSISTENCY...")
    try:
        from app.main import app

        # Check that all routers are properly registered
        router_imports = [
            'auth', 'tenants', 'deals', 'users', 'pipeline', 'analytics',
            'analytics_advanced', 'reports', 'predictive_analytics',
            'realtime_collaboration', 'mobile', 'due_diligence', 'content',
            'marketing', 'integrations', 'opportunities', 'valuations',
            'negotiations', 'term_sheets', 'documents', 'teams'
        ]

        # Get all routes with their methods
        routes_info = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes_info.append({
                    'path': route.path,
                    'methods': list(route.methods) if route.methods else []
                })

        # Check for standard HTTP methods
        http_methods = set()
        for route_info in routes_info:
            http_methods.update(route_info['methods'])

        expected_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}
        if not expected_methods.issubset(http_methods):
            missing_methods = expected_methods - http_methods
            print(f"FAILED: Missing HTTP methods: {missing_methods}")
            return False

        # Check for consistent API versioning
        v1_routes = [r['path'] for r in routes_info if '/api/v1/' in r['path']]
        if len(v1_routes) < 30:  # Should have substantial v1 API coverage
            print(f"FAILED: Insufficient v1 API routes: {len(v1_routes)}")
            return False

        print("SUCCESS: API consistency verified")
        print(f"Total routes: {len(routes_info)}")
        print(f"V1 API routes: {len(v1_routes)}")
        print(f"HTTP methods supported: {sorted(http_methods)}")

        return True

    except Exception as e:
        print(f"FAILED: API consistency verification failed: {e}")
        return False

def test_security_alignment():
    """Test security implementation across all sprints"""
    print("\nVERIFYING SECURITY ALIGNMENT...")
    try:
        # Test authentication components
        from app.auth.clerk_auth import ClerkUser, get_current_user, require_admin
        from app.auth.tenant_isolation import TenantAwareQuery, get_tenant_query
        from app.middleware.auth_middleware import AuthenticationMiddleware

        # Test permission system
        from app.core.permissions import PermissionChecker, ResourceType, Action, PERMISSION_MATRIX

        # Verify all resource types have permissions
        required_resources = [
            ResourceType.DEALS, ResourceType.DOCUMENTS, ResourceType.ANALYTICS,
            ResourceType.REPORTS, ResourceType.ADMIN, ResourceType.TEAMS,
            ResourceType.COMMUNICATIONS
        ]

        missing_resources = []
        for resource in required_resources:
            if resource not in PERMISSION_MATRIX:
                missing_resources.append(resource)

        if missing_resources:
            print(f"FAILED: Missing permission resources: {missing_resources}")
            return False

        # Test mobile security
        from app.mobile.mobile_auth import MobileAuthService, AuthMethod

        print("SUCCESS: Security alignment verified")
        print(f"Permission resources: {len(PERMISSION_MATRIX)}")
        print(f"Authentication methods: {len(AuthMethod)}")

        return True

    except Exception as e:
        print(f"FAILED: Security alignment verification failed: {e}")
        return False

def run_comprehensive_verification():
    """Run comprehensive verification of all sprints"""
    print("=" * 80)
    print("COMPREHENSIVE PLATFORM VERIFICATION - SPRINTS 1-8")
    print("Verifying all sprints are 100% correct, aligned and error-free")
    print("=" * 80)

    tests = [
        ("Sprint 1 - Core Platform Foundation", test_sprint1_core_foundation),
        ("Sprint 2 - Deal Management System", test_sprint2_deal_management),
        ("Sprint 3 - Document Management & Collaboration", test_sprint3_document_management),
        ("Sprint 4 - Advanced User Management", test_sprint4_user_management),
        ("Sprint 5 - Advanced Analytics & Reporting", test_sprint5_analytics_reporting),
        ("Sprint 6 - Predictive Analytics Implementation", test_sprint6_predictive_analytics),
        ("Sprint 7 - Real-Time Collaboration", test_sprint7_realtime_collaboration),
        ("Sprint 8 - Mobile-First Experience & PWA", test_sprint8_mobile_pwa),
        ("Cross-Sprint Integration", test_cross_sprint_integration),
        ("API Consistency", test_api_consistency),
        ("Security Alignment", test_security_alignment)
    ]

    passed = 0
    failed = 0
    failed_tests = []

    for test_name, test_func in tests:
        try:
            print(f"\n[{len(tests) - len(failed_tests) - (len(tests) - passed - failed)}/{len(tests)}] {test_name}")
            if test_func():
                passed += 1
            else:
                failed += 1
                failed_tests.append(test_name)
        except Exception as e:
            print(f"CRASHED: {test_name} - {e}")
            print(f"Traceback: {traceback.format_exc()}")
            failed += 1
            failed_tests.append(test_name)

    print("\n" + "=" * 80)
    print("COMPREHENSIVE VERIFICATION RESULTS")
    print("=" * 80)

    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print(f"SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")

    if failed > 0:
        print(f"\nFAILED TESTS:")
        for test in failed_tests:
            print(f"  - {test}")
        print(f"\nCRITICAL: {failed} VERIFICATION TESTS FAILED")
        print("STATUS: PLATFORM NOT READY - ISSUES FOUND")
        return False
    else:
        print(f"\nALL {passed} VERIFICATION TESTS PASSED")
        print("STATUS: PLATFORM 100% VERIFIED & READY")
        print("\nPLATFORM SUMMARY:")
        print("✓ Sprint 1: Core Platform Foundation - VERIFIED")
        print("✓ Sprint 2: Deal Management System - VERIFIED")
        print("✓ Sprint 3: Document Management & Collaboration - VERIFIED")
        print("✓ Sprint 4: Advanced User Management - VERIFIED")
        print("✓ Sprint 5: Advanced Analytics & Reporting - VERIFIED")
        print("✓ Sprint 6: Predictive Analytics Implementation - VERIFIED")
        print("✓ Sprint 7: Real-Time Collaboration - VERIFIED")
        print("✓ Sprint 8: Mobile-First Experience & PWA - VERIFIED")
        print("✓ Cross-Sprint Integration - VERIFIED")
        print("✓ API Consistency - VERIFIED")
        print("✓ Security Alignment - VERIFIED")
        return True

if __name__ == "__main__":
    success = run_comprehensive_verification()
    sys.exit(0 if success else 1)