#!/usr/bin/env python3
"""
Database Migration Verification Script for Render
Run this after migration to verify schema creation
Works from /app directory
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from app.core.config import settings
    import psycopg

    def verify_database_schema():
        """Verify that all expected tables were created"""

        expected_tables = {
            'organizations',
            'users',
            'organization_memberships',
            'subscriptions',
            'organization_settings',
            'invoices',
            'usage_records',
            'alembic_version'
        }

        try:
            # Connect to database
            print(f"🔗 Connecting to database...")
            db_url = getattr(settings, 'DATABASE_URL', None) or os.getenv('DATABASE_URL')
            if not db_url:
                print("❌ DATABASE_URL not found")
                return False
            conn = psycopg.connect(db_url)
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)

            actual_tables = {row[0] for row in cursor.fetchall()}
            print(f"📋 Found {len(actual_tables)} tables: {sorted(actual_tables)}")

            # Check for expected tables
            missing_tables = expected_tables - actual_tables
            extra_tables = actual_tables - expected_tables

            if missing_tables:
                print(f"❌ Missing tables: {sorted(missing_tables)}")
                return False

            if extra_tables:
                print(f"ℹ️  Extra tables: {sorted(extra_tables)}")

            print(f"✅ All expected tables present!")

            # Check migration version
            cursor.execute("SELECT version_num FROM alembic_version;")
            version = cursor.fetchone()
            if version:
                print(f"📊 Migration version: {version[0]}")
            else:
                print("⚠️  No migration version found")

            # Test basic operations
            cursor.execute("SELECT COUNT(*) FROM organizations;")
            org_count = cursor.fetchone()[0]
            print(f"📈 Organizations table accessible: {org_count} rows")

            cursor.execute("SELECT COUNT(*) FROM users;")
            user_count = cursor.fetchone()[0]
            print(f"👥 Users table accessible: {user_count} rows")

            conn.close()
            return True

        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def verify_alembic_status():
        """Verify Alembic migration status"""
        try:
            # Check current migration
            result = os.popen('alembic current').read().strip()
            print(f"🔄 Alembic status: {result}")

            if '001' in result or 'initial_schema' in result:
                print("✅ Migration 001 successfully applied")
                return True
            else:
                print("❌ Migration 001 not found in current status")
                return False

        except Exception as e:
            print(f"❌ Alembic verification failed: {e}")
            return False

    if __name__ == "__main__":
        print("🚀 Starting Database Migration Verification")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("=" * 50)
        print(f"📁 Current directory: {os.getcwd()}")

        # Verify environment
        db_url = getattr(settings, 'DATABASE_URL', None) or os.getenv('DATABASE_URL')
        print(f"🌍 DATABASE_URL configured: {'Yes' if db_url else 'No'}")
        print(f"🐍 Python version: {sys.version}")

        # Run verifications
        alembic_ok = verify_alembic_status()
        print()
        schema_ok = verify_database_schema()

        print()
        print("=" * 50)
        if alembic_ok and schema_ok:
            print("🎉 Migration verification SUCCESSFUL!")
            print("✅ Database is ready for application use")
        else:
            print("💥 Migration verification FAILED!")
            print("❌ Please check the errors above and retry migration")
            sys.exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"📁 Current directory: {os.getcwd()}")
    print("🔧 Make sure you're running from the correct directory and dependencies are installed")
    import traceback
    traceback.print_exc()
    sys.exit(1)
