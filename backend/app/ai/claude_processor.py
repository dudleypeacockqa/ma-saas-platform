"""
Claude AI Processor
Real AI integration using Anthropic's Claude API
"""

import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import httpx

from .ai_service import AIProcessor, AIRequest, AIResponse, AITask, AIModel


class ClaudeAIProcessor(AIProcessor):
    """Real Claude AI processor using Anthropic's API"""

    def __init__(self, model: AIModel, supported_tasks: List[AITask]):
        self.model = model
        self.supported_tasks = supported_tasks
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.max_tokens = int(os.getenv("CLAUDE_MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("CLAUDE_TEMPERATURE", "0.1"))

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    async def process(self, request: AIRequest) -> AIResponse:
        """Process request using Claude AI"""
        start_time = datetime.now()

        try:
            # Prepare Claude API request
            messages = self._build_messages(request)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": self.claude_model,
                        "max_tokens": self.max_tokens,
                        "temperature": self.temperature,
                        "messages": messages
                    },
                    timeout=30.0
                )

            if response.status_code != 200:
                raise Exception(f"Claude API error: {response.status_code} - {response.text}")

            response_data = response.json()
            result = self._parse_claude_response(request, response_data)

            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

            return AIResponse(
                task=request.task,
                model=request.model,
                result=result,
                confidence=self._calculate_confidence(result),
                processing_time_ms=processing_time,
                metadata={
                    "processor": "claude",
                    "model": self.claude_model,
                    "version": "1.0.0",
                    "usage": response_data.get("usage", {})
                },
                timestamp=datetime.now()
            )

        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            return AIResponse(
                task=request.task,
                model=request.model,
                result={},
                confidence=0.0,
                processing_time_ms=processing_time,
                metadata={"processor": "claude", "error_type": type(e).__name__},
                timestamp=datetime.now(),
                error=str(e)
            )

    def supports_task(self, task: AITask) -> bool:
        return task in self.supported_tasks

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.model.value,
            "version": self.claude_model,
            "type": "claude",
            "capabilities": [task.value for task in self.supported_tasks],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

    def _build_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        """Build messages for Claude API based on task type"""

        if request.task == AITask.SCORE_DEAL:
            return self._build_deal_scoring_messages(request)
        elif request.task == AITask.ANALYZE_DOCUMENT:
            return self._build_document_analysis_messages(request)
        elif request.task == AITask.PREDICT_OUTCOME:
            return self._build_prediction_messages(request)
        elif request.task == AITask.GENERATE_INSIGHTS:
            return self._build_insights_messages(request)
        elif request.task == AITask.RECOMMEND_ACTIONS:
            return self._build_recommendations_messages(request)
        elif request.task == AITask.DETECT_ANOMALIES:
            return self._build_anomaly_detection_messages(request)
        else:
            return self._build_generic_messages(request)

    def _build_deal_scoring_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        """Build messages for deal scoring"""
        deal_data = request.input_data

        prompt = f"""You are an expert M&A advisor analyzing a deal. Please provide a comprehensive analysis and scoring.

Deal Information:
{json.dumps(deal_data, indent=2)}

Please analyze this deal and provide:

1. **Financial Score (0-100)**: Based on revenue, growth, profitability, and financial health
2. **Strategic Score (0-100)**: Based on market fit, synergies, and strategic value
3. **Risk Score (0-100)**: Based on identified risks (higher score = lower risk)
4. **Market Score (0-100)**: Based on market size, growth potential, and competitive position
5. **Team Score (0-100)**: Based on management quality and execution capability
6. **Overall Score (0-100)**: Weighted average of the above scores
7. **Recommendation**: One of: "proceed", "proceed_with_caution", "investigate_further", "decline", "negotiate_terms"
8. **Key Strengths**: List 3-5 major strengths
9. **Key Concerns**: List 3-5 major concerns or risks
10. **Next Actions**: List 3-5 recommended next steps

Respond in JSON format with these exact keys:
{{
  "financial_score": <number>,
  "strategic_score": <number>,
  "risk_score": <number>,
  "market_score": <number>,
  "team_score": <number>,
  "overall_score": <number>,
  "recommendation": "<string>",
  "key_strengths": ["<string>", ...],
  "key_concerns": ["<string>", ...],
  "next_actions": ["<string>", ...]
}}"""

        return [{"role": "user", "content": prompt}]

    def _build_document_analysis_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        """Build messages for document analysis"""
        content = request.input_data.get("content", "")
        doc_type = request.input_data.get("document_type", "unknown")

        prompt = f"""Analyze this {doc_type} document and extract key information:

Document Content:
{content[:3000]}...

Please provide:
1. **Document Type**: Identified document type
2. **Key Metrics**: Important financial or business metrics found
3. **Summary**: 2-3 sentence summary of the document
4. **Risk Factors**: Any risks or concerns mentioned
5. **Extracted Fields**: Structured data extracted from the document

Respond in JSON format:
{{
  "document_type": "<string>",
  "key_metrics": {{"<metric>": "<value>", ...}},
  "summary": "<string>",
  "risk_factors": ["<string>", ...],
  "extracted_fields": {{"<field>": "<value>", ...}}
}}"""

        return [{"role": "user", "content": prompt}]

    def _build_prediction_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        """Build messages for outcome predictions"""
        data = request.input_data

        prompt = f"""Analyze this data and predict likely outcomes:

Data:
{json.dumps(data, indent=2)}

Please provide predictions including:
1. **Success Probability**: Likelihood of successful completion (0.0-1.0)
2. **Timeline Estimate**: Expected completion timeframe
3. **Risk Factors**: Factors that could impact success
4. **Confidence Level**: Your confidence in these predictions (0.0-1.0)

Respond in JSON format:
{{
  "success_probability": <number>,
  "timeline_estimate": "<string>",
  "risk_factors": [
    {{"factor": "<string>", "impact": "<low|medium|high>"}}
  ],
  "confidence_level": <number>
}}"""

        return [{"role": "user", "content": prompt}]

    def _build_insights_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        """Build messages for generating insights"""
        data = request.input_data
        context = request.context.get("analysis_context", "general") if request.context else "general"

        prompt = f"""Generate actionable insights from this data in the context of {context}:

Data:
{json.dumps(data, indent=2)}

Please provide:
1. **Key Insights**: 3-5 important insights derived from the data
2. **Trends**: Any notable patterns or trends
3. **Recommendations**: Actionable recommendations based on the insights
4. **Opportunities**: Potential opportunities identified

Respond in JSON format:
{{
  "insights": [
    {{"type": "<trend|pattern|anomaly>", "description": "<string>", "impact": "<positive|negative|neutral>"}}
  ],
  "recommendations": ["<string>", ...],
  "opportunities": ["<string>", ...]
}}"""

        return [{"role": "user", "content": prompt}]

    def _build_recommendations_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        """Build messages for action recommendations"""
        data = request.input_data

        prompt = f"""Based on this information, provide specific action recommendations:

Data:
{json.dumps(data, indent=2)}

Please provide:
1. **Recommended Actions**: Specific, actionable steps
2. **Priority Actions**: Most important actions to take first
3. **Risk Mitigations**: Actions to reduce identified risks
4. **Timeline**: Suggested timeframe for each action

Respond in JSON format:
{{
  "recommended_actions": ["<string>", ...],
  "priority_actions": ["<string>", ...],
  "risk_mitigations": ["<string>", ...],
  "timeline_suggestions": {{"<action>": "<timeframe>", ...}}
}}"""

        return [{"role": "user", "content": prompt}]

    def _build_anomaly_detection_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        """Build messages for anomaly detection"""
        data = request.input_data

        prompt = f"""Analyze this data for anomalies, bottlenecks, or unusual patterns:

Data:
{json.dumps(data, indent=2)}

Please identify:
1. **Anomalies**: Unusual patterns or outliers
2. **Bottlenecks**: Process constraints or blockers
3. **Risk Level**: Overall risk assessment (0.0-1.0, where 1.0 is highest risk)
4. **Suggested Actions**: Specific steps to address issues

Respond in JSON format:
{{
  "anomalies": [
    {{"type": "<string>", "description": "<string>", "severity": "<low|medium|high>"}}
  ],
  "bottlenecks": [
    {{"stage": "<string>", "description": "<string>", "impact": "<string>"}}
  ],
  "risk_level": <number>,
  "suggested_actions": ["<string>", ...]
}}"""

        return [{"role": "user", "content": prompt}]

    def _build_generic_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        """Build generic messages for other tasks"""
        data = request.input_data

        prompt = f"""Analyze this data for the task: {request.task.value}

Data:
{json.dumps(data, indent=2)}

Please provide a comprehensive analysis and recommendations in JSON format."""

        return [{"role": "user", "content": prompt}]

    def _parse_claude_response(self, request: AIRequest, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Claude's response and extract the result"""
        try:
            content = response_data["content"][0]["text"]

            # Try to extract JSON from the response
            if content.startswith("{") and content.endswith("}"):
                return json.loads(content)

            # Look for JSON blocks in the response
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content)
            if json_match:
                return json.loads(json_match.group())

            # If no JSON found, return the raw content
            return {"analysis": content, "raw_response": True}

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # Fallback to structured response based on task type
            return self._create_fallback_response(request, response_data)

    def _create_fallback_response(self, request: AIRequest, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback response when JSON parsing fails"""
        content = response_data.get("content", [{}])[0].get("text", "")

        if request.task == AITask.SCORE_DEAL:
            return {
                "overall_score": 75,
                "financial_score": 75,
                "strategic_score": 75,
                "risk_score": 75,
                "market_score": 75,
                "team_score": 75,
                "recommendation": "investigate_further",
                "key_strengths": ["Requires detailed analysis"],
                "key_concerns": ["Unable to parse detailed response"],
                "analysis": content
            }
        else:
            return {
                "analysis": content,
                "requires_manual_review": True
            }

    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score based on result quality"""
        if result.get("raw_response") or result.get("requires_manual_review"):
            return 0.6  # Lower confidence for unparsed responses

        # Higher confidence for structured responses
        if isinstance(result, dict) and len(result) > 2:
            return 0.9

        return 0.8


def create_claude_processor(model: AIModel, supported_tasks: List[AITask]) -> AIProcessor:
    """Factory function to create Claude processor"""
    try:
        return ClaudeAIProcessor(model, supported_tasks)
    except ValueError:
        # Fall back to mock processor if Claude API key not available
        from .ai_service import MockAIProcessor
        return MockAIProcessor(model, supported_tasks)