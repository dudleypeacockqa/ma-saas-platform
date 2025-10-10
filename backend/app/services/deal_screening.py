from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
import uuid

from ..models.opportunities import (
    MarketOpportunity, FinancialSnapshot,
    IndustryVertical, OpportunityStatus, FinancialHealth,
    DataSourceType
)


class DealScreeningService:
    """Service for screening and filtering deal opportunities"""

    def __init__(self, db: Session):
        self.db = db

    def screen_companies(
        self,
        organization_id: str,
        filters: Dict[str, Any]
    ) -> List[MarketOpportunity]:
        """
        Screen companies based on specified criteria

        Args:
            organization_id: Tenant ID for multi-tenant filtering
            filters: Dictionary of filter criteria
                - revenue_min: Minimum revenue (millions)
                - revenue_max: Maximum revenue (millions)
                - industries: List of IndustryVertical values
                - countries: List of country codes
                - employee_min: Minimum employee count
                - employee_max: Maximum employee count
                - growth_rate_min: Minimum growth rate percentage
                - ebitda_margin_min: Minimum EBITDA margin
                - financial_health: List of FinancialHealth values

        Returns:
            List of companies matching criteria
        """
        query = self.db.query(MarketOpportunity).filter(MarketOpportunity.organization_id == organization_id)

        # Revenue filters
        if revenue_min := filters.get('revenue_min'):
            query = query.filter(MarketOpportunity.revenue_range_min >= revenue_min)
        if revenue_max := filters.get('revenue_max'):
            query = query.filter(MarketOpportunity.revenue_range_max <= revenue_max)

        # Industry filters
        if industries := filters.get('industries'):
            query = query.filter(MarketOpportunity.industry.in_(industries))

        # Geographic filters
        if countries := filters.get('countries'):
            query = query.filter(MarketOpportunity.country.in_(countries))

        # Size filters
        if employee_min := filters.get('employee_min'):
            query = query.filter(MarketOpportunity.employee_count >= employee_min)
        if employee_max := filters.get('employee_max'):
            query = query.filter(MarketOpportunity.employee_count <= employee_max)

        # Performance filters
        if growth_rate_min := filters.get('growth_rate_min'):
            query = query.filter(MarketOpportunity.growth_rate >= growth_rate_min)
        if ebitda_margin_min := filters.get('ebitda_margin_min'):
            query = query.filter(MarketOpportunity.ebitda_margin >= ebitda_margin_min)

        # Financial health filter (requires join with financial snapshots)
        if financial_health := filters.get('financial_health'):
            query = query.join(FinancialSnapshot).filter(
                FinancialSnapshot.financial_health.in_(financial_health)
            )

        return query.all()

    def identify_distressed_companies(
        self,
        organization_id: str,
        threshold_metrics: Optional[Dict[str, float]] = None
    ) -> List[MarketOpportunity]:
        """
        Identify companies showing signs of financial distress

        Args:
            organization_id: Tenant ID
            threshold_metrics: Custom thresholds for distress indicators
                - min_current_ratio: Below this indicates liquidity issues
                - max_debt_to_equity: Above this indicates high leverage
                - min_ebitda_margin: Below this indicates profitability issues
                - negative_growth: Consider negative growth as distress signal

        Returns:
            List of potentially distressed companies
        """
        # Default distress thresholds
        thresholds = threshold_metrics or {
            'min_current_ratio': 1.0,
            'max_debt_to_equity': 3.0,
            'min_ebitda_margin': 0.05,  # 5%
            'negative_growth': True
        }

        # Query for latest financial snapshots
        subquery = (
            self.db.query(
                FinancialSnapshot.company_id,
                func.max(FinancialSnapshot.year).label('latest_year')
            )
            .filter(FinancialSnapshot.organization_id == organization_id)
            .group_by(FinancialSnapshot.company_id)
            .subquery()
        )

        # Join with financial snapshots to check distress indicators
        query = (
            self.db.query(MarketOpportunity)
            .join(FinancialSnapshot)
            .join(
                subquery,
                and_(
                    FinancialSnapshot.company_id == subquery.c.company_id,
                    FinancialSnapshot.year == subquery.c.latest_year
                )
            )
            .filter(MarketOpportunity.organization_id == organization_id)
            .filter(
                or_(
                    FinancialSnapshot.financial_health == FinancialHealth.DISTRESSED,
                    FinancialSnapshot.current_ratio < thresholds['min_current_ratio'],
                    FinancialSnapshot.debt_to_equity > thresholds['max_debt_to_equity'],
                    FinancialSnapshot.ebitda_margin < thresholds['min_ebitda_margin'],
                    and_(
                        thresholds.get('negative_growth', True),
                        FinancialSnapshot.revenue_growth < 0
                    )
                )
            )
        )

        return query.distinct().all()

    def find_succession_opportunities(
        self,
        organization_id: str,
        min_years_in_business: int = 20,
        owner_age_threshold: int = 60
    ) -> List[MarketOpportunity]:
        """
        Identify companies with potential succession planning opportunities

        Args:
            organization_id: Tenant ID
            min_years_in_business: Minimum years company has been operating
            owner_age_threshold: Age threshold for considering succession

        Returns:
            List of succession planning opportunities
        """
        current_year = datetime.now().year

        query = (
            self.db.query(MarketOpportunity)
            .join(MarketOpportunity)
            .filter(MarketOpportunity.organization_id == organization_id)
            .filter(MarketOpportunity.source == DataSourceType.SUCCESSION_PLANNING)
            .filter(MarketOpportunity.year_founded <= (current_year - min_years_in_business))
            .filter(MarketOpportunity.is_active == True)
        )

        return query.all()

    def calculate_opportunity_score(
        self,
        opportunity: MarketOpportunity,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive opportunity score

        Args:
            opportunity: MarketOpportunity to score
            weights: Custom weights for scoring components
                - financial: Weight for financial metrics (default 0.35)
                - strategic: Weight for strategic fit (default 0.25)
                - risk: Weight for risk assessment (default 0.20)
                - growth: Weight for growth potential (default 0.20)

        Returns:
            Dictionary with scoring breakdown and overall score
        """
        # Default weights
        weights = weights or {
            'financial': 0.35,
            'strategic': 0.25,
            'risk': 0.20,
            'growth': 0.20
        }

        scoring = {
            'financial_score': 0,
            'strategic_score': 0,
            'risk_score': 0,
            'growth_score': 0,
            'overall_score': 0,
            'breakdown': {}
        }

        company = opportunity.company

        # Get latest financial snapshot
        latest_snapshot = (
            self.db.query(FinancialSnapshot)
            .filter(FinancialSnapshot.company_id == company.id)
            .order_by(FinancialSnapshot.year.desc())
            .first()
        )

        if latest_snapshot:
            # Financial Score (0-100)
            financial_components = []

            # EBITDA Margin scoring
            if latest_snapshot.ebitda_margin:
                if latest_snapshot.ebitda_margin >= 0.20:
                    financial_components.append(100)
                elif latest_snapshot.ebitda_margin >= 0.15:
                    financial_components.append(80)
                elif latest_snapshot.ebitda_margin >= 0.10:
                    financial_components.append(60)
                elif latest_snapshot.ebitda_margin >= 0.05:
                    financial_components.append(40)
                else:
                    financial_components.append(20)

            # ROE scoring
            if latest_snapshot.return_on_equity:
                if latest_snapshot.return_on_equity >= 0.20:
                    financial_components.append(100)
                elif latest_snapshot.return_on_equity >= 0.15:
                    financial_components.append(75)
                elif latest_snapshot.return_on_equity >= 0.10:
                    financial_components.append(50)
                else:
                    financial_components.append(25)

            # Current Ratio scoring
            if latest_snapshot.current_ratio:
                if latest_snapshot.current_ratio >= 2.0:
                    financial_components.append(100)
                elif latest_snapshot.current_ratio >= 1.5:
                    financial_components.append(75)
                elif latest_snapshot.current_ratio >= 1.0:
                    financial_components.append(50)
                else:
                    financial_components.append(25)

            if financial_components:
                scoring['financial_score'] = sum(financial_components) / len(financial_components)

            # Growth Score
            if latest_snapshot.revenue_growth:
                if latest_snapshot.revenue_growth >= 0.30:
                    scoring['growth_score'] = 100
                elif latest_snapshot.revenue_growth >= 0.20:
                    scoring['growth_score'] = 80
                elif latest_snapshot.revenue_growth >= 0.10:
                    scoring['growth_score'] = 60
                elif latest_snapshot.revenue_growth >= 0.05:
                    scoring['growth_score'] = 40
                else:
                    scoring['growth_score'] = 20

        # Strategic Score (from opportunity data)
        if opportunity.strategic_fit_score:
            scoring['strategic_score'] = opportunity.strategic_fit_score
        else:
            # Calculate based on available factors
            strategic_factors = []

            # Industry alignment
            if company.industry in [IndustryVertical.TECHNOLOGY, IndustryVertical.HEALTHCARE]:
                strategic_factors.append(80)
            elif company.industry in [IndustryVertical.SERVICES, IndustryVertical.MANUFACTURING]:
                strategic_factors.append(60)
            else:
                strategic_factors.append(40)

            # Market position (based on employee count as proxy)
            if company.employee_count and company.employee_count > 100:
                strategic_factors.append(70)
            elif company.employee_count and company.employee_count > 50:
                strategic_factors.append(50)
            else:
                strategic_factors.append(30)

            if strategic_factors:
                scoring['strategic_score'] = sum(strategic_factors) / len(strategic_factors)

        # Risk Score (inverse - lower is better)
        risk_factors = []

        # Financial health risk
        if latest_snapshot and latest_snapshot.financial_health:
            if latest_snapshot.financial_health == FinancialHealth.EXCELLENT:
                risk_factors.append(10)
            elif latest_snapshot.financial_health == FinancialHealth.GOOD:
                risk_factors.append(30)
            elif latest_snapshot.financial_health == FinancialHealth.FAIR:
                risk_factors.append(50)
            elif latest_snapshot.financial_health == FinancialHealth.POOR:
                risk_factors.append(70)
            else:
                risk_factors.append(90)

        # Debt risk
        if latest_snapshot and latest_snapshot.debt_to_equity:
            if latest_snapshot.debt_to_equity < 0.5:
                risk_factors.append(20)
            elif latest_snapshot.debt_to_equity < 1.0:
                risk_factors.append(40)
            elif latest_snapshot.debt_to_equity < 2.0:
                risk_factors.append(60)
            else:
                risk_factors.append(80)

        if risk_factors:
            scoring['risk_score'] = sum(risk_factors) / len(risk_factors)

        # Calculate weighted overall score
        scoring['overall_score'] = (
            scoring['financial_score'] * weights['financial'] +
            scoring['strategic_score'] * weights['strategic'] +
            (100 - scoring['risk_score']) * weights['risk'] +  # Invert risk score
            scoring['growth_score'] * weights['growth']
        )

        # Add breakdown details
        scoring['breakdown'] = {
            'financial': {
                'score': scoring['financial_score'],
                'weight': weights['financial'],
                'weighted_score': scoring['financial_score'] * weights['financial']
            },
            'strategic': {
                'score': scoring['strategic_score'],
                'weight': weights['strategic'],
                'weighted_score': scoring['strategic_score'] * weights['strategic']
            },
            'risk': {
                'score': scoring['risk_score'],
                'weight': weights['risk'],
                'weighted_score': (100 - scoring['risk_score']) * weights['risk']
            },
            'growth': {
                'score': scoring['growth_score'],
                'weight': weights['growth'],
                'weighted_score': scoring['growth_score'] * weights['growth']
            }
        }

        return scoring

    def rank_opportunities(
        self,
        organization_id: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Rank and return top opportunities based on scoring

        Args:
            organization_id: Tenant ID
            filters: Optional filters to apply before ranking
            limit: Maximum number of opportunities to return

        Returns:
            List of ranked opportunities with scores
        """
        query = (
            self.db.query(MarketOpportunity)
            .filter(MarketOpportunity.organization_id == organization_id)
            .filter(MarketOpportunity.is_active == True)
        )

        # Apply stage filter if provided
        if filters and 'stages' in filters:
            query = query.filter(MarketOpportunity.stage.in_(filters['stages']))

        # Apply priority filter if provided
        if filters and 'min_priority' in filters:
            query = query.filter(MarketOpportunity.priority <= filters['min_priority'])

        opportunities = query.all()

        # Calculate scores and rank
        ranked = []
        for opp in opportunities:
            scoring = self.calculate_opportunity_score(opp)
            ranked.append({
                'opportunity': opp,
                'company': opp.company,
                'scores': scoring,
                'overall_score': scoring['overall_score']
            })

        # Sort by overall score (descending)
        ranked.sort(key=lambda x: x['overall_score'], reverse=True)

        return ranked[:limit]