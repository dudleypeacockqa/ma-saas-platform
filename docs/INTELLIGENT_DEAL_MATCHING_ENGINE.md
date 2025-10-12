# Intelligent Deal Matching Engine - Technical Specification

**Component**: AI-Powered Deal Matching System
**Priority**: MUST HAVE - Quarter 1-2
**Dependencies**: Deal Management Platform, Financial Intelligence Engine
**Estimated Effort**: 6 weeks

## Executive Summary

The Intelligent Deal Matching Engine is the network effect catalyst that transforms isolated M&A professionals into a connected ecosystem. By applying sophisticated AI algorithms to deal characteristics, financial profiles, and behavioral patterns, the system delivers 90%+ relevant matches while protecting confidentiality through intelligent anonymization.

**Key Differentiators:**

- Multi-dimensional similarity scoring (financial, strategic, operational)
- Privacy-preserving deal sharing with progressive disclosure
- Behavioral learning from user interactions and preferences
- Real-time market intelligence and competitive insights
- Cross-border and cross-industry matching capabilities

---

## 🧠 AI MATCHING ALGORITHMS

### 1. Core Matching Architecture

```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import asyncio

@dataclass
class DealCharacteristics:
    """Comprehensive deal characteristics for matching"""

    # Basic deal metadata
    deal_id: str
    tenant_id: str
    deal_type: str  # acquisition, disposal, merger, etc.
    deal_side: str  # buy_side, sell_side

    # Financial characteristics
    enterprise_value: Optional[float]
    revenue_ltm: Optional[float]
    ebitda_ltm: Optional[float]
    ebitda_margin: Optional[float]
    revenue_growth_rate: Optional[float]

    # Industry and geography
    primary_industry: str
    secondary_industries: List[str]
    geography: str
    target_geographies: List[str]

    # Strategic characteristics
    business_model: str
    customer_base: str
    distribution_channels: List[str]
    competitive_advantages: List[str]

    # Transaction characteristics
    transaction_rationale: str
    integration_complexity: str
    regulatory_considerations: List[str]

    # Timing and preferences
    preferred_timeline: str
    funding_preferences: List[str]
    deal_size_flexibility: float  # ±percentage

    # Confidentiality and sharing
    confidentiality_level: str
    sharing_permissions: Dict[str, bool]
    anonymous_sharing: bool

@dataclass
class MatchingResult:
    """Result of deal matching with detailed scoring"""

    target_deal_id: str
    similarity_score: float  # 0-1 overall similarity
    confidence_score: float  # 0-1 confidence in match quality

    # Detailed similarity breakdown
    financial_similarity: float
    strategic_similarity: float
    operational_similarity: float
    geographic_similarity: float
    temporal_similarity: float

    # Match explanation
    key_similarities: List[str]
    potential_synergies: List[str]
    risk_factors: List[str]

    # Interaction metadata
    match_rank: int
    generated_at: datetime
    expires_at: Optional[datetime]

class IntelligentDealMatchingEngine:
    """Advanced AI-powered deal matching system"""

    def __init__(self, ai_service, financial_service, market_data_service):
        self.ai_service = ai_service
        self.financial_service = financial_service
        self.market_data_service = market_data_service

        # Machine learning models
        self.similarity_model = self._load_similarity_model()
        self.preference_model = self._load_preference_model()
        self.market_model = self._load_market_model()

        # Text processing for strategic matching
        self.text_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )

    async def find_matches(self, source_deal: DealCharacteristics,
                          match_criteria: MatchCriteria,
                          limit: int = 20) -> List[MatchingResult]:
        """Find best matching deals with comprehensive AI analysis"""

        # Get candidate deals from database
        candidates = await self._get_candidate_deals(source_deal, match_criteria)

        # Calculate multi-dimensional similarity scores
        similarity_scores = await self._calculate_similarity_matrix(
            source_deal, candidates
        )

        # Apply user preference learning
        preference_adjusted_scores = await self._apply_preference_learning(
            source_deal.tenant_id, similarity_scores
        )

        # Generate detailed match results
        match_results = await self._generate_match_results(
            source_deal, candidates, preference_adjusted_scores
        )

        # Sort by overall match quality and return top matches
        ranked_matches = sorted(
            match_results,
            key=lambda x: x.similarity_score * x.confidence_score,
            reverse=True
        )

        return ranked_matches[:limit]

    async def _calculate_similarity_matrix(self, source_deal: DealCharacteristics,
                                         candidates: List[DealCharacteristics]) -> np.ndarray:
        """Calculate comprehensive similarity matrix"""

        # Run similarity calculations in parallel
        financial_task = self._calculate_financial_similarity(source_deal, candidates)
        strategic_task = self._calculate_strategic_similarity(source_deal, candidates)
        operational_task = self._calculate_operational_similarity(source_deal, candidates)
        geographic_task = self._calculate_geographic_similarity(source_deal, candidates)
        temporal_task = self._calculate_temporal_similarity(source_deal, candidates)

        financial_sim, strategic_sim, operational_sim, geographic_sim, temporal_sim = \
            await asyncio.gather(
                financial_task, strategic_task, operational_task,
                geographic_task, temporal_task
            )

        # Weighted combination of similarity dimensions
        weights = {
            'financial': 0.35,
            'strategic': 0.30,
            'operational': 0.20,
            'geographic': 0.10,
            'temporal': 0.05
        }

        overall_similarity = (
            weights['financial'] * financial_sim +
            weights['strategic'] * strategic_sim +
            weights['operational'] * operational_sim +
            weights['geographic'] * geographic_sim +
            weights['temporal'] * temporal_sim
        )

        return overall_similarity

    async def _calculate_financial_similarity(self, source: DealCharacteristics,
                                            candidates: List[DealCharacteristics]) -> np.ndarray:
        """Calculate financial profile similarity"""

        # Financial metrics for comparison
        metrics = ['enterprise_value', 'revenue_ltm', 'ebitda_ltm', 'ebitda_margin', 'revenue_growth_rate']

        # Create financial feature vectors
        source_vector = np.array([
            getattr(source, metric, 0) or 0 for metric in metrics
        ])

        candidate_vectors = np.array([
            [getattr(candidate, metric, 0) or 0 for metric in metrics]
            for candidate in candidates
        ])

        # Normalize financial metrics to comparable scales
        normalized_source = self._normalize_financial_vector(source_vector)
        normalized_candidates = np.array([
            self._normalize_financial_vector(vector)
            for vector in candidate_vectors
        ])

        # Calculate similarity using weighted metrics
        financial_weights = np.array([0.3, 0.25, 0.25, 0.15, 0.05])  # EV, Revenue, EBITDA, Margin, Growth

        similarities = []
        for candidate_vector in normalized_candidates:
            # Calculate weighted Euclidean distance
            distance = np.sqrt(np.sum(
                financial_weights * (normalized_source - candidate_vector) ** 2
            ))
            # Convert distance to similarity (0-1 scale)
            similarity = 1 / (1 + distance)
            similarities.append(similarity)

        return np.array(similarities)

    async def _calculate_strategic_similarity(self, source: DealCharacteristics,
                                            candidates: List[DealCharacteristics]) -> np.ndarray:
        """Calculate strategic fit similarity using AI analysis"""

        # Combine strategic text fields for analysis
        source_strategic_text = self._combine_strategic_fields(source)
        candidate_strategic_texts = [
            self._combine_strategic_fields(candidate) for candidate in candidates
        ]

        # Use AI to analyze strategic similarity
        ai_prompt = f"""
        Analyze strategic similarity between the source deal and candidate deals.

        SOURCE DEAL STRATEGY:
        {source_strategic_text}

        CANDIDATE DEALS:
        {chr(10).join([f"{i+1}. {text}" for i, text in enumerate(candidate_strategic_texts)])}

        For each candidate, provide:
        1. Strategic similarity score (0-1)
        2. Key strategic synergies
        3. Potential integration challenges

        Return JSON format:
        {{
            "similarities": [0.85, 0.72, ...],
            "synergies": [["synergy1", "synergy2"], ...],
            "challenges": [["challenge1"], ...]
        }}
        """

        ai_response = await self.ai_service.analyze_content(ai_prompt)

        try:
            analysis = json.loads(ai_response)
            return np.array(analysis['similarities'])
        except:
            # Fallback to text similarity if AI analysis fails
            return await self._calculate_text_similarity(
                source_strategic_text, candidate_strategic_texts
            )

    async def _calculate_operational_similarity(self, source: DealCharacteristics,
                                              candidates: List[DealCharacteristics]) -> np.ndarray:
        """Calculate operational model similarity"""

        similarities = []

        for candidate in candidates:
            similarity_factors = []

            # Business model similarity
            if source.business_model == candidate.business_model:
                similarity_factors.append(1.0)
            elif self._similar_business_models(source.business_model, candidate.business_model):
                similarity_factors.append(0.7)
            else:
                similarity_factors.append(0.3)

            # Customer base overlap
            customer_similarity = self._calculate_customer_base_similarity(
                source.customer_base, candidate.customer_base
            )
            similarity_factors.append(customer_similarity)

            # Distribution channel overlap
            channel_similarity = self._calculate_list_similarity(
                source.distribution_channels, candidate.distribution_channels
            )
            similarity_factors.append(channel_similarity)

            # Competitive advantages overlap
            advantage_similarity = self._calculate_list_similarity(
                source.competitive_advantages, candidate.competitive_advantages
            )
            similarity_factors.append(advantage_similarity)

            # Average operational similarity
            operational_similarity = np.mean(similarity_factors)
            similarities.append(operational_similarity)

        return np.array(similarities)

    async def _calculate_geographic_similarity(self, source: DealCharacteristics,
                                             candidates: List[DealCharacteristics]) -> np.ndarray:
        """Calculate geographic proximity and market overlap"""

        similarities = []

        # Geographic scoring matrix
        geography_scores = {
            ('UK', 'UK'): 1.0,
            ('UK', 'Ireland'): 0.9,
            ('UK', 'EU'): 0.7,
            ('UK', 'US'): 0.5,
            ('US', 'US'): 1.0,
            ('US', 'Canada'): 0.9,
            ('US', 'EU'): 0.6,
            ('EU', 'EU'): 1.0,
            ('EU', 'UK'): 0.7,
        }

        for candidate in candidates:
            # Primary geography match
            primary_match = geography_scores.get(
                (source.geography, candidate.geography), 0.3
            )

            # Target geography overlap
            target_overlap = len(set(source.target_geographies) &
                               set(candidate.target_geographies)) / \
                           max(len(source.target_geographies), 1)

            # Combined geographic similarity
            geographic_similarity = 0.7 * primary_match + 0.3 * target_overlap
            similarities.append(geographic_similarity)

        return np.array(similarities)
```

### 2. Privacy-Preserving Deal Sharing

```python
class PrivacyPreservingDealSharing:
    """Manage confidential deal sharing with progressive disclosure"""

    def __init__(self):
        self.anonymization_engine = DealAnonymizationEngine()
        self.disclosure_manager = ProgressiveDisclosureManager()

    async def create_anonymous_deal_profile(self, deal: DealCharacteristics,
                                          sharing_level: str) -> AnonymousDealProfile:
        """Create anonymized deal profile for matching"""

        anonymization_rules = {
            'public': {
                'include_fields': ['industry', 'geography', 'deal_type', 'size_range'],
                'mask_fields': ['company_name', 'specific_financials'],
                'generalize_fields': ['enterprise_value', 'revenue_ltm']
            },
            'network': {
                'include_fields': ['industry', 'geography', 'deal_type', 'financial_metrics'],
                'mask_fields': ['company_name', 'advisor_names'],
                'generalize_fields': ['specific_locations']
            },
            'verified_professionals': {
                'include_fields': ['all_except_restricted'],
                'mask_fields': ['company_name', 'contact_details'],
                'generalize_fields': []
            }
        }

        rules = anonymization_rules[sharing_level]

        anonymous_profile = AnonymousDealProfile(
            anonymous_id=generate_anonymous_id(deal.deal_id),
            industry_category=self._generalize_industry(deal.primary_industry),
            geography_region=self._generalize_geography(deal.geography),
            size_category=self._categorize_deal_size(deal.enterprise_value),
            business_model_type=deal.business_model,
            strategic_rationale=self._sanitize_text(deal.transaction_rationale),
            financial_profile=self._create_financial_profile(deal, rules),
            matching_preferences=deal.funding_preferences,
            anonymization_level=sharing_level,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )

        return anonymous_profile

    async def request_additional_disclosure(self, requester_tenant_id: str,
                                          target_anonymous_id: str,
                                          justification: str) -> DisclosureRequest:
        """Request additional information about anonymous deal"""

        # Validate requester credentials and track record
        requester_score = await self._calculate_trust_score(requester_tenant_id)

        disclosure_request = DisclosureRequest(
            requester_id=requester_tenant_id,
            target_deal_id=target_anonymous_id,
            justification=justification,
            requester_trust_score=requester_score,
            requested_fields=['company_industry_details', 'financial_details'],
            status='pending_review',
            created_at=datetime.utcnow()
        )

        # AI-powered request evaluation
        approval_probability = await self._evaluate_disclosure_request(disclosure_request)

        if approval_probability > 0.8:
            disclosure_request.status = 'auto_approved'
            await self._grant_disclosure(disclosure_request)
        else:
            # Send to deal owner for manual review
            await self._notify_disclosure_request(disclosure_request)

        return disclosure_request

    async def _evaluate_disclosure_request(self, request: DisclosureRequest) -> float:
        """AI evaluation of disclosure request appropriateness"""

        ai_prompt = f"""
        Evaluate this deal disclosure request for appropriateness and likelihood of mutual benefit:

        REQUESTER PROFILE:
        - Trust Score: {request.requester_trust_score}/10
        - Justification: {request.justification}

        REQUESTED INFORMATION:
        {', '.join(request.requested_fields)}

        Consider:
        1. Professional legitimacy of request
        2. Potential for mutual value creation
        3. Appropriateness of information requested
        4. Risk of information misuse

        Return approval probability (0-1) with reasoning.
        """

        ai_response = await self.ai_service.analyze_content(ai_prompt)

        # Extract probability from AI response
        try:
            probability = float(re.search(r'(\d+\.?\d*)', ai_response).group(1))
            return min(probability, 1.0)
        except:
            return 0.5  # Default to manual review
```

### 3. Behavioral Learning and Personalization

```python
class DealMatchingPersonalization:
    """Learn user preferences and improve matching over time"""

    def __init__(self):
        self.interaction_tracker = MatchingInteractionTracker()
        self.preference_model = UserPreferenceModel()

    async def track_user_interaction(self, user_id: str, interaction: MatchingInteraction):
        """Track user interactions with matching results"""

        interaction_data = {
            'user_id': user_id,
            'match_id': interaction.match_id,
            'interaction_type': interaction.interaction_type,  # view, contact, dismiss, save
            'interaction_duration': interaction.duration_seconds,
            'deal_characteristics': interaction.deal_characteristics,
            'match_similarities': interaction.match_similarities,
            'user_rating': interaction.user_rating,  # Optional 1-5 rating
            'timestamp': datetime.utcnow()
        }

        await self.interaction_tracker.record_interaction(interaction_data)

        # Update user preference model
        await self._update_preference_model(user_id, interaction_data)

    async def _update_preference_model(self, user_id: str, interaction: Dict):
        """Update user preference model based on interaction"""

        # Get current user preferences
        current_preferences = await self.preference_model.get_preferences(user_id)

        # Extract preference signals from interaction
        preference_updates = {}

        if interaction['interaction_type'] in ['contact', 'save']:
            # Positive signal - reinforce these characteristics
            for characteristic, value in interaction['deal_characteristics'].items():
                current_weight = current_preferences.get(characteristic, 0.5)
                # Increase weight for characteristics that led to positive interactions
                preference_updates[characteristic] = min(current_weight + 0.1, 1.0)

        elif interaction['interaction_type'] == 'dismiss':
            # Negative signal - reduce weight for these characteristics
            for characteristic, value in interaction['deal_characteristics'].items():
                current_weight = current_preferences.get(characteristic, 0.5)
                preference_updates[characteristic] = max(current_weight - 0.05, 0.1)

        # Apply learning rate decay
        learning_rate = 0.1 * (0.95 ** current_preferences.get('interaction_count', 0))

        # Update preferences with decay
        for char, new_weight in preference_updates.items():
            current_preferences[char] = (
                (1 - learning_rate) * current_preferences.get(char, 0.5) +
                learning_rate * new_weight
            )

        current_preferences['interaction_count'] = current_preferences.get('interaction_count', 0) + 1

        await self.preference_model.update_preferences(user_id, current_preferences)

    async def get_personalized_matches(self, user_id: str, source_deal: DealCharacteristics,
                                     base_matches: List[MatchingResult]) -> List[MatchingResult]:
        """Apply personalization to base matching results"""

        user_preferences = await self.preference_model.get_preferences(user_id)

        personalized_matches = []

        for match in base_matches:
            # Calculate personalization boost
            personalization_score = await self._calculate_personalization_score(
                match, user_preferences
            )

            # Apply personalization boost to similarity score
            boosted_similarity = min(
                match.similarity_score * (1 + 0.2 * personalization_score),
                1.0
            )

            personalized_match = MatchingResult(
                target_deal_id=match.target_deal_id,
                similarity_score=boosted_similarity,
                confidence_score=match.confidence_score,
                financial_similarity=match.financial_similarity,
                strategic_similarity=match.strategic_similarity,
                operational_similarity=match.operational_similarity,
                geographic_similarity=match.geographic_similarity,
                temporal_similarity=match.temporal_similarity,
                key_similarities=match.key_similarities,
                potential_synergies=match.potential_synergies,
                risk_factors=match.risk_factors,
                match_rank=match.match_rank,
                generated_at=match.generated_at,
                expires_at=match.expires_at
            )

            personalized_matches.append(personalized_match)

        # Re-sort by personalized scores
        return sorted(
            personalized_matches,
            key=lambda x: x.similarity_score * x.confidence_score,
            reverse=True
        )
```

---

## 🏗️ DATABASE SCHEMA DESIGN

```sql
-- Deal matching and network effects
CREATE SCHEMA deal_matching;

-- Anonymous deal profiles for public matching
CREATE TABLE deal_matching.anonymous_deal_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anonymous_id VARCHAR(100) UNIQUE NOT NULL, -- Public identifier
    source_deal_id UUID NOT NULL, -- References original deal
    source_tenant_id UUID NOT NULL,

    -- Anonymized deal characteristics
    industry_category VARCHAR(100) NOT NULL,
    geography_region VARCHAR(100) NOT NULL,
    deal_type VARCHAR(50) NOT NULL,
    deal_side VARCHAR(20) NOT NULL,
    size_category VARCHAR(50) NOT NULL, -- '0-1M', '1-10M', '10-100M', '100M+'

    -- Business profile
    business_model_type VARCHAR(100),
    customer_base_type VARCHAR(100),
    distribution_model VARCHAR(100),
    revenue_model VARCHAR(100),

    -- Strategic information
    strategic_rationale TEXT,
    competitive_advantages TEXT[],
    integration_complexity VARCHAR(50),

    -- Financial profile (ranges/categories only)
    financial_profile JSONB NOT NULL, -- Ranges, not exact figures
    growth_profile JSONB NOT NULL,

    -- Matching preferences
    preferred_deal_types VARCHAR(50)[],
    preferred_geographies VARCHAR(100)[],
    funding_preferences VARCHAR(50)[],
    timeline_preferences VARCHAR(50)[],

    -- Privacy and sharing controls
    anonymization_level VARCHAR(50) NOT NULL, -- 'public', 'network', 'verified_only'
    sharing_permissions JSONB NOT NULL DEFAULT '{}',
    disclosure_requests_enabled BOOLEAN DEFAULT true,

    -- Lifecycle management
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'expired', 'withdrawn')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    INDEX idx_anonymous_profiles_category (industry_category, geography_region, size_category),
    INDEX idx_anonymous_profiles_type (deal_type, deal_side),
    INDEX idx_anonymous_profiles_active (status, expires_at),
    INDEX idx_anonymous_profiles_search USING gin(to_tsvector('english', strategic_rationale))
);

-- Matching results and recommendations
CREATE TABLE deal_matching.matching_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_tenant_id UUID NOT NULL,
    source_deal_id UUID NOT NULL,
    target_anonymous_id UUID REFERENCES deal_matching.anonymous_deal_profiles(id),

    -- Similarity scoring
    overall_similarity_score DECIMAL(4,3) NOT NULL CHECK (overall_similarity_score >= 0 AND overall_similarity_score <= 1),
    confidence_score DECIMAL(4,3) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),

    -- Detailed similarity breakdown
    financial_similarity DECIMAL(4,3),
    strategic_similarity DECIMAL(4,3),
    operational_similarity DECIMAL(4,3),
    geographic_similarity DECIMAL(4,3),
    temporal_similarity DECIMAL(4,3),

    -- AI-generated insights
    key_similarities TEXT[],
    potential_synergies TEXT[],
    risk_factors TEXT[],
    ai_analysis TEXT,

    -- Matching metadata
    match_rank INTEGER NOT NULL,
    algorithm_version VARCHAR(20) NOT NULL,
    calculation_time_ms INTEGER,

    -- Personalization
    personalization_boost DECIMAL(3,2) DEFAULT 0.0,
    user_preference_factors JSONB DEFAULT '{}',

    -- Result lifecycle
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_viewed BOOLEAN DEFAULT false,
    viewed_at TIMESTAMP WITH TIME ZONE,

    INDEX idx_matching_results_source (source_tenant_id, source_deal_id, match_rank),
    INDEX idx_matching_results_similarity (overall_similarity_score DESC, confidence_score DESC),
    INDEX idx_matching_results_generated (generated_at DESC)
);

-- User interactions with matching results
CREATE TABLE deal_matching.matching_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    matching_result_id UUID NOT NULL REFERENCES deal_matching.matching_results(id),

    -- Interaction details
    interaction_type VARCHAR(50) NOT NULL CHECK (interaction_type IN (
        'view', 'detailed_view', 'contact_request', 'save', 'dismiss',
        'share', 'rate', 'follow_up', 'expression_of_interest'
    )),
    interaction_duration_seconds INTEGER,

    -- User feedback
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    feedback_text TEXT,
    relevance_score INTEGER CHECK (relevance_score >= 1 AND relevance_score <= 10),

    -- Interaction context
    interaction_source VARCHAR(50) DEFAULT 'web_app',
    device_type VARCHAR(20),
    session_id UUID,

    -- Follow-up tracking
    led_to_contact BOOLEAN DEFAULT false,
    led_to_meeting BOOLEAN DEFAULT false,
    led_to_transaction BOOLEAN DEFAULT false,
    transaction_value DECIMAL(15,2),

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    INDEX idx_interactions_user (user_id, created_at DESC),
    INDEX idx_interactions_result (matching_result_id),
    INDEX idx_interactions_type (interaction_type, created_at),
    INDEX idx_interactions_success (led_to_transaction, transaction_value DESC)
);

-- User preference learning and personalization
CREATE TABLE deal_matching.user_matching_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,

    -- Learned preferences (0-1 weights)
    industry_preferences JSONB NOT NULL DEFAULT '{}',
    geography_preferences JSONB NOT NULL DEFAULT '{}',
    size_preferences JSONB NOT NULL DEFAULT '{}',
    deal_type_preferences JSONB NOT NULL DEFAULT '{}',

    -- Financial characteristic preferences
    financial_metric_preferences JSONB NOT NULL DEFAULT '{}',
    growth_pattern_preferences JSONB NOT NULL DEFAULT '{}',
    risk_tolerance_preferences JSONB NOT NULL DEFAULT '{}',

    -- Strategic preferences
    business_model_preferences JSONB NOT NULL DEFAULT '{}',
    integration_complexity_preferences JSONB NOT NULL DEFAULT '{}',
    timeline_preferences JSONB NOT NULL DEFAULT '{}',

    -- Learning metadata
    total_interactions INTEGER DEFAULT 0,
    successful_matches INTEGER DEFAULT 0,
    preference_confidence DECIMAL(3,2) DEFAULT 0.0,
    last_learning_update TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Model versioning
    preference_model_version VARCHAR(20) NOT NULL DEFAULT '1.0',

    -- Lifecycle
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(user_id),
    INDEX idx_preferences_tenant (tenant_id),
    INDEX idx_preferences_confidence (preference_confidence DESC),
    INDEX idx_preferences_updated (updated_at DESC)
);

-- Disclosure requests for anonymous deals
CREATE TABLE deal_matching.disclosure_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_tenant_id UUID NOT NULL,
    requester_user_id UUID NOT NULL,
    target_anonymous_id UUID NOT NULL REFERENCES deal_matching.anonymous_deal_profiles(id),
    target_tenant_id UUID NOT NULL, -- Owner of the anonymous deal

    -- Request details
    requested_information_level VARCHAR(50) NOT NULL CHECK (requested_information_level IN (
        'basic_contact', 'detailed_financials', 'company_identity', 'full_disclosure'
    )),
    justification TEXT NOT NULL,
    use_case_description TEXT,

    -- Requester validation
    requester_trust_score DECIMAL(3,2),
    requester_verification_level VARCHAR(50),
    requester_past_success_rate DECIMAL(3,2),

    -- AI evaluation
    ai_approval_score DECIMAL(3,2),
    ai_risk_assessment TEXT,
    ai_recommendation VARCHAR(50),

    -- Request status and response
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN (
        'pending', 'under_review', 'approved', 'denied', 'expired', 'withdrawn'
    )),
    response_message TEXT,
    approved_information_level VARCHAR(50),

    -- Disclosure tracking
    disclosure_granted_at TIMESTAMP WITH TIME ZONE,
    disclosure_expires_at TIMESTAMP WITH TIME ZONE,
    information_accessed_at TIMESTAMP WITH TIME ZONE,

    -- Audit trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by UUID,

    INDEX idx_disclosure_requests_target (target_tenant_id, status),
    INDEX idx_disclosure_requests_requester (requester_tenant_id, created_at DESC),
    INDEX idx_disclosure_requests_status (status, created_at),
    INDEX idx_disclosure_requests_ai_score (ai_approval_score DESC)
);

-- Matching performance metrics and analytics
CREATE TABLE deal_matching.matching_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,

    -- Time period for metrics
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Matching performance metrics
    total_matches_generated INTEGER DEFAULT 0,
    high_quality_matches INTEGER DEFAULT 0, -- Similarity > 0.8
    user_engagement_rate DECIMAL(5,4) DEFAULT 0.0,
    contact_conversion_rate DECIMAL(5,4) DEFAULT 0.0,
    successful_transaction_rate DECIMAL(5,4) DEFAULT 0.0,

    -- Algorithm performance
    average_match_quality DECIMAL(4,3),
    average_confidence_score DECIMAL(4,3),
    algorithm_processing_time_ms INTEGER,
    personalization_impact DECIMAL(3,2),

    -- User satisfaction metrics
    average_user_rating DECIMAL(3,2),
    relevance_score_average DECIMAL(4,2),
    user_retention_rate DECIMAL(5,4),

    -- Business impact
    total_deal_value_matched DECIMAL(18,2),
    successful_transactions_count INTEGER DEFAULT 0,
    platform_revenue_attributed DECIMAL(15,2),

    -- Calculated metrics
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    INDEX idx_matching_analytics_tenant_period (tenant_id, period_start, period_end),
    INDEX idx_matching_analytics_performance (average_match_quality DESC, user_engagement_rate DESC)
);
```

---

## 🚀 API SPECIFICATIONS

```python
# Deal Matching API Routes
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional

router = APIRouter(prefix="/api/v1/deal-matching", tags=["deal-matching"])

@router.post("/find-matches/{deal_id}", response_model=List[DealMatchResult])
async def find_deal_matches(
    deal_id: str,
    match_criteria: MatchCriteria,
    limit: int = Query(20, ge=1, le=50),
    include_personalization: bool = True,
    current_user: User = Depends(get_current_user)
) -> List[DealMatchResult]:
    """Find matching deals with AI-powered similarity analysis"""

    # Validate deal access
    deal = await deal_service.get_deal(deal_id, current_user.tenant_id)
    if not deal:
        raise HTTPException(404, "Deal not found")

    # Convert deal to characteristics for matching
    deal_characteristics = await deal_service.extract_characteristics(deal)

    # Find base matches
    base_matches = await matching_engine.find_matches(
        source_deal=deal_characteristics,
        match_criteria=match_criteria,
        limit=limit * 2  # Get more for personalization filtering
    )

    # Apply personalization if requested
    if include_personalization:
        personalized_matches = await personalization_service.get_personalized_matches(
            user_id=current_user.id,
            source_deal=deal_characteristics,
            base_matches=base_matches
        )
        final_matches = personalized_matches[:limit]
    else:
        final_matches = base_matches[:limit]

    # Track matching request for analytics
    await analytics_service.track_matching_request(
        user_id=current_user.id,
        deal_id=deal_id,
        matches_found=len(final_matches),
        criteria=match_criteria
    )

    return [DealMatchResult.from_matching_result(match) for match in final_matches]

@router.post("/anonymous-profile/{deal_id}", response_model=AnonymousProfileResponse)
async def create_anonymous_profile(
    deal_id: str,
    sharing_config: AnonymousSharingConfig,
    current_user: User = Depends(get_current_user)
) -> AnonymousProfileResponse:
    """Create anonymous deal profile for marketplace sharing"""

    # Validate deal ownership
    deal = await deal_service.get_deal(deal_id, current_user.tenant_id)
    if not deal:
        raise HTTPException(404, "Deal not found")

    # Check permissions to create anonymous profile
    if not await permissions_service.can_create_anonymous_profile(current_user, deal):
        raise HTTPException(403, "Insufficient permissions")

    # Extract deal characteristics
    deal_characteristics = await deal_service.extract_characteristics(deal)

    # Create anonymous profile
    anonymous_profile = await privacy_service.create_anonymous_deal_profile(
        deal=deal_characteristics,
        sharing_level=sharing_config.sharing_level,
        custom_permissions=sharing_config.custom_permissions
    )

    # Store profile for matching
    await deal_matching_service.store_anonymous_profile(anonymous_profile)

    # Log profile creation
    await audit_service.log_anonymous_profile_creation(
        user_id=current_user.id,
        deal_id=deal_id,
        profile_id=anonymous_profile.anonymous_id
    )

    return AnonymousProfileResponse(
        anonymous_id=anonymous_profile.anonymous_id,
        sharing_level=anonymous_profile.anonymization_level,
        expires_at=anonymous_profile.expires_at,
        estimated_matches=await matching_engine.estimate_match_count(anonymous_profile)
    )

@router.post("/interaction/{match_id}", response_model=InteractionResponse)
async def record_match_interaction(
    match_id: str,
    interaction: MatchInteractionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> InteractionResponse:
    """Record user interaction with matching result for learning"""

    # Validate match result exists and belongs to user
    match_result = await matching_service.get_match_result(match_id)
    if not match_result or match_result.source_tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Match not found")

    # Record interaction
    interaction_record = await matching_service.record_interaction(
        user_id=current_user.id,
        match_id=match_id,
        interaction_type=interaction.interaction_type,
        duration_seconds=interaction.duration_seconds,
        user_rating=interaction.user_rating,
        feedback=interaction.feedback
    )

    # Update personalization model in background
    background_tasks.add_task(
        personalization_service.update_user_preferences,
        current_user.id,
        interaction_record
    )

    # Track for analytics
    background_tasks.add_task(
        analytics_service.track_interaction,
        interaction_record
    )

    return InteractionResponse(
        interaction_id=interaction_record.id,
        personalization_updated=True,
        recommendations_refreshed=interaction.interaction_type in ['save', 'contact']
    )

@router.post("/disclosure-request", response_model=DisclosureRequestResponse)
async def request_deal_disclosure(
    disclosure_request: CreateDisclosureRequest,
    current_user: User = Depends(get_current_user)
) -> DisclosureRequestResponse:
    """Request additional information about anonymous deal"""

    # Validate anonymous profile exists
    anonymous_profile = await matching_service.get_anonymous_profile(
        disclosure_request.anonymous_id
    )
    if not anonymous_profile:
        raise HTTPException(404, "Anonymous deal not found")

    # Check if disclosure requests are enabled
    if not anonymous_profile.disclosure_requests_enabled:
        raise HTTPException(400, "Disclosure requests not enabled for this deal")

    # Calculate requester trust score
    trust_score = await trust_service.calculate_trust_score(current_user.tenant_id)

    # Create disclosure request
    request = await disclosure_service.create_request(
        requester_tenant_id=current_user.tenant_id,
        requester_user_id=current_user.id,
        target_anonymous_id=disclosure_request.anonymous_id,
        justification=disclosure_request.justification,
        requested_level=disclosure_request.information_level,
        trust_score=trust_score
    )

    # AI evaluation of request
    ai_evaluation = await ai_service.evaluate_disclosure_request(request)
    await disclosure_service.update_ai_evaluation(request.id, ai_evaluation)

    # Auto-approve high-confidence requests
    if ai_evaluation.approval_score > 0.85 and trust_score > 7.0:
        await disclosure_service.approve_request(
            request.id,
            approved_level=disclosure_request.information_level,
            auto_approved=True
        )
    else:
        # Send to deal owner for review
        await notification_service.notify_disclosure_request(request)

    return DisclosureRequestResponse.from_request(request)

@router.get("/analytics", response_model=MatchingAnalytics)
async def get_matching_analytics(
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
    current_user: User = Depends(get_current_user)
) -> MatchingAnalytics:
    """Get comprehensive matching analytics for tenant"""

    # Default to last 30 days if no period specified
    if not period_start:
        period_start = datetime.utcnow() - timedelta(days=30)
    if not period_end:
        period_end = datetime.utcnow()

    # Get analytics data
    analytics = await analytics_service.get_matching_analytics(
        tenant_id=current_user.tenant_id,
        period_start=period_start,
        period_end=period_end
    )

    return MatchingAnalytics.from_analytics_data(analytics)

@router.get("/market-intelligence", response_model=MarketIntelligence)
async def get_market_intelligence(
    industry: Optional[str] = None,
    geography: Optional[str] = None,
    deal_size_range: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> MarketIntelligence:
    """Get market intelligence and deal flow insights"""

    # Validate subscription level for market intelligence
    if not await subscription_service.has_feature(current_user.tenant_id, "market_intelligence"):
        raise HTTPException(403, "Market intelligence requires premium subscription")

    # Get market intelligence data
    market_data = await market_intelligence_service.get_insights(
        industry=industry,
        geography=geography,
        deal_size_range=deal_size_range,
        requester_tenant=current_user.tenant_id
    )

    return MarketIntelligence.from_market_data(market_data)
```

---

## 🧪 TESTING STRATEGY

```python
# Unit Tests for Matching Engine
class TestIntelligentMatching:
    async def test_financial_similarity_calculation(self):
        """Test financial similarity scoring"""
        source_deal = create_test_deal_characteristics(
            enterprise_value=10_000_000,
            revenue_ltm=8_000_000,
            ebitda_ltm=2_000_000
        )

        candidate_deal = create_test_deal_characteristics(
            enterprise_value=12_000_000,
            revenue_ltm=9_000_000,
            ebitda_ltm=2_400_000
        )

        similarity = await matching_engine._calculate_financial_similarity(
            source_deal, [candidate_deal]
        )

        assert similarity[0] > 0.8  # Should be high similarity

    async def test_privacy_preserving_anonymization(self):
        """Test anonymous profile creation"""
        source_deal = create_test_deal_characteristics()

        anonymous_profile = await privacy_service.create_anonymous_deal_profile(
            deal=source_deal,
            sharing_level="public"
        )

        # Ensure sensitive information is masked
        assert source_deal.target_company_name not in str(anonymous_profile)
        assert anonymous_profile.size_category in ["1-10M", "10-100M", "100M+"]
        assert anonymous_profile.industry_category is not None

# Integration Tests
class TestMatchingIntegration:
    async def test_end_to_end_matching_workflow(self):
        """Test complete matching workflow"""
        # Create test deals
        source_deal_id = await create_test_deal()
        target_deals = await create_test_matching_candidates(count=10)

        # Find matches
        response = await client.post(
            f"/api/v1/deal-matching/find-matches/{source_deal_id}",
            json={"industry_filter": "technology", "geography_filter": "UK"}
        )

        assert response.status_code == 200
        matches = response.json()
        assert len(matches) > 0
        assert all(match["similarity_score"] >= 0 for match in matches)

    async def test_personalization_learning(self):
        """Test that personalization improves over time"""
        user_id = "test-user"

        # Generate initial matches
        initial_matches = await get_test_matches(user_id)

        # Simulate positive interactions with tech deals
        for i in range(5):
            await matching_service.record_interaction(
                user_id=user_id,
                match_id=f"tech-match-{i}",
                interaction_type="contact",
                user_rating=5
            )

        # Get new matches - should favor tech deals
        personalized_matches = await get_test_matches(user_id)

        tech_match_ratio = sum(1 for m in personalized_matches
                              if "technology" in m.industry_category) / len(personalized_matches)

        assert tech_match_ratio > 0.6  # Should show preference for tech deals

# Performance Tests
class TestMatchingPerformance:
    async def test_matching_response_time(self):
        """Test matching performance under load"""
        start_time = time.time()

        # Find matches for deal with 1000+ candidates
        matches = await matching_engine.find_matches(
            source_deal=create_large_test_deal(),
            match_criteria=MatchCriteria(),
            limit=20
        )

        end_time = time.time()
        response_time = end_time - start_time

        assert response_time < 3.0  # Should complete within 3 seconds
        assert len(matches) == 20

    async def test_concurrent_matching_requests(self):
        """Test system performance with concurrent matching"""
        tasks = []

        for i in range(50):
            task = matching_engine.find_matches(
                source_deal=create_test_deal_characteristics(f"deal-{i}"),
                match_criteria=MatchCriteria(),
                limit=10
            )
            tasks.append(task)

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        assert total_time < 10.0  # All 50 requests in under 10 seconds
        assert all(len(result) <= 10 for result in results)
```

---

## 📊 SUCCESS METRICS

```python
class DealMatchingKPIs:
    """Key performance indicators for deal matching success"""

    # Matching Quality Metrics
    AVERAGE_MATCH_RELEVANCE = "average_match_relevance_score"
    HIGH_QUALITY_MATCH_RATE = "matches_above_80_percent_similarity"
    USER_SATISFACTION_RATING = "user_rating_average"

    # Engagement Metrics
    MATCH_VIEW_RATE = "percentage_matches_viewed"
    CONTACT_CONVERSION_RATE = "views_to_contact_conversion"
    SUCCESSFUL_CONNECTION_RATE = "contacts_to_meetings_conversion"

    # Business Impact Metrics
    DEAL_COMPLETION_RATE = "meetings_to_transactions_conversion"
    TOTAL_DEAL_VALUE_FACILITATED = "total_transaction_value_matched"
    PLATFORM_REVENUE_ATTRIBUTION = "revenue_from_successful_matches"

    # Network Effect Metrics
    ACTIVE_ANONYMOUS_PROFILES = "monthly_active_anonymous_deals"
    CROSS_TENANT_MATCHES = "matches_between_different_tenants"
    NETWORK_GROWTH_RATE = "new_connections_monthly"

    TARGET_VALUES = {
        AVERAGE_MATCH_RELEVANCE: 7.5,        # Out of 10
        HIGH_QUALITY_MATCH_RATE: 0.4,        # 40% of matches above 80% similarity
        USER_SATISFACTION_RATING: 4.2,       # Out of 5
        MATCH_VIEW_RATE: 0.8,                # 80% of matches viewed
        CONTACT_CONVERSION_RATE: 0.15,       # 15% of views lead to contact
        SUCCESSFUL_CONNECTION_RATE: 0.6,     # 60% of contacts lead to meetings
        DEAL_COMPLETION_RATE: 0.2,           # 20% of meetings lead to deals
        TOTAL_DEAL_VALUE_FACILITATED: 100_000_000,  # £100M annually
        PLATFORM_REVENUE_ATTRIBUTION: 0.3,   # 30% of platform revenue
        ACTIVE_ANONYMOUS_PROFILES: 500,      # 500 active profiles monthly
        CROSS_TENANT_MATCHES: 0.7,           # 70% of matches cross-tenant
        NETWORK_GROWTH_RATE: 0.1             # 10% monthly growth
    }
```

This Intelligent Deal Matching Engine creates the network effects that transform your platform from a tool into an ecosystem. By delivering 90%+ relevant matches while protecting confidentiality, it becomes the primary reason M&A professionals join and stay on your platform.

The combination of AI-powered similarity analysis, privacy-preserving sharing, and continuous learning ensures that the platform becomes more valuable as it grows - creating an "impossible to refuse" competitive moat.
