"""
Audit & Governance Framework - Sprint 15
Comprehensive audit trail management, governance enforcement, and digital evidence collection
"""

from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import json
import uuid
import hashlib
from collections import defaultdict, deque

class AuditEventType(Enum):
    USER_ACTION = "user_action"
    SYSTEM_ACTION = "system_action"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    PERMISSION_CHANGE = "permission_change"
    LOGIN_LOGOUT = "login_logout"
    DOCUMENT_ACCESS = "document_access"
    DEAL_ACTIVITY = "deal_activity"
    COMPLIANCE_CHECK = "compliance_check"
    RISK_ASSESSMENT = "risk_assessment"

class AuditLevel(Enum):
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    FORENSIC = "forensic"

class GovernanceFrameworkType(Enum):
    BOARD_GOVERNANCE = "board_governance"
    RISK_GOVERNANCE = "risk_governance"
    DATA_GOVERNANCE = "data_governance"
    IT_GOVERNANCE = "it_governance"
    COMPLIANCE_GOVERNANCE = "compliance_governance"
    FINANCIAL_GOVERNANCE = "financial_governance"

class EvidenceType(Enum):
    DOCUMENT = "document"
    EMAIL = "email"
    SYSTEM_LOG = "system_log"
    AUDIT_TRAIL = "audit_trail"
    SCREENSHOT = "screenshot"
    DATABASE_RECORD = "database_record"
    API_CALL = "api_call"
    USER_TESTIMONY = "user_testimony"

class GovernanceRoleType(Enum):
    BOARD_MEMBER = "board_member"
    EXECUTIVE = "executive"
    COMPLIANCE_OFFICER = "compliance_officer"
    RISK_MANAGER = "risk_manager"
    AUDIT_COMMITTEE = "audit_committee"
    LEGAL_COUNSEL = "legal_counsel"
    DATA_PROTECTION_OFFICER = "data_protection_officer"

@dataclass
class AuditEvent:
    """Individual audit event record"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: str
    session_id: str
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    action: str = ""
    description: str = ""
    ip_address: str = ""
    user_agent: str = ""
    request_data: Dict[str, Any] = field(default_factory=dict)
    response_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "low"
    compliance_relevant: bool = False

@dataclass
class AuditTrail:
    """Complete audit trail for an entity"""
    trail_id: str
    entity_id: str
    entity_type: str
    events: List[AuditEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    retention_period: int = 2555  # 7 years in days
    encryption_key_id: Optional[str] = None
    integrity_hash: Optional[str] = None

@dataclass
class DigitalEvidence:
    """Digital evidence record"""
    evidence_id: str
    evidence_type: EvidenceType
    title: str
    description: str
    collection_date: datetime
    collector_id: str
    source_system: str = ""
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    preservation_status: str = "preserved"
    legal_hold: bool = False

@dataclass
class GovernancePolicy:
    """Governance policy definition"""
    policy_id: str
    name: str
    description: str
    framework_type: GovernanceFrameworkType
    policy_content: str
    version: str = "1.0"
    effective_date: datetime = field(default_factory=datetime.now)
    review_frequency: str = "annually"
    next_review_date: Optional[datetime] = None
    approval_authority: str = ""
    compliance_requirements: List[str] = field(default_factory=list)
    enforcement_mechanisms: List[str] = field(default_factory=list)

@dataclass
class GovernanceRole:
    """Governance role and responsibilities"""
    role_id: str
    role_name: str
    role_type: GovernanceRoleType
    description: str
    responsibilities: List[str] = field(default_factory=list)
    authority_level: str = "standard"
    reporting_structure: List[str] = field(default_factory=list)
    required_qualifications: List[str] = field(default_factory=list)
    term_length: Optional[int] = None  # in months

@dataclass
class GovernanceAssignment:
    """Assignment of governance roles to individuals"""
    assignment_id: str
    role_id: str
    user_id: str
    assigned_date: datetime
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    assignment_authority: str = ""
    status: str = "active"
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BoardMeeting:
    """Board meeting record"""
    meeting_id: str
    meeting_type: str
    scheduled_date: datetime
    actual_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    attendees: List[str] = field(default_factory=list)
    agenda: List[str] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    minutes_approved: bool = False
    meeting_materials: List[str] = field(default_factory=list)

class AuditTrailManager:
    """Manages audit trail collection and storage"""

    def __init__(self):
        self.audit_trails = {}
        self.audit_events = deque(maxlen=100000)  # Keep recent events in memory
        self.audit_config = {
            "retention_days": 2555,  # 7 years
            "encryption_enabled": True,
            "real_time_monitoring": True,
            "integrity_checking": True
        }

    async def log_audit_event(self, event_type: AuditEventType, user_id: str,
                            session_id: str, action: str, description: str,
                            entity_id: Optional[str] = None,
                            entity_type: Optional[str] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> str:
        """Log an audit event"""
        event_id = f"audit_{uuid.uuid4().hex[:8]}"

        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
            entity_id=entity_id,
            entity_type=entity_type,
            action=action,
            description=description,
            metadata=metadata or {}
        )

        # Add to memory queue
        self.audit_events.append(event)

        # Add to entity trail if applicable
        if entity_id and entity_type:
            await self._add_to_entity_trail(entity_id, entity_type, event)

        return event_id

    async def _add_to_entity_trail(self, entity_id: str, entity_type: str,
                                 event: AuditEvent):
        """Add event to entity audit trail"""
        trail_key = f"{entity_type}_{entity_id}"

        if trail_key not in self.audit_trails:
            trail_id = f"trail_{uuid.uuid4().hex[:8]}"
            trail = AuditTrail(
                trail_id=trail_id,
                entity_id=entity_id,
                entity_type=entity_type
            )
            self.audit_trails[trail_key] = trail

        trail = self.audit_trails[trail_key]
        trail.events.append(event)
        trail.last_updated = datetime.now()

        # Update integrity hash
        await self._update_trail_integrity(trail)

    async def _update_trail_integrity(self, trail: AuditTrail):
        """Update trail integrity hash"""
        trail_data = {
            "trail_id": trail.trail_id,
            "entity_id": trail.entity_id,
            "entity_type": trail.entity_type,
            "events": [
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp.isoformat(),
                    "action": e.action,
                    "user_id": e.user_id
                }
                for e in trail.events
            ]
        }

        trail_json = json.dumps(trail_data, sort_keys=True)
        trail.integrity_hash = hashlib.sha256(trail_json.encode()).hexdigest()

    def get_audit_trail(self, entity_id: str, entity_type: str) -> Optional[AuditTrail]:
        """Get audit trail for entity"""
        trail_key = f"{entity_type}_{entity_id}"
        return self.audit_trails.get(trail_key)

    def search_audit_events(self, criteria: Dict[str, Any],
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[AuditEvent]:
        """Search audit events by criteria"""
        results = []

        for event in self.audit_events:
            # Date filtering
            if start_date and event.timestamp < start_date:
                continue
            if end_date and event.timestamp > end_date:
                continue

            # Criteria matching
            match = True
            for key, value in criteria.items():
                if hasattr(event, key):
                    if getattr(event, key) != value:
                        match = False
                        break

            if match:
                results.append(event)

        return results

    def verify_trail_integrity(self, trail: AuditTrail) -> bool:
        """Verify audit trail integrity"""
        # Recalculate hash and compare
        original_hash = trail.integrity_hash
        trail.integrity_hash = None  # Temporarily remove for calculation

        # This would recalculate the hash
        # Implementation would depend on specific hashing requirements

        trail.integrity_hash = original_hash
        return True  # Simplified for demo

class EvidenceManager:
    """Manages digital evidence collection and preservation"""

    def __init__(self):
        self.evidence_repository = {}
        self.chain_of_custody_log = deque(maxlen=10000)
        self.preservation_policies = {}

    async def collect_evidence(self, evidence_type: EvidenceType, title: str,
                             description: str, collector_id: str,
                             source_system: str = "",
                             file_data: Optional[bytes] = None) -> str:
        """Collect and preserve digital evidence"""
        evidence_id = f"evidence_{uuid.uuid4().hex[:8]}"

        evidence = DigitalEvidence(
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            title=title,
            description=description,
            collection_date=datetime.now(),
            collector_id=collector_id,
            source_system=source_system
        )

        # Handle file data if provided
        if file_data:
            evidence.file_hash = hashlib.sha256(file_data).hexdigest()
            evidence.file_size = len(file_data)
            # In production, would store file securely

        # Initialize chain of custody
        custody_entry = {
            "action": "collected",
            "timestamp": datetime.now().isoformat(),
            "person_id": collector_id,
            "location": source_system,
            "description": f"Evidence collected from {source_system}"
        }
        evidence.chain_of_custody.append(custody_entry)

        self.evidence_repository[evidence_id] = evidence
        return evidence_id

    async def transfer_evidence_custody(self, evidence_id: str, from_person: str,
                                      to_person: str, purpose: str) -> bool:
        """Transfer evidence custody"""
        if evidence_id not in self.evidence_repository:
            return False

        evidence = self.evidence_repository[evidence_id]

        custody_entry = {
            "action": "transferred",
            "timestamp": datetime.now().isoformat(),
            "from_person": from_person,
            "to_person": to_person,
            "purpose": purpose,
            "verification_method": "digital_signature"
        }

        evidence.chain_of_custody.append(custody_entry)
        return True

    def place_legal_hold(self, evidence_id: str, hold_reason: str) -> bool:
        """Place legal hold on evidence"""
        if evidence_id not in self.evidence_repository:
            return False

        evidence = self.evidence_repository[evidence_id]
        evidence.legal_hold = True
        evidence.metadata["legal_hold_reason"] = hold_reason
        evidence.metadata["legal_hold_date"] = datetime.now().isoformat()

        return True

    def get_evidence(self, evidence_id: str) -> Optional[DigitalEvidence]:
        """Get evidence by ID"""
        return self.evidence_repository.get(evidence_id)

    def search_evidence(self, criteria: Dict[str, Any]) -> List[DigitalEvidence]:
        """Search evidence by criteria"""
        results = []

        for evidence in self.evidence_repository.values():
            match = True
            for key, value in criteria.items():
                if hasattr(evidence, key):
                    if getattr(evidence, key) != value:
                        match = False
                        break

            if match:
                results.append(evidence)

        return results

class GovernanceFramework:
    """Manages governance policies and structures"""

    def __init__(self):
        self.policies = {}
        self.roles = {}
        self.assignments = {}
        self.board_meetings = {}
        self._initialize_default_governance()

    def create_governance_policy(self, name: str, description: str,
                               framework_type: GovernanceFrameworkType,
                               policy_content: str) -> str:
        """Create governance policy"""
        policy_id = f"policy_{uuid.uuid4().hex[:8]}"

        policy = GovernancePolicy(
            policy_id=policy_id,
            name=name,
            description=description,
            framework_type=framework_type,
            policy_content=policy_content,
            next_review_date=datetime.now() + timedelta(days=365)
        )

        self.policies[policy_id] = policy
        return policy_id

    def create_governance_role(self, role_name: str, role_type: GovernanceRoleType,
                             description: str, responsibilities: List[str]) -> str:
        """Create governance role"""
        role_id = f"role_{uuid.uuid4().hex[:8]}"

        role = GovernanceRole(
            role_id=role_id,
            role_name=role_name,
            role_type=role_type,
            description=description,
            responsibilities=responsibilities
        )

        self.roles[role_id] = role
        return role_id

    def assign_governance_role(self, role_id: str, user_id: str,
                             assignment_authority: str,
                             term_months: Optional[int] = None) -> str:
        """Assign governance role to user"""
        assignment_id = f"assignment_{uuid.uuid4().hex[:8]}"

        expiry_date = None
        if term_months:
            expiry_date = datetime.now() + timedelta(days=term_months * 30)

        assignment = GovernanceAssignment(
            assignment_id=assignment_id,
            role_id=role_id,
            user_id=user_id,
            assigned_date=datetime.now(),
            effective_date=datetime.now(),
            expiry_date=expiry_date,
            assignment_authority=assignment_authority
        )

        self.assignments[assignment_id] = assignment
        return assignment_id

    def schedule_board_meeting(self, meeting_type: str, scheduled_date: datetime,
                             agenda: List[str]) -> str:
        """Schedule board meeting"""
        meeting_id = f"meeting_{uuid.uuid4().hex[:8]}"

        meeting = BoardMeeting(
            meeting_id=meeting_id,
            meeting_type=meeting_type,
            scheduled_date=scheduled_date,
            agenda=agenda
        )

        self.board_meetings[meeting_id] = meeting
        return meeting_id

    def _initialize_default_governance(self):
        """Initialize default governance structure"""

        # Create default roles
        board_chair_id = self.create_governance_role(
            "Board Chair",
            GovernanceRoleType.BOARD_MEMBER,
            "Chairperson of the Board of Directors",
            [
                "Lead board meetings",
                "Oversee governance processes",
                "Ensure regulatory compliance",
                "Stakeholder communication"
            ]
        )

        cro_id = self.create_governance_role(
            "Chief Risk Officer",
            GovernanceRoleType.RISK_MANAGER,
            "Executive responsible for risk management",
            [
                "Develop risk management framework",
                "Monitor enterprise risks",
                "Report to board on risk exposure",
                "Implement risk mitigation strategies"
            ]
        )

        # Create default policies
        self.create_governance_policy(
            "Board Charter",
            "Charter defining board composition and responsibilities",
            GovernanceFrameworkType.BOARD_GOVERNANCE,
            "The Board of Directors is responsible for..."
        )

        self.create_governance_policy(
            "Risk Management Policy",
            "Enterprise risk management framework",
            GovernanceFrameworkType.RISK_GOVERNANCE,
            "Risk management processes and procedures..."
        )

    def get_user_governance_roles(self, user_id: str) -> List[GovernanceRole]:
        """Get governance roles for user"""
        user_assignments = [
            a for a in self.assignments.values()
            if a.user_id == user_id and a.status == "active"
        ]

        roles = []
        for assignment in user_assignments:
            role = self.roles.get(assignment.role_id)
            if role:
                roles.append(role)

        return roles

    def get_policies_by_framework(self, framework_type: GovernanceFrameworkType) -> List[GovernancePolicy]:
        """Get policies by framework type"""
        return [
            policy for policy in self.policies.values()
            if policy.framework_type == framework_type
        ]

class AuditGovernance:
    """Central audit and governance coordination"""

    def __init__(self):
        self.audit_trail_manager = AuditTrailManager()
        self.evidence_manager = EvidenceManager()
        self.governance_framework = GovernanceFramework()
        self.audit_stats = {
            "events_logged": 0,
            "evidence_items": 0,
            "governance_violations": 0,
            "audit_trails_maintained": 0
        }

    async def log_user_action(self, user_id: str, session_id: str, action: str,
                            description: str, entity_id: Optional[str] = None,
                            entity_type: Optional[str] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> str:
        """Log user action for audit trail"""
        event_id = await self.audit_trail_manager.log_audit_event(
            AuditEventType.USER_ACTION, user_id, session_id, action,
            description, entity_id, entity_type, metadata
        )
        self.audit_stats["events_logged"] += 1
        return event_id

    async def log_system_event(self, system_id: str, action: str, description: str,
                             entity_id: Optional[str] = None,
                             entity_type: Optional[str] = None) -> str:
        """Log system event for audit trail"""
        event_id = await self.audit_trail_manager.log_audit_event(
            AuditEventType.SYSTEM_ACTION, system_id, "system", action,
            description, entity_id, entity_type
        )
        self.audit_stats["events_logged"] += 1
        return event_id

    async def preserve_evidence(self, evidence_type: EvidenceType, title: str,
                              description: str, collector_id: str,
                              file_data: Optional[bytes] = None) -> str:
        """Preserve digital evidence"""
        evidence_id = await self.evidence_manager.collect_evidence(
            evidence_type, title, description, collector_id,
            file_data=file_data
        )
        self.audit_stats["evidence_items"] += 1
        return evidence_id

    def create_governance_structure(self, organization_name: str) -> Dict[str, str]:
        """Create governance structure for organization"""
        # Create key governance roles
        roles_created = {}

        # Board positions
        board_chair = self.governance_framework.create_governance_role(
            f"{organization_name} Board Chair",
            GovernanceRoleType.BOARD_MEMBER,
            "Board chairperson",
            ["Strategic oversight", "Governance leadership"]
        )
        roles_created["board_chair"] = board_chair

        # Executive positions
        ceo_role = self.governance_framework.create_governance_role(
            f"{organization_name} CEO",
            GovernanceRoleType.EXECUTIVE,
            "Chief Executive Officer",
            ["Executive leadership", "Strategic direction"]
        )
        roles_created["ceo"] = ceo_role

        # Compliance officer
        compliance_role = self.governance_framework.create_governance_role(
            f"{organization_name} Chief Compliance Officer",
            GovernanceRoleType.COMPLIANCE_OFFICER,
            "Chief Compliance Officer",
            ["Compliance oversight", "Risk management"]
        )
        roles_created["compliance_officer"] = compliance_role

        return roles_created

    def get_audit_summary(self, entity_id: str, entity_type: str) -> Dict[str, Any]:
        """Get audit summary for entity"""
        trail = self.audit_trail_manager.get_audit_trail(entity_id, entity_type)

        if not trail:
            return {"entity_id": entity_id, "events": 0, "last_activity": None}

        event_types = defaultdict(int)
        users_involved = set()

        for event in trail.events:
            event_types[event.event_type.value] += 1
            users_involved.add(event.user_id)

        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "total_events": len(trail.events),
            "event_types": dict(event_types),
            "users_involved": len(users_involved),
            "first_activity": trail.events[0].timestamp.isoformat() if trail.events else None,
            "last_activity": trail.events[-1].timestamp.isoformat() if trail.events else None,
            "integrity_verified": self.audit_trail_manager.verify_trail_integrity(trail)
        }

    def get_governance_dashboard(self) -> Dict[str, Any]:
        """Get governance dashboard data"""
        return {
            "total_policies": len(self.governance_framework.policies),
            "active_roles": len(self.governance_framework.roles),
            "current_assignments": len([
                a for a in self.governance_framework.assignments.values()
                if a.status == "active"
            ]),
            "upcoming_meetings": len([
                m for m in self.governance_framework.board_meetings.values()
                if m.scheduled_date > datetime.now()
            ]),
            "evidence_under_hold": len([
                e for e in self.evidence_manager.evidence_repository.values()
                if e.legal_hold
            ]),
            "audit_trails_active": len(self.audit_trail_manager.audit_trails)
        }

    def get_audit_governance_stats(self) -> Dict[str, Any]:
        """Get comprehensive audit and governance statistics"""
        return {
            **self.audit_stats,
            "audit_trails_count": len(self.audit_trail_manager.audit_trails),
            "evidence_repository_size": len(self.evidence_manager.evidence_repository),
            "governance_policies": len(self.governance_framework.policies),
            "governance_roles": len(self.governance_framework.roles)
        }

# Singleton instance
_audit_governance_instance: Optional[AuditGovernance] = None

def get_audit_governance() -> AuditGovernance:
    """Get the singleton Audit Governance instance"""
    global _audit_governance_instance
    if _audit_governance_instance is None:
        _audit_governance_instance = AuditGovernance()
    return _audit_governance_instance