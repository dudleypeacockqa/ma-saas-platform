"""
Advanced Performance Analytics & Optimization Engine - Sprint 17
Real-time integration performance monitoring and optimization recommendations
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from collections import defaultdict
import json
import statistics

class PerformanceMetric(Enum):
    INTEGRATION_VELOCITY = "integration_velocity"
    MILESTONE_COMPLETION_RATE = "milestone_completion_rate"
    SYNERGY_REALIZATION_RATE = "synergy_realization_rate"
    EMPLOYEE_RETENTION = "employee_retention"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    FINANCIAL_PERFORMANCE = "financial_performance"
    CULTURAL_HARMONY = "cultural_harmony"
    CHANGE_ADOPTION_RATE = "change_adoption_rate"
    COMMUNICATION_EFFECTIVENESS = "communication_effectiveness"

class OptimizationCategory(Enum):
    PROCESS_IMPROVEMENT = "process_improvement"
    RESOURCE_ALLOCATION = "resource_allocation"
    TIMELINE_OPTIMIZATION = "timeline_optimization"
    RISK_MITIGATION = "risk_mitigation"
    COMMUNICATION_ENHANCEMENT = "communication_enhancement"
    TECHNOLOGY_OPTIMIZATION = "technology_optimization"
    CULTURE_ACCELERATION = "culture_acceleration"
    SYNERGY_ACCELERATION = "synergy_acceleration"

class BenchmarkType(Enum):
    INDUSTRY_AVERAGE = "industry_average"
    BEST_IN_CLASS = "best_in_class"
    HISTORICAL_PERFORMANCE = "historical_performance"
    PEER_COMPARISON = "peer_comparison"
    THEORETICAL_OPTIMAL = "theoretical_optimal"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PerformanceDataPoint:
    metric: PerformanceMetric
    value: float
    timestamp: datetime
    integration_id: str
    organization_id: Optional[str] = None
    department: Optional[str] = None
    confidence: float = 1.0
    data_source: str = "system"

@dataclass
class BenchmarkData:
    metric: PerformanceMetric
    benchmark_type: BenchmarkType
    value: float
    industry: str
    deal_size_category: str
    geography: str
    confidence_interval: Tuple[float, float]
    sample_size: int
    last_updated: datetime

@dataclass
class OptimizationRecommendation:
    recommendation_id: str
    category: OptimizationCategory
    title: str
    description: str
    expected_impact: float
    implementation_effort: str
    timeline_weeks: int
    resource_requirements: Dict[str, Any]
    risk_level: str
    confidence_score: float
    supporting_metrics: List[PerformanceMetric]
    implementation_steps: List[str]

@dataclass
class PerformanceAlert:
    alert_id: str
    integration_id: str
    severity: AlertSeverity
    metric: PerformanceMetric
    current_value: float
    expected_value: float
    variance_percentage: float
    trend_direction: str
    message: str
    recommended_actions: List[str]
    timestamp: datetime

class PerformanceTracker:
    def __init__(self):
        self.performance_data = defaultdict(list)
        self.alert_thresholds = {
            PerformanceMetric.INTEGRATION_VELOCITY: {'low': 0.7, 'critical': 0.5},
            PerformanceMetric.MILESTONE_COMPLETION_RATE: {'low': 0.8, 'critical': 0.6},
            PerformanceMetric.SYNERGY_REALIZATION_RATE: {'low': 0.75, 'critical': 0.5},
            PerformanceMetric.EMPLOYEE_RETENTION: {'low': 0.9, 'critical': 0.8},
            PerformanceMetric.CUSTOMER_SATISFACTION: {'low': 0.8, 'critical': 0.7}
        }

    async def track_performance_metrics(self, integration_id: str,
                                      metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track and analyze performance metrics for integration"""

        performance_points = []
        current_timestamp = datetime.utcnow()

        # Process integration velocity metrics
        if 'integration_velocity' in metrics_data:
            velocity_data = metrics_data['integration_velocity']
            velocity_score = await self._calculate_integration_velocity(velocity_data)
            performance_points.append(PerformanceDataPoint(
                metric=PerformanceMetric.INTEGRATION_VELOCITY,
                value=velocity_score,
                timestamp=current_timestamp,
                integration_id=integration_id,
                data_source='integration_tracker'
            ))

        # Process milestone completion metrics
        if 'milestone_data' in metrics_data:
            milestone_data = metrics_data['milestone_data']
            completion_rate = await self._calculate_milestone_completion_rate(milestone_data)
            performance_points.append(PerformanceDataPoint(
                metric=PerformanceMetric.MILESTONE_COMPLETION_RATE,
                value=completion_rate,
                timestamp=current_timestamp,
                integration_id=integration_id,
                data_source='milestone_tracker'
            ))

        # Process synergy realization metrics
        if 'synergy_data' in metrics_data:
            synergy_data = metrics_data['synergy_data']
            realization_rate = await self._calculate_synergy_realization_rate(synergy_data)
            performance_points.append(PerformanceDataPoint(
                metric=PerformanceMetric.SYNERGY_REALIZATION_RATE,
                value=realization_rate,
                timestamp=current_timestamp,
                integration_id=integration_id,
                data_source='synergy_tracker'
            ))

        # Process employee retention metrics
        if 'hr_data' in metrics_data:
            hr_data = metrics_data['hr_data']
            retention_rate = await self._calculate_employee_retention(hr_data)
            performance_points.append(PerformanceDataPoint(
                metric=PerformanceMetric.EMPLOYEE_RETENTION,
                value=retention_rate,
                timestamp=current_timestamp,
                integration_id=integration_id,
                data_source='hr_system'
            ))

        # Process customer satisfaction metrics
        if 'customer_data' in metrics_data:
            customer_data = metrics_data['customer_data']
            satisfaction_score = await self._calculate_customer_satisfaction(customer_data)
            performance_points.append(PerformanceDataPoint(
                metric=PerformanceMetric.CUSTOMER_SATISFACTION,
                value=satisfaction_score,
                timestamp=current_timestamp,
                integration_id=integration_id,
                data_source='customer_feedback'
            ))

        # Process operational efficiency metrics
        if 'operational_data' in metrics_data:
            operational_data = metrics_data['operational_data']
            efficiency_score = await self._calculate_operational_efficiency(operational_data)
            performance_points.append(PerformanceDataPoint(
                metric=PerformanceMetric.OPERATIONAL_EFFICIENCY,
                value=efficiency_score,
                timestamp=current_timestamp,
                integration_id=integration_id,
                data_source='operational_systems'
            ))

        # Store performance data
        for point in performance_points:
            self.performance_data[integration_id].append(point)

        # Generate performance analysis
        analysis = await self._analyze_performance_trends(integration_id, performance_points)

        # Generate alerts for concerning metrics
        alerts = await self._generate_performance_alerts(integration_id, performance_points)

        return {
            'integration_id': integration_id,
            'performance_points': [point.__dict__ for point in performance_points],
            'trend_analysis': analysis,
            'alerts': [alert.__dict__ for alert in alerts],
            'tracking_timestamp': current_timestamp,
            'metrics_count': len(performance_points)
        }

    async def _calculate_integration_velocity(self, velocity_data: Dict[str, Any]) -> float:
        """Calculate integration velocity score based on progress rate"""

        planned_milestones = velocity_data.get('planned_milestones', 1)
        completed_milestones = velocity_data.get('completed_milestones', 0)
        elapsed_weeks = velocity_data.get('elapsed_weeks', 1)
        planned_weeks = velocity_data.get('planned_weeks', 52)

        # Calculate completion rate vs planned timeline
        planned_completion_rate = elapsed_weeks / planned_weeks
        actual_completion_rate = completed_milestones / planned_milestones if planned_milestones > 0 else 0

        # Velocity is actual vs planned progress
        velocity_ratio = actual_completion_rate / planned_completion_rate if planned_completion_rate > 0 else 0

        # Cap at 1.0 for perfect/ahead of schedule performance
        return min(1.0, velocity_ratio)

    async def _calculate_milestone_completion_rate(self, milestone_data: Dict[str, Any]) -> float:
        """Calculate milestone completion rate"""

        total_milestones = milestone_data.get('total_milestones', 1)
        completed_milestones = milestone_data.get('completed_milestones', 0)
        on_time_completion = milestone_data.get('on_time_completions', 0)

        # Base completion rate
        completion_rate = completed_milestones / total_milestones if total_milestones > 0 else 0

        # Quality factor for on-time completion
        on_time_factor = on_time_completion / completed_milestones if completed_milestones > 0 else 1

        # Combined score
        return completion_rate * (0.7 + 0.3 * on_time_factor)

    async def _calculate_synergy_realization_rate(self, synergy_data: Dict[str, Any]) -> float:
        """Calculate synergy realization rate"""

        planned_value = synergy_data.get('planned_synergy_value', 1)
        realized_value = synergy_data.get('realized_synergy_value', 0)
        time_factor = synergy_data.get('realization_time_factor', 1.0)

        # Base realization rate
        realization_rate = realized_value / planned_value if planned_value > 0 else 0

        # Adjust for timing (faster realization is better)
        time_adjusted_rate = realization_rate * time_factor

        return min(1.0, time_adjusted_rate)

    async def _calculate_employee_retention(self, hr_data: Dict[str, Any]) -> float:
        """Calculate employee retention rate during integration"""

        total_employees_start = hr_data.get('employees_at_start', 1)
        employees_remaining = hr_data.get('employees_current', 1)
        voluntary_departures = hr_data.get('voluntary_departures', 0)
        key_talent_retention = hr_data.get('key_talent_retained', 1)
        total_key_talent = hr_data.get('total_key_talent', 1)

        # Overall retention rate
        overall_retention = employees_remaining / total_employees_start if total_employees_start > 0 else 1

        # Key talent retention rate
        key_talent_rate = key_talent_retention / total_key_talent if total_key_talent > 0 else 1

        # Weighted combination (key talent more important)
        return overall_retention * 0.6 + key_talent_rate * 0.4

    async def _calculate_customer_satisfaction(self, customer_data: Dict[str, Any]) -> float:
        """Calculate customer satisfaction during integration"""

        satisfaction_scores = customer_data.get('satisfaction_scores', [])
        retention_rate = customer_data.get('customer_retention_rate', 1.0)
        complaint_volume = customer_data.get('complaint_volume_change', 0)

        # Average satisfaction score
        avg_satisfaction = statistics.mean(satisfaction_scores) / 10 if satisfaction_scores else 0.5

        # Adjust for retention and complaints
        retention_factor = min(1.0, retention_rate)
        complaint_factor = max(0.5, 1.0 - abs(complaint_volume) / 100)

        return avg_satisfaction * 0.5 + retention_factor * 0.3 + complaint_factor * 0.2

    async def _calculate_operational_efficiency(self, operational_data: Dict[str, Any]) -> float:
        """Calculate operational efficiency metrics"""

        cost_efficiency = operational_data.get('cost_efficiency_improvement', 0)
        process_efficiency = operational_data.get('process_efficiency_score', 0.5)
        system_uptime = operational_data.get('system_uptime_percentage', 0.99)
        automation_level = operational_data.get('automation_adoption_rate', 0.5)

        # Normalize cost efficiency (percentage improvement to 0-1 scale)
        cost_factor = min(1.0, max(0.0, (cost_efficiency + 10) / 20))  # -10% to +10% range

        return (cost_factor * 0.3 + process_efficiency * 0.3 +
                system_uptime * 0.2 + automation_level * 0.2)

    async def _analyze_performance_trends(self, integration_id: str,
                                        current_points: List[PerformanceDataPoint]) -> Dict[str, Any]:
        """Analyze performance trends and patterns"""

        historical_data = self.performance_data.get(integration_id, [])
        all_data = historical_data + current_points

        trends = {}

        # Analyze trends for each metric
        for metric in PerformanceMetric:
            metric_data = [point for point in all_data if point.metric == metric]
            if len(metric_data) >= 2:
                trends[metric.value] = await self._calculate_metric_trend(metric_data)

        # Calculate overall performance score
        current_scores = [point.value for point in current_points]
        overall_score = statistics.mean(current_scores) if current_scores else 0.5

        # Identify concerning trends
        concerning_trends = [
            metric for metric, trend_data in trends.items()
            if trend_data.get('direction') == 'declining' and trend_data.get('significance') > 0.05
        ]

        return {
            'overall_performance_score': overall_score,
            'metric_trends': trends,
            'concerning_trends': concerning_trends,
            'trend_confidence': self._calculate_trend_confidence(all_data),
            'data_points_analyzed': len(all_data),
            'analysis_timestamp': datetime.utcnow()
        }

    async def _calculate_metric_trend(self, metric_data: List[PerformanceDataPoint]) -> Dict[str, Any]:
        """Calculate trend for a specific metric"""

        if len(metric_data) < 2:
            return {'direction': 'unknown', 'significance': 0, 'rate': 0}

        # Sort by timestamp
        sorted_data = sorted(metric_data, key=lambda x: x.timestamp)
        values = [point.value for point in sorted_data]

        # Calculate linear trend
        n = len(values)
        x_values = list(range(n))

        # Simple linear regression
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        slope = numerator / denominator if denominator != 0 else 0

        # Determine trend direction
        if slope > 0.01:
            direction = 'improving'
        elif slope < -0.01:
            direction = 'declining'
        else:
            direction = 'stable'

        # Calculate significance (simplified R-squared approximation)
        y_pred = [y_mean + slope * (x - x_mean) for x in x_values]
        ss_res = sum((y - y_pred) ** 2 for y, y_pred in zip(values, y_pred))
        ss_tot = sum((y - y_mean) ** 2 for y in values)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        return {
            'direction': direction,
            'rate': slope,
            'significance': r_squared,
            'recent_value': values[-1],
            'change_from_start': values[-1] - values[0] if len(values) > 1 else 0
        }

    async def _generate_performance_alerts(self, integration_id: str,
                                         performance_points: List[PerformanceDataPoint]) -> List[PerformanceAlert]:
        """Generate alerts for performance issues"""

        alerts = []
        current_timestamp = datetime.utcnow()

        for point in performance_points:
            thresholds = self.alert_thresholds.get(point.metric)
            if not thresholds:
                continue

            alert_severity = None
            if point.value <= thresholds.get('critical', 0):
                alert_severity = AlertSeverity.CRITICAL
            elif point.value <= thresholds.get('low', 0):
                alert_severity = AlertSeverity.HIGH

            if alert_severity:
                # Get expected value (could be from benchmarks or targets)
                expected_value = await self._get_expected_value(point.metric)
                variance = ((point.value - expected_value) / expected_value * 100) if expected_value > 0 else 0

                alert = PerformanceAlert(
                    alert_id=f"{integration_id}_{point.metric.value}_{int(current_timestamp.timestamp())}",
                    integration_id=integration_id,
                    severity=alert_severity,
                    metric=point.metric,
                    current_value=point.value,
                    expected_value=expected_value,
                    variance_percentage=variance,
                    trend_direction=await self._get_recent_trend_direction(integration_id, point.metric),
                    message=await self._generate_alert_message(point.metric, point.value, expected_value),
                    recommended_actions=await self._get_recommended_actions(point.metric, alert_severity),
                    timestamp=current_timestamp
                )
                alerts.append(alert)

        return alerts

class BenchmarkingEngine:
    def __init__(self):
        self.benchmark_database = {}
        self.peer_networks = {}
        self.industry_standards = {}

    async def get_performance_benchmarks(self, integration_context: Dict[str, Any]) -> Dict[str, BenchmarkData]:
        """Get relevant performance benchmarks for integration context"""

        industry = integration_context.get('industry', 'general')
        deal_size = integration_context.get('deal_size_category', 'medium')
        geography = integration_context.get('geography', 'global')

        benchmarks = {}

        # Get industry benchmarks for each metric
        for metric in PerformanceMetric:
            # Industry average benchmark
            industry_benchmark = await self._get_industry_benchmark(
                metric, industry, deal_size, geography
            )
            if industry_benchmark:
                benchmarks[f"{metric.value}_industry"] = industry_benchmark

            # Best-in-class benchmark
            best_in_class = await self._get_best_in_class_benchmark(
                metric, industry, deal_size, geography
            )
            if best_in_class:
                benchmarks[f"{metric.value}_best_in_class"] = best_in_class

            # Peer comparison benchmark
            peer_benchmark = await self._get_peer_benchmark(
                metric, integration_context
            )
            if peer_benchmark:
                benchmarks[f"{metric.value}_peer"] = peer_benchmark

        return benchmarks

    async def _get_industry_benchmark(self, metric: PerformanceMetric, industry: str,
                                    deal_size: str, geography: str) -> Optional[BenchmarkData]:
        """Get industry average benchmark for metric"""

        # Simulated benchmark data - in real implementation would query benchmark database
        benchmark_values = {
            'tech': {
                PerformanceMetric.INTEGRATION_VELOCITY: 0.85,
                PerformanceMetric.MILESTONE_COMPLETION_RATE: 0.78,
                PerformanceMetric.SYNERGY_REALIZATION_RATE: 0.72,
                PerformanceMetric.EMPLOYEE_RETENTION: 0.88,
                PerformanceMetric.CUSTOMER_SATISFACTION: 0.82
            },
            'finance': {
                PerformanceMetric.INTEGRATION_VELOCITY: 0.75,
                PerformanceMetric.MILESTONE_COMPLETION_RATE: 0.85,
                PerformanceMetric.SYNERGY_REALIZATION_RATE: 0.80,
                PerformanceMetric.EMPLOYEE_RETENTION: 0.85,
                PerformanceMetric.CUSTOMER_SATISFACTION: 0.88
            },
            'general': {metric: 0.75 for metric in PerformanceMetric}
        }

        industry_benchmarks = benchmark_values.get(industry, benchmark_values['general'])
        value = industry_benchmarks.get(metric)

        if value is None:
            return None

        # Adjust for deal size (larger deals typically have more challenges)
        size_adjustments = {'small': 1.05, 'medium': 1.0, 'large': 0.95}
        adjusted_value = value * size_adjustments.get(deal_size, 1.0)

        return BenchmarkData(
            metric=metric,
            benchmark_type=BenchmarkType.INDUSTRY_AVERAGE,
            value=adjusted_value,
            industry=industry,
            deal_size_category=deal_size,
            geography=geography,
            confidence_interval=(adjusted_value * 0.9, adjusted_value * 1.1),
            sample_size=100,  # Simulated
            last_updated=datetime.utcnow()
        )

    async def compare_to_benchmarks(self, integration_id: str,
                                  performance_data: List[PerformanceDataPoint],
                                  benchmarks: Dict[str, BenchmarkData]) -> Dict[str, Any]:
        """Compare performance data to benchmarks"""

        comparisons = {}

        for point in performance_data:
            metric_comparisons = {}

            # Compare to industry average
            industry_key = f"{point.metric.value}_industry"
            if industry_key in benchmarks:
                industry_benchmark = benchmarks[industry_key]
                variance = ((point.value - industry_benchmark.value) / industry_benchmark.value * 100)
                metric_comparisons['industry_average'] = {
                    'benchmark_value': industry_benchmark.value,
                    'current_value': point.value,
                    'variance_percentage': variance,
                    'performance_rating': await self._get_performance_rating(variance)
                }

            # Compare to best-in-class
            best_in_class_key = f"{point.metric.value}_best_in_class"
            if best_in_class_key in benchmarks:
                best_benchmark = benchmarks[best_in_class_key]
                variance = ((point.value - best_benchmark.value) / best_benchmark.value * 100)
                metric_comparisons['best_in_class'] = {
                    'benchmark_value': best_benchmark.value,
                    'current_value': point.value,
                    'variance_percentage': variance,
                    'performance_rating': await self._get_performance_rating(variance)
                }

            comparisons[point.metric.value] = metric_comparisons

        # Overall benchmark performance
        overall_rating = await self._calculate_overall_benchmark_performance(comparisons)

        return {
            'integration_id': integration_id,
            'metric_comparisons': comparisons,
            'overall_performance_rating': overall_rating,
            'comparison_timestamp': datetime.utcnow()
        }

    async def _get_performance_rating(self, variance_percentage: float) -> str:
        """Get performance rating based on variance from benchmark"""

        if variance_percentage >= 10:
            return 'excellent'
        elif variance_percentage >= 0:
            return 'above_average'
        elif variance_percentage >= -10:
            return 'average'
        elif variance_percentage >= -20:
            return 'below_average'
        else:
            return 'poor'

class IntegrationAnalytics:
    def __init__(self):
        self.analytics_models = {}
        self.prediction_engines = {}
        self.correlation_analyzers = {}

    async def generate_integration_dashboard(self, integration_id: str,
                                           performance_data: List[PerformanceDataPoint],
                                           benchmarks: Dict[str, BenchmarkData]) -> Dict[str, Any]:
        """Generate comprehensive integration performance dashboard"""

        # Current performance summary
        current_summary = await self._generate_current_performance_summary(performance_data)

        # Trend analysis
        trend_analysis = await self._generate_trend_analysis(integration_id, performance_data)

        # Benchmark comparison
        benchmark_comparison = await self._generate_benchmark_comparison(performance_data, benchmarks)

        # Risk assessment
        risk_assessment = await self._generate_risk_assessment(integration_id, performance_data)

        # Predictive insights
        predictions = await self._generate_performance_predictions(integration_id, performance_data)

        # Success probability
        success_probability = await self._calculate_integration_success_probability(performance_data)

        return {
            'integration_id': integration_id,
            'dashboard_data': {
                'current_performance': current_summary,
                'trends': trend_analysis,
                'benchmark_comparison': benchmark_comparison,
                'risk_assessment': risk_assessment,
                'predictions': predictions,
                'success_probability': success_probability,
                'last_updated': datetime.utcnow()
            },
            'data_freshness': await self._calculate_data_freshness(performance_data),
            'dashboard_confidence': await self._calculate_dashboard_confidence(performance_data)
        }

class PerformanceOptimizer:
    def __init__(self):
        self.performance_tracker = PerformanceTracker()
        self.benchmarking_engine = BenchmarkingEngine()
        self.analytics_engine = IntegrationAnalytics()
        self.optimization_algorithms = {}
        self.active_optimizations = {}

    async def initiate_performance_optimization(self, integration_id: str,
                                              optimization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate comprehensive performance optimization analysis"""

        # Track current performance metrics
        performance_tracking = await self.performance_tracker.track_performance_metrics(
            integration_id, optimization_data.get('metrics_data', {})
        )

        # Get relevant benchmarks
        integration_context = optimization_data.get('integration_context', {})
        benchmarks = await self.benchmarking_engine.get_performance_benchmarks(integration_context)

        # Compare to benchmarks
        benchmark_comparison = await self.benchmarking_engine.compare_to_benchmarks(
            integration_id,
            [PerformanceDataPoint(**point) for point in performance_tracking['performance_points']],
            benchmarks
        )

        # Generate analytics dashboard
        dashboard = await self.analytics_engine.generate_integration_dashboard(
            integration_id,
            [PerformanceDataPoint(**point) for point in performance_tracking['performance_points']],
            benchmarks
        )

        # Generate optimization recommendations
        recommendations = await self._generate_optimization_recommendations(
            integration_id, performance_tracking, benchmark_comparison, dashboard
        )

        # Create optimization plan
        optimization_plan = await self._create_optimization_plan(integration_id, recommendations)

        # Store optimization state
        optimization_state = {
            'integration_id': integration_id,
            'performance_tracking': performance_tracking,
            'benchmark_comparison': benchmark_comparison,
            'dashboard': dashboard,
            'recommendations': recommendations,
            'optimization_plan': optimization_plan,
            'status': 'initiated',
            'created_date': datetime.utcnow()
        }

        self.active_optimizations[integration_id] = optimization_state

        return {
            'integration_id': integration_id,
            'optimization_status': 'initiated',
            'performance_summary': {
                'overall_score': dashboard['dashboard_data']['current_performance'].get('overall_score'),
                'alerts_count': len(performance_tracking.get('alerts', [])),
                'metrics_tracked': performance_tracking.get('metrics_count', 0)
            },
            'benchmark_performance': {
                'industry_rating': benchmark_comparison.get('overall_performance_rating'),
                'improvement_areas': len([
                    comp for comp in benchmark_comparison.get('metric_comparisons', {}).values()
                    if any(rating.get('performance_rating') in ['below_average', 'poor']
                          for rating in comp.values())
                ])
            },
            'optimization_overview': {
                'recommendations_count': len(recommendations),
                'high_impact_recommendations': len([
                    rec for rec in recommendations
                    if rec.get('expected_impact', 0) > 0.7
                ]),
                'implementation_timeline_weeks': optimization_plan.get('total_timeline_weeks')
            },
            'next_steps': await self._generate_optimization_next_steps(optimization_state),
            'created_date': datetime.utcnow()
        }

    async def _generate_optimization_recommendations(self, integration_id: str,
                                                   performance_tracking: Dict[str, Any],
                                                   benchmark_comparison: Dict[str, Any],
                                                   dashboard: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate specific optimization recommendations"""

        recommendations = []
        rec_id_counter = 1

        # Analyze alerts for immediate action items
        alerts = performance_tracking.get('alerts', [])
        for alert in alerts:
            if alert['severity'] in ['high', 'critical']:
                rec = await self._create_alert_based_recommendation(
                    f"{integration_id}_alert_{rec_id_counter}", alert
                )
                recommendations.append(rec)
                rec_id_counter += 1

        # Analyze benchmark gaps
        metric_comparisons = benchmark_comparison.get('metric_comparisons', {})
        for metric, comparisons in metric_comparisons.items():
            for benchmark_type, comparison in comparisons.items():
                if comparison.get('performance_rating') in ['below_average', 'poor']:
                    rec = await self._create_benchmark_improvement_recommendation(
                        f"{integration_id}_benchmark_{rec_id_counter}", metric, comparison
                    )
                    recommendations.append(rec)
                    rec_id_counter += 1

        # Analyze trends for proactive recommendations
        trends = dashboard['dashboard_data'].get('trends', {})
        for metric, trend_data in trends.items():
            if trend_data.get('direction') == 'declining':
                rec = await self._create_trend_improvement_recommendation(
                    f"{integration_id}_trend_{rec_id_counter}", metric, trend_data
                )
                recommendations.append(rec)
                rec_id_counter += 1

        # Generate strategic optimization recommendations
        strategic_recs = await self._generate_strategic_recommendations(
            integration_id, dashboard, rec_id_counter
        )
        recommendations.extend(strategic_recs)

        # Sort by expected impact and implementation feasibility
        recommendations.sort(key=lambda x: (x.expected_impact, -x.timeline_weeks), reverse=True)

        return recommendations

    async def _create_alert_based_recommendation(self, rec_id: str,
                                               alert: Dict[str, Any]) -> OptimizationRecommendation:
        """Create recommendation based on performance alert"""

        metric = alert['metric']
        severity = alert['severity']

        return OptimizationRecommendation(
            recommendation_id=rec_id,
            category=OptimizationCategory.RISK_MITIGATION,
            title=f"Address {metric} Performance Issue",
            description=f"Current {metric} performance is {alert['variance_percentage']:.1f}% below expected. {alert['message']}",
            expected_impact=0.8 if severity == 'critical' else 0.6,
            implementation_effort='medium' if severity == 'critical' else 'low',
            timeline_weeks=2 if severity == 'critical' else 1,
            resource_requirements={
                'team_size': 2 if severity == 'critical' else 1,
                'budget_estimate': 'medium' if severity == 'critical' else 'low',
                'external_support': severity == 'critical'
            },
            risk_level='low',
            confidence_score=0.9,
            supporting_metrics=[PerformanceMetric(metric)],
            implementation_steps=alert.get('recommended_actions', [])
        )

# Service instance management
_performance_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the singleton performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer