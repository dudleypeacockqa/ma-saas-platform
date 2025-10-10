"""Embedding service for generating and managing document embeddings"""

import asyncio
from typing import List, Dict, Any, Optional
import hashlib
import json
from datetime import datetime

import openai
from openai import AsyncOpenAI
import tiktoken
import numpy as np
import structlog

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.document import Document


logger = structlog.get_logger(__name__)


class EmbeddingService:
    """
    Service for generating and managing document embeddings using OpenAI.
    Implements batch processing, caching, and semantic search capabilities.
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.EMBEDDING_MODEL
        self.dimensions = settings.EMBEDDING_DIMENSIONS
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self._cache = {}  # Simple in-memory cache
        self.max_tokens = 8191  # Maximum tokens for embedding model

    async def generate_embedding(self, text: str, cache: bool = True) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to generate embedding for
            cache: Whether to use caching

        Returns:
            List of float values representing the embedding
        """
        try:
            # Check cache
            if cache:
                cache_key = self._get_cache_key(text)
                if cache_key in self._cache:
                    logger.debug("Returning cached embedding", cache_key=cache_key[:8])
                    return self._cache[cache_key]

            # Truncate text if too long
            text = self._truncate_text(text)

            # Generate embedding
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )

            embedding = response.data[0].embedding

            # Cache the result
            if cache:
                self._cache[cache_key] = embedding

            return embedding

        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            raise

    async def batch_generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 20
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to generate embeddings for
            batch_size: Number of texts to process in each batch

        Returns:
            List of embeddings corresponding to input texts
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Truncate texts in batch
            batch = [self._truncate_text(text) for text in batch]

            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    encoding_format="float"
                )

                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

                logger.info(
                    "Batch embeddings generated",
                    batch_num=i // batch_size + 1,
                    batch_size=len(batch)
                )

            except Exception as e:
                logger.error(
                    "Batch embedding generation failed",
                    batch_num=i // batch_size + 1,
                    error=str(e)
                )
                # Add None for failed embeddings
                embeddings.extend([None] * len(batch))

        return embeddings

    async def process_document(
        self,
        document_id: str,
        content: str,
        title: str = "",
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> Dict[str, Any]:
        """
        Process a document by chunking and generating embeddings.

        Args:
            document_id: Document identifier
            content: Document content
            title: Document title
            chunk_size: Size of text chunks for embedding
            overlap: Overlap between chunks

        Returns:
            Dictionary with processing results
        """
        try:
            # Combine title and content for embedding
            full_text = f"{title}\n\n{content}" if title else content

            # Generate chunks if document is large
            chunks = self._create_chunks(full_text, chunk_size, overlap)

            # Generate embeddings for chunks
            chunk_embeddings = await self.batch_generate_embeddings(chunks)

            # Calculate average embedding for the document
            valid_embeddings = [e for e in chunk_embeddings if e is not None]
            if valid_embeddings:
                avg_embedding = np.mean(valid_embeddings, axis=0).tolist()
            else:
                # Fallback to single embedding
                avg_embedding = await self.generate_embedding(full_text[:self.max_tokens])

            result = {
                "document_id": document_id,
                "embedding": avg_embedding,
                "chunk_count": len(chunks),
                "chunk_embeddings": chunk_embeddings,
                "embedding_model": self.model,
                "generated_at": datetime.utcnow().isoformat()
            }

            logger.info(
                "Document processed",
                document_id=document_id,
                chunks=len(chunks),
                embedding_dim=len(avg_embedding)
            )

            return result

        except Exception as e:
            logger.error("Document processing failed", document_id=document_id, error=str(e))
            raise

    async def semantic_search(
        self,
        query: str,
        organization_id: str,
        limit: int = 10,
        threshold: float = 0.7,
        document_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using vector similarity.

        Args:
            query: Search query
            organization_id: Organization ID for multi-tenant isolation
            limit: Maximum number of results
            threshold: Similarity threshold (0-1)
            document_type: Optional filter by document type

        Returns:
            List of search results with similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)

            # Perform vector search in database
            async with AsyncSessionLocal() as session:
                # Build the search query
                sql = """
                    SELECT
                        id,
                        title,
                        content,
                        document_type,
                        1 - (embedding <=> :query_embedding::vector) AS similarity
                    FROM documents
                    WHERE
                        organization_id = :org_id
                        AND embedding IS NOT NULL
                        AND is_deleted = FALSE
                """

                params = {
                    "query_embedding": query_embedding,
                    "org_id": organization_id
                }

                if document_type:
                    sql += " AND document_type = :doc_type"
                    params["doc_type"] = document_type

                sql += f"""
                    AND 1 - (embedding <=> :query_embedding::vector) > :threshold
                    ORDER BY embedding <=> :query_embedding::vector
                    LIMIT :limit
                """
                params["threshold"] = threshold
                params["limit"] = limit

                result = await session.execute(sql, params)
                rows = result.fetchall()

                # Format results
                search_results = []
                for row in rows:
                    search_results.append({
                        "document_id": str(row.id),
                        "title": row.title,
                        "content_snippet": row.content[:500],
                        "document_type": row.document_type,
                        "similarity_score": float(row.similarity)
                    })

                logger.info(
                    "Semantic search completed",
                    query=query[:50],
                    results=len(search_results),
                    organization_id=organization_id
                )

                return search_results

        except Exception as e:
            logger.error("Semantic search failed", error=str(e), query=query)
            raise

    async def find_similar_documents(
        self,
        document_id: str,
        organization_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find documents similar to a given document.

        Args:
            document_id: Source document ID
            organization_id: Organization ID for multi-tenant isolation
            limit: Maximum number of similar documents

        Returns:
            List of similar documents with similarity scores
        """
        try:
            async with AsyncSessionLocal() as session:
                # Get the source document's embedding
                source_doc = await session.get(Document, document_id)
                if not source_doc or not source_doc.embedding:
                    return []

                # Find similar documents
                sql = """
                    SELECT
                        id,
                        title,
                        document_type,
                        1 - (embedding <=> :source_embedding::vector) AS similarity
                    FROM documents
                    WHERE
                        organization_id = :org_id
                        AND id != :doc_id
                        AND embedding IS NOT NULL
                        AND is_deleted = FALSE
                    ORDER BY embedding <=> :source_embedding::vector
                    LIMIT :limit
                """

                result = await session.execute(sql, {
                    "source_embedding": source_doc.embedding,
                    "org_id": organization_id,
                    "doc_id": document_id,
                    "limit": limit
                })
                rows = result.fetchall()

                similar_docs = []
                for row in rows:
                    similar_docs.append({
                        "document_id": str(row.id),
                        "title": row.title,
                        "document_type": row.document_type,
                        "similarity_score": float(row.similarity)
                    })

                return similar_docs

        except Exception as e:
            logger.error("Similar documents search failed", error=str(e), document_id=document_id)
            raise

    def _truncate_text(self, text: str) -> str:
        """Truncate text to fit within model's token limit"""
        tokens = self.encoding.encode(text)
        if len(tokens) > self.max_tokens:
            tokens = tokens[:self.max_tokens]
            text = self.encoding.decode(tokens)
        return text

    def _create_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Create overlapping chunks from text"""
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap

        return chunks

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(f"{text}_{self.model}".encode()).hexdigest()

    def clear_cache(self):
        """Clear the embedding cache"""
        self._cache.clear()
        logger.info("Embedding cache cleared")

    async def update_document_embedding(
        self,
        document_id: str,
        embedding: List[float]
    ) -> None:
        """
        Update a document's embedding in the database.

        Args:
            document_id: Document ID
            embedding: Embedding vector
        """
        try:
            async with AsyncSessionLocal() as session:
                document = await session.get(Document, document_id)
                if document:
                    document.embedding = embedding
                    document.embedding_model = self.model
                    document.embedding_generated_at = datetime.utcnow()
                    await session.commit()

                    logger.info("Document embedding updated", document_id=document_id)

        except Exception as e:
            logger.error("Failed to update document embedding", error=str(e), document_id=document_id)
            raise