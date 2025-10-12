"""
Sprint 10 Simple Verification Test
Basic functionality test for enterprise features
"""

import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_enterprise_imports():
    """Test that all enterprise modules can be imported"""
    try:
        from app.enterprise import (
            get_integrations_hub, get_enterprise_admin_service,
            get_performance_manager, get_business_intelligence_service
        )
        print("PASS - Enterprise modules imported successfully")
        return True
    except Exception as e:
        print(f"FAIL - Import failed: {e}")
        return False

def test_service_initialization():
    """Test that all services can be initialized"""
    try:
        from app.enterprise import (
            get_integrations_hub, get_enterprise_admin_service,
            get_performance_manager, get_business_intelligence_service
        )

        # Initialize all services
        hub = get_integrations_hub()
        admin = get_enterprise_admin_service()
        perf = get_performance_manager()
        bi = get_business_intelligence_service()

        print("PASS - All enterprise services initialized successfully")
        return True
    except Exception as e:
        print(f"FAIL - Service initialization failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of each service"""
    try:
        from app.enterprise import (
            get_integrations_hub, get_enterprise_admin_service,
            get_performance_manager, get_business_intelligence_service,
            MetricType
        )

        # Test business intelligence
        bi = get_business_intelligence_service()
        metric_id = bi.track_business_metric(
            name="test_metric",
            value=100.0,
            unit="USD",
            metric_type=MetricType.FINANCIAL,
            organization_id="test_org"
        )

        if metric_id:
            print("PASS - Business intelligence metric tracking works")
        else:
            print("FAIL - Business intelligence metric tracking failed")
            return False

        # Test performance manager
        perf = get_performance_manager()
        if hasattr(perf, 'cache_manager') and hasattr(perf, 'queue_manager'):
            print("PASS - Performance manager components available")
        else:
            print("FAIL - Performance manager missing components")
            return False

        # Test enterprise admin
        admin = get_enterprise_admin_service()
        if hasattr(admin, 'compliance_manager'):
            print("PASS - Enterprise admin compliance manager available")
        else:
            print("FAIL - Enterprise admin missing compliance manager")
            return False

        # Test integrations hub
        hub = get_integrations_hub()
        if hasattr(hub, 'active_integrations') and hasattr(hub, 'connectors'):
            print("PASS - Integrations hub components available")
        else:
            print("FAIL - Integrations hub missing components")
            return False

        return True
    except Exception as e:
        print(f"FAIL - Basic functionality test failed: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints can be imported"""
    try:
        from app.api.v1 import enterprise
        if hasattr(enterprise, 'router'):
            print("PASS - Enterprise API endpoints available")
            return True
        else:
            print("FAIL - Enterprise API router not found")
            return False
    except Exception as e:
        print(f"FAIL - API endpoints test failed: {e}")
        return False

def main():
    """Run all simple verification tests"""
    print("Sprint 10 Enterprise Features - Simple Verification")
    print("=" * 55)

    tests = [
        ("Import Test", test_enterprise_imports),
        ("Service Initialization", test_service_initialization),
        ("Basic Functionality", test_basic_functionality),
        ("API Endpoints", test_api_endpoints)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1

    print(f"\nSummary:")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\nSprint 10 Enterprise Features: Basic verification PASSED!")
        print("All core components are working correctly")
        return True
    else:
        print(f"\n{total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)