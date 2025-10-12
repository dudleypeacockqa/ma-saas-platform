"""
Regulatory Intelligence - Sprint 15
Advanced regulatory monitoring, compliance reporting, and legal document analysis
"""

from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import json
import uuid
import re
from collections import defaultdict, deque

class RegulatoryDomain(Enum):
    SECURITIES = "securities"
    BANKING = "banking"
    INSURANCE = "insurance"
    ANTITRUST = "antitrust"
    TAX = "tax"
    LABOR = "labor"
    ENVIRONMENTAL = "environmental"
    DATA_PROTECTION = "data_protection"
    CONSUMER_PROTECTION = "consumer_protection"
    HEALTHCARE = "healthcare"

class Jurisdiction(Enum):
    US_FEDERAL = "us_federal"
    US_STATE = "us_state"
    EU = "european_union"
    UK = "united_kingdom"
    CANADA = "canada"
    AUSTRALIA = "australia"
    SINGAPORE = "singapore"
    HONG_KONG = "hong_kong"
    INTERNATIONAL = "international"

class RegulationType(Enum):
    LAW = "law"
    REGULATION = "regulation"
    GUIDANCE = "guidance"
    INTERPRETATION = "interpretation"
    ENFORCEMENT_ACTION = "enforcement_action"
    PROPOSED_RULE = "proposed_rule"
    FINAL_RULE = "final_rule"

class ComplianceReportType(Enum):
    QUARTERLY_FILING = "quarterly_filing"
    ANNUAL_REPORT = "annual_report"
    TRANSACTION_NOTICE = "transaction_notice"
    COMPLIANCE_CERTIFICATE = "compliance_certificate"
    REGULATORY_SUBMISSION = "regulatory_submission"
    AUDIT_REPORT = "audit_report"
    DISCLOSURE_STATEMENT = "disclosure_statement"

class AlertSeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RegulatoryDocument:
    """Regulatory document or rule"""
    document_id: str
    title: str
    description: str
    regulation_type: RegulationType
    domain: RegulatoryDomain
    jurisdiction: Jurisdiction
    effective_date: datetime
    publication_date: datetime
    source_url: str = ""
    document_text: str = ""
    key_provisions: List[str] = field(default_factory=list)
    compliance_deadlines: List[datetime] = field(default_factory=list)
    affected_entities: List[str] = field(default_factory=list)
    related_documents: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

@dataclass
class RegulatoryChange:
    """Regulatory change notification"""
    change_id: str
    document_id: str
    change_type: str  # amendment, repeal, new_rule, etc.
    change_description: str
    effective_date: datetime
    impact_assessment: str = ""
    affected_provisions: List[str] = field(default_factory=list)
    transition_period: Optional[int] = None  # days
    compliance_actions_required: List[str] = field(default_factory=list)
    severity: AlertSeverity = AlertSeverity.MEDIUM

@dataclass
class ComplianceObligation:
    """Specific compliance obligation"""
    obligation_id: str
    title: str
    description: str
    regulatory_source: str
    domain: RegulatoryDomain
    jurisdiction: Jurisdiction
    due_frequency: str  # annually, quarterly, etc.
    next_due_date: datetime
    responsible_party: str = ""
    compliance_actions: List[str] = field(default_factory=list)
    documentation_required: List[str] = field(default_factory=list)
    penalties_for_non_compliance: str = ""

@dataclass
class ComplianceReport:
    """Generated compliance report"""
    report_id: str
    report_type: ComplianceReportType
    title: str
    reporting_period_start: datetime
    reporting_period_end: datetime
    jurisdiction: Jurisdiction
    domain: RegulatoryDomain
    generated_date: datetime
    submitted_date: Optional[datetime] = None
    report_content: Dict[str, Any] = field(default_factory=dict)
    supporting_documents: List[str] = field(default_factory=list)
    submission_reference: str = ""
    status: str = "draft"

@dataclass
class RegulatoryAlert:
    """Regulatory alert notification"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    domain: RegulatoryDomain
    jurisdictions: List[Jurisdiction] = field(default_factory=list)
    alert_date: datetime = field(default_factory=datetime.now)
    effective_date: Optional[datetime] = None
    action_required: bool = False
    deadline: Optional[datetime] = None
    related_documents: List[str] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    acknowledged_by: List[str] = field(default_factory=list)

@dataclass
class LegalAnalysis:
    """Legal document analysis result"""
    analysis_id: str
    document_id: str
    analysis_type: str
    key_findings: List[str] = field(default_factory=list)
    risk_assessment: str = ""
    compliance_implications: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    analysis_date: datetime = field(default_factory=datetime.now)
    analyst_id: str = ""

class RegulatoryMonitor:
    """Monitors regulatory changes and updates"""

    def __init__(self):
        self.regulatory_documents = {}
        self.regulatory_changes = {}
        self.monitoring_sources = {}
        self.alert_subscriptions = defaultdict(list)
        self.monitoring_active = False

    def add_monitoring_source(self, source_id: str, source_name: str,
                            source_url: str, domains: List[RegulatoryDomain],
                            jurisdictions: List[Jurisdiction]) -> bool:
        """Add regulatory monitoring source"""
        self.monitoring_sources[source_id] = {
            "name": source_name,
            "url": source_url,
            "domains": domains,
            "jurisdictions": jurisdictions,
            "last_checked": None,
            "active": True
        }
        return True

    async def start_monitoring(self):
        """Start regulatory monitoring"""
        self.monitoring_active = True

        while self.monitoring_active:
            await self._check_regulatory_updates()
            await asyncio.sleep(3600)  # Check hourly

    async def _check_regulatory_updates(self):
        """Check for regulatory updates from sources"""
        for source_id, source_config in self.monitoring_sources.items():
            if not source_config["active"]:
                continue

            try:
                # Simulate checking regulatory source
                # In production, would fetch from actual regulatory APIs/feeds
                updates = await self._fetch_updates_from_source(source_id, source_config)

                for update in updates:
                    await self._process_regulatory_update(update)

                source_config["last_checked"] = datetime.now()

            except Exception as e:
                print(f"Error checking source {source_id}: {e}")

    async def _fetch_updates_from_source(self, source_id: str,
                                       source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch updates from regulatory source"""
        # Simulate fetching regulatory updates
        # In production, would integrate with actual regulatory data feeds
        return []

    async def _process_regulatory_update(self, update: Dict[str, Any]):
        """Process regulatory update"""
        # Create regulatory document if new
        if "document" in update:
            doc_data = update["document"]
            document_id = self._create_regulatory_document(doc_data)

            # Check if this affects any monitored entities
            await self._assess_regulatory_impact(document_id)

        # Create regulatory change if modification
        if "change" in update:
            change_data = update["change"]
            self._create_regulatory_change(change_data)

    def _create_regulatory_document(self, doc_data: Dict[str, Any]) -> str:
        """Create regulatory document record"""
        document_id = f"reg_doc_{uuid.uuid4().hex[:8]}"

        document = RegulatoryDocument(
            document_id=document_id,
            title=doc_data.get("title", ""),
            description=doc_data.get("description", ""),
            regulation_type=RegulationType(doc_data.get("type", "regulation")),
            domain=RegulatoryDomain(doc_data.get("domain", "securities")),
            jurisdiction=Jurisdiction(doc_data.get("jurisdiction", "us_federal")),
            effective_date=datetime.fromisoformat(doc_data.get("effective_date", datetime.now().isoformat())),
            publication_date=datetime.fromisoformat(doc_data.get("publication_date", datetime.now().isoformat())),
            source_url=doc_data.get("source_url", ""),
            document_text=doc_data.get("text", "")
        )

        self.regulatory_documents[document_id] = document
        return document_id

    def _create_regulatory_change(self, change_data: Dict[str, Any]) -> str:
        """Create regulatory change record"""
        change_id = f"reg_change_{uuid.uuid4().hex[:8]}"

        change = RegulatoryChange(
            change_id=change_id,
            document_id=change_data.get("document_id", ""),
            change_type=change_data.get("change_type", "amendment"),
            change_description=change_data.get("description", ""),
            effective_date=datetime.fromisoformat(change_data.get("effective_date", datetime.now().isoformat())),
            impact_assessment=change_data.get("impact", ""),
            severity=AlertSeverity(change_data.get("severity", "medium"))
        )

        self.regulatory_changes[change_id] = change
        return change_id

    async def _assess_regulatory_impact(self, document_id: str):
        """Assess impact of regulatory document"""
        document = self.regulatory_documents.get(document_id)
        if not document:
            return

        # Analyze document for compliance implications
        # This would use NLP/ML in production
        impact_analysis = self._analyze_regulatory_impact(document)

        # Generate alerts if high impact
        if impact_analysis.get("high_impact", False):
            await self._generate_regulatory_alert(document, impact_analysis)

    def _analyze_regulatory_impact(self, document: RegulatoryDocument) -> Dict[str, Any]:
        """Analyze regulatory document impact"""
        # Simplified impact analysis
        # In production, would use sophisticated NLP and legal analysis

        high_impact_keywords = [
            "merger", "acquisition", "disclosure", "reporting",
            "compliance", "penalty", "enforcement", "deadline"
        ]

        text_lower = document.document_text.lower()
        keyword_matches = sum(1 for keyword in high_impact_keywords if keyword in text_lower)

        return {
            "high_impact": keyword_matches >= 3,
            "keyword_matches": keyword_matches,
            "compliance_deadlines_found": len(document.compliance_deadlines),
            "affected_domains": [document.domain.value]
        }

    async def _generate_regulatory_alert(self, document: RegulatoryDocument,
                                       impact_analysis: Dict[str, Any]):
        """Generate regulatory alert"""
        alert_id = f"alert_{uuid.uuid4().hex[:8]}"

        alert = RegulatoryAlert(
            alert_id=alert_id,
            title=f"New Regulatory Requirement: {document.title}",
            description=f"New regulation effective {document.effective_date.strftime('%Y-%m-%d')}",
            severity=AlertSeverity.HIGH,
            domain=document.domain,
            jurisdictions=[document.jurisdiction],
            effective_date=document.effective_date,
            action_required=True,
            related_documents=[document.document_id]
        )

        # Send alert to subscribers
        await self._distribute_alert(alert)

    async def _distribute_alert(self, alert: RegulatoryAlert):
        """Distribute alert to subscribers"""
        subscribers = self.alert_subscriptions.get(alert.domain, [])

        for subscriber_id in subscribers:
            # In production, would send actual notifications
            print(f"Alert sent to {subscriber_id}: {alert.title}")

    def subscribe_to_alerts(self, user_id: str, domains: List[RegulatoryDomain]):
        """Subscribe to regulatory alerts"""
        for domain in domains:
            if user_id not in self.alert_subscriptions[domain]:
                self.alert_subscriptions[domain].append(user_id)

    def stop_monitoring(self):
        """Stop regulatory monitoring"""
        self.monitoring_active = False

    def get_regulatory_documents(self, domain: Optional[RegulatoryDomain] = None,
                               jurisdiction: Optional[Jurisdiction] = None) -> List[RegulatoryDocument]:
        """Get regulatory documents with optional filtering"""
        documents = list(self.regulatory_documents.values())

        if domain:
            documents = [d for d in documents if d.domain == domain]

        if jurisdiction:
            documents = [d for d in documents if d.jurisdiction == jurisdiction]

        return sorted(documents, key=lambda x: x.publication_date, reverse=True)

class DocumentAnalyzer:
    """Analyzes legal and regulatory documents"""

    def __init__(self):
        self.analysis_models = {}
        self.analysis_cache = {}

    async def analyze_document(self, document_id: str, document_text: str,
                             analysis_type: str = "compliance") -> str:
        """Analyze legal document"""
        analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"

        # Perform analysis based on type
        if analysis_type == "compliance":
            analysis_result = await self._compliance_analysis(document_text)
        elif analysis_type == "risk":
            analysis_result = await self._risk_analysis(document_text)
        elif analysis_type == "contract":
            analysis_result = await self._contract_analysis(document_text)
        else:
            analysis_result = await self._general_analysis(document_text)

        analysis = LegalAnalysis(
            analysis_id=analysis_id,
            document_id=document_id,
            analysis_type=analysis_type,
            **analysis_result
        )

        self.analysis_cache[analysis_id] = analysis
        return analysis_id

    async def _compliance_analysis(self, document_text: str) -> Dict[str, Any]:
        """Perform compliance-focused analysis"""
        # Simplified compliance analysis
        compliance_keywords = [
            "shall", "must", "required", "prohibited", "compliance",
            "violation", "penalty", "deadline", "reporting"
        ]

        findings = []
        implications = []
        recommendations = []

        text_lower = document_text.lower()

        for keyword in compliance_keywords:
            if keyword in text_lower:
                findings.append(f"Contains compliance requirement: {keyword}")

        # Extract potential deadlines
        deadline_patterns = [
            r"within (\d+) days",
            r"by (\w+ \d+, \d{4})",
            r"no later than (\w+ \d+)"
        ]

        for pattern in deadline_patterns:
            matches = re.findall(pattern, document_text, re.IGNORECASE)
            for match in matches:
                implications.append(f"Deadline identified: {match}")

        if "penalty" in text_lower or "fine" in text_lower:
            implications.append("Document contains penalty provisions")
            recommendations.append("Review penalty implications and ensure compliance")

        return {
            "key_findings": findings,
            "compliance_implications": implications,
            "recommended_actions": recommendations,
            "confidence_score": 0.8
        }

    async def _risk_analysis(self, document_text: str) -> Dict[str, Any]:
        """Perform risk-focused analysis"""
        risk_keywords = [
            "liability", "indemnification", "damages", "breach",
            "default", "termination", "force majeure"
        ]

        findings = []
        implications = []
        recommendations = []

        text_lower = document_text.lower()

        for keyword in risk_keywords:
            if keyword in text_lower:
                findings.append(f"Risk factor identified: {keyword}")

        if "unlimited liability" in text_lower:
            implications.append("Unlimited liability exposure identified")
            recommendations.append("Consider liability cap negotiations")

        return {
            "key_findings": findings,
            "compliance_implications": implications,
            "recommended_actions": recommendations,
            "confidence_score": 0.7
        }

    async def _contract_analysis(self, document_text: str) -> Dict[str, Any]:
        """Perform contract-focused analysis"""
        # Simplified contract analysis
        return await self._general_analysis(document_text)

    async def _general_analysis(self, document_text: str) -> Dict[str, Any]:
        """Perform general document analysis"""
        return {
            "key_findings": ["Document analyzed"],
            "compliance_implications": ["General review completed"],
            "recommended_actions": ["Further review may be required"],
            "confidence_score": 0.5
        }

    def get_analysis(self, analysis_id: str) -> Optional[LegalAnalysis]:
        """Get analysis result by ID"""
        return self.analysis_cache.get(analysis_id)

class ComplianceReporting:
    """Generates compliance reports and filings"""

    def __init__(self):
        self.report_templates = {}
        self.generated_reports = {}
        self.compliance_obligations = {}
        self._initialize_report_templates()

    def create_compliance_obligation(self, title: str, description: str,
                                   regulatory_source: str, domain: RegulatoryDomain,
                                   jurisdiction: Jurisdiction, due_frequency: str,
                                   next_due_date: datetime) -> str:
        """Create compliance obligation"""
        obligation_id = f"obligation_{uuid.uuid4().hex[:8]}"

        obligation = ComplianceObligation(
            obligation_id=obligation_id,
            title=title,
            description=description,
            regulatory_source=regulatory_source,
            domain=domain,
            jurisdiction=jurisdiction,
            due_frequency=due_frequency,
            next_due_date=next_due_date
        )

        self.compliance_obligations[obligation_id] = obligation
        return obligation_id

    async def generate_compliance_report(self, report_type: ComplianceReportType,
                                       reporting_period_start: datetime,
                                       reporting_period_end: datetime,
                                       jurisdiction: Jurisdiction,
                                       domain: RegulatoryDomain) -> str:
        """Generate compliance report"""
        report_id = f"report_{uuid.uuid4().hex[:8]}"

        # Get appropriate template
        template_key = f"{report_type.value}_{jurisdiction.value}_{domain.value}"
        template = self.report_templates.get(template_key)

        if not template:
            template = self._get_default_template(report_type)

        # Generate report content
        report_content = await self._generate_report_content(
            template, reporting_period_start, reporting_period_end
        )

        report = ComplianceReport(
            report_id=report_id,
            report_type=report_type,
            title=f"{report_type.value.replace('_', ' ').title()} - {reporting_period_end.strftime('%Y-%m-%d')}",
            reporting_period_start=reporting_period_start,
            reporting_period_end=reporting_period_end,
            jurisdiction=jurisdiction,
            domain=domain,
            generated_date=datetime.now(),
            report_content=report_content
        )

        self.generated_reports[report_id] = report
        return report_id

    async def _generate_report_content(self, template: Dict[str, Any],
                                     start_date: datetime,
                                     end_date: datetime) -> Dict[str, Any]:
        """Generate report content based on template"""
        # Simplified report generation
        content = {
            "executive_summary": "Compliance status for reporting period",
            "reporting_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "compliance_status": "Compliant",
            "violations": [],
            "remedial_actions": [],
            "certifications": []
        }

        return content

    def _initialize_report_templates(self):
        """Initialize report templates"""
        # Quarterly filing template
        self.report_templates["quarterly_filing_us_federal_securities"] = {
            "sections": [
                "Financial Position",
                "Operating Results",
                "Cash Flows",
                "Material Changes",
                "Certifications"
            ],
            "required_data": [
                "financial_statements",
                "management_discussion",
                "controls_assessment"
            ]
        }

        # Annual report template
        self.report_templates["annual_report_us_federal_securities"] = {
            "sections": [
                "Business Overview",
                "Risk Factors",
                "Financial Statements",
                "Management Discussion",
                "Corporate Governance",
                "Executive Compensation"
            ],
            "required_data": [
                "audited_financials",
                "governance_report",
                "compensation_disclosure"
            ]
        }

    def _get_default_template(self, report_type: ComplianceReportType) -> Dict[str, Any]:
        """Get default template for report type"""
        return {
            "sections": ["Executive Summary", "Compliance Status", "Recommendations"],
            "required_data": ["compliance_data"]
        }

    def get_compliance_obligations_due(self, days_ahead: int = 30) -> List[ComplianceObligation]:
        """Get compliance obligations due within specified days"""
        cutoff_date = datetime.now() + timedelta(days=days_ahead)

        return [
            obligation for obligation in self.compliance_obligations.values()
            if obligation.next_due_date <= cutoff_date
        ]

    def get_report(self, report_id: str) -> Optional[ComplianceReport]:
        """Get compliance report by ID"""
        return self.generated_reports.get(report_id)

class RegulatoryIntelligence:
    """Central regulatory intelligence coordination"""

    def __init__(self):
        self.regulatory_monitor = RegulatoryMonitor()
        self.document_analyzer = DocumentAnalyzer()
        self.compliance_reporting = ComplianceReporting()
        self.intelligence_stats = {
            "documents_monitored": 0,
            "alerts_generated": 0,
            "reports_generated": 0,
            "analyses_completed": 0
        }

    async def start_regulatory_monitoring(self):
        """Start regulatory monitoring"""
        await self.regulatory_monitor.start_monitoring()

    async def analyze_regulatory_document(self, document_id: str,
                                        document_text: str) -> str:
        """Analyze regulatory document"""
        analysis_id = await self.document_analyzer.analyze_document(
            document_id, document_text, "compliance"
        )
        self.intelligence_stats["analyses_completed"] += 1
        return analysis_id

    async def generate_compliance_report(self, report_type: ComplianceReportType,
                                       period_start: datetime, period_end: datetime,
                                       jurisdiction: Jurisdiction,
                                       domain: RegulatoryDomain) -> str:
        """Generate compliance report"""
        report_id = await self.compliance_reporting.generate_compliance_report(
            report_type, period_start, period_end, jurisdiction, domain
        )
        self.intelligence_stats["reports_generated"] += 1
        return report_id

    def subscribe_to_regulatory_alerts(self, user_id: str,
                                     domains: List[RegulatoryDomain]):
        """Subscribe to regulatory alerts"""
        self.regulatory_monitor.subscribe_to_alerts(user_id, domains)

    def get_regulatory_calendar(self, jurisdiction: Jurisdiction,
                              days_ahead: int = 90) -> Dict[str, Any]:
        """Get regulatory calendar"""
        obligations_due = self.compliance_reporting.get_compliance_obligations_due(days_ahead)

        calendar_events = []
        for obligation in obligations_due:
            calendar_events.append({
                "obligation_id": obligation.obligation_id,
                "title": obligation.title,
                "due_date": obligation.next_due_date.isoformat(),
                "domain": obligation.domain.value,
                "frequency": obligation.due_frequency
            })

        return {
            "jurisdiction": jurisdiction.value,
            "period_days": days_ahead,
            "total_obligations": len(calendar_events),
            "upcoming_obligations": sorted(calendar_events, key=lambda x: x["due_date"])
        }

    def get_regulatory_dashboard(self) -> Dict[str, Any]:
        """Get regulatory intelligence dashboard"""
        recent_documents = self.regulatory_monitor.get_regulatory_documents()[:10]
        obligations_due = self.compliance_reporting.get_compliance_obligations_due(30)

        return {
            "recent_regulatory_documents": len(recent_documents),
            "obligations_due_30_days": len(obligations_due),
            "active_monitoring_sources": len([
                s for s in self.regulatory_monitor.monitoring_sources.values()
                if s["active"]
            ]),
            "total_compliance_obligations": len(self.compliance_reporting.compliance_obligations),
            "alerts_this_month": self.intelligence_stats["alerts_generated"],
            "reports_generated": self.intelligence_stats["reports_generated"]
        }

    def get_regulatory_intelligence_stats(self) -> Dict[str, Any]:
        """Get regulatory intelligence statistics"""
        return {
            **self.intelligence_stats,
            "monitoring_sources": len(self.regulatory_monitor.monitoring_sources),
            "regulatory_documents": len(self.regulatory_monitor.regulatory_documents),
            "compliance_obligations": len(self.compliance_reporting.compliance_obligations)
        }

# Singleton instance
_regulatory_intelligence_instance: Optional[RegulatoryIntelligence] = None

def get_regulatory_intelligence() -> RegulatoryIntelligence:
    """Get the singleton Regulatory Intelligence instance"""
    global _regulatory_intelligence_instance
    if _regulatory_intelligence_instance is None:
        _regulatory_intelligence_instance = RegulatoryIntelligence()
    return _regulatory_intelligence_instance