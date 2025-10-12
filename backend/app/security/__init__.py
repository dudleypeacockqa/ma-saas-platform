"""
Enterprise-Grade Security Module
Bank-level security controls for M&A platform
"""

from .encryption.field_encryption import FieldEncryptionService
from .encryption.hsm_integration import HSMService
from .encryption.key_management import KeyManagementService
from .authentication.mfa_service import MFAService
from .authentication.webauthn_handler import WebAuthnHandler
from .authentication.sso_providers import SSOProvider
from .authorization.rbac_engine import RBACEngine
from .authorization.abac_policies import ABACPolicyEngine
from .authorization.permission_service import PermissionService
from .compliance.gdpr_service import GDPRService
from .compliance.audit_logger import AuditLogger
from .compliance.compliance_reports import ComplianceReportService
from .monitoring.security_monitor import SecurityMonitor
from .monitoring.anomaly_detection import AnomalyDetectionService
from .monitoring.incident_response import IncidentResponseService

__all__ = [
    "FieldEncryptionService",
    "HSMService",
    "KeyManagementService",
    "MFAService",
    "WebAuthnHandler",
    "SSOProvider",
    "RBACEngine",
    "ABACPolicyEngine",
    "PermissionService",
    "GDPRService",
    "AuditLogger",
    "ComplianceReportService",
    "SecurityMonitor",
    "AnomalyDetectionService",
    "IncidentResponseService"
]

# Security configuration
SECURITY_CONFIG = {
    "encryption": {
        "algorithm": "AES-256-GCM",
        "key_rotation_days": 30,
        "hsm_enabled": True
    },
    "authentication": {
        "mfa_required": True,
        "session_timeout_minutes": 30,
        "max_concurrent_sessions": 3
    },
    "compliance": {
        "audit_retention_days": 2555,  # 7 years
        "gdpr_enabled": True,
        "pci_compliance": True
    },
    "monitoring": {
        "real_time_alerts": True,
        "anomaly_detection": True,
        "incident_auto_response": True
    }
}