"""
Data Warehouse Service for Analytics
Handles ETL, data aggregation, and metric computation
"""
import asyncio
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import func, select, and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
import pandas as pd
import numpy as np
import redis
import json
import hashlib
from enum import Enum

from app.models.analytics import (
    MetricSnapshot, AggregatedMetric, MetricType,
    AggregationPeriod, AlertConfiguration, AlertHistory,
    AlertSeverity, ComparisonOperator
)
from app.models.deal import Deal, DealStage
from app.models.prospects import Prospect, ProspectStatus, OutreachCampaign
from app.models.organization import Organization
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)

class DataWarehouse:
    """
    Central data warehouse for analytics processing
    Handles ETL, aggregation, and caching
    """

    def __init__(self, db: Session, redis_client: Optional[redis.Redis] = None):
        self.db = db
        self.redis = redis_client or redis.Redis(
            host='localhost', port=6379, decode_responses=True
        )
        self.cache_ttl = 3600  # 1 hour default cache

    # ETL Pipeline Methods
    async def extract_metrics(self, organization_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Extract metrics from various data sources
        """
        metrics = {}

        # Extract SaaS metrics
        metrics['saas'] = await self._extract_saas_metrics(organization_id, start_date, end_date)

        # Extract deal metrics
        metrics['deals'] = await self._extract_deal_metrics(organization_id, start_date, end_date)

        # Extract content metrics
        metrics['content'] = await self._extract_content_metrics(organization_id, start_date, end_date)

        # Extract prospect metrics
        metrics['prospects'] = await self._extract_prospect_metrics(organization_id, start_date, end_date)

        return metrics

    async def _extract_saas_metrics(self, org_id: str, start_date: date, end_date: date) -> Dict:
        """Extract SaaS platform metrics"""
        org = self.db.query(Organization).filter(Organization.id == org_id).first()

        if not org:
            return {}

        # Calculate subscribers (simplified - in real app would track actual subscriptions)
        total_users = self.db.query(func.count()).select_from(
            self.db.query(Organization).filter(Organization.created_at <= end_date)
        ).scalar()

        # Calculate MRR based on subscription tiers
        tier_pricing = {
            'free': 0,
            'starter': 99,
            'professional': 499,
            'enterprise': 999
        }

        mrr = self.db.query(
            func.sum(
                func.coalesce(
                    func.cast(tier_pricing.get(Organization.subscription_tier, 0), Decimal),
                    0
                )
            )
        ).filter(
            Organization.created_at <= end_date
        ).scalar() or Decimal('0')

        return {
            'total_organizations': total_users,
            'mrr': float(mrr),
            'arr': float(mrr * 12),
            'active_users': total_users,  # Simplified
            'churn_rate': 0.05  # Placeholder - would calculate from actual data
        }

    async def _extract_deal_metrics(self, org_id: str, start_date: date, end_date: date) -> Dict:
        """Extract deal pipeline metrics"""
        deals = self.db.query(Deal).filter(
            Deal.organization_id == org_id,
            Deal.created_at.between(start_date, end_date)
        ).all()

        total_value = sum(deal.deal_value or 0 for deal in deals)
        won_deals = [d for d in deals if d.stage == DealStage.CLOSED_WON]
        lost_deals = [d for d in deals if d.stage == DealStage.CLOSED_LOST]

        win_rate = (len(won_deals) / len(deals) * 100) if deals else 0

        # Calculate average deal velocity
        closed_deals = won_deals + lost_deals
        avg_velocity = np.mean([
            d.days_in_pipeline for d in closed_deals if d.days_in_pipeline
        ]) if closed_deals else 0

        return {
            'total_deals': len(deals),
            'pipeline_value': float(total_value),
            'won_deals': len(won_deals),
            'lost_deals': len(lost_deals),
            'win_rate': win_rate,
            'avg_deal_velocity': avg_velocity,
            'avg_deal_size': float(total_value / len(deals)) if deals else 0
        }

    async def _extract_content_metrics(self, org_id: str, start_date: date, end_date: date) -> Dict:
        """Extract content and podcast metrics"""
        # Placeholder - would integrate with actual podcast/content APIs
        return {
            'podcast_downloads': np.random.randint(5000, 15000),
            'podcast_listeners': np.random.randint(2000, 8000),
            'blog_views': np.random.randint(10000, 50000),
            'content_engagement': np.random.uniform(0.02, 0.08),
            'social_reach': np.random.randint(50000, 200000)
        }

    async def _extract_prospect_metrics(self, org_id: str, start_date: date, end_date: date) -> Dict:
        """Extract prospect and lead metrics"""
        prospects = self.db.query(Prospect).filter(
            Prospect.organization_id == org_id,
            Prospect.created_at.between(start_date, end_date)
        ).all()

        qualified = [p for p in prospects if p.status == ProspectStatus.QUALIFIED]
        converted = [p for p in prospects if p.status == ProspectStatus.CUSTOMER]

        return {
            'total_prospects': len(prospects),
            'qualified_leads': len(qualified),
            'converted_customers': len(converted),
            'conversion_rate': (len(converted) / len(prospects) * 100) if prospects else 0,
            'avg_lead_score': np.mean([p.lead_score for p in prospects]) if prospects else 0
        }

    async def transform_metrics(self, raw_metrics: Dict) -> List[MetricSnapshot]:
        """
        Transform raw metrics into standardized format
        """
        snapshots = []
        timestamp = datetime.utcnow()

        # Transform SaaS metrics
        for metric_name, value in raw_metrics.get('saas', {}).items():
            metric_type = self._map_metric_type(metric_name)
            if metric_type:
                snapshots.append(MetricSnapshot(
                    metric_type=metric_type,
                    metric_value=Decimal(str(value)),
                    timestamp=timestamp,
                    date=timestamp.date(),
                    hour=timestamp.hour,
                    source='etl_pipeline',
                    dimensions={'category': 'saas'},
                ))

        # Transform deal metrics
        for metric_name, value in raw_metrics.get('deals', {}).items():
            metric_type = self._map_metric_type(metric_name)
            if metric_type:
                snapshots.append(MetricSnapshot(
                    metric_type=metric_type,
                    metric_value=Decimal(str(value)),
                    timestamp=timestamp,
                    date=timestamp.date(),
                    hour=timestamp.hour,
                    source='etl_pipeline',
                    dimensions={'category': 'deals'},
                ))

        return snapshots

    def _map_metric_type(self, metric_name: str) -> Optional[MetricType]:
        """Map metric names to MetricType enum"""
        mapping = {
            'mrr': MetricType.MRR,
            'arr': MetricType.ARR,
            'total_organizations': MetricType.SUBSCRIBERS,
            'churn_rate': MetricType.CHURN_RATE,
            'pipeline_value': MetricType.DEAL_PIPELINE_VALUE,
            'win_rate': MetricType.DEAL_WIN_RATE,
            'avg_deal_velocity': MetricType.DEAL_VELOCITY,
            'total_deals': MetricType.DEAL_COUNT,
            'avg_deal_size': MetricType.AVG_DEAL_SIZE,
            'podcast_downloads': MetricType.PODCAST_DOWNLOADS,
            'podcast_listeners': MetricType.PODCAST_LISTENERS,
            'blog_views': MetricType.BLOG_VIEWS,
            'content_engagement': MetricType.CONTENT_ENGAGEMENT,
            'social_reach': MetricType.SOCIAL_REACH
        }
        return mapping.get(metric_name)

    async def load_metrics(self, snapshots: List[MetricSnapshot], organization_id: str) -> int:
        """
        Load metric snapshots into the database
        """
        count = 0
        for snapshot in snapshots:
            snapshot.organization_id = organization_id
            self.db.add(snapshot)
            count += 1

        try:
            self.db.commit()
            logger.info(f"Loaded {count} metric snapshots for org {organization_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to load metrics: {str(e)}")
            raise

        return count

    # Aggregation Methods
    async def aggregate_metrics(
        self,
        organization_id: str,
        metric_type: MetricType,
        period: AggregationPeriod,
        start_date: datetime,
        end_date: datetime
    ) -> AggregatedMetric:
        """
        Aggregate metrics for a specific time period
        """
        # Query raw metrics
        snapshots = self.db.query(MetricSnapshot).filter(
            MetricSnapshot.organization_id == organization_id,
            MetricSnapshot.metric_type == metric_type,
            MetricSnapshot.timestamp.between(start_date, end_date)
        ).all()

        if not snapshots:
            return None

        values = [float(s.metric_value) for s in snapshots]

        # Calculate aggregations
        aggregated = AggregatedMetric(
            organization_id=organization_id,
            metric_type=metric_type,
            period=period,
            period_start=start_date,
            period_end=end_date,
            sum_value=Decimal(str(sum(values))),
            avg_value=Decimal(str(np.mean(values))),
            min_value=Decimal(str(min(values))),
            max_value=Decimal(str(max(values))),
            count=len(values),
            std_deviation=Decimal(str(np.std(values))),
            percentile_25=Decimal(str(np.percentile(values, 25))),
            percentile_50=Decimal(str(np.percentile(values, 50))),
            percentile_75=Decimal(str(np.percentile(values, 75))),
            percentile_95=Decimal(str(np.percentile(values, 95)))
        )

        # Calculate period-over-period changes
        prev_start = start_date - (end_date - start_date)
        prev_end = start_date
        prev_snapshots = self.db.query(MetricSnapshot).filter(
            MetricSnapshot.organization_id == organization_id,
            MetricSnapshot.metric_type == metric_type,
            MetricSnapshot.timestamp.between(prev_start, prev_end)
        ).all()

        if prev_snapshots:
            prev_values = [float(s.metric_value) for s in prev_snapshots]
            prev_avg = np.mean(prev_values)
            aggregated.previous_period_value = Decimal(str(prev_avg))
            aggregated.period_change = aggregated.avg_value - Decimal(str(prev_avg))
            if prev_avg > 0:
                aggregated.period_change_percent = Decimal(str(
                    (float(aggregated.avg_value) - prev_avg) / prev_avg * 100
                ))

        # Save to database
        self.db.merge(aggregated)
        self.db.commit()

        return aggregated

    async def run_aggregation_job(
        self,
        organization_id: str,
        period: AggregationPeriod = AggregationPeriod.DAILY
    ):
        """
        Run aggregation job for all metric types
        """
        # Determine time range based on period
        now = datetime.utcnow()
        if period == AggregationPeriod.HOURLY:
            start = now.replace(minute=0, second=0, microsecond=0)
            end = start + timedelta(hours=1)
        elif period == AggregationPeriod.DAILY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == AggregationPeriod.WEEKLY:
            days_since_monday = now.weekday()
            start = (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end = start + timedelta(weeks=1)
        elif period == AggregationPeriod.MONTHLY:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Calculate last day of month
            if now.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)

        # Aggregate each metric type
        for metric_type in MetricType:
            try:
                await self.aggregate_metrics(
                    organization_id, metric_type, period, start, end
                )
            except Exception as e:
                logger.error(f"Failed to aggregate {metric_type}: {str(e)}")

    # Caching Methods
    def get_cache_key(self, organization_id: str, query_params: Dict) -> str:
        """Generate cache key for query results"""
        params_str = json.dumps(query_params, sort_keys=True)
        return f"analytics:{organization_id}:{hashlib.md5(params_str.encode()).hexdigest()}"

    async def get_cached_metrics(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached metrics"""
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {str(e)}")
        return None

    async def cache_metrics(self, cache_key: str, data: Dict, ttl: int = None):
        """Cache metrics data"""
        try:
            self.redis.setex(
                cache_key,
                ttl or self.cache_ttl,
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache storage failed: {str(e)}")

    # Query Methods
    async def query_metrics(
        self,
        organization_id: str,
        metric_types: List[MetricType],
        start_date: datetime,
        end_date: datetime,
        period: AggregationPeriod = AggregationPeriod.DAILY,
        dimensions: Dict = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Query aggregated metrics with optional caching
        """
        # Check cache if enabled
        if use_cache:
            cache_key = self.get_cache_key(organization_id, {
                'metric_types': [m.value for m in metric_types],
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'period': period.value,
                'dimensions': dimensions
            })
            cached = await self.get_cached_metrics(cache_key)
            if cached:
                return pd.DataFrame(cached)

        # Query from database
        query = self.db.query(AggregatedMetric).filter(
            AggregatedMetric.organization_id == organization_id,
            AggregatedMetric.metric_type.in_(metric_types),
            AggregatedMetric.period == period,
            AggregatedMetric.period_start.between(start_date, end_date)
        )

        if dimensions:
            for key, value in dimensions.items():
                query = query.filter(
                    AggregatedMetric.dimensions[key].astext == value
                )

        results = query.all()

        # Convert to DataFrame
        df = pd.DataFrame([{
            'metric_type': r.metric_type.value,
            'period_start': r.period_start,
            'period_end': r.period_end,
            'value': float(r.avg_value),
            'sum': float(r.sum_value),
            'min': float(r.min_value),
            'max': float(r.max_value),
            'count': r.count,
            'change': float(r.period_change) if r.period_change else None,
            'change_percent': float(r.period_change_percent) if r.period_change_percent else None
        } for r in results])

        # Cache results if enabled
        if use_cache and not df.empty:
            await self.cache_metrics(cache_key, df.to_dict('records'))

        return df

    # Alert Processing
    async def check_alerts(self, organization_id: str):
        """
        Check and trigger alerts based on current metrics
        """
        alerts = self.db.query(AlertConfiguration).filter(
            AlertConfiguration.organization_id == organization_id,
            AlertConfiguration.is_active == True
        ).all()

        for alert in alerts:
            try:
                await self._evaluate_alert(alert)
            except Exception as e:
                logger.error(f"Failed to evaluate alert {alert.id}: {str(e)}")

    async def _evaluate_alert(self, alert: AlertConfiguration):
        """Evaluate a single alert condition"""
        # Get recent metric values
        since = datetime.utcnow() - timedelta(seconds=alert.time_window)
        snapshots = self.db.query(MetricSnapshot).filter(
            MetricSnapshot.organization_id == alert.organization_id,
            MetricSnapshot.metric_type == alert.metric_type,
            MetricSnapshot.timestamp >= since
        ).all()

        if not snapshots:
            return

        # Check if condition is met
        current_value = np.mean([float(s.metric_value) for s in snapshots])
        threshold = float(alert.threshold_value)

        condition_met = False
        if alert.operator == ComparisonOperator.GREATER_THAN:
            condition_met = current_value > threshold
        elif alert.operator == ComparisonOperator.LESS_THAN:
            condition_met = current_value < threshold
        elif alert.operator == ComparisonOperator.GREATER_EQUAL:
            condition_met = current_value >= threshold
        elif alert.operator == ComparisonOperator.LESS_EQUAL:
            condition_met = current_value <= threshold
        elif alert.operator == ComparisonOperator.EQUALS:
            condition_met = abs(current_value - threshold) < 0.01
        elif alert.operator == ComparisonOperator.NOT_EQUALS:
            condition_met = abs(current_value - threshold) >= 0.01

        if condition_met:
            await self._trigger_alert(alert, current_value)

    async def _trigger_alert(self, alert: AlertConfiguration, current_value: float):
        """Trigger an alert and send notifications"""
        # Check cooldown
        if alert.last_triggered:
            time_since = (datetime.utcnow() - alert.last_triggered).total_seconds()
            if time_since < alert.cooldown_period:
                return

        # Create alert history record
        history = AlertHistory(
            alert_configuration_id=alert.id,
            organization_id=alert.organization_id,
            triggered_at=datetime.utcnow(),
            severity=alert.severity,
            metric_type=alert.metric_type,
            metric_value=Decimal(str(current_value)),
            threshold_value=alert.threshold_value,
            notification_status='sent'
        )

        self.db.add(history)

        # Update alert configuration
        alert.last_triggered = datetime.utcnow()
        alert.trigger_count += 1
        alert.last_value = Decimal(str(current_value))

        self.db.commit()

        # Send notifications (would integrate with actual notification services)
        logger.info(f"Alert triggered: {alert.name} - Value: {current_value}")

    # Data Quality Methods
    async def validate_data_quality(self, organization_id: str) -> Dict[str, Any]:
        """
        Validate data quality and completeness
        """
        issues = []
        now = datetime.utcnow()

        # Check for missing data
        for metric_type in MetricType:
            last_snapshot = self.db.query(MetricSnapshot).filter(
                MetricSnapshot.organization_id == organization_id,
                MetricSnapshot.metric_type == metric_type
            ).order_by(MetricSnapshot.timestamp.desc()).first()

            if not last_snapshot:
                issues.append({
                    'type': 'missing_data',
                    'metric': metric_type.value,
                    'message': 'No data available'
                })
            elif (now - last_snapshot.timestamp).total_seconds() > 86400:
                issues.append({
                    'type': 'stale_data',
                    'metric': metric_type.value,
                    'last_update': last_snapshot.timestamp,
                    'message': 'Data is more than 24 hours old'
                })

        # Check for anomalies
        for metric_type in [MetricType.MRR, MetricType.DEAL_PIPELINE_VALUE]:
            recent = self.db.query(MetricSnapshot).filter(
                MetricSnapshot.organization_id == organization_id,
                MetricSnapshot.metric_type == metric_type,
                MetricSnapshot.timestamp >= now - timedelta(days=7)
            ).all()

            if recent:
                values = [float(s.metric_value) for s in recent]
                mean = np.mean(values)
                std = np.std(values)

                # Check for outliers (3 standard deviations)
                outliers = [v for v in values if abs(v - mean) > 3 * std]
                if outliers:
                    issues.append({
                        'type': 'anomaly',
                        'metric': metric_type.value,
                        'outliers': outliers,
                        'message': f'Found {len(outliers)} anomalous values'
                    })

        return {
            'is_healthy': len(issues) == 0,
            'issues': issues,
            'last_check': now
        }