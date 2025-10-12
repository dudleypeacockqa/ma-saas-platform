#!/usr/bin/env python3
"""
Critical Issues Check
Identify and document all critical issues that need attention
"""

import sys
import os
import requests
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_server_health():
    """Check if server is responding properly"""
    print("CHECKING SERVER HEALTH...")
    try:
        # Test basic endpoints
        base_url = "http://127.0.0.1:8000"

        # Check root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code != 200:
            print(f"CRITICAL: Root endpoint failed - Status {response.status_code}")
            return False

        # Check health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"CRITICAL: Health endpoint failed - Status {response.status_code}")
            return False

        health_data = response.json()
        print(f"Server Status: {health_data.get('status', 'unknown')}")
        print(f"Clerk Configured: {health_data.get('clerk_configured', False)}")
        print(f"Database Configured: {health_data.get('database_configured', False)}")
        print(f"Webhook Configured: {health_data.get('webhook_configured', False)}")

        return True

    except requests.exceptions.ConnectionError:
        print("CRITICAL: Cannot connect to server on port 8000")
        return False
    except Exception as e:
        print(f"CRITICAL: Server health check failed: {e}")
        return False

def check_environment_variables():
    """Check critical environment variables"""
    print("\nCHECKING ENVIRONMENT VARIABLES...")

    required_vars = {
        "DATABASE_URL": "Database connection",
        "CLERK_SECRET_KEY": "Authentication",
        "CLERK_WEBHOOK_SECRET": "Webhook verification"
    }

    optional_vars = {
        "STRIPE_SECRET_KEY": "Payment processing",
        "R2_ACCESS_KEY_ID": "File storage",
        "R2_SECRET_ACCESS_KEY": "File storage"
    }

    missing_required = []
    missing_optional = []

    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_required.append(f"{var} ({description})")

    for var, description in optional_vars.items():
        if not os.getenv(var):
            missing_optional.append(f"{var} ({description})")

    if missing_required:
        print("CRITICAL MISSING ENVIRONMENT VARIABLES:")
        for var in missing_required:
            print(f"  - {var}")
    else:
        print("SUCCESS: All required environment variables present")

    if missing_optional:
        print("WARNING: Missing optional environment variables:")
        for var in missing_optional:
            print(f"  - {var}")

    return len(missing_required) == 0

def check_database_connectivity():
    """Check database connection and initialization"""
    print("\nCHECKING DATABASE CONNECTIVITY...")

    try:
        from app.core.database import engine
        from sqlalchemy import text

        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.fetchone()[0] == 1:
                print("SUCCESS: Database connection working")
            else:
                print("CRITICAL: Database connection test failed")
                return False

        # Check if tables exist
        from app.models.base import Base
        from sqlalchemy import inspect

        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # Get expected tables from models
        expected_tables = list(Base.metadata.tables.keys())
        missing_tables = [table for table in expected_tables if table not in existing_tables]

        if missing_tables:
            print(f"WARNING: Missing database tables: {missing_tables}")
            print("Database may need initialization")
        else:
            print(f"SUCCESS: All {len(expected_tables)} database tables present")

        return True

    except Exception as e:
        print(f"CRITICAL: Database connectivity check failed: {e}")
        return False

def check_authentication_system():
    """Check authentication system"""
    print("\nCHECKING AUTHENTICATION SYSTEM...")

    try:
        from app.auth.clerk_auth import ClerkUser
        from app.core.permissions import PermissionChecker, PERMISSION_MATRIX

        # Check permission matrix
        if len(PERMISSION_MATRIX) < 5:
            print("CRITICAL: Insufficient permission resources defined")
            return False

        print(f"SUCCESS: Permission matrix has {len(PERMISSION_MATRIX)} resources")

        # Test protected endpoint (should return 401 without auth)
        try:
            response = requests.get("http://127.0.0.1:8000/api/protected-example", timeout=5)
            if response.status_code == 401:
                print("SUCCESS: Protected endpoints properly secured")
            else:
                print(f"WARNING: Protected endpoint returned {response.status_code} instead of 401")
        except:
            print("WARNING: Could not test protected endpoint")

        return True

    except Exception as e:
        print(f"CRITICAL: Authentication system check failed: {e}")
        return False

def check_api_routes():
    """Check API route registration"""
    print("\nCHECKING API ROUTES...")

    try:
        from app.main import app

        routes = [route.path for route in app.routes if hasattr(route, 'path')]

        # Count routes by category
        route_categories = {
            'core': len([r for r in routes if r in ['/', '/health']]),
            'auth': len([r for r in routes if '/auth' in r]),
            'deals': len([r for r in routes if '/deals' in r]),
            'documents': len([r for r in routes if '/documents' in r]),
            'analytics': len([r for r in routes if '/analytics' in r or '/reports' in r]),
            'collaboration': len([r for r in routes if '/collaboration' in r]),
            'mobile': len([r for r in routes if '/mobile' in r])
        }

        issues = []
        if route_categories['core'] < 2:
            issues.append("Missing core routes")
        if route_categories['deals'] < 5:
            issues.append("Insufficient deal routes")
        if route_categories['documents'] < 5:
            issues.append("Insufficient document routes")

        if issues:
            print("CRITICAL ROUTE ISSUES:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"SUCCESS: {len(routes)} total routes registered")
            for category, count in route_categories.items():
                print(f"  {category}: {count} routes")
            return True

    except Exception as e:
        print(f"CRITICAL: API route check failed: {e}")
        return False

def check_critical_imports():
    """Check that all critical modules can be imported"""
    print("\nCHECKING CRITICAL IMPORTS...")

    critical_modules = [
        "app.main",
        "app.models.user",
        "app.models.organization",
        "app.models.deal",
        "app.models.documents",
        "app.auth.clerk_auth",
        "app.core.permissions",
        "app.api.v1.documents",
        "app.api.v1.mobile",
        "app.realtime.websocket_manager",
        "app.mobile.pwa_service"
    ]

    failed_imports = []

    for module in critical_modules:
        try:
            __import__(module)
        except Exception as e:
            failed_imports.append(f"{module}: {e}")

    if failed_imports:
        print("CRITICAL IMPORT FAILURES:")
        for failure in failed_imports:
            print(f"  - {failure}")
        return False
    else:
        print(f"SUCCESS: All {len(critical_modules)} critical modules imported successfully")
        return True

def run_critical_issues_check():
    """Run comprehensive critical issues check"""
    print("=" * 60)
    print("CRITICAL ISSUES CHECK")
    print("Identifying real issues that need attention")
    print("=" * 60)

    checks = [
        ("Critical Module Imports", check_critical_imports),
        ("Environment Variables", check_environment_variables),
        ("API Route Registration", check_api_routes),
        ("Authentication System", check_authentication_system),
        ("Database Connectivity", check_database_connectivity),
        ("Server Health", check_server_health)
    ]

    passed = 0
    failed = 0
    critical_issues = []

    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
                print(f"[PASS] {check_name}: PASSED")
            else:
                failed += 1
                critical_issues.append(check_name)
                print(f"[FAIL] {check_name}: FAILED")
        except Exception as e:
            failed += 1
            critical_issues.append(f"{check_name} (Exception: {e})")
            print(f"[CRASH] {check_name}: CRASHED - {e}")

    print("\n" + "=" * 60)
    print("CRITICAL ISSUES CHECK RESULTS")
    print("=" * 60)

    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")

    if failed > 0:
        print(f"\n[ALERT] CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"  - {issue}")
        print(f"\n[FAIL] PLATFORM STATUS: NOT PRODUCTION READY")
        print("RECOMMENDATION: Address critical issues before deployment")
        return False
    else:
        print(f"\n[PASS] NO CRITICAL ISSUES FOUND")
        print("[PASS] PLATFORM STATUS: PRODUCTION READY")
        return True

if __name__ == "__main__":
    success = run_critical_issues_check()
    sys.exit(0 if success else 1)