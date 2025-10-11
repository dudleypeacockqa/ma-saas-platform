#!/usr/bin/env python3
"""
Setup script for FREE storage options - Perfect for bootstrapping
Run this to configure and test your chosen free storage provider
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_supabase():
    """Setup Supabase Storage (1GB free + 2GB bandwidth/month)"""

    print("\n" + "="*60)
    print("SUPABASE STORAGE SETUP (FREE TIER)")
    print("="*60)
    print("\nSupabase provides:")
    print("✓ 1GB free storage")
    print("✓ 2GB bandwidth per month")
    print("✓ Row Level Security for multi-tenant isolation")
    print("✓ Built-in authentication")
    print("✓ GDPR compliant")

    print("\n📋 Setup Instructions:")
    print("\n1. Create free account at https://supabase.com")
    print("\n2. Create a new project (takes ~2 minutes)")
    print("\n3. Go to Settings > API and copy:")
    print("   - Project URL → SUPABASE_URL")
    print("   - Anon/Public key → SUPABASE_ANON_KEY")
    print("   - Service Role key → SUPABASE_SERVICE_KEY (for admin operations)")

    print("\n4. Add to your .env file:")
    print("   STORAGE_PROVIDER=supabase")
    print("   SUPABASE_URL=https://[your-project].supabase.co")
    print("   SUPABASE_ANON_KEY=[your-anon-key]")
    print("   SUPABASE_SERVICE_KEY=[your-service-key]")
    print("   SUPABASE_BUCKET_NAME=ma-documents")

    print("\n5. Create storage bucket:")
    print("   - Go to Storage in Supabase dashboard")
    print("   - Click 'New bucket'")
    print("   - Name: 'ma-documents'")
    print("   - Public: OFF (keep it private)")

    print("\n6. Set Row Level Security (RLS) policies:")
    print("   Run this SQL in Supabase SQL Editor:")

    print("""
-- Enable RLS on storage
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their organization's files
CREATE POLICY "org_isolation" ON storage.objects
FOR ALL USING (
    bucket_id = 'ma-documents' AND
    (storage.foldername(name))[1] = current_setting('app.organization_id')::text
);

-- Policy: Enforce folder structure
CREATE POLICY "folder_structure" ON storage.objects
FOR INSERT WITH CHECK (
    bucket_id = 'ma-documents' AND
    name ~ '^organizations/[a-f0-9-]+/(deals/[a-f0-9-]+/)?documents/.*'
);
    """)

    return test_supabase_connection()

def setup_cloudflare_r2():
    """Setup Cloudflare R2 (10GB free + unlimited bandwidth)"""

    print("\n" + "="*60)
    print("CLOUDFLARE R2 SETUP (GENEROUS FREE TIER)")
    print("="*60)
    print("\nCloudflare R2 provides:")
    print("✓ 10GB free storage per month")
    print("✓ UNLIMITED egress (no bandwidth charges!)")
    print("✓ S3-compatible API")
    print("✓ Global CDN included")
    print("✓ 1 million Class A operations free/month")

    print("\n📋 Setup Instructions:")
    print("\n1. Create free account at https://dash.cloudflare.com")
    print("\n2. Go to R2 Object Storage")
    print("\n3. Create a bucket named 'ma-documents'")
    print("\n4. Generate API credentials:")
    print("   - Go to R2 > Manage R2 API Tokens")
    print("   - Create token with 'Object Read & Write' permissions")

    print("\n5. Add to your .env file:")
    print("   STORAGE_PROVIDER=r2")
    print("   CLOUDFLARE_ACCOUNT_ID=[your-account-id]")
    print("   R2_ACCESS_KEY_ID=[your-access-key]")
    print("   R2_SECRET_ACCESS_KEY=[your-secret-key]")
    print("   R2_BUCKET_NAME=ma-documents")
    print("   R2_ENDPOINT=https://[account-id].r2.cloudflarestorage.com")

    print("\n6. Configure CORS for browser uploads:")
    print("   - Go to bucket settings")
    print("   - Add CORS rule for your domain")

    return test_r2_connection()

def test_supabase_connection():
    """Test Supabase connection and configuration"""

    print("\n🧪 Testing Supabase connection...")

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')

    if not url or not key:
        print("❌ Missing Supabase credentials in .env")
        return False

    try:
        from supabase import create_client

        client = create_client(url, key)

        # Test bucket access
        buckets = client.storage.list_buckets()
        print(f"✅ Connected to Supabase")
        print(f"   Found {len(buckets)} storage buckets")

        # Check if ma-documents bucket exists
        bucket_exists = any(b['name'] == 'ma-documents' for b in buckets)
        if bucket_exists:
            print("✅ Bucket 'ma-documents' exists")
        else:
            print("⚠️  Bucket 'ma-documents' not found - create it in dashboard")

        return True

    except ImportError:
        print("❌ Supabase client not installed")
        print("   Run: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_r2_connection():
    """Test Cloudflare R2 connection"""

    print("\n🧪 Testing Cloudflare R2 connection...")

    access_key = os.getenv('R2_ACCESS_KEY_ID')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
    endpoint = os.getenv('R2_ENDPOINT')

    if not access_key or not secret_key:
        print("❌ Missing R2 credentials in .env")
        return False

    try:
        import boto3

        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto'
        )

        # List buckets
        response = s3_client.list_buckets()
        print(f"✅ Connected to Cloudflare R2")
        print(f"   Found {len(response['Buckets'])} buckets")

        # Check for ma-documents bucket
        bucket_exists = any(b['Name'] == 'ma-documents' for b in response['Buckets'])
        if bucket_exists:
            print("✅ Bucket 'ma-documents' exists")
        else:
            print("⚠️  Bucket 'ma-documents' not found - create it in dashboard")

        return True

    except ImportError:
        print("❌ boto3 not installed")
        print("   Run: pip install boto3")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def compare_providers():
    """Compare free storage providers for bootstrapping"""

    print("\n" + "="*60)
    print("FREE STORAGE PROVIDER COMPARISON")
    print("="*60)

    providers = [
        {
            'name': 'Supabase',
            'storage': '1GB',
            'bandwidth': '2GB/month',
            'file_size': '50MB max',
            'pros': '✓ RLS security\n✓ Built-in auth\n✓ Real-time capabilities',
            'cons': '✗ Limited storage\n✗ Bandwidth limits',
            'best_for': 'Starting out, <100 users'
        },
        {
            'name': 'Cloudflare R2',
            'storage': '10GB/month',
            'bandwidth': 'UNLIMITED',
            'file_size': '5TB max',
            'pros': '✓ No egress fees\n✓ S3-compatible\n✓ Global CDN',
            'cons': '✗ No built-in auth\n✗ Less integrated',
            'best_for': 'Growing, high bandwidth'
        },
        {
            'name': 'Firebase Storage',
            'storage': '5GB',
            'bandwidth': '1GB/day',
            'file_size': '5GB max',
            'pros': '✓ Google infrastructure\n✓ Good SDKs\n✓ Security rules',
            'cons': '✗ Vendor lock-in\n✗ Complex pricing',
            'best_for': 'Mobile apps, Google stack'
        }
    ]

    for p in providers:
        print(f"\n📦 {p['name']}")
        print(f"   Storage: {p['storage']}")
        print(f"   Bandwidth: {p['bandwidth']}")
        print(f"   Max file: {p['file_size']}")
        print(f"\n   Pros:\n   {p['pros']}")
        print(f"\n   Cons:\n   {p['cons']}")
        print(f"\n   Best for: {p['best_for']}")
        print("-" * 40)

    print("\n💡 RECOMMENDATION FOR BOOTSTRAPPING:")
    print("\n1. Start with Supabase (easiest setup, best security)")
    print("2. Add Cloudflare R2 when you need more storage")
    print("3. Use provider factory to switch seamlessly")

def main():
    """Main setup flow"""

    print("\n" + "🚀 FREE STORAGE SETUP FOR BOOTSTRAPPING 🚀".center(60))
    print("="*60)

    print("\nChoose your free storage provider:")
    print("\n1. Supabase (Recommended - 1GB free, best security)")
    print("2. Cloudflare R2 (10GB free, unlimited bandwidth)")
    print("3. Compare all options")
    print("4. Test existing configuration")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == '1':
        setup_supabase()
    elif choice == '2':
        setup_cloudflare_r2()
    elif choice == '3':
        compare_providers()
    elif choice == '4':
        print("\nTesting configured provider...")
        provider = os.getenv('STORAGE_PROVIDER', 'supabase')
        if provider == 'supabase':
            test_supabase_connection()
        elif provider == 'r2':
            test_r2_connection()
        else:
            print(f"Unknown provider: {provider}")

    print("\n✅ Setup complete! Your app will automatically use the configured provider.")
    print("\nNext steps:")
    print("1. Complete the provider setup in their dashboard")
    print("2. Add credentials to your .env file")
    print("3. Run this script again to test (option 4)")
    print("4. Your document upload will work with zero cost!")

if __name__ == "__main__":
    main()