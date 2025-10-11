"""
AWS S3 Service for document storage
Story 3.1: Document Upload API - S3 integration
"""

import os
import uuid
import mimetypes
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta
import hashlib

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config

from app.core.config import settings


class S3Service:
    """
    Service for interacting with AWS S3 for document storage
    """

    def __init__(self):
        """Initialize S3 client with configuration"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            config=Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'}
            )
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'ma-platform-documents')
        self.bucket_region = os.getenv('AWS_REGION', 'us-east-1')

    def _generate_s3_key(self, organization_id: str, deal_id: Optional[str], filename: str) -> str:
        """
        Generate a unique S3 key for the document
        Format: organizations/{org_id}/deals/{deal_id}/documents/{uuid}_{filename}
        """
        unique_id = uuid.uuid4().hex[:8]
        safe_filename = filename.replace(' ', '_').replace('/', '_')

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
        Upload a document to S3 with encryption

        Args:
            file: File object to upload
            filename: Original filename
            organization_id: Organization UUID
            deal_id: Optional deal UUID
            content_type: MIME type of the file
            metadata: Additional metadata to store with the file

        Returns:
            Dictionary containing S3 upload information
        """
        try:
            # Generate S3 key
            s3_key = self._generate_s3_key(organization_id, deal_id, filename)

            # Detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = 'application/octet-stream'

            # Prepare metadata
            s3_metadata = {
                'organization_id': organization_id,
                'uploaded_at': datetime.utcnow().isoformat(),
                'original_filename': filename
            }
            if deal_id:
                s3_metadata['deal_id'] = deal_id
            if metadata:
                s3_metadata.update(metadata)

            # Calculate file hash
            file_content = file.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
            file.seek(0)  # Reset file pointer

            # Upload to S3 with server-side encryption
            response = self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                ServerSideEncryption='AES256',
                Metadata=s3_metadata,
                Tagging=f"organization={organization_id}&environment={os.getenv('ENVIRONMENT', 'production')}"
            )

            # Generate URL
            url = f"https://{self.bucket_name}.s3.{self.bucket_region}.amazonaws.com/{s3_key}"

            return {
                'success': True,
                's3_bucket': self.bucket_name,
                's3_key': s3_key,
                's3_url': url,
                's3_etag': response.get('ETag', '').strip('"'),
                'file_hash': file_hash,
                'file_size': len(file_content),
                'content_type': content_type
            }

        except NoCredentialsError:
            return {
                'success': False,
                'error': 'AWS credentials not configured'
            }
        except ClientError as e:
            return {
                'success': False,
                'error': f"S3 upload failed: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }

    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        download: bool = False
    ) -> Optional[str]:
        """
        Generate a presigned URL for secure document access

        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            download: If True, force download instead of view

        Returns:
            Presigned URL or None if error
        """
        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': s3_key
            }

            if download:
                params['ResponseContentDisposition'] = 'attachment'

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expiration
            )
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
        Generate a presigned URL for direct browser upload

        Returns:
            Dictionary with presigned POST data for browser upload
        """
        try:
            s3_key = self._generate_s3_key(organization_id, deal_id, filename)

            # Generate presigned POST data
            presigned_post = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=s3_key,
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
                's3_key': s3_key
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_document(self, s3_key: str) -> bool:
        """
        Delete a document from S3

        Args:
            s3_key: S3 object key

        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
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
        Copy a document to a new location (for versioning)

        Args:
            source_key: Source S3 key
            organization_id: Organization UUID
            deal_id: Optional deal UUID
            new_filename: New filename for the copy

        Returns:
            Dictionary with new S3 information
        """
        try:
            new_key = self._generate_s3_key(organization_id, deal_id, new_filename)

            # Copy object
            copy_source = {'Bucket': self.bucket_name, 'Key': source_key}
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=new_key,
                ServerSideEncryption='AES256'
            )

            url = f"https://{self.bucket_name}.s3.{self.bucket_region}.amazonaws.com/{new_key}"

            return {
                'success': True,
                's3_bucket': self.bucket_name,
                's3_key': new_key,
                's3_url': url
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_document_metadata(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a document

        Args:
            s3_key: S3 object key

        Returns:
            Dictionary with document metadata or None
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )

            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag', '').strip('"'),
                'metadata': response.get('Metadata', {}),
                'server_side_encryption': response.get('ServerSideEncryption')
            }

        except ClientError:
            return None

    def create_bucket_if_not_exists(self) -> bool:
        """
        Create S3 bucket if it doesn't exist (for initial setup)

        Returns:
            True if bucket exists or was created
        """
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Bucket doesn't exist, create it
                try:
                    if self.bucket_region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.bucket_region}
                        )

                    # Enable versioning
                    self.s3_client.put_bucket_versioning(
                        Bucket=self.bucket_name,
                        VersioningConfiguration={'Status': 'Enabled'}
                    )

                    # Set bucket encryption
                    self.s3_client.put_bucket_encryption(
                        Bucket=self.bucket_name,
                        ServerSideEncryptionConfiguration={
                            'Rules': [
                                {
                                    'ApplyServerSideEncryptionByDefault': {
                                        'SSEAlgorithm': 'AES256'
                                    }
                                }
                            ]
                        }
                    )

                    # Set lifecycle policy for old versions
                    self.s3_client.put_bucket_lifecycle_configuration(
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
                                    'ID': 'DeleteIncompleteMultipartUploads',
                                    'Status': 'Enabled',
                                    'AbortIncompleteMultipartUpload': {
                                        'DaysAfterInitiation': 7
                                    }
                                }
                            ]
                        }
                    )

                    return True
                except ClientError:
                    return False
            else:
                return False


# Singleton instance
s3_service = S3Service()