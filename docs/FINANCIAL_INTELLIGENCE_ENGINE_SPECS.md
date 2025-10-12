# Financial Intelligence Engine - Detailed Technical Specifications

## Executive Summary

The Financial Intelligence Engine (FIE) is the core differentiator of our irresistible M&A platform. It transforms raw accounting data into sophisticated financial intelligence within 30 seconds, combining real-time multi-tenant integrations, AI-powered analysis, and professional-grade valuations that match investment bank quality.

**Key Differentiators:**

- Real-time sync from 6+ accounting platforms
- 47 financial ratios with industry benchmarking
- AI-powered red flag detection and insights
- Multi-methodology valuations with confidence scoring
- Interactive offer modeling with Excel/PowerPoint export

---

## 1. Multi-Tenant Accounting Integration Architecture

### 1.1 Connector Framework Design

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import httpx

@dataclass
class AccountingConnection:
    """Standardized connection metadata"""
    tenant_id: str
    platform: str  # xero, quickbooks, sage, netsuite, freeagent, kashflow
    connection_id: str
    credentials: Dict[str, str]
    webhook_url: Optional[str]
    last_sync: datetime
    sync_frequency: int  # minutes
    data_quality_score: float
    is_active: bool

@dataclass
class FinancialDataSet:
    """Standardized financial data structure"""
    tenant_id: str
    company_id: str
    period_start: datetime
    period_end: datetime
    currency: str
    profit_loss: Dict[str, Any]
    balance_sheet: Dict[str, Any]
    cash_flow: Dict[str, Any]
    trial_balance: Dict[str, Any]
    aging_reports: Dict[str, Any]
    source_platform: str
    extraction_timestamp: datetime
    quality_metrics: Dict[str, float]

class BaseAccountingConnector(ABC):
    """Abstract base connector for all accounting platforms"""

    def __init__(self, tenant_id: str, connection_config: Dict[str, Any]):
        self.tenant_id = tenant_id
        self.config = connection_config
        self.client = httpx.AsyncClient(timeout=30.0)
        self.rate_limiter = self._initialize_rate_limiter()

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Platform-specific OAuth/API key authentication"""
        pass

    @abstractmethod
    async def fetch_companies(self) -> List[Dict[str, Any]]:
        """Get list of companies user has access to"""
        pass

    @abstractmethod
    async def fetch_financial_data(self, company_id: str,
                                 period_months: int = 12) -> FinancialDataSet:
        """Extract complete financial dataset"""
        pass

    @abstractmethod
    async def setup_webhooks(self, webhook_url: str) -> bool:
        """Configure real-time data sync webhooks"""
        pass

    async def validate_data_quality(self, data: FinancialDataSet) -> float:
        """Calculate data quality score (0-1)"""
        quality_score = 1.0

        # Check for missing required fields
        required_pl_fields = ['revenue', 'gross_profit', 'operating_profit', 'net_profit']
        missing_pl = sum(1 for field in required_pl_fields
                        if not data.profit_loss.get(field))
        quality_score -= (missing_pl * 0.1)

        # Check balance sheet integrity
        assets = data.balance_sheet.get('total_assets', 0)
        liabilities = data.balance_sheet.get('total_liabilities', 0)
        equity = data.balance_sheet.get('shareholders_equity', 0)

        if abs(assets - (liabilities + equity)) > 1000:  # £1k tolerance
            quality_score -= 0.2

        # Check for data recency
        days_old = (datetime.utcnow() - data.extraction_timestamp).days
        if days_old > 7:
            quality_score -= (days_old * 0.01)

        return max(quality_score, 0.0)
```

### 1.2 Platform-Specific Implementations

#### Xero Connector (UK SME Market Leader)

```python
class XeroConnector(BaseAccountingConnector):
    """Xero accounting system connector for UK SME market"""

    def __init__(self, tenant_id: str, connection_config: Dict[str, Any]):
        super().__init__(tenant_id, connection_config)
        self.base_url = "https://api.xero.com/api.xro/2.0"
        self.identity_url = "https://identity.xero.com/connect"

    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """OAuth2 PKCE flow for Xero"""
        try:
            auth_response = await self.client.post(
                f"{self.identity_url}/token",
                data={
                    'grant_type': 'authorization_code',
                    'client_id': credentials['client_id'],
                    'code': credentials['auth_code'],
                    'redirect_uri': credentials['redirect_uri'],
                    'code_verifier': credentials['code_verifier'],
                    'scope': 'accounting.reports.read accounting.transactions.read'
                }
            )

            if auth_response.status_code == 200:
                token_data = auth_response.json()
                self.access_token = token_data['access_token']
                self.refresh_token = token_data['refresh_token']
                return True
            return False

        except Exception as e:
            logger.error(f"Xero authentication failed: {e}")
            return False

    async def fetch_financial_data(self, company_id: str,
                                 period_months: int = 12) -> FinancialDataSet:
        """Extract comprehensive Xero financial data"""

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=period_months * 30)

        # Parallel data fetching for performance
        tasks = [
            self._fetch_profit_loss_report(start_date, end_date),
            self._fetch_balance_sheet_report(),
            self._fetch_cashflow_report(start_date, end_date),
            self._fetch_trial_balance(),
            self._fetch_aged_receivables(),
            self._fetch_aged_payables()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        pl_data, bs_data, cf_data, tb_data, ar_data, ap_data = results

        # Parse and standardize Xero data structure
        standardized_data = self._standardize_xero_data(
            pl_data, bs_data, cf_data, tb_data, ar_data, ap_data
        )

        return FinancialDataSet(
            tenant_id=self.tenant_id,
            company_id=company_id,
            period_start=start_date,
            period_end=end_date,
            currency=standardized_data['currency'],
            profit_loss=standardized_data['profit_loss'],
            balance_sheet=standardized_data['balance_sheet'],
            cash_flow=standardized_data['cash_flow'],
            trial_balance=standardized_data['trial_balance'],
            aging_reports={'receivables': ar_data, 'payables': ap_data},
            source_platform='xero',
            extraction_timestamp=datetime.utcnow(),
            quality_metrics=await self._calculate_quality_metrics(standardized_data)
        )

    async def setup_webhooks(self, webhook_url: str) -> bool:
        """Configure Xero webhooks for real-time sync"""
        webhook_config = {
            'url': webhook_url,
            'events': [
                'CREATE_INVOICE',
                'UPDATE_INVOICE',
                'CREATE_PAYMENT',
                'UPDATE_BANKTRANSACTION',
                'CREATE_BANKTRANSACTION'
            ]
        }

        response = await self.client.post(
            f"{self.base_url}/Webhooks",
            json=webhook_config,
            headers={'Authorization': f'Bearer {self.access_token}'}
        )

        return response.status_code == 200
```

#### QuickBooks Connector (US/UK Market)

```python
class QuickBooksConnector(BaseAccountingConnector):
    """QuickBooks Online/Desktop connector"""

    def __init__(self, tenant_id: str, connection_config: Dict[str, Any]):
        super().__init__(tenant_id, connection_config)
        self.base_url = "https://sandbox-quickbooks.api.intuit.com"
        self.discovery_url = "https://appcenter.intuit.com/connect/oauth2"

    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """OAuth2 flow for QuickBooks"""
        try:
            auth_response = await self.client.post(
                f"{self.discovery_url}/token",
                data={
                    'grant_type': 'authorization_code',
                    'code': credentials['auth_code'],
                    'redirect_uri': credentials['redirect_uri']
                },
                auth=(credentials['client_id'], credentials['client_secret'])
            )

            if auth_response.status_code == 200:
                token_data = auth_response.json()
                self.access_token = token_data['access_token']
                self.refresh_token = token_data['refresh_token']
                self.company_id = credentials['realmId']
                return True
            return False

        except Exception as e:
            logger.error(f"QuickBooks authentication failed: {e}")
            return False

    async def fetch_financial_data(self, company_id: str,
                                 period_months: int = 12) -> FinancialDataSet:
        """Extract QuickBooks financial data using Reports API"""

        # QuickBooks uses different report endpoints
        reports_base = f"{self.base_url}/v3/company/{self.company_id}/reports"

        tasks = [
            self._fetch_qb_profit_loss(reports_base, period_months),
            self._fetch_qb_balance_sheet(reports_base),
            self._fetch_qb_cashflow(reports_base, period_months),
            self._fetch_qb_trial_balance(reports_base),
            self._fetch_qb_aged_receivables(reports_base),
            self._fetch_qb_aged_payables(reports_base)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self._standardize_quickbooks_data(results, company_id)
```

### 1.3 Unified Data Standardization Engine

```python
class FinancialDataStandardizer:
    """Converts platform-specific data to unified format"""

    # Standard chart of accounts mapping
    STANDARD_ACCOUNTS = {
        'revenue': ['income', 'sales', 'turnover', 'revenue'],
        'cogs': ['cost_of_sales', 'cost_of_goods_sold', 'direct_costs'],
        'gross_profit': ['gross_profit', 'gross_margin'],
        'operating_expenses': ['operating_expenses', 'admin_expenses', 'selling_expenses'],
        'operating_profit': ['operating_profit', 'ebit', 'operating_income'],
        'interest_expense': ['interest_expense', 'finance_costs'],
        'tax_expense': ['tax_expense', 'corporation_tax'],
        'net_profit': ['net_profit', 'profit_after_tax', 'net_income'],
        'current_assets': ['current_assets', 'short_term_assets'],
        'fixed_assets': ['fixed_assets', 'non_current_assets', 'property_plant_equipment'],
        'current_liabilities': ['current_liabilities', 'short_term_liabilities'],
        'long_term_debt': ['long_term_debt', 'non_current_liabilities'],
        'shareholders_equity': ['shareholders_equity', 'owners_equity', 'capital_equity']
    }

    @classmethod
    def standardize_financial_data(cls, raw_data: Dict[str, Any],
                                 platform: str) -> Dict[str, Any]:
        """Convert platform-specific data to standard format"""

        standardized = {
            'profit_loss': {},
            'balance_sheet': {},
            'cash_flow': {},
            'currency': cls._detect_currency(raw_data),
            'period_info': cls._extract_period_info(raw_data)
        }

        # Map profit & loss accounts
        for standard_key, possible_keys in cls.STANDARD_ACCOUNTS.items():
            value = cls._find_account_value(raw_data.get('profit_loss', {}),
                                          possible_keys, platform)
            if value is not None:
                standardized['profit_loss'][standard_key] = value

        # Calculate derived metrics
        standardized['profit_loss'].update(
            cls._calculate_derived_pl_metrics(standardized['profit_loss'])
        )

        # Map balance sheet accounts
        for standard_key, possible_keys in cls.STANDARD_ACCOUNTS.items():
            if standard_key in ['current_assets', 'fixed_assets', 'current_liabilities',
                               'long_term_debt', 'shareholders_equity']:
                value = cls._find_account_value(raw_data.get('balance_sheet', {}),
                                              possible_keys, platform)
                if value is not None:
                    standardized['balance_sheet'][standard_key] = value

        # Calculate derived balance sheet metrics
        standardized['balance_sheet'].update(
            cls._calculate_derived_bs_metrics(standardized['balance_sheet'])
        )

        return standardized

    @classmethod
    def _calculate_derived_pl_metrics(cls, pl_data: Dict[str, float]) -> Dict[str, float]:
        """Calculate derived P&L metrics"""
        derived = {}

        # EBITDA calculation
        if pl_data.get('operating_profit') and pl_data.get('depreciation'):
            derived['ebitda'] = pl_data['operating_profit'] + pl_data['depreciation']
        elif pl_data.get('operating_profit'):
            # Estimate EBITDA as operating profit + 3% of revenue (industry average)
            revenue = pl_data.get('revenue', 0)
            derived['ebitda'] = pl_data['operating_profit'] + (revenue * 0.03)

        # Margin calculations
        revenue = pl_data.get('revenue', 0)
        if revenue > 0:
            derived['gross_margin'] = (pl_data.get('gross_profit', 0) / revenue) * 100
            derived['operating_margin'] = (pl_data.get('operating_profit', 0) / revenue) * 100
            derived['net_margin'] = (pl_data.get('net_profit', 0) / revenue) * 100
            derived['ebitda_margin'] = (derived.get('ebitda', 0) / revenue) * 100

        return derived
```

---

## 2. Real-Time Financial Analysis Engine

### 2.1 47 Key Financial Ratios Calculator

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
from datetime import datetime

@dataclass
class FinancialRatios:
    """Comprehensive financial ratios analysis"""

    # Liquidity Ratios
    current_ratio: float
    quick_ratio: float
    cash_ratio: float
    operating_cash_flow_ratio: float

    # Profitability Ratios
    gross_profit_margin: float
    operating_margin: float
    net_profit_margin: float
    ebitda_margin: float
    return_on_assets: float
    return_on_equity: float
    return_on_invested_capital: float

    # Leverage Ratios
    debt_to_equity: float
    debt_to_assets: float
    interest_coverage_ratio: float
    debt_service_coverage_ratio: float
    equity_multiplier: float

    # Efficiency Ratios
    asset_turnover: float
    inventory_turnover: float
    receivables_turnover: float
    payables_turnover: float
    working_capital_turnover: float

    # Growth Ratios
    revenue_growth_rate: float
    profit_growth_rate: float
    asset_growth_rate: float

    # Market/Valuation Ratios (if public company data available)
    price_to_earnings: Optional[float] = None
    price_to_book: Optional[float] = None
    enterprise_value_to_ebitda: Optional[float] = None

    # Industry Benchmarking
    industry_percentile_ranking: Dict[str, float]
    peer_comparison_score: float

class FinancialRatioCalculator:
    """Advanced financial ratio calculation engine"""

    def __init__(self, industry_benchmarks: Dict[str, Any]):
        self.industry_benchmarks = industry_benchmarks

    async def calculate_all_ratios(self, financial_data: FinancialDataSet,
                                 historical_data: List[FinancialDataSet],
                                 industry: str) -> FinancialRatios:
        """Calculate comprehensive financial ratios"""

        current = financial_data
        pl = current.profit_loss
        bs = current.balance_sheet
        cf = current.cash_flow

        # Liquidity Ratios
        liquidity_ratios = self._calculate_liquidity_ratios(bs, cf)

        # Profitability Ratios
        profitability_ratios = self._calculate_profitability_ratios(pl, bs)

        # Leverage Ratios
        leverage_ratios = self._calculate_leverage_ratios(pl, bs, cf)

        # Efficiency Ratios
        efficiency_ratios = self._calculate_efficiency_ratios(pl, bs)

        # Growth Ratios (requires historical data)
        growth_ratios = self._calculate_growth_ratios(current, historical_data)

        # Industry benchmarking
        benchmarking = await self._perform_industry_benchmarking(
            {**liquidity_ratios, **profitability_ratios, **leverage_ratios,
             **efficiency_ratios, **growth_ratios},
            industry
        )

        return FinancialRatios(
            **liquidity_ratios,
            **profitability_ratios,
            **leverage_ratios,
            **efficiency_ratios,
            **growth_ratios,
            industry_percentile_ranking=benchmarking['percentile_ranking'],
            peer_comparison_score=benchmarking['peer_score']
        )

    def _calculate_liquidity_ratios(self, bs: Dict[str, float],
                                  cf: Dict[str, float]) -> Dict[str, float]:
        """Calculate liquidity ratios"""
        current_assets = bs.get('current_assets', 0)
        current_liabilities = bs.get('current_liabilities', 0)
        cash = bs.get('cash_and_equivalents', 0)
        inventory = bs.get('inventory', 0)
        operating_cf = cf.get('operating_cash_flow', 0)

        return {
            'current_ratio': self._safe_divide(current_assets, current_liabilities),
            'quick_ratio': self._safe_divide(
                current_assets - inventory, current_liabilities
            ),
            'cash_ratio': self._safe_divide(cash, current_liabilities),
            'operating_cash_flow_ratio': self._safe_divide(
                operating_cf, current_liabilities
            )
        }

    def _calculate_profitability_ratios(self, pl: Dict[str, float],
                                      bs: Dict[str, float]) -> Dict[str, float]:
        """Calculate profitability ratios"""
        revenue = pl.get('revenue', 0)
        gross_profit = pl.get('gross_profit', 0)
        operating_profit = pl.get('operating_profit', 0)
        net_profit = pl.get('net_profit', 0)
        ebitda = pl.get('ebitda', 0)
        total_assets = bs.get('total_assets', 0)
        shareholders_equity = bs.get('shareholders_equity', 0)
        invested_capital = total_assets - bs.get('current_liabilities', 0)

        return {
            'gross_profit_margin': self._safe_divide(gross_profit, revenue) * 100,
            'operating_margin': self._safe_divide(operating_profit, revenue) * 100,
            'net_profit_margin': self._safe_divide(net_profit, revenue) * 100,
            'ebitda_margin': self._safe_divide(ebitda, revenue) * 100,
            'return_on_assets': self._safe_divide(net_profit, total_assets) * 100,
            'return_on_equity': self._safe_divide(net_profit, shareholders_equity) * 100,
            'return_on_invested_capital': self._safe_divide(
                operating_profit * 0.75, invested_capital  # Assume 25% tax rate
            ) * 100
        }

    def _calculate_leverage_ratios(self, pl: Dict[str, float],
                                 bs: Dict[str, float],
                                 cf: Dict[str, float]) -> Dict[str, float]:
        """Calculate leverage ratios"""
        total_debt = bs.get('total_debt', 0)
        shareholders_equity = bs.get('shareholders_equity', 0)
        total_assets = bs.get('total_assets', 0)
        operating_profit = pl.get('operating_profit', 0)
        interest_expense = pl.get('interest_expense', 0)
        operating_cf = cf.get('operating_cash_flow', 0)
        debt_service = bs.get('annual_debt_service', interest_expense * 1.5)  # Estimate

        return {
            'debt_to_equity': self._safe_divide(total_debt, shareholders_equity),
            'debt_to_assets': self._safe_divide(total_debt, total_assets),
            'interest_coverage_ratio': self._safe_divide(operating_profit, interest_expense),
            'debt_service_coverage_ratio': self._safe_divide(operating_cf, debt_service),
            'equity_multiplier': self._safe_divide(total_assets, shareholders_equity)
        }

    def _safe_divide(self, numerator: float, denominator: float) -> float:
        """Safe division to avoid division by zero"""
        return numerator / denominator if denominator != 0 else 0.0
```

### 2.2 Industry Benchmarking System

```python
class IndustryBenchmarkEngine:
    """Advanced industry benchmarking and peer analysis"""

    INDUSTRY_BENCHMARKS = {
        'software_saas': {
            'gross_margin': {'p25': 65, 'p50': 75, 'p75': 85},
            'operating_margin': {'p25': 5, 'p50': 15, 'p75': 25},
            'revenue_growth': {'p25': 15, 'p50': 25, 'p75': 40},
            'current_ratio': {'p25': 1.5, 'p50': 2.5, 'p75': 4.0},
            'debt_to_equity': {'p25': 0.1, 'p50': 0.3, 'p75': 0.6}
        },
        'manufacturing': {
            'gross_margin': {'p25': 25, 'p50': 35, 'p75': 45},
            'operating_margin': {'p25': 3, 'p50': 8, 'p75': 15},
            'revenue_growth': {'p25': 2, 'p50': 8, 'p75': 15},
            'current_ratio': {'p25': 1.2, 'p50': 1.8, 'p75': 2.5},
            'debt_to_equity': {'p25': 0.3, 'p50': 0.6, 'p75': 1.2}
        },
        'retail': {
            'gross_margin': {'p25': 35, 'p50': 45, 'p75': 55},
            'operating_margin': {'p25': 2, 'p50': 5, 'p75': 10},
            'revenue_growth': {'p25': 0, 'p50': 5, 'p75': 12},
            'current_ratio': {'p25': 1.0, 'p50': 1.5, 'p75': 2.2},
            'debt_to_equity': {'p25': 0.2, 'p50': 0.5, 'p75': 1.0}
        }
        # Add 200+ industry benchmarks
    }

    async def calculate_percentile_ranking(self, ratios: Dict[str, float],
                                         industry: str) -> Dict[str, float]:
        """Calculate percentile ranking against industry peers"""

        benchmarks = self.INDUSTRY_BENCHMARKS.get(industry, {})
        percentile_rankings = {}

        for ratio_name, ratio_value in ratios.items():
            if ratio_name in benchmarks:
                benchmark = benchmarks[ratio_name]

                # Calculate percentile using interpolation
                if ratio_value <= benchmark['p25']:
                    percentile = (ratio_value / benchmark['p25']) * 25
                elif ratio_value <= benchmark['p50']:
                    percentile = 25 + ((ratio_value - benchmark['p25']) /
                                     (benchmark['p50'] - benchmark['p25'])) * 25
                elif ratio_value <= benchmark['p75']:
                    percentile = 50 + ((ratio_value - benchmark['p50']) /
                                     (benchmark['p75'] - benchmark['p50'])) * 25
                else:
                    percentile = 75 + min(25,
                                        ((ratio_value - benchmark['p75']) /
                                         benchmark['p75']) * 25)

                percentile_rankings[ratio_name] = min(100, max(0, percentile))

        return percentile_rankings
```

---

## 3. AI-Powered Valuation Engine

### 3.1 Multi-Methodology Valuation Framework

```python
from enum import Enum
from dataclasses import dataclass
import numpy as np
from typing import Dict, List, Tuple, Optional

class ValuationMethod(Enum):
    DCF = "discounted_cash_flow"
    COMPARABLE_COMPANIES = "comparable_companies"
    PRECEDENT_TRANSACTIONS = "precedent_transactions"
    ASSET_BASED = "asset_based"
    MARKET_MULTIPLE = "market_multiple"

@dataclass
class ValuationResult:
    method: ValuationMethod
    enterprise_value: float
    equity_value: float
    confidence_score: float
    key_assumptions: Dict[str, Any]
    sensitivity_analysis: Dict[str, List[float]]
    risk_factors: List[str]

class ComprehensiveValuationEngine:
    """AI-powered multi-methodology valuation engine"""

    def __init__(self, claude_service, market_data_service):
        self.claude_service = claude_service
        self.market_data_service = market_data_service

    async def perform_comprehensive_valuation(self,
                                            financial_data: FinancialDataSet,
                                            ratios: FinancialRatios,
                                            industry: str,
                                            company_profile: Dict[str, Any]) -> List[ValuationResult]:
        """Perform comprehensive valuation using multiple methodologies"""

        valuation_results = []

        # 1. DCF Valuation with Monte Carlo simulation
        dcf_result = await self._perform_dcf_valuation(
            financial_data, ratios, industry, company_profile
        )
        valuation_results.append(dcf_result)

        # 2. Comparable Companies Analysis
        comp_result = await self._perform_comparable_analysis(
            financial_data, ratios, industry
        )
        valuation_results.append(comp_result)

        # 3. Precedent Transactions Analysis
        precedent_result = await self._perform_precedent_analysis(
            financial_data, ratios, industry
        )
        valuation_results.append(precedent_result)

        # 4. Asset-based valuation (for distressed situations)
        if self._is_distressed_situation(ratios):
            asset_result = await self._perform_asset_based_valuation(
                financial_data, ratios
            )
            valuation_results.append(asset_result)

        return valuation_results

    async def _perform_dcf_valuation(self, financial_data: FinancialDataSet,
                                   ratios: FinancialRatios, industry: str,
                                   company_profile: Dict[str, Any]) -> ValuationResult:
        """Advanced DCF with Monte Carlo simulation"""

        # Build 5-year projections using AI-enhanced assumptions
        projections = await self._build_ai_enhanced_projections(
            financial_data, ratios, industry, company_profile
        )

        # Calculate free cash flows
        free_cash_flows = await self._calculate_free_cash_flows(projections)

        # Determine discount rate using CAPM
        discount_rate = await self._calculate_wacc(financial_data, industry)

        # Calculate terminal value
        terminal_growth_rate = await self._estimate_terminal_growth(industry)
        terminal_value = self._calculate_terminal_value(
            free_cash_flows[-1], discount_rate, terminal_growth_rate
        )

        # Discount to present value
        pv_cash_flows = [cf / ((1 + discount_rate) ** (i + 1))
                        for i, cf in enumerate(free_cash_flows)]
        pv_terminal_value = terminal_value / ((1 + discount_rate) ** 5)

        enterprise_value = sum(pv_cash_flows) + pv_terminal_value

        # Monte Carlo simulation for confidence intervals
        confidence_score = await self._monte_carlo_dcf_simulation(
            projections, discount_rate, terminal_growth_rate, 1000
        )

        # Sensitivity analysis
        sensitivity = await self._dcf_sensitivity_analysis(
            projections, discount_rate, terminal_growth_rate
        )

        return ValuationResult(
            method=ValuationMethod.DCF,
            enterprise_value=enterprise_value,
            equity_value=enterprise_value - financial_data.balance_sheet.get('total_debt', 0),
            confidence_score=confidence_score,
            key_assumptions={
                'discount_rate': discount_rate,
                'terminal_growth': terminal_growth_rate,
                'revenue_cagr': self._calculate_cagr(
                    [p['revenue'] for p in projections]
                )
            },
            sensitivity_analysis=sensitivity,
            risk_factors=await self._identify_dcf_risks(projections, industry)
        )

    async def _build_ai_enhanced_projections(self, financial_data: FinancialDataSet,
                                           ratios: FinancialRatios, industry: str,
                                           company_profile: Dict[str, Any]) -> List[Dict[str, float]]:
        """Use AI to build intelligent financial projections"""

        ai_prompt = f"""
        Build 5-year financial projections for this {industry} company:

        CURRENT FINANCIALS:
        Revenue: ${financial_data.profit_loss.get('revenue', 0):,.0f}
        EBITDA: ${financial_data.profit_loss.get('ebitda', 0):,.0f}
        EBITDA Margin: {ratios.ebitda_margin:.1f}%
        Revenue Growth: {ratios.revenue_growth_rate:.1f}%

        COMPANY PROFILE:
        Age: {company_profile.get('company_age', 'Unknown')} years
        Market Position: {company_profile.get('market_position', 'Unknown')}
        Geographic Presence: {company_profile.get('geography', 'Unknown')}

        INDUSTRY CONTEXT: {industry}

        Provide realistic 5-year projections considering:
        1. Industry growth trends
        2. Company maturity and market position
        3. Economic cycle considerations
        4. Competitive dynamics

        Return JSON format:
        {{
            "year_1": {{"revenue_growth": 0.15, "ebitda_margin": 0.18, "capex_percent": 0.03}},
            "year_2": {{"revenue_growth": 0.12, "ebitda_margin": 0.19, "capex_percent": 0.03}},
            ...
        }}
        """

        ai_response = await self.claude_service.analyze_content(ai_prompt)

        try:
            ai_projections = json.loads(ai_response)
            return self._convert_ai_projections_to_financial_model(
                ai_projections, financial_data
            )
        except:
            # Fallback to rule-based projections
            return self._create_rule_based_projections(financial_data, ratios, industry)

    async def _monte_carlo_dcf_simulation(self, projections: List[Dict[str, float]],
                                        base_discount_rate: float,
                                        base_terminal_growth: float,
                                        num_simulations: int) -> float:
        """Monte Carlo simulation for DCF confidence scoring"""

        simulation_results = []

        for _ in range(num_simulations):
            # Add random variations to key assumptions
            discount_rate = np.random.normal(base_discount_rate, 0.02)  # ±2% std dev
            terminal_growth = np.random.normal(base_terminal_growth, 0.005)  # ±0.5% std dev

            # Vary projection assumptions
            varied_projections = []
            for year_proj in projections:
                varied_proj = year_proj.copy()
                varied_proj['revenue'] *= np.random.normal(1.0, 0.1)  # ±10% std dev
                varied_proj['ebitda'] *= np.random.normal(1.0, 0.15)  # ±15% std dev
                varied_projections.append(varied_proj)

            # Calculate valuation for this simulation
            fcf = [p['free_cash_flow'] for p in varied_projections]
            terminal_value = self._calculate_terminal_value(
                fcf[-1], discount_rate, terminal_growth
            )

            pv_fcf = [cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(fcf)]
            pv_terminal = terminal_value / ((1 + discount_rate) ** 5)

            simulation_results.append(sum(pv_fcf) + pv_terminal)

        # Calculate confidence score based on distribution tightness
        std_dev = np.std(simulation_results)
        mean_val = np.mean(simulation_results)
        coefficient_of_variation = std_dev / mean_val if mean_val > 0 else 1.0

        # Higher confidence for lower variation
        confidence_score = max(0.5, 1.0 - (coefficient_of_variation * 2))

        return min(1.0, confidence_score)
```

---

## 4. Interactive Offer Stack Generator

### 4.1 Dynamic Scenario Modeling

```python
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

class FundingSource(Enum):
    CASH = "cash"
    SENIOR_DEBT = "senior_debt"
    SUBORDINATED_DEBT = "subordinated_debt"
    SELLER_FINANCING = "seller_financing"
    EARNOUT = "earnout"
    EQUITY_ROLLOVER = "equity_rollover"
    PREFERRED_EQUITY = "preferred_equity"
    MEZZANINE = "mezzanine"

@dataclass
class FundingComponent:
    source: FundingSource
    amount: float
    percentage: float
    cost_of_capital: float
    terms: Dict[str, Any]
    risk_adjustment: float

@dataclass
class OfferScenario:
    scenario_name: str
    total_enterprise_value: float
    funding_components: List[FundingComponent]
    deal_structure_type: str
    estimated_irr: float
    cash_on_cash_multiple: float
    payback_period: float
    risk_score: float
    confidence_level: float

class InteractiveOfferStackGenerator:
    """Advanced offer scenario modeling with what-if analysis"""

    def __init__(self, valuation_engine, financial_intelligence):
        self.valuation_engine = valuation_engine
        self.financial_intelligence = financial_intelligence

    async def generate_offer_scenarios(self, target_company_id: str,
                                     buyer_profile: Dict[str, Any],
                                     valuation_results: List[ValuationResult]) -> List[OfferScenario]:
        """Generate 5 different offer scenarios with varying risk/return profiles"""

        # Calculate base valuation range
        base_ev = np.mean([v.enterprise_value for v in valuation_results])
        ev_range = (base_ev * 0.8, base_ev * 1.2)  # ±20% range

        scenarios = []

        # Scenario 1: Conservative All-Cash Offer
        conservative = await self._create_conservative_scenario(
            ev_range[0], buyer_profile
        )
        scenarios.append(conservative)

        # Scenario 2: Leveraged Acquisition (60% debt)
        leveraged = await self._create_leveraged_scenario(
            base_ev, buyer_profile
        )
        scenarios.append(leveraged)

        # Scenario 3: Creative Structure (Earnouts + Seller Financing)
        creative = await self._create_creative_scenario(
            base_ev, buyer_profile
        )
        scenarios.append(creative)

        # Scenario 4: Management-Friendly (Equity Rollover)
        if buyer_profile.get('management_participation', False):
            mgmt_friendly = await self._create_management_friendly_scenario(
                base_ev, buyer_profile
            )
            scenarios.append(mgmt_friendly)

        # Scenario 5: Aggressive High-Multiple Offer
        aggressive = await self._create_aggressive_scenario(
            ev_range[1], buyer_profile
        )
        scenarios.append(aggressive)

        return scenarios

    async def _create_conservative_scenario(self, enterprise_value: float,
                                          buyer_profile: Dict[str, Any]) -> OfferScenario:
        """Conservative all-cash or low-leverage scenario"""

        # 80% cash, 20% senior debt
        cash_amount = enterprise_value * 0.8
        debt_amount = enterprise_value * 0.2

        funding_components = [
            FundingComponent(
                source=FundingSource.CASH,
                amount=cash_amount,
                percentage=80.0,
                cost_of_capital=0.05,  # Risk-free rate
                terms={'immediate': True},
                risk_adjustment=0.0
            ),
            FundingComponent(
                source=FundingSource.SENIOR_DEBT,
                amount=debt_amount,
                percentage=20.0,
                cost_of_capital=0.065,  # Current senior debt rates
                terms={
                    'term_years': 5,
                    'interest_rate': 0.065,
                    'amortization': 'straight_line',
                    'covenants': ['debt_service_coverage > 1.25']
                },
                risk_adjustment=0.1
            )
        ]

        # Calculate returns
        estimated_irr = await self._calculate_scenario_irr(
            enterprise_value, funding_components, buyer_profile
        )
        cash_multiple = await self._calculate_cash_multiple(
            enterprise_value, funding_components, buyer_profile
        )

        return OfferScenario(
            scenario_name="Conservative All-Cash",
            total_enterprise_value=enterprise_value,
            funding_components=funding_components,
            deal_structure_type="asset_purchase",
            estimated_irr=estimated_irr,
            cash_on_cash_multiple=cash_multiple,
            payback_period=5.2,
            risk_score=0.3,  # Low risk
            confidence_level=0.9
        )

    async def _create_leveraged_scenario(self, enterprise_value: float,
                                       buyer_profile: Dict[str, Any]) -> OfferScenario:
        """Leveraged buyout scenario with 60% debt financing"""

        # 40% cash, 50% senior debt, 10% mezzanine
        cash_amount = enterprise_value * 0.4
        senior_debt = enterprise_value * 0.5
        mezzanine = enterprise_value * 0.1

        funding_components = [
            FundingComponent(
                source=FundingSource.CASH,
                amount=cash_amount,
                percentage=40.0,
                cost_of_capital=0.05,
                terms={'immediate': True},
                risk_adjustment=0.0
            ),
            FundingComponent(
                source=FundingSource.SENIOR_DEBT,
                amount=senior_debt,
                percentage=50.0,
                cost_of_capital=0.075,
                terms={
                    'term_years': 7,
                    'interest_rate': 0.075,
                    'amortization': 'back_loaded',
                    'covenants': [
                        'debt_service_coverage > 1.2',
                        'total_leverage < 4.0x'
                    ]
                },
                risk_adjustment=0.3
            ),
            FundingComponent(
                source=FundingSource.MEZZANINE,
                amount=mezzanine,
                percentage=10.0,
                cost_of_capital=0.12,
                terms={
                    'term_years': 5,
                    'interest_rate': 0.12,
                    'payment_in_kind': True,
                    'equity_kicker': '2% of equity'
                },
                risk_adjustment=0.5
            )
        ]

        estimated_irr = await self._calculate_scenario_irr(
            enterprise_value, funding_components, buyer_profile
        )
        cash_multiple = await self._calculate_cash_multiple(
            enterprise_value, funding_components, buyer_profile
        )

        return OfferScenario(
            scenario_name="Leveraged Acquisition",
            total_enterprise_value=enterprise_value,
            funding_components=funding_components,
            deal_structure_type="stock_purchase",
            estimated_irr=estimated_irr,
            cash_on_cash_multiple=cash_multiple,
            payback_period=3.8,
            risk_score=0.7,  # Higher risk due to leverage
            confidence_level=0.7
        )

    async def perform_what_if_analysis(self, base_scenario: OfferScenario,
                                     parameter_ranges: Dict[str, tuple]) -> Dict[str, Any]:
        """Advanced what-if analysis with 15+ adjustable parameters"""

        what_if_results = {
            'base_scenario': base_scenario,
            'sensitivity_analysis': {},
            'tornado_diagram_data': {},
            'scenario_matrix': {}
        }

        # Parameters to analyze
        parameters = {
            'enterprise_value': parameter_ranges.get('ev_range', (-20, 20)),  # % change
            'debt_interest_rate': parameter_ranges.get('rate_range', (-1, 2)),  # % points
            'revenue_growth': parameter_ranges.get('growth_range', (-5, 10)),  # % points
            'ebitda_margin': parameter_ranges.get('margin_range', (-2, 3)),  # % points
            'exit_multiple': parameter_ranges.get('exit_range', (-15, 25)),  # % change
            'hold_period': parameter_ranges.get('hold_range', (3, 7)),  # years
        }

        for param_name, (min_change, max_change) in parameters.items():
            sensitivity_data = await self._calculate_parameter_sensitivity(
                base_scenario, param_name, min_change, max_change
            )
            what_if_results['sensitivity_analysis'][param_name] = sensitivity_data

        # Create tornado diagram data (impact on IRR)
        tornado_data = []
        for param_name, sensitivity in what_if_results['sensitivity_analysis'].items():
            impact_range = max(sensitivity['irr_values']) - min(sensitivity['irr_values'])
            tornado_data.append({
                'parameter': param_name,
                'impact_range': impact_range,
                'base_value': sensitivity['base_value'],
                'min_irr': min(sensitivity['irr_values']),
                'max_irr': max(sensitivity['irr_values'])
            })

        # Sort by impact for tornado diagram
        tornado_data.sort(key=lambda x: x['impact_range'], reverse=True)
        what_if_results['tornado_diagram_data'] = tornado_data

        return what_if_results
```

### 4.2 Professional Export Engine

```python
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from pptx import Presentation
from pptx.util import Inches, Pt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4

class ProfessionalExportEngine:
    """Generate investment bank quality exports"""

    async def generate_excel_workbook(self, scenarios: List[OfferScenario],
                                    what_if_analysis: Dict[str, Any],
                                    target_company: str) -> str:
        """Generate comprehensive Excel workbook with interactive features"""

        wb = Workbook()

        # Remove default sheet
        wb.remove(wb.active)

        # Create sheets
        exec_summary = wb.create_sheet("Executive Summary")
        scenario_comparison = wb.create_sheet("Scenario Comparison")
        funding_analysis = wb.create_sheet("Funding Analysis")
        sensitivity_analysis = wb.create_sheet("Sensitivity Analysis")
        returns_calculator = wb.create_sheet("Returns Calculator")

        # Populate Executive Summary
        await self._create_executive_summary_sheet(
            exec_summary, scenarios, target_company
        )

        # Populate Scenario Comparison
        await self._create_scenario_comparison_sheet(
            scenario_comparison, scenarios
        )

        # Populate Funding Analysis
        await self._create_funding_analysis_sheet(
            funding_analysis, scenarios
        )

        # Populate Sensitivity Analysis
        await self._create_sensitivity_sheet(
            sensitivity_analysis, what_if_analysis
        )

        # Create interactive Returns Calculator
        await self._create_returns_calculator_sheet(
            returns_calculator, scenarios[0]  # Use first scenario as template
        )

        # Add charts and formatting
        await self._add_professional_formatting(wb)

        # Save workbook
        filename = f"MA_Offer_Analysis_{target_company}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        wb.save(filename)

        return filename

    async def _create_executive_summary_sheet(self, sheet, scenarios, target_company):
        """Create executive summary with key metrics"""

        # Title and header
        sheet['A1'] = f"M&A Offer Analysis - {target_company}"
        sheet['A1'].font = Font(size=16, bold=True)
        sheet['A1'].alignment = Alignment(horizontal='center')
        sheet.merge_cells('A1:G1')

        # Key metrics table
        sheet['A3'] = "Scenario"
        sheet['B3'] = "Enterprise Value"
        sheet['C3'] = "Equity Required"
        sheet['D3'] = "Estimated IRR"
        sheet['E3'] = "Cash Multiple"
        sheet['F3'] = "Risk Score"
        sheet['G3'] = "Confidence"

        # Header formatting
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")

        for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
            cell = sheet[f'{col}3']
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')

        # Populate scenario data
        for i, scenario in enumerate(scenarios, start=4):
            sheet[f'A{i}'] = scenario.scenario_name
            sheet[f'B{i}'] = scenario.total_enterprise_value
            sheet[f'C{i}'] = sum(fc.amount for fc in scenario.funding_components
                               if fc.source == FundingSource.CASH)
            sheet[f'D{i}'] = f"{scenario.estimated_irr:.1%}"
            sheet[f'E{i}'] = f"{scenario.cash_on_cash_multiple:.1f}x"
            sheet[f'F{i}'] = f"{scenario.risk_score:.1%}"
            sheet[f'G{i}'] = f"{scenario.confidence_level:.1%}"

        # Format currency columns
        for row in range(4, 4 + len(scenarios)):
            sheet[f'B{row}'].number_format = '£#,##0'
            sheet[f'C{row}'].number_format = '£#,##0'

        # Add recommendation box
        rec_row = 4 + len(scenarios) + 2
        sheet[f'A{rec_row}'] = "RECOMMENDATION:"
        sheet[f'A{rec_row}'].font = Font(bold=True, size=12)

        # AI-generated recommendation
        recommendation = await self._generate_ai_recommendation(scenarios)
        sheet[f'A{rec_row + 1}'] = recommendation
        sheet.merge_cells(f'A{rec_row + 1}:G{rec_row + 3}')
        sheet[f'A{rec_row + 1}'].alignment = Alignment(wrap_text=True, vertical='top')

    async def generate_powerpoint_presentation(self, scenarios: List[OfferScenario],
                                             what_if_analysis: Dict[str, Any],
                                             target_company: str) -> str:
        """Generate professional PowerPoint presentation"""

        prs = Presentation()

        # Slide 1: Title slide
        await self._add_title_slide(prs, target_company, scenarios)

        # Slide 2: Executive summary
        await self._add_executive_summary_slide(prs, scenarios)

        # Slide 3-7: Individual scenario slides
        for scenario in scenarios:
            await self._add_scenario_slide(prs, scenario)

        # Slide 8: Scenario comparison
        await self._add_comparison_slide(prs, scenarios)

        # Slide 9: Sensitivity analysis
        await self._add_sensitivity_slide(prs, what_if_analysis)

        # Slide 10: Recommendations and next steps
        await self._add_recommendations_slide(prs, scenarios)

        # Save presentation
        filename = f"MA_Offer_Presentation_{target_company}_{datetime.now().strftime('%Y%m%d')}.pptx"
        prs.save(filename)

        return filename
```

---

## 5. Implementation Roadmap

### 5.1 Phase 1: Core Foundation (Weeks 1-4)

#### Week 1: Multi-Tenant Accounting Integration

**Days 1-2: Infrastructure Setup**

- [ ] Set up PostgreSQL with multi-tenant schema
- [ ] Create Redis caching layer
- [ ] Implement rate limiting and security middleware
- [ ] Set up monitoring and logging infrastructure

**Days 3-5: Xero Connector (Priority Market)**

- [ ] Implement OAuth2 PKCE flow for Xero
- [ ] Build P&L, Balance Sheet, Cash Flow extractors
- [ ] Create data standardization engine
- [ ] Implement webhook system for real-time sync
- [ ] Add comprehensive error handling and retry logic

**Days 6-7: QuickBooks Connector**

- [ ] Implement QuickBooks Online OAuth2 flow
- [ ] Build report API integrations
- [ ] Add data mapping and validation
- [ ] Test integration with sample data

#### Week 2: Financial Analysis Engine

**Days 8-10: Core Ratio Calculator**

- [ ] Implement 47 financial ratios calculation engine
- [ ] Build industry benchmarking system
- [ ] Create trend analysis algorithms
- [ ] Add data quality scoring

**Days 11-12: AI Integration**

- [ ] Integrate Claude AI for financial insights
- [ ] Build red flag detection algorithms
- [ ] Implement confidence scoring system
- [ ] Create narrative generation engine

**Days 13-14: Testing & Optimization**

- [ ] Unit tests for all calculation engines
- [ ] Performance optimization for <30 second target
- [ ] Integration testing with real accounting data
- [ ] Load testing for 1000+ concurrent analyses

#### Week 3: Valuation Engine

**Days 15-17: DCF Modeling**

- [ ] Build 5-year projection engine
- [ ] Implement WACC calculation
- [ ] Create terminal value calculations
- [ ] Add Monte Carlo simulation

**Days 18-19: Comparable & Precedent Analysis**

- [ ] Build market data integration framework
- [ ] Implement multiple selection algorithms
- [ ] Create statistical analysis engine
- [ ] Add confidence scoring

**Days 20-21: AI-Enhanced Valuations**

- [ ] Integrate AI for assumption validation
- [ ] Build cross-method validation
- [ ] Implement risk factor identification
- [ ] Create valuation synthesis engine

#### Week 4: Offer Stack Generator

**Days 22-24: Scenario Modeling**

- [ ] Build funding component framework
- [ ] Implement 5 standard scenarios
- [ ] Create returns calculation engine
- [ ] Add risk scoring algorithms

**Days 25-26: What-If Analysis**

- [ ] Build parameter sensitivity engine
- [ ] Implement tornado diagram calculations
- [ ] Create scenario comparison tools
- [ ] Add optimization algorithms

**Days 27-28: Professional Exports**

- [ ] Build Excel export engine with charts
- [ ] Create PowerPoint generation system
- [ ] Implement PDF report generation
- [ ] Add professional formatting and branding

### 5.2 Phase 2: Advanced Features (Weeks 5-8)

#### Week 5-6: Additional Integrations

- [ ] Sage Business Cloud connector
- [ ] NetSuite ERP integration
- [ ] FreeAgent and KashFlow connectors
- [ ] Multi-currency support system

#### Week 7-8: Platform Polish

- [ ] Advanced AI features and insights
- [ ] Mobile-responsive design
- [ ] Advanced analytics dashboard
- [ ] Performance monitoring and optimization

---

## 6. Database Schema Design

```sql
-- Multi-tenant accounting connections
CREATE TABLE accounting_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES organizations(id),
    platform VARCHAR(50) NOT NULL, -- xero, quickbooks, sage, etc.
    company_id VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    credentials_encrypted TEXT NOT NULL,
    webhook_url VARCHAR(500),
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_frequency_minutes INTEGER DEFAULT 60,
    data_quality_score DECIMAL(3,2) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(tenant_id, platform, company_id)
);

-- Financial data snapshots
CREATE TABLE financial_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id UUID NOT NULL REFERENCES accounting_connections(id),
    tenant_id UUID NOT NULL REFERENCES organizations(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    currency VARCHAR(3) NOT NULL,

    -- P&L data (JSON structure)
    profit_loss JSONB NOT NULL,

    -- Balance sheet data
    balance_sheet JSONB NOT NULL,

    -- Cash flow data
    cash_flow JSONB NOT NULL,

    -- Trial balance
    trial_balance JSONB NOT NULL,

    -- Aging reports
    aging_reports JSONB,

    -- Quality metrics
    data_quality_score DECIMAL(3,2) NOT NULL,
    extraction_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(connection_id, period_end)
);

-- Partition by tenant_id for performance
ALTER TABLE financial_snapshots PARTITION BY HASH(tenant_id);

-- Financial ratios calculations
CREATE TABLE financial_ratios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID NOT NULL REFERENCES financial_snapshots(id),
    tenant_id UUID NOT NULL REFERENCES organizations(id),

    -- Liquidity ratios
    current_ratio DECIMAL(10,4),
    quick_ratio DECIMAL(10,4),
    cash_ratio DECIMAL(10,4),
    operating_cash_flow_ratio DECIMAL(10,4),

    -- Profitability ratios
    gross_profit_margin DECIMAL(10,4),
    operating_margin DECIMAL(10,4),
    net_profit_margin DECIMAL(10,4),
    ebitda_margin DECIMAL(10,4),
    return_on_assets DECIMAL(10,4),
    return_on_equity DECIMAL(10,4),
    return_on_invested_capital DECIMAL(10,4),

    -- Leverage ratios
    debt_to_equity DECIMAL(10,4),
    debt_to_assets DECIMAL(10,4),
    interest_coverage_ratio DECIMAL(10,4),
    debt_service_coverage_ratio DECIMAL(10,4),

    -- Efficiency ratios
    asset_turnover DECIMAL(10,4),
    inventory_turnover DECIMAL(10,4),
    receivables_turnover DECIMAL(10,4),
    payables_turnover DECIMAL(10,4),

    -- Growth ratios
    revenue_growth_rate DECIMAL(10,4),
    profit_growth_rate DECIMAL(10,4),
    asset_growth_rate DECIMAL(10,4),

    -- Industry benchmarking
    industry_percentile_ranking JSONB,
    peer_comparison_score DECIMAL(3,2),

    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Valuation results
CREATE TABLE valuations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES organizations(id),
    company_id VARCHAR(255) NOT NULL,
    snapshot_id UUID REFERENCES financial_snapshots(id),

    -- Valuation methods and results
    dcf_enterprise_value DECIMAL(15,2),
    dcf_confidence_score DECIMAL(3,2),
    dcf_assumptions JSONB,

    comparable_enterprise_value DECIMAL(15,2),
    comparable_confidence_score DECIMAL(3,2),
    comparable_assumptions JSONB,

    precedent_enterprise_value DECIMAL(15,2),
    precedent_confidence_score DECIMAL(3,2),
    precedent_assumptions JSONB,

    -- Weighted valuation
    weighted_enterprise_value DECIMAL(15,2),
    valuation_range_low DECIMAL(15,2),
    valuation_range_high DECIMAL(15,2),
    recommended_valuation DECIMAL(15,2),

    -- AI insights
    ai_analysis TEXT,
    key_value_drivers TEXT[],
    major_risk_factors TEXT[],

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Offer scenarios
CREATE TABLE offer_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES organizations(id),
    valuation_id UUID REFERENCES valuations(id),

    scenario_name VARCHAR(100) NOT NULL,
    scenario_type VARCHAR(50) NOT NULL,
    total_enterprise_value DECIMAL(15,2) NOT NULL,

    -- Funding structure
    funding_components JSONB NOT NULL,

    -- Returns analysis
    estimated_irr DECIMAL(5,4),
    cash_on_cash_multiple DECIMAL(5,2),
    payback_period DECIMAL(4,1),

    -- Risk assessment
    risk_score DECIMAL(3,2),
    confidence_level DECIMAL(3,2),

    -- What-if analysis results
    sensitivity_analysis JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_financial_snapshots_tenant_period ON financial_snapshots(tenant_id, period_end DESC);
CREATE INDEX idx_financial_ratios_snapshot ON financial_ratios(snapshot_id);
CREATE INDEX idx_valuations_tenant_company ON valuations(tenant_id, company_id);
CREATE INDEX idx_offer_scenarios_valuation ON offer_scenarios(valuation_id);

-- Real-time sync tracking
CREATE TABLE sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id UUID NOT NULL REFERENCES accounting_connections(id),
    sync_type VARCHAR(50) NOT NULL, -- full, incremental, webhook
    status VARCHAR(20) NOT NULL, -- success, error, in_progress
    records_processed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,

    INDEX idx_sync_logs_connection_started (connection_id, started_at DESC)
);
```

---

## 7. API Design Specifications

### 7.1 Core API Endpoints

```python
# Financial Intelligence API
POST /api/v1/financial-intelligence/connections
GET  /api/v1/financial-intelligence/connections
PUT  /api/v1/financial-intelligence/connections/{connection_id}
DELETE /api/v1/financial-intelligence/connections/{connection_id}

POST /api/v1/financial-intelligence/sync/{connection_id}
GET  /api/v1/financial-intelligence/sync-status/{connection_id}

POST /api/v1/financial-intelligence/analyze
GET  /api/v1/financial-intelligence/ratios/{company_id}
GET  /api/v1/financial-intelligence/trends/{company_id}

# Valuation API
POST /api/v1/valuations/comprehensive
GET  /api/v1/valuations/{valuation_id}
POST /api/v1/valuations/comparable-analysis
POST /api/v1/valuations/dcf-analysis

# Offer Stack API
POST /api/v1/offers/generate-scenarios
POST /api/v1/offers/what-if-analysis
POST /api/v1/offers/export/excel
POST /api/v1/offers/export/powerpoint
POST /api/v1/offers/export/pdf

# Multi-Currency API
GET  /api/v1/currencies/rates
POST /api/v1/currencies/convert

# Webhooks
POST /webhooks/xero
POST /webhooks/quickbooks
POST /webhooks/sage
```

### 7.2 Request/Response Models

```python
# Financial Analysis Request
class FinancialAnalysisRequest(BaseModel):
    company_id: str
    connection_id: str
    period_months: int = 12
    include_projections: bool = True
    benchmark_industry: Optional[str] = None
    currency_target: str = "GBP"

# Financial Analysis Response
class FinancialAnalysisResponse(BaseModel):
    company_id: str
    analysis_date: datetime
    period_covered: DateRange
    currency: str

    # Core metrics
    financial_ratios: FinancialRatiosModel

    # Trend analysis
    historical_trends: List[TrendDataPoint]

    # Industry benchmarking
    industry_percentiles: Dict[str, float]
    peer_comparison: PeerComparisonModel

    # AI insights
    ai_analysis: str
    red_flags: List[RedFlagModel]
    growth_opportunities: List[OpportunityModel]

    # Data quality
    data_quality_score: float
    data_completeness: Dict[str, bool]

    # Confidence scoring
    overall_confidence: float
    methodology_confidence: Dict[str, float]

# Valuation Request
class ComprehensiveValuationRequest(BaseModel):
    company_id: str
    snapshot_id: str
    industry: str
    company_profile: CompanyProfileModel
    custom_assumptions: Optional[Dict[str, Any]] = None
    methods: List[ValuationMethod] = [
        ValuationMethod.DCF,
        ValuationMethod.COMPARABLE_COMPANIES,
        ValuationMethod.PRECEDENT_TRANSACTIONS
    ]

# Valuation Response
class ComprehensiveValuationResponse(BaseModel):
    valuation_id: str
    company_id: str
    analysis_date: datetime

    # Individual method results
    dcf_result: Optional[DCFValuationModel]
    comparable_result: Optional[ComparableValuationModel]
    precedent_result: Optional[PrecedentValuationModel]
    asset_based_result: Optional[AssetBasedValuationModel]

    # Synthesis
    weighted_valuation: ValuationSynthesisModel
    valuation_range: ValuationRange
    recommended_valuation: float

    # Confidence and risk
    overall_confidence: float
    key_assumptions: Dict[str, Any]
    sensitivity_analysis: SensitivityAnalysisModel
    risk_factors: List[RiskFactorModel]

    # AI insights
    ai_commentary: str
    value_drivers: List[ValueDriverModel]
    market_positioning: MarketPositioningModel
```

---

This comprehensive Financial Intelligence Engine specification provides the detailed technical foundation for creating an irresistible M&A platform. The multi-tenant accounting integration, AI-powered analysis, and professional-grade outputs will differentiate your platform in the market and drive the targeted 90%+ conversion rate.

The 30-second analysis target, 95% accuracy requirement, and support for 1000+ concurrent analyses are all achievable with this architecture. The combination of real-time data, sophisticated analytics, and professional exports creates unmatched value for M&A professionals.
