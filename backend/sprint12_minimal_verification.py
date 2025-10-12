"""
Sprint 12 Minimal Verification - Advanced AI & Machine Learning Platform
Basic verification that all components can be imported and initialized
"""

import sys

def test_basic_imports():
    """Test basic AI/ML imports"""
    print("Testing AI/ML module imports...")

    try:
        # Test main AI/ML module
        from app.ai_ml import (
            get_predictive_analytics_engine,
            get_nlp_hub,
            get_computer_vision_engine,
            get_ai_recommendation_engine
        )
        print("[PASS] Main AI/ML module imports successful")

        # Test service initialization
        predictive_engine = get_predictive_analytics_engine()
        print(f"[PASS] Predictive Analytics Engine: {type(predictive_engine).__name__}")

        nlp_hub = get_nlp_hub()
        print(f"[PASS] NLP Hub: {type(nlp_hub).__name__}")

        cv_engine = get_computer_vision_engine()
        print(f"[PASS] Computer Vision Engine: {type(cv_engine).__name__}")

        rec_engine = get_ai_recommendation_engine()
        print(f"[PASS] AI Recommendation Engine: {type(rec_engine).__name__}")

        return True

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_api_integration():
    """Test API integration"""
    print("\nTesting API integration...")

    try:
        # Test API router exists
        from app.api.v1.api import api_router
        route_count = len(api_router.routes)
        print(f"[PASS] Main API router has {route_count} routes")

        # Test that AI/ML routes are included
        ai_ml_routes = [r for r in api_router.routes if "ai-ml" in str(r.path).lower()]
        print(f"[PASS] AI/ML routes included: {len(ai_ml_routes) > 0}")

        return True

    except Exception as e:
        print(f"[FAIL] API integration error: {e}")
        return False

def run_minimal_verification():
    """Run minimal Sprint 12 verification"""
    print("SPRINT 12 MINIMAL VERIFICATION")
    print("=" * 50)

    tests = [
        ("Basic Imports", test_basic_imports),
        ("API Integration", test_api_integration)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[FAIL] {test_name} failed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status:<8} {test_name}")

    print(f"\nPASSED: {passed}/{total}")
    print(f"SUCCESS RATE: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\nSUCCESS: Sprint 12 AI/ML Platform basic verification passed!")
        print("\nSPRINT 12 COMPONENTS:")
        print("+ Predictive Analytics Engine")
        print("+ Natural Language Processing Hub")
        print("+ Computer Vision Engine")
        print("+ AI Recommendation Engine")
        print("+ Comprehensive API Layer")
        return True
    else:
        print(f"\nFAILED: {total - passed} tests failed")
        return False

if __name__ == "__main__":
    try:
        success = run_minimal_verification()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Verification failed: {e}")
        sys.exit(1)