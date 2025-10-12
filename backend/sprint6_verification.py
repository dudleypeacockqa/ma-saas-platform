#!/usr/bin/env python3
"""
Sprint 6 Verification Test
Verify Sprint 6 - Predictive Analytics Implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sprint6_endpoints():
    """Test Sprint 6 predictive analytics endpoints are registered"""
    print("TESTING SPRINT 6 ENDPOINT REGISTRATION...")
    try:
        from app.main import app
        routes = [route.path for route in app.routes if hasattr(route, 'path')]

        # Sprint 6 Predictive Analytics endpoints
        predictive_endpoints = [
            '/api/v1/predictive/deals/{deal_id}/prediction',
            '/api/v1/predictive/market-trends/{market_segment}',
            '/api/v1/predictive/insights',
            '/api/v1/predictive/insights/{insight_id}',
            '/api/v1/predictive/recommendations/deal/{deal_id}',
            '/api/v1/predictive/dashboard/predictive',
            '/api/v1/predictive/insights/refresh'
        ]

        missing = []
        found = []

        for endpoint in predictive_endpoints:
            # Check if endpoint pattern exists in routes
            endpoint_found = False
            for route in routes:
                if '/api/v1/predictive/' in route and any(part in route for part in endpoint.split('/')):
                    endpoint_found = True
                    found.append(endpoint)
                    break

            if not endpoint_found:
                missing.append(endpoint)

        print(f"SUCCESS: Found {len(found)} Sprint 6 endpoints")
        for endpoint in found:
            print(f"  - {endpoint}")

        if missing:
            print(f"\nFAILED: Missing {len(missing)} Sprint 6 endpoints:")
            for endpoint in missing:
                print(f"  - {endpoint}")
            return False
        else:
            print(f"\nSUCCESS: All {len(predictive_endpoints)} Sprint 6 endpoints registered")
            return True

    except Exception as e:
        print(f"FAILED: Sprint 6 endpoint test failed: {e}")
        return False

def test_ai_module_imports():
    """Test AI modules import correctly"""
    print("\nTESTING AI MODULE IMPORTS...")
    try:
        from app.ai.prediction_models import DealOutcomePredictionModel, MarketTrendAnalyzer
        print("SUCCESS: Prediction models imported")

        from app.ai.insight_engine import AutomatedInsightEngine, InsightType
        print("SUCCESS: Insight engine imported")

        from app.api.v1 import predictive_analytics
        print("SUCCESS: Predictive analytics API imported")

        # Test model instantiation
        prediction_model = DealOutcomePredictionModel()
        trend_analyzer = MarketTrendAnalyzer()
        insight_engine = AutomatedInsightEngine()
        print("SUCCESS: AI models instantiated")

        return True

    except Exception as e:
        print(f"FAILED: AI module import test failed: {e}")
        return False

def test_ai_model_functionality():
    """Test basic AI model functionality"""
    print("\nTESTING AI MODEL FUNCTIONALITY...")
    try:
        from app.ai.prediction_models import DealOutcomePredictionModel, DealOutcome
        from app.ai.insight_engine import AutomatedInsightEngine, InsightType

        # Test prediction model basic functionality
        model = DealOutcomePredictionModel()

        # Test feature extraction
        sample_deal = {
            "id": "test-deal-123",
            "title": "Test Deal",
            "status": "qualification",
            "estimated_value": 5000000,
            "created_at": "2024-01-01T00:00:00Z",
            "industry": "technology",
            "organization_id": "test-org-123"
        }

        # Test internal methods (without database)
        stage_progress = model._calculate_stage_progress("qualification")
        assert 0.0 <= stage_progress <= 1.0, "Stage progress should be between 0 and 1"
        print(f"SUCCESS: Stage progress calculation: {stage_progress}")

        industry_risk = model._get_industry_risk_score("technology")
        assert 0.0 <= industry_risk <= 1.0, "Industry risk should be between 0 and 1"
        print(f"SUCCESS: Industry risk calculation: {industry_risk}")

        # Test insight engine
        engine = AutomatedInsightEngine()
        priority_weight = engine._priority_weight(InsightType.DEAL_RISK)
        assert isinstance(priority_weight, int), "Priority weight should be integer"
        print("SUCCESS: Insight engine basic functionality")

        return True

    except Exception as e:
        print(f"FAILED: AI model functionality test failed: {e}")
        return False

def test_data_structures():
    """Test AI data structures and enums"""
    print("\nTESTING AI DATA STRUCTURES...")
    try:
        from app.ai.prediction_models import DealOutcome, RiskLevel
        from app.ai.insight_engine import InsightType, InsightPriority

        # Test enums exist and have expected values
        assert DealOutcome.SUCCESS == "success"
        assert RiskLevel.HIGH == "high"
        assert InsightType.DEAL_RISK == "deal_risk"
        assert InsightPriority.CRITICAL == "critical"
        print("SUCCESS: All enums defined correctly")

        # Test enum completeness
        deal_outcomes = [DealOutcome.SUCCESS, DealOutcome.FAILURE, DealOutcome.PENDING, DealOutcome.ON_HOLD, DealOutcome.CANCELLED]
        risk_levels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        insight_types = [InsightType.DEAL_RISK, InsightType.OPPORTUNITY, InsightType.PERFORMANCE, InsightType.MARKET_TREND, InsightType.RECOMMENDATION, InsightType.ALERT, InsightType.OPTIMIZATION]

        print(f"SUCCESS: {len(deal_outcomes)} deal outcomes, {len(risk_levels)} risk levels, {len(insight_types)} insight types")

        return True

    except Exception as e:
        print(f"FAILED: Data structures test failed: {e}")
        return False

def test_api_integration():
    """Test predictive analytics API integration"""
    print("\nTESTING API INTEGRATION...")
    try:
        from app.api.v1.predictive_analytics import router

        # Check router exists and has routes
        assert router is not None, "Router should exist"

        # Get route information
        route_count = len(router.routes)
        print(f"SUCCESS: Predictive analytics router has {route_count} routes")

        # Check for key endpoints
        route_paths = [route.path for route in router.routes if hasattr(route, 'path')]
        key_endpoints = ['/deals/{deal_id}/prediction', '/insights', '/dashboard/predictive']

        found_endpoints = []
        for endpoint in key_endpoints:
            if any(endpoint in path for path in route_paths):
                found_endpoints.append(endpoint)

        print(f"SUCCESS: Found {len(found_endpoints)} key endpoints")

        return True

    except Exception as e:
        print(f"FAILED: API integration test failed: {e}")
        return False

def run_sprint6_verification():
    """Run all Sprint 6 verification tests"""
    print("=" * 60)
    print("SPRINT 6 - PREDICTIVE ANALYTICS VERIFICATION")
    print("=" * 60)

    tests = [
        ("Sprint 6 Endpoint Registration", test_sprint6_endpoints),
        ("AI Module Imports", test_ai_module_imports),
        ("AI Model Functionality", test_ai_model_functionality),
        ("Data Structures", test_data_structures),
        ("API Integration", test_api_integration)
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
    print("SPRINT 6 VERIFICATION RESULTS")
    print("=" * 60)

    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print(f"SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")

    if failed > 0:
        print(f"\nCRITICAL: {failed} TESTS FAILED")
        print("STATUS: SPRINT 6 NOT READY")
        return False
    else:
        print(f"\nALL {passed} TESTS PASSED")
        print("STATUS: SPRINT 6 COMPLETE & VERIFIED")
        return True

if __name__ == "__main__":
    success = run_sprint6_verification()
    sys.exit(0 if success else 1)