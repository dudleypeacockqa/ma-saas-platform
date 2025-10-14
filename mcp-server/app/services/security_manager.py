"""
BMAD v6 Security Manager Service
Centralized API key management and authentication for MCP server
"""

import os
import jwt
import hashlib
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class SecurityManager:
    """Centralized security management for BMAD v6 MCP server."""
    
    def __init__(self):
        self.api_keys: Dict[str, str] = {}
        self.encrypted_keys: Dict[str, bytes] = {}
        self.access_tokens: Dict[str, Dict[str, Any]] = {}
        
        # Initialize encryption
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        logger.info("Initialized BMAD v6 Security Manager")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for API key storage."""
        key_env = os.getenv("MCP_ENCRYPTION_KEY")
        if key_env:
            return key_env.encode()
        
        # Generate new key (in production, this should be stored securely)
        key = Fernet.generate_key()
        logger.warning("Generated new encryption key - store securely in production")
        return key
    
    async def initialize(self):
        """Initialize security manager with environment variables."""
        
        # Load API keys from environment
        api_key_mappings = {
            "stripe": "STRIPE_SECRET_KEY",
            "clerk": "CLERK_SECRET_KEY", 
            "sendgrid": "SENDGRID_API_KEY",
            "huggingface": "HUGGINGFACE_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY"
        }
        
        for service, env_var in api_key_mappings.items():
            api_key = os.getenv(env_var)
            if api_key:
                await self.store_api_key(service, api_key)
                logger.info(f"Loaded API key for service: {service}")
            else:
                logger.warning(f"API key not found for service: {service} (env: {env_var})")
    
    async def store_api_key(self, service: str, api_key: str) -> bool:
        """Store API key securely with encryption."""
        try:
            # Encrypt the API key
            encrypted_key = self.cipher_suite.encrypt(api_key.encode())
            self.encrypted_keys[service] = encrypted_key
            
            # Store hash for validation
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            self.api_keys[service] = key_hash
            
            logger.info(f"Stored encrypted API key for service: {service}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store API key for {service}: {str(e)}")
            return False
    
    async def get_api_key(self, service: str) -> Optional[str]:
        """Retrieve and decrypt API key for service."""
        try:
            encrypted_key = self.encrypted_keys.get(service)
            if not encrypted_key:
                logger.warning(f"No API key found for service: {service}")
                return None
            
            # Decrypt the API key
            decrypted_key = self.cipher_suite.decrypt(encrypted_key).decode()
            return decrypted_key
            
        except Exception as e:
            logger.error(f"Failed to retrieve API key for {service}: {str(e)}")
            return None
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT access token."""
        try:
            # In production, use proper JWT secret from environment
            jwt_secret = os.getenv("JWT_SECRET", "bmad-v6-mcp-secret")
            
            # Decode and validate token
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            
            # Check expiration
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                raise ValueError("Token expired")
            
            return payload
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise ValueError("Invalid token")
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            raise ValueError("Token validation failed")
    
    async def generate_token(self, user_id: str, permissions: List[str] = None) -> str:
        """Generate JWT access token."""
        try:
            jwt_secret = os.getenv("JWT_SECRET", "bmad-v6-mcp-secret")
            
            payload = {
                "user_id": user_id,
                "permissions": permissions or [],
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            
            token = jwt.encode(payload, jwt_secret, algorithm="HS256")
            
            # Store token info
            self.access_tokens[token] = {
                "user_id": user_id,
                "permissions": permissions,
                "created_at": datetime.utcnow()
            }
            
            return token
            
        except Exception as e:
            logger.error(f"Token generation error: {str(e)}")
            raise ValueError("Token generation failed")
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke access token."""
        try:
            if token in self.access_tokens:
                del self.access_tokens[token]
                logger.info("Token revoked successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Token revocation error: {str(e)}")
            return False
    
    async def audit_log(self, action: str, user_id: str, details: Dict[str, Any] = None):
        """Log security-related actions for audit trail."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "details": details or {},
            "ip_address": details.get("ip_address") if details else None
        }
        
        # In production, store in secure audit log database
        logger.info(f"AUDIT: {audit_entry}")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security manager statistics."""
        return {
            "stored_api_keys": len(self.api_keys),
            "active_tokens": len(self.access_tokens),
            "encryption_enabled": bool(self.encryption_key)
        }

