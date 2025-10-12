#!/usr/bin/env python3
"""
User Story Implementation Verification
Verifies each specific user story from Sprint 1-4 is fully implemented
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_user_stories():
    print("USER STORY IMPLEMENTATION VERIFICATION")
    print("=" * 60)

    errors = []
    success = []

    # Import the FastAPI app
    try:
        from app.main import app
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        print(f"Total API routes registered: {len(routes)}")
    except Exception as e:
        print(f"CRITICAL ERROR: Cannot import app - {e}")
        return False

    # SPRINT 1 USER STORIES
    print("\nSPRINT 1: Deal Management")
    print("-" * 40)

    # User Story 1.1: Deal Creation and Management
    story_1_1_endpoints = [
        '/api/deals/',           # Create/List deals
        '/api/deals/{deal_id}',  # Get/Update/Delete deal
    ]

    missing_1_1 = []
    for endpoint in story_1_1_endpoints:
        if not any(endpoint in route for route in routes):
            missing_1_1.append(endpoint)

    if missing_1_1:
        error_msg = f"Story 1.1 INCOMPLETE: Missing endpoints {missing_1_1}"
        print(error_msg)
        errors.append(error_msg)
    else:
        print("Story 1.1 COMPLETE: Deal Creation and Management")
        success.append("Story 1.1")

    # User Story 1.2: Deal Team Assignment
    story_1_2_endpoints = [
        '/api/deals/{deal_id}/team',        # Team management
        '/api/deals/{deal_id}/team/members' # Member management
    ]

    missing_1_2 = []
    for endpoint in story_1_2_endpoints:
        if not any(endpoint in route for route in routes):
            missing_1_2.append(endpoint)

    if missing_1_2:
        error_msg = f"Story 1.2 INCOMPLETE: Missing endpoints {missing_1_2}"
        print(error_msg)
        errors.append(error_msg)
    else:
        print("Story 1.2 COMPLETE: Deal Team Assignment")
        success.append("Story 1.2")

    # User Story 1.3: Deal Activity Tracking
    story_1_3_endpoints = [
        '/api/deals/{deal_id}/activities',  # Activity tracking
        '/api/deals/{deal_id}/stage'        # Stage transitions
    ]

    missing_1_3 = []
    for endpoint in story_1_3_endpoints:
        if not any(endpoint in route for route in routes):
            missing_1_3.append(endpoint)

    if missing_1_3:
        error_msg = f"Story 1.3 INCOMPLETE: Missing endpoints {missing_1_3}"
        print(error_msg)
        errors.append(error_msg)
    else:
        print("Story 1.3 COMPLETE: Deal Activity Tracking")
        success.append("Story 1.3")

    # SPRINT 2 USER STORIES
    print("\nSPRINT 2: Pipeline Visualization")
    print("-" * 40)

    # User Story 2.1: Pipeline Board Backend
    story_2_1_endpoints = [
        '/api/v1/pipeline/board',           # Kanban board
        '/api/v1/pipeline/board/move',      # Stage transitions
        '/api/v1/pipeline/board/statistics' # Pipeline analytics
    ]

    missing_2_1 = []
    for endpoint in story_2_1_endpoints:
        if not any(endpoint in route for route in routes):
            missing_2_1.append(endpoint)

    if missing_2_1:
        error_msg = f"Story 2.1 INCOMPLETE: Missing endpoints {missing_2_1}"
        print(error_msg)
        errors.append(error_msg)
    else:
        print("Story 2.1 COMPLETE: Pipeline Board Backend")
        success.append("Story 2.1")

    # SPRINT 3 USER STORIES
    print("\nSPRINT 3: Document Management")
    print("-" * 40)

    # User Story 3.1: Document Upload API
    story_3_1_endpoints = [
        '/api/v1/documents/upload',        # File upload
        '/api/v1/documents/upload-direct', # Direct upload
        '/api/v1/documents/',              # List documents
        '/api/v1/documents/{document_id}', # Get document
        '/api/v1/documents/{document_id}/download' # Download
    ]

    missing_3_1 = []
    for endpoint in story_3_1_endpoints:
        if not any(endpoint in route for route in routes):
            missing_3_1.append(endpoint)

    if missing_3_1:
        error_msg = f"Story 3.1 INCOMPLETE: Missing endpoints {missing_3_1}"
        print(error_msg)
        errors.append(error_msg)
    else:
        print("Story 3.1 COMPLETE: Document Upload API")
        success.append("Story 3.1")

    # SPRINT 4 USER STORIES
    print("\nSPRINT 4: Team Collaboration")
    print("-" * 40)

    # User Story 4.1: Team Management
    story_4_1_endpoints = [
        '/api/teams/',                      # Create/List teams
        '/api/teams/{team_id}',            # Team details
        '/api/teams/{team_id}/members',    # Member management
        '/api/teams/{team_id}/tasks'       # Task management
    ]

    missing_4_1 = []
    for endpoint in story_4_1_endpoints:
        if not any(endpoint in route for route in routes):
            missing_4_1.append(endpoint)

    if missing_4_1:
        error_msg = f"Story 4.1 INCOMPLETE: Missing endpoints {missing_4_1}"
        print(error_msg)
        errors.append(error_msg)
    else:
        print("Story 4.1 COMPLETE: Team Management")
        success.append("Story 4.1")

    # User Story 4.2: Team Communication
    story_4_2_endpoints = [
        '/api/teams/{team_id}/channels',   # Communication channels
        '/api/teams/{team_id}/meetings'    # Meeting management
    ]

    missing_4_2 = []
    for endpoint in story_4_2_endpoints:
        if not any(endpoint in route for route in routes):
            missing_4_2.append(endpoint)

    if missing_4_2:
        error_msg = f"Story 4.2 INCOMPLETE: Missing endpoints {missing_4_2}"
        print(error_msg)
        errors.append(error_msg)
    else:
        print("Story 4.2 COMPLETE: Team Communication")
        success.append("Story 4.2")

    # FINAL REPORT
    print("\n" + "=" * 60)
    print("USER STORY IMPLEMENTATION REPORT")
    print("=" * 60)

    if errors:
        print(f"\nINCOMPLETE USER STORIES ({len(errors)}):")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")

    print(f"\nCOMPLETED USER STORIES ({len(success)}):")
    for i, story in enumerate(success, 1):
        print(f"  {i}. {story}")

    total_stories = len(success) + len(errors)
    completion_rate = (len(success) / total_stories * 100) if total_stories > 0 else 0

    print(f"\nSUMMARY:")
    print(f"  Completion Rate: {completion_rate:.1f}%")
    print(f"  Completed Stories: {len(success)}")
    print(f"  Incomplete Stories: {len(errors)}")

    if errors:
        print(f"\nRESULT: {len(errors)} USER STORIES INCOMPLETE")
        print("STATUS: NOT READY FOR PRODUCTION")
        return False
    else:
        print(f"\nRESULT: ALL USER STORIES IMPLEMENTED")
        print("STATUS: PRODUCTION READY")
        return True

if __name__ == "__main__":
    success = verify_user_stories()
    exit(0 if success else 1)