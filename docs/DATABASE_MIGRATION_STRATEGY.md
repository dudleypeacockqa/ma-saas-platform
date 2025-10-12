# Database Migration Strategy - Multi-Tenant PostgreSQL Implementation

**Objective**: Seamless database setup and evolution for multi-tenant M&A platform
**Priority**: CRITICAL - Foundation for all services
**Dependencies**: PostgreSQL 15+, Alembic, Multi-tenant isolation

---

## 🏗️ **MULTI-TENANT DATABASE ARCHITECTURE**

### **Schema-Based Tenant Isolation Strategy**

```sql
-- Master tenant registry and schema management
CREATE SCHEMA IF NOT EXISTS platform_core;

-- Core platform tables (cross-tenant)
CREATE TABLE platform_core.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_slug VARCHAR(50) UNIQUE NOT NULL, -- subdomain identifier
    tenant_name VARCHAR(255) NOT NULL,

    -- Subscription and billing
    subscription_tier VARCHAR(50) NOT NULL DEFAULT 'trial',
    subscription_status VARCHAR(20) NOT NULL DEFAULT 'active',
    billing_email VARCHAR(255),

    -- Schema management
    database_schema_name VARCHAR(50) UNIQUE NOT NULL,
    schema_created_at TIMESTAMP WITH TIME ZONE,
    schema_version VARCHAR(20) DEFAULT '1.0',

    -- Usage and limits
    user_limit INTEGER DEFAULT 5,
    deal_limit INTEGER DEFAULT 100,
    storage_limit_gb INTEGER DEFAULT 10,

    -- Audit and lifecycle
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,

    INDEX idx_tenants_slug (tenant_slug),
    INDEX idx_tenants_schema (database_schema_name),
    INDEX idx_tenants_status (subscription_status, is_active)
);

-- Schema creation tracking
CREATE TABLE platform_core.schema_migrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES platform_core.tenants(id),
    migration_version VARCHAR(50) NOT NULL,
    migration_name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    execution_time_ms INTEGER,
    success BOOLEAN NOT NULL,
    error_message TEXT,

    UNIQUE(tenant_id, migration_version),
    INDEX idx_migrations_tenant (tenant_id, applied_at),
    INDEX idx_migrations_version (migration_version, success)
);
```

### **Tenant Schema Creation Process**

```python
# Automated tenant schema management
class TenantSchemaManager:
    """Manages creation and evolution of tenant-specific schemas"""

    def __init__(self, db_connection, alembic_config):
        self.db = db_connection
        self.alembic_config = alembic_config
        self.schema_templates = SchemaTemplates()

    async def create_tenant_schema(self, tenant_id: str, tenant_slug: str) -> TenantSchema:
        """Create complete schema for new tenant"""

        schema_name = f"tenant_{tenant_slug}"

        try:
            # 1. Create PostgreSQL schema
            await self._create_postgres_schema(schema_name)

            # 2. Apply all migrations to new schema
            await self._apply_initial_migrations(schema_name)

            # 3. Create tenant-specific indexes
            await self._create_performance_indexes(schema_name)

            # 4. Set up row-level security policies
            await self._configure_rls_policies(schema_name)

            # 5. Create initial data (pipeline stages, etc.)
            await self._seed_initial_data(schema_name, tenant_id)

            # 6. Update tenant registry
            await self._register_schema_creation(tenant_id, schema_name)

            logger.info(f"Created schema {schema_name} for tenant {tenant_id}")

            return TenantSchema(
                tenant_id=tenant_id,
                schema_name=schema_name,
                version="1.0",
                created_at=datetime.utcnow()
            )

        except Exception as e:
            # Rollback on failure
            await self._rollback_schema_creation(schema_name)
            raise TenantSchemaCreationError(f"Failed to create schema for {tenant_id}: {e}")

    async def _create_postgres_schema(self, schema_name: str):
        """Create PostgreSQL schema with proper permissions"""

        schema_sql = f"""
        CREATE SCHEMA IF NOT EXISTS {schema_name};

        -- Grant usage to application user
        GRANT USAGE ON SCHEMA {schema_name} TO ma_platform_app;
        GRANT CREATE ON SCHEMA {schema_name} TO ma_platform_app;

        -- Set default privileges for new tables
        ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name}
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ma_platform_app;

        ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name}
        GRANT USAGE, SELECT ON SEQUENCES TO ma_platform_app;
        """

        await self.db.execute(schema_sql)

    async def _apply_initial_migrations(self, schema_name: str):
        """Apply all current migrations to new tenant schema"""

        # Set schema search path for migrations
        alembic_env = {
            'schema_name': schema_name,
            'target_metadata': get_tenant_metadata()
        }

        # Run Alembic migrations in tenant schema context
        with self.alembic_config.begin_transaction() as connection:
            connection.execute(f"SET search_path TO {schema_name}")

            # Apply all migrations up to current head
            alembic.command.upgrade(self.alembic_config, "head")

    async def _create_performance_indexes(self, schema_name: str):
        """Create performance-critical indexes for tenant schema"""

        performance_indexes = [
            # Deal management indexes
            f"CREATE INDEX CONCURRENTLY idx_{schema_name}_deals_search ON {schema_name}.deals USING gin(to_tsvector('english', deal_name || ' ' || COALESCE(description, '')))",
            f"CREATE INDEX CONCURRENTLY idx_{schema_name}_deals_value ON {schema_name}.deals (enterprise_value DESC NULLS LAST)",
            f"CREATE INDEX CONCURRENTLY idx_{schema_name}_deals_stage_date ON {schema_name}.deals (current_stage_id, expected_close_date)",

            # Activity indexes for real-time features
            f"CREATE INDEX CONCURRENTLY idx_{schema_name}_activities_timeline ON {schema_name}.deal_activities (deal_id, created_at DESC)",
            f"CREATE INDEX CONCURRENTLY idx_{schema_name}_activities_user ON {schema_name}.deal_activities (lead_participant_id, scheduled_at)",

            # Document indexes for fast retrieval
            f"CREATE INDEX CONCURRENTLY idx_{schema_name}_documents_deal_type ON {schema_name}.deal_documents (deal_id, document_type, uploaded_at DESC)",

            # Financial data indexes
            f"CREATE INDEX CONCURRENTLY idx_{schema_name}_financial_snapshots_date ON {schema_name}.financial_snapshots (connection_id, period_end DESC)",

            # Matching and analytics indexes
            f"CREATE INDEX CONCURRENTLY idx_{schema_name}_matching_results_score ON {schema_name}.matching_results (overall_similarity_score DESC, confidence_score DESC)"
        ]

        for index_sql in performance_indexes:
            try:
                await self.db.execute(index_sql)
            except Exception as e:
                logger.warning(f"Failed to create index: {e}")

    async def _configure_rls_policies(self, schema_name: str):
        """Configure Row Level Security for additional data protection"""

        rls_policies = [
            # Enable RLS on all tenant tables
            f"ALTER TABLE {schema_name}.deals ENABLE ROW LEVEL SECURITY",
            f"ALTER TABLE {schema_name}.deal_activities ENABLE ROW LEVEL SECURITY",
            f"ALTER TABLE {schema_name}.deal_documents ENABLE ROW LEVEL SECURITY",

            # Create policies for application access
            f"""CREATE POLICY tenant_isolation_deals ON {schema_name}.deals
                FOR ALL TO ma_platform_app
                USING (current_setting('app.current_tenant_id') = tenant_id::text)""",

            f"""CREATE POLICY tenant_isolation_activities ON {schema_name}.deal_activities
                FOR ALL TO ma_platform_app
                USING (current_setting('app.current_tenant_id') = tenant_id::text)""",

            f"""CREATE POLICY tenant_isolation_documents ON {schema_name}.deal_documents
                FOR ALL TO ma_platform_app
                USING (current_setting('app.current_tenant_id') = tenant_id::text)"""
        ]

        for policy_sql in rls_policies:
            await self.db.execute(policy_sql)
```

---

## 🔄 **MIGRATION MANAGEMENT SYSTEM**

### **Alembic Configuration for Multi-Tenant**

```python
# Custom Alembic environment for multi-tenant migrations
class MultiTenantAlembicEnvironment:
    """Custom Alembic environment supporting multi-tenant schema migrations"""

    def __init__(self):
        self.tenant_manager = TenantManager()

    def run_migrations_online(self):
        """Run migrations for all active tenants"""

        # Connect to database
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            # First, run platform core migrations
            self._run_platform_migrations(connection)

            # Then, run tenant-specific migrations
            active_tenants = self._get_active_tenants(connection)

            for tenant in active_tenants:
                self._run_tenant_migrations(connection, tenant)

    def _run_platform_migrations(self, connection):
        """Run migrations for platform core schema"""

        connection.execute("SET search_path TO platform_core")

        context.configure(
            connection=connection,
            target_metadata=platform_core_metadata,
            version_table_schema="platform_core",
            include_schemas=["platform_core"]
        )

        with context.begin_transaction():
            context.run_migrations()

    def _run_tenant_migrations(self, connection, tenant: TenantInfo):
        """Run migrations for specific tenant schema"""

        schema_name = tenant.database_schema_name

        # Set search path to tenant schema
        connection.execute(f"SET search_path TO {schema_name}")

        # Configure Alembic context for tenant
        context.configure(
            connection=connection,
            target_metadata=tenant_metadata,
            version_table_schema=schema_name,
            include_schemas=[schema_name],
            version_table=f"alembic_version_{schema_name}"
        )

        with context.begin_transaction():
            try:
                context.run_migrations()

                # Log successful migration
                self._log_migration_success(tenant.id, context.get_current_revision())

            except Exception as e:
                # Log migration failure
                self._log_migration_failure(tenant.id, str(e))
                raise

    def _get_active_tenants(self, connection) -> List[TenantInfo]:
        """Get all active tenants requiring migration"""

        result = connection.execute("""
            SELECT id, tenant_slug, database_schema_name, schema_version
            FROM platform_core.tenants
            WHERE is_active = true
            ORDER BY created_at
        """)

        return [TenantInfo(**row) for row in result.fetchall()]
```

### **Zero-Downtime Migration Strategy**

```python
# Zero-downtime migration implementation
class ZeroDowntimeMigrations:
    """Implement database changes without service interruption"""

    def __init__(self):
        self.migration_coordinator = MigrationCoordinator()
        self.schema_versioning = SchemaVersioning()

    async def execute_zero_downtime_migration(self, migration_plan: MigrationPlan) -> MigrationResult:
        """Execute database migration with zero downtime"""

        migration_id = str(uuid.uuid4())

        try:
            # Phase 1: Preparation (background)
            await self._prepare_migration(migration_plan, migration_id)

            # Phase 2: Schema changes (minimal lock time)
            await self._apply_schema_changes(migration_plan, migration_id)

            # Phase 3: Data migration (background, batched)
            await self._migrate_data_in_batches(migration_plan, migration_id)

            # Phase 4: Cleanup and finalization
            await self._finalize_migration(migration_plan, migration_id)

            return MigrationResult(
                migration_id=migration_id,
                status="completed",
                duration_seconds=self._get_migration_duration(migration_id),
                affected_tenants=migration_plan.target_tenants,
                downtime_seconds=0
            )

        except Exception as e:
            # Rollback strategy
            await self._rollback_migration(migration_plan, migration_id, str(e))
            raise

    async def _prepare_migration(self, plan: MigrationPlan, migration_id: str):
        """Prepare migration without affecting live traffic"""

        # Create migration tracking
        await self._create_migration_tracking(migration_id, plan)

        # Validate migration safety
        safety_check = await self._validate_migration_safety(plan)
        if not safety_check.is_safe:
            raise MigrationSafetyError(safety_check.issues)

        # Pre-create new columns/tables if needed
        for change in plan.schema_changes:
            if change.change_type in ["add_column", "create_table"]:
                await self._pre_create_schema_objects(change)

    async def _apply_schema_changes(self, plan: MigrationPlan, migration_id: str):
        """Apply schema changes with minimal lock time"""

        for tenant in plan.target_tenants:
            schema_name = tenant.database_schema_name

            # Use advisory locks to coordinate
            async with self._acquire_schema_lock(schema_name):
                # Apply changes atomically
                async with self.db.transaction():
                    for change in plan.schema_changes:
                        await self._apply_single_change(schema_name, change)

                    # Update schema version
                    await self._update_schema_version(tenant.id, plan.target_version)

    async def _migrate_data_in_batches(self, plan: MigrationPlan, migration_id: str):
        """Migrate data in small batches to avoid locks"""

        if not plan.data_migrations:
            return

        for tenant in plan.target_tenants:
            for data_migration in plan.data_migrations:
                await self._process_data_migration_batches(
                    tenant.database_schema_name,
                    data_migration,
                    batch_size=1000,
                    migration_id=migration_id
                )

    async def _process_data_migration_batches(self, schema_name: str,
                                            data_migration: DataMigration,
                                            batch_size: int,
                                            migration_id: str):
        """Process data migration in small batches"""

        total_rows = await self._count_migration_rows(schema_name, data_migration)
        processed_rows = 0

        while processed_rows < total_rows:
            batch_start = processed_rows
            batch_end = min(processed_rows + batch_size, total_rows)

            # Process batch with progress tracking
            await self._process_migration_batch(
                schema_name, data_migration, batch_start, batch_end
            )

            processed_rows = batch_end

            # Log progress
            await self._log_migration_progress(
                migration_id, schema_name, processed_rows, total_rows
            )

            # Brief pause to avoid overwhelming database
            await asyncio.sleep(0.1)
```

---

## 📊 **DATABASE PERFORMANCE OPTIMIZATION**

### **Connection Pool Management**

```python
# Optimized connection pooling for multi-tenant architecture
class MultiTenantConnectionPool:
    """Optimized connection pooling supporting multi-tenant workloads"""

    def __init__(self):
        self.pools = {}  # Per-service connection pools
        self.tenant_cache = TenantCache()
        self.query_optimizer = QueryOptimizer()

    async def get_tenant_connection(self, tenant_id: str, service: str) -> Connection:
        """Get optimized connection for tenant and service"""

        # Get tenant schema information
        tenant_info = await self.tenant_cache.get_tenant_info(tenant_id)

        # Get or create service-specific pool
        pool_key = f"{service}_{tenant_info.database_schema_name}"
        if pool_key not in self.pools:
            self.pools[pool_key] = await self._create_service_pool(service, tenant_info)

        # Acquire connection from pool
        connection = await self.pools[pool_key].acquire()

        # Set tenant context
        await connection.execute(f"SET app.current_tenant_id = '{tenant_id}'")
        await connection.execute(f"SET search_path = {tenant_info.database_schema_name}")

        return connection

    async def _create_service_pool(self, service: str, tenant_info: TenantInfo) -> ConnectionPool:
        """Create optimized connection pool for service"""

        pool_config = {
            "min_size": SERVICE_POOL_CONFIG[service]["min_connections"],
            "max_size": SERVICE_POOL_CONFIG[service]["max_connections"],
            "max_queries": 50000,  # Rotate connections after 50k queries
            "max_inactive_connection_lifetime": 300,  # 5 minutes
            "command_timeout": 30
        }

        return await asyncpg.create_pool(
            host=os.getenv("DATABASE_HOST"),
            port=int(os.getenv("DATABASE_PORT", 5432)),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            database=os.getenv("DATABASE_NAME"),
            **pool_config
        )

# Service-specific connection pool sizing
SERVICE_POOL_CONFIG = {
    "deal-service": {"min_connections": 5, "max_connections": 20},
    "financial-intelligence": {"min_connections": 3, "max_connections": 15},
    "template-engine": {"min_connections": 2, "max_connections": 10},
    "document-service": {"min_connections": 3, "max_connections": 12},
    "deal-matching": {"min_connections": 2, "max_connections": 8},
    "notification-service": {"min_connections": 2, "max_connections": 8},
    "analytics-service": {"min_connections": 2, "max_connections": 10}
}
```

### **Query Performance Optimization**

```sql
-- Performance monitoring and optimization queries
-- 1. Identify slow queries across all tenant schemas
CREATE OR REPLACE FUNCTION analyze_slow_queries()
RETURNS TABLE (
    schema_name TEXT,
    query TEXT,
    total_time NUMERIC,
    calls BIGINT,
    mean_time NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        schemaname::TEXT,
        query::TEXT,
        total_exec_time as total_time,
        calls,
        mean_exec_time as mean_time
    FROM pg_stat_statements
    WHERE schemaname LIKE 'tenant_%'
    ORDER BY total_exec_time DESC
    LIMIT 50;
END;
$$ LANGUAGE plpgsql;

-- 2. Monitor index usage across tenant schemas
CREATE OR REPLACE FUNCTION monitor_index_usage()
RETURNS TABLE (
    schema_name TEXT,
    table_name TEXT,
    index_name TEXT,
    index_scans BIGINT,
    tuples_read BIGINT,
    tuples_fetched BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        schemaname::TEXT,
        tablename::TEXT,
        indexrelname::TEXT,
        idx_scan,
        idx_tup_read,
        idx_tup_fetch
    FROM pg_stat_user_indexes
    WHERE schemaname LIKE 'tenant_%'
    ORDER BY idx_scan DESC;
END;
$$ LANGUAGE plpgsql;

-- 3. Tenant storage usage monitoring
CREATE OR REPLACE FUNCTION tenant_storage_usage()
RETURNS TABLE (
    tenant_id UUID,
    schema_name TEXT,
    total_size_mb NUMERIC,
    table_count INTEGER,
    index_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id as tenant_id,
        t.database_schema_name::TEXT,
        (pg_size_pretty(pg_total_relation_size(c.oid))::NUMERIC / 1024 / 1024) as total_size_mb,
        COUNT(DISTINCT c.relname)::INTEGER as table_count,
        COUNT(DISTINCT i.indexrelname)::INTEGER as index_count
    FROM platform_core.tenants t
    JOIN pg_class c ON c.relnamespace = (
        SELECT oid FROM pg_namespace WHERE nspname = t.database_schema_name
    )
    LEFT JOIN pg_stat_user_indexes i ON i.schemaname = t.database_schema_name
    WHERE t.is_active = true
    GROUP BY t.id, t.database_schema_name, c.oid;
END;
$$ LANGUAGE plpgsql;
```

---

## 🔒 **BACKUP AND DISASTER RECOVERY**

### **Automated Backup Strategy**

```python
# Comprehensive backup and recovery system
class DatabaseBackupSystem:
    """Automated backup and disaster recovery for multi-tenant database"""

    def __init__(self):
        self.backup_storage = CloudBackupStorage()
        self.encryption = BackupEncryption()
        self.scheduler = BackupScheduler()

    async def setup_backup_strategy(self) -> BackupConfiguration:
        """Configure comprehensive backup strategy"""

        backup_config = BackupConfiguration(
            # Full database backups
            full_backup_schedule="daily at 02:00 UTC",
            full_backup_retention_days=30,

            # Incremental backups
            incremental_backup_schedule="every 4 hours",
            incremental_backup_retention_days=7,

            # Transaction log backups
            log_backup_schedule="every 15 minutes",
            log_backup_retention_hours=72,

            # Point-in-time recovery capability
            pitr_retention_days=7,

            # Cross-region replication
            replica_regions=["us-east-1", "eu-west-1"],
            replica_lag_tolerance_seconds=30
        )

        await self.scheduler.configure_backups(backup_config)
        return backup_config

    async def execute_tenant_backup(self, tenant_id: str, backup_type: str) -> BackupResult:
        """Execute backup for specific tenant"""

        tenant_info = await self.tenant_manager.get_tenant_info(tenant_id)
        schema_name = tenant_info.database_schema_name

        backup_id = f"{tenant_id}_{backup_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        try:
            if backup_type == "full":
                result = await self._execute_full_schema_backup(schema_name, backup_id)
            elif backup_type == "incremental":
                result = await self._execute_incremental_backup(schema_name, backup_id)
            else:
                raise ValueError(f"Unknown backup type: {backup_type}")

            # Encrypt and store backup
            encrypted_backup = await self.encryption.encrypt_backup(result.backup_data)
            storage_path = await self.backup_storage.store_backup(encrypted_backup, backup_id)

            # Update backup metadata
            await self._record_backup_metadata(tenant_id, backup_id, storage_path, result)

            return BackupResult(
                backup_id=backup_id,
                tenant_id=tenant_id,
                backup_type=backup_type,
                size_bytes=result.size_bytes,
                duration_seconds=result.duration_seconds,
                storage_path=storage_path,
                success=True
            )

        except Exception as e:
            await self._record_backup_failure(tenant_id, backup_id, str(e))
            raise BackupError(f"Backup failed for tenant {tenant_id}: {e}")

    async def restore_tenant_from_backup(self, tenant_id: str,
                                       backup_id: str = None,
                                       point_in_time: datetime = None) -> RestoreResult:
        """Restore tenant data from backup or point-in-time"""

        if backup_id and point_in_time:
            raise ValueError("Cannot specify both backup_id and point_in_time")

        tenant_info = await self.tenant_manager.get_tenant_info(tenant_id)

        if point_in_time:
            # Point-in-time recovery
            return await self._restore_point_in_time(tenant_info, point_in_time)
        else:
            # Backup-based recovery
            backup_id = backup_id or await self._find_latest_backup(tenant_id)
            return await self._restore_from_backup(tenant_info, backup_id)

    async def _execute_full_schema_backup(self, schema_name: str, backup_id: str) -> BackupData:
        """Execute full backup of tenant schema"""

        backup_sql = f"""
        pg_dump
            --host={os.getenv('DATABASE_HOST')}
            --port={os.getenv('DATABASE_PORT')}
            --username={os.getenv('DATABASE_USER')}
            --dbname={os.getenv('DATABASE_NAME')}
            --schema={schema_name}
            --format=custom
            --compress=9
            --verbose
            --file=/tmp/{backup_id}.dump
        """

        start_time = time.time()
        process = await asyncio.create_subprocess_shell(
            backup_sql,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()
        duration = time.time() - start_time

        if process.returncode != 0:
            raise BackupError(f"pg_dump failed: {stderr.decode()}")

        # Read backup file
        backup_path = f"/tmp/{backup_id}.dump"
        with open(backup_path, 'rb') as f:
            backup_data = f.read()

        # Cleanup temporary file
        os.remove(backup_path)

        return BackupData(
            backup_data=backup_data,
            size_bytes=len(backup_data),
            duration_seconds=duration,
            backup_type="full"
        )
```

This database migration strategy provides the robust foundation needed for your multi-tenant M&A platform, ensuring seamless scalability, zero-downtime operations, and enterprise-grade reliability as you grow from startup to £200M valuation.
