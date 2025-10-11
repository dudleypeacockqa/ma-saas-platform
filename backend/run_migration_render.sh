#!/bin/bash
# Database Migration Script for Render
# Works from /app directory (Render's default)

set -e  # Exit on any error

echo "🚀 Starting Database Migration Process"
echo "⏰ Timestamp: $(date)"
echo "=================================================="

# Step 1: Check current directory
echo "📁 Current directory: $(pwd)"
echo "📋 Listing files:"
ls -la

# Step 2: Verify environment
echo ""
echo "🌍 Verifying environment..."
echo "Python version: $(python --version)"
echo "DATABASE_URL available: $(echo $DATABASE_URL | cut -c1-30)..."

# Step 3: Check if alembic.ini exists
echo ""
echo "🔍 Checking for alembic.ini..."
if [ -f "alembic.ini" ]; then
    echo "✅ Found alembic.ini in current directory"
else
    echo "❌ alembic.ini not found"
    exit 1
fi

# Step 4: Check current migration status
echo ""
echo "🔍 Checking current migration status..."
alembic current || echo "No migrations applied yet"

# Step 5: List available migrations
echo ""
echo "📋 Available migrations:"
alembic history --verbose || echo "No migration history found"

# Step 6: Run migrations
echo ""
echo "🔄 Running database migrations..."
alembic upgrade head

# Step 7: Verify migration success
echo ""
echo "✅ Migration completed! Verifying results..."
alembic current

# Step 8: Run verification script if it exists
echo ""
if [ -f "verify_migration.py" ]; then
    echo "🧪 Running comprehensive verification..."
    python verify_migration.py
else
    echo "⚠️  verify_migration.py not found, skipping detailed verification"
fi

echo ""
echo "=================================================="
echo "🎉 Migration process completed successfully!"
echo "📊 Database schema is ready for application use"
