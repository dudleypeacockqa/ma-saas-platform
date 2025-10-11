#!/usr/bin/env python3
"""
Quick migration script that bypasses alembic.ini issues
Run directly: python quick_migrate.py
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.getcwd())

def run_migration():
    """Run migration by directly executing SQL"""
    try:
        import psycopg
        from datetime import datetime

        # Get database URL from environment
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL not found in environment")
            return False

        print("🚀 Quick Migration Script")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("=" * 50)

        # Connect to database
        print("🔗 Connecting to database...")
        conn = psycopg.connect(db_url)
        cursor = conn.cursor()

        # Check if alembic_version table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'alembic_version'
            );
        """)
        alembic_exists = cursor.fetchone()[0]

        if alembic_exists:
            cursor.execute("SELECT version_num FROM alembic_version;")
            current_version = cursor.fetchone()
            if current_version:
                print(f"✅ Migration already applied: {current_version[0]}")
                print("📊 Database is already migrated")
                return True

        print("📋 Checking current tables...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = [row[0] for row in cursor.fetchall()]
        print(f"📊 Found {len(tables)} existing tables")

        # Check if core tables exist
        required_tables = ['organizations', 'users', 'subscriptions']
        missing_tables = [t for t in required_tables if t not in tables]

        if not missing_tables:
            print(f"✅ All required tables exist: {required_tables}")

            # Create alembic_version table if it doesn't exist
            if not alembic_exists:
                print("📝 Creating alembic_version table...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alembic_version (
                        version_num VARCHAR(32) NOT NULL,
                        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                    );
                """)

                # Insert migration version
                cursor.execute("""
                    INSERT INTO alembic_version (version_num)
                    VALUES ('001_initial_schema_with_pgvector')
                    ON CONFLICT (version_num) DO NOTHING;
                """)

                conn.commit()
                print("✅ Migration version recorded: 001_initial_schema_with_pgvector")

            print("🎉 Database is ready!")
            return True
        else:
            print(f"⚠️  Missing tables: {missing_tables}")
            print("❌ Tables need to be created via Alembic migration")
            return False

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
