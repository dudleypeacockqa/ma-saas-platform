#!/bin/bash
# Database Migration Script for Render Shell
# Run this script in the Render shell environment

set -e  # Exit on any error

echo "🚀 Starting Database Migration Process"
echo "⏰ Timestamp: $(date)"
echo "=" | tr ' ' '=' | head -c 50; echo

# Step 1: Navigate to correct directory
echo "📁 Navigating to backend directory..."
cd /opt/render/project/src/backend || {
    echo "❌ Failed to navigate to backend directory"
    exit 1
}
echo "✅ Current directory: $(pwd)"

# Step 2: Verify environment
echo
echo "🌍 Verifying environment..."
echo "Python version: $(python --version)"
echo "DATABASE_URL available: $(echo $DATABASE_URL | cut -c1-30)..."

# Step 3: Check if dependencies are installed
echo
echo "📦 Checking dependencies..."
if ! python -c "import alembic" 2>/dev/null; then
    echo "📥 Installing Alembic..."
    pip install alembic==1.14.0
fi

if ! python -c "import psycopg" 2>/dev/null; then
    echo "📥 Installing psycopg..."
    pip install psycopg[binary]==3.2.3
fi

echo "✅ Dependencies verified"

# Step 4: Check current migration status
echo
echo "🔍 Checking current migration status..."
alembic current || echo "No migrations applied yet"

# Step 5: List available migrations
echo
echo "📋 Available migrations:"
alembic history --verbose

# Step 6: Run migrations
echo
echo "🔄 Running database migrations..."
alembic upgrade head

# Step 7: Verify migration success
echo
echo "✅ Migration completed! Verifying results..."
alembic current

# Step 8: Run verification script
echo
echo "🧪 Running comprehensive verification..."
python verify_migration.py

echo
echo "=" | tr ' ' '=' | head -c 50; echo
echo "🎉 Migration process completed successfully!"
echo "📊 Database schema is ready for application use"