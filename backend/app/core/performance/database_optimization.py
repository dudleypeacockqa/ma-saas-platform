"""
Database Performance Optimization
Query optimization, connection pooling, and intelligent indexing
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import asyncpg
from asyncpg.pool import Pool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import text, event
import structlog

logger = structlog.get_logger()


class QueryType(Enum):
    """Query type classification"""
    OLTP = "oltp"  # Transactional
    OLAP = "olap"  # Analytical
    BATCH = "batch"  # Batch processing
    REALTIME = "realtime"  # Real-time queries


@dataclass
class QueryPlan:
    """Query execution plan"""
    query_id: str
    query_text: str
    execution_time: float
    rows_affected: int
    index_usage: List[str]
    optimization_hints: List[str]
    cost_estimate: float


@dataclass
class ConnectionPoolConfig:
    """Connection pool configuration"""
    min_size: int = 10
    max_size: int = 100
    max_queries: int = 50000
    max_inactive_connection_lifetime: float = 300.0
    timeout: float = 60.0
    command_timeout: float = 60.0
    max_cached_statement_lifetime: int = 3600
    max_cacheable_statement_size: int = 1024


class DatabaseOptimizer:
    """Main database optimization controller"""

    def __init__(self):
        self.pools: Dict[str, Pool] = {}
        self.query_cache = {}
        self.slow_query_log = []
        self.index_advisor = IndexAdvisor()
        self.query_optimizer = QueryOptimizer()
        self.connection_manager = ConnectionPoolManager()

    async def initialize(self, database_urls: Dict[str, str]) -> None:
        """Initialize database connections and optimization"""

        for name, url in database_urls.items():
            pool = await self._create_optimized_pool(url)
            self.pools[name] = pool

        # Start background optimization tasks
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._optimize_queries())
        asyncio.create_task(self._manage_connections())

    async def execute_optimized_query(
        self,
        query: str,
        params: Optional[List] = None,
        query_type: QueryType = QueryType.OLTP,
        timeout: Optional[float] = None
    ) -> Any:
        """Execute query with optimization"""

        # Get appropriate connection pool
        pool = self._select_pool(query_type)

        # Optimize query
        optimized_query = await self.query_optimizer.optimize(query, params)

        # Check query cache
        cache_key = self._generate_cache_key(optimized_query, params)
        cached_result = self.query_cache.get(cache_key)

        if cached_result and self._is_cache_valid(cached_result):
            logger.info("query_cache_hit", query=query[:50])
            return cached_result["result"]

        # Execute query
        start_time = datetime.utcnow()

        try:
            async with pool.acquire() as conn:
                # Set query timeout
                if timeout:
                    await conn.execute(f"SET statement_timeout = {int(timeout * 1000)}")

                # Execute with performance tracking
                result = await self._execute_with_tracking(
                    conn,
                    optimized_query,
                    params
                )

                # Cache result if appropriate
                if self._should_cache(query_type, result):
                    self.query_cache[cache_key] = {
                        "result": result,
                        "timestamp": datetime.utcnow(),
                        "ttl": self._get_cache_ttl(query_type)
                    }

                return result

        except asyncio.TimeoutError:
            logger.error("query_timeout", query=query[:50], timeout=timeout)
            raise
        finally:
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            # Log slow queries
            if execution_time > 1.0:
                await self._log_slow_query(query, execution_time)

    async def _create_optimized_pool(self, database_url: str) -> Pool:
        """Create optimized connection pool"""

        config = ConnectionPoolConfig()

        return await asyncpg.create_pool(
            database_url,
            min_size=config.min_size,
            max_size=config.max_size,
            max_queries=config.max_queries,
            max_inactive_connection_lifetime=config.max_inactive_connection_lifetime,
            timeout=config.timeout,
            command_timeout=config.command_timeout,
            max_cached_statement_lifetime=config.max_cached_statement_lifetime,
            max_cacheable_statement_size=config.max_cacheable_statement_size,
            init=self._init_connection
        )

    async def _init_connection(self, conn: asyncpg.Connection) -> None:
        """Initialize connection with optimizations"""

        # Set performance parameters
        await conn.execute("SET jit = 'on'")
        await conn.execute("SET random_page_cost = 1.1")
        await conn.execute("SET effective_cache_size = '8GB'")
        await conn.execute("SET shared_buffers = '2GB'")
        await conn.execute("SET work_mem = '64MB'")
        await conn.execute("SET maintenance_work_mem = '256MB'")

        # Enable query tracking
        await conn.execute("SET track_io_timing = 'on'")
        await conn.execute("SET track_functions = 'all'")

    def _select_pool(self, query_type: QueryType) -> Pool:
        """Select appropriate connection pool for query type"""

        if query_type == QueryType.OLAP:
            return self.pools.get("analytics", self.pools["primary"])
        elif query_type == QueryType.BATCH:
            return self.pools.get("batch", self.pools["primary"])
        elif query_type == QueryType.REALTIME:
            return self.pools.get("realtime", self.pools["primary"])
        else:
            return self.pools["primary"]

    async def _execute_with_tracking(
        self,
        conn: asyncpg.Connection,
        query: str,
        params: Optional[List]
    ) -> Any:
        """Execute query with performance tracking"""

        # Enable query explanation for analysis
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"

        try:
            # Get execution plan (in development mode)
            if logger.level <= 10:  # DEBUG level
                plan = await conn.fetchval(explain_query, *params if params else [])
                logger.debug("query_plan", plan=plan)
        except:
            pass  # Ignore explain errors

        # Execute actual query
        if params:
            result = await conn.fetch(query, *params)
        else:
            result = await conn.fetch(query)

        return result

    async def _monitor_performance(self) -> None:
        """Monitor database performance continuously"""

        while True:
            try:
                # Collect performance metrics
                metrics = await self._collect_performance_metrics()

                # Check for issues
                issues = self._identify_performance_issues(metrics)

                if issues:
                    logger.warning("database_performance_issues", issues=issues)

                    # Auto-remediate if possible
                    await self._auto_remediate(issues)

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error("performance_monitoring_error", error=str(e))
                await asyncio.sleep(120)

    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect database performance metrics"""

        metrics = {}

        async with self.pools["primary"].acquire() as conn:
            # Connection metrics
            metrics["connections"] = {
                "active": len([c for c in self.pools["primary"]._holders if c.in_use]),
                "idle": len([c for c in self.pools["primary"]._holders if not c.in_use]),
                "total": len(self.pools["primary"]._holders)
            }

            # Query performance
            stats = await conn.fetch("""
                SELECT
                    calls,
                    total_time,
                    mean_time,
                    max_time,
                    rows,
                    query
                FROM pg_stat_statements
                WHERE total_time > 1000
                ORDER BY total_time DESC
                LIMIT 10
            """)

            metrics["slow_queries"] = [
                {
                    "query": row["query"][:100],
                    "calls": row["calls"],
                    "avg_time": row["mean_time"],
                    "total_time": row["total_time"]
                }
                for row in stats
            ]

            # Table statistics
            table_stats = await conn.fetch("""
                SELECT
                    schemaname,
                    tablename,
                    n_live_tup,
                    n_dead_tup,
                    last_vacuum,
                    last_autovacuum
                FROM pg_stat_user_tables
                WHERE n_dead_tup > 1000
                ORDER BY n_dead_tup DESC
                LIMIT 10
            """)

            metrics["table_health"] = [
                {
                    "table": f"{row['schemaname']}.{row['tablename']}",
                    "dead_tuples": row["n_dead_tup"],
                    "needs_vacuum": row["n_dead_tup"] > row["n_live_tup"] * 0.2
                }
                for row in table_stats
            ]

            # Index usage
            index_stats = await conn.fetch("""
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                WHERE idx_scan = 0
                AND schemaname NOT IN ('pg_catalog', 'information_schema')
            """)

            metrics["unused_indexes"] = [
                {
                    "index": row["indexname"],
                    "table": f"{row['schemaname']}.{row['tablename']}"
                }
                for row in index_stats
            ]

        return metrics

    def _identify_performance_issues(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify performance issues from metrics"""

        issues = []

        # Connection pool exhaustion
        if metrics["connections"]["active"] > metrics["connections"]["total"] * 0.8:
            issues.append({
                "type": "connection_pool_exhaustion",
                "severity": "high",
                "message": f"Connection pool at {metrics['connections']['active']}/{metrics['connections']['total']} capacity"
            })

        # Slow queries
        for query in metrics.get("slow_queries", []):
            if query["avg_time"] > 1000:  # > 1 second
                issues.append({
                    "type": "slow_query",
                    "severity": "medium",
                    "query": query["query"],
                    "avg_time": query["avg_time"]
                })

        # Table maintenance needed
        for table in metrics.get("table_health", []):
            if table["needs_vacuum"]:
                issues.append({
                    "type": "vacuum_needed",
                    "severity": "low",
                    "table": table["table"],
                    "dead_tuples": table["dead_tuples"]
                })

        # Unused indexes
        if len(metrics.get("unused_indexes", [])) > 10:
            issues.append({
                "type": "unused_indexes",
                "severity": "low",
                "count": len(metrics["unused_indexes"]),
                "message": "Multiple unused indexes consuming resources"
            })

        return issues

    async def _auto_remediate(self, issues: List[Dict[str, Any]]) -> None:
        """Auto-remediate identified issues"""

        for issue in issues:
            try:
                if issue["type"] == "connection_pool_exhaustion":
                    # Increase pool size temporarily
                    await self.connection_manager.expand_pool(20)

                elif issue["type"] == "vacuum_needed":
                    # Schedule vacuum
                    asyncio.create_task(self._vacuum_table(issue["table"]))

                elif issue["type"] == "unused_indexes":
                    # Log for manual review (don't auto-drop)
                    logger.info("unused_indexes_detected", count=issue["count"])

            except Exception as e:
                logger.error("auto_remediation_failed", issue=issue, error=str(e))

    async def _vacuum_table(self, table_name: str) -> None:
        """Vacuum specific table"""

        async with self.pools["primary"].acquire() as conn:
            await conn.execute(f"VACUUM ANALYZE {table_name}")
            logger.info("table_vacuumed", table=table_name)

    async def _optimize_queries(self) -> None:
        """Continuous query optimization"""

        while True:
            try:
                # Analyze slow query log
                if self.slow_query_log:
                    for query_info in self.slow_query_log[-10:]:
                        # Generate optimization suggestions
                        suggestions = await self.query_optimizer.suggest_optimizations(
                            query_info["query"]
                        )

                        if suggestions:
                            logger.info("query_optimization_suggestions",
                                      query=query_info["query"][:50],
                                      suggestions=suggestions)

                    # Clear processed queries
                    self.slow_query_log = self.slow_query_log[-100:]

                await asyncio.sleep(300)  # Every 5 minutes

            except Exception as e:
                logger.error("query_optimization_error", error=str(e))
                await asyncio.sleep(600)

    async def _manage_connections(self) -> None:
        """Manage connection pools dynamically"""

        while True:
            try:
                await self.connection_manager.optimize_pools(self.pools)
                await asyncio.sleep(30)
            except Exception as e:
                logger.error("connection_management_error", error=str(e))
                await asyncio.sleep(60)

    def _generate_cache_key(self, query: str, params: Optional[List]) -> str:
        """Generate cache key for query"""

        import hashlib
        key_string = f"{query}:{str(params)}"
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]

    def _is_cache_valid(self, cached_item: Dict) -> bool:
        """Check if cached result is still valid"""

        ttl = cached_item.get("ttl", 60)
        age = (datetime.utcnow() - cached_item["timestamp"]).total_seconds()
        return age < ttl

    def _should_cache(self, query_type: QueryType, result: Any) -> bool:
        """Determine if result should be cached"""

        # Don't cache realtime or transactional queries
        if query_type in [QueryType.REALTIME, QueryType.OLTP]:
            return False

        # Cache analytical and batch queries
        return query_type in [QueryType.OLAP, QueryType.BATCH]

    def _get_cache_ttl(self, query_type: QueryType) -> int:
        """Get cache TTL for query type"""

        ttl_map = {
            QueryType.OLAP: 3600,  # 1 hour
            QueryType.BATCH: 1800,  # 30 minutes
            QueryType.OLTP: 60,  # 1 minute
            QueryType.REALTIME: 0  # No cache
        }

        return ttl_map.get(query_type, 60)

    async def _log_slow_query(self, query: str, execution_time: float) -> None:
        """Log slow query for analysis"""

        self.slow_query_log.append({
            "query": query,
            "execution_time": execution_time,
            "timestamp": datetime.utcnow()
        })

        # Also log to monitoring
        logger.warning("slow_query_detected",
                      query=query[:100],
                      execution_time=execution_time)


class QueryOptimizer:
    """Query optimization engine"""

    async def optimize(self, query: str, params: Optional[List]) -> str:
        """Optimize query for performance"""

        optimized = query

        # Add optimization hints
        if "SELECT" in query.upper():
            optimized = self._add_select_hints(optimized)

        # Optimize JOIN order
        if "JOIN" in query.upper():
            optimized = self._optimize_join_order(optimized)

        # Add appropriate indexes hints
        if "WHERE" in query.upper():
            optimized = self._add_index_hints(optimized)

        return optimized

    def _add_select_hints(self, query: str) -> str:
        """Add SELECT optimization hints"""

        # Add LIMIT if not present for safety
        if "LIMIT" not in query.upper() and "SELECT" in query.upper():
            # Check if it's a COUNT query
            if "COUNT(*)" not in query.upper():
                query += " LIMIT 10000"  # Safety limit

        return query

    def _optimize_join_order(self, query: str) -> str:
        """Optimize JOIN order for performance"""

        # This would analyze table statistics and reorder JOINs
        # For now, return as-is
        return query

    def _add_index_hints(self, query: str) -> str:
        """Add index usage hints"""

        # This would analyze available indexes and add hints
        # For now, return as-is
        return query

    async def suggest_optimizations(self, query: str) -> List[str]:
        """Suggest query optimizations"""

        suggestions = []

        # Check for missing indexes
        if "WHERE" in query.upper() and "INDEX" not in query.upper():
            suggestions.append("Consider adding index on WHERE clause columns")

        # Check for SELECT *
        if "SELECT *" in query.upper():
            suggestions.append("Avoid SELECT *, specify needed columns")

        # Check for missing LIMIT
        if "LIMIT" not in query.upper():
            suggestions.append("Add LIMIT clause to prevent large result sets")

        # Check for OR conditions
        if " OR " in query.upper():
            suggestions.append("Consider replacing OR with UNION for better performance")

        # Check for LIKE with leading wildcard
        if "LIKE '%" in query.upper():
            suggestions.append("Leading wildcard in LIKE prevents index usage")

        return suggestions


class IndexAdvisor:
    """Intelligent index advisory system"""

    async def analyze_workload(self, workload: List[str]) -> List[Dict[str, Any]]:
        """Analyze query workload and suggest indexes"""

        index_suggestions = []

        for query in workload:
            # Extract WHERE clause columns
            where_columns = self._extract_where_columns(query)

            # Extract JOIN columns
            join_columns = self._extract_join_columns(query)

            # Extract ORDER BY columns
            order_columns = self._extract_order_columns(query)

            # Generate index suggestions
            if where_columns:
                index_suggestions.append({
                    "type": "btree",
                    "columns": where_columns,
                    "reason": "Frequent WHERE clause filtering",
                    "estimated_improvement": "50-70%"
                })

            if join_columns:
                index_suggestions.append({
                    "type": "hash",
                    "columns": join_columns,
                    "reason": "JOIN optimization",
                    "estimated_improvement": "30-50%"
                })

            if order_columns:
                index_suggestions.append({
                    "type": "btree",
                    "columns": order_columns,
                    "reason": "ORDER BY optimization",
                    "estimated_improvement": "20-40%"
                })

        return self._deduplicate_suggestions(index_suggestions)

    def _extract_where_columns(self, query: str) -> List[str]:
        """Extract columns from WHERE clause"""

        # Simplified extraction - production would use SQL parser
        columns = []

        if "WHERE" in query.upper():
            # Extract column names (simplified)
            where_part = query.upper().split("WHERE")[1].split("ORDER BY")[0]
            # This is simplified - real implementation would parse properly
            words = where_part.split()
            for i, word in enumerate(words):
                if word in ["=", ">", "<", ">=", "<=", "LIKE", "IN"]:
                    if i > 0:
                        columns.append(words[i-1].strip("(),'\""))

        return columns

    def _extract_join_columns(self, query: str) -> List[str]:
        """Extract columns from JOIN conditions"""

        columns = []

        if "JOIN" in query.upper():
            # Extract JOIN condition columns (simplified)
            parts = query.upper().split("ON")
            for part in parts[1:]:
                # Extract column names around = sign
                if "=" in part:
                    eq_parts = part.split("=")
                    for eq_part in eq_parts:
                        words = eq_part.strip().split(".")
                        if len(words) > 1:
                            columns.append(words[-1].strip("() "))

        return columns

    def _extract_order_columns(self, query: str) -> List[str]:
        """Extract columns from ORDER BY clause"""

        columns = []

        if "ORDER BY" in query.upper():
            order_part = query.upper().split("ORDER BY")[1]
            # Extract column names (simplified)
            col_parts = order_part.split(",")
            for col in col_parts:
                columns.append(col.strip().split()[0])

        return columns

    def _deduplicate_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Remove duplicate index suggestions"""

        unique = {}

        for suggestion in suggestions:
            key = f"{suggestion['type']}:{','.join(suggestion['columns'])}"
            if key not in unique:
                unique[key] = suggestion

        return list(unique.values())


class ConnectionPoolManager:
    """Dynamic connection pool management"""

    def __init__(self):
        self.pool_stats = {}
        self.expansion_history = []

    async def optimize_pools(self, pools: Dict[str, Pool]) -> None:
        """Optimize connection pools based on usage"""

        for name, pool in pools.items():
            stats = await self._get_pool_stats(pool)
            self.pool_stats[name] = stats

            # Check if pool needs adjustment
            if stats["usage_ratio"] > 0.8:
                # High usage - consider expanding
                await self.expand_pool(pool, increment=10)
            elif stats["usage_ratio"] < 0.2 and stats["size"] > stats["min_size"]:
                # Low usage - consider shrinking
                await self.shrink_pool(pool, decrement=5)

    async def expand_pool(self, pool: Pool, increment: int = 10) -> None:
        """Expand connection pool"""

        current_size = len(pool._holders)
        new_size = min(current_size + increment, pool._maxsize)

        if new_size > current_size:
            pool._maxsize = new_size
            logger.info("pool_expanded", from_size=current_size, to_size=new_size)

            self.expansion_history.append({
                "timestamp": datetime.utcnow(),
                "action": "expand",
                "size_change": increment
            })

    async def shrink_pool(self, pool: Pool, decrement: int = 5) -> None:
        """Shrink connection pool"""

        current_size = len(pool._holders)
        new_size = max(current_size - decrement, pool._minsize)

        if new_size < current_size:
            # Close idle connections
            for holder in pool._holders:
                if not holder.in_use and len(pool._holders) > new_size:
                    await holder.close()

            logger.info("pool_shrinked", from_size=current_size, to_size=new_size)

            self.expansion_history.append({
                "timestamp": datetime.utcnow(),
                "action": "shrink",
                "size_change": -decrement
            })

    async def _get_pool_stats(self, pool: Pool) -> Dict[str, Any]:
        """Get connection pool statistics"""

        active = len([h for h in pool._holders if h.in_use])
        idle = len([h for h in pool._holders if not h.in_use])
        total = len(pool._holders)

        return {
            "active": active,
            "idle": idle,
            "size": total,
            "min_size": pool._minsize,
            "max_size": pool._maxsize,
            "usage_ratio": active / total if total > 0 else 0
        }


class PreparedStatementCache:
    """Cache for prepared statements"""

    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}

    async def get_or_prepare(
        self,
        conn: asyncpg.Connection,
        query: str
    ) -> asyncpg.PreparedStatement:
        """Get or prepare statement"""

        if query in self.cache:
            self.access_count[query] = self.access_count.get(query, 0) + 1
            return self.cache[query]

        # Prepare new statement
        stmt = await conn.prepare(query)

        # Add to cache if space available
        if len(self.cache) < self.max_size:
            self.cache[query] = stmt
            self.access_count[query] = 1
        else:
            # Evict least used
            await self._evict_lru()
            self.cache[query] = stmt
            self.access_count[query] = 1

        return stmt

    async def _evict_lru(self) -> None:
        """Evict least recently used statement"""

        if not self.access_count:
            return

        # Find least accessed
        min_query = min(self.access_count, key=self.access_count.get)

        # Remove from cache
        del self.cache[min_query]
        del self.access_count[min_query]