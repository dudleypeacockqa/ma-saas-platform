# Database Migration Guide for M&A SaaS Platform

## Overview

This guide provides step-by-step instructions for running database migrations on Render, where the database is not publicly accessible and must be executed from within the Render network environment.

## Prerequisites

- Render account with deployed `ma-saas-backend` service
- PostgreSQL database `ma-saas-db` provisioned and connected
- All environment variables properly configured in Render dashboard

## Configuration Status ✅

- **Alembic Configuration**: Cleaned up merge conflicts and properly configured to use `DATABASE_URL` from environment
- **Migration Environment**: Properly imports all required models (Organization, User, Subscription, etc.)
- **Database URL**: Handled via environment variables, no hardcoded values

## Migration Execution Steps

### Step 1: Access Render Shell

1. Navigate to the [Render Dashboard](https://dashboard.render.com)
2. Go to your `ma-saas-backend` service
3. Click on the "Shell" tab to open a terminal session
4. Wait for the shell to initialize (may take 30-60 seconds)

### Step 2: Navigate to Backend Directory

```bash
cd /opt/render/project/src/backend
```

### Step 3: Verify Environment

```bash
# Verify you're in the correct directory
pwd
ls -la

# Check that DATABASE_URL is available
echo $DATABASE_URL | cut -c1-30  # Shows first 30 chars for verification

# Verify Python environment
python --version
which python
```

### Step 4: Install Dependencies (if needed)

```bash
# Install requirements if not already installed
pip install -r requirements.txt

# Verify Alembic installation
alembic --version
```

### Step 5: Check Migration Status

```bash
# Check current migration status
alembic current

# List available migrations
alembic history --verbose
```

### Step 6: Run Migrations

```bash
# Execute all pending migrations
alembic upgrade head
```

### Step 7: Verify Migration Success

```bash
# Check final migration status
alembic current

# Verify database connection (optional)
python -c "
from app.core.config import settings
import psycopg
try:
    conn = psycopg.connect(settings.DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\';')
    tables = cursor.fetchall()
    print('Tables created:', [t[0] for t in tables])
    conn.close()
    print('✅ Database connection and schema verification successful')
except Exception as e:
    print('❌ Database verification failed:', e)
"
```

## Expected Migration Output

When successful, you should see output similar to:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial migration: Create multi-tenant schema
```

## Expected Database Schema

The migration creates the following tables:

- **organizations** - Core tenant/organization data
- **users** - User accounts and authentication
- **organization_memberships** - User-organization relationships
- **subscriptions** - Billing and subscription management
- **organization_settings** - Tenant-specific configuration
- **invoices** - Billing invoice records
- **usage_records** - Usage tracking for billing

## Troubleshooting

### Common Issues and Solutions

#### Issue: "alembic: command not found"

```bash
# Install alembic if missing
pip install alembic==1.14.0
```

#### Issue: "ModuleNotFoundError: No module named 'app'"

```bash
# Ensure you're in the backend directory
cd /opt/render/project/src/backend
export PYTHONPATH=/opt/render/project/src/backend:$PYTHONPATH
```

#### Issue: "sqlalchemy.exc.OperationalError: connection failed"

```bash
# Verify DATABASE_URL environment variable
echo $DATABASE_URL | grep -o "^[^:]*://[^@]*@[^/]*"
# Should show postgresql://user@host format
```

#### Issue: Migration partially failed

```bash
# Check current migration state
alembic current

# If needed, downgrade and retry
alembic downgrade -1
alembic upgrade head
```

## Rollback Procedures

If migration needs to be rolled back:

```bash
# Downgrade to previous version
alembic downgrade -1

# Or downgrade to base (removes all tables)
alembic downgrade base
```

⚠️ **Warning**: Rollback will delete all data. Only use in development environment.

## Verification Checklist

After successful migration:

- [ ] `alembic current` shows migration 001
- [ ] All expected tables exist in database
- [ ] Application can connect to database
- [ ] No error messages in migration output
- [ ] Environment variables properly configured

## Next Steps

After successful migration:

1. Test application database connectivity
2. Verify authentication flow works
3. Test basic CRUD operations
4. Deploy application updates
5. Monitor application logs for database-related issues

## Support

If you encounter issues:

1. Check the full error message in Render shell
2. Verify all environment variables are set correctly
3. Ensure database service is running and accessible
4. Review Render service logs for additional context

## Migration History

| Version | Description                 | Date    | Status   |
| ------- | --------------------------- | ------- | -------- |
| 001     | Initial multi-tenant schema | Current | ✅ Ready |

---

_This guide will be updated as new migrations are added to the system._
