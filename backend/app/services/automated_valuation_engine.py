"""
Automated Valuation Engine
DCF, Comparable, and Precedent Transaction Analysis with AI-enhanced insights
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import logging
from enum import Enum
import numpy as np
import pandas as pd
from statistics import median, mean
import math

from app.services.claude_service import ClaudeService
from app.services.financial_intelligence import FinancialIntelligenceEngine

logger = logging.getLogger(__name__)

class ValuationMethod(Enum):
    """Valuation methodologies"""
    DCF = "dcf"
    COMPARABLE_COMPANIES = "comparable_companies"
    PRECEDENT_TRANSACTIONS = "precedent_transactions"
    ASSET_BASED = "asset_based"
    MARKET_MULTIPLE = "market_multiple"
    SUM_OF_PARTS = "sum_of_parts"

class RiskProfile(Enum):
    """Company risk profiles"""
    LOW_RISK = "low_risk"
    MODERATE_RISK = "moderate_risk"
    HIGH_RISK = "high_risk"
    DISTRESSED = "distressed"

@dataclass
class ValuationAssumptions:
    """Key valuation assumptions"""
    revenue_growth_rates: List[float]  # 5-year projections
    ebitda_margins: List[float]
    capex_as_percent_revenue: List[float]
    working_capital_as_percent_revenue: float
    tax_rate: float
    terminal_growth_rate: float
    discount_rate: float
    beta: float
    risk_free_rate: float
    market_risk_premium: float

@dataclass
class ComparableCompany:
    """Comparable company data"""
    company_name: str
    ticker: str
    market_cap: Decimal
    enterprise_value: Decimal
    revenue_ttm: Decimal
    ebitda_ttm: Decimal
    ev_revenue_multiple: float
    ev_ebitda_multiple: float
    revenue_growth_rate: float
    ebitda_margin: float
    geography: str
    industry_sub_sector: str

@dataclass
class PrecedentTransaction:
    """Precedent transaction data"""
    target_company: str
    acquirer: str
    transaction_date: datetime
    transaction_value: Decimal
    revenue_ttm: Decimal
    ebitda_ttm: Decimal
    ev_revenue_multiple: float
    ev_ebitda_multiple: float
    transaction_type: str  # strategic, financial, etc.
    geography: str
    industry: str
    deal_premium: Optional[float]

@dataclass
class ValuationResult:
    """Individual valuation method result"""
    method: ValuationMethod
    valuation: Decimal
    confidence_level: float
    key_assumptions: Dict[str, Any]
    sensitivity_analysis: Dict[str, List[float]]
    risk_factors: List[str]
    methodology_notes: str

@dataclass
class ComprehensiveValuation:
    """Complete valuation analysis"""
    company_id: str
    analysis_date: datetime
    valuation_results: List[ValuationResult]
    weighted_average_valuation: Decimal
    valuation_range: Tuple[Decimal, Decimal]
    recommended_valuation: Decimal
    confidence_score: float
    key_value_drivers: List[str]
    major_risk_factors: List[str]
    ai_insights: str
    benchmarking_data: Dict[str, Any]

class AutomatedValuationEngine:
    """
    Automated Valuation Engine

    Advanced multi-methodology valuation system that:
    - Performs DCF analysis with Monte Carlo simulation
    - Analyzes comparable companies with statistical refinement
    - Reviews precedent transactions with relevance weighting
    - Applies AI-enhanced insights and adjustments
    - Provides confidence scoring and risk assessment
    - Generates sensitivity analysis and scenario modeling
    """

    def __init__(self, financial_engine: FinancialIntelligenceEngine):
        self.financial_engine = financial_engine
        self.claude_service = ClaudeService()

        # Market data sources (in production, integrate with real data providers)
        self.market_data_sources = {
            'comparable_companies': 'bloomberg_api',
            'precedent_transactions': 'refinitiv_api',
            'market_multiples': 'factset_api'
        }

        # Industry-specific assumptions
        self.industry_defaults = {
            'software': {
                'terminal_growth': 0.025,
                'discount_rate_range': (0.10, 0.15),
                'typical_multiples': {'ev_revenue': (5.0, 12.0), 'ev_ebitda': (15.0, 30.0)}
            },
            'manufacturing': {
                'terminal_growth': 0.02,
                'discount_rate_range': (0.08, 0.12),
                'typical_multiples': {'ev_revenue': (1.0, 3.0), 'ev_ebitda': (8.0, 15.0)}
            },
            'healthcare': {
                'terminal_growth': 0.03,
                'discount_rate_range': (0.09, 0.14),
                'typical_multiples': {'ev_revenue': (3.0, 8.0), 'ev_ebitda': (12.0, 25.0)}
            }
        }

    async def perform_comprehensive_valuation(
        self,
        company_id: str,
        industry: str,
        custom_assumptions: Optional[Dict[str, Any]] = None
    ) -> ComprehensiveValuation:
        """
        Perform comprehensive multi-method valuation analysis

        Process:
        1. Gather financial data and build projections
        2. Perform DCF analysis with sensitivity testing
        3. Analyze comparable companies
        4. Review precedent transactions
        5. Apply AI-enhanced insights and adjustments
        6. Calculate weighted valuation and ranges
        7. Generate risk assessment and confidence scoring
        """

        logger.info(f"Starting comprehensive valuation for company {company_id}")

        # Step 1: Get financial intelligence and projections
        financial_analysis = await self.financial_engine.analyze_company_financials(
            company_id, include_projections=True
        )

        # Step 2: Build valuation assumptions
        assumptions = await self._build_valuation_assumptions(
            financial_analysis, industry, custom_assumptions
        )

        # Step 3: Perform individual valuation methods
        valuation_results = []

        # DCF Analysis
        dcf_result = await self._perform_dcf_analysis(
            financial_analysis, assumptions
        )
        valuation_results.append(dcf_result)

        # Comparable Companies Analysis
        comparable_result = await self._perform_comparable_analysis(
            financial_analysis, industry, assumptions
        )
        valuation_results.append(comparable_result)

        # Precedent Transactions Analysis
        precedent_result = await self._perform_precedent_analysis(
            financial_analysis, industry, assumptions
        )
        valuation_results.append(precedent_result)

        # Step 4: Apply AI-enhanced analysis
        ai_insights = await self._generate_ai_valuation_insights(
            financial_analysis, valuation_results, industry
        )

        # Step 5: Calculate weighted valuation
        weighted_valuation = await self._calculate_weighted_valuation(valuation_results)

        # Step 6: Determine valuation range and recommendation
        valuation_range = await self._calculate_valuation_range(valuation_results)
        recommended_valuation = await self._determine_recommended_valuation(
            valuation_results, ai_insights
        )

        # Step 7: Calculate confidence score
        confidence_score = await self._calculate_confidence_score(
            valuation_results, financial_analysis
        )

        # Step 8: Identify key value drivers and risks
        value_drivers = await self._identify_value_drivers(financial_analysis, ai_insights)
        risk_factors = await self._identify_risk_factors(financial_analysis, ai_insights)

        return ComprehensiveValuation(
            company_id=company_id,
            analysis_date=datetime.utcnow(),
            valuation_results=valuation_results,
            weighted_average_valuation=weighted_valuation,
            valuation_range=valuation_range,
            recommended_valuation=recommended_valuation,
            confidence_score=confidence_score,
            key_value_drivers=value_drivers,
            major_risk_factors=risk_factors,
            ai_insights=ai_insights,
            benchmarking_data=await self._generate_benchmarking_data(
                financial_analysis, industry
            )
        )

    # DCF Analysis Methods

    async def _perform_dcf_analysis(
        self,
        financial_analysis,
        assumptions: ValuationAssumptions
    ) -> ValuationResult:
        """Perform comprehensive DCF analysis with Monte Carlo simulation"""

        logger.info("Performing DCF analysis")

        # Step 1: Build financial projections
        projections = await self._build_financial_projections(
            financial_analysis, assumptions
        )

        # Step 2: Calculate free cash flows
        free_cash_flows = await self._calculate_free_cash_flows(projections, assumptions)

        # Step 3: Calculate terminal value
        terminal_value = await self._calculate_terminal_value(
            free_cash_flows[-1], assumptions
        )

        # Step 4: Discount cash flows to present value
        pv_cash_flows = await self._discount_cash_flows(free_cash_flows, assumptions.discount_rate)
        pv_terminal_value = terminal_value / ((1 + assumptions.discount_rate) ** 5)

        # Step 5: Calculate enterprise value
        enterprise_value = sum(pv_cash_flows) + pv_terminal_value

        # Step 6: Perform sensitivity analysis
        sensitivity_analysis = await self._perform_dcf_sensitivity_analysis(
            financial_analysis, assumptions
        )

        # Step 7: Monte Carlo simulation for confidence intervals
        monte_carlo_results = await self._perform_monte_carlo_dcf(
            financial_analysis, assumptions, n_simulations=1000
        )

        return ValuationResult(
            method=ValuationMethod.DCF,
            valuation=Decimal(enterprise_value),
            confidence_level=monte_carlo_results['confidence_level'],
            key_assumptions={
                'discount_rate': assumptions.discount_rate,
                'terminal_growth': assumptions.terminal_growth_rate,
                'revenue_cagr': self._calculate_cagr(assumptions.revenue_growth_rates),
                'avg_ebitda_margin': mean(assumptions.ebitda_margins)
            },
            sensitivity_analysis=sensitivity_analysis,
            risk_factors=await self._identify_dcf_risks(assumptions, financial_analysis),
            methodology_notes=f"5-year DCF with {assumptions.terminal_growth_rate:.1%} terminal growth"
        )

    async def _build_financial_projections(
        self,
        financial_analysis,
        assumptions: ValuationAssumptions
    ) -> Dict[str, List[float]]:
        """Build 5-year financial projections"""

        current_revenue = financial_analysis.key_metrics.get('revenue', 0)
        current_ebitda = financial_analysis.key_metrics.get('ebitda', 0)

        projections = {
            'revenue': [current_revenue],
            'ebitda': [current_ebitda],
            'capex': [],
            'working_capital_change': [],
            'taxes': []
        }

        # Project 5 years forward
        for year in range(5):
            # Revenue growth
            revenue = projections['revenue'][-1] * (1 + assumptions.revenue_growth_rates[year])
            projections['revenue'].append(revenue)

            # EBITDA
            ebitda = revenue * assumptions.ebitda_margins[year]
            projections['ebitda'].append(ebitda)

            # Capital expenditure
            capex = revenue * assumptions.capex_as_percent_revenue[year]
            projections['capex'].append(capex)

            # Working capital change
            wc_change = revenue * assumptions.working_capital_as_percent_revenue * 0.1  # 10% of WC requirement
            projections['working_capital_change'].append(wc_change)

            # Taxes (simplified)
            taxes = ebitda * assumptions.tax_rate if ebitda > 0 else 0
            projections['taxes'].append(taxes)

        return projections

    async def _calculate_free_cash_flows(
        self,
        projections: Dict[str, List[float]],
        assumptions: ValuationAssumptions
    ) -> List[float]:
        """Calculate free cash flows from projections"""

        free_cash_flows = []

        # Skip year 0 (current year)
        for year in range(1, 6):
            ebitda = projections['ebitda'][year]
            capex = projections['capex'][year - 1]  # Index adjustment
            wc_change = projections['working_capital_change'][year - 1]
            taxes = projections['taxes'][year - 1]

            # Free Cash Flow = EBITDA - Taxes - CapEx - Change in WC
            fcf = ebitda - taxes - capex - wc_change
            free_cash_flows.append(fcf)

        return free_cash_flows

    async def _calculate_terminal_value(
        self,
        final_year_fcf: float,
        assumptions: ValuationAssumptions
    ) -> float:
        """Calculate terminal value using Gordon Growth Model"""

        terminal_fcf = final_year_fcf * (1 + assumptions.terminal_growth_rate)
        terminal_value = terminal_fcf / (assumptions.discount_rate - assumptions.terminal_growth_rate)

        return terminal_value

    async def _discount_cash_flows(
        self,
        cash_flows: List[float],
        discount_rate: float
    ) -> List[float]:
        """Discount cash flows to present value"""

        pv_cash_flows = []

        for year, cf in enumerate(cash_flows, 1):
            pv = cf / ((1 + discount_rate) ** year)
            pv_cash_flows.append(pv)

        return pv_cash_flows

    # Comparable Companies Analysis

    async def _perform_comparable_analysis(
        self,
        financial_analysis,
        industry: str,
        assumptions: ValuationAssumptions
    ) -> ValuationResult:
        """Perform comparable companies analysis"""

        logger.info("Performing comparable companies analysis")

        # Step 1: Identify comparable companies
        comparables = await self._identify_comparable_companies(financial_analysis, industry)

        # Step 2: Calculate trading multiples
        trading_multiples = await self._calculate_trading_multiples(comparables)

        # Step 3: Apply multiples to target company
        target_revenue = financial_analysis.key_metrics.get('revenue', 0)
        target_ebitda = financial_analysis.key_metrics.get('ebitda', 0)

        # Calculate valuation using different multiples
        ev_revenue_valuation = target_revenue * trading_multiples['median_ev_revenue']
        ev_ebitda_valuation = target_ebitda * trading_multiples['median_ev_ebitda']

        # Weight the valuations (typically favor EBITDA multiple for profitable companies)
        if target_ebitda > 0:
            comparable_valuation = (ev_revenue_valuation * 0.3) + (ev_ebitda_valuation * 0.7)
        else:
            comparable_valuation = ev_revenue_valuation  # Use revenue multiple for unprofitable companies

        # Perform sensitivity analysis
        sensitivity = await self._perform_comparable_sensitivity_analysis(
            target_revenue, target_ebitda, comparables
        )

        return ValuationResult(
            method=ValuationMethod.COMPARABLE_COMPANIES,
            valuation=Decimal(comparable_valuation),
            confidence_level=trading_multiples['confidence_level'],
            key_assumptions={
                'median_ev_revenue_multiple': trading_multiples['median_ev_revenue'],
                'median_ev_ebitda_multiple': trading_multiples['median_ev_ebitda'],
                'comparable_companies_count': len(comparables)
            },
            sensitivity_analysis=sensitivity,
            risk_factors=await self._identify_comparable_risks(comparables, financial_analysis),
            methodology_notes=f"Based on {len(comparables)} comparable public companies"
        )

    # Precedent Transactions Analysis

    async def _perform_precedent_analysis(
        self,
        financial_analysis,
        industry: str,
        assumptions: ValuationAssumptions
    ) -> ValuationResult:
        """Perform precedent transactions analysis"""

        logger.info("Performing precedent transactions analysis")

        # Step 1: Identify relevant precedent transactions
        precedents = await self._identify_precedent_transactions(financial_analysis, industry)

        # Step 2: Calculate transaction multiples
        transaction_multiples = await self._calculate_transaction_multiples(precedents)

        # Step 3: Apply multiples to target company
        target_revenue = financial_analysis.key_metrics.get('revenue', 0)
        target_ebitda = financial_analysis.key_metrics.get('ebitda', 0)

        # Calculate valuation using precedent multiples
        ev_revenue_valuation = target_revenue * transaction_multiples['median_ev_revenue']
        ev_ebitda_valuation = target_ebitda * transaction_multiples['median_ev_ebitda']

        # Weight based on availability and relevance
        if target_ebitda > 0 and transaction_multiples['ebitda_transactions'] >= 3:
            precedent_valuation = (ev_revenue_valuation * 0.4) + (ev_ebitda_valuation * 0.6)
        else:
            precedent_valuation = ev_revenue_valuation

        return ValuationResult(
            method=ValuationMethod.PRECEDENT_TRANSACTIONS,
            valuation=Decimal(precedent_valuation),
            confidence_level=transaction_multiples['confidence_level'],
            key_assumptions={
                'median_transaction_ev_revenue': transaction_multiples['median_ev_revenue'],
                'median_transaction_ev_ebitda': transaction_multiples['median_ev_ebitda'],
                'relevant_transactions_count': len(precedents)
            },
            sensitivity_analysis=await self._perform_precedent_sensitivity_analysis(
                target_revenue, target_ebitda, precedents
            ),
            risk_factors=["Transaction market timing", "Deal structure differences"],
            methodology_notes=f"Based on {len(precedents)} relevant M&A transactions"
        )

    # Weighting and Synthesis Methods

    async def _calculate_weighted_valuation(
        self,
        valuation_results: List[ValuationResult]
    ) -> Decimal:
        """Calculate weighted average valuation based on confidence levels"""

        total_weight = 0
        weighted_sum = 0

        for result in valuation_results:
            weight = result.confidence_level
            weighted_sum += float(result.valuation) * weight
            total_weight += weight

        return Decimal(weighted_sum / total_weight) if total_weight > 0 else Decimal(0)

    async def _calculate_valuation_range(
        self,
        valuation_results: List[ValuationResult]
    ) -> Tuple[Decimal, Decimal]:
        """Calculate valuation range from all methods"""

        valuations = [float(result.valuation) for result in valuation_results]

        # Statistical approach: use confidence intervals
        mean_val = mean(valuations)
        std_dev = np.std(valuations) if len(valuations) > 1 else mean_val * 0.2

        # 80% confidence interval (approximately 1.28 standard deviations)
        low_val = max(0, mean_val - (1.28 * std_dev))
        high_val = mean_val + (1.28 * std_dev)

        return (Decimal(low_val), Decimal(high_val))

    # AI Enhancement Methods

    async def _generate_ai_valuation_insights(
        self,
        financial_analysis,
        valuation_results: List[ValuationResult],
        industry: str
    ) -> str:
        """Generate AI-powered valuation insights and adjustments"""

        valuation_summary = "\n".join([
            f"{result.method.value}: ${float(result.valuation):,.0f} (confidence: {result.confidence_level:.1%})"
            for result in valuation_results
        ])

        financial_metrics = f"""
        Revenue: ${financial_analysis.key_metrics.get('revenue', 0):,.0f}
        EBITDA: ${financial_analysis.key_metrics.get('ebitda', 0):,.0f}
        Revenue Growth: {financial_analysis.key_metrics.get('revenue_growth', 0):.1%}
        EBITDA Margin: {financial_analysis.key_metrics.get('ebitda_margin', 0):.1%}
        """

        ai_prompt = f"""
        Analyze this comprehensive valuation and provide investment-grade insights:

        COMPANY INDUSTRY: {industry}

        FINANCIAL METRICS:
        {financial_metrics}

        VALUATION RESULTS:
        {valuation_summary}

        KEY RISK FACTORS:
        {'; '.join(financial_analysis.risk_indicators)}

        GROWTH SIGNALS:
        {'; '.join(financial_analysis.growth_signals)}

        As a valuation expert, provide:
        1. Assessment of valuation methodology appropriateness
        2. Key value drivers and their impact
        3. Risk factors affecting valuation confidence
        4. Market positioning relative to peers
        5. Recommended valuation adjustments
        6. Investment thesis summary

        Focus on actionable insights for M&A decision-making.
        """

        ai_insights = await self.claude_service.analyze_content(ai_prompt)
        return ai_insights

    # Helper Methods

    def _calculate_cagr(self, growth_rates: List[float]) -> float:
        """Calculate compound annual growth rate"""
        if not growth_rates:
            return 0.0

        compound = 1.0
        for rate in growth_rates:
            compound *= (1 + rate)

        return compound ** (1 / len(growth_rates)) - 1

    # Placeholder methods for data retrieval (would connect to real market data in production)

    async def _build_valuation_assumptions(
        self,
        financial_analysis,
        industry: str,
        custom_assumptions: Optional[Dict[str, Any]]
    ) -> ValuationAssumptions:
        """Build comprehensive valuation assumptions"""

        # Industry defaults
        industry_data = self.industry_defaults.get(industry, self.industry_defaults['software'])

        # Calculate discount rate using CAPM
        risk_free_rate = 0.045  # Current 10-year treasury
        market_risk_premium = 0.065
        beta = custom_assumptions.get('beta', 1.2) if custom_assumptions else 1.2

        discount_rate = risk_free_rate + (beta * market_risk_premium)

        # Build revenue growth assumptions based on historical performance
        historical_growth = financial_analysis.key_metrics.get('revenue_growth', 0.05)
        revenue_growth_rates = [
            historical_growth * 0.9,  # Year 1: slightly conservative
            historical_growth * 0.8,  # Year 2: more conservative
            historical_growth * 0.7,  # Year 3: continued deceleration
            historical_growth * 0.6,  # Year 4
            historical_growth * 0.5   # Year 5: mature growth
        ]

        return ValuationAssumptions(
            revenue_growth_rates=revenue_growth_rates,
            ebitda_margins=[financial_analysis.key_metrics.get('ebitda_margin', 0.15)] * 5,
            capex_as_percent_revenue=[0.03] * 5,  # 3% of revenue
            working_capital_as_percent_revenue=0.05,  # 5% of revenue
            tax_rate=0.25,  # 25% corporate tax rate
            terminal_growth_rate=industry_data['terminal_growth'],
            discount_rate=discount_rate,
            beta=beta,
            risk_free_rate=risk_free_rate,
            market_risk_premium=market_risk_premium
        )

    async def _identify_comparable_companies(
        self, financial_analysis, industry: str
    ) -> List[ComparableCompany]:
        """Identify comparable public companies (placeholder implementation)"""

        # In production, this would query real market data APIs
        return [
            ComparableCompany(
                company_name="Comparable Co 1",
                ticker="COMP1",
                market_cap=Decimal("1000000000"),
                enterprise_value=Decimal("1200000000"),
                revenue_ttm=Decimal("500000000"),
                ebitda_ttm=Decimal("100000000"),
                ev_revenue_multiple=2.4,
                ev_ebitda_multiple=12.0,
                revenue_growth_rate=0.15,
                ebitda_margin=0.20,
                geography="North America",
                industry_sub_sector=industry
            )
            # Additional comparable companies would be added
        ]

    async def _calculate_trading_multiples(
        self, comparables: List[ComparableCompany]
    ) -> Dict[str, float]:
        """Calculate trading multiples statistics"""

        ev_revenue_multiples = [comp.ev_revenue_multiple for comp in comparables]
        ev_ebitda_multiples = [comp.ev_ebitda_multiple for comp in comparables if comp.ev_ebitda_multiple > 0]

        return {
            'median_ev_revenue': median(ev_revenue_multiples) if ev_revenue_multiples else 0,
            'median_ev_ebitda': median(ev_ebitda_multiples) if ev_ebitda_multiples else 0,
            'mean_ev_revenue': mean(ev_revenue_multiples) if ev_revenue_multiples else 0,
            'mean_ev_ebitda': mean(ev_ebitda_multiples) if ev_ebitda_multiples else 0,
            'confidence_level': 0.8 if len(comparables) >= 5 else 0.6
        }

    # Additional placeholder methods for complete implementation
    async def _identify_precedent_transactions(self, financial_analysis, industry): pass
    async def _calculate_transaction_multiples(self, precedents): pass
    async def _perform_dcf_sensitivity_analysis(self, financial_analysis, assumptions): pass
    async def _perform_monte_carlo_dcf(self, financial_analysis, assumptions, n_simulations): pass
    async def _identify_dcf_risks(self, assumptions, financial_analysis): pass
    async def _perform_comparable_sensitivity_analysis(self, revenue, ebitda, comparables): pass
    async def _identify_comparable_risks(self, comparables, financial_analysis): pass
    async def _perform_precedent_sensitivity_analysis(self, revenue, ebitda, precedents): pass
    async def _determine_recommended_valuation(self, results, ai_insights): pass
    async def _calculate_confidence_score(self, results, financial_analysis): pass
    async def _identify_value_drivers(self, financial_analysis, ai_insights): pass
    async def _identify_risk_factors(self, financial_analysis, ai_insights): pass
    async def _generate_benchmarking_data(self, financial_analysis, industry): pass