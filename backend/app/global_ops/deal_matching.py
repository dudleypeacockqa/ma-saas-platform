"""
Deal Matching Engine - Sprint 11
AI-powered intelligent deal matching and strategic fit analysis
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json
import math
from abc import ABC, abstractmethod


class DealType(str, Enum):
    ACQUISITION = "acquisition"
    MERGER = "merger"
    JOINT_VENTURE = "joint_venture"
    STRATEGIC_PARTNERSHIP = "strategic_partnership"
    ASSET_PURCHASE = "asset_purchase"
    SPIN_OFF = "spin_off"
    MANAGEMENT_BUYOUT = "management_buyout"
    LEVERAGED_BUYOUT = "leveraged_buyout"


class MatchingCriteria(str, Enum):
    INDUSTRY_ALIGNMENT = "industry_alignment"
    GEOGRAPHIC_SYNERGY = "geographic_synergy"
    FINANCIAL_COMPATIBILITY = "financial_compatibility"
    STRATEGIC_FIT = "strategic_fit"
    CULTURAL_ALIGNMENT = "cultural_alignment"
    TECHNOLOGY_SYNERGY = "technology_synergy"
    MARKET_POSITIONING = "market_positioning"
    REGULATORY_COMPATIBILITY = "regulatory_compatibility"


class DealStage(str, Enum):
    OPPORTUNITY_IDENTIFICATION = "opportunity_identification"
    INITIAL_SCREENING = "initial_screening"
    DETAILED_ANALYSIS = "detailed_analysis"
    VALUATION = "valuation"
    NEGOTIATION = "negotiation"
    DUE_DILIGENCE = "due_diligence"
    CLOSING = "closing"
    INTEGRATION = "integration"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CompanyProfile:
    company_id: str
    name: str
    industry_sector: str
    geographic_regions: List[str]
    revenue: Optional[float]
    employees: Optional[int]
    valuation: Optional[float]
    growth_rate: Optional[float]
    technology_stack: List[str]
    market_position: str
    financial_health_score: float
    strategic_priorities: List[str]
    available_for: List[DealType]
    created_at: datetime
    updated_at: datetime


@dataclass
class MatchScore:
    overall_score: float
    criteria_scores: Dict[MatchingCriteria, float]
    confidence_level: float
    explanation: str
    key_synergies: List[str]
    potential_challenges: List[str]
    score_breakdown: Dict[str, Any]


@dataclass
class DealMatch:
    match_id: str
    buyer_profile: CompanyProfile
    seller_profile: CompanyProfile
    deal_type: DealType
    match_score: MatchScore
    estimated_deal_value: Optional[float]
    strategic_rationale: str
    synergy_potential: float
    risk_assessment: Dict[str, Any]
    timeline_estimate: int  # days
    match_date: datetime
    status: str


@dataclass
class StrategicFitAnalysis:
    analysis_id: str
    buyer_id: str
    target_id: str
    strategic_alignment_score: float
    operational_synergies: List[Dict[str, Any]]
    financial_synergies: List[Dict[str, Any]]
    market_synergies: List[Dict[str, Any]]
    technology_synergies: List[Dict[str, Any]]
    integration_complexity: float
    cultural_fit_score: float
    regulatory_fit_score: float
    overall_recommendation: str
    analysis_date: datetime


@dataclass
class MarketTimingAnalysis:
    timing_id: str
    deal_type: DealType
    industry_sector: str
    geographic_region: str
    market_conditions_score: float
    timing_recommendation: str
    optimal_window_start: datetime
    optimal_window_end: datetime
    key_timing_factors: List[str]
    competitive_activity: str
    regulatory_calendar: List[Dict[str, Any]]
    analysis_date: datetime


class ScoringAlgorithm(ABC):
    """Abstract base class for scoring algorithms"""

    @abstractmethod
    def calculate_score(self, buyer: CompanyProfile, seller: CompanyProfile, criteria: MatchingCriteria) -> float:
        pass


class IndustryAlignmentScorer(ScoringAlgorithm):
    """Scores industry alignment between companies"""

    def calculate_score(self, buyer: CompanyProfile, seller: CompanyProfile, criteria: MatchingCriteria) -> float:
        if buyer.industry_sector == seller.industry_sector:
            return 1.0
        elif self._are_related_industries(buyer.industry_sector, seller.industry_sector):
            return 0.7
        else:
            return 0.3

    def _are_related_industries(self, industry1: str, industry2: str) -> bool:
        # Simplified industry relationship mapping
        related_industries = {
            "technology": ["telecommunications", "media", "financial_services"],
            "healthcare": ["pharmaceuticals", "medical_devices", "biotechnology"],
            "financial_services": ["technology", "insurance", "real_estate"],
            "manufacturing": ["automotive", "aerospace", "industrial"]
        }

        return (
            industry2 in related_industries.get(industry1, []) or
            industry1 in related_industries.get(industry2, [])
        )


class GeographicSynergyScorer(ScoringAlgorithm):
    """Scores geographic synergy potential"""

    def calculate_score(self, buyer: CompanyProfile, seller: CompanyProfile, criteria: MatchingCriteria) -> float:
        buyer_regions = set(buyer.geographic_regions)
        seller_regions = set(seller.geographic_regions)

        # Calculate overlap and complementarity
        overlap = len(buyer_regions.intersection(seller_regions))
        total_regions = len(buyer_regions.union(seller_regions))

        if total_regions == 0:
            return 0.5

        # Higher score for some overlap but also new market access
        overlap_ratio = overlap / len(buyer_regions) if buyer_regions else 0
        expansion_potential = len(seller_regions - buyer_regions) / len(buyer_regions) if buyer_regions else 0

        score = (overlap_ratio * 0.4) + (min(expansion_potential, 1.0) * 0.6)
        return min(score, 1.0)


class FinancialCompatibilityScorer(ScoringAlgorithm):
    """Scores financial compatibility"""

    def calculate_score(self, buyer: CompanyProfile, seller: CompanyProfile, criteria: MatchingCriteria) -> float:
        # Check if both have financial data
        if not all([buyer.revenue, seller.revenue, buyer.valuation, seller.valuation]):
            return 0.5  # Default score when data is missing

        # Size compatibility - prefer targets that are 10-50% of buyer size
        size_ratio = seller.revenue / buyer.revenue if buyer.revenue > 0 else 0

        if 0.1 <= size_ratio <= 0.5:
            size_score = 1.0
        elif 0.05 <= size_ratio <= 0.75:
            size_score = 0.8
        elif size_ratio <= 1.0:
            size_score = 0.6
        else:
            size_score = 0.3

        # Financial health compatibility
        health_score = min(buyer.financial_health_score, seller.financial_health_score)

        # Growth compatibility
        growth_compatibility = 1.0
        if buyer.growth_rate and seller.growth_rate:
            growth_diff = abs(buyer.growth_rate - seller.growth_rate)
            growth_compatibility = max(0.5, 1.0 - (growth_diff / 50))  # Penalty for large growth differences

        # Weighted average
        final_score = (size_score * 0.4) + (health_score * 0.4) + (growth_compatibility * 0.2)
        return min(final_score, 1.0)


class StrategicFitScorer(ScoringAlgorithm):
    """Scores strategic fit and synergy potential"""

    def calculate_score(self, buyer: CompanyProfile, seller: CompanyProfile, criteria: MatchingCriteria) -> float:
        # Check strategic priorities alignment
        buyer_priorities = set(buyer.strategic_priorities)
        seller_capabilities = set(seller.technology_stack + [seller.market_position])

        alignment_score = len(buyer_priorities.intersection(seller_capabilities)) / len(buyer_priorities) if buyer_priorities else 0.5

        # Market position complementarity
        position_scores = {
            ("market_leader", "niche_player"): 0.9,
            ("market_leader", "emerging_player"): 0.8,
            ("growth_company", "established_player"): 0.85,
            ("niche_player", "market_leader"): 0.7
        }

        position_score = position_scores.get((buyer.market_position, seller.market_position), 0.6)

        # Technology synergy
        tech_overlap = len(set(buyer.technology_stack).intersection(set(seller.technology_stack)))
        tech_expansion = len(set(seller.technology_stack) - set(buyer.technology_stack))
        tech_score = min(1.0, (tech_overlap * 0.3 + tech_expansion * 0.7) / 5)  # Normalize

        # Weighted combination
        final_score = (alignment_score * 0.4) + (position_score * 0.3) + (tech_score * 0.3)
        return min(final_score, 1.0)


class DealMatchingEngine:
    """AI-powered deal matching and strategic fit analysis engine"""

    def __init__(self):
        self.company_profiles: Dict[str, CompanyProfile] = {}
        self.scoring_algorithms: Dict[MatchingCriteria, ScoringAlgorithm] = {
            MatchingCriteria.INDUSTRY_ALIGNMENT: IndustryAlignmentScorer(),
            MatchingCriteria.GEOGRAPHIC_SYNERGY: GeographicSynergyScorer(),
            MatchingCriteria.FINANCIAL_COMPATIBILITY: FinancialCompatibilityScorer(),
            MatchingCriteria.STRATEGIC_FIT: StrategicFitScorer()
        }
        self.deal_matches: List[DealMatch] = []
        self.matching_history: List[Dict[str, Any]] = []

    def add_company_profile(self, profile: CompanyProfile) -> bool:
        """Add or update a company profile"""
        self.company_profiles[profile.company_id] = profile
        return True

    def find_matches(
        self,
        buyer_id: str,
        deal_type: DealType,
        criteria_weights: Optional[Dict[MatchingCriteria, float]] = None,
        min_score_threshold: float = 0.6,
        max_results: int = 10
    ) -> List[DealMatch]:
        """Find potential deal matches for a buyer"""

        if buyer_id not in self.company_profiles:
            raise ValueError(f"Buyer profile not found: {buyer_id}")

        buyer_profile = self.company_profiles[buyer_id]

        # Default criteria weights
        if criteria_weights is None:
            criteria_weights = {
                MatchingCriteria.STRATEGIC_FIT: 0.3,
                MatchingCriteria.FINANCIAL_COMPATIBILITY: 0.25,
                MatchingCriteria.INDUSTRY_ALIGNMENT: 0.2,
                MatchingCriteria.GEOGRAPHIC_SYNERGY: 0.15,
                MatchingCriteria.TECHNOLOGY_SYNERGY: 0.1
            }

        matches = []

        # Evaluate all potential targets
        for seller_id, seller_profile in self.company_profiles.items():
            if seller_id == buyer_id:
                continue

            # Check if seller is available for this deal type
            if deal_type not in seller_profile.available_for:
                continue

            # Calculate match score
            match_score = self._calculate_match_score(
                buyer_profile, seller_profile, criteria_weights
            )

            # Only include matches above threshold
            if match_score.overall_score >= min_score_threshold:
                # Estimate deal value
                estimated_value = self._estimate_deal_value(buyer_profile, seller_profile, deal_type)

                # Generate strategic rationale
                rationale = self._generate_strategic_rationale(buyer_profile, seller_profile, match_score)

                # Create match object
                deal_match = DealMatch(
                    match_id=f"match_{buyer_id}_{seller_id}_{datetime.now().timestamp()}",
                    buyer_profile=buyer_profile,
                    seller_profile=seller_profile,
                    deal_type=deal_type,
                    match_score=match_score,
                    estimated_deal_value=estimated_value,
                    strategic_rationale=rationale,
                    synergy_potential=match_score.overall_score * 0.8,  # Synergy is typically less than match score
                    risk_assessment=self._assess_deal_risk(buyer_profile, seller_profile),
                    timeline_estimate=self._estimate_timeline(buyer_profile, seller_profile, deal_type),
                    match_date=datetime.now(),
                    status="identified"
                )

                matches.append(deal_match)

        # Sort by overall score and return top matches
        matches.sort(key=lambda x: x.match_score.overall_score, reverse=True)
        final_matches = matches[:max_results]

        # Store matches
        self.deal_matches.extend(final_matches)

        return final_matches

    def analyze_strategic_fit(
        self,
        buyer_id: str,
        target_id: str
    ) -> StrategicFitAnalysis:
        """Perform detailed strategic fit analysis"""

        if buyer_id not in self.company_profiles or target_id not in self.company_profiles:
            raise ValueError("Company profiles not found")

        buyer = self.company_profiles[buyer_id]
        target = self.company_profiles[target_id]

        analysis_id = f"fit_{buyer_id}_{target_id}_{datetime.now().timestamp()}"

        # Analyze different types of synergies
        operational_synergies = self._analyze_operational_synergies(buyer, target)
        financial_synergies = self._analyze_financial_synergies(buyer, target)
        market_synergies = self._analyze_market_synergies(buyer, target)
        technology_synergies = self._analyze_technology_synergies(buyer, target)

        # Calculate overall scores
        strategic_alignment = self._calculate_strategic_alignment(buyer, target)
        integration_complexity = self._assess_integration_complexity(buyer, target)
        cultural_fit = self._assess_cultural_fit(buyer, target)
        regulatory_fit = self._assess_regulatory_fit(buyer, target)

        # Generate recommendation
        overall_score = (strategic_alignment + cultural_fit + regulatory_fit) / 3
        if overall_score >= 0.8:
            recommendation = "Highly Recommended"
        elif overall_score >= 0.6:
            recommendation = "Recommended with Conditions"
        else:
            recommendation = "Not Recommended"

        return StrategicFitAnalysis(
            analysis_id=analysis_id,
            buyer_id=buyer_id,
            target_id=target_id,
            strategic_alignment_score=strategic_alignment,
            operational_synergies=operational_synergies,
            financial_synergies=financial_synergies,
            market_synergies=market_synergies,
            technology_synergies=technology_synergies,
            integration_complexity=integration_complexity,
            cultural_fit_score=cultural_fit,
            regulatory_fit_score=regulatory_fit,
            overall_recommendation=recommendation,
            analysis_date=datetime.now()
        )

    def analyze_market_timing(
        self,
        deal_type: DealType,
        industry_sector: str,
        geographic_region: str
    ) -> MarketTimingAnalysis:
        """Analyze optimal timing for deal execution"""

        timing_id = f"timing_{deal_type.value}_{industry_sector}_{datetime.now().timestamp()}"

        # Analyze market conditions
        market_conditions = self._analyze_market_conditions(industry_sector, geographic_region)

        # Determine optimal timing window
        current_date = datetime.now()
        optimal_start = current_date + timedelta(days=30)  # Allow for preparation
        optimal_end = current_date + timedelta(days=180)   # Market timing window

        # Key timing factors
        timing_factors = [
            "Regulatory calendar considerations",
            "Market valuation levels",
            "Competitive activity timing",
            "Economic cycle positioning",
            "Industry-specific seasonal factors"
        ]

        # Assess competitive activity
        competitive_activity = "moderate"  # Would be based on real market data

        # Generate regulatory calendar
        regulatory_calendar = [
            {
                "event": "Earnings season",
                "date": (current_date + timedelta(days=45)).isoformat(),
                "impact": "high"
            },
            {
                "event": "Regulatory review period",
                "date": (current_date + timedelta(days=90)).isoformat(),
                "impact": "medium"
            }
        ]

        return MarketTimingAnalysis(
            timing_id=timing_id,
            deal_type=deal_type,
            industry_sector=industry_sector,
            geographic_region=geographic_region,
            market_conditions_score=market_conditions,
            timing_recommendation="Favorable" if market_conditions > 0.7 else "Cautious",
            optimal_window_start=optimal_start,
            optimal_window_end=optimal_end,
            key_timing_factors=timing_factors,
            competitive_activity=competitive_activity,
            regulatory_calendar=regulatory_calendar,
            analysis_date=current_date
        )

    def get_match_recommendations(
        self,
        buyer_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get personalized match recommendations with insights"""

        if buyer_id not in self.company_profiles:
            raise ValueError(f"Buyer profile not found: {buyer_id}")

        buyer = self.company_profiles[buyer_id]

        # Extract preferences
        preferred_deal_types = preferences.get("deal_types", [DealType.ACQUISITION])
        preferred_industries = preferences.get("industries", [buyer.industry_sector])
        preferred_regions = preferences.get("regions", buyer.geographic_regions)
        max_deal_size = preferences.get("max_deal_size")
        min_synergy_score = preferences.get("min_synergy_score", 0.6)

        recommendations = {
            "buyer_id": buyer_id,
            "buyer_name": buyer.name,
            "generated_at": datetime.now().isoformat(),
            "total_opportunities": 0,
            "recommendations_by_type": {},
            "top_recommendations": [],
            "market_insights": {},
            "timing_analysis": {}
        }

        # Find matches for each preferred deal type
        for deal_type in preferred_deal_types:
            matches = self.find_matches(
                buyer_id=buyer_id,
                deal_type=deal_type,
                min_score_threshold=min_synergy_score
            )

            # Filter by preferences
            filtered_matches = []
            for match in matches:
                # Industry filter
                if preferred_industries and match.seller_profile.industry_sector not in preferred_industries:
                    continue

                # Region filter
                if preferred_regions:
                    seller_regions = set(match.seller_profile.geographic_regions)
                    preferred_regions_set = set(preferred_regions)
                    if not seller_regions.intersection(preferred_regions_set):
                        continue

                # Deal size filter
                if max_deal_size and match.estimated_deal_value and match.estimated_deal_value > max_deal_size:
                    continue

                filtered_matches.append(match)

            recommendations["recommendations_by_type"][deal_type.value] = {
                "count": len(filtered_matches),
                "matches": [self._match_to_dict(match) for match in filtered_matches[:5]]
            }
            recommendations["total_opportunities"] += len(filtered_matches)

            # Add to top recommendations
            recommendations["top_recommendations"].extend(filtered_matches[:3])

        # Sort top recommendations by score
        recommendations["top_recommendations"].sort(
            key=lambda x: x.match_score.overall_score,
            reverse=True
        )
        recommendations["top_recommendations"] = recommendations["top_recommendations"][:10]

        # Add market insights
        recommendations["market_insights"] = {
            "active_sectors": list(set(preferred_industries)),
            "opportunity_density": "high" if recommendations["total_opportunities"] > 20 else "moderate",
            "average_match_score": sum(
                m.match_score.overall_score for m in recommendations["top_recommendations"]
            ) / max(len(recommendations["top_recommendations"]), 1)
        }

        return recommendations

    def _calculate_match_score(
        self,
        buyer: CompanyProfile,
        seller: CompanyProfile,
        criteria_weights: Dict[MatchingCriteria, float]
    ) -> MatchScore:
        """Calculate comprehensive match score"""

        criteria_scores = {}
        weighted_sum = 0
        total_weight = 0

        # Calculate score for each criteria
        for criteria, weight in criteria_weights.items():
            if criteria in self.scoring_algorithms:
                score = self.scoring_algorithms[criteria].calculate_score(buyer, seller, criteria)
                criteria_scores[criteria] = score
                weighted_sum += score * weight
                total_weight += weight

        # Calculate overall score
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0

        # Calculate confidence level based on data availability
        confidence = self._calculate_confidence(buyer, seller)

        # Generate explanation
        explanation = self._generate_score_explanation(criteria_scores, overall_score)

        # Identify key synergies and challenges
        synergies = self._identify_synergies(buyer, seller, criteria_scores)
        challenges = self._identify_challenges(buyer, seller, criteria_scores)

        return MatchScore(
            overall_score=overall_score,
            criteria_scores=criteria_scores,
            confidence_level=confidence,
            explanation=explanation,
            key_synergies=synergies,
            potential_challenges=challenges,
            score_breakdown={
                "criteria_weights": criteria_weights,
                "weighted_scores": {k.value: v * criteria_weights.get(k, 0) for k, v in criteria_scores.items()}
            }
        )

    def _estimate_deal_value(self, buyer: CompanyProfile, seller: CompanyProfile, deal_type: DealType) -> Optional[float]:
        """Estimate deal value based on company metrics"""
        if not seller.valuation:
            return None

        # Base valuation
        base_value = seller.valuation

        # Apply deal type multipliers
        multipliers = {
            DealType.ACQUISITION: 1.2,  # Premium for control
            DealType.MERGER: 1.1,       # Merger of equals
            DealType.STRATEGIC_PARTNERSHIP: 0.3,  # Partial value
            DealType.ASSET_PURCHASE: 0.8,  # Asset value discount
            DealType.MANAGEMENT_BUYOUT: 0.9   # Management discount
        }

        multiplier = multipliers.get(deal_type, 1.0)
        return base_value * multiplier

    def _generate_strategic_rationale(self, buyer: CompanyProfile, seller: CompanyProfile, match_score: MatchScore) -> str:
        """Generate strategic rationale for the deal"""
        rationale_parts = []

        # Industry rationale
        if buyer.industry_sector == seller.industry_sector:
            rationale_parts.append(f"Strategic consolidation opportunity in {buyer.industry_sector}")
        else:
            rationale_parts.append(f"Diversification into {seller.industry_sector} sector")

        # Geographic rationale
        new_regions = set(seller.geographic_regions) - set(buyer.geographic_regions)
        if new_regions:
            rationale_parts.append(f"Market expansion into {', '.join(list(new_regions)[:2])}")

        # Financial rationale
        if seller.growth_rate and buyer.growth_rate and seller.growth_rate > buyer.growth_rate:
            rationale_parts.append("Access to higher growth business")

        # Technology rationale
        new_tech = set(seller.technology_stack) - set(buyer.technology_stack)
        if new_tech:
            rationale_parts.append(f"Technology enhancement through {', '.join(list(new_tech)[:2])}")

        return ". ".join(rationale_parts) + "."

    def _assess_deal_risk(self, buyer: CompanyProfile, seller: CompanyProfile) -> Dict[str, Any]:
        """Assess risks associated with the deal"""
        risks = {
            "overall_risk_level": "medium",
            "integration_risk": "medium",
            "financial_risk": "low",
            "regulatory_risk": "low",
            "market_risk": "medium",
            "key_risk_factors": []
        }

        # Size-based risk
        if seller.revenue and buyer.revenue:
            size_ratio = seller.revenue / buyer.revenue
            if size_ratio > 0.5:
                risks["integration_risk"] = "high"
                risks["key_risk_factors"].append("Large acquisition relative to buyer size")

        # Financial health risk
        if seller.financial_health_score < 0.6:
            risks["financial_risk"] = "high"
            risks["key_risk_factors"].append("Target financial health concerns")

        # Geographic risk
        if not set(buyer.geographic_regions).intersection(set(seller.geographic_regions)):
            risks["market_risk"] = "high"
            risks["key_risk_factors"].append("No geographic overlap - new market entry risk")

        return risks

    def _estimate_timeline(self, buyer: CompanyProfile, seller: CompanyProfile, deal_type: DealType) -> int:
        """Estimate deal completion timeline in days"""
        base_timelines = {
            DealType.ACQUISITION: 180,
            DealType.MERGER: 240,
            DealType.STRATEGIC_PARTNERSHIP: 90,
            DealType.ASSET_PURCHASE: 120,
            DealType.MANAGEMENT_BUYOUT: 150
        }

        base_timeline = base_timelines.get(deal_type, 180)

        # Adjust for complexity factors
        if seller.revenue and seller.revenue > 1_000_000_000:  # Large deal
            base_timeline += 60

        # Cross-border complexity
        if not set(buyer.geographic_regions).intersection(set(seller.geographic_regions)):
            base_timeline += 30

        # Regulatory complexity
        if buyer.industry_sector in ["financial_services", "healthcare", "telecommunications"]:
            base_timeline += 45

        return base_timeline

    # Additional helper methods for synergy analysis
    def _analyze_operational_synergies(self, buyer: CompanyProfile, target: CompanyProfile) -> List[Dict[str, Any]]:
        """Analyze operational synergy opportunities"""
        synergies = []

        # Cost synergies
        synergies.append({
            "type": "cost_reduction",
            "category": "operational",
            "description": "Elimination of duplicate functions",
            "estimated_value": target.revenue * 0.05 if target.revenue else 0,
            "realization_timeline": "12-18 months",
            "confidence": 0.8
        })

        # Scale synergies
        if buyer.revenue and target.revenue:
            combined_revenue = buyer.revenue + target.revenue
            if combined_revenue > buyer.revenue * 1.5:
                synergies.append({
                    "type": "scale_benefits",
                    "category": "operational",
                    "description": "Increased purchasing power and operational leverage",
                    "estimated_value": combined_revenue * 0.02,
                    "realization_timeline": "6-12 months",
                    "confidence": 0.7
                })

        return synergies

    def _analyze_financial_synergies(self, buyer: CompanyProfile, target: CompanyProfile) -> List[Dict[str, Any]]:
        """Analyze financial synergy opportunities"""
        synergies = []

        # Tax synergies
        synergies.append({
            "type": "tax_optimization",
            "category": "financial",
            "description": "Optimized tax structure and jurisdiction benefits",
            "estimated_value": target.revenue * 0.02 if target.revenue else 0,
            "realization_timeline": "6-12 months",
            "confidence": 0.6
        })

        # Financing synergies
        if buyer.financial_health_score > target.financial_health_score:
            synergies.append({
                "type": "financing_optimization",
                "category": "financial",
                "description": "Improved cost of capital for combined entity",
                "estimated_value": target.valuation * 0.01 if target.valuation else 0,
                "realization_timeline": "3-6 months",
                "confidence": 0.7
            })

        return synergies

    def _analyze_market_synergies(self, buyer: CompanyProfile, target: CompanyProfile) -> List[Dict[str, Any]]:
        """Analyze market synergy opportunities"""
        synergies = []

        # Market expansion
        new_regions = set(target.geographic_regions) - set(buyer.geographic_regions)
        if new_regions:
            synergies.append({
                "type": "market_expansion",
                "category": "market",
                "description": f"Access to new markets: {', '.join(list(new_regions)[:2])}",
                "estimated_value": target.revenue * 0.15 if target.revenue else 0,
                "realization_timeline": "12-24 months",
                "confidence": 0.6
            })

        # Cross-selling opportunities
        if buyer.industry_sector != target.industry_sector:
            synergies.append({
                "type": "cross_selling",
                "category": "market",
                "description": "Cross-selling opportunities to combined customer base",
                "estimated_value": min(buyer.revenue, target.revenue) * 0.1 if all([buyer.revenue, target.revenue]) else 0,
                "realization_timeline": "18-36 months",
                "confidence": 0.5
            })

        return synergies

    def _analyze_technology_synergies(self, buyer: CompanyProfile, target: CompanyProfile) -> List[Dict[str, Any]]:
        """Analyze technology synergy opportunities"""
        synergies = []

        # Technology complementarity
        new_tech = set(target.technology_stack) - set(buyer.technology_stack)
        if new_tech:
            synergies.append({
                "type": "technology_enhancement",
                "category": "technology",
                "description": f"Access to new technologies: {', '.join(list(new_tech)[:3])}",
                "estimated_value": target.valuation * 0.05 if target.valuation else 0,
                "realization_timeline": "6-18 months",
                "confidence": 0.7
            })

        return synergies

    def _calculate_strategic_alignment(self, buyer: CompanyProfile, target: CompanyProfile) -> float:
        """Calculate strategic alignment score"""
        return self.scoring_algorithms[MatchingCriteria.STRATEGIC_FIT].calculate_score(
            buyer, target, MatchingCriteria.STRATEGIC_FIT
        )

    def _assess_integration_complexity(self, buyer: CompanyProfile, target: CompanyProfile) -> float:
        """Assess integration complexity (0 = simple, 1 = complex)"""
        complexity_factors = 0

        # Size differential
        if buyer.revenue and target.revenue:
            size_ratio = target.revenue / buyer.revenue
            if size_ratio > 0.5:
                complexity_factors += 0.3

        # Geographic complexity
        if not set(buyer.geographic_regions).intersection(set(target.geographic_regions)):
            complexity_factors += 0.2

        # Industry differences
        if buyer.industry_sector != target.industry_sector:
            complexity_factors += 0.2

        # Technology stack differences
        tech_overlap = len(set(buyer.technology_stack).intersection(set(target.technology_stack)))
        total_tech = len(set(buyer.technology_stack + target.technology_stack))
        if total_tech > 0 and tech_overlap / total_tech < 0.3:
            complexity_factors += 0.3

        return min(complexity_factors, 1.0)

    def _assess_cultural_fit(self, buyer: CompanyProfile, target: CompanyProfile) -> float:
        """Assess cultural fit between organizations"""
        # Simplified cultural fit assessment
        # In production, this would consider company culture surveys, values alignment, etc.

        # Geographic cultural proximity
        cultural_score = 0.7  # Base score

        # Industry cultural alignment
        if buyer.industry_sector == target.industry_sector:
            cultural_score += 0.2

        # Size-based cultural alignment
        if buyer.employees and target.employees:
            size_ratio = min(buyer.employees, target.employees) / max(buyer.employees, target.employees)
            cultural_score += size_ratio * 0.1

        return min(cultural_score, 1.0)

    def _assess_regulatory_fit(self, buyer: CompanyProfile, target: CompanyProfile) -> float:
        """Assess regulatory compatibility"""
        # Base regulatory fit
        regulatory_score = 0.8

        # Industry regulatory complexity
        high_regulation_sectors = ["financial_services", "healthcare", "telecommunications", "energy"]
        if buyer.industry_sector in high_regulation_sectors or target.industry_sector in high_regulation_sectors:
            regulatory_score -= 0.2

        # Cross-border regulatory complexity
        if not set(buyer.geographic_regions).intersection(set(target.geographic_regions)):
            regulatory_score -= 0.1

        return max(regulatory_score, 0.3)

    def _analyze_market_conditions(self, industry_sector: str, geographic_region: str) -> float:
        """Analyze current market conditions for timing"""
        # Mock market conditions analysis
        # In production, this would use real market data

        base_score = 0.75

        # Industry-specific adjustments
        growth_sectors = ["technology", "healthcare", "renewable_energy"]
        if industry_sector in growth_sectors:
            base_score += 0.1

        # Regional adjustments
        stable_regions = ["north_america", "europe"]
        if geographic_region in stable_regions:
            base_score += 0.05

        return min(base_score, 1.0)

    def _calculate_confidence(self, buyer: CompanyProfile, seller: CompanyProfile) -> float:
        """Calculate confidence level in the match score"""
        data_completeness = 0

        # Check data availability for both companies
        for profile in [buyer, seller]:
            profile_completeness = 0
            total_fields = 8

            if profile.revenue:
                profile_completeness += 1
            if profile.employees:
                profile_completeness += 1
            if profile.valuation:
                profile_completeness += 1
            if profile.growth_rate:
                profile_completeness += 1
            if profile.technology_stack:
                profile_completeness += 1
            if profile.geographic_regions:
                profile_completeness += 1
            if profile.strategic_priorities:
                profile_completeness += 1
            if profile.financial_health_score:
                profile_completeness += 1

            data_completeness += profile_completeness / total_fields

        return data_completeness / 2  # Average of both profiles

    def _generate_score_explanation(self, criteria_scores: Dict[MatchingCriteria, float], overall_score: float) -> str:
        """Generate explanation for the match score"""
        explanations = []

        if overall_score >= 0.8:
            explanations.append("Excellent strategic fit with strong synergy potential.")
        elif overall_score >= 0.6:
            explanations.append("Good strategic alignment with notable opportunities.")
        else:
            explanations.append("Limited strategic fit with significant challenges.")

        # Highlight strongest criteria
        if criteria_scores:
            best_criteria = max(criteria_scores.items(), key=lambda x: x[1])
            if best_criteria[1] >= 0.8:
                explanations.append(f"Particularly strong {best_criteria[0].value.replace('_', ' ')}.")

        return " ".join(explanations)

    def _identify_synergies(self, buyer: CompanyProfile, seller: CompanyProfile, criteria_scores: Dict) -> List[str]:
        """Identify key synergies"""
        synergies = []

        if criteria_scores.get(MatchingCriteria.GEOGRAPHIC_SYNERGY, 0) > 0.7:
            synergies.append("Geographic market expansion opportunities")

        if criteria_scores.get(MatchingCriteria.TECHNOLOGY_SYNERGY, 0) > 0.7:
            synergies.append("Technology stack complementarity")

        if criteria_scores.get(MatchingCriteria.FINANCIAL_COMPATIBILITY, 0) > 0.7:
            synergies.append("Financial and operational scale benefits")

        if not synergies:
            synergies.append("Limited synergies identified")

        return synergies

    def _identify_challenges(self, buyer: CompanyProfile, seller: CompanyProfile, criteria_scores: Dict) -> List[str]:
        """Identify potential challenges"""
        challenges = []

        if criteria_scores.get(MatchingCriteria.CULTURAL_ALIGNMENT, 0) < 0.5:
            challenges.append("Cultural integration complexity")

        if buyer.industry_sector != seller.industry_sector:
            challenges.append("Cross-industry integration challenges")

        if not set(buyer.geographic_regions).intersection(set(seller.geographic_regions)):
            challenges.append("New market entry risks")

        if not challenges:
            challenges.append("Standard integration and execution risks")

        return challenges

    def _match_to_dict(self, match: DealMatch) -> Dict[str, Any]:
        """Convert match object to dictionary for serialization"""
        return {
            "match_id": match.match_id,
            "target_company": {
                "id": match.seller_profile.company_id,
                "name": match.seller_profile.name,
                "industry": match.seller_profile.industry_sector,
                "regions": match.seller_profile.geographic_regions
            },
            "deal_type": match.deal_type.value,
            "match_score": match.match_score.overall_score,
            "estimated_value": match.estimated_deal_value,
            "synergy_potential": match.synergy_potential,
            "timeline_estimate": match.timeline_estimate,
            "key_synergies": match.match_score.key_synergies,
            "strategic_rationale": match.strategic_rationale
        }


# Service instance and dependency injection
_deal_matching_engine: Optional[DealMatchingEngine] = None


def get_deal_matching_engine() -> DealMatchingEngine:
    """Get Deal Matching Engine instance"""
    global _deal_matching_engine
    if _deal_matching_engine is None:
        _deal_matching_engine = DealMatchingEngine()
    return _deal_matching_engine