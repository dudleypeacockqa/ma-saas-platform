#!/usr/bin/env python3
"""
Environment Resolution Test
Verifies that all critical environment and dependency issues have been resolved
"""

import os
import sys
from pathlib import Path

def test_environment_variables():
    """Test that required environment variables are available"""
    print("Testing environment variables...")

    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("[OK] dotenv loaded successfully")
    except ImportError:
        print("[FAIL] dotenv not available")
        return False

    # Check critical environment variables
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'STORAGE_PROVIDER',
        'ANTHROPIC_API_KEY',
        'CLERK_SECRET_KEY',
        'STRIPE_SECRET_KEY'
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"[OK] {var} is set")

    if missing_vars:
        print(f"[FAIL] Missing required environment variables: {missing_vars}")
        return False

    print("[OK] All required environment variables are set")
    return True

def test_dependencies():
    """Test that required dependencies are available"""
    print("\nTesting dependencies...")

    # Test core dependencies
    dependencies = [
        ('fastapi', 'FastAPI framework'),
        ('sqlalchemy', 'SQLAlchemy ORM'),
        ('pytest', 'Testing framework'),
        ('aiohttp', 'Async HTTP client'),
        ('anthropic', 'Claude API'),
        ('stripe', 'Stripe payments'),
    ]

    missing_deps = []
    for dep, description in dependencies:
        try:
            __import__(dep)
            print(f"[OK] {dep} ({description})")
        except ImportError:
            missing_deps.append(dep)
            print(f"[FAIL] {dep} ({description}) - MISSING")

    if missing_deps:
        print(f"[FAIL] Missing dependencies: {missing_deps}")
        return False

    print("[OK] All required dependencies are available")
    return True

def test_pytest_configuration():
    """Test pytest configuration and dotenv integration"""
    print("\nTesting pytest configuration...")

    try:
        import pytest
        print("[OK] pytest is available")
    except ImportError:
        print("[FAIL] pytest not available")
        return False

    # Check if pytest-dotenv is available
    try:
        import pytest_dotenv
        print("[OK] pytest-dotenv is available")
    except ImportError:
        print("[WARN] pytest-dotenv not available")
        # This is acceptable as we can install it dynamically
        pass

    return True

def test_app_import():
    """Test that the FastAPI app can be imported without configuration errors"""
    print("\nTesting FastAPI app import...")

    try:
        # Set minimal test environment
        os.environ.setdefault('DATABASE_URL', 'sqlite:///./test.db')
        os.environ.setdefault('SECRET_KEY', 'test-secret-key')
        os.environ.setdefault('STORAGE_PROVIDER', 'r2')

        from app.main_complete import app
        print("[OK] FastAPI app imported successfully")

        # Test that app is configured
        if hasattr(app, 'routes'):
            print(f"[OK] App has {len(app.routes)} routes configured")

        return True

    except Exception as e:
        print(f"[FAIL] Failed to import FastAPI app: {e}")
        return False

def main():
    """Run all environment resolution tests"""
    print("=" * 60)
    print("M&A SaaS Platform - Environment Resolution Test")
    print("=" * 60)

    tests = [
        test_environment_variables,
        test_dependencies,
        test_pytest_configuration,
        test_app_import
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[FAIL] Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Environment Resolution Test Results:")
    print(f"[OK] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")
    print("=" * 60)

    if failed == 0:
        print("SUCCESS: ALL ENVIRONMENT ISSUES RESOLVED!")
        print("Platform is ready for testing and deployment.")
        return 0
    else:
        print("WARNING: Some issues remain. Please review the failed tests above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())