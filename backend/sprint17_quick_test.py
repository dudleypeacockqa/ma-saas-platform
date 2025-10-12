"""
Quick Sprint 17 Verification Test - Advanced Post-Merger Integration & Value Creation Platform
Quick verification of all Sprint 17 components
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all Sprint 17 modules can be imported"""

    print("Testing Sprint 17 imports...")

    try:
        # Test integration platform imports
        from app.integration_platform import (
            get_integration_engine,
            get_synergy_manager,
            get_cultural_integration_manager,
            get_performance_optimizer
        )
        print("  Integration platform imports: PASSED")

        # Test API imports
        from app.api.v1 import integration_platform
        from app.api.v1.api import api_router
        print("  API integration imports: PASSED")

        # Test individual modules
        from app.integration_platform.integration_engine import IntegrationEngine
        from app.integration_platform.synergy_management import SynergyManager
        from app.integration_platform.cultural_integration import CulturalIntegrationManager
        from app.integration_platform.performance_optimization import PerformanceOptimizer
        print("  Individual module imports: PASSED")

        return True

    except Exception as e:
        print(f"  Import test FAILED: {e}")
        return False

def test_service_instances():
    """Test that service instances can be created"""

    print("Testing service instance creation...")

    try:
        from app.integration_platform import (
            get_integration_engine,
            get_synergy_manager,
            get_cultural_integration_manager,
            get_performance_optimizer
        )

        # Test singleton instances
        engine1 = get_integration_engine()
        engine2 = get_integration_engine()
        assert engine1 is engine2, "Integration engine not singleton"

        synergy1 = get_synergy_manager()
        synergy2 = get_synergy_manager()
        assert synergy1 is synergy2, "Synergy manager not singleton"

        cultural1 = get_cultural_integration_manager()
        cultural2 = get_cultural_integration_manager()
        assert cultural1 is cultural2, "Cultural manager not singleton"

        performance1 = get_performance_optimizer()
        performance2 = get_performance_optimizer()
        assert performance1 is performance2, "Performance optimizer not singleton"

        print("  Service instance creation: PASSED")
        return True

    except Exception as e:
        print(f"  Service instance test FAILED: {e}")
        return False

def test_api_router():
    """Test that API router includes integration platform"""

    print("Testing API router configuration...")

    try:
        from app.api.v1.api import api_router

        # Check if integration platform router is included
        integration_routes = []
        for route in api_router.routes:
            if hasattr(route, 'path') and '/integration' in route.path:
                integration_routes.append(route.path)

        assert len(integration_routes) > 0, "No integration routes found"
        print(f"  Found {len(integration_routes)} integration routes")
        print("  API router configuration: PASSED")
        return True

    except Exception as e:
        print(f"  API router test FAILED: {e}")
        return False

def main():
    """Run quick verification tests"""

    print("=" * 60)
    print("Sprint 17 Quick Verification Test")
    print("=" * 60)

    tests = [
        test_imports,
        test_service_instances,
        test_api_router
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 60)
    print("RESULTS:")
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total*100):.1f}%")

    if passed == total:
        print("ALL TESTS PASSED! Sprint 17 basic verification successful.")
    else:
        print(f"SOME TESTS FAILED! {total-passed} test(s) failed.")

    print("=" * 60)

    # Test basic functionality without async
    print("\nTesting basic class instantiation...")
    try:
        from app.integration_platform.integration_engine import IntegrationEngine
        from app.integration_platform.synergy_management import SynergyManager
        from app.integration_platform.cultural_integration import CulturalIntegrationManager
        from app.integration_platform.performance_optimization import PerformanceOptimizer

        engine = IntegrationEngine()
        synergy = SynergyManager()
        cultural = CulturalIntegrationManager()
        performance = PerformanceOptimizer()

        print("  Class instantiation: PASSED")

        # Test enum imports
        from app.integration_platform.integration_engine import IntegrationType, MilestoneStatus
        from app.integration_platform.synergy_management import SynergyType, SynergyStatus
        from app.integration_platform.cultural_integration import CulturalDimension, SentimentScore
        from app.integration_platform.performance_optimization import PerformanceMetric, OptimizationCategory

        print("  Enum imports: PASSED")

        print("\nSprint 17 components successfully loaded and instantiated!")

    except Exception as e:
        print(f"  Basic functionality test FAILED: {e}")

if __name__ == "__main__":
    main()