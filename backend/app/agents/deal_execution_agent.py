"""
Deal Execution Agent
Orchestrates the entire M&A deal process from evaluation to closing
"""
import asyncio
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
import json
from enum import Enum

from app.models.deal import Deal, DealStage, DealType, DealPriority
from app.models.transactions import (
    TransactionPhase, TransactionPhaseType, FinancialModel, ModelType,
    IntegrationPlan, SynergyTracking, SynergyType, VendorManagement,
    VendorType, ClosingChecklist, IntegrationStatus
)
from app.models.due_diligence import (
    DueDiligenceProcess, RiskAssessment, DocumentStatus, RiskLevel
)
from app.services.due_diligence import DueDiligenceService
from app.services.financial_modeling import (
    FinancialModelingEngine, DCFInputs, LBOInputs
)

logger = logging.getLogger(__name__)

class DealExecutionPhase(str, Enum):
    """Deal execution phases"""
    EVALUATION = "evaluation"
    DUE_DILIGENCE = "due_diligence"
    NEGOTIATION = "negotiation"
    DOCUMENTATION = "documentation"
    CLOSING = "closing"
    INTEGRATION = "integration"

class DealExecutionAgent:
    """
    Comprehensive deal execution orchestration agent
    """

    def __init__(self, db: Session):
        self.db = db
        self.dd_service = DueDiligenceService(db)
        self.financial_engine = FinancialModelingEngine()
        self.phase_templates = self._load_phase_templates()

    def _load_phase_templates(self) -> Dict[str, Dict]:
        """Load deal phase templates"""
        return {
            DealType.ACQUISITION: {
                TransactionPhaseType.ORIGINATION: {
                    "duration_days": 30,
                    "key_activities": [
                        "Market scanning and opportunity identification",
                        "Initial target screening",
                        "Strategic fit assessment"
                    ],
                    "deliverables": [
                        "Target long list",
                        "Initial screening memo",
                        "Strategic rationale"
                    ]
                },
                TransactionPhaseType.INITIAL_CONTACT: {
                    "duration_days": 14,
                    "key_activities": [
                        "Management introduction",
                        "Gauge seller interest",
                        "Initial discussions"
                    ],
                    "deliverables": [
                        "Meeting notes",
                        "Interest confirmation",
                        "Process letter"
                    ]
                },
                TransactionPhaseType.DUE_DILIGENCE: {
                    "duration_days": 45,
                    "key_activities": [
                        "Financial due diligence",
                        "Legal due diligence",
                        "Commercial due diligence",
                        "Technical due diligence"
                    ],
                    "deliverables": [
                        "Due diligence reports",
                        "Risk assessment",
                        "Valuation models",
                        "Integration planning"
                    ]
                },
                TransactionPhaseType.CLOSING: {
                    "duration_days": 30,
                    "key_activities": [
                        "Final documentation",
                        "Regulatory approvals",
                        "Financing arrangements",
                        "Closing conditions"
                    ],
                    "deliverables": [
                        "Purchase agreement",
                        "Disclosure schedules",
                        "Closing certificates",
                        "Wire instructions"
                    ]
                }
            },
            DealType.LEVERAGED_BUYOUT: {
                TransactionPhaseType.FINANCING: {
                    "duration_days": 30,
                    "key_activities": [
                        "Debt financing arrangement",
                        "Bank presentations",
                        "Credit agreement negotiation",
                        "Equity commitment letters"
                    ],
                    "deliverables": [
                        "Financing commitment",
                        "Credit agreement",
                        "Fee letters",
                        "Sources and uses"
                    ]
                }
            }
        }

    async def evaluate_opportunity(
        self,
        deal_id: str,
        perform_valuation: bool = True
    ) -> Dict[str, Any]:
        """
        Initial deal evaluation and screening
        """
        deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        evaluation = {
            "deal_id": str(deal_id),
            "evaluation_date": datetime.utcnow(),
            "strategic_fit": await self._assess_strategic_fit(deal),
            "market_analysis": await self._analyze_market(deal),
            "preliminary_valuation": None,
            "key_risks": [],
            "recommendation": None
        }

        # Perform preliminary valuation if requested
        if perform_valuation and deal.target_revenue:
            valuation = await self._preliminary_valuation(deal)
            evaluation["preliminary_valuation"] = valuation

        # Identify key risks
        evaluation["key_risks"] = self._identify_preliminary_risks(deal)

        # Generate recommendation
        evaluation["recommendation"] = self._generate_evaluation_recommendation(evaluation)

        # Create or update evaluation phase
        phase = self._create_phase(
            deal_id,
            TransactionPhaseType.SCREENING,
            "Initial Evaluation",
            duration_days=7
        )

        # Update deal stage if appropriate
        if evaluation["recommendation"]["proceed"]:
            deal.stage = DealStage.INITIAL_REVIEW
            self.db.commit()

        logger.info(f"Completed evaluation for deal {deal_id}")
        return evaluation

    async def _assess_strategic_fit(self, deal: Deal) -> Dict[str, Any]:
        """Assess strategic fit of the deal"""
        fit_score = 0.0
        factors = []

        # Industry alignment
        if deal.target_industry:
            industry_fit = 0.8  # Would be calculated based on portfolio
            fit_score += industry_fit * 0.3
            factors.append({
                "factor": "Industry alignment",
                "score": industry_fit,
                "notes": f"Target in {deal.target_industry}"
            })

        # Size and scale
        if deal.deal_value:
            size_fit = 0.7  # Based on fund size/mandate
            fit_score += size_fit * 0.2
            factors.append({
                "factor": "Deal size",
                "score": size_fit,
                "notes": f"Deal value: ${deal.deal_value:,.0f}"
            })

        # Geographic fit
        geographic_fit = 0.9 if deal.target_country in ["US", "GB", "CA"] else 0.6
        fit_score += geographic_fit * 0.2
        factors.append({
            "factor": "Geographic presence",
            "score": geographic_fit,
            "notes": f"Target in {deal.target_country or 'Unknown'}"
        })

        # Synergy potential (simplified)
        synergy_score = 0.75
        fit_score += synergy_score * 0.3
        factors.append({
            "factor": "Synergy potential",
            "score": synergy_score,
            "notes": "Revenue and cost synergies identified"
        })

        return {
            "overall_score": fit_score,
            "factors": factors,
            "strategic_rationale": deal.strategic_rationale or "Strategic expansion opportunity"
        }

    async def _analyze_market(self, deal: Deal) -> Dict[str, Any]:
        """Analyze market conditions and competitive landscape"""
        return {
            "market_size": "Estimated $10B TAM",  # Would integrate with market data
            "growth_rate": "15% CAGR",
            "competitive_position": "Top 5 player",
            "market_trends": [
                "Digital transformation driving growth",
                "Consolidation among smaller players",
                "Increasing regulatory requirements"
            ],
            "competitive_threats": deal.competitive_landscape or []
        }

    async def _preliminary_valuation(self, deal: Deal) -> Dict[str, Any]:
        """Perform preliminary valuation"""
        # Simple multiple-based valuation
        valuations = {}

        if deal.target_revenue:
            # Revenue multiple
            industry_revenue_multiple = 2.5  # Would be from market data
            valuations["revenue_multiple"] = {
                "method": "Revenue Multiple",
                "multiple": industry_revenue_multiple,
                "value": float(deal.target_revenue) * industry_revenue_multiple
            }

        if deal.target_ebitda:
            # EBITDA multiple
            industry_ebitda_multiple = 10.0  # Would be from market data
            valuations["ebitda_multiple"] = {
                "method": "EBITDA Multiple",
                "multiple": industry_ebitda_multiple,
                "value": float(deal.target_ebitda) * industry_ebitda_multiple
            }

        # Valuation range
        all_values = [v["value"] for v in valuations.values()]
        if all_values:
            valuation_range = {
                "low": min(all_values) * 0.8,
                "midpoint": sum(all_values) / len(all_values),
                "high": max(all_values) * 1.2
            }
        else:
            valuation_range = None

        return {
            "methods": valuations,
            "valuation_range": valuation_range,
            "implied_premium": self._calculate_implied_premium(deal, valuation_range)
        }

    def _calculate_implied_premium(
        self,
        deal: Deal,
        valuation_range: Optional[Dict]
    ) -> Optional[float]:
        """Calculate implied premium over current valuation"""
        if not valuation_range or not deal.deal_value:
            return None

        midpoint = valuation_range["midpoint"]
        return ((float(deal.deal_value) - midpoint) / midpoint) * 100 if midpoint > 0 else None

    def _identify_preliminary_risks(self, deal: Deal) -> List[Dict]:
        """Identify preliminary risks"""
        risks = []

        # Deal-specific risks
        if deal.risk_level == "high" or deal.risk_level == "critical":
            risks.append({
                "type": "execution",
                "description": "High execution risk identified",
                "severity": deal.risk_level,
                "mitigation": "Enhanced due diligence required"
            })

        # Industry risks
        if deal.target_industry and "technology" in deal.target_industry.lower():
            risks.append({
                "type": "technology",
                "description": "Technology obsolescence risk",
                "severity": "medium",
                "mitigation": "Technology due diligence required"
            })

        # Size risks
        if deal.deal_value and float(deal.deal_value) > 1000000000:
            risks.append({
                "type": "size",
                "description": "Large transaction requires significant resources",
                "severity": "medium",
                "mitigation": "Ensure adequate financing and team resources"
            })

        # Add from deal's key_risks if available
        if deal.key_risks:
            for risk in deal.key_risks[:3]:  # Top 3 risks
                risks.append({
                    "type": "identified",
                    "description": risk,
                    "severity": "medium",
                    "mitigation": "Address in due diligence"
                })

        return risks

    def _generate_evaluation_recommendation(self, evaluation: Dict) -> Dict[str, Any]:
        """Generate recommendation based on evaluation"""
        strategic_score = evaluation["strategic_fit"]["overall_score"]
        risks = evaluation["key_risks"]

        # Decision logic
        high_risk_count = sum(1 for r in risks if r["severity"] in ["high", "critical"])

        if strategic_score >= 0.7 and high_risk_count == 0:
            recommendation = "PROCEED"
            proceed = True
            confidence = "High"
        elif strategic_score >= 0.5 and high_risk_count <= 1:
            recommendation = "PROCEED WITH CAUTION"
            proceed = True
            confidence = "Medium"
        else:
            recommendation = "RECONSIDER"
            proceed = False
            confidence = "Low"

        return {
            "recommendation": recommendation,
            "proceed": proceed,
            "confidence": confidence,
            "next_steps": self._get_next_steps(proceed),
            "conditions": self._get_proceed_conditions(risks) if proceed else []
        }

    def _get_next_steps(self, proceed: bool) -> List[str]:
        """Get recommended next steps"""
        if proceed:
            return [
                "Execute NDA",
                "Request initial information",
                "Assemble deal team",
                "Prepare detailed valuation",
                "Initiate due diligence preparation"
            ]
        else:
            return [
                "Re-evaluate strategic rationale",
                "Address identified risks",
                "Consider alternative targets",
                "Update investment thesis"
            ]

    def _get_proceed_conditions(self, risks: List[Dict]) -> List[str]:
        """Get conditions for proceeding"""
        conditions = []

        for risk in risks:
            if risk["severity"] in ["high", "critical"]:
                conditions.append(f"Must address: {risk['description']}")

        conditions.extend([
            "Successful due diligence completion",
            "Valuation within acceptable range",
            "Financing arrangement confirmed",
            "Key employee retention agreements"
        ])

        return conditions[:5]  # Top 5 conditions

    async def orchestrate_due_diligence(
        self,
        deal_id: str,
        checklist_id: Optional[str] = None
    ) -> DueDiligenceProcess:
        """
        Orchestrate comprehensive due diligence process
        """
        deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        # Generate checklist if not provided
        if not checklist_id:
            checklist = await self.dd_service.generate_checklist(
                deal_id,
                deal.deal_type,
                deal.target_industry or "general",
                customize=True
            )
            checklist_id = checklist.id

        # Create due diligence process
        process = DueDiligenceProcess(
            deal_id=deal_id,
            checklist_id=checklist_id,
            name=f"{deal.title} - Due Diligence",
            target_completion_date=datetime.utcnow() + timedelta(days=45),
            current_phase="preparation"
        )

        self.db.add(process)
        self.db.flush()

        # Create transaction phase
        dd_phase = self._create_phase(
            deal_id,
            TransactionPhaseType.DUE_DILIGENCE,
            "Due Diligence",
            duration_days=45
        )

        # Coordinate vendors
        vendors = await self.dd_service.coordinate_vendors(deal_id, str(process.id))

        # Update deal stage
        deal.stage = DealStage.DUE_DILIGENCE
        self.db.commit()

        logger.info(f"Orchestrated due diligence for deal {deal_id}")
        return process

    async def perform_valuation_analysis(
        self,
        deal_id: str,
        valuation_methods: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive valuation analysis
        """
        deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        if not valuation_methods:
            valuation_methods = ["dcf", "comps", "precedent", "lbo"]

        results = {}

        # DCF Valuation
        if "dcf" in valuation_methods and deal.target_revenue:
            dcf_inputs = DCFInputs(
                revenue_base=float(deal.target_revenue),
                revenue_growth_rates=[0.15, 0.12, 0.10, 0.08, 0.05],
                ebitda_margins=[0.20, 0.21, 0.22, 0.22, 0.23],
                wacc=0.10,
                terminal_growth=0.025,
                tax_rate=0.21,
                nwc_pct_revenue=0.10,
                capex_pct_revenue=0.03
            )
            dcf_result = self.financial_engine.dcf_model(dcf_inputs)

            # Save to database
            self._save_financial_model(
                deal_id,
                ModelType.DCF,
                "DCF Valuation",
                dcf_result
            )

            results["dcf"] = dcf_result

        # LBO Analysis
        if "lbo" in valuation_methods and deal.deal_value:
            lbo_inputs = LBOInputs(
                purchase_price=float(deal.deal_value),
                equity_pct=0.40,
                debt_cost=0.06,
                exit_multiple=12.0,
                holding_period=5,
                revenue_base=float(deal.target_revenue) if deal.target_revenue else 0,
                revenue_growth_rates=[0.10, 0.08, 0.07, 0.06, 0.05],
                ebitda_margins=[0.20, 0.21, 0.22, 0.23, 0.24],
                tax_rate=0.21
            )
            lbo_result = self.financial_engine.lbo_model(lbo_inputs)

            # Save to database
            self._save_financial_model(
                deal_id,
                ModelType.LBO,
                "LBO Analysis",
                lbo_result
            )

            results["lbo"] = lbo_result

        # Comparable Company Analysis
        if "comps" in valuation_methods:
            # Mock comparables data (would come from market data service)
            comparables = [
                {
                    "name": "Comp A",
                    "enterprise_value": 500000000,
                    "revenue": 100000000,
                    "ebitda": 20000000,
                    "ebit": 15000000,
                    "market_cap": 450000000,
                    "net_income": 10000000
                },
                {
                    "name": "Comp B",
                    "enterprise_value": 750000000,
                    "revenue": 125000000,
                    "ebitda": 30000000,
                    "ebit": 25000000,
                    "market_cap": 700000000,
                    "net_income": 18000000
                }
            ]

            target_metrics = {
                "revenue": float(deal.target_revenue) if deal.target_revenue else 0,
                "ebitda": float(deal.target_ebitda) if deal.target_ebitda else 0
            }

            comps_result = self.financial_engine.comparable_company_analysis(
                target_metrics,
                comparables
            )

            results["comps"] = comps_result

        # Generate football field chart data
        results["valuation_summary"] = self._generate_valuation_summary(results)

        return results

    def _save_financial_model(
        self,
        deal_id: str,
        model_type: ModelType,
        model_name: str,
        results: Dict
    ):
        """Save financial model to database"""
        model = FinancialModel(
            deal_id=deal_id,
            model_type=model_type,
            model_name=model_name,
            enterprise_value=Decimal(str(results.get("enterprise_value", 0))),
            base_assumptions={
                "wacc": results.get("wacc"),
                "terminal_growth": results.get("terminal_growth"),
                "revenue_growth": results.get("revenue_growth_rates", [])
            },
            sensitivity_results=results.get("sensitivity_analysis", {}),
            confidence_level=Decimal("75.0")  # Default confidence
        )

        self.db.add(model)
        self.db.commit()

    def _generate_valuation_summary(self, results: Dict) -> Dict:
        """Generate valuation summary across methods"""
        valuations = []

        if "dcf" in results:
            valuations.append({
                "method": "DCF",
                "value": results["dcf"]["enterprise_value"],
                "type": "intrinsic"
            })

        if "lbo" in results:
            # LBO provides return metrics, not valuation
            # Use entry valuation
            valuations.append({
                "method": "LBO",
                "value": results["lbo"]["equity_investment"] + results["lbo"]["debt_amount"],
                "type": "financial_buyer"
            })

        if "comps" in results and results["comps"]["valuation_range"]:
            valuations.append({
                "method": "Comparables",
                "value": results["comps"]["valuation_range"]["midpoint"],
                "type": "relative"
            })

        if valuations:
            all_values = [v["value"] for v in valuations]
            return {
                "methods": valuations,
                "range": {
                    "low": min(all_values),
                    "high": max(all_values),
                    "average": sum(all_values) / len(all_values)
                }
            }
        return {}

    async def manage_closing_process(
        self,
        deal_id: str
    ) -> List[ClosingChecklist]:
        """
        Manage deal closing process and checklist
        """
        deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        # Create closing phase
        closing_phase = self._create_phase(
            deal_id,
            TransactionPhaseType.CLOSING_PREPARATION,
            "Closing Preparation",
            duration_days=30
        )

        # Generate closing checklist
        checklist_items = self._generate_closing_checklist(deal)

        for item in checklist_items:
            checklist = ClosingChecklist(
                deal_id=deal_id,
                category=item["category"],
                item_name=item["name"],
                description=item["description"],
                is_condition_precedent=item.get("is_cp", False),
                responsible_party=item.get("responsible", "buyer"),
                due_date=datetime.utcnow() + timedelta(days=item.get("days_before_closing", 5)),
                status="pending"
            )
            self.db.add(checklist)

        # Update deal stage
        deal.stage = DealStage.CLOSING
        self.db.commit()

        # Return checklist
        return self.db.query(ClosingChecklist).filter(
            ClosingChecklist.deal_id == deal_id
        ).all()

    def _generate_closing_checklist(self, deal: Deal) -> List[Dict]:
        """Generate closing checklist items"""
        checklist = [
            {
                "category": "legal",
                "name": "Purchase Agreement Execution",
                "description": "Final execution of definitive purchase agreement",
                "is_cp": True,
                "responsible": "both",
                "days_before_closing": 1
            },
            {
                "category": "legal",
                "name": "Board Resolutions",
                "description": "Board approval and resolutions for transaction",
                "is_cp": True,
                "responsible": "both",
                "days_before_closing": 3
            },
            {
                "category": "financial",
                "name": "Financing Confirmation",
                "description": "Confirmation of financing arrangements",
                "is_cp": True,
                "responsible": "buyer",
                "days_before_closing": 5
            },
            {
                "category": "financial",
                "name": "Working Capital Adjustment",
                "description": "Final working capital calculation and adjustment",
                "is_cp": False,
                "responsible": "both",
                "days_before_closing": 2
            },
            {
                "category": "regulatory",
                "name": "Regulatory Approvals",
                "description": "All required regulatory approvals obtained",
                "is_cp": True,
                "responsible": "both",
                "days_before_closing": 10
            },
            {
                "category": "operational",
                "name": "Key Employee Agreements",
                "description": "Employment agreements with key personnel",
                "is_cp": False,
                "responsible": "buyer",
                "days_before_closing": 7
            },
            {
                "category": "operational",
                "name": "Transition Services Agreement",
                "description": "TSA for post-closing support",
                "is_cp": False,
                "responsible": "both",
                "days_before_closing": 5
            }
        ]

        # Add deal-specific items
        if deal.deal_type == DealType.LEVERAGED_BUYOUT:
            checklist.append({
                "category": "financial",
                "name": "Debt Financing Documents",
                "description": "Credit agreement and security documents",
                "is_cp": True,
                "responsible": "buyer",
                "days_before_closing": 3
            })

        if deal.target_country != "US":
            checklist.append({
                "category": "regulatory",
                "name": "Foreign Investment Approval",
                "description": "CFIUS or equivalent approval",
                "is_cp": True,
                "responsible": "buyer",
                "days_before_closing": 30
            })

        return checklist

    async def plan_integration(
        self,
        deal_id: str,
        integration_approach: str = "full"
    ) -> IntegrationPlan:
        """
        Create post-acquisition integration plan
        """
        deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        # Create integration plan
        plan = IntegrationPlan(
            deal_id=deal_id,
            plan_name=f"{deal.title} - Integration Plan",
            integration_type=integration_approach,
            integration_speed="moderate",
            integration_start_date=deal.expected_close_date or date.today(),
            day_100_date=(deal.expected_close_date or date.today()) + timedelta(days=100),
            full_integration_target=(deal.expected_close_date or date.today()) + timedelta(days=365),
            overall_status=IntegrationStatus.NOT_STARTED
        )

        # Define workstreams
        plan.workstreams = self._define_integration_workstreams(deal, integration_approach)

        # Set milestones
        plan.day_1_milestones = [
            "Welcome communication to all employees",
            "Leadership team announcement",
            "Critical system access confirmed",
            "Day 1 readiness checklist completed"
        ]

        plan.day_30_milestones = [
            "Integration team fully staffed",
            "Detailed integration plan communicated",
            "Initial synergy projects launched",
            "Cultural assessment completed"
        ]

        plan.day_60_milestones = [
            "Quick win synergies realized",
            "Systems integration roadmap finalized",
            "Organization structure finalized",
            "Customer communication completed"
        ]

        plan.day_100_milestones = [
            "Major integration milestones achieved",
            "Synergy realization on track",
            "Employee retention targets met",
            "Integration scorecard green"
        ]

        # Identify synergies
        synergies = await self._identify_synergies(deal)
        plan.synergy_targets = {
            "revenue": sum(s["value"] for s in synergies if s["type"] == SynergyType.REVENUE),
            "cost": sum(s["value"] for s in synergies if s["type"] == SynergyType.COST),
            "total": sum(s["value"] for s in synergies)
        }

        self.db.add(plan)
        self.db.flush()

        # Create synergy tracking records
        for synergy in synergies:
            tracking = SynergyTracking(
                deal_id=deal_id,
                integration_plan_id=plan.id,
                synergy_type=synergy["type"],
                synergy_name=synergy["name"],
                description=synergy["description"],
                target_annual_value=Decimal(str(synergy["value"])),
                target_realization_date=date.today() + timedelta(days=synergy.get("days_to_realize", 180)),
                confidence_level=Decimal(str(synergy.get("confidence", 70)))
            )
            self.db.add(tracking)

        self.db.commit()

        logger.info(f"Created integration plan for deal {deal_id}")
        return plan

    def _define_integration_workstreams(
        self,
        deal: Deal,
        approach: str
    ) -> Dict[str, Any]:
        """Define integration workstreams"""
        workstreams = {
            "finance": {
                "lead": "CFO",
                "priority": "high",
                "activities": [
                    "Financial systems integration",
                    "Reporting harmonization",
                    "Treasury consolidation",
                    "Tax structure optimization"
                ]
            },
            "operations": {
                "lead": "COO",
                "priority": "high",
                "activities": [
                    "Supply chain optimization",
                    "Facility consolidation",
                    "Process standardization",
                    "Quality systems alignment"
                ]
            },
            "commercial": {
                "lead": "CCO",
                "priority": "high",
                "activities": [
                    "Sales force integration",
                    "Customer communication",
                    "Product portfolio optimization",
                    "Pricing harmonization"
                ]
            },
            "technology": {
                "lead": "CTO",
                "priority": "medium",
                "activities": [
                    "IT systems integration",
                    "Data migration",
                    "Security alignment",
                    "Infrastructure consolidation"
                ]
            },
            "hr": {
                "lead": "CHRO",
                "priority": "high",
                "activities": [
                    "Organization design",
                    "Retention programs",
                    "Culture integration",
                    "Benefits harmonization"
                ]
            }
        }

        if approach == "standalone":
            # Reduce integration scope for standalone approach
            for ws in workstreams.values():
                ws["priority"] = "low" if ws["priority"] == "medium" else "medium"
                ws["activities"] = ws["activities"][:2]  # Fewer activities

        return workstreams

    async def _identify_synergies(self, deal: Deal) -> List[Dict]:
        """Identify potential synergies"""
        synergies = []

        # Revenue synergies
        if deal.target_revenue:
            revenue_base = float(deal.target_revenue)

            synergies.append({
                "type": SynergyType.REVENUE,
                "name": "Cross-selling opportunities",
                "description": "Sell existing products to target's customers",
                "value": revenue_base * 0.03,  # 3% of revenue
                "confidence": 70,
                "days_to_realize": 365
            })

            synergies.append({
                "type": SynergyType.REVENUE,
                "name": "Geographic expansion",
                "description": "Leverage combined geographic presence",
                "value": revenue_base * 0.02,  # 2% of revenue
                "confidence": 60,
                "days_to_realize": 540
            })

        # Cost synergies
        if deal.target_ebitda:
            cost_base = float(deal.target_revenue - deal.target_ebitda) if deal.target_revenue else 0

            synergies.append({
                "type": SynergyType.COST,
                "name": "SG&A optimization",
                "description": "Eliminate duplicate functions",
                "value": cost_base * 0.05 if cost_base > 0 else 0,  # 5% of costs
                "confidence": 80,
                "days_to_realize": 180
            })

            synergies.append({
                "type": SynergyType.COST,
                "name": "Procurement savings",
                "description": "Leverage combined purchasing power",
                "value": cost_base * 0.02 if cost_base > 0 else 0,  # 2% of costs
                "confidence": 75,
                "days_to_realize": 270
            })

        return synergies

    def _create_phase(
        self,
        deal_id: str,
        phase_type: TransactionPhaseType,
        phase_name: str,
        duration_days: int
    ) -> TransactionPhase:
        """Create or update transaction phase"""
        phase = self.db.query(TransactionPhase).filter(
            TransactionPhase.deal_id == deal_id,
            TransactionPhase.phase_type == phase_type
        ).first()

        if not phase:
            phase = TransactionPhase(
                deal_id=deal_id,
                phase_type=phase_type,
                phase_name=phase_name,
                planned_start_date=date.today(),
                planned_end_date=date.today() + timedelta(days=duration_days)
            )
            self.db.add(phase)
        else:
            phase.actual_start_date = date.today()
            phase.is_active = True

        # Load template activities if available
        templates = self.phase_templates.get(
            self.db.query(Deal).get(deal_id).deal_type, {}
        )
        if phase_type in templates:
            template = templates[phase_type]
            phase.key_activities = template.get("key_activities", [])
            phase.deliverables = template.get("deliverables", [])

        self.db.commit()
        return phase