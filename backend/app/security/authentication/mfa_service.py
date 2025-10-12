"""
Multi-Factor Authentication Service
Enterprise-grade MFA with FIDO2/WebAuthn support
"""

import secrets
import qrcode
import io
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import pyotp
from webauthn import generate_registration_options, verify_registration_response
from webauthn import generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    PublicKeyCredentialCreationOptions,
    AuthenticationCredential,
    RegistrationCredential
)
import logging
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings
from app.models.users import User

logger = logging.getLogger(__name__)

Base = declarative_base()

class MFADevice(Base):
    """Database model for MFA devices"""
    __tablename__ = "mfa_devices"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False)
    device_type = Column(String(50), nullable=False)  # totp, webauthn, backup
    device_name = Column(String(100), nullable=False)
    secret_key = Column(Text)  # For TOTP
    credential_id = Column(Text)  # For WebAuthn
    public_key = Column(Text)  # For WebAuthn
    counter = Column(Integer, default=0)  # For WebAuthn
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    is_active = Column(Boolean, default=True)
    backup_codes = Column(Text)  # JSON array of backup codes

class MFAChallenge(Base):
    """Database model for MFA challenges"""
    __tablename__ = "mfa_challenges"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False)
    challenge_type = Column(String(50), nullable=False)
    challenge_data = Column(Text)  # JSON data for challenge
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)

class MFAService:
    """
    Enterprise Multi-Factor Authentication Service
    Supports TOTP, WebAuthn/FIDO2, and backup codes
    """

    def __init__(self):
        self.rp_id = settings.DOMAIN_NAME or "localhost"
        self.rp_name = "M&A Platform"
        self.totp_issuer = "M&A Platform"

    async def setup_totp(self, user: User, device_name: str = "Authenticator App") -> Dict[str, Any]:
        """
        Set up Time-based One-Time Password (TOTP) authentication

        Args:
            user: User object
            device_name: Human-readable device name

        Returns:
            Dictionary with QR code and backup codes
        """
        try:
            # Generate secret key
            secret = pyotp.random_base32()

            # Create TOTP object
            totp = pyotp.TOTP(secret)

            # Generate provisioning URI for QR code
            provisioning_uri = totp.provisioning_uri(
                name=user.email,
                issuer_name=self.totp_issuer
            )

            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)

            qr_image = qr.make_image(fill_color="black", back_color="white")
            img_buffer = io.BytesIO()
            qr_image.save(img_buffer, format='PNG')
            qr_code_base64 = base64.b64encode(img_buffer.getvalue()).decode()

            # Generate backup codes
            backup_codes = self._generate_backup_codes()

            # Store device (will be activated after verification)
            device_id = f"totp_{secrets.token_hex(16)}"

            # In production, this would save to database
            device_data = {
                "id": device_id,
                "user_id": user.id,
                "device_type": "totp",
                "device_name": device_name,
                "secret_key": secret,
                "backup_codes": backup_codes,
                "is_active": False  # Will be activated after verification
            }

            logger.info(f"TOTP setup initiated for user {user.id}")

            return {
                "device_id": device_id,
                "secret": secret,
                "qr_code": f"data:image/png;base64,{qr_code_base64}",
                "backup_codes": backup_codes,
                "provisioning_uri": provisioning_uri
            }

        except Exception as e:
            logger.error(f"TOTP setup failed for user {user.id}: {str(e)}")
            raise

    async def verify_totp_setup(self, user: User, device_id: str, token: str) -> bool:
        """
        Verify TOTP setup with user-provided token

        Args:
            user: User object
            device_id: Device identifier
            token: TOTP token from user

        Returns:
            True if verification successful
        """
        try:
            # Get device data (from database in production)
            # For now, we'll simulate getting the secret
            device_data = self._get_device_data(device_id)

            if not device_data or device_data["user_id"] != user.id:
                return False

            secret = device_data["secret_key"]
            totp = pyotp.TOTP(secret)

            # Verify token (with window for clock skew)
            if totp.verify(token, valid_window=1):
                # Activate device
                device_data["is_active"] = True
                device_data["last_used"] = datetime.utcnow()

                logger.info(f"TOTP verified and activated for user {user.id}")
                return True

            return False

        except Exception as e:
            logger.error(f"TOTP verification failed for user {user.id}: {str(e)}")
            return False

    async def setup_webauthn(self, user: User, device_name: str = "Security Key") -> Dict[str, Any]:
        """
        Set up WebAuthn/FIDO2 authentication

        Args:
            user: User object
            device_name: Human-readable device name

        Returns:
            WebAuthn registration options for client
        """
        try:
            # Generate registration options
            options = generate_registration_options(
                rp_id=self.rp_id,
                rp_name=self.rp_name,
                user_id=user.id.encode('utf-8'),
                user_name=user.email,
                user_display_name=user.full_name or user.email,
                authenticator_selection=AuthenticatorSelectionCriteria(
                    user_verification=UserVerificationRequirement.PREFERRED
                )
            )

            # Store challenge for verification
            challenge_id = f"webauthn_{secrets.token_hex(16)}"
            challenge_data = {
                "id": challenge_id,
                "user_id": user.id,
                "challenge_type": "webauthn_registration",
                "challenge_data": {
                    "challenge": base64.b64encode(options.challenge).decode(),
                    "device_name": device_name
                },
                "expires_at": datetime.utcnow() + timedelta(minutes=5)
            }

            # In production, save to database
            logger.info(f"WebAuthn registration initiated for user {user.id}")

            return {
                "challenge_id": challenge_id,
                "options": {
                    "challenge": base64.b64encode(options.challenge).decode(),
                    "rp": {"id": options.rp.id, "name": options.rp.name},
                    "user": {
                        "id": base64.b64encode(options.user.id).decode(),
                        "name": options.user.name,
                        "displayName": options.user.display_name
                    },
                    "pubKeyCredParams": [
                        {"type": "public-key", "alg": param.alg}
                        for param in options.pub_key_cred_params
                    ],
                    "timeout": options.timeout,
                    "attestation": options.attestation,
                    "authenticatorSelection": {
                        "userVerification": options.authenticator_selection.user_verification
                    }
                }
            }

        except Exception as e:
            logger.error(f"WebAuthn setup failed for user {user.id}: {str(e)}")
            raise

    async def verify_webauthn_registration(
        self,
        user: User,
        challenge_id: str,
        credential: Dict[str, Any]
    ) -> bool:
        """
        Verify WebAuthn registration response

        Args:
            user: User object
            challenge_id: Challenge identifier
            credential: WebAuthn credential from client

        Returns:
            True if registration successful
        """
        try:
            # Get challenge data
            challenge_data = self._get_challenge_data(challenge_id)
            if not challenge_data or challenge_data["user_id"] != user.id:
                return False

            challenge = base64.b64decode(challenge_data["challenge_data"]["challenge"])

            # Verify registration response
            verification = verify_registration_response(
                credential=RegistrationCredential.parse_raw(credential),
                expected_challenge=challenge,
                expected_origin=f"https://{self.rp_id}",
                expected_rp_id=self.rp_id
            )

            if verification.verified:
                # Store credential
                device_id = f"webauthn_{secrets.token_hex(16)}"
                device_data = {
                    "id": device_id,
                    "user_id": user.id,
                    "device_type": "webauthn",
                    "device_name": challenge_data["challenge_data"]["device_name"],
                    "credential_id": base64.b64encode(verification.credential_id).decode(),
                    "public_key": base64.b64encode(verification.credential_public_key).decode(),
                    "counter": verification.sign_count,
                    "is_active": True
                }

                # Mark challenge as used
                challenge_data["is_used"] = True

                logger.info(f"WebAuthn registration successful for user {user.id}")
                return True

            return False

        except Exception as e:
            logger.error(f"WebAuthn registration verification failed: {str(e)}")
            return False

    async def initiate_totp_auth(self, user: User) -> Dict[str, Any]:
        """
        Initiate TOTP authentication

        Args:
            user: User object

        Returns:
            Challenge information
        """
        try:
            # Check if user has TOTP device
            devices = self._get_user_devices(user.id, "totp")
            if not devices:
                raise ValueError("No TOTP device found for user")

            challenge_id = f"totp_{secrets.token_hex(16)}"
            challenge_data = {
                "id": challenge_id,
                "user_id": user.id,
                "challenge_type": "totp_auth",
                "expires_at": datetime.utcnow() + timedelta(minutes=5)
            }

            return {
                "challenge_id": challenge_id,
                "method": "totp",
                "message": "Enter code from your authenticator app"
            }

        except Exception as e:
            logger.error(f"TOTP auth initiation failed: {str(e)}")
            raise

    async def verify_totp_auth(self, user: User, challenge_id: str, token: str) -> bool:
        """
        Verify TOTP authentication token

        Args:
            user: User object
            challenge_id: Challenge identifier
            token: TOTP token

        Returns:
            True if authentication successful
        """
        try:
            # Get challenge and verify it's valid
            challenge_data = self._get_challenge_data(challenge_id)
            if not challenge_data or challenge_data["user_id"] != user.id:
                return False

            # Get user's TOTP devices
            devices = self._get_user_devices(user.id, "totp")

            for device in devices:
                if not device["is_active"]:
                    continue

                secret = device["secret_key"]
                totp = pyotp.TOTP(secret)

                if totp.verify(token, valid_window=1):
                    # Update last used
                    device["last_used"] = datetime.utcnow()

                    # Mark challenge as used
                    challenge_data["is_used"] = True

                    logger.info(f"TOTP authentication successful for user {user.id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"TOTP authentication failed: {str(e)}")
            return False

    async def verify_backup_code(self, user: User, code: str) -> bool:
        """
        Verify backup recovery code

        Args:
            user: User object
            code: Backup code

        Returns:
            True if code is valid
        """
        try:
            devices = self._get_user_devices(user.id)

            for device in devices:
                if device.get("backup_codes"):
                    backup_codes = device["backup_codes"]
                    if code in backup_codes:
                        # Remove used code
                        backup_codes.remove(code)
                        device["backup_codes"] = backup_codes

                        logger.info(f"Backup code used for user {user.id}")
                        return True

            return False

        except Exception as e:
            logger.error(f"Backup code verification failed: {str(e)}")
            return False

    def _generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup recovery codes"""
        codes = []
        for _ in range(count):
            code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
            # Format as XXXX-XXXX for readability
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        return codes

    def _get_device_data(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device data by ID (mock implementation)"""
        # In production, this would query the database
        # For now, return None to simulate no device found
        return None

    def _get_challenge_data(self, challenge_id: str) -> Optional[Dict[str, Any]]:
        """Get challenge data by ID (mock implementation)"""
        # In production, this would query the database
        return None

    def _get_user_devices(self, user_id: str, device_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user's MFA devices (mock implementation)"""
        # In production, this would query the database
        return []

    async def get_user_mfa_status(self, user: User) -> Dict[str, Any]:
        """
        Get user's MFA configuration status

        Args:
            user: User object

        Returns:
            MFA status information
        """
        try:
            devices = self._get_user_devices(user.id)

            totp_devices = [d for d in devices if d["device_type"] == "totp" and d["is_active"]]
            webauthn_devices = [d for d in devices if d["device_type"] == "webauthn" and d["is_active"]]

            return {
                "mfa_enabled": len(devices) > 0,
                "totp_configured": len(totp_devices) > 0,
                "webauthn_configured": len(webauthn_devices) > 0,
                "backup_codes_available": any(d.get("backup_codes") for d in devices),
                "devices": [
                    {
                        "id": d["id"],
                        "name": d["device_name"],
                        "type": d["device_type"],
                        "last_used": d.get("last_used"),
                        "created_at": d["created_at"]
                    }
                    for d in devices if d["is_active"]
                ]
            }

        except Exception as e:
            logger.error(f"Failed to get MFA status for user {user.id}: {str(e)}")
            raise

# Global MFA service instance
mfa_service = MFAService()