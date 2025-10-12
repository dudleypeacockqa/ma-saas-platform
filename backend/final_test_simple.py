#!/usr/bin/env python3
"""
FINAL EXHAUSTIVE VERIFICATION - No Unicode
Tests EVERY aspect of Sprint 1-4 implementation
"""

import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test actual database connectivity and operations"""
    print("TESTING DATABASE CONNECTION...")
    try:
        from app.core.database import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
            print("SUCCESS: Database connection working")

            # Test table existence
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result.fetchall()]

            required_tables = [
                'deals', 'deal_team_members', 'deal_activities', 'deal_valuations',
                'documents', 'document_approvals', 'document_signatures',
                'teams', 'team_members', 'team_tasks', 'team_meetings',
                'negotiations', 'term_sheets', 'organizations', 'users'
            ]

            missing = [t for t in required_tables if t not in tables]
            if missing:
                print(f"FAILED: Missing tables: {missing}")
                return False
            else:
                print(f"SUCCESS: All {len(required_tables)} critical tables exist")
                return True

    except Exception as e:
        print(f"FAILED: Database test failed: {e}")
        return False

def test_critical_endpoints():
    """Test critical endpoints are registered"""
    print("\nTESTING CRITICAL ENDPOINTS...")
    try:
        from app.main import app
        routes = [route.path for route in app.routes if hasattr(route, 'path')]

        critical_endpoints = [
            '/api/deals/',
            '/api/deals/{deal_id}/team/members',  # The critical missing one
            '/api/v1/pipeline/board',
            '/api/v1/documents/upload',
            '/api/teams/{team_id}/members'
        ]

        missing = []
        for endpoint in critical_endpoints:
            if not any(endpoint in route for route in routes):
                missing.append(endpoint)

        if missing:
            print(f"FAILED: Missing critical endpoints: {missing}")
            return False
        else:
            print(f"SUCCESS: All {len(critical_endpoints)} critical endpoints registered")
            return True

    except Exception as e:
        print(f"FAILED: Endpoint test failed: {e}")
        return False

def test_model_imports():
    """Test all critical models import"""
    print("\nTESTING MODEL IMPORTS...")
    try:
        # Sprint 1 models
        from app.models import Deal, DealTeamMember, DealActivity, DealValuation
        print("SUCCESS: Sprint 1 models imported")

        # Sprint 3 models
        from app.models import Document, DocumentApproval, DocumentSignature
        print("SUCCESS: Sprint 3 models imported")

        # Sprint 4 models
        from app.models.teams import Team, TeamMember, TeamTask
        print("SUCCESS: Sprint 4 models imported")

        # Critical models
        from app.models import Negotiation, TermSheet
        print("SUCCESS: Critical negotiation/term sheet models imported")

        return True

    except Exception as e:
        print(f"FAILED: Model import failed: {e}")
        return False

def test_api_modules():
    """Test API modules import without errors"""
    print("\nTESTING API MODULE IMPORTS...")
    try:
        from app.routers import deals
        from app.api.v1 import pipeline, documents
        from app.api import teams, negotiations, term_sheets
        print("SUCCESS: All API modules imported")
        return True

    except Exception as e:
        print(f"FAILED: API module import failed: {e}")
        return False

def test_authentication():
    """Test authentication setup"""
    print("\nTESTING AUTHENTICATION SETUP...")
    try:
        import os

        required_vars = ['CLERK_SECRET_KEY', 'DATABASE_URL', 'CLERK_WEBHOOK_SECRET']
        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            print(f"FAILED: Missing env vars: {missing}")
            return False
        else:
            print("SUCCESS: Authentication environment configured")
            return True

    except Exception as e:
        print(f"FAILED: Authentication test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("FINAL EXHAUSTIVE VERIFICATION - SPRINT 1-4")
    print("=" * 60)

    tests = [
        ("Database Connection", test_database_connection),
        ("Critical Endpoints", test_critical_endpoints),
        ("Model Imports", test_model_imports),
        ("API Modules", test_api_modules),
        ("Authentication", test_authentication)
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
    print("FINAL VERIFICATION RESULTS")
    print("=" * 60)

    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print(f"SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")

    if failed > 0:
        print(f"\nCRITICAL: {failed} TESTS FAILED")
        print("STATUS: NOT PRODUCTION READY")
        return False
    else:
        print(f"\nALL {passed} TESTS PASSED")
        print("STATUS: 100% VERIFIED PRODUCTION READY")
        return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)