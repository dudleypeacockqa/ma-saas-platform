"""
NLP Hub - Sprint 12
Natural Language Processing capabilities for document analysis and contract intelligence
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import re
from abc import ABC, abstractmethod

class DocumentType(Enum):
    CONTRACT = "contract"
    FINANCIAL_STATEMENT = "financial_statement"
    DUE_DILIGENCE_REPORT = "due_diligence_report"
    LEGAL_DOCUMENT = "legal_document"
    PRESENTATION = "presentation"
    CORRESPONDENCE = "correspondence"
    REGULATORY_FILING = "regulatory_filing"
    TECHNICAL_DOCUMENT = "technical_document"

class LanguageCode(Enum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    CHINESE = "zh"
    JAPANESE = "ja"

class SentimentType(Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class ContractClauseType(Enum):
    TERMINATION = "termination"
    LIABILITY = "liability"
    INDEMNIFICATION = "indemnification"
    CONFIDENTIALITY = "confidentiality"
    NON_COMPETE = "non_compete"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    PAYMENT_TERMS = "payment_terms"
    FORCE_MAJEURE = "force_majeure"
    GOVERNING_LAW = "governing_law"
    DISPUTE_RESOLUTION = "dispute_resolution"

class RiskLevel(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class TextAnalysisResult:
    """Result of text analysis operations"""
    text_id: str
    language: LanguageCode
    word_count: int
    sentence_count: int
    paragraph_count: int
    reading_level: str
    key_topics: List[str]
    confidence_score: float
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SentimentAnalysis:
    """Sentiment analysis results"""
    overall_sentiment: SentimentType
    sentiment_score: float  # -1.0 to 1.0
    confidence: float
    positive_indicators: List[str]
    negative_indicators: List[str]
    neutral_sections: List[str]
    emotion_breakdown: Dict[str, float]
    risk_flags: List[str]

@dataclass
class ContractClause:
    """Individual contract clause analysis"""
    clause_type: ContractClauseType
    text_content: str
    risk_level: RiskLevel
    risk_score: float
    key_terms: List[str]
    recommendations: List[str]
    precedent_references: List[str]
    compliance_notes: List[str]

@dataclass
class ContractAnalysis:
    """Comprehensive contract analysis results"""
    contract_id: str
    document_type: DocumentType
    total_clauses: int
    analyzed_clauses: List[ContractClause]
    overall_risk_score: float
    compliance_status: str
    red_flags: List[str]
    recommendations: List[str]
    missing_clauses: List[ContractClauseType]
    unusual_terms: List[str]
    market_standard_comparison: Dict[str, str]

@dataclass
class EntityExtraction:
    """Named entity recognition results"""
    companies: List[Dict[str, Any]]
    people: List[Dict[str, Any]]
    dates: List[Dict[str, Any]]
    monetary_amounts: List[Dict[str, Any]]
    locations: List[Dict[str, Any]]
    legal_entities: List[Dict[str, Any]]
    technical_terms: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]

@dataclass
class DocumentSummary:
    """AI-generated document summary"""
    executive_summary: str
    key_points: List[str]
    action_items: List[str]
    deadlines: List[Dict[str, Any]]
    stakeholders: List[str]
    risks_identified: List[str]
    opportunities: List[str]
    next_steps: List[str]

class NLPProcessor(ABC):
    """Abstract base class for NLP processors"""

    @abstractmethod
    def process_text(self, text: str, language: LanguageCode) -> TextAnalysisResult:
        pass

    @abstractmethod
    def extract_entities(self, text: str) -> EntityExtraction:
        pass

class DocumentAnalyzer:
    """Advanced document analysis with NLP capabilities"""

    def __init__(self):
        self.supported_languages = list(LanguageCode)
        self.document_cache = {}
        self.analysis_history = []

    def analyze_document(self, document_content: str, document_type: DocumentType,
                        language: LanguageCode = LanguageCode.ENGLISH) -> TextAnalysisResult:
        """Perform comprehensive document analysis"""

        # Simulate NLP processing
        word_count = len(document_content.split())
        sentence_count = document_content.count('.') + document_content.count('!') + document_content.count('?')
        paragraph_count = document_content.count('\n\n') + 1

        # Extract key topics using keyword analysis
        key_topics = self._extract_key_topics(document_content, document_type)

        # Determine reading level
        reading_level = self._calculate_reading_level(word_count, sentence_count)

        result = TextAnalysisResult(
            text_id=f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            language=language,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            reading_level=reading_level,
            key_topics=key_topics,
            confidence_score=0.92,
            processing_time=1.2
        )

        self.analysis_history.append(result)
        return result

    def extract_entities(self, document_content: str) -> EntityExtraction:
        """Extract named entities from document"""

        # Simulate entity extraction
        companies = [
            {"name": "Acme Corp", "confidence": 0.95, "context": "acquisition target"},
            {"name": "Global Industries", "confidence": 0.89, "context": "strategic partner"}
        ]

        people = [
            {"name": "John Smith", "role": "CEO", "confidence": 0.92},
            {"name": "Sarah Johnson", "role": "CFO", "confidence": 0.88}
        ]

        dates = [
            {"date": "2024-03-15", "context": "closing date", "confidence": 0.94},
            {"date": "2024-02-01", "context": "due diligence start", "confidence": 0.87}
        ]

        monetary_amounts = [
            {"amount": 150000000, "currency": "USD", "context": "purchase price", "confidence": 0.96},
            {"amount": 5000000, "currency": "USD", "context": "escrow amount", "confidence": 0.91}
        ]

        locations = [
            {"location": "New York", "type": "city", "confidence": 0.93},
            {"location": "Delaware", "type": "state", "confidence": 0.89}
        ]

        return EntityExtraction(
            companies=companies,
            people=people,
            dates=dates,
            monetary_amounts=monetary_amounts,
            locations=locations,
            legal_entities=[],
            technical_terms=[],
            confidence_scores={
                "overall": 0.91,
                "companies": 0.92,
                "people": 0.90,
                "dates": 0.91,
                "amounts": 0.94
            }
        )

    def generate_summary(self, document_content: str, document_type: DocumentType) -> DocumentSummary:
        """Generate AI-powered document summary"""

        # Simulate AI summarization
        if document_type == DocumentType.CONTRACT:
            return DocumentSummary(
                executive_summary="Strategic acquisition agreement for technology assets with standard terms and competitive valuation.",
                key_points=[
                    "Purchase price of $150M with standard escrow provisions",
                    "90-day due diligence period with material adverse change provisions",
                    "Key management retention through earnout structure",
                    "Comprehensive IP transfer with standard warranties"
                ],
                action_items=[
                    "Complete financial due diligence by March 1st",
                    "Obtain regulatory approvals in target jurisdictions",
                    "Finalize management retention agreements",
                    "Execute definitive purchase agreement"
                ],
                deadlines=[
                    {"task": "Due diligence completion", "date": "2024-03-01", "priority": "high"},
                    {"task": "Regulatory filing", "date": "2024-02-15", "priority": "medium"}
                ],
                stakeholders=["Acquiring company board", "Target company management", "Regulatory bodies", "Investment banks"],
                risks_identified=[
                    "Regulatory approval timeline uncertainty",
                    "Key customer concentration risk",
                    "Technology integration complexity"
                ],
                opportunities=[
                    "Market expansion through target's customer base",
                    "Cost synergies in overlapping operations",
                    "Technology enhancement capabilities"
                ],
                next_steps=[
                    "Initiate regulatory approval process",
                    "Begin integration planning",
                    "Secure financing commitments"
                ]
            )

        return DocumentSummary(
            executive_summary="Document analysis completed with key insights extracted.",
            key_points=["Key business terms identified", "Standard industry practices observed"],
            action_items=["Review and validate findings", "Distribute to stakeholders"],
            deadlines=[],
            stakeholders=["Document reviewers", "Legal team"],
            risks_identified=["Minor compliance considerations"],
            opportunities=["Process optimization potential"],
            next_steps=["Proceed with standard review process"]
        )

    def _extract_key_topics(self, content: str, doc_type: DocumentType) -> List[str]:
        """Extract key topics based on document type"""
        topics = []
        content_lower = content.lower()

        # M&A specific terms
        ma_terms = {
            "acquisition": ["acquisition", "acquire", "purchase", "buy"],
            "due_diligence": ["due diligence", "dd", "investigation"],
            "valuation": ["valuation", "price", "value", "worth"],
            "synergies": ["synergy", "synergies", "cost savings"],
            "integration": ["integration", "merge", "combine"],
            "regulatory": ["regulatory", "approval", "antitrust"],
            "financing": ["financing", "funding", "capital"]
        }

        for topic, keywords in ma_terms.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)

        return topics[:10]  # Return top 10 topics

    def _calculate_reading_level(self, word_count: int, sentence_count: int) -> str:
        """Calculate reading level using simplified formula"""
        if sentence_count == 0:
            return "unknown"

        avg_words_per_sentence = word_count / sentence_count

        if avg_words_per_sentence < 10:
            return "elementary"
        elif avg_words_per_sentence < 15:
            return "middle_school"
        elif avg_words_per_sentence < 20:
            return "high_school"
        elif avg_words_per_sentence < 25:
            return "college"
        else:
            return "graduate"

class ContractIntelligence:
    """Advanced contract analysis and intelligence"""

    def __init__(self):
        self.clause_patterns = self._initialize_clause_patterns()
        self.risk_indicators = self._initialize_risk_indicators()
        self.market_standards = self._load_market_standards()

    def analyze_contract(self, contract_content: str, contract_type: str = "general") -> ContractAnalysis:
        """Perform comprehensive contract analysis"""

        # Extract and analyze clauses
        clauses = self._extract_clauses(contract_content)
        analyzed_clauses = [self._analyze_clause(clause) for clause in clauses]

        # Calculate overall risk
        overall_risk = self._calculate_overall_risk(analyzed_clauses)

        # Identify red flags
        red_flags = self._identify_red_flags(contract_content, analyzed_clauses)

        # Generate recommendations
        recommendations = self._generate_recommendations(analyzed_clauses, overall_risk)

        # Check for missing standard clauses
        missing_clauses = self._check_missing_clauses(analyzed_clauses, contract_type)

        return ContractAnalysis(
            contract_id=f"contract_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            document_type=DocumentType.CONTRACT,
            total_clauses=len(clauses),
            analyzed_clauses=analyzed_clauses,
            overall_risk_score=overall_risk,
            compliance_status="compliant" if overall_risk < 0.7 else "review_required",
            red_flags=red_flags,
            recommendations=recommendations,
            missing_clauses=missing_clauses,
            unusual_terms=self._identify_unusual_terms(contract_content),
            market_standard_comparison=self._compare_to_market_standards(analyzed_clauses)
        )

    def _extract_clauses(self, content: str) -> List[str]:
        """Extract individual clauses from contract"""
        # Simulate clause extraction
        clauses = [
            "The purchase price shall be $150,000,000 payable at closing.",
            "Seller represents and warrants that all financial statements are accurate.",
            "This agreement shall terminate on March 15, 2024 unless extended.",
            "Buyer shall indemnify seller against all claims arising from the business.",
            "All disputes shall be resolved through binding arbitration in Delaware."
        ]
        return clauses

    def _analyze_clause(self, clause_text: str) -> ContractClause:
        """Analyze individual contract clause"""
        # Determine clause type
        clause_type = self._classify_clause(clause_text)

        # Assess risk level
        risk_level, risk_score = self._assess_clause_risk(clause_text, clause_type)

        # Extract key terms
        key_terms = self._extract_key_terms(clause_text)

        # Generate recommendations
        recommendations = self._generate_clause_recommendations(clause_type, risk_level)

        return ContractClause(
            clause_type=clause_type,
            text_content=clause_text,
            risk_level=risk_level,
            risk_score=risk_score,
            key_terms=key_terms,
            recommendations=recommendations,
            precedent_references=[],
            compliance_notes=[]
        )

    def _classify_clause(self, clause_text: str) -> ContractClauseType:
        """Classify clause type based on content"""
        text_lower = clause_text.lower()

        if any(term in text_lower for term in ["terminate", "termination", "expire"]):
            return ContractClauseType.TERMINATION
        elif any(term in text_lower for term in ["liable", "liability", "damages"]):
            return ContractClauseType.LIABILITY
        elif any(term in text_lower for term in ["indemnify", "indemnification", "hold harmless"]):
            return ContractClauseType.INDEMNIFICATION
        elif any(term in text_lower for term in ["confidential", "non-disclosure", "proprietary"]):
            return ContractClauseType.CONFIDENTIALITY
        elif any(term in text_lower for term in ["payment", "price", "compensation"]):
            return ContractClauseType.PAYMENT_TERMS
        else:
            return ContractClauseType.PAYMENT_TERMS  # Default

    def _assess_clause_risk(self, clause_text: str, clause_type: ContractClauseType) -> Tuple[RiskLevel, float]:
        """Assess risk level of a clause"""
        # Simulate risk assessment
        risk_indicators = ["unlimited", "perpetual", "broadly", "solely", "exclusively"]
        risk_count = sum(1 for indicator in risk_indicators if indicator in clause_text.lower())

        if risk_count >= 3:
            return RiskLevel.CRITICAL, 0.9
        elif risk_count == 2:
            return RiskLevel.HIGH, 0.75
        elif risk_count == 1:
            return RiskLevel.MEDIUM, 0.5
        else:
            return RiskLevel.LOW, 0.25

    def _extract_key_terms(self, clause_text: str) -> List[str]:
        """Extract key terms from clause"""
        # Simulate key term extraction
        amounts = re.findall(r'\$[\d,]+', clause_text)
        dates = re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b|\b\w+ \d{1,2}, \d{4}\b', clause_text)

        key_terms = amounts + dates
        return key_terms[:5]  # Return top 5 key terms

    def _generate_clause_recommendations(self, clause_type: ContractClauseType, risk_level: RiskLevel) -> List[str]:
        """Generate recommendations for specific clause"""
        if risk_level == RiskLevel.CRITICAL:
            return ["Immediate legal review required", "Consider alternative language", "Negotiate risk mitigation"]
        elif risk_level == RiskLevel.HIGH:
            return ["Legal review recommended", "Consider risk allocation", "Review industry standards"]
        else:
            return ["Standard clause review", "Verify compliance requirements"]

    def _calculate_overall_risk(self, clauses: List[ContractClause]) -> float:
        """Calculate overall contract risk score"""
        if not clauses:
            return 0.0

        total_risk = sum(clause.risk_score for clause in clauses)
        return total_risk / len(clauses)

    def _identify_red_flags(self, content: str, clauses: List[ContractClause]) -> List[str]:
        """Identify contract red flags"""
        red_flags = []

        # Check for high-risk clauses
        high_risk_clauses = [c for c in clauses if c.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        if high_risk_clauses:
            red_flags.append(f"Found {len(high_risk_clauses)} high-risk clauses requiring review")

        # Check for unusual terms
        if "unlimited liability" in content.lower():
            red_flags.append("Unlimited liability clause detected")

        if "non-compete" in content.lower() and "perpetual" in content.lower():
            red_flags.append("Perpetual non-compete clause may be unenforceable")

        return red_flags

    def _generate_recommendations(self, clauses: List[ContractClause], overall_risk: float) -> List[str]:
        """Generate overall contract recommendations"""
        recommendations = []

        if overall_risk > 0.7:
            recommendations.append("Comprehensive legal review recommended before execution")

        if overall_risk > 0.5:
            recommendations.append("Consider risk mitigation strategies")

        recommendations.append("Verify all monetary amounts and dates")
        recommendations.append("Confirm compliance with applicable regulations")

        return recommendations

    def _check_missing_clauses(self, clauses: List[ContractClause], contract_type: str) -> List[ContractClauseType]:
        """Check for missing standard clauses"""
        present_types = {clause.clause_type for clause in clauses}

        # Standard clauses for M&A contracts
        standard_clauses = {
            ContractClauseType.TERMINATION,
            ContractClauseType.LIABILITY,
            ContractClauseType.INDEMNIFICATION,
            ContractClauseType.GOVERNING_LAW,
            ContractClauseType.DISPUTE_RESOLUTION
        }

        return list(standard_clauses - present_types)

    def _identify_unusual_terms(self, content: str) -> List[str]:
        """Identify unusual or non-standard terms"""
        # Simulate unusual term detection
        return ["Accelerated vesting provisions", "Reverse breakup fee structure"]

    def _compare_to_market_standards(self, clauses: List[ContractClause]) -> Dict[str, str]:
        """Compare clauses to market standards"""
        return {
            "overall_assessment": "Generally aligned with market standards",
            "payment_terms": "Standard 30-day payment terms",
            "liability_caps": "Market-standard liability limitations",
            "termination_rights": "Balanced termination provisions"
        }

    def _initialize_clause_patterns(self) -> Dict:
        """Initialize clause recognition patterns"""
        return {}

    def _initialize_risk_indicators(self) -> List[str]:
        """Initialize risk indicator terms"""
        return ["unlimited", "perpetual", "broadly", "solely", "irrevocable"]

    def _load_market_standards(self) -> Dict:
        """Load market standard comparisons"""
        return {}

class SentimentAnalyzer:
    """Advanced sentiment analysis for documents and communications"""

    def __init__(self):
        self.emotion_lexicon = self._load_emotion_lexicon()
        self.risk_indicators = self._load_risk_indicators()

    def analyze_sentiment(self, text: str, context: str = "general") -> SentimentAnalysis:
        """Perform comprehensive sentiment analysis"""

        # Calculate overall sentiment
        sentiment_score = self._calculate_sentiment_score(text)
        sentiment_type = self._classify_sentiment(sentiment_score)

        # Extract indicators
        positive_indicators = self._extract_positive_indicators(text)
        negative_indicators = self._extract_negative_indicators(text)
        neutral_sections = self._identify_neutral_sections(text)

        # Analyze emotions
        emotion_breakdown = self._analyze_emotions(text)

        # Identify risk flags
        risk_flags = self._identify_sentiment_risks(text, sentiment_score)

        return SentimentAnalysis(
            overall_sentiment=sentiment_type,
            sentiment_score=sentiment_score,
            confidence=0.88,
            positive_indicators=positive_indicators,
            negative_indicators=negative_indicators,
            neutral_sections=neutral_sections,
            emotion_breakdown=emotion_breakdown,
            risk_flags=risk_flags
        )

    def _calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score from -1.0 to 1.0"""
        # Simulate sentiment calculation
        positive_words = ["good", "excellent", "positive", "successful", "beneficial", "strong"]
        negative_words = ["bad", "poor", "negative", "failed", "problematic", "weak"]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        total_words = len(text.split())
        if total_words == 0:
            return 0.0

        score = (positive_count - negative_count) / max(total_words, 1)
        return max(-1.0, min(1.0, score * 10))  # Scale and clamp

    def _classify_sentiment(self, score: float) -> SentimentType:
        """Classify sentiment based on score"""
        if score >= 0.6:
            return SentimentType.VERY_POSITIVE
        elif score >= 0.2:
            return SentimentType.POSITIVE
        elif score >= -0.2:
            return SentimentType.NEUTRAL
        elif score >= -0.6:
            return SentimentType.NEGATIVE
        else:
            return SentimentType.VERY_NEGATIVE

    def _extract_positive_indicators(self, text: str) -> List[str]:
        """Extract positive sentiment indicators"""
        indicators = []
        positive_phrases = [
            "strong performance", "excellent results", "positive outlook",
            "successful completion", "beneficial outcome", "significant growth"
        ]

        text_lower = text.lower()
        for phrase in positive_phrases:
            if phrase in text_lower:
                indicators.append(phrase)

        return indicators

    def _extract_negative_indicators(self, text: str) -> List[str]:
        """Extract negative sentiment indicators"""
        indicators = []
        negative_phrases = [
            "significant concerns", "potential issues", "substantial risks",
            "poor performance", "negative impact", "major problems"
        ]

        text_lower = text.lower()
        for phrase in negative_phrases:
            if phrase in text_lower:
                indicators.append(phrase)

        return indicators

    def _identify_neutral_sections(self, text: str) -> List[str]:
        """Identify neutral sections of text"""
        # Simulate neutral section identification
        return ["Background information", "Standard procedures", "Factual statements"]

    def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotional content breakdown"""
        # Simulate emotion analysis
        return {
            "confidence": 0.35,
            "optimism": 0.28,
            "concern": 0.15,
            "excitement": 0.12,
            "uncertainty": 0.10
        }

    def _identify_sentiment_risks(self, text: str, sentiment_score: float) -> List[str]:
        """Identify sentiment-based risks"""
        risks = []

        if sentiment_score < -0.5:
            risks.append("Highly negative sentiment may indicate relationship issues")

        if "urgent" in text.lower() and sentiment_score < 0:
            risks.append("Urgent negative sentiment requires immediate attention")

        if "concerns" in text.lower():
            risks.append("Stakeholder concerns identified in communication")

        return risks

    def _load_emotion_lexicon(self) -> Dict:
        """Load emotion lexicon for analysis"""
        return {}

    def _load_risk_indicators(self) -> List[str]:
        """Load sentiment risk indicators"""
        return ["urgent", "crisis", "emergency", "critical", "severe"]

class NLPHub:
    """Central hub for all NLP operations"""

    def __init__(self):
        self.document_analyzer = DocumentAnalyzer()
        self.contract_intelligence = ContractIntelligence()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.processing_stats = {
            "documents_processed": 0,
            "contracts_analyzed": 0,
            "sentiment_analyses": 0,
            "total_processing_time": 0.0
        }

    def process_document(self, content: str, document_type: DocumentType,
                        analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Process document with comprehensive NLP analysis"""
        start_time = datetime.now()

        results = {}

        # Basic text analysis
        if analysis_type in ["comprehensive", "basic"]:
            results["text_analysis"] = self.document_analyzer.analyze_document(
                content, document_type
            )

        # Entity extraction
        if analysis_type in ["comprehensive", "entities"]:
            results["entities"] = self.document_analyzer.extract_entities(content)

        # Document summary
        if analysis_type in ["comprehensive", "summary"]:
            results["summary"] = self.document_analyzer.generate_summary(content, document_type)

        # Contract analysis (if applicable)
        if document_type == DocumentType.CONTRACT and analysis_type in ["comprehensive", "contract"]:
            results["contract_analysis"] = self.contract_intelligence.analyze_contract(content)

        # Sentiment analysis
        if analysis_type in ["comprehensive", "sentiment"]:
            results["sentiment"] = self.sentiment_analyzer.analyze_sentiment(content)

        # Update stats
        processing_time = (datetime.now() - start_time).total_seconds()
        self._update_processing_stats(document_type, processing_time)

        results["processing_metadata"] = {
            "analysis_type": analysis_type,
            "processing_time": processing_time,
            "timestamp": datetime.now(),
            "nlp_version": "1.0.0"
        }

        return results

    def batch_process_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple documents in batch"""
        results = []

        for doc in documents:
            content = doc.get("content", "")
            doc_type = DocumentType(doc.get("type", "contract"))
            analysis_type = doc.get("analysis_type", "comprehensive")

            result = self.process_document(content, doc_type, analysis_type)
            result["document_id"] = doc.get("id", f"doc_{len(results)}")
            results.append(result)

        return results

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get NLP processing statistics"""
        return {
            **self.processing_stats,
            "average_processing_time": (
                self.processing_stats["total_processing_time"] /
                max(self.processing_stats["documents_processed"], 1)
            ),
            "last_updated": datetime.now()
        }

    def _update_processing_stats(self, document_type: DocumentType, processing_time: float):
        """Update internal processing statistics"""
        self.processing_stats["documents_processed"] += 1
        self.processing_stats["total_processing_time"] += processing_time

        if document_type == DocumentType.CONTRACT:
            self.processing_stats["contracts_analyzed"] += 1

        # Sentiment analysis is included in comprehensive processing
        self.processing_stats["sentiment_analyses"] += 1

# Singleton instance
_nlp_hub_instance: Optional[NLPHub] = None

def get_nlp_hub() -> NLPHub:
    """Get the singleton NLP Hub instance"""
    global _nlp_hub_instance
    if _nlp_hub_instance is None:
        _nlp_hub_instance = NLPHub()
    return _nlp_hub_instance