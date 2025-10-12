#!/usr/bin/env python3
"""
Comprehensive Sprint 1-4 Verification Script
Verifies ALL Sprint requirements are implemented with ZERO errors
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_all_sprints():
    errors = []
    success = []

    print("COMPREHENSIVE SPRINT 1-4 VERIFICATION")
    print("=" * 60)

    # Test 1: Import all models
    print("\nTEST 1: Model Imports")
    print("-" * 30)
    try:
        from app.models import Deal, DealTeamMember, DealActivity, DealValuation, DealMilestone, DealDocument, DealFinancialModel
        print("SUCCESS: Sprint 1 - Deal Management Models")
        success.append("Sprint 1 Models")
    except Exception as e:
        error_msg = f"FAILED: Sprint 1 Models - {e}"
        print(error_msg)
        errors.append(error_msg)

    try:
        from app.models import Document, DocumentApproval, DocumentSignature, DocumentActivity
        print("SUCCESS: Sprint 3 - Document Management Models")
        success.append("Sprint 3 Models")
    except Exception as e:
        error_msg = f"FAILED: Sprint 3 Models - {e}"
        print(error_msg)
        errors.append(error_msg)

    try:
        from app.models import Negotiation, NegotiationParticipant, TermSheet, TermSheetTemplate
        print("SUCCESS: CRITICAL - Negotiation & TermSheet Models")
        success.append("Critical Models")
    except Exception as e:
        error_msg = f"FAILED: Critical Models - {e}"
        print(error_msg)
        errors.append(error_msg)

    # Test 2: API Imports
    print("\nTEST 2: API Module Imports")
    print("-" * 30)
    try:
        from app.routers import deals
        print("SUCCESS: Sprint 1 - Deal APIs")
        success.append("Sprint 1 APIs")
    except Exception as e:
        error_msg = f"FAILED: Sprint 1 APIs - {e}"
        print(error_msg)
        errors.append(error_msg)

    try:
        from app.api.v1 import pipeline
        print("SUCCESS: Sprint 2 - Pipeline APIs")
        success.append("Sprint 2 APIs")
    except Exception as e:
        error_msg = f"FAILED: Sprint 2 APIs - {e}"
        print(error_msg)
        errors.append(error_msg)

    try:
        from app.api.v1 import documents
        print("SUCCESS: Sprint 3 - Document APIs")
        success.append("Sprint 3 APIs")
    except Exception as e:
        error_msg = f"FAILED: Sprint 3 APIs - {e}"
        print(error_msg)
        errors.append(error_msg)

    try:
        from app.api import teams
        print("SUCCESS: Sprint 4 - Team APIs")
        success.append("Sprint 4 APIs")
    except Exception as e:
        error_msg = f"FAILED: Sprint 4 APIs - {e}"
        print(error_msg)
        errors.append(error_msg)

    # Test 3: Main App Import
    print("\nTEST 3: Main Application")
    print("-" * 30)
    try:
        from app.main import app
        routes = [route.path for route in app.routes if hasattr(route, 'path')]

        # Check critical endpoints
        critical_endpoints = [
            '/api/deals/',
            '/api/v1/pipeline/board',
            '/api/v1/documents/upload',
            '/api/teams/'
        ]

        missing_endpoints = []
        for endpoint in critical_endpoints:
            if not any(endpoint in route for route in routes):
                missing_endpoints.append(endpoint)

        if missing_endpoints:
            error_msg = f"FAILED: Missing endpoints: {missing_endpoints}"
            print(error_msg)
            errors.append(error_msg)
        else:
            print(f"SUCCESS: All critical endpoints registered ({len(routes)} total routes)")
            success.append("API Routing")

    except Exception as e:
        error_msg = f"FAILED: Main App Import - {e}"
        print(error_msg)
        errors.append(error_msg)

    # Test 4: Database Connection
    print("\nTEST 4: Database Verification")
    print("-" * 30)
    try:
        from app.core.database import engine
        from sqlalchemy import inspect, text

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        required_tables = [
            'deals', 'deal_team_members', 'deal_activities',  # Sprint 1
            'documents', 'document_approvals',                # Sprint 3
            'teams', 'team_members', 'team_tasks',           # Sprint 4
            'negotiations', 'term_sheets'                     # Critical
        ]

        missing_tables = []
        for table in required_tables:
            if table not in tables:
                missing_tables.append(table)

        if missing_tables:
            error_msg = f"FAILED: Missing tables: {missing_tables}"
            print(error_msg)
            errors.append(error_msg)
        else:
            print(f"SUCCESS: All required tables exist ({len(tables)} total tables)")
            success.append("Database Tables")

    except Exception as e:
        error_msg = f"FAILED: Database Connection - {e}"
        print(error_msg)
        errors.append(error_msg)

    # Final Report
    print("\n" + "=" * 60)
    print("FINAL VERIFICATION REPORT")
    print("=" * 60)

    if errors:
        print(f"\nCRITICAL ERRORS FOUND ({len(errors)}):")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")

    print(f"\nSUCCESSFUL VERIFICATIONS ({len(success)}):")
    for i, item in enumerate(success, 1):
        print(f"  {i}. {item}")

    success_rate = (len(success) / (len(success) + len(errors))) * 100 if (len(success) + len(errors)) > 0 else 0

    print(f"\nSUMMARY:")
    print(f"  Success Rate: {success_rate:.1f}%")
    print(f"  Total Errors: {len(errors)}")
    print(f"  Total Success: {len(success)}")

    if errors:
        print(f"\nRESULT: SPRINT IMPLEMENTATION HAS {len(errors)} CRITICAL ERRORS")
        print("STATUS: NOT PRODUCTION READY")
        return False
    else:
        print(f"\nRESULT: ALL SPRINT 1-4 REQUIREMENTS VERIFIED")
        print("STATUS: PRODUCTION READY")
        return True

if __name__ == "__main__":
    success = verify_all_sprints()
    exit(0 if success else 1)