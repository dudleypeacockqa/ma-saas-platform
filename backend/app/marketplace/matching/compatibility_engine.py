"""
Intelligent Compatibility Engine
AI-powered buyer-seller matching with detailed reasoning
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import json

logger = logging.getLogger(__name__)

class CompatibilityDimension(Enum):
    """Dimensions of buyer-seller compatibility"""
    STRATEGIC_FIT = "strategic_fit"
    CULTURAL_ALIGNMENT = "cultural_alignment"
    FINANCIAL_CAPACITY = "financial_capacity"
    GEOGRAPHIC_SYNERGY = "geographic_synergy"
    OPERATIONAL_SYNERGY = "operational_synergy"
    REGULATORY_ALIGNMENT = "regulatory_alignment"
    TIMING_ALIGNMENT = "timing_alignment"

class RiskFactor(Enum):
    """Risk factors in M&A transactions"""
    INTEGRATION_COMPLEXITY = "integration_complexity"
    CULTURAL_MISMATCH = "cultural_mismatch"
    REGULATORY_HURDLES = "regulatory_hurdles"
    VALUATION_GAP = "valuation_gap"
    FINANCING_RISK = "financing_risk"
    MARKET_VOLATILITY = "market_volatility"
    COMPETITIVE_THREATS = "competitive_threats"

@dataclass
class BuyerProfile:
    """Comprehensive buyer profile for matching"""
    buyer_id: str
    company_name: str
    industry_sectors: List[str]
    geographic_focus: List[str]
    deal_size_range: Tuple[float, float]
    acquisition_strategy: str
    cultural_values: Dict[str, float]
    integration_capabilities: Dict[str, float]
    financial_capacity: Dict[str, float]
    historical_deals: List[Dict[str, Any]]
    investment_criteria: Dict[str, Any]
    timeline_preferences: Dict[str, Any]

@dataclass
class SellerProfile:
    """Comprehensive seller profile for matching"""
    seller_id: str
    company_name: str
    industry_sector: str
    geography: str
    company_size: Dict[str, float]
    business_model: str
    cultural_attributes: Dict[str, float]
    financial_performance: Dict[str, float]
    strategic_assets: List[str]
    sale_motivations: List[str]
    timeline_constraints: Dict[str, Any]
    valuation_expectations: Dict[str, float]

@dataclass
class CompatibilityScore:
    """Detailed compatibility assessment"""
    overall_score: float
    dimension_scores: Dict[CompatibilityDimension, float]
    reasoning: str
    synergy_opportunities: List[str]
    risk_factors: List[RiskFactor]
    success_probability: float
    recommended_structure: Dict[str, Any]
    negotiation_strategy: Dict[str, Any]

@dataclass
class MatchResult:
    """Complete matching result with analysis"""
    match_id: str
    buyer_profile: BuyerProfile
    seller_profile: SellerProfile
    compatibility_score: CompatibilityScore
    valuation_analysis: Dict[str, Any]
    market_context: Dict[str, Any]
    generated_at: datetime

class CompatibilityEngine:
    """
    AI-Powered Compatibility Engine
    Intelligent matching of buyers and sellers with detailed reasoning
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self.similarity_weights = {
            CompatibilityDimension.STRATEGIC_FIT: 0.25,
            CompatibilityDimension.CULTURAL_ALIGNMENT: 0.15,
            CompatibilityDimension.FINANCIAL_CAPACITY: 0.20,
            CompatibilityDimension.GEOGRAPHIC_SYNERGY: 0.10,
            CompatibilityDimension.OPERATIONAL_SYNERGY: 0.15,
            CompatibilityDimension.REGULATORY_ALIGNMENT: 0.10,
            CompatibilityDimension.TIMING_ALIGNMENT: 0.05
        }

    async def find_compatible_matches(
        self,
        target_profile: BuyerProfile | SellerProfile,
        candidate_pool: List[BuyerProfile | SellerProfile],
        max_matches: int = 50
    ) -> List[MatchResult]:
        """
        Find compatible matches using AI-powered analysis

        Args:
            target_profile: Profile to find matches for
            candidate_pool: Pool of candidates to match against
            max_matches: Maximum number of matches to return

        Returns:
            List of ranked match results with detailed analysis
        """
        try:
            matches = []

            # Analyze each candidate
            for candidate in candidate_pool:
                if isinstance(target_profile, BuyerProfile) and isinstance(candidate, SellerProfile):
                    match_result = await self._analyze_buyer_seller_match(target_profile, candidate)
                elif isinstance(target_profile, SellerProfile) and isinstance(candidate, BuyerProfile):
                    match_result = await self._analyze_buyer_seller_match(candidate, target_profile)
                else:
                    continue  # Skip same-type matches

                if match_result.compatibility_score.overall_score > 0.6:  # Minimum threshold
                    matches.append(match_result)

            # Sort by overall compatibility score
            matches.sort(key=lambda x: x.compatibility_score.overall_score, reverse=True)

            logger.info(f"Found {len(matches)} compatible matches from {len(candidate_pool)} candidates")
            return matches[:max_matches]

        except Exception as e:
            logger.error(f"Compatibility matching failed: {str(e)}")
            raise

    async def _analyze_buyer_seller_match(
        self,
        buyer: BuyerProfile,
        seller: SellerProfile
    ) -> MatchResult:
        """
        Perform comprehensive buyer-seller compatibility analysis

        Args:
            buyer: Buyer profile
            seller: Seller profile

        Returns:
            Detailed match result with compatibility analysis
        """
        try:
            # Calculate compatibility across all dimensions
            dimension_scores = {}

            # Strategic fit analysis
            dimension_scores[CompatibilityDimension.STRATEGIC_FIT] = await self._analyze_strategic_fit(buyer, seller)

            # Cultural alignment analysis
            dimension_scores[CompatibilityDimension.CULTURAL_ALIGNMENT] = await self._analyze_cultural_alignment(buyer, seller)

            # Financial capacity analysis
            dimension_scores[CompatibilityDimension.FINANCIAL_CAPACITY] = await self._analyze_financial_capacity(buyer, seller)

            # Geographic synergy analysis
            dimension_scores[CompatibilityDimension.GEOGRAPHIC_SYNERGY] = await self._analyze_geographic_synergy(buyer, seller)

            # Operational synergy analysis
            dimension_scores[CompatibilityDimension.OPERATIONAL_SYNERGY] = await self._analyze_operational_synergy(buyer, seller)

            # Regulatory alignment analysis
            dimension_scores[CompatibilityDimension.REGULATORY_ALIGNMENT] = await self._analyze_regulatory_alignment(buyer, seller)

            # Timing alignment analysis
            dimension_scores[CompatibilityDimension.TIMING_ALIGNMENT] = await self._analyze_timing_alignment(buyer, seller)

            # Calculate overall compatibility score
            overall_score = sum(
                score * self.similarity_weights[dimension]
                for dimension, score in dimension_scores.items()
            )

            # Generate detailed reasoning
            reasoning = await self._generate_compatibility_reasoning(buyer, seller, dimension_scores)

            # Identify synergy opportunities
            synergy_opportunities = await self._identify_synergy_opportunities(buyer, seller, dimension_scores)

            # Assess risk factors
            risk_factors = await self._assess_risk_factors(buyer, seller, dimension_scores)

            # Calculate success probability
            success_probability = await self._calculate_success_probability(dimension_scores, risk_factors)

            # Generate deal structure recommendations
            recommended_structure = await self._recommend_deal_structure(buyer, seller, dimension_scores)

            # Generate negotiation strategy
            negotiation_strategy = await self._generate_negotiation_strategy(buyer, seller, dimension_scores)

            # Perform valuation analysis
            valuation_analysis = await self._perform_valuation_analysis(buyer, seller)

            # Get market context
            market_context = await self._get_market_context(buyer, seller)

            # Create compatibility score object
            compatibility_score = CompatibilityScore(
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                reasoning=reasoning,
                synergy_opportunities=synergy_opportunities,
                risk_factors=risk_factors,
                success_probability=success_probability,
                recommended_structure=recommended_structure,
                negotiation_strategy=negotiation_strategy
            )

            # Create match result
            match_result = MatchResult(
                match_id=f"match_{buyer.buyer_id}_{seller.seller_id}_{int(datetime.now().timestamp())}",
                buyer_profile=buyer,
                seller_profile=seller,
                compatibility_score=compatibility_score,
                valuation_analysis=valuation_analysis,
                market_context=market_context,
                generated_at=datetime.now()
            )

            return match_result

        except Exception as e:
            logger.error(f"Match analysis failed for buyer {buyer.buyer_id} and seller {seller.seller_id}: {str(e)}")
            raise

    async def _analyze_strategic_fit(self, buyer: BuyerProfile, seller: SellerProfile) -> float:
        """
        Analyze strategic fit between buyer and seller

        Factors:
        - Industry alignment
        - Business model compatibility
        - Strategic asset complementarity
        - Market expansion opportunities
        - Competitive positioning
        """
        try:
            strategic_score = 0.0

            # Industry alignment (40% weight)
            industry_alignment = self._calculate_industry_alignment(buyer.industry_sectors, seller.industry_sector)
            strategic_score += 0.4 * industry_alignment

            # Strategic asset alignment (30% weight)
            asset_alignment = self._calculate_asset_alignment(buyer.investment_criteria, seller.strategic_assets)
            strategic_score += 0.3 * asset_alignment

            # Market expansion potential (20% weight)
            expansion_potential = self._calculate_expansion_potential(buyer.geographic_focus, seller.geography)
            strategic_score += 0.2 * expansion_potential

            # Acquisition strategy alignment (10% weight)
            strategy_alignment = self._calculate_strategy_alignment(buyer.acquisition_strategy, seller.business_model)
            strategic_score += 0.1 * strategy_alignment

            return min(strategic_score, 1.0)

        except Exception as e:
            logger.error(f"Strategic fit analysis failed: {str(e)}")
            return 0.5  # Default moderate score

    async def _analyze_cultural_alignment(self, buyer: BuyerProfile, seller: SellerProfile) -> float:
        """
        Analyze cultural compatibility between organizations

        Factors:
        - Leadership styles
        - Decision-making processes
        - Risk tolerance
        - Innovation culture
        - Employee values
        """
        try:
            # Calculate cultural distance using cosine similarity
            buyer_values = np.array(list(buyer.cultural_values.values()))
            seller_values = np.array(list(seller.cultural_attributes.values()))

            if len(buyer_values) == 0 or len(seller_values) == 0:
                return 0.5  # Default moderate alignment

            # Ensure same dimensionality
            min_length = min(len(buyer_values), len(seller_values))
            buyer_values = buyer_values[:min_length]
            seller_values = seller_values[:min_length]

            # Calculate cosine similarity
            similarity = cosine_similarity(
                buyer_values.reshape(1, -1),
                seller_values.reshape(1, -1)
            )[0][0]

            # Convert to 0-1 scale (cosine similarity ranges from -1 to 1)
            cultural_alignment = (similarity + 1) / 2

            return cultural_alignment

        except Exception as e:
            logger.error(f"Cultural alignment analysis failed: {str(e)}")
            return 0.5

    async def _analyze_financial_capacity(self, buyer: BuyerProfile, seller: SellerProfile) -> float:
        """
        Analyze buyer's financial capacity to acquire seller

        Factors:
        - Deal size vs buyer capacity
        - Financing availability
        - Cash vs debt structure
        - Financial strength ratios
        """
        try:
            # Get seller valuation estimate
            seller_valuation = seller.valuation_expectations.get("target_valuation", 0)

            # Check if within buyer's range
            min_deal_size, max_deal_size = buyer.deal_size_range

            if seller_valuation < min_deal_size:
                size_alignment = 0.3  # Too small
            elif seller_valuation > max_deal_size:
                size_alignment = 0.2  # Too large
            else:
                # Calculate position within range
                range_position = (seller_valuation - min_deal_size) / (max_deal_size - min_deal_size)
                size_alignment = 1.0 - abs(0.5 - range_position)  # Peak at middle of range

            # Assess financial strength
            buyer_strength = buyer.financial_capacity.get("debt_capacity", 0.5)
            financial_strength = min(buyer_strength, 1.0)

            # Combined score
            capacity_score = 0.7 * size_alignment + 0.3 * financial_strength

            return capacity_score

        except Exception as e:
            logger.error(f"Financial capacity analysis failed: {str(e)}")
            return 0.5

    async def _analyze_geographic_synergy(self, buyer: BuyerProfile, seller: SellerProfile) -> float:
        """
        Analyze geographic synergies and market expansion opportunities

        Factors:
        - Market overlap vs expansion
        - Regional expertise
        - Distribution synergies
        - Regulatory environment similarity
        """
        try:
            geographic_score = 0.0

            # Check if seller geography is in buyer's focus areas
            if seller.geography in buyer.geographic_focus:
                geographic_score += 0.6  # Market expansion opportunity

            # Check for regional clustering benefits
            buyer_regions = set(buyer.geographic_focus)
            seller_region = {seller.geography}

            # Calculate geographic proximity benefits (simplified)
            proximity_bonus = 0.3 if len(buyer_regions.intersection(seller_region)) > 0 else 0.1
            geographic_score += proximity_bonus

            # Add distribution synergy potential
            distribution_synergy = 0.1  # Base assumption
            geographic_score += distribution_synergy

            return min(geographic_score, 1.0)

        except Exception as e:
            logger.error(f"Geographic synergy analysis failed: {str(e)}")
            return 0.5

    async def _analyze_operational_synergy(self, buyer: BuyerProfile, seller: SellerProfile) -> float:
        """
        Analyze operational synergies and integration potential

        Factors:
        - Technology integration
        - Process optimization
        - Cost reduction opportunities
        - Operational expertise transfer
        """
        try:
            operational_score = 0.0

            # Integration capability assessment
            integration_capability = buyer.integration_capabilities.get("operational_integration", 0.5)
            operational_score += 0.4 * integration_capability

            # Technology synergy potential
            tech_synergy = 0.3  # Would be calculated from actual technology stacks
            operational_score += 0.3 * tech_synergy

            # Process optimization potential
            process_optimization = 0.25  # Would be calculated from operational metrics
            operational_score += 0.3 * process_optimization

            return min(operational_score, 1.0)

        except Exception as e:
            logger.error(f"Operational synergy analysis failed: {str(e)}")
            return 0.5

    async def _analyze_regulatory_alignment(self, buyer: BuyerProfile, seller: SellerProfile) -> float:
        """
        Analyze regulatory compatibility and compliance alignment

        Factors:
        - Regulatory environment similarity
        - Compliance history
        - Antitrust considerations
        - Industry-specific regulations
        """
        try:
            # Simplified regulatory analysis
            # In production, this would integrate with regulatory databases

            # Check for antitrust concerns (simplified)
            antitrust_risk = 0.1 if buyer.industry_sectors[0] == seller.industry_sector else 0.0

            # Regulatory environment alignment
            regulatory_alignment = 0.8  # Base assumption of good alignment

            # Compliance capability
            compliance_score = buyer.integration_capabilities.get("regulatory_compliance", 0.7)

            overall_regulatory = (1 - antitrust_risk) * regulatory_alignment * compliance_score

            return overall_regulatory

        except Exception as e:
            logger.error(f"Regulatory alignment analysis failed: {str(e)}")
            return 0.7

    async def _analyze_timing_alignment(self, buyer: BuyerProfile, seller: SellerProfile) -> float:
        """
        Analyze timing compatibility between buyer and seller

        Factors:
        - Transaction timeline preferences
        - Market timing considerations
        - Due diligence timeline
        - Closing timeline compatibility
        """
        try:
            # Get timeline preferences
            buyer_timeline = buyer.timeline_preferences.get("preferred_timeline_months", 6)
            seller_timeline = seller.timeline_constraints.get("required_timeline_months", 6)

            # Calculate timeline alignment
            timeline_diff = abs(buyer_timeline - seller_timeline)
            timing_alignment = max(0, 1 - (timeline_diff / 12))  # Normalize to 12 months max difference

            return timing_alignment

        except Exception as e:
            logger.error(f"Timing alignment analysis failed: {str(e)}")
            return 0.5

    def _calculate_industry_alignment(self, buyer_sectors: List[str], seller_sector: str) -> float:
        """Calculate industry alignment score"""
        if seller_sector in buyer_sectors:
            return 1.0
        # Could add logic for related industries
        return 0.3

    def _calculate_asset_alignment(self, buyer_criteria: Dict[str, Any], seller_assets: List[str]) -> float:
        """Calculate strategic asset alignment"""
        # Simplified calculation
        return 0.7

    def _calculate_expansion_potential(self, buyer_geo: List[str], seller_geo: str) -> float:
        """Calculate market expansion potential"""
        if seller_geo in buyer_geo:
            return 0.8  # Market consolidation
        else:
            return 1.0  # Market expansion

    def _calculate_strategy_alignment(self, buyer_strategy: str, seller_model: str) -> float:
        """Calculate acquisition strategy alignment"""
        # Simplified alignment logic
        strategy_alignment_matrix = {
            ("growth", "saas"): 0.9,
            ("consolidation", "traditional"): 0.8,
            ("technology", "tech"): 0.95,
            ("diversification", "different"): 0.6
        }
        return strategy_alignment_matrix.get((buyer_strategy, seller_model), 0.5)

    async def _generate_compatibility_reasoning(
        self,
        buyer: BuyerProfile,
        seller: SellerProfile,
        dimension_scores: Dict[CompatibilityDimension, float]
    ) -> str:
        """Generate detailed AI reasoning for compatibility assessment"""
        try:
            reasoning_parts = []

            # Strategic fit reasoning
            if dimension_scores[CompatibilityDimension.STRATEGIC_FIT] > 0.8:
                reasoning_parts.append(f"Excellent strategic fit with {seller.company_name} operating in {buyer.company_name}'s target industry sectors")
            elif dimension_scores[CompatibilityDimension.STRATEGIC_FIT] > 0.6:
                reasoning_parts.append(f"Good strategic alignment with potential for market expansion and operational synergies")
            else:
                reasoning_parts.append(f"Limited strategic overlap requiring careful integration planning")

            # Financial capacity reasoning
            if dimension_scores[CompatibilityDimension.FINANCIAL_CAPACITY] > 0.8:
                reasoning_parts.append(f"Strong financial capacity to execute transaction within target valuation range")
            elif dimension_scores[CompatibilityDimension.FINANCIAL_CAPACITY] > 0.6:
                reasoning_parts.append(f"Adequate financial resources with potential financing requirements")
            else:
                reasoning_parts.append(f"Financial capacity constraints may require creative deal structuring")

            # Cultural alignment reasoning
            if dimension_scores[CompatibilityDimension.CULTURAL_ALIGNMENT] > 0.7:
                reasoning_parts.append(f"High cultural compatibility reducing integration risks")
            elif dimension_scores[CompatibilityDimension.CULTURAL_ALIGNMENT] > 0.5:
                reasoning_parts.append(f"Moderate cultural alignment with manageable integration challenges")
            else:
                reasoning_parts.append(f"Significant cultural differences requiring dedicated change management")

            reasoning = ". ".join(reasoning_parts) + "."
            return reasoning

        except Exception as e:
            logger.error(f"Reasoning generation failed: {str(e)}")
            return "Compatibility assessment completed with mixed results requiring detailed due diligence."

    # Additional helper methods would be implemented here...
    async def _identify_synergy_opportunities(self, buyer: BuyerProfile, seller: SellerProfile, scores: Dict) -> List[str]:
        return ["Revenue synergies through cross-selling", "Cost synergies through operational optimization", "Technology integration benefits"]

    async def _assess_risk_factors(self, buyer: BuyerProfile, seller: SellerProfile, scores: Dict) -> List[RiskFactor]:
        risk_factors = []
        if scores[CompatibilityDimension.CULTURAL_ALIGNMENT] < 0.5:
            risk_factors.append(RiskFactor.CULTURAL_MISMATCH)
        if scores[CompatibilityDimension.REGULATORY_ALIGNMENT] < 0.6:
            risk_factors.append(RiskFactor.REGULATORY_HURDLES)
        return risk_factors

    async def _calculate_success_probability(self, scores: Dict, risks: List[RiskFactor]) -> float:
        base_probability = sum(scores.values()) / len(scores)
        risk_adjustment = len(risks) * 0.05  # 5% reduction per risk factor
        return max(base_probability - risk_adjustment, 0.1)

    async def _recommend_deal_structure(self, buyer: BuyerProfile, seller: SellerProfile, scores: Dict) -> Dict[str, Any]:
        return {
            "recommended_structure": "cash_and_earnout",
            "earnout_percentage": 20,
            "cash_percentage": 80,
            "reasoning": "Balanced structure to align interests and manage valuation risk"
        }

    async def _generate_negotiation_strategy(self, buyer: BuyerProfile, seller: SellerProfile, scores: Dict) -> Dict[str, Any]:
        return {
            "key_value_drivers": ["market_expansion", "operational_synergies"],
            "potential_concerns": ["cultural_integration", "regulatory_approval"],
            "negotiation_approach": "collaborative",
            "timeline_strategy": "standard_process"
        }

    async def _perform_valuation_analysis(self, buyer: BuyerProfile, seller: SellerProfile) -> Dict[str, Any]:
        return {
            "estimated_valuation_range": [5000000, 7000000],
            "synergy_value": 1500000,
            "transaction_costs": 300000,
            "net_value_creation": 1200000
        }

    async def _get_market_context(self, buyer: BuyerProfile, seller: SellerProfile) -> Dict[str, Any]:
        return {
            "market_conditions": "favorable",
            "industry_multiples": {"revenue": 2.5, "ebitda": 8.0},
            "recent_transactions": 15,
            "market_trends": "consolidation_phase"
        }

# Global compatibility engine instance
compatibility_engine = CompatibilityEngine()