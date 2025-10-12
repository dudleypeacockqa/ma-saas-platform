#!/usr/bin/env python3
"""
Sprint 4 Permission System Test
Verifies the new M&A role-based access control implementation
"""

import requests
import sys
from datetime import datetime

def test_sprint4_permissions():
    """Test Sprint 4 permission system implementation"""

    print("=" * 60)
    print("SPRINT 4 PERMISSION SYSTEM VERIFICATION")
    print("=" * 60)

    base_url = "http://localhost:8000"
    success_count = 0
    total_tests = 5

    # Test 1: Public Endpoints Still Accessible
    print("\n1. TESTING PUBLIC ENDPOINT ACCESS")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   SUCCESS: Root endpoint accessible")
            print(f"   API Version: {data.get('version', 'Unknown')}")
            success_count += 1
        else:
            print(f"   ERROR: Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: Public endpoint test failed: {e}")

    # Test 2: Health Check Still Works
    print("\n2. TESTING HEALTH CHECK")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   SUCCESS: Health endpoint accessible")
            print(f"   Database configured: {health_data.get('database_configured', False)}")
            success_count += 1
        else:
            print(f"   ERROR: Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ERROR: Health check failed: {e}")

    # Test 3: Protected API Requires Authentication
    print("\n3. TESTING DOCUMENT API PROTECTION")
    try:
        response = requests.get(f"{base_url}/api/v1/documents/")
        if response.status_code in [401, 403]:
            print("   SUCCESS: Document API properly protected")
            print(f"   Authentication/Permission required (HTTP {response.status_code})")
            success_count += 1
        else:
            print(f"   ERROR: Expected 401 or 403, got: {response.status_code}")
            if response.status_code == 200:
                print("   WARNING: API is not protected!")
    except Exception as e:
        print(f"   ERROR: Authentication test failed: {e}")

    # Test 4: Permission System Imports
    print("\n4. TESTING PERMISSION SYSTEM IMPORTS")
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))

        from app.core.permissions import PermissionChecker, ResourceType, Action
        from app.middleware.permission_middleware import require_permission, require_role
        from app.models.user import OrganizationRole

        print("   SUCCESS: All permission components import correctly")
        print(f"   ResourceTypes: {len(list(ResourceType))}")
        print(f"   Actions: {len(list(Action))}")
        print(f"   M&A Roles: {len([r for r in OrganizationRole if r.value.startswith('ma:')])}")
        success_count += 1
    except Exception as e:
        print(f"   ERROR: Permission system import failed: {e}")

    # Test 5: Permission Matrix Validation
    print("\n5. TESTING PERMISSION MATRIX")
    try:
        from app.core.permissions import PERMISSION_MATRIX, PermissionChecker
        from app.models.user import OrganizationRole

        # Test key permission scenarios
        managing_partner_can_create_deals = PermissionChecker.has_permission(
            OrganizationRole.MANAGING_PARTNER,
            ResourceType.DEALS,
            Action.CREATE
        )

        client_cannot_delete_docs = not PermissionChecker.has_permission(
            OrganizationRole.CLIENT,
            ResourceType.DOCUMENTS,
            Action.DELETE
        )

        if managing_partner_can_create_deals and client_cannot_delete_docs:
            print("   SUCCESS: Permission matrix working correctly")
            print("   Managing Partner can create deals: [YES]")
            print("   Client cannot delete documents: [YES]")
            success_count += 1
        else:
            print("   ERROR: Permission matrix validation failed")
            print(f"   Managing Partner create deals: {managing_partner_can_create_deals}")
            print(f"   Client delete docs (should be False): {not client_cannot_delete_docs}")
    except Exception as e:
        print(f"   ERROR: Permission matrix test failed: {e}")

    # Final Results
    print("\n" + "=" * 60)
    print("SPRINT 4 PERMISSION SYSTEM RESULTS")
    print("=" * 60)

    percentage = (success_count / total_tests) * 100
    print(f"Tests Passed: {success_count}/{total_tests} ({percentage:.1f}%)")

    if success_count >= 5:
        print("STATUS: SPRINT 4 PERMISSION SYSTEM COMPLETE")
        print("RESULT: M&A Role-Based Access Control is working")
        status = "COMPLETE"
    elif success_count >= 4:
        print("STATUS: SPRINT 4 MOSTLY FUNCTIONAL")
        print("RESULT: Core permission features working")
        status = "FUNCTIONAL"
    else:
        print("STATUS: SPRINT 4 NEEDS MORE WORK")
        print("RESULT: Permission system has issues")
        status = "INCOMPLETE"

    print(f"\nFINAL STATUS: {status}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return success_count >= 5

if __name__ == "__main__":
    print("Starting Sprint 4 Permission System Verification...")
    print("Server should be running on http://localhost:8000")

    try:
        success = test_sprint4_permissions()
        if success:
            print("\nSUCCESS: Sprint 4 permission system verified")
            print("READY FOR: Next Sprint 4 features (User Management)")
            sys.exit(0)
        else:
            print("\nNEEDS WORK: Sprint 4 permission system failed")
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Verification failed: {e}")
        sys.exit(1)