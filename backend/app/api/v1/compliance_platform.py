"""
Compliance Platform API - Sprint 15
RESTful API endpoints for compliance management, risk assessment, audit governance, and regulatory intelligence
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from app.compliance import (
    get_compliance_engine,
    get_risk_assessment,
    get_audit_governance,
    get_regulatory_intelligence
)
from app.compliance.compliance_engine import (
    ComplianceFrameworkType, PolicyType, ViolationSeverity, MonitoringFrequency
)
from app.compliance.risk_assessment import (
    RiskCategory, RiskLevel, MitigationStrategy, RiskImpactType
)
from app.compliance.audit_governance import (
    AuditEventType, GovernanceFrameworkType, EvidenceType, GovernanceRoleType
)
from app.compliance.regulatory_intelligence import (
    RegulatoryDomain, Jurisdiction, ComplianceReportType, AlertSeverity
)

router = APIRouter()

# Request/Response Models
class ComplianceFrameworkRequest(BaseModel):
    name: str
    description: str
    framework_type: str
    jurisdiction: str

class CompliancePolicyRequest(BaseModel):
    name: str
    description: str
    policy_type: str
    framework: str

class ComplianceRuleRequest(BaseModel):
    policy_id: str
    name: str
    description: str
    framework: str
    policy_type: str
    rule_expression: str
    severity: str

class EntityAssessmentRequest(BaseModel):
    entity_id: str
    entity_type: str
    entity_data: Dict[str, Any]
    framework: str

class RiskModelRequest(BaseModel):
    name: str
    description: str
    category: str

class RiskFactorRequest(BaseModel):
    model_id: str
    name: str
    description: str
    category: str
    weight: float = Field(ge=0.0, le=1.0)

class RiskAssessmentRequest(BaseModel):
    entity_id: str
    entity_type: str
    entity_data: Dict[str, Any]
    model_ids: List[str]

class MitigationPlanRequest(BaseModel):
    assessment_id: str
    strategy: str
    actions: List[str]
    responsible_party: str

class AuditEventRequest(BaseModel):
    event_type: str
    user_id: str
    session_id: str
    action: str
    description: str
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    metadata: Dict[str, Any] = {}

class EvidenceRequest(BaseModel):
    evidence_type: str
    title: str
    description: str
    collector_id: str
    source_system: str = ""

class GovernancePolicyRequest(BaseModel):
    name: str
    description: str
    framework_type: str
    policy_content: str

class RegulatoryAlertSubscriptionRequest(BaseModel):
    user_id: str
    domains: List[str]

class ComplianceReportRequest(BaseModel):
    report_type: str
    period_start: datetime
    period_end: datetime
    jurisdiction: str
    domain: str

# =============================================================================
# COMPLIANCE ENGINE ENDPOINTS
# =============================================================================

@router.post("/compliance/frameworks",
             summary="Create Compliance Framework",
             description="Create a new compliance framework")
async def create_compliance_framework(request: ComplianceFrameworkRequest) -> Dict[str, Any]:
    """Create compliance framework"""
    compliance_engine = get_compliance_engine()

    try:
        framework_type = ComplianceFrameworkType(request.framework_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid framework type")

    framework_id = await compliance_engine.create_compliance_framework(
        name=request.name,
        description=request.description,
        framework_type=framework_type,
        jurisdiction=request.jurisdiction
    )

    return {
        "success": True,
        "framework_id": framework_id,
        "message": "Compliance framework created successfully"
    }

@router.get("/compliance/frameworks",
            summary="List Compliance Frameworks",
            description="Get all compliance frameworks")
async def list_compliance_frameworks() -> Dict[str, Any]:
    """List compliance frameworks"""
    compliance_engine = get_compliance_engine()
    frameworks = compliance_engine.get_compliance_frameworks()

    return {
        "success": True,
        "frameworks": [
            {
                "framework_id": f.framework_id,
                "name": f.name,
                "description": f.description,
                "framework_type": f.framework_type.value,
                "jurisdiction": f.jurisdiction,
                "version": f.version,
                "implementation_date": f.implementation_date.isoformat(),
                "policies_count": len(f.policies),
                "requirements_count": len(f.requirements)
            }
            for f in frameworks
        ],
        "count": len(frameworks)
    }

@router.post("/compliance/policies",
             summary="Create Compliance Policy",
             description="Create a new compliance policy")
async def create_compliance_policy(request: CompliancePolicyRequest) -> Dict[str, Any]:
    """Create compliance policy"""
    compliance_engine = get_compliance_engine()

    try:
        policy_type = PolicyType(request.policy_type)
        framework = ComplianceFrameworkType(request.framework)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid policy type or framework")

    policy_id = await compliance_engine.create_compliance_policy(
        name=request.name,
        description=request.description,
        policy_type=policy_type,
        framework=framework
    )

    return {
        "success": True,
        "policy_id": policy_id,
        "message": "Compliance policy created successfully"
    }

@router.post("/compliance/rules",
             summary="Add Compliance Rule",
             description="Add a compliance rule to a policy")
async def add_compliance_rule(request: ComplianceRuleRequest) -> Dict[str, Any]:
    """Add compliance rule"""
    compliance_engine = get_compliance_engine()

    try:
        framework = ComplianceFrameworkType(request.framework)
        policy_type = PolicyType(request.policy_type)
        severity = ViolationSeverity(request.severity)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid enum values")

    success = await compliance_engine.add_compliance_rule(
        policy_id=request.policy_id,
        name=request.name,
        description=request.description,
        framework=framework,
        policy_type=policy_type,
        rule_expression=request.rule_expression,
        severity=severity
    )

    return {
        "success": success,
        "message": "Compliance rule added successfully" if success else "Failed to add rule"
    }

@router.post("/compliance/assess",
             summary="Assess Entity Compliance",
             description="Perform compliance assessment on entity")
async def assess_entity_compliance(request: EntityAssessmentRequest) -> Dict[str, Any]:
    """Assess entity compliance"""
    compliance_engine = get_compliance_engine()

    try:
        framework = ComplianceFrameworkType(request.framework)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid framework")

    assessment_id = await compliance_engine.assess_entity_compliance(
        entity_id=request.entity_id,
        entity_type=request.entity_type,
        entity_data=request.entity_data,
        framework=framework
    )

    assessment = compliance_engine.get_compliance_assessment(assessment_id)

    return {
        "success": True,
        "assessment_id": assessment_id,
        "assessment": {
            "entity_id": assessment.entity_id,
            "entity_type": assessment.entity_type,
            "framework": assessment.framework.value,
            "overall_status": assessment.overall_status.value,
            "score": assessment.score,
            "violations_count": len(assessment.violations),
            "assessment_date": assessment.assessment_date.isoformat(),
            "next_assessment_due": assessment.next_assessment_due.isoformat() if assessment.next_assessment_due else None
        }
    }

@router.get("/compliance/violations",
            summary="Get Compliance Violations",
            description="Get compliance violations with optional filtering")
async def get_compliance_violations(
    entity_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Get compliance violations"""
    compliance_engine = get_compliance_engine()

    severity_enum = None
    if severity:
        try:
            severity_enum = ViolationSeverity(severity)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid severity")

    violations = compliance_engine.get_violations(entity_id, severity_enum)

    return {
        "success": True,
        "violations": [
            {
                "violation_id": v.violation_id,
                "rule_id": v.rule_id,
                "entity_id": v.entity_id,
                "entity_type": v.entity_type,
                "severity": v.severity.value,
                "violation_date": v.violation_date.isoformat(),
                "description": v.description,
                "status": v.status,
                "assigned_to": v.assigned_to,
                "resolved_at": v.resolved_at.isoformat() if v.resolved_at else None
            }
            for v in violations
        ],
        "count": len(violations)
    }

@router.post("/compliance/monitoring/start",
             summary="Start Compliance Monitoring",
             description="Start real-time compliance monitoring")
async def start_compliance_monitoring() -> Dict[str, Any]:
    """Start compliance monitoring"""
    compliance_engine = get_compliance_engine()

    await compliance_engine.start_compliance_monitoring()

    return {
        "success": True,
        "message": "Compliance monitoring started"
    }

@router.get("/compliance/stats",
            summary="Compliance Statistics",
            description="Get compliance engine statistics")
async def get_compliance_stats() -> Dict[str, Any]:
    """Get compliance statistics"""
    compliance_engine = get_compliance_engine()
    stats = compliance_engine.get_compliance_stats()

    return {
        "success": True,
        "statistics": stats
    }

# =============================================================================
# RISK ASSESSMENT ENDPOINTS
# =============================================================================

@router.post("/risk/models",
             summary="Create Risk Model",
             description="Create a new risk assessment model")
async def create_risk_model(request: RiskModelRequest) -> Dict[str, Any]:
    """Create risk model"""
    risk_assessment = get_risk_assessment()

    try:
        category = RiskCategory(request.category)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid risk category")

    model_id = risk_assessment.risk_engine.create_risk_model(
        name=request.name,
        description=request.description,
        category=category
    )

    return {
        "success": True,
        "model_id": model_id,
        "message": "Risk model created successfully"
    }

@router.post("/risk/factors",
             summary="Add Risk Factor",
             description="Add a risk factor to a model")
async def add_risk_factor(request: RiskFactorRequest) -> Dict[str, Any]:
    """Add risk factor"""
    risk_assessment = get_risk_assessment()

    try:
        category = RiskCategory(request.category)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid risk category")

    success = risk_assessment.risk_engine.add_risk_factor(
        model_id=request.model_id,
        name=request.name,
        description=request.description,
        category=category,
        weight=request.weight
    )

    return {
        "success": success,
        "message": "Risk factor added successfully" if success else "Failed to add risk factor"
    }

@router.post("/risk/assess",
             summary="Perform Risk Assessment",
             description="Perform comprehensive risk assessment")
async def perform_risk_assessment(request: RiskAssessmentRequest) -> Dict[str, Any]:
    """Perform risk assessment"""
    risk_assessment = get_risk_assessment()

    assessment_ids = await risk_assessment.perform_risk_assessment(
        entity_id=request.entity_id,
        entity_type=request.entity_type,
        entity_data=request.entity_data,
        model_ids=request.model_ids
    )

    assessments = []
    for assessment_id in assessment_ids:
        assessment = risk_assessment.risk_engine.get_risk_assessment(assessment_id)
        if assessment:
            assessments.append({
                "assessment_id": assessment_id,
                "risk_category": assessment.risk_category.value,
                "risk_level": assessment.risk_level.name,
                "risk_score": assessment.risk_score,
                "probability": assessment.probability,
                "impact": assessment.impact,
                "assessment_date": assessment.assessment_date.isoformat(),
                "recommendations": assessment.recommendations
            })

    return {
        "success": True,
        "assessment_ids": assessment_ids,
        "assessments": assessments,
        "count": len(assessments)
    }

@router.post("/risk/mitigation",
             summary="Create Mitigation Plan",
             description="Create risk mitigation plan")
async def create_mitigation_plan(request: MitigationPlanRequest) -> Dict[str, Any]:
    """Create mitigation plan"""
    risk_assessment = get_risk_assessment()

    try:
        strategy = MitigationStrategy(request.strategy)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mitigation strategy")

    plan_id = risk_assessment.risk_engine.create_mitigation_plan(
        assessment_id=request.assessment_id,
        strategy=strategy,
        actions=request.actions,
        responsible_party=request.responsible_party
    )

    return {
        "success": True,
        "plan_id": plan_id,
        "message": "Mitigation plan created successfully"
    }

@router.get("/risk/models",
            summary="List Risk Models",
            description="Get all risk models")
async def list_risk_models() -> Dict[str, Any]:
    """List risk models"""
    risk_assessment = get_risk_assessment()
    models = risk_assessment.risk_engine.get_risk_models()

    return {
        "success": True,
        "models": [
            {
                "model_id": m.model_id,
                "name": m.name,
                "description": m.description,
                "category": m.category.value,
                "factors_count": len(m.factors),
                "scenarios_count": len(m.scenarios),
                "version": m.version,
                "created_at": m.created_at.isoformat()
            }
            for m in models
        ],
        "count": len(models)
    }

@router.get("/risk/dashboard",
            summary="Risk Dashboard",
            description="Get risk assessment dashboard data")
async def get_risk_dashboard() -> Dict[str, Any]:
    """Get risk dashboard"""
    risk_assessment = get_risk_assessment()
    dashboard_data = risk_assessment.get_risk_dashboard_data()

    return {
        "success": True,
        "dashboard": dashboard_data
    }

@router.get("/risk/stats",
            summary="Risk Statistics",
            description="Get risk assessment statistics")
async def get_risk_stats() -> Dict[str, Any]:
    """Get risk statistics"""
    risk_assessment = get_risk_assessment()
    stats = risk_assessment.get_risk_stats()

    return {
        "success": True,
        "statistics": stats
    }

# =============================================================================
# AUDIT & GOVERNANCE ENDPOINTS
# =============================================================================

@router.post("/audit/events",
             summary="Log Audit Event",
             description="Log an audit event")
async def log_audit_event(request: AuditEventRequest) -> Dict[str, Any]:
    """Log audit event"""
    audit_governance = get_audit_governance()

    try:
        event_type = AuditEventType(request.event_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event type")

    event_id = await audit_governance.log_user_action(
        user_id=request.user_id,
        session_id=request.session_id,
        action=request.action,
        description=request.description,
        entity_id=request.entity_id,
        entity_type=request.entity_type,
        metadata=request.metadata
    )

    return {
        "success": True,
        "event_id": event_id,
        "message": "Audit event logged successfully"
    }

@router.get("/audit/trail/{entity_id}",
            summary="Get Audit Trail",
            description="Get audit trail for entity")
async def get_audit_trail(entity_id: str, entity_type: str = Query(...)) -> Dict[str, Any]:
    """Get audit trail"""
    audit_governance = get_audit_governance()

    trail = audit_governance.audit_trail_manager.get_audit_trail(entity_id, entity_type)

    if not trail:
        return {
            "success": True,
            "audit_trail": None,
            "message": "No audit trail found for entity"
        }

    return {
        "success": True,
        "audit_trail": {
            "trail_id": trail.trail_id,
            "entity_id": trail.entity_id,
            "entity_type": trail.entity_type,
            "events_count": len(trail.events),
            "created_at": trail.created_at.isoformat(),
            "last_updated": trail.last_updated.isoformat(),
            "integrity_hash": trail.integrity_hash,
            "events": [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type.value,
                    "timestamp": e.timestamp.isoformat(),
                    "user_id": e.user_id,
                    "action": e.action,
                    "description": e.description
                }
                for e in trail.events[-50:]  # Last 50 events
            ]
        }
    }

@router.post("/audit/evidence",
             summary="Preserve Evidence",
             description="Collect and preserve digital evidence")
async def preserve_evidence(request: EvidenceRequest) -> Dict[str, Any]:
    """Preserve digital evidence"""
    audit_governance = get_audit_governance()

    try:
        evidence_type = EvidenceType(request.evidence_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid evidence type")

    evidence_id = await audit_governance.preserve_evidence(
        evidence_type=evidence_type,
        title=request.title,
        description=request.description,
        collector_id=request.collector_id
    )

    return {
        "success": True,
        "evidence_id": evidence_id,
        "message": "Evidence preserved successfully"
    }

@router.post("/governance/policies",
             summary="Create Governance Policy",
             description="Create a governance policy")
async def create_governance_policy(request: GovernancePolicyRequest) -> Dict[str, Any]:
    """Create governance policy"""
    audit_governance = get_audit_governance()

    try:
        framework_type = GovernanceFrameworkType(request.framework_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid framework type")

    policy_id = audit_governance.governance_framework.create_governance_policy(
        name=request.name,
        description=request.description,
        framework_type=framework_type,
        policy_content=request.policy_content
    )

    return {
        "success": True,
        "policy_id": policy_id,
        "message": "Governance policy created successfully"
    }

@router.get("/governance/dashboard",
            summary="Governance Dashboard",
            description="Get governance dashboard data")
async def get_governance_dashboard() -> Dict[str, Any]:
    """Get governance dashboard"""
    audit_governance = get_audit_governance()
    dashboard_data = audit_governance.get_governance_dashboard()

    return {
        "success": True,
        "dashboard": dashboard_data
    }

@router.get("/audit/summary/{entity_id}",
            summary="Audit Summary",
            description="Get audit summary for entity")
async def get_audit_summary(entity_id: str, entity_type: str = Query(...)) -> Dict[str, Any]:
    """Get audit summary"""
    audit_governance = get_audit_governance()
    summary = audit_governance.get_audit_summary(entity_id, entity_type)

    return {
        "success": True,
        "audit_summary": summary
    }

@router.get("/audit/stats",
            summary="Audit Statistics",
            description="Get audit and governance statistics")
async def get_audit_stats() -> Dict[str, Any]:
    """Get audit statistics"""
    audit_governance = get_audit_governance()
    stats = audit_governance.get_audit_governance_stats()

    return {
        "success": True,
        "statistics": stats
    }

# =============================================================================
# REGULATORY INTELLIGENCE ENDPOINTS
# =============================================================================

@router.post("/regulatory/monitoring/start",
             summary="Start Regulatory Monitoring",
             description="Start regulatory change monitoring")
async def start_regulatory_monitoring() -> Dict[str, Any]:
    """Start regulatory monitoring"""
    regulatory_intelligence = get_regulatory_intelligence()

    await regulatory_intelligence.start_regulatory_monitoring()

    return {
        "success": True,
        "message": "Regulatory monitoring started"
    }

@router.post("/regulatory/alerts/subscribe",
             summary="Subscribe to Regulatory Alerts",
             description="Subscribe to regulatory alerts")
async def subscribe_regulatory_alerts(request: RegulatoryAlertSubscriptionRequest) -> Dict[str, Any]:
    """Subscribe to regulatory alerts"""
    regulatory_intelligence = get_regulatory_intelligence()

    try:
        domains = [RegulatoryDomain(domain) for domain in request.domains]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid regulatory domain")

    regulatory_intelligence.subscribe_to_regulatory_alerts(
        user_id=request.user_id,
        domains=domains
    )

    return {
        "success": True,
        "message": f"Subscribed to alerts for {len(domains)} domains"
    }

@router.post("/regulatory/reports",
             summary="Generate Compliance Report",
             description="Generate regulatory compliance report")
async def generate_compliance_report(request: ComplianceReportRequest) -> Dict[str, Any]:
    """Generate compliance report"""
    regulatory_intelligence = get_regulatory_intelligence()

    try:
        report_type = ComplianceReportType(request.report_type)
        jurisdiction = Jurisdiction(request.jurisdiction)
        domain = RegulatoryDomain(request.domain)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid enum values")

    report_id = await regulatory_intelligence.generate_compliance_report(
        report_type=report_type,
        period_start=request.period_start,
        period_end=request.period_end,
        jurisdiction=jurisdiction,
        domain=domain
    )

    return {
        "success": True,
        "report_id": report_id,
        "message": "Compliance report generated successfully"
    }

@router.get("/regulatory/calendar",
            summary="Regulatory Calendar",
            description="Get regulatory compliance calendar")
async def get_regulatory_calendar(
    jurisdiction: str = Query(...),
    days_ahead: int = Query(90)
) -> Dict[str, Any]:
    """Get regulatory calendar"""
    regulatory_intelligence = get_regulatory_intelligence()

    try:
        jurisdiction_enum = Jurisdiction(jurisdiction)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid jurisdiction")

    calendar_data = regulatory_intelligence.get_regulatory_calendar(
        jurisdiction=jurisdiction_enum,
        days_ahead=days_ahead
    )

    return {
        "success": True,
        "regulatory_calendar": calendar_data
    }

@router.get("/regulatory/dashboard",
            summary="Regulatory Dashboard",
            description="Get regulatory intelligence dashboard")
async def get_regulatory_dashboard() -> Dict[str, Any]:
    """Get regulatory dashboard"""
    regulatory_intelligence = get_regulatory_intelligence()
    dashboard_data = regulatory_intelligence.get_regulatory_dashboard()

    return {
        "success": True,
        "dashboard": dashboard_data
    }

@router.get("/regulatory/stats",
            summary="Regulatory Intelligence Statistics",
            description="Get regulatory intelligence statistics")
async def get_regulatory_stats() -> Dict[str, Any]:
    """Get regulatory intelligence statistics"""
    regulatory_intelligence = get_regulatory_intelligence()
    stats = regulatory_intelligence.get_regulatory_intelligence_stats()

    return {
        "success": True,
        "statistics": stats
    }

# =============================================================================
# COMPREHENSIVE COMPLIANCE PLATFORM ENDPOINTS
# =============================================================================

@router.get("/compliance/platform/health",
            summary="Compliance Platform Health",
            description="Get overall compliance platform health")
async def get_compliance_platform_health() -> Dict[str, Any]:
    """Get compliance platform health"""
    compliance_engine = get_compliance_engine()
    risk_assessment = get_risk_assessment()
    audit_governance = get_audit_governance()
    regulatory_intelligence = get_regulatory_intelligence()

    return {
        "success": True,
        "platform_health": {
            "compliance_engine": {
                "status": "operational",
                "statistics": compliance_engine.get_compliance_stats()
            },
            "risk_assessment": {
                "status": "operational",
                "statistics": risk_assessment.get_risk_stats()
            },
            "audit_governance": {
                "status": "operational",
                "statistics": audit_governance.get_audit_governance_stats()
            },
            "regulatory_intelligence": {
                "status": "operational",
                "statistics": regulatory_intelligence.get_regulatory_intelligence_stats()
            }
        },
        "overall_status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/compliance/platform/dashboard",
            summary="Compliance Platform Dashboard",
            description="Get comprehensive compliance platform dashboard")
async def get_compliance_platform_dashboard() -> Dict[str, Any]:
    """Get compliance platform dashboard"""
    compliance_engine = get_compliance_engine()
    risk_assessment = get_risk_assessment()
    audit_governance = get_audit_governance()
    regulatory_intelligence = get_regulatory_intelligence()

    # Get dashboard data from all components
    compliance_stats = compliance_engine.get_compliance_stats()
    risk_dashboard = risk_assessment.get_risk_dashboard_data()
    governance_dashboard = audit_governance.get_governance_dashboard()
    regulatory_dashboard = regulatory_intelligence.get_regulatory_dashboard()

    return {
        "success": True,
        "compliance_dashboard": {
            "compliance_overview": {
                "frameworks_active": compliance_stats.get("frameworks_active", 0),
                "policies_created": compliance_stats.get("policies_created", 0),
                "violations_total": compliance_stats.get("violations_total", 0),
                "open_violations": compliance_stats.get("open_violations", 0)
            },
            "risk_overview": {
                "total_assessments": risk_dashboard.get("total_assessments", 0),
                "high_risk_count": risk_dashboard.get("high_risk_count", 0),
                "risk_distribution": risk_dashboard.get("risk_level_distribution", {})
            },
            "governance_overview": {
                "total_policies": governance_dashboard.get("total_policies", 0),
                "active_roles": governance_dashboard.get("active_roles", 0),
                "audit_trails_active": governance_dashboard.get("audit_trails_active", 0)
            },
            "regulatory_overview": {
                "recent_documents": regulatory_dashboard.get("recent_regulatory_documents", 0),
                "obligations_due": regulatory_dashboard.get("obligations_due_30_days", 0),
                "compliance_obligations": regulatory_dashboard.get("total_compliance_obligations", 0)
            }
        },
        "summary": {
            "total_frameworks": compliance_stats.get("frameworks_active", 0),
            "total_assessments": risk_dashboard.get("total_assessments", 0),
            "total_audit_events": compliance_stats.get("events_logged", 0),
            "total_reports": regulatory_dashboard.get("reports_generated", 0)
        }
    }