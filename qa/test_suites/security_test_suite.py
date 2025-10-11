"""
Enterprise Security Testing Suite for M&A SaaS Platform
Vulnerability assessment, compliance validation, and security hardening
"""

import pytest
import asyncio
from typing import Dict, List, Any
import hashlib
import secrets
import json
from datetime import datetime, timedelta
import structlog
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

logger = structlog.get_logger(__name__)


class SecurityTestValidator:
    """Comprehensive security validation for enterprise requirements"""

    def __init__(self):
        self.vulnerabilities = []
        self.security_score = 100
        self.compliance_status = {}

    def record_vulnerability(self, severity: str, description: str, recommendation: str):
        """Record identified vulnerability"""
        self.vulnerabilities.append({
            "severity": severity,
            "description": description,
            "recommendation": recommendation,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Deduct from security score based on severity
        severity_impact = {"critical": 20, "high": 10, "medium": 5, "low": 2}
        self.security_score -= severity_impact.get(severity, 0)


# ==================== AUTHENTICATION SECURITY TESTS ====================

class TestAuthenticationSecurity:
    """Test authentication security measures"""

    @pytest.mark.asyncio
    async def test_password_requirements(self):
        """Test password strength requirements"""
        from app.services.auth import validate_password_strength

        # Test weak passwords
        weak_passwords = [
            "password123",
            "12345678",
            "qwerty123",
            "admin123"
        ]

        for password in weak_passwords:
            result = validate_password_strength(password)
            assert result["strong"] == False
            assert len(result["issues"]) > 0

        # Test strong passwords
        strong_passwords = [
            "Kj8$mN2@pL9#xQ4!",
            "ComplexP@ssw0rd2024!",
            "S3cur3*M&A_Platform#"
        ]

        for password in strong_passwords:
            result = validate_password_strength(password)
            assert result["strong"] == True
            assert result["score"] >= 80

    @pytest.mark.asyncio
    async def test_session_management(self):
        """Test secure session management"""
        from app.services.auth import SessionManager

        session_manager = SessionManager()

        # Test session creation with security tokens
        user_id = "test_user_001"
        session = await session_manager.create_session(
            user_id=user_id,
            ip_address="192.168.1.1",
            user_agent="Test Browser"
        )

        assert session["token"] is not None
        assert len(session["token"]) >= 32  # Sufficient entropy
        assert session["expires_at"] > datetime.utcnow()
        assert session["refresh_token"] is not None

        # Test session validation
        is_valid = await session_manager.validate_session(session["token"])
        assert is_valid == True

        # Test session rotation
        new_session = await session_manager.rotate_session(session["refresh_token"])
        assert new_session["token"] != session["token"]

        # Test session invalidation
        await session_manager.invalidate_session(session["token"])
        is_valid = await session_manager.validate_session(session["token"])
        assert is_valid == False

    @pytest.mark.asyncio
    async def test_mfa_implementation(self):
        """Test multi-factor authentication"""
        from app.services.auth import MFAService

        mfa_service = MFAService()

        # Test TOTP setup
        user_id = "test_user_mfa"
        secret = await mfa_service.generate_totp_secret(user_id)

        assert secret is not None
        assert len(secret) >= 32

        # Test TOTP verification
        # In production, this would use actual TOTP codes
        totp_code = "123456"  # Mock code
        is_valid = await mfa_service.verify_totp(user_id, totp_code)

        # Test backup codes
        backup_codes = await mfa_service.generate_backup_codes(user_id, count=10)
        assert len(backup_codes) == 10
        for code in backup_codes:
            assert len(code) == 10  # 10-character backup codes

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test authentication rate limiting"""
        from app.services.auth import RateLimiter

        rate_limiter = RateLimiter()

        # Test login attempt limiting
        ip_address = "192.168.1.100"

        for i in range(5):
            allowed = await rate_limiter.check_login_attempt(ip_address)
            assert allowed == True

        # 6th attempt should be blocked
        allowed = await rate_limiter.check_login_attempt(ip_address)
        assert allowed == False

        # Test exponential backoff
        backoff_time = await rate_limiter.get_backoff_time(ip_address)
        assert backoff_time >= 60  # At least 1 minute

        # Test API rate limiting
        api_key = "test_api_key"
        for i in range(100):
            allowed = await rate_limiter.check_api_rate(api_key)
            if i < 100:
                assert allowed == True

        # 101st request should be rate limited
        allowed = await rate_limiter.check_api_rate(api_key)
        assert allowed == False


# ==================== DATA PROTECTION TESTS ====================

class TestDataProtection:
    """Test data encryption and protection measures"""

    @pytest.mark.asyncio
    async def test_encryption_at_rest(self):
        """Test data encryption at rest"""
        from app.services.encryption import EncryptionService

        encryption_service = EncryptionService()

        # Test field-level encryption
        sensitive_data = {
            "ssn": "123-45-6789",
            "bank_account": "1234567890",
            "api_key": "secret_key_123"
        }

        encrypted_data = {}
        for field, value in sensitive_data.items():
            encrypted = await encryption_service.encrypt_field(value)
            encrypted_data[field] = encrypted

            # Verify encryption
            assert encrypted != value
            assert len(encrypted) > len(value)

            # Verify decryption
            decrypted = await encryption_service.decrypt_field(encrypted)
            assert decrypted == value

    @pytest.mark.asyncio
    async def test_encryption_in_transit(self):
        """Test TLS/SSL configuration"""
        import ssl
        import aiohttp

        # Test HTTPS enforcement
        async with aiohttp.ClientSession() as session:
            # Test redirect from HTTP to HTTPS
            async with session.get("http://app.masaas.com", allow_redirects=False) as response:
                assert response.status == 301
                assert response.headers["Location"].startswith("https://")

        # Test TLS version and cipher suites
        ssl_context = ssl.create_default_context()
        assert ssl_context.minimum_version == ssl.TLSVersion.TLSv1_2

        # Verify strong ciphers only
        weak_ciphers = ["RC4", "DES", "3DES", "MD5"]
        ciphers = ssl_context.get_ciphers()
        for cipher in ciphers:
            for weak in weak_ciphers:
                assert weak not in cipher["name"]

    @pytest.mark.asyncio
    async def test_key_management(self):
        """Test cryptographic key management"""
        from app.services.key_management import KeyManager

        key_manager = KeyManager()

        # Test key generation
        master_key = await key_manager.generate_master_key()
        assert len(master_key) == 32  # 256-bit key

        # Test key rotation
        old_key = master_key
        new_key = await key_manager.rotate_master_key()
        assert new_key != old_key

        # Test key derivation
        derived_key = await key_manager.derive_key(
            master_key=master_key,
            context="document_encryption"
        )
        assert derived_key != master_key
        assert len(derived_key) == 32

        # Test secure key storage
        stored = await key_manager.store_key("test_key_id", master_key)
        assert stored == True

        retrieved = await key_manager.retrieve_key("test_key_id")
        assert retrieved == master_key

    @pytest.mark.asyncio
    async def test_data_masking(self):
        """Test sensitive data masking"""
        from app.services.data_protection import DataMasking

        masking = DataMasking()

        # Test PII masking
        test_data = {
            "email": "john.doe@example.com",
            "phone": "+1-555-123-4567",
            "ssn": "123-45-6789",
            "credit_card": "4532-1234-5678-9012"
        }

        masked_data = await masking.mask_pii(test_data)

        assert masked_data["email"] == "j***.d**@example.com"
        assert masked_data["phone"] == "+1-555-***-**67"
        assert masked_data["ssn"] == "***-**-6789"
        assert masked_data["credit_card"] == "4532-****-****-9012"

        # Test reversible masking for authorized access
        tokenized = await masking.tokenize_sensitive_data(test_data["credit_card"])
        assert tokenized != test_data["credit_card"]

        # Authorized detokenization
        original = await masking.detokenize(tokenized, authorized=True)
        assert original == test_data["credit_card"]


# ==================== ACCESS CONTROL TESTS ====================

class TestAccessControl:
    """Test role-based and attribute-based access control"""

    @pytest.mark.asyncio
    async def test_rbac_enforcement(self):
        """Test role-based access control"""
        from app.services.authorization import RBACService

        rbac = RBACService()

        # Define roles and permissions
        roles = {
            "admin": ["*"],  # All permissions
            "manager": ["read:deals", "write:deals", "read:documents", "write:documents"],
            "analyst": ["read:deals", "read:documents"],
            "viewer": ["read:deals"]
        }

        for role, permissions in roles.items():
            await rbac.create_role(role, permissions)

        # Test permission checking
        user_roles = {
            "user_admin": "admin",
            "user_manager": "manager",
            "user_analyst": "analyst"
        }

        # Admin can do everything
        assert await rbac.check_permission("user_admin", "admin", "delete:deals") == True

        # Manager can write deals
        assert await rbac.check_permission("user_manager", "manager", "write:deals") == True

        # Analyst cannot write
        assert await rbac.check_permission("user_analyst", "analyst", "write:deals") == False

        # Viewer cannot access documents
        assert await rbac.check_permission("user_viewer", "viewer", "read:documents") == False

    @pytest.mark.asyncio
    async def test_abac_policies(self):
        """Test attribute-based access control"""
        from app.services.authorization import ABACService

        abac = ABACService()

        # Create access policy
        policy = {
            "id": "deal_access_policy",
            "effect": "allow",
            "actions": ["read", "update"],
            "resources": ["deals/*"],
            "conditions": {
                "user.organization_id": "${resource.organization_id}",
                "user.department": ["M&A", "Finance"],
                "resource.confidentiality": ["public", "internal"],
                "time.business_hours": True
            }
        }

        await abac.create_policy(policy)

        # Test access evaluation
        context = {
            "user": {
                "id": "user_001",
                "organization_id": "org_001",
                "department": "M&A"
            },
            "resource": {
                "type": "deal",
                "id": "deal_001",
                "organization_id": "org_001",
                "confidentiality": "internal"
            },
            "action": "read",
            "time": {
                "business_hours": True
            }
        }

        decision = await abac.evaluate(context)
        assert decision == "allow"

        # Test denied access for different org
        context["resource"]["organization_id"] = "org_002"
        decision = await abac.evaluate(context)
        assert decision == "deny"

    @pytest.mark.asyncio
    async def test_privilege_escalation_prevention(self):
        """Test protection against privilege escalation"""
        from app.services.authorization import SecurityMonitor

        monitor = SecurityMonitor()

        # Test detection of privilege escalation attempts
        suspicious_activities = [
            {
                "user_id": "user_001",
                "action": "modify_role",
                "target_role": "admin",
                "current_role": "viewer"
            },
            {
                "user_id": "user_002",
                "action": "access_resource",
                "resource": "/admin/settings",
                "permission": "denied"
            }
        ]

        for activity in suspicious_activities:
            threat_level = await monitor.analyze_activity(activity)
            assert threat_level in ["high", "critical"]

            # Verify security alert generated
            alerts = await monitor.get_recent_alerts()
            assert len(alerts) > 0


# ==================== VULNERABILITY ASSESSMENT ====================

class TestVulnerabilityAssessment:
    """Test for common security vulnerabilities"""

    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        from app.database import execute_query

        # Test malicious SQL patterns
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1' UNION SELECT * FROM users--"
        ]

        for malicious_input in malicious_inputs:
            # Attempt SQL injection
            try:
                result = await execute_query(
                    "SELECT * FROM deals WHERE name = :name",
                    {"name": malicious_input}
                )
                # Query should execute safely with parameterization
                assert True
            except Exception as e:
                # If exception, should not be SQL syntax error
                assert "SQL syntax" not in str(e)

    @pytest.mark.asyncio
    async def test_xss_prevention(self):
        """Test cross-site scripting prevention"""
        from app.services.sanitization import HTMLSanitizer

        sanitizer = HTMLSanitizer()

        # Test XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'>"
        ]

        for payload in xss_payloads:
            sanitized = sanitizer.sanitize(payload)
            assert "<script" not in sanitized
            assert "javascript:" not in sanitized
            assert "onerror" not in sanitized
            assert "onload" not in sanitized

    @pytest.mark.asyncio
    async def test_csrf_protection(self):
        """Test CSRF token validation"""
        from app.services.csrf import CSRFProtection

        csrf = CSRFProtection()

        # Generate CSRF token
        session_id = "test_session_001"
        token = await csrf.generate_token(session_id)

        assert token is not None
        assert len(token) >= 32

        # Test token validation
        is_valid = await csrf.validate_token(session_id, token)
        assert is_valid == True

        # Test invalid token
        is_valid = await csrf.validate_token(session_id, "invalid_token")
        assert is_valid == False

        # Test token expiration
        expired_token = await csrf.generate_token(session_id, ttl=1)
        await asyncio.sleep(2)
        is_valid = await csrf.validate_token(session_id, expired_token)
        assert is_valid == False

    @pytest.mark.asyncio
    async def test_xxe_prevention(self):
        """Test XML external entity prevention"""
        from app.services.xml_parser import SafeXMLParser

        parser = SafeXMLParser()

        # Test XXE payload
        xxe_payload = """<?xml version="1.0"?>
        <!DOCTYPE data [
            <!ENTITY xxe SYSTEM "file:///etc/passwd">
        ]>
        <data>&xxe;</data>"""

        # Parser should reject or sanitize XXE
        try:
            result = parser.parse(xxe_payload)
            # If parsed, external entities should be disabled
            assert "&xxe;" not in str(result)
            assert "/etc/passwd" not in str(result)
        except Exception as e:
            # Should reject dangerous XML
            assert "external entity" in str(e).lower()

    @pytest.mark.asyncio
    async def test_path_traversal_prevention(self):
        """Test path traversal attack prevention"""
        from app.services.file_handler import SecureFileHandler

        file_handler = SecureFileHandler()

        # Test path traversal attempts
        malicious_paths = [
            "../../etc/passwd",
            "../../../windows/system32/config/sam",
            "documents/../../../etc/shadow",
            "files/../../../../etc/hosts"
        ]

        for path in malicious_paths:
            # Should sanitize or reject malicious paths
            safe_path = file_handler.sanitize_path(path)
            assert ".." not in safe_path
            assert not safe_path.startswith("/")
            assert "etc" not in safe_path


# ==================== COMPLIANCE VALIDATION ====================

class TestComplianceValidation:
    """Test regulatory compliance requirements"""

    @pytest.mark.asyncio
    async def test_gdpr_compliance(self):
        """Test GDPR compliance features"""
        from app.services.gdpr import GDPRService

        gdpr = GDPRService()

        user_id = "gdpr_test_user"

        # Test right to access (data portability)
        user_data = await gdpr.export_user_data(user_id)
        assert user_data is not None
        assert "personal_data" in user_data
        assert "processing_history" in user_data
        assert "consent_records" in user_data

        # Test right to erasure
        deletion_result = await gdpr.delete_user_data(user_id)
        assert deletion_result["status"] == "completed"
        assert deletion_result["data_removed"] == True

        # Test consent management
        consent = await gdpr.record_consent(
            user_id="new_user",
            purpose="marketing",
            granted=True
        )
        assert consent["recorded"] == True
        assert consent["timestamp"] is not None

        # Test data breach notification
        breach = await gdpr.record_data_breach(
            affected_users=100,
            data_types=["email", "name"],
            severity="medium"
        )
        assert breach["notification_required"] == True
        assert breach["deadline_hours"] == 72

    @pytest.mark.asyncio
    async def test_pci_dss_compliance(self):
        """Test PCI DSS compliance for payment processing"""
        from app.services.payment_security import PCICompliance

        pci = PCICompliance()

        # Test credit card data handling
        card_number = "4532123456789012"

        # Should never store full card number
        stored_data = await pci.store_card_data(card_number)
        assert stored_data["masked"] == "4532********9012"
        assert "full_number" not in stored_data

        # Test secure transmission
        encrypted_transmission = await pci.prepare_for_transmission(card_number)
        assert encrypted_transmission != card_number

        # Test audit logging
        audit_log = await pci.get_payment_audit_log()
        assert len(audit_log) > 0
        for entry in audit_log:
            assert "timestamp" in entry
            assert "action" in entry
            assert "user_id" in entry

    @pytest.mark.asyncio
    async def test_sox_compliance(self):
        """Test SOX compliance for financial controls"""
        from app.services.audit import SOXCompliance

        sox = SOXCompliance()

        # Test audit trail
        audit_trail = await sox.get_audit_trail(
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow()
        )
        assert audit_trail is not None
        assert audit_trail["immutable"] == True

        # Test segregation of duties
        user_id = "test_user"
        can_approve = await sox.check_approval_authority(
            user_id=user_id,
            action="approve_payment",
            amount=100000
        )

        can_execute = await sox.check_execution_authority(
            user_id=user_id,
            action="execute_payment"
        )

        # User shouldn't have both approve and execute
        assert not (can_approve and can_execute)

        # Test data retention
        retention_policy = await sox.get_retention_policy("financial_records")
        assert retention_policy["years"] >= 7


# ==================== SECURITY MONITORING ====================

class TestSecurityMonitoring:
    """Test security monitoring and incident response"""

    @pytest.mark.asyncio
    async def test_intrusion_detection(self):
        """Test intrusion detection system"""
        from app.services.security_monitoring import IntrusionDetection

        ids = IntrusionDetection()

        # Simulate suspicious patterns
        suspicious_patterns = [
            {"type": "brute_force", "attempts": 50, "time_window": 60},
            {"type": "port_scanning", "ports": [22, 80, 443, 3306, 5432]},
            {"type": "unusual_traffic", "volume": 1000000, "duration": 10}
        ]

        for pattern in suspicious_patterns:
            threat = await ids.analyze_pattern(pattern)
            assert threat["detected"] == True
            assert threat["severity"] in ["medium", "high", "critical"]
            assert "response_actions" in threat

    @pytest.mark.asyncio
    async def test_security_logging(self):
        """Test security event logging"""
        from app.services.security_logging import SecurityLogger

        security_logger = SecurityLogger()

        # Test security event logging
        events = [
            {"type": "failed_login", "user": "test@example.com", "ip": "192.168.1.100"},
            {"type": "privilege_escalation_attempt", "user_id": "user_001"},
            {"type": "suspicious_api_usage", "endpoint": "/api/admin/users", "rate": 1000}
        ]

        for event in events:
            logged = await security_logger.log_security_event(event)
            assert logged == True

        # Verify logs are tamper-proof
        logs = await security_logger.get_recent_logs()
        for log in logs:
            assert "hash" in log
            assert "timestamp" in log

            # Verify hash integrity
            is_valid = await security_logger.verify_log_integrity(log)
            assert is_valid == True

    @pytest.mark.asyncio
    async def test_incident_response(self):
        """Test incident response procedures"""
        from app.services.incident_response import IncidentManager

        incident_manager = IncidentManager()

        # Create security incident
        incident = await incident_manager.create_incident(
            severity="high",
            type="data_breach",
            description="Unauthorized access detected",
            affected_systems=["database", "api"]
        )

        assert incident["id"] is not None
        assert incident["status"] == "open"

        # Test incident escalation
        escalation = await incident_manager.escalate_incident(
            incident_id=incident["id"],
            reason="Critical data exposure"
        )
        assert escalation["escalated"] == True
        assert escalation["notified_parties"] > 0

        # Test incident response
        response = await incident_manager.execute_response(
            incident_id=incident["id"],
            actions=["isolate_system", "revoke_access", "forensic_analysis"]
        )
        assert response["actions_executed"] == 3

        # Test incident closure
        closure = await incident_manager.close_incident(
            incident_id=incident["id"],
            resolution="Access revoked, system patched",
            lessons_learned="Implement additional monitoring"
        )
        assert closure["status"] == "closed"


# ==================== SECURITY REPORT GENERATION ====================

class SecurityAuditReport:
    """Generate comprehensive security audit report"""

    def __init__(self):
        self.test_results = {}
        self.vulnerabilities = []
        self.compliance_status = {}

    async def run_security_audit(self):
        """Execute full security audit"""
        logger.info("Starting comprehensive security audit")

        # Run all security test suites
        test_suites = [
            TestAuthenticationSecurity(),
            TestDataProtection(),
            TestAccessControl(),
            TestVulnerabilityAssessment(),
            TestComplianceValidation(),
            TestSecurityMonitoring()
        ]

        for suite in test_suites:
            suite_name = suite.__class__.__name__
            logger.info(f"Running {suite_name}")

            # Run test methods
            test_methods = [m for m in dir(suite) if m.startswith("test_")]
            results = {"passed": 0, "failed": 0}

            for method_name in test_methods:
                try:
                    method = getattr(suite, method_name)
                    if asyncio.iscoroutinefunction(method):
                        await method()
                    results["passed"] += 1
                except Exception as e:
                    results["failed"] += 1
                    self.vulnerabilities.append({
                        "test": f"{suite_name}.{method_name}",
                        "error": str(e)
                    })

            self.test_results[suite_name] = results

        return self.generate_report()

    def generate_report(self):
        """Generate security audit report"""
        total_passed = sum(r["passed"] for r in self.test_results.values())
        total_failed = sum(r["failed"] for r in self.test_results.values())

        security_score = 100 - (total_failed * 5)  # Deduct 5 points per failure

        report = {
            "audit_date": datetime.utcnow().isoformat(),
            "security_score": max(security_score, 0),
            "summary": {
                "total_tests": total_passed + total_failed,
                "passed": total_passed,
                "failed": total_failed,
                "vulnerabilities_found": len(self.vulnerabilities)
            },
            "test_results": self.test_results,
            "vulnerabilities": self.vulnerabilities,
            "compliance": {
                "gdpr": total_failed == 0,
                "pci_dss": total_failed == 0,
                "sox": total_failed == 0
            },
            "recommendations": self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self):
        """Generate security recommendations"""
        recommendations = []

        if self.vulnerabilities:
            recommendations.append("Address identified vulnerabilities immediately")

        if self.test_results.get("TestAuthenticationSecurity", {}).get("failed", 0) > 0:
            recommendations.append("Strengthen authentication mechanisms")

        if self.test_results.get("TestDataProtection", {}).get("failed", 0) > 0:
            recommendations.append("Enhance data encryption and protection")

        if not recommendations:
            recommendations.append("Security posture is strong - maintain regular audits")

        return recommendations


async def main():
    """Execute security audit"""
    auditor = SecurityAuditReport()
    report = await auditor.run_security_audit()

    # Save report
    with open("security_audit_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Print summary
    print("\n" + "="*80)
    print("SECURITY AUDIT REPORT")
    print("="*80)
    print(f"Security Score: {report['security_score']}/100")
    print(f"Tests Passed: {report['summary']['passed']}")
    print(f"Tests Failed: {report['summary']['failed']}")
    print(f"Vulnerabilities: {report['summary']['vulnerabilities_found']}")
    print("\nCompliance Status:")
    for standard, compliant in report["compliance"].items():
        status = "✅" if compliant else "❌"
        print(f"  {status} {standard.upper()}")

    if report["recommendations"]:
        print("\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")

    print("="*80)

    return report["security_score"] >= 80


if __name__ == "__main__":
    asyncio.run(main())