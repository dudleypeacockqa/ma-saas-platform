"""
Chart and Visualization Generator
Creates charts for valuation reports and dashboards
"""
from typing import List, Dict, Any, Optional
import io
import base64

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ChartGenerator:
    """Generate charts for financial analysis"""

    def __init__(self):
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required. Install with: pip install matplotlib")

    def generate_waterfall_chart(
        self,
        categories: List[str],
        values: List[float],
        title: str = "DCF Valuation Waterfall"
    ) -> str:
        """
        Generate waterfall chart for DCF valuation build-up

        Args:
            categories: List of category labels
            values: List of values (positive and negative)
            title: Chart title

        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Calculate cumulative values
        cumulative = np.cumsum([0] + values[:-1])

        # Colors
        colors = ['green' if v > 0 else 'red' for v in values[:-1]] + ['blue']

        # Create bars
        ax.bar(range(len(values)), values, bottom=cumulative, color=colors, alpha=0.7)

        # Connect with lines
        for i in range(len(values) - 1):
            ax.plot([i, i + 1], [cumulative[i] + values[i], cumulative[i] + values[i]],
                   'k--', linewidth=0.5)

        # Formatting
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('Value ($M)', fontsize=12)
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for i, (cat, val) in enumerate(zip(categories, values)):
            y_pos = cumulative[i] + val
            ax.text(i, y_pos, f'${val:.1f}M', ha='center', va='bottom' if val > 0 else 'top')

        plt.tight_layout()

        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    def generate_sensitivity_heatmap(
        self,
        param1_values: List[float],
        param2_values: List[float],
        results_matrix: List[List[float]],
        param1_label: str,
        param2_label: str,
        title: str = "Sensitivity Analysis"
    ) -> str:
        """
        Generate heatmap for two-way sensitivity analysis

        Args:
            param1_values: X-axis parameter values
            param2_values: Y-axis parameter values
            results_matrix: Matrix of results
            param1_label: X-axis label
            param2_label: Y-axis label
            title: Chart title

        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Create heatmap
        im = ax.imshow(results_matrix, cmap='RdYlGn', aspect='auto')

        # Set ticks
        ax.set_xticks(np.arange(len(param1_values)))
        ax.set_yticks(np.arange(len(param2_values)))
        ax.set_xticklabels([f"{v:.1f}" for v in param1_values])
        ax.set_yticklabels([f"{v:.1f}" for v in param2_values])

        # Labels
        ax.set_xlabel(param1_label, fontsize=12)
        ax.set_ylabel(param2_label, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Add text annotations
        for i in range(len(param2_values)):
            for j in range(len(param1_values)):
                text = ax.text(j, i, f"{results_matrix[i][j]:.1f}",
                             ha="center", va="center", color="black", fontsize=8)

        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Enterprise Value ($M)', rotation=270, labelpad=20)

        plt.tight_layout()

        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    def generate_revenue_projection_chart(
        self,
        years: List[int],
        revenue_projections: List[float],
        title: str = "Revenue Projections"
    ) -> str:
        """
        Generate line chart for revenue projections

        Args:
            years: Year labels
            revenue_projections: Projected revenues
            title: Chart title

        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(years, revenue_projections, marker='o', linewidth=2, markersize=8, color='#2563eb')
        ax.fill_between(years, revenue_projections, alpha=0.3, color='#2563eb')

        # Formatting
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Revenue ($M)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3)

        # Add value labels
        for year, rev in zip(years, revenue_projections):
            ax.text(year, rev, f'${rev:.1f}M', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    def generate_comparable_multiples_chart(
        self,
        company_names: List[str],
        ev_ebitda_multiples: List[float],
        target_multiple: float,
        title: str = "EV/EBITDA Multiples Comparison"
    ) -> str:
        """
        Generate bar chart comparing company multiples

        Args:
            company_names: List of company names
            ev_ebitda_multiples: List of multiples
            target_multiple: Target company multiple
            title: Chart title

        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Colors
        colors = ['#93c5fd' if i < len(company_names) - 1 else '#2563eb'
                 for i in range(len(company_names))]

        bars = ax.bar(company_names, ev_ebitda_multiples, color=colors, alpha=0.8)

        # Add median line
        median = np.median(ev_ebitda_multiples)
        ax.axhline(y=median, color='red', linestyle='--', linewidth=2, label=f'Median: {median:.1f}x')

        # Formatting
        ax.set_ylabel('EV/EBITDA Multiple (x)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticklabels(company_names, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}x', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    def generate_lbo_returns_chart(
        self,
        years: List[int],
        equity_values: List[float],
        debt_balances: List[float],
        title: str = "LBO Returns Analysis"
    ) -> str:
        """
        Generate stacked area chart for LBO equity build-up

        Args:
            years: Year labels
            equity_values: Equity values by year
            debt_balances: Debt balances by year
            title: Chart title

        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Stacked area chart
        ax.fill_between(years, 0, debt_balances, alpha=0.6, color='#ef4444', label='Debt')
        ax.fill_between(years, debt_balances,
                       [d + e for d, e in zip(debt_balances, equity_values)],
                       alpha=0.6, color='#22c55e', label='Equity')

        # Formatting
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Value ($M)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(alpha=0.3)

        plt.tight_layout()

        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    def generate_valuation_range_chart(
        self,
        methods: List[str],
        low_values: List[float],
        base_values: List[float],
        high_values: List[float],
        title: str = "Valuation Summary by Method"
    ) -> str:
        """
        Generate range chart showing valuation by method

        Args:
            methods: Valuation method names
            low_values: Low-end valuations
            base_values: Base case valuations
            high_values: High-end valuations
            title: Chart title

        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        y_pos = np.arange(len(methods))

        # Plot ranges
        for i, (low, base, high) in enumerate(zip(low_values, base_values, high_values)):
            ax.plot([low, high], [i, i], 'o-', linewidth=2, markersize=8, color='#3b82f6')
            ax.plot(base, i, 'D', markersize=10, color='#22c55e', zorder=10)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(methods)
        ax.set_xlabel('Enterprise Value ($M)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        # Legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#3b82f6', markersize=8, label='Range'),
            Line2D([0], [0], marker='D', color='w', markerfacecolor='#22c55e', markersize=10, label='Base Case')
        ]
        ax.legend(handles=legend_elements, loc='best')

        plt.tight_layout()

        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    def generate_monte_carlo_distribution(
        self,
        simulation_results: List[float],
        base_case: float,
        title: str = "Monte Carlo Valuation Distribution"
    ) -> str:
        """
        Generate histogram for Monte Carlo simulation results

        Args:
            simulation_results: List of simulated valuations
            base_case: Base case valuation
            title: Chart title

        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Histogram
        n, bins, patches = ax.hist(simulation_results, bins=50, alpha=0.7, color='#3b82f6', edgecolor='black')

        # Add base case line
        ax.axvline(x=base_case, color='red', linestyle='--', linewidth=2, label=f'Base Case: ${base_case:.1f}M')

        # Add percentiles
        p10 = np.percentile(simulation_results, 10)
        p90 = np.percentile(simulation_results, 90)
        ax.axvline(x=p10, color='orange', linestyle=':', linewidth=1.5, label=f'P10: ${p10:.1f}M')
        ax.axvline(x=p90, color='green', linestyle=':', linewidth=1.5, label=f'P90: ${p90:.1f}M')

        # Formatting
        ax.set_xlabel('Enterprise Value ($M)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()

        return f"data:image/png;base64,{image_base64}"
