"""
Storage Factory - Provider-agnostic storage service
Allows switching between storage providers based on configuration
Perfect for bootstrapping with free tiers
"""

import os
from typing import Dict, Any, BinaryIO, Optional, Protocol
from enum import Enum


class StorageProvider(str, Enum):
    """Supported storage providers with security ratings"""
    AWS_S3 = "s3"  # Enterprise-grade, HIPAA/SOC2 compliant
    SUPABASE = "supabase"  # RLS security, GDPR compliant, 1GB free
    CLOUDFLARE_R2 = "r2"  # S3-compatible, 10GB free, no egress fees
    LOCAL = "local"  # Development only, not for production


class StorageServiceProtocol(Protocol):
    """Protocol defining required methods for any storage service"""

    def upload_document(
        self,
        file: BinaryIO,
        filename: str,
        organization_id: str,
        deal_id: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Upload a document with security features"""
        ...

    def generate_signed_url(
        self,
        storage_path: str,
        expiration: int = 3600,
        download: bool = False
    ) -> Optional[str]:
        """Generate time-limited signed URL"""
        ...

    def delete_document(self, storage_path: str) -> bool:
        """Delete a document"""
        ...

    def copy_document(
        self,
        source_path: str,
        organization_id: str,
        deal_id: Optional[str],
        new_filename: str
    ) -> Dict[str, Any]:
        """Copy a document for versioning"""
        ...


class StorageFactory:
    """
    Factory for creating storage service instances based on configuration

    Security considerations for each provider:
    - Cloudflare R2: S3-compatible security, global CDN, DDoS protection
    - AWS S3: HIPAA, SOC2, ISO 27001 compliant
    - Supabase: RLS, GDPR compliant, encryption at rest
    """

    @staticmethod
    def create_storage_service() -> StorageServiceProtocol:
        """
        Create storage service based on environment configuration

        Priority for 100daysandbeyond.com (Cloudflare ecosystem):
        1. Cloudflare R2 (preferred - already using Cloudflare)
        2. AWS S3 (fallback for enterprise)
        3. Supabase (alternative free option)
        """
        provider = os.getenv('STORAGE_PROVIDER', 'r2').lower()

        # PRIMARY: Use Cloudflare R2 (best for Cloudflare ecosystem)
        if provider == 'r2' or os.getenv('R2_ACCESS_KEY_ID'):
            if os.getenv('CLOUDFLARE_ACCOUNT_ID') and os.getenv('R2_ACCESS_KEY_ID'):
                from app.services.r2_storage_service import get_r2_storage_service
                return get_r2_storage_service()

        # FALLBACK 1: Use AWS S3 if explicitly configured
        if provider == 's3' and os.getenv('AWS_ACCESS_KEY_ID'):
            from app.services.s3_service import s3_service
            return s3_service

        # FALLBACK 2: Use Supabase if configured (removed - not using Supabase)
        # if provider == 'supabase':
        #     if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_ANON_KEY'):
        #         from app.services.supabase_storage_service import supabase_storage_service
        #         return supabase_storage_service

        # Try any available provider
        if os.getenv('R2_ACCESS_KEY_ID'):
            from app.services.r2_storage_service import r2_storage_service
            return r2_storage_service

        if os.getenv('AWS_ACCESS_KEY_ID'):
            from app.services.s3_service import s3_service
            return s3_service

        # Supabase removed - not using it
        # if os.getenv('SUPABASE_URL'):
        #     from app.services.supabase_storage_service import supabase_storage_service
        #     return supabase_storage_service

        # Default to R2 (show configuration needed)
        raise ValueError(
            "No storage provider configured. For Cloudflare R2, set:\n"
            "STORAGE_PROVIDER=r2\n"
            "CLOUDFLARE_ACCOUNT_ID=your-account-id\n"
            "R2_ACCESS_KEY_ID=your-access-key\n"
            "R2_SECRET_ACCESS_KEY=your-secret-key\n"
            "R2_BUCKET_NAME=ma-platform-documents"
        )

    @staticmethod
    def get_provider_info() -> Dict[str, Any]:
        """Get information about the current storage provider"""
        provider = os.getenv('STORAGE_PROVIDER', 'r2').lower()

        provider_info = {
            'r2': {
                'name': 'Cloudflare R2',
                'free_tier': '10GB storage/month, UNLIMITED egress',
                'security': 'DDoS protection, global CDN, encryption at rest',
                'best_for': '100daysandbeyond.com - Already in Cloudflare ecosystem',
                'limits': '5TB per file',
                'advantages': [
                    '✅ Zero egress fees (saves $$$)',
                    '✅ Integrated with existing Cloudflare setup',
                    '✅ 285+ edge locations worldwide',
                    '✅ Automatic DDoS protection',
                    '✅ S3-compatible API'
                ]
            },
            's3': {
                'name': 'AWS S3',
                'free_tier': '5GB storage (12 months only)',
                'security': 'Enterprise-grade, HIPAA/SOC2/ISO compliant',
                'best_for': 'Enterprise compliance requirements',
                'limits': '5TB per file',
                'disadvantages': [
                    '❌ Expensive egress fees ($0.09/GB)',
                    '❌ Complex pricing',
                    '❌ Only 12 months free'
                ]
            },
            'supabase': {
                'name': 'Supabase Storage',
                'free_tier': '1GB storage + 2GB bandwidth/month',
                'security': 'RLS, GDPR compliant, encryption at rest',
                'best_for': 'Small projects, integrated auth',
                'limits': '50MB per file on free tier'
            }
        }

        current_provider = provider_info.get(provider, provider_info['r2'])
        current_provider['active'] = True
        current_provider['provider_key'] = provider

        return current_provider


# Global storage service instance (lazy-loaded)
_storage_service = None
_storage_info = None

def get_storage_service():
    """Get the storage service instance (lazy-loaded)"""
    global _storage_service
    if _storage_service is None:
        from dotenv import load_dotenv
        load_dotenv()  # Ensure env vars are loaded
        _storage_service = StorageFactory.create_storage_service()
    return _storage_service

def get_storage_info():
    """Get storage provider info (lazy-loaded)"""
    global _storage_info
    if _storage_info is None:
        from dotenv import load_dotenv
        load_dotenv()  # Ensure env vars are loaded
        _storage_info = StorageFactory.get_provider_info()
    return _storage_info

# For backward compatibility - lazy loading
storage_service = None  # Will be set by get_storage_service() when first needed
storage_info = None     # Will be set by get_storage_info() when first needed