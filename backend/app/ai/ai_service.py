"""
Core AI Service
Central AI orchestration and model management
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
import asyncio
import json
from abc import ABC, abstractmethod

class AIModel(str, Enum):
    """AI model types available in the platform"""
    DOCUMENT_ANALYZER = "document_analyzer"
    DEAL_SCORER = "deal_scorer"
    MARKET_INTELLIGENCE = "market_intelligence"
    RISK_ASSESSOR = "risk_assessor"
    CONTENT_SUMMARIZER = "content_summarizer"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    SENTIMENT_ANALYZER = "sentiment_analyzer"
    FINANCIAL_FORECASTER = "financial_forecaster"
    WORKFLOW_PREDICTOR = "workflow_predictor"
    SEMANTIC_SEARCH = "semantic_search"

class AITask(str, Enum):
    """Types of AI tasks that can be performed"""
    ANALYZE_DOCUMENT = "analyze_document"
    SCORE_DEAL = "score_deal"
    SUMMARIZE_CONTENT = "summarize_content"
    EXTRACT_DATA = "extract_data"
    PREDICT_OUTCOME = "predict_outcome"
    GENERATE_INSIGHTS = "generate_insights"
    CLASSIFY_CONTENT = "classify_content"
    DETECT_ANOMALIES = "detect_anomalies"
    RECOMMEND_ACTIONS = "recommend_actions"
    SEARCH_SEMANTIC = "search_semantic"

@dataclass
class AIRequest:
    """AI processing request"""
    task: AITask
    model: AIModel
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    priority: int = 5  # 1-10, 10 is highest
    timeout_seconds: int = 30
    
@dataclass
class AIResponse:
    """AI processing response"""
    task: AITask
    model: AIModel
    result: Dict[str, Any]
    confidence: float  # 0.0 - 1.0
    processing_time_ms: int
    metadata: Dict[str, Any]
    timestamp: datetime
    error: Optional[str] = None
    
class AIProcessor(ABC):
    """Base class for AI processors"""
    
    @abstractmethod
    async def process(self, request: AIRequest) -> AIResponse:
        """Process an AI request"""
        pass
    
    @abstractmethod
    def supports_task(self, task: AITask) -> bool:
        """Check if processor supports a task"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        pass

class MockAIProcessor(AIProcessor):
    """Mock AI processor for development and testing"""
    
    def __init__(self, model: AIModel, supported_tasks: List[AITask]):
        self.model = model
        self.supported_tasks = supported_tasks
    
    async def process(self, request: AIRequest) -> AIResponse:
        """Process request with mock responses"""
        start_time = datetime.now()
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Generate mock results based on task
        result = self._generate_mock_result(request)
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AIResponse(
            task=request.task,
            model=request.model,
            result=result,
            confidence=0.85 + (hash(str(request.input_data)) % 15) / 100,  # Mock confidence
            processing_time_ms=processing_time,
            metadata={
                "processor": "mock",
                "version": "1.0.0",
                "model_info": self.get_model_info()
            },
            timestamp=datetime.now()
        )
    
    def supports_task(self, task: AITask) -> bool:
        return task in self.supported_tasks
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.model.value,
            "version": "mock-1.0",
            "type": "mock",
            "capabilities": [task.value for task in self.supported_tasks]
        }
    
    def _generate_mock_result(self, request: AIRequest) -> Dict[str, Any]:
        """Generate mock results based on task type"""
        if request.task == AITask.ANALYZE_DOCUMENT:
            return {
                "document_type": "financial_statement",
                "key_metrics": {
                    "revenue": "$10.5M",
                    "growth_rate": "15%",
                    "profit_margin": "12.3%"
                },
                "risk_factors": ["Market volatility", "Regulatory changes"],
                "summary": "Strong financial performance with moderate growth prospects."
            }
        
        elif request.task == AITask.SCORE_DEAL:
            return {
                "overall_score": 78,
                "financial_score": 82,
                "strategic_score": 75,
                "risk_score": 68,
                "recommendation": "Proceed with due diligence",
                "key_strengths": ["Strong market position", "Experienced team"],
                "key_concerns": ["High debt ratio", "Market saturation"]
            }
        
        elif request.task == AITask.SUMMARIZE_CONTENT:
            return {
                "executive_summary": "This document outlines key business metrics and strategic initiatives.",
                "key_points": [
                    "Revenue growth of 15% year-over-year",
                    "Expansion into new markets planned",
                    "Technology modernization underway"
                ],
                "word_count": 250,
                "reading_time_minutes": 2
            }
        
        elif request.task == AITask.EXTRACT_DATA:
            return {
                "extracted_fields": {
                    "company_name": "TechCorp Inc.",
                    "valuation": "$50M",
                    "employees": 150,
                    "location": "San Francisco, CA"
                },
                "confidence_scores": {
                    "company_name": 0.95,
                    "valuation": 0.78,
                    "employees": 0.92,
                    "location": 0.88
                }
            }
        
        elif request.task == AITask.PREDICT_OUTCOME:
            return {
                "prediction": "successful_completion",
                "probability": 0.73,
                "timeline_estimate": "6-8 weeks",
                "risk_factors": [
                    {"factor": "Regulatory approval", "impact": "medium"},
                    {"factor": "Market conditions", "impact": "low"}
                ]
            }
        
        elif request.task == AITask.GENERATE_INSIGHTS:
            return {
                "insights": [
                    {
                        "type": "trend",
                        "description": "Deal velocity has increased 25% this quarter",
                        "impact": "positive"
                    },
                    {
                        "type": "pattern",
                        "description": "Technology deals show higher success rates",
                        "impact": "informational"
                    }
                ],
                "recommendations": [
                    "Focus on technology sector opportunities",
                    "Increase deal pipeline capacity"
                ]
            }
        
        else:
            return {
                "status": "processed",
                "message": f"Mock processing completed for {request.task.value}",
                "data": request.input_data
            }

class AIService:
    """Central AI service orchestrator"""
    
    def __init__(self):
        self.processors: Dict[AIModel, AIProcessor] = {}
        self.task_queue: List[AIRequest] = []
        self.processing_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_processing_time_ms": 0
        }
        self._initialize_processors()
    
    def _initialize_processors(self):
        """Initialize AI processors with mock implementations"""
        # Document Intelligence Processor
        self.processors[AIModel.DOCUMENT_ANALYZER] = MockAIProcessor(
            AIModel.DOCUMENT_ANALYZER,
            [AITask.ANALYZE_DOCUMENT, AITask.EXTRACT_DATA, AITask.CLASSIFY_CONTENT]
        )
        
        # Deal Insights Processor
        self.processors[AIModel.DEAL_SCORER] = MockAIProcessor(
            AIModel.DEAL_SCORER,
            [AITask.SCORE_DEAL, AITask.PREDICT_OUTCOME, AITask.RECOMMEND_ACTIONS]
        )
        
        # Content Processing Processor
        self.processors[AIModel.CONTENT_SUMMARIZER] = MockAIProcessor(
            AIModel.CONTENT_SUMMARIZER,
            [AITask.SUMMARIZE_CONTENT, AITask.EXTRACT_DATA]
        )
        
        # Market Intelligence Processor
        self.processors[AIModel.MARKET_INTELLIGENCE] = MockAIProcessor(
            AIModel.MARKET_INTELLIGENCE,
            [AITask.GENERATE_INSIGHTS, AITask.PREDICT_OUTCOME, AITask.DETECT_ANOMALIES]
        )
        
        # Risk Assessment Processor
        self.processors[AIModel.RISK_ASSESSOR] = MockAIProcessor(
            AIModel.RISK_ASSESSOR,
            [AITask.ANALYZE_DOCUMENT, AITask.DETECT_ANOMALIES, AITask.PREDICT_OUTCOME]
        )
        
        # Recommendation Engine Processor
        self.processors[AIModel.RECOMMENDATION_ENGINE] = MockAIProcessor(
            AIModel.RECOMMENDATION_ENGINE,
            [AITask.RECOMMEND_ACTIONS, AITask.GENERATE_INSIGHTS]
        )
        
        # Semantic Search Processor
        self.processors[AIModel.SEMANTIC_SEARCH] = MockAIProcessor(
            AIModel.SEMANTIC_SEARCH,
            [AITask.SEARCH_SEMANTIC, AITask.CLASSIFY_CONTENT]
        )
    
    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process an AI request"""
        self.processing_stats["total_requests"] += 1
        
        try:
            # Find appropriate processor
            processor = self.processors.get(request.model)
            if not processor:
                raise ValueError(f"No processor available for model {request.model}")
            
            if not processor.supports_task(request.task):
                raise ValueError(f"Model {request.model} does not support task {request.task}")
            
            # Process the request
            response = await processor.process(request)
            
            # Update stats
            self.processing_stats["successful_requests"] += 1
            self._update_average_processing_time(response.processing_time_ms)
            
            return response
            
        except Exception as e:
            self.processing_stats["failed_requests"] += 1
            return AIResponse(
                task=request.task,
                model=request.model,
                result={},
                confidence=0.0,
                processing_time_ms=0,
                metadata={"error_type": type(e).__name__},
                timestamp=datetime.now(),
                error=str(e)
            )
    
    def _update_average_processing_time(self, processing_time_ms: int):
        """Update running average processing time"""
        current_avg = self.processing_stats["average_processing_time_ms"]
        total_successful = self.processing_stats["successful_requests"]
        
        if total_successful == 1:
            self.processing_stats["average_processing_time_ms"] = processing_time_ms
        else:
            new_avg = ((current_avg * (total_successful - 1)) + processing_time_ms) / total_successful
            self.processing_stats["average_processing_time_ms"] = int(new_avg)
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available AI models"""
        models = []
        for model, processor in self.processors.items():
            model_info = processor.get_model_info()
            model_info["model_id"] = model.value
            models.append(model_info)
        return models
    
    def get_model_capabilities(self, model: AIModel) -> List[str]:
        """Get capabilities of a specific model"""
        processor = self.processors.get(model)
        if not processor:
            return []
        
        return [task.value for task in AITask if processor.supports_task(task)]
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get AI processing statistics"""
        stats = self.processing_stats.copy()
        stats["active_models"] = len(self.processors)
        stats["success_rate"] = (
            stats["successful_requests"] / max(stats["total_requests"], 1)
        ) * 100
        return stats
    
    async def batch_process(self, requests: List[AIRequest]) -> List[AIResponse]:
        """Process multiple AI requests in parallel"""
        tasks = [self.process_request(request) for request in requests]
        return await asyncio.gather(*tasks, return_exceptions=False)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on AI service"""
        return {
            "status": "healthy",
            "active_processors": len(self.processors),
            "processing_stats": self.get_processing_stats(),
            "timestamp": datetime.now().isoformat()
        }

# Global AI service instance
_ai_service: Optional[AIService] = None

def get_ai_service() -> AIService:
    """Get global AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service

# Utility functions for common AI tasks
async def analyze_document(document_content: str, document_type: str = "unknown", 
                          user_id: Optional[str] = None, 
                          organization_id: Optional[str] = None) -> AIResponse:
    """Analyze a document using AI"""
    request = AIRequest(
        task=AITask.ANALYZE_DOCUMENT,
        model=AIModel.DOCUMENT_ANALYZER,
        input_data={
            "content": document_content,
            "document_type": document_type
        },
        user_id=user_id,
        organization_id=organization_id
    )
    return await get_ai_service().process_request(request)

async def score_deal(deal_data: Dict[str, Any], 
                     user_id: Optional[str] = None, 
                     organization_id: Optional[str] = None) -> AIResponse:
    """Score a deal using AI"""
    request = AIRequest(
        task=AITask.SCORE_DEAL,
        model=AIModel.DEAL_SCORER,
        input_data=deal_data,
        user_id=user_id,
        organization_id=organization_id
    )
    return await get_ai_service().process_request(request)

async def summarize_content(content: str, max_length: int = 500,
                           user_id: Optional[str] = None, 
                           organization_id: Optional[str] = None) -> AIResponse:
    """Summarize content using AI"""
    request = AIRequest(
        task=AITask.SUMMARIZE_CONTENT,
        model=AIModel.CONTENT_SUMMARIZER,
        input_data={
            "content": content,
            "max_length": max_length
        },
        user_id=user_id,
        organization_id=organization_id
    )
    return await get_ai_service().process_request(request)

async def generate_insights(data: Dict[str, Any], context: str = "general",
                           user_id: Optional[str] = None, 
                           organization_id: Optional[str] = None) -> AIResponse:
    """Generate insights from data using AI"""
    request = AIRequest(
        task=AITask.GENERATE_INSIGHTS,
        model=AIModel.MARKET_INTELLIGENCE,
        input_data=data,
        context={"analysis_context": context},
        user_id=user_id,
        organization_id=organization_id
    )
    return await get_ai_service().process_request(request)