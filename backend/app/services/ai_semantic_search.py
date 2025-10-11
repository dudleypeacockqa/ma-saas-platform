"""AI-powered semantic search integration with Claude MCP and vector database"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio
import json
import numpy as np
import structlog

from app.services.claude_mcp import ClaudeMCPService
from app.services.embeddings import EmbeddingService
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.deal import Deal

logger = structlog.get_logger(__name__)


class AISemanticSearchService:
    """
    Integrates Claude MCP with vector database for intelligent semantic search.
    Combines AI analysis with similarity search for enhanced M&A insights.
    """

    def __init__(self):
        self.claude_service = ClaudeMCPService()
        self.embedding_service = EmbeddingService()
        self._context_cache = {}

    async def intelligent_deal_search(
        self,
        query: str,
        organization_id: str,
        search_context: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Perform intelligent deal search combining semantic search with AI analysis.

        Args:
            query: Search query
            organization_id: Organization ID for tenant isolation
            search_context: Additional context for AI analysis
            limit: Maximum number of results

        Returns:
            Search results with AI-enhanced insights
        """
        try:
            # Step 1: Generate query embedding
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Step 2: Perform vector similarity search
            similar_documents = await self._vector_search(
                query_embedding,
                organization_id,
                limit * 2  # Get more for AI filtering
            )

            # Step 3: Extract deal data from similar documents
            deal_candidates = await self._extract_deal_data(similar_documents)

            # Step 4: Use Claude to analyze and rank results
            ai_analysis = await self.claude_service.analyze_deal(
                {
                    "query": query,
                    "candidates": deal_candidates,
                    "context": search_context
                }
            )

            # Step 5: Combine results with AI insights
            enhanced_results = await self._enhance_with_ai_insights(
                similar_documents[:limit],
                ai_analysis
            )

            # Step 6: Generate strategic recommendations
            recommendations = await self._generate_search_recommendations(
                query,
                enhanced_results,
                search_context
            )

            return {
                "query": query,
                "results": enhanced_results,
                "ai_insights": {
                    "confidence_score": ai_analysis.confidence_score,
                    "strategic_value": ai_analysis.strategic_value,
                    "key_insights": ai_analysis.key_insights[:3]
                },
                "recommendations": recommendations,
                "total_analyzed": len(deal_candidates),
                "search_timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("Intelligent deal search failed", error=str(e))
            raise

    async def find_similar_deals_with_ai(
        self,
        deal_id: str,
        organization_id: str,
        analysis_depth: str = "standard"
    ) -> Dict[str, Any]:
        """
        Find similar deals using vector similarity and AI analysis.

        Args:
            deal_id: Source deal ID
            organization_id: Organization ID
            analysis_depth: Level of AI analysis (quick/standard/deep)

        Returns:
            Similar deals with AI comparison insights
        """
        try:
            # Get source deal embedding
            source_embedding = await self._get_deal_embedding(deal_id)

            if not source_embedding:
                return {"error": "Source deal not found or has no embedding"}

            # Find similar deals via vector search
            similar_deals = await self._vector_search(
                source_embedding,
                organization_id,
                limit=20
            )

            # Perform AI comparison analysis
            comparisons = []
            for deal in similar_deals[:10]:
                comparison = await self._ai_compare_deals(
                    deal_id,
                    deal["document_id"],
                    analysis_depth
                )
                comparisons.append({
                    **deal,
                    "ai_comparison": comparison
                })

            # Sort by combined score (similarity + strategic fit)
            comparisons.sort(
                key=lambda x: (
                    x["similarity_score"] * 0.5 +
                    x["ai_comparison"].get("strategic_fit", 0) * 0.5
                ),
                reverse=True
            )

            return {
                "source_deal_id": deal_id,
                "similar_deals": comparisons[:5],
                "analysis_depth": analysis_depth,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("Similar deals search failed", error=str(e))
            raise

    async def ecosystem_intelligence_search(
        self,
        focus_areas: List[str],
        organization_id: str,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Perform ecosystem intelligence search combining multiple data sources.

        Args:
            focus_areas: Areas of focus for intelligence gathering
            organization_id: Organization ID
            time_range: Optional time range filter

        Returns:
            Comprehensive ecosystem intelligence report
        """
        try:
            # Generate embeddings for each focus area
            focus_embeddings = await asyncio.gather(*[
                self.embedding_service.generate_embedding(area)
                for area in focus_areas
            ])

            # Search for relevant documents across all focus areas
            all_results = []
            for area, embedding in zip(focus_areas, focus_embeddings):
                results = await self._vector_search(
                    embedding,
                    organization_id,
                    limit=15
                )
                all_results.extend(results)

            # Deduplicate and aggregate results
            unique_results = self._deduplicate_results(all_results)

            # Generate ecosystem intelligence using Claude
            ecosystem_data = {
                "focus_areas": focus_areas,
                "document_count": len(unique_results),
                "time_range": {
                    "start": time_range[0].isoformat() if time_range else None,
                    "end": time_range[1].isoformat() if time_range else None
                },
                "key_findings": self._extract_key_findings(unique_results)
            }

            strategic_insights = await self.claude_service.generate_strategic_insights(
                ecosystem_data,
                focus_areas
            )

            return {
                "focus_areas": focus_areas,
                "intelligence_summary": strategic_insights,
                "document_sources": len(unique_results),
                "confidence_level": self._calculate_confidence(unique_results),
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("Ecosystem intelligence search failed", error=str(e))
            raise

    async def partnership_opportunity_search(
        self,
        organization_profile: Dict[str, Any],
        search_criteria: Dict[str, Any],
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Search for partnership opportunities using AI and semantic search.

        Args:
            organization_profile: Profile of searching organization
            search_criteria: Partnership search criteria
            organization_id: Organization ID

        Returns:
            Partnership opportunities with AI scoring
        """
        try:
            # Generate search embedding from criteria
            search_text = self._build_partnership_search_text(search_criteria)
            search_embedding = await self.embedding_service.generate_embedding(search_text)

            # Search for potential partners
            potential_partners = await self._vector_search(
                search_embedding,
                organization_id,
                limit=30
            )

            # Use Claude to identify and score partnerships
            partnerships = await self.claude_service.identify_partnerships(
                organization_profile,
                {
                    **search_criteria,
                    "candidates": potential_partners
                }
            )

            # Enhance with semantic relevance scores
            enhanced_partnerships = []
            for partnership in partnerships:
                # Find matching document from search results
                matching_doc = next(
                    (doc for doc in potential_partners
                     if doc.get("document_id") == partnership.partner_id),
                    None
                )

                enhanced_partnerships.append({
                    "partner_id": partnership.partner_id,
                    "compatibility_score": partnership.compatibility_score,
                    "strategic_fit": partnership.strategic_fit,
                    "influence_score": partnership.influence_score,
                    "semantic_relevance": matching_doc["similarity_score"] if matching_doc else 0,
                    "synergy_areas": partnership.synergy_areas,
                    "potential_value": partnership.potential_value,
                    "risk_factors": partnership.risk_factors,
                    "recommended_actions": partnership.recommended_actions,
                    "combined_score": (
                        partnership.compatibility_score * 0.4 +
                        partnership.strategic_fit * 0.3 +
                        partnership.influence_score * 0.2 +
                        (matching_doc["similarity_score"] if matching_doc else 0) * 0.1
                    )
                })

            # Sort by combined score
            enhanced_partnerships.sort(key=lambda x: x["combined_score"], reverse=True)

            return {
                "search_criteria": search_criteria,
                "partnerships_found": len(enhanced_partnerships),
                "top_opportunities": enhanced_partnerships[:10],
                "search_quality": self._assess_search_quality(enhanced_partnerships),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("Partnership opportunity search failed", error=str(e))
            raise

    async def _vector_search(
        self,
        embedding: List[float],
        organization_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search in database"""
        async with SessionLocal() as session:
            # This would use actual SQL with pgvector
            # Simplified for demonstration
            results = []
            # Query would be:
            # SELECT *, 1 - (embedding <=> :query_embedding) as similarity
            # FROM documents
            # WHERE organization_id = :org_id
            # ORDER BY embedding <=> :query_embedding
            # LIMIT :limit

            return results

    async def _extract_deal_data(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract deal data from documents"""
        deals = []
        for doc in documents:
            # Extract structured deal information
            deal_data = {
                "document_id": doc["document_id"],
                "title": doc.get("title"),
                "content": doc.get("content_snippet"),
                "similarity_score": doc.get("similarity_score", 0),
                "metadata": doc.get("metadata", {})
            }
            deals.append(deal_data)
        return deals

    async def _enhance_with_ai_insights(
        self,
        search_results: List[Dict[str, Any]],
        ai_analysis: Any
    ) -> List[Dict[str, Any]]:
        """Enhance search results with AI insights"""
        enhanced = []
        for result in search_results:
            enhanced.append({
                **result,
                "ai_insights": {
                    "relevance": ai_analysis.confidence_score,
                    "strategic_value": ai_analysis.strategic_value,
                    "risk_factors": ai_analysis.risk_assessment
                }
            })
        return enhanced

    async def _generate_search_recommendations(
        self,
        query: str,
        results: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate strategic recommendations based on search results"""
        if not results:
            return ["Consider broadening search criteria", "Review alternative keywords"]

        recommendations = []
        if len(results) < 5:
            recommendations.append("Limited results found - consider expanding search parameters")

        # Add context-specific recommendations
        if context and context.get("deal_size"):
            recommendations.append(f"Focus on deals within {context['deal_size']} range")

        return recommendations[:5]

    async def _get_deal_embedding(self, deal_id: str) -> Optional[List[float]]:
        """Get embedding for a specific deal"""
        async with SessionLocal() as session:
            # Query for deal document embedding
            # This would fetch from database
            return None

    async def _ai_compare_deals(
        self,
        deal1_id: str,
        deal2_id: str,
        analysis_depth: str
    ) -> Dict[str, Any]:
        """Compare two deals using AI analysis"""
        # Simplified comparison logic
        return {
            "strategic_fit": 0.85,
            "synergies": ["Market overlap", "Technology alignment"],
            "differences": ["Deal size", "Geography"],
            "recommendation": "Strong compatibility"
        }

    def _deduplicate_results(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate results"""
        seen = set()
        unique = []
        for result in results:
            doc_id = result.get("document_id")
            if doc_id and doc_id not in seen:
                seen.add(doc_id)
                unique.append(result)
        return unique

    def _extract_key_findings(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract key findings from documents"""
        findings = []
        for doc in documents[:5]:
            if doc.get("title"):
                findings.append(doc["title"])
        return findings

    def _calculate_confidence(
        self,
        results: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence level based on results"""
        if not results:
            return 0.0

        avg_similarity = sum(r.get("similarity_score", 0) for r in results) / len(results)
        return min(avg_similarity * 1.2, 1.0)  # Scale and cap at 1.0

    def _build_partnership_search_text(
        self,
        criteria: Dict[str, Any]
    ) -> str:
        """Build search text from partnership criteria"""
        parts = []
        if criteria.get("industry"):
            parts.append(f"Industry: {criteria['industry']}")
        if criteria.get("capabilities"):
            parts.append(f"Capabilities: {', '.join(criteria['capabilities'])}")
        if criteria.get("geography"):
            parts.append(f"Geography: {criteria['geography']}")
        return " ".join(parts)

    def _assess_search_quality(
        self,
        results: List[Dict[str, Any]]
    ) -> str:
        """Assess the quality of search results"""
        if not results:
            return "No results"

        avg_score = sum(r.get("combined_score", 0) for r in results) / len(results)

        if avg_score > 0.8:
            return "Excellent"
        elif avg_score > 0.6:
            return "Good"
        elif avg_score > 0.4:
            return "Fair"
        else:
            return "Poor"