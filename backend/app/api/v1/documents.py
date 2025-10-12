"""
Document Management API Endpoints
Story 3.1: Document Upload API - Secure file upload and management
"""

import os
import io
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update, delete
from sqlalchemy.orm import selectinload

from app.core.deps import get_db, get_current_user, get_current_tenant
from app.models.documents import Document, DocumentCategory, DocumentStatus
from app.services.storage_factory import storage_service
from app.middleware.permission_middleware import require_permission, require_senior_role, load_document_context
from app.core.permissions import ResourceType, Action
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    FolderCreate,
    FolderResponse,
    UploadResponse
)

router = APIRouter()

# Maximum file size (500MB)
MAX_FILE_SIZE = 500 * 1024 * 1024

# Allowed file extensions for security
ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.txt', '.csv', '.rtf', '.odt', '.ods', '.odp',
    '.png', '.jpg', '.jpeg', '.gif', '.bmp',
    '.zip', '.rar', '.7z',
    '.xml', '.json', '.yaml', '.yml'
}


def validate_file(file: UploadFile) -> bool:
    """Validate file type and size"""
    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not allowed"
        )

    # Check file size (this is a simplified check)
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum of {MAX_FILE_SIZE / (1024*1024)}MB"
        )

    return True


@router.post("/upload", response_model=UploadResponse)
@require_permission(ResourceType.DOCUMENTS, Action.CREATE)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    deal_id: Optional[UUID] = Form(None),
    folder_path: str = Form("/"),
    document_type: Optional[DocumentCategory] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    is_confidential: bool = Form(True),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
) -> UploadResponse:
    """
    Upload a document to S3 and save metadata to database.
    Supports attaching to deals and organizing in folders.
    """

    # Validate file
    validate_file(file)

    # Prepare file metadata
    file_extension = os.path.splitext(file.filename)[1].lower()
    content_type = file.content_type or 'application/octet-stream'

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    # Create file-like object for S3
    file_obj = io.BytesIO(file_content)

    # Upload to configured storage provider (R2, S3, etc.)
    storage_result = storage_service.upload_document(
        file=file_obj,
        filename=file.filename,
        organization_id=str(tenant_id),
        deal_id=str(deal_id) if deal_id else None,
        content_type=content_type,
        metadata={
            'uploaded_by': current_user.get('id', ''),
            'user_email': current_user.get('email', '')
        }
    )

    if not storage_result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=storage_result.get('error', 'Failed to upload file to storage')
        )

    # Create document record with storage-agnostic fields
    document = Document(
        id=uuid4(),
        organization_id=tenant_id,
        filename=file.filename,
        original_filename=file.filename,
        file_extension=file_extension,
        mime_type=content_type,
        file_size=file_size,
        s3_bucket=storage_result.get('r2_bucket') or storage_result.get('s3_bucket') or storage_result.get('bucket', ''),
        s3_key=storage_result.get('r2_key') or storage_result.get('s3_key') or storage_result.get('path', ''),
        s3_url=storage_result.get('r2_url') or storage_result.get('s3_url') or storage_result.get('signed_url', ''),
        s3_etag=storage_result.get('r2_etag') or storage_result.get('s3_etag') or storage_result.get('file_hash', ''),
        document_type=document_type or DocumentCategory.OTHER,
        status=DocumentStatus.AVAILABLE,
        folder_path=folder_path,
        deal_id=deal_id,
        uploaded_by=UUID(current_user.get('id', str(tenant_id))),
        title=title or file.filename,
        description=description,
        tags=tags.split(',') if tags else [],
        is_confidential=is_confidential,
        access_level='private' if is_confidential else 'team'
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Generate presigned URL for access
    presigned_url = storage_service.generate_signed_url(
        storage_path=document.s3_key,
        expiration=86400  # 24 hours
    )

    return UploadResponse(
        document_id=document.id,
        filename=document.filename,
        file_size=document.file_size,
        mime_type=document.mime_type,
        s3_key=document.s3_key,
        presigned_url=presigned_url,
        status="success",
        message="Document uploaded successfully"
    )


@router.post("/upload-direct", response_model=Dict[str, Any])
@require_permission(ResourceType.DOCUMENTS, Action.CREATE)
async def get_upload_presigned_url(
    filename: str,
    content_type: str,
    deal_id: Optional[UUID] = None,
    folder_path: str = "/",
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
) -> Dict[str, Any]:
    """
    Get a presigned URL for direct browser upload to S3.
    This allows large file uploads directly from the browser without going through the server.
    """

    # Validate file extension
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not allowed"
        )

    # Generate presigned POST data
    presigned_data = storage_service.generate_upload_signed_url(
        organization_id=str(tenant_id),
        deal_id=str(deal_id) if deal_id else None,
        filename=filename,
        content_type=content_type,
        expiration=3600  # 1 hour
    )

    if not presigned_data['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=presigned_data.get('error', 'Failed to generate upload URL')
        )

    return {
        **presigned_data,
        'document_id': str(uuid4()),  # Pre-generate document ID
        'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }


@router.get("/", response_model=DocumentListResponse)
@require_permission(ResourceType.DOCUMENTS, Action.READ)
async def list_documents(
    deal_id: Optional[UUID] = Query(None),
    folder_path: Optional[str] = Query("/"),
    document_type: Optional[DocumentCategory] = Query(None),
    search: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    is_confidential: Optional[bool] = Query(None),
    sort_by: str = Query("uploaded_at", regex="^(filename|uploaded_at|file_size|modified_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
) -> DocumentListResponse:
    """
    List documents with filtering, search, and pagination.
    """

    # Build query
    query = select(Document).where(
        Document.organization_id == tenant_id,
        Document.status == DocumentStatus.AVAILABLE
    )

    # Apply filters
    if deal_id:
        query = query.where(Document.deal_id == deal_id)

    if folder_path:
        query = query.where(Document.folder_path == folder_path)

    if document_type:
        query = query.where(Document.document_type == document_type)

    if is_confidential is not None:
        query = query.where(Document.is_confidential == is_confidential)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Document.filename.ilike(search_term),
                Document.title.ilike(search_term),
                Document.description.ilike(search_term)
            )
        )

    if tags:
        # Filter by tags (documents that have any of the specified tags)
        for tag in tags:
            query = query.where(Document.tags.contains([tag]))

    # Apply sorting
    order_column = getattr(Document, sort_by)
    if sort_order == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())

    # Count total documents
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Execute query
    result = await db.execute(query)
    documents = result.scalars().all()

    # Generate presigned URLs for each document
    documents_with_urls = []
    for doc in documents:
        presigned_url = storage_service.generate_signed_url(
            s3_key=doc.s3_key,
            expiration=3600  # 1 hour
        )

        doc_dict = doc.to_dict()
        doc_dict['presigned_url'] = presigned_url
        documents_with_urls.append(DocumentResponse(**doc_dict))

    return DocumentListResponse(
        data=documents_with_urls,
        pagination={
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    )


@router.get("/{document_id}", response_model=DocumentResponse)
@require_permission(ResourceType.DOCUMENTS, Action.READ, context_loader=load_document_context)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
) -> DocumentResponse:
    """
    Get document details with presigned URL for download.
    """

    # Get document
    query = select(Document).where(
        Document.id == document_id,
        Document.organization_id == tenant_id
    )
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Update access tracking
    document.view_count += 1
    document.accessed_at = datetime.utcnow()
    document.last_accessed_by = UUID(current_user.get('id', str(tenant_id)))
    await db.commit()

    # Generate presigned URL
    presigned_url = storage_service.generate_signed_url(
        storage_path=document.s3_key,
        expiration=3600  # 1 hour
    )

    doc_dict = document.to_dict()
    doc_dict['presigned_url'] = presigned_url

    return DocumentResponse(**doc_dict)


@router.get("/{document_id}/download")
@require_permission(ResourceType.DOCUMENTS, Action.READ, context_loader=load_document_context)
async def download_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Get a presigned URL for downloading a document.
    """

    # Get document
    query = select(Document).where(
        Document.id == document_id,
        Document.organization_id == tenant_id
    )
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Update download tracking
    document.download_count += 1
    document.accessed_at = datetime.utcnow()
    document.last_accessed_by = UUID(current_user.get('id', str(tenant_id)))
    await db.commit()

    # Generate presigned URL for download
    presigned_url = storage_service.generate_signed_url(
        storage_path=document.s3_key,
        expiration=300,  # 5 minutes
        download=True
    )

    if not presigned_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )

    # Return redirect to presigned URL
    return JSONResponse(
        content={
            "download_url": presigned_url,
            "filename": document.filename,
            "expires_in": 300
        }
    )


@router.patch("/{document_id}", response_model=DocumentResponse)
@require_permission(ResourceType.DOCUMENTS, Action.UPDATE, context_loader=load_document_context)
async def update_document(
    document_id: UUID,
    document_update: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
) -> DocumentResponse:
    """
    Update document metadata (not the file itself).
    """

    # Get document
    query = select(Document).where(
        Document.id == document_id,
        Document.organization_id == tenant_id
    )
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Update fields
    update_data = document_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)

    document.modified_at = datetime.utcnow()

    await db.commit()
    await db.refresh(document)

    # Generate presigned URL
    presigned_url = storage_service.generate_signed_url(
        storage_path=document.s3_key,
        expiration=3600
    )

    doc_dict = document.to_dict()
    doc_dict['presigned_url'] = presigned_url

    return DocumentResponse(**doc_dict)


@router.delete("/{document_id}")
@require_permission(ResourceType.DOCUMENTS, Action.DELETE, context_loader=load_document_context)
async def delete_document(
    document_id: UUID,
    permanent: bool = Query(False, description="Permanently delete from S3"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Delete or archive a document.
    """

    # Get document
    query = select(Document).where(
        Document.id == document_id,
        Document.organization_id == tenant_id
    )
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if permanent:
        # Delete from S3
        storage_service.delete_document(document.s3_key)

        # Delete from database
        await db.delete(document)
    else:
        # Soft delete (archive)
        document.status = DocumentStatus.ARCHIVED
        document.modified_at = datetime.utcnow()

    await db.commit()

    return {"status": "success", "message": "Document deleted successfully"}


# Folder endpoints will be implemented later when DocumentFolder model is created