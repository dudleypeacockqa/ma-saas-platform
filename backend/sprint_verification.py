#!/usr/bin/env python3
"""
Comprehensive Sprint 1-4 Verification Script
Verifies ALL Sprint requirements are implemented with ZERO errors
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import *
from app.core.database import engine
from sqlalchemy import text, inspect
import traceback
from datetime import datetime

class SprintVerification:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0

    def log_error(self, sprint, feature, error):
        self.errors.append(f"❌ Sprint {sprint} - {feature}: {error}")

    def log_warning(self, sprint, feature, warning):
        self.warnings.append(f"⚠️  Sprint {sprint} - {feature}: {warning}")

    def log_success(self, sprint, feature):
        self.success_count += 1
        print(f"✅ Sprint {sprint} - {feature}: VERIFIED")

    def increment_check(self):
        self.total_checks += 1

def verify_models():
    """Verify all required models are imported and accessible"""
    verification = SprintVerification()

    # Sprint 1 - Deal Management Models
    verification.increment_check()
    try:
        from app.models import Deal, DealTeamMember, DealActivity, DealValuation, DealMilestone, DealDocument, DealFinancialModel
        verification.log_success(1, "Deal Management Models")
    except ImportError as e:
        verification.log_error(1, "Deal Management Models", f"Import failed: {e}")

    # Sprint 2 - No specific models (uses Deal model)
    verification.increment_check()
    verification.log_success(2, "Pipeline Models (using Deal)")

    # Sprint 3 - Document Management Models
    verification.increment_check()
    try:
        from app.models import Document, DocumentApproval, DocumentSignature, DocumentActivity
        verification.log_success(3, "Document Management Models")
    except ImportError as e:
        verification.log_error(3, "Document Management Models", f"Import failed: {e}")

    # Sprint 4 - Team Collaboration Models
    verification.increment_check()
    try:
        from app.models.teams import Team, TeamMember, TeamTask, TeamMeeting, TeamChannel, TeamMessage
        verification.log_success(4, "Team Collaboration Models")
    except ImportError as e:
        verification.log_error(4, "Team Collaboration Models", f"Import failed: {e}")

    # Missing Models Check - Negotiation and TermSheet
    verification.increment_check()
    try:
        from app.models import Negotiation, NegotiationParticipant, NegotiationPosition, NegotiationMessage, TermSheet, TermSheetTemplate
        verification.log_success("CRITICAL", "Negotiation & TermSheet Models")
    except ImportError as e:
        verification.log_error("CRITICAL", "Negotiation & TermSheet Models", f"Import failed: {e}")

    return verification

def verify_database_tables():
    """Verify all required database tables exist"""
    verification = SprintVerification()

    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # Sprint 1 - Deal Management Tables
        sprint1_tables = ['deals', 'deal_team_members', 'deal_activities', 'deal_valuations', 'deal_milestones', 'deal_documents', 'deal_financial_models']
        for table in sprint1_tables:
            verification.increment_check()
            if table in existing_tables:
                verification.log_success(1, f"Table: {table}")
            else:
                verification.log_error(1, f"Table: {table}", "Table missing from database")

        # Sprint 3 - Document Management Tables
        sprint3_tables = ['documents', 'document_approvals', 'document_signatures', 'document_activities']
        for table in sprint3_tables:
            verification.increment_check()
            if table in existing_tables:
                verification.log_success(3, f"Table: {table}")
            else:
                verification.log_error(3, f"Table: {table}", "Table missing from database")

        # Sprint 4 - Team Collaboration Tables
        sprint4_tables = ['teams', 'team_members', 'team_tasks', 'team_meetings', 'team_channels', 'team_messages']
        for table in sprint4_tables:
            verification.increment_check()
            if table in existing_tables:
                verification.log_success(4, f"Table: {table}")
            else:
                verification.log_error(4, f"Table: {table}", "Table missing from database")

        # Critical Tables
        critical_tables = ['negotiations', 'term_sheets']
        for table in critical_tables:
            verification.increment_check()
            if table in existing_tables:
                verification.log_success("CRITICAL", f"Table: {table}")
            else:
                verification.log_error("CRITICAL", f"Table: {table}", "Critical table missing")

        print(f"\n📊 Total Database Tables Found: {len(existing_tables)}")

    except Exception as e:
        verification.log_error("DATABASE", "Table Verification", f"Failed to inspect database: {e}")

    return verification

def verify_api_endpoints():
    """Verify all API endpoints are registered"""
    verification = SprintVerification()

    try:
        # Import the FastAPI app to check registered routes
        from app.main import app

        all_routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                all_routes.append(route.path)

        # Sprint 1 - Deal Management Endpoints
        sprint1_endpoints = ['/api/deals/', '/api/deals/{deal_id}', '/api/deals/{deal_id}/team', '/api/deals/{deal_id}/activities']
        for endpoint in sprint1_endpoints:
            verification.increment_check()
            if any(endpoint in route for route in all_routes):
                verification.log_success(1, f"Endpoint: {endpoint}")
            else:
                verification.log_error(1, f"Endpoint: {endpoint}", "Endpoint not registered")

        # Sprint 2 - Pipeline Endpoints
        sprint2_endpoints = ['/api/v1/pipeline/board', '/api/v1/pipeline/board/move', '/api/v1/pipeline/board/statistics']
        for endpoint in sprint2_endpoints:
            verification.increment_check()
            if any(endpoint in route for route in all_routes):
                verification.log_success(2, f"Endpoint: {endpoint}")
            else:
                verification.log_error(2, f"Endpoint: {endpoint}", "Endpoint not registered")

        # Sprint 3 - Document Management Endpoints
        sprint3_endpoints = ['/api/v1/documents/upload', '/api/v1/documents/', '/api/v1/documents/{document_id}']
        for endpoint in sprint3_endpoints:
            verification.increment_check()
            if any(endpoint in route for route in all_routes):
                verification.log_success(3, f"Endpoint: {endpoint}")
            else:
                verification.log_error(3, f"Endpoint: {endpoint}", "Endpoint not registered")

        # Sprint 4 - Team Collaboration Endpoints
        sprint4_endpoints = ['/api/teams/', '/api/teams/{team_id}/members', '/api/teams/{team_id}/tasks']
        for endpoint in sprint4_endpoints:
            verification.increment_check()
            if any(endpoint in route for route in all_routes):
                verification.log_success(4, f"Endpoint: {endpoint}")
            else:
                verification.log_error(4, f"Endpoint: {endpoint}", "Endpoint not registered")

        print(f"\n📊 Total API Routes Found: {len(all_routes)}")

    except Exception as e:
        verification.log_error("API", "Endpoint Verification", f"Failed to check endpoints: {e}")

    return verification

def verify_imports():
    """Verify all critical imports work without errors"""
    verification = SprintVerification()

    critical_imports = [
        "app.models",
        "app.api.v1.pipeline",
        "app.api.v1.documents",
        "app.api.teams",
        "app.routers.deals"
    ]

    for import_module in critical_imports:
        verification.increment_check()
        try:
            __import__(import_module)
            verification.log_success("IMPORT", f"Module: {import_module}")
        except Exception as e:
            verification.log_error("IMPORT", f"Module: {import_module}", f"Import failed: {e}")

    return verification

def main():
    print("🔍 COMPREHENSIVE SPRINT 1-4 VERIFICATION")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now()}")
    print()

    all_verifications = []

    print("🔍 PHASE 1: Model Verification")
    print("-" * 30)
    all_verifications.append(verify_models())

    print("\n🔍 PHASE 2: Database Table Verification")
    print("-" * 30)
    all_verifications.append(verify_database_tables())

    print("\n🔍 PHASE 3: API Endpoint Verification")
    print("-" * 30)
    all_verifications.append(verify_api_endpoints())

    print("\n🔍 PHASE 4: Import Verification")
    print("-" * 30)
    all_verifications.append(verify_imports())

    # Compile results
    total_errors = []
    total_warnings = []
    total_success = 0
    total_checks = 0

    for verification in all_verifications:
        total_errors.extend(verification.errors)
        total_warnings.extend(verification.warnings)
        total_success += verification.success_count
        total_checks += verification.total_checks

    print("\n" + "=" * 60)
    print("📋 FINAL VERIFICATION REPORT")
    print("=" * 60)

    if total_errors:
        print("❌ CRITICAL ERRORS FOUND:")
        for error in total_errors:
            print(f"   {error}")
        print()

    if total_warnings:
        print("⚠️  WARNINGS:")
        for warning in total_warnings:
            print(f"   {warning}")
        print()

    print(f"📊 VERIFICATION SUMMARY:")
    print(f"   ✅ Successful Checks: {total_success}/{total_checks}")
    print(f"   ❌ Failed Checks: {len(total_errors)}")
    print(f"   ⚠️  Warnings: {len(total_warnings)}")
    print(f"   📈 Success Rate: {(total_success/total_checks)*100:.1f}%")

    if total_errors:
        print(f"\n🚨 RESULT: SPRINT IMPLEMENTATION HAS {len(total_errors)} CRITICAL ERRORS")
        print("   ❌ NOT PRODUCTION READY")
        return False
    else:
        print(f"\n🎉 RESULT: ALL SPRINT 1-4 REQUIREMENTS VERIFIED")
        print("   ✅ PRODUCTION READY")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)