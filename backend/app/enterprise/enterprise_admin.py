"""
Enterprise Administration Service
Advanced user management, compliance, and security features
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import hashlib
from abc import ABC, abstractmethod

class ComplianceFramework(str, Enum):
    """Supported compliance frameworks"""
    SOX = "sox"  # Sarbanes-Oxley
    GDPR = "gdpr"  # General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    ISO27001 = "iso27001"  # Information Security Management
    SOC2 = "soc2"  # Service Organization Control 2

class AuditEventType(str, Enum):
    """Types of audit events"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    DATA_ACCESSED = "data_accessed"
    DATA_MODIFIED = "data_modified"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    INTEGRATION_ADDED = "integration_added"
    INTEGRATION_REMOVED = "integration_removed"
    SECURITY_VIOLATION = "security_violation"
    COMPLIANCE_CHECK = "compliance_check"

class DataRetentionPolicy(str, Enum):
    """Data retention policy types"""
    DAYS_30 = "30_days"
    DAYS_90 = "90_days"
    MONTHS_6 = "6_months"
    YEAR_1 = "1_year"
    YEARS_3 = "3_years"
    YEARS_7 = "7_years"
    INDEFINITE = "indefinite"

class SecurityLevel(str, Enum):
    """Security access levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

@dataclass
class AuditTrail:
    """Audit trail entry for compliance tracking"""
    audit_id: str
    event_type: AuditEventType
    user_id: str
    organization_id: str
    resource_type: str
    resource_id: str
    action: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    timestamp: datetime
    compliance_tags: List[str] = None
    risk_level: str = "low"
    metadata: Dict[str, Any] = None
    
@dataclass
class CompliancePolicy:
    """Compliance policy configuration"""
    policy_id: str
    framework: ComplianceFramework
    organization_id: str
    name: str
    description: str
    requirements: List[Dict[str, Any]]
    controls: List[Dict[str, Any]]
    audit_frequency: str  # Cron expression
    retention_policy: DataRetentionPolicy
    notification_settings: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_audit: Optional[datetime] = None
    next_audit: Optional[datetime] = None
    
@dataclass
class SecurityConfiguration:
    """Enterprise security configuration"""
    config_id: str
    organization_id: str
    password_policy: Dict[str, Any]
    mfa_requirements: Dict[str, Any]
    session_management: Dict[str, Any]
    ip_restrictions: List[str]
    device_management: Dict[str, Any]
    access_controls: Dict[str, Any]
    encryption_settings: Dict[str, Any]
    audit_settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
@dataclass
class WhiteLabelConfig:
    """White-label branding configuration"""
    config_id: str
    organization_id: str
    brand_name: str
    logo_url: str
    favicon_url: str
    primary_color: str
    secondary_color: str
    custom_domain: str
    email_templates: Dict[str, str]
    legal_documents: Dict[str, str]
    feature_flags: Dict[str, bool]
    custom_css: str
    created_at: datetime
    updated_at: datetime
    
class ComplianceManager:
    """Manager for compliance policies and audit trails"""
    
    def __init__(self):
        self.policies: Dict[str, CompliancePolicy] = {}
        self.audit_trails: List[AuditTrail] = []
        self.compliance_reports: Dict[str, Dict[str, Any]] = {}
        
    def add_policy(self, policy: CompliancePolicy) -> bool:
        """Add a new compliance policy"""
        try:
            self.policies[policy.policy_id] = policy
            return True
        except Exception:
            return False
    
    def record_audit_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        organization_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        details: Dict[str, Any],
        ip_address: str = "unknown",
        user_agent: str = "unknown"
    ) -> str:
        """Record an audit event"""
        audit_id = f"audit_{int(datetime.now().timestamp())}_{len(self.audit_trails)}"
        
        # Determine compliance tags based on event type and details
        compliance_tags = self._determine_compliance_tags(event_type, details)
        
        # Assess risk level
        risk_level = self._assess_risk_level(event_type, details)
        
        audit_entry = AuditTrail(
            audit_id=audit_id,
            event_type=event_type,
            user_id=user_id,
            organization_id=organization_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(),
            compliance_tags=compliance_tags,
            risk_level=risk_level
        )
        
        self.audit_trails.append(audit_entry)
        
        # Keep only recent audit trails (last 100,000 entries)
        if len(self.audit_trails) > 100000:
            self.audit_trails = self.audit_trails[-100000:]
        
        return audit_id
    
    def _determine_compliance_tags(self, event_type: AuditEventType, details: Dict[str, Any]) -> List[str]:
        """Determine which compliance frameworks apply to this event"""
        tags = []
        
        # SOX requirements
        if event_type in [AuditEventType.DATA_MODIFIED, AuditEventType.DATA_DELETED, 
                          AuditEventType.SYSTEM_CONFIG_CHANGED]:
            tags.append(ComplianceFramework.SOX.value)
        
        # GDPR requirements
        if event_type in [AuditEventType.DATA_ACCESSED, AuditEventType.DATA_EXPORTED,
                          AuditEventType.USER_CREATED, AuditEventType.USER_DELETED]:
            tags.append(ComplianceFramework.GDPR.value)
        
        # Security-related events
        if event_type in [AuditEventType.USER_LOGIN, AuditEventType.SECURITY_VIOLATION,
                          AuditEventType.PERMISSION_GRANTED]:
            tags.append(ComplianceFramework.ISO27001.value)
        
        return tags
    
    def _assess_risk_level(self, event_type: AuditEventType, details: Dict[str, Any]) -> str:
        """Assess the risk level of an audit event"""
        high_risk_events = [
            AuditEventType.SECURITY_VIOLATION,
            AuditEventType.DATA_DELETED,
            AuditEventType.SYSTEM_CONFIG_CHANGED,
            AuditEventType.INTEGRATION_REMOVED
        ]
        
        medium_risk_events = [
            AuditEventType.DATA_MODIFIED,
            AuditEventType.DATA_EXPORTED,
            AuditEventType.PERMISSION_GRANTED,
            AuditEventType.ROLE_ASSIGNED
        ]
        
        if event_type in high_risk_events:
            return "high"
        elif event_type in medium_risk_events:
            return "medium"
        else:
            return "low"
    
    def get_audit_trail(
        self,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[AuditTrail]:
        """Get filtered audit trail"""
        filtered_trails = self.audit_trails
        
        if organization_id:
            filtered_trails = [t for t in filtered_trails if t.organization_id == organization_id]
        
        if user_id:
            filtered_trails = [t for t in filtered_trails if t.user_id == user_id]
        
        if event_type:
            filtered_trails = [t for t in filtered_trails if t.event_type == event_type]
        
        if start_date:
            filtered_trails = [t for t in filtered_trails if t.timestamp >= start_date]
        
        if end_date:
            filtered_trails = [t for t in filtered_trails if t.timestamp <= end_date]
        
        # Sort by timestamp, most recent first
        filtered_trails.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered_trails[:limit]
    
    def generate_compliance_report(
        self,
        organization_id: str,
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate a compliance report for a specific framework"""
        report_id = f"report_{framework.value}_{int(datetime.now().timestamp())}"
        
        # Get relevant audit trails
        relevant_trails = [
            trail for trail in self.audit_trails
            if trail.organization_id == organization_id and
               trail.timestamp >= start_date and
               trail.timestamp <= end_date and
               framework.value in (trail.compliance_tags or [])
        ]
        
        # Analyze the data
        total_events = len(relevant_trails)
        event_types = {}
        risk_levels = {"low": 0, "medium": 0, "high": 0}
        
        for trail in relevant_trails:
            event_type = trail.event_type.value
            event_types[event_type] = event_types.get(event_type, 0) + 1
            risk_levels[trail.risk_level] += 1
        
        # Generate compliance score (simplified)
        compliance_score = min(100, max(0, 100 - (risk_levels["high"] * 10) - (risk_levels["medium"] * 3)))
        
        report = {
            "report_id": report_id,
            "organization_id": organization_id,
            "framework": framework.value,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_events": total_events,
                "compliance_score": compliance_score,
                "risk_distribution": risk_levels,
                "event_types": event_types
            },
            "findings": self._generate_compliance_findings(framework, relevant_trails),
            "recommendations": self._generate_compliance_recommendations(framework, relevant_trails),
            "generated_at": datetime.now().isoformat()
        }
        
        self.compliance_reports[report_id] = report
        return report
    
    def _generate_compliance_findings(self, framework: ComplianceFramework, trails: List[AuditTrail]) -> List[str]:
        """Generate compliance findings based on audit trails"""
        findings = []
        
        high_risk_count = sum(1 for trail in trails if trail.risk_level == "high")
        if high_risk_count > 0:
            findings.append(f"{high_risk_count} high-risk events detected")
        
        security_violations = sum(1 for trail in trails if trail.event_type == AuditEventType.SECURITY_VIOLATION)
        if security_violations > 0:
            findings.append(f"{security_violations} security violations recorded")
        
        if framework == ComplianceFramework.GDPR:
            data_access_events = sum(1 for trail in trails if trail.event_type == AuditEventType.DATA_ACCESSED)
            if data_access_events > 100:
                findings.append(f"High volume of data access events ({data_access_events})")
        
        if not findings:
            findings.append("No significant compliance issues identified")
        
        return findings
    
    def _generate_compliance_recommendations(self, framework: ComplianceFramework, trails: List[AuditTrail]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if framework == ComplianceFramework.SOX:
            recommendations.extend([
                "Implement additional controls for financial data modifications",
                "Review system configuration change procedures",
                "Enhance segregation of duties for critical operations"
            ])
        
        elif framework == ComplianceFramework.GDPR:
            recommendations.extend([
                "Review data access patterns for compliance",
                "Implement data minimization practices",
                "Ensure proper consent management"
            ])
        
        elif framework == ComplianceFramework.ISO27001:
            recommendations.extend([
                "Regular security awareness training",
                "Implement continuous security monitoring",
                "Review and update security policies"
            ])
        
        return recommendations
    
    def get_compliance_summary(self, organization_id: str) -> Dict[str, Any]:
        """Get compliance summary for an organization"""
        org_trails = [t for t in self.audit_trails if t.organization_id == organization_id]
        
        # Last 30 days summary
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_trails = [t for t in org_trails if t.timestamp >= thirty_days_ago]
        
        risk_summary = {"low": 0, "medium": 0, "high": 0}
        for trail in recent_trails:
            risk_summary[trail.risk_level] += 1
        
        frameworks_coverage = {}
        for framework in ComplianceFramework:
            framework_trails = [
                t for t in recent_trails 
                if framework.value in (t.compliance_tags or [])
            ]
            frameworks_coverage[framework.value] = len(framework_trails)
        
        return {
            "organization_id": organization_id,
            "period": "last_30_days",
            "total_audit_events": len(recent_trails),
            "risk_summary": risk_summary,
            "frameworks_coverage": frameworks_coverage,
            "active_policies": len([p for p in self.policies.values() if p.organization_id == organization_id and p.is_active]),
            "last_updated": datetime.now().isoformat()
        }

class EnterpriseAdminService:
    """Central service for enterprise administration features"""
    
    def __init__(self):
        self.compliance_manager = ComplianceManager()
        self.security_configs: Dict[str, SecurityConfiguration] = {}
        self.whitelabel_configs: Dict[str, WhiteLabelConfig] = {}
        self.sso_configurations: Dict[str, Dict[str, Any]] = {}
        
    def create_security_config(self, config: SecurityConfiguration) -> bool:
        """Create or update security configuration"""
        try:
            self.security_configs[config.organization_id] = config
            
            # Record audit event
            self.compliance_manager.record_audit_event(
                event_type=AuditEventType.SYSTEM_CONFIG_CHANGED,
                user_id="system",
                organization_id=config.organization_id,
                resource_type="security_config",
                resource_id=config.config_id,
                action="create_or_update",
                details={"config_type": "security"}
            )
            
            return True
        except Exception:
            return False
    
    def create_whitelabel_config(self, config: WhiteLabelConfig) -> bool:
        """Create or update white-label configuration"""
        try:
            self.whitelabel_configs[config.organization_id] = config
            
            # Record audit event
            self.compliance_manager.record_audit_event(
                event_type=AuditEventType.SYSTEM_CONFIG_CHANGED,
                user_id="system",
                organization_id=config.organization_id,
                resource_type="whitelabel_config",
                resource_id=config.config_id,
                action="create_or_update",
                details={"config_type": "whitelabel", "brand_name": config.brand_name}
            )
            
            return True
        except Exception:
            return False
    
    def configure_sso(
        self,
        organization_id: str,
        provider: str,
        configuration: Dict[str, Any]
    ) -> bool:
        """Configure SSO for an organization"""
        try:
            if organization_id not in self.sso_configurations:
                self.sso_configurations[organization_id] = {}
            
            self.sso_configurations[organization_id][provider] = {
                **configuration,
                "configured_at": datetime.now().isoformat(),
                "is_active": True
            }
            
            # Record audit event
            self.compliance_manager.record_audit_event(
                event_type=AuditEventType.SYSTEM_CONFIG_CHANGED,
                user_id="system",
                organization_id=organization_id,
                resource_type="sso_config",
                resource_id=f"sso_{provider}",
                action="configure",
                details={"provider": provider, "config_type": "sso"}
            )
            
            return True
        except Exception:
            return False
    
    def get_security_config(self, organization_id: str) -> Optional[SecurityConfiguration]:
        """Get security configuration for an organization"""
        return self.security_configs.get(organization_id)
    
    def get_whitelabel_config(self, organization_id: str) -> Optional[WhiteLabelConfig]:
        """Get white-label configuration for an organization"""
        return self.whitelabel_configs.get(organization_id)
    
    def get_sso_config(self, organization_id: str) -> Dict[str, Any]:
        """Get SSO configuration for an organization"""
        return self.sso_configurations.get(organization_id, {})
    
    def get_admin_dashboard_data(self, organization_id: str) -> Dict[str, Any]:
        """Get comprehensive admin dashboard data"""
        return {
            "organization_id": organization_id,
            "security_config": bool(self.get_security_config(organization_id)),
            "whitelabel_config": bool(self.get_whitelabel_config(organization_id)),
            "sso_providers": list(self.get_sso_config(organization_id).keys()),
            "compliance_summary": self.compliance_manager.get_compliance_summary(organization_id),
            "recent_audit_events": len(self.compliance_manager.get_audit_trail(
                organization_id=organization_id,
                start_date=datetime.now() - timedelta(days=7),
                limit=100
            )),
            "generated_at": datetime.now().isoformat()
        }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get enterprise admin service statistics"""
        return {
            "total_security_configs": len(self.security_configs),
            "total_whitelabel_configs": len(self.whitelabel_configs),
            "total_sso_configs": len(self.sso_configurations),
            "total_audit_events": len(self.compliance_manager.audit_trails),
            "total_compliance_policies": len(self.compliance_manager.policies),
            "service_status": "active"
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on enterprise admin service"""
        return {
            "status": "healthy",
            "active_configurations": len(self.security_configs) + len(self.whitelabel_configs),
            "audit_trail_entries": len(self.compliance_manager.audit_trails),
            "compliance_policies": len(self.compliance_manager.policies),
            "timestamp": datetime.now().isoformat()
        }

# Global enterprise admin service instance
_enterprise_admin_service: Optional[EnterpriseAdminService] = None

def get_enterprise_admin_service() -> EnterpriseAdminService:
    """Get global enterprise admin service instance"""
    global _enterprise_admin_service
    if _enterprise_admin_service is None:
        _enterprise_admin_service = EnterpriseAdminService()
    return _enterprise_admin_service