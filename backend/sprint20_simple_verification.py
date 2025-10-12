#!/usr/bin/env python3
"""
Sprint 20 - Critical Platform Stabilization Verification Script (Simple)
Tests fixes implemented in Sprint 20 - no Unicode characters for Windows compatibility
"""

import os
import sys
import json
import asyncio
import traceback
from datetime import datetime
from typing import Dict, Any, List
import importlib.util

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_result(component: str, test_name: str, success: bool, details: str = "", error: str = ""):
    """Create consistent test result format"""
    return {
        "component": component,
        "test": test_name,
        "status": "PASSED" if success else "FAILED",
        "details": details,
        "error": error
    }

class Sprint20Verifier:
    def __init__(self):
        self.results = []

    async def verify_integration_engine_fixes(self) -> Dict[str, Any]:
        """Verify the integration engine fixes from Sprint 17 failures"""
        print("[INFO] Testing Integration Engine Fixes...")

        # Test 1: Cultural Integration Manager
        try:
            from app.integration_platform.cultural_integration import (
                CulturalIntegrationManager,
                get_cultural_integration_manager,
                CulturalDimension,
                CulturalProfile
            )

            manager = get_cultural_integration_manager()

            # Test the previously missing method exists
            assert hasattr(manager, '_generate_integration_recommendations'), \
                "Missing _generate_integration_recommendations method"

            # Test method can be called (basic functionality test)
            dimension_gaps = {CulturalDimension.COMMUNICATION_STYLE: 0.5}
            risk_areas = [CulturalDimension.COMMUNICATION_STYLE]

            recommendations = await manager._generate_integration_recommendations(dimension_gaps, risk_areas)
            assert isinstance(recommendations, list), "Recommendations should be a list"
            assert len(recommendations) > 0, "Should generate recommendations for risk areas"

            self.results.append(test_result(
                "cultural_integration",
                "missing_method_fix",
                True,
                f"Generated {len(recommendations)} recommendations successfully"
            ))
            print(f"[PASS] Cultural Integration Manager - Generated {len(recommendations)} recommendations")

        except Exception as e:
            self.results.append(test_result(
                "cultural_integration",
                "missing_method_fix",
                False,
                error=str(e)
            ))
            print(f"[FAIL] Cultural Integration Manager: {str(e)}")

        # Test 2: Performance Optimization Manager
        try:
            from app.integration_platform.performance_optimization import (
                PerformanceTracker,
                PerformanceDataPoint,
                PerformanceMetric
            )

            tracker = PerformanceTracker()

            # Test the previously missing method exists
            assert hasattr(tracker, '_calculate_trend_confidence'), \
                "Missing _calculate_trend_confidence method"

            # Test method can be called
            sample_data = [
                PerformanceDataPoint(
                    metric=PerformanceMetric.INTEGRATION_VELOCITY,
                    value=0.8,
                    timestamp=datetime.now(),
                    integration_id="test_integration",
                    confidence=0.9
                )
            ]

            confidence = tracker._calculate_trend_confidence(sample_data)
            assert isinstance(confidence, (int, float)), "Confidence should be numeric"
            assert 0 <= confidence <= 1, "Confidence should be between 0 and 1"

            self.results.append(test_result(
                "performance_optimization",
                "missing_method_fix",
                True,
                f"Calculated trend confidence: {confidence:.3f}"
            ))
            print(f"[PASS] Performance Optimization Manager - Trend confidence: {confidence:.3f}")

        except Exception as e:
            self.results.append(test_result(
                "performance_optimization",
                "missing_method_fix",
                False,
                error=str(e)
            ))
            print(f"[FAIL] Performance Optimization Manager: {str(e)}")

        return {"status": "completed", "tests_run": len(self.results)}

    async def verify_redis_configuration(self) -> Dict[str, Any]:
        """Verify Redis configuration has been added"""
        print("[INFO] Testing Redis Configuration...")

        try:
            from app.core.config import settings

            # Test Redis URL setting exists
            assert hasattr(settings, 'REDIS_URL'), "Missing REDIS_URL setting"
            assert hasattr(settings, 'redis_url'), "Missing redis_url legacy setting"

            # Test default value is set
            assert settings.REDIS_URL is not None, "REDIS_URL should have a default value"
            assert 'redis://' in settings.REDIS_URL, "REDIS_URL should be a Redis URL"

            self.results.append(test_result(
                "redis_config",
                "configuration_added",
                True,
                f"Redis URL configured: {settings.REDIS_URL}"
            ))
            print(f"[PASS] Redis Configuration - URL: {settings.REDIS_URL}")

        except Exception as e:
            self.results.append(test_result(
                "redis_config",
                "configuration_added",
                False,
                error=str(e)
            ))
            print(f"[FAIL] Redis Configuration: {str(e)}")

        return {"status": "completed"}

    async def verify_core_imports(self) -> Dict[str, Any]:
        """Verify all core modules can be imported without errors"""
        print("[INFO] Testing Core Module Imports...")

        critical_modules = [
            "app.main",
            "app.core.config",
            "app.core.database",
            "app.models.base"
        ]

        import_success = 0
        for module_name in critical_modules:
            try:
                module = importlib.import_module(module_name)
                self.results.append(test_result(
                    "core_imports",
                    f"import_{module_name.replace('.', '_')}",
                    True,
                    f"Successfully imported {module_name}"
                ))
                import_success += 1
                print(f"[PASS] Import {module_name}")

            except Exception as e:
                self.results.append(test_result(
                    "core_imports",
                    f"import_{module_name.replace('.', '_')}",
                    False,
                    error=f"Failed to import {module_name}: {str(e)}"
                ))
                print(f"[FAIL] Import {module_name}: {str(e)}")

        print(f"[INFO] Core imports: {import_success}/{len(critical_modules)} successful")
        return {"status": "completed"}

    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "PASSED"])
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Group results by component
        components = {}
        for result in self.results:
            component = result["component"]
            if component not in components:
                components[component] = {"passed": 0, "failed": 0, "tests": []}

            if result["status"] == "PASSED":
                components[component]["passed"] += 1
            else:
                components[component]["failed"] += 1
            components[component]["tests"].append(result)

        summary = {
            "total_components": len(components),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": round(success_rate, 2),
            "component_breakdown": components,
            "overall_status": "PASSED" if failed_tests == 0 else "FAILED"
        }

        return summary

    async def run_verification(self) -> Dict[str, Any]:
        """Run all verification tests"""
        print("=" * 60)
        print("SPRINT 20 PLATFORM STABILIZATION VERIFICATION")
        print("=" * 60)

        # Run all verification tests
        await self.verify_integration_engine_fixes()
        await self.verify_redis_configuration()
        await self.verify_core_imports()

        # Generate summary
        summary = self.generate_summary()

        # Display results
        self.display_results(summary)

        return {
            "sprint": "Sprint 20 - Critical Platform Stabilization",
            "verification_timestamp": datetime.now().isoformat(),
            "test_results": {result["component"]: result for result in self.results},
            "summary": summary
        }

    def display_results(self, summary: Dict[str, Any]):
        """Display verification results"""
        print("\n" + "=" * 60)
        print("SPRINT 20 VERIFICATION RESULTS")
        print("=" * 60)

        overall_status = "PASSED" if summary['overall_status'] == 'PASSED' else "FAILED"
        print(f"Overall Status: {overall_status}")
        print(f"Success Rate: {summary['success_rate']}%")
        print(f"Tests: {summary['passed_tests']}/{summary['total_tests']} passed")
        print()

        # Component breakdown
        print("Component Results:")
        for component, data in summary["component_breakdown"].items():
            status = "PASS" if data["failed"] == 0 else "FAIL"
            print(f"  [{status}] {component}: {data['passed']}/{data['passed'] + data['failed']} tests passed")

            # Show failed tests
            if data["failed"] > 0:
                for test in data["tests"]:
                    if test["status"] == "FAILED":
                        print(f"    [FAIL] {test['test']}: {test['error']}")

        print("\n" + "=" * 60)

        if summary['overall_status'] == 'PASSED':
            print("SUCCESS: Sprint 20 fixes have been successfully verified!")
            print("- Integration engine failures resolved")
            print("- Redis configuration added")
            print("- Core platform components functional")
        else:
            print("WARNING: Some issues remain to be addressed:")
            failed_components = [comp for comp, data in summary["component_breakdown"].items() if data["failed"] > 0]
            for comp in failed_components:
                print(f"   - {comp} has failures")

async def main():
    """Main verification runner"""
    verifier = Sprint20Verifier()

    try:
        results = await verifier.run_verification()

        # Save results to file
        with open("sprint20_verification_results.json", "w") as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: sprint20_verification_results.json")

        # Return appropriate exit code
        return 0 if results["summary"]["overall_status"] == "PASSED" else 1

    except Exception as e:
        print(f"\nERROR: Verification failed with error: {str(e)}")
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)