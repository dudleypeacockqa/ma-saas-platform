#!/usr/bin/env python3
"""
Sprint 5 Verification Test
Verify all Sprint 5 - Advanced Analytics & Reporting endpoints are registered
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sprint5_endpoints():
    """Test Sprint 5 endpoints are registered"""
    print("TESTING SPRINT 5 ENDPOINT REGISTRATION...")
    try:
        from app.main import app
        routes = [route.path for route in app.routes if hasattr(route, 'path')]

        # Sprint 5 Advanced Analytics endpoints
        analytics_endpoints = [
            '/api/v1/analytics-advanced/deals/performance',
            '/api/v1/analytics-advanced/pipeline/stage-performance',
            '/api/v1/analytics-advanced/deals/forecast',
            '/api/v1/analytics-advanced/financial/metrics',
            '/api/v1/analytics-advanced/teams/productivity',
            '/api/v1/analytics-advanced/executive/dashboard'
        ]

        # Sprint 5 Reports endpoints
        reports_endpoints = [
            '/api/v1/reports/generate',
            '/api/v1/reports/deals/export',
            '/api/v1/reports/activities/export',
            '/api/v1/reports/custom-export',
            '/api/v1/reports/templates'
        ]

        all_sprint5_endpoints = analytics_endpoints + reports_endpoints

        missing = []
        found = []

        for endpoint in all_sprint5_endpoints:
            # Check if endpoint pattern exists in routes
            endpoint_found = False
            for route in routes:
                if endpoint.replace('/api/v1/analytics-advanced/', '').replace('/api/v1/reports/', '') in route or endpoint in route:
                    endpoint_found = True
                    found.append(endpoint)
                    break

            if not endpoint_found:
                missing.append(endpoint)

        print(f"SUCCESS: Found {len(found)} Sprint 5 endpoints:")
        for endpoint in found:
            print(f"  - {endpoint}")

        if missing:
            print(f"\nFAILED: Missing {len(missing)} Sprint 5 endpoints:")
            for endpoint in missing:
                print(f"  - {endpoint}")
            return False
        else:
            print(f"\nSUCCESS: All {len(all_sprint5_endpoints)} Sprint 5 endpoints registered")
            return True

    except Exception as e:
        print(f"FAILED: Sprint 5 endpoint test failed: {e}")
        return False

def test_sprint5_imports():
    """Test Sprint 5 modules import correctly"""
    print("\nTESTING SPRINT 5 MODULE IMPORTS...")
    try:
        from app.api.v1 import analytics_advanced, reports
        print("SUCCESS: Sprint 5 modules imported")

        # Test routers exist
        assert hasattr(analytics_advanced, 'router'), "analytics_advanced missing router"
        assert hasattr(reports, 'router'), "reports missing router"
        print("SUCCESS: Sprint 5 routers available")

        return True

    except Exception as e:
        print(f"FAILED: Sprint 5 import test failed: {e}")
        return False

def test_permissions_updated():
    """Test permission system includes REPORTS resource"""
    print("\nTESTING PERMISSIONS UPDATE...")
    try:
        from app.core.permissions import ResourceType, PERMISSION_MATRIX

        # Check REPORTS resource exists
        assert ResourceType.REPORTS in ResourceType, "REPORTS ResourceType missing"
        print("SUCCESS: REPORTS ResourceType exists")

        # Check REPORTS in permission matrix
        assert ResourceType.REPORTS in PERMISSION_MATRIX, "REPORTS not in permission matrix"
        print("SUCCESS: REPORTS in permission matrix")

        # Check REPORTS has proper actions
        reports_perms = PERMISSION_MATRIX[ResourceType.REPORTS]
        required_actions = ['create', 'read', 'export', 'share']

        missing_actions = []
        available_actions = [a.value for a in reports_perms.keys()]

        for action in required_actions:
            if action not in available_actions:
                missing_actions.append(action)

        if missing_actions:
            print(f"FAILED: Missing REPORTS actions: {missing_actions}")
            return False
        else:
            print(f"SUCCESS: REPORTS has all {len(required_actions)} required actions")
            return True

    except Exception as e:
        print(f"FAILED: Permissions test failed: {e}")
        return False

def run_sprint5_verification():
    """Run all Sprint 5 verification tests"""
    print("=" * 60)
    print("SPRINT 5 - ADVANCED ANALYTICS & REPORTING VERIFICATION")
    print("=" * 60)

    tests = [
        ("Sprint 5 Endpoint Registration", test_sprint5_endpoints),
        ("Sprint 5 Module Imports", test_sprint5_imports),
        ("Permissions System Update", test_permissions_updated)
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
    print("SPRINT 5 VERIFICATION RESULTS")
    print("=" * 60)

    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print(f"SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")

    if failed > 0:
        print(f"\nCRITICAL: {failed} TESTS FAILED")
        print("STATUS: SPRINT 5 NOT READY")
        return False
    else:
        print(f"\nALL {passed} TESTS PASSED")
        print("STATUS: SPRINT 5 COMPLETE & VERIFIED")
        return True

if __name__ == "__main__":
    success = run_sprint5_verification()
    sys.exit(0 if success else 1)