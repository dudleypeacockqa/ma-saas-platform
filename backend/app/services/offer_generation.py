"""
Automated Offer Stack Generator Service
Professional acquisition proposals in minutes
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
import asyncio
import numpy as np
from enum import Enum

from app.core.database import get_db
from app.models.deals import Deal
from app.services.financial_intelligence import FinancialIntelligenceService
from app.services.market_intelligence import MarketIntelligenceService
from app.integrations.accounting_connectors import AccountingConnectorService

class FundingType(Enum):
    CASH = "cash"
    DEBT = "debt"
    SELLER_FINANCE = "seller_finance"
    EARNOUT = "earnout"
    HYBRID = "hybrid"

class PaymentTiming(Enum):
    UPFRONT = "upfront"
    DEFERRED = "deferred"
    MILESTONE = "milestone"
    EARNOUT = "earnout"

@dataclass
class DealParameters:
    """Core deal parameters for offer generation"""
    target_company_id: str
    purchase_price_range: tuple[float, float]
    buyer_profile: Dict[str, Any]
    seller_preferences: Dict[str, Any]
    transaction_type: str  # asset_deal, stock_deal, merger
    jurisdiction: str
    currency: str
    financing_constraints: Dict[str, Any]
    timeline_requirements: Dict[str, Any]

@dataclass
class FundingStructure:
    """Individual funding scenario structure"""
    scenario_name: str
    funding_type: FundingType
    total_purchase_price: Decimal
    cash_component: Decimal
    debt_component: Decimal
    seller_finance_component: Decimal
    earnout_component: Decimal
    payment_schedule: List[Dict[str, Any]]
    working_capital_adjustment: Decimal
    transaction_costs: Decimal
    financing_terms: Dict[str, Any]

@dataclass
class FinancialProjections:
    """Financial projections and returns analysis"""
    revenue_projections: List[Decimal]  # 5-year projections
    ebitda_projections: List[Decimal]
    capex_projections: List[Decimal]
    working_capital_changes: List[Decimal]
    terminal_value: Decimal
    discount_rate: float

    # Returns metrics
    irr: float
    multiple_of_money: float
    cash_on_cash_return: float
    payback_period: float

@dataclass
class SensitivityAnalysis:
    """Sensitivity analysis results"""
    base_case_irr: float
    revenue_sensitivity: Dict[str, float]  # {"-10%": 15.2, "base": 18.5, "+10%": 21.8}
    margin_sensitivity: Dict[str, float]
    exit_multiple_sensitivity: Dict[str, float]
    cost_synergy_sensitivity: Dict[str, float]
    tornado_chart_data: List[Dict[str, Any]]

@dataclass
class OfferScenario:
    """Complete offer scenario with all analysis"""
    scenario_id: str
    funding_structure: FundingStructure
    financial_projections: FinancialProjections
    sensitivity_analysis: SensitivityAnalysis
    risk_assessment: Dict[str, Any]
    seller_acceptance_probability: float
    optimization_score: float
    market_competitiveness: Dict[str, Any]

@dataclass
class ExportPackage:
    """Generated export files for the offer"""
    excel_model_path: str
    powerpoint_presentation_path: str
    pdf_summary_path: str
    web_dashboard_url: str
    email_package_data: Dict[str, Any]

@dataclass
class OfferStack:
    """Complete offer stack with all scenarios and exports"""
    deal_id: str
    scenarios: List[OfferScenario]
    recommended_scenario: OfferScenario
    market_intelligence: Dict[str, Any]
    export_package: ExportPackage
    generation_timestamp: datetime
    assumptions: Dict[str, Any]

class OfferStructureGenerator:
    """Generates multiple funding structure scenarios"""

    def __init__(self, financial_service: FinancialIntelligenceService):
        self.financial_service = financial_service

    async def generate_funding_scenarios(self, deal_params: DealParameters) -> List[FundingStructure]:
        """Generate 5+ funding scenarios automatically"""
        scenarios = []

        # Cash scenario
        cash_scenario = await self._generate_cash_scenario(deal_params)
        scenarios.append(cash_scenario)

        # Debt-financed scenario
        debt_scenario = await self._generate_debt_scenario(deal_params)
        scenarios.append(debt_scenario)

        # Seller financing scenario
        seller_finance_scenario = await self._generate_seller_finance_scenario(deal_params)
        scenarios.append(seller_finance_scenario)

        # Earnout scenario
        earnout_scenario = await self._generate_earnout_scenario(deal_params)
        scenarios.append(earnout_scenario)

        # Hybrid scenario (optimal mix)
        hybrid_scenario = await self._generate_hybrid_scenario(deal_params)
        scenarios.append(hybrid_scenario)

        return scenarios

    async def _generate_cash_scenario(self, deal_params: DealParameters) -> FundingStructure:
        """Generate all-cash acquisition scenario"""
        purchase_price = Decimal(str((deal_params.purchase_price_range[0] + deal_params.purchase_price_range[1]) / 2))

        return FundingStructure(
            scenario_name="All-Cash Acquisition",
            funding_type=FundingType.CASH,
            total_purchase_price=purchase_price,
            cash_component=purchase_price,
            debt_component=Decimal('0'),
            seller_finance_component=Decimal('0'),
            earnout_component=Decimal('0'),
            payment_schedule=[
                {
                    "payment_date": "closing",
                    "amount": float(purchase_price * Decimal('0.9')),
                    "description": "Purchase price at closing"
                },
                {
                    "payment_date": "12_months",
                    "amount": float(purchase_price * Decimal('0.1')),
                    "description": "Escrow release (subject to indemnity)"
                }
            ],
            working_capital_adjustment=Decimal('0'),
            transaction_costs=purchase_price * Decimal('0.03'),  # 3% transaction costs
            financing_terms={
                "cash_required": float(purchase_price),
                "financing_contingency": False,
                "closing_certainty": "high"
            }
        )

    async def _generate_debt_scenario(self, deal_params: DealParameters) -> FundingStructure:
        """Generate debt-financed acquisition scenario"""
        purchase_price = Decimal(str((deal_params.purchase_price_range[0] + deal_params.purchase_price_range[1]) / 2))

        # Get target financials for debt capacity
        target_financials = await self.financial_service.get_company_financials(deal_params.target_company_id)
        ttm_ebitda = Decimal(str(target_financials.get('ttm_ebitda', 0)))

        # Conservative 4x EBITDA debt capacity
        max_debt = ttm_ebitda * Decimal('4.0')
        debt_component = min(purchase_price * Decimal('0.7'), max_debt)
        cash_component = purchase_price - debt_component

        return FundingStructure(
            scenario_name="Debt-Financed Acquisition",
            funding_type=FundingType.DEBT,
            total_purchase_price=purchase_price,
            cash_component=cash_component,
            debt_component=debt_component,
            seller_finance_component=Decimal('0'),
            earnout_component=Decimal('0'),
            payment_schedule=[
                {
                    "payment_date": "closing",
                    "amount": float(cash_component + debt_component),
                    "description": "Purchase price at closing (cash + debt)"
                }
            ],
            working_capital_adjustment=Decimal('0'),
            transaction_costs=purchase_price * Decimal('0.04'),  # 4% with debt fees
            financing_terms={
                "debt_amount": float(debt_component),
                "interest_rate": 7.5,  # Current market rates
                "term_years": 7,
                "debt_service_coverage": float(ttm_ebitda / (debt_component * Decimal('0.075'))),
                "financing_contingency": True,
                "lender_approval_required": True
            }
        )

    async def _generate_seller_finance_scenario(self, deal_params: DealParameters) -> FundingStructure:
        """Generate seller financing scenario"""
        purchase_price = Decimal(str((deal_params.purchase_price_range[0] + deal_params.purchase_price_range[1]) / 2))

        # 30% seller financing typical
        seller_finance_component = purchase_price * Decimal('0.3')
        cash_component = purchase_price - seller_finance_component

        return FundingStructure(
            scenario_name="Seller-Financed Acquisition",
            funding_type=FundingType.SELLER_FINANCE,
            total_purchase_price=purchase_price,
            cash_component=cash_component,
            debt_component=Decimal('0'),
            seller_finance_component=seller_finance_component,
            earnout_component=Decimal('0'),
            payment_schedule=[
                {
                    "payment_date": "closing",
                    "amount": float(cash_component),
                    "description": "Cash at closing"
                },
                {
                    "payment_date": "monthly",
                    "amount": float(seller_finance_component / 60),  # 5-year term
                    "description": "Monthly seller note payments"
                }
            ],
            working_capital_adjustment=Decimal('0'),
            transaction_costs=purchase_price * Decimal('0.025'),
            financing_terms={
                "seller_note_amount": float(seller_finance_component),
                "interest_rate": 6.0,  # Below market for seller
                "term_years": 5,
                "personal_guarantee": False,
                "subordination": True,
                "seller_motivation_required": True
            }
        )

    async def _generate_earnout_scenario(self, deal_params: DealParameters) -> FundingStructure:
        """Generate earnout-based scenario"""
        base_price = Decimal(str(deal_params.purchase_price_range[0]))
        max_earnout = Decimal(str(deal_params.purchase_price_range[1] - deal_params.purchase_price_range[0]))

        return FundingStructure(
            scenario_name="Earnout-Based Acquisition",
            funding_type=FundingType.EARNOUT,
            total_purchase_price=base_price + max_earnout,
            cash_component=base_price,
            debt_component=Decimal('0'),
            seller_finance_component=Decimal('0'),
            earnout_component=max_earnout,
            payment_schedule=[
                {
                    "payment_date": "closing",
                    "amount": float(base_price),
                    "description": "Base purchase price"
                },
                {
                    "payment_date": "year_1",
                    "amount": float(max_earnout * Decimal('0.4')),
                    "description": "Year 1 earnout (performance-based)"
                },
                {
                    "payment_date": "year_2",
                    "amount": float(max_earnout * Decimal('0.35')),
                    "description": "Year 2 earnout (performance-based)"
                },
                {
                    "payment_date": "year_3",
                    "amount": float(max_earnout * Decimal('0.25')),
                    "description": "Year 3 earnout (performance-based)"
                }
            ],
            working_capital_adjustment=Decimal('0'),
            transaction_costs=base_price * Decimal('0.03'),
            financing_terms={
                "earnout_metrics": ["revenue_growth", "ebitda_margin", "customer_retention"],
                "earnout_period_years": 3,
                "earnout_calculation": "objective",
                "dispute_resolution": "arbitration",
                "management_retention_required": True
            }
        )

    async def _generate_hybrid_scenario(self, deal_params: DealParameters) -> FundingStructure:
        """Generate optimal hybrid scenario"""
        purchase_price = Decimal(str((deal_params.purchase_price_range[0] + deal_params.purchase_price_range[1]) / 2))

        # Balanced approach: 50% cash, 25% debt, 15% seller finance, 10% earnout
        cash_component = purchase_price * Decimal('0.5')
        debt_component = purchase_price * Decimal('0.25')
        seller_finance_component = purchase_price * Decimal('0.15')
        earnout_component = purchase_price * Decimal('0.1')

        return FundingStructure(
            scenario_name="Optimized Hybrid Structure",
            funding_type=FundingType.HYBRID,
            total_purchase_price=purchase_price,
            cash_component=cash_component,
            debt_component=debt_component,
            seller_finance_component=seller_finance_component,
            earnout_component=earnout_component,
            payment_schedule=[
                {
                    "payment_date": "closing",
                    "amount": float(cash_component + debt_component),
                    "description": "Cash and debt at closing"
                },
                {
                    "payment_date": "monthly",
                    "amount": float(seller_finance_component / 48),  # 4-year seller note
                    "description": "Monthly seller note payments"
                },
                {
                    "payment_date": "annual",
                    "amount": float(earnout_component / 2),  # 2-year earnout
                    "description": "Annual earnout payments (performance-based)"
                }
            ],
            working_capital_adjustment=Decimal('0'),
            transaction_costs=purchase_price * Decimal('0.035'),
            financing_terms={
                "risk_optimization": "balanced",
                "seller_acceptance_probability": 0.85,
                "buyer_risk_mitigation": "high",
                "financing_certainty": "medium-high"
            }
        )

class InteractiveModelingEngine:
    """Real-time financial modeling with what-if analysis"""

    def __init__(self):
        self.calculation_cache = {}

    async def calculate_financial_projections(
        self,
        deal_params: DealParameters,
        funding_structure: FundingStructure,
        scenario_assumptions: Dict[str, Any]
    ) -> FinancialProjections:
        """Calculate comprehensive financial projections"""

        # Get base financial data
        financial_service = FinancialIntelligenceService()
        target_financials = await financial_service.get_company_financials(deal_params.target_company_id)

        # Base financial metrics
        base_revenue = Decimal(str(target_financials.get('ttm_revenue', 0)))
        base_ebitda = Decimal(str(target_financials.get('ttm_ebitda', 0)))

        # Growth assumptions
        revenue_growth_rates = scenario_assumptions.get('revenue_growth', [0.1, 0.08, 0.06, 0.05, 0.04])
        margin_improvement = scenario_assumptions.get('margin_improvement', 0.02)  # 200 bps
        cost_synergies = scenario_assumptions.get('cost_synergies', 0.15)  # 15%

        # Calculate 5-year projections
        revenue_projections = []
        ebitda_projections = []

        current_revenue = base_revenue
        current_ebitda_margin = base_ebitda / base_revenue if base_revenue > 0 else Decimal('0.15')

        for year, growth_rate in enumerate(revenue_growth_rates):
            # Revenue projection
            current_revenue *= (1 + Decimal(str(growth_rate)))
            revenue_projections.append(current_revenue)

            # EBITDA projection with margin improvement and synergies
            synergy_benefit = current_revenue * Decimal(str(cost_synergies)) if year == 0 else Decimal('0')
            improved_margin = current_ebitda_margin + Decimal(str(margin_improvement * (year + 1) / 5))
            current_ebitda = current_revenue * improved_margin + synergy_benefit
            ebitda_projections.append(current_ebitda)

        # Terminal value calculation
        terminal_growth = Decimal('0.025')  # 2.5% terminal growth
        terminal_ebitda = ebitda_projections[-1] * (1 + terminal_growth)
        terminal_multiple = Decimal('8.0')  # 8x EBITDA terminal multiple
        terminal_value = terminal_ebitda * terminal_multiple

        # Discount rate based on deal risk and market conditions
        risk_free_rate = 0.045  # Current 10-year treasury
        equity_risk_premium = 0.065  # Market risk premium
        company_risk_premium = 0.025  # Company-specific risk
        discount_rate = risk_free_rate + equity_risk_premium + company_risk_premium

        # DCF calculation
        dcf_value = self._calculate_dcf_value(
            ebitda_projections,
            terminal_value,
            discount_rate,
            funding_structure
        )

        # Returns calculation
        total_investment = funding_structure.cash_component + funding_structure.debt_component
        irr = self._calculate_irr(total_investment, ebitda_projections, terminal_value, discount_rate)
        multiple_of_money = float(dcf_value / total_investment) if total_investment > 0 else 0

        return FinancialProjections(
            revenue_projections=revenue_projections,
            ebitda_projections=ebitda_projections,
            capex_projections=[rev * Decimal('0.03') for rev in revenue_projections],  # 3% of revenue
            working_capital_changes=[Decimal('0')] * 5,  # Simplified
            terminal_value=terminal_value,
            discount_rate=discount_rate,
            irr=irr,
            multiple_of_money=multiple_of_money,
            cash_on_cash_return=irr,  # Simplified
            payback_period=3.5  # Estimated
        )

    def _calculate_dcf_value(
        self,
        ebitda_projections: List[Decimal],
        terminal_value: Decimal,
        discount_rate: float,
        funding_structure: FundingStructure
    ) -> Decimal:
        """Calculate DCF enterprise value"""
        pv_sum = Decimal('0')

        for year, ebitda in enumerate(ebitda_projections, 1):
            # Convert EBITDA to free cash flow (simplified)
            free_cash_flow = ebitda * Decimal('0.75')  # Tax and capex adjustment
            pv = free_cash_flow / ((1 + Decimal(str(discount_rate))) ** year)
            pv_sum += pv

        # Terminal value PV
        terminal_pv = terminal_value / ((1 + Decimal(str(discount_rate))) ** len(ebitda_projections))

        return pv_sum + terminal_pv

    def _calculate_irr(
        self,
        initial_investment: Decimal,
        cash_flows: List[Decimal],
        terminal_value: Decimal,
        discount_rate: float
    ) -> float:
        """Calculate IRR using iterative method"""
        # Simplified IRR calculation - would use numpy.irr in production
        return discount_rate + 0.05  # Placeholder

    async def perform_sensitivity_analysis(
        self,
        base_projections: FinancialProjections,
        deal_params: DealParameters
    ) -> SensitivityAnalysis:
        """Perform comprehensive sensitivity analysis"""

        base_irr = base_projections.irr

        # Revenue sensitivity
        revenue_sensitivity = {}
        for variance in [-0.2, -0.1, 0, 0.1, 0.2]:
            # Recalculate with revenue variance
            modified_irr = base_irr * (1 + variance * 0.8)  # Simplified
            revenue_sensitivity[f"{variance*100:+.0f}%"] = modified_irr

        # Similar for other sensitivities
        margin_sensitivity = {
            "-200bps": base_irr * 0.85,
            "-100bps": base_irr * 0.92,
            "Base": base_irr,
            "+100bps": base_irr * 1.08,
            "+200bps": base_irr * 1.15
        }

        exit_multiple_sensitivity = {
            "6.0x": base_irr * 0.80,
            "7.0x": base_irr * 0.90,
            "8.0x": base_irr,
            "9.0x": base_irr * 1.10,
            "10.0x": base_irr * 1.20
        }

        cost_synergy_sensitivity = {
            "0%": base_irr * 0.75,
            "10%": base_irr * 0.90,
            "15%": base_irr,
            "20%": base_irr * 1.10,
            "25%": base_irr * 1.20
        }

        # Tornado chart data (impact ranking)
        tornado_data = [
            {"variable": "Exit Multiple", "impact": 0.40},
            {"variable": "Revenue Growth", "impact": 0.32},
            {"variable": "EBITDA Margin", "impact": 0.28},
            {"variable": "Cost Synergies", "impact": 0.25}
        ]

        return SensitivityAnalysis(
            base_case_irr=base_irr,
            revenue_sensitivity=revenue_sensitivity,
            margin_sensitivity=margin_sensitivity,
            exit_multiple_sensitivity=exit_multiple_sensitivity,
            cost_synergy_sensitivity=cost_synergy_sensitivity,
            tornado_chart_data=tornado_data
        )

class OptimizationEngine:
    """AI-powered deal structure optimization"""

    def __init__(self, market_service: MarketIntelligenceService):
        self.market_service = market_service

    async def optimize_deal_structure(
        self,
        scenarios: List[OfferScenario],
        deal_params: DealParameters
    ) -> OfferScenario:
        """Select optimal deal structure using multi-criteria optimization"""

        scores = []
        for scenario in scenarios:
            score = await self._calculate_optimization_score(scenario, deal_params)
            scenario.optimization_score = score
            scores.append((score, scenario))

        # Return highest scoring scenario
        return max(scores, key=lambda x: x[0])[1]

    async def _calculate_optimization_score(
        self,
        scenario: OfferScenario,
        deal_params: DealParameters
    ) -> float:
        """Multi-criteria optimization scoring"""

        # Weight factors
        weights = {
            'irr': 0.30,
            'seller_acceptance': 0.25,
            'execution_certainty': 0.20,
            'market_competitiveness': 0.15,
            'risk_mitigation': 0.10
        }

        # Normalize scores (0-1)
        irr_score = min(scenario.financial_projections.irr / 0.25, 1.0)  # Cap at 25% IRR
        acceptance_score = scenario.seller_acceptance_probability
        execution_score = self._calculate_execution_certainty(scenario.funding_structure)
        market_score = await self._calculate_market_competitiveness(scenario, deal_params)
        risk_score = self._calculate_risk_mitigation_score(scenario)

        # Weighted average
        total_score = (
            weights['irr'] * irr_score +
            weights['seller_acceptance'] * acceptance_score +
            weights['execution_certainty'] * execution_score +
            weights['market_competitiveness'] * market_score +
            weights['risk_mitigation'] * risk_score
        )

        return total_score

    def _calculate_execution_certainty(self, funding_structure: FundingStructure) -> float:
        """Calculate execution certainty score"""
        if funding_structure.funding_type == FundingType.CASH:
            return 0.95
        elif funding_structure.funding_type == FundingType.SELLER_FINANCE:
            return 0.85
        elif funding_structure.funding_type == FundingType.DEBT:
            return 0.75
        elif funding_structure.funding_type == FundingType.EARNOUT:
            return 0.70
        else:  # Hybrid
            return 0.80

    async def _calculate_market_competitiveness(
        self,
        scenario: OfferScenario,
        deal_params: DealParameters
    ) -> float:
        """Calculate market competitiveness score"""
        # Get market comparables
        market_data = await self.market_service.get_market_comparables(
            deal_params.target_company_id
        )

        # Compare to market multiples and terms
        market_multiple = market_data.get('median_ev_ebitda', 8.0)
        scenario_multiple = float(scenario.funding_structure.total_purchase_price) / float(scenario.financial_projections.ebitda_projections[0])

        # Score based on competitiveness (higher multiple = more competitive)
        if scenario_multiple >= market_multiple * 1.1:
            return 0.95  # Very competitive
        elif scenario_multiple >= market_multiple:
            return 0.80  # Competitive
        elif scenario_multiple >= market_multiple * 0.9:
            return 0.65  # Moderately competitive
        else:
            return 0.40  # Below market

    def _calculate_risk_mitigation_score(self, scenario: OfferScenario) -> float:
        """Calculate risk mitigation effectiveness"""
        base_score = 0.5

        # Earnout reduces valuation risk
        if scenario.funding_structure.earnout_component > 0:
            base_score += 0.2

        # Seller financing aligns interests
        if scenario.funding_structure.seller_finance_component > 0:
            base_score += 0.15

        # Lower leverage reduces financial risk
        if scenario.funding_structure.debt_component / scenario.funding_structure.total_purchase_price < 0.5:
            base_score += 0.15

        return min(base_score, 1.0)

class OfferStackGeneratorService:
    """Main orchestrator for automated offer generation"""

    def __init__(self):
        self.financial_service = FinancialIntelligenceService()
        self.market_service = MarketIntelligenceService()
        self.structure_generator = OfferStructureGenerator(self.financial_service)
        self.modeling_engine = InteractiveModelingEngine()
        self.optimization_engine = OptimizationEngine(self.market_service)

    async def generate_offer_stack(self, deal_params: DealParameters) -> OfferStack:
        """Generate complete offer stack in <5 minutes"""
        start_time = datetime.now()

        # Step 1: Generate funding scenarios (parallel)
        funding_structures = await self.structure_generator.generate_funding_scenarios(deal_params)

        # Step 2: Calculate financial projections for each scenario (parallel)
        scenario_tasks = []
        for structure in funding_structures:
            task = self._create_offer_scenario(deal_params, structure)
            scenario_tasks.append(task)

        scenarios = await asyncio.gather(*scenario_tasks)

        # Step 3: Optimize and rank scenarios
        recommended_scenario = await self.optimization_engine.optimize_deal_structure(scenarios, deal_params)

        # Step 4: Generate market intelligence
        market_intelligence = await self.market_service.get_comprehensive_market_analysis(
            deal_params.target_company_id
        )

        # Step 5: Generate export package (can be done asynchronously)
        export_package = await self._generate_export_package(scenarios, recommended_scenario)

        generation_time = (datetime.now() - start_time).total_seconds()

        return OfferStack(
            deal_id=deal_params.target_company_id,
            scenarios=scenarios,
            recommended_scenario=recommended_scenario,
            market_intelligence=market_intelligence,
            export_package=export_package,
            generation_timestamp=datetime.now(),
            assumptions={
                "generation_time_seconds": generation_time,
                "scenarios_generated": len(scenarios),
                "optimization_method": "multi_criteria",
                "market_data_date": datetime.now().isoformat()
            }
        )

    async def _create_offer_scenario(
        self,
        deal_params: DealParameters,
        funding_structure: FundingStructure
    ) -> OfferScenario:
        """Create complete offer scenario with all analysis"""

        # Financial projections
        projections = await self.modeling_engine.calculate_financial_projections(
            deal_params, funding_structure, {}
        )

        # Sensitivity analysis
        sensitivity = await self.modeling_engine.perform_sensitivity_analysis(
            projections, deal_params
        )

        # Risk assessment
        risk_assessment = await self._assess_scenario_risk(funding_structure, projections)

        # Seller acceptance probability
        acceptance_probability = await self._calculate_seller_acceptance_probability(
            funding_structure, deal_params
        )

        return OfferScenario(
            scenario_id=f"{funding_structure.funding_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            funding_structure=funding_structure,
            financial_projections=projections,
            sensitivity_analysis=sensitivity,
            risk_assessment=risk_assessment,
            seller_acceptance_probability=acceptance_probability,
            optimization_score=0.0,  # Will be calculated in optimization
            market_competitiveness={}
        )

    async def _assess_scenario_risk(
        self,
        funding_structure: FundingStructure,
        projections: FinancialProjections
    ) -> Dict[str, Any]:
        """Assess risk factors for scenario"""

        return {
            "execution_risk": "low" if funding_structure.funding_type == FundingType.CASH else "medium",
            "financial_risk": "low" if funding_structure.debt_component / funding_structure.total_purchase_price < 0.5 else "medium",
            "valuation_risk": "low" if funding_structure.earnout_component > 0 else "medium",
            "integration_risk": "medium",  # Default
            "market_risk": "medium",  # Default
            "regulatory_risk": "low",  # Default
            "overall_risk_rating": "medium"
        }

    async def _calculate_seller_acceptance_probability(
        self,
        funding_structure: FundingStructure,
        deal_params: DealParameters
    ) -> float:
        """Calculate probability of seller acceptance"""

        base_probability = 0.60  # Base acceptance rate

        # Adjust based on funding structure
        if funding_structure.funding_type == FundingType.CASH:
            base_probability += 0.25  # Cash premium
        elif funding_structure.funding_type == FundingType.EARNOUT:
            base_probability += 0.15  # Upside potential
        elif funding_structure.funding_type == FundingType.DEBT:
            base_probability += 0.10  # Reasonable certainty

        # Adjust for price competitiveness
        # This would integrate with market intelligence

        return min(base_probability, 0.95)

    async def _generate_export_package(
        self,
        scenarios: List[OfferScenario],
        recommended_scenario: OfferScenario
    ) -> ExportPackage:
        """Generate all export formats"""

        # This would integrate with actual export engines
        return ExportPackage(
            excel_model_path="/exports/excel/offer_model.xlsx",
            powerpoint_presentation_path="/exports/ppt/investor_presentation.pptx",
            pdf_summary_path="/exports/pdf/executive_summary.pdf",
            web_dashboard_url="/dashboard/offer-analysis",
            email_package_data={
                "subject": "Acquisition Proposal - Professional Analysis",
                "attachments": ["offer_model.xlsx", "executive_summary.pdf"],
                "template": "professional_proposal"
            }
        )

# Example usage
async def example_usage():
    """Example of generating an offer stack"""

    deal_params = DealParameters(
        target_company_id="company_123",
        purchase_price_range=(5000000, 7000000),  # $5M - $7M
        buyer_profile={
            "type": "strategic",
            "cash_available": 3000000,
            "debt_capacity": 4000000,
            "acquisition_experience": "high"
        },
        seller_preferences={
            "timeline": "6_months",
            "certainty_importance": "high",
            "tax_optimization": True,
            "continued_involvement": False
        },
        transaction_type="stock_deal",
        jurisdiction="US",
        currency="USD",
        financing_constraints={
            "max_leverage": 4.0,
            "min_cash_at_closing": 0.3
        },
        timeline_requirements={
            "due_diligence_weeks": 8,
            "financing_weeks": 6,
            "closing_weeks": 4
        }
    )

    generator = OfferStackGeneratorService()
    offer_stack = await generator.generate_offer_stack(deal_params)

    print(f"Generated {len(offer_stack.scenarios)} scenarios")
    print(f"Recommended scenario: {offer_stack.recommended_scenario.funding_structure.scenario_name}")
    print(f"Expected IRR: {offer_stack.recommended_scenario.financial_projections.irr:.1%}")
    print(f"Seller acceptance probability: {offer_stack.recommended_scenario.seller_acceptance_probability:.1%}")

if __name__ == "__main__":
    asyncio.run(example_usage())