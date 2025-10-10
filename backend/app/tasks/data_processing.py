"""
Background Tasks for Data Processing and Analytics
Uses Celery for distributed task processing
"""
from celery import Celery, Task
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta, date
from typing import Dict, List, Any
import os
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.data_warehouse import DataWarehouse
from app.models.analytics import (
    MetricType, AggregationPeriod, AlertConfiguration,
    ReportConfiguration, BusinessGoal
)
from app.models.organization import Organization
import redis

logger = get_task_logger(__name__)

# Initialize Celery
celery_app = Celery(
    'analytics_tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'collect-metrics-hourly': {
        'task': 'app.tasks.data_processing.collect_metrics',
        'schedule': crontab(minute=0),  # Every hour
        'kwargs': {'period': 'hourly'}
    },
    'aggregate-metrics-daily': {
        'task': 'app.tasks.data_processing.aggregate_metrics',
        'schedule': crontab(hour=0, minute=30),  # Daily at 00:30
        'kwargs': {'period': 'daily'}
    },
    'aggregate-metrics-weekly': {
        'task': 'app.tasks.data_processing.aggregate_metrics',
        'schedule': crontab(day_of_week=1, hour=1, minute=0),  # Monday at 01:00
        'kwargs': {'period': 'weekly'}
    },
    'aggregate-metrics-monthly': {
        'task': 'app.tasks.data_processing.aggregate_metrics',
        'schedule': crontab(day_of_month=1, hour=2, minute=0),  # First day of month at 02:00
        'kwargs': {'period': 'monthly'}
    },
    'check-alerts': {
        'task': 'app.tasks.data_processing.check_alerts',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'generate-scheduled-reports': {
        'task': 'app.tasks.data_processing.generate_scheduled_reports',
        'schedule': crontab(minute=0),  # Every hour
    },
    'update-business-goals': {
        'task': 'app.tasks.data_processing.update_business_goals',
        'schedule': crontab(hour=6, minute=0),  # Daily at 06:00
    },
    'cleanup-old-data': {
        'task': 'app.tasks.data_processing.cleanup_old_data',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Sunday at 03:00
    },
}

class DatabaseTask(Task):
    """Base task class with database session management"""
    _db = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None

@celery_app.task(base=DatabaseTask, bind=True, name='app.tasks.data_processing.collect_metrics')
def collect_metrics(self, period: str = 'hourly', organization_id: str = None):
    """
    Collect metrics from various sources
    """
    try:
        db = self.db
        warehouse = DataWarehouse(db)
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

        # Get organizations to process
        if organization_id:
            orgs = db.query(Organization).filter(Organization.id == organization_id).all()
        else:
            orgs = db.query(Organization).filter(Organization.is_active == True).all()

        results = []
        for org in orgs:
            try:
                logger.info(f"Collecting metrics for org {org.id}")

                # Determine date range based on period
                end_date = date.today()
                if period == 'hourly':
                    start_date = end_date
                elif period == 'daily':
                    start_date = end_date - timedelta(days=1)
                elif period == 'weekly':
                    start_date = end_date - timedelta(days=7)
                else:
                    start_date = end_date - timedelta(days=30)

                # Extract metrics
                metrics = celery_app.loop.run_until_complete(
                    warehouse.extract_metrics(str(org.id), start_date, end_date)
                )

                # Transform metrics
                snapshots = celery_app.loop.run_until_complete(
                    warehouse.transform_metrics(metrics)
                )

                # Load metrics
                count = celery_app.loop.run_until_complete(
                    warehouse.load_metrics(snapshots, str(org.id))
                )

                results.append({
                    'organization_id': str(org.id),
                    'metrics_collected': count,
                    'status': 'success'
                })

            except Exception as e:
                logger.error(f"Failed to collect metrics for org {org.id}: {str(e)}")
                results.append({
                    'organization_id': str(org.id),
                    'error': str(e),
                    'status': 'failed'
                })

        return {
            'task': 'collect_metrics',
            'period': period,
            'organizations_processed': len(orgs),
            'results': results
        }

    except Exception as e:
        logger.error(f"Collect metrics task failed: {str(e)}")
        raise

@celery_app.task(base=DatabaseTask, bind=True, name='app.tasks.data_processing.aggregate_metrics')
def aggregate_metrics(self, period: str = 'daily', organization_id: str = None):
    """
    Aggregate metrics for different time periods
    """
    try:
        db = self.db
        warehouse = DataWarehouse(db)

        # Map string period to enum
        period_map = {
            'hourly': AggregationPeriod.HOURLY,
            'daily': AggregationPeriod.DAILY,
            'weekly': AggregationPeriod.WEEKLY,
            'monthly': AggregationPeriod.MONTHLY
        }
        agg_period = period_map.get(period, AggregationPeriod.DAILY)

        # Get organizations to process
        if organization_id:
            orgs = db.query(Organization).filter(Organization.id == organization_id).all()
        else:
            orgs = db.query(Organization).filter(Organization.is_active == True).all()

        results = []
        for org in orgs:
            try:
                logger.info(f"Aggregating metrics for org {org.id}, period {period}")

                # Run aggregation
                celery_app.loop.run_until_complete(
                    warehouse.run_aggregation_job(str(org.id), agg_period)
                )

                results.append({
                    'organization_id': str(org.id),
                    'status': 'success'
                })

            except Exception as e:
                logger.error(f"Failed to aggregate metrics for org {org.id}: {str(e)}")
                results.append({
                    'organization_id': str(org.id),
                    'error': str(e),
                    'status': 'failed'
                })

        return {
            'task': 'aggregate_metrics',
            'period': period,
            'organizations_processed': len(orgs),
            'results': results
        }

    except Exception as e:
        logger.error(f"Aggregate metrics task failed: {str(e)}")
        raise

@celery_app.task(base=DatabaseTask, bind=True, name='app.tasks.data_processing.check_alerts')
def check_alerts(self, organization_id: str = None):
    """
    Check alert conditions and trigger notifications
    """
    try:
        db = self.db
        warehouse = DataWarehouse(db)

        # Get organizations to check
        if organization_id:
            orgs = db.query(Organization).filter(Organization.id == organization_id).all()
        else:
            orgs = db.query(Organization).filter(Organization.is_active == True).all()

        alerts_triggered = 0
        for org in orgs:
            try:
                celery_app.loop.run_until_complete(
                    warehouse.check_alerts(str(org.id))
                )

                # Count triggered alerts
                recent_alerts = db.query(AlertHistory).filter(
                    AlertHistory.organization_id == org.id,
                    AlertHistory.triggered_at >= datetime.utcnow() - timedelta(minutes=5)
                ).count()

                alerts_triggered += recent_alerts

            except Exception as e:
                logger.error(f"Failed to check alerts for org {org.id}: {str(e)}")

        return {
            'task': 'check_alerts',
            'organizations_checked': len(orgs),
            'alerts_triggered': alerts_triggered
        }

    except Exception as e:
        logger.error(f"Check alerts task failed: {str(e)}")
        raise

@celery_app.task(base=DatabaseTask, bind=True, name='app.tasks.data_processing.generate_scheduled_reports')
def generate_scheduled_reports(self):
    """
    Generate and send scheduled reports
    """
    try:
        db = self.db
        now = datetime.utcnow()

        # Find reports due for generation
        reports = db.query(ReportConfiguration).filter(
            ReportConfiguration.is_scheduled == True,
            ReportConfiguration.next_run <= now
        ).all()

        results = []
        for report in reports:
            try:
                logger.info(f"Generating report {report.id}: {report.name}")

                # Generate report (simplified - would integrate with reporting service)
                report_data = generate_report.delay(str(report.id))

                # Update next run time based on schedule
                from croniter import croniter
                cron = croniter(report.schedule_cron, now)
                report.next_run = cron.get_next(datetime)
                report.last_generated = now

                db.commit()

                results.append({
                    'report_id': str(report.id),
                    'name': report.name,
                    'status': 'generated'
                })

            except Exception as e:
                logger.error(f"Failed to generate report {report.id}: {str(e)}")
                results.append({
                    'report_id': str(report.id),
                    'error': str(e),
                    'status': 'failed'
                })

        return {
            'task': 'generate_scheduled_reports',
            'reports_processed': len(reports),
            'results': results
        }

    except Exception as e:
        logger.error(f"Generate scheduled reports task failed: {str(e)}")
        raise

@celery_app.task(base=DatabaseTask, bind=True, name='app.tasks.data_processing.generate_report')
def generate_report(self, report_id: str):
    """
    Generate a specific report
    """
    try:
        db = self.db
        warehouse = DataWarehouse(db)

        report = db.query(ReportConfiguration).filter(
            ReportConfiguration.id == report_id
        ).first()

        if not report:
            raise ValueError(f"Report {report_id} not found")

        logger.info(f"Generating report: {report.name}")

        # Extract metrics based on report configuration
        metric_types = [MetricType(m) for m in report.metrics]

        # Parse time range
        time_range = report.time_range or {'type': 'relative', 'value': 'last_30_days'}
        if time_range['type'] == 'relative':
            if time_range['value'] == 'last_7_days':
                start_date = datetime.utcnow() - timedelta(days=7)
            elif time_range['value'] == 'last_30_days':
                start_date = datetime.utcnow() - timedelta(days=30)
            elif time_range['value'] == 'last_90_days':
                start_date = datetime.utcnow() - timedelta(days=90)
            else:
                start_date = datetime.utcnow() - timedelta(days=30)
            end_date = datetime.utcnow()
        else:
            start_date = datetime.fromisoformat(time_range['start'])
            end_date = datetime.fromisoformat(time_range['end'])

        # Query metrics
        df = celery_app.loop.run_until_complete(
            warehouse.query_metrics(
                str(report.organization_id),
                metric_types,
                start_date,
                end_date,
                dimensions=report.filters
            )
        )

        # Generate report output (simplified)
        report_content = {
            'report_id': str(report.id),
            'name': report.name,
            'generated_at': datetime.utcnow().isoformat(),
            'data': df.to_dict('records') if not df.empty else [],
            'summary': {
                'total_metrics': len(df),
                'date_range': f"{start_date.date()} to {end_date.date()}"
            }
        }

        # Send to recipients (would integrate with email service)
        if report.recipients:
            logger.info(f"Sending report to {len(report.recipients)} recipients")

        return report_content

    except Exception as e:
        logger.error(f"Generate report task failed: {str(e)}")
        raise

@celery_app.task(base=DatabaseTask, bind=True, name='app.tasks.data_processing.update_business_goals')
def update_business_goals(self):
    """
    Update progress on business goals
    """
    try:
        db = self.db
        warehouse = DataWarehouse(db)

        goals = db.query(BusinessGoal).filter(
            BusinessGoal.status == 'active'
        ).all()

        results = []
        for goal in goals:
            try:
                # Get current metric value
                snapshots = db.query(MetricSnapshot).filter(
                    MetricSnapshot.organization_id == goal.organization_id,
                    MetricSnapshot.metric_type == goal.metric_type,
                    MetricSnapshot.date == date.today()
                ).all()

                if snapshots:
                    current_value = sum(float(s.metric_value) for s in snapshots) / len(snapshots)
                    goal.current_value = current_value

                    # Calculate progress
                    if goal.baseline_value and goal.target_value:
                        total_change = float(goal.target_value) - float(goal.baseline_value)
                        current_change = current_value - float(goal.baseline_value)
                        if total_change != 0:
                            goal.progress_percent = (current_change / total_change) * 100

                    # Check if on track
                    days_total = (goal.target_date - goal.start_date).days
                    days_elapsed = (date.today() - goal.start_date).days
                    expected_progress = (days_elapsed / days_total) * 100 if days_total > 0 else 0
                    goal.is_on_track = goal.progress_percent >= expected_progress * 0.9

                    # Update status if completed
                    if goal.progress_percent >= 100:
                        goal.status = 'completed'
                        goal.completed_at = datetime.utcnow()

                    db.commit()

                    results.append({
                        'goal_id': str(goal.id),
                        'name': goal.name,
                        'progress': float(goal.progress_percent),
                        'status': goal.status
                    })

            except Exception as e:
                logger.error(f"Failed to update goal {goal.id}: {str(e)}")

        return {
            'task': 'update_business_goals',
            'goals_processed': len(goals),
            'results': results
        }

    except Exception as e:
        logger.error(f"Update business goals task failed: {str(e)}")
        raise

@celery_app.task(base=DatabaseTask, bind=True, name='app.tasks.data_processing.cleanup_old_data')
def cleanup_old_data(self, retention_days: int = 90):
    """
    Clean up old metric snapshots and alert history
    """
    try:
        db = self.db
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # Delete old metric snapshots
        deleted_snapshots = db.query(MetricSnapshot).filter(
            MetricSnapshot.timestamp < cutoff_date
        ).delete()

        # Delete old alert history
        deleted_alerts = db.query(AlertHistory).filter(
            AlertHistory.triggered_at < cutoff_date
        ).delete()

        db.commit()

        logger.info(f"Cleaned up {deleted_snapshots} snapshots and {deleted_alerts} alert records")

        return {
            'task': 'cleanup_old_data',
            'deleted_snapshots': deleted_snapshots,
            'deleted_alerts': deleted_alerts,
            'cutoff_date': cutoff_date.isoformat()
        }

    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        raise

@celery_app.task(bind=True, name='app.tasks.data_processing.calculate_predictive_metrics')
def calculate_predictive_metrics(self, organization_id: str):
    """
    Calculate predictive metrics using ML models
    """
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler
        import numpy as np
        import pandas as pd

        db = SessionLocal()
        warehouse = DataWarehouse(db)

        # Get historical data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=180)  # 6 months of data

        df = celery_app.loop.run_until_complete(
            warehouse.query_metrics(
                organization_id,
                [MetricType.MRR, MetricType.SUBSCRIBERS, MetricType.CHURN_RATE],
                start_date,
                end_date,
                AggregationPeriod.DAILY
            )
        )

        if df.empty:
            return {'error': 'Insufficient data for predictions'}

        # Prepare data for prediction
        df['days_from_start'] = (df['period_start'] - df['period_start'].min()).dt.days

        predictions = {}

        # Predict MRR growth
        mrr_data = df[df['metric_type'] == 'mrr'].copy()
        if len(mrr_data) > 30:
            X = mrr_data[['days_from_start']].values
            y = mrr_data['value'].values

            model = LinearRegression()
            model.fit(X, y)

            # Predict next 30 days
            future_days = np.array([[i] for i in range(len(X), len(X) + 30)])
            mrr_predictions = model.predict(future_days)

            predictions['mrr_30_days'] = float(mrr_predictions[-1])
            predictions['mrr_growth_rate'] = float(
                (mrr_predictions[-1] - y[-1]) / y[-1] * 100
            )

        # Predict churn
        churn_data = df[df['metric_type'] == 'churn_rate'].copy()
        if len(churn_data) > 30:
            recent_churn = churn_data['value'].tail(30).mean()
            predictions['predicted_churn'] = float(recent_churn)
            predictions['churn_trend'] = 'increasing' if churn_data['value'].tail(7).mean() > churn_data['value'].tail(30).mean() else 'decreasing'

        db.close()

        return {
            'task': 'calculate_predictive_metrics',
            'organization_id': organization_id,
            'predictions': predictions
        }

    except Exception as e:
        logger.error(f"Predictive metrics calculation failed: {str(e)}")
        raise

# Export task functions for external use
__all__ = [
    'collect_metrics',
    'aggregate_metrics',
    'check_alerts',
    'generate_scheduled_reports',
    'generate_report',
    'update_business_goals',
    'cleanup_old_data',
    'calculate_predictive_metrics'
]