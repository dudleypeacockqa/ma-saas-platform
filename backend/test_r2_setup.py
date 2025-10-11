#!/usr/bin/env python3
"""
Cloudflare R2 Setup Verification Script
Tests R2 configuration and connectivity for 100daysandbeyond.com
"""

import os
import sys
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import requests

def load_environment():
    """Load environment variables from .env file"""
    if not os.path.exists('.env'):
        print("❌ ERROR: .env file not found!")
        print("📋 Please copy .env.r2.template to .env first:")
        print("   cp .env.r2.template .env")
        return False
    
    load_dotenv()
    return True

def check_required_variables():
    """Check if all required R2 environment variables are set"""
    required_vars = [
        'CLOUDFLARE_ACCOUNT_ID',
        'CLOUDFLARE_R2_ACCESS_KEY_ID', 
        'CLOUDFLARE_R2_SECRET_ACCESS_KEY',
        'CLOUDFLARE_R2_BUCKET_NAME',
        'CLOUDFLARE_R2_ENDPOINT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f'your_{var.lower()}_here':
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ ERROR: Missing or placeholder environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📋 Please update your .env file with actual Cloudflare R2 credentials")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_r2_connection():
    """Test connection to Cloudflare R2"""
    try:
        # Create R2 client
        r2_client = boto3.client(
            's3',
            endpoint_url=os.getenv('CLOUDFLARE_R2_ENDPOINT'),
            aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY'),
            region_name='auto'
        )
        
        # Test bucket access
        bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')
        response = r2_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Successfully connected to R2 bucket: {bucket_name}")
        return r2_client
        
    except NoCredentialsError:
        print("❌ ERROR: Invalid R2 credentials")
        return None
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ ERROR: Bucket '{bucket_name}' not found")
            print("📋 Please create the bucket in Cloudflare R2 dashboard")
        else:
            print(f"❌ ERROR: R2 connection failed: {e}")
        return None
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {e}")
        return None

def test_file_operations(r2_client):
    """Test basic file upload/download operations"""
    if not r2_client:
        return False
    
    try:
        bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')
        test_key = 'test/setup_verification.txt'
        test_content = 'R2 setup verification successful!'
        
        # Test upload
        r2_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        print("✅ File upload test successful")
        
        # Test download
        response = r2_client.get_object(Bucket=bucket_name, Key=test_key)
        downloaded_content = response['Body'].read().decode('utf-8')
        
        if downloaded_content == test_content:
            print("✅ File download test successful")
        else:
            print("❌ ERROR: Downloaded content doesn't match uploaded content")
            return False
        
        # Test delete
        r2_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("✅ File deletion test successful")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: File operations test failed: {e}")
        return False

def test_cors_configuration():
    """Test CORS configuration for web access"""
    try:
        # This would require additional setup, so we'll just validate the config
        cors_origins = os.getenv('R2_CORS_ORIGINS', '').split(',')
        expected_origins = ['https://100daysandbeyond.com', 'https://www.100daysandbeyond.com']
        
        for origin in expected_origins:
            if origin in cors_origins:
                print(f"✅ CORS origin configured: {origin}")
            else:
                print(f"⚠️  WARNING: CORS origin missing: {origin}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: CORS configuration check failed: {e}")
        return False

def print_setup_summary():
    """Print setup summary and next steps"""
    print("\n" + "="*60)
    print("🎉 CLOUDFLARE R2 SETUP VERIFICATION COMPLETE")
    print("="*60)
    
    print("\n📊 Configuration Summary:")
    print(f"   Storage Provider: {os.getenv('STORAGE_PROVIDER')}")
    print(f"   Bucket Name: {os.getenv('CLOUDFLARE_R2_BUCKET_NAME')}")
    print(f"   Max File Size: {os.getenv('R2_MAX_FILE_SIZE', '100MB')}")
    print(f"   Signed URL Expiry: {os.getenv('R2_SIGNED_URL_EXPIRY', '3600')} seconds")
    
    print("\n🚀 Next Steps:")
    print("   1. Your R2 storage is ready for document uploads")
    print("   2. Start your FastAPI backend: uvicorn app.main:app --reload")
    print("   3. Test document upload via your frontend")
    print("   4. Monitor usage in Cloudflare R2 dashboard")
    
    print("\n💰 Cost Benefits:")
    print("   ✅ 10GB storage FREE forever")
    print("   ✅ UNLIMITED bandwidth FREE")
    print("   ✅ 10M operations/month FREE")
    print("   ✅ Perfect for bootstrapping your M&A platform!")

def main():
    """Main verification function"""
    print("🔧 Cloudflare R2 Setup Verification")
    print("="*40)
    
    # Step 1: Load environment
    if not load_environment():
        sys.exit(1)
    
    # Step 2: Check required variables
    if not check_required_variables():
        sys.exit(1)
    
    # Step 3: Test R2 connection
    print("\n🔗 Testing R2 connection...")
    r2_client = test_r2_connection()
    if not r2_client:
        sys.exit(1)
    
    # Step 4: Test file operations
    print("\n📁 Testing file operations...")
    if not test_file_operations(r2_client):
        sys.exit(1)
    
    # Step 5: Test CORS configuration
    print("\n🌐 Checking CORS configuration...")
    test_cors_configuration()
    
    # Step 6: Print summary
    print_setup_summary()

if __name__ == "__main__":
    main()
