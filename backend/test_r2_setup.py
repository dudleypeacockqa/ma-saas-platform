#!/usr/bin/env python3
"""
Cloudflare R2 Setup & Test Script for 100daysandbeyond.com
Complete setup guide for document storage using Cloudflare R2
"""

import os
import sys
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime

# Load environment variables
load_dotenv()

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(title.center(60))
    print("="*60)

def test_r2_configuration():
    """Test Cloudflare R2 configuration and permissions"""

    print_header("CLOUDFLARE R2 CONFIGURATION TEST")
    print("\n🌐 Testing R2 for 100daysandbeyond.com")
    print("━" * 60)

    # Check environment variables
    print("\n1. Checking environment variables...")

    required_vars = {
        'CLOUDFLARE_ACCOUNT_ID': os.getenv('CLOUDFLARE_ACCOUNT_ID'),
        'R2_ACCESS_KEY_ID': os.getenv('R2_ACCESS_KEY_ID'),
        'R2_SECRET_ACCESS_KEY': os.getenv('R2_SECRET_ACCESS_KEY'),
        'R2_BUCKET_NAME': os.getenv('R2_BUCKET_NAME', 'ma-platform-documents')
    }

    missing_vars = [var for var, value in required_vars.items() if not value]

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\n📋 Please add these to your .env file:")
        print("\n# Cloudflare R2 Configuration")
        print("STORAGE_PROVIDER=r2")
        for var in missing_vars:
            if var == 'R2_BUCKET_NAME':
                print(f"{var}=ma-platform-documents")
            else:
                print(f"{var}=your_value_here")
        return False

    print("✅ All environment variables are set")
    print(f"   Account ID: {required_vars['CLOUDFLARE_ACCOUNT_ID'][:8]}...")
    print(f"   Bucket: {required_vars['R2_BUCKET_NAME']}")
    print(f"   Access Key: {required_vars['R2_ACCESS_KEY_ID'][:10]}...")

    # Create R2 client
    print("\n2. Creating R2 client...")

    endpoint_url = f"https://{required_vars['CLOUDFLARE_ACCOUNT_ID']}.r2.cloudflarestorage.com"
    print(f"   Endpoint: {endpoint_url}")

    try:
        r2_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=required_vars['R2_ACCESS_KEY_ID'],
            aws_secret_access_key=required_vars['R2_SECRET_ACCESS_KEY'],
            region_name='auto'  # R2 uses 'auto' as region
        )
        print("✅ R2 client created successfully")
    except Exception as e:
        print(f"❌ Failed to create R2 client: {e}")
        return False

    # Test bucket access
    print("\n3. Testing bucket access...")
    bucket_name = required_vars['R2_BUCKET_NAME']

    try:
        # Check if bucket exists
        r2_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' exists and is accessible")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"⚠️  Bucket '{bucket_name}' does not exist")
            print("\nWould you like to create it? (y/n): ", end='')
            if input().lower() == 'y':
                try:
                    r2_client.create_bucket(Bucket=bucket_name)
                    print(f"✅ Bucket '{bucket_name}' created successfully")
                except ClientError as create_error:
                    print(f"❌ Failed to create bucket: {create_error}")
                    return False
            else:
                return False
        elif error_code == '403':
            print(f"❌ Access denied to bucket '{bucket_name}'")
            print("   Check your R2 API token permissions")
            return False
        else:
            print(f"❌ Error accessing bucket: {e}")
            return False

    # Configure bucket settings
    print("\n4. Configuring bucket settings...")

    # Enable versioning
    try:
        r2_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print("✅ Versioning enabled")
    except ClientError as e:
        print(f"⚠️  Could not enable versioning: {e}")

    # Configure CORS for browser uploads
    print("\n5. Configuring CORS for browser uploads...")

    cors_config = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                'AllowedOrigins': [
                    'https://100daysandbeyond.com',
                    'https://*.100daysandbeyond.com',
                    'http://localhost:3000',
                    'http://localhost:5173'
                ],
                'ExposeHeaders': ['ETag', 'x-amz-server-side-encryption'],
                'MaxAgeSeconds': 3600
            }
        ]
    }

    try:
        r2_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_config
        )
        print("✅ CORS configured for 100daysandbeyond.com")
    except ClientError as e:
        print(f"⚠️  Could not configure CORS: {e}")

    # Test upload
    print("\n6. Testing document upload...")

    test_key = f"test/r2-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    test_content = b'Cloudflare R2 test for 100daysandbeyond.com MA Platform'

    try:
        r2_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain',
            Metadata={'test': 'true', 'platform': '100daysandbeyond'}
        )
        print(f"✅ Successfully uploaded test file: {test_key}")
    except ClientError as e:
        print(f"❌ Failed to upload test file: {e}")
        return False

    # Test read
    print("\n7. Testing document retrieval...")

    try:
        response = r2_client.get_object(Bucket=bucket_name, Key=test_key)
        content = response['Body'].read()
        if content == test_content:
            print("✅ Successfully retrieved test file")
        else:
            print("⚠️  File content mismatch")
    except ClientError as e:
        print(f"❌ Failed to retrieve test file: {e}")
        return False

    # Test presigned URL
    print("\n8. Testing presigned URL generation...")

    try:
        presigned_url = r2_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': test_key},
            ExpiresIn=3600
        )
        print("✅ Successfully generated presigned URL")
        print(f"   URL preview: {presigned_url[:80]}...")
    except ClientError as e:
        print(f"❌ Failed to generate presigned URL: {e}")
        return False

    # Test delete
    print("\n9. Testing document deletion...")

    try:
        r2_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("✅ Successfully deleted test file")
    except ClientError as e:
        print(f"❌ Failed to delete test file: {e}")
        return False

    # Calculate usage
    print("\n10. Checking R2 usage (Free Tier: 10GB)...")

    try:
        paginator = r2_client.get_paginator('list_objects_v2')
        total_size = 0
        total_count = 0

        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' in page:
                for obj in page['Contents']:
                    total_size += obj['Size']
                    total_count += 1

        size_gb = total_size / (1024 ** 3)
        free_tier_usage = (size_gb / 10) * 100

        print(f"✅ Current usage:")
        print(f"   Files: {total_count}")
        print(f"   Storage: {size_gb:.3f} GB / 10 GB ({free_tier_usage:.1f}% of free tier)")
        print(f"   Bandwidth cost: $0 (unlimited free egress!)")

    except Exception as e:
        print(f"⚠️  Could not calculate usage: {e}")

    # Summary
    print_header("✅ TEST SUCCESSFUL")
    print("\n🎉 Cloudflare R2 is configured and ready!")
    print("\n📊 Your R2 Benefits:")
    print("   • 10GB free storage (2x AWS S3)")
    print("   • ZERO bandwidth fees (saves $$$)")
    print("   • Integrated with Cloudflare CDN")
    print("   • DDoS protection included")
    print("   • S3-compatible API")

    print("\n🔧 Environment variables configured:")
    print(f"   STORAGE_PROVIDER=r2")
    print(f"   CLOUDFLARE_ACCOUNT_ID={required_vars['CLOUDFLARE_ACCOUNT_ID'][:8]}...")
    print(f"   R2_ACCESS_KEY_ID={required_vars['R2_ACCESS_KEY_ID'][:10]}...")
    print(f"   R2_SECRET_ACCESS_KEY=***hidden***")
    print(f"   R2_BUCKET_NAME={required_vars['R2_BUCKET_NAME']}")

    print("\n🚀 Next Steps:")
    print("   1. Your document upload will now use Cloudflare R2")
    print("   2. Files are served through Cloudflare's global CDN")
    print("   3. Automatic DDoS protection for all uploads")
    print("   4. Zero bandwidth costs as you scale!")

    return True

def setup_instructions():
    """Display setup instructions for Cloudflare R2"""

    print_header("CLOUDFLARE R2 SETUP GUIDE")
    print("\nFor 100daysandbeyond.com - Stay in the Cloudflare Ecosystem")
    print("━" * 60)

    print("\n📋 QUICK SETUP (5 minutes):")

    print("\n1️⃣  Sign in to Cloudflare Dashboard")
    print("   https://dash.cloudflare.com")
    print("   (Use your existing 100daysandbeyond.com account)")

    print("\n2️⃣  Navigate to R2 Object Storage")
    print("   • Click 'R2' in the left sidebar")
    print("   • Click 'Create bucket'")
    print("   • Name: ma-platform-documents")
    print("   • Location: Automatic")
    print("   • Click 'Create bucket'")

    print("\n3️⃣  Generate R2 API Credentials")
    print("   • Go to R2 > Manage R2 API tokens")
    print("   • Click 'Create API token'")
    print("   • Token name: 'MA Platform Storage'")
    print("   • Permissions: Select 'Object Read & Write'")
    print("   • TTL: Leave empty (no expiration)")
    print("   • Click 'Create API Token'")
    print("   • SAVE THE CREDENTIALS (shown only once!)")

    print("\n4️⃣  Add to your .env file:")
    print("""
# Cloudflare R2 Storage (10GB free, unlimited bandwidth)
STORAGE_PROVIDER=r2
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
R2_ACCESS_KEY_ID=your_access_key_here
R2_SECRET_ACCESS_KEY=your_secret_key_here
R2_BUCKET_NAME=ma-platform-documents
    """)

    print("\n5️⃣  Optional: Custom Domain (docs.100daysandbeyond.com)")
    print("   • In R2 bucket settings, click 'Settings'")
    print("   • Under 'Custom Domains', add: docs.100daysandbeyond.com")
    print("   • Cloudflare will automatically configure DNS")
    print("   • Add to .env: R2_PUBLIC_DOMAIN=docs.100daysandbeyond.com")

    print("\n6️⃣  Run this script to test:")
    print("   python test_r2_setup.py")

    print("\n" + "─" * 60)
    print("💡 WHY CLOUDFLARE R2?")
    print("\n✅ Perfect fit for 100daysandbeyond.com:")
    print("   • Already using Cloudflare DNS & Security")
    print("   • Single vendor = simpler management")
    print("   • Integrated DDoS protection")
    print("   • Automatic CDN distribution")

    print("\n💰 Cost Comparison (Monthly):")
    print("┌─────────────┬────────────┬──────────────┬─────────────┐")
    print("│ Storage     │ R2 (Free)  │ AWS S3       │ Savings     │")
    print("├─────────────┼────────────┼──────────────┼─────────────┤")
    print("│ 10GB        │ $0         │ $0.23        │ $0.23       │")
    print("│ 100GB down  │ $0         │ $9.00        │ $9.00       │")
    print("│ 1TB down    │ $0         │ $90.00       │ $90.00      │")
    print("└─────────────┴────────────┴──────────────┴─────────────┘")
    print("* R2 has ZERO bandwidth fees vs S3's $0.09/GB")

    print("\n🔐 Security Features:")
    print("   • Encryption at rest (AES-256)")
    print("   • Cloudflare DDoS protection")
    print("   • Access control via API tokens")
    print("   • Versioning for document history")
    print("   • CORS configured for your domain")

def main():
    """Main entry point"""

    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        setup_instructions()
    else:
        print("\n🚀 CLOUDFLARE R2 FOR 100DAYSANDBEYOND.COM")
        print("━" * 60)
        print("\nOptions:")
        print("1. Test existing R2 configuration")
        print("2. Show setup instructions")
        print("3. Exit")

        choice = input("\nChoice (1-3): ").strip()

        if choice == '1':
            success = test_r2_configuration()
            sys.exit(0 if success else 1)
        elif choice == '2':
            setup_instructions()
        else:
            print("Exiting...")

if __name__ == "__main__":
    main()