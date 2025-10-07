"""
Valuation Report Generator
Creates professional PDF reports with charts and analysis
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal
import io
import os
from sqlalchemy.orm import Session

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image as RLImage
    )
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from ..models.financial_models import (
    ValuationModel, DCFModel, ComparableCompanyAnalysis,
    PrecedentTransactionAnalysis, LBOModel, ValuationReport
)


class ValuationReportGenerator:
    """Generate professional PDF valuation reports"""

    def __init__(self, db: Session):
        self.db = db

        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")

    def generate_comprehensive_report(
        self,
        valuation_id: str,
        organization_id: str,
        include_charts: bool = True
    ) -> bytes:
        """
        Generate comprehensive valuation report PDF

        Args:
            valuation_id: Valuation model ID
            organization_id: Organization ID for multi-tenancy
            include_charts: Whether to include charts and visualizations

        Returns:
            PDF bytes
        """
        # Fetch valuation and all sub-models
        valuation = self.db.query(ValuationModel).filter(
            ValuationModel.id == valuation_id,
            ValuationModel.organization_id == organization_id
        ).first()

        if not valuation:
            raise ValueError(f"Valuation {valuation_id} not found")

        # Create PDF buffer
        buffer = io.BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Build report content
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Title Page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("VALUATION ANALYSIS", title_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"<b>{valuation.company_name}</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"{valuation.industry}", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"Valuation Date: {valuation.valuation_date.strftime('%B %d, %Y')}",
            styles['Normal']
        ))
        story.append(PageBreak())

        # Executive Summary
        story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
        story.append(Spacer(1, 12))

        summary_data = [
            ['Metric', 'Value'],
            ['Company Name', valuation.company_name],
            ['Industry', valuation.industry],
            ['Primary Methodology', valuation.primary_method.value.replace('_', ' ').title()],
            ['Enterprise Value (Base Case)', self._format_currency(valuation.base_case_value)],
        ]

        if valuation.ev_revenue_multiple:
            summary_data.append(['EV/Revenue Multiple', f"{float(valuation.ev_revenue_multiple):.1f}x"])
        if valuation.ev_ebitda_multiple:
            summary_data.append(['EV/EBITDA Multiple', f"{float(valuation.ev_ebitda_multiple):.1f}x"])

        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Valuation Range
        if valuation.pessimistic_value and valuation.optimistic_value:
            story.append(Paragraph("Valuation Range", heading_style))
            range_data = [
                ['Scenario', 'Enterprise Value'],
                ['Pessimistic', self._format_currency(valuation.pessimistic_value)],
                ['Base Case', self._format_currency(valuation.base_case_value)],
                ['Optimistic', self._format_currency(valuation.optimistic_value)],
            ]

            range_table = Table(range_data, colWidths=[3*inch, 3*inch])
            range_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 2), (-1, 2), colors.lightgreen),
            ]))

            story.append(range_table)
            story.append(PageBreak())

        # DCF Analysis
        dcf_models = valuation.dcf_models
        if dcf_models:
            for dcf in dcf_models:
                story.extend(self._generate_dcf_section(dcf, styles, heading_style, include_charts))

        # Comparable Company Analysis
        comp_analyses = valuation.comparable_analyses
        if comp_analyses:
            for comp in comp_analyses:
                story.extend(self._generate_comparable_section(comp, styles, heading_style))

        # Precedent Transaction Analysis
        prec_analyses = valuation.precedent_transactions
        if prec_analyses:
            for prec in prec_analyses:
                story.extend(self._generate_precedent_section(prec, styles, heading_style))

        # LBO Analysis
        lbo_models = valuation.lbo_models
        if lbo_models:
            for lbo in lbo_models:
                story.extend(self._generate_lbo_section(lbo, styles, heading_style, include_charts))

        # Build PDF
        doc.build(story)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def _generate_dcf_section(
        self,
        dcf: DCFModel,
        styles,
        heading_style,
        include_charts: bool
    ) -> List:
        """Generate DCF analysis section"""
        story = []

        story.append(Paragraph("DISCOUNTED CASH FLOW ANALYSIS", heading_style))
        story.append(Spacer(1, 12))

        # Key Assumptions
        assumptions_data = [
            ['Assumption', 'Value'],
            ['WACC', f"{float(dcf.wacc):.2f}%"],
            ['Terminal Growth Rate', f"{float(dcf.terminal_growth_rate):.2f}%" if dcf.terminal_growth_rate else 'N/A'],
            ['Projection Period', f"{dcf.projection_years} years"],
            ['Tax Rate', f"{float(dcf.tax_rate):.1f}%"],
        ]

        assumptions_table = Table(assumptions_data, colWidths=[3*inch, 2*inch])
        assumptions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(assumptions_table)
        story.append(Spacer(1, 20))

        # Revenue Projections
        if dcf.revenue_projections:
            story.append(Paragraph("Revenue Projections", styles['Heading3']))

            headers = ['Year'] + [f"Year {i+1}" for i in range(len(dcf.revenue_projections))]
            revenue_row = ['Revenue ($)'] + [
                self._format_currency(rev) for rev in dcf.revenue_projections
            ]

            proj_table = Table([headers, revenue_row])
            proj_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))

            story.append(proj_table)
            story.append(Spacer(1, 20))

        # Valuation Summary
        valuation_data = [
            ['Component', 'Value'],
            ['PV of Cash Flows', self._format_currency(sum(dcf.present_values) if dcf.present_values else 0)],
            ['Terminal Value', self._format_currency(dcf.terminal_value)],
            ['Enterprise Value', self._format_currency(dcf.enterprise_value)],
            ['Less: Net Debt', self._format_currency(dcf.net_debt)],
            ['Equity Value', self._format_currency(dcf.equity_value)],
        ]

        val_table = Table(valuation_data, colWidths=[3*inch, 2*inch])
        val_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -2), (-1, -1), colors.lightgreen),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))

        story.append(val_table)
        story.append(PageBreak())

        return story

    def _generate_comparable_section(
        self,
        comp: ComparableCompanyAnalysis,
        styles,
        heading_style
    ) -> List:
        """Generate comparable company analysis section"""
        story = []

        story.append(Paragraph("COMPARABLE COMPANY ANALYSIS", heading_style))
        story.append(Spacer(1, 12))

        # Multiples Summary
        multiples_data = [
            ['Multiple', 'Mean', 'Median', 'Selected'],
            [
                'EV/Revenue',
                f"{float(comp.ev_revenue_mean):.1f}x" if comp.ev_revenue_mean else 'N/A',
                f"{float(comp.ev_revenue_median):.1f}x" if comp.ev_revenue_median else 'N/A',
                f"{float(comp.selected_ev_revenue):.1f}x" if comp.selected_ev_revenue else 'N/A',
            ],
            [
                'EV/EBITDA',
                f"{float(comp.ev_ebitda_mean):.1f}x" if comp.ev_ebitda_mean else 'N/A',
                f"{float(comp.ev_ebitda_median):.1f}x" if comp.ev_ebitda_median else 'N/A',
                f"{float(comp.selected_ev_ebitda):.1f}x" if comp.selected_ev_ebitda else 'N/A',
            ],
        ]

        multiples_table = Table(multiples_data)
        multiples_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (3, 1), (3, -1), colors.lightblue),
        ]))

        story.append(multiples_table)
        story.append(Spacer(1, 20))

        # Implied Valuation
        story.append(Paragraph("Implied Enterprise Value", styles['Heading3']))
        story.append(Paragraph(
            f"<b>{self._format_currency(comp.implied_enterprise_value)}</b>",
            styles['Normal']
        ))

        story.append(PageBreak())
        return story

    def _generate_precedent_section(
        self,
        prec: PrecedentTransactionAnalysis,
        styles,
        heading_style
    ) -> List:
        """Generate precedent transaction analysis section"""
        story = []

        story.append(Paragraph("PRECEDENT TRANSACTION ANALYSIS", heading_style))
        story.append(Spacer(1, 12))

        story.append(Paragraph(
            f"Analysis of {len(prec.precedent_transactions)} comparable M&A transactions",
            styles['Normal']
        ))
        story.append(Spacer(1, 12))

        # Transaction Multiples
        multiples_data = [
            ['Multiple', 'Mean', 'Median', 'Selected'],
            [
                'EV/Revenue',
                f"{float(prec.ev_revenue_mean):.1f}x" if prec.ev_revenue_mean else 'N/A',
                f"{float(prec.ev_revenue_median):.1f}x" if prec.ev_revenue_median else 'N/A',
                f"{float(prec.selected_ev_revenue):.1f}x" if prec.selected_ev_revenue else 'N/A',
            ],
            [
                'EV/EBITDA',
                f"{float(prec.ev_ebitda_mean):.1f}x" if prec.ev_ebitda_mean else 'N/A',
                f"{float(prec.ev_ebitda_median):.1f}x" if prec.ev_ebitda_median else 'N/A',
                f"{float(prec.selected_ev_ebitda):.1f}x" if prec.selected_ev_ebitda else 'N/A',
            ],
        ]

        multiples_table = Table(multiples_data)
        multiples_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(multiples_table)
        story.append(Spacer(1, 20))

        # Implied Valuation
        story.append(Paragraph("Implied Enterprise Value", styles['Heading3']))
        story.append(Paragraph(
            f"<b>{self._format_currency(prec.implied_enterprise_value)}</b>",
            styles['Normal']
        ))

        story.append(PageBreak())
        return story

    def _generate_lbo_section(
        self,
        lbo: LBOModel,
        styles,
        heading_style,
        include_charts: bool
    ) -> List:
        """Generate LBO analysis section"""
        story = []

        story.append(Paragraph("LEVERAGED BUYOUT ANALYSIS", heading_style))
        story.append(Spacer(1, 12))

        # Transaction Structure
        structure_data = [
            ['Component', 'Amount', '% of Total'],
            ['Purchase Price', self._format_currency(lbo.purchase_price), '100%'],
            ['Equity Investment', self._format_currency(lbo.equity_investment),
             f"{float(lbo.equity_investment)/float(lbo.purchase_price)*100:.1f}%"],
            ['Total Debt', self._format_currency(lbo.total_debt),
             f"{float(lbo.total_debt)/float(lbo.purchase_price)*100:.1f}%"],
        ]

        structure_table = Table(structure_data)
        structure_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(structure_table)
        story.append(Spacer(1, 20))

        # Returns Analysis
        story.append(Paragraph("Returns Analysis", styles['Heading3']))

        returns_data = [
            ['Metric', 'Value'],
            ['Money Multiple (MOIC)', f"{float(lbo.money_multiple):.2f}x"],
            ['IRR', f"{float(lbo.irr):.1f}%"],
            ['Cash-on-Cash Return', f"{float(lbo.cash_on_cash_return):.1f}%"],
            ['Exit Enterprise Value', self._format_currency(lbo.exit_enterprise_value)],
        ]

        returns_table = Table(returns_data, colWidths=[3*inch, 2*inch])
        returns_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, 2), colors.lightgreen),
        ]))

        story.append(returns_table)
        story.append(PageBreak())

        return story

    def _format_currency(self, amount: Optional[Decimal]) -> str:
        """Format decimal as currency"""
        if amount is None:
            return "N/A"

        amount_float = float(amount)

        if amount_float >= 1_000_000_000:
            return f"${amount_float/1_000_000_000:.2f}B"
        elif amount_float >= 1_000_000:
            return f"${amount_float/1_000_000:.2f}M"
        elif amount_float >= 1_000:
            return f"${amount_float/1_000:.2f}K"
        else:
            return f"${amount_float:,.0f}"

    def save_report_to_db(
        self,
        valuation_id: str,
        organization_id: str,
        pdf_bytes: bytes,
        created_by: str,
        report_type: str = "Comprehensive Valuation Report"
    ) -> ValuationReport:
        """Save generated report to database"""

        # In production, upload PDF to S3 and store URL
        # For now, we'll just store metadata
        pdf_url = f"/reports/{valuation_id}.pdf"  # Placeholder

        report = ValuationReport(
            valuation_id=valuation_id,
            organization_id=organization_id,
            report_title=report_type,
            report_type=report_type,
            generated_by=created_by,
            pdf_url=pdf_url,
            include_dcf=True,
            include_comparable=True,
            include_precedent=True,
            include_lbo=True,
            include_sensitivity=True
        )

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report
