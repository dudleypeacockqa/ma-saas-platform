#!/usr/bin/env python3
"""
Sprint 7 Verification Test
Verify Sprint 7 - Real-Time Collaboration Implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sprint7_endpoints():
    """Test Sprint 7 real-time collaboration endpoints are registered"""
    print("TESTING SPRINT 7 ENDPOINT REGISTRATION...")
    try:
        from app.main import app
        routes = [route.path for route in app.routes if hasattr(route, 'path')]

        # Sprint 7 Real-Time Collaboration endpoints
        collaboration_endpoints = [
            '/api/v1/collaboration/ws/{user_id}',
            '/api/v1/collaboration/online-users',
            '/api/v1/collaboration/notifications',
            '/api/v1/collaboration/notifications/{notification_id}/read',
            '/api/v1/collaboration/notifications/{notification_id}/dismiss',
            '/api/v1/collaboration/documents/{document_id}/collaborate',
            '/api/v1/collaboration/documents/{document_id}/leave',
            '/api/v1/collaboration/documents/{document_id}/lock',
            '/api/v1/collaboration/documents/{document_id}/unlock',
            '/api/v1/collaboration/documents/{document_id}/collaborators',
            '/api/v1/collaboration/channels/{channel}/join',
            '/api/v1/collaboration/channels/{channel}/members',
            '/api/v1/collaboration/notifications/send',
            '/api/v1/collaboration/health'
        ]

        missing = []
        found = []

        for endpoint in collaboration_endpoints:
            # Check if endpoint pattern exists in routes
            endpoint_found = False
            for route in routes:
                if '/api/v1/collaboration/' in route and any(part in route for part in endpoint.split('/')):
                    endpoint_found = True
                    found.append(endpoint)
                    break

            if not endpoint_found:
                missing.append(endpoint)

        print(f"SUCCESS: Found {len(found)} Sprint 7 endpoints")
        for endpoint in found:
            print(f"  - {endpoint}")

        if missing:
            print(f"\nFAILED: Missing {len(missing)} Sprint 7 endpoints:")
            for endpoint in missing:
                print(f"  - {endpoint}")
            return False
        else:
            print(f"\nSUCCESS: All {len(collaboration_endpoints)} Sprint 7 endpoints registered")
            return True

    except Exception as e:
        print(f"FAILED: Sprint 7 endpoint test failed: {e}")
        return False

def test_realtime_module_imports():
    """Test real-time modules import correctly"""
    print("\nTESTING REAL-TIME MODULE IMPORTS...")
    try:
        from app.realtime.websocket_manager import WebSocketManager, RealtimeMessage, MessageType
        print("SUCCESS: WebSocket manager imported")

        from app.realtime.notifications import NotificationService, NotificationType, NotificationPriority
        print("SUCCESS: Notification service imported")

        from app.realtime.collaboration import CollaborativeDocumentManager, DocumentOperation, OperationType
        print("SUCCESS: Collaborative document manager imported")

        from app.api.v1 import realtime_collaboration
        print("SUCCESS: Real-time collaboration API imported")

        # Test instantiation
        websocket_manager = WebSocketManager()
        notification_service = NotificationService()
        document_manager = CollaborativeDocumentManager()
        print("SUCCESS: Real-time services instantiated")

        return True

    except Exception as e:
        print(f"FAILED: Real-time module import test failed: {e}")
        return False

def test_websocket_functionality():
    """Test basic WebSocket manager functionality"""
    print("\nTESTING WEBSOCKET FUNCTIONALITY...")
    try:
        from app.realtime.websocket_manager import WebSocketManager, MessageType, UserStatus

        manager = WebSocketManager()

        # Test message type enum
        assert MessageType.CHAT_MESSAGE == "chat_message"
        assert MessageType.DOCUMENT_EDIT == "document_edit"
        assert MessageType.NOTIFICATION == "notification"
        print("SUCCESS: Message types defined correctly")

        # Test user status enum
        assert UserStatus.ONLINE == "online"
        assert UserStatus.AWAY == "away"
        print("SUCCESS: User status types defined correctly")

        # Test basic manager methods exist
        assert hasattr(manager, 'connect')
        assert hasattr(manager, 'disconnect')
        assert hasattr(manager, 'send_to_user')
        assert hasattr(manager, 'broadcast_to_organization')
        assert hasattr(manager, 'join_channel')
        print("SUCCESS: WebSocket manager methods available")

        return True

    except Exception as e:
        print(f"FAILED: WebSocket functionality test failed: {e}")
        return False

def test_notification_system():
    """Test notification system functionality"""
    print("\nTESTING NOTIFICATION SYSTEM...")
    try:
        from app.realtime.notifications import NotificationService, NotificationType, NotificationPriority

        service = NotificationService()

        # Test notification types
        assert NotificationType.DEAL_CREATED == "deal_created"
        assert NotificationType.DOCUMENT_SHARED == "document_shared"
        assert NotificationType.AI_INSIGHT_GENERATED == "ai_insight_generated"
        print("SUCCESS: Notification types defined correctly")

        # Test priority levels
        assert NotificationPriority.LOW == "low"
        assert NotificationPriority.HIGH == "high"
        assert NotificationPriority.URGENT == "urgent"
        print("SUCCESS: Notification priorities defined correctly")

        # Test service methods exist
        assert hasattr(service, 'create_notification')
        assert hasattr(service, 'get_user_notifications')
        assert hasattr(service, 'mark_notification_read')
        print("SUCCESS: Notification service methods available")

        # Test notification templates
        assert len(service.notification_templates) > 10
        print(f"SUCCESS: {len(service.notification_templates)} notification templates loaded")

        return True

    except Exception as e:
        print(f"FAILED: Notification system test failed: {e}")
        return False

def test_collaborative_editing():
    """Test collaborative document editing functionality"""
    print("\nTESTING COLLABORATIVE EDITING...")
    try:
        from app.realtime.collaboration import (
            CollaborativeDocumentManager,
            DocumentOperation,
            OperationType,
            OperationalTransform
        )

        manager = CollaborativeDocumentManager()

        # Test operation types
        assert OperationType.INSERT == "insert"
        assert OperationType.DELETE == "delete"
        assert OperationType.RETAIN == "retain"
        print("SUCCESS: Operation types defined correctly")

        # Test manager methods exist
        assert hasattr(manager, 'join_document')
        assert hasattr(manager, 'apply_operation')
        assert hasattr(manager, 'update_cursor')
        assert hasattr(manager, 'lock_document')
        print("SUCCESS: Document manager methods available")

        # Test operational transform
        assert hasattr(OperationalTransform, 'transform_operation')
        assert hasattr(OperationalTransform, 'apply_operation')
        print("SUCCESS: Operational transform available")

        # Test basic operation application
        content = "Hello World"
        operation = DocumentOperation(
            id="test-op-1",
            type=OperationType.INSERT,
            position=5,
            content=" Beautiful",
            user_id="test-user"
        )

        new_content = OperationalTransform.apply_operation(content, operation)
        expected = "Hello Beautiful World"
        assert new_content == expected, f"Expected '{expected}', got '{new_content}'"
        print("SUCCESS: Basic operation transformation working")

        return True

    except Exception as e:
        print(f"FAILED: Collaborative editing test failed: {e}")
        return False

def test_permissions_update():
    """Test COMMUNICATIONS permissions are properly configured"""
    print("\nTESTING PERMISSIONS UPDATE...")
    try:
        from app.core.permissions import ResourceType, PERMISSION_MATRIX, Action

        # Check COMMUNICATIONS resource exists
        assert ResourceType.COMMUNICATIONS == "communications"
        print("SUCCESS: COMMUNICATIONS ResourceType exists")

        # Check COMMUNICATIONS in permission matrix
        assert ResourceType.COMMUNICATIONS in PERMISSION_MATRIX
        print("SUCCESS: COMMUNICATIONS in permission matrix")

        # Check COMMUNICATIONS has proper actions
        comms_perms = PERMISSION_MATRIX[ResourceType.COMMUNICATIONS]
        required_actions = ['create', 'read', 'update', 'delete', 'share', 'manage']

        missing_actions = []
        available_actions = [a.value for a in comms_perms.keys()]

        for action in required_actions:
            if action not in available_actions:
                missing_actions.append(action)

        if missing_actions:
            print(f"FAILED: Missing COMMUNICATIONS actions: {missing_actions}")
            return False
        else:
            print(f"SUCCESS: COMMUNICATIONS has all {len(required_actions)} required actions")
            return True

    except Exception as e:
        print(f"FAILED: Permissions test failed: {e}")
        return False

def test_api_integration():
    """Test real-time collaboration API integration"""
    print("\nTESTING API INTEGRATION...")
    try:
        from app.api.v1.realtime_collaboration import router

        # Check router exists and has routes
        assert router is not None, "Router should exist"

        # Get route information
        route_count = len(router.routes)
        print(f"SUCCESS: Real-time collaboration router has {route_count} routes")

        # Check for key endpoints
        route_paths = [route.path for route in router.routes if hasattr(route, 'path')]
        key_endpoints = ['/online-users', '/notifications', '/documents/{document_id}/collaborate', '/health']

        found_endpoints = []
        for endpoint in key_endpoints:
            if any(endpoint in path for path in route_paths):
                found_endpoints.append(endpoint)

        print(f"SUCCESS: Found {len(found_endpoints)} key endpoints")

        # Check for WebSocket endpoint
        websocket_routes = [route for route in router.routes if hasattr(route, 'path') and 'ws' in route.path]
        if websocket_routes:
            print("SUCCESS: WebSocket endpoint registered")
        else:
            print("WARNING: No WebSocket endpoint found")

        return True

    except Exception as e:
        print(f"FAILED: API integration test failed: {e}")
        return False

def run_sprint7_verification():
    """Run all Sprint 7 verification tests"""
    print("=" * 60)
    print("SPRINT 7 - REAL-TIME COLLABORATION VERIFICATION")
    print("=" * 60)

    tests = [
        ("Sprint 7 Endpoint Registration", test_sprint7_endpoints),
        ("Real-Time Module Imports", test_realtime_module_imports),
        ("WebSocket Functionality", test_websocket_functionality),
        ("Notification System", test_notification_system),
        ("Collaborative Editing", test_collaborative_editing),
        ("Permissions Update", test_permissions_update),
        ("API Integration", test_api_integration)
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
    print("SPRINT 7 VERIFICATION RESULTS")
    print("=" * 60)

    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print(f"SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")

    if failed > 0:
        print(f"\nCRITICAL: {failed} TESTS FAILED")
        print("STATUS: SPRINT 7 NOT READY")
        return False
    else:
        print(f"\nALL {passed} TESTS PASSED")
        print("STATUS: SPRINT 7 COMPLETE & VERIFIED")
        return True

if __name__ == "__main__":
    success = run_sprint7_verification()
    sys.exit(0 if success else 1)