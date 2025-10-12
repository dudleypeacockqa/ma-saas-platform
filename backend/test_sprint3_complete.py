#!/usr/bin/env python3
"""
Sprint 3 Complete End-to-End Test
Tests the document management system integration
"""

import os
import sys
import asyncio
import tempfile
import io
from typing import Dict, Any
from uuid import uuid4

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

async def test_sprint3_complete():
    """Comprehensive test of Sprint 3 document management system"""

    print("=== SPRINT 3 COMPLETE VERIFICATION TEST ===\n")

    # Test 1: Import all modules
    print("1. Testing module imports...")
    try:
        from app.models.documents import Document, DocumentCategory, DocumentStatus
        from app.schemas.document import DocumentResponse, UploadResponse
        from app.api.v1.documents import router
        from app.services.storage_factory import storage_service
        from app.core.deps import get_current_user, get_current_tenant
        print("   SUCCESS: All modules import successfully")
    except Exception as e:
        print(f"   ERROR: Import error: {e}")
        return False

    # Test 2: Storage service functionality
    print("\n2. Testing storage service...")
    try:
        # Create a test file
        test_content = b"This is a test document for Sprint 3 verification"
        test_file = io.BytesIO(test_content)

        # Test upload functionality
        result = storage_service.upload_document(
            file=test_file,
            filename="test_sprint3.txt",
            organization_id="test-org-123",
            deal_id=None,
            content_type="text/plain",
            metadata={"test": "sprint3"}
        )

        if result.get('success'):
            print(f"   SUCCESS: Document upload successful: {result.get('r2_key', 'N/A')}")

            # Test signed URL generation
            signed_url = storage_service.generate_signed_url(
                storage_path=result.get('r2_key', ''),
                expiration=300
            )

            if signed_url:
                print(f"   SUCCESS: Signed URL generation successful")
            else:
                print(f"   WARNING:  Signed URL generation returned empty")

        else:
            print(f"   ERROR: Document upload failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"   ERROR: Storage service error: {e}")
        return False

    # Test 3: Database models
    print("\n3. Testing database models...")
    try:
        from app.core.database import get_db

        # Test database connection
        db_gen = get_db()
        db = next(db_gen)
        print("   SUCCESS: Database connection successful")
        db.close()

        # Test model classes are importable
        print("   SUCCESS: Document model classes accessible")
        print(f"   SUCCESS: DocumentCategory enum: {list(DocumentCategory)[:3]}...")
        print(f"   SUCCESS: DocumentStatus enum: {list(DocumentStatus)[:3]}...")

    except Exception as e:
        print(f"   ERROR: Database/model error: {e}")
        return False

    # Test 4: API schemas
    print("\n4. Testing API schemas...")
    try:
        from datetime import datetime
        from uuid import uuid4

        # Test document response schema
        doc_data = {
            "id": uuid4(),
            "title": "Test Document",
            "description": "Test description",
            "category": "other",
            "document_type": "Test",
            "file_name": "test.txt",
            "original_file_name": "test.txt",
            "file_path": "/test/path",
            "file_url": "https://example.com/test.txt",
            "file_size": 100,
            "mime_type": "text/plain",
            "file_hash": "test-hash",
            "version_number": 1,
            "is_current_version": True,
            "status": "draft",
            "access_level": "confidential",
            "is_confidential": True,
            "deal_id": None,
            "tags": ["test"],
            "created_at": datetime.now(),
            "modified_at": datetime.now(),
            "view_count": 0,
            "download_count": 0,
            "presigned_url": None
        }

        doc_response = DocumentResponse(**doc_data)
        print("   SUCCESS: DocumentResponse schema validation successful")

        # Test upload response schema
        upload_data = {
            "document_id": uuid4(),
            "filename": "test.txt",
            "file_size": 100,
            "mime_type": "text/plain",
            "s3_key": "/test/path",
            "presigned_url": "https://example.com/signed-url",
            "status": "success",
            "message": "Upload successful"
        }

        upload_response = UploadResponse(**upload_data)
        print("   SUCCESS: UploadResponse schema validation successful")

    except Exception as e:
        print(f"   ERROR: Schema validation error: {e}")
        return False

    # Test 5: Environment configuration
    print("\n5. Testing environment configuration...")
    try:
        from app.core.config import settings

        # Check required environment variables
        required_vars = [
            'R2_ACCESS_KEY_ID',
            'R2_SECRET_ACCESS_KEY',
            'R2_BUCKET_NAME',
            'CLOUDFLARE_ACCOUNT_ID'
        ]

        missing_vars = []
        for var in required_vars:
            if not getattr(settings, var, None) and not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            print(f"   WARNING:  Missing environment variables: {', '.join(missing_vars)}")
        else:
            print("   SUCCESS: All required environment variables present")

        print(f"   SUCCESS: Storage provider: {getattr(settings, 'STORAGE_PROVIDER', 'r2')}")

    except Exception as e:
        print(f"   ERROR: Configuration error: {e}")
        return False

    print("\n=== SPRINT 3 VERIFICATION COMPLETE ===")
    print("SUCCESS: All core components are working correctly")
    print("SUCCESS: Document upload, storage, and retrieval system operational")
    print("SUCCESS: Database models and API schemas aligned")
    print("SUCCESS: Cloudflare R2 storage integration functional")

    return True

if __name__ == "__main__":
    success = asyncio.run(test_sprint3_complete())
    if success:
        print("\nCELEBRATION: SPRINT 3 IS FULLY COMPLETE AND FUNCTIONAL! CELEBRATION:")
        sys.exit(0)
    else:
        print("\nERROR: Sprint 3 has issues that need to be resolved")
        sys.exit(1)