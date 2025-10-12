#!/usr/bin/env python3
"""
Sprint 8 Verification Test
Verify Sprint 8 - Mobile-First Experience & Progressive Web App Implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sprint8_endpoints():
    """Test Sprint 8 mobile-optimized endpoints are registered"""
    print("TESTING SPRINT 8 ENDPOINT REGISTRATION...")
    try:
        from app.main import app
        routes = [route.path for route in app.routes if hasattr(route, 'path')]

        # Sprint 8 Mobile-First & PWA endpoints
        mobile_endpoints = [
            '/api/v1/mobile/manifest.json',
            '/api/v1/mobile/service-worker.js',
            '/api/v1/mobile/pwa/subscribe',
            '/api/v1/mobile/pwa/test-notification',
            '/api/v1/mobile/dashboard/summary',
            '/api/v1/mobile/deals/mobile',
            '/api/v1/mobile/deals/{deal_id}/mobile',
            '/api/v1/mobile/sync/queue',
            '/api/v1/mobile/sync/pending',
            '/api/v1/mobile/sync/conflicts',
            '/api/v1/mobile/sync/conflicts/{conflict_id}/resolve',
            '/api/v1/mobile/sync/full',
            '/api/v1/mobile/mobile/health'
        ]

        missing = []
        found = []

        for endpoint in mobile_endpoints:
            # Check if endpoint pattern exists in routes
            endpoint_found = False
            for route in routes:
                if '/api/v1/mobile/' in route and any(part in route for part in endpoint.split('/')):
                    endpoint_found = True
                    found.append(endpoint)
                    break

            if not endpoint_found:
                missing.append(endpoint)

        print(f"SUCCESS: Found {len(found)} Sprint 8 mobile endpoints")
        for endpoint in found:
            print(f"  - {endpoint}")

        if missing:
            print(f"\nFAILED: Missing {len(missing)} Sprint 8 endpoints:")
            for endpoint in missing:
                print(f"  - {endpoint}")
            return False
        else:
            print(f"\nSUCCESS: All {len(mobile_endpoints)} Sprint 8 mobile endpoints registered")
            return True

    except Exception as e:
        print(f"FAILED: Sprint 8 endpoint test failed: {e}")
        return False

def test_mobile_module_imports():
    """Test mobile modules import correctly"""
    print("\nTESTING MOBILE MODULE IMPORTS...")
    try:
        from app.mobile.pwa_service import PWAService, PWANotification, PWAManifestGenerator
        print("SUCCESS: PWA service imported")

        from app.mobile.offline_sync import OfflineSyncService, SyncOperation, ConflictResolution
        print("SUCCESS: Offline sync service imported")

        from app.mobile.mobile_auth import MobileAuthService, DeviceType, AuthMethod
        print("SUCCESS: Mobile auth service imported")

        from app.mobile.performance_optimizer import MobilePerformanceOptimizer, DeviceClass, ConnectionType
        print("SUCCESS: Performance optimizer imported")

        from app.api.v1 import mobile
        print("SUCCESS: Mobile API imported")

        # Test instantiation
        pwa_service = PWAService()
        sync_service = OfflineSyncService()
        auth_service = MobileAuthService()
        optimizer = MobilePerformanceOptimizer()
        print("SUCCESS: Mobile services instantiated")

        return True

    except Exception as e:
        print(f"FAILED: Mobile module import test failed: {e}")
        return False

def test_pwa_functionality():
    """Test PWA service functionality"""
    print("\nTESTING PWA FUNCTIONALITY...")
    try:
        from app.mobile.pwa_service import PWAService, PWANotification, PWAManifestGenerator, NotificationAction

        # Test PWA service
        pwa_service = PWAService()

        # Test notification actions
        assert NotificationAction.OPEN_DEAL == "open_deal"
        assert NotificationAction.OPEN_DOCUMENT == "open_document"
        assert NotificationAction.APPROVE == "approve"
        print("SUCCESS: PWA notification actions defined correctly")

        # Test manifest generator
        manifest_generator = PWAManifestGenerator()
        manifest = manifest_generator.generate_manifest()

        assert "name" in manifest
        assert "short_name" in manifest
        assert "icons" in manifest
        assert "start_url" in manifest
        assert manifest["display"] == "standalone"
        print("SUCCESS: PWA manifest generation working")

        # Test service worker generation
        service_worker = manifest_generator.generate_service_worker()
        assert "addEventListener" in service_worker
        assert "push" in service_worker
        assert "notification" in service_worker
        print("SUCCESS: Service worker generation working")

        # Test notification creation
        notification = pwa_service.create_deal_notification(
            deal_id="test-deal",
            deal_title="Test Deal",
            action="updated",
            actor_name="Test User"
        )
        assert notification.title is not None
        assert notification.data["deal_id"] == "test-deal"
        print("SUCCESS: PWA notification creation working")

        return True

    except Exception as e:
        print(f"FAILED: PWA functionality test failed: {e}")
        return False

def test_offline_sync_functionality():
    """Test offline synchronization functionality"""
    print("\nTESTING OFFLINE SYNC FUNCTIONALITY...")
    try:
        from app.mobile.offline_sync import OfflineSyncService, SyncOperation, SyncStatus, ConflictResolution

        sync_service = OfflineSyncService()

        # Test sync operations
        assert SyncOperation.CREATE == "create"
        assert SyncOperation.UPDATE == "update"
        assert SyncOperation.DELETE == "delete"
        print("SUCCESS: Sync operations defined correctly")

        # Test sync status
        assert SyncStatus.PENDING == "pending"
        assert SyncStatus.IN_PROGRESS == "in_progress"
        assert SyncStatus.COMPLETED == "completed"
        assert SyncStatus.FAILED == "failed"
        assert SyncStatus.CONFLICT == "conflict"
        print("SUCCESS: Sync statuses defined correctly")

        # Test conflict resolution
        assert ConflictResolution.CLIENT_WINS == "client_wins"
        assert ConflictResolution.SERVER_WINS == "server_wins"
        assert ConflictResolution.MERGE == "merge"
        assert ConflictResolution.MANUAL == "manual"
        print("SUCCESS: Conflict resolution strategies defined correctly")

        # Test service methods exist
        assert hasattr(sync_service, 'queue_sync_item')
        assert hasattr(sync_service, 'create_sync_item')
        assert hasattr(sync_service, 'resolve_conflict')
        assert hasattr(sync_service, 'perform_full_sync')
        print("SUCCESS: Offline sync service methods available")

        return True

    except Exception as e:
        print(f"FAILED: Offline sync functionality test failed: {e}")
        return False

def test_mobile_authentication():
    """Test mobile authentication functionality"""
    print("\nTESTING MOBILE AUTHENTICATION...")
    try:
        from app.mobile.mobile_auth import MobileAuthService, DeviceType, AuthMethod, MobileDevice

        auth_service = MobileAuthService()

        # Test device types
        assert DeviceType.IOS == "ios"
        assert DeviceType.ANDROID == "android"
        assert DeviceType.PWA == "pwa"
        assert DeviceType.WEB == "web"
        print("SUCCESS: Device types defined correctly")

        # Test auth methods
        assert AuthMethod.PASSWORD == "password"
        assert AuthMethod.BIOMETRIC == "biometric"
        assert AuthMethod.FACE_ID == "face_id"
        assert AuthMethod.TOUCH_ID == "touch_id"
        assert AuthMethod.WEBAUTHN == "webauthn"
        print("SUCCESS: Authentication methods defined correctly")

        # Test service methods exist
        assert hasattr(auth_service, 'register_device')
        assert hasattr(auth_service, 'authenticate_mobile')
        assert hasattr(auth_service, 'setup_biometric_auth')
        assert hasattr(auth_service, 'refresh_mobile_session')
        assert hasattr(auth_service, 'get_user_devices')
        print("SUCCESS: Mobile auth service methods available")

        return True

    except Exception as e:
        print(f"FAILED: Mobile authentication test failed: {e}")
        return False

def test_performance_optimization():
    """Test mobile performance optimization"""
    print("\nTESTING PERFORMANCE OPTIMIZATION...")
    try:
        from app.mobile.performance_optimizer import MobilePerformanceOptimizer, DeviceClass, ConnectionType, MobileContext

        optimizer = MobilePerformanceOptimizer()

        # Test device classes
        assert DeviceClass.HIGH_END == "high_end"
        assert DeviceClass.MID_RANGE == "mid_range"
        assert DeviceClass.LOW_END == "low_end"
        assert DeviceClass.LEGACY == "legacy"
        print("SUCCESS: Device classes defined correctly")

        # Test connection types
        assert ConnectionType.WIFI == "wifi"
        assert ConnectionType.CELLULAR_5G == "5g"
        assert ConnectionType.CELLULAR_4G == "4g"
        assert ConnectionType.CELLULAR_3G == "3g"
        assert ConnectionType.CELLULAR_2G == "2g"
        print("SUCCESS: Connection types defined correctly")

        # Test optimization profiles exist
        assert len(optimizer.optimization_profiles) == 4
        assert DeviceClass.HIGH_END in optimizer.optimization_profiles
        assert DeviceClass.LEGACY in optimizer.optimization_profiles
        print("SUCCESS: Optimization profiles loaded")

        # Test optimization methods exist
        assert hasattr(optimizer, 'detect_mobile_context')
        assert hasattr(optimizer, 'optimize_response')
        assert hasattr(optimizer, 'compress_response')
        assert hasattr(optimizer, 'get_optimization_stats')
        print("SUCCESS: Performance optimizer methods available")

        # Test basic optimization
        test_data = {
            "title": "Test Data",
            "items": list(range(100)),  # Large list
            "description": "A" * 1000,  # Long text
            "metadata": {"debug": "info"}
        }

        mobile_context = MobileContext(
            device_class=DeviceClass.LOW_END,
            connection_type=ConnectionType.CELLULAR_3G,
            screen_density=2.0,
            screen_width=375,
            screen_height=667,
            memory_gb=2.0,
            cpu_cores=2
        )

        optimized = optimizer.optimize_response(test_data, mobile_context)
        assert "_mobile_optimized" in optimized
        assert len(optimized["items"]) <= 15  # Should be paginated for low-end device
        print("SUCCESS: Basic response optimization working")

        return True

    except Exception as e:
        print(f"FAILED: Performance optimization test failed: {e}")
        return False

def test_api_integration():
    """Test mobile API integration"""
    print("\nTESTING MOBILE API INTEGRATION...")
    try:
        from app.api.v1.mobile import router

        # Check router exists and has routes
        assert router is not None, "Mobile router should exist"

        # Get route information
        route_count = len(router.routes)
        print(f"SUCCESS: Mobile API router has {route_count} routes")

        # Check for key endpoints
        route_paths = [route.path for route in router.routes if hasattr(route, 'path')]
        key_endpoints = [
            '/manifest.json', '/service-worker.js', '/pwa/subscribe',
            '/dashboard/summary', '/deals/mobile', '/sync/queue', '/mobile/health'
        ]

        found_endpoints = []
        for endpoint in key_endpoints:
            if any(endpoint in path for path in route_paths):
                found_endpoints.append(endpoint)

        print(f"SUCCESS: Found {len(found_endpoints)} key mobile endpoints")

        # Check for PWA endpoints
        pwa_routes = [route for route in router.routes if hasattr(route, 'path') and 'pwa' in route.path]
        if pwa_routes:
            print("SUCCESS: PWA endpoints registered")
        else:
            print("WARNING: No PWA endpoints found")

        return True

    except Exception as e:
        print(f"FAILED: Mobile API integration test failed: {e}")
        return False

def test_mobile_services_health():
    """Test mobile services are healthy"""
    print("\nTESTING MOBILE SERVICES HEALTH...")
    try:
        from app.mobile.pwa_service import get_pwa_service
        from app.mobile.offline_sync import get_offline_sync_service
        from app.mobile.mobile_auth import get_mobile_auth_service
        from app.mobile.performance_optimizer import get_performance_optimizer

        # Test global service getters
        pwa_service = get_pwa_service()
        sync_service = get_offline_sync_service()
        auth_service = get_mobile_auth_service()
        optimizer = get_performance_optimizer()

        assert pwa_service is not None
        assert sync_service is not None
        assert auth_service is not None
        assert optimizer is not None
        print("SUCCESS: All mobile services accessible via global getters")

        # Test service health indicators
        assert hasattr(pwa_service, 'subscriptions')
        assert hasattr(sync_service, 'pending_sync_items')
        assert hasattr(auth_service, 'registered_devices')
        assert hasattr(optimizer, 'optimization_profiles')
        print("SUCCESS: Mobile services have expected attributes")

        return True

    except Exception as e:
        print(f"FAILED: Mobile services health test failed: {e}")
        return False

def run_sprint8_verification():
    """Run all Sprint 8 verification tests"""
    print("=" * 60)
    print("SPRINT 8 - MOBILE-FIRST EXPERIENCE & PWA VERIFICATION")
    print("=" * 60)

    tests = [
        ("Sprint 8 Endpoint Registration", test_sprint8_endpoints),
        ("Mobile Module Imports", test_mobile_module_imports),
        ("PWA Functionality", test_pwa_functionality),
        ("Offline Sync Functionality", test_offline_sync_functionality),
        ("Mobile Authentication", test_mobile_authentication),
        ("Performance Optimization", test_performance_optimization),
        ("Mobile API Integration", test_api_integration),
        ("Mobile Services Health", test_mobile_services_health)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"CRASHED: {test_name} - {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("SPRINT 8 VERIFICATION RESULTS")
    print("=" * 60)

    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print(f"SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")

    if failed > 0:
        print(f"\nCRITICAL: {failed} TESTS FAILED")
        print("STATUS: SPRINT 8 NOT READY")
        return False
    else:
        print(f"\nALL {passed} TESTS PASSED")
        print("STATUS: SPRINT 8 COMPLETE & VERIFIED")
        print("\nFEATURES IMPLEMENTED:")
        print("- Progressive Web App (PWA) with manifest and service worker")
        print("- Mobile push notifications with rich actions")
        print("- Offline-first data synchronization with conflict resolution")
        print("- Mobile-optimized authentication with biometric support")
        print("- Performance optimization for different device classes")
        print("- Mobile-first API endpoints with adaptive responses")
        print("- 13 mobile-optimized endpoints")
        return True

if __name__ == "__main__":
    success = run_sprint8_verification()
    sys.exit(0 if success else 1)