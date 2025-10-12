"""
Due Diligence Automation Engine - AI-powered document analysis and data room management
Automates due diligence processes with intelligent document analysis and risk detection
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import uuid
import re
from abc import ABC, abstractmethod

# Data Models and Enums
class DocumentType(Enum):
    FINANCIAL_STATEMENT = "financial_statement"
    AUDIT_REPORT = "audit_report"
    TAX_RETURN = "tax_return"
    LEGAL_AGREEMENT = "legal_agreement"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    REGULATORY_FILING = "regulatory_filing"
    INSURANCE_POLICY = "insurance_policy"
    ENVIRONMENTAL_REPORT = "environmental_report"
    EMPLOYEE_RECORDS = "employee_records"
    CUSTOMER_CONTRACT = "customer_contract"
    SUPPLIER_AGREEMENT = "supplier_agreement"
    REAL_ESTATE_DOCUMENT = "real_estate_document"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AnalysisStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"

class DataRoomAccess(Enum):
    READ_ONLY = "read_only"
    UPLOAD = "upload"
    ADMIN = "admin"

class ReviewPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class DocumentMetadata:
    """Document metadata and classification"""
    document_id: str
    filename: str
    document_type: DocumentType
    file_size: int
    upload_date: datetime
    uploaded_by: str
    version: int = 1
    tags: List[str] = field(default_factory=list)
    security_classification: str = "confidential"
    retention_period_days: int = 2555  # 7 years default

@dataclass
class DocumentAnalysis:
    """AI-powered document analysis results"""
    analysis_id: str
    document_id: str
    analysis_type: str
    status: AnalysisStatus
    confidence_score: float
    key_findings: List[str]
    risk_flags: List[str]
    extracted_data: Dict[str, Any]
    anomalies_detected: List[str]
    compliance_issues: List[str]
    recommendations: List[str]
    analysis_date: datetime = field(default_factory=datetime.now)

@dataclass
class RiskFlag:
    """Risk flag identified during analysis"""
    flag_id: str
    document_id: str
    risk_type: str
    risk_level: RiskLevel
    description: str
    evidence: str
    mitigation_suggestions: List[str]
    requires_legal_review: bool = False
    flagged_date: datetime = field(default_factory=datetime.now)

@dataclass
class DataRoomUser:
    """Data room user and access management"""
    user_id: str
    name: str
    organization: str
    email: str
    access_level: DataRoomAccess
    permitted_folders: List[str]
    access_granted_date: datetime
    last_activity: Optional[datetime] = None
    download_log: List[str] = field(default_factory=list)

@dataclass
class QAItem:
    """Question and answer item for automated Q&A"""
    qa_id: str
    question: str
    category: str
    priority: ReviewPriority
    status: str
    answer: Optional[str] = None
    supporting_documents: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    created_date: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None

class DocumentAnalysisEngine:
    """Advanced AI-powered document analysis engine"""

    def __init__(self):
        self.analysis_models = {}
        self.document_index = {}
        self.risk_patterns = defaultdict(list)
        self.analysis_history = defaultdict(list)

    def initialize_analysis_models(self) -> bool:
        """Initialize AI models for document analysis"""
        try:
            # Initialize different analysis models
            self.analysis_models = {
                "financial_analyzer": {
                    "model_type": "financial_nlp",
                    "capabilities": ["revenue_recognition", "expense_analysis", "ratio_calculation"],
                    "accuracy": 0.92
                },
                "legal_analyzer": {
                    "model_type": "legal_nlp",
                    "capabilities": ["contract_terms", "liability_assessment", "compliance_check"],
                    "accuracy": 0.89
                },
                "risk_detector": {
                    "model_type": "anomaly_detection",
                    "capabilities": ["outlier_detection", "pattern_analysis", "fraud_indicators"],
                    "accuracy": 0.85
                },
                "compliance_checker": {
                    "model_type": "regulatory_compliance",
                    "capabilities": ["regulatory_mapping", "requirement_validation", "gap_analysis"],
                    "accuracy": 0.91
                }
            }

            # Initialize risk patterns
            self._initialize_risk_patterns()

            return True
        except Exception:
            return False

    def analyze_document(self, document_id: str, document_content: str,
                        document_type: DocumentType,
                        analysis_types: List[str]) -> DocumentAnalysis:
        """Perform comprehensive AI analysis on document"""

        analysis_id = f"analysis_{document_id}_{int(datetime.now().timestamp())}"

        # Extract basic document information
        basic_info = self._extract_basic_information(document_content, document_type)

        # Perform specific analyses
        key_findings = []
        risk_flags = []
        extracted_data = {}
        anomalies = []
        compliance_issues = []
        recommendations = []

        for analysis_type in analysis_types:
            if analysis_type == "financial_analysis":
                financial_results = self._perform_financial_analysis(document_content, document_type)
                key_findings.extend(financial_results["findings"])
                extracted_data.update(financial_results["data"])
                anomalies.extend(financial_results["anomalies"])

            elif analysis_type == "legal_analysis":
                legal_results = self._perform_legal_analysis(document_content, document_type)
                key_findings.extend(legal_results["findings"])
                risk_flags.extend(legal_results["risks"])
                compliance_issues.extend(legal_results["compliance"])

            elif analysis_type == "risk_assessment":
                risk_results = self._perform_risk_assessment(document_content, document_type)
                risk_flags.extend(risk_results["risks"])
                anomalies.extend(risk_results["anomalies"])
                recommendations.extend(risk_results["recommendations"])

            elif analysis_type == "compliance_check":
                compliance_results = self._perform_compliance_check(document_content, document_type)
                compliance_issues.extend(compliance_results["issues"])
                recommendations.extend(compliance_results["recommendations"])

        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(
            document_type, len(key_findings), len(risk_flags), len(anomalies)
        )

        # Determine analysis status
        status = self._determine_analysis_status(risk_flags, compliance_issues, anomalies)

        analysis = DocumentAnalysis(
            analysis_id=analysis_id,
            document_id=document_id,
            analysis_type=",".join(analysis_types),
            status=status,
            confidence_score=confidence_score,
            key_findings=key_findings,
            risk_flags=risk_flags,
            extracted_data=extracted_data,
            anomalies_detected=anomalies,
            compliance_issues=compliance_issues,
            recommendations=recommendations
        )

        # Store analysis history
        self.analysis_history[document_id].append(analysis)

        return analysis

    def batch_analyze_documents(self, documents: List[Dict[str, Any]]) -> List[DocumentAnalysis]:
        """Batch analyze multiple documents"""
        results = []

        for doc_info in documents:
            try:
                analysis = self.analyze_document(
                    document_id=doc_info["document_id"],
                    document_content=doc_info["content"],
                    document_type=DocumentType(doc_info["document_type"]),
                    analysis_types=doc_info.get("analysis_types", ["risk_assessment"])
                )
                results.append(analysis)
            except Exception as e:
                # Create failed analysis record
                failed_analysis = DocumentAnalysis(
                    analysis_id=f"failed_{doc_info['document_id']}_{int(datetime.now().timestamp())}",
                    document_id=doc_info["document_id"],
                    analysis_type="failed",
                    status=AnalysisStatus.FAILED,
                    confidence_score=0.0,
                    key_findings=[],
                    risk_flags=[f"Analysis failed: {str(e)}"],
                    extracted_data={},
                    anomalies_detected=[],
                    compliance_issues=[],
                    recommendations=["Re-upload document with correct format"]
                )
                results.append(failed_analysis)

        return results

    def generate_risk_summary(self, document_analyses: List[DocumentAnalysis]) -> Dict[str, Any]:
        """Generate comprehensive risk summary from multiple document analyses"""

        risk_summary = {
            "total_documents_analyzed": len(document_analyses),
            "high_risk_documents": 0,
            "critical_issues_count": 0,
            "risk_categories": defaultdict(int),
            "top_risk_flags": [],
            "compliance_gaps": [],
            "recommended_actions": [],
            "overall_risk_level": RiskLevel.LOW
        }

        all_risk_flags = []
        all_compliance_issues = []
        all_recommendations = []

        for analysis in document_analyses:
            # Count risk levels
            high_risk_flags = [flag for flag in analysis.risk_flags if "high" in flag.lower() or "critical" in flag.lower()]
            if high_risk_flags:
                risk_summary["high_risk_documents"] += 1

            # Collect all flags and issues
            all_risk_flags.extend(analysis.risk_flags)
            all_compliance_issues.extend(analysis.compliance_issues)
            all_recommendations.extend(analysis.recommendations)

            # Count anomalies as potential risks
            if len(analysis.anomalies_detected) > 2:
                risk_summary["critical_issues_count"] += 1

        # Categorize risks
        for flag in all_risk_flags:
            category = self._categorize_risk_flag(flag)
            risk_summary["risk_categories"][category] += 1

        # Top risk flags (most common)
        flag_counts = defaultdict(int)
        for flag in all_risk_flags:
            flag_counts[flag] += 1

        risk_summary["top_risk_flags"] = sorted(
            flag_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Unique compliance issues
        risk_summary["compliance_gaps"] = list(set(all_compliance_issues))

        # Prioritized recommendations
        recommendation_counts = defaultdict(int)
        for rec in all_recommendations:
            recommendation_counts[rec] += 1

        risk_summary["recommended_actions"] = sorted(
            recommendation_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Determine overall risk level
        if risk_summary["critical_issues_count"] > 5:
            risk_summary["overall_risk_level"] = RiskLevel.CRITICAL
        elif risk_summary["high_risk_documents"] > len(document_analyses) * 0.3:
            risk_summary["overall_risk_level"] = RiskLevel.HIGH
        elif risk_summary["high_risk_documents"] > 0:
            risk_summary["overall_risk_level"] = RiskLevel.MEDIUM
        else:
            risk_summary["overall_risk_level"] = RiskLevel.LOW

        return dict(risk_summary)

    def _extract_basic_information(self, content: str, doc_type: DocumentType) -> Dict[str, Any]:
        """Extract basic information from document"""
        basic_info = {
            "word_count": len(content.split()),
            "has_tables": "table" in content.lower() or "|" in content,
            "has_dates": bool(re.search(r'\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}', content)),
            "has_numbers": bool(re.search(r'\$?[\d,]+\.?\d*', content)),
            "document_length": len(content)
        }

        # Document type specific extractions
        if doc_type == DocumentType.FINANCIAL_STATEMENT:
            basic_info["has_revenue"] = "revenue" in content.lower()
            basic_info["has_expenses"] = "expense" in content.lower() or "cost" in content.lower()
            basic_info["has_balance_sheet"] = "balance sheet" in content.lower()

        elif doc_type == DocumentType.LEGAL_AGREEMENT:
            basic_info["has_terms"] = "terms" in content.lower() and "conditions" in content.lower()
            basic_info["has_signatures"] = "signature" in content.lower() or "signed" in content.lower()
            basic_info["has_liability"] = "liability" in content.lower() or "indemnif" in content.lower()

        return basic_info

    def _perform_financial_analysis(self, content: str, doc_type: DocumentType) -> Dict[str, Any]:
        """Perform AI-powered financial analysis"""
        results = {
            "findings": [],
            "data": {},
            "anomalies": []
        }

        # Extract financial numbers
        number_pattern = r'\$?([\d,]+\.?\d*)'
        numbers = re.findall(number_pattern, content)
        financial_values = [float(n.replace(',', '')) for n in numbers if n.replace(',', '').replace('.', '').isdigit()]

        if financial_values:
            results["data"]["financial_values_found"] = len(financial_values)
            results["data"]["max_value"] = max(financial_values)
            results["data"]["total_value"] = sum(financial_values)

            # Detect anomalies
            if len(financial_values) > 5:
                avg_value = sum(financial_values) / len(financial_values)
                outliers = [v for v in financial_values if v > avg_value * 10]
                if outliers:
                    results["anomalies"].append(f"Detected {len(outliers)} potential outlier values")

        # Revenue analysis
        if "revenue" in content.lower():
            results["findings"].append("Revenue information present")
            if "decline" in content.lower() or "decrease" in content.lower():
                results["findings"].append("Potential revenue decline mentioned")

        # Profitability analysis
        if "profit" in content.lower() or "ebitda" in content.lower():
            results["findings"].append("Profitability metrics present")
            if "loss" in content.lower() and "net" in content.lower():
                results["findings"].append("Net loss indicators present")

        # Cash flow analysis
        if "cash flow" in content.lower():
            results["findings"].append("Cash flow information available")
            if "negative" in content.lower() and "cash" in content.lower():
                results["anomalies"].append("Potential negative cash flow mentioned")

        return results

    def _perform_legal_analysis(self, content: str, doc_type: DocumentType) -> Dict[str, Any]:
        """Perform AI-powered legal analysis"""
        results = {
            "findings": [],
            "risks": [],
            "compliance": []
        }

        # Contract term analysis
        if doc_type in [DocumentType.LEGAL_AGREEMENT, DocumentType.CUSTOMER_CONTRACT]:
            if "termination" in content.lower():
                results["findings"].append("Termination clauses present")

            if "liability" in content.lower():
                results["findings"].append("Liability provisions identified")
                if "unlimited" in content.lower() and "liability" in content.lower():
                    results["risks"].append("Unlimited liability exposure detected")

            if "indemnification" in content.lower():
                results["findings"].append("Indemnification clauses present")

            # Risk indicators
            risk_terms = ["penalty", "default", "breach", "damages", "lawsuit", "litigation"]
            for term in risk_terms:
                if term in content.lower():
                    results["risks"].append(f"Legal risk indicator: {term}")

        # Regulatory compliance
        regulatory_terms = ["regulation", "compliance", "sec", "gdpr", "sox", "hipaa"]
        for term in regulatory_terms:
            if term.upper() in content.upper():
                results["compliance"].append(f"Regulatory reference: {term.upper()}")

        # Intellectual property
        if doc_type == DocumentType.INTELLECTUAL_PROPERTY:
            ip_terms = ["patent", "trademark", "copyright", "trade secret"]
            for term in ip_terms:
                if term in content.lower():
                    results["findings"].append(f"IP asset identified: {term}")

        return results

    def _perform_risk_assessment(self, content: str, doc_type: DocumentType) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        results = {
            "risks": [],
            "anomalies": [],
            "recommendations": []
        }

        # Generic risk indicators
        high_risk_terms = [
            "bankruptcy", "insolvent", "default", "breach", "violation",
            "penalty", "fine", "investigation", "audit", "fraud"
        ]

        for term in high_risk_terms:
            if term in content.lower():
                results["risks"].append(f"High risk indicator: {term}")

        # Financial distress indicators
        distress_terms = ["going concern", "liquidity crisis", "cash shortage", "covenant violation"]
        for term in distress_terms:
            if term in content.lower():
                results["risks"].append(f"Financial distress indicator: {term}")
                results["recommendations"].append("Conduct additional financial due diligence")

        # Environmental risks
        if doc_type == DocumentType.ENVIRONMENTAL_REPORT:
            env_risks = ["contamination", "hazardous", "pollution", "remediation"]
            for term in env_risks:
                if term in content.lower():
                    results["risks"].append(f"Environmental risk: {term}")

        # Document inconsistencies
        dates = re.findall(r'\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}', content)
        if len(set(dates)) > 10:  # Too many different dates
            results["anomalies"].append("High number of different dates - potential inconsistency")

        # Missing information
        if doc_type == DocumentType.FINANCIAL_STATEMENT:
            required_elements = ["revenue", "expense", "asset", "liability"]
            missing = [elem for elem in required_elements if elem not in content.lower()]
            if missing:
                results["anomalies"].append(f"Missing financial elements: {', '.join(missing)}")

        return results

    def _perform_compliance_check(self, content: str, doc_type: DocumentType) -> Dict[str, Any]:
        """Perform regulatory compliance analysis"""
        results = {
            "issues": [],
            "recommendations": []
        }

        # SOX compliance for financial documents
        if doc_type in [DocumentType.FINANCIAL_STATEMENT, DocumentType.AUDIT_REPORT]:
            if "management certification" not in content.lower():
                results["issues"].append("SOX: Missing management certification")
                results["recommendations"].append("Obtain management certification for SOX compliance")

            if "internal control" not in content.lower():
                results["issues"].append("SOX: No internal control assessment mentioned")

        # Tax compliance
        if doc_type == DocumentType.TAX_RETURN:
            if "signature" not in content.lower():
                results["issues"].append("Tax: Missing required signatures")

            if "preparer" not in content.lower():
                results["issues"].append("Tax: Missing preparer information")

        # GDPR compliance for employee records
        if doc_type == DocumentType.EMPLOYEE_RECORDS:
            if "consent" not in content.lower():
                results["issues"].append("GDPR: Missing data processing consent")

            if "retention" not in content.lower():
                results["issues"].append("GDPR: No data retention policy mentioned")

        return results

    def _calculate_confidence_score(self, doc_type: DocumentType, findings_count: int,
                                  risks_count: int, anomalies_count: int) -> float:
        """Calculate analysis confidence score"""
        base_score = 0.7

        # Adjust based on findings
        if findings_count > 5:
            base_score += 0.15
        elif findings_count > 2:
            base_score += 0.1

        # Adjust based on document type complexity
        complex_types = [DocumentType.FINANCIAL_STATEMENT, DocumentType.LEGAL_AGREEMENT]
        if doc_type in complex_types:
            base_score += 0.05

        # Reduce score for high risk/anomaly count
        if risks_count > 5 or anomalies_count > 3:
            base_score -= 0.1

        return max(0.3, min(0.95, base_score))

    def _determine_analysis_status(self, risk_flags: List[str], compliance_issues: List[str],
                                 anomalies: List[str]) -> AnalysisStatus:
        """Determine analysis status based on findings"""
        if len(risk_flags) > 5 or len(compliance_issues) > 3:
            return AnalysisStatus.REQUIRES_REVIEW

        if len(anomalies) > 5:
            return AnalysisStatus.REQUIRES_REVIEW

        return AnalysisStatus.COMPLETED

    def _categorize_risk_flag(self, flag: str) -> str:
        """Categorize risk flag into type"""
        flag_lower = flag.lower()

        if any(term in flag_lower for term in ["financial", "revenue", "cash", "profit"]):
            return "Financial"
        elif any(term in flag_lower for term in ["legal", "contract", "liability", "litigation"]):
            return "Legal"
        elif any(term in flag_lower for term in ["compliance", "regulatory", "sox", "gdpr"]):
            return "Compliance"
        elif any(term in flag_lower for term in ["operational", "process", "system"]):
            return "Operational"
        elif any(term in flag_lower for term in ["environmental", "safety", "health"]):
            return "Environmental"
        else:
            return "Other"

    def _initialize_risk_patterns(self) -> None:
        """Initialize known risk patterns for detection"""
        self.risk_patterns = {
            "financial_distress": [
                r"going\s+concern",
                r"liquidity\s+crisis",
                r"covenant\s+violation",
                r"cash\s+shortage"
            ],
            "legal_issues": [
                r"pending\s+litigation",
                r"regulatory\s+investigation",
                r"breach\s+of\s+contract",
                r"intellectual\s+property\s+dispute"
            ],
            "operational_risks": [
                r"key\s+person\s+dependency",
                r"system\s+failure",
                r"supply\s+chain\s+disruption",
                r"customer\s+concentration"
            ]
        }

class DataRoomManager:
    """Advanced data room management and access control"""

    def __init__(self):
        self.data_rooms = {}
        self.users = {}
        self.access_logs = defaultdict(list)
        self.folder_structure = defaultdict(dict)
        self.document_metadata = {}

    def create_data_room(self, data_room_id: str, name: str, deal_id: str,
                        administrator: str) -> bool:
        """Create new data room"""
        try:
            self.data_rooms[data_room_id] = {
                "data_room_id": data_room_id,
                "name": name,
                "deal_id": deal_id,
                "administrator": administrator,
                "created_date": datetime.now(),
                "status": "active",
                "security_settings": {
                    "watermarking": True,
                    "download_restrictions": True,
                    "view_tracking": True,
                    "expiry_date": datetime.now() + timedelta(days=365)
                }
            }

            # Create default folder structure
            self._create_default_folders(data_room_id)

            return True
        except Exception:
            return False

    def add_user(self, data_room_id: str, user: DataRoomUser) -> bool:
        """Add user to data room with specific access permissions"""
        if data_room_id not in self.data_rooms:
            return False

        user_key = f"{data_room_id}_{user.user_id}"
        self.users[user_key] = user

        # Log access grant
        self.access_logs[data_room_id].append({
            "action": "user_added",
            "user_id": user.user_id,
            "access_level": user.access_level.value,
            "timestamp": datetime.now()
        })

        return True

    def upload_document(self, data_room_id: str, user_id: str,
                       document_metadata: DocumentMetadata,
                       folder_path: str) -> bool:
        """Upload document to data room"""
        user_key = f"{data_room_id}_{user_id}"

        # Check user permissions
        if user_key not in self.users:
            return False

        user = self.users[user_key]
        if user.access_level not in [DataRoomAccess.UPLOAD, DataRoomAccess.ADMIN]:
            return False

        # Check folder permissions
        if folder_path not in user.permitted_folders and user.access_level != DataRoomAccess.ADMIN:
            return False

        # Store document metadata
        doc_key = f"{data_room_id}_{document_metadata.document_id}"
        self.document_metadata[doc_key] = {
            "metadata": document_metadata,
            "folder_path": folder_path,
            "data_room_id": data_room_id
        }

        # Update folder structure
        if folder_path not in self.folder_structure[data_room_id]:
            self.folder_structure[data_room_id][folder_path] = []

        self.folder_structure[data_room_id][folder_path].append(document_metadata.document_id)

        # Log upload
        self.access_logs[data_room_id].append({
            "action": "document_uploaded",
            "user_id": user_id,
            "document_id": document_metadata.document_id,
            "folder_path": folder_path,
            "timestamp": datetime.now()
        })

        return True

    def get_user_accessible_documents(self, data_room_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get list of documents accessible to user"""
        user_key = f"{data_room_id}_{user_id}"

        if user_key not in self.users:
            return []

        user = self.users[user_key]
        accessible_docs = []

        # Get documents from permitted folders
        permitted_folders = user.permitted_folders if user.access_level != DataRoomAccess.ADMIN else self.folder_structure[data_room_id].keys()

        for folder_path in permitted_folders:
            if folder_path in self.folder_structure.get(data_room_id, {}):
                for doc_id in self.folder_structure[data_room_id][folder_path]:
                    doc_key = f"{data_room_id}_{doc_id}"
                    if doc_key in self.document_metadata:
                        doc_info = self.document_metadata[doc_key]
                        accessible_docs.append({
                            "document_id": doc_id,
                            "filename": doc_info["metadata"].filename,
                            "document_type": doc_info["metadata"].document_type.value,
                            "file_size": doc_info["metadata"].file_size,
                            "upload_date": doc_info["metadata"].upload_date.isoformat(),
                            "folder_path": folder_path,
                            "tags": doc_info["metadata"].tags
                        })

        return accessible_docs

    def track_document_access(self, data_room_id: str, user_id: str,
                            document_id: str, action: str) -> bool:
        """Track document access for audit trail"""
        # Log the access
        self.access_logs[data_room_id].append({
            "action": f"document_{action}",
            "user_id": user_id,
            "document_id": document_id,
            "timestamp": datetime.now()
        })

        # Update user's last activity
        user_key = f"{data_room_id}_{user_id}"
        if user_key in self.users:
            self.users[user_key].last_activity = datetime.now()

            # Track downloads
            if action == "downloaded":
                self.users[user_key].download_log.append(f"{document_id}:{datetime.now().isoformat()}")

        return True

    def get_data_room_analytics(self, data_room_id: str) -> Dict[str, Any]:
        """Get comprehensive data room analytics"""
        if data_room_id not in self.data_rooms:
            return {}

        # User activity analytics
        user_activities = defaultdict(int)
        document_access_counts = defaultdict(int)
        access_by_day = defaultdict(int)

        for log_entry in self.access_logs.get(data_room_id, []):
            user_activities[log_entry["user_id"]] += 1
            if "document_" in log_entry["action"]:
                document_access_counts[log_entry.get("document_id", "unknown")] += 1

            access_date = log_entry["timestamp"].date()
            access_by_day[access_date.isoformat()] += 1

        # Document statistics
        total_documents = sum(
            len(docs) for docs in self.folder_structure.get(data_room_id, {}).values()
        )

        # Most active users
        most_active_users = sorted(
            user_activities.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Most accessed documents
        most_accessed_docs = sorted(
            document_access_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        return {
            "data_room_id": data_room_id,
            "total_documents": total_documents,
            "total_users": len([u for u in self.users.keys() if u.startswith(f"{data_room_id}_")]),
            "total_activities": sum(user_activities.values()),
            "most_active_users": most_active_users,
            "most_accessed_documents": most_accessed_docs,
            "daily_activity": dict(access_by_day),
            "folder_distribution": {
                folder: len(docs)
                for folder, docs in self.folder_structure.get(data_room_id, {}).items()
            }
        }

    def _create_default_folders(self, data_room_id: str) -> None:
        """Create default folder structure for data room"""
        default_folders = [
            "01_Executive_Summary",
            "02_Corporate_Information",
            "03_Financial_Information",
            "04_Legal_Documents",
            "05_Commercial_Information",
            "06_Operations",
            "07_Human_Resources",
            "08_Technology_IP",
            "09_Environmental_Health_Safety",
            "10_Insurance_Risk_Management"
        ]

        self.folder_structure[data_room_id] = {folder: [] for folder in default_folders}

class QAAutomationEngine:
    """Automated Q&A management and response generation"""

    def __init__(self):
        self.qa_database = {}
        self.knowledge_base = defaultdict(list)
        self.response_templates = {}
        self.assignment_rules = {}

    def create_qa_item(self, qa_item: QAItem) -> bool:
        """Create new Q&A item"""
        try:
            self.qa_database[qa_item.qa_id] = qa_item

            # Auto-assign based on category
            if qa_item.category in self.assignment_rules:
                qa_item.assigned_to = self.assignment_rules[qa_item.category]

            # Set due date based on priority
            if not qa_item.due_date:
                priority_days = {
                    ReviewPriority.URGENT: 1,
                    ReviewPriority.HIGH: 3,
                    ReviewPriority.MEDIUM: 7,
                    ReviewPriority.LOW: 14
                }
                days_to_add = priority_days.get(qa_item.priority, 7)
                qa_item.due_date = datetime.now() + timedelta(days=days_to_add)

            return True
        except Exception:
            return False

    def generate_automated_response(self, qa_id: str, document_analyses: List[DocumentAnalysis]) -> Optional[str]:
        """Generate automated response using AI and document analysis"""
        if qa_id not in self.qa_database:
            return None

        qa_item = self.qa_database[qa_id]
        question = qa_item.question.lower()

        # Search for relevant information in document analyses
        relevant_info = []
        supporting_docs = []

        for analysis in document_analyses:
            # Check if analysis contains relevant information
            if self._is_relevant_to_question(question, analysis):
                relevant_info.extend(analysis.key_findings)
                supporting_docs.append(analysis.document_id)

                # Extract specific data points
                if analysis.extracted_data:
                    relevant_info.extend([
                        f"{key}: {value}" for key, value in analysis.extracted_data.items()
                        if self._keyword_match(question, key)
                    ])

        # Generate response based on question type
        if "financial" in question or "revenue" in question or "profit" in question:
            response = self._generate_financial_response(question, relevant_info)
        elif "legal" in question or "contract" in question or "agreement" in question:
            response = self._generate_legal_response(question, relevant_info)
        elif "risk" in question or "compliance" in question:
            response = self._generate_risk_response(question, relevant_info)
        else:
            response = self._generate_generic_response(question, relevant_info)

        # Update Q&A item with response
        if response:
            qa_item.answer = response
            qa_item.supporting_documents = supporting_docs
            qa_item.status = "answered"

        return response

    def get_pending_questions(self, assignee: Optional[str] = None,
                            priority: Optional[ReviewPriority] = None) -> List[Dict[str, Any]]:
        """Get pending Q&A items"""
        pending_questions = []

        for qa_item in self.qa_database.values():
            if qa_item.status in ["pending", "in_progress"]:
                # Filter by assignee
                if assignee and qa_item.assigned_to != assignee:
                    continue

                # Filter by priority
                if priority and qa_item.priority != priority:
                    continue

                pending_questions.append({
                    "qa_id": qa_item.qa_id,
                    "question": qa_item.question,
                    "category": qa_item.category,
                    "priority": qa_item.priority.value,
                    "status": qa_item.status,
                    "assigned_to": qa_item.assigned_to,
                    "created_date": qa_item.created_date.isoformat(),
                    "due_date": qa_item.due_date.isoformat() if qa_item.due_date else None,
                    "is_overdue": qa_item.due_date and qa_item.due_date < datetime.now()
                })

        # Sort by priority and due date
        pending_questions.sort(key=lambda x: (
            self._priority_sort_key(x["priority"]),
            x["due_date"] or "9999-12-31"
        ))

        return pending_questions

    def _is_relevant_to_question(self, question: str, analysis: DocumentAnalysis) -> bool:
        """Determine if document analysis is relevant to question"""
        question_words = set(question.split())

        # Check key findings
        for finding in analysis.key_findings:
            finding_words = set(finding.lower().split())
            if len(question_words.intersection(finding_words)) > 1:
                return True

        # Check extracted data keys
        for key in analysis.extracted_data.keys():
            if any(word in key.lower() for word in question_words):
                return True

        return False

    def _keyword_match(self, question: str, key: str) -> bool:
        """Check if key matches question keywords"""
        question_words = question.split()
        return any(word in key.lower() for word in question_words if len(word) > 3)

    def _generate_financial_response(self, question: str, relevant_info: List[str]) -> str:
        """Generate financial-specific response"""
        if not relevant_info:
            return "Financial information is under review. Detailed analysis will be provided upon completion of financial due diligence."

        response_parts = ["Based on the financial documentation reviewed:"]
        response_parts.extend([f"• {info}" for info in relevant_info[:5]])

        if "revenue" in question:
            response_parts.append("Additional revenue analysis is available in the financial due diligence report.")

        return "\n".join(response_parts)

    def _generate_legal_response(self, question: str, relevant_info: List[str]) -> str:
        """Generate legal-specific response"""
        if not relevant_info:
            return "Legal matters are under review by counsel. Detailed legal analysis will be provided following legal due diligence completion."

        response_parts = ["Based on legal document review:"]
        response_parts.extend([f"• {info}" for info in relevant_info[:5]])
        response_parts.append("Please refer to legal due diligence report for comprehensive analysis.")

        return "\n".join(response_parts)

    def _generate_risk_response(self, question: str, relevant_info: List[str]) -> str:
        """Generate risk-specific response"""
        if not relevant_info:
            return "Risk assessment is in progress. Comprehensive risk analysis will be provided upon completion of due diligence review."

        response_parts = ["Based on risk assessment:"]
        response_parts.extend([f"• {info}" for info in relevant_info[:5]])
        response_parts.append("Detailed risk mitigation strategies are outlined in the risk assessment report.")

        return "\n".join(response_parts)

    def _generate_generic_response(self, question: str, relevant_info: List[str]) -> str:
        """Generate generic response"""
        if not relevant_info:
            return "This matter is under review as part of the due diligence process. Additional information will be provided as it becomes available."

        response_parts = ["Based on available documentation:"]
        response_parts.extend([f"• {info}" for info in relevant_info[:3]])

        return "\n".join(response_parts)

    def _priority_sort_key(self, priority: str) -> int:
        """Get sort key for priority"""
        priority_map = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        return priority_map.get(priority, 2)

class DueDiligenceAutomation:
    """Main due diligence automation orchestrator"""

    def __init__(self):
        self.document_analysis_engine = DocumentAnalysisEngine()
        self.data_room_manager = DataRoomManager()
        self.qa_automation_engine = QAAutomationEngine()
        self.automation_metrics = defaultdict(dict)

    async def initialize_due_diligence_process(self, deal_id: str, data_room_config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize comprehensive due diligence process"""

        # Initialize analysis models
        models_initialized = self.document_analysis_engine.initialize_analysis_models()

        # Create data room
        data_room_id = f"dataroom_{deal_id}"
        data_room_created = self.data_room_manager.create_data_room(
            data_room_id=data_room_id,
            name=f"Data Room - {deal_id}",
            deal_id=deal_id,
            administrator=data_room_config.get("administrator", "admin")
        )

        # Add initial users
        users_added = 0
        for user_config in data_room_config.get("users", []):
            user = DataRoomUser(
                user_id=user_config["user_id"],
                name=user_config["name"],
                organization=user_config["organization"],
                email=user_config["email"],
                access_level=DataRoomAccess(user_config["access_level"]),
                permitted_folders=user_config.get("permitted_folders", []),
                access_granted_date=datetime.now()
            )

            if self.data_room_manager.add_user(data_room_id, user):
                users_added += 1

        return {
            "deal_id": deal_id,
            "data_room_id": data_room_id,
            "initialization_status": "completed",
            "models_initialized": models_initialized,
            "data_room_created": data_room_created,
            "users_added": users_added,
            "initialization_timestamp": datetime.now().isoformat()
        }

    async def process_document_batch(self, data_room_id: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process batch of documents with automated analysis"""

        # Perform batch analysis
        analyses = self.document_analysis_engine.batch_analyze_documents(documents)

        # Generate risk summary
        risk_summary = self.document_analysis_engine.generate_risk_summary(analyses)

        # Auto-generate Q&A items based on analyses
        qa_items_created = await self._auto_generate_qa_items(analyses)

        # Update metrics
        self.automation_metrics[data_room_id]["documents_processed"] = len(documents)
        self.automation_metrics[data_room_id]["analyses_completed"] = len(analyses)
        self.automation_metrics[data_room_id]["qa_items_generated"] = qa_items_created

        return {
            "data_room_id": data_room_id,
            "documents_processed": len(documents),
            "analyses_completed": len([a for a in analyses if a.status == AnalysisStatus.COMPLETED]),
            "analyses_requiring_review": len([a for a in analyses if a.status == AnalysisStatus.REQUIRES_REVIEW]),
            "risk_summary": risk_summary,
            "qa_items_generated": qa_items_created,
            "processing_timestamp": datetime.now().isoformat()
        }

    async def generate_due_diligence_summary(self, deal_id: str) -> Dict[str, Any]:
        """Generate comprehensive due diligence summary"""

        data_room_id = f"dataroom_{deal_id}"

        # Get all document analyses
        all_analyses = []
        for analyses_list in self.document_analysis_engine.analysis_history.values():
            all_analyses.extend(analyses_list)

        # Generate comprehensive risk summary
        risk_summary = self.document_analysis_engine.generate_risk_summary(all_analyses)

        # Get data room analytics
        data_room_analytics = self.data_room_manager.get_data_room_analytics(data_room_id)

        # Get pending Q&A items
        pending_questions = self.qa_automation_engine.get_pending_questions()

        # Calculate completion metrics
        completion_metrics = self._calculate_completion_metrics(all_analyses, pending_questions)

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            deal_id, risk_summary, completion_metrics, len(all_analyses)
        )

        return {
            "deal_id": deal_id,
            "summary_timestamp": datetime.now().isoformat(),
            "executive_summary": executive_summary,
            "risk_summary": risk_summary,
            "completion_metrics": completion_metrics,
            "data_room_analytics": data_room_analytics,
            "pending_questions_count": len(pending_questions),
            "recommendations": self._generate_dd_recommendations(risk_summary, completion_metrics)
        }

    async def _auto_generate_qa_items(self, analyses: List[DocumentAnalysis]) -> int:
        """Auto-generate Q&A items based on document analyses"""
        qa_items_created = 0

        for analysis in analyses:
            # Generate questions based on risk flags
            for risk_flag in analysis.risk_flags:
                if "high" in risk_flag.lower() or "critical" in risk_flag.lower():
                    qa_item = QAItem(
                        qa_id=f"qa_{analysis.document_id}_{int(datetime.now().timestamp())}",
                        question=f"Please provide additional information regarding: {risk_flag}",
                        category=self._categorize_question(risk_flag),
                        priority=ReviewPriority.HIGH,
                        status="pending"
                    )

                    if self.qa_automation_engine.create_qa_item(qa_item):
                        qa_items_created += 1

            # Generate questions based on compliance issues
            for compliance_issue in analysis.compliance_issues:
                qa_item = QAItem(
                    qa_id=f"qa_{analysis.document_id}_compliance_{int(datetime.now().timestamp())}",
                    question=f"Please address compliance matter: {compliance_issue}",
                    category="Compliance",
                    priority=ReviewPriority.MEDIUM,
                    status="pending"
                )

                if self.qa_automation_engine.create_qa_item(qa_item):
                    qa_items_created += 1

        return qa_items_created

    def _categorize_question(self, content: str) -> str:
        """Categorize question based on content"""
        content_lower = content.lower()

        if any(term in content_lower for term in ["financial", "revenue", "cash", "profit"]):
            return "Financial"
        elif any(term in content_lower for term in ["legal", "contract", "liability"]):
            return "Legal"
        elif any(term in content_lower for term in ["compliance", "regulatory"]):
            return "Compliance"
        elif any(term in content_lower for term in ["operational", "business"]):
            return "Operational"
        else:
            return "General"

    def _calculate_completion_metrics(self, analyses: List[DocumentAnalysis],
                                    pending_questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate due diligence completion metrics"""
        total_analyses = len(analyses)
        completed_analyses = len([a for a in analyses if a.status == AnalysisStatus.COMPLETED])
        requiring_review = len([a for a in analyses if a.status == AnalysisStatus.REQUIRES_REVIEW])

        completion_percentage = (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0

        return {
            "total_documents_analyzed": total_analyses,
            "completed_analyses": completed_analyses,
            "requiring_review": requiring_review,
            "completion_percentage": round(completion_percentage, 2),
            "pending_questions": len(pending_questions),
            "overdue_questions": len([q for q in pending_questions if q.get("is_overdue", False)])
        }

    def _generate_executive_summary(self, deal_id: str, risk_summary: Dict[str, Any],
                                  completion_metrics: Dict[str, Any], total_docs: int) -> str:
        """Generate executive summary of due diligence"""
        summary_parts = []

        summary_parts.append(f"Due diligence review for Deal {deal_id} has analyzed {total_docs} documents.")

        # Completion status
        completion_pct = completion_metrics["completion_percentage"]
        if completion_pct >= 90:
            summary_parts.append("Due diligence is substantially complete.")
        elif completion_pct >= 70:
            summary_parts.append("Due diligence is well advanced with most areas covered.")
        else:
            summary_parts.append("Due diligence is in progress with additional analysis required.")

        # Risk assessment
        risk_level = risk_summary["overall_risk_level"]
        if risk_level == RiskLevel.LOW:
            summary_parts.append("Overall risk profile is manageable with standard risk mitigation measures.")
        elif risk_level == RiskLevel.MEDIUM:
            summary_parts.append("Moderate risk factors identified requiring specific attention and mitigation strategies.")
        elif risk_level == RiskLevel.HIGH:
            summary_parts.append("Significant risk factors detected requiring comprehensive risk management and additional due diligence.")
        else:
            summary_parts.append("Critical risk factors identified requiring immediate attention and potential deal structure modifications.")

        # Action items
        pending_count = completion_metrics["pending_questions"]
        if pending_count > 0:
            summary_parts.append(f"{pending_count} outstanding questions require resolution before closing.")

        return " ".join(summary_parts)

    def _generate_dd_recommendations(self, risk_summary: Dict[str, Any],
                                   completion_metrics: Dict[str, Any]) -> List[str]:
        """Generate due diligence recommendations"""
        recommendations = []

        # Completion-based recommendations
        if completion_metrics["completion_percentage"] < 90:
            recommendations.append("Complete analysis of remaining documents before proceeding to closing")

        if completion_metrics["pending_questions"] > 0:
            recommendations.append("Resolve all outstanding Q&A items")

        # Risk-based recommendations
        risk_level = risk_summary["overall_risk_level"]
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Implement comprehensive risk mitigation strategies")
            recommendations.append("Consider additional warranties and indemnifications")

        if risk_summary["high_risk_documents"] > 0:
            recommendations.append("Conduct specialized review of high-risk documents")

        # Process recommendations
        if completion_metrics["overdue_questions"] > 0:
            recommendations.append("Prioritize resolution of overdue Q&A items")

        return recommendations

# Service instance management
_due_diligence_automation_instance = None

def get_due_diligence_automation() -> DueDiligenceAutomation:
    """Get singleton due diligence automation instance"""
    global _due_diligence_automation_instance
    if _due_diligence_automation_instance is None:
        _due_diligence_automation_instance = DueDiligenceAutomation()
    return _due_diligence_automation_instance