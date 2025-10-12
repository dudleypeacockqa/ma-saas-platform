#!/usr/bin/env python3
"""
Direct test of document functionality without going through FastAPI server
This tests the actual document upload logic directly
"""

import os
import sys
import asyncio
import tempfile
import io
from uuid import uuid4

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

async def test_document_upload_direct():
    """Test document upload directly without authentication"""

    print("=== DIRECT DOCUMENT UPLOAD TEST ===\n")

    try:
        # Test storage service directly
        from app.services.storage_factory import storage_service

        print("1. Testing storage service upload...")
        test_content = b"This is a test PDF document for M&A due diligence"
        test_file = io.BytesIO(test_content)

        result = storage_service.upload_document(
            file=test_file,
            filename="due_diligence_test.pdf",
            organization_id="test-org-456",
            deal_id="deal-789",
            content_type="application/pdf",
            metadata={
                "test": "direct_upload",
                "deal_phase": "due_diligence"
            }
        )

        if result.get('success'):
            print(f"   SUCCESS: Upload to R2: {result.get('r2_key', 'N/A')}")

            # Test signed URL generation
            signed_url = storage_service.generate_signed_url(
                storage_path=result.get('r2_key', ''),
                expiration=300
            )

            if signed_url:
                print(f"   SUCCESS: Signed URL generated: {signed_url[:50]}...")
            else:
                print(f"   ERROR: Failed to generate signed URL")
                return False

        else:
            print(f"   ERROR: Upload failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"   ERROR: Storage test failed: {e}")
        return False

    # Test database operation directly
    print("\n2. Testing database document creation...")
    try:
        from app.core.database import SessionLocal
        from app.models.documents import Document, DocumentCategory, DocumentStatus, AccessLevel

        # Create database session
        db = SessionLocal()

        try:
            # Create document record
            doc = Document(
                organization_id=str(uuid4()),
                title="Test M&A Agreement",
                description="Test document for Sprint 3 verification",
                category=DocumentCategory.PURCHASE_AGREEMENT,
                document_type="Purchase Agreement",
                deal_id=str(uuid4()),
                file_name="ma_agreement_test.pdf",
                original_file_name="M&A Purchase Agreement.pdf",
                file_path=result.get('r2_key', '/test/path'),
                file_url=signed_url,
                file_size=len(test_content),
                mime_type="application/pdf",
                file_hash="test-hash-123",
                version_number=1,
                is_current_version=True,
                status=DocumentStatus.DRAFT,
                access_level=AccessLevel.CONFIDENTIAL,
                is_confidential=True,
                tags=["test", "ma", "agreement"],
                created_by=str(uuid4()),
                updated_by=str(uuid4())
            )

            # Save to database
            db.add(doc)
            db.commit()
            db.refresh(doc)

            print(f"   SUCCESS: Document saved to database with ID: {doc.id}")
            print(f"   SUCCESS: Document category: {doc.category}")
            print(f"   SUCCESS: Document status: {doc.status}")

            # Test querying the document
            retrieved_doc = db.query(Document).filter(Document.id == doc.id).first()
            if retrieved_doc:
                print(f"   SUCCESS: Document retrieved from database: {retrieved_doc.title}")
            else:
                print(f"   ERROR: Could not retrieve document from database")
                return False

        finally:
            db.close()

    except Exception as e:
        print(f"   ERROR: Database test failed: {e}")
        return False

    print("\n=== DIRECT TEST COMPLETE ===")
    print("SUCCESS: Document upload and database operations working")
    print("SUCCESS: Storage service functional")
    print("SUCCESS: Database models working")

    return True

if __name__ == "__main__":
    success = asyncio.run(test_document_upload_direct())
    if success:
        print("\n✓ CORE DOCUMENT FUNCTIONALITY IS WORKING")
        print("✓ Issue is with FastAPI server initialization, not document logic")
    else:
        print("\n✗ Core document functionality has issues")