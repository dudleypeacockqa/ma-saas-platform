"""
Mobile Authentication Service
Enhanced authentication for mobile devices and PWAs
"""

import jwt
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import secrets
import hashlib
import asyncio

logger = logging.getLogger(__name__)


class DeviceType(str, Enum):
    """Mobile device types"""
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    PWA = "pwa"
    TABLET = "tablet"
    DESKTOP = "desktop"


class AuthMethod(str, Enum):
    """Authentication methods for mobile"""
    PASSWORD = "password"
    BIOMETRIC = "biometric"
    PIN = "pin"
    PATTERN = "pattern"
    FACE_ID = "face_id"
    TOUCH_ID = "touch_id"
    VOICE = "voice"
    WEBAUTHN = "webauthn"


@dataclass
class MobileDevice:
    """Mobile device registration"""
    device_id: str
    user_id: str
    organization_id: str
    device_type: DeviceType
    device_name: str
    os_version: str
    app_version: str
    push_token: Optional[str]
    biometric_enabled: bool
    last_login: datetime
    created_at: datetime
    is_trusted: bool = False
    auth_methods: List[AuthMethod] = None

    def __post_init__(self):
        if self.auth_methods is None:
            self.auth_methods = [AuthMethod.PASSWORD]


@dataclass
class BiometricData:
    """Biometric authentication data"""
    device_id: str
    user_id: str
    biometric_type: AuthMethod
    public_key: str
    challenge: str
    created_at: datetime
    last_used: Optional[datetime] = None
    use_count: int = 0


@dataclass
class MobileSession:
    """Mobile authentication session"""
    session_id: str
    user_id: str
    organization_id: str
    device_id: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    refresh_expires_at: datetime
    created_at: datetime
    last_activity: datetime
    is_active: bool = True


class MobileAuthService:
    """Service for mobile authentication management"""

    def __init__(self, jwt_secret: str = "your-jwt-secret"):
        self.jwt_secret = jwt_secret
        self.registered_devices: Dict[str, MobileDevice] = {}
        self.biometric_data: Dict[str, BiometricData] = {}
        self.active_sessions: Dict[str, MobileSession] = {}
        self.trusted_devices: Dict[str, List[str]] = {}  # user_id -> device_ids

    async def register_device(
        self,
        user_id: str,
        organization_id: str,
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register a new mobile device"""

        try:
            # Generate unique device ID
            device_id = self._generate_device_id(device_info)

            # Create device registration
            device = MobileDevice(
                device_id=device_id,
                user_id=user_id,
                organization_id=organization_id,
                device_type=DeviceType(device_info.get("device_type", "web")),
                device_name=device_info.get("device_name", "Unknown Device"),
                os_version=device_info.get("os_version", "Unknown"),
                app_version=device_info.get("app_version", "1.0.0"),
                push_token=device_info.get("push_token"),
                biometric_enabled=device_info.get("biometric_enabled", False),
                last_login=datetime.utcnow(),
                created_at=datetime.utcnow()
            )

            # Store device registration
            self.registered_devices[device_id] = device

            # Initialize trusted devices list if needed
            if user_id not in self.trusted_devices:
                self.trusted_devices[user_id] = []

            logger.info(f"Registered mobile device {device_id} for user {user_id}")

            return {
                "device_id": device_id,
                "status": "registered",
                "device_name": device.device_name,
                "biometric_available": device.biometric_enabled,
                "registered_at": device.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to register mobile device: {e}")
            raise

    async def authenticate_mobile(
        self,
        user_id: str,
        organization_id: str,
        device_id: str,
        auth_method: AuthMethod,
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Authenticate mobile device"""

        try:
            # Verify device is registered
            if device_id not in self.registered_devices:
                raise ValueError("Device not registered")

            device = self.registered_devices[device_id]

            # Verify user and organization match
            if device.user_id != user_id or device.organization_id != organization_id:
                raise ValueError("Invalid device credentials")

            # Authenticate based on method
            auth_success = False

            if auth_method == AuthMethod.PASSWORD:
                auth_success = await self._authenticate_password(credentials)
            elif auth_method == AuthMethod.BIOMETRIC:
                auth_success = await self._authenticate_biometric(device_id, credentials)
            elif auth_method == AuthMethod.PIN:
                auth_success = await self._authenticate_pin(device_id, credentials)
            elif auth_method == AuthMethod.WEBAUTHN:
                auth_success = await self._authenticate_webauthn(device_id, credentials)
            else:
                raise ValueError(f"Unsupported authentication method: {auth_method}")

            if not auth_success:
                raise ValueError("Authentication failed")

            # Create mobile session
            session = await self._create_mobile_session(user_id, organization_id, device_id)

            # Update device last login
            device.last_login = datetime.utcnow()

            # Check if device should be trusted
            if not device.is_trusted and self._should_trust_device(device):
                device.is_trusted = True
                self.trusted_devices[user_id].append(device_id)

            logger.info(f"Mobile authentication successful for user {user_id} on device {device_id}")

            return {
                "status": "authenticated",
                "session_id": session.session_id,
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "expires_at": session.expires_at.isoformat(),
                "device_trusted": device.is_trusted,
                "biometric_available": device.biometric_enabled
            }

        except Exception as e:
            logger.error(f"Mobile authentication failed: {e}")
            raise

    async def setup_biometric_auth(
        self,
        user_id: str,
        device_id: str,
        biometric_type: AuthMethod,
        public_key: str
    ) -> bool:
        """Set up biometric authentication for device"""

        try:
            # Verify device exists and belongs to user
            if device_id not in self.registered_devices:
                return False

            device = self.registered_devices[device_id]
            if device.user_id != user_id:
                return False

            # Generate challenge
            challenge = secrets.token_urlsafe(32)

            # Store biometric data
            biometric_data = BiometricData(
                device_id=device_id,
                user_id=user_id,
                biometric_type=biometric_type,
                public_key=public_key,
                challenge=challenge,
                created_at=datetime.utcnow()
            )

            self.biometric_data[f"{device_id}_{biometric_type}"] = biometric_data

            # Update device
            device.biometric_enabled = True
            if biometric_type not in device.auth_methods:
                device.auth_methods.append(biometric_type)

            logger.info(f"Set up {biometric_type} authentication for device {device_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to setup biometric auth: {e}")
            return False

    async def refresh_mobile_session(
        self,
        refresh_token: str
    ) -> Dict[str, Any]:
        """Refresh mobile session using refresh token"""

        try:
            # Find session by refresh token
            session = None
            for sess in self.active_sessions.values():
                if sess.refresh_token == refresh_token and sess.is_active:
                    session = sess
                    break

            if not session:
                raise ValueError("Invalid refresh token")

            # Check if refresh token is expired
            if datetime.utcnow() > session.refresh_expires_at:
                session.is_active = False
                raise ValueError("Refresh token expired")

            # Generate new access token
            new_access_token = self._generate_access_token(
                session.user_id,
                session.organization_id,
                session.device_id
            )

            # Update session
            session.access_token = new_access_token
            session.expires_at = datetime.utcnow() + timedelta(hours=1)
            session.last_activity = datetime.utcnow()

            logger.info(f"Refreshed mobile session for user {session.user_id}")

            return {
                "status": "refreshed",
                "access_token": new_access_token,
                "expires_at": session.expires_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to refresh mobile session: {e}")
            raise

    async def logout_mobile_device(
        self,
        user_id: str,
        device_id: str,
        session_id: Optional[str] = None
    ) -> bool:
        """Logout from mobile device"""

        try:
            if session_id:
                # Logout specific session
                if session_id in self.active_sessions:
                    session = self.active_sessions[session_id]
                    if session.user_id == user_id and session.device_id == device_id:
                        session.is_active = False
                        del self.active_sessions[session_id]
                        return True
            else:
                # Logout all sessions for device
                sessions_to_remove = []
                for sess_id, session in self.active_sessions.items():
                    if session.user_id == user_id and session.device_id == device_id:
                        session.is_active = False
                        sessions_to_remove.append(sess_id)

                for sess_id in sessions_to_remove:
                    del self.active_sessions[sess_id]

                return len(sessions_to_remove) > 0

            return False

        except Exception as e:
            logger.error(f"Failed to logout mobile device: {e}")
            return False

    async def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all registered devices for user"""

        devices = []
        for device in self.registered_devices.values():
            if device.user_id == user_id:
                # Count active sessions for device
                active_sessions = len([
                    s for s in self.active_sessions.values()
                    if s.user_id == user_id and s.device_id == device.device_id and s.is_active
                ])

                devices.append({
                    "device_id": device.device_id,
                    "device_name": device.device_name,
                    "device_type": device.device_type,
                    "os_version": device.os_version,
                    "app_version": device.app_version,
                    "is_trusted": device.is_trusted,
                    "biometric_enabled": device.biometric_enabled,
                    "auth_methods": [method.value for method in device.auth_methods],
                    "last_login": device.last_login.isoformat(),
                    "active_sessions": active_sessions,
                    "created_at": device.created_at.isoformat()
                })

        return devices

    async def revoke_device_access(self, user_id: str, device_id: str) -> bool:
        """Revoke access for a specific device"""

        try:
            # Remove device registration
            if device_id in self.registered_devices:
                device = self.registered_devices[device_id]
                if device.user_id == user_id:
                    del self.registered_devices[device_id]

                    # Remove from trusted devices
                    if user_id in self.trusted_devices:
                        self.trusted_devices[user_id] = [
                            d for d in self.trusted_devices[user_id] if d != device_id
                        ]

                    # Deactivate all sessions for device
                    await self.logout_mobile_device(user_id, device_id)

                    # Remove biometric data
                    biometric_keys_to_remove = [
                        key for key in self.biometric_data.keys()
                        if key.startswith(f"{device_id}_")
                    ]
                    for key in biometric_keys_to_remove:
                        del self.biometric_data[key]

                    logger.info(f"Revoked access for device {device_id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Failed to revoke device access: {e}")
            return False

    def _generate_device_id(self, device_info: Dict[str, Any]) -> str:
        """Generate unique device ID"""

        # Create a hash based on device characteristics
        device_string = f"{device_info.get('device_name', '')}-{device_info.get('os_version', '')}-{device_info.get('hardware_id', '')}-{datetime.utcnow().timestamp()}"
        return hashlib.sha256(device_string.encode()).hexdigest()[:16]

    async def _create_mobile_session(
        self,
        user_id: str,
        organization_id: str,
        device_id: str
    ) -> MobileSession:
        """Create new mobile session"""

        session_id = secrets.token_urlsafe(32)
        access_token = self._generate_access_token(user_id, organization_id, device_id)
        refresh_token = secrets.token_urlsafe(32)

        session = MobileSession(
            session_id=session_id,
            user_id=user_id,
            organization_id=organization_id,
            device_id=device_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            refresh_expires_at=datetime.utcnow() + timedelta(days=30),
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )

        self.active_sessions[session_id] = session
        return session

    def _generate_access_token(
        self,
        user_id: str,
        organization_id: str,
        device_id: str
    ) -> str:
        """Generate JWT access token"""

        payload = {
            "user_id": user_id,
            "organization_id": organization_id,
            "device_id": device_id,
            "iat": datetime.utcnow().timestamp(),
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
            "type": "mobile_access"
        }

        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    async def _authenticate_password(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate using password"""
        # Mock implementation - would verify against actual user store
        password = credentials.get("password")
        return password is not None and len(password) >= 6

    async def _authenticate_biometric(self, device_id: str, credentials: Dict[str, Any]) -> bool:
        """Authenticate using biometric data"""
        # Mock implementation - would verify biometric signature
        biometric_type = credentials.get("biometric_type")
        signature = credentials.get("signature")

        biometric_key = f"{device_id}_{biometric_type}"
        if biometric_key in self.biometric_data:
            biometric_data = self.biometric_data[biometric_key]
            biometric_data.last_used = datetime.utcnow()
            biometric_data.use_count += 1
            return signature is not None  # Mock validation

        return False

    async def _authenticate_pin(self, device_id: str, credentials: Dict[str, Any]) -> bool:
        """Authenticate using PIN"""
        # Mock implementation - would verify PIN hash
        pin = credentials.get("pin")
        return pin is not None and len(pin) >= 4

    async def _authenticate_webauthn(self, device_id: str, credentials: Dict[str, Any]) -> bool:
        """Authenticate using WebAuthn"""
        # Mock implementation - would verify WebAuthn assertion
        assertion = credentials.get("assertion")
        return assertion is not None

    def _should_trust_device(self, device: MobileDevice) -> bool:
        """Determine if device should be trusted"""
        # Trust device if it has been used multiple times and has biometric auth
        login_count = 5  # Mock - would track actual login count
        return login_count >= 3 and device.biometric_enabled


# Global mobile auth service instance
mobile_auth_service: Optional[MobileAuthService] = None

def get_mobile_auth_service() -> MobileAuthService:
    """Get the global mobile auth service instance"""
    global mobile_auth_service
    if mobile_auth_service is None:
        mobile_auth_service = MobileAuthService()
    return mobile_auth_service