"""
Pydantic schemas for Document API validation
Story 3.1: Document Upload API - Request/Response schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.documents import DocumentCategory, DocumentStatus


class DocumentBase(BaseModel):
    """Base document schema"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    document_type: Optional[DocumentCategory] = DocumentCategory.OTHER
    folder_path: str = Field("/", max_length=500)
    deal_id: Optional[UUID] = None
    tags: List[str] = Field(default_factory=list)
    is_confidential: bool = True
    document_metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class DocumentCreate(DocumentBase):
    """Schema for creating a document (metadata only, file uploaded separately)"""
    pass


class DocumentUpdate(BaseModel):
    """Schema for updating document metadata"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    document_type: Optional[DocumentCategory] = None
    folder_path: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    is_confidential: Optional[bool] = None
    document_metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: UUID
    filename: str
    original_filename: str
    file_extension: str
    mime_type: str
    file_size: int
    document_type: str
    status: str
    folder_path: str
    deal_id: Optional[UUID] = None
    version: int
    is_latest_version: bool
    is_confidential: bool
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str]
    uploaded_at: datetime
    modified_at: datetime
    download_count: int
    view_count: int
    presigned_url: Optional[str] = None  # Added for frontend access

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """Schema for paginated document list"""
    data: List[DocumentResponse]
    pagination: Dict[str, Any] = Field(
        ...,
        example={
            "page": 1,
            "per_page": 20,
            "total": 100,
            "pages": 5
        }
    )

    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseModel):
    """Response after successful upload"""
    document_id: UUID
    filename: str
    file_size: int
    mime_type: str
    s3_key: str
    presigned_url: Optional[str] = None
    status: str
    message: str

    model_config = ConfigDict(from_attributes=True)


class FolderBase(BaseModel):
    """Base folder schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    deal_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class FolderCreate(FolderBase):
    """Schema for creating a folder"""
    parent_path: str = Field("/", max_length=500)


class FolderUpdate(BaseModel):
    """Schema for updating a folder"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class FolderResponse(BaseModel):
    """Schema for folder response"""
    id: UUID
    name: str
    path: str
    parent_id: Optional[UUID] = None
    deal_id: Optional[UUID] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_system_folder: bool
    is_readonly: bool
    created_at: datetime
    modified_at: datetime
    document_count: int
    total_size: int

    model_config = ConfigDict(from_attributes=True)


class DocumentSearchParams(BaseModel):
    """Search parameters for documents"""
    search: Optional[str] = None
    deal_id: Optional[UUID] = None
    folder_path: Optional[str] = "/"
    document_type: Optional[DocumentCategory] = None
    tags: Optional[List[str]] = None
    is_confidential: Optional[bool] = None
    uploaded_after: Optional[datetime] = None
    uploaded_before: Optional[datetime] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class DocumentBulkOperation(BaseModel):
    """Schema for bulk document operations"""
    operation: str = Field(..., pattern="^(move|delete|archive|update_tags)$")
    document_ids: List[UUID] = Field(..., min_length=1)
    data: Optional[Dict[str, Any]] = None

    @field_validator('data')
    def validate_operation_data(cls, v, info):
        """Validate that certain operations include required data"""
        operation = info.data.get('operation')
        if operation in ['move', 'update_tags'] and not v:
            raise ValueError(f"Operation '{operation}' requires data")
        return v


class DocumentVersionInfo(BaseModel):
    """Information about document versions"""
    id: UUID
    version: int
    filename: str
    file_size: int
    uploaded_at: datetime
    uploaded_by: UUID
    is_latest: bool
    changes_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentStatistics(BaseModel):
    """Document statistics for dashboard"""
    total_documents: int
    total_size: int
    by_type: Dict[str, int]
    by_deal: Dict[str, int]
    recent_uploads: List[DocumentResponse]
    most_accessed: List[DocumentResponse]

    model_config = ConfigDict(from_attributes=True)