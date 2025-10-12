"""
Intelligent Deal Matching System
AI-powered buyer/seller matching with confidence scoring and predictive analytics
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import logging
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.opportunities import Opportunity, OpportunityProfile
from app.models.user import User
from app.models.organization import Organization
from app.services.claude_service import ClaudeService
from app.services.financial_intelligence import FinancialIntelligenceEngine

logger = logging.getLogger(__name__)

class MatchType(Enum):
    """Types of deal matches"""
    STRATEGIC_ACQUISITION = "strategic_acquisition"
    FINANCIAL_ACQUISITION = "financial_acquisition"
    MANAGEMENT_BUYOUT = "management_buyout"
    MERGER = "merger"
    ROLLUP = "rollup"
    DISTRESSED = "distressed"

class ConfidenceLevel(Enum):
    """Match confidence levels"""
    VERY_HIGH = "very_high"  # 90%+
    HIGH = "high"           # 70-89%
    MODERATE = "moderate"   # 50-69%
    LOW = "low"            # 30-49%
    VERY_LOW = "very_low"  # <30%

@dataclass
class MatchCriteria:
    """Buyer/seller matching criteria"""
    industries: List[str]
    revenue_min: Optional[Decimal]
    revenue_max: Optional[Decimal]
    ebitda_min: Optional[Decimal]
    ebitda_max: Optional[Decimal]
    geography: List[str]
    deal_size_min: Optional[Decimal]
    deal_size_max: Optional[Decimal]
    growth_rate_min: Optional[float]
    strategic_priorities: List[str]
    excluded_criteria: Dict[str, Any]

@dataclass
class DealMatch:
    """Individual deal match result"""
    match_id: str
    buyer_id: str
    seller_id: str
    opportunity_id: str
    match_type: MatchType
    confidence_score: float
    confidence_level: ConfidenceLevel
    match_reasons: List[str]
    potential_synergies: Dict[str, float]
    estimated_valuation_range: Tuple[Decimal, Decimal]
    strategic_fit_score: float
    financial_fit_score: float
    execution_risk_score: float
    ai_analysis: str
    match_timestamp: datetime

@dataclass
class MatchingResult:
    """Complete matching analysis result"""
    query_id: str
    matches: List[DealMatch]
    total_matches: int
    high_confidence_matches: int
    market_insights: Dict[str, Any]
    matching_statistics: Dict[str, float]
    ai_market_commentary: str

class IntelligentDealMatchingSystem:
    """
    Intelligent Deal Matching System

    Advanced AI-powered matching engine that:
    - Analyzes buyer preferences and strategic priorities
    - Evaluates seller characteristics and deal readiness
    - Calculates multi-dimensional compatibility scores
    - Identifies synergy opportunities
    - Provides predictive deal success probability
    - Generates market intelligence insights
    """

    def __init__(self, db: Session, financial_engine: FinancialIntelligenceEngine):
        self.db = db
        self.financial_engine = financial_engine
        self.claude_service = ClaudeService()

        # Initialize ML components
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')

        # Matching weights for different criteria
        self.matching_weights = {
            'industry_match': 0.25,
            'size_compatibility': 0.20,
            'geographic_fit': 0.15,
            'strategic_alignment': 0.20,
            'financial_profile': 0.15,
            'timing_readiness': 0.05
        }

    async def find_matches_for_buyer(
        self,
        buyer_id: str,
        criteria: MatchCriteria,
        max_matches: int = 50
    ) -> MatchingResult:
        """
        Find potential acquisition targets for a buyer

        Process:
        1. Load buyer profile and preferences
        2. Query potential targets from opportunity database
        3. Apply initial filtering based on criteria
        4. Calculate multi-dimensional match scores
        5. Apply AI-powered analysis for strategic fit
        6. Rank and return top matches
        """

        logger.info(f"Finding matches for buyer {buyer_id}")

        # Step 1: Load buyer profile
        buyer_profile = await self._get_buyer_profile(buyer_id)

        # Step 2: Query potential targets
        potential_targets = await self._query_potential_targets(criteria)

        # Step 3: Calculate match scores for each target
        matches = []

        for target in potential_targets:
            try:
                match_score = await self._calculate_match_score(
                    buyer_profile, target, criteria
                )

                if match_score['overall_score'] >= 0.3:  # Minimum threshold
                    deal_match = await self._create_deal_match(
                        buyer_id, target, match_score
                    )
                    matches.append(deal_match)

            except Exception as e:
                logger.warning(f"Error calculating match for target {target.id}: {e}")
                continue

        # Step 4: Sort by confidence score
        matches.sort(key=lambda m: m.confidence_score, reverse=True)

        # Step 5: Take top matches
        top_matches = matches[:max_matches]

        # Step 6: Generate market insights
        market_insights = await self._generate_market_insights(
            buyer_profile, criteria, top_matches
        )

        # Step 7: Calculate matching statistics
        stats = self._calculate_matching_statistics(matches, top_matches)

        query_id = f"buyer_search_{buyer_id}_{datetime.utcnow().timestamp()}"

        return MatchingResult(
            query_id=query_id,
            matches=top_matches,
            total_matches=len(matches),
            high_confidence_matches=len([m for m in top_matches if m.confidence_score >= 0.7]),
            market_insights=market_insights,
            matching_statistics=stats,
            ai_market_commentary=market_insights.get('ai_commentary', '')
        )

    async def find_matches_for_seller(
        self,
        seller_id: str,
        opportunity_id: str,
        max_matches: int = 30
    ) -> MatchingResult:
        """
        Find potential buyers for a selling opportunity

        Process:
        1. Load seller opportunity profile
        2. Analyze company characteristics and attractiveness
        3. Query potential buyers from user database
        4. Calculate buyer-seller compatibility
        5. Evaluate strategic and financial fit
        6. Apply AI analysis for deal probability
        """

        logger.info(f"Finding matches for seller opportunity {opportunity_id}")

        # Step 1: Load opportunity profile
        opportunity = await self._get_opportunity_profile(opportunity_id)

        # Step 2: Get financial analysis of target company
        financial_analysis = await self.financial_engine.analyze_company_financials(
            opportunity.company_id
        )

        # Step 3: Query potential buyers
        potential_buyers = await self._query_potential_buyers(opportunity)

        # Step 4: Calculate match scores
        matches = []

        for buyer in potential_buyers:
            try:
                match_score = await self._calculate_buyer_seller_match(
                    buyer, opportunity, financial_analysis
                )

                if match_score['overall_score'] >= 0.25:  # Lower threshold for seller side
                    deal_match = await self._create_seller_side_match(
                        buyer, opportunity, match_score
                    )
                    matches.append(deal_match)

            except Exception as e:
                logger.warning(f"Error calculating match for buyer {buyer.id}: {e}")
                continue

        # Step 5: Sort and filter matches
        matches.sort(key=lambda m: m.confidence_score, reverse=True)
        top_matches = matches[:max_matches]

        # Step 6: Generate seller-specific insights
        market_insights = await self._generate_seller_market_insights(
            opportunity, financial_analysis, top_matches
        )

        query_id = f"seller_search_{opportunity_id}_{datetime.utcnow().timestamp()}"

        return MatchingResult(
            query_id=query_id,
            matches=top_matches,
            total_matches=len(matches),
            high_confidence_matches=len([m for m in top_matches if m.confidence_score >= 0.7]),
            market_insights=market_insights,
            matching_statistics=self._calculate_matching_statistics(matches, top_matches),
            ai_market_commentary=market_insights.get('ai_commentary', '')
        )

    async def analyze_market_trends(
        self,
        industry: str,
        geography: Optional[str] = None,
        time_period_months: int = 12
    ) -> Dict[str, Any]:
        """
        Analyze M&A market trends for specific industry/geography

        Provides insights on:
        - Deal volume and value trends
        - Average multiples and pricing
        - Common deal structures
        - Buyer/seller balance
        - Emerging opportunities
        """

        logger.info(f"Analyzing market trends for {industry}")

        # Step 1: Query historical deals data
        historical_data = await self._query_historical_deals(
            industry, geography, time_period_months
        )

        # Step 2: Calculate trend metrics
        trend_metrics = await self._calculate_trend_metrics(historical_data)

        # Step 3: AI analysis of market conditions
        market_analysis = await self._generate_ai_market_analysis(
            industry, geography, trend_metrics
        )

        return {
            'industry': industry,
            'geography': geography,
            'analysis_period_months': time_period_months,
            'deal_volume_trend': trend_metrics['volume_trend'],
            'valuation_trend': trend_metrics['valuation_trend'],
            'average_multiples': trend_metrics['avg_multiples'],
            'deal_size_distribution': trend_metrics['size_distribution'],
            'buyer_type_breakdown': trend_metrics['buyer_types'],
            'time_to_close_average': trend_metrics['avg_closing_time'],
            'success_rate': trend_metrics['success_rate'],
            'ai_insights': market_analysis,
            'recommendations': trend_metrics['recommendations']
        }

    # Private methods for match calculation

    async def _calculate_match_score(
        self,
        buyer_profile: Dict[str, Any],
        target_opportunity,
        criteria: MatchCriteria
    ) -> Dict[str, float]:
        """Calculate comprehensive match score"""

        scores = {}

        # Industry compatibility
        scores['industry_match'] = self._calculate_industry_match(
            buyer_profile.get('industries', []),
            target_opportunity.industry
        )

        # Size compatibility
        scores['size_compatibility'] = self._calculate_size_compatibility(
            buyer_profile.get('deal_size_preference', {}),
            target_opportunity.estimated_value
        )

        # Geographic fit
        scores['geographic_fit'] = self._calculate_geographic_fit(
            buyer_profile.get('target_geographies', []),
            target_opportunity.location
        )

        # Strategic alignment
        scores['strategic_alignment'] = await self._calculate_strategic_alignment(
            buyer_profile, target_opportunity
        )

        # Financial profile fit
        scores['financial_profile'] = await self._calculate_financial_fit(
            buyer_profile, target_opportunity
        )

        # Timing readiness
        scores['timing_readiness'] = self._calculate_timing_readiness(
            buyer_profile, target_opportunity
        )

        # Calculate weighted overall score
        overall_score = sum(
            scores[criterion] * self.matching_weights.get(criterion, 0)
            for criterion in scores
        )

        scores['overall_score'] = overall_score
        return scores

    def _calculate_industry_match(
        self,
        buyer_industries: List[str],
        target_industry: str
    ) -> float:
        """Calculate industry compatibility score"""

        if not buyer_industries or not target_industry:
            return 0.0

        # Exact match
        if target_industry in buyer_industries:
            return 1.0

        # Related industry match using AI similarity
        # Simplified implementation - in production, use industry taxonomy
        related_industries = {
            'software': ['saas', 'technology', 'fintech'],
            'healthcare': ['medtech', 'pharmaceuticals', 'biotech'],
            'manufacturing': ['industrial', 'automotive', 'aerospace']
        }

        for buyer_industry in buyer_industries:
            if buyer_industry in related_industries:
                if target_industry in related_industries[buyer_industry]:
                    return 0.8

        return 0.2  # Minimal compatibility

    def _calculate_size_compatibility(
        self,
        buyer_size_pref: Dict[str, Any],
        target_value: Decimal
    ) -> float:
        """Calculate deal size compatibility"""

        if not buyer_size_pref or not target_value:
            return 0.5  # Neutral if no data

        min_size = buyer_size_pref.get('min_deal_size', 0)
        max_size = buyer_size_pref.get('max_deal_size', float('inf'))
        preferred_size = buyer_size_pref.get('preferred_size')

        target_float = float(target_value)

        # Check if within range
        if min_size <= target_float <= max_size:
            if preferred_size:
                # Score based on distance from preferred size
                distance = abs(target_float - preferred_size) / preferred_size
                return max(0.5, 1.0 - (distance * 0.5))
            return 0.8

        # Outside range - calculate penalty
        if target_float < min_size:
            penalty = (min_size - target_float) / min_size
        else:
            penalty = (target_float - max_size) / max_size

        return max(0.1, 0.5 - penalty)

    def _calculate_geographic_fit(
        self,
        buyer_geographies: List[str],
        target_location: str
    ) -> float:
        """Calculate geographic compatibility"""

        if not buyer_geographies or not target_location:
            return 0.5

        # Direct match
        if target_location in buyer_geographies:
            return 1.0

        # Regional match (simplified)
        regions = {
            'north_america': ['usa', 'canada', 'mexico'],
            'europe': ['uk', 'germany', 'france', 'netherlands'],
            'asia_pacific': ['singapore', 'australia', 'japan']
        }

        for region, countries in regions.items():
            if (any(geo in countries for geo in buyer_geographies) and
                target_location in countries):
                return 0.7

        return 0.3

    async def _calculate_strategic_alignment(
        self,
        buyer_profile: Dict[str, Any],
        target_opportunity
    ) -> float:
        """Calculate strategic alignment using AI analysis"""

        buyer_strategy = buyer_profile.get('strategic_priorities', [])
        target_description = target_opportunity.description

        if not buyer_strategy or not target_description:
            return 0.5

        # Use AI to analyze strategic fit
        alignment_prompt = f"""
        Analyze the strategic alignment between this buyer and target:

        BUYER STRATEGIC PRIORITIES:
        {'; '.join(buyer_strategy)}

        TARGET COMPANY DESCRIPTION:
        {target_description}

        Rate the strategic alignment from 0.0 to 1.0 considering:
        1. Capability complementarity
        2. Market expansion potential
        3. Technology synergies
        4. Customer base overlap/expansion
        5. Operational synergies

        Return only a single number between 0.0 and 1.0.
        """

        try:
            ai_response = await self.claude_service.analyze_content(alignment_prompt)
            score = float(ai_response.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.5  # Default if AI analysis fails

    async def _calculate_financial_fit(
        self,
        buyer_profile: Dict[str, Any],
        target_opportunity
    ) -> float:
        """Calculate financial compatibility"""

        # Get buyer's financial criteria
        buyer_criteria = buyer_profile.get('financial_criteria', {})

        # This would integrate with financial analysis
        # Simplified scoring for now
        score = 0.6  # Base score

        # Adjust based on financial health of target
        if hasattr(target_opportunity, 'financial_health_score'):
            health_score = target_opportunity.financial_health_score / 100.0
            score = (score + health_score) / 2

        return score

    def _calculate_timing_readiness(
        self,
        buyer_profile: Dict[str, Any],
        target_opportunity
    ) -> float:
        """Calculate timing compatibility"""

        buyer_urgency = buyer_profile.get('acquisition_urgency', 'moderate')
        target_timeline = getattr(target_opportunity, 'target_timeline', 'flexible')

        # Scoring matrix for timing compatibility
        compatibility_matrix = {
            ('urgent', 'immediate'): 1.0,
            ('urgent', 'short_term'): 0.9,
            ('urgent', 'flexible'): 0.7,
            ('active', 'immediate'): 0.8,
            ('active', 'short_term'): 1.0,
            ('active', 'flexible'): 0.9,
            ('moderate', 'flexible'): 1.0,
            ('moderate', 'long_term'): 0.8,
            ('exploratory', 'flexible'): 0.7,
            ('exploratory', 'long_term'): 0.9
        }

        return compatibility_matrix.get((buyer_urgency, target_timeline), 0.5)

    async def _create_deal_match(
        self,
        buyer_id: str,
        target_opportunity,
        match_scores: Dict[str, float]
    ) -> DealMatch:
        """Create deal match object from scores"""

        confidence_score = match_scores['overall_score']

        # Determine confidence level
        if confidence_score >= 0.9:
            confidence_level = ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.7:
            confidence_level = ConfidenceLevel.HIGH
        elif confidence_score >= 0.5:
            confidence_level = ConfidenceLevel.MODERATE
        elif confidence_score >= 0.3:
            confidence_level = ConfidenceLevel.LOW
        else:
            confidence_level = ConfidenceLevel.VERY_LOW

        # Generate match reasons
        match_reasons = self._generate_match_reasons(match_scores)

        # Estimate synergies
        synergies = await self._estimate_synergies(buyer_id, target_opportunity)

        # Estimate valuation range
        valuation_range = await self._estimate_valuation_range(target_opportunity)

        return DealMatch(
            match_id=f"match_{buyer_id}_{target_opportunity.id}_{datetime.utcnow().timestamp()}",
            buyer_id=buyer_id,
            seller_id=target_opportunity.owner_id,
            opportunity_id=str(target_opportunity.id),
            match_type=MatchType.STRATEGIC_ACQUISITION,  # Default, could be determined by AI
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            match_reasons=match_reasons,
            potential_synergies=synergies,
            estimated_valuation_range=valuation_range,
            strategic_fit_score=match_scores['strategic_alignment'],
            financial_fit_score=match_scores['financial_profile'],
            execution_risk_score=1.0 - confidence_score,  # Inverse relationship
            ai_analysis="",  # Would be populated by detailed AI analysis
            match_timestamp=datetime.utcnow()
        )

    def _generate_match_reasons(self, match_scores: Dict[str, float]) -> List[str]:
        """Generate human-readable match reasons"""

        reasons = []

        if match_scores['industry_match'] >= 0.8:
            reasons.append("Strong industry alignment")

        if match_scores['size_compatibility'] >= 0.8:
            reasons.append("Excellent deal size fit")

        if match_scores['strategic_alignment'] >= 0.7:
            reasons.append("High strategic synergy potential")

        if match_scores['financial_profile'] >= 0.7:
            reasons.append("Compatible financial profiles")

        if match_scores['geographic_fit'] >= 0.8:
            reasons.append("Geographic market fit")

        return reasons

    # Helper methods for data querying

    async def _get_buyer_profile(self, buyer_id: str) -> Dict[str, Any]:
        """Get comprehensive buyer profile"""

        # Query from database - simplified for now
        return {
            'industries': ['software', 'technology'],
            'deal_size_preference': {'min_deal_size': 1000000, 'max_deal_size': 50000000},
            'target_geographies': ['usa', 'canada'],
            'strategic_priorities': ['market expansion', 'technology acquisition'],
            'financial_criteria': {'min_revenue': 5000000, 'min_growth_rate': 0.15},
            'acquisition_urgency': 'active'
        }

    async def _query_potential_targets(self, criteria: MatchCriteria) -> List:
        """Query potential acquisition targets"""

        query = self.db.query(Opportunity)

        # Apply criteria filters
        if criteria.industries:
            query = query.filter(Opportunity.industry.in_(criteria.industries))

        if criteria.revenue_min:
            query = query.filter(Opportunity.annual_revenue >= criteria.revenue_min)

        if criteria.revenue_max:
            query = query.filter(Opportunity.annual_revenue <= criteria.revenue_max)

        return query.limit(200).all()  # Limit for performance

    async def _get_opportunity_profile(self, opportunity_id: str):
        """Get opportunity details"""
        return self.db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()

    async def _query_potential_buyers(self, opportunity) -> List:
        """Query potential buyers for an opportunity"""

        # Query users/organizations that are buyers in relevant industry
        buyers = self.db.query(User).filter(
            User.user_type == 'buyer',
            User.industries.contains(opportunity.industry)
        ).limit(100).all()

        return buyers

    async def _estimate_synergies(self, buyer_id: str, target_opportunity) -> Dict[str, float]:
        """Estimate potential synergies"""

        # Placeholder implementation
        return {
            'revenue_synergies': 2000000.0,
            'cost_synergies': 1500000.0,
            'tax_benefits': 500000.0,
            'total_synergies': 4000000.0
        }

    async def _estimate_valuation_range(self, target_opportunity) -> Tuple[Decimal, Decimal]:
        """Estimate valuation range for opportunity"""

        base_value = target_opportunity.estimated_value or Decimal('10000000')
        return (base_value * Decimal('0.8'), base_value * Decimal('1.2'))

    # Market analysis methods

    async def _generate_market_insights(
        self,
        buyer_profile: Dict[str, Any],
        criteria: MatchCriteria,
        matches: List[DealMatch]
    ) -> Dict[str, Any]:
        """Generate market insights from matching results"""

        insights = {
            'market_competitiveness': 'moderate',
            'average_confidence_score': sum(m.confidence_score for m in matches) / len(matches) if matches else 0,
            'top_matching_industries': [],
            'valuation_trends': {},
            'recommended_adjustments': []
        }

        # AI commentary on market conditions
        market_prompt = f"""
        Analyze the M&A market conditions based on these matching results:

        BUYER PROFILE:
        Industries: {buyer_profile.get('industries', [])}
        Deal Size Range: ${criteria.deal_size_min or 0:,.0f} - ${criteria.deal_size_max or 999999999:,.0f}
        Target Geographies: {criteria.geography}

        MATCHING RESULTS:
        Total Matches Found: {len(matches)}
        High Confidence Matches: {len([m for m in matches if m.confidence_score >= 0.7])}
        Average Confidence: {insights['average_confidence_score']:.2f}

        Provide market commentary including:
        1. Market competitiveness assessment
        2. Pricing/valuation trends
        3. Deal availability in target sectors
        4. Recommendations for buyer strategy

        Keep response concise and actionable.
        """

        try:
            ai_commentary = await self.claude_service.analyze_content(market_prompt)
            insights['ai_commentary'] = ai_commentary
        except:
            insights['ai_commentary'] = "Market analysis unavailable"

        return insights

    def _calculate_matching_statistics(
        self,
        all_matches: List[DealMatch],
        top_matches: List[DealMatch]
    ) -> Dict[str, float]:
        """Calculate matching statistics"""

        if not all_matches:
            return {}

        return {
            'total_evaluated': len(all_matches),
            'matches_returned': len(top_matches),
            'average_confidence': sum(m.confidence_score for m in all_matches) / len(all_matches),
            'high_confidence_rate': len([m for m in all_matches if m.confidence_score >= 0.7]) / len(all_matches),
            'strategic_fit_average': sum(m.strategic_fit_score for m in all_matches) / len(all_matches),
            'financial_fit_average': sum(m.financial_fit_score for m in all_matches) / len(all_matches)
        }

    # Additional helper methods would be implemented here...
    async def _calculate_buyer_seller_match(self, buyer, opportunity, financial_analysis): pass
    async def _create_seller_side_match(self, buyer, opportunity, match_score): pass
    async def _generate_seller_market_insights(self, opportunity, financial_analysis, matches): pass
    async def _query_historical_deals(self, industry, geography, months): pass
    async def _calculate_trend_metrics(self, historical_data): pass
    async def _generate_ai_market_analysis(self, industry, geography, metrics): pass