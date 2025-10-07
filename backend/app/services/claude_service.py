import os
import json
import httpx
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from app.core.config import settings

class DealAnalysisRequest(BaseModel):
    deal_name: str
    target_company: str
    industry: Optional[str] = None
    deal_value: Optional[float] = None
    description: Optional[str] = None
    documents: Optional[List[str]] = None

class DealAnalysisResponse(BaseModel):
    analysis: str
    risk_factors: List[str]
    opportunities: List[str]
    recommendations: List[str]
    confidence_score: float

class MarketResearchRequest(BaseModel):
    industry: str
    company_name: Optional[str] = None
    geographic_focus: Optional[str] = "UK"

class MarketResearchResponse(BaseModel):
    market_overview: str
    key_players: List[str]
    market_trends: List[str]
    growth_projections: str
    competitive_landscape: str

class ClaudeService:
    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.base_url = "https://api.anthropic.com/v1"
        
    async def analyze_deal(self, request: DealAnalysisRequest) -> DealAnalysisResponse:
        """Analyze an M&A deal using Claude AI"""
        
        prompt = f"""
        As an expert M&A advisor, analyze the following deal opportunity:
        
        Deal Name: {request.deal_name}
        Target Company: {request.target_company}
        Industry: {request.industry or 'Not specified'}
        Deal Value: {f'£{request.deal_value:,.0f}' if request.deal_value else 'Not specified'}
        Description: {request.description or 'Not provided'}
        
        Please provide a comprehensive analysis including:
        1. Overall assessment of the deal
        2. Key risk factors to consider
        3. Strategic opportunities
        4. Specific recommendations for due diligence
        5. A confidence score (0-100) for deal success
        
        Format your response as JSON with the following structure:
        {{
            "analysis": "detailed analysis text",
            "risk_factors": ["risk1", "risk2", "risk3"],
            "opportunities": ["opportunity1", "opportunity2", "opportunity3"],
            "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
            "confidence_score": 75.5
        }}
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-sonnet-20240229",
                        "max_tokens": 2000,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["content"][0]["text"]
                    
                    # Parse JSON response
                    try:
                        analysis_data = json.loads(content)
                        return DealAnalysisResponse(**analysis_data)
                    except json.JSONDecodeError:
                        # Fallback if JSON parsing fails
                        return DealAnalysisResponse(
                            analysis=content,
                            risk_factors=["Unable to parse specific risks"],
                            opportunities=["Unable to parse specific opportunities"],
                            recommendations=["Review analysis manually"],
                            confidence_score=50.0
                        )
                else:
                    raise Exception(f"Claude API error: {response.status_code}")
                    
        except Exception as e:
            # Return fallback response if Claude API fails
            return DealAnalysisResponse(
                analysis=f"Analysis temporarily unavailable. Error: {str(e)}",
                risk_factors=["API service unavailable"],
                opportunities=["Manual analysis required"],
                recommendations=["Retry analysis later"],
                confidence_score=0.0
            )
    
    async def research_market(self, request: MarketResearchRequest) -> MarketResearchResponse:
        """Research market conditions for M&A opportunities"""
        
        prompt = f"""
        As a market research analyst, provide comprehensive market intelligence for M&A opportunities in:
        
        Industry: {request.industry}
        Company Focus: {request.company_name or 'General market'}
        Geographic Focus: {request.geographic_focus}
        
        Please provide:
        1. Market overview and size
        2. Key players and competitors
        3. Current market trends
        4. Growth projections
        5. Competitive landscape analysis
        
        Focus on information relevant to M&A decision-making and deal sourcing.
        
        Format as JSON:
        {{
            "market_overview": "detailed overview",
            "key_players": ["company1", "company2", "company3"],
            "market_trends": ["trend1", "trend2", "trend3"],
            "growth_projections": "growth analysis",
            "competitive_landscape": "competitive analysis"
        }}
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-sonnet-20240229",
                        "max_tokens": 2000,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["content"][0]["text"]
                    
                    try:
                        research_data = json.loads(content)
                        return MarketResearchResponse(**research_data)
                    except json.JSONDecodeError:
                        return MarketResearchResponse(
                            market_overview=content,
                            key_players=["Unable to parse specific players"],
                            market_trends=["Unable to parse specific trends"],
                            growth_projections="Unable to parse projections",
                            competitive_landscape="Unable to parse landscape"
                        )
                else:
                    raise Exception(f"Claude API error: {response.status_code}")
                    
        except Exception as e:
            return MarketResearchResponse(
                market_overview=f"Market research temporarily unavailable. Error: {str(e)}",
                key_players=["API service unavailable"],
                market_trends=["Manual research required"],
                growth_projections="Retry research later",
                competitive_landscape="Manual analysis required"
            )
    
    async def analyze_document(self, document_content: str, document_type: str = "general") -> Dict[str, Any]:
        """Analyze uploaded documents for key insights"""
        
        prompt = f"""
        Analyze the following {document_type} document for M&A due diligence:
        
        Document Content:
        {document_content[:4000]}  # Limit content to avoid token limits
        
        Please extract and summarize:
        1. Key financial metrics (if applicable)
        2. Important risks or red flags
        3. Strategic value points
        4. Compliance or legal considerations
        5. Overall assessment
        
        Provide a structured summary suitable for M&A decision-making.
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-sonnet-20240229",
                        "max_tokens": 1500,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "summary": result["content"][0]["text"],
                        "document_type": document_type,
                        "analysis_date": "2024-01-01",  # Would use actual date
                        "confidence": "high"
                    }
                else:
                    raise Exception(f"Claude API error: {response.status_code}")
                    
        except Exception as e:
            return {
                "summary": f"Document analysis temporarily unavailable. Error: {str(e)}",
                "document_type": document_type,
                "analysis_date": "2024-01-01",
                "confidence": "low"
            }

# Global service instance
claude_service = ClaudeService()
