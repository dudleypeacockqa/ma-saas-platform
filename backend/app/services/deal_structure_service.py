"""
Deal Structure Service for M&A SaaS Platform
Comprehensive service for deal structuring with optimization and analysis capabilities
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session
import uuid
import json
from copy import deepcopy

from ..models.negotiations import (
    DealStructure, Negotiation,
    DealStructureType
)
from ..models.deal import Deal


class DealStructureService:
    """Service for managing deal structures with optimization capabilities"""

    def __init__(self, db: Session):
        self.db = db

    def create_deal_structure(
        self,
        negotiation_id: str,
        name: str,
        structure_type: DealStructureType,
        description: Optional[str] = None,
        structure_details: Dict[str, Any] = None,
        total_consideration: Optional[Decimal] = None,
        cash_component: Optional[Decimal] = None,
        stock_component: Optional[Decimal] = None,
        debt_component: Optional[Decimal] = None,
        earnout_component: Optional[Decimal] = None,
        created_by_id: Optional[str] = None
    ) -> DealStructure:
        """
        Create a new deal structure option

        Args:
            negotiation_id: Associated negotiation ID
            name: Structure name
            structure_type: Type of deal structure
            description: Structure description
            structure_details: Detailed structure configuration
            total_consideration: Total consideration amount
            cash_component: Cash portion
            stock_component: Stock portion
            debt_component: Debt portion
            earnout_component: Earnout portion
            created_by_id: User creating the structure

        Returns:
            Created deal structure instance
        """
        negotiation = (
            self.db.query(Negotiation)
            .filter(Negotiation.id == negotiation_id)
            .first()
        )
        if not negotiation:
            raise ValueError("Negotiation not found")

        if not structure_details:
            structure_details = self._get_default_structure_details(structure_type)

        deal_structure = DealStructure(
            organization_id=negotiation.organization_id,
            negotiation_id=negotiation_id,
            name=name,
            structure_type=structure_type,
            description=description,
            structure_details=structure_details,
            total_consideration=total_consideration,
            cash_component=cash_component,
            stock_component=stock_component,
            debt_component=debt_component,
            earnout_component=earnout_component,
            created_by=created_by_id
        )

        self.db.add(deal_structure)
        self.db.commit()
        self.db.refresh(deal_structure)

        # Perform initial analysis
        self.analyze_structure(deal_structure.id, negotiation.organization_id)

        return deal_structure

    def analyze_structure(
        self,
        structure_id: str,
        organization_id: str,
        tax_rates: Optional[Dict[str, float]] = None,
        discount_rate: float = 0.10
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a deal structure

        Args:
            structure_id: Deal structure ID
            organization_id: Tenant ID for security
            tax_rates: Custom tax rates for analysis
            discount_rate: Discount rate for NPV calculations

        Returns:
            Dictionary with analysis results
        """
        structure = (
            self.db.query(DealStructure)
            .filter(
                DealStructure.id == structure_id,
                DealStructure.organization_id == organization_id
            )
            .first()
        )

        if not structure:
            raise ValueError("Deal structure not found")

        # Default tax rates if not provided
        if not tax_rates:
            tax_rates = {
                'corporate_tax_rate': 0.21,
                'capital_gains_rate': 0.20,
                'ordinary_income_rate': 0.37,
                'depreciation_recapture_rate': 0.25
            }

        analysis = {
            'structure_id': structure_id,
            'structure_type': structure.structure_type.value,
            'total_consideration': float(structure.total_consideration) if structure.total_consideration else 0,
            'tax_analysis': {},
            'financial_metrics': {},
            'risk_assessment': {},
            'recommendations': []
        }

        # Tax analysis
        analysis['tax_analysis'] = self._analyze_tax_implications(structure, tax_rates)

        # Financial metrics
        analysis['financial_metrics'] = self._calculate_financial_metrics(
            structure, discount_rate
        )

        # Risk assessment
        analysis['risk_assessment'] = self._assess_risks(structure)

        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(structure, analysis)

        # Update the structure with analysis results
        structure.buyer_tax_impact = analysis['tax_analysis'].get('buyer_impact', {})
        structure.seller_tax_impact = analysis['tax_analysis'].get('seller_impact', {})
        structure.estimated_tax_savings = Decimal(str(analysis['tax_analysis'].get('total_savings', 0)))
        structure.net_present_value = Decimal(str(analysis['financial_metrics'].get('npv', 0)))
        structure.internal_rate_of_return = Decimal(str(analysis['financial_metrics'].get('irr', 0)))
        structure.return_on_investment = Decimal(str(analysis['financial_metrics'].get('roi', 0)))
        structure.risk_score = analysis['risk_assessment'].get('overall_score', 5)

        self.db.commit()

        return analysis

    def optimize_structure(
        self,
        negotiation_id: str,
        organization_id: str,
        optimization_criteria: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate optimized deal structure options

        Args:
            negotiation_id: Negotiation ID
            organization_id: Tenant ID
            optimization_criteria: Criteria for optimization
                - minimize_tax: Boolean to minimize tax impact
                - maximize_cash: Boolean to maximize cash component
                - minimize_risk: Boolean to minimize overall risk
                - target_irr: Target internal rate of return
            constraints: Constraints for optimization
                - max_debt_ratio: Maximum debt to total consideration ratio
                - min_cash_ratio: Minimum cash component ratio
                - max_earnout_ratio: Maximum earnout component ratio

        Returns:
            List of optimized structure options
        """
        negotiation = (
            self.db.query(Negotiation)
            .filter(
                Negotiation.id == negotiation_id,
                Negotiation.organization_id == organization_id
            )
            .first()
        )

        if not negotiation:
            raise ValueError("Negotiation not found")

        if not constraints:
            constraints = {
                'max_debt_ratio': 0.70,
                'min_cash_ratio': 0.30,
                'max_earnout_ratio': 0.20
            }

        # Get deal information for optimization
        deal = negotiation.deal
        if not deal or not deal.deal_value:
            raise ValueError("Deal value not available for optimization")

        total_value = float(deal.deal_value)
        optimized_structures = []

        # Generate different structure combinations
        structure_combinations = self._generate_structure_combinations(
            total_value, constraints
        )

        for i, combo in enumerate(structure_combinations):
            # Create temporary structure for analysis
            temp_structure = DealStructure(
                organization_id=organization_id,
                negotiation_id=negotiation_id,
                name=f"Optimized Option {i+1}",
                structure_type=combo['structure_type'],
                total_consideration=Decimal(str(total_value)),
                cash_component=Decimal(str(combo['cash'])),
                stock_component=Decimal(str(combo['stock'])),
                debt_component=Decimal(str(combo['debt'])),
                earnout_component=Decimal(str(combo['earnout'])),
                structure_details=combo['details']
            )

            # Analyze this structure
            analysis = self._quick_analyze_structure(temp_structure, optimization_criteria)

            optimized_structures.append({
                'structure': combo,
                'analysis': analysis,
                'optimization_score': self._calculate_optimization_score(
                    analysis, optimization_criteria
                )
            })

        # Sort by optimization score
        optimized_structures.sort(
            key=lambda x: x['optimization_score'],
            reverse=True
        )

        return optimized_structures[:5]  # Return top 5 options

    def compare_structures(
        self,
        structure_ids: List[str],
        organization_id: str,
        comparison_criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple deal structures

        Args:
            structure_ids: List of structure IDs to compare
            organization_id: Tenant ID for security
            comparison_criteria: Specific criteria to compare

        Returns:
            Dictionary with comparison results
        """
        structures = (
            self.db.query(DealStructure)
            .filter(
                DealStructure.id.in_(structure_ids),
                DealStructure.organization_id == organization_id
            )
            .all()
        )

        if len(structures) != len(structure_ids):
            raise ValueError("One or more structures not found")

        if not comparison_criteria:
            comparison_criteria = [
                'total_consideration',
                'tax_efficiency',
                'risk_level',
                'implementation_complexity',
                'expected_returns'
            ]

        comparison = {
            'structures': [],
            'comparison_matrix': {},
            'recommendations': {}
        }

        # Prepare structure data
        for structure in structures:
            structure_data = {
                'id': structure.id,
                'name': structure.name,
                'type': structure.structure_type.value,
                'total_consideration': float(structure.total_consideration or 0),
                'components': {
                    'cash': float(structure.cash_component or 0),
                    'stock': float(structure.stock_component or 0),
                    'debt': float(structure.debt_component or 0),
                    'earnout': float(structure.earnout_component or 0)
                },
                'metrics': {
                    'npv': float(structure.net_present_value or 0),
                    'irr': float(structure.internal_rate_of_return or 0),
                    'roi': float(structure.return_on_investment or 0),
                    'risk_score': structure.risk_score or 5,
                    'complexity': structure.implementation_complexity or 3
                },
                'tax_savings': float(structure.estimated_tax_savings or 0)
            }
            comparison['structures'].append(structure_data)

        # Create comparison matrix
        for criterion in comparison_criteria:
            comparison['comparison_matrix'][criterion] = self._compare_criterion(
                comparison['structures'], criterion
            )

        # Generate recommendations
        comparison['recommendations'] = self._generate_comparison_recommendations(
            comparison['structures']
        )

        return comparison

    def scenario_analysis(
        self,
        structure_id: str,
        organization_id: str,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform scenario analysis on a deal structure

        Args:
            structure_id: Deal structure ID
            organization_id: Tenant ID for security
            scenarios: List of scenarios to analyze
                Each scenario should contain variable changes like:
                - market_conditions: "bull", "bear", "stable"
                - ebitda_multiple_change: percentage change
                - tax_rate_change: percentage point change
                - integration_cost_factor: multiplier for integration costs

        Returns:
            Dictionary with scenario analysis results
        """
        structure = (
            self.db.query(DealStructure)
            .filter(
                DealStructure.id == structure_id,
                DealStructure.organization_id == organization_id
            )
            .first()
        )

        if not structure:
            raise ValueError("Deal structure not found")

        scenario_results = {
            'base_case': self._get_base_case_metrics(structure),
            'scenarios': [],
            'sensitivity_analysis': {},
            'risk_adjusted_metrics': {}
        }

        # Analyze each scenario
        for i, scenario in enumerate(scenarios):
            scenario_name = scenario.get('name', f"Scenario {i+1}")
            scenario_metrics = self._analyze_scenario(structure, scenario)

            scenario_results['scenarios'].append({
                'name': scenario_name,
                'assumptions': scenario,
                'metrics': scenario_metrics,
                'variance_from_base': self._calculate_variance(
                    scenario_results['base_case'],
                    scenario_metrics
                )
            })

        # Perform sensitivity analysis
        scenario_results['sensitivity_analysis'] = self._perform_sensitivity_analysis(
            structure, scenarios
        )

        # Calculate risk-adjusted metrics
        scenario_results['risk_adjusted_metrics'] = self._calculate_risk_adjusted_metrics(
            scenario_results['scenarios']
        )

        return scenario_results

    def get_structure_recommendations(
        self,
        negotiation_id: str,
        organization_id: str,
        deal_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get AI-powered structure recommendations

        Args:
            negotiation_id: Negotiation ID
            organization_id: Tenant ID
            deal_context: Additional context about the deal

        Returns:
            List of recommended structures with rationale
        """
        negotiation = (
            self.db.query(Negotiation)
            .filter(
                Negotiation.id == negotiation_id,
                Negotiation.organization_id == organization_id
            )
            .first()
        )

        if not negotiation:
            raise ValueError("Negotiation not found")

        deal = negotiation.deal
        recommendations = []

        # Asset Purchase Recommendation
        if self._should_recommend_asset_purchase(deal, deal_context):
            asset_rec = self._create_asset_purchase_recommendation(deal, deal_context)
            recommendations.append(asset_rec)

        # Stock Purchase Recommendation
        if self._should_recommend_stock_purchase(deal, deal_context):
            stock_rec = self._create_stock_purchase_recommendation(deal, deal_context)
            recommendations.append(stock_rec)

        # Merger Recommendation
        if self._should_recommend_merger(deal, deal_context):
            merger_rec = self._create_merger_recommendation(deal, deal_context)
            recommendations.append(merger_rec)

        # LBO Recommendation
        if self._should_recommend_lbo(deal, deal_context):
            lbo_rec = self._create_lbo_recommendation(deal, deal_context)
            recommendations.append(lbo_rec)

        # Sort by recommendation score
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)

        return recommendations

    # Private methods for analysis and calculations

    def _get_default_structure_details(self, structure_type: DealStructureType) -> Dict[str, Any]:
        """Get default structure details based on type"""
        base_details = {
            'consideration_structure': {},
            'closing_conditions': [],
            'representations_warranties': [],
            'indemnification': {},
            'post_closing_adjustments': {}
        }

        if structure_type == DealStructureType.ASSET_PURCHASE:
            base_details.update({
                'assets_included': [],
                'liabilities_assumed': [],
                'allocation_schedule': {},
                'bulk_sale_compliance': True
            })
        elif structure_type == DealStructureType.STOCK_PURCHASE:
            base_details.update({
                'share_class': 'common',
                'voting_agreements': {},
                'transfer_restrictions': {},
                'board_composition': {}
            })
        elif structure_type == DealStructureType.MERGER:
            base_details.update({
                'merger_type': 'forward_triangular',
                'exchange_ratio': {},
                'surviving_entity': 'buyer',
                'board_composition': {}
            })

        return base_details

    def _analyze_tax_implications(self, structure: DealStructure, tax_rates: Dict[str, float]) -> Dict[str, Any]:
        """Analyze tax implications of the structure"""
        tax_analysis = {
            'buyer_impact': {},
            'seller_impact': {},
            'total_savings': 0,
            'structure_efficiency': 0
        }

        total_consideration = float(structure.total_consideration or 0)

        if structure.structure_type == DealStructureType.ASSET_PURCHASE:
            # Asset purchase generally better for buyer (step-up basis)
            # But seller may face ordinary income treatment
            buyer_benefit = total_consideration * 0.15  # Depreciation benefits
            seller_penalty = total_consideration * 0.05  # Ordinary income vs capital gains

            tax_analysis['buyer_impact'] = {
                'depreciation_benefit': buyer_benefit,
                'net_impact': buyer_benefit
            }
            tax_analysis['seller_impact'] = {
                'ordinary_income_treatment': seller_penalty,
                'net_impact': -seller_penalty
            }
            tax_analysis['total_savings'] = buyer_benefit - seller_penalty

        elif structure.structure_type == DealStructureType.STOCK_PURCHASE:
            # Stock purchase generally better for seller (capital gains)
            # Less beneficial for buyer (no step-up)
            seller_benefit = total_consideration * 0.08  # Capital gains treatment
            buyer_penalty = total_consideration * 0.05  # No step-up basis

            tax_analysis['buyer_impact'] = {
                'no_step_up_cost': buyer_penalty,
                'net_impact': -buyer_penalty
            }
            tax_analysis['seller_impact'] = {
                'capital_gains_benefit': seller_benefit,
                'net_impact': seller_benefit
            }
            tax_analysis['total_savings'] = seller_benefit - buyer_penalty

        # Calculate structure efficiency (0-100)
        if total_consideration > 0:
            tax_analysis['structure_efficiency'] = min(100, max(0,
                (tax_analysis['total_savings'] / (total_consideration * 0.1)) * 100
            ))

        return tax_analysis

    def _calculate_financial_metrics(self, structure: DealStructure, discount_rate: float) -> Dict[str, Any]:
        """Calculate financial metrics for the structure"""
        total_consideration = float(structure.total_consideration or 0)
        cash_component = float(structure.cash_component or 0)

        # Simple NPV calculation (would be more complex in real implementation)
        expected_synergies = total_consideration * 0.10  # Assume 10% synergies
        integration_costs = total_consideration * 0.03   # Assume 3% integration costs
        annual_benefit = expected_synergies - integration_costs

        # 5-year NPV calculation
        npv = 0
        for year in range(1, 6):
            npv += annual_benefit / ((1 + discount_rate) ** year)

        npv -= cash_component  # Subtract initial cash outlay

        # IRR calculation (simplified)
        irr = (annual_benefit / cash_component) if cash_component > 0 else 0

        # ROI calculation
        roi = (npv / cash_component * 100) if cash_component > 0 else 0

        return {
            'npv': npv,
            'irr': irr * 100,  # Convert to percentage
            'roi': roi,
            'expected_synergies': expected_synergies,
            'integration_costs': integration_costs,
            'payback_period': cash_component / annual_benefit if annual_benefit > 0 else float('inf')
        }

    def _assess_risks(self, structure: DealStructure) -> Dict[str, Any]:
        """Assess risks associated with the structure"""
        risks = {
            'regulatory_risk': 3,  # 1-10 scale
            'integration_risk': 5,
            'financing_risk': 4,
            'market_risk': 4,
            'execution_risk': 3,
            'overall_score': 0,
            'risk_factors': []
        }

        # Adjust risks based on structure type
        if structure.structure_type == DealStructureType.MERGER:
            risks['regulatory_risk'] += 2
            risks['integration_risk'] += 1
            risks['risk_factors'].append("Merger requires regulatory approval")

        if structure.debt_component and structure.total_consideration:
            debt_ratio = float(structure.debt_component) / float(structure.total_consideration)
            if debt_ratio > 0.5:
                risks['financing_risk'] += 2
                risks['risk_factors'].append("High debt component increases financing risk")

        if structure.earnout_component and structure.total_consideration:
            earnout_ratio = float(structure.earnout_component) / float(structure.total_consideration)
            if earnout_ratio > 0.2:
                risks['execution_risk'] += 2
                risks['risk_factors'].append("Significant earnout component increases execution risk")

        # Calculate overall risk score
        risk_scores = [risks['regulatory_risk'], risks['integration_risk'],
                      risks['financing_risk'], risks['market_risk'], risks['execution_risk']]
        risks['overall_score'] = sum(risk_scores) / len(risk_scores)

        return risks

    def _generate_recommendations(self, structure: DealStructure, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        tax_efficiency = analysis['tax_analysis'].get('structure_efficiency', 0)
        if tax_efficiency < 50:
            recommendations.append("Consider alternative structure for better tax efficiency")

        risk_score = analysis['risk_assessment'].get('overall_score', 5)
        if risk_score > 7:
            recommendations.append("High risk structure - consider risk mitigation strategies")

        debt_ratio = 0
        if structure.debt_component and structure.total_consideration:
            debt_ratio = float(structure.debt_component) / float(structure.total_consideration)

        if debt_ratio > 0.6:
            recommendations.append("Consider reducing debt component to lower financing risk")

        npv = analysis['financial_metrics'].get('npv', 0)
        if npv < 0:
            recommendations.append("Structure shows negative NPV - review assumptions or consider alternatives")

        return recommendations

    def _generate_structure_combinations(self, total_value: float, constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate different structure combinations for optimization"""
        combinations = []

        # Asset Purchase combinations
        for cash_ratio in [0.3, 0.5, 0.7, 0.9]:
            for debt_ratio in [0.0, 0.2, 0.4]:
                if cash_ratio + debt_ratio <= 1.0:
                    stock_ratio = 1.0 - cash_ratio - debt_ratio
                    if stock_ratio >= 0:
                        combinations.append({
                            'structure_type': DealStructureType.ASSET_PURCHASE,
                            'cash': total_value * cash_ratio,
                            'stock': total_value * stock_ratio,
                            'debt': total_value * debt_ratio,
                            'earnout': 0,
                            'details': self._get_default_structure_details(DealStructureType.ASSET_PURCHASE)
                        })

        # Stock Purchase combinations
        for cash_ratio in [0.2, 0.4, 0.6, 0.8]:
            for earnout_ratio in [0.0, 0.1, 0.2]:
                if cash_ratio + earnout_ratio <= 1.0:
                    stock_ratio = 1.0 - cash_ratio - earnout_ratio
                    if stock_ratio >= 0:
                        combinations.append({
                            'structure_type': DealStructureType.STOCK_PURCHASE,
                            'cash': total_value * cash_ratio,
                            'stock': total_value * stock_ratio,
                            'debt': 0,
                            'earnout': total_value * earnout_ratio,
                            'details': self._get_default_structure_details(DealStructureType.STOCK_PURCHASE)
                        })

        return combinations[:15]  # Limit to 15 combinations

    def _quick_analyze_structure(self, structure: DealStructure, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Quick analysis for optimization purposes"""
        analysis = {
            'tax_efficiency': 50,  # Default values
            'risk_score': 5,
            'cash_efficiency': 50,
            'npv': 0
        }

        # Tax efficiency based on structure type
        if structure.structure_type == DealStructureType.ASSET_PURCHASE:
            analysis['tax_efficiency'] = 70
        elif structure.structure_type == DealStructureType.STOCK_PURCHASE:
            analysis['tax_efficiency'] = 60

        # Cash efficiency
        if structure.cash_component and structure.total_consideration:
            cash_ratio = float(structure.cash_component) / float(structure.total_consideration)
            analysis['cash_efficiency'] = cash_ratio * 100

        # Risk score (inverse of debt ratio)
        if structure.debt_component and structure.total_consideration:
            debt_ratio = float(structure.debt_component) / float(structure.total_consideration)
            analysis['risk_score'] = 3 + (debt_ratio * 4)  # 3-7 range

        return analysis

    def _calculate_optimization_score(self, analysis: Dict[str, Any], criteria: Dict[str, Any]) -> float:
        """Calculate optimization score based on criteria"""
        score = 0
        weight_sum = 0

        if criteria.get('minimize_tax', False):
            score += analysis['tax_efficiency'] * 0.3
            weight_sum += 0.3

        if criteria.get('maximize_cash', False):
            score += analysis['cash_efficiency'] * 0.25
            weight_sum += 0.25

        if criteria.get('minimize_risk', False):
            score += (10 - analysis['risk_score']) * 10 * 0.25  # Invert risk score
            weight_sum += 0.25

        # Default equal weighting if no specific criteria
        if weight_sum == 0:
            score = (analysis['tax_efficiency'] + analysis['cash_efficiency'] +
                    (10 - analysis['risk_score']) * 10) / 3
        else:
            score = score / weight_sum

        return score

    def _compare_criterion(self, structures: List[Dict], criterion: str) -> Dict[str, Any]:
        """Compare structures on a specific criterion"""
        comparison = {
            'best_structure': None,
            'worst_structure': None,
            'values': {},
            'ranking': []
        }

        values = []
        for structure in structures:
            if criterion == 'tax_efficiency':
                value = structure['tax_savings']
            elif criterion == 'risk_level':
                value = -structure['metrics']['risk_score']  # Lower is better
            elif criterion == 'expected_returns':
                value = structure['metrics']['npv']
            elif criterion == 'implementation_complexity':
                value = -structure['metrics']['complexity']  # Lower is better
            else:
                value = structure.get(criterion, 0)

            values.append((structure['id'], value))
            comparison['values'][structure['id']] = value

        # Sort and rank
        values.sort(key=lambda x: x[1], reverse=True)
        comparison['best_structure'] = values[0][0]
        comparison['worst_structure'] = values[-1][0]
        comparison['ranking'] = [item[0] for item in values]

        return comparison

    def _generate_comparison_recommendations(self, structures: List[Dict]) -> Dict[str, str]:
        """Generate recommendations from structure comparison"""
        recommendations = {}

        # Find best overall structure
        best_npv = max(structures, key=lambda x: x['metrics']['npv'])
        recommendations['highest_value'] = f"Structure '{best_npv['name']}' offers the highest NPV"

        # Find lowest risk
        lowest_risk = min(structures, key=lambda x: x['metrics']['risk_score'])
        recommendations['lowest_risk'] = f"Structure '{lowest_risk['name']}' has the lowest risk profile"

        # Find most tax efficient
        most_tax_efficient = max(structures, key=lambda x: x['tax_savings'])
        recommendations['tax_efficient'] = f"Structure '{most_tax_efficient['name']}' is most tax efficient"

        return recommendations

    def _get_base_case_metrics(self, structure: DealStructure) -> Dict[str, float]:
        """Get base case metrics for scenario analysis"""
        return {
            'npv': float(structure.net_present_value or 0),
            'irr': float(structure.internal_rate_of_return or 0),
            'roi': float(structure.return_on_investment or 0),
            'total_consideration': float(structure.total_consideration or 0)
        }

    def _analyze_scenario(self, structure: DealStructure, scenario: Dict[str, Any]) -> Dict[str, float]:
        """Analyze a specific scenario"""
        base_metrics = self._get_base_case_metrics(structure)

        # Apply scenario adjustments
        multiplier = 1.0
        if scenario.get('market_conditions') == 'bull':
            multiplier = 1.2
        elif scenario.get('market_conditions') == 'bear':
            multiplier = 0.8

        ebitda_change = scenario.get('ebitda_multiple_change', 0)
        multiplier *= (1 + ebitda_change / 100)

        return {
            'npv': base_metrics['npv'] * multiplier,
            'irr': base_metrics['irr'] * multiplier,
            'roi': base_metrics['roi'] * multiplier,
            'total_consideration': base_metrics['total_consideration']
        }

    def _calculate_variance(self, base_case: Dict[str, float], scenario: Dict[str, float]) -> Dict[str, float]:
        """Calculate variance between base case and scenario"""
        variance = {}
        for key in base_case:
            if base_case[key] != 0:
                variance[key] = ((scenario[key] - base_case[key]) / base_case[key]) * 100
            else:
                variance[key] = 0
        return variance

    def _perform_sensitivity_analysis(self, structure: DealStructure, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform sensitivity analysis"""
        # Simplified sensitivity analysis
        return {
            'most_sensitive_factor': 'market_conditions',
            'sensitivity_factors': {
                'market_conditions': 'High',
                'ebitda_multiple': 'Medium',
                'tax_rates': 'Low'
            }
        }

    def _calculate_risk_adjusted_metrics(self, scenarios: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate risk-adjusted metrics across scenarios"""
        if not scenarios:
            return {}

        npv_values = [s['metrics']['npv'] for s in scenarios]
        irr_values = [s['metrics']['irr'] for s in scenarios]

        return {
            'expected_npv': sum(npv_values) / len(npv_values),
            'npv_std_dev': self._calculate_std_dev(npv_values),
            'expected_irr': sum(irr_values) / len(irr_values),
            'irr_std_dev': self._calculate_std_dev(irr_values)
        }

    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5

    # Recommendation helper methods
    def _should_recommend_asset_purchase(self, deal: Deal, context: Optional[Dict[str, Any]]) -> bool:
        """Determine if asset purchase should be recommended"""
        return True  # Simplified - would have more complex logic

    def _should_recommend_stock_purchase(self, deal: Deal, context: Optional[Dict[str, Any]]) -> bool:
        """Determine if stock purchase should be recommended"""
        return True  # Simplified - would have more complex logic

    def _should_recommend_merger(self, deal: Deal, context: Optional[Dict[str, Any]]) -> bool:
        """Determine if merger should be recommended"""
        return deal.deal_value and deal.deal_value > Decimal('100000000')  # Large deals

    def _should_recommend_lbo(self, deal: Deal, context: Optional[Dict[str, Any]]) -> bool:
        """Determine if LBO should be recommended"""
        return context and context.get('private_equity_buyer', False)

    def _create_asset_purchase_recommendation(self, deal: Deal, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create asset purchase recommendation"""
        return {
            'structure_type': DealStructureType.ASSET_PURCHASE,
            'name': 'Asset Purchase Structure',
            'description': 'Purchase specific assets and assume selected liabilities',
            'recommendation_score': 85,
            'pros': ['Step-up basis for buyer', 'Selective liability assumption', 'Clean transaction'],
            'cons': ['Ordinary income treatment for seller', 'Complex asset transfer'],
            'recommended_components': {
                'cash': 60,
                'stock': 30,
                'earnout': 10
            }
        }

    def _create_stock_purchase_recommendation(self, deal: Deal, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create stock purchase recommendation"""
        return {
            'structure_type': DealStructureType.STOCK_PURCHASE,
            'name': 'Stock Purchase Structure',
            'description': 'Purchase equity interests in the target company',
            'recommendation_score': 75,
            'pros': ['Capital gains treatment for seller', 'Simple transaction structure', 'Maintain contracts'],
            'cons': ['No step-up basis', 'Assume all liabilities', 'Due diligence complexity'],
            'recommended_components': {
                'cash': 50,
                'stock': 35,
                'earnout': 15
            }
        }

    def _create_merger_recommendation(self, deal: Deal, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create merger recommendation"""
        return {
            'structure_type': DealStructureType.MERGER,
            'name': 'Merger Structure',
            'description': 'Combine entities through statutory merger',
            'recommendation_score': 70,
            'pros': ['Tax-free reorganization potential', 'Operational synergies', 'Brand consolidation'],
            'cons': ['Regulatory approval required', 'Shareholder approval needed', 'Integration complexity'],
            'recommended_components': {
                'cash': 40,
                'stock': 60,
                'earnout': 0
            }
        }

    def _create_lbo_recommendation(self, deal: Deal, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create LBO recommendation"""
        return {
            'structure_type': DealStructureType.LEVERAGED_BUYOUT,
            'name': 'Leveraged Buyout Structure',
            'description': 'Use significant debt financing for acquisition',
            'recommendation_score': 80,
            'pros': ['Maximize returns with leverage', 'Tax shield benefits', 'Maintain control'],
            'cons': ['High financial risk', 'Debt service requirements', 'Covenant restrictions'],
            'recommended_components': {
                'cash': 20,
                'debt': 70,
                'equity': 10
            }
        }