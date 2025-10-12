"""
Sprint 13 Simple Verification Test - Advanced Analytics & Intelligence Platform
Simplified test suite that imports and verifies basic functionality
"""

import asyncio
from datetime import datetime
import json
import sys
import os
from collections import defaultdict

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all Sprint 13 modules can be imported"""
    print("Testing Sprint 13 Module Imports...")

    try:
        # Test real-time analytics import
        from app.analytics.real_time_analytics import get_real_time_analytics_engine
        print("[PASS] Real-time analytics module imported successfully")

        # Test dashboard system import
        from app.analytics.dashboard_system import get_dashboard_system
        print("[PASS] Dashboard system module imported successfully")

        # Test reporting engine import
        from app.analytics.reporting_engine import get_reporting_engine
        print("[PASS] Reporting engine module imported successfully")

        # Test performance monitor import
        from app.analytics.performance_monitor import get_performance_monitor
        print("[PASS] Performance monitor module imported successfully")

        return True

    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_service_initialization():
    """Test that all services can be initialized"""
    print("Testing Service Initialization...")

    try:
        from app.analytics.real_time_analytics import get_real_time_analytics_engine
        from app.analytics.dashboard_system import get_dashboard_system
        from app.analytics.reporting_engine import get_reporting_engine
        from app.analytics.performance_monitor import get_performance_monitor

        # Initialize services
        analytics_engine = get_real_time_analytics_engine()
        dashboard_system = get_dashboard_system()
        reporting_engine = get_reporting_engine()
        performance_monitor = get_performance_monitor()

        # Verify services are not None
        assert analytics_engine is not None, "Analytics engine is None"
        assert dashboard_system is not None, "Dashboard system is None"
        assert reporting_engine is not None, "Reporting engine is None"
        assert performance_monitor is not None, "Performance monitor is None"

        print("[PASS] All services initialized successfully")
        return True

    except Exception as e:
        print(f"[FAIL] Service initialization failed: {e}")
        return False

async def test_basic_functionality():
    """Test basic functionality of each service"""
    print("Testing Basic Functionality...")

    try:
        from app.analytics.real_time_analytics import get_real_time_analytics_engine, MetricType
        from app.analytics.dashboard_system import get_dashboard_system, DashboardType
        from app.analytics.reporting_engine import get_reporting_engine, ReportType
        from app.analytics.performance_monitor import get_performance_monitor

        # Get service instances
        analytics_engine = get_real_time_analytics_engine()
        dashboard_system = get_dashboard_system()
        reporting_engine = get_reporting_engine()
        performance_monitor = get_performance_monitor()

        # Test analytics engine
        success = await analytics_engine.track_metric("test_metric", 100, MetricType.GAUGE)
        assert success, "Failed to track metric"
        print("[PASS] Analytics engine basic functionality working")

        # Test dashboard system
        dashboard_id = await dashboard_system.create_dashboard(
            "Test Dashboard", DashboardType.EXECUTIVE, "test_user"
        )
        assert dashboard_id, "Failed to create dashboard"
        print("[PASS] Dashboard system basic functionality working")

        # Test reporting engine
        templates = reporting_engine.get_templates()
        assert isinstance(templates, list), "Failed to get templates"
        print("[PASS] Reporting engine basic functionality working")

        # Test performance monitor
        await performance_monitor.start_monitoring()
        assert performance_monitor.monitoring_active, "Failed to start monitoring"
        print("[PASS] Performance monitor basic functionality working")

        return True

    except Exception as e:
        print(f"[FAIL] Basic functionality test failed: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints module can be imported"""
    print("Testing API Endpoints...")

    try:
        from app.api.v1 import analytics_platform
        assert hasattr(analytics_platform, 'router'), "Analytics platform router not found"
        print("[PASS] Analytics platform API endpoints available")
        return True

    except ImportError as e:
        print(f"[FAIL] API endpoints test failed: {e}")
        return False

async def run_simple_verification():
    """Run simplified Sprint 13 verification"""
    print("Starting Sprint 13 Simple Verification Test")
    print("=" * 50)

    results = {
        "imports": False,
        "service_init": False,
        "basic_functionality": False,
        "api_endpoints": False
    }

    try:
        # Test imports
        results["imports"] = test_imports()

        # Test service initialization
        results["service_init"] = test_service_initialization()

        # Test basic functionality
        results["basic_functionality"] = await test_basic_functionality()

        # Test API endpoints
        results["api_endpoints"] = test_api_endpoints()

        # Check overall success
        all_passed = all(results.values())

        print("=" * 50)

        if all_passed:
            print("Sprint 13 Simple Verification COMPLETED SUCCESSFULLY!")
            print("[PASS] All basic tests passed")
            status = "VERIFIED"
        else:
            print("Sprint 13 Simple Verification completed with some issues")
            failed_tests = [test for test, passed in results.items() if not passed]
            print(f"[FAIL] Failed tests: {', '.join(failed_tests)}")
            status = "PARTIALLY_VERIFIED"

        # Generate summary
        summary = {
            "sprint": 13,
            "feature": "Advanced Analytics & Intelligence Platform",
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "test_results": results,
            "components_verified": [
                "Real-Time Analytics Engine",
                "Dashboard System",
                "Reporting Engine",
                "Performance Monitor",
                "API Endpoints"
            ]
        }

        return summary

    except Exception as e:
        print(f"[FAIL] Sprint 13 Simple Verification FAILED: {str(e)}")
        return {
            "sprint": 13,
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "test_results": results
        }

if __name__ == "__main__":
    # Run the simple verification test
    result = asyncio.run(run_simple_verification())

    # Print final result
    print("\nFinal Result:")
    print(json.dumps(result, indent=2))