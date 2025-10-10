"""Search and semantic query API endpoints"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
import structlog

from app.services.embeddings import EmbeddingService
from app.api.deps import get_current_user, get_db
from app.core.database import AsyncSession
from app.models.document import Document


logger = structlog.get_logger(__name__)

router = APIRouter()


class SemanticSearchRequest(BaseModel):
    """Request model for semantic search"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    document_type: Optional[str] = Field(None, description="Filter by document type")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold")


class SearchResult(BaseModel):
    """Search result model"""
    document_id: str
    title: str
    content_snippet: str
    document_type: str
    similarity_score: float
    metadata: Optional[Dict[str, Any]] = None


class DocumentUploadRequest(BaseModel):
    """Request model for document upload with embedding"""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    document_type: str = Field(..., description="Type of document (deal, report, presentation, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: Optional[List[str]] = Field(None, description="Document tags")
    deal_id: Optional[str] = Field(None, description="Associated deal ID")
    partnership_id: Optional[str] = Field(None, description="Associated partnership ID")


class SimilarDocumentsRequest(BaseModel):
    """Request model for finding similar documents"""
    document_id: str = Field(..., description="Source document ID")
    limit: int = Field(5, ge=1, le=20, description="Maximum number of similar documents")


@router.post("/semantic", response_model=List[SearchResult])
async def semantic_search(
    request: SemanticSearchRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform semantic search using vector embeddings.

    This endpoint searches documents based on semantic similarity
    using AI-generated embeddings, providing more intelligent results
    than traditional keyword search.
    """
    try:
        embedding_service = EmbeddingService()

        results = await embedding_service.semantic_search(
            query=request.query,
            organization_id=str(current_user.organization_id),
            limit=request.limit,
            threshold=request.threshold,
            document_type=request.document_type
        )

        # Convert to response model
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                document_id=result["document_id"],
                title=result["title"],
                content_snippet=result["content_snippet"],
                document_type=result["document_type"],
                similarity_score=result["similarity_score"]
            ))

        logger.info(
            "Semantic search completed",
            user_id=current_user.id,
            query=request.query[:50],
            results=len(search_results)
        )

        return search_results

    except Exception as e:
        logger.error("Semantic search failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed. Please try again."
        )


@router.get("/fulltext")
async def fulltext_search(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Results offset for pagination"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform full-text search on documents.

    This endpoint uses PostgreSQL's full-text search capabilities
    for fast keyword-based searching with ranking and stemming support.
    """
    try:
        # Build the search query
        query = f"""
            SELECT
                id,
                title,
                content,
                document_type,
                ts_rank_cd(
                    to_tsvector('english', title || ' ' || content),
                    plainto_tsquery('english', :search_query)
                ) AS rank
            FROM documents
            WHERE
                organization_id = :org_id
                AND to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', :search_query)
                AND is_deleted = FALSE
        """

        params = {
            "search_query": q,
            "org_id": str(current_user.organization_id)
        }

        if document_type:
            query += " AND document_type = :doc_type"
            params["doc_type"] = document_type

        query += """
            ORDER BY rank DESC
            LIMIT :limit OFFSET :offset
        """
        params["limit"] = limit
        params["offset"] = offset

        result = await db.execute(query, params)
        rows = result.fetchall()

        # Format results
        search_results = []
        for row in rows:
            search_results.append({
                "document_id": str(row.id),
                "title": row.title,
                "content_snippet": row.content[:500],
                "document_type": row.document_type,
                "relevance_score": float(row.rank)
            })

        return {
            "results": search_results,
            "total": len(search_results),
            "query": q,
            "offset": offset,
            "limit": limit
        }

    except Exception as e:
        logger.error("Fulltext search failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed. Please try again."
        )


@router.post("/upload-document")
async def upload_document_with_embedding(
    request: DocumentUploadRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document and generate its embedding for semantic search.

    This endpoint creates a new document, generates its vector embedding,
    and stores it for future semantic search and similarity matching.
    """
    try:
        embedding_service = EmbeddingService()

        # Generate embedding for the document
        result = await embedding_service.process_document(
            document_id="temp",  # Will be replaced with actual ID
            content=request.content,
            title=request.title
        )

        # Create document in database
        document = Document(
            organization_id=current_user.organization_id,
            owner_id=current_user.id,
            title=request.title,
            content=request.content,
            document_type=request.document_type,
            embedding=result["embedding"],
            embedding_model=result["embedding_model"],
            embedding_generated_at=result["generated_at"],
            metadata=request.metadata,
            tags=request.tags,
            deal_id=request.deal_id,
            partnership_id=request.partnership_id
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        logger.info(
            "Document uploaded with embedding",
            document_id=str(document.id),
            user_id=current_user.id
        )

        return {
            "document_id": str(document.id),
            "title": document.title,
            "document_type": document.document_type,
            "embedding_generated": True,
            "embedding_model": result["embedding_model"]
        }

    except Exception as e:
        logger.error("Document upload failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document. Please try again."
        )


@router.post("/similar-documents", response_model=List[Dict[str, Any]])
async def find_similar_documents(
    request: SimilarDocumentsRequest,
    current_user=Depends(get_current_user)
):
    """
    Find documents similar to a given document.

    This endpoint uses vector similarity to find documents that are
    semantically similar to the specified document, useful for finding
    related deals, reports, or partnerships.
    """
    try:
        embedding_service = EmbeddingService()

        similar_docs = await embedding_service.find_similar_documents(
            document_id=request.document_id,
            organization_id=str(current_user.organization_id),
            limit=request.limit
        )

        logger.info(
            "Similar documents found",
            source_document_id=request.document_id,
            results=len(similar_docs),
            user_id=current_user.id
        )

        return similar_docs

    except Exception as e:
        logger.error("Similar documents search failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find similar documents. Please try again."
        )


@router.post("/batch-embed")
async def batch_generate_embeddings(
    document_ids: List[str],
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate embeddings for multiple documents in batch.

    This endpoint processes multiple documents efficiently,
    generating embeddings for documents that don't have them yet.
    """
    try:
        embedding_service = EmbeddingService()
        processed_count = 0
        failed_count = 0

        for doc_id in document_ids:
            try:
                # Get document from database
                document = await db.get(Document, doc_id)
                if not document or document.organization_id != current_user.organization_id:
                    failed_count += 1
                    continue

                # Skip if already has embedding
                if document.embedding:
                    continue

                # Generate embedding
                result = await embedding_service.process_document(
                    document_id=str(document.id),
                    content=document.content,
                    title=document.title
                )

                # Update document
                document.embedding = result["embedding"]
                document.embedding_model = result["embedding_model"]
                document.embedding_generated_at = result["generated_at"]
                processed_count += 1

            except Exception as e:
                logger.error("Failed to process document", document_id=doc_id, error=str(e))
                failed_count += 1

        await db.commit()

        return {
            "total_documents": len(document_ids),
            "processed": processed_count,
            "failed": failed_count,
            "already_embedded": len(document_ids) - processed_count - failed_count
        }

    except Exception as e:
        logger.error("Batch embedding failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch embedding failed. Please try again."
        )


@router.get("/search-filters")
async def get_search_filters(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available search filters and facets.

    Returns document types, tags, and other filterable attributes
    available in the user's organization.
    """
    try:
        # Get unique document types
        doc_types_query = """
            SELECT DISTINCT document_type, COUNT(*) as count
            FROM documents
            WHERE organization_id = :org_id AND is_deleted = FALSE
            GROUP BY document_type
            ORDER BY count DESC
        """
        doc_types_result = await db.execute(doc_types_query, {"org_id": str(current_user.organization_id)})
        doc_types = [{"type": row.document_type, "count": row.count} for row in doc_types_result]

        # Get popular tags
        tags_query = """
            SELECT jsonb_array_elements_text(tags) as tag, COUNT(*) as count
            FROM documents
            WHERE organization_id = :org_id AND tags IS NOT NULL AND is_deleted = FALSE
            GROUP BY tag
            ORDER BY count DESC
            LIMIT 20
        """
        tags_result = await db.execute(tags_query, {"org_id": str(current_user.organization_id)})
        popular_tags = [{"tag": row.tag, "count": row.count} for row in tags_result]

        return {
            "document_types": doc_types,
            "popular_tags": popular_tags,
            "total_documents": sum(dt["count"] for dt in doc_types)
        }

    except Exception as e:
        logger.error("Failed to get search filters", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get search filters."
        )