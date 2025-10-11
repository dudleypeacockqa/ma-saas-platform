#!/usr/bin/env python3
"""
Test script to verify AWS S3 configuration
Run this after setting up your AWS account and environment variables
"""

import os
import sys
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError

# Load environment variables
load_dotenv()

def test_s3_configuration():
    """Test S3 configuration and permissions"""

    print("=" * 60)
    print("AWS S3 CONFIGURATION TEST")
    print("=" * 60)

    # Check environment variables
    print("\n1. Checking environment variables...")

    required_vars = {
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'AWS_REGION': os.getenv('AWS_REGION'),
        'S3_BUCKET_NAME': os.getenv('S3_BUCKET_NAME')
    }

    missing_vars = [var for var, value in required_vars.items() if not value]

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease set these in your .env file:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        return False

    print("✅ All environment variables are set")
    print(f"   Region: {required_vars['AWS_REGION']}")
    print(f"   Bucket: {required_vars['S3_BUCKET_NAME']}")
    print(f"   Access Key: {required_vars['AWS_ACCESS_KEY_ID'][:10]}...")

    # Create S3 client
    print("\n2. Creating S3 client...")

    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=required_vars['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=required_vars['AWS_SECRET_ACCESS_KEY'],
            region_name=required_vars['AWS_REGION']
        )
        print("✅ S3 client created successfully")
    except Exception as e:
        print(f"❌ Failed to create S3 client: {e}")
        return False

    # Test bucket access
    print("\n3. Testing bucket access...")
    bucket_name = required_vars['S3_BUCKET_NAME']

    try:
        # Check if bucket exists and we have access
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' exists and is accessible")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ Bucket '{bucket_name}' does not exist")
            print("\nWould you like to create it? (y/n): ", end='')
            if input().lower() == 'y':
                try:
                    if required_vars['AWS_REGION'] == 'us-east-1':
                        s3_client.create_bucket(Bucket=bucket_name)
                    else:
                        s3_client.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': required_vars['AWS_REGION']}
                        )
                    print(f"✅ Bucket '{bucket_name}' created successfully")
                except ClientError as create_error:
                    print(f"❌ Failed to create bucket: {create_error}")
                    return False
            else:
                return False
        elif error_code == '403':
            print(f"❌ Access denied to bucket '{bucket_name}'")
            print("   Check your IAM permissions")
            return False
        else:
            print(f"❌ Error accessing bucket: {e}")
            return False
    except NoCredentialsError:
        print("❌ AWS credentials not found or invalid")
        return False

    # Test bucket configuration
    print("\n4. Checking bucket configuration...")

    # Check versioning
    try:
        versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
        if versioning.get('Status') == 'Enabled':
            print("✅ Versioning is enabled")
        else:
            print("⚠️  Versioning is not enabled")
            print("   Enabling versioning...")
            s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            print("✅ Versioning enabled")
    except ClientError as e:
        print(f"⚠️  Could not check versioning: {e}")

    # Check encryption
    try:
        encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
        print("✅ Encryption is configured")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            print("⚠️  Encryption is not configured")
            print("   Configuring encryption...")
            s3_client.put_bucket_encryption(
                Bucket=bucket_name,
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
            print("✅ Encryption configured")
        else:
            print(f"⚠️  Could not check encryption: {e}")

    # Test upload permission
    print("\n5. Testing upload permission...")

    test_key = 'test/test-file.txt'
    test_content = b'This is a test file for MA Platform'

    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ServerSideEncryption='AES256',
            Metadata={'test': 'true'}
        )
        print(f"✅ Successfully uploaded test file: {test_key}")
    except ClientError as e:
        print(f"❌ Failed to upload test file: {e}")
        return False

    # Test read permission
    print("\n6. Testing read permission...")

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
        content = response['Body'].read()
        if content == test_content:
            print("✅ Successfully read test file")
        else:
            print("⚠️  File content mismatch")
    except ClientError as e:
        print(f"❌ Failed to read test file: {e}")
        return False

    # Test presigned URL generation
    print("\n7. Testing presigned URL generation...")

    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': test_key},
            ExpiresIn=3600
        )
        print("✅ Successfully generated presigned URL")
        print(f"   URL (first 80 chars): {presigned_url[:80]}...")
    except ClientError as e:
        print(f"❌ Failed to generate presigned URL: {e}")
        return False

    # Test delete permission
    print("\n8. Testing delete permission...")

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print(f"✅ Successfully deleted test file")
    except ClientError as e:
        print(f"❌ Failed to delete test file: {e}")
        return False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("\n🎉 All tests passed! Your S3 configuration is ready.")
    print("\nYour environment variables are correctly set:")
    print(f"  AWS_ACCESS_KEY_ID={required_vars['AWS_ACCESS_KEY_ID'][:10]}...")
    print(f"  AWS_SECRET_ACCESS_KEY=***hidden***")
    print(f"  AWS_REGION={required_vars['AWS_REGION']}")
    print(f"  S3_BUCKET_NAME={required_vars['S3_BUCKET_NAME']}")
    print("\n✅ You can now use the document upload features!")

    return True


if __name__ == "__main__":
    success = test_s3_configuration()
    sys.exit(0 if success else 1)