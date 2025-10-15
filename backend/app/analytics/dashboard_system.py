"""
Dashboard System - Sprint 13
Advanced dashboard management, visualization engine, and interactive analytics interface
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json

class VisualizationType(Enum):
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    AREA_CHART = "area_chart"
    SCATTER_PLOT = "scatter_plot"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TABLE = "table"
    METRIC_CARD = "metric_card"
    PROGRESS_BAR = "progress_bar"
    SPARKLINE = "sparkline"

class DashboardType(Enum):
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    FINANCIAL = "financial"
    PERFORMANCE = "performance"
    CUSTOM = "custom"

class RefreshInterval(Enum):
    REAL_TIME = "real_time"
    FIVE_SECONDS = "5s"
    THIRTY_SECONDS = "30s"
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    HOURLY = "1h"
    MANUAL = "manual"

class LayoutType(Enum):
    GRID = "grid"
    FREE_FORM = "free_form"
    TABS = "tabs"
    ACCORDION = "accordion"

class AccessLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"
    RESTRICTED = "restricted"

@dataclass
class ChartConfig:
    """Configuration for chart visualizations"""
    title: str
    chart_type: VisualizationType
    data_source: str
    x_axis: str
    y_axis: List[str]
    colors: List[str] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WidgetPosition:
    """Widget position and size on dashboard"""
    x: int
    y: int
    width: int
    height: int
    z_index: int = 0

@dataclass
class Widget:
    """Dashboard widget definition"""
    widget_id: str
    title: str
    visualization_type: VisualizationType
    data_query: str
    position: WidgetPosition
    config: ChartConfig
    refresh_interval: RefreshInterval = RefreshInterval.FIVE_MINUTES
    is_visible: bool = True
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class DashboardLayout:
    """Dashboard layout configuration"""
    layout_type: LayoutType
    columns: int
    rows: int
    gap: int
    padding: int
    responsive: bool = True
    breakpoints: Dict[str, int] = field(default_factory=dict)

@dataclass
class Dashboard:
    """Complete dashboard definition"""
    dashboard_id: str
    name: str
    description: str
    dashboard_type: DashboardType
    layout: DashboardLayout
    widgets: List[Widget]
    owner_id: str
    access_level: AccessLevel = AccessLevel.PRIVATE
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    shared_with: List[str] = field(default_factory=list)

@dataclass
class VisualizationData:
    """Data for visualization rendering"""
    labels: List[str]
    datasets: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DashboardSnapshot:
    """Dashboard state snapshot"""
    snapshot_id: str
    dashboard_id: str
    timestamp: datetime
    widget_data: Dict[str, VisualizationData]
    performance_metrics: Dict[str, float]

class VisualizationEngine:
    """Handles data processing and visualization generation"""

    def __init__(self):
        self.data_processors = {
            VisualizationType.LINE_CHART: self._process_line_chart,
            VisualizationType.BAR_CHART: self._process_bar_chart,
            VisualizationType.PIE_CHART: self._process_pie_chart,
            VisualizationType.AREA_CHART: self._process_area_chart,
            VisualizationType.GAUGE: self._process_gauge,
            VisualizationType.METRIC_CARD: self._process_metric_card,
            VisualizationType.TABLE: self._process_table
        }

    def generate_visualization(self, widget: Widget, raw_data: Dict[str, Any]) -> VisualizationData:
        """Generate visualization data for a widget"""
        processor = self.data_processors.get(
            widget.visualization_type,
            self._process_default
        )

        return processor(widget, raw_data)

    def _process_line_chart(self, widget: Widget, raw_data: Dict[str, Any]) -> VisualizationData:
        """Process data for line chart"""
        # Extract time series data
        timestamps = raw_data.get("timestamps", [])
        metrics = raw_data.get("metrics", {})

        labels = [ts.strftime("%H:%M") for ts in timestamps]
        datasets = []

        for metric_name, values in metrics.items():
            datasets.append({
                "label": metric_name,
                "data": values,
                "borderColor": self._get_color_for_metric(metric_name),
                "backgroundColor": self._get_color_for_metric(metric_name, alpha=0.2),
                "tension": 0.4
            })

        return VisualizationData(
            labels=labels,
            datasets=datasets,
            metadata={"chart_type": "line", "time_range": "1h"}
        )

    def _process_bar_chart(self, widget: Widget, raw_data: Dict[str, Any]) -> VisualizationData:
        """Process data for bar chart"""
        categories = raw_data.get("categories", [])
        values = raw_data.get("values", [])

        datasets = [{
            "label": widget.title,
            "data": values,
            "backgroundColor": [
                self._get_color_for_index(i) for i in range(len(values))
            ],
            "borderWidth": 1
        }]

        return VisualizationData(
            labels=categories,
            datasets=datasets,
            metadata={"chart_type": "bar"}
        )

    def _process_pie_chart(self, widget: Widget, raw_data: Dict[str, Any]) -> VisualizationData:
        """Process data for pie chart"""
        labels = raw_data.get("labels", [])
        values = raw_data.get("values", [])

        datasets = [{
            "data": values,
            "backgroundColor": [
                self._get_color_for_index(i) for i in range(len(values))
            ],
            "borderWidth": 2
        }]

        return VisualizationData(
            labels=labels,
            datasets=datasets,
            metadata={"chart_type": "pie"}
        )

    def _process_area_chart(self, widget: Widget, raw_data: Dict[str, Any]) -> VisualizationData:
        """Process data for area chart"""
        timestamps = raw_data.get("timestamps", [])
        metrics = raw_data.get("metrics", {})

        labels = [ts.strftime("%H:%M") for ts in timestamps]
        datasets = []

        for metric_name, values in metrics.items():
            datasets.append({
                "label": metric_name,
                "data": values,
                "fill": True,
                "backgroundColor": self._get_color_for_metric(metric_name, alpha=0.3),
                "borderColor": self._get_color_for_metric(metric_name),
                "tension": 0.4
            })

        return VisualizationData(
            labels=labels,
            datasets=datasets,
            metadata={"chart_type": "area"}
        )

    def _process_gauge(self, widget: Widget, raw_data: Dict[str, Any]) -> VisualizationData:
        """Process data for gauge chart"""
        current_value = raw_data.get("current_value", 0)
        max_value = raw_data.get("max_value", 100)
        min_value = raw_data.get("min_value", 0)

        return VisualizationData(
            labels=["Current", "Remaining"],
            datasets=[{
                "data": [current_value, max_value - current_value],
                "backgroundColor": ["#4CAF50", "#E0E0E0"],
                "borderWidth": 0
            }],
            metadata={
                "chart_type": "gauge",
                "value": current_value,
                "min": min_value,
                "max": max_value
            }
        )

    def _process_metric_card(self, widget: Widget, raw_data: Dict[str, Any]) -> VisualizationData:
        """Process data for metric card"""
        value = raw_data.get("value", 0)
        change = raw_data.get("change", 0)
        unit = raw_data.get("unit", "")

        return VisualizationData(
            labels=[],
            datasets=[],
            metadata={
                "chart_type": "metric_card",
                "value": value,
                "change": change,
                "unit": unit,
                "trend": "up" if change > 0 else "down" if change < 0 else "stable"
            }
        )

    def _process_table(self, widget: Widget, raw_data: Dict[str, Any]) -> VisualizationData:
        """Process data for table"""
        headers = raw_data.get("headers", [])
        rows = raw_data.get("rows", [])

        return VisualizationData(
            labels=headers,
            datasets=rows,
            metadata={"chart_type": "table"}
        )

    def _process_default(self, widget: Widget, raw_data: Dict[str, Any]) -> VisualizationData:
        """Default data processor"""
        return VisualizationData(
            labels=[],
            datasets=[],
            metadata={"chart_type": "unknown", "error": "Unsupported visualization type"}
        )

    def _get_color_for_metric(self, metric_name: str, alpha: float = 1.0) -> str:
        """Get consistent color for metric"""
        colors = [
            "#2196F3", "#4CAF50", "#FF9800", "#F44336",
            "#9C27B0", "#607D8B", "#795548", "#009688"
        ]
        index = hash(metric_name) % len(colors)
        base_color = colors[index]

        if alpha < 1.0:
            # Convert hex to rgba
            hex_color = base_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"

        return base_color

    def _get_color_for_index(self, index: int) -> str:
        """Get color by index"""
        colors = [
            "#2196F3", "#4CAF50", "#FF9800", "#F44336",
            "#9C27B0", "#607D8B", "#795548", "#009688",
            "#CDDC39", "#00BCD4", "#E91E63", "#3F51B5"
        ]
        return colors[index % len(colors)]

class DashboardManager:
    """Manages dashboard lifecycle and operations"""

    def __init__(self):
        self.dashboards = {}
        self.templates = {}
        self.user_dashboards = defaultdict(list)
        self._initialize_templates()

    def create_dashboard(self, name: str, dashboard_type: DashboardType,
                        owner_id: str, description: str = "") -> str:
        """Create a new dashboard"""
        dashboard_id = f"dash_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create default layout
        layout = DashboardLayout(
            layout_type=LayoutType.GRID,
            columns=12,
            rows=8,
            gap=16,
            padding=24,
            responsive=True,
            breakpoints={"sm": 576, "md": 768, "lg": 992, "xl": 1200}
        )

        dashboard = Dashboard(
            dashboard_id=dashboard_id,
            name=name,
            description=description,
            dashboard_type=dashboard_type,
            layout=layout,
            widgets=[],
            owner_id=owner_id
        )

        self.dashboards[dashboard_id] = dashboard
        self.user_dashboards[owner_id].append(dashboard_id)

        return dashboard_id

    def add_widget(self, dashboard_id: str, widget: Widget) -> bool:
        """Add widget to dashboard"""
        if dashboard_id not in self.dashboards:
            return False

        self.dashboards[dashboard_id].widgets.append(widget)
        self.dashboards[dashboard_id].updated_at = datetime.now()
        return True

    def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """Remove widget from dashboard"""
        if dashboard_id not in self.dashboards:
            return False

        dashboard = self.dashboards[dashboard_id]
        dashboard.widgets = [w for w in dashboard.widgets if w.widget_id != widget_id]
        dashboard.updated_at = datetime.now()
        return True

    def update_widget(self, dashboard_id: str, widget_id: str,
                     updates: Dict[str, Any]) -> bool:
        """Update widget configuration"""
        if dashboard_id not in self.dashboards:
            return False

        dashboard = self.dashboards[dashboard_id]
        for widget in dashboard.widgets:
            if widget.widget_id == widget_id:
                # Update widget properties
                for key, value in updates.items():
                    if hasattr(widget, key):
                        setattr(widget, key, value)

                widget.last_updated = datetime.now()
                dashboard.updated_at = datetime.now()
                return True

        return False

    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard by ID"""
        return self.dashboards.get(dashboard_id)

    def get_user_dashboards(self, user_id: str) -> List[Dashboard]:
        """Get all dashboards for a user"""
        dashboard_ids = self.user_dashboards.get(user_id, [])
        return [self.dashboards[did] for did in dashboard_ids if did in self.dashboards]

    def share_dashboard(self, dashboard_id: str, user_ids: List[str]) -> bool:
        """Share dashboard with users"""
        if dashboard_id not in self.dashboards:
            return False

        dashboard = self.dashboards[dashboard_id]
        dashboard.shared_with.extend(user_ids)
        dashboard.access_level = AccessLevel.INTERNAL
        dashboard.updated_at = datetime.now()

        return True

    def clone_dashboard(self, dashboard_id: str, new_name: str,
                       new_owner_id: str) -> Optional[str]:
        """Clone an existing dashboard"""
        original = self.dashboards.get(dashboard_id)
        if not original:
            return None

        new_dashboard_id = f"dash_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Deep copy the dashboard
        cloned_dashboard = Dashboard(
            dashboard_id=new_dashboard_id,
            name=new_name,
            description=f"Clone of {original.name}",
            dashboard_type=original.dashboard_type,
            layout=original.layout,
            widgets=[],
            owner_id=new_owner_id
        )

        # Clone widgets with new IDs
        for widget in original.widgets:
            new_widget_id = f"widget_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            cloned_widget = Widget(
                widget_id=new_widget_id,
                title=widget.title,
                visualization_type=widget.visualization_type,
                data_query=widget.data_query,
                position=widget.position,
                config=widget.config,
                refresh_interval=widget.refresh_interval
            )
            cloned_dashboard.widgets.append(cloned_widget)

        self.dashboards[new_dashboard_id] = cloned_dashboard
        self.user_dashboards[new_owner_id].append(new_dashboard_id)

        return new_dashboard_id

    def _initialize_templates(self):
        """Initialize dashboard templates"""
        # Executive Dashboard Template
        self.templates["executive"] = {
            "name": "Executive Dashboard",
            "description": "High-level KPIs and business metrics",
            "widgets": [
                {
                    "title": "Total Deals",
                    "type": VisualizationType.METRIC_CARD,
                    "position": {"x": 0, "y": 0, "width": 3, "height": 2}
                },
                {
                    "title": "Revenue Trend",
                    "type": VisualizationType.LINE_CHART,
                    "position": {"x": 3, "y": 0, "width": 6, "height": 4}
                },
                {
                    "title": "Deal Status",
                    "type": VisualizationType.PIE_CHART,
                    "position": {"x": 9, "y": 0, "width": 3, "height": 4}
                }
            ]
        }

class DashboardSystem:
    """Central dashboard system coordinating all dashboard operations"""

    def __init__(self):
        self.dashboard_manager = DashboardManager()
        self.visualization_engine = VisualizationEngine()
        self.active_subscriptions = {}
        self.performance_metrics = {
            "dashboards_created": 0,
            "widgets_rendered": 0,
            "real_time_updates": 0
        }

    async def create_dashboard(self, name: str, dashboard_type: DashboardType,
                             owner_id: str, description: str = "") -> str:
        """Create a new dashboard"""
        dashboard_id = self.dashboard_manager.create_dashboard(
            name, dashboard_type, owner_id, description
        )
        self.performance_metrics["dashboards_created"] += 1
        return dashboard_id

    async def get_dashboard_data(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Get complete dashboard with rendered data"""
        dashboard = self.dashboard_manager.get_dashboard(dashboard_id)
        if not dashboard:
            return None

        # Render all widgets
        widget_data = {}
        for widget in dashboard.widgets:
            # Simulate data fetching based on widget query
            raw_data = await self._fetch_widget_data(widget)
            visualization_data = self.visualization_engine.generate_visualization(widget, raw_data)
            widget_data[widget.widget_id] = visualization_data.__dict__

        self.performance_metrics["widgets_rendered"] += len(dashboard.widgets)

        return {
            "dashboard": dashboard.__dict__,
            "widget_data": widget_data,
            "last_updated": datetime.now().isoformat()
        }

    async def get_widget_data(self, dashboard_id: str, widget_id: str) -> Optional[VisualizationData]:
        """Get data for a specific widget"""
        dashboard = self.dashboard_manager.get_dashboard(dashboard_id)
        if not dashboard:
            return None

        widget = next((w for w in dashboard.widgets if w.widget_id == widget_id), None)
        if not widget:
            return None

        raw_data = await self._fetch_widget_data(widget)
        return self.visualization_engine.generate_visualization(widget, raw_data)

    async def _fetch_widget_data(self, widget: Widget) -> Dict[str, Any]:
        """Fetch data for widget based on its query"""
        # Simulate data fetching based on widget type and query
        # In production, this would query the real-time analytics engine

        if widget.visualization_type == VisualizationType.METRIC_CARD:
            return {
                "value": 1250,
                "change": 15.3,
                "unit": widget.config.options.get("unit", "")
            }

        elif widget.visualization_type == VisualizationType.LINE_CHART:
            # Generate sample time series data
            now = datetime.now()
            timestamps = [now - timedelta(minutes=i*5) for i in range(12)]
            timestamps.reverse()

            return {
                "timestamps": timestamps,
                "metrics": {
                    "deals": [10, 15, 12, 18, 20, 25, 30, 28, 35, 32, 40, 45],
                    "revenue": [100, 150, 120, 180, 200, 250, 300, 280, 350, 320, 400, 450]
                }
            }

        elif widget.visualization_type == VisualizationType.PIE_CHART:
            return {
                "labels": ["Active", "Pending", "Completed", "Cancelled"],
                "values": [45, 25, 20, 10]
            }

        elif widget.visualization_type == VisualizationType.BAR_CHART:
            return {
                "categories": ["Q1", "Q2", "Q3", "Q4"],
                "values": [120, 150, 180, 200]
            }

        return {}

    def get_system_stats(self) -> Dict[str, Any]:
        """Get dashboard system statistics"""
        return {
            **self.performance_metrics,
            "total_dashboards": len(self.dashboard_manager.dashboards),
            "total_widgets": sum(len(d.widgets) for d in self.dashboard_manager.dashboards.values()),
            "active_subscriptions": len(self.active_subscriptions)
        }

# Singleton instance
_dashboard_system_instance: Optional[DashboardSystem] = None

def get_dashboard_system() -> DashboardSystem:
    """Get the singleton Dashboard System instance"""
    global _dashboard_system_instance
    if _dashboard_system_instance is None:
        _dashboard_system_instance = DashboardSystem()
    return _dashboard_system_instance