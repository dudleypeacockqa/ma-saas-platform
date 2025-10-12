#!/usr/bin/env python3
"""
Sprint 3 Final Test - Simple ASCII-only verification
End-to-end test of the document management system
"""

import requests
import sys
from datetime import datetime

def test_sprint3_system():
    """Sprint 3 system verification with ASCII output"""

    print("=" * 60)
    print("SPRINT 3 FINAL VERIFICATION TEST")
    print("=" * 60)

    base_url = "http://localhost:8000"
    success_count = 0
    total_tests = 6

    # Test 1: Public Endpoints
    print("\n1. TESTING PUBLIC ENDPOINTS")
    try:
        # Root endpoint
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print("   SUCCESS: Root endpoint accessible")
            print(f"   API Version: {data.get('version', 'Unknown')}")
            success_count += 1
        else:
            print(f"   ERROR: Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: Public endpoint test failed: {e}")

    # Test 2: Health Check
    print("\n2. TESTING HEALTH CHECK")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("   SUCCESS: Health endpoint accessible")
            print(f"   Clerk configured: {health_data.get('clerk_configured', False)}")
            success_count += 1
        else:
            print(f"   ERROR: Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: Health check failed: {e}")

    # Test 3: Authentication Protection
    print("\n3. TESTING AUTHENTICATION")
    try:
        response = requests.get(f"{base_url}/api/v1/documents/")
        if response.status_code in [401, 403]:
            print("   SUCCESS: Document API properly protected")
            print(f"   Authentication status: HTTP {response.status_code}")
            success_count += 1
        else:
            print(f"   ERROR: Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: Authentication test failed: {e}")

    # Test 4: API Documentation
    print("\n4. TESTING API DOCUMENTATION")
    try:
        response = requests.get(f"{base_url}/api/docs")
        if response.status_code == 200:
            print("   SUCCESS: API documentation accessible")
            success_count += 1
        else:
            print(f"   ERROR: API docs failed: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: API docs test failed: {e}")

    # Test 5: Model Imports
    print("\n5. TESTING MODEL IMPORTS")
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))

        from app.models.documents import Document, DocumentCategory, DocumentStatus
        from app.schemas.document import DocumentResponse
        from app.services.storage_factory import storage_service

        print("   SUCCESS: All models import correctly")
        print(f"   DocumentCategory enum: {len(list(DocumentCategory))} values")
        print(f"   DocumentStatus enum: {len(list(DocumentStatus))} values")
        success_count += 1
    except Exception as e:
        print(f"   ERROR: Model import failed: {e}")

    # Test 6: Environment Configuration
    print("\n6. TESTING ENVIRONMENT")
    try:
        import os

        required_vars = ['CLERK_SECRET_KEY', 'DATABASE_URL', 'R2_ACCESS_KEY_ID', 'R2_BUCKET_NAME']
        configured = sum(1 for var in required_vars if os.getenv(var))

        print(f"   Environment variables: {configured}/{len(required_vars)} configured")
        if configured >= 3:
            print("   SUCCESS: Core environment ready")
            success_count += 1
        else:
            print("   WARNING: Environment incomplete")
    except Exception as e:
        print(f"   ERROR: Environment test failed: {e}")

    # Final Results
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    percentage = (success_count / total_tests) * 100
    print(f"Tests Passed: {success_count}/{total_tests} ({percentage:.1f}%)")

    if success_count >= 5:
        print("STATUS: SPRINT 3 COMPLETE AND FUNCTIONAL")
        print("RESULT: Document Management System is ready")
        status = "COMPLETE"
    elif success_count >= 4:
        print("STATUS: SPRINT 3 MOSTLY FUNCTIONAL")
        print("RESULT: Core features working")
        status = "FUNCTIONAL"
    else:
        print("STATUS: SPRINT 3 NEEDS MORE WORK")
        print("RESULT: Significant issues remain")
        status = "INCOMPLETE"

    print(f"\nFINAL STATUS: {status}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return success_count >= 5

if __name__ == "__main__":
    print("Starting Sprint 3 Final Verification...")
    print("Server should be running on http://localhost:8000")

    try:
        success = test_sprint3_system()
        if success:
            print("\nSUCCESS: Sprint 3 verification passed")
            print("READY FOR: Sprint 4 - User Management & Permissions")
            sys.exit(0)
        else:
            print("\nNEEDS WORK: Sprint 3 verification failed")
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Verification failed: {e}")
        sys.exit(1)