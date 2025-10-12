"""
Deal Insights Service
AI-powered deal analysis, scoring, and market intelligence
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics
from .ai_service import AIService, AIRequest, AIResponse, AITask, AIModel, get_ai_service

class DealStage(str, Enum):
    """Deal pipeline stages"""
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    INITIAL_CONTACT = "initial_contact"
    PRELIMINARY_REVIEW = "preliminary_review"
    DUE_DILIGENCE = "due_diligence"
    TERM_NEGOTIATION = "term_negotiation"
    LEGAL_REVIEW = "legal_review"
    CLOSING = "closing"
    COMPLETED = "completed"
    LOST = "lost"

class DealCategory(str, Enum):
    """Deal categorization"""
    ACQUISITION = "acquisition"
    MERGER = "merger"
    STRATEGIC_INVESTMENT = "strategic_investment"
    PRIVATE_EQUITY = "private_equity"
    VENTURE_CAPITAL = "venture_capital"
    ASSET_PURCHASE = "asset_purchase"
    JOINT_VENTURE = "joint_venture"
    PARTNERSHIP = "partnership"

class IndustryVertical(str, Enum):
    """Industry verticals for market analysis"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCIAL_SERVICES = "financial_services"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    ENERGY = "energy"
    REAL_ESTATE = "real_estate"
    TELECOMMUNICATIONS = "telecommunications"
    AUTOMOTIVE = "automotive"
    CONSUMER_GOODS = "consumer_goods"
    MEDIA_ENTERTAINMENT = "media_entertainment"
    AEROSPACE = "aerospace"
    AGRICULTURE = "agriculture"
    OTHER = "other"

@dataclass
class DealScore:
    """Comprehensive deal scoring result"""
    deal_id: str
    overall_score: int  # 0-100
    financial_score: int  # 0-100
    strategic_score: int  # 0-100
    market_score: int  # 0-100
    risk_score: int  # 0-100 (lower is better)
    execution_score: int  # 0-100
    recommendation: str
    confidence_level: float  # 0.0-1.0
    key_strengths: List[str]
    key_concerns: List[str]
    score_breakdown: Dict[str, Any]
    timestamp: datetime
    
@dataclass
class MarketIntelligence:
    """Market intelligence and trends analysis"""
    industry: IndustryVertical
    market_trends: List[Dict[str, Any]]
    competitive_landscape: Dict[str, Any]
    valuation_benchmarks: Dict[str, float]
    growth_projections: Dict[str, float]
    risk_factors: List[str]
    opportunities: List[str]
    market_sentiment: float  # -1.0 to 1.0
    confidence_score: float  # 0.0 to 1.0
    analysis_date: datetime
    
@dataclass
class DealRecommendation:
    """AI-generated deal recommendation"""
    deal_id: str
    recommendation_type: str  # "proceed", "cautious", "reject", "more_info"
    priority_level: int  # 1-5, 5 is highest
    reasoning: List[str]
    suggested_actions: List[str]
    timeline_estimate: str
    resource_requirements: Dict[str, Any]
    success_probability: float  # 0.0-1.0
    generated_at: datetime
    
class DealInsightsService:
    """AI-powered deal insights and analysis service"""
    
    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or get_ai_service()
        self.scoring_weights = self._initialize_scoring_weights()
        self.industry_benchmarks = self._initialize_industry_benchmarks()
        
    def _initialize_scoring_weights(self) -> Dict[str, float]:
        """Initialize weights for deal scoring components"""
        return {
            "financial_performance": 0.25,
            "strategic_fit": 0.20,
            "market_position": 0.15,
            "management_team": 0.15,
            "execution_risk": 0.10,
            "financial_risk": 0.10,
            "regulatory_risk": 0.05
        }
    
    def _initialize_industry_benchmarks(self) -> Dict[IndustryVertical, Dict[str, float]]:
        """Initialize industry benchmarks for comparison"""
        return {
            IndustryVertical.TECHNOLOGY: {
                "avg_revenue_multiple": 8.5,
                "avg_ebitda_multiple": 15.2,
                "avg_growth_rate": 25.0,
                "avg_margin": 18.5
            },
            IndustryVertical.HEALTHCARE: {
                "avg_revenue_multiple": 4.2,
                "avg_ebitda_multiple": 12.8,
                "avg_growth_rate": 12.0,
                "avg_margin": 15.2
            },
            IndustryVertical.FINANCIAL_SERVICES: {
                "avg_revenue_multiple": 3.8,
                "avg_ebitda_multiple": 11.5,
                "avg_growth_rate": 8.5,
                "avg_margin": 22.1
            },
            IndustryVertical.MANUFACTURING: {
                "avg_revenue_multiple": 2.1,
                "avg_ebitda_multiple": 8.9,
                "avg_growth_rate": 6.2,
                "avg_margin": 12.8
            }
            # Add more industries as needed
        }
    
    async def score_deal(self, deal_data: Dict[str, Any],
                        user_id: Optional[str] = None,
                        organization_id: Optional[str] = None) -> DealScore:
        """Generate comprehensive deal score using AI analysis"""
        # Prepare data for AI analysis
        ai_request = AIRequest(
            task=AITask.SCORE_DEAL,
            model=AIModel.DEAL_SCORER,
            input_data=deal_data,
            context={
                "scoring_weights": self.scoring_weights,
                "include_breakdown": True,
                "industry_benchmarks": self.industry_benchmarks.get(
                    IndustryVertical(deal_data.get("industry", "other")), {}
                )
            },
            user_id=user_id,
            organization_id=organization_id
        )
        
        ai_response = await self.ai_service.process_request(ai_request)
        result = ai_response.result
        
        # Calculate component scores
        financial_score = self._calculate_financial_score(deal_data)
        strategic_score = self._calculate_strategic_score(deal_data)
        market_score = self._calculate_market_score(deal_data)
        risk_score = self._calculate_risk_score(deal_data)
        execution_score = self._calculate_execution_score(deal_data)
        
        # Calculate overall score
        overall_score = int(
            (financial_score * 0.3) +
            (strategic_score * 0.25) +
            (market_score * 0.20) +
            ((100 - risk_score) * 0.15) +  # Invert risk score
            (execution_score * 0.10)
        )
        
        return DealScore(
            deal_id=deal_data.get("deal_id", "unknown"),
            overall_score=overall_score,
            financial_score=financial_score,
            strategic_score=strategic_score,
            market_score=market_score,
            risk_score=risk_score,
            execution_score=execution_score,
            recommendation=result.get("recommendation", "Review required"),
            confidence_level=ai_response.confidence,
            key_strengths=result.get("key_strengths", []),
            key_concerns=result.get("key_concerns", []),
            score_breakdown={
                "financial": financial_score,
                "strategic": strategic_score,
                "market": market_score,
                "risk": risk_score,
                "execution": execution_score,
                "ai_insights": result
            },
            timestamp=datetime.now()
        )
    
    async def analyze_market_intelligence(self, industry: IndustryVertical,
                                        geographic_focus: Optional[str] = None,
                                        user_id: Optional[str] = None,
                                        organization_id: Optional[str] = None) -> MarketIntelligence:
        """Generate market intelligence report for an industry"""
        ai_request = AIRequest(
            task=AITask.GENERATE_INSIGHTS,
            model=AIModel.MARKET_INTELLIGENCE,
            input_data={
                "industry": industry.value,
                "geographic_focus": geographic_focus,
                "analysis_type": "market_intelligence",
                "include_trends": True,
                "include_benchmarks": True,
                "include_projections": True
            },
            context={
                "industry_benchmarks": self.industry_benchmarks.get(industry, {}),
                "analysis_depth": "comprehensive"
            },
            user_id=user_id,
            organization_id=organization_id
        )
        
        ai_response = await self.ai_service.process_request(ai_request)
        insights = ai_response.result.get("insights", [])
        
        # Extract market trends
        market_trends = []
        for insight in insights:
            if insight.get("type") == "trend":
                market_trends.append({
                    "trend": insight.get("description", ""),
                    "impact": insight.get("impact", "medium"),
                    "confidence": 0.8,
                    "timeline": "12-18 months"
                })
        
        # Generate competitive landscape
        competitive_landscape = {
            "market_concentration": "moderate",
            "key_players": 5,
            "barriers_to_entry": "medium",
            "competitive_intensity": "high"
        }
        
        # Get valuation benchmarks
        benchmarks = self.industry_benchmarks.get(industry, {})
        
        return MarketIntelligence(
            industry=industry,
            market_trends=market_trends,
            competitive_landscape=competitive_landscape,
            valuation_benchmarks=benchmarks,
            growth_projections={
                "1_year": benchmarks.get("avg_growth_rate", 10.0),
                "3_year": benchmarks.get("avg_growth_rate", 10.0) * 0.8,
                "5_year": benchmarks.get("avg_growth_rate", 10.0) * 0.6
            },
            risk_factors=[
                "Market volatility",
                "Regulatory changes",
                "Technology disruption",
                "Economic conditions"
            ],
            opportunities=[
                "Digital transformation",
                "Market consolidation",
                "International expansion",
                "Product innovation"
            ],
            market_sentiment=0.15,  # Slightly positive
            confidence_score=ai_response.confidence,
            analysis_date=datetime.now()
        )
    
    async def generate_deal_recommendations(self, deals_data: List[Dict[str, Any]],
                                          criteria: Dict[str, Any] = None,
                                          user_id: Optional[str] = None,
                                          organization_id: Optional[str] = None) -> List[DealRecommendation]:
        """Generate AI-powered recommendations for multiple deals"""
        recommendations = []
        
        for deal_data in deals_data:
            # Score the deal first
            deal_score = await self.score_deal(deal_data, user_id, organization_id)
            
            # Generate recommendation based on score
            recommendation_type = self._determine_recommendation_type(deal_score)
            priority_level = self._calculate_priority_level(deal_score)
            
            # Use AI for detailed reasoning
            ai_request = AIRequest(
                task=AITask.RECOMMEND_ACTIONS,
                model=AIModel.RECOMMENDATION_ENGINE,
                input_data={
                    "deal_data": deal_data,
                    "deal_score": deal_score.__dict__,
                    "criteria": criteria or {}
                },
                user_id=user_id,
                organization_id=organization_id
            )
            
            ai_response = await self.ai_service.process_request(ai_request)
            ai_result = ai_response.result
            
            recommendation = DealRecommendation(
                deal_id=deal_data.get("deal_id", "unknown"),
                recommendation_type=recommendation_type,
                priority_level=priority_level,
                reasoning=ai_result.get("reasoning", []),
                suggested_actions=ai_result.get("suggested_actions", []),
                timeline_estimate=self._estimate_timeline(deal_score),
                resource_requirements={
                    "analyst_hours": 40 if deal_score.overall_score > 70 else 20,
                    "due_diligence_weeks": 6 if deal_score.overall_score > 80 else 4,
                    "estimated_cost": "$50K-100K" if deal_score.overall_score > 75 else "$25K-50K"
                },
                success_probability=deal_score.overall_score / 100.0,
                generated_at=datetime.now()
            )
            
            recommendations.append(recommendation)
        
        # Sort by priority and score
        recommendations.sort(key=lambda x: (x.priority_level, x.success_probability), reverse=True)
        
        return recommendations
    
    def _calculate_financial_score(self, deal_data: Dict[str, Any]) -> int:
        """Calculate financial component score"""
        score = 50  # Base score
        
        # Revenue growth
        growth_rate = deal_data.get("revenue_growth_rate", 0)
        if growth_rate > 20:
            score += 20
        elif growth_rate > 10:
            score += 10
        elif growth_rate < 0:
            score -= 15
        
        # Profitability
        ebitda_margin = deal_data.get("ebitda_margin", 0)
        if ebitda_margin > 15:
            score += 15
        elif ebitda_margin > 5:
            score += 8
        elif ebitda_margin < 0:
            score -= 20
        
        # Debt levels
        debt_to_equity = deal_data.get("debt_to_equity", 1.0)
        if debt_to_equity < 0.5:
            score += 10
        elif debt_to_equity > 2.0:
            score -= 15
        
        return max(0, min(100, score))
    
    def _calculate_strategic_score(self, deal_data: Dict[str, Any]) -> int:
        """Calculate strategic fit score"""
        score = 50  # Base score
        
        # Strategic alignment
        strategic_fit = deal_data.get("strategic_fit_rating", 3)  # 1-5 scale
        score += (strategic_fit - 3) * 15
        
        # Market position
        market_position = deal_data.get("market_position", "unknown")
        if market_position == "leader":
            score += 20
        elif market_position == "challenger":
            score += 10
        elif market_position == "niche":
            score += 5
        
        # Synergy potential
        synergy_potential = deal_data.get("synergy_potential", "medium")
        if synergy_potential == "high":
            score += 15
        elif synergy_potential == "low":
            score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_market_score(self, deal_data: Dict[str, Any]) -> int:
        """Calculate market attractiveness score"""
        score = 50  # Base score
        
        # Market size
        market_size = deal_data.get("market_size", "unknown")
        if market_size == "large":
            score += 20
        elif market_size == "medium":
            score += 10
        elif market_size == "small":
            score -= 5
        
        # Market growth
        market_growth = deal_data.get("market_growth_rate", 5)
        if market_growth > 15:
            score += 15
        elif market_growth > 5:
            score += 8
        elif market_growth < 0:
            score -= 15
        
        # Competitive intensity
        competition = deal_data.get("competitive_intensity", "medium")
        if competition == "low":
            score += 15
        elif competition == "high":
            score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_risk_score(self, deal_data: Dict[str, Any]) -> int:
        """Calculate risk score (higher means more risky)"""
        score = 30  # Base risk score
        
        # Financial risk factors
        if deal_data.get("revenue_concentration", 0) > 50:
            score += 15  # Customer concentration risk
        
        if deal_data.get("debt_to_equity", 1.0) > 2.0:
            score += 20  # High leverage risk
        
        # Operational risk factors
        management_risk = deal_data.get("management_risk", "medium")
        if management_risk == "high":
            score += 15
        elif management_risk == "low":
            score -= 5
        
        # Regulatory risk
        regulatory_risk = deal_data.get("regulatory_risk", "medium")
        if regulatory_risk == "high":
            score += 20
        elif regulatory_risk == "low":
            score -= 10
        
        # Market risk
        market_volatility = deal_data.get("market_volatility", "medium")
        if market_volatility == "high":
            score += 10
        
        return max(0, min(100, score))
    
    def _calculate_execution_score(self, deal_data: Dict[str, Any]) -> int:
        """Calculate execution feasibility score"""
        score = 60  # Base score
        
        # Deal complexity
        complexity = deal_data.get("deal_complexity", "medium")
        if complexity == "low":
            score += 15
        elif complexity == "high":
            score -= 20
        
        # Integration difficulty
        integration_risk = deal_data.get("integration_risk", "medium")
        if integration_risk == "low":
            score += 10
        elif integration_risk == "high":
            score -= 15
        
        # Timeline feasibility
        timeline_pressure = deal_data.get("timeline_pressure", "medium")
        if timeline_pressure == "low":
            score += 10
        elif timeline_pressure == "high":
            score -= 10
        
        return max(0, min(100, score))
    
    def _determine_recommendation_type(self, deal_score: DealScore) -> str:
        """Determine recommendation type based on deal score"""
        if deal_score.overall_score >= 80:
            return "proceed"
        elif deal_score.overall_score >= 60:
            return "cautious"
        elif deal_score.overall_score >= 40:
            return "more_info"
        else:
            return "reject"
    
    def _calculate_priority_level(self, deal_score: DealScore) -> int:
        """Calculate priority level (1-5) based on deal score"""
        if deal_score.overall_score >= 85:
            return 5
        elif deal_score.overall_score >= 70:
            return 4
        elif deal_score.overall_score >= 55:
            return 3
        elif deal_score.overall_score >= 40:
            return 2
        else:
            return 1
    
    def _estimate_timeline(self, deal_score: DealScore) -> str:
        """Estimate deal completion timeline"""
        if deal_score.execution_score >= 80:
            return "4-6 weeks"
        elif deal_score.execution_score >= 60:
            return "6-10 weeks"
        elif deal_score.execution_score >= 40:
            return "10-16 weeks"
        else:
            return "16+ weeks"
    
    def get_industry_benchmarks(self, industry: IndustryVertical) -> Dict[str, float]:
        """Get benchmarks for a specific industry"""
        return self.industry_benchmarks.get(industry, {})
    
    def get_supported_industries(self) -> List[str]:
        """Get list of supported industries"""
        return [industry.value for industry in IndustryVertical]
    
    def get_scoring_methodology(self) -> Dict[str, Any]:
        """Get information about the scoring methodology"""
        return {
            "weights": self.scoring_weights,
            "components": {
                "financial_score": "Revenue growth, profitability, debt levels",
                "strategic_score": "Strategic fit, market position, synergies",
                "market_score": "Market size, growth, competitive intensity",
                "risk_score": "Financial, operational, regulatory, market risks",
                "execution_score": "Deal complexity, integration risk, timeline"
            },
            "scale": "0-100 for all components",
            "overall_calculation": "Weighted average of all components"
        }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "supported_industries": len(IndustryVertical),
            "scoring_components": len(self.scoring_weights),
            "ai_service_stats": self.ai_service.get_processing_stats(),
            "service_status": "active"
        }

# Global deal insights service
_deal_insights_service: Optional[DealInsightsService] = None

def get_deal_insights_service() -> DealInsightsService:
    """Get global deal insights service instance"""
    global _deal_insights_service
    if _deal_insights_service is None:
        _deal_insights_service = DealInsightsService()
    return _deal_insights_service