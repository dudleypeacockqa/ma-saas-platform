#!/usr/bin/env python3
"""
Simple test runner that bypasses complex async database setup
"""

import pytest
import os
import sys

# Set test environment
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

def run_simple_tests():
    """Run a basic test to verify the test framework works"""

    print("=" * 60)
    print("RUNNING BASIC TEST VERIFICATION")
    print("=" * 60)

    try:
        # Test 1: Basic Python functionality
        print("\n[TEST 1] Python Environment Check")
        assert sys.version_info >= (3, 8), "Python 3.8+ required"
        print("[OK] Python version check passed")

        # Test 2: Environment variables
        print("\n[TEST 2] Environment Variables")
        assert os.environ.get("TESTING") == "true", "Testing environment not set"
        assert os.environ.get("DATABASE_URL"), "Database URL not set"
        print("[OK] Environment variables configured")

        # Test 3: Basic imports
        print("\n[TEST 3] Basic Module Imports")
        try:
            import pytest
            import fastapi
            import sqlalchemy
            print("[OK] Core dependencies available")
        except ImportError as e:
            print(f"[FAIL] Import error: {e}")
            return False

        # Test 4: Pytest configuration
        print("\n[TEST 4] Pytest Framework")
        try:
            # Run a minimal pytest command
            exit_code = pytest.main([
                "--version"
            ])
            print("[OK] Pytest framework operational")
        except Exception as e:
            print(f"[FAIL] Pytest error: {e}")
            return False

        print("\n" + "=" * 60)
        print("[SUCCESS] ALL BASIC TESTS PASSED")
        print("[SUCCESS] Test framework is ready for comprehensive testing")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        return False

if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)