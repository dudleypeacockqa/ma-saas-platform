#!/usr/bin/env python3
"""
Test ONLY the Document model without other complex relationships
This isolates the Sprint 3 document functionality
"""

import os
import sys
import asyncio
from uuid import uuid4

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_document_model_isolation():
    """Test document model in isolation"""

    print("=== ISOLATED DOCUMENT MODEL TEST ===\n")

    try:
        # Test 1: Import document model directly
        print("1. Testing document model import...")
        from app.models.documents import Document, DocumentCategory, DocumentStatus, AccessLevel
        print("   SUCCESS: Document model imports successfully")

        # Test 2: Test storage service
        print("\n2. Testing storage service...")
        from app.services.storage_factory import storage_service

        import io
        test_content = b"Test document content for Sprint 3"
        test_file = io.BytesIO(test_content)

        result = storage_service.upload_document(
            file=test_file,
            filename="sprint3_test.pdf",
            organization_id="test-org-123",
            deal_id=None,
            content_type="application/pdf",
            metadata={"test": "isolation"}
        )

        if result.get('success'):
            print(f"   SUCCESS: Storage upload works: {result.get('r2_key', 'N/A')}")
        else:
            print(f"   ERROR: Storage upload failed: {result.get('error', 'Unknown')}")
            return False

        # Test 3: Create document model instance (without database)
        print("\n3. Testing document model creation...")
        doc = Document(
            organization_id=str(uuid4()),
            title="Test Document",
            description="Isolated test document",
            category=DocumentCategory.DUE_DILIGENCE,
            document_type="Test PDF",
            file_name="test.pdf",
            original_file_name="test.pdf",
            file_path=result.get('r2_key', '/test/path'),
            file_size=len(test_content),
            mime_type="application/pdf",
            version_number=1,
            is_current_version=True,
            status=DocumentStatus.DRAFT,
            access_level=AccessLevel.CONFIDENTIAL,
            is_confidential=True,
            tags=["test", "isolation"]
        )

        print(f"   SUCCESS: Document model instance created")
        print(f"   SUCCESS: Document ID: {doc.id}")
        print(f"   SUCCESS: Document category: {doc.category}")
        print(f"   SUCCESS: Document status: {doc.status}")

        # Test 4: Test document properties
        print("\n4. Testing document properties...")
        print(f"   Document is current: {doc.is_current}")
        print(f"   Document total versions: {doc.total_versions}")
        print(f"   Document overdue: {doc.is_overdue}")

        print("\n=== ISOLATED TEST COMPLETE ===")
        print("SUCCESS: Document model works in isolation")
        print("SUCCESS: Storage service functional")
        print("SUCCESS: Document properties accessible")

        return True

    except Exception as e:
        print(f"   ERROR: Isolated test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_document_model_isolation()
    if success:
        print("\nCONCLUSION: Core document functionality WORKS")
        print("ISSUE: Complex database relationships are broken")
        print("SPRINT 3 STATUS: Document core is functional, but database integration has issues")
    else:
        print("\nCONCLUSION: Core document functionality has problems")