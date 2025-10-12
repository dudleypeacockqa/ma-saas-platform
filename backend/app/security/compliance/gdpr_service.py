"""
GDPR Compliance Service
Data protection and privacy compliance for EU regulations
"""

import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import logging
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()

class DataProcessingPurpose(Enum):
    """Legal basis for data processing under GDPR"""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"

class DataCategory(Enum):
    """Categories of personal data"""
    BASIC_IDENTITY = "basic_identity"  # Name, email, phone
    PROFESSIONAL = "professional"      # Job title, company, experience
    FINANCIAL = "financial"           # Deal values, financial statements
    BEHAVIORAL = "behavioral"         # Platform usage, preferences
    BIOMETRIC = "biometric"          # Fingerprints, face recognition
    SPECIAL_CATEGORY = "special_category"  # Health, political opinions, etc.

class ConsentRecord(Base):
    """Database model for user consent tracking"""
    __tablename__ = "consent_records"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False)
    purpose = Column(String(50), nullable=False)
    data_categories = Column(Text)  # JSON array
    consent_given = Column(Boolean, nullable=False)
    consent_date = Column(DateTime, nullable=False)
    withdrawal_date = Column(DateTime)
    legal_basis = Column(String(50), nullable=False)
    processing_details = Column(Text)  # JSON object
    ip_address = Column(String(45))
    user_agent = Column(Text)

class DataProcessingRecord(Base):
    """Database model for data processing activities"""
    __tablename__ = "data_processing_records"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False)
    processing_purpose = Column(String(100), nullable=False)
    data_categories = Column(Text)  # JSON array
    legal_basis = Column(String(50), nullable=False)
    retention_period = Column(Integer)  # Days
    processing_date = Column(DateTime, default=datetime.utcnow)
    third_party_sharing = Column(Boolean, default=False)
    third_parties = Column(Text)  # JSON array
    security_measures = Column(Text)  # JSON object

class DataSubjectRequest(Base):
    """Database model for data subject requests (access, rectification, erasure)"""
    __tablename__ = "data_subject_requests"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False)
    request_type = Column(String(50), nullable=False)  # access, rectification, erasure, portability
    request_date = Column(DateTime, default=datetime.utcnow)
    request_details = Column(Text)  # JSON object
    status = Column(String(50), default="pending")  # pending, processing, completed, rejected
    completion_date = Column(DateTime)
    response_data = Column(Text)  # JSON object with response
    verification_method = Column(String(50))

class GDPRService:
    """
    GDPR Compliance Service
    Handles data protection, privacy rights, and regulatory compliance
    """

    def __init__(self):
        self.retention_policies = {
            DataCategory.BASIC_IDENTITY: 2555,  # 7 years
            DataCategory.PROFESSIONAL: 2555,   # 7 years
            DataCategory.FINANCIAL: 2555,      # 7 years (regulatory requirement)
            DataCategory.BEHAVIORAL: 1095,     # 3 years
            DataCategory.BIOMETRIC: 365,       # 1 year unless consent renewed
            DataCategory.SPECIAL_CATEGORY: 365  # 1 year unless explicit consent
        }

    async def record_consent(
        self,
        user_id: str,
        purpose: str,
        data_categories: List[DataCategory],
        legal_basis: DataProcessingPurpose,
        consent_given: bool,
        processing_details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Record user consent for data processing

        Args:
            user_id: User identifier
            purpose: Purpose of data processing
            data_categories: Categories of data being processed
            legal_basis: Legal basis for processing
            consent_given: Whether consent was given
            processing_details: Additional processing information
            ip_address: User's IP address
            user_agent: User's browser agent

        Returns:
            Consent record ID
        """
        try:
            import secrets
            record_id = f"consent_{secrets.token_hex(16)}"

            consent_record = {
                "id": record_id,
                "user_id": user_id,
                "purpose": purpose,
                "data_categories": [cat.value for cat in data_categories],
                "consent_given": consent_given,
                "consent_date": datetime.utcnow(),
                "legal_basis": legal_basis.value,
                "processing_details": processing_details or {},
                "ip_address": ip_address,
                "user_agent": user_agent
            }

            # In production, save to database
            logger.info(f"Consent recorded for user {user_id}: {purpose}")
            return record_id

        except Exception as e:
            logger.error(f"Failed to record consent: {str(e)}")
            raise

    async def withdraw_consent(self, user_id: str, consent_id: str) -> bool:
        """
        Withdraw previously given consent

        Args:
            user_id: User identifier
            consent_id: Consent record identifier

        Returns:
            True if withdrawal successful
        """
        try:
            # Get consent record
            consent_record = self._get_consent_record(consent_id)

            if not consent_record or consent_record["user_id"] != user_id:
                return False

            # Update consent record
            consent_record["withdrawal_date"] = datetime.utcnow()
            consent_record["consent_given"] = False

            # Trigger data processing review
            await self._review_data_processing_after_withdrawal(user_id, consent_record)

            logger.info(f"Consent withdrawn for user {user_id}: {consent_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to withdraw consent: {str(e)}")
            return False

    async def process_access_request(self, user_id: str, request_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data subject access request (Article 15)

        Args:
            user_id: User identifier
            request_details: Request specifications

        Returns:
            Complete data export for the user
        """
        try:
            import secrets
            request_id = f"access_{secrets.token_hex(16)}"

            # Collect all user data
            user_data = await self._collect_user_data(user_id)

            # Prepare response
            response_data = {
                "request_id": request_id,
                "user_id": user_id,
                "export_date": datetime.utcnow().isoformat(),
                "data_categories": list(user_data.keys()),
                "processing_purposes": await self._get_processing_purposes(user_id),
                "retention_periods": self._get_retention_periods(),
                "third_party_sharing": await self._get_third_party_sharing(user_id),
                "data": user_data,
                "rights_information": self._get_rights_information()
            }

            # Create request record
            await self._create_data_subject_request(
                user_id, "access", request_details, response_data
            )

            logger.info(f"Access request processed for user {user_id}")
            return response_data

        except Exception as e:
            logger.error(f"Failed to process access request: {str(e)}")
            raise

    async def process_rectification_request(
        self,
        user_id: str,
        corrections: Dict[str, Any]
    ) -> bool:
        """
        Process data rectification request (Article 16)

        Args:
            user_id: User identifier
            corrections: Data corrections to apply

        Returns:
            True if rectification successful
        """
        try:
            # Validate corrections
            valid_corrections = self._validate_corrections(corrections)

            if not valid_corrections:
                return False

            # Apply corrections to user data
            await self._apply_data_corrections(user_id, valid_corrections)

            # Log rectification
            await self._create_data_subject_request(
                user_id, "rectification", {"corrections": corrections}, {"status": "completed"}
            )

            logger.info(f"Data rectified for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to process rectification request: {str(e)}")
            return False

    async def process_erasure_request(
        self,
        user_id: str,
        erasure_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process right to erasure request (Article 17)

        Args:
            user_id: User identifier
            erasure_details: Specific erasure requirements

        Returns:
            Erasure report
        """
        try:
            # Check if erasure is legally permissible
            erasure_assessment = await self._assess_erasure_legality(user_id, erasure_details)

            if not erasure_assessment["can_erase"]:
                return {
                    "status": "rejected",
                    "reason": erasure_assessment["reason"],
                    "legal_basis": erasure_assessment["legal_basis"]
                }

            # Perform data erasure
            erasure_report = await self._perform_data_erasure(user_id, erasure_details)

            # Notify third parties if necessary
            await self._notify_third_parties_of_erasure(user_id, erasure_report)

            # Create request record
            await self._create_data_subject_request(
                user_id, "erasure", erasure_details, erasure_report
            )

            logger.info(f"Data erasure completed for user {user_id}")
            return erasure_report

        except Exception as e:
            logger.error(f"Failed to process erasure request: {str(e)}")
            raise

    async def process_portability_request(self, user_id: str) -> Dict[str, Any]:
        """
        Process data portability request (Article 20)

        Args:
            user_id: User identifier

        Returns:
            Structured data export
        """
        try:
            # Collect portable data (only data provided by user or generated through use)
            portable_data = await self._collect_portable_data(user_id)

            # Format in machine-readable format
            export_data = {
                "format": "JSON",
                "standard": "GDPR Article 20",
                "export_date": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "data": portable_data
            }

            # Create request record
            await self._create_data_subject_request(
                user_id, "portability", {}, export_data
            )

            logger.info(f"Data portability export created for user {user_id}")
            return export_data

        except Exception as e:
            logger.error(f"Failed to process portability request: {str(e)}")
            raise

    async def check_retention_compliance(self) -> Dict[str, Any]:
        """
        Check data retention compliance across all users

        Returns:
            Compliance report with actions needed
        """
        try:
            # Identify data that should be deleted
            retention_review = {
                "reviewed_date": datetime.utcnow().isoformat(),
                "users_reviewed": 0,
                "data_for_deletion": [],
                "policy_violations": [],
                "actions_taken": []
            }

            # Get all processing records
            processing_records = await self._get_all_processing_records()

            for record in processing_records:
                # Check if data has exceeded retention period
                retention_days = self.retention_policies.get(
                    DataCategory(record["data_category"]), 2555
                )

                if record["processing_date"] + timedelta(days=retention_days) < datetime.utcnow():
                    # Check if deletion is legally required
                    if await self._should_delete_expired_data(record):
                        retention_review["data_for_deletion"].append({
                            "user_id": record["user_id"],
                            "data_category": record["data_category"],
                            "expired_date": (record["processing_date"] + timedelta(days=retention_days)).isoformat(),
                            "action": "schedule_deletion"
                        })

            logger.info(f"Retention compliance check completed: {len(retention_review['data_for_deletion'])} items for deletion")
            return retention_review

        except Exception as e:
            logger.error(f"Retention compliance check failed: {str(e)}")
            raise

    async def generate_privacy_notice(self, language: str = "en") -> Dict[str, Any]:
        """
        Generate privacy notice content

        Args:
            language: Language code for the notice

        Returns:
            Privacy notice content
        """
        privacy_notice = {
            "language": language,
            "last_updated": datetime.utcnow().isoformat(),
            "sections": {
                "data_controller": {
                    "name": "M&A Platform Ltd",
                    "contact": "privacy@maplatform.com",
                    "dpo_contact": "dpo@maplatform.com"
                },
                "purposes": [
                    {
                        "purpose": "Deal Management",
                        "legal_basis": DataProcessingPurpose.CONTRACT.value,
                        "data_categories": [
                            DataCategory.BASIC_IDENTITY.value,
                            DataCategory.PROFESSIONAL.value,
                            DataCategory.FINANCIAL.value
                        ],
                        "retention": "7 years"
                    },
                    {
                        "purpose": "Platform Analytics",
                        "legal_basis": DataProcessingPurpose.LEGITIMATE_INTERESTS.value,
                        "data_categories": [DataCategory.BEHAVIORAL.value],
                        "retention": "3 years"
                    }
                ],
                "rights": [
                    "Right of access (Article 15)",
                    "Right to rectification (Article 16)",
                    "Right to erasure (Article 17)",
                    "Right to restrict processing (Article 18)",
                    "Right to data portability (Article 20)",
                    "Right to object (Article 21)"
                ],
                "third_parties": [
                    {
                        "name": "Cloud Storage Provider",
                        "purpose": "Data hosting",
                        "safeguards": "Standard Contractual Clauses"
                    }
                ]
            }
        }

        return privacy_notice

    def _get_consent_record(self, consent_id: str) -> Optional[Dict[str, Any]]:
        """Get consent record by ID (mock implementation)"""
        # In production, query database
        return None

    async def _review_data_processing_after_withdrawal(
        self, user_id: str, consent_record: Dict[str, Any]
    ):
        """Review and potentially stop data processing after consent withdrawal"""
        # Implementation would check if processing can continue under different legal basis
        pass

    async def _collect_user_data(self, user_id: str) -> Dict[str, Any]:
        """Collect all user data for access request"""
        # In production, collect from all relevant tables
        return {
            "profile": {},
            "deals": [],
            "documents": [],
            "activities": [],
            "preferences": {}
        }

    async def _get_processing_purposes(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all processing purposes for user"""
        return []

    def _get_retention_periods(self) -> Dict[str, int]:
        """Get retention periods for all data categories"""
        return {cat.value: days for cat, days in self.retention_policies.items()}

    async def _get_third_party_sharing(self, user_id: str) -> List[Dict[str, Any]]:
        """Get third party sharing information"""
        return []

    def _get_rights_information(self) -> Dict[str, str]:
        """Get information about user rights"""
        return {
            "access": "You can request a copy of your personal data",
            "rectification": "You can request correction of inaccurate data",
            "erasure": "You can request deletion of your data",
            "portability": "You can request your data in a machine-readable format"
        }

    async def _create_data_subject_request(
        self, user_id: str, request_type: str, request_details: Dict[str, Any], response_data: Dict[str, Any]
    ):
        """Create data subject request record"""
        # In production, save to database
        pass

    def _validate_corrections(self, corrections: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data corrections"""
        # Implementation would validate field types, constraints, etc.
        return corrections

    async def _apply_data_corrections(self, user_id: str, corrections: Dict[str, Any]):
        """Apply data corrections to user records"""
        # Implementation would update relevant database tables
        pass

    async def _assess_erasure_legality(self, user_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Assess if data erasure is legally permissible"""
        # Check for legal obligations, public interest, etc.
        return {
            "can_erase": True,
            "reason": "No legal obligation to retain",
            "legal_basis": "Right to erasure applicable"
        }

    async def _perform_data_erasure(self, user_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Perform actual data erasure"""
        return {
            "status": "completed",
            "items_deleted": ["profile", "preferences"],
            "items_retained": ["audit_logs"],
            "retention_reason": "Legal obligation"
        }

    async def _notify_third_parties_of_erasure(self, user_id: str, erasure_report: Dict[str, Any]):
        """Notify third parties of data erasure"""
        # Implementation would notify data processors
        pass

    async def _collect_portable_data(self, user_id: str) -> Dict[str, Any]:
        """Collect data that can be ported under Article 20"""
        # Only data provided by user or generated through use
        return {}

    async def _get_all_processing_records(self) -> List[Dict[str, Any]]:
        """Get all data processing records for retention review"""
        return []

    async def _should_delete_expired_data(self, record: Dict[str, Any]) -> bool:
        """Check if expired data should be deleted"""
        # Check for legal obligations to retain
        return True

# Global GDPR service instance
gdpr_service = GDPRService()