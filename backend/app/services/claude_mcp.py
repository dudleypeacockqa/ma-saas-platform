"""Claude MCP (Model Context Protocol) Integration Service for M&A Intelligence"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import asyncio
from datetime import datetime

import anthropic
from anthropic import AsyncAnthropic
import structlog

from app.core.config import settings
from app.services.prompts import MA_DOMAIN_PROMPTS


logger = structlog.get_logger(__name__)


@dataclass
class DealAnalysis:
    """Structure for M&A deal analysis results"""
    deal_id: str
    confidence_score: float
    strategic_value: float
    risk_assessment: Dict[str, float]
    recommendations: List[str]
    key_insights: List[str]
    red_flags: List[str]
    synergies: List[str]
    valuation_notes: str
    timestamp: datetime


@dataclass
class PartnershipRecommendation:
    """Structure for partnership recommendations"""
    partner_id: str
    compatibility_score: float
    strategic_fit: float
    influence_score: float
    synergy_areas: List[str]
    potential_value: str
    risk_factors: List[str]
    recommended_actions: List[str]


class ClaudeMCPService:
    """
    Claude MCP integration for M&A domain expertise and AI-powered analysis.
    Implements sophisticated deal analysis, partnership identification, and
    strategic recommendations using Claude's advanced capabilities.
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = settings.CLAUDE_MAX_TOKENS
        self.temperature = settings.CLAUDE_TEMPERATURE
        self._cache = {}  # Simple in-memory cache
        self._cache_ttl = 3600  # 1 hour

    async def analyze_deal(
        self,
        deal_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> DealAnalysis:
        """
        Perform comprehensive M&A deal analysis with strategic recommendations.

        Args:
            deal_data: Deal information including financials, terms, parties
            context: Additional context like market conditions, portfolio strategy

        Returns:
            DealAnalysis with insights and recommendations
        """
        try:
            # Build the analysis prompt
            prompt = MA_DOMAIN_PROMPTS["deal_analysis"].format(
                deal_data=json.dumps(deal_data, indent=2),
                context=json.dumps(context or {}, indent=2)
            )

            # Check cache
            cache_key = f"deal_analysis_{hash(prompt)}"
            if cache_key in self._cache:
                cached_result, timestamp = self._cache[cache_key]
                if (datetime.now() - timestamp).seconds < self._cache_ttl:
                    logger.info("Returning cached deal analysis", deal_id=deal_data.get("id"))
                    return cached_result

            # Make API call to Claude
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=settings.CLAUDE_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse the response
            analysis = self._parse_deal_analysis(response.content[0].text, deal_data.get("id", "unknown"))

            # Cache the result
            self._cache[cache_key] = (analysis, datetime.now())

            logger.info(
                "Deal analysis completed",
                deal_id=analysis.deal_id,
                confidence=analysis.confidence_score
            )

            return analysis

        except Exception as e:
            logger.error("Deal analysis failed", error=str(e), deal_data=deal_data)
            raise

    async def identify_partnerships(
        self,
        organization_profile: Dict[str, Any],
        search_criteria: Optional[Dict[str, Any]] = None
    ) -> List[PartnershipRecommendation]:
        """
        Identify and score potential partnerships using AI-powered matching.

        Args:
            organization_profile: Current organization's profile and objectives
            search_criteria: Specific criteria for partner search

        Returns:
            List of partnership recommendations ranked by compatibility
        """
        try:
            prompt = MA_DOMAIN_PROMPTS["partnership_identification"].format(
                organization=json.dumps(organization_profile, indent=2),
                criteria=json.dumps(search_criteria or {}, indent=2)
            )

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.5,  # Lower temperature for more consistent scoring
                system=settings.CLAUDE_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            partnerships = self._parse_partnership_recommendations(response.content[0].text)

            # Sort by compatibility score
            partnerships.sort(key=lambda x: x.compatibility_score, reverse=True)

            logger.info(
                "Partnership identification completed",
                organization=organization_profile.get("name"),
                recommendations_count=len(partnerships)
            )

            return partnerships

        except Exception as e:
            logger.error("Partnership identification failed", error=str(e))
            raise

    async def generate_strategic_insights(
        self,
        ecosystem_data: Dict[str, Any],
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate strategic insights from ecosystem intelligence data.

        Args:
            ecosystem_data: Market and ecosystem intelligence data
            focus_areas: Specific areas to focus analysis on

        Returns:
            Strategic insights and recommendations
        """
        try:
            prompt = MA_DOMAIN_PROMPTS["strategic_insights"].format(
                ecosystem_data=json.dumps(ecosystem_data, indent=2),
                focus_areas=", ".join(focus_areas) if focus_areas else "general market analysis"
            )

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=settings.CLAUDE_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            insights = self._parse_strategic_insights(response.content[0].text)

            logger.info("Strategic insights generated", focus_areas=focus_areas)

            return insights

        except Exception as e:
            logger.error("Strategic insights generation failed", error=str(e))
            raise

    async def optimize_deal_structure(
        self,
        deal_parameters: Dict[str, Any],
        optimization_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Optimize M&A deal structure based on specified goals.

        Args:
            deal_parameters: Current deal structure and terms
            optimization_goals: Goals like tax efficiency, risk mitigation, etc.

        Returns:
            Optimized deal structure with recommendations
        """
        try:
            prompt = MA_DOMAIN_PROMPTS["deal_optimization"].format(
                deal_parameters=json.dumps(deal_parameters, indent=2),
                goals=", ".join(optimization_goals)
            )

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.6,
                system=settings.CLAUDE_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            optimization = self._parse_deal_optimization(response.content[0].text)

            logger.info(
                "Deal structure optimized",
                original_value=deal_parameters.get("value"),
                optimization_goals=optimization_goals
            )

            return optimization

        except Exception as e:
            logger.error("Deal optimization failed", error=str(e))
            raise

    async def assess_integration_readiness(
        self,
        acquirer_profile: Dict[str, Any],
        target_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess post-merger integration readiness and identify key challenges.

        Args:
            acquirer_profile: Acquiring company profile
            target_profile: Target company profile

        Returns:
            Integration readiness assessment with action items
        """
        try:
            prompt = MA_DOMAIN_PROMPTS["integration_assessment"].format(
                acquirer=json.dumps(acquirer_profile, indent=2),
                target=json.dumps(target_profile, indent=2)
            )

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.5,
                system=settings.CLAUDE_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            assessment = self._parse_integration_assessment(response.content[0].text)

            logger.info(
                "Integration readiness assessed",
                acquirer=acquirer_profile.get("name"),
                target=target_profile.get("name")
            )

            return assessment

        except Exception as e:
            logger.error("Integration assessment failed", error=str(e))
            raise

    def _parse_deal_analysis(self, response_text: str, deal_id: str) -> DealAnalysis:
        """Parse Claude's response into structured DealAnalysis"""
        try:
            # Parse JSON response from Claude
            data = json.loads(response_text)

            return DealAnalysis(
                deal_id=deal_id,
                confidence_score=data.get("confidence_score", 0.0),
                strategic_value=data.get("strategic_value", 0.0),
                risk_assessment=data.get("risk_assessment", {}),
                recommendations=data.get("recommendations", []),
                key_insights=data.get("key_insights", []),
                red_flags=data.get("red_flags", []),
                synergies=data.get("synergies", []),
                valuation_notes=data.get("valuation_notes", ""),
                timestamp=datetime.now()
            )
        except json.JSONDecodeError:
            # Fallback for non-JSON responses
            return DealAnalysis(
                deal_id=deal_id,
                confidence_score=0.5,
                strategic_value=0.5,
                risk_assessment={"parsing_error": 1.0},
                recommendations=[response_text[:500]],
                key_insights=[],
                red_flags=["Unable to parse complete analysis"],
                synergies=[],
                valuation_notes="Analysis requires manual review",
                timestamp=datetime.now()
            )

    def _parse_partnership_recommendations(self, response_text: str) -> List[PartnershipRecommendation]:
        """Parse Claude's response into partnership recommendations"""
        try:
            data = json.loads(response_text)
            recommendations = []

            for item in data.get("recommendations", []):
                rec = PartnershipRecommendation(
                    partner_id=item.get("partner_id", ""),
                    compatibility_score=item.get("compatibility_score", 0.0),
                    strategic_fit=item.get("strategic_fit", 0.0),
                    influence_score=item.get("influence_score", 0.0),
                    synergy_areas=item.get("synergy_areas", []),
                    potential_value=item.get("potential_value", ""),
                    risk_factors=item.get("risk_factors", []),
                    recommended_actions=item.get("recommended_actions", [])
                )
                recommendations.append(rec)

            return recommendations

        except json.JSONDecodeError:
            logger.warning("Failed to parse partnership recommendations as JSON")
            return []

    def _parse_strategic_insights(self, response_text: str) -> Dict[str, Any]:
        """Parse strategic insights from Claude's response"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "insights": [response_text[:1000]],
                "recommendations": [],
                "market_trends": [],
                "opportunities": [],
                "threats": []
            }

    def _parse_deal_optimization(self, response_text: str) -> Dict[str, Any]:
        """Parse deal optimization recommendations"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "optimized_structure": {},
                "improvements": [],
                "estimated_savings": 0,
                "risk_reduction": 0,
                "implementation_steps": []
            }

    def _parse_integration_assessment(self, response_text: str) -> Dict[str, Any]:
        """Parse integration assessment from Claude's response"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "readiness_score": 0.5,
                "key_challenges": [],
                "success_factors": [],
                "risk_areas": [],
                "action_items": [],
                "timeline": "Not determined"
            }

    async def batch_analyze_deals(
        self,
        deals: List[Dict[str, Any]],
        batch_size: int = 5
    ) -> List[DealAnalysis]:
        """
        Analyze multiple deals in batches for efficiency.

        Args:
            deals: List of deal data to analyze
            batch_size: Number of concurrent analyses

        Returns:
            List of DealAnalysis results
        """
        results = []
        for i in range(0, len(deals), batch_size):
            batch = deals[i:i + batch_size]
            tasks = [self.analyze_deal(deal) for deal in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error("Batch deal analysis failed", error=str(result))
                else:
                    results.append(result)

        return results

    def clear_cache(self):
        """Clear the analysis cache"""
        self._cache.clear()
        logger.info("Claude MCP cache cleared")