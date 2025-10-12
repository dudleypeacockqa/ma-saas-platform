#!/usr/bin/env python3
"""
Sprint 20 - Critical Platform Stabilization Verification Script
Tests all fixes implemented in Sprint 20 and validates core platform functionality
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
        self.test_summary = {
            "sprint": "Sprint 20 - Critical Platform Stabilization",
            "verification_timestamp": datetime.utcnow().isoformat(),
            "test_results": {},
            "summary": {}
        }

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

        except Exception as e:
            self.results.append(test_result(
                "cultural_integration",
                "missing_method_fix",
                False,
                error=str(e)
            ))

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
                    timestamp=datetime.utcnow(),
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

        except Exception as e:
            self.results.append(test_result(
                "performance_optimization",
                "missing_method_fix",
                False,
                error=str(e)
            ))

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

        except Exception as e:
            self.results.append(test_result(
                "redis_config",
                "configuration_added",
                False,
                error=str(e)
            ))

        return {"status": "completed"}

    async def verify_core_imports(self) -> Dict[str, Any]:
        """Verify all core modules can be imported without errors"""
        print("📦 Testing Core Module Imports...")

        critical_modules = [
            "app.main",
            "app.core.config",
            "app.core.database",
            "app.models.base",
            "app.models.user",
            "app.models.organization",
            "app.models.deal",
            "app.api.deals",
            "app.api.users",
            "app.auth.clerk_auth"
        ]

        for module_name in critical_modules:
            try:
                module = importlib.import_module(module_name)
                self.results.append(test_result(
                    "core_imports",
                    f"import_{module_name.replace('.', '_')}",
                    True,
                    f"Successfully imported {module_name}"
                ))

            except Exception as e:
                self.results.append(test_result(
                    "core_imports",
                    f"import_{module_name.replace('.', '_')}",
                    False,
                    error=f"Failed to import {module_name}: {str(e)}"
                ))

        return {"status": "completed"}

    async def verify_database_models(self) -> Dict[str, Any]:
        """Verify database models are properly defined"""
        print("🗄️ Testing Database Models...")

        try:
            from app.models.base import Base
            from app.models import user, organization, deal

            # Test base model exists
            assert Base is not None, "Base model should exist"

            # Test critical models exist
            assert hasattr(user, 'User'), "User model should exist"
            assert hasattr(organization, 'Organization'), "Organization model should exist"
            assert hasattr(deal, 'Deal'), "Deal model should exist"

            self.results.append(test_result(
                "database_models",
                "model_definitions",
                True,
                "All critical models are properly defined"
            ))

        except Exception as e:
            self.results.append(test_result(
                "database_models",
                "model_definitions",
                False,
                error=str(e)
            ))

        return {"status": "completed"}

    async def verify_api_structure(self) -> Dict[str, Any]:
        """Verify API endpoints are properly structured"""
        print("🌐 Testing API Structure...")

        try:
            from app.main import app

            # Test FastAPI app exists
            assert app is not None, "FastAPI app should exist"

            # Test routes are registered
            routes = [route.path for route in app.routes]

            # Check for critical endpoints
            critical_endpoints = ["/", "/health"]
            missing_endpoints = [ep for ep in critical_endpoints if ep not in routes]

            if not missing_endpoints:
                self.results.append(test_result(
                    "api_structure",
                    "critical_endpoints",
                    True,
                    f"Found {len(routes)} total routes including all critical endpoints"
                ))
            else:
                self.results.append(test_result(
                    "api_structure",
                    "critical_endpoints",
                    False,
                    error=f"Missing endpoints: {missing_endpoints}"
                ))

        except Exception as e:
            self.results.append(test_result(
                "api_structure",
                "critical_endpoints",
                False,
                error=str(e)
            ))

        return {"status": "completed"}

    async def verify_authentication_setup(self) -> Dict[str, Any]:
        """Verify authentication components are properly set up"""
        print("🔐 Testing Authentication Setup...")

        try:
            from app.auth.clerk_auth import ClerkUser, get_current_user
            from app.auth.webhooks import router as webhook_router

            # Test Clerk components exist
            assert ClerkUser is not None, "ClerkUser should exist"
            assert get_current_user is not None, "get_current_user should exist"
            assert webhook_router is not None, "Webhook router should exist"

            self.results.append(test_result(
                "authentication",
                "clerk_components",
                True,
                "All Clerk authentication components are available"
            ))

        except Exception as e:
            self.results.append(test_result(
                "authentication",
                "clerk_components",
                False,
                error=str(e)
            ))

        return {"status": "completed"}

    async def verify_environment_configuration(self) -> Dict[str, Any]:
        """Verify environment configuration is complete"""
        print("⚙️ Testing Environment Configuration...")

        try:
            from app.core.config import settings

            # Critical settings that should exist
            critical_settings = [
                'DATABASE_URL',
                'REDIS_URL',
                'app_name',
                'debug',
                'allowed_origins'
            ]

            missing_settings = []
            for setting in critical_settings:
                if not hasattr(settings, setting):
                    missing_settings.append(setting)

            if not missing_settings:
                self.results.append(test_result(
                    "environment",
                    "critical_settings",
                    True,
                    f"All {len(critical_settings)} critical settings are configured"
                ))
            else:
                self.results.append(test_result(
                    "environment",
                    "critical_settings",
                    False,
                    error=f"Missing settings: {missing_settings}"
                ))

        except Exception as e:
            self.results.append(test_result(
                "environment",
                "critical_settings",
                False,
                error=str(e)
            ))

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
        print("🚀 Starting Sprint 20 Platform Stabilization Verification")
        print("=" * 60)

        # Run all verification tests
        await self.verify_integration_engine_fixes()
        await self.verify_redis_configuration()
        await self.verify_core_imports()
        await self.verify_database_models()
        await self.verify_api_structure()
        await self.verify_authentication_setup()
        await self.verify_environment_configuration()

        # Generate summary
        summary = self.generate_summary()

        # Store results
        self.test_summary["test_results"] = {result["component"]: result for result in self.results}
        self.test_summary["summary"] = summary

        # Display results
        self.display_results(summary)

        return self.test_summary

    def display_results(self, summary: Dict[str, Any]):
        """Display verification results"""
        print("\n" + "=" * 60)
        print("📊 SPRINT 20 VERIFICATION RESULTS")
        print("=" * 60)

        print(f"Overall Status: {'✅ PASSED' if summary['overall_status'] == 'PASSED' else '❌ FAILED'}")
        print(f"Success Rate: {summary['success_rate']}%")
        print(f"Tests: {summary['passed_tests']}/{summary['total_tests']} passed")
        print()

        # Component breakdown
        print("📋 Component Results:")
        for component, data in summary["component_breakdown"].items():
            status = "✅" if data["failed"] == 0 else "❌"
            print(f"  {status} {component}: {data['passed']}/{data['passed'] + data['failed']} tests passed")

            # Show failed tests
            if data["failed"] > 0:
                for test in data["tests"]:
                    if test["status"] == "FAILED":
                        print(f"    ❌ {test['test']}: {test['error']}")

        print("\n" + "=" * 60)

        if summary['overall_status'] == 'PASSED':
            print("🎉 Sprint 20 fixes have been successfully verified!")
            print("✅ Integration engine failures resolved")
            print("✅ Redis configuration added")
            print("✅ Core platform components functional")
        else:
            print("⚠️ Some issues remain to be addressed:")
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

        print(f"\n📄 Results saved to: sprint20_verification_results.json")

        # Return appropriate exit code
        return 0 if results["summary"]["overall_status"] == "PASSED" else 1

    except Exception as e:
        print(f"\n❌ Verification failed with error: {str(e)}")
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)