"""
Compliance Engine - Sprint 15
Advanced compliance monitoring, policy management, and regulatory framework enforcement
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

class ComplianceFrameworkType(Enum):
    SOX = "sarbanes_oxley"
    GDPR = "gdpr"
    SEC = "sec_regulations"
    COSO = "coso"
    ISO27001 = "iso_27001"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    CUSTOM = "custom"

class PolicyType(Enum):
    DATA_PROTECTION = "data_protection"
    FINANCIAL_REPORTING = "financial_reporting"
    DOCUMENT_RETENTION = "document_retention"
    ACCESS_CONTROL = "access_control"
    CONFLICT_OF_INTEREST = "conflict_of_interest"
    ANTI_MONEY_LAUNDERING = "anti_money_laundering"
    INSIDER_TRADING = "insider_trading"
    CYBER_SECURITY = "cyber_security"

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    EXCEPTION_GRANTED = "exception_granted"
    REMEDIATION_REQUIRED = "remediation_required"

class ViolationSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MonitoringFrequency(Enum):
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

@dataclass
class ComplianceRule:
    """Individual compliance rule definition"""
    rule_id: str
    name: str
    description: str
    framework: ComplianceFrameworkType
    policy_type: PolicyType
    rule_expression: str  # Boolean expression for evaluation
    severity: ViolationSeverity
    auto_remediation: bool = False
    remediation_actions: List[str] = field(default_factory=list)
    monitoring_frequency: MonitoringFrequency = MonitoringFrequency.DAILY
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class CompliancePolicy:
    """Compliance policy containing multiple rules"""
    policy_id: str
    name: str
    description: str
    policy_type: PolicyType
    framework: ComplianceFrameworkType
    rules: List[ComplianceRule] = field(default_factory=list)
    approval_required: bool = True
    version: str = "1.0"
    effective_date: datetime = field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    owner: str = ""
    status: str = "active"

@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    rule_id: str
    entity_id: str  # ID of entity being monitored
    entity_type: str  # Type of entity (deal, document, user, etc.)
    severity: ViolationSeverity
    violation_date: datetime
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    status: str = "open"
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    remediation_actions: List[str] = field(default_factory=list)

@dataclass
class ComplianceAssessment:
    """Compliance assessment result"""
    assessment_id: str
    entity_id: str
    entity_type: str
    framework: ComplianceFrameworkType
    assessment_date: datetime
    overall_status: ComplianceStatus
    score: float  # 0-100 compliance score
    violations: List[ComplianceViolation] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_assessment_due: Optional[datetime] = None
    assessor: str = ""

@dataclass
class ComplianceFramework:
    """Regulatory compliance framework definition"""
    framework_id: str
    name: str
    description: str
    framework_type: ComplianceFrameworkType
    jurisdiction: str
    version: str
    policies: List[CompliancePolicy] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    mandatory_controls: List[str] = field(default_factory=list)
    reporting_requirements: Dict[str, Any] = field(default_factory=dict)
    implementation_date: datetime = field(default_factory=datetime.now)

class RuleEvaluator:
    """Evaluates compliance rules against data"""

    def __init__(self):
        self.evaluation_functions = {}
        self._register_default_functions()

    def evaluate_rule(self, rule: ComplianceRule, entity_data: Dict[str, Any]) -> bool:
        """Evaluate a compliance rule against entity data"""
        try:
            # Parse and evaluate the rule expression
            return self._evaluate_expression(rule.rule_expression, entity_data)
        except Exception as e:
            print(f"Error evaluating rule {rule.rule_id}: {e}")
            return False

    def _evaluate_expression(self, expression: str, data: Dict[str, Any]) -> bool:
        """Evaluate boolean expression safely"""
        # Simple expression evaluator
        # In production, use a proper expression parser

        # Replace data references with actual values
        evaluated_expression = expression
        for key, value in data.items():
            placeholder = f"${key}"
            if placeholder in expression:
                if isinstance(value, str):
                    evaluated_expression = evaluated_expression.replace(
                        placeholder, f"'{value}'"
                    )
                else:
                    evaluated_expression = evaluated_expression.replace(
                        placeholder, str(value)
                    )

        # Evaluate basic conditions
        try:
            # Safety check - only allow safe operations
            allowed_operators = ['==', '!=', '>', '<', '>=', '<=', 'and', 'or', 'not', 'in']

            # Simple validation
            if any(dangerous in evaluated_expression for dangerous in ['import', 'exec', 'eval', '__']):
                return False

            # Use eval with restricted globals (be careful in production)
            return bool(eval(evaluated_expression, {"__builtins__": {}}, {}))

        except:
            return False

    def _register_default_functions(self):
        """Register default evaluation functions"""
        self.evaluation_functions = {
            "has_field": lambda data, field: field in data and data[field] is not None,
            "field_equals": lambda data, field, value: data.get(field) == value,
            "field_contains": lambda data, field, value: value in str(data.get(field, "")),
            "date_within_days": lambda data, field, days: self._check_date_within(data, field, days),
            "numeric_range": lambda data, field, min_val, max_val: min_val <= data.get(field, 0) <= max_val
        }

    def _check_date_within(self, data: Dict[str, Any], field: str, days: int) -> bool:
        """Check if date field is within specified days"""
        try:
            field_date = data.get(field)
            if isinstance(field_date, str):
                field_date = datetime.fromisoformat(field_date)
            elif not isinstance(field_date, datetime):
                return False

            return (datetime.now() - field_date).days <= days
        except:
            return False

class PolicyEngine:
    """Manages and enforces compliance policies"""

    def __init__(self):
        self.policies = {}
        self.frameworks = {}
        self.rule_evaluator = RuleEvaluator()
        self._initialize_default_frameworks()

    def create_policy(self, name: str, description: str, policy_type: PolicyType,
                     framework: ComplianceFrameworkType) -> str:
        """Create a new compliance policy"""
        policy_id = f"policy_{uuid.uuid4().hex[:8]}"

        policy = CompliancePolicy(
            policy_id=policy_id,
            name=name,
            description=description,
            policy_type=policy_type,
            framework=framework
        )

        self.policies[policy_id] = policy
        return policy_id

    def add_rule_to_policy(self, policy_id: str, rule: ComplianceRule) -> bool:
        """Add a compliance rule to a policy"""
        if policy_id not in self.policies:
            return False

        self.policies[policy_id].rules.append(rule)
        return True

    def create_compliance_rule(self, name: str, description: str,
                              framework: ComplianceFrameworkType,
                              policy_type: PolicyType,
                              rule_expression: str,
                              severity: ViolationSeverity) -> ComplianceRule:
        """Create a new compliance rule"""
        rule_id = f"rule_{uuid.uuid4().hex[:8]}"

        return ComplianceRule(
            rule_id=rule_id,
            name=name,
            description=description,
            framework=framework,
            policy_type=policy_type,
            rule_expression=rule_expression,
            severity=severity
        )

    def evaluate_entity_compliance(self, entity_id: str, entity_type: str,
                                 entity_data: Dict[str, Any],
                                 framework: ComplianceFrameworkType) -> List[ComplianceViolation]:
        """Evaluate entity against compliance rules"""
        violations = []

        # Get relevant policies for the framework
        relevant_policies = [
            policy for policy in self.policies.values()
            if policy.framework == framework and policy.status == "active"
        ]

        for policy in relevant_policies:
            for rule in policy.rules:
                if not rule.enabled:
                    continue

                # Evaluate rule
                is_compliant = self.rule_evaluator.evaluate_rule(rule, entity_data)

                if not is_compliant:
                    violation = ComplianceViolation(
                        violation_id=f"violation_{uuid.uuid4().hex[:8]}",
                        rule_id=rule.rule_id,
                        entity_id=entity_id,
                        entity_type=entity_type,
                        severity=rule.severity,
                        violation_date=datetime.now(),
                        description=f"Violation of rule: {rule.name}",
                        evidence={"rule_expression": rule.rule_expression, "entity_data": entity_data}
                    )
                    violations.append(violation)

        return violations

    def _initialize_default_frameworks(self):
        """Initialize default compliance frameworks"""

        # SOX Framework
        sox_framework = ComplianceFramework(
            framework_id="sox_2002",
            name="Sarbanes-Oxley Act",
            description="US federal law for corporate financial reporting",
            framework_type=ComplianceFrameworkType.SOX,
            jurisdiction="United States",
            version="2002",
            requirements=[
                "Internal control over financial reporting",
                "Management assessment of controls",
                "Auditor attestation",
                "CEO/CFO certification"
            ],
            mandatory_controls=[
                "Segregation of duties",
                "Authorization controls",
                "Documentation requirements",
                "Periodic review and testing"
            ]
        )

        # GDPR Framework
        gdpr_framework = ComplianceFramework(
            framework_id="gdpr_2018",
            name="General Data Protection Regulation",
            description="EU regulation on data protection and privacy",
            framework_type=ComplianceFrameworkType.GDPR,
            jurisdiction="European Union",
            version="2018",
            requirements=[
                "Lawful basis for processing",
                "Data subject rights",
                "Privacy by design",
                "Data protection impact assessments"
            ],
            mandatory_controls=[
                "Consent management",
                "Data breach notification",
                "Data retention policies",
                "Cross-border transfer controls"
            ]
        )

        self.frameworks["sox_2002"] = sox_framework
        self.frameworks["gdpr_2018"] = gdpr_framework

    def get_framework(self, framework_id: str) -> Optional[ComplianceFramework]:
        """Get compliance framework by ID"""
        return self.frameworks.get(framework_id)

    def list_frameworks(self) -> List[ComplianceFramework]:
        """List all compliance frameworks"""
        return list(self.frameworks.values())

    def get_policies_by_framework(self, framework: ComplianceFrameworkType) -> List[CompliancePolicy]:
        """Get policies for a specific framework"""
        return [
            policy for policy in self.policies.values()
            if policy.framework == framework
        ]

class ComplianceMonitor:
    """Monitors compliance in real-time"""

    def __init__(self, policy_engine: PolicyEngine):
        self.policy_engine = policy_engine
        self.monitoring_active = False
        self.monitoring_queue = deque()
        self.violation_handlers = []
        self.monitoring_stats = {
            "entities_monitored": 0,
            "violations_detected": 0,
            "assessments_completed": 0
        }

    async def start_monitoring(self):
        """Start compliance monitoring"""
        self.monitoring_active = True

        while self.monitoring_active:
            await self._process_monitoring_queue()
            await asyncio.sleep(60)  # Check every minute

    async def _process_monitoring_queue(self):
        """Process entities in monitoring queue"""
        while self.monitoring_queue:
            monitoring_task = self.monitoring_queue.popleft()
            await self._monitor_entity(monitoring_task)

    async def _monitor_entity(self, task: Dict[str, Any]):
        """Monitor individual entity for compliance"""
        try:
            entity_id = task["entity_id"]
            entity_type = task["entity_type"]
            entity_data = task["entity_data"]
            framework = task["framework"]

            # Evaluate compliance
            violations = self.policy_engine.evaluate_entity_compliance(
                entity_id, entity_type, entity_data, framework
            )

            if violations:
                await self._handle_violations(violations)

            self.monitoring_stats["entities_monitored"] += 1
            if violations:
                self.monitoring_stats["violations_detected"] += len(violations)

        except Exception as e:
            print(f"Error monitoring entity: {e}")

    async def _handle_violations(self, violations: List[ComplianceViolation]):
        """Handle detected violations"""
        for violation in violations:
            # Execute violation handlers
            for handler in self.violation_handlers:
                try:
                    await handler(violation)
                except Exception as e:
                    print(f"Error in violation handler: {e}")

    def queue_entity_for_monitoring(self, entity_id: str, entity_type: str,
                                  entity_data: Dict[str, Any],
                                  framework: ComplianceFrameworkType):
        """Queue entity for compliance monitoring"""
        monitoring_task = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "entity_data": entity_data,
            "framework": framework,
            "queued_at": datetime.now()
        }

        self.monitoring_queue.append(monitoring_task)

    def add_violation_handler(self, handler: Callable):
        """Add violation handler function"""
        self.violation_handlers.append(handler)

    def stop_monitoring(self):
        """Stop compliance monitoring"""
        self.monitoring_active = False

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        return {
            **self.monitoring_stats,
            "queue_size": len(self.monitoring_queue),
            "active_handlers": len(self.violation_handlers),
            "monitoring_active": self.monitoring_active
        }

class ComplianceEngine:
    """Central compliance engine coordinating all compliance operations"""

    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.compliance_monitor = ComplianceMonitor(self.policy_engine)
        self.assessments = {}
        self.violations = {}
        self.compliance_stats = {
            "frameworks_active": 0,
            "policies_created": 0,
            "violations_total": 0,
            "assessments_completed": 0
        }

    async def create_compliance_framework(self, name: str, description: str,
                                        framework_type: ComplianceFrameworkType,
                                        jurisdiction: str) -> str:
        """Create a new compliance framework"""
        framework_id = f"framework_{uuid.uuid4().hex[:8]}"

        framework = ComplianceFramework(
            framework_id=framework_id,
            name=name,
            description=description,
            framework_type=framework_type,
            jurisdiction=jurisdiction,
            version="1.0"
        )

        self.policy_engine.frameworks[framework_id] = framework
        self.compliance_stats["frameworks_active"] += 1

        return framework_id

    async def create_compliance_policy(self, name: str, description: str,
                                     policy_type: PolicyType,
                                     framework: ComplianceFrameworkType) -> str:
        """Create a compliance policy"""
        policy_id = self.policy_engine.create_policy(
            name, description, policy_type, framework
        )
        self.compliance_stats["policies_created"] += 1
        return policy_id

    async def add_compliance_rule(self, policy_id: str, name: str, description: str,
                                framework: ComplianceFrameworkType,
                                policy_type: PolicyType, rule_expression: str,
                                severity: ViolationSeverity) -> bool:
        """Add a compliance rule to a policy"""
        rule = self.policy_engine.create_compliance_rule(
            name, description, framework, policy_type, rule_expression, severity
        )

        return self.policy_engine.add_rule_to_policy(policy_id, rule)

    async def assess_entity_compliance(self, entity_id: str, entity_type: str,
                                     entity_data: Dict[str, Any],
                                     framework: ComplianceFrameworkType) -> str:
        """Perform compliance assessment on entity"""
        assessment_id = f"assessment_{uuid.uuid4().hex[:8]}"

        # Get violations
        violations = self.policy_engine.evaluate_entity_compliance(
            entity_id, entity_type, entity_data, framework
        )

        # Calculate compliance score
        total_rules = sum(
            len(policy.rules) for policy in self.policy_engine.policies.values()
            if policy.framework == framework and policy.status == "active"
        )

        if total_rules == 0:
            score = 100.0
        else:
            violation_count = len(violations)
            score = max(0, ((total_rules - violation_count) / total_rules) * 100)

        # Determine overall status
        if not violations:
            overall_status = ComplianceStatus.COMPLIANT
        elif any(v.severity == ViolationSeverity.CRITICAL for v in violations):
            overall_status = ComplianceStatus.NON_COMPLIANT
        else:
            overall_status = ComplianceStatus.REMEDIATION_REQUIRED

        # Create assessment
        assessment = ComplianceAssessment(
            assessment_id=assessment_id,
            entity_id=entity_id,
            entity_type=entity_type,
            framework=framework,
            assessment_date=datetime.now(),
            overall_status=overall_status,
            score=score,
            violations=violations,
            next_assessment_due=datetime.now() + timedelta(days=90)
        )

        self.assessments[assessment_id] = assessment
        self.compliance_stats["assessments_completed"] += 1

        # Store violations
        for violation in violations:
            self.violations[violation.violation_id] = violation
            self.compliance_stats["violations_total"] += 1

        return assessment_id

    async def start_compliance_monitoring(self):
        """Start real-time compliance monitoring"""
        await self.compliance_monitor.start_monitoring()

    def queue_compliance_check(self, entity_id: str, entity_type: str,
                             entity_data: Dict[str, Any],
                             framework: ComplianceFrameworkType):
        """Queue entity for compliance monitoring"""
        self.compliance_monitor.queue_entity_for_monitoring(
            entity_id, entity_type, entity_data, framework
        )

    def get_compliance_assessment(self, assessment_id: str) -> Optional[ComplianceAssessment]:
        """Get compliance assessment by ID"""
        return self.assessments.get(assessment_id)

    def get_violations(self, entity_id: Optional[str] = None,
                      severity: Optional[ViolationSeverity] = None) -> List[ComplianceViolation]:
        """Get compliance violations with optional filtering"""
        violations = list(self.violations.values())

        if entity_id:
            violations = [v for v in violations if v.entity_id == entity_id]

        if severity:
            violations = [v for v in violations if v.severity == severity]

        return violations

    def get_compliance_frameworks(self) -> List[ComplianceFramework]:
        """Get all compliance frameworks"""
        return self.policy_engine.list_frameworks()

    def get_compliance_stats(self) -> Dict[str, Any]:
        """Get comprehensive compliance statistics"""
        monitoring_stats = self.compliance_monitor.get_monitoring_stats()

        return {
            **self.compliance_stats,
            **monitoring_stats,
            "active_policies": len([p for p in self.policy_engine.policies.values() if p.status == "active"]),
            "open_violations": len([v for v in self.violations.values() if v.status == "open"]),
            "frameworks_available": len(self.policy_engine.frameworks)
        }

# Singleton instance
_compliance_engine_instance: Optional[ComplianceEngine] = None

def get_compliance_engine() -> ComplianceEngine:
    """Get the singleton Compliance Engine instance"""
    global _compliance_engine_instance
    if _compliance_engine_instance is None:
        _compliance_engine_instance = ComplianceEngine()
    return _compliance_engine_instance