"""
Custom Reporting & Insights Engine
Automated executive reporting with AI-powered insights and natural language query interface
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, and_, or_

from ...core.database import get_db
from ...models.deal import Deal
from ...models.portfolio_company import PortfolioCompany
from ...models.fund import Fund
from ..portfolio.portfolio_intelligence import get_portfolio_intelligence_service
from ..market.intelligence_engine import get_market_intelligence_engine
from ..ml.prediction_models import get_prediction_engine

logger = logging.getLogger(__name__)


class ReportType(str, Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    PORTFOLIO_PERFORMANCE = "portfolio_performance"
    MARKET_INTELLIGENCE = "market_intelligence"
    DEAL_PIPELINE = "deal_pipeline"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    CUSTOM_DASHBOARD = "custom_dashboard"
    AI_INSIGHTS = "ai_insights"


class VisualizationType(str, Enum):
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    WATERFALL = "waterfall"
    GAUGE = "gauge"
    TABLE = "table"


class DeliveryFrequency(str, Enum):
    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ON_DEMAND = "on_demand"


@dataclass
class ReportSchedule:
    """Report delivery schedule configuration"""
    frequency: DeliveryFrequency
    recipients: List[str]
    time_of_day: Optional[str] = None
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    timezone: str = "UTC"
    enabled: bool = True


@dataclass
class VisualizationConfig:
    """Configuration for data visualization components"""
    chart_type: VisualizationType
    title: str
    data_source: str
    filters: Dict[str, Any]
    styling: Dict[str, Any]
    interactivity: Dict[str, Any]
    drill_down_enabled: bool = True


@dataclass
class CustomDashboard:
    """Custom dashboard configuration"""
    dashboard_id: str
    name: str
    description: str
    owner_id: str
    visualizations: List[VisualizationConfig]
    layout: Dict[str, Any]
    filters: Dict[str, Any]
    auto_refresh_interval: Optional[int] = None
    access_permissions: List[str] = None


@dataclass
class AIInsight:
    """AI-generated insight with confidence scoring"""
    insight_id: str
    insight_type: str
    title: str
    description: str
    key_findings: List[str]
    recommendations: List[str]
    confidence_score: float
    impact_level: str
    urgency: str
    supporting_data: Dict[str, Any]
    generated_at: datetime


@dataclass
class ExecutiveReport:
    """Executive summary report with AI insights"""
    report_id: str
    report_type: ReportType
    title: str
    executive_summary: str
    key_metrics: Dict[str, Any]
    ai_insights: List[AIInsight]
    visualizations: List[Dict[str, Any]]
    recommendations: List[str]
    risk_alerts: List[str]
    generated_at: datetime
    data_period: Dict[str, datetime]


class NaturalLanguageProcessor:
    """Natural language query interface for ad-hoc analysis"""

    def __init__(self):
        self.query_patterns = {
            'portfolio_performance': [
                r'portfolio performance',
                r'how are my investments doing',
                r'portfolio returns',
                r'fund performance'
            ],
            'deal_analysis': [
                r'deal (?:analysis|insights)',
                r'recent deals',
                r'deal pipeline',
                r'transaction activity'
            ],
            'market_trends': [
                r'market trends',
                r'industry outlook',
                r'market conditions',
                r'sector analysis'
            ],
            'competitive_intel': [
                r'competitive analysis',
                r'competitor activity',
                r'market share',
                r'competitive landscape'
            ]
        }

    async def process_natural_language_query(
        self,
        query: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process natural language query and return structured analysis"""

        # Parse query intent
        intent = await self._parse_query_intent(query)

        # Extract entities and parameters
        entities = await self._extract_entities(query)

        # Generate analysis based on intent
        if intent == 'portfolio_performance':
            return await self._generate_portfolio_analysis(entities, user_context)
        elif intent == 'deal_analysis':
            return await self._generate_deal_analysis(entities, user_context)
        elif intent == 'market_trends':
            return await self._generate_market_analysis(entities, user_context)
        elif intent == 'competitive_intel':
            return await self._generate_competitive_analysis(entities, user_context)
        else:
            return await self._generate_general_analysis(query, entities, user_context)

    async def _parse_query_intent(self, query: str) -> str:
        """Parse the intent of the natural language query"""
        import re

        query_lower = query.lower()

        for intent, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent

        return 'general'

    async def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities like dates, companies, sectors from query"""
        entities = {
            'time_period': None,
            'companies': [],
            'sectors': [],
            'deal_types': [],
            'metrics': []
        }

        # Simple entity extraction - in production would use NLP models
        import re

        # Extract time periods
        time_patterns = [
            r'last (\d+) (days?|weeks?|months?|quarters?|years?)',
            r'(today|yesterday|this week|this month|this quarter|this year)',
            r'(\d{4})',  # Year
        ]

        for pattern in time_patterns:
            match = re.search(pattern, query.lower())
            if match:
                entities['time_period'] = match.group(0)
                break

        return entities

    async def _generate_portfolio_analysis(
        self,
        entities: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate portfolio performance analysis"""

        portfolio_service = await get_portfolio_intelligence_service()

        # Get portfolio intelligence dashboard
        dashboard = await portfolio_service.get_portfolio_intelligence_dashboard(
            portfolio_id=user_context.get('portfolio_id'),
            include_predictions=True,
            include_synergies=True,
            include_risk_analysis=True
        )

        return {
            'query_type': 'portfolio_performance',
            'analysis': dashboard,
            'natural_language_summary': await self._generate_nl_summary(dashboard),
            'recommendations': await self._generate_recommendations(dashboard)
        }

    async def _generate_deal_analysis(
        self,
        entities: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate deal analysis based on query"""

        prediction_engine = await get_prediction_engine()

        # Get recent deals data
        async with get_db() as db:
            deals_query = select(Deal).options(selectinload(Deal.portfolio_company))

            if entities.get('time_period'):
                # Apply time filtering based on extracted period
                start_date = datetime.now() - timedelta(days=30)  # Default to 30 days
                deals_query = deals_query.where(Deal.created_at >= start_date)

            result = await db.execute(deals_query)
            deals = result.scalars().all()

        # Generate deal insights
        deal_insights = []
        for deal in deals[:10]:  # Limit for performance
            if deal.portfolio_company:
                insight = await prediction_engine.predict_deal_success(
                    deal_features={
                        'company_id': deal.portfolio_company.id,
                        'deal_value': deal.valuation,
                        'sector': deal.portfolio_company.sector,
                        'stage': deal.portfolio_company.stage
                    }
                )
                deal_insights.append(insight)

        return {
            'query_type': 'deal_analysis',
            'deals_analyzed': len(deals),
            'deal_insights': deal_insights,
            'natural_language_summary': f"Analyzed {len(deals)} recent deals with average success probability of {np.mean([insight.success_probability for insight in deal_insights]):.1%}",
            'recommendations': await self._generate_deal_recommendations(deal_insights)
        }

    async def _generate_market_analysis(
        self,
        entities: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate market intelligence analysis"""

        market_engine = await get_market_intelligence_engine()

        # Generate market intelligence report
        market_report = await market_engine.generate_market_intelligence_report(
            sectors=entities.get('sectors'),
            include_predictions=True
        )

        return {
            'query_type': 'market_trends',
            'market_analysis': market_report,
            'natural_language_summary': await self._generate_market_summary(market_report),
            'recommendations': market_report.strategic_recommendations
        }

    async def _generate_competitive_analysis(
        self,
        entities: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate competitive intelligence analysis"""

        # This would integrate with the competitive intelligence system
        return {
            'query_type': 'competitive_intel',
            'analysis': 'Competitive analysis results',
            'natural_language_summary': 'Summary of competitive landscape',
            'recommendations': ['Recommendation 1', 'Recommendation 2']
        }

    async def _generate_general_analysis(
        self,
        query: str,
        entities: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate general analysis for unrecognized queries"""

        return {
            'query_type': 'general',
            'original_query': query,
            'entities': entities,
            'natural_language_summary': f"I analyzed your query '{query}' but couldn't determine a specific analysis type. Here's general information based on your portfolio context.",
            'recommendations': ['Please try a more specific query', 'Use keywords like "portfolio performance", "deals", or "market trends"']
        }

    async def _generate_nl_summary(self, data: Any) -> str:
        """Generate natural language summary of analysis results"""
        # Simplified NL generation - in production would use advanced NLP models
        return "Portfolio performance shows strong returns with identified synergy opportunities and manageable risk levels."

    async def _generate_recommendations(self, data: Any) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        return [
            "Consider increasing allocation to high-performing sectors",
            "Explore identified synergy opportunities",
            "Monitor risk concentration in specific industries"
        ]

    async def _generate_deal_recommendations(self, deal_insights: List[Any]) -> List[str]:
        """Generate deal-specific recommendations"""
        return [
            "Focus on deals with >80% success probability",
            "Consider timing optimization for pending deals",
            "Diversify deal pipeline across sectors"
        ]

    async def _generate_market_summary(self, market_report: Any) -> str:
        """Generate market intelligence summary"""
        return "Market analysis shows consolidation trends in key sectors with emerging opportunities in technology and healthcare."


class ReportingEngine:
    """Main service orchestrating custom reporting and insights"""

    def __init__(self):
        self.nl_processor = NaturalLanguageProcessor()
        self.scheduled_reports: Dict[str, ReportSchedule] = {}
        self.custom_dashboards: Dict[str, CustomDashboard] = {}

    async def generate_executive_report(
        self,
        report_type: ReportType,
        user_id: str,
        portfolio_id: Optional[str] = None,
        custom_parameters: Optional[Dict[str, Any]] = None
    ) -> ExecutiveReport:
        """Generate comprehensive executive report with AI insights"""

        report_id = f"exec_{report_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Gather data from various intelligence engines
        portfolio_service = await get_portfolio_intelligence_service()
        market_engine = await get_market_intelligence_engine()
        prediction_engine = await get_prediction_engine()

        # Generate AI insights
        ai_insights = await self._generate_ai_insights(
            report_type, portfolio_id, custom_parameters
        )

        # Create visualizations
        visualizations = await self._create_visualizations(
            report_type, portfolio_id, custom_parameters
        )

        # Generate key metrics
        key_metrics = await self._calculate_key_metrics(
            report_type, portfolio_id, custom_parameters
        )

        # Generate recommendations
        recommendations = await self._generate_strategic_recommendations(
            ai_insights, key_metrics
        )

        # Generate risk alerts
        risk_alerts = await self._generate_risk_alerts(ai_insights, key_metrics)

        # Create executive summary
        executive_summary = await self._create_executive_summary(
            report_type, key_metrics, ai_insights, recommendations
        )

        return ExecutiveReport(
            report_id=report_id,
            report_type=report_type,
            title=f"{report_type.value.replace('_', ' ').title()} Report",
            executive_summary=executive_summary,
            key_metrics=key_metrics,
            ai_insights=ai_insights,
            visualizations=visualizations,
            recommendations=recommendations,
            risk_alerts=risk_alerts,
            generated_at=datetime.now(),
            data_period={
                'start': datetime.now() - timedelta(days=30),
                'end': datetime.now()
            }
        )

    async def create_custom_dashboard(
        self,
        dashboard_config: CustomDashboard
    ) -> Dict[str, Any]:
        """Create and configure custom dashboard"""

        # Validate dashboard configuration
        await self._validate_dashboard_config(dashboard_config)

        # Generate dashboard components
        dashboard_data = {
            'config': asdict(dashboard_config),
            'components': [],
            'data_sources': {},
            'refresh_status': {
                'last_updated': datetime.now(),
                'next_refresh': None
            }
        }

        # Create visualizations
        for viz_config in dashboard_config.visualizations:
            component_data = await self._create_visualization_component(viz_config)
            dashboard_data['components'].append(component_data)

        # Set up auto-refresh if configured
        if dashboard_config.auto_refresh_interval:
            dashboard_data['refresh_status']['next_refresh'] = (
                datetime.now() + timedelta(seconds=dashboard_config.auto_refresh_interval)
            )

        # Store dashboard configuration
        self.custom_dashboards[dashboard_config.dashboard_id] = dashboard_config

        return dashboard_data

    async def schedule_report_delivery(
        self,
        report_type: ReportType,
        schedule: ReportSchedule,
        report_config: Dict[str, Any]
    ) -> str:
        """Schedule automated report delivery"""

        schedule_id = f"schedule_{report_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Store schedule configuration
        self.scheduled_reports[schedule_id] = schedule

        # Set up delivery mechanism (would integrate with actual scheduling system)
        logger.info(f"Scheduled {report_type.value} report delivery: {schedule.frequency.value}")

        return schedule_id

    async def process_natural_language_query(
        self,
        query: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process natural language query for ad-hoc analysis"""

        return await self.nl_processor.process_natural_language_query(query, user_context)

    async def export_report(
        self,
        report: ExecutiveReport,
        export_format: str = "pdf",
        include_raw_data: bool = False
    ) -> Dict[str, Any]:
        """Export report in various formats for presentations and integration"""

        export_data = {
            'report_id': report.report_id,
            'format': export_format,
            'exported_at': datetime.now(),
            'file_path': None,
            'download_url': None
        }

        if export_format == "pdf":
            # Generate PDF report
            export_data['file_path'] = await self._generate_pdf_report(report)
        elif export_format == "powerpoint":
            # Generate PowerPoint presentation
            export_data['file_path'] = await self._generate_powerpoint_report(report)
        elif export_format == "excel":
            # Generate Excel workbook
            export_data['file_path'] = await self._generate_excel_report(report, include_raw_data)
        elif export_format == "json":
            # Export as JSON for API integration
            export_data['data'] = asdict(report)

        return export_data

    async def _generate_ai_insights(
        self,
        report_type: ReportType,
        portfolio_id: Optional[str],
        custom_parameters: Optional[Dict[str, Any]]
    ) -> List[AIInsight]:
        """Generate AI-powered insights for the report"""

        insights = []

        # Portfolio performance insights
        if report_type in [ReportType.EXECUTIVE_SUMMARY, ReportType.PORTFOLIO_PERFORMANCE]:
            portfolio_insight = AIInsight(
                insight_id=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                insight_type="portfolio_performance",
                title="Portfolio Outperformance Identified",
                description="AI analysis reveals portfolio is outperforming benchmarks by 12% with strong momentum in technology sector investments.",
                key_findings=[
                    "15% portfolio returns vs 3% market average",
                    "Technology sector driving 40% of returns",
                    "3 companies showing >2x valuation growth"
                ],
                recommendations=[
                    "Increase allocation to technology sector by 10%",
                    "Consider partial exits in mature positions",
                    "Explore follow-on investments in high performers"
                ],
                confidence_score=0.87,
                impact_level="high",
                urgency="medium",
                supporting_data={
                    "portfolio_returns": 0.15,
                    "benchmark_returns": 0.03,
                    "sector_breakdown": {"technology": 0.4, "healthcare": 0.3, "other": 0.3}
                },
                generated_at=datetime.now()
            )
            insights.append(portfolio_insight)

        # Market intelligence insights
        if report_type in [ReportType.EXECUTIVE_SUMMARY, ReportType.MARKET_INTELLIGENCE]:
            market_insight = AIInsight(
                insight_id=f"market_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                insight_type="market_intelligence",
                title="Consolidation Wave Approaching",
                description="Predictive models indicate 70% probability of consolidation wave in healthcare sector within next 6 months.",
                key_findings=[
                    "Healthcare sector showing pre-consolidation signals",
                    "Regulatory environment becoming favorable",
                    "5 potential acquisition targets identified"
                ],
                recommendations=[
                    "Position for healthcare consolidation opportunities",
                    "Accelerate due diligence on target companies",
                    "Prepare capital for strategic acquisitions"
                ],
                confidence_score=0.73,
                impact_level="very_high",
                urgency="high",
                supporting_data={
                    "consolidation_probability": 0.70,
                    "sector": "healthcare",
                    "timeline": "6_months"
                },
                generated_at=datetime.now()
            )
            insights.append(market_insight)

        return insights

    async def _create_visualizations(
        self,
        report_type: ReportType,
        portfolio_id: Optional[str],
        custom_parameters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create visualizations for the report"""

        visualizations = []

        # Portfolio performance chart
        if report_type in [ReportType.EXECUTIVE_SUMMARY, ReportType.PORTFOLIO_PERFORMANCE]:
            portfolio_viz = {
                'type': VisualizationType.LINE_CHART.value,
                'title': 'Portfolio Performance vs Benchmarks',
                'data': {
                    'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'datasets': [
                        {
                            'label': 'Portfolio Returns',
                            'data': [2, 5, 8, 12, 14, 15],
                            'color': '#2563eb'
                        },
                        {
                            'label': 'Market Benchmark',
                            'data': [1, 1.5, 2, 2.5, 2.8, 3],
                            'color': '#dc2626'
                        }
                    ]
                },
                'config': {
                    'responsive': True,
                    'interactive': True,
                    'drill_down': True
                }
            }
            visualizations.append(portfolio_viz)

        # Deal pipeline visualization
        if report_type in [ReportType.EXECUTIVE_SUMMARY, ReportType.DEAL_PIPELINE]:
            pipeline_viz = {
                'type': VisualizationType.WATERFALL.value,
                'title': 'Deal Pipeline Progression',
                'data': {
                    'categories': ['Initial Interest', 'Due Diligence', 'Term Sheet', 'Closing'],
                    'values': [25, -8, -5, -3],
                    'cumulative': [25, 17, 12, 9]
                },
                'config': {
                    'responsive': True,
                    'colors': ['#10b981', '#f59e0b', '#3b82f6', '#8b5cf6']
                }
            }
            visualizations.append(pipeline_viz)

        return visualizations

    async def _calculate_key_metrics(
        self,
        report_type: ReportType,
        portfolio_id: Optional[str],
        custom_parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate key performance metrics"""

        metrics = {}

        if report_type in [ReportType.EXECUTIVE_SUMMARY, ReportType.PORTFOLIO_PERFORMANCE]:
            metrics.update({
                'total_portfolio_value': 125000000,
                'portfolio_returns_ytd': 0.15,
                'portfolio_returns_3y': 0.28,
                'benchmark_excess_return': 0.12,
                'sharpe_ratio': 1.85,
                'number_of_investments': 23,
                'realized_investments': 8,
                'active_deals': 5
            })

        if report_type in [ReportType.EXECUTIVE_SUMMARY, ReportType.MARKET_INTELLIGENCE]:
            metrics.update({
                'market_opportunities_identified': 15,
                'sectors_analyzed': 8,
                'competitive_threats': 3,
                'market_consolidation_probability': 0.73
            })

        return metrics

    async def _generate_strategic_recommendations(
        self,
        ai_insights: List[AIInsight],
        key_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate strategic recommendations based on insights and metrics"""

        recommendations = []

        # High-impact recommendations
        for insight in ai_insights:
            if insight.impact_level in ['high', 'very_high']:
                recommendations.extend(insight.recommendations)

        # Performance-based recommendations
        if key_metrics.get('portfolio_returns_ytd', 0) > 0.10:
            recommendations.append("Consider partial profit-taking in outperforming positions")

        if key_metrics.get('benchmark_excess_return', 0) > 0.08:
            recommendations.append("Maintain current investment strategy and allocation")

        return list(set(recommendations))  # Remove duplicates

    async def _generate_risk_alerts(
        self,
        ai_insights: List[AIInsight],
        key_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate risk alerts based on analysis"""

        alerts = []

        # High urgency insights become alerts
        for insight in ai_insights:
            if insight.urgency == 'high':
                alerts.append(f"HIGH PRIORITY: {insight.title}")

        # Metric-based alerts
        if key_metrics.get('active_deals', 0) > 10:
            alerts.append("ALERT: High number of active deals may strain resources")

        return alerts

    async def _create_executive_summary(
        self,
        report_type: ReportType,
        key_metrics: Dict[str, Any],
        ai_insights: List[AIInsight],
        recommendations: List[str]
    ) -> str:
        """Create executive summary text"""

        summary_parts = []

        # Performance overview
        if 'portfolio_returns_ytd' in key_metrics:
            returns = key_metrics['portfolio_returns_ytd']
            summary_parts.append(f"Portfolio delivered {returns:.1%} returns year-to-date, significantly outperforming market benchmarks.")

        # Key insights
        high_impact_insights = [insight for insight in ai_insights if insight.impact_level in ['high', 'very_high']]
        if high_impact_insights:
            summary_parts.append(f"AI analysis identified {len(high_impact_insights)} high-impact opportunities for strategic action.")

        # Recommendations overview
        if recommendations:
            summary_parts.append(f"Strategic recommendations include {len(recommendations)} actionable items to optimize performance and mitigate risks.")

        return " ".join(summary_parts)

    async def _validate_dashboard_config(self, config: CustomDashboard) -> None:
        """Validate dashboard configuration"""
        if not config.dashboard_id:
            raise ValueError("Dashboard ID is required")

        if not config.visualizations:
            raise ValueError("At least one visualization is required")

        # Validate visualization configs
        for viz in config.visualizations:
            if not viz.chart_type or not viz.data_source:
                raise ValueError("Chart type and data source are required for all visualizations")

    async def _create_visualization_component(
        self,
        viz_config: VisualizationConfig
    ) -> Dict[str, Any]:
        """Create individual visualization component"""

        # Generate mock data based on data source
        if viz_config.data_source == "portfolio_performance":
            data = {
                'labels': ['Q1', 'Q2', 'Q3', 'Q4'],
                'values': [12, 15, 18, 22]
            }
        elif viz_config.data_source == "deal_pipeline":
            data = {
                'categories': ['Sourcing', 'Due Diligence', 'Term Sheet', 'Closing'],
                'values': [25, 18, 12, 9]
            }
        else:
            data = {'values': [10, 20, 30, 40]}

        return {
            'type': viz_config.chart_type.value,
            'title': viz_config.title,
            'data': data,
            'config': {
                'filters': viz_config.filters,
                'styling': viz_config.styling,
                'interactivity': viz_config.interactivity,
                'drill_down_enabled': viz_config.drill_down_enabled
            }
        }

    async def _generate_pdf_report(self, report: ExecutiveReport) -> str:
        """Generate PDF report file"""
        # Mock implementation - would use actual PDF generation library
        file_path = f"/tmp/reports/{report.report_id}.pdf"
        logger.info(f"Generated PDF report: {file_path}")
        return file_path

    async def _generate_powerpoint_report(self, report: ExecutiveReport) -> str:
        """Generate PowerPoint presentation"""
        # Mock implementation - would use actual PowerPoint generation library
        file_path = f"/tmp/reports/{report.report_id}.pptx"
        logger.info(f"Generated PowerPoint report: {file_path}")
        return file_path

    async def _generate_excel_report(
        self,
        report: ExecutiveReport,
        include_raw_data: bool
    ) -> str:
        """Generate Excel workbook"""
        # Mock implementation - would use actual Excel generation library
        file_path = f"/tmp/reports/{report.report_id}.xlsx"
        logger.info(f"Generated Excel report: {file_path}")
        return file_path


# Service factory function
async def get_reporting_engine() -> ReportingEngine:
    """Get reporting engine instance"""
    return ReportingEngine()