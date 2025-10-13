"""
Cloudflare R2 Storage Service - S3-compatible with superior pricing
Perfect for bootstrapping and scaling within Cloudflare ecosystem
Story 3.1: Document Upload API - Cloudflare R2 integration
"""

import os
import uuid
import mimetypes
import hashlib
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta
import json

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config

from app.core.config import settings


class R2StorageService:
    """
    Cloudflare R2 Storage Service

    Benefits over S3:
    - 10GB free storage (vs 5GB S3)
    - ZERO egress fees (vs $0.09/GB S3)
    - 10M Class A & 10M Class B operations free/month
    - Integrated with Cloudflare CDN and security
    - S3-compatible API for easy migration

    Security features:
    - Cloudflare Zero Trust integration
    - DDoS protection included
    - Global CDN with 285+ PoPs
    - Encryption at rest
    - Signed URLs for access control
    """

    def __init__(self):
        """Initialize R2 client using S3-compatible API"""
        # R2 credentials
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.access_key_id = os.getenv('R2_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('R2_BUCKET_NAME', 'ma-platform-documents')

        if not all([self.account_id, self.access_key_id, self.secret_access_key]):
            raise ValueError(
                "Cloudflare R2 credentials not configured. "
                "Please set CLOUDFLARE_ACCOUNT_ID, R2_ACCESS_KEY_ID, and R2_SECRET_ACCESS_KEY"
            )

        # R2 endpoint URL
        self.endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"

        # Initialize S3-compatible client for R2
        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name='auto',  # R2 uses 'auto' as region
            config=Config(
                signature_version='s3v4',
                retries={'max_attempts': 3, 'mode': 'standard'}
            )
        )

        # Custom domain for public access (if configured)
        self.public_domain = os.getenv('R2_PUBLIC_DOMAIN')  # e.g., 'docs.100daysandbeyond.com'

        # Defer bucket initialization until first use
        self._bucket_initialized = False

    def _ensure_bucket_exists(self):
        """Create R2 bucket if it doesn't exist - only called when bucket is actually needed"""
        if self._bucket_initialized:
            return

        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            print(f"R2 bucket '{self.bucket_name}' exists")
            self._bucket_initialized = True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                try:
                    # Create bucket in R2
                    self.client.create_bucket(Bucket=self.bucket_name)

                    # Configure bucket settings
                    self._configure_bucket()

                    print(f"Created R2 bucket '{self.bucket_name}'")
                    self._bucket_initialized = True
                except ClientError as create_error:
                    print(f"Failed to create bucket: {create_error}")
                    raise
            else:
                print(f"Bucket access error: {e}")

    def _configure_bucket(self):
        """Configure R2 bucket with security settings"""
        try:
            # Enable versioning for document history
            self.client.put_bucket_versioning(
                Bucket=self.bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )

            # Set lifecycle rules for old versions
            self.client.put_bucket_lifecycle_configuration(
                Bucket=self.bucket_name,
                LifecycleConfiguration={
                    'Rules': [
                        {
                            'ID': 'DeleteOldVersions',
                            'Status': 'Enabled',
                            'NoncurrentVersionExpiration': {
                                'NoncurrentDays': 90
                            }
                        },
                        {
                            'ID': 'AbortIncompleteMultipart',
                            'Status': 'Enabled',
                            'AbortIncompleteMultipartUpload': {
                                'DaysAfterInitiation': 7
                            }
                        }
                    ]
                }
            )

            # Configure CORS for browser uploads
            cors_config = {
                'CORSRules': [
                    {
                        'AllowedHeaders': ['*'],
                        'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                        'AllowedOrigins': [
                            'https://100daysandbeyond.com',
                            'https://*.100daysandbeyond.com',
                            'http://localhost:3000',  # Development
                            'http://localhost:5173'   # Vite dev server
                        ],
                        'ExposeHeaders': ['ETag', 'x-amz-server-side-encryption'],
                        'MaxAgeSeconds': 3600
                    }
                ]
            }
            self.client.put_bucket_cors(
                Bucket=self.bucket_name,
                CORSConfiguration=cors_config
            )

        except ClientError as e:
            print(f"Bucket configuration warning: {e}")

    def _generate_r2_key(self, organization_id: str, deal_id: Optional[str], filename: str) -> str:
        """
        Generate R2 object key with organization isolation
        Format: organizations/{org_id}/deals/{deal_id}/documents/{uuid}_{filename}
        """
        unique_id = uuid.uuid4().hex[:8]
        # Sanitize filename for security
        safe_filename = os.path.basename(filename).replace(' ', '_').replace('/', '_')

        if deal_id:
            return f"organizations/{organization_id}/deals/{deal_id}/documents/{unique_id}_{safe_filename}"
        else:
            return f"organizations/{organization_id}/documents/{unique_id}_{safe_filename}"

    def upload_document(
        self,
        file: BinaryIO,
        filename: str,
        organization_id: str,
        deal_id: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload document to Cloudflare R2

        Benefits:
        - No egress fees when users download
        - Automatic CDN distribution
        - DDoS protection included
        """
        # Ensure bucket exists before upload
        self._ensure_bucket_exists()

        try:
            # Generate R2 key
            r2_key = self._generate_r2_key(organization_id, deal_id, filename)

            # Detect content type
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = 'application/octet-stream'

            # Read file and calculate hash
            file_content = file.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
            file.seek(0)

            # Prepare metadata (R2 supports S3-style metadata)
            r2_metadata = {
                'organization_id': organization_id,
                'uploaded_at': datetime.utcnow().isoformat(),
                'original_filename': filename,
                'file_hash': file_hash
            }

            if deal_id:
                r2_metadata['deal_id'] = deal_id

            if metadata:
                r2_metadata.update(metadata)

            # Upload to R2 with server-side encryption
            response = self.client.put_object(
                Bucket=self.bucket_name,
                Key=r2_key,
                Body=file_content,
                ContentType=content_type,
                Metadata=r2_metadata,
                # R2 automatically encrypts at rest
                ServerSideEncryption='AES256',
                # Cache control for CDN
                CacheControl='private, max-age=31536000'
            )

            # Generate URL (use custom domain if configured)
            if self.public_domain:
                url = f"https://{self.public_domain}/{r2_key}"
            else:
                url = f"{self.endpoint_url}/{self.bucket_name}/{r2_key}"

            return {
                'success': True,
                'storage_provider': 'cloudflare_r2',
                'r2_bucket': self.bucket_name,
                'r2_key': r2_key,
                'r2_url': url,
                'r2_etag': response.get('ETag', '').strip('"'),
                'file_hash': file_hash,
                'file_size': len(file_content),
                'content_type': content_type
            }

        except NoCredentialsError:
            return {
                'success': False,
                'error': 'R2 credentials not configured'
            }
        except ClientError as e:
            return {
                'success': False,
                'error': f"R2 upload failed: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }

    def generate_presigned_url(
        self,
        r2_key: str,
        expiration: int = 3600,
        download: bool = False
    ) -> Optional[str]:
        """
        Generate presigned URL for secure document access

        Note: R2 presigned URLs have ZERO bandwidth cost!
        """
        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': r2_key
            }

            if download:
                params['ResponseContentDisposition'] = f'attachment; filename="{os.path.basename(r2_key)}"'

            url = self.client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expiration
            )

            # Optionally use custom domain
            if self.public_domain and not download:
                # For public domain, create a time-limited token
                # This would require Cloudflare Workers for signed URLs
                pass

            return url

        except ClientError:
            return None

    def generate_upload_presigned_url(
        self,
        organization_id: str,
        deal_id: Optional[str],
        filename: str,
        content_type: str,
        expiration: int = 3600
    ) -> Dict[str, Any]:
        """
        Generate presigned URL for direct browser upload to R2

        Benefits:
        - Reduces server load
        - Faster uploads via Cloudflare edge
        - No bandwidth costs
        """
        # Ensure bucket exists before generating URLs
        self._ensure_bucket_exists()

        try:
            r2_key = self._generate_r2_key(organization_id, deal_id, filename)

            # Generate presigned POST (works better with CORS)
            presigned_post = self.client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=r2_key,
                Fields={
                    'Content-Type': content_type,
                    'x-amz-server-side-encryption': 'AES256',
                    'x-amz-meta-organization_id': organization_id,
                    'x-amz-meta-original_filename': filename
                },
                Conditions=[
                    {'Content-Type': content_type},
                    ['content-length-range', 1, 524288000],  # Max 500MB
                    {'x-amz-server-side-encryption': 'AES256'}
                ],
                ExpiresIn=expiration
            )

            return {
                'success': True,
                'upload_url': presigned_post['url'],
                'fields': presigned_post['fields'],
                'r2_key': r2_key
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_document(self, r2_key: str) -> bool:
        """Delete document from R2"""
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=r2_key
            )
            return True
        except ClientError:
            return False

    def copy_document(
        self,
        source_key: str,
        organization_id: str,
        deal_id: Optional[str],
        new_filename: str
    ) -> Dict[str, Any]:
        """
        Copy document in R2 (for versioning)

        R2 supports S3-style copy operations
        """
        try:
            new_key = self._generate_r2_key(organization_id, deal_id, new_filename)

            # Copy object in R2
            copy_source = {'Bucket': self.bucket_name, 'Key': source_key}
            self.client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=new_key,
                ServerSideEncryption='AES256'
            )

            if self.public_domain:
                url = f"https://{self.public_domain}/{new_key}"
            else:
                url = f"{self.endpoint_url}/{self.bucket_name}/{new_key}"

            return {
                'success': True,
                'r2_bucket': self.bucket_name,
                'r2_key': new_key,
                'r2_url': url
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_document_metadata(self, r2_key: str) -> Optional[Dict[str, Any]]:
        """Get document metadata from R2"""
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=r2_key
            )

            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag', '').strip('"'),
                'metadata': response.get('Metadata', {}),
                'cache_control': response.get('CacheControl'),
                'server_side_encryption': response.get('ServerSideEncryption')
            }

        except ClientError:
            return None

    def create_bucket_if_not_exists(self) -> bool:
        """Ensure R2 bucket exists and is configured"""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                try:
                    self.client.create_bucket(Bucket=self.bucket_name)
                    self._configure_bucket()
                    return True
                except ClientError:
                    return False
            return False

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get R2 usage statistics

        R2 Free Tier:
        - 10GB storage
        - 10M Class A operations (PUT, POST, LIST)
        - 10M Class B operations (GET)
        - UNLIMITED egress
        """
        try:
            # Get bucket size (note: this lists all objects, use sparingly)
            paginator = self.client.get_paginator('list_objects_v2')
            total_size = 0
            total_count = 0

            for page in paginator.paginate(Bucket=self.bucket_name):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        total_size += obj['Size']
                        total_count += 1

            # Convert to readable format
            size_gb = total_size / (1024 ** 3)

            return {
                'provider': 'Cloudflare R2',
                'bucket': self.bucket_name,
                'total_files': total_count,
                'total_size_bytes': total_size,
                'total_size_gb': round(size_gb, 2),
                'free_tier_usage': f"{round(size_gb / 10 * 100, 1)}%" if size_gb <= 10 else "Exceeded",
                'estimated_monthly_cost': 0 if size_gb <= 10 else round((size_gb - 10) * 0.015, 2),
                'bandwidth_cost': 0,  # Always zero with R2!
                'note': 'R2 has ZERO egress fees - unlimited free bandwidth!'
            }

        except Exception as e:
            return {
                'error': str(e),
                'provider': 'Cloudflare R2'
            }


# Lazy singleton instance - initialized only when needed
_r2_storage_service = None

def get_r2_storage_service() -> R2StorageService:
    """Get the R2 storage service singleton instance"""
    global _r2_storage_service
    if _r2_storage_service is None:
        _r2_storage_service = R2StorageService()
    return _r2_storage_service

# For backward compatibility
r2_storage_service = None  # Will be set by get_r2_storage_service() when first needed