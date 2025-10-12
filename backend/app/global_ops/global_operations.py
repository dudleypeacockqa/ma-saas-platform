"""
Global Operations Hub - Sprint 11
Multi-currency, multi-jurisdiction operations management for global M&A
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json
from decimal import Decimal, ROUND_HALF_UP
from abc import ABC, abstractmethod


class Currency(str, Enum):
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    JPY = "JPY"  # Japanese Yen
    CNY = "CNY"  # Chinese Yuan
    CAD = "CAD"  # Canadian Dollar
    AUD = "AUD"  # Australian Dollar
    CHF = "CHF"  # Swiss Franc
    SGD = "SGD"  # Singapore Dollar
    HKD = "HKD"  # Hong Kong Dollar
    INR = "INR"  # Indian Rupee
    BRL = "BRL"  # Brazilian Real
    MXN = "MXN"  # Mexican Peso
    KRW = "KRW"  # South Korean Won


class Jurisdiction(str, Enum):
    UNITED_STATES = "US"
    UNITED_KINGDOM = "GB"
    EUROPEAN_UNION = "EU"
    CANADA = "CA"
    AUSTRALIA = "AU"
    JAPAN = "JP"
    CHINA = "CN"
    SINGAPORE = "SG"
    HONG_KONG = "HK"
    INDIA = "IN"
    BRAZIL = "BR"
    MEXICO = "MX"
    SOUTH_KOREA = "KR"
    SWITZERLAND = "CH"


class TaxJurisdiction(str, Enum):
    FEDERAL = "federal"
    STATE_PROVINCIAL = "state_provincial"
    LOCAL = "local"
    INTERNATIONAL = "international"


class TimeZone(str, Enum):
    UTC = "UTC"
    EST = "America/New_York"
    PST = "America/Los_Angeles"
    GMT = "Europe/London"
    CET = "Europe/Paris"
    JST = "Asia/Tokyo"
    CST_CHINA = "Asia/Shanghai"
    SGT = "Asia/Singapore"
    AEST = "Australia/Sydney"
    IST = "Asia/Kolkata"


@dataclass
class ExchangeRate:
    from_currency: Currency
    to_currency: Currency
    rate: Decimal
    timestamp: datetime
    source: str
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None


@dataclass
class CurrencyConversion:
    conversion_id: str
    from_currency: Currency
    to_currency: Currency
    original_amount: Decimal
    converted_amount: Decimal
    exchange_rate: Decimal
    conversion_date: datetime
    fees: Decimal
    net_amount: Decimal


@dataclass
class TaxRegulation:
    jurisdiction: Jurisdiction
    tax_type: str
    rate: float
    applicable_threshold: Optional[Decimal]
    exemptions: List[str]
    effective_date: datetime
    expiry_date: Optional[datetime]
    description: str


@dataclass
class RegulatoryRequirement:
    requirement_id: str
    jurisdiction: Jurisdiction
    category: str
    description: str
    compliance_deadline: datetime
    severity: str  # critical, high, medium, low
    applicable_deal_size: Optional[Decimal]
    required_actions: List[str]
    penalties: Dict[str, Any]


@dataclass
class GlobalDealStructure:
    structure_id: str
    deal_id: str
    primary_jurisdiction: Jurisdiction
    secondary_jurisdictions: List[Jurisdiction]
    base_currency: Currency
    deal_currencies: List[Currency]
    tax_optimization_strategy: str
    regulatory_pathway: str
    estimated_completion_time: int  # days
    complexity_score: float


class CurrencyManager:
    """Manages multi-currency operations and conversions"""

    def __init__(self):
        self.exchange_rates: Dict[Tuple[Currency, Currency], ExchangeRate] = {}
        self.conversion_history: List[CurrencyConversion] = []
        self.rate_providers: List[str] = ["central_bank", "financial_data", "market_data"]

    def get_exchange_rate(
        self,
        from_currency: Currency,
        to_currency: Currency,
        date: Optional[datetime] = None
    ) -> Optional[ExchangeRate]:
        """Get current or historical exchange rate"""

        if from_currency == to_currency:
            return ExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=Decimal('1.0'),
                timestamp=datetime.now(),
                source="identity"
            )

        # Simulate real-time exchange rates
        rate_key = (from_currency, to_currency)

        # Mock exchange rates (in production, these would come from financial data providers)
        mock_rates = {
            (Currency.USD, Currency.EUR): Decimal('0.85'),
            (Currency.USD, Currency.GBP): Decimal('0.73'),
            (Currency.USD, Currency.JPY): Decimal('110.25'),
            (Currency.USD, Currency.CNY): Decimal('6.45'),
            (Currency.EUR, Currency.USD): Decimal('1.18'),
            (Currency.GBP, Currency.USD): Decimal('1.37'),
            (Currency.JPY, Currency.USD): Decimal('0.0091'),
            (Currency.CNY, Currency.USD): Decimal('0.155')
        }

        if rate_key in mock_rates:
            rate = ExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=mock_rates[rate_key],
                timestamp=datetime.now(),
                source="market_data",
                bid=mock_rates[rate_key] * Decimal('0.9995'),
                ask=mock_rates[rate_key] * Decimal('1.0005')
            )

            self.exchange_rates[rate_key] = rate
            return rate

        return None

    def convert_currency(
        self,
        amount: Decimal,
        from_currency: Currency,
        to_currency: Currency,
        fee_percentage: float = 0.001
    ) -> CurrencyConversion:
        """Convert amount from one currency to another"""

        conversion_id = f"conv_{from_currency.value}_{to_currency.value}_{datetime.now().timestamp()}"

        exchange_rate = self.get_exchange_rate(from_currency, to_currency)
        if not exchange_rate:
            raise ValueError(f"Exchange rate not available for {from_currency} to {to_currency}")

        converted_amount = amount * exchange_rate.rate
        fees = converted_amount * Decimal(str(fee_percentage))
        net_amount = converted_amount - fees

        conversion = CurrencyConversion(
            conversion_id=conversion_id,
            from_currency=from_currency,
            to_currency=to_currency,
            original_amount=amount,
            converted_amount=converted_amount,
            exchange_rate=exchange_rate.rate,
            conversion_date=datetime.now(),
            fees=fees,
            net_amount=net_amount
        )

        self.conversion_history.append(conversion)
        return conversion

    def get_multi_currency_summary(
        self,
        amounts: Dict[Currency, Decimal],
        target_currency: Currency
    ) -> Dict[str, Any]:
        """Convert multiple currency amounts to target currency and provide summary"""

        total_in_target = Decimal('0')
        conversions = []

        for currency, amount in amounts.items():
            if currency == target_currency:
                converted_amount = amount
                conversion = None
            else:
                conversion = self.convert_currency(amount, currency, target_currency)
                converted_amount = conversion.net_amount
                conversions.append(conversion)

            total_in_target += converted_amount

        return {
            "target_currency": target_currency.value,
            "total_amount": total_in_target,
            "individual_conversions": conversions,
            "currency_breakdown": [
                {
                    "currency": curr.value,
                    "original_amount": amt,
                    "converted_amount": self.convert_currency(amt, curr, target_currency).net_amount
                }
                for curr, amt in amounts.items()
            ],
            "summary_date": datetime.now().isoformat()
        }


class RegulatoryManager:
    """Manages regulatory compliance across jurisdictions"""

    def __init__(self):
        self.tax_regulations: Dict[Jurisdiction, List[TaxRegulation]] = {}
        self.regulatory_requirements: Dict[Jurisdiction, List[RegulatoryRequirement]] = {}
        self.compliance_calendar: List[Dict[str, Any]] = []

    def get_tax_implications(
        self,
        deal_value: Decimal,
        buyer_jurisdiction: Jurisdiction,
        seller_jurisdiction: Jurisdiction,
        deal_structure: str
    ) -> Dict[str, Any]:
        """Calculate tax implications for cross-border transactions"""

        implications = {
            "buyer_jurisdiction": buyer_jurisdiction.value,
            "seller_jurisdiction": seller_jurisdiction.value,
            "deal_value": deal_value,
            "deal_structure": deal_structure,
            "tax_breakdown": {},
            "total_tax_burden": Decimal('0'),
            "optimization_opportunities": [],
            "compliance_requirements": []
        }

        # Mock tax calculations (in production, these would use real tax codes)
        if buyer_jurisdiction != seller_jurisdiction:
            # Cross-border transaction
            withholding_tax_rate = 0.05  # 5% withholding tax
            withholding_tax = deal_value * Decimal(str(withholding_tax_rate))

            implications["tax_breakdown"]["withholding_tax"] = {
                "rate": withholding_tax_rate,
                "amount": withholding_tax,
                "jurisdiction": seller_jurisdiction.value
            }
            implications["total_tax_burden"] += withholding_tax

            # Transaction tax
            transaction_tax_rate = 0.001  # 0.1% transaction tax
            transaction_tax = deal_value * Decimal(str(transaction_tax_rate))

            implications["tax_breakdown"]["transaction_tax"] = {
                "rate": transaction_tax_rate,
                "amount": transaction_tax,
                "jurisdiction": buyer_jurisdiction.value
            }
            implications["total_tax_burden"] += transaction_tax

            # Optimization opportunities
            implications["optimization_opportunities"] = [
                "Consider tax treaty benefits between jurisdictions",
                "Evaluate alternative deal structures for tax efficiency",
                "Review timing of transaction for tax year optimization"
            ]

        # Domestic transaction
        else:
            capital_gains_rate = 0.20  # 20% capital gains tax
            capital_gains_tax = deal_value * Decimal(str(capital_gains_rate))

            implications["tax_breakdown"]["capital_gains"] = {
                "rate": capital_gains_rate,
                "amount": capital_gains_tax,
                "jurisdiction": buyer_jurisdiction.value
            }
            implications["total_tax_burden"] += capital_gains_tax

        return implications

    def get_regulatory_requirements(
        self,
        deal_value: Decimal,
        jurisdictions: List[Jurisdiction],
        industry_sector: str
    ) -> List[RegulatoryRequirement]:
        """Get regulatory requirements for a deal across multiple jurisdictions"""

        requirements = []

        for jurisdiction in jurisdictions:
            # Mock regulatory requirements
            base_requirements = [
                {
                    "category": "antitrust",
                    "description": "Antitrust clearance required for deals above threshold",
                    "threshold": Decimal('100_000_000'),
                    "deadline_days": 120,
                    "severity": "critical"
                },
                {
                    "category": "foreign_investment",
                    "description": "Foreign investment review for strategic sectors",
                    "threshold": Decimal('50_000_000'),
                    "deadline_days": 90,
                    "severity": "high"
                },
                {
                    "category": "securities",
                    "description": "Securities filing requirements for public companies",
                    "threshold": Decimal('10_000_000'),
                    "deadline_days": 30,
                    "severity": "high"
                }
            ]

            for req_data in base_requirements:
                if deal_value >= req_data["threshold"]:
                    requirement = RegulatoryRequirement(
                        requirement_id=f"req_{jurisdiction.value}_{req_data['category']}_{datetime.now().timestamp()}",
                        jurisdiction=jurisdiction,
                        category=req_data["category"],
                        description=req_data["description"],
                        compliance_deadline=datetime.now() + timedelta(days=req_data["deadline_days"]),
                        severity=req_data["severity"],
                        applicable_deal_size=req_data["threshold"],
                        required_actions=[
                            f"Submit {req_data['category']} filing",
                            "Await regulatory approval",
                            "Provide additional documentation if requested"
                        ],
                        penalties={
                            "monetary": deal_value * Decimal('0.01'),  # 1% of deal value
                            "other": "Potential deal blocking"
                        }
                    )
                    requirements.append(requirement)

        return requirements

    def create_compliance_calendar(
        self,
        requirements: List[RegulatoryRequirement]
    ) -> List[Dict[str, Any]]:
        """Create compliance calendar with all regulatory deadlines"""

        calendar_events = []

        for req in requirements:
            # Add milestone events leading up to compliance deadline
            milestones = [
                {"days_before": 60, "description": "Begin preparation"},
                {"days_before": 30, "description": "Submit initial filing"},
                {"days_before": 14, "description": "Follow up on status"},
                {"days_before": 7, "description": "Final compliance check"},
                {"days_before": 0, "description": "Compliance deadline"}
            ]

            for milestone in milestones:
                event_date = req.compliance_deadline - timedelta(days=milestone["days_before"])

                calendar_events.append({
                    "event_id": f"cal_{req.requirement_id}_{milestone['days_before']}",
                    "requirement_id": req.requirement_id,
                    "jurisdiction": req.jurisdiction.value,
                    "category": req.category,
                    "event_date": event_date,
                    "description": milestone["description"],
                    "severity": req.severity,
                    "is_deadline": milestone["days_before"] == 0
                })

        # Sort by date
        calendar_events.sort(key=lambda x: x["event_date"])

        self.compliance_calendar = calendar_events
        return calendar_events


class LocalizationManager:
    """Manages localization and cultural considerations"""

    def __init__(self):
        self.locale_data: Dict[Jurisdiction, Dict[str, Any]] = {}
        self.business_cultures: Dict[Jurisdiction, Dict[str, Any]] = {}

    def get_business_culture_insights(
        self,
        jurisdiction: Jurisdiction
    ) -> Dict[str, Any]:
        """Get business culture and practice insights for jurisdiction"""

        # Mock business culture data
        culture_insights = {
            Jurisdiction.JAPAN: {
                "decision_making": "consensus_based",
                "negotiation_style": "relationship_focused",
                "communication": "indirect",
                "meeting_culture": "formal",
                "timeline_expectations": "deliberate",
                "key_considerations": [
                    "Relationship building is crucial before business discussions",
                    "Allow extra time for consensus-building processes",
                    "Respect for hierarchy and seniority important"
                ]
            },
            Jurisdiction.CHINA: {
                "decision_making": "hierarchical",
                "negotiation_style": "competitive",
                "communication": "context_dependent",
                "meeting_culture": "formal",
                "timeline_expectations": "variable",
                "key_considerations": [
                    "Government relationships may be important",
                    "Face-saving and respect crucial in negotiations",
                    "Local partnerships often beneficial"
                ]
            },
            Jurisdiction.UNITED_STATES: {
                "decision_making": "efficiency_focused",
                "negotiation_style": "direct",
                "communication": "explicit",
                "meeting_culture": "informal",
                "timeline_expectations": "fast",
                "key_considerations": [
                    "Focus on ROI and financial metrics",
                    "Legal documentation and compliance critical",
                    "Speed and decisiveness valued"
                ]
            }
        }

        return culture_insights.get(jurisdiction, {
            "decision_making": "varies",
            "negotiation_style": "mixed",
            "communication": "context_dependent",
            "meeting_culture": "professional",
            "timeline_expectations": "moderate",
            "key_considerations": ["Research local business practices"]
        })

    def get_optimal_meeting_times(
        self,
        participant_timezones: List[TimeZone],
        duration_hours: int = 1
    ) -> List[Dict[str, Any]]:
        """Find optimal meeting times across multiple time zones"""

        # Simplified time zone optimization
        optimal_times = []

        # Mock calculation for demonstration
        base_times = ["09:00", "10:00", "14:00", "15:00"]

        for time_str in base_times:
            time_slot = {
                "suggested_time_utc": f"{time_str} UTC",
                "local_times": {},
                "total_score": 0
            }

            # Calculate local times and score
            for tz in participant_timezones:
                # Simplified - in production would use proper timezone conversion
                local_time = f"{time_str} {tz.value}"
                time_slot["local_times"][tz.value] = local_time

                # Score based on business hours (simplified)
                hour = int(time_str.split(":")[0])
                if 9 <= hour <= 17:
                    time_slot["total_score"] += 10
                else:
                    time_slot["total_score"] += 5

            optimal_times.append(time_slot)

        # Sort by score
        optimal_times.sort(key=lambda x: x["total_score"], reverse=True)

        return optimal_times[:3]  # Return top 3 options


class GlobalOperationsHub:
    """Central hub for global operations management"""

    def __init__(self):
        self.currency_manager = CurrencyManager()
        self.regulatory_manager = RegulatoryManager()
        self.localization_manager = LocalizationManager()
        self.active_operations: Dict[str, GlobalDealStructure] = {}

    def create_global_deal_structure(
        self,
        deal_id: str,
        deal_value: Decimal,
        buyer_jurisdiction: Jurisdiction,
        seller_jurisdiction: Jurisdiction,
        deal_currency: Currency,
        complexity_factors: List[str]
    ) -> GlobalDealStructure:
        """Create optimized global deal structure"""

        structure_id = f"struct_{deal_id}_{datetime.now().timestamp()}"

        # Determine additional jurisdictions based on complexity
        secondary_jurisdictions = []
        if "subsidiary_locations" in complexity_factors:
            secondary_jurisdictions.extend([Jurisdiction.SINGAPORE, Jurisdiction.HONG_KONG])

        if "regulatory_arbitrage" in complexity_factors:
            secondary_jurisdictions.append(Jurisdiction.SWITZERLAND)

        # Determine currency considerations
        deal_currencies = [deal_currency]
        if buyer_jurisdiction != seller_jurisdiction:
            # Add local currencies for cross-border deals
            jurisdiction_currencies = {
                Jurisdiction.UNITED_STATES: Currency.USD,
                Jurisdiction.EUROPEAN_UNION: Currency.EUR,
                Jurisdiction.JAPAN: Currency.JPY,
                Jurisdiction.CHINA: Currency.CNY
            }

            for jurisdiction in [buyer_jurisdiction, seller_jurisdiction]:
                if jurisdiction in jurisdiction_currencies:
                    currency = jurisdiction_currencies[jurisdiction]
                    if currency not in deal_currencies:
                        deal_currencies.append(currency)

        # Calculate complexity score
        complexity_score = len(complexity_factors) * 0.2 + len(secondary_jurisdictions) * 0.15
        if buyer_jurisdiction != seller_jurisdiction:
            complexity_score += 0.3

        # Estimate completion time based on complexity
        base_days = 90
        complexity_days = int(complexity_score * 60)
        estimated_completion = base_days + complexity_days

        structure = GlobalDealStructure(
            structure_id=structure_id,
            deal_id=deal_id,
            primary_jurisdiction=buyer_jurisdiction,
            secondary_jurisdictions=secondary_jurisdictions,
            base_currency=deal_currency,
            deal_currencies=deal_currencies,
            tax_optimization_strategy="standard_treaty_benefits",
            regulatory_pathway="parallel_filing",
            estimated_completion_time=estimated_completion,
            complexity_score=complexity_score
        )

        self.active_operations[structure_id] = structure
        return structure

    def analyze_global_opportunity(
        self,
        deal_value: Decimal,
        target_jurisdictions: List[Jurisdiction],
        industry_sector: str
    ) -> Dict[str, Any]:
        """Comprehensive analysis of global deal opportunity"""

        analysis = {
            "deal_value": deal_value,
            "target_jurisdictions": [j.value for j in target_jurisdictions],
            "industry_sector": industry_sector,
            "analysis_date": datetime.now().isoformat(),
            "regulatory_analysis": {},
            "tax_analysis": {},
            "currency_analysis": {},
            "cultural_considerations": {},
            "overall_feasibility": "high",
            "recommended_structure": {},
            "timeline_estimates": {},
            "risk_factors": []
        }

        # Regulatory analysis for each jurisdiction
        for jurisdiction in target_jurisdictions:
            requirements = self.regulatory_manager.get_regulatory_requirements(
                deal_value, [jurisdiction], industry_sector
            )
            analysis["regulatory_analysis"][jurisdiction.value] = {
                "requirements_count": len(requirements),
                "critical_requirements": [r for r in requirements if r.severity == "critical"],
                "estimated_timeline": max([120] + [r.compliance_deadline.day for r in requirements])
            }

        # Currency analysis
        if len(target_jurisdictions) > 1:
            # Multi-jurisdiction currency considerations
            primary_currency = Currency.USD  # Default

            currency_exposure = {}
            for jurisdiction in target_jurisdictions:
                # Mock currency exposure calculation
                exposure_percentage = 1.0 / len(target_jurisdictions)
                currency_exposure[jurisdiction.value] = {
                    "exposure_percentage": exposure_percentage,
                    "hedging_recommended": exposure_percentage > 0.25
                }

            analysis["currency_analysis"] = {
                "primary_currency": primary_currency.value,
                "currency_exposure": currency_exposure,
                "hedging_strategy": "forward_contracts"
            }

        # Overall recommendations
        analysis["recommended_structure"] = {
            "primary_jurisdiction": target_jurisdictions[0].value,
            "holding_structure": "international_holding_company",
            "tax_strategy": "treaty_optimization",
            "regulatory_strategy": "parallel_approval_process"
        }

        return analysis

    def get_cross_border_requirements(
        self,
        from_jurisdiction: Jurisdiction,
        to_jurisdiction: Jurisdiction,
        deal_value: Decimal
    ) -> Dict[str, Any]:
        """Get specific requirements for cross-border transactions"""

        requirements = {
            "from_jurisdiction": from_jurisdiction.value,
            "to_jurisdiction": to_jurisdiction.value,
            "deal_value": deal_value,
            "regulatory_requirements": [],
            "tax_implications": {},
            "documentation_requirements": [],
            "approval_timeline": {},
            "cost_estimates": {}
        }

        # Get regulatory requirements
        all_requirements = self.regulatory_manager.get_regulatory_requirements(
            deal_value, [from_jurisdiction, to_jurisdiction], "general"
        )
        requirements["regulatory_requirements"] = all_requirements

        # Get tax implications
        tax_implications = self.regulatory_manager.get_tax_implications(
            deal_value, from_jurisdiction, to_jurisdiction, "asset_acquisition"
        )
        requirements["tax_implications"] = tax_implications

        # Documentation requirements
        requirements["documentation_requirements"] = [
            "Purchase agreement with local law amendments",
            "Regulatory filing forms for each jurisdiction",
            "Tax clearance certificates",
            "Foreign investment notifications",
            "Environmental compliance certificates"
        ]

        # Timeline estimates
        requirements["approval_timeline"] = {
            "preparation_phase": "30-45 days",
            "regulatory_review": "60-120 days",
            "final_approvals": "14-30 days",
            "total_estimated": "104-195 days"
        }

        return requirements


# Service instance and dependency injection
_global_operations_hub: Optional[GlobalOperationsHub] = None


def get_global_operations_hub() -> GlobalOperationsHub:
    """Get Global Operations Hub instance"""
    global _global_operations_hub
    if _global_operations_hub is None:
        _global_operations_hub = GlobalOperationsHub()
    return _global_operations_hub