"""
Document Intelligence Service
AI-powered document analysis, summarization, and data extraction
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
import re
import json
from .ai_service import AIService, AIRequest, AIResponse, AITask, AIModel, get_ai_service

class DocumentType(str, Enum):
    """Types of documents that can be analyzed"""
    FINANCIAL_STATEMENT = "financial_statement"
    BUSINESS_PLAN = "business_plan"
    DUE_DILIGENCE_REPORT = "due_diligence_report"
    LEGAL_DOCUMENT = "legal_document"
    MARKET_RESEARCH = "market_research"
    VALUATION_REPORT = "valuation_report"
    TERM_SHEET = "term_sheet"
    LOI = "letter_of_intent"
    NDA = "non_disclosure_agreement"
    PRESENTATION = "presentation"
    EMAIL = "email"
    CONTRACT = "contract"
    UNKNOWN = "unknown"

class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DocumentAnalysis:
    """Complete document analysis result"""
    document_id: str
    document_type: DocumentType
    content_summary: str
    key_metrics: Dict[str, Any]
    risk_factors: List[Dict[str, Any]]
    extracted_entities: Dict[str, List[str]]
    sentiment_score: float  # -1.0 to 1.0
    confidence_score: float  # 0.0 to 1.0
    processing_time_ms: int
    timestamp: datetime
    metadata: Dict[str, Any]
    
@dataclass
class ContentSummary:
    """Document content summary"""
    executive_summary: str
    key_points: List[str]
    action_items: List[str]
    important_dates: List[Dict[str, Any]]
    financial_highlights: List[str]
    risks_identified: List[str]
    word_count: int
    reading_time_minutes: int
    
@dataclass
class DataExtraction:
    """Extracted structured data from document"""
    entities: Dict[str, List[str]]  # person, organization, location, etc.
    financial_data: Dict[str, Any]  # revenue, costs, valuations, etc.
    dates: List[Dict[str, Any]]  # important dates and deadlines
    contacts: List[Dict[str, Any]]  # people and contact information
    metrics: Dict[str, float]  # quantitative metrics
    confidence_scores: Dict[str, float]  # confidence for each extraction
    
class DocumentIntelligenceService:
    """AI-powered document intelligence service"""
    
    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or get_ai_service()
        self.document_type_patterns = self._initialize_document_patterns()
        
    def _initialize_document_patterns(self) -> Dict[DocumentType, List[str]]:
        """Initialize patterns for document type detection"""
        return {
            DocumentType.FINANCIAL_STATEMENT: [
                r'balance\s+sheet', r'income\s+statement', r'cash\s+flow',
                r'revenue', r'ebitda', r'profit\s+and\s+loss', r'p&l'
            ],
            DocumentType.BUSINESS_PLAN: [
                r'business\s+plan', r'executive\s+summary', r'market\s+analysis',
                r'competitive\s+landscape', r'go-to-market', r'business\s+model'
            ],
            DocumentType.DUE_DILIGENCE_REPORT: [
                r'due\s+diligence', r'dd\s+report', r'management\s+interview',
                r'financial\s+review', r'operational\s+assessment'
            ],
            DocumentType.LEGAL_DOCUMENT: [
                r'agreement', r'contract', r'terms\s+and\s+conditions',
                r'whereas', r'hereby', r'party\s+of\s+the\s+first\s+part'
            ],
            DocumentType.VALUATION_REPORT: [
                r'valuation', r'dcf', r'discounted\s+cash\s+flow',
                r'comparable\s+company', r'trading\s+multiples', r'enterprise\s+value'
            ],
            DocumentType.TERM_SHEET: [
                r'term\s+sheet', r'investment\s+terms', r'pre-money\s+valuation',
                r'post-money\s+valuation', r'liquidation\s+preference'
            ],
            DocumentType.LOI: [
                r'letter\s+of\s+intent', r'loi', r'non-binding',
                r'intent\s+to\s+purchase', r'preliminary\s+agreement'
            ],
            DocumentType.NDA: [
                r'non-disclosure', r'nda', r'confidentiality\s+agreement',
                r'confidential\s+information', r'proprietary\s+information'
            ]
        }
    
    async def analyze_document(self, content: str, document_id: str,
                              hint_type: Optional[DocumentType] = None,
                              user_id: Optional[str] = None,
                              organization_id: Optional[str] = None) -> DocumentAnalysis:
        """Perform comprehensive document analysis"""
        start_time = datetime.now()
        
        # Detect document type
        detected_type = hint_type or self._detect_document_type(content)
        
        # Perform AI analysis
        ai_request = AIRequest(
            task=AITask.ANALYZE_DOCUMENT,
            model=AIModel.DOCUMENT_ANALYZER,
            input_data={
                "content": content,
                "document_type": detected_type.value,
                "document_id": document_id
            },
            context={
                "analysis_depth": "comprehensive",
                "include_risk_assessment": True,
                "include_entity_extraction": True
            },
            user_id=user_id,
            organization_id=organization_id
        )
        
        ai_response = await self.ai_service.process_request(ai_request)
        
        # Extract entities using pattern matching
        entities = self._extract_entities(content)
        
        # Calculate sentiment
        sentiment_score = self._calculate_sentiment(content)
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return DocumentAnalysis(
            document_id=document_id,
            document_type=detected_type,
            content_summary=ai_response.result.get("summary", ""),
            key_metrics=ai_response.result.get("key_metrics", {}),
            risk_factors=self._format_risk_factors(ai_response.result.get("risk_factors", [])),
            extracted_entities=entities,
            sentiment_score=sentiment_score,
            confidence_score=ai_response.confidence,
            processing_time_ms=processing_time,
            timestamp=datetime.now(),
            metadata={
                "ai_model": ai_response.model.value,
                "ai_processing_time_ms": ai_response.processing_time_ms,
                "document_length": len(content),
                "word_count": len(content.split())
            }
        )
    
    async def summarize_document(self, content: str, max_length: int = 500,
                                user_id: Optional[str] = None,
                                organization_id: Optional[str] = None) -> ContentSummary:
        """Generate a comprehensive summary of document content"""
        # Use AI to generate summary
        ai_request = AIRequest(
            task=AITask.SUMMARIZE_CONTENT,
            model=AIModel.CONTENT_SUMMARIZER,
            input_data={
                "content": content,
                "max_length": max_length,
                "include_key_points": True,
                "include_action_items": True
            },
            user_id=user_id,
            organization_id=organization_id
        )
        
        ai_response = await self.ai_service.process_request(ai_request)
        result = ai_response.result
        
        # Extract additional information
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)  # Assume 200 words per minute
        
        return ContentSummary(
            executive_summary=result.get("executive_summary", ""),
            key_points=result.get("key_points", []),
            action_items=self._extract_action_items(content),
            important_dates=self._extract_dates(content),
            financial_highlights=self._extract_financial_highlights(content),
            risks_identified=self._extract_risks(content),
            word_count=word_count,
            reading_time_minutes=reading_time
        )
    
    async def extract_structured_data(self, content: str,
                                     user_id: Optional[str] = None,
                                     organization_id: Optional[str] = None) -> DataExtraction:
        """Extract structured data from document"""
        # Use AI for data extraction
        ai_request = AIRequest(
            task=AITask.EXTRACT_DATA,
            model=AIModel.DOCUMENT_ANALYZER,
            input_data={
                "content": content,
                "extraction_types": ["entities", "financial_data", "dates", "contacts"]
            },
            user_id=user_id,
            organization_id=organization_id
        )
        
        ai_response = await self.ai_service.process_request(ai_request)
        ai_result = ai_response.result.get("extracted_fields", {})
        
        # Enhanced extraction using pattern matching
        entities = self._extract_entities(content)
        financial_data = self._extract_financial_data(content)
        dates = self._extract_dates(content)
        contacts = self._extract_contacts(content)
        metrics = self._extract_metrics(content)
        
        # Combine AI and pattern-based results
        combined_entities = {**entities, **ai_result.get("entities", {})}
        combined_financial = {**financial_data, **ai_result.get("financial_data", {})}
        
        return DataExtraction(
            entities=combined_entities,
            financial_data=combined_financial,
            dates=dates,
            contacts=contacts,
            metrics=metrics,
            confidence_scores=ai_response.result.get("confidence_scores", {})
        )
    
    def _detect_document_type(self, content: str) -> DocumentType:
        """Detect document type using pattern matching"""
        content_lower = content.lower()
        scores = {}
        
        for doc_type, patterns in self.document_type_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content_lower))
                score += matches
            scores[doc_type] = score
        
        if scores:
            best_match = max(scores, key=scores.get)
            if scores[best_match] > 0:
                return best_match
        
        return DocumentType.UNKNOWN
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract entities using pattern matching"""
        entities = {
            "companies": [],
            "people": [],
            "locations": [],
            "currencies": [],
            "percentages": []
        }
        
        # Company patterns (simplified)
        company_patterns = [
            r'([A-Z][a-zA-Z\s]+(?:Inc|LLC|Corp|Ltd|Company|Co))',
            r'([A-Z][a-zA-Z\s]+(?:Corporation|Incorporated|Limited))'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, content)
            entities["companies"].extend([match.strip() for match in matches])
        
        # Currency amounts
        currency_pattern = r'\$[\d,]+(?:\.\d{2})?[MBK]?'
        entities["currencies"] = re.findall(currency_pattern, content)
        
        # Percentages
        percentage_pattern = r'\d+(?:\.\d+)?%'
        entities["percentages"] = re.findall(percentage_pattern, content)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def _extract_financial_data(self, content: str) -> Dict[str, Any]:
        """Extract financial data using pattern matching"""
        financial_data = {}
        
        # Revenue patterns
        revenue_patterns = [
            r'revenue[:\s]+\$([\d,]+(?:\.\d+)?[MBK]?)',
            r'sales[:\s]+\$([\d,]+(?:\.\d+)?[MBK]?)'
        ]
        
        for pattern in revenue_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                financial_data["revenue"] = match.group(1)
                break
        
        # EBITDA patterns
        ebitda_pattern = r'ebitda[:\s]+\$([\d,]+(?:\.\d+)?[MBK]?)'
        match = re.search(ebitda_pattern, content, re.IGNORECASE)
        if match:
            financial_data["ebitda"] = match.group(1)
        
        # Valuation patterns
        valuation_patterns = [
            r'valuation[:\s]+\$([\d,]+(?:\.\d+)?[MBK]?)',
            r'enterprise\s+value[:\s]+\$([\d,]+(?:\.\d+)?[MBK]?)'
        ]
        
        for pattern in valuation_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                financial_data["valuation"] = match.group(1)
                break
        
        return financial_data
    
    def _extract_dates(self, content: str) -> List[Dict[str, Any]]:
        """Extract important dates from content"""
        dates = []
        
        # Date patterns
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'([A-Za-z]+\s+\d{1,2},?\s+\d{4})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                dates.append({
                    "date": match,
                    "context": "extracted",
                    "type": "general"
                })
        
        return dates[:10]  # Limit to first 10 dates
    
    def _extract_contacts(self, content: str) -> List[Dict[str, Any]]:
        """Extract contact information"""
        contacts = []
        
        # Email pattern
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        emails = re.findall(email_pattern, content)
        
        for email in emails:
            contacts.append({
                "type": "email",
                "value": email,
                "context": "document"
            })
        
        # Phone pattern (simplified)
        phone_pattern = r'(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})'
        phones = re.findall(phone_pattern, content)
        
        for phone in phones:
            contacts.append({
                "type": "phone",
                "value": phone,
                "context": "document"
            })
        
        return contacts
    
    def _extract_metrics(self, content: str) -> Dict[str, float]:
        """Extract quantitative metrics"""
        metrics = {}
        
        # Growth rate
        growth_pattern = r'growth[:\s]+([\d.]+)%'
        match = re.search(growth_pattern, content, re.IGNORECASE)
        if match:
            metrics["growth_rate"] = float(match.group(1))
        
        # Margin
        margin_pattern = r'margin[:\s]+([\d.]+)%'
        match = re.search(margin_pattern, content, re.IGNORECASE)
        if match:
            metrics["margin"] = float(match.group(1))
        
        return metrics
    
    def _extract_action_items(self, content: str) -> List[str]:
        """Extract action items from content"""
        action_patterns = [
            r'action\s+item[:\s]+([^\n.]+)',
            r'todo[:\s]+([^\n.]+)',
            r'next\s+steps?[:\s]+([^\n.]+)'
        ]
        
        action_items = []
        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            action_items.extend(matches)
        
        return action_items[:5]  # Limit to 5 items
    
    def _extract_financial_highlights(self, content: str) -> List[str]:
        """Extract financial highlights"""
        highlights = []
        
        # Look for financial statements
        financial_keywords = ['revenue', 'profit', 'ebitda', 'growth', 'margin', 'valuation']
        sentences = content.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in financial_keywords):
                if len(sentence.strip()) > 10:  # Avoid short fragments
                    highlights.append(sentence.strip())
        
        return highlights[:3]  # Top 3 highlights
    
    def _extract_risks(self, content: str) -> List[str]:
        """Extract risk-related content"""
        risk_keywords = ['risk', 'concern', 'challenge', 'threat', 'issue', 'problem']
        risks = []
        sentences = content.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in risk_keywords):
                if len(sentence.strip()) > 10:
                    risks.append(sentence.strip())
        
        return risks[:3]  # Top 3 risks
    
    def _calculate_sentiment(self, content: str) -> float:
        """Calculate sentiment score using simple pattern matching"""
        positive_words = ['excellent', 'strong', 'good', 'positive', 'growth', 'success', 'opportunity']
        negative_words = ['poor', 'weak', 'bad', 'negative', 'decline', 'risk', 'concern', 'challenge']
        
        words = content.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0
        
        return (positive_count - negative_count) / total_sentiment_words
    
    def _format_risk_factors(self, risk_factors: List[str]) -> List[Dict[str, Any]]:
        """Format risk factors with metadata"""
        formatted_risks = []
        
        for risk in risk_factors:
            # Simple risk level assessment
            risk_level = RiskLevel.MEDIUM
            if any(word in risk.lower() for word in ['critical', 'severe', 'major']):
                risk_level = RiskLevel.HIGH
            elif any(word in risk.lower() for word in ['minor', 'low', 'small']):
                risk_level = RiskLevel.LOW
            
            formatted_risks.append({
                "description": risk,
                "level": risk_level.value,
                "category": "general",
                "impact": "medium"
            })
        
        return formatted_risks
    
    def get_supported_document_types(self) -> List[str]:
        """Get list of supported document types"""
        return [doc_type.value for doc_type in DocumentType]
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "supported_document_types": len(DocumentType),
            "ai_service_stats": self.ai_service.get_processing_stats(),
            "service_status": "active"
        }

# Global document intelligence service
_document_intelligence_service: Optional[DocumentIntelligenceService] = None

def get_document_intelligence_service() -> DocumentIntelligenceService:
    """Get global document intelligence service instance"""
    global _document_intelligence_service
    if _document_intelligence_service is None:
        _document_intelligence_service = DocumentIntelligenceService()
    return _document_intelligence_service