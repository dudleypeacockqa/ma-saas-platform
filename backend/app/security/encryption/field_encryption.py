"""
Field-Level Encryption Service
AES-256 encryption for sensitive financial data
"""

import os
import base64
from typing import Optional, Dict, Any, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets
import logging
from datetime import datetime, timedelta
from sqlalchemy import Column, String, LargeBinary, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

class EncryptionKey(Base):
    """Database model for encryption key metadata"""
    __tablename__ = "encryption_keys"

    key_id = Column(String(64), primary_key=True)
    key_type = Column(String(50), nullable=False)  # field, document, backup
    algorithm = Column(String(50), nullable=False, default="AES-256-GCM")
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    hsm_key_id = Column(String(255))  # Reference to HSM key
    salt = Column(LargeBinary)

class FieldEncryptionService:
    """
    Enterprise-grade field-level encryption service
    Supports AES-256-GCM with key rotation and HSM integration
    """

    def __init__(self):
        self.algorithm = "AES-256-GCM"
        self.key_cache: Dict[str, bytes] = {}
        self.salt_cache: Dict[str, bytes] = {}

    def generate_key(self, key_type: str = "field") -> tuple[str, bytes]:
        """
        Generate new encryption key with metadata

        Args:
            key_type: Type of key (field, document, backup)

        Returns:
            Tuple of (key_id, key_bytes)
        """
        try:
            key_id = f"{key_type}_{secrets.token_hex(16)}"
            key_bytes = AESGCM.generate_key(bit_length=256)
            salt = os.urandom(16)

            # Store key metadata (not the actual key)
            expires_at = datetime.utcnow() + timedelta(days=30)

            # In production, this would integrate with HSM
            # For now, we'll use environment-based key derivation

            self.key_cache[key_id] = key_bytes
            self.salt_cache[key_id] = salt

            logger.info(f"Generated new encryption key: {key_id}")
            return key_id, key_bytes

        except Exception as e:
            logger.error(f"Key generation failed: {str(e)}")
            raise

    def derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2

        Args:
            password: Master password
            salt: Cryptographic salt

        Returns:
            Derived key bytes
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
        )
        return kdf.derive(password.encode())

    def encrypt_field(
        self,
        data: Union[str, int, float, Dict[str, Any]],
        key_id: Optional[str] = None,
        additional_data: Optional[bytes] = None
    ) -> Dict[str, str]:
        """
        Encrypt field data with AES-256-GCM

        Args:
            data: Data to encrypt
            key_id: Encryption key identifier
            additional_data: Additional authenticated data

        Returns:
            Dictionary with encrypted data and metadata
        """
        try:
            # Convert data to string for encryption
            if isinstance(data, (dict, list)):
                import json
                plaintext = json.dumps(data, sort_keys=True)
            else:
                plaintext = str(data)

            # Get or generate encryption key
            if not key_id:
                key_id, key_bytes = self.generate_key("field")
            else:
                key_bytes = self._get_key(key_id)

            # Generate nonce (96 bits for GCM)
            nonce = os.urandom(12)

            # Encrypt with AES-GCM
            aesgcm = AESGCM(key_bytes)
            ciphertext = aesgcm.encrypt(
                nonce,
                plaintext.encode('utf-8'),
                additional_data
            )

            # Return encrypted data with metadata
            return {
                "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
                "nonce": base64.b64encode(nonce).decode('utf-8'),
                "key_id": key_id,
                "algorithm": self.algorithm,
                "encrypted_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Field encryption failed: {str(e)}")
            raise

    def decrypt_field(
        self,
        encrypted_data: Dict[str, str],
        additional_data: Optional[bytes] = None
    ) -> Union[str, int, float, Dict[str, Any]]:
        """
        Decrypt field data

        Args:
            encrypted_data: Encrypted data dictionary
            additional_data: Additional authenticated data

        Returns:
            Decrypted original data
        """
        try:
            # Extract encryption metadata
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            nonce = base64.b64decode(encrypted_data["nonce"])
            key_id = encrypted_data["key_id"]

            # Get decryption key
            key_bytes = self._get_key(key_id)

            # Decrypt with AES-GCM
            aesgcm = AESGCM(key_bytes)
            plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, additional_data)
            plaintext = plaintext_bytes.decode('utf-8')

            # Try to parse as JSON (for complex data types)
            try:
                import json
                return json.loads(plaintext)
            except json.JSONDecodeError:
                # Return as string if not JSON
                # Try to convert back to original type
                try:
                    # Try int
                    if plaintext.isdigit():
                        return int(plaintext)
                    # Try float
                    return float(plaintext)
                except ValueError:
                    return plaintext

        except Exception as e:
            logger.error(f"Field decryption failed: {str(e)}")
            raise

    def _get_key(self, key_id: str) -> bytes:
        """
        Retrieve encryption key by ID

        Args:
            key_id: Key identifier

        Returns:
            Key bytes
        """
        # Check cache first
        if key_id in self.key_cache:
            return self.key_cache[key_id]

        # In production, this would retrieve from HSM or secure key store
        # For now, derive from environment variable
        master_key = settings.ENCRYPTION_MASTER_KEY
        if not master_key:
            raise ValueError("Master encryption key not configured")

        salt = self.salt_cache.get(key_id, b'default_salt_change_in_prod')
        key_bytes = self.derive_key_from_password(f"{master_key}_{key_id}", salt)

        # Cache for performance
        self.key_cache[key_id] = key_bytes
        return key_bytes

    def rotate_key(self, old_key_id: str) -> str:
        """
        Rotate encryption key and return new key ID

        Args:
            old_key_id: Current key identifier

        Returns:
            New key identifier
        """
        try:
            # Generate new key
            new_key_id, new_key_bytes = self.generate_key("field")

            # Mark old key as inactive (don't delete - needed for decryption)
            # In production, this would update database

            logger.info(f"Key rotated from {old_key_id} to {new_key_id}")
            return new_key_id

        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            raise

    def encrypt_financial_data(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive financial fields

        Args:
            financial_data: Dictionary containing financial information

        Returns:
            Dictionary with encrypted sensitive fields
        """
        sensitive_fields = [
            "purchase_price",
            "valuation",
            "revenue",
            "ebitda",
            "debt",
            "equity_value",
            "irr",
            "multiple",
            "synergies"
        ]

        encrypted_data = financial_data.copy()

        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field] is not None:
                # Add field name as additional authenticated data
                additional_data = f"field:{field}".encode('utf-8')
                encrypted_data[field] = self.encrypt_field(
                    encrypted_data[field],
                    additional_data=additional_data
                )

        return encrypted_data

    def decrypt_financial_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt financial data fields

        Args:
            encrypted_data: Dictionary with encrypted financial fields

        Returns:
            Dictionary with decrypted financial data
        """
        decrypted_data = encrypted_data.copy()

        for field, value in encrypted_data.items():
            if isinstance(value, dict) and "ciphertext" in value:
                # This is an encrypted field
                additional_data = f"field:{field}".encode('utf-8')
                decrypted_data[field] = self.decrypt_field(value, additional_data)

        return decrypted_data

    def create_searchable_hash(self, data: str, key_id: str) -> str:
        """
        Create searchable hash for encrypted data
        Allows searching without decryption

        Args:
            data: Original data
            key_id: Encryption key identifier

        Returns:
            Searchable hash
        """
        try:
            # Use HMAC for deterministic but secure hashing
            import hmac

            key_bytes = self._get_key(key_id)
            search_hash = hmac.new(
                key_bytes,
                data.lower().encode('utf-8'),  # Case-insensitive
                hashes.SHA256()
            ).hexdigest()

            return search_hash

        except Exception as e:
            logger.error(f"Searchable hash creation failed: {str(e)}")
            raise

# Global encryption service instance
encryption_service = FieldEncryptionService()

# Helper functions for easy integration
def encrypt_sensitive_field(data: Any, field_name: str) -> Dict[str, str]:
    """Helper function to encrypt a single field"""
    additional_data = f"field:{field_name}".encode('utf-8')
    return encryption_service.encrypt_field(data, additional_data=additional_data)

def decrypt_sensitive_field(encrypted_data: Dict[str, str], field_name: str) -> Any:
    """Helper function to decrypt a single field"""
    additional_data = f"field:{field_name}".encode('utf-8')
    return encryption_service.decrypt_field(encrypted_data, additional_data)

def encrypt_financial_record(financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to encrypt financial record"""
    return encryption_service.encrypt_financial_data(financial_data)

def decrypt_financial_record(encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to decrypt financial record"""
    return encryption_service.decrypt_financial_data(encrypted_data)